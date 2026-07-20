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
from pathlib import Path

# ── Canonical model roster — declared ONCE (KTD-1 / R2) ──────────────────────
CURRENT_MODEL_ALIASES = {
    "haiku", "sonnet", "opus", "fable", "inherit",
    "default", "best", "opusplan", "sonnet[1m]", "opus[1m]",
}
CURRENT_MODEL_IDS = {
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
# like claude-opus-4-8 from non-model tokens like claude-code).
MODEL_ID_RE = re.compile(r"claude-(?:[a-z]+-)*\d[a-z0-9.\-]*")

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
        if len(cells) < 5:
            continue
        cid, verdict, _wave, targets, degradation = cells[:5]
        if verdict not in ("adopt", "adopt-partial"):
            continue
        if cid not in native:
            continue
        if not _GENERATED_TARGET.search(targets):
            continue  # not adopted into a generated body — no fence needed
        deg = degradation.lower()
        if deg.startswith("yes") or "portable prose" in deg:
            continue
        fails.append(f"degradation-coverage: adopt row `{cid}` (claude-native, "
                     f"generated target) names no degradation mechanism: "
                     f"'{degradation}'")
    return fails


# ── tracked-artifact secret-scan (KTD-13, blocking) ──────────────────────────
_SECRET_PATTERNS = (
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key header"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key id"),
    (re.compile(r"\bASIA[0-9A-Z]{16}\b"), "AWS temp key id"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "GitHub token"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "Slack token"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "API secret key"),
    (re.compile(r"(?i)\b(?:password|passwd|secret|api[_-]?key)\b\s*[:=]\s*"
                r"['\"][^'\"]{6,}['\"]"), "inline credential assignment"),
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
    """The committed-but-unwired guard ALWAYS passes (CI/skip-adopter
    state). Wiring is asserted executable/correct only when a
    settings.local.json entry references it; never required."""
    root = Path(root)
    guard = root / ".claude" / "hooks" / "report-only-guard.sh"
    if not guard.exists():
        return []  # nothing to validate; presence is not required here
    local = root / ".claude" / "settings.local.json"
    if not local.exists():
        return []  # committed-and-unwired: the shipped state, always green
    try:
        settings = json.loads(local.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []  # malformed local settings is a separate concern, not ours
    import os
    fails = []
    # Any command hook wired locally must resolve to an existing, executable
    # script — this subsumes the guard and never requires it to be wired.
    for _event, configs in (settings.get("hooks", {}) or {}).items():
        for cfg in configs:
            for hk in cfg.get("hooks", []):
                if hk.get("type") != "command":
                    continue
                cmd = hk.get("command", "")
                m = re.search(r"\$CLAUDE_PROJECT_DIR/(\S+)", cmd)
                if not m:
                    continue
                target = root / m.group(1)
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


if __name__ == "__main__":
    import sys
    root = Path(__file__).resolve().parents[2]
    if "--staleness-report" in sys.argv:
        flags = staleness_report(root)
        if flags:
            print(f"Staleness report — {len(flags)} project-spec model-ID flags:")
            for f in flags:
                print(f"  · {f}")
        else:
            print("Staleness report: no retired model IDs in project specs.")
