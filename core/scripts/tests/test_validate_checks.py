"""Fixture-driven tests for the U14 enforcement checks (test-first, KTD-4).
Each check is a pure function over a root path or text inputs, so it is
exercised on synthetic fixtures here and wired into the sequential
validator against the real repo separately.
"""
from conftest import REPO_ROOT

import validate_checks as vc


# ── model-roster currency (fail) ─────────────────────────────────────────────

def test_roster_flags_retired_ids_in_framework_files(tmp_path):
    sk = tmp_path / ".claude" / "skills" / "demo"
    sk.mkdir(parents=True)
    (sk / "SKILL.md").write_text(
        "---\nname: demo\nmodel: sonnet\n---\nUse claude-3-5-sonnet-latest here.\n",
        encoding="utf-8")
    fails = vc.check_model_roster(tmp_path)
    assert any("claude-3-5-sonnet-latest" in f and "demo" in f for f in fails)


def test_roster_passes_current_ids_and_aliases(tmp_path):
    sk = tmp_path / ".claude" / "skills" / "ok"
    sk.mkdir(parents=True)
    (sk / "SKILL.md").write_text(
        "---\nname: ok\nmodel: fable\n---\nPin claude-opus-4-8 and mention "
        "claude-code and the claude-plugins-official marketplace.\n",
        encoding="utf-8")
    assert vc.check_model_roster(tmp_path) == []


def test_roster_declared_once():
    assert "claude-fable-5" in vc.CURRENT_MODEL_IDS
    assert "claude-opus-4-8" in vc.CURRENT_MODEL_IDS


def test_roster_green_on_real_repo():
    assert vc.check_model_roster(REPO_ROOT) == []


# ── tiering presence (fail) ──────────────────────────────────────────────────

def test_tiering_flags_missing_model(tmp_path):
    d = tmp_path / ".claude" / "skills" / "nomodel"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: nomodel\n---\nbody\n", encoding="utf-8")
    fails = vc.check_tiering_presence(tmp_path)
    assert any("nomodel" in f for f in fails)


def test_tiering_passes_with_model(tmp_path):
    for name in ("a", "cli-watch"):
        d = tmp_path / ".claude" / "skills" / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            f"---\nname: {name}\nmodel: sonnet\neffort: high\n---\nb\n",
            encoding="utf-8")
    assert vc.check_tiering_presence(tmp_path) == []


def test_tiering_green_on_real_repo_including_watchers():
    assert vc.check_tiering_presence(REPO_ROOT) == []


# ── degradation coverage join (fail) ─────────────────────────────────────────

MANIFEST = """
| id | capability | class | status | gates | evidence |
|---|---|---|---|---|---|
| workflows.tool | Workflow | claude-native | verified | none | x |
| models.roster | roster | platform | verified | none | y |
"""


def test_degradation_fails_when_claude_native_adopt_lacks_mechanism():
    matrix = ("| id | verdict | wave | target files | degradation | unattended | tags |\n"
              "|---|---|---|---|---|---|---|\n"
              "| workflows.tool | adopt | C | `.claude/skills/x/SKILL.md` | no | no | — |\n")
    fails = vc.check_degradation_coverage(MANIFEST, matrix)
    assert any("workflows.tool" in f for f in fails)


def test_degradation_passes_with_fence_mechanism():
    matrix = ("| id | verdict | wave | target files | degradation | unattended | tags |\n"
              "|---|---|---|---|---|---|---|\n"
              "| workflows.tool | adopt | C | `.claude/skills/x/SKILL.md` | yes — fenced section | no | — |\n")
    assert vc.check_degradation_coverage(MANIFEST, matrix) == []


def test_degradation_ignores_non_generated_target_and_portable_prose():
    matrix = ("| id | verdict | wave | target files | degradation | unattended | tags |\n"
              "|---|---|---|---|---|---|---|\n"
              "| workflows.tool | adopt | C | `.claude/hooks/x.sh`, setup.sh | no — hook not generated | no | — |\n"
              "| workflows.tool | adopt | C | `.claude/skills/y/SKILL.md` | no — portable prose | no | — |\n")
    # First row targets a non-generated surface; second is portable prose —
    # neither needs a fence, so no failure.
    assert vc.check_degradation_coverage(MANIFEST, matrix) == []


def test_degradation_green_on_real_repo():
    manifest = (REPO_ROOT / "docs/capabilities.md").read_text(encoding="utf-8")
    matrix = (REPO_ROOT / "docs/ledger/adoption-matrix.md").read_text(encoding="utf-8")
    assert vc.check_degradation_coverage(manifest, matrix) == []


# ── tracked-artifact secret-scan (fail, blocking) ────────────────────────────

