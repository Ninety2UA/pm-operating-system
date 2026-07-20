# report-only-guard.sh — companion doc

The PreToolUse backstop for scheduled watcher runs (`/cli-watch`,
`/repo-watch` in `report-only` mode). Ships committed but **unwired**;
setup wires it into `.claude/settings.local.json` (never the committed
`settings.json`) only when the owner chooses an automation home that can
set the marker. Every hook in this repo ships as a triple: script,
this companion doc, and its drill test
(`core/scripts/tests/test_report_only_guard.py`). (Ledger AS-07.)

## The three safety layers (KTD-5)

1. **Restricted tool profile — the necessary layer.** Applied to the
   scheduled invocation itself, per-run: the watcher skills declare
   `disallowed-tools` (portable, any home), and wrapper-launched homes add
   `claude -p ... --permission-mode dontAsk --disallowedTools ...` plus
   settings deny rules. A home that cannot enforce this layer is offered
   only as an explicitly-degraded choice (see `docs/capabilities.md`,
   per-home enforcement table).
2. **This guard — defense in depth.** Keys on `CE_REPORT_ONLY` (set by the
   scheduler on the invocation; hook subprocesses inherit the parent env).
   Interactive sessions (no marker) take the inert fast path — a guard bug
   cannot brick normal editing. Marked runs are fail-closed: unparseable
   payloads, unknown tools, off-allowlist fetch hosts, credential-shaped
   reads, and any write outside `knowledge/currency/` are denied with
   exit 2 (the blocking exit code; exit 1 would not block).
3. **The owner's ledger gate — the real trust boundary.** Even a fully
   escaped report-only run yields only files the owner sees in
   `git status`; adoption happens only through owner-marked ledger lines.

## Wiring (written by setup, local only)

```json
{
  "hooks": {
    "PreToolUse": [
      { "hooks": [ { "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/report-only-guard.sh" } ] }
    ]
  }
}
```

The scheduled invocation (e.g. launchd/cron wrapper) sets the marker:

```bash
CE_REPORT_ONLY=1 claude -p "/cli-watch report-only" \
  --permission-mode dontAsk \
  --disallowedTools Bash \
  --allowed-tools "Read Glob Grep WebSearch WebFetch Write Edit Skill"
```

## Drill (direct-drive, host-independent)

The marker must be set on the **guard** process, not on `printf` — in a
pipeline, an `VAR=val cmd1 | cmd2` prefix binds `VAR` only to `cmd1`, so
put `CE_REPORT_ONLY=1` on the `bash` side of the pipe:

```bash
printf '{"tool_name":"Bash","tool_input":{"command":"rm -rf x"}}' \
  | CE_REPORT_ONLY=1 bash .claude/hooks/report-only-guard.sh; echo $?   # → 2 (denied)
printf '{"tool_name":"Bash","tool_input":{}}' \
  | bash .claude/hooks/report-only-guard.sh; echo $?                     # → 0 (interactive: inert)
```

Full drill matrix: `core/scripts/tests/test_report_only_guard.py`.

## Recovery / notes

- The guard never affects interactive sessions; if a scheduled run is
  wrongly blocked, run it manually (unmarked) and read
  `knowledge/currency/guard.log` for the deny lines.
- `disableAllHooks` would disable this hook — which is why the profile
  (layer 1), not the guard, carries containment.
- The marker is an env var, not a file: nothing a run does to the repo can
  disable the guard mid-run.
