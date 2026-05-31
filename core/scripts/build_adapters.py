#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Generate cross-tool Agent Skills adapters from the Claude Code source.

The personal-os system authors its skills, agents, and commands under `.claude/`.
This generator emits a committed `.agents/skills/<name>/SKILL.md` tree (the open
"Agent Skills" standard) read natively by Codex CLI, Antigravity, Cursor, and
other conformant tools. One source of truth (`.claude/`), one generated tree.

Sources (all mapped identically to a skill):
  - .claude/skills/<name>/SKILL.md   (30)
  - .claude/agents/<name>.md          (3)
  - .claude/commands/<name>.md        (1)

The body is lightly neutralized — the SKILL.md format and the `mcp__server__tool`
MCP naming are shared standards, so this removes only genuinely Claude-specific
tokens (the Slack *plugin* name, `$ARGUMENTS`, `$CLAUDE_PROJECT_DIR`,
`AskUserQuestion`, `.claude/skills/...` reference paths).

Usage:
  uv run core/scripts/build_adapters.py            # generate + write .agents/skills
  uv run core/scripts/build_adapters.py --check     # verify no drift / no leftover Claude-isms (exit 1 on issue)
  uv run core/scripts/build_adapters.py --dry-run   # show what would change, write nothing
  uv run core/scripts/build_adapters.py --verbose
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

import yaml

# ── Paths ──────────────────────────────────────────────────────────────────
_env_root = os.environ.get("PERSONAL_OS_ROOT", "").strip()
ROOT = Path(_env_root).resolve() if _env_root else Path(__file__).resolve().parents[2]
SRC_SKILLS = ROOT / ".claude" / "skills"
SRC_AGENTS = ROOT / ".claude" / "agents"
SRC_COMMANDS = ROOT / ".claude" / "commands"

# Generated trees this script owns (repo-relative). Stale-file pruning is scoped
# to these, so unmanaged files are never touched.
MANAGED_BASES = (".agents/skills", ".codex/agents", ".cursor/agents")

# Per-agent traits for native subagent emission (Codex/Cursor). Any agent not
# listed gets the safe default (read/write, foreground).
AGENT_TRAITS = {
    "system-health": {"readonly": True, "background": False, "sandbox": "read-only"},
    "deep-research": {"readonly": False, "background": True, "sandbox": None},
    "batch-evaluator": {"readonly": False, "background": True, "sandbox": None},
}
DEFAULT_TRAITS = {"readonly": False, "background": False, "sandbox": None}

# Frontmatter keys carried into the generated SKILL.md. Everything else
# (allowed-tools, model, color, tools) is host-specific and dropped.
KEEP_FIELDS = ("name", "description", "argument-hint")

# Server name → human-friendly label used when rewriting MCP tool references.
SERVER_FRIENDLY = {"plugin_slack_slack": "Slack"}

# Tokens that must never survive into a generated file (residual = transform gap).
RESIDUAL_TOKENS = (
    r"mcp__",
    r"\$ARGUMENTS",
    r"\$CLAUDE_PROJECT_DIR",
    r"AskUserQuestion",
    r"\.claude/skills/",
)

PROVENANCE_NOTE = "do not edit — regenerate with: uv run core/scripts/build_adapters.py"


# ── Frontmatter helpers ──────────────────────────────────────────────────────
def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Mirrors server.py / validate.py idiom."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2]


