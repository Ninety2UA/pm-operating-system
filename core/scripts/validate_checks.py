#!/usr/bin/env python3
"""U14 enforcement checks as pure functions over a root path (or text
inputs), so each is fixture-testable in isolation and wired into the
sequential validator against the real repo. Fail-class checks return a
list of blocking problems; warn-class return non-blocking notices.

Home of tests: core/scripts/tests/test_validate_checks.py.
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import date
from pathlib import Path

# ── Canonical model roster — declared ONCE (KTD-1 / R2) ──────────────────────
CURRENT_MODEL_ALIASES = {
    "haiku", "sonnet", "opus", "fable", "inherit",
    "default", "best", "opusplan", "sonnet[1m]", "opus[1m]",
}
CURRENT_MODEL_IDS = {
    # current defaults (verified 2026-09-11 against the deprecations table):
    # Fable 5.1 and Opus 5 are the default Fable/Opus models; Fable 5 and
    # Opus 4.8 remain Active
    "claude-fable-5-1", "claude-opus-5",
    "claude-fable-5", "claude-sonnet-5", "claude-opus-4-8",
    "claude-haiku-4-5-20251001",
    # legacy-but-Active per the deprecations table (docs/capabilities.md)
    "claude-opus-4-7", "claude-opus-4-6", "claude-opus-4-5",
    "claude-opus-4-5-20251101", "claude-sonnet-4-6",
    "claude-sonnet-4-5-20250929",
    # dateless convenience aliases for Active models (cap-models: dateless
    # is a valid alias pre-4.6 and the canonical ID for 4.6+)
    "claude-haiku-4-5", "claude-sonnet-4-5",
}
# Model-ID SHAPE: `claude-` then eventually a digit (distinguishes real IDs
# like claude-opus-4-8 from non-model tokens like claude-code). The trailing
# class excludes a final `.`/`-` and does not span a version separator, so a
# current ID at a sentence end ("…claude-opus-4-8.") or a longer suffix
# ("claude-opus-4-8-20260101") is captured exactly, not mangled into a
# false-positive. `[a-z]+` segments must not themselves end in a digit run
# that belongs to the id.
MODEL_ID_RE = re.compile(r"claude-(?:[a-z]+-)*\d[a-z0-9]*(?:-[a-z0-9]+)*")

# Frontmatter-bearing framework files (tiering scans these).
_FRONTMATTER_GLOBS = (
    ".claude/skills/*/SKILL.md",
    ".claude/agents/*.md",
    ".claude/commands/*.md",
)
# All framework content, incl. references/ (roster scans these — a retired
# ID in a reference file is just as stale).
_CONTENT_GLOBS = _FRONTMATTER_GLOBS + (".claude/skills/**/references/**/*.md",)


def _frontmatter_md(root: Path):
    for g in _FRONTMATTER_GLOBS:
        yield from root.glob(g)


def _content_md(root: Path):
    seen = set()
    for g in _CONTENT_GLOBS:
        for f in root.glob(g):
            if f not in seen:
                seen.add(f)
                yield f


# ── BOM check (fail): Claude Code silently ignores a skill/agent/command file
# whose .md starts with a UTF-8 byte-order mark (fixed upstream in v2.1.239
# as a diagnosis; the file still loads wrong on older builds). Check 1 already
# hard-fails such a file as "no frontmatter fence"; this names the cause.
_BOM = b"\xef\xbb\xbf"
_BOM_EXTRA = ("AGENTS.md", "CLAUDE.md", "docs/*.md")


def check_bom(root: Path | str) -> list[str]:
    root = Path(root)
    files = list(_frontmatter_md(root))
    for g in _BOM_EXTRA:
        files.extend(root.glob(g))
    out = []
    for f in sorted(set(files)):
        try:
            head = f.read_bytes()[:3]
        except OSError:
            continue
        if head == _BOM:
            out.append(f"{f.relative_to(root)}: starts with a UTF-8 BOM "
                       "(Claude Code ignores such files)")
    return out


def check_model_roster(root: Path | str) -> list[str]:
    """Fail any framework markdown file referencing a model ID outside the
    current roster (i.e. a retired ID). Aliases and non-model `claude-*`
    tokens are ignored by construction."""
    root = Path(root)
    fails = []
    for f in sorted(_content_md(root)):
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in MODEL_ID_RE.findall(line):
                if m not in CURRENT_MODEL_IDS:
                    fails.append(f"{f.relative_to(root)}:{i}: retired/unknown "
                                 f"model ID `{m}`")
    return fails


# ── tiering presence (R2 enforcement) ────────────────────────────────────────
def _top_level_key(text: str, key: str):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    fm = text[:end] if end != -1 else text
    m = re.search(rf"(?m)^{re.escape(key)}:\s*(.+)$", fm)
    return m.group(1).strip() if m else None


def check_tiering_presence(root: Path | str) -> list[str]:
    """Every skill/agent/command carries a deliberate `model:` assignment
    (a pin or explicit `inherit`). The two watcher skills, pinned at
    creation, pass."""
    root = Path(root)
    fails = []
    for f in sorted(_frontmatter_md(root)):
        model = _top_level_key(f.read_text(encoding="utf-8"), "model")
        if not model:
            fails.append(f"{f.relative_to(root)}: no `model:` assignment "
                         f"(pin or explicit `inherit` required)")
    return fails


# ── degradation coverage join (R4 / U14) ─────────────────────────────────────
def _table_rows(text: str):
    """Yield lists-of-cells for every pipe-table data row (skips separators)."""
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):  # separator row
            continue
        yield cells


def _claude_native_ids(manifest_text: str) -> set[str]:
    ids = set()
    for cells in _table_rows(manifest_text):
        if len(cells) >= 3 and cells[2] == "claude-native":
            ids.add(cells[0])
    return ids


# A capability needs a degradation mechanism only when it is adopted INTO a
# generated body (skill/agent/command). Rows targeting non-generated
# surfaces (hooks, setup.sh, core/, docs/) never reach the portable tree.
_GENERATED_TARGET = re.compile(r"\.claude/(?:skills|agents|commands)/")


def check_degradation_coverage(manifest_text: str, matrix_text: str) -> list[str]:
    """The three-way join: an adoption-matrix row tagged adopt(-partial),
    whose id is a manifest claude-native capability AND whose target lands
    in a generated body, must name a degradation mechanism unless it is
    explicitly portable prose."""
    native = _claude_native_ids(manifest_text)
    fails = []
    for cells in _table_rows(matrix_text):
        if len(cells) < 4:
            continue
        cid, verdict = cells[0], cells[1]
        targets = cells[3]
        if verdict not in ("adopt", "adopt-partial"):
            continue
        if cid not in native:
            continue
        if not _GENERATED_TARGET.search(targets):
            continue  # not adopted into a generated body — no fence needed
        # A row missing the degradation column entirely (truncated to <5
        # cells) is a violation, not a skip — that is exactly the omission
        # the check exists to catch.
        degradation = cells[4] if len(cells) >= 5 else ""
        deg = degradation.lower()
        # Require an affirmative "yes" mechanism or an explicit, unqualified
        # "portable prose" exemption. A negated form ("not portable prose")
        # must not pass.
        exempt_portable = ("portable prose" in deg
                           and "not portable prose" not in deg
                           and "n't portable prose" not in deg)
        if deg.startswith("yes") or exempt_portable:
            continue
        fails.append(f"degradation-coverage: adopt row `{cid}` (claude-native, "
                     f"generated target) names no degradation mechanism: "
                     f"'{degradation or '<missing column>'}'")
    return fails


# ── tracked-artifact secret-scan (KTD-13, blocking) ──────────────────────────
_SECRET_PATTERNS = (
    (re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"), "private key header"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key id"),
    (re.compile(r"\bASIA[0-9A-Z]{16}\b"), "AWS temp key id"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "GitHub token"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "GitHub fine-grained PAT"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "Slack token"),
    # Anthropic and OpenAI-project keys carry hyphens right after the prefix,
    # so match the broader shape; the generic sk- backstop follows.
    (re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"), "Anthropic API key"),
    (re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,}"), "OpenAI project key"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "API secret key"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{30,}"), "Google API key"),
    (re.compile(r"\bya29\.[0-9A-Za-z_-]{20,}"), "Google OAuth token"),
    (re.compile(r"\bglpat-[0-9A-Za-z_-]{20,}"), "GitLab PAT"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
     "JWT"),
    # Credential assignments — quoted OR unquoted value with enough entropy.
    (re.compile(r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token"
                r"|auth[_-]?token|client[_-]?secret)\b\s*[:=]\s*"
                r"(?:['\"][^'\"]{6,}['\"]|[^\s'\"#]{8,})"),
     "credential assignment"),
)
_SECRET_SCAN_ROOTS = ("docs/ledger", "docs/capabilities.md", "core/watchers")
_ALLOW_ESCAPE = "# secret-scan: allow"


def check_tracked_secret_scan(root: Path | str) -> list[str]:
    """Blocking scan of portfolio-public tracked artifacts for
    credential-shaped strings. Git SHAs (40-char hex) are not matched by
    any pattern; an inline `# secret-scan: allow` exempts a line."""
    root = Path(root)
    targets: list[Path] = []
    for rel in _SECRET_SCAN_ROOTS:
        p = root / rel
        if p.is_dir():
            targets += [f for f in p.rglob("*") if f.is_file()]
        elif p.is_file():
            targets.append(p)
    fails = []
    for f in sorted(targets):
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if _ALLOW_ESCAPE in line:
                continue
            for pat, label in _SECRET_PATTERNS:
                if pat.search(line):
                    fails.append(f"{f.relative_to(root)}:{i}: possible {label} "
                                 f"in tracked artifact")
                    break
    return fails


# ── guard-wiring (KTD-5) ─────────────────────────────────────────────────────
def check_guard_wiring(root: Path | str) -> list[str]:
    """Wiring is NEVER required — the committed-but-unwired guard (and a
    skip-adopter with no guard at all) always passes. But when
    settings.local.json wires any command hook, that hook must resolve to an
    existing, executable script, whatever it points at."""
    root = Path(root)
    local = root / ".claude" / "settings.local.json"
    if not local.exists():
        return []  # committed-and-unwired: the shipped state, always green
    try:
        settings = json.loads(local.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []  # malformed local settings is a separate concern, not ours
    if not isinstance(settings, dict):
        return []
    import os
    fails = []
    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        return []
    # Any command hook wired locally must resolve to an existing, executable
    # script — this subsumes the guard and never requires it to be wired.
    for _event, configs in hooks.items():
        if not isinstance(configs, list):
            continue
        for cfg in configs:
            if not isinstance(cfg, dict):
                continue
            for hk in cfg.get("hooks", []) or []:
                if not isinstance(hk, dict) or hk.get("type") != "command":
                    continue
                cmd = hk.get("command", "")
                if not isinstance(cmd, str):
                    continue
                m = re.search(r"\$CLAUDE_PROJECT_DIR/(\S+)", cmd)
                if not m:
                    continue
                # Strip surrounding quotes the command may carry around the
                # path (the style Claude Code's own docs use).
                rel = m.group(1).strip('"\'')
                target = root / rel
                if not target.exists():
                    fails.append(f"hook wired in settings.local.json to a "
                                 f"missing path: {cmd}")
                elif not os.access(target, os.X_OK):
                    fails.append(f"hook wired but not executable: {target.name}")
    return fails


# ── warn-class ───────────────────────────────────────────────────────────────
def _git_sha_exists(root: Path, sha: str) -> bool:
    try:
        r = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                           cwd=root, capture_output=True, timeout=10)
        return r.returncode == 0
    except Exception:
        return True  # git unavailable → don't warn spuriously


def check_ledger_links(root: Path | str) -> list[str]:
    """Warn on an `Adopted-in` provenance SHA that does not resolve in git
    (a dangling implementing-commit link). Legitimately-deferred `—` rows
    do not warn."""
    root = Path(root)
    warns = []
    ledger_dir = root / "docs" / "ledger"
    if not ledger_dir.is_dir():
        return warns
    sha_re = re.compile(r"`([0-9a-f]{7,40})`")
    for f in sorted(ledger_dir.glob("*.md")):
        for cells in _table_rows(f.read_text(encoding="utf-8")):
            if not cells or cells[-1] == "—":
                continue
            m = sha_re.fullmatch(cells[-1])
            if m and not _git_sha_exists(root, m.group(1)):
                warns.append(f"{f.relative_to(root)}: adopt line `{cells[0]}` "
                             f"links dangling commit `{m.group(1)}`")
    return warns


def check_live_registry(root: Path | str) -> list[str]:
    """Warn when a present live registry fails schema validation."""
    root = Path(root)
    reg = root / "knowledge" / "currency" / "repo-registry.json"
    if not reg.exists():
        return []
    import sys
    sys.path.insert(0, str(root / "core" / "scripts"))
    import currency
    try:
        data = json.loads(reg.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return [f"live registry unreadable: {e}"]
    return [f"live registry: {e}" for e in currency.validate_registry(data)]


def check_currency_lock_ignored(root: Path | str) -> list[str]:
    """Warn if the currency lock is not gitignored (check 35 covers only
    .claude/*.lock — this lock lives under knowledge/currency/)."""
    root = Path(root)
    lock = "knowledge/currency/currency.lock"
    try:
        r = subprocess.run(["git", "check-ignore", lock], cwd=root,
                           capture_output=True, timeout=10)
        if r.returncode != 0:
            return [f"{lock} is not gitignored (KTD-6 lock hygiene)"]
    except Exception:
        pass
    return []


# ── guard-wiring timeout notice (warn, KTD6) ─────────────────────────────────
_GUARD_TIMEOUT_FLOOR = 600  # the platform default for a PreToolUse command hook


def _local_command_hooks(root: Path):
    """Yield the command-hook dicts wired in .claude/settings.local.json;
    nothing when the file is absent or malformed (same tolerance as
    check_guard_wiring, which stays the fail-class owner of wiring)."""
    local = root / ".claude" / "settings.local.json"
    if not local.exists():
        return
    try:
        settings = json.loads(local.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    hooks = settings.get("hooks") if isinstance(settings, dict) else None
    if not isinstance(hooks, dict):
        return
    for configs in hooks.values():
        if not isinstance(configs, list):
            continue
        for cfg in configs:
            if not isinstance(cfg, dict):
                continue
            for hk in cfg.get("hooks", []) or []:
                if isinstance(hk, dict) and hk.get("type") == "command":
                    yield hk


def check_guard_wiring_timeout(root: Path | str) -> list[str]:
    """Warn when the wired report-only guard declares an explicit `timeout`
    below the platform default. A host-side hook timeout is fail-open, so a
    lower value narrows the window in which the guard's own stall budget
    can deny; the documented wiring block carries no timeout (KTD6).
    Absent or >= 600 is silent."""
    root = Path(root)
    warns = []
    for hk in _local_command_hooks(root):
        cmd = hk.get("command", "")
        if not isinstance(cmd, str) or "report-only-guard.sh" not in cmd:
            continue
        t = hk.get("timeout")
        if isinstance(t, bool) or not isinstance(t, (int, float)):
            continue
        if t < _GUARD_TIMEOUT_FLOOR:
            warns.append(f"settings.local.json wires the report-only guard "
                         f"with timeout {t:g} < {_GUARD_TIMEOUT_FLOOR} — a "
                         f"host-side hook timeout is fail-open; drop it so "
                         f"the platform default applies and the guard's own "
                         f"stall budget is what denies")
    return warns


# ── secret-bypass lint (warn, R10) ───────────────────────────────────────────
# In prose a path token ends at whitespace, a quote or backtick, or sentence
# punctuation. A following word char, hyphen, slash, or dotted suffix means
# the glob has not matched the whole token (bash `*.key` never matches
# `server.key.bak`); a preceding word char, hyphen, dot, or slash means an
# unanchored literal like `/etc/shadow` is only a tail of a longer token.
_TOK_END = r"(?![\w\-/]|\.\w)"
_TOK_START = r"(?<![\w\-./])"


def _credential_glob_re(glob: str) -> re.Pattern:
    """Translate one bash case-pattern literal into a prose regex: a leading
    `*` is any prefix (no left anchor), a trailing `*` any suffix, an
    interior `*` any run of non-space characters. `.env` is the one
    deliberate tightening — it keeps its leading dot behind a non-word
    lookbehind so `process.env` and "env var" never match, and the
    `.example|.sample|.template|.dist` suffixes stay readable."""
    if glob == "*.env":
        return re.compile(r"(?<!\w)\.env" + _TOK_END)
    if glob == "*.env.*":
        return re.compile(r"(?<!\w)\.env\.(?!(?:example|sample|template|dist)\b)\w")
    body = r"\S*?".join(re.escape(p) for p in glob.split("*") if p)
    left = "" if glob.startswith("*") else _TOK_START
    right = "" if glob.endswith("*") else _TOK_END
    return re.compile(left + body + right)


# Declared ONCE: one entry per literal of the guard's `credential_shaped()`
# case block (.claude/hooks/report-only-guard.sh), in the guard's order. The
# parity test parses that block from disk and asserts the key set matches.
# Keys are the bash globs — the only thing a message ever echoes.
CREDENTIAL_PATH_PATTERNS: dict[str, re.Pattern] = {
    glob: _credential_glob_re(glob) for glob in (
        "*/.ssh", "*/.ssh/*", "*id_rsa*", "*id_ed25519*", "*id_ecdsa*",
        "*id_dsa*",
        "*/.aws", "*/.aws/*", "*/.config/gcloud", "*/.config/gcloud/*",
        "*/.config/gh", "*/.config/gh/*",
        "*/.gnupg", "*/.gnupg/*", "*/.netrc", "*/.pgpass", "*.htpasswd",
        "*/.docker/config.json", "*/.kube/config", "*/.kube",
        "*/.zsh_history", "*/.bash_history", "*/.python_history",
        "*/.node_repl_history",
        "*/.git-credentials", "*/.npmrc", "*/.pypirc",
        "/etc/shadow", "/etc/gshadow", "/etc/master.passwd",
        "*.tfstate", "*.tfstate.*",
        "*.pem", "*.key", "*.p12", "*.pfx", "*.gpg", "*.asc", "*.env",
        "*.env.*",
        "*client_secret*",
        "*secret*.json", "*secret*.txt", "*secret*.yaml", "*secret*.yml",
        "*secret*.env",
        "*token*.json", "*token*.txt", "*-token", "*_token",
        "*password*.json", "*password*.txt", "*credential*.json",
        "*apikey*", "*api_key*",
    )
}
_READ_VERB_RE = re.compile(
    r"\b(read|cat|grep|glob|head|tail|open|print|dump|echo|source|view)\b",
    re.IGNORECASE)
