"""Fixture-driven tests for the U14 enforcement checks (test-first, KTD-4).
Each check is a pure function over a root path or text inputs, so it is
exercised on synthetic fixtures here and wired into the sequential
validator against the real repo separately.
"""
import pytest
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
    # 2026-09 defaults (CLI-2026-09-11-22 / -103)
    assert "claude-fable-5-1" in vc.CURRENT_MODEL_IDS
    assert "claude-opus-5" in vc.CURRENT_MODEL_IDS


def test_roster_passes_2026_09_default_ids(tmp_path):
    sk = tmp_path / ".claude" / "skills" / "ok"
    sk.mkdir(parents=True)
    (sk / "SKILL.md").write_text(
        "---\nname: ok\nmodel: opus\n---\nPins claude-opus-5 and claude-fable-5-1.\n",
        encoding="utf-8")
    assert vc.check_model_roster(tmp_path) == []


# ── BOM (fail) — CLI-2026-09-11-60 ────────────────────────────────────────────

def test_bom_flags_frontmatter_file_starting_with_bom(tmp_path):
    sk = tmp_path / ".claude" / "skills" / "bomd"
    sk.mkdir(parents=True)
    (sk / "SKILL.md").write_bytes(
        b"\xef\xbb\xbf---\nname: bomd\nmodel: sonnet\n---\nbody\n")
    fails = vc.check_bom(tmp_path)
    assert len(fails) == 1 and "bomd" in fails[0] and "BOM" in fails[0]


