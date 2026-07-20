"""Characterization tests pinning the adapter generator's current behavior
(KTD-4): each transform_body neutralization rule, the residual-token net,
frontmatter rendering, and both native agent renderers — captured before the
U5 mechanism changes so U5's diff shows up as deliberate test updates.
"""
from conftest import REPO_ROOT

import build_adapters as ba


# ── transform_body: one test per neutralization rule ─────────────────────────

def test_tool_naming_note_blockquote_dropped():
    src = "> **Tool naming note:** these vary by host.\n\nBody stays."
    assert ba.transform_body(src) == "Body stays."


def test_claude_project_dir_variants():
    src = ("${CLAUDE_PROJECT_DIR//\\//-} and `$CLAUDE_PROJECT_DIR` and "
           "$CLAUDE_PROJECT_DIR and `CLAUDE_PROJECT_DIR` and CLAUDE_PROJECT_DIR")
    assert ba.transform_body(src) == (
        "$(pwd | tr / -) and `$(pwd)` and $(pwd) and `the project root` "
        "and the project root"
    )


def test_mcp_names_to_prose_with_friendly_server():
    src = ("Use `mcp__manager-ai__*` then mcp__manager-ai__list_tasks "
           "and `mcp__plugin_slack_slack__post`")
    assert ba.transform_body(src) == (
        "Use the manager-ai MCP server's tools then the `list_tasks` tool "
        "(manager-ai MCP server) and the `post` tool (Slack MCP server)"
    )


def test_arguments_substitution():
    assert ba.transform_body("Given `$ARGUMENTS` or $ARGUMENTS") == (
        "Given the arguments provided when you were invoked or "
        "the arguments provided when you were invoked"
    )


def test_askuserquestion_substitution():
    assert ba.transform_body("Ask via `AskUserQuestion` or AskUserQuestion") == \
        "Ask via structured questions or structured questions"


def test_skill_reference_paths_relativized():
    assert ba.transform_body("See .claude/skills/morning/references/checklist.md now") == \
        "See references/checklist.md now"


# ── residual net ─────────────────────────────────────────────────────────────

def test_scan_residual_catches_every_token_family():
    body = "\n".join([
        "wire mcp__manager-ai__list_tasks name",
        "raw $ARGUMENTS here",
        "path $CLAUDE_PROJECT_DIR here",
        "tool AskUserQuestion here",
        "ref .claude/skills/morning/SKILL.md here",
    ])
    problems = ba.scan_residual({"x.md": body.encode("utf-8")})
    assert len(problems) == 5, problems


def test_scan_residual_exempts_generated_from_line():
    data = "generated_from: .claude/skills/morning/SKILL.md\n".encode("utf-8")
    assert ba.scan_residual({"x.md": data}) == []


# ── frontmatter + description rendering ──────────────────────────────────────

def test_render_frontmatter_block_scalar_and_hint():
    fm = {"name": "demo", "description": "Line one\n\nLine two with detail",
          "argument-hint": "[quick]"}
    assert ba.render_frontmatter(fm, "src/x.md", "abc123") == (
        "---\n"
        "name: demo\n"
        "description: |-\n"
        "  Line one\n"
        "\n"
        "  Line two with detail\n"
        'argument-hint: "[quick]"\n'
        "generated_from: src/x.md\n"
        "source_sha256: abc123\n"
        'x_generated_note: "do not edit — regenerate with: '
        'uv run core/scripts/build_adapters.py"\n'
        "---\n"
    )


def test_lead_description_strips_example_blocks():
    desc = "Use this when X.\n<example>\nfoo\n</example>"
    assert ba.lead_description(desc) == "Use this when X."


# ── native renderers, characterized against the real repo agents ─────────────
# system-health carries a model pin in source; deep-research inherits. Their
# rendered outputs must match the committed adapter files exactly — this pins
# the full render path (traits, lead description, provenance) while staying
# valid across deliberate regenerations, complementing check 38.

def _render_pair(agent_name: str):
    src = REPO_ROOT / ".claude" / "agents" / f"{agent_name}.md"
    raw = src.read_text(encoding="utf-8")
    fm, body = ba.split_frontmatter(raw)
    fm = dict(fm)
    if fm.get("description"):
        fm["description"] = ba.transform_body(str(fm["description"]))
    import hashlib
    sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    generated_from = f".claude/agents/{agent_name}.md"
    new_body = ba.transform_body(body).lstrip("\n")
    if agent_name == "system-health":
        new_body = ("**READ-ONLY:** This is a diagnostic scan — never modify "
                    "any file or task/project state.\n\n" + new_body)
    traits = ba.AGENT_TRAITS.get(agent_name, ba.DEFAULT_TRAITS)
    cursor = ba.render_cursor_agent(agent_name, fm, new_body, generated_from, sha, traits)
    codex = ba.render_codex_agent(agent_name, fm, new_body, generated_from, sha, traits)
    return cursor, codex


def test_system_health_renders_to_committed_output():
    cursor, codex = _render_pair("system-health")
    assert cursor == (REPO_ROOT / ".cursor/agents/system-health.md").read_text(encoding="utf-8")
    assert codex == (REPO_ROOT / ".codex/agents/system-health.toml").read_text(encoding="utf-8")
    # trait characterization: read-only diagnostic agent
    assert "readonly: true" in cursor
    assert 'sandbox_mode = "read-only"' in codex


def test_deep_research_renders_to_committed_output():
    cursor, codex = _render_pair("deep-research")
    assert cursor == (REPO_ROOT / ".cursor/agents/deep-research.md").read_text(encoding="utf-8")
    assert codex == (REPO_ROOT / ".codex/agents/deep-research.toml").read_text(encoding="utf-8")
    assert "is_background: true" in cursor


def test_full_tree_in_sync():
    """The committed generated trees match the generator exactly (drift = fail)."""
    assert ba.check_adapters() == []
