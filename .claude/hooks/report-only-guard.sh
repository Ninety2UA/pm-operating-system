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

# Extract fields with a REAL JSON parser, not regex over raw bytes: a greedy
# regex picks the LAST "tool_name" (a nested key inside tool_input would
# spoof it), and raw bytes don't decode JSON escapes. tool_name comes from
# the top-level object; file_path/path/url from tool_input only. Each field
# is emitted base64-encoded on its own line so no value (paths with spaces,
# tabs, newlines) can break the framing. python3 is already a dependency
# (resolve_path); if it is missing or the payload doesn't parse, fail closed.
_fields="$(printf '%s' "$payload" | python3 -c '
import json, sys, base64
try:
    d = json.load(sys.stdin)
    assert isinstance(d, dict)
except Exception:
    sys.exit(3)
ti = d.get("tool_input")
if not isinstance(ti, dict):
    ti = {}
def b(v):
    return base64.b64encode((v if isinstance(v, str) else "").encode()).decode()
print(b(d.get("tool_name")))
print(b(ti.get("file_path")))
print(b(ti.get("path")))
print(b(ti.get("url")))
' 2>/dev/null)" || deny "unparseable hook payload (fail-closed under CE_REPORT_ONLY)"

# Pick each base64 line by number (sed preserves empty lines, which `read`
# with a whitespace IFS would collapse; portable to bash 3.2 with no arrays).
_decode() { printf '%s\n' "$_fields" | sed -n "${1}p" | base64 --decode 2>/dev/null; }
tool="$(_decode 1)"
path="$(_decode 2)"
gpath="$(_decode 3)"
url="$(_decode 4)"

[ -n "$tool" ] || deny "unparseable hook payload (fail-closed under CE_REPORT_ONLY)"

# Domains a report-only run may fetch (KTD-5 egress pin). Extend per-run
# with CE_FETCH_ALLOW="host1,host2" on the scheduled invocation.
FETCH_ALLOW="code.claude.com platform.claude.com claude.com www.anthropic.com anthropic.com github.com api.github.com raw.githubusercontent.com objects.githubusercontent.com docs.github.com"
if [ -n "${CE_FETCH_ALLOW:-}" ]; then
  FETCH_ALLOW="$FETCH_ALLOW $(printf '%s' "$CE_FETCH_ALLOW" | tr ',' ' ')"
fi

credential_shaped() {
  # Credential-bearing directories and filenames. Word-shaped tokens
  # (secret/token/password/credential/apikey) require a credential-ish
  # extension so a benign path like a `secret-scan` doc is not denied,
  # while the specific dotfiles/keys below match by location or name.
  case "$1" in
    */.ssh|*/.ssh/*|*id_rsa*|*id_ed25519*|*id_ecdsa*|*id_dsa*|\
    */.aws|*/.aws/*|*/.config/gcloud|*/.config/gcloud/*|*/.config/gh|*/.config/gh/*|\
    */.gnupg|*/.gnupg/*|*/.netrc|*/.pgpass|*.htpasswd|\
    */.docker/config.json|*/.kube/config|*/.kube|\
    */.zsh_history|*/.bash_history|*/.python_history|*/.node_repl_history|\
    */.git-credentials|*/.npmrc|*/.pypirc|\
    /etc/shadow|/etc/gshadow|/etc/master.passwd|\
    *.tfstate|*.tfstate.*|\
    *.pem|*.key|*.p12|*.pfx|*.gpg|*.asc|*.env|*.env.*|\
    *client_secret*|\
    *secret*.json|*secret*.txt|*secret*.yaml|*secret*.yml|*secret*.env|\
    *token*.json|*token*.txt|*-token|*_token|\
    *password*.json|*password*.txt|*credential*.json|*apikey*|*api_key*)
      return 0 ;;
  esac
  return 1
}

# Portable realpath: GNU `realpath -m`, else BSD `realpath`, else python3.
resolve_path() {
  realpath -m "$1" 2>/dev/null || realpath "$1" 2>/dev/null \
    || python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "$1" 2>/dev/null \
    || printf ''
}