def test_bom_ignores_clean_file_and_covers_agents_md(tmp_path):
    sk = tmp_path / ".claude" / "skills" / "clean"
    sk.mkdir(parents=True)
    (sk / "SKILL.md").write_text("---\nname: clean\n---\nbody\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_bytes(b"\xef\xbb\xbf# Agents\n")
    fails = vc.check_bom(tmp_path)
    assert [f for f in fails if "clean" in f] == []
    assert any(f.startswith("AGENTS.md") for f in fails)


def test_bom_green_on_real_repo():
    assert vc.check_bom(REPO_ROOT) == []


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


def test_secret_scan_catches_provider_key_shapes(tmp_path):
    led = tmp_path / "docs" / "ledger"
    led.mkdir(parents=True)
    secrets = [
        "sk-ant-api03-Xh2mP9qL4vN8rT1wY6bC3dF5gJ7kM0nQ-abcdEFGH_1234",
        "github_pat_11ABCDEFG0abcdefghijKLMNOP_qrstuvwxyz012345",
        "AIzaSyD-9tSrke72PouQMnMX-a7eZSW0jkFMBWYxx",
        "sk-proj-abcDEF12-ghiJKL34-mnoPQR56-stuVWX78",
        "password = hunter2secretvalue",
        "access_token: abcdefgh12345678",
    ]
    for s in secrets:
        (led / "x.md").write_text(s + "\n", encoding="utf-8")
        assert vc.check_tracked_secret_scan(tmp_path) != [], f"missed: {s}"
    # never echoes the raw secret into the message
    (led / "x.md").write_text(secrets[0] + "\n", encoding="utf-8")
    for f in vc.check_tracked_secret_scan(tmp_path):
        assert secrets[0] not in f


def test_secret_scan_no_false_positive_on_prose_and_shas(tmp_path):
    led = tmp_path / "docs" / "ledger"
    led.mkdir(parents=True)
    (led / "x.md").write_text(
        "provenance `a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2` and the\n"
        "client_secret*.json gitignore rule, plus `# secret-scan: allow`.\n"
        "The secret sauce is respectful rationales.\n", encoding="utf-8")
    assert vc.check_tracked_secret_scan(tmp_path) == []


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


def test_guard_wired_with_quoted_path_passes(tmp_path):
    cl = tmp_path / ".claude"
    (cl / "hooks").mkdir(parents=True)
    g = cl / "hooks" / "report-only-guard.sh"
    g.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    g.chmod(0o755)
    (cl / "settings.local.json").write_text(
        '{"hooks":{"PreToolUse":[{"hooks":[{"type":"command",'
        '"command":"\\"$CLAUDE_PROJECT_DIR/.claude/hooks/report-only-guard.sh\\""}]}]}}',
        encoding="utf-8")
    assert vc.check_guard_wiring(tmp_path) == []


def test_guard_deleted_but_still_wired_fails(tmp_path):
    cl = tmp_path / ".claude"
    (cl / "hooks").mkdir(parents=True)
    # guard file intentionally absent, but settings still wires it
    (cl / "settings.local.json").write_text(
        '{"hooks":{"PreToolUse":[{"hooks":[{"type":"command",'
        '"command":"$CLAUDE_PROJECT_DIR/.claude/hooks/report-only-guard.sh"}]}]}}',
        encoding="utf-8")
    assert vc.check_guard_wiring(tmp_path) != []


def test_guard_wiring_tolerates_malformed_settings_shape(tmp_path):
    cl = tmp_path / ".claude"
    (cl / "hooks").mkdir(parents=True)
    (cl / "hooks" / "report-only-guard.sh").write_text("x", encoding="utf-8")
    for bad in ('{"hooks": "not a dict"}',
                '{"hooks": {"PreToolUse": "not a list"}}',
                '{"hooks": {"PreToolUse": [{"hooks": "nope"}]}}',
                '[]'):
        (cl / "settings.local.json").write_text(bad, encoding="utf-8")
        # must not raise, and must not fail on a shape it can't interpret
        assert vc.check_guard_wiring(tmp_path) == []


def test_guard_wiring_green_on_real_repo():
    assert vc.check_guard_wiring(REPO_ROOT) == []


# ── MODEL_ID_RE precision (P2) ───────────────────────────────────────────────

def test_model_id_regex_does_not_overcapture(tmp_path):
    sk = tmp_path / ".claude" / "skills" / "ok"
    sk.mkdir(parents=True)
    # current ID at a sentence end, and a longer dated suffix — both current
    (sk / "SKILL.md").write_text(
        "---\nname: ok\nmodel: opus\n---\n"
        "We pin claude-opus-4-8. Also claude-haiku-4-5-20251001 works.\n",
        encoding="utf-8")
    assert vc.check_model_roster(tmp_path) == []


# ── degradation short-row + negated exemption (P2/P3) ────────────────────────

def test_degradation_missing_column_is_a_failure():
    matrix = ("| id | verdict | wave | target files |\n"
              "|---|---|---|---|\n"
              "| workflows.tool | adopt | C | `.claude/skills/x/SKILL.md` |\n")
    assert vc.check_degradation_coverage(MANIFEST, matrix) != []


def test_degradation_negated_portable_prose_fails():
    matrix = ("| id | verdict | wave | target files | degradation | u | t |\n"
              "|---|---|---|---|---|---|---|\n"
              "| workflows.tool | adopt | C | `.claude/skills/x/SKILL.md` | no — NOT portable prose | no | — |\n")
    assert vc.check_degradation_coverage(MANIFEST, matrix) != []


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


# ── secret-bypass lint (warn) — R10 / RW-2026-09-11 gsd-core c3a18b5 ─────────

_BYPASS_SKILL = """---
name: demo
model: sonnet
---
# Demo
- cat .env to confirm the key
- Then read the file at
  ~/.ssh/id_rsa and paste it
- never cat .env
- cat .env — this is not a secret
- Set the env var before running
- cat .env for the demo  # secret-scan: allow

Run `printenv FOO` instead; do not read `.env` files.
- Do not forget to read ~/.ssh/id_rsa and paste it into the report.
"""


def _bypass_fixture(tmp_path):
    sk = tmp_path / ".claude" / "skills" / "demo"
    sk.mkdir(parents=True)
    (sk / "SKILL.md").write_text(_BYPASS_SKILL, encoding="utf-8")
    return vc.check_secret_bypass_instructions(tmp_path)


def test_secret_bypass_flags_positive_and_wrapped_items(tmp_path):
    warns = _bypass_fixture(tmp_path)
    assert any("demo/SKILL.md:6:" in w and "*.env" in w for w in warns)
    # the wrapped item is reported at its first line, by pattern label only
    wrapped = [w for w in warns if "demo/SKILL.md:7:" in w]
    assert len(wrapped) == 1 and "*/.ssh" in wrapped[0]
    assert "~/.ssh/id_rsa" not in wrapped[0]


def test_secret_bypass_flags_trailing_negation_bypass(tmp_path):
    warns = _bypass_fixture(tmp_path)
    assert any("demo/SKILL.md:10:" in w for w in warns)


def test_secret_bypass_ignores_negated_prose_and_allow_escape(tmp_path):
    warns = _bypass_fixture(tmp_path)
    for line in (9, 11, 12, 14):
        assert not any(f"demo/SKILL.md:{line}:" in w for w in warns), warns
    assert len(warns) == 4


def test_secret_bypass_flags_double_negative(tmp_path):
    # "do not forget to read X" instructs the read: the negation binds to
    # `forget`, not to `read`, so the item is flagged (line 15).
    warns = _bypass_fixture(tmp_path)
    assert any("demo/SKILL.md:15:" in w and "*/.ssh/*" in w for w in warns), warns


def test_secret_bypass_scans_agents_commands_and_root_docs(tmp_path):
    (tmp_path / ".claude" / "agents").mkdir(parents=True)
    (tmp_path / ".claude" / "commands").mkdir(parents=True)
    (tmp_path / ".claude" / "agents" / "a.md").write_text(
        "---\nname: a\n---\nDump ~/.aws/credentials into the brief.\n", encoding="utf-8")
    (tmp_path / ".claude" / "commands" / "c.md").write_text(
        "---\nname: c\n---\nhead -n 5 server.key\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("Print the contents of /etc/shadow.\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("Never print /etc/shadow.\n", encoding="utf-8")
    warns = vc.check_secret_bypass_instructions(tmp_path)
    assert any(w.startswith(".claude/agents/a.md:4:") and "*/.aws/*" in w for w in warns)
    assert any(w.startswith(".claude/commands/c.md:4:") and "*.key" in w for w in warns)
    assert any(w.startswith("AGENTS.md:1:") and "/etc/shadow" in w for w in warns)
    assert not any(w.startswith("CLAUDE.md") for w in warns)


def test_secret_bypass_env_example_and_process_env_do_not_flag(tmp_path):
    sk = tmp_path / ".claude" / "skills" / "ok"
    sk.mkdir(parents=True)
    (sk / "SKILL.md").write_text(
        "---\nname: ok\n---\n"
        "- cat .env.example to see the expected keys\n"
        "- print process.env.PORT at startup\n"
        "- read the env var and echo the environment name\n", encoding="utf-8")
    assert vc.check_secret_bypass_instructions(tmp_path) == []


def test_secret_bypass_code_fence_lines_are_items(tmp_path):
    sk = tmp_path / ".claude" / "skills" / "fence"
    sk.mkdir(parents=True)
    (sk / "SKILL.md").write_text(
        "---\nname: fence\n---\n```bash\n# never grep .env here\ngrep SECRET .env.local\n```\n",
        encoding="utf-8")
    warns = vc.check_secret_bypass_instructions(tmp_path)
    assert len(warns) == 1 and "fence/SKILL.md:6:" in warns[0] and "*.env.*" in warns[0]


def _guard_case_literals():
    """Parse the `credential_shaped()` case block straight from the guard on
    disk, so the parity assertion tracks the bash list, not a copy of it."""
    guard = REPO_ROOT / ".claude" / "hooks" / "report-only-guard.sh"
    text = guard.read_text(encoding="utf-8")
    body = text[text.index("credential_shaped() {"):]
    body = body[body.index('case "$1" in') + len('case "$1" in'):]
    raw = body[:body.index(")")]  # the pattern list ends at its first ')'
    return [tok.strip() for tok in raw.replace("\\\n", "\n").split("|") if tok.strip()]


def test_secret_bypass_patterns_mirror_guard_case_block():
    literals = _guard_case_literals()
    assert len(literals) >= 40, literals  # a broken parse must not pass vacuously
    assert len(literals) == len(set(literals))
    assert set(literals) == set(vc.CREDENTIAL_PATH_PATTERNS)


def test_secret_bypass_green_on_real_repo():
    assert vc.check_secret_bypass_instructions(REPO_ROOT) == []


# ── backup coverage (warn) — R11 ─────────────────────────────────────────────

def _git(*args, cwd):
    import subprocess
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                    "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main",
                    *args], cwd=cwd, check=True, capture_output=True, timeout=30)