_NEGATION_RE = re.compile(r"^(?:never|not|don['’]t|no)$", re.IGNORECASE)
_READ_WINDOW = 60        # max chars between the verb's end and the path
_NEGATION_TOKENS = 3     # tokens immediately before the verb that can negate it
_BYPASS_SCAN_GLOBS = (".claude/skills/**/*.md", ".claude/agents/*.md",
                      ".claude/commands/*.md")
_BYPASS_SCAN_FILES = ("AGENTS.md", "CLAUDE.md")
_LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_HEADING_RE = re.compile(r"^\s*#{1,6}\s")
_RULE_RE = re.compile(r"^\s*(?:---|\*\*\*|___)\s*$")
_FENCE_RE = re.compile(r"^\s*(?:```|~~~)")


def _prose_items(text: str):
    """Split markdown into (first_line, text) scan units: a list item with
    its wrapped continuation lines, a paragraph, a heading, or — inside a
    code fence — each line on its own (a fenced `grep .env` is a command,
    not prose, and a neighbouring comment does not negate it)."""
    items, buf, start, fenced = [], [], 0, False

    def flush():
        if buf:
            items.append((start, " ".join(l.strip() for l in buf)))
        buf.clear()

    for i, line in enumerate(text.splitlines(), 1):
        if _FENCE_RE.match(line):
            flush()
            fenced = not fenced
            continue
        if fenced:
            if line.strip():
                items.append((i, line.strip()))
            continue
        if not line.strip() or _RULE_RE.match(line):
            flush()
            continue
        if _HEADING_RE.match(line):
            flush()
            items.append((i, line.strip()))
            continue
        if _LIST_ITEM_RE.match(line):
            flush()
            start = i
        elif not buf:
            start = i
        buf.append(line)
    flush()
    return items


