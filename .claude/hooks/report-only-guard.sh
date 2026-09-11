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
#     tools passes; Write/Edit only to knowledge/currency/currency.lock or
#     knowledge/currency/reports/<cli|repo>/<today>.md (a report-only run
#     advances no state); Read/Grep/Glob only on a non-credential path
#     inside the project; WebFetch only to allowlisted domains; Bash and
#     every MCP tool are denied.
#   - Exit 2 blocks the tool call (exit 1 would NOT block — hooks docs).
#   - Stall budget (KTD6): a hook that reaches the host's timeout is
#     cancelled and the tool call proceeds — fail-open. So every external
#     step here (the JSON parser, realpath, date, tr) runs behind a process
#     substitution and is read with a 10 s bounded builtin `read -t`; an
#     expired or empty read kills the child and takes the deny path. The
#     host payload is read by a bounded builtin loop, never `cat`. A
#     trapped TERM/HUP/INT also lands in the deny path (an untrapped
#     signal death runs the EXIT trap with status 0 and the host sees
#     143: fail-open). Builtins only: no `sleep`, no `timeout`, no
#     background timer (bash delivers a trapped signal only after the
#     current foreground command returns, so a timer could not interrupt
#     a stalled command substitution anyway — but it DOES interrupt a
#     blocking `read -t`, verified on bash 3.2.57).
#
# Wired BY HAND into .claude/settings.local.json when the owner opts into
# automation (setup prints the pointer; it never writes the block — see
# the companion doc for the JSON, which carries no `timeout` on purpose).
# Committed-but-unwired is the shipped state and must stay green in CI
# (validator check 11 exempts it; the guard-wiring check validates the
# local wiring when present). Bash 3.2 floor: no arrays, no ${var,,}.

# ── Interactive fast path: inert without the scheduler marker ─────────────
if [ -z "${CE_REPORT_ONLY:-}" ]; then
  exit 0
fi

# ── Scheduled run: fail closed from here on ───────────────────────────────
# A PreToolUse hook that exits with anything other than 2 is treated as
# NON-blocking by Claude Code, so a crash (missing dependency, syntax slip,
# 127/1) would fail OPEN and let the tool run. Trap the final exit: convert
# any unexpected non-0/non-2 code into an explicit deny (2). allow() exits 0
# and deny() exits 2, so legitimate decisions pass through untouched.
trap '_ec=$?; if [ "$_ec" != 0 ] && [ "$_ec" != 2 ]; then echo "report-only guard: internal error (fail-closed, exit $_ec)" >&2; exit 2; fi' EXIT

# ── Stall budget (KTD6) ───────────────────────────────────────────────────
STALL=10      # seconds per bounded read; the host default (600 s) is the ceiling
_child=""     # pid of the process substitution currently being read

_reap() {
  if [ -n "$_child" ]; then kill "$_child" 2>/dev/null; _child=""; fi
}

# bounded_line VAR CMD [ARG...]: run CMD behind a process substitution with
# stdin and stderr on /dev/null, read its first output line into VAR within
# the stall budget, then kill the child whether or not it answered. Returns
# non-zero when the read expired or produced nothing (bash 3.2 returns 1
# for both; neither is trusted); the caller decides between a deny (the
# fences) and a placeholder (the log timestamp).
#
# `$!` is the substitution's subshell, and bash 3.2 does not exec-optimize
# it: a plain `<(date)` forks date under that subshell, and killing the
# subshell orphans the stalled binary. So every CMD passed here is a
# wrapper function whose last step `exec`s the real binary, which makes the
# killed pid the binary itself. Those wrappers (`_date`, `_lower`,
# `_resolve`) must only ever run inside this substitution — an `exec` in
# the guard's own shell would replace the guard.
_date() { exec date "$@"; }

bounded_line() {
  _bl_var="$1"; shift
  _bl_out=""
  exec 3< <("$@" </dev/null 2>/dev/null)
  _child=$!
  IFS= read -r -t "$STALL" -u 3 _bl_out
  _bl_rc=$?
  _reap
  exec 3<&-
  eval "$_bl_var=\$_bl_out"
  [ "$_bl_rc" = 0 ] && [ -n "$_bl_out" ]
}