def _work_repo(tmp_path, name="work"):
    d = tmp_path / name
    d.mkdir()
    _git("init", "-q", "-b", "main", cwd=d)
    (d / "f.txt").write_text("x\n", encoding="utf-8")
    _git("add", "f.txt", cwd=d)
    _git("commit", "-qm", "init", cwd=d)
    return d


def _bare_origin(tmp_path):
    bare = tmp_path / "origin.git"
    bare.mkdir()
    _git("init", "-q", "--bare", "-b", "main", cwd=bare)
    return bare


def test_backup_warns_without_origin_remote(tmp_path):
    d = _work_repo(tmp_path)
    warns = vc.check_backup_coverage(d)
    assert len(warns) == 1 and "origin" in warns[0]


def test_backup_silent_when_main_in_sync_and_warns_when_ahead(tmp_path):
    d = _work_repo(tmp_path)
    _git("remote", "add", "origin", str(_bare_origin(tmp_path)), cwd=d)
    _git("push", "-q", "-u", "origin", "main", cwd=d)
    assert vc.check_backup_coverage(d) == []
    (d / "g.txt").write_text("y\n", encoding="utf-8")
    _git("add", "g.txt", cwd=d)
    _git("commit", "-qm", "local only", cwd=d)
    warns = vc.check_backup_coverage(d)
    assert len(warns) == 1 and "ahead" in warns[0] and "main" in warns[0]