def _negated(text: str, verb_start: int) -> bool:
    tokens = text[:verb_start].split()[-_NEGATION_TOKENS:]
    return any(_NEGATION_RE.match(t.strip("*_`\"'(),.;:!?")) for t in tokens)


def check_secret_bypass_instructions(root: Path | str) -> list[str]:
    """Warn on catalog prose that tells an agent to read a credential-shaped
    path — the report-only guard denies exactly these reads at marker time,
    so the instruction is a bypass the guard cannot honour. Scans per
    paragraph / list item (prose wraps); an imperative read verb within
    60 characters before a credential path flags unless a negation sits
    within three tokens before the verb or the item carries
    `# secret-scan: allow`. Messages name the glob label, never the text."""
    root = Path(root)
    files = set()
    for g in _BYPASS_SCAN_GLOBS:
        files.update(f for f in root.glob(g) if f.is_file())
    for rel in _BYPASS_SCAN_FILES:
        if (root / rel).is_file():
            files.add(root / rel)
    warns = []
    for f in sorted(files):
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_no, item in _prose_items(text):
            if _ALLOW_ESCAPE in item:
                continue
            verbs = [m for m in _READ_VERB_RE.finditer(item)
                     if not _negated(item, m.start())]
            if not verbs:
                continue
            labels, verb = [], None
            for label, pat in CREDENTIAL_PATH_PATTERNS.items():
                for pm in pat.finditer(item):
                    hit = next((v for v in verbs if v.end() <= pm.start()
                                and pm.start() - v.end() <= _READ_WINDOW), None)
                    if hit:
                        labels.append(label)
                        verb = verb or hit.group(1).lower()
                        break
            if labels:
                warns.append(f"{f.relative_to(root)}:{line_no}: instructs "
                             f"`{verb}` on a credential-shaped path "
                             f"({', '.join(labels)}) — the guard denies that "
                             f"read; negate it, switch to printenv, or mark "
                             f"`# secret-scan: allow`")
    return warns


