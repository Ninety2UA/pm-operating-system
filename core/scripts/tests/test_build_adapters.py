"""Characterization tests pinning the adapter generator's current behavior
(KTD-4): each transform_body neutralization rule, the residual-token net,
frontmatter rendering, and both native agent renderers — captured before the
U5 mechanism changes so U5's diff shows up as deliberate test updates.

The 2026-09 wave (U3) adds the generated-file manifest and the ownership
refusal: those tests drive the real build against a `fake_root` fixture so
every disk-touching scenario (delete, refuse, force, bootstrap) is real.
`test_full_tree_in_sync` stays a real-repo test and needs the committed
manifest at `.agents/skills.lock.json`.
"""
import hashlib
import json

import pytest
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
        "hook .claude/hooks/report-only-guard.sh here",
        "flag run_in_background: false here",
        "run /skill-doctor here",
        "run claude plugin validate . here",
    ])
    problems = ba.scan_residual({"x.md": body.encode("utf-8")})
    assert len(problems) == 9, problems


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


def test_check_adapters_reports_both_systemexit_and_marker_errors(monkeypatch):
    """A malformed marker (HostMarkerError) AND a plain SystemExit (e.g. a
    source missing `name`) must both be reported by check_adapters, not
    escape and abort the validator run."""
    for exc in (ba.HostMarkerError("unclosed host block opened at line 1"),
                SystemExit("ERROR: source has no `name` in frontmatter")):
        def boom(_e=exc):
            raise _e
        monkeypatch.setattr(ba, "build_outputs", boom)
        problems = ba.check_adapters()
        assert problems and "generator error" in problems[0], exc


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
                "claude-haiku-4-5-20251001", "claude-opus-4-8",
                "claude-opus-5", "claude-fable-5-1"):
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


# ── U3: Claude-only pointers in the leak net (KTD11) ─────────────────────────
# One case per new token; `Monitor` is deliberately NOT in the net (it occurs
# as an ordinary word in a copied reference file).

@pytest.mark.parametrize("leak", [
    "see .claude/hooks/report-only-guard.sh",
    "see .claude/agents/deep-research.md",
    "see .claude/commands/morning.md",
    "pass run_in_background: false",
    "then run /skill-doctor",
    "then run claude plugin validate .",
])
def test_leak_net_catches_claude_only_pointers(leak):
    hits = ba.scan_residual({"x.md": f"body {leak} here".encode("utf-8")})
    assert hits, leak


def test_leak_net_leaves_monitor_and_core_paths_alone():
    for benign in ("Monitor the run", "see core/scripts/validate.py",
                   "the .claude/settings.json file"):
        assert ba.scan_residual({"x.md": benign.encode("utf-8")}) == [], benign


def test_leak_net_exempts_codex_provenance_header():
    """The Codex TOML header names its `.claude/agents/` source on purpose,
    exactly like the YAML `generated_from:` line."""
    toml = (b"# generated-from: .claude/agents/probe.md  sha256:abc\n"
            b"# do not edit\nname = \"probe\"\n")
    assert ba.scan_residual({".codex/agents/probe.toml": toml}) == []


# ── U3: manifest + ownership refusal (KTD4) ─────────────────────────────────

SKILL_SRC = "---\nname: demo\ndescription: Demo skill\n---\n\nBody of demo.\n"
REF_SRC = "Reference notes, first edition.\n"
AGENT_SRC = ("---\nname: probe\ndescription: Probe agent\nmodel: opus\n---\n\n"
             "Probe body.\n")

DEMO_SKILL = ".agents/skills/demo/SKILL.md"
DEMO_REF = ".agents/skills/demo/references/notes.md"
PROBE_SKILL = ".agents/skills/probe/SKILL.md"
PROBE_CURSOR = ".cursor/agents/probe.md"
PROBE_CODEX = ".codex/agents/probe.toml"