def test_backup_silent_without_upstream_and_when_detached(tmp_path):
    d = _work_repo(tmp_path)
    _git("remote", "add", "origin", str(_bare_origin(tmp_path)), cwd=d)
    assert vc.check_backup_coverage(d) == []  # origin present, main never pushed
    _git("checkout", "-q", "--detach", cwd=d)
    assert vc.check_backup_coverage(d) == []


def test_backup_undetermined_outside_a_repo_and_without_git(tmp_path, monkeypatch):
    """An unrunnable probe says so (R7): silence there reads as "backed up"
    to every caller."""
    off = vc.check_backup_coverage(tmp_path / "not-a-repo-yet")
    assert len(off) == 1 and "could not determine" in off[0]
    d = _work_repo(tmp_path)  # would warn (no origin) — unless git is absent
    nobin = tmp_path / "nobin"
    nobin.mkdir()
    monkeypatch.setenv("PATH", str(nobin))
    nogit = vc.check_backup_coverage(d)
    assert len(nogit) == 1 and "could not determine" in nogit[0]


def test_backup_green_on_real_repo():
    # This check's real-repo output depends on the clone's push state (an
    # unpushed local `main` legitimately warns), so the real-repo smoke
    # asserts only the clone-invariant half: the repository has an `origin`
    # remote. The tmp_path fixtures above pin both warn and both silent paths.
    warns = vc.check_backup_coverage(REPO_ROOT)
    assert not any(w.startswith("no `origin` remote") for w in warns), warns


# ── guard-wiring timeout notice (warn) — R7 / KTD6 ───────────────────────────

def _wire_guard(tmp_path, timeout=None):
    cl = tmp_path / ".claude"
    (cl / "hooks").mkdir(parents=True, exist_ok=True)
    g = cl / "hooks" / "report-only-guard.sh"
    g.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    g.chmod(0o755)
    extra = "" if timeout is None else f',"timeout":{timeout}'
    (cl / "settings.local.json").write_text(
        '{"hooks":{"PreToolUse":[{"hooks":[{"type":"command",'
        '"command":"$CLAUDE_PROJECT_DIR/.claude/hooks/report-only-guard.sh"'
        + extra + '}]}]}}', encoding="utf-8")


