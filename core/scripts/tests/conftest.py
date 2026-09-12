"""Shared fixtures for the core/scripts test harness.

Run the suite with:
    uv run --with pytest --with pyyaml pytest core/scripts/tests/

(pyyaml is build_adapters' runtime dependency; uv's ephemeral env needs it
declared explicitly because pytest is the entry point here, not a script
with inline metadata.)

The suite is hermetic with respect to the owner's account (R11): a sandboxed
`HOME` is applied before collection and a per-test watch fails any test that
changes one of the four live config files or anything under the memory
directory. See `core/CODING_STANDARDS.md` §Tests. (RW-2026-09-12-11,
RW-2026-09-12-12)
"""
import hashlib
import os
import pwd
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / "core" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_checks import home_tilde  # noqa: E402  (the one `~` rule, shared with the validator)

# ── Hermetic HOME (KTD9 / R11) ───────────────────────────────────────────────
# The four config files any host of this framework writes. `install_for.py`
# targets the first three; the fourth is the Claude Code settings file. The
# watch is deliberately file-scoped: `~/.claude` as a whole is rewritten by
# the running host constantly, and a guard that cries wolf gets disabled.
WATCHED_CONFIGS = (
    ".codex/config.toml",
    ".cursor/mcp.json",
    ".gemini/config/mcp_config.json",
    ".claude/settings.json",
)

# Environment variables the sandbox sets or forwards, captured for restore.
_SANDBOX_KEYS = ("HOME", "XDG_CONFIG_HOME", "UV_CACHE_DIR",
                 "UV_PYTHON_INSTALL_DIR", "PERSONAL_OS_MEMORY_DIR")

# Filled by pytest_sessionstart: real_home (Path | None), memory_dir
# (Path | None), sandbox (Path | None), saved_env (dict), notices (list[str]).
SANDBOX: dict = {"real_home": None, "memory_dir": None, "sandbox": None,
                 "saved_env": {}, "notices": []}


def resolve_real_home(getpwuid=pwd.getpwuid, uid=None):
    """The account's home from the password database, never from `HOME`.

    The watch has to know where the live files are *after* `HOME` is moved,
    and it must not trust an environment a test may already have edited. A
    uid with no password-database entry (a container running an unmapped uid)
    yields `(None, notice)`: the sandbox still applies, only the watch is
    skipped."""
    try:
        entry = getpwuid(os.getuid() if uid is None else uid)
    except (KeyError, TypeError, OSError) as exc:
        return None, (f"live-config watch skipped: no password-database entry "
                      f"for this uid ({type(exc).__name__}); the HOME sandbox "
                      f"still applies")
    home = getattr(entry, "pw_dir", None) or (entry[5] if len(entry) > 5 else None)
    if not home:
        return None, ("live-config watch skipped: the password-database entry "
                      "carries no home directory; the HOME sandbox still applies")
    return Path(home), None


def default_memory_dir(real_home: Path | None, root: Path = REPO_ROOT) -> Path | None:
    """Where `validate.py` looks for this project's memory store. Claude Code
    encodes the absolute project path by replacing `/` with `-`. Returns None
    when it cannot be computed, so the caller forwards nothing."""
    if real_home is None:
        return None
    return real_home / ".claude" / "projects" / str(root).replace("/", "-") / "memory"