@pytest.fixture
def fake_root(tmp_path, monkeypatch):
    """A minimal source tree under tmp_path: one skill with a references/
    file (unmarked generated copy) and one agent (all three managed bases).
    ROOT and the SRC_* globals are import-time constants, so patch them."""
    root = tmp_path / "repo"
    (root / ".claude" / "skills" / "demo" / "references").mkdir(parents=True)
    (root / ".claude" / "skills" / "demo" / "SKILL.md").write_text(SKILL_SRC, encoding="utf-8")
    (root / ".claude" / "skills" / "demo" / "references" / "notes.md").write_text(
        REF_SRC, encoding="utf-8")
    (root / ".claude" / "agents").mkdir()
    (root / ".claude" / "agents" / "probe.md").write_text(AGENT_SRC, encoding="utf-8")
    (root / ".claude" / "commands").mkdir()
    monkeypatch.setattr(ba, "ROOT", root)
    monkeypatch.setattr(ba, "SRC_SKILLS", root / ".claude" / "skills")
    monkeypatch.setattr(ba, "SRC_AGENTS", root / ".claude" / "agents")
    monkeypatch.setattr(ba, "SRC_COMMANDS", root / ".claude" / "commands")
    return root


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _build(force: bool = False) -> int:
    return ba.cmd_build(dry_run=False, verbose=False, force=force)


def test_deleted_source_skill_is_removed_via_manifest(fake_root, capsys):
    """THE deadlock scenario (KTD4): a deleted source skill's generated copies
    carry no marker in references/, so only the manifest can prove ownership
    and let the build remove them."""
    assert _build() == 0
    assert (fake_root / DEMO_REF).is_file()
    manifest = json.loads(ba.manifest_path().read_text(encoding="utf-8"))
    assert DEMO_SKILL in manifest and DEMO_REF in manifest

    import shutil
    shutil.rmtree(fake_root / ".claude" / "skills" / "demo")

    assert _build() == 0, capsys.readouterr()
    assert not (fake_root / DEMO_SKILL).exists()
    assert not (fake_root / DEMO_REF).exists()
    assert not (fake_root / ".agents" / "skills" / "demo").exists()  # pruned
    manifest = json.loads(ba.manifest_path().read_text(encoding="utf-8"))
    assert DEMO_SKILL not in manifest and DEMO_REF not in manifest
    assert PROBE_SKILL in manifest  # the surviving agent is still listed
    assert ba.check_adapters() == []


def test_two_builds_produce_identical_deterministic_manifest(fake_root):
    assert _build() == 0
    first = ba.manifest_path().read_bytes()
    assert _build() == 0
    assert ba.manifest_path().read_bytes() == first

    text = first.decode("utf-8")
    manifest = json.loads(text)
    outputs = ba.build_outputs()
    # exactly the expected set, hashed over the generated bytes, all bases
    assert manifest == {rel: _sha(data) for rel, data in outputs.items()}
    assert {DEMO_SKILL, DEMO_REF, PROBE_SKILL, PROBE_CURSOR, PROBE_CODEX} <= set(manifest)
    # sorted keys, one entry per line, no timestamps
    assert list(manifest) == sorted(manifest)
    entry_lines = [ln for ln in text.splitlines() if ln.strip().startswith('"')]
    assert len(entry_lines) == len(manifest)
    assert "time" not in text.lower() and "date" not in text.lower()
    assert text.endswith("\n")


def test_manifest_path_outside_managed_bases(fake_root):
    assert _build() == 0
    rel = ba.manifest_path().relative_to(fake_root).as_posix()
    assert rel == ".agents/skills.lock.json"
    assert ba.manifest_path().is_file()
    assert rel not in ba.build_outputs()
    assert rel not in ba.disk_files()


def test_dry_run_never_writes_manifest_or_outputs(fake_root, capsys):
    assert ba.cmd_build(dry_run=True, verbose=False, force=False) == 0
    assert not ba.manifest_path().exists()
    assert ba.disk_files() == set()
    assert "would create 5" in capsys.readouterr().out