def test_secret_scan_flags_credentials(tmp_path):
    led = tmp_path / "docs" / "ledger"
    led.mkdir(parents=True)
    (led / "x.md").write_text(
        "provenance sha a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2\n"
        "aws AKIAIOSFODNN7EXAMPLE key\n", encoding="utf-8")
    fails = vc.check_tracked_secret_scan(tmp_path)
    # Flags the credential by location + label — and must NOT echo the raw
    # secret token into validator output.
    assert any("AWS access key" in f and "x.md:2" in f for f in fails)
    assert not any("AKIAIOSFODNN7EXAMPLE" in f for f in fails)
    # A 40-char git SHA must NOT be mistaken for a secret.
    assert not any(":1:" in f for f in fails)


def test_secret_scan_inline_allow_escape(tmp_path):
    led = tmp_path / "docs" / "ledger"
    led.mkdir(parents=True)
    (led / "x.md").write_text(
        "example token AKIAIOSFODNN7EXAMPLE  # secret-scan: allow\n",
        encoding="utf-8")
    assert vc.check_tracked_secret_scan(tmp_path) == []


def test_secret_scan_flags_private_key_header(tmp_path):
    w = tmp_path / "core" / "watchers"
    w.mkdir(parents=True)
    (w / "x.json").write_text("-----BEGIN RSA PRIVATE KEY-----\n", encoding="utf-8")
    assert vc.check_tracked_secret_scan(tmp_path) != []


def test_secret_scan_green_on_real_repo():
    assert vc.check_tracked_secret_scan(REPO_ROOT) == []


# ── guard-wiring (fail only on broken wiring) ────────────────────────────────

def test_guard_unwired_passes(tmp_path):
    h = tmp_path / ".claude" / "hooks"
    h.mkdir(parents=True)
    (h / "report-only-guard.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    (tmp_path / ".claude" / "settings.json").write_text("{}", encoding="utf-8")
    assert vc.check_guard_wiring(tmp_path) == []


def test_guard_wired_to_missing_path_fails(tmp_path):
    cl = tmp_path / ".claude"
    (cl / "hooks").mkdir(parents=True)
    (cl / "hooks" / "report-only-guard.sh").write_text("x", encoding="utf-8")
    (cl / "settings.local.json").write_text(
        '{"hooks":{"PreToolUse":[{"hooks":[{"type":"command",'
        '"command":"$CLAUDE_PROJECT_DIR/.claude/hooks/does-not-exist.sh"}]}]}}',
        encoding="utf-8")
    assert vc.check_guard_wiring(tmp_path) != []


def test_guard_wired_correctly_passes(tmp_path):
    cl = tmp_path / ".claude"
    (cl / "hooks").mkdir(parents=True)
    g = cl / "hooks" / "report-only-guard.sh"
    g.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    g.chmod(0o755)
    (cl / "settings.local.json").write_text(
        '{"hooks":{"PreToolUse":[{"hooks":[{"type":"command",'
        '"command":"$CLAUDE_PROJECT_DIR/.claude/hooks/report-only-guard.sh"}]}]}}',
        encoding="utf-8")
    assert vc.check_guard_wiring(tmp_path) == []


def test_guard_wiring_green_on_real_repo():
    assert vc.check_guard_wiring(REPO_ROOT) == []


# ── warn-class checks ────────────────────────────────────────────────────────

def test_ledger_link_warns_on_dangling_sha(tmp_path):
    led = tmp_path / "docs" / "ledger"
    led.mkdir(parents=True)
    (led / "m.md").write_text(
        "| CE-01 | p | adopt | r | prov | rev | tags | `deadbee` |\n", encoding="utf-8")
    warns = vc.check_ledger_links(tmp_path)
    assert any("deadbee" in w for w in warns)


def test_live_registry_warn_when_malformed(tmp_path):
    cur = tmp_path / "knowledge" / "currency"
    cur.mkdir(parents=True)
    (cur / "repo-registry.json").write_text('{"repos": "notdict"}', encoding="utf-8")
    assert vc.check_live_registry(tmp_path) != []
    # Absent registry → no warning.
    (cur / "repo-registry.json").unlink()
    assert vc.check_live_registry(tmp_path) == []


# ── staleness report (warn-only, project specs) ──────────────────────────────

def test_staleness_report_lists_retired_ids_in_project_specs(tmp_path):
    proj = tmp_path / "projects" / "demo"
    proj.mkdir(parents=True)
    (proj / "spec.md").write_text("stack pins claude-3-5-sonnet-latest\n", encoding="utf-8")
    flags = vc.staleness_report(tmp_path)
    assert any("demo" in f and "claude-3-5-sonnet-latest" in f for f in flags)
