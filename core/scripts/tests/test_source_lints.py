"""Source lints and test-harness hermeticity (R11, R12).

Three guards live here:

* the live-config watch wired in `conftest.py` is exercised end to end — a
  write inside the sandbox is silent, an explicit-`env` subprocess that
  escapes the sandbox is named in `~/...` form, and no file content reaches
  the failure message. Every escape drill runs against an injected home under
  `tmp_path`: no test writes to the account's real files, and the watch over
  them stays enforcement only. The password-database resolution that finds
  those files is proven separately, by feeding `resolve_real_home` a lookup
  that fails (RW-2026-09-12-11, RW-2026-09-12-12);
* the spawn lint fails any sync `subprocess` call in `core/scripts/*.py` or
  `core/mcp/*.py` whose timeout is missing, `None`, zero, negative, or over
  the ceiling — an unbounded spawn turns a hung binary into a hung gate
  (RW-2026-09-12-8);
* the source-grep lint fails any test that reads a skill, agent, command,
  hook, or script as text and searches it for substrings, which proves only
  that the source is the source (RW-2026-09-12-13).

Both lints walk the files `git ls-files` reports rather than a filesystem
glob: a checkout can carry gitignored local scripts under `core/scripts/`
that would otherwise be linted on one machine and not another.

The hermeticity tests live in this module rather than one of their own
because the unit that introduced them ships exactly one new test file.
"""
import ast
import os
import subprocess
import sys
from pathlib import Path

import install_for  # noqa: E402  — imported at collection to prove the sandbox
from conftest import (REPO_ROOT, SANDBOX, diff_states, resolve_real_home,
                      snapshot_state, tilde)

# ═══ hermeticity (R11) ═══════════════════════════════════════════════════════

# The child's env dict is the escape shape the guard drill uses: no `HOME`,
# so the sandbox is invisible to it. The target comes in as an absolute path,
# so a drill never has to resolve — or touch — the account's real home.
_APPEND_SCRIPT = (
    "import pathlib, sys\n"
    "p = pathlib.Path(sys.argv[1])\n"
    "p.parent.mkdir(parents=True, exist_ok=True)\n"
    "with p.open('ab') as fh: fh.write(sys.argv[2].encode())\n"
)


def _explicit_env_writer(script: str, *args) -> subprocess.CompletedProcess:
    """A child started the way the guard drill starts one: an explicit `env`
    dict with no `HOME`, so it never sees the sandbox."""
    return subprocess.run([sys.executable, "-c", script, *args],
                          env={"PATH": os.environ["PATH"]},
                          capture_output=True, text=True, timeout=60)


def test_home_is_sandboxed_before_collection():
    """`install_for.py` binds `Path.home()` at import, in its config-path
    constants. This module imports it at collection time, so the assertion
    fails if the sandbox is ever moved from `pytest_sessionstart` into a
    fixture."""
    sandbox = SANDBOX["sandbox"]
    assert Path.home() == sandbox
    assert str(install_for.CODEX_CONFIG).startswith(str(sandbox))
    assert str(install_for.CURSOR_CONFIG).startswith(str(sandbox))
    assert str(install_for.ANTIGRAVITY_CONFIG).startswith(str(sandbox))
    assert SANDBOX["real_home"] != sandbox


def test_sandbox_home_is_a_sibling_of_the_test_project(tmp_path):
    """The guard drill builds denied rows under the home directory precisely
    to land outside the project fence; a sandbox nested in the project would
    silently turn those rows into in-project writes."""
    home = Path.home()
    assert tmp_path not in home.parents and home != tmp_path
    assert home not in tmp_path.parents


def test_a_watched_write_inside_the_sandbox_is_silent():
    home, memory = SANDBOX["real_home"], SANDBOX["memory_dir"]
    before = snapshot_state(home, memory)
    target = Path.home() / ".codex" / "config.toml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("[mcp_servers.manager-ai]\n", encoding="utf-8")
    assert diff_states(before, snapshot_state(home, memory), home) == []