def test_guard_timeout_below_600_warns(tmp_path):
    _wire_guard(tmp_path, timeout=120)
    warns = vc.check_guard_wiring_timeout(tmp_path)
    assert len(warns) == 1 and "120" in warns[0] and "600" in warns[0]
    assert vc.check_guard_wiring(tmp_path) == []  # the fail check is unchanged


def test_guard_timeout_600_or_absent_is_silent(tmp_path):
    _wire_guard(tmp_path, timeout=600)
    assert vc.check_guard_wiring_timeout(tmp_path) == []
    _wire_guard(tmp_path)
    assert vc.check_guard_wiring_timeout(tmp_path) == []


def test_guard_timeout_green_on_real_repo():
    assert vc.check_guard_wiring_timeout(REPO_ROOT) == []


# ── staleness report: watcher reports + progress ratchet (local mode) ────────

def _completed_report(tmp_path, watcher, day):
    d = tmp_path / "knowledge" / "currency" / "reports" / watcher
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{day}.md").write_text(
        f"# report {day}\n\n<!-- report-complete: {day} -->\n", encoding="utf-8")


def test_watcher_staleness_lists_report_older_than_14_days(tmp_path):
    from datetime import date, timedelta
    today = date(2026, 9, 11)
    _completed_report(tmp_path, "cli", (today - timedelta(days=20)).isoformat())
    _completed_report(tmp_path, "repo", (today - timedelta(days=3)).isoformat())
    flags = vc.watcher_report_staleness(tmp_path, today=today)
    assert len(flags) == 1 and flags[0].startswith("cli:") and "20 days" in flags[0]


def test_watcher_staleness_silent_without_reports_or_when_fresh(tmp_path):
    from datetime import date
    today = date(2026, 9, 11)
    assert vc.watcher_report_staleness(tmp_path, today=today) == []
    _completed_report(tmp_path, "cli", "2026-09-01")
    # an older completed report plus a fresh one: only the newest counts
    _completed_report(tmp_path, "cli", "2026-07-01")
    assert vc.watcher_report_staleness(tmp_path, today=today) == []


def _project(tmp_path, name, status, log):
    p = tmp_path / "projects" / name
    p.mkdir(parents=True)
    (p / "idea.md").write_text(
        f"---\ntitle: {name}\nproject_status: {status}\n---\n# {name}\n\n"
        f"## Progress Log\n{log}", encoding="utf-8")


def test_progress_ratchet_lists_status_without_log_line(tmp_path):
    _project(tmp_path, "x", "active", "")
    _project(tmp_path, "y", "active", "- 2026-09-01: Activated after the pre-mortem.\n")
    _project(tmp_path, "z", "archived", "- 2026-09-01: Started.\n- 2026-09-02: Archived — dead.\n")
    _project(tmp_path, "w", "idea", "")  # idea/evaluating are not ratcheted
    flags = vc.project_progress_ratchet(tmp_path)
    assert flags == ["projects/x/idea.md"]


def test_staleness_sections_shape(tmp_path):
    sections = vc.staleness_sections(tmp_path)
    titles = [s[0] for s in sections]
    assert len(sections) == 5 and all(isinstance(s[1], list) for s in sections)
    assert any("model" in t.lower() for t in titles)
    assert any("watcher" in t.lower() for t in titles)
    assert any("progress" in t.lower() for t in titles)
    assert any("template" in t.lower() for t in titles)
    assert any("source" in t.lower() for t in titles)


# ── privacy-placement (warn) — R5 / RW-2026-09-12-5 ──────────────────────────

def _ignored_but_tracked(tmp_path):
    """A repo whose ignore rules cover a file that is already in the index —
    the exact state `.gitignore` cannot undo on its own."""
    d = _work_repo(tmp_path)
    (d / "secrets.md").write_text("personal\n", encoding="utf-8")
    _git("add", "secrets.md", cwd=d)
    _git("commit", "-qm", "track it", cwd=d)
    (d / ".gitignore").write_text("secrets.md\n", encoding="utf-8")
    _git("add", ".gitignore", cwd=d)
    _git("commit", "-qm", "ignore it", cwd=d)
    return d