log() {
  bounded_line _stamp _date -u +%FT%TZ || _stamp="unknown-time"
  # One log line per decision: a line break inside the message (the parser
  # already rejects them in tool fields; this is defense in depth for the
  # guard's own text) is written as a literal \n or \r escape.
  _m="$1"; _m="${_m//$'\n'/\\n}"; _m="${_m//$'\r'/\\r}"
  # stderr is silenced BEFORE the append is opened, so a missing log dir
  # (wrong or unset CLAUDE_PROJECT_DIR) degrades silently, as documented.
  echo "[$_stamp] $_m" 2>/dev/null \
    >> "${CLAUDE_PROJECT_DIR:-.}/knowledge/currency/guard.log" || true
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

# A signal mid-run is a deny, never a 143. Reap the child first so nothing
# is left holding the host's pipes.
trap '_reap; deny "signal received mid-run (fail-closed under CE_REPORT_ONLY)"' TERM HUP INT

# ── Host payload: bounded builtin read loop, never `cat` ──────────────────
payload=""; _line=""; _t0=$SECONDS
while IFS= read -r -t "$STALL" _line; do
  payload="$payload$_line"$'\n'
  _t0=$SECONDS
done
payload="$payload$_line"   # the last line arrives without its newline
# bash 3.2 returns 1 for both EOF and an expired read; only the clock tells
# them apart. A host that spends the budget on its final write (or never
# closes stdin) is a stall, whatever bytes have arrived.
if [ $((SECONDS - _t0)) -ge $((STALL - 1)) ]; then
  deny "host payload stalled (fail-closed under CE_REPORT_ONLY)"
fi

# Extract fields with a REAL JSON parser, not regex over raw bytes: a greedy
# regex picks the LAST "tool_name" (a nested key inside tool_input would
# spoof it), and raw bytes don't decode JSON escapes. tool_name comes from
# the top-level object; file_path/path/url from tool_input only. Each field
# is emitted on its own line with every byte octal-escaped (\0ooo) so no
# value (paths with spaces, tabs, newlines, quotes) can break the framing,
# and is decoded below by the printf builtin — no sed/base64 forks. The
# parser reads the already-captured payload from a here-string (it never
# touches host stdin) and is bounded like every other external step; if
# python3 is missing, the payload doesn't parse, a field carries a NUL or a
# line break, or the interpreter stalls, the read comes back empty and we
# fail closed.
_fields_ok=1
tool_e=""; path_e=""; gpath_e=""; url_e=""
exec 3< <(exec python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    assert isinstance(d, dict)
    ti = d.get("tool_input")
    if not isinstance(ti, dict):
        ti = {}
    def enc(v):
        s = v if isinstance(v, str) else ""
        if "\x00" in s or "\n" in s or "\r" in s:
            # No legitimate path or URL carries NUL or a line break; a
            # newline in a path would let the run forge a guard.log line.
            raise ValueError("control character in field")
        return "".join("\\0%o" % b for b in s.encode("utf-8"))
    out = [enc(d.get("tool_name")), enc(ti.get("file_path")),
           enc(ti.get("path")), enc(ti.get("url"))]
except Exception:
    sys.exit(3)
for line in out:
    print(line)
' <<< "$payload" 2>/dev/null)
_child=$!
{ IFS= read -r -t "$STALL" -u 3 tool_e && IFS= read -r -t "$STALL" -u 3 path_e \
  && IFS= read -r -t "$STALL" -u 3 gpath_e && IFS= read -r -t "$STALL" -u 3 url_e; } \
  || _fields_ok=0
_reap
exec 3<&-
[ "$_fields_ok" = 1 ] || deny "unparseable or stalled hook payload (fail-closed under CE_REPORT_ONLY)"

# _decode VAR ENC: printf builtin decode of the octal escapes. bash 3.2's
# `printf -v` leaves VAR holding the previous call's buffer when the result
# is empty, so an empty field is assigned explicitly.
_decode() {
  if [ -n "$2" ]; then printf -v "$1" '%b' "$2"; else eval "$1=''"; fi
}
_decode tool  "$tool_e"
_decode path  "$path_e"
_decode gpath "$gpath_e"
_decode url   "$url_e"

[ -n "$tool" ] || deny "unparseable hook payload (fail-closed under CE_REPORT_ONLY)"

# Domains a report-only run may fetch (KTD-5 egress pin). Extend per-run
# with CE_FETCH_ALLOW="host1,host2" on the scheduled invocation.
FETCH_ALLOW="code.claude.com platform.claude.com claude.com www.anthropic.com anthropic.com github.com api.github.com raw.githubusercontent.com objects.githubusercontent.com docs.github.com"
if [ -n "${CE_FETCH_ALLOW:-}" ]; then
  FETCH_ALLOW="$FETCH_ALLOW ${CE_FETCH_ALLOW//,/ }"
fi

credential_shaped() {
  # Credential-bearing directories and filenames. Word-shaped tokens
  # (secret/token/password/credential/apikey) require a credential-ish
  # extension so a benign path like a `secret-scan` doc is not denied,
  # while the specific dotfiles/keys below match by location or name.
  # Matched case-insensitively (builtin `nocasematch`, scoped to this
  # function): the default macOS volume is case-insensitive, so `.SSH/ID_RSA`
  # opens the real key and must be denied exactly like `.ssh/id_rsa`.
  shopt -s nocasematch
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
      shopt -u nocasematch; return 0 ;;
  esac
  shopt -u nocasematch
  return 1
}

# Portable realpath: GNU `realpath -m`, else BSD `realpath`, else python3.
# Always invoked through bounded_line (never $(...)), so a stalled resolver
# is a deny, not a hang.
_resolve() {
  realpath -m "$1" 2>/dev/null || realpath "$1" 2>/dev/null \
    || exec python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "$1" 2>/dev/null
}

# Lowercase via tr, behind the same bound (bash 3.2 has no ${var,,}).
_lower() { exec tr 'A-Z' 'a-z' <<< "$1"; }

# _redact_kv VAR STRING: rewrite `k=v` pairs joined by `&` so the value of
# every secret-shaped key becomes REDACTED. Keys match by case-insensitive
# substring (token, key, signature, password, secret, credential, plus the
# exact names sig and auth), so api_key, client_secret, refresh_token and
# the X-Amz-* presigned parameters are covered; over-redacting a benign
# `keyword=` in a local log is the accepted cost. Builtins only.
_redact_kv() {
  _rk_var="$1"; _rk_q="$2"; _rk_out=""; _rk_more=1
  while [ "$_rk_more" = 1 ]; do
    case "$_rk_q" in
      *\&*) _rk_p="${_rk_q%%&*}"; _rk_q="${_rk_q#*&}" ;;
      *)    _rk_p="$_rk_q"; _rk_more=0 ;;
    esac
    case "$_rk_p" in
      *=*)
        _rk_k="${_rk_p%%=*}"
        shopt -s nocasematch
        case "$_rk_k" in
          *token*|*key*|sig|*signature*|auth|*password*|*secret*|*credential*)
            _rk_p="$_rk_k=REDACTED" ;;
        esac
        shopt -u nocasematch ;;
    esac
    _rk_out="$_rk_out$_rk_p"
    [ "$_rk_more" = 1 ] && _rk_out="$_rk_out&"
  done
  printf -v "$_rk_var" '%s' "$_rk_out"
}