# ── backup coverage (warn, R11) ──────────────────────────────────────────────
def _git_stdout(root: Path, *args: str):
    """stdout of a git command against `root`, or None when git is
    unavailable, `root` is not a repository, or the command fails."""
    try:
        r = subprocess.run(["git", "-C", str(root), *args],
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def check_backup_coverage(root: Path | str) -> list[str]:
    """Warn when the framework cannot be recreated from its remote: no
    `origin` remote, or `main` tracks an upstream and is ahead of it.
    Silent when git is unavailable, outside a repository, or when `main`
    has no upstream (nothing to compare against)."""
    root = Path(root)
    remotes = _git_stdout(root, "remote")
    if remotes is None:
        return []
    warns = []
    if "origin" not in remotes.split():
        warns.append("no `origin` remote — the framework cannot be recreated "
                     "from a remote; add one and push `main`")
    upstream = _git_stdout(root, "rev-parse", "--abbrev-ref",
                           "--symbolic-full-name", "main@{upstream}")
    if not upstream:
        return warns
    ahead = _git_stdout(root, "rev-list", "--count", f"{upstream}..main")
    if ahead and ahead.isdigit() and int(ahead) > 0:
        warns.append(f"`main` is {ahead} commit(s) ahead of `{upstream}` — "
                     f"push so the remote holds a full copy")
    return warns


# ── staleness report (R17, warn-only, --staleness-report mode) ───────────────
def staleness_report(root: Path | str) -> list[str]:
    """List project specs referencing retired model IDs — a flag, never a
    failure (projects/ is gitignored, out of scope for rewriting)."""
    root = Path(root)
    flags = []
    projects = root / "projects"
    if not projects.is_dir():
        return flags
    for spec in sorted(projects.glob("*/spec.md")):
        for i, line in enumerate(spec.read_text(encoding="utf-8").splitlines(), 1):
            for m in MODEL_ID_RE.findall(line):
                if m not in CURRENT_MODEL_IDS:
                    flags.append(f"{spec.relative_to(root)}:{i}: retired model "
                                 f"ID `{m}`")
    return flags


# ── staleness report extensions (local mode only, KTD5) ──────────────────────
_WATCHER_MAX_AGE_DAYS = 14
_RATCHET_STEMS = {"active": "activ", "paused": "paus", "archived": "archiv"}
_DATED_LOG_LINE_RE = re.compile(r"^\s*[-*]\s*(?:\*\*)?\d{4}-\d{2}-\d{2}")
_PROGRESS_HEADING_RE = re.compile(r"(?im)^##\s+Progress Log\s*$")


def _currency_module():
    try:
        import currency
    except ImportError:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import currency
    return currency


def watcher_report_staleness(root: Path | str, today: date | None = None,
                             max_age_days: int = _WATCHER_MAX_AGE_DAYS) -> list[str]:
    """Per watcher, flag the newest completed report when it is older than
    `max_age_days` — a watcher that silently stopped firing looks green to
    every point-in-time check. Silent for a watcher with no completed
    report (a first run is not stale). Reads gitignored data: local mode."""
    root = Path(root)
    reports = root / "knowledge" / "currency" / "reports"
    if not reports.is_dir():
        return []
    today = today or date.today()
    currency = _currency_module()
    flags = []
    for wdir in sorted(p for p in reports.iterdir() if p.is_dir()):
        done = currency.completed_reports(wdir)  # oldest → newest
        if not done:
            continue
        newest = done[-1]
        age = (today - date.fromisoformat(newest.stem)).days
        if age > max_age_days:
            flags.append(f"{wdir.name}: newest completed report {newest.name} "
                         f"is {age} days old (threshold {max_age_days})")
    return flags


def _section(text: str, heading_re: re.Pattern) -> str:
    m = heading_re.search(text)
    if not m:
        return ""
    body = text[m.end():]
    nxt = re.search(r"(?m)^##\s", body)
    return body[:nxt.start()] if nxt else body


def project_progress_ratchet(root: Path | str) -> list[str]:
    """Projects whose `project_status` is active/paused/archived but whose
    Progress Log has no dated line recording that transition — the status
    moved without the log ratcheting with it. Best effort: a dated line
    mentioning the status stem counts. Paths only (projects/ is
    gitignored: local mode)."""
    root = Path(root)
    projects = root / "projects"
    if not projects.is_dir():
        return []
    flags = []
    for idea in sorted(projects.glob("*/idea.md")):
        try:
            text = idea.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        status = (_top_level_key(text, "project_status") or "").split("#")[0]
        stem = _RATCHET_STEMS.get(status.strip().lower())
        if not stem:
            continue
        log = _section(text, _PROGRESS_HEADING_RE)
        if not any(_DATED_LOG_LINE_RE.match(l) and stem in l.lower()
                   for l in log.splitlines()):
            flags.append(str(idea.relative_to(root)))
    return flags


def staleness_sections(root: Path | str) -> list[tuple[str, list[str]]]:
    """The local-mode report as (title, flags) sections. Everything here
    reads gitignored data, so none of it is ever a default-run warning."""
    return [
        ("Retired model IDs in project specs", staleness_report(root)),
        (f"Watcher reports older than {_WATCHER_MAX_AGE_DAYS} days",
         watcher_report_staleness(root)),
        ("Projects whose Progress Log never records their status (ratchet)",
         project_progress_ratchet(root)),
    ]


if __name__ == "__main__":
    import sys
    root = Path(__file__).resolve().parents[2]
    if "--staleness-report" in sys.argv:
        for title, flags in staleness_sections(root):
            print(f"{title}: {len(flags) or 'none'}")
            for f in flags:
                print(f"  · {f}")