def test_privacy_placement_flags_tracked_but_ignored_file(tmp_path):
    d = _ignored_but_tracked(tmp_path)
    warns = vc.check_privacy_placement(d)
    assert len(warns) == 1, warns
    assert "secrets.md" in warns[0]
    assert ".gitignore:1:secrets.md" in warns[0]      # the rule that fired
    assert "git rm --cached" in warns[0]              # the remedy


def test_privacy_placement_silent_when_negated_and_loud_off_repo(tmp_path):
    d = _ignored_but_tracked(tmp_path)
    (d / ".gitignore").write_text("secrets.md\n!secrets.md\n", encoding="utf-8")
    _git("add", ".gitignore", cwd=d)
    _git("commit", "-qm", "negate it", cwd=d)
    assert vc.check_privacy_placement(d) == []
    off = vc.check_privacy_placement(tmp_path / "not-a-repo-yet")
    assert len(off) == 1 and "could not determine" in off[0]


def test_privacy_placement_ignores_the_users_global_exclude(tmp_path):
    """The check must answer the same on every machine, so a path ignored
    only by the user's global exclude file is not tracked-but-ignored."""
    d = _work_repo(tmp_path)
    (d / "notes.md").write_text("x\n", encoding="utf-8")
    _git("add", "notes.md", cwd=d)
    _git("commit", "-qm", "track", cwd=d)
    glob_ex = tmp_path / "global-exclude"
    glob_ex.write_text("notes.md\n", encoding="utf-8")
    _git("config", "core.excludesFile", str(glob_ex), cwd=d)
    assert vc.check_privacy_placement(d) == []


def test_privacy_placement_green_on_real_repo():
    assert vc.check_privacy_placement(REPO_ROOT) == []


# ── tree-hygiene (warn) — R6 / RW-2026-09-12-6 ───────────────────────────────

def test_tree_hygiene_flags_tracked_symlink_without_leaking_home(tmp_path):
    import os
    from pathlib import Path as _P
    d = _work_repo(tmp_path)
    os.symlink(str(_P.home() / "private" / "keys"), d / "link")
    _git("add", "link", cwd=d)
    warns = vc.check_tracked_tree_hygiene(d)
    assert len(warns) == 1, warns
    assert "link" in warns[0] and "symlink" in warns[0]
    assert "~/private/keys" in warns[0]
    assert "/Users/" not in warns[0] and "/home/" not in warns[0]


def test_tree_hygiene_redacts_a_relative_target_that_escapes_the_repo(tmp_path):
    """A stored target such as `../../Users/<name>/.ssh/id_rsa` is neither
    absolute nor under the home directory, so it used to print verbatim
    (review finding); it must be named without being shown."""
    import os
    d = _work_repo(tmp_path)
    os.symlink("../../Users/someone/.ssh/id_rsa", d / "link")
    _git("add", "link", cwd=d)
    warns = vc.check_tracked_tree_hygiene(d)
    assert len(warns) == 1, warns
    assert "relative target outside the repository" in warns[0]
    assert "someone" not in warns[0] and "id_rsa" not in warns[0]


def test_tree_hygiene_flags_case_folding_collision(tmp_path):
    import subprocess as sp
    d = _work_repo(tmp_path)
    blob = sp.run(["git", "hash-object", "-w", "--stdin"], cwd=d, input=b"x\n",
                  capture_output=True, timeout=30).stdout.decode().strip()
    for name in ("Notes.md", "notes.md"):
        _git("update-index", "--add", "--cacheinfo", f"100644,{blob},{name}", cwd=d)
    warns = vc.check_tracked_tree_hygiene(d)
    assert len(warns) == 1, warns
    assert "Notes.md" in warns[0] and "notes.md" in warns[0]
    assert "case" in warns[0].lower()


def test_tree_hygiene_green_on_real_repo():
    assert vc.check_tracked_tree_hygiene(REPO_ROOT) == []


# ── template tokens (--staleness-report section) — CE-U-11 / RW-2026-09-12-9 ─

_TOKEN_DOC = """---
title: Demo
due_date: [YYYY-MM-DD]
---
Inline `[YYYY-MM-DD]` is documentation, not an unfilled field.

````
```json
{"created_date": "[YYYY-MM-DD]"}
```
[see categories]
````

Still unfilled: [Project name] here.
"""