def test_an_explicit_env_subprocess_write_is_named(tmp_path):
    """The one write a sandbox cannot stop: a child launched with an explicit
    `env` dict. The drill runs against an injected home — the watch over the
    account's real files is enforcement, never a test subject."""
    fake_home = tmp_path / "home"
    target = fake_home / ".codex" / "config.toml"
    target.parent.mkdir(parents=True)

    before = snapshot_state(fake_home, None)
    proc = _explicit_env_writer(_APPEND_SCRIPT, str(target),
                                "[mcp_servers.manager-ai]\n")
    assert proc.returncode == 0, proc.stderr
    changes = diff_states(before, snapshot_state(fake_home, None), fake_home)
    assert changes == ["~/.codex/config.toml was created"], changes

    before = snapshot_state(fake_home, None)
    proc = _explicit_env_writer(_APPEND_SCRIPT, str(target), 'model = "x"\n')
    assert proc.returncode == 0, proc.stderr
    changes = diff_states(before, snapshot_state(fake_home, None), fake_home)
    assert changes == ["~/.codex/config.toml changed"], changes
    assert "mcp_servers" not in " ".join(changes)


def test_a_write_under_a_forwarded_memory_directory_is_named(tmp_path):
    """Validator check 12 keeps its coverage through `PERSONAL_OS_MEMORY_DIR`,
    so the forward has to stay read-only in practice: every file under the
    forwarded directory is watched, and one created there is named like a
    config write."""
    fake_home = tmp_path / "home"
    fake_memory = fake_home / ".claude" / "projects" / "x" / "memory"
    fake_memory.mkdir(parents=True)
    (fake_memory / "MEMORY.md").write_text("- [T](t.md) — hook\n", encoding="utf-8")

    before = snapshot_state(fake_home, fake_memory)
    proc = _explicit_env_writer(_APPEND_SCRIPT, str(fake_memory / "zz-drill.md"),
                                "drill\n")
    assert proc.returncode == 0, proc.stderr
    changes = diff_states(before, snapshot_state(fake_home, fake_memory), fake_home)
    assert changes == ["~/.claude/projects/x/memory/zz-drill.md was created"], changes

    # A read of the same directory moves nothing.
    before = snapshot_state(fake_home, fake_memory)
    (fake_memory / "MEMORY.md").read_bytes()
    assert diff_states(before, snapshot_state(fake_home, fake_memory), fake_home) == []


def test_the_watch_names_the_file_without_printing_any_of_it(tmp_path):
    fake_home = tmp_path / "home"
    cfg = fake_home / ".cursor" / "mcp.json"
    cfg.parent.mkdir(parents=True)
    cfg.write_text('{"token": "SUPER-SECRET-VALUE"}\n', encoding="utf-8")
    before = snapshot_state(fake_home, None)
    cfg.write_text('{"token": "SUPER-SECRET-VALUE", "x": 1}\n', encoding="utf-8")
    changes = diff_states(before, snapshot_state(fake_home, None), fake_home)
    assert changes == ["~/.cursor/mcp.json changed"]
    assert "SUPER-SECRET" not in " ".join(changes)
    assert tilde(str(cfg), fake_home) == "~/.cursor/mcp.json"


def test_a_uid_without_a_password_entry_skips_the_watch_with_a_notice():
    def missing(_uid):
        raise KeyError("uid not found")

    home, notice = resolve_real_home(getpwuid=missing, uid=4242)
    assert home is None
    assert "watch skipped" in notice and "sandbox still applies" in notice
    # The sandbox itself does not depend on the lookup.
    assert Path.home() == SANDBOX["sandbox"]


def test_the_forwarded_memory_directory_keeps_validator_check_12_running():
    """Without the forward the sandboxed HOME would degrade check 12 to its
    not-found notice and the memory frontmatter would stop being checked."""
    proc = subprocess.run([sys.executable, str(REPO_ROOT / "core/scripts/validate.py")],
                          capture_output=True, text=True, cwd=REPO_ROOT, timeout=300)
    assert "memory dir not found" not in proc.stdout, proc.stdout
    assert os.environ.get("PERSONAL_OS_MEMORY_DIR")