def _uv_dir(*args) -> str | None:
    """`uv` derives its cache and managed-python directories from HOME, so both
    are captured before the override and forwarded: without them the validator's
    server-import check (27) re-downloads an interpreter and a dependency set
    inside the suite."""
    try:
        proc = subprocess.run(["uv", *args], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    out = proc.stdout.strip()
    return out if proc.returncode == 0 and out else None


def pytest_sessionstart(session):
    """Sandbox `HOME` before collection.

    Not a session fixture: a module that binds `Path.home()` at import time
    (`install_for.py` does, in its config-path constants) evaluates it during
    collection, before any fixture runs."""
    real_home, notice = resolve_real_home()
    if notice:
        SANDBOX["notices"].append(notice)
        print(notice)
    SANDBOX["real_home"] = real_home

    env_mem = os.environ.get("PERSONAL_OS_MEMORY_DIR", "").strip()
    memory = Path(env_mem) if env_mem else default_memory_dir(real_home)
    if memory is not None and not memory.is_dir():
        memory = None
    SANDBOX["memory_dir"] = memory

    uv_cache = _uv_dir("cache", "dir")
    uv_python = _uv_dir("python", "dir")

    # A sibling of every test's project directory, never a parent of one: the
    # guard drill's denied rows build paths under the home directory precisely
    # to land outside the project fence.
    sandbox = Path(tempfile.mkdtemp(prefix="personal-os-sandbox-home-"))
    SANDBOX["sandbox"] = sandbox
    SANDBOX["saved_env"] = {k: os.environ.get(k) for k in _SANDBOX_KEYS}

    os.environ["HOME"] = str(sandbox)
    os.environ["XDG_CONFIG_HOME"] = str(sandbox / ".config")
    if uv_cache:
        os.environ["UV_CACHE_DIR"] = uv_cache
    if uv_python:
        os.environ["UV_PYTHON_INSTALL_DIR"] = uv_python
    if memory is not None:
        # Read-only by intent: the variable enforces nothing, the watch below
        # is what keeps the forward honest. It keeps validator check 12 running
        # inside the suite instead of degrading to its not-found notice.
        os.environ["PERSONAL_OS_MEMORY_DIR"] = str(memory)


def pytest_sessionfinish(session, exitstatus):
    for key, value in SANDBOX["saved_env"].items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    sandbox = SANDBOX.get("sandbox")
    if sandbox is not None:
        shutil.rmtree(sandbox, ignore_errors=True)


def watched_paths(home: Path, memory: Path | None) -> list[Path]:
    """The four named config files plus every file under the memory directory.
    Recomputed on each snapshot so a file a test *creates* is caught too."""
    paths = [home / rel for rel in WATCHED_CONFIGS]
    if memory is not None and memory.is_dir():
        paths += sorted(p for p in memory.rglob("*") if p.is_file())
    return paths


def file_state(path: Path):
    """Existence, size, and a content digest — never the bytes and never the
    mtime. A failing assertion can then name the file without printing any of
    it, and a concurrent host rewrite with identical content does not blame an
    innocent test."""
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return None
    except OSError as exc:
        return ("unreadable", exc.errno)
    return (len(data), hashlib.sha256(data).hexdigest())


def snapshot_state(home: Path, memory: Path | None) -> dict[str, object]:
    return {str(p): file_state(p) for p in watched_paths(home, memory)}


def tilde(path: str, home: Path) -> str:
    """`~/...` form: no username reaches a failure message or a PR quoting it."""
    return home_tilde(path, str(home))


def diff_states(before: dict, after: dict, home: Path) -> list[str]:
    changes = []
    for key in sorted(set(before) | set(after)):
        was, now = before.get(key), after.get(key)
        if was == now:
            continue
        label = tilde(key, home)
        if was is None:
            changes.append(f"{label} was created")
        elif now is None:
            changes.append(f"{label} was removed")
        else:
            changes.append(f"{label} changed")
    return changes


@pytest.fixture(autouse=True)
def live_config_untouched(request):
    """Fail the test that changed one of the owner's live files, by name.

    Function-scoped so the failure carries the test id: the sandbox stops the
    ordinary leak, this catches the one that escapes it — most often a
    subprocess launched with an explicit `env=` dict, which never sees the
    sandboxed `HOME` and resolves the real one through the password
    database."""
    home = SANDBOX.get("real_home")
    if home is None:
        yield
        return
    memory = SANDBOX.get("memory_dir")
    before = snapshot_state(home, memory)
    yield
    changes = diff_states(before, snapshot_state(home, memory), home)
    assert not changes, (
        "this test changed the owner's live configuration: " + "; ".join(changes)
        + f" [test: {request.node.nodeid}]. The suite runs under a sandboxed "
        "HOME, so the write escaped it: a subprocess started with an explicit "
        "`env=` dict sees the real home through the password database — pass "
        "`{**os.environ, ...}` unless isolation is the point. Another process "
        "on this host can also write these files while the suite runs; re-run "
        "to confirm before blaming the test."
    )