_TOKEN_DOC2 = """```
```json
[Actionable task name]
```
[P0|P1|P2|P3]
"""


def test_template_tokens_masks_code_and_flags_prose_and_frontmatter(tmp_path):
    t = tmp_path / "tasks"
    t.mkdir()
    (t / "demo.md").write_text(_TOKEN_DOC, encoding="utf-8")
    flags = vc.check_template_tokens(tmp_path)
    assert len(flags) == 2, flags
    assert flags[0].startswith("tasks/demo.md:3:") and "[YYYY-MM-DD]" in flags[0]
    assert flags[1].startswith("tasks/demo.md:14:") and "[Project name]" in flags[1]


def test_template_tokens_info_string_line_is_not_a_closing_fence(tmp_path):
    p = tmp_path / "projects" / "demo"
    p.mkdir(parents=True)
    (p / "idea.md").write_text(_TOKEN_DOC2, encoding="utf-8")
    flags = vc.check_template_tokens(tmp_path)
    assert len(flags) == 1, flags
    assert flags[0].startswith("projects/demo/idea.md:5:")
    assert "[P0|P1|P2|P3]" in flags[0]


def test_template_tokens_flags_unresolved_mustache(tmp_path):
    t = tmp_path / "tasks"
    t.mkdir()
    (t / "m.md").write_text("Owner is {{owner}} today.\n", encoding="utf-8")
    flags = vc.check_template_tokens(tmp_path)
    assert len(flags) == 1 and "{{owner}}" in flags[0]


# ── source pointers (--staleness-report section) — GB-U-16 / RW-2026-09-12-10 ─

def _artifact(tmp_path, rel, text):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_source_pointers_flags_missing_pointer_and_honours_exemption(tmp_path):
    _artifact(tmp_path, "knowledge/session-reviews/2026/09/12_build.md",
              "---\ntitle: Build\n---\n# Build\n")
    _artifact(tmp_path, "knowledge/session-reviews/2026/09/11_plan.md",
              "---\ntitle: Plan\nsources_exempt: true  # transcript-only session\n---\n")
    flags = vc.check_source_pointers(tmp_path)
    assert len(flags) == 1, flags
    assert flags[0].startswith("knowledge/session-reviews/2026/09/12_build.md:")
    assert "sources:" in flags[0]


def test_source_pointers_flags_an_empty_sources_list(tmp_path):
    """`sources: []` and a bare `sources:` key name no source at all, so they
    are missing pointers, not compliant ones (review finding)."""
    _artifact(tmp_path, "knowledge/session-reviews/2026/09/12_empty.md",
              "---\ntitle: Empty\nsources: []\n---\n# Empty\n")
    _artifact(tmp_path, "knowledge/session-reviews/2026/09/12_bare.md",
              "---\ntitle: Bare\nsources:\n---\n# Bare\n")
    flags = vc.check_source_pointers(tmp_path)
    assert len(flags) == 2, flags
    assert all("no `sources:` pointer" in f for f in flags)


def test_source_pointers_flags_vanished_source_and_passes_a_live_one(tmp_path):
    _artifact(tmp_path, "knowledge/journals/2026/09/11.md", "# day\n")
    _artifact(tmp_path, "knowledge/journals/2026/weekly/W37.md",
              "---\nsources:\n  - knowledge/journals/2026/09/11.md\n"
              "  - knowledge/journals/2026/09/09.md\n---\n# Week 37\n")
    _artifact(tmp_path, "knowledge/journals/2026/quarterly/Q3.md",
              "---\nsources:\n  - knowledge/journals/2026/weekly/W37.md\n---\n")
    flags = vc.check_source_pointers(tmp_path)
    assert len(flags) == 1, flags
    assert flags[0].startswith("knowledge/journals/2026/weekly/W37.md:4:")
    assert "09/09.md" in flags[0] and "no longer exists" in flags[0]