def _dq(value: str) -> str:
    """Double-quote a scalar for YAML output."""
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_frontmatter(fm: dict, generated_from: str, sha: str) -> str:
    """Build the generated SKILL.md frontmatter with controlled formatting.

    `description` is emitted as a literal block scalar so multi-line content
    (e.g. agent `<example>` blocks) is preserved faithfully.
    """
    lines = ["---", f"name: {fm['name']}"]
    description = str(fm.get("description", "")).rstrip("\n")
    lines.append("description: |-")
    for dl in description.split("\n"):
        lines.append(f"  {dl}" if dl.strip() else "")
    if fm.get("argument-hint") is not None:
        lines.append(f"argument-hint: {_dq(fm['argument-hint'])}")
    lines.append(f"generated_from: {generated_from}")
    lines.append(f"source_sha256: {sha}")
    lines.append(f"x_generated_note: {_dq(PROVENANCE_NOTE)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def lead_description(description: str) -> str:
    """Concise one-line 'when to use' — strip <example>/<commentary> blocks and
    collapse whitespace. A native subagent `description` wants a single line."""
    desc = str(description)
    cut = len(desc)
    for marker in ("<example>", "<commentary>"):
        i = desc.find(marker)
        if i != -1:
            cut = min(cut, i)
    return " ".join(desc[:cut].split())


def render_cursor_agent(name, fm, body, generated_from, sha, traits) -> str:
    """Cursor native subagent: .cursor/agents/<name>.md (frontmatter + body)."""
    lines = [
        "---",
        f"name: {name}",
        f"description: {_dq(lead_description(fm.get('description', '')))}",
        "model: inherit",
        f"readonly: {str(traits['readonly']).lower()}",
        f"is_background: {str(traits['background']).lower()}",
        f"generated_from: {generated_from}",
        f"source_sha256: {sha}",
        f"x_generated_note: {_dq(PROVENANCE_NOTE)}",
        "---",
    ]
    out = "\n".join(lines) + "\n\n" + body
    return out if out.endswith("\n") else out + "\n"


def render_codex_agent(name, fm, body, generated_from, sha, traits) -> str:
    """Codex native subagent: .codex/agents/<name>.toml (hand-emitted TOML)."""
    lines = [
        f"# generated-from: {generated_from}  sha256:{sha}",
        f"# {PROVENANCE_NOTE}",
        f"name = {_dq(name)}",
        f"description = {_dq(lead_description(fm.get('description', '')))}",
    ]
    if traits["sandbox"]:
        lines.append(f"sandbox_mode = {_dq(traits['sandbox'])}")
    instructions = body.rstrip("\n")
    if "'''" not in instructions:  # TOML multi-line literal — no escaping needed
        lines.append(f"developer_instructions = '''\n{instructions}\n'''")
    else:  # rare fallback: basic multi-line string with escapes
        esc = instructions.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
        lines.append(f'developer_instructions = """\n{esc}\n"""')
    return "\n".join(lines) + "\n"


# ── Body neutralization ───────────────────────────────────────────────────────
def _friendly(server: str) -> str:
    return SERVER_FRIENDLY.get(server, server)


def _sub_mcp_wildcard(m: re.Match) -> str:
    return f"the {_friendly(m.group(1))} MCP server's tools"


def _sub_mcp_tool(m: re.Match) -> str:
    return f"the `{m.group(2)}` tool ({_friendly(m.group(1))} MCP server)"


def transform_body(body: str) -> str:
    """Neutralize Claude-specific tokens. Order matters (see inline notes)."""
    # 1. Drop the "Tool naming note" blockquote (becomes nonsense once mcp__ is
    #    rewritten to prose) — must run BEFORE the MCP transforms.
    body = re.sub(r"(?m)^> \*\*Tool naming note:\*\*.*\n\n?", "", body)

    # 2. CLAUDE_PROJECT_DIR — to a portable shell equivalent in code, prose
    #    elsewhere. Specific param-expansion first, then $VAR, then bare word.
    body = body.replace("${CLAUDE_PROJECT_DIR//\\//-}", "$(pwd | tr / -)")
    body = body.replace("`$CLAUDE_PROJECT_DIR`", "`$(pwd)`")
    body = body.replace("$CLAUDE_PROJECT_DIR", "$(pwd)")
    body = body.replace("`CLAUDE_PROJECT_DIR`", "`the project root`")
    body = body.replace("CLAUDE_PROJECT_DIR", "the project root")

    # 3. MCP wire-names → logical prose (wildcards before specific tools).
    body = re.sub(r"`?mcp__([a-z0-9_-]+)__\*`?", _sub_mcp_wildcard, body)
    body = re.sub(r"`?mcp__([a-z0-9_-]+)__([a-z0-9_]+)`?", _sub_mcp_tool, body)

    # 4. $ARGUMENTS (Claude-specific substitution).
    body = re.sub(r"`?\$ARGUMENTS`?", "the arguments provided when you were invoked", body)

    # 5. AskUserQuestion (Claude-specific structured-question tool). "structured
    #    questions" reads acceptably as both a noun ("the structured questions
    #    schema") and an instrument ("via structured questions").
    body = body.replace("`AskUserQuestion`", "structured questions")
    body = body.replace("AskUserQuestion", "structured questions")

    # 6. Reference paths → skill-relative (references/ is copied alongside).
    body = re.sub(r"\.claude/skills/[a-z0-9-]+/references/", "references/", body)

    return body


def is_text(data: bytes) -> bool:
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


# ── Output assembly ────────────────────────────────────────────────────────────
def iter_sources() -> list[Path]:
    sources: list[Path] = []
    sources += sorted(SRC_SKILLS.glob("*/SKILL.md"))
    sources += sorted(SRC_AGENTS.glob("*.md"))
    sources += sorted(SRC_COMMANDS.glob("*.md"))
    return sources


def build_outputs() -> dict[str, bytes]:
    """Return {repo_relative_path: bytes} for every generated file across all
    managed trees (.agents/skills, .codex/agents, .cursor/agents)."""
    outputs: dict[str, bytes] = {}
    for src in iter_sources():
        raw = src.read_text(encoding="utf-8")
        fm, body = split_frontmatter(raw)
        name = fm.get("name")
        if not name:
            raise SystemExit(f"ERROR: {src.relative_to(ROOT)} has no `name` in frontmatter")

        # Neutralize Claude-isms in the carried frontmatter too (descriptions
        # cite `AskUserQuestion`, etc.) — not just the body.
        fm = dict(fm)
        if fm.get("description"):
            fm["description"] = transform_body(str(fm["description"]))
        if fm.get("argument-hint"):
            fm["argument-hint"] = transform_body(str(fm["argument-hint"]))

        generated_from = str(src.relative_to(ROOT))
        sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        new_body = transform_body(body).lstrip("\n")
        if name == "system-health":
            new_body = (
                "**READ-ONLY:** This is a diagnostic scan — never modify any file "
                "or task/project state.\n\n" + new_body
            )

        # 1. Skill adapter — every source (skills, agents, command) → .agents/skills
        skill_md = render_frontmatter(fm, generated_from, sha) + "\n" + new_body
        if not skill_md.endswith("\n"):
            skill_md += "\n"
        outputs[f".agents/skills/{name}/SKILL.md"] = skill_md.encode("utf-8")

        # Copy + transform the references/ subtree, if any.
        refdir = src.parent / "references"
        if refdir.is_dir():
            for f in sorted(refdir.rglob("*")):
                if not f.is_file():
                    continue
                rel = f.relative_to(refdir).as_posix()
                data = f.read_bytes()
                if is_text(data):
                    data = transform_body(data.decode("utf-8")).encode("utf-8")
                outputs[f".agents/skills/{name}/references/{rel}"] = data

        # 2. Native subagents — agents only → .codex/agents + .cursor/agents
        if src.parent == SRC_AGENTS:
            traits = AGENT_TRAITS.get(name, DEFAULT_TRAITS)
            outputs[f".cursor/agents/{name}.md"] = render_cursor_agent(
                name, fm, new_body, generated_from, sha, traits).encode("utf-8")
            outputs[f".codex/agents/{name}.toml"] = render_codex_agent(
                name, fm, new_body, generated_from, sha, traits).encode("utf-8")
    return outputs


def scan_residual(outputs: dict[str, bytes]) -> list[str]:
    """Find any forbidden Claude-isms that survived into generated text files."""
    pattern = re.compile("|".join(RESIDUAL_TOKENS))
    problems: list[str] = []
    for rel, data in sorted(outputs.items()):
        if not is_text(data):
            continue
        for i, line in enumerate(data.decode("utf-8").splitlines(), 1):
            # `generated_from:` is intentional provenance pointing at the source.
            if line.lstrip().startswith("generated_from:"):
                continue
            for hit in pattern.findall(line):
                problems.append(f"{rel}:{i}: leftover `{hit}` → {line.strip()[:100]}")
    return problems


# ── Commands ───────────────────────────────────────────────────────────────────
def disk_files() -> set[str]:
    """All files currently on disk under the managed trees (repo-relative)."""
    found: set[str] = set()
    for base in MANAGED_BASES:
        bp = ROOT / base
        if bp.is_dir():
            found |= {p.relative_to(ROOT).as_posix() for p in bp.rglob("*") if p.is_file()}
    return found


def check_adapters() -> list[str]:
    """Pure check: return problem strings (missing / orphan / stale / leftover).
    No printing, no exit — safe to import and call from validate.py."""
    try:
        outputs = build_outputs()
    except Exception as e:  # source error → report instead of crashing the caller
        return [f"generator error: {e}"]
    expected = set(outputs)
    on_disk = disk_files()
    problems: list[str] = []
    problems += [f"missing: {r}" for r in sorted(expected - on_disk)]
    problems += [f"orphan: {r}" for r in sorted(on_disk - expected)]
    problems += [
        f"stale: {r}" for r in sorted(expected & on_disk)
        if (ROOT / r).read_bytes() != outputs[r]
    ]
    problems += [f"leftover: {p}" for p in scan_residual(outputs)]
    return problems


def cmd_build(dry_run: bool, verbose: bool) -> int:
    outputs = build_outputs()
    expected = set(outputs)
    on_disk = disk_files()

    created = sorted(r for r in expected if r not in on_disk)
    removed = sorted(r for r in on_disk if r not in expected)
    updated = sorted(
        r for r in expected
        if r in on_disk and (ROOT / r).read_bytes() != outputs[r]
    )

    residual = scan_residual(outputs)
    if residual:
        print("✗ leftover Claude-isms in generated output (fix transforms):", file=sys.stderr)
        for p in residual:
            print(f"   {p}", file=sys.stderr)
        return 1

    if dry_run:
        print(f"[dry-run] would create {len(created)}, update {len(updated)}, remove {len(removed)}")
        for r in created:
            print(f"   + {r}")
        for r in updated:
            print(f"   ~ {r}")
        for r in removed:
            print(f"   - {r}")
        return 0

    for rel, data in outputs.items():
        dest = ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or dest.read_bytes() != data:
            dest.write_bytes(data)

    for rel in removed:
        (ROOT / rel).unlink()
    # Prune now-empty directories within each managed base (bottom-up).
    for base in MANAGED_BASES:
        bp = ROOT / base
        if bp.is_dir():
            for d in sorted((p for p in bp.rglob("*") if p.is_dir()), reverse=True):
                if not any(d.iterdir()):
                    d.rmdir()

    skills = sum(1 for r in expected if r.endswith("/SKILL.md"))
    subagents = sum(1 for r in expected if r.startswith((".codex/agents/", ".cursor/agents/")))
    print(f"✓ generated {skills} skills + {subagents} native subagent files "
          f"({len(created)} new, {len(updated)} updated, {len(removed)} removed, "
          f"{len(expected)} files total)")
    if verbose:
        for r in created:
            print(f"   + {r}")
        for r in updated:
            print(f"   ~ {r}")
        for r in removed:
            print(f"   - {r}")
    return 0


def cmd_check(verbose: bool) -> int:
    problems = check_adapters()
    if not problems:
        print("✓ adapters in sync — no drift, no leftover Claude-isms")
        return 0
    print("✗ adapter drift detected — run: uv run core/scripts/build_adapters.py", file=sys.stderr)
    for p in problems:
        print(f"   {p}", file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate .agents/skills from .claude source")
    ap.add_argument("--check", action="store_true", help="verify no drift; exit 1 on issue")
    ap.add_argument("--dry-run", action="store_true", help="show changes without writing")
    ap.add_argument("--verbose", "-v", action="store_true", help="list every changed file")
    args = ap.parse_args()

    if not SRC_SKILLS.is_dir():
        print(f"ERROR: no source skills at {SRC_SKILLS} (set PERSONAL_OS_ROOT?)", file=sys.stderr)
        return 2

    if args.check:
        return cmd_check(args.verbose)
    return cmd_build(args.dry_run, args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