def test_foreign_user_file_survives_and_fails_build(fake_root, capsys):
    """A Cursor user's own `.cursor/agents/mine.md` (no marker, not in the
    manifest) is never touched: it is named on stderr and the build exits 1
    after writing every non-conflicting output. `--force` removes it."""
    assert _build() == 0
    capsys.readouterr()
    mine = fake_root / ".cursor" / "agents" / "mine.md"
    mine.write_text("---\nname: mine\n---\nMy own agent.\n", encoding="utf-8")
    # make a real pending write so "non-conflicting outputs are written first" is observable
    (fake_root / ".claude" / "skills" / "demo" / "SKILL.md").write_text(
        SKILL_SRC.replace("Body of demo.", "Body of demo, v2."), encoding="utf-8")

    assert _build() == 1
    err = capsys.readouterr().err
    assert ".cursor/agents/mine.md" in err
    assert "--force" in err
    assert mine.read_text(encoding="utf-8").endswith("My own agent.\n")
    assert b"Body of demo, v2." in (fake_root / DEMO_SKILL).read_bytes()
    # the manifest was still written and lists every expected path
    manifest = json.loads(ba.manifest_path().read_text(encoding="utf-8"))
    assert manifest == {rel: _sha(d) for rel, d in ba.build_outputs().items()}
    # --check keeps today's orphan verdict for the refused file
    assert "orphan: .cursor/agents/mine.md" in ba.check_adapters()

    assert _build(force=True) == 0
    assert not mine.exists()
    assert ba.check_adapters() == []


def test_bootstrap_without_manifest_overwrites_expected_keeps_foreign(fake_root, capsys):
    """No manifest on disk (the July contract): every expected path is owned,
    so an unmarked stale references/ copy is overwritten; a marker-less
    non-expected file still needs the marker or --force and is left in place."""
    stale_ref = fake_root / DEMO_REF
    stale_ref.parent.mkdir(parents=True)
    stale_ref.write_text("an older generated copy, no marker\n", encoding="utf-8")
    stray = fake_root / ".agents" / "skills" / "stray.md"
    stray.write_text("not ours\n", encoding="utf-8")
    assert not ba.manifest_path().exists()

    assert _build() == 1
    err = capsys.readouterr().err
    assert ".agents/skills/stray.md" in err
    assert stray.read_text(encoding="utf-8") == "not ours\n"
    assert stale_ref.read_bytes() == ba.build_outputs()[DEMO_REF]
    assert ba.manifest_path().is_file()  # written even though the build exited 1


def test_hand_edited_marked_skill_is_overwritten(fake_root):
    assert _build() == 0
    gen = fake_root / DEMO_SKILL
    edited = gen.read_text(encoding="utf-8").replace("Body of demo.", "Body of demo, edited by hand.")
    assert "generated_from:" in edited
    gen.write_text(edited, encoding="utf-8")
    assert _build() == 0
    assert gen.read_bytes() == ba.build_outputs()[DEMO_SKILL]


def test_unmarked_copy_matching_manifest_is_overwritten_on_source_change(fake_root):
    assert _build() == 0
    (fake_root / ".claude" / "skills" / "demo" / "references" / "notes.md").write_text(
        "Reference notes, second edition.\n", encoding="utf-8")
    assert _build() == 0
    assert (fake_root / DEMO_REF).read_text(encoding="utf-8") == "Reference notes, second edition.\n"


def test_unmarked_copy_matching_neither_is_refused(fake_root, capsys):
    assert _build() == 0
    capsys.readouterr()
    ref = fake_root / DEMO_REF
    ref.write_text("hand-edited generated copy\n", encoding="utf-8")
    assert _build() == 1
    err = capsys.readouterr().err
    assert DEMO_REF in err
    assert ref.read_text(encoding="utf-8") == "hand-edited generated copy\n"
    # refused paths are omitted from the manifest; the rest is listed
    manifest = json.loads(ba.manifest_path().read_text(encoding="utf-8"))
    assert DEMO_REF not in manifest and DEMO_SKILL in manifest
    # --force overwrites it and the tree is green again
    assert _build(force=True) == 0
    assert ref.read_bytes() == ba.build_outputs()[DEMO_REF]
    assert ba.check_adapters() == []


