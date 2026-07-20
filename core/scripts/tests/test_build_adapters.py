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


# ── U5: host-conditional sections (KTD-8) ────────────────────────────────────

def test_host_section_keeps_only_fallback():
    src = ("before\n"
           "<!-- host:claude-code -->\n"
           "Use the Workflow tool.\n"
           "<!-- host:fallback (portable hosts see only this section) -->\n"
           "Run the evaluations sequentially.\n"
           "<!-- host:end -->\n"
           "after")
    assert ba.transform_body(src) == \
        "before\nRun the evaluations sequentially.\nafter"


def test_host_section_without_fallback_drops_block():
    src = "a\n<!-- host:claude-code -->\nclaude only\n<!-- host:end -->\nb"
    assert ba.transform_body(src) == "a\nb"


def test_host_marker_errors_are_named():
    import pytest
    for bad, msg_part in [
        ("<!-- host:claude-code -->\nx", "unclosed"),
        ("<!-- host:end -->", "without an open block"),
        ("<!-- host:fallback -->\nx\n<!-- host:end -->", "outside a claude-code block"),
        ("<!-- host:claude-code -->\n<!-- host:claude-code -->\n<!-- host:end -->",
         "nested"),
        # Misspelled / suffixed directives must error, not silently mis-parse.
        ("<!-- host:falback -->\nx\n<!-- host:end -->", "unknown host directive"),
        ("<!-- host:claude-code-extra -->\nx\n<!-- host:end -->", "unknown host directive"),
    ]:
        with pytest.raises(SystemExit) as exc:
            ba.transform_body(bad)
        assert "host-marker error" in str(exc.value)
        assert msg_part in str(exc.value)


def test_host_markers_inside_code_fence_are_literal():
    """A skill documenting the marker syntax inside a fenced block must not
    have that example parsed as a live marker."""
    src = ("intro\n"
           "```\n"
           "<!-- host:claude-code -->\n"
           "example native content\n"
           "<!-- host:end -->\n"
           "```\n"
           "outro")
    # No error raised (the markers are inside a fence), content preserved.
    assert ba.transform_body(src) == src


def test_host_marker_error_does_not_crash_check_adapters(monkeypatch):
    """A malformed marker is a HostMarkerError (a SystemExit subclass); it
    must be reported by check_adapters, not escape and abort the validator."""
    def boom():
        raise ba.HostMarkerError("unclosed host block opened at line 1")
    monkeypatch.setattr(ba, "build_outputs", boom)
    problems = ba.check_adapters()
    assert problems and "generator error" in problems[0]


def test_cursor_model_exemption_frontmatter_only():
    """A model ID in a .cursor frontmatter line is exempt; the same string
    in the BODY is a real leak that must be flagged."""
    fm_only = b"---\nname: t\nmodel: claude-opus-4-8\n---\n\nbody text\n"
    assert ba.scan_residual({".cursor/agents/t.md": fm_only}) == []
    body_leak = b"---\nname: t\nmodel: inherit\n---\n\nmodel: claude-opus-4-8 in body\n"
    assert ba.scan_residual({".cursor/agents/t.md": body_leak}) != []


def test_ordering_invariant_fallback_is_reneutralized():
    """THE load-bearing fixture (KTD-8): a fenced block whose fallback contains
    a token from every transformable RESIDUAL_TOKENS family must come out fully
    neutralized, proving host-section stripping runs before every other step."""
    src = ("<!-- host:claude-code -->\n"
           "Native path.\n"
           "<!-- host:fallback -->\n"
           "Call mcp__manager-ai__list_tasks with $ARGUMENTS from "
           "$CLAUDE_PROJECT_DIR via AskUserQuestion, see "
           ".claude/skills/morning/references/x.md.\n"
           "<!-- host:end -->\n")
    out = ba.transform_body(src)
    assert ba.scan_residual({"f.md": out.encode("utf-8")}) == [], out
    assert "the `list_tasks` tool (manager-ai MCP server)" in out
    assert "the arguments provided when you were invoked" in out
    assert "structured questions" in out
    assert "references/x.md" in out


def test_raw_model_id_in_fallback_is_flagged_not_rewritten():
    """Model IDs are detection-only: a raw ID surviving in fallback prose is a
    real leak the net must flag (there is no safe automatic rewrite for it)."""
    src = ("<!-- host:claude-code -->\nnative\n<!-- host:fallback -->\n"
           "pin claude-fable-5 here\n<!-- host:end -->\n")
    out = ba.transform_body(src)
    hits = ba.scan_residual({"f.md": out.encode("utf-8")})
    assert hits and "claude-fable-5" in hits[0]


# ── U5: model/effort tier propagation (KTD-1) ────────────────────────────────

def test_codex_renderer_maps_model_and_effort():
    fm = {"description": "d", "model": "haiku", "effort": "low"}
    out = ba.render_codex_agent("t", fm, "body", "src", "sha", ba.DEFAULT_TRAITS)
    assert 'model = "gpt-5.4-mini"' in out
    assert 'model_reasoning_effort = "low"' in out


def test_codex_renderer_inherit_omits_model_key():
    fm = {"description": "d", "model": "inherit"}
    out = ba.render_codex_agent("t", fm, "body", "src", "sha", ba.DEFAULT_TRAITS)
    assert "model =" not in out
    assert "model_reasoning_effort" not in out
    # no-model-at-all behaves like inherit
    out2 = ba.render_codex_agent("t", {"description": "d"}, "body", "src", "sha",
                                 ba.DEFAULT_TRAITS)
    assert "model =" not in out2


def test_codex_effort_max_maps_to_xhigh():
    fm = {"description": "d", "model": "fable", "effort": "max"}
    out = ba.render_codex_agent("t", fm, "body", "src", "sha", ba.DEFAULT_TRAITS)
    assert 'model = "gpt-5.6-sol"' in out
    assert 'model_reasoning_effort = "xhigh"' in out


def test_cursor_renderer_verified_set_only():
    opus = ba.render_cursor_agent("t", {"description": "d", "model": "opus"},
                                  "b", "src", "sha", ba.DEFAULT_TRAITS)
    assert "model: claude-opus-4-8" in opus
    for unverified in ("sonnet", "haiku", "fable", "inherit", "claude-sonnet-5"):
        out = ba.render_cursor_agent("t", {"description": "d", "model": unverified},
                                     "b", "src", "sha", ba.DEFAULT_TRAITS)
        assert "model: inherit" in out, unverified


# ── U5: model-ID leak net ────────────────────────────────────────────────────

def test_leak_net_catches_raw_model_ids():
    for raw in ("claude-fable-5", "claude-3-5-sonnet-latest",
                "claude-haiku-4-5-20251001", "claude-opus-4-8"):
        hits = ba.scan_residual({"x.md": f"pin {raw} here".encode("utf-8")})
        assert hits, raw


def test_leak_net_ignores_aliases_and_non_model_tokens():
    for benign in ("model: sonnet", "the claude-code changelog",
                   "claude-plugins-official marketplace"):
        assert ba.scan_residual({"x.md": benign.encode("utf-8")}) == [], benign


def test_leak_net_exempts_cursor_model_line_only():
    # The exemption applies to the model line in Cursor frontmatter…
    cursor_fm = b"---\nname: x\nmodel: claude-opus-4-8\n---\nbody\n"
    assert ba.scan_residual({".cursor/agents/x.md": cursor_fm}) == []
    # …but the same model ID in a skill body is a real leak.
    skill = b"---\nname: x\n---\nmodel: claude-opus-4-8 here\n"
    assert ba.scan_residual({".agents/skills/x/SKILL.md": skill}) != []
