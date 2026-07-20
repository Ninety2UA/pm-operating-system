#!/usr/bin/env bash
# Report-only guard — PreToolUse backstop for scheduled watcher runs.
#
# Layer 2 of the unattended-safety design (KTD-5): the restricted tool
# profile on the scheduled invocation is the necessary containment layer;
# this hook is defense-in-depth behind it, and the owner's ledger gate is
# the real trust boundary. Companion doc: report-only-guard.md (same dir).
#
# Discriminator: the scheduler sets CE_REPORT_ONLY=1 on the invocation
# (hook subprocesses inherit the parent environment — verified against the
# hooks docs in docs/capabilities.md, id hooks.env-inheritance). A TTY test
# is NOT available inside a PreToolUse subprocess and is not used.
#
# Semantics:
#   - Marker absent/empty  -> interactive session -> exit 0 before touching
#     anything (a guard bug can never brick normal editing).
#   - Marker set (ANY value, malformed included) -> scheduled report-only
#     semantics, fail-closed: only an explicit allowlist of read/fetch
#     tools passes; Write/Edit only under knowledge/currency/; WebFetch
#     only to allowlisted domains; Bash and every MCP tool are denied.
#   - Exit 2 blocks the tool call (exit 1 would NOT block — hooks docs).
#
# Wired by setup ONLY in .claude/settings.local.json when the owner opts
# into automation; committed-but-unwired is the shipped state and must
# stay green in CI (validator check 11 exempts it; U14's guard-wiring
# check validates the local wiring when present).

# ── Interactive fast path: inert without the scheduler marker ─────────────
if [ -z "${CE_REPORT_ONLY:-}" ]; then
  exit 0
fi

# ── Scheduled run: fail closed from here on ───────────────────────────────
log() {
  echo "[$(date -u +%FT%TZ)] $1" \
    >> "${CLAUDE_PROJECT_DIR:-.}/knowledge/currency/guard.log" 2>/dev/null || true
}

deny() {
  log "DENY: $1"
  echo "report-only guard: $1" >&2
  exit 2
}

allow() {
  log "allow: $1"
  exit 0
}

payload="$(cat 2>/dev/null || true)"
tool="$(printf '%s' "$payload" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
[ -n "$tool" ] || deny "unparseable hook payload (fail-closed under CE_REPORT_ONLY)"

# First file-ish path or URL in tool_input (fail-closed if absent where needed).
path="$(printf '%s' "$payload" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
url="$(printf '%s' "$payload" | sed -n 's/.*"url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"

# Domains a report-only run may fetch (KTD-5 egress pin). Extend per-run
# with CE_FETCH_ALLOW="host1,host2" on the scheduled invocation.
FETCH_ALLOW="code.claude.com platform.claude.com claude.com www.anthropic.com anthropic.com github.com api.github.com raw.githubusercontent.com objects.githubusercontent.com docs.github.com"
if [ -n "${CE_FETCH_ALLOW:-}" ]; then
  FETCH_ALLOW="$FETCH_ALLOW $(printf '%s' "$CE_FETCH_ALLOW" | tr ',' ' ')"
fi

credential_shaped() {
  case "$1" in
    *client_secret*|*token*|*credential*|*.pem|*.key|*.env|*.env.*|*/.ssh/*|*/.aws/*|*/.config/gcloud/*|*/.netrc)
      return 0 ;;
  esac
  return 1
}

case "$tool" in
  Skill|Glob|Grep|WebSearch)
    allow "$tool"
    ;;
  Read)
    if credential_shaped "$path"; then
      deny "Read of credential-shaped path blocked: $path"
    fi
    allow "Read $path"
    ;;
  WebFetch)
    host="$(printf '%s' "$url" | sed -n 's|^[a-z]*://\([^/:]*\).*|\1|p')"
    [ -n "$host" ] || deny "WebFetch with unparseable URL"
    for a in $FETCH_ALLOW; do
      if [ "$host" = "$a" ]; then
        allow "WebFetch $host"
      fi
    done
    deny "WebFetch to off-allowlist host: $host"
    ;;
  Write|Edit|NotebookEdit)
    # Reject path traversal first: a `..` segment could escape the fence
    # (e.g. knowledge/currency/../../AGENTS.md matches the glob below but
    # resolves outside the report scope).
    case "$path" in
      *..*)
        deny "$tool with '..' in path (traversal): $path"
        ;;
    esac
    case "$path" in
      */knowledge/currency/*|knowledge/currency/*)
        allow "$tool $path"
        ;;
      *)
        deny "$tool outside knowledge/currency/: ${path:-<no path>}"
        ;;
    esac
    ;;
  *)
    # Bash, every mcp__* tool (including mutating manager-ai paths like
    # prune_completed_tasks), Agent spawns, and anything unrecognized.
    deny "tool not in the report-only profile: $tool"
    ;;
esac