case "$tool" in
  Skill)
    allow "$tool"
    ;;
  WebSearch)
    # A search query string is an ungated egress channel. A scheduled
    # report-only run fetches known doc/repo URLs via WebFetch and does not
    # need open search, so deny it here (open search is a full/interactive
    # operation). Documented in report-only-guard.md.
    deny "WebSearch (ungated egress) not permitted in a report-only run"
    ;;
  Read|Grep|Glob)
    # Grep (output_mode=content) and Glob (filename disclosure) are read
    # primitives too — gate them through the same credential check as Read,
    # else a scheduled run could dump ~/.ssh, ~/.aws, *.env into a report.
    # Read uses file_path; Grep/Glob use path — check whichever is present.
    checkpath="${path:-$gpath}"
    if credential_shaped "$checkpath" || credential_shaped "$gpath"; then
      deny "$tool of credential-shaped path blocked: ${checkpath:-$gpath}"
    fi
    allow "$tool ${checkpath:-<no path>}"
    ;;
  WebFetch)
    # A real fetch URL carries a scheme; without '://' the host can't be
    # parsed, so fail closed rather than treating the leading label as a host.
    case "$url" in
      *"://"*) : ;;
      *) deny "WebFetch with schemeless/unparseable URL: ${url:-<none>}" ;;
    esac
    # The guard reads RAW (not JSON-decoded) payload bytes, but WebFetch
    # JSON-decodes then parses via WHATWG. A backslash in the raw value is
    # therefore a parser-differential vector — either a JSON control escape
    # (\t \n \r \uXXXX, which WHATWG strips → different host) or a WHATWG
    # authority delimiter (\ acts like / for special schemes). A legitimate
    # allowlisted https URL never contains a backslash, so fail closed.
    case "$url" in
      *\\*) deny "WebFetch URL contains a backslash (parser-differential): $url" ;;
    esac
    # Parse the RFC 3986 authority: strip scheme, drop any query or fragment,
    # take the substring after the LAST '@' as authority (so a userinfo like
    # `github.com:@evil` cannot masquerade as the host), then strip the port.
    rest="${url#*://}"
    rest="${rest%%[?#]*}"
    authority="${rest%%/*}"
    hostport="${authority##*@}"
    host="${hostport%%:*}"
    host="$(printf '%s' "$host" | tr 'A-Z' 'a-z')"
    case "$host" in
      ""|*[!a-z0-9.-]*)
        deny "WebFetch with unparseable or malformed host: ${url}" ;;
    esac
    for a in $FETCH_ALLOW; do
      if [ "$host" = "$a" ]; then
        allow "WebFetch $host"
      fi
    done
    deny "WebFetch to off-allowlist host: $host"
    ;;
  Write|Edit|NotebookEdit)
    # Reject path traversal (a genuine `..` path SEGMENT), but not a mere
    # double-dot inside a filename (e.g. report..2026.md is legitimate).
    case "/$path/" in
      */../*)
        deny "$tool with '..' path segment (traversal): $path"
        ;;
    esac
    # Fence writes to the project's own knowledge/currency/. Accept a
    # repo-relative path or one anchored at CLAUDE_PROJECT_DIR; reject a
    # bare-substring match elsewhere (e.g. /tmp/knowledge/currency/...).
    proj="${CLAUDE_PROJECT_DIR:-}"
    case "$path" in
      knowledge/currency/*)
        allow "$tool $path" ;;
    esac
    if [ -n "$proj" ]; then
      case "$path" in
        "$proj"/knowledge/currency/*)
          allow "$tool $path" ;;
      esac
    fi
    # Real filesystem check (defense in depth vs symlinks): if the parent
    # resolves inside the currency dir, allow. Only trusted when BOTH paths
    # resolve to non-empty absolute paths (a failed realpath must never
    # fail open); otherwise the string fence above is the sole gate.
    if [ -n "$proj" ]; then
      parent="$(resolve_path "$(dirname "$path")")"
      cur="$(resolve_path "$proj/knowledge/currency")"
      if [ -n "$parent" ] && [ -n "$cur" ]; then
        case "$parent/" in
          "$cur"/*) allow "$tool $path (realpath-confirmed)" ;;
        esac
      fi
    fi
    deny "$tool outside knowledge/currency/: ${path:-<no path>}"
    ;;
  *)
    # Bash, every mcp__* tool (including mutating manager-ai paths like
    # prune_completed_tasks), Agent spawns, and anything unrecognized.
    deny "tool not in the report-only profile: $tool"
    ;;
esac