# ═══ shared: the files the lints walk ════════════════════════════════════════

def _tracked(*pathspecs) -> list[Path]:
    proc = subprocess.run(["git", "ls-files", "-z", "--", *pathspecs],
                          cwd=REPO_ROOT, capture_output=True, timeout=30)
    assert proc.returncode == 0, proc.stderr
    return [REPO_ROOT / p.decode("utf-8")
            for p in proc.stdout.split(b"\0") if p]


def tracked_framework_sources() -> list[Path]:
    """`core/scripts/*.py` (tests excluded — they bound their own spawns at
    the pipe) and `core/mcp/*.py`, one directory level each."""
    wanted = {REPO_ROOT / "core" / "scripts", REPO_ROOT / "core" / "mcp"}
    return [p for p in _tracked("core/scripts", "core/mcp")
            if p.suffix == ".py" and p.parent in wanted]


def tracked_test_modules() -> list[Path]:
    return [p for p in _tracked("core/scripts/tests") if p.name.startswith("test_")
            and p.suffix == ".py"]


# ═══ spawn lint (R12 / RW-2026-09-12-8) ══════════════════════════════════════

SYNC_SPAWNS = frozenset({"run", "call", "check_call", "check_output"})
TIMEOUT_CEILING_SECONDS = 600


def _spawn_aliases(tree: ast.AST) -> tuple[set[str], dict[str, str]]:
    """Names that reach `subprocess`: module aliases (`import subprocess as
    sp`) and direct function aliases (`from subprocess import run as r`)."""
    modules, funcs = set(), {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "subprocess":
                    modules.add(alias.asname or "subprocess")
        elif isinstance(node, ast.ImportFrom) and node.module == "subprocess":
            for alias in node.names:
                if alias.name in SYNC_SPAWNS:
                    funcs[alias.asname or alias.name] = alias.name
    return modules, funcs


def _module_literals(tree: ast.AST) -> dict[str, object]:
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            value = _literal_number(node.value)
            if value is not None:
                out[node.targets[0].id] = value
    return out


def _literal_number(node):
    """A number the lint can judge: a literal, a negated literal, or `None`
    (reported as the sentinel string 'None'). Anything else is trusted."""
    if isinstance(node, ast.Constant):
        if node.value is None:
            return "None"
        if isinstance(node.value, bool):
            return None
        if isinstance(node.value, (int, float)):
            return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        inner = _literal_number(node.operand)
        return -inner if isinstance(inner, (int, float)) else None
    return None


def _spawn_label(func, modules, funcs) -> str | None:
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) \
            and func.value.id in modules and func.attr in SYNC_SPAWNS:
        return f"subprocess.{func.attr}"
    if isinstance(func, ast.Name) and func.id in funcs:
        return f"subprocess.{funcs[func.id]}"
    return None


