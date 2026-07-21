# Capability Manifest

Verified inventory of the Anthropic / Claude Code capability surface this
framework builds on, plus the external-vendor facts the adapter generator
and watchers depend on. Every row was verified against a live source on the
date below; nothing here is assumed from memory.

- **Verified:** 2026-07-20 (owner CLI: Claude Code v2.1.215; Desktop app 1.22209.3 present)
- **Row schema (pinned — U14's degradation-coverage join keys on `id`):**
  `| id | capability | class | status | gates | evidence |`
  - `id` — stable per-capability identifier, kebab/dot, never renamed (append-only file).
  - `class` — portability class, exactly one of: `portable` (survives the
    Agent Skills standard on all hosts), `claude-native` (Claude Code only —
    adopting it into a skill/agent body requires a degradation rule),
    `platform` (Anthropic API/account surface, not a skill-body concern),
    `external` (another vendor's surface).
  - `status` — `verified` | `verified-in-product` (attested by the running
    v2.1.215 tool schema but absent from web docs) | `partial` | `absent`
    (confirmed not to exist) | `unverified`.
  - `gates` — version / plan / entitlement gates, or `none`. Availability
    classes only; never account or entitlement identifiers.
  - Machine-parse contract: capability rows are markdown table rows whose
    first cell matches `[a-z0-9][a-z0-9.-]*`; parse every such row in the
    file regardless of which table it sits in.

## Models and effort

| id | capability | class | status | gates | evidence |
|---|---|---|---|---|---|
| models.roster | Current model IDs: `claude-fable-5`, `claude-opus-4-8`, `claude-sonnet-5`, `claude-haiku-4-5-20251001` — all Active | platform | verified | Fable 5 GA; Mythos 5 invite-only | platform.claude.com/docs/en/about-claude/models/model-ids-and-versions |
| models.aliases | Frontmatter/CLI aliases: `haiku`, `sonnet`, `opus`, `fable`, `inherit` (+ `default`, `best`, `opusplan`, `sonnet[1m]`, `opus[1m]` in /model) | claude-native | verified | none | code.claude.com/docs/en/model-config |
| models.retired | `-latest` aliases no longer exist; retired: all `claude-3-*`, `claude-opus-4-20250514`, `claude-sonnet-4-20250514`; deprecated `claude-opus-4-1-20250805` (retires 2026-08-05). Legacy-but-active: opus-4-5/4-6/4-7, sonnet-4-5/4-6 | platform | verified | none | platform.claude.com/docs/en/about-claude/model-deprecations |
| effort.levels | Effort vocabulary: `low`, `medium`, `high`, `xhigh`, `max` — complete set; default `high` | platform | verified | xhigh: Fable 5/Mythos 5/Opus 4.8/4.7/Sonnet 5 only | platform.claude.com/docs/en/build-with-claude/effort |
| effort.skill-frontmatter | `effort:` in SKILL.md — "Overrides the session effort level" | claude-native | verified | none | code.claude.com/docs/en/skills |
| effort.agent-frontmatter | `effort:` in agent .md — documented (GitHub issue #65598 "not planned" is stale; docs win) | claude-native | verified | none | code.claude.com/docs/en/sub-agents |
| model.skill-frontmatter | `model:` in SKILL.md — same values as /model, or `inherit`; turn-scoped | claude-native | verified | none | code.claude.com/docs/en/skills |
| model.agent-frontmatter | `model:` in agent .md — `sonnet`/`opus`/`haiku`/`fable`/full ID/`inherit` (default `inherit`) | claude-native | verified | `fable` alias needs v2.1.170+ | code.claude.com/docs/en/sub-agents |
| fast-mode | `/fast` toggle; Opus 4.8 (4.7 removed 2026-07-24); flat premium pricing, usage credits on subscription plans | claude-native | verified | research preview; CLI only; Team/Ent owner opt-in | code.claude.com/docs/en/fast-mode |

## Orchestration

| id | capability | class | status | gates | evidence |
|---|---|---|---|---|---|
| workflows.tool | `Workflow` model-callable tool: script-orchestrated subagent fan-out, background, resumable in-session | claude-native | verified | v2.1.154+; paid plans; Pro opt-in via /config | code.claude.com/docs/en/workflows |
| workflows.primitives | Official script primitives: `agent()`, `pipeline()`; caps 16 concurrent / 1,000 per run | claude-native | verified | none | code.claude.com/docs/en/workflows |
| workflows.parallel | `parallel()` barrier primitive + `budget` object + phase()/log() | claude-native | verified-in-product | v2.1.215 tool schema documents them; web docs do not — prefer agent()/pipeline() in durable scripts | in-product Workflow schema (2026-07-20) |
| workflows.ultracode | Ultracode = `xhigh` effort + standing workflow permission, not an API effort level; `/effort ultracode` | claude-native | verified | `--effort ultracode` v2.1.203+ | platform.claude.com/docs/en/build-with-claude/effort |
| workflows.keyword-human-only | `ultracode` keyword opt-in only in human-typed prompts — NOT `-p`, scheduled-task prompts, webhooks | claude-native | verified | hardened v2.1.210 | code.claude.com/docs/en/workflows |
| goal.command | `/goal` session objective (prompt-based Stop-hook wrapper); user-typed only, no model-callable tool | claude-native | verified | v2.1.139+; trusted workspace; ≤4,000 chars | code.claude.com/docs/en/goal |
| agents.subagents | Agent tool: per-invocation `model`, `isolation: "worktree"`, `run_in_background`, named continuation via SendMessage | claude-native | verified | background default v2.1.198+ | code.claude.com/docs/en/sub-agents |
| agents.teams | Agent teams: experimental, disabled by default (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`); TeamCreate/TeamDelete removed; SendMessage + Task* tools remain | claude-native | partial | experimental — document as opt-in, never in core paths | code.claude.com/docs/en/agent-teams |
| workflows.budget-directive | "+Nk" token-budget prompt directives | claude-native | verified-in-product | in-product schema only; treat as unstable, never load-bearing | code.claude.com/docs/en/workflows (absent) |
| checkpointing | Automatic per-prompt code snapshots; `/rewind` (not bash-command file changes) | claude-native | verified | none | code.claude.com/docs/en/checkpointing |
| plugins | Plugin marketplaces bundling skills/agents/hooks/MCP/LSP | claude-native | verified | claude-plugins-official auto-available | code.claude.com/docs/en/discover-plugins |
| skills.standard | Skills follow the Agent Skills open standard (agentskills.io); CC extends it (invocation control, `context: fork`, dynamic context) | portable | verified | none | code.claude.com/docs/en/skills |
| skills.disable-model-invocation | `disable-model-invocation: true` blocks auto-load, subagent preload, and (v2.1.196+) scheduled-task firing — a schedulable skill must NOT set it | claude-native | verified | v2.1.196+ for the scheduled-task block | code.claude.com/docs/en/skills |

## Scheduling and automation homes

| id | capability | class | status | gates | evidence |
|---|---|---|---|---|---|
| sched.cron-insession | CronCreate/CronList/CronDelete: session-scoped prompts, 7-day expiry, ≤50/session, no disk persistence, fires between turns in the SAME session | claude-native | verified | none | code.claude.com/docs/en/scheduled-tasks |
| sched.loop | `/loop` + ScheduleWakeup dynamic pacing; wakeups inherit the session's MCP + permission surface | claude-native | verified | 7-day expiry | code.claude.com/docs/en/scheduled-tasks |
| sched.desktop | Desktop scheduled tasks: app-internal scheduler, fresh local session per fire, per-task working folder + permission mode + always-allow list, optional worktree; runs only while app open | claude-native | verified | Desktop app required | code.claude.com/docs/en/desktop-scheduled-tasks |
| sched.cloud-routines | Cloud routines: schedule via `/schedule` CLI or web; fresh clone per run from default branch; ≥1-hour interval; no permission prompts during runs | platform | verified | research preview; Pro/Max/Team/Enterprise + Claude Code on web enabled | code.claude.com/docs/en/routines |
| sched.cloud-writes | Routine pushes restricted to `claude/*` branches by default (per-repo unrestricted toggle); never local files; commits appear as the user's GitHub identity | platform | verified | none | code.claude.com/docs/en/routines |
| sched.cloud-skills | Cloud sessions load project skills committed to the cloned repo's `.claude/skills/` (not `~/.claude/skills/`) | platform | verified | none | code.claude.com/docs/en/skills |
| sched.headless | External scheduler → `claude -p` wrapper: full per-run enforcement via `--permission-mode dontAsk`, `--disallowedTools`, `--settings`, plus caller-set env; `--bare` would skip hooks/skills — do not use with the guard | claude-native | verified | none | code.claude.com/docs/en/headless, /cli-reference |

### Per-home enforcement (the KTD-5 containment question)

`enforceable` = can this home apply the restricted tool profile (deny Bash +
mutating MCP, fence writes, pin fetch egress) to the scheduled run itself,
per-run, without touching interactive sessions?

| id | home | enforceable | marker (PreToolUse-observable) | notes |
|---|---|---|---|---|
| home.wrapper | External cron/launchd → `claude -p` + flags | yes — full profile by construction | yes — caller-set env (`CE_REPORT_ONLY=1`); hooks inherit parent env (documented) | the gold-standard local home; setup wires a launchd/cron wrapper. Direct-drive drill: put the marker on the guard process, `printf … \| CE_REPORT_ONLY=1 bash …guard.sh` (a pipeline `VAR=val cmd1` prefix binds only to `cmd1`) |
| home.desktop | Desktop scheduled task | partial — per-task `dontAsk` mode denies anything outside allow rules; skill-level `disallowed-tools` applies; no per-run settings/env | no documented env marker; `permission_mode` field in hook stdin usable as a disclosed convention | offered with reduced-guarantee disclosure |
| home.cloud | Cloud routine | partial-by-different-means — no tool permission system, but infra enforces: per-environment network allowlist (403 `host_not_allowed`), connector removal, `claude/*` branch scoping; cannot touch local files at all | yes — per-environment custom env vars (documented) + `CLAUDE_CODE_REMOTE=true` | cannot write a repo-visible report into the local checkout; reports surface via transcript or documented read-back |
| home.insession | In-session cron / `/loop` | no — prompt into the same session; inherits full session tool surface; skill-level `disallowed-tools` is the only narrowing | no — no documented signal distinguishes a cron/wakeup turn | not offered as an enforced option; disclosed-degraded only |

## Hooks and enforcement primitives

| id | capability | class | status | gates | evidence |
|---|---|---|---|---|---|
| hooks.lifecycle | 30 documented events incl. SessionStart/End, UserPromptSubmit, Pre/PostToolUse, PostToolUseFailure, PermissionRequest/Denied, SubagentStart/Stop, Setup, PreCompact, FileChanged, WorktreeCreate/Remove | claude-native | verified | none | code.claude.com/docs/en/hooks |
| hooks.pretooluse | PreToolUse stdin JSON: session_id, transcript_path, cwd, permission_mode, tool_name, tool_input; exit 2 blocks (exit 1 does NOT); JSON `permissionDecision: allow/deny/ask` | claude-native | verified | none | code.claude.com/docs/en/hooks |
| hooks.env-inheritance | "The hook process inherits the parent environment" — a caller-set env var is readable inside a hook subprocess | claude-native | verified | none | code.claude.com/docs/en/hooks |
| hooks.disableable | `disableAllHooks` exists — a guard hook is never a sufficient sole layer; deny rules are not bypassable by hooks | claude-native | verified | none | code.claude.com/docs/en/hooks, /permissions |
| perms.deny-syntax | Deny rules: bare tool name removes tool from context; `WebFetch(domain:x)` egress pinning; `mcp__server__tool` per-tool deny; `Read()`/`Edit()` path rules (gitignore globs); deny at any level wins; evaluated deny→ask→allow | claude-native | verified | Read-deny blocks Edit v2.1.208+ | code.claude.com/docs/en/permissions |
| perms.bash-caveat | "If Bash is allowed, Claude can still use curl… to reach any URL" — deny Bash is a prerequisite for any fetch allowlist to be meaningful | claude-native | verified | none | code.claude.com/docs/en/permissions |
| perms.dontask | `--permission-mode dontAsk` denies anything not in allow rules or the read-only set — deny-by-default for unattended runs | claude-native | verified | none | code.claude.com/docs/en/headless |
| skills.disallowed-tools | SKILL.md `disallowed-tools:` removes tools while the skill is active — a portable, home-independent profile core | claude-native | verified | none | code.claude.com/docs/en/skills |
| sandbox.os | OS-level sandboxing: macOS Seatbelt built-in; `sandbox.network.allowedDomains` (no domains pre-allowed), `filesystem.denyRead`, `credentials.files/envVars` deny/mask | claude-native | verified | credentials v2.1.187+/2.1.199+; macOS/Linux only | code.claude.com/docs/en/sandboxing |

## External vendor surfaces (adapter + watcher dependencies)

| id | capability | class | status | gates | evidence |
|---|---|---|---|---|---|
| cursor.agent-model | Cursor agent-file `model:` — exactly two options: `inherit` (default) or a specific model ID; Claude addressable by ID (doc example `claude-opus-4-8[effort=high]`) | external | verified | only `claude-opus-4-8` slug verbatim in docs; other Claude-5 slugs pattern-consistent but inferred | cursor.com/docs/context/subagents |
| cursor.reads-claude-agents | Cursor natively reads `.cursor/agents/`, `.claude/agents/`, `.codex/agents/` (`.cursor/` wins on name collision) | external | verified | none | cursor.com/docs/context/subagents |
| codex.agent-model | Codex agent TOML: inherit by OMITTING `model` (no `inherit` token); `model_reasoning_effort`: minimal/low/medium/high/xhigh | external | verified | none | developers.openai.com/codex (→ learn.chatgpt.com) |
| codex.model-tiers | Mapping targets: `gpt-5.4-mini` (subagent mini tier), `gpt-5.6-terra` (balanced), `gpt-5.6-sol` (frontier flagship) | external | verified | vendor vocabulary drifts — unwatched coupling, see note below | learn.chatgpt.com/docs/models |
| github.atom-feeds | Per-repo `commits.atom` / `releases.atom`: unauthenticated, 20 entries, full SHAs + timestamps, outside the REST rate budget | external | verified | none | live probe 2026-07-20 (superpowers, gbrain) |
| github.compare-api | `api.github.com/repos/O/R/compare/A...B` unauthenticated: commits[] + files[] (≤250 commits unpaged / ≤300 files); rate budget 60/hr/IP | external | verified | none | docs.github.com REST rate limits + live probe |
| github.compare-diff | `github.com/O/R/compare/A...B.diff` plain-text unified diff — full file-level delta with zero API budget | external | verified | none | live probe 2026-07-20 |
| github.delta-engine | Chosen delta pipeline: poll `commits.atom` (free) → compare API only on change (≤6 calls/run) → fallback order `.diff` page → atom-only → HTML titles. Viable for 6 repos on any sane cadence | external | verified | none | cap-vendors verification run 2026-07-20 |

## Confirmed absent or unstable (chase no phantoms)

| id | capability | class | status | gates | evidence |
|---|---|---|---|---|---|
| absent.model-latest-aliases | `-latest` model aliases | platform | absent | — | model-ids page: no such aliases exist |
| absent.goal-tool | Model-callable `/goal` tool | claude-native | absent | — | code.claude.com/docs/en/goal (user command only) |
| absent.teamcreate | TeamCreate/TeamDelete tools | claude-native | absent | removed v2.1.178 | code.claude.com/docs/en/agent-teams |
| absent.cron-durable | Durable / disk-persisted in-session cron | claude-native | absent | `durable:` flag is a no-op | in-product CronCreate schema + scheduled-tasks docs |
| absent.insession-marker | Scheduled-origin signal for in-session cron//loop turns, observable from a PreToolUse hook | claude-native | absent | — | code.claude.com/docs/en/scheduled-tasks + /hooks (silent) |
| unstable.teams | Agent teams for production reliance | claude-native | partial | experimental; /resume drops teammates | code.claude.com/docs/en/agent-teams |

## Standing notes

- **Unwatched coupling (accepted risk):** the Codex/Cursor model-vocabulary
  mapping tables in `core/scripts/build_adapters.py` encode external vendors'
  naming. `repo-watch` watches the six mined repos, not Codex or Cursor
  releases — vendor renames surface only when a consumer breaks or a manual
  re-verification runs. Recorded per the plan's System-Wide Impact.
- **Cloud trust base:** cloud routines and ultrareview place the claude.ai
  account in the trust base; two-factor auth and a spend alert are stated
  prerequisites wherever setup offers them.
- **Ultrareview / fast mode entitlements:** research previews, verified
  available in the owner's product surface (system-prompt attestation +
  docs); billing via usage credits — availability classes only recorded here.
- This file is the platform watcher's first baseline (U10 consumes it).