proj="${CLAUDE_PROJECT_DIR:-}"

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
    # The directory-shaped literals need a slash before the name (`*/.ssh`),
    # so a relative spelling (`.ssh`, `.npmrc`) is checked as `./.ssh`; the
    # original strings stay in the log and deny messages.
    _cp="$checkpath"; case "$_cp" in ''|/*) : ;; *) _cp="./$_cp" ;; esac
    _gp="$gpath";     case "$_gp" in ''|/*) : ;; *) _gp="./$_gp" ;; esac
    if credential_shaped "$_cp" || credential_shaped "$_gp"; then
      deny "$tool of credential-shaped path blocked: ${checkpath:-$gpath}"
    fi
    # R8 project fence, for all three read primitives (Read carries
    # file_path; Grep/Glob carry path): a path-less search (the whole cwd,
    # or the home directory when the host runs elsewhere), a `..` segment,
    # or a path outside the project are content-dump routes. A relative
    # path without `..` counts as inside. An absolute path must BOTH
    # string-prefix the project dir AND, when both sides resolve,
    # realpath-confirm it — stricter than the write fence, which trusts the
    # resolved form alone and falls back to the string form only when no
    # resolver answers. With the project dir unset, an absolute path cannot
    # be placed and is denied. A report-only run never needs a file outside
    # CLAUDE_PROJECT_DIR (both watcher skills read only repo paths), so the
    # fence costs the watchers nothing and closes the dotfile-exfil route.
    fence="$checkpath"
    [ -n "$fence" ] || deny "$tool without a path (content dump by pattern): <no path>"
    case "/$fence/" in
      */../*) deny "$tool with '..' path segment (traversal): $fence" ;;
    esac
    case "$fence" in
      /*)
        [ -n "$proj" ] || deny "$tool with an absolute path and no CLAUDE_PROJECT_DIR: $fence"
        case "$fence" in
          "$proj"|"$proj"/*) : ;;
          *) deny "$tool outside the project directory: $fence" ;;
        esac
        rg=""; rp=""
        bounded_line rg _resolve "$fence" || rg=""
        bounded_line rp _resolve "$proj" || rp=""
        if [ -n "$rg" ] && [ -n "$rp" ]; then
          case "$rg" in
            "$rp"|"$rp"/*) : ;;
            *) deny "$tool resolves outside the project directory: $fence -> $rg" ;;
          esac
        fi
        ;;
    esac
    allow "$tool $checkpath"
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
    scheme="${url%%://*}"
    rest="${url#*://}"
    authority="${rest%%[/?#]*}"
    tail="${rest#"$authority"}"        # path, query, fragment — verbatim
    hostport="${authority##*@}"
    host="${hostport%%:*}"
    bounded_line host _lower "$host" || deny "WebFetch host could not be normalised (stalled tr, fail-closed): $url"
    case "$host" in
      ""|*[!a-z0-9.-]*)
        deny "WebFetch with unparseable or malformed host: ${url}" ;;
    esac
    # KTD7: log the FULL URL on an allowed fetch so receipts reconcile by
    # URL, not host — after dropping userinfo and replacing the values of
    # secret-shaped query (and fragment) parameters with a placeholder; see
    # _redact_kv for the key rule. The log is local and gitignored, never
    # copied into a tracked file.
    frag=""; query=""
    case "$tail" in *\#*) frag="#${tail#*\#}"; tail="${tail%%\#*}" ;; esac
    case "$tail" in *\?*) query="${tail#*\?}"; tail="${tail%%\?*}" ;; esac
    if [ -n "$query" ]; then
      _redact_kv query "$query"
      query="?$query"
    fi
    case "$frag" in
      *=*) _redact_kv _rf "${frag#\#}"; frag="#$_rf" ;;
    esac
    logurl="$scheme://$hostport$tail$query$frag"
    logurl="${logurl//$'\n'/%0A}"; logurl="${logurl//$'\r'/%0D}"
    for a in $FETCH_ALLOW; do
      if [ "$host" = "$a" ]; then
        allow "WebFetch $logurl"
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
    # R8 write fence, as a positive shape: the ONLY writable targets under
    # the marker are knowledge/currency/currency.lock and
    # knowledge/currency/reports/<cli|repo>/<today>.md, where today is the
    # local or the UTC date (both are legitimate for a few hours around
    # midnight; yesterday's report and any other name are denied). Every
    # other path under knowledge/currency/ — the baseline, the registry,
    # their .tmp siblings, the log, .v2 snapshots, root-level files — is
    # state a report-only run must not advance, and is denied and logged.
    # Evaluated on the basename plus the RESOLVED parent (never whole-string
    # equality), so `//`, `./` and case variants cannot dodge a deny; the
    # string form is the fallback when resolution fails, so a failed
    # realpath can never skip a deny; and an existing target is resolved
    # first, so a report name that is really a symlink to a state file is
    # denied. Principle: allowlisted root + depth floor + resolve-then-check
    # (agent-skills 45fd4a0). The root itself can never be a target.
    target="$path"
    if [ -e "$target" ] || [ -L "$target" ]; then
      bounded_line target _resolve "$target" \
        || deny "$tool target could not be resolved (stalled realpath, fail-closed): $path"
    fi
    case "$target" in
      */*) parent_str="${target%/*}"; [ -n "$parent_str" ] || parent_str=/ ;;
      *)   parent_str=. ;;
    esac
    base="${target##*/}"
    rparent=""; cur=""
    bounded_line rparent _resolve "$parent_str" || rparent=""
    if [ -n "$proj" ]; then
      bounded_line cur _resolve "$proj/knowledge/currency" || cur=""
    fi
    kind=outside
    if [ -n "$rparent" ] && [ -n "$cur" ]; then
      case "$rparent" in
        "$cur")                                 kind=root ;;
        "$cur/reports/cli"|"$cur/reports/repo") kind=reports ;;
        "$cur"/*)                               kind=inside ;;
      esac
    else
      # String fallback (no resolver answered): exact spellings only.
      s="$parent_str"
      if [ -n "$proj" ]; then
        case "$s" in "$proj"/*) s="${s#"$proj"/}" ;; esac
      fi
      case "$s" in
        knowledge/currency)                                              kind=root ;;
        knowledge/currency/reports/cli|knowledge/currency/reports/repo)  kind=reports ;;
        knowledge/currency/*)                                            kind=inside ;;
      esac
    fi
    case "$kind" in
      root)
        [ "$base" = "currency.lock" ] && allow "$tool $path"
        ;;
      reports)
        today_local=""; today_utc=""
        bounded_line today_local _date +%F \
          || deny "$tool: today's date could not be established (stalled date, fail-closed): $path"
        bounded_line today_utc _date -u +%F \
          || deny "$tool: today's date could not be established (stalled date, fail-closed): $path"
        if [ "$base" = "$today_local.md" ] || [ "$base" = "$today_utc.md" ]; then
          allow "$tool $path"
        fi
        ;;
    esac
    case "$kind" in
      outside) deny "$tool outside knowledge/currency/: ${path:-<no path>}" ;;
      *)       deny "$tool target is not the lock or today's report (a report-only run advances no state): $path" ;;
    esac
    ;;
  *)
    # Bash, every mcp__* tool (including mutating manager-ai paths like
    # prune_completed_tasks), Agent spawns, and anything unrecognized.
    deny "tool not in the report-only profile: $tool"
    ;;
esac