def test_classify_matrix():
    """The write decision per the KTD4 diagram, as a pure function."""
    marked = b"---\nname: x\ngenerated_from: .claude/skills/x/SKILL.md\n---\nbody\n"
    plain = b"plain bytes\n"
    other = b"other bytes\n"
    manifest = {"p": _sha(plain)}
    # not on disk → create; identical → leave
    assert ba.classify("p", None, plain, manifest) == "create"
    assert ba.classify("p", plain, plain, manifest) == "leave"
    # expected, differs: manifest hash → overwrite; marker → overwrite; neither → refuse
    assert ba.classify("p", plain, other, manifest) == "overwrite"
    assert ba.classify("q", marked, other, manifest) == "overwrite"
    assert ba.classify("q", plain, other, manifest) == "refuse"
    # not expected: manifest hash → remove; marker → remove; neither → refuse
    assert ba.classify("p", plain, None, manifest) == "remove"
    assert ba.classify("q", marked, None, manifest) == "remove"
    assert ba.classify("q", plain, None, manifest) == "refuse"
    # bootstrap (no manifest): expected paths owned; orphans need the marker
    assert ba.classify("q", plain, other, None) == "overwrite"
    assert ba.classify("q", plain, None, None) == "refuse"
    assert ba.classify("q", marked, None, None) == "remove"


def test_provenance_marker_detection():
    assert ba.has_provenance_marker(
        b"---\nname: x\ngenerated_from: .claude/skills/x/SKILL.md\n---\nbody\n")
    assert ba.has_provenance_marker(b"# generated-from: .claude/agents/x.md  sha256:abc\nname = \"x\"\n")
    # the marker counts only in frontmatter / the TOML header, not in a body
    assert not ba.has_provenance_marker(b"---\nname: x\n---\ngenerated_from: mentioned in body\n")
    assert not ba.has_provenance_marker(b"plain reference copy\n")
    assert not ba.has_provenance_marker(b"\x00\xff binary")


def test_check_adapters_manifest_forms(fake_root):
    assert _build() == 0
    assert ba.check_adapters() == []
    mrel = ba.MANIFEST_REL

    # hand-edited generated file: disk differs from both expected and manifest
    ref = fake_root / DEMO_REF
    ref.write_text("hand-edited\n", encoding="utf-8")
    problems = ba.check_adapters()
    assert f"manifest: {DEMO_REF}" in problems
    assert f"stale: {DEMO_REF}" not in problems
    assert _build(force=True) == 0

    # source-only change: disk still equals the last generated bytes → stale
    (fake_root / ".claude" / "skills" / "demo" / "references" / "notes.md").write_text(
        "third edition\n", encoding="utf-8")
    problems = ba.check_adapters()
    assert f"stale: {DEMO_REF}" in problems
    assert f"manifest: {DEMO_REF}" not in problems
    assert _build() == 0
    assert ba.check_adapters() == []

    # manifest value disagrees with the expected bytes → out of date
    manifest = json.loads(ba.manifest_path().read_text(encoding="utf-8"))
    tampered = dict(manifest)
    tampered[DEMO_SKILL] = "0" * 64
    ba.manifest_path().write_text(json.dumps(tampered, indent=2, sort_keys=True) + "\n")
    assert f"manifest: {mrel} (out of date)" in ba.check_adapters()

    # extra key → out of date
    extra = dict(manifest)
    extra[".agents/skills/gone/SKILL.md"] = "0" * 64
    ba.manifest_path().write_text(json.dumps(extra, indent=2, sort_keys=True) + "\n")
    assert f"manifest: {mrel} (out of date)" in ba.check_adapters()

    # unreadable → named, never silently treated as absent
    ba.manifest_path().write_text("<<<<<<< HEAD\n{}\n", encoding="utf-8")
    assert any(p.startswith(f"manifest: {mrel} (unreadable") for p in ba.check_adapters())

    # absent
    ba.manifest_path().unlink()
    assert "manifest: absent" in ba.check_adapters()


def test_unreadable_manifest_fails_build_without_writing(fake_root, capsys):
    assert _build() == 0
    (fake_root / ".claude" / "skills" / "demo" / "SKILL.md").write_text(
        SKILL_SRC.replace("Body of demo.", "Body of demo, v2."), encoding="utf-8")
    ba.manifest_path().write_text("<<<<<<< HEAD\n{}\n", encoding="utf-8")
    assert _build() == 1
    assert "unreadable" in capsys.readouterr().err
    assert b"Body of demo, v2." not in (fake_root / DEMO_SKILL).read_bytes()