def spawn_lint_findings(paths) -> list[tuple[str, int, str, str]]:
    """(file, line, call, reason) for every sync `subprocess` call whose
    timeout is missing or unusable. `Popen` is a documented gap: its bound
    lives on the pipe handling, not on a keyword."""
    findings = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        modules, funcs = _spawn_aliases(tree)
        constants = _module_literals(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            label = _spawn_label(node.func, modules, funcs)
            if label is None:
                continue
            keywords = {kw.arg: kw.value for kw in node.keywords}
            if None in keywords:          # **options — the shape is not visible
                continue
            if "timeout" not in keywords:
                findings.append((path.name, node.lineno, label, "no timeout"))
                continue
            value = keywords["timeout"]
            if isinstance(value, ast.Name):
                value = constants.get(value.id)
                judged = value if value is not None else "trusted"
            else:
                judged = _literal_number(value)
                judged = "trusted" if judged is None else judged
            if judged == "trusted":
                continue
            if judged == "None":
                findings.append((path.name, node.lineno, label, "timeout=None"))
            elif judged == 0:
                findings.append((path.name, node.lineno, label, "timeout=0"))
            elif judged < 0:
                findings.append((path.name, node.lineno, label, "negative timeout"))
            elif judged > TIMEOUT_CEILING_SECONDS:
                findings.append((path.name, node.lineno, label,
                                 f"timeout above the {TIMEOUT_CEILING_SECONDS}s ceiling"))
    return sorted(findings)


SPAWN_FIXTURE = r'''
import subprocess
from subprocess import run as run_alias

T_ZERO = 0
T_OK = 10

def missing():
    subprocess.run(["x"])  # FLAG no timeout

def bounded():
    subprocess.run(["x"], timeout=10)

def zero():
    subprocess.check_output(["x"], timeout=0)  # FLAG timeout=0

def none():
    subprocess.call(["x"], timeout=None)  # FLAG timeout=None

def named_zero():
    subprocess.check_call(["x"], timeout=T_ZERO)  # FLAG timeout=0

def named_ok():
    subprocess.run(["x"], timeout=T_OK)

def popen_gap():
    subprocess.Popen(["x"], stdout=subprocess.PIPE)

def aliased():
    run_alias(["x"])  # FLAG no timeout

def negative():
    subprocess.run(["x"], timeout=-1)  # FLAG negative timeout

def over_ceiling():
    subprocess.run(["x"], timeout=6000)  # FLAG ceiling

def splatted(opts):
    subprocess.run(["x"], **opts)

def computed(budget):
    subprocess.run(["x"], timeout=budget)
'''


def _marked_lines(source: str) -> set[int]:
    return {n for n, line in enumerate(source.splitlines(), 1) if "# FLAG" in line}


def test_spawn_lint_flags_every_unbounded_shape(tmp_path):
    mod = tmp_path / "fixture_spawns.py"
    mod.write_text(SPAWN_FIXTURE, encoding="utf-8")
    findings = spawn_lint_findings([mod])
    assert {line for _, line, _, _ in findings} == _marked_lines(SPAWN_FIXTURE)
    reasons = {line: reason for _, line, _, reason in findings}
    assert set(reasons.values()) == {"no timeout", "timeout=0", "timeout=None",
                                     "negative timeout",
                                     f"timeout above the {TIMEOUT_CEILING_SECONDS}s ceiling"}


def test_framework_sources_spawn_nothing_unbounded():
    sources = tracked_framework_sources()
    assert sources, "the tracked source list is empty — the lint would pass vacuously"
    findings = spawn_lint_findings(sources)
    assert findings == [], "\n".join(f"{f}:{ln}: {call} — {why}"
                                     for f, ln, call, why in findings)


# ═══ source-grep lint (R12 / RW-2026-09-12-13) ═══════════════════════════════

TRACKED_PREFIXES = (".claude/skills", ".claude/agents", ".claude/commands",
                    ".claude/hooks", "core/scripts")
TEXT_SEARCH_METHODS = frozenset({"index", "find", "startswith", "endswith",
                                 "count", "split"})
RE_SEARCH_FUNCS = frozenset({"search", "match", "findall"})

# (file, function, reason). Two entries by design; both are parses of a
# committed artifact's own syntax, which cannot be observed any other way.
GREP_ALLOW = (
    ("test_validate_checks.py", "_guard_case_literals",
     "parses the guard's bash case block so the parity assertion tracks the "
     "list on disk instead of a copy of it"),
    ("test_report_only_guard.py", "_doc_json_block",
     "extracts the fenced JSON wiring block from the hook doc and asserts the "
     "parsed structure, not the prose around it"),
)
GREP_ALLOW_CEILING = 2


def _opaque_names(func) -> set[str]:
    """Names whose value the lint must never resolve: parameters and fixtures,
    loop variables, `with ... as` targets, and anything assigned more than
    once."""
    names, assigned = set(), {}
    for node in ast.walk(func):
        if isinstance(node, ast.arguments):
            for arg in [*node.posonlyargs, *node.args, *node.kwonlyargs]:
                names.add(arg.arg)
            for extra in (node.vararg, node.kwarg):
                if extra:
                    names.add(extra.arg)
        elif isinstance(node, (ast.For, ast.AsyncFor)) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
        elif isinstance(node, ast.withitem) and isinstance(node.optional_vars, ast.Name):
            names.add(node.optional_vars.id)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned[target.id] = assigned.get(target.id, 0) + 1
    names |= {n for n, count in assigned.items() if count > 1}
    return names


def _single_assignments(func, opaque) -> dict[str, ast.AST]:
    out = {}
    for node in ast.walk(func):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id not in opaque:
            out[node.targets[0].id] = node.value
    return out


def _module_names(tree) -> dict[str, ast.AST | None]:
    """Module-level bindings. A value of `None` marks an import or an
    expression the lint does not resolve: still a module-level root, so it is
    a repository path rather than a fixture."""
    out: dict[str, ast.AST | None] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    out[target.id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            out[node.target.id] = node.value
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                out[alias.asname or alias.name.split(".")[0]] = None
    return out


def _segment(node) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return "*"


def _path_segments(node, opaque, locals_, module_names, depth=0) -> list[str] | None:
    """The literal segments of a `/` path chain, or None when the base is not
    a module-level name — a `tmp_path` chain, a fixture, or a parameter."""
    if depth > 8:
        return None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        base = _path_segments(node.left, opaque, locals_, module_names, depth + 1)
        return None if base is None else [*base, _segment(node.right)]
    if isinstance(node, ast.Name):
        if node.id in opaque:
            return None
        if node.id in locals_:
            return _path_segments(locals_[node.id], opaque, locals_, module_names, depth + 1)
        if node.id in module_names:
            value = module_names[node.id]
            if value is None:
                return []
            resolved = _path_segments(value, opaque, locals_, module_names, depth + 1)
            return [] if resolved is None else resolved
    return None


def _is_tracked(segments: list[str]) -> bool:
    joined = "/".join(s for s in segments if s)
    return any(joined.startswith(prefix) for prefix in TRACKED_PREFIXES)


def _read_path_expr(value):
    """The path expression of `<path>.read_text(...)` or `open(<path>).read()`."""
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute):
        if value.func.attr == "read_text":
            return value.func.value
        inner = value.func.value
        if value.func.attr == "read" and isinstance(inner, ast.Call) \
                and isinstance(inner.func, ast.Name) and inner.func.id == "open" and inner.args:
            return inner.args[0]
    return None


def _searched_line(func, names: set[str]) -> int | None:
    for node in ast.walk(func):
        if isinstance(node, ast.Compare):
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, (ast.In, ast.NotIn)) and isinstance(comparator, ast.Name) \
                        and comparator.id in names:
                    return node.lineno
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            subject = node.func.value
            if node.func.attr in TEXT_SEARCH_METHODS and isinstance(subject, ast.Name) \
                    and subject.id in names:
                return node.lineno
            if node.func.attr in RE_SEARCH_FUNCS and isinstance(subject, ast.Name) \
                    and subject.id == "re" \
                    and any(isinstance(a, ast.Name) and a.id in names for a in node.args):
                return node.lineno
    return None


