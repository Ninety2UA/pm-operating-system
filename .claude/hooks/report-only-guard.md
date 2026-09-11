# report-only-guard.sh — companion doc

The PreToolUse backstop for scheduled watcher runs (`/cli-watch`,
`/repo-watch` in `report-only` mode). Ships committed but **unwired**; the
owner wires it **by hand** into `.claude/settings.local.json` (never the
committed `settings.json`) when choosing an automation home that can set
the marker — `setup.sh` prints the pointer to this doc and does not write
the block. Every hook in this repo ships as a triple: script, this
companion doc, and its drill test
(`core/scripts/tests/test_report_only_guard.py`). (Ledger AS-07; hardened
in the 2026-09-11 currency wave under R7–R9 and KTD6–KTD7.)

## The three safety layers (KTD-5)

1. **Restricted tool profile — the necessary layer.** Applied to the
   scheduled invocation itself, per-run. The watcher skills declare only
   `allowed-tools` (a pre-approval list, not a restriction), so the
   restriction has to come from the invocation: wrapper-launched homes pass
   `claude -p ... --permission-mode dontAsk --disallowedTools ...` plus
   settings deny rules. A home that cannot enforce this layer is offered
   only as an explicitly-degraded choice (see `docs/capabilities.md`,
   per-home enforcement table).
2. **This guard — defense in depth.** Keys on `CE_REPORT_ONLY` (set by the
   scheduler on the invocation; hook subprocesses inherit the parent env).
   Interactive sessions (no marker) take the inert fast path — a guard bug
   cannot brick normal editing. Marked runs are fail-closed: unparseable or
   stalled payloads, a stalled parser / resolver / `date`, a mid-run
   signal, unknown tools, off-allowlist fetch hosts, credential-shaped
   reads, path-less or out-of-project `Grep`/`Glob`, and any write that is
   not the lock or today's report are denied with exit 2 (the blocking exit
   code; exit 1 would not block).
3. **The owner's ledger gate — the real trust boundary.** Even a fully
   escaped report-only run yields only files the owner sees in
   `git status`; adoption happens only through owner-marked ledger lines.

## Wiring (by hand, local only)

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

The block carries **no `timeout`** on purpose: a command hook that reaches
its timeout is cancelled and the tool call proceeds — fail-open (see
`docs/capabilities.md`, id `hooks.pretooluse`) — so an explicit value could
only lower the platform default of 600 s, which is the ceiling; the guard's
own bounded reads (10 s per external step, next section) are the real
budget, and the validator's guard-wiring check warns when a wired guard
declares any explicit timeout below 600.

The scheduled invocation (e.g. launchd/cron wrapper) sets the marker:

```bash
CE_REPORT_ONLY=1 claude -p "/cli-watch report-only" \
  --permission-mode dontAsk \
  --disallowedTools Bash \
  --allowed-tools "Read Glob Grep WebSearch WebFetch Write Edit Skill"
```

## Stall budget (KTD6)

A guard that hangs is a guard that is skipped. Every external step — the
JSON parser (`python3`), `realpath`, `date`, `tr` — runs behind a process
substitution with stdin and stderr on `/dev/null` and is read with a 10 s
bounded builtin `read -t`; an expired or empty read kills the child and
takes the deny path (exit 2). The host payload is read by a bounded
builtin loop, never `cat`; a host that spends the budget on its final
write, or never closes stdin, is a stall and is denied. `TERM`, `HUP` and
`INT` are trapped into the same deny path, because an untrapped signal
death runs the EXIT trap with status 0 and the host sees 143 — fail-open.
No `sleep`, no `timeout`, no background timer: bash delivers a trapped
signal only after the current foreground command or command substitution
returns (a timer could never interrupt a stalled `$(...)`), but it does
interrupt a blocking `read -t` — both verified on the drill's bash 3.2.57.
A stall inside bash's own startup is outside the script and stays bounded
only by the host default.

## Write fence under the marker (R8)

A report-only run advances no state. The only writable targets are:

| Allowed target | Role |
|---|---|
| `knowledge/currency/currency.lock` | the run lock |
| `knowledge/currency/reports/cli/<today>.md` | today's platform report |
| `knowledge/currency/reports/repo/<today>.md` | today's ecosystem report |