def test_source_pointers_exemption_without_a_reason_still_flags(tmp_path):
    _artifact(tmp_path, "knowledge/session-reviews/2026/09/12_x.md",
              "---\nsources_exempt: true\n---\n")
    flags = vc.check_source_pointers(tmp_path)
    assert len(flags) == 1 and "reason" in flags[0]


# ── subprocess timeouts (validate.py) — R8 / GSD-U-11 / RW-2026-09-12-8 ──────
#
# One validator run under a stub PATH serves all three assertions: each stall
# costs its own budget in wall time (10 s + 10 s + 30 s), so three separate
# runs would triple that for no extra coverage. Each stub stalls only on the
# argument shape its check uses and delegates everything else to the real
# binary, so no other check changes behaviour.

def _stub(dirpath, name, body):
    p = dirpath / name
    p.write_text(body, encoding="utf-8")
    p.chmod(0o755)
    return p


@pytest.fixture(scope="module")
def stalled_validator(tmp_path_factory):
    import os
    import shutil
    import subprocess as sp
    import sys
    stubs = tmp_path_factory.mktemp("stalled-bin")
    real_which = shutil.which("which")
    real_git = shutil.which("git")
    assert real_which and real_git, "drill needs the real which/git to delegate to"
    _stub(stubs, "which",
          "#!/bin/sh\n"
          "# check 13 looks up the .mcp.json server command; stall only there.\n"
          'case "$1" in uv) exec sleep 45 ;; esac\n'
          f'exec {real_which} "$@"\n')
    _stub(stubs, "git",
          "#!/bin/sh\n"
          "# check 17 lists tracked markdown; stall only on that shape.\n"
          'for a in "$@"; do case "$a" in *.md) exec sleep 45 ;; esac; done\n'
          f'exec {real_git} "$@"\n')
    _stub(stubs, "uv", "#!/bin/sh\nexec sleep 45\n")
    proc = sp.run(
        [sys.executable, str(REPO_ROOT / "core/scripts/validate.py")],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=240,
        env={**os.environ, "PATH": f"{stubs}{os.pathsep}{os.environ['PATH']}"},
    )
    return proc


def test_stalled_which_is_a_named_failure_not_a_hang(stalled_validator):
    assert stalled_validator.returncode != 0
    assert "`which uv` timed out after 10s" in stalled_validator.stdout


def test_stalled_git_fails_check_17_without_a_green_link_scan(stalled_validator):
    out = stalled_validator.stdout
    assert "`git ls-files` timed out after 10s" in out
    # The link / marker / noise scans must not report a clean sweep off an
    # emptied file list.
    assert "broken link" not in out


@pytest.fixture(scope="module")
def failed_git_validator(tmp_path_factory):
    """A `git ls-files` that exits non-zero (not a repository, or a broken
    index) must fail check 17 by name, never feed checks 17-19 an empty list
    they would report as three clean sweeps (review finding: the timeout was
    the only guarded failure)."""
    import os
    import shutil
    import subprocess as sp
    import sys
    stubs = tmp_path_factory.mktemp("failed-git-bin")
    real_git = shutil.which("git")
    assert real_git, "drill needs the real git to delegate to"
    _stub(stubs, "git",
          "#!/bin/sh\n"
          "# check 17 lists tracked markdown; fail only on that shape.\n"
          'for a in "$@"; do case "$a" in *.md) echo "fatal: not a git repository" >&2; exit 128 ;; esac; done\n'
          f'exec {real_git} "$@"\n')
    return sp.run(
        [sys.executable, str(REPO_ROOT / "core/scripts/validate.py")],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=240,
        env={**os.environ, "PATH": f"{stubs}{os.pathsep}{os.environ['PATH']}"},
    )


def test_failed_git_listing_fails_check_17_without_a_green_link_scan(failed_git_validator):
    out = failed_git_validator.stdout
    assert failed_git_validator.returncode != 0
    assert "`git ls-files` exited 128" in out
    assert "broken link" not in out


def test_stalled_uv_reports_the_import_budget_not_a_traceback(stalled_validator):
    out, err = stalled_validator.stdout, stalled_validator.stderr
    assert "server.py import timed out after 30s" in out
    assert "Traceback" not in out and "Traceback" not in err