def _outermost_functions(tree) -> list[ast.AST]:
    found = []

    def visit(body):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                found.append(node)
            elif isinstance(node, ast.ClassDef):
                visit(node.body)

    visit(tree.body)
    return found


def grep_lint_findings(paths) -> list[tuple[str, str, int]]:
    """(file, function, line) for every function that reads a committed
    skill, agent, command, hook, or script as text and then searches that
    text. The search may sit anywhere in the function: both sanctioned sites
    read in a helper and assert elsewhere."""
    findings = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        module_names = _module_names(tree)
        for func in _outermost_functions(tree):
            opaque = _opaque_names(func)
            locals_ = _single_assignments(func, opaque)
            tracked = set()
            for node in ast.walk(func):
                if not (isinstance(node, ast.Assign) and len(node.targets) == 1
                        and isinstance(node.targets[0], ast.Name)):
                    continue
                path_expr = _read_path_expr(node.value)
                if path_expr is None:
                    continue
                segments = _path_segments(path_expr, opaque, locals_, module_names)
                if segments is not None and _is_tracked(segments):
                    tracked.add(node.targets[0].id)
            if not tracked:
                continue
            line = _searched_line(func, tracked)
            if line is not None:
                findings.append((path.name, func.name, line))
    return sorted(findings)