`<today>` is the local **or** the UTC date (`date +%F` / `date -u +%F`), so
a run straddling midnight stays valid while yesterday's report is denied.

Denied and logged: everything else under `knowledge/currency/` —
`cli-baseline.json`, `repo-registry.json`, their `.tmp` siblings,
`guard.log`, `.v2.md` snapshots, prior-dated reports, root-level files,
`reports/<anything else>/`, and the directory itself — plus every path
outside `knowledge/currency/` and every `..` segment. The check runs on the
basename plus the **resolved** parent (never whole-string equality), so
`//`, `./` and case variants cannot dodge a deny; the exact string form is
the fallback when no resolver answers, so a failed `realpath` can never
skip a deny; and an existing target is resolved first, so a report name
that is really a symlink to a state file (or a report directory that is
really a symlink up the tree) is denied. Principle: allowlisted root, depth
floor, resolve-then-check. The fence gates tool calls only: the post-commit
close-out runs unmarked through Python and is unaffected.

## Egress channels under the marker

A scheduled report-only run may fetch only allowlisted hosts via `WebFetch`
(the authority is parsed WHATWG-compatibly — backslash-normalized, userinfo
stripped after the last `@` — so a host masquerade cannot slip an
off-allowlist fetch past the pin). `WebSearch` is **denied** under the
marker: a search query string is an ungated egress channel the allowlist
can't constrain, and delta runs fetch known doc/repo URLs rather than
searching. Open search remains available in an interactive/full run (where
the guard is inert).

`Grep` and `Glob` pass the same credential-path check as `Read` **and** a
path fence: a missing or empty `path`, a `..` segment, or a path that does
not resolve inside `CLAUDE_PROJECT_DIR` is a content-dump-by-pattern route
and is denied (a relative path without `..` counts as inside; an absolute
path must string-prefix the project dir and, when both sides resolve,
realpath-confirm; with the project dir unset an absolute path is denied).
A project-relative, non-credential path is allowed.

## The log

`knowledge/currency/guard.log` is **local and gitignored** (the whole
`knowledge/currency/` tree is) and is never copied into a tracked file. An
allowed `WebFetch` logs the **full URL** (KTD7: receipts reconcile by URL,
not by host) after dropping any userinfo and replacing the values of
secret-shaped query parameters — `token`, `key`, `sig`, `signature`,
`auth`, `password`, `secret`, `access_token`, matched case-insensitively —
with `REDACTED`. Every deny appends a `DENY:` line; the drill asserts that
side effect against a temporary project, so the repo's real log is never
written by tests.

## Drill (direct-drive, host-independent)

The marker must be set on the **guard** process, not on `printf` — in a
pipeline, an `VAR=val cmd1 | cmd2` prefix binds `VAR` only to `cmd1`, so
put `CE_REPORT_ONLY=1` on the `bash` side of the pipe. Point
`CLAUDE_PROJECT_DIR` at a scratch dir that has a `knowledge/currency/` so
the deny line lands there, not in the real log:

```bash
printf '{"tool_name":"Bash","tool_input":{"command":"rm -rf x"}}' \
  | CE_REPORT_ONLY=1 CLAUDE_PROJECT_DIR=/tmp/guard-drill \
    bash .claude/hooks/report-only-guard.sh; echo $?                  # → 2 (denied)
printf '{"tool_name":"Bash","tool_input":{}}' \
  | bash .claude/hooks/report-only-guard.sh; echo $?                  # → 0 (interactive: inert)
```

Full drill matrix: `core/scripts/tests/test_report_only_guard.py` — every
payload against a temporary project, plus the stall, signal, byte-complete
payload, symlink, redacted-URL and wiring-block drills.

## Recovery / notes

- The guard never affects interactive sessions; if a scheduled run is
  wrongly blocked, run it manually (unmarked) and read
  `knowledge/currency/guard.log` for the deny lines.
- A deny that reads `stalled` or `signal received` means the host, the
  interpreter or a resolver did not answer inside the budget — the tool
  call was blocked, not skipped; rerun once the host is idle.
- `disableAllHooks` would disable this hook — which is why the profile
  (layer 1), not the guard, carries containment.
- The marker is an env var, not a file: nothing a run does to the repo can
  disable the guard mid-run.