def stale_allow_entries(findings, allow) -> list[tuple[str, str]]:
    """An allow-list entry whose function no longer greps. The list ratchets
    one way: a site that stops needing its exemption loses it."""
    flagged = {(f, fn) for f, fn, _ in findings}
    return [(entry[0], entry[1]) for entry in allow if (entry[0], entry[1]) not in flagged]


def allow_list_within_ceiling(allow, ceiling: int) -> bool:
    return len(allow) == ceiling


GREP_FIXTURE = r'''
import json
import re
from conftest import REPO_ROOT

DOC = REPO_ROOT / ".claude" / "skills" / "demo" / "SKILL.md"

def flagged_membership():
    text = (REPO_ROOT / ".claude" / "skills" / "x" / "SKILL.md").read_text(encoding="utf-8")
    assert "foo" in text

def flagged_local_chain():
    guard = REPO_ROOT / ".claude" / "hooks" / "x.sh"
    body = guard.read_text(encoding="utf-8")
    return body.index("case")

def flagged_module_constant():
    text = DOC.read_text(encoding="utf-8")
    return re.search("name:", text)

def flagged_open_read():
    with_open = open(REPO_ROOT / "core" / "scripts" / "validate.py").read()
    return with_open.startswith("#!")

def clean_tmp_path(tmp_path):
    text = (tmp_path / "SKILL.md").read_text(encoding="utf-8")
    assert "foo" in text

def clean_fixture_root(fake_root):
    text = (fake_root / ".claude" / "skills" / "demo" / "SKILL.md").read_text()
    assert "foo" in text

def clean_json_parse():
    data = json.loads(DOC.read_text(encoding="utf-8"))
    assert data["k"] == 1

def clean_exact_equality():
    text = DOC.read_text(encoding="utf-8")
    assert text == "exact\n"

def clean_read_without_search():
    src = (REPO_ROOT / "core" / "scripts" / "validate.py").read_text(encoding="utf-8")
    return len(src)

def clean_untracked_prefix():
    text = (REPO_ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    assert "foo" in text
'''


def test_grep_lint_flags_source_greps_and_leaves_data_reads_alone(tmp_path):
    mod = tmp_path / "test_fixture_greps.py"
    mod.write_text(GREP_FIXTURE, encoding="utf-8")
    flagged = {fn for _, fn, _ in grep_lint_findings([mod])}
    expected = {"flagged_membership", "flagged_local_chain",
                "flagged_module_constant", "flagged_open_read"}
    assert flagged == expected


def test_grep_lint_reports_exactly_the_allow_listed_sites():
    modules = tracked_test_modules()
    assert modules, "the tracked test list is empty — the lint would pass vacuously"
    findings = grep_lint_findings(modules)
    assert {(f, fn) for f, fn, _ in findings} == {(e[0], e[1]) for e in GREP_ALLOW}, findings
    assert stale_allow_entries(findings, GREP_ALLOW) == []


def test_stale_allow_entries_are_reported():
    findings = [("test_validate_checks.py", "_guard_case_literals", 12)]
    allow = (GREP_ALLOW[0], ("test_report_only_guard.py", "_doc_json_block", "r"))
    assert stale_allow_entries(findings, allow) == [("test_report_only_guard.py",
                                                     "_doc_json_block")]


def test_allow_list_length_equals_its_ceiling():
    """Raising the ceiling is a visible diff line, and `core/CODING_STANDARDS.md`
    requires the PR that raises it to say why the test cannot be behavioural."""
    assert allow_list_within_ceiling(GREP_ALLOW, GREP_ALLOW_CEILING)
    third = ("test_new.py", "_reads_a_skill", "no reason given")
    assert not allow_list_within_ceiling((*GREP_ALLOW, third), GREP_ALLOW_CEILING)
