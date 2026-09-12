# Adoption Matrix — 2026-07-20

The single gateable decision artifact merging the capability manifest
(`docs/capabilities.md`, U1) and the mining ledger
(`2026-07-20-ecosystem-mining.md`, U2). Implementation waves execute from
this file only; every wave-C/D/E/F change traces back to a row here, and
so does every wave-G change (the 2026-09-11 currency wave, recorded in
the dated ledger `2026-09-11-currency-wave.md`) and every wave-H change
(the 2026-09-12 recovered-windows wave, recorded in
`2026-09-12-recovered-windows-wave.md`).

**Gate record:** wave approvals in this run are executed under the owner's
standing instruction of 2026-07-20 ("complete the plan end-to-end,
iterate until perfect"); the initiative lands on a feature branch and the
pull request is the owner's final merge gate. Heightened-review rows are
additionally flagged in the PR description for explicit owner eyes.

**Gate record (2026-09-11):** the owner directed that every candidate line
in both 2026-09-11 watcher reports — the 7 CLI adopt-candidates and the
33 RW adopt/adapt candidates, 40 in all — be applied in one wave while
unavailable, delegating the apply step through the pipeline rather than
leaving the decision lines for a later owner-marked full run (wave-plan
KTD1, KTD2). The wave lands on `feat/currency-wave-2026-09` and the pull
request is the owner's merge gate. Heightened-review rows are flagged in
the PR description for explicit owner eyes; every downgrade (RW-9 and
RW-26 to `document`, RW-34 and RW-40 to `adopt-partial`) carries its
reason on its row here and on the dated ledger. The report snapshots,
ticked decision lines, cli baseline, and cursor advance happen after the
commit (U13) and are gitignored side effects the PR description lists. Exception recorded after review: three intermediate commits on the wave branch (`854a44b`, `61ded4e`, `9d7fa15`) carry a stale adapter manifest that `075fedd` caught up, so `build_adapters.py --check` is red inside the wave and green at its head; the branch is merged with a merge commit rather than squashed so every `Adopted-in` SHA in the dated ledger stays resolvable, and the "adapters regenerate in the same commit" rule holds from the next wave on (the standard now names this exception). The three compare windows the run could not see (compound-engineering 51, gsd-core 890, gbrain 403 oldest commits after each seed) were paged and classified on 2026-09-11 after the wave landed; their 31 adopt/adapt candidates carry provisional IDs and await the owner's marks in the 2026-09-11 repo report, so their matrix rows belong to the wave that adopts them.

**Gate record (2026-09-12):** the owner reviewed the recovered-window
recommendation and marked 30 of the 31 candidate lines in the 2026-09-11
repo report for adoption, delegating the apply step through the pipeline
rather than leaving them for a later owner-marked full run (wave-plan KTD1).
The thirty-first, the opt-in pre-commit gate hook (GSD-U-21), is marked
`document` by owner decision: interactive sessions stay hook-free (July
KTD-5) and a validator run on every commit reverses that, so the hashed
adapter manifest and the same-commit regeneration rule stay the mechanism.
GB-U-20 (non-Latin slugs beyond Latin diacritics) is carried as `document`
from its report row. Every marked row landed with an adjustment and none was
downgraded; the adjustments are on the rows of the dated ledger
`2026-09-12-recovered-windows-wave.md`, which mints `RW-2026-09-12-N` ids and
keeps each provisional report id on the row as `(was GSD-U-3)` so both stay
searchable. The wave lands on `feat/recovered-windows-2026-09` across nine
implementation commits (each carrying its own tests and regenerated
adapters), this record-only commit, and a close-out commit that fills
`Adopted-in`; the pull request is the owner's merge gate and flags the
heightened-review rows for explicit owner eyes. As in wave G the branch is
merged with a merge commit rather than squashed, so every `Adopted-in` sha in
the dated ledger stays resolvable on `main`. One repo-hygiene decision is
recorded here because it is not reversible by editing a file: three tracked
files that the ignore rules already covered (`knowledge/voice-guide.md` and
two personal `idea.md` files) were removed from the index in U1. They stay on
disk, and the removal is forward-only — history and every existing fork keep
them, so untracking stops future exposure and does not undo past exposure,
and a history rewrite remains the owner's separate decision (KTD8). If the
two project ideas were meant as shipped examples rather than personal notes,
the alternative is a per-file negation in `.gitignore` plus an allow-list
entry in the new `privacy-placement` check; the pull-request description
names that choice. No registry cursor moves and no baseline is written: all
six cursors already sit at their 2026-09-11 heads and every commit this wave
classifies is older than the cursor of its repo.

**Row contract:** decision rows are markdown table rows keyed by a
manifest `id` or ledger ID in the first cell. Columns: source | verdict |
wave | target files | degradation rule | unattended | tags. Verdicts:
`adopt`, `adopt-partial`, `document`, `defer`, `not-applicable`.
`degradation` = yes → the mechanism that keeps generated adapters clean
(KEEP_FIELDS drop, fenced section with fallback, or renderer map).
**Dispositions (RW-2026-09-11-24):** every review or audit finding that
reaches this file is recorded as adopted (§A/§C), deferred (§D), or
rejected (§E), each with its rationale on the row or its ledger row;
rows are append-only — a later row that changes a disposition names the
earlier row it supersedes instead of rewriting it (the two 2026-09-11
moves, CE-10 and GB-04, are recorded on their §C rows). `/pre-mortem`
findings are the next intended consumer of this convention.

## A. Platform capability adoptions (from the manifest)

| id | verdict | wave | target files | degradation | unattended | tags |
|---|---|---|---|---|---|---|
| model.skill-frontmatter | adopt | C | all `.claude/skills/*/SKILL.md`, `.claude/commands/analyze.md` | yes — KEEP_FIELDS drops `model`; native renderers map-or-omit (U5) | no | — |
| effort.skill-frontmatter | adopt | C | all `.claude/skills/*/SKILL.md` | yes — KEEP_FIELDS drops `effort`; Codex maps to `model_reasoning_effort` (U5) | no | — |
| model.agent-frontmatter | adopt | C | `.claude/agents/*.md` | yes — renderer map-or-omit (U5) | no | — |
| effort.agent-frontmatter | adopt | C | `.claude/agents/*.md` | yes — Codex `model_reasoning_effort`; Cursor bracket param omitted (unverified) | no | — |
| workflows.tool | adopt | C | `.claude/agents/batch-evaluator.md` (fan-out), `.claude/skills/launch/SKILL.md` (batch stage note) | yes — fenced Claude-native section; sequential fallback preserves prior behavior (AE2) | no — owner-triggered only (KTD-11) | heightened-review (batch behavior) |
| agents.subagents | adopt | C | `.claude/skills/morning/SKILL.md`, `weekly`, `process-backlog` (background-subagent + model-tier dispatch notes) | yes — fenced or host-neutral phrasing | no | — |
| sched.cron-insession + sched.loop | document | E | `setup.sh` (disclosed-degraded only), `docs/portability.md` | no — never generated into skills | no | per manifest: not offered as enforced homes |
| sched.desktop | adopt | E | `setup.sh` automation offer (partial-enforcement local home) | no | report-only | disclosure required |
| sched.headless | adopt | E | `setup.sh` (launchd/cron wrapper — the fully-enforced local home) | no | report-only | — |
| sched.cloud-routines | adopt | E | `setup.sh` (cloud home + disclosure + teardown) | no | report-only | heightened-review (grant surface) |
| hooks.pretooluse + hooks.env-inheritance | adopt | C | `.claude/hooks/report-only-guard.sh`, `core/scripts/validate.py` exemption | no — hook never generated into portable tree | n/a — guard exists to police unattended runs | heightened-review (safety code) |
| perms.deny-syntax + perms.dontask + skills.disallowed-tools | adopt | C/D | watcher skills' frontmatter, wrapper profile in setup | no | report-only | heightened-review (allowed-tools surface) |
| sandbox.os | document | F | `docs/portability.md` note (optional OS-level hardening for the wrapper home) | no | — | — |
| agents.teams | document | F | `README.md`/`docs/index.html` capability story (opt-in, experimental) | no | no | — |
| goal.command | document | F | docs only (user-typed surface; skills cannot invoke) | no | no | — |
| checkpointing + plugins + fast-mode + ultrareview | document | F | `README.md` modernization story, `docs/portability.md` | no | no | — |
| workflows.keyword-human-only | adopt | D | watcher skills (report-only runs never attempt workflow orchestration — enforced upstream) | no | report-only | — |
| github.delta-engine | adopt | D | `.claude/skills/repo-watch/` (atom-poll → compare → `.diff` fallback order) | no | report-only | — |
| CLI-2026-09-11-14 | adopt | G | `CLAUDE.md` §Framework Self-Audit — `/skill-doctor` pointer (interactive only; the validator never runs it) | no — Claude-only pointer lives in `CLAUDE.md`, never in a generated body (KTD11) | no | — |
| CLI-2026-09-11-22 | adopt | G | `core/scripts/validate_checks.py` (`CURRENT_MODEL_IDS`), `docs/capabilities.md` roster row, `core/scripts/tests/test_validate_checks.py`, `core/scripts/tests/test_build_adapters.py` | no — raw model IDs stay out of skill and agent bodies (KTD10); the residual net enforces it | no | — |
| CLI-2026-09-11-38 | adopt | G | `setup.sh` (the three duplicated cloud-home spots), `docs/portability.md` (one sentence), `docs/capabilities.md` (`sched.cloud-routines`, `home.cloud`) — disclosure only, no home detection (KTD12) | no — never generated | report-only (cloud home) | heightened-review (setup surface), implemented-from: v2.1.251 |
| CLI-2026-09-11-60 | adopt | G | `core/scripts/validate_checks.py` (`check_bom`, fail-class per KTD5), `core/scripts/validate.py` wiring line, `core/scripts/tests/test_validate_checks.py` | n/a — validator code | no | heightened-review (validator) |
| CLI-2026-09-11-78 | adopt | G | `CLAUDE.md` §Framework Self-Audit — `claude plugin validate .` pointer (the validator never runs it) | no — Claude-only pointer lives in `CLAUDE.md` only (KTD11) | no | — |
| CLI-2026-09-11-99 | adopt | G (U13, post-commit) | owner memory `feedback_ultraplan_workflow.md` and its `MEMORY.md` index line — outside the repo; the PR description lists it as a side effect | n/a — not a repo file | no | — |
| CLI-2026-09-11-103 | adopt | G | as CLI-2026-09-11-22 plus the manifest fast-mode row; `CURSOR_MODEL_MAP` unchanged (`opus` → `claude-opus-4-8`, test-pinned) | no — as CLI-2026-09-11-22 (KTD10) | no | — |
| manifest-refresh-2026-09-11 | adopt | G | `docs/capabilities.md` — verified line to 2026-09-11 / v2.1.268; text edits on the hooks, permissions, headless, subagents, and workflows rows; three append-only rows (`absent.todo-tools`, `absent.ultraplan`, `skills.frontmatter-hooks`); folds the report's 106 document-class lines | no — manifest text | no | — |

## B. Model and effort tier assignments (executed by U7)

Tier vocabulary (provenance: CE-12 extraction/generation/ceiling, SP-08
explicit-tiering, GSD-08 effort ladder — re-implemented for this repo):
**mechanical** (haiku + low/medium) — capture, sync, scaffolding;
**structured** (sonnet + medium/high) — framework-fill, classification,
ops; **judgment** (inherit + high/xhigh) — synthesis, strategy, voice.
`inherit` is a deliberate assignment: follow the session model.

| file | model | effort | class |
|---|---|---|---|
| skills/ab-test | sonnet | medium | structured |
| skills/competitive-analysis | inherit | high | judgment |
| skills/decision | inherit | high | judgment |
| skills/discover-ideas | sonnet | medium | structured |
| skills/gtm-plan | inherit | high | judgment |
| skills/launch | inherit | high | judgment (orchestrator) |
| skills/lean-canvas | sonnet | high | structured |
| skills/log-meeting | haiku | low | mechanical |
| skills/make-slides | sonnet | medium | structured |
| skills/meeting-prep | sonnet | medium | structured |
| skills/meeting-sync | haiku | medium | mechanical |
| skills/morning | sonnet | medium | structured (daily ops) |
| skills/outcome-roadmap | inherit | high | judgment |
| skills/plan-okrs | inherit | high | judgment |
| skills/prd | inherit | high | judgment (flagship artifact) |
| skills/pre-mortem | inherit | high | judgment (adversarial) |
| skills/prioritize | sonnet | medium | structured (formulaic) |
| skills/process-backlog | sonnet | medium | structured (classification) |
| skills/quarterly | inherit | high | judgment |
| skills/refresh-goals | inherit | high | judgment (conversation) |
| skills/research-topic | inherit | high | judgment |
| skills/session-review | sonnet | medium | structured (capture) |
| skills/spec | inherit | xhigh | judgment — heaviest artifact; deliberate pin above session default |
| skills/spin-up | sonnet | medium | structured |
| skills/sprint-plan | sonnet | medium | structured |
| skills/user-stories | sonnet | high | structured (decomposition) |
| skills/validate-project | inherit | high | judgment |
| skills/weekly | inherit | high | judgment (pattern analysis) |
| skills/weekly-update | sonnet | medium | structured (memo) |
| skills/write | inherit | high | judgment (voice) |
| skills/cli-watch (new, U10) | sonnet | high | structured — fetch-classify on a schedule; pinned at creation |
| skills/repo-watch (new, U11) | sonnet | high | structured — same workload shape |
| agents/batch-evaluator | inherit | medium | orchestrator — volume eval; workers dispatched cheaper |
| agents/deep-research | inherit | high | judgment (multi-source synthesis) |
| agents/system-health | sonnet (existing pin) | medium | structured (diagnostic scan) |
| commands/analyze | inherit | high | judgment |

## C. Ecosystem adoptions (from the ledger, this initiative)

| id | verdict | wave | target files | degradation | unattended | tags |
|---|---|---|---|---|---|---|
| SP-03 + AS-03 | adopt | C | `.claude/skills/prd/SKILL.md`, `spec`, `process-backlog` — Common Rationalizations / Red Flags sections on the hard rules | no — portable prose | no | — |
| SP-04 | adopt | C | `AGENTS.md` — verification-before-completion evidence rule (coercive register explicitly not imported) | no | no | — |
| AS-10 | adopt | C | `AGENTS.md` — skill-first mandate (promoted from private host memory) | no | no | — |
| SP-15 | adopt | C | `AGENTS.md` — anti-sycophancy: feedback is evaluated, not performed | no | no | — |
| SP-16 | adopt | C | `AGENTS.md` — 3-failed-fixes → question the architecture | no | no | — |
| AS-09 | adopt | C | `AGENTS.md` — orchestration anti-patterns (user-as-orchestrator; no persona chains) | no | no | — |
| GB-05 | adopt | C | `AGENTS.md` — durable-artifact output rules (deterministic links, no chat-slop, preserve phrasing) | no | no | — |
| CE-05 | adopt | C | `.claude/skills/spec/SKILL.md` — section-map lazy-reading guidance for consumers of large specs | no | no | — |
| GSD-07 | adopt | C | `.claude/skills/session-review/SKILL.md` — learnings cite their originating artifact; never invented | no | report-only | — |
| CE-13 | adopt | C | `.claude/commands/analyze.md`, `.claude/skills/decision/SKILL.md` — position-freeze + project-floor evidence rules | no | no | — |
| SP-08 + CE-12 + GSD-08 | adopt | C | section B above (the tier vocabulary) + dispatch guidance in batch-evaluator | no | no | — |
| AS-05 + CE-15 + GS-05 | adopt | C | `.claude/hooks/report-only-guard.sh` + U9 profile design (pause taxonomy, accident-not-security framing, state-file mechanics) | no — hook not generated | n/a | heightened-review (safety code) |
| AS-07 | adopt | C | guard ships as script + companion doc + drill test (U9) | no | n/a | heightened-review (hooks) |
| GS-08 | adopt | D | watcher skills — report-only default / full manual twin modes | no | report-only | — |
| GB-06 | adopt | D | watcher skills — hardcoded-action gate: actions never parsed from fetched content | no | report-only | heightened-review (watcher safety) |
| GB-07 | adopt | D/E | watcher references + setup — cron hygiene (thin prompts, idempotency, stagger, sample-first) | no | report-only | — |
| AS-06 | adopt | D | watcher references — conditional-request freshness (304 = verification, not memory) | no | report-only | — |
| GB-11 | adopt | D | `.claude/skills/morning/SKILL.md` currency step — read-only guarantee + gap-honesty line | no | report-only | — |
| GB-10 | adopt-partial | E | `setup.sh` — consent-gated automation choice with stated costs/prerequisites (the cost-matrix posture; identity-doc half n/a) | no | no | — |
| GB-08 | adopt-partial | F | `core/scripts/validate.py` — blocking tracked-artifact secret-scan realizes the privacy-linter core; full genericization linter deferred | no | report-only | heightened-review (validator) |
| AS-12 | adopt | — | realized by this plan's own sequencing (characterization before mechanisms); recorded as corroboration, no new work | no | no | — |
| RW-2026-09-11-1 | adopt-partial | G | `.claude/skills/prd/SKILL.md` — Step 2 constraints-first checklist (floor + ratchets; no CONSTRAINTS.md file convention) | no — portable prose | no | — |
| RW-2026-09-11-2 | adopt | G | `.claude/skills/spec/SKILL.md` — Step 7 Phase 0 capability map for multi-capability PRDs | no — portable prose | no | — |
| RW-2026-09-11-3 | adopt | G | `.claude/skills/spec/SKILL.md` — Step 3 `--rebuild` in-progress soft refusal, `-rN` same-day archive suffix | no — portable prose | no | — |
| RW-2026-09-11-4 | adopt-partial | G | `AGENTS.md` §Context Management — budget levels (levels only; upstream recency ordering not imported) | no — host-neutral prose | no | — |
| RW-2026-09-11-5 | adopt-partial | G | `.claude/hooks/report-only-guard.sh`, `.claude/hooks/report-only-guard.md`, `core/scripts/tests/test_report_only_guard.py` — marker-time write fence (allowlisted targets, depth floor); the owner-check clause is not adopted, the guard denies instead | no — hook never generated | n/a — guard polices unattended runs | heightened-review (safety code), implemented-from: 45fd4a0 |
| RW-2026-09-11-6 | adopt | G | `docs/data-handling.md` (new), linked from `AGENTS.md` and `CONTRIBUTING.md` | no — doc | no | — |
| RW-2026-09-11-7 | adopt | G | `.claude/skills/session-review/SKILL.md` — extraction item 9 and the `## Skill gaps` template section (resolves GB-04) | no — portable prose | no | — |
| RW-2026-09-11-9 | document | G | none — the first-pass trim of `spec`/`prd`/`make-slides` found no verbatim-duplicated block to move; byte counts recorded on the ledger row; the full restructure stays deferred (SP-01, AS-11; FW-2026-09-06) | n/a | no | — |
| RW-2026-09-11-10 | adopt | G | `core/CODING_STANDARDS.md` (new), linked from `core/README.md` and `CONTRIBUTING.md` | no — doc | no | — |
| RW-2026-09-11-11 | adopt-partial | G | `.claude/skills/prd/SKILL.md` (Objective + Means shape), `.claude/skills/plan-okrs/SKILL.md` (same shape; `Means:` line per Objective) — no Key-Decision plumbing | no — portable prose | no | — |
| RW-2026-09-11-12 | adopt-partial | G | `.claude/skills/ab-test/SKILL.md` — matched-control, small-sample, and no-padding guardrails (prose, not statistics code) | no — portable prose | no | — |
| RW-2026-09-11-16 | adopt | G | `.claude/skills/decision/SKILL.md`, `.claude/skills/write/SKILL.md`, `.claude/skills/launch/SKILL.md` — Rationalization guard sections in the `/prd` shape | no — portable prose | no | — |
| RW-2026-09-11-17 | adopt | G | `CLAUDE.md` §Framework Self-Audit falsifiability bullet; `core/CODING_STANDARDS.md` §Tests | no — doc | no | — |
| RW-2026-09-11-18 | adopt | G | `.claude/skills/weekly/SKILL.md` — sub-step 8c before-measurement for rewrites | no — portable prose | no | — |
| RW-2026-09-11-19 | adopt-partial | G | `.claude/skills/discover-ideas/SKILL.md` — Step 1 three-path triage, owner-approval gated (`/refresh-goals` untouched) | no — portable prose | no | — |
| RW-2026-09-11-23 | adopt | G | `.claude/skills/decision/SKILL.md` — optional `amends:` / `amended_by:` fields and the reciprocity paragraph | no — portable prose | no | — |
| RW-2026-09-11-24 | adopt | G | `docs/ledger/adoption-matrix.md` — the Dispositions paragraph under Row contract above | no — doc | no | — |
| RW-2026-09-11-25 | adopt | G | `.claude/skills/weekly/SKILL.md`, `.claude/skills/quarterly/SKILL.md` — `## Findings` this-cycle vs carried-over blocks | no — portable prose | no | — |
| RW-2026-09-11-26 | document | G | none — no new hook this wave (KTD8): marker-time credential-read denial already exists and U4 closes the `Grep`/`Glob` content-dump routes; interactive sessions stay hook-free (July KTD-5); follow-up FW-2026-09-03 | n/a | no | heightened-review (hooks) |
| RW-2026-09-11-27 | adopt | G | `core/scripts/validate_checks.py` (`check_secret_bypass_instructions`, `CREDENTIAL_PATH_PATTERNS`), `core/scripts/validate.py` wiring, `core/scripts/tests/test_validate_checks.py` (guard-parity test) — warn-class `secret-bypass` | n/a — validator code | no | heightened-review (validator), implemented-from: c3a18b5 |
| RW-2026-09-11-28 | adopt | G | `.claude/hooks/report-only-guard.sh` and `.md` (bounded builtin reads, `TERM` trap, wiring block without `timeout`), `core/scripts/tests/test_report_only_guard.py` (stall and signal tests), `core/scripts/validate_checks.py` (`check_guard_wiring_timeout`, warns below 600) | no — hook never generated | n/a — guard polices unattended runs | heightened-review (safety code), implemented-from: 9eef1b7 |
| RW-2026-09-11-29 | adopt-partial | G | `core/scripts/validate_checks.py` (`project_progress_ratchet`) — `--staleness-report` only (KTD5, R31); a log-presence check, not transition validation | n/a — validator code, local report mode | no | — |
| RW-2026-09-11-30 | adopt | G | `.claude/skills/spec/SKILL.md` — Step 7 minimum-solution check; over-scope tags surfaced in the Step 9.5 review and Step 10 summary | no — portable prose | no | — |
| RW-2026-09-11-32 | adopt | G | `core/scripts/build_adapters.py`, `.agents/skills.lock.json` (new), `core/scripts/tests/test_build_adapters.py` — hashed manifest of generated bytes; `--check` gains the `manifest:` verdicts (resolves CE-10 with RW-2026-09-11-41) | no — generator code; the manifest lives outside the managed bases | no | heightened-review (generator) |
| RW-2026-09-11-33 | adopt-partial | G | `core/scripts/validate_checks.py` (`watcher_report_staleness`, `staleness_sections`) — `--staleness-report` only; the staleness half of the batch | n/a — validator code, local report mode | no | — |
| RW-2026-09-11-34 | adopt-partial | G | `AGENTS.md` §Session-End Reflection consent line; `.claude/skills/quarterly/SKILL.md` Step 7 named-command check — the timestamp/TTL half is a platform feature (v2.1.214), so no staleness frontmatter (KTD8) | no — host-neutral prose | no | heightened-review (memory/consent surface), implemented-from: d337920 |
| RW-2026-09-11-35 | adopt-partial | G | `setup.sh` — fail-closed posture line at the top of the automation block (statement only; the EOF default was verified, no ladder mechanics) | no — never generated | no | heightened-review (setup surface), implemented-from: 1ec6a6e |
| RW-2026-09-11-36 | adopt | G | `CONTRIBUTING.md` (new), linked from `README.md` and `core/README.md` | no — doc | no | — |
| RW-2026-09-11-37 | adopt | G | `core/scripts/validate_checks.py` (`check_backup_coverage`), `core/scripts/validate.py` wiring, `core/scripts/tests/test_validate_checks.py` — warn-class `backup-coverage` | n/a — validator code | no | — |
| RW-2026-09-11-40 | adopt-partial | G | `core/scripts/tests/test_report_only_guard.py` — side-effect (`DENY:` line in a temporary `guard.log`), wiring-JSON, stall, and signal assertions; the delta over AS-07 only (KTD8) | no — tests | n/a — guard polices unattended runs | heightened-review (guard test surface), implemented-from: c118e24 |
| RW-2026-09-11-41 | adopt | G | `core/scripts/build_adapters.py` — manifest-first, marker-second ownership; refuse-and-list unless `--force`; check 38 verdicts unchanged (resolves CE-10 with RW-2026-09-11-32) | no — generator code | no | heightened-review (generator/setup surface), implemented-from: c241216 |
| RW-2026-09-11-42 | adopt-partial | G | `.claude/skills/cli-watch/SKILL.md`, `.claude/skills/cli-watch/references/report-template.md`, `.claude/skills/repo-watch/SKILL.md`, `.claude/skills/repo-watch/references/report-template.md` — self-attested receipts section, `guard.log` reconciliation, the two recovery lines; no hook, no hash chain (KTD7) | no — portable prose (host-neutral receipts) | report-only | heightened-review (watcher enforcement surface), implemented-from: 1d41ee3 |
| RW-2026-09-11-43 | adopt | G | `.claude/agents/batch-evaluator.md`, `.claude/agents/deep-research.md` (Dispatch discipline paragraph); `AGENTS.md` §Working Conventions foreground-dispatch bullet | no — host-neutral prose, no Claude-only tokens | no | — |
| CE-10 | adopt | G | resolved by RW-2026-09-11-32/-41 — `core/scripts/build_adapters.py`, `.agents/skills.lock.json` (moved from §D on 2026-09-11) | no — generator code | no | heightened-review (generator) |
| GB-04 | adopt | G | resolved by RW-2026-09-11-7 — `.claude/skills/session-review/SKILL.md` `## Skill gaps` section, the friction-log half (moved from §D on 2026-09-11; CE-07 and GS-03 remain deferred there) | no — portable prose | no | — |
| RW-2026-09-12-1 | adapt | H | `core/scripts/workspace.py` (new loader plus the nine result builders), `core/mcp/server.py`, `core/scripts/tests/test_workspace.py`, `core/README.md`, `AGENTS.md` `list_tasks` bullet; consumer lines in `.claude/agents/system-health.md`, `.claude/skills/process-backlog/SKILL.md`, `.claude/skills/morning/SKILL.md` — every read tool carries `unreadable`, never a silent drop | n/a — MCP code; the consumer lines are portable prose | no | heightened-review (MCP handlers), (was GSD-U-3) |
| RW-2026-09-12-2 | adapt | H | `core/scripts/workspace.py`, `core/mcp/server.py` (`body_truncated` + `body_limit` per row), `core/scripts/tests/test_workspace.py`, `AGENTS.md`; consumer `.claude/agents/system-health.md` (reads the file when a row is clipped) | n/a — MCP code | no | heightened-review (MCP handlers), (was GB-U-9) |
| RW-2026-09-12-3 | adapt | H | `core/scripts/workspace.py`, `core/mcp/server.py` (`prune_completed_tasks` preview-by-default, strict `confirm`, `consent_given`), `core/scripts/tests/test_workspace.py`, `AGENTS.md` prune bullet; `.claude/skills/quarterly/SKILL.md` Step 3b consent beat | n/a — MCP code; the `/quarterly` step is portable prose | no | heightened-review (MCP handlers, destructive verb), (was GSD-U-24) |
| RW-2026-09-12-4 | adapt | H | as RW-2026-09-12-1..3 — the preview path writes nothing at all (no archive mkdir) and `/quarterly` Step 3b calls it first, recording a declined run | n/a — MCP code | no | heightened-review (MCP handlers), (was GB-U-2) |
| RW-2026-09-12-5 | adopt | H | `.gitignore` plus the index removal of the three tracked-but-ignored files (U1); `core/scripts/validate_checks.py` (`check_privacy_placement`), `core/scripts/validate.py` wiring, `core/scripts/tests/test_validate_checks.py` — warn class `privacy-placement` | n/a — validator code | no | heightened-review (validator, repo hygiene), (was GSD-U-20) |
| RW-2026-09-12-6 | adopt | H | `core/scripts/validate_checks.py` (`check_tracked_tree_hygiene`), `core/scripts/validate.py` wiring, `core/scripts/tests/test_validate_checks.py` — warn class `tree-hygiene`; `.gitignore` `node_modules` trailing slash (U1) | n/a — validator code | no | (was GB-U-13) |
| RW-2026-09-12-7 | adapt | H | `core/scripts/validate_checks.py` (`check_backup_coverage` three-state probe), `core/scripts/tests/test_validate_checks.py` (the silence test renamed and flipped) | n/a — validator code | no | (was GB-U-6) |
| RW-2026-09-12-8 | adapt | H | `core/scripts/validate.py` (five spawn sites, `SUBPROCESS_TIMEOUT` / `MCP_IMPORT_TIMEOUT`), `core/scripts/tests/test_validate_checks.py` (three stall drills), `core/scripts/tests/test_source_lints.py` (AST spawn lint), `core/CODING_STANDARDS.md` | n/a — validator code | no | heightened-review (validator), (was GSD-U-11) |
| RW-2026-09-12-9 | adapt | H | `core/scripts/validate_checks.py` (`mask_code`, `check_template_tokens`, `staleness_sections`), `core/scripts/tests/test_validate_checks.py`, `CLAUDE.md` local-report-mode bullet | n/a — validator code, local report mode | no | heightened-review (validator), (was CE-U-11) |
| RW-2026-09-12-10 | adapt | H | `core/scripts/validate_checks.py` (`check_source_pointers`), `core/scripts/tests/test_validate_checks.py`; writer stamps in `.claude/skills/weekly/SKILL.md`, `.claude/skills/quarterly/SKILL.md`, `.claude/skills/session-review/SKILL.md` | n/a — validator code, local report mode; the writer stamps are portable prose | no | (was GB-U-16) |
| RW-2026-09-12-11 | adapt | H | `core/scripts/tests/conftest.py` (session-start `HOME` / `XDG_CONFIG_HOME` sandbox, uv cache and memory dir forwarded), `core/scripts/tests/test_source_lints.py`, `core/CODING_STANDARDS.md` | n/a — test harness | no | heightened-review (test harness over live config), (was GSD-U-12) |
| RW-2026-09-12-12 | adapt | H | `core/scripts/tests/conftest.py` (autouse watch over four config files and the forwarded memory dir), `core/scripts/tests/test_source_lints.py` | n/a — test harness | no | (was GB-U-1) |
| RW-2026-09-12-13 | adapt | H | `core/scripts/tests/test_source_lints.py` (source-grep AST lint, allow-list with ceiling and stale-entry report), `core/CODING_STANDARDS.md` | n/a — test harness | no | heightened-review (test enforcement), (was GSD-U-18) |
| RW-2026-09-12-14 | adopt | H | `.gitignore` — `CLAUDE.local.md` and `AGENTS.local.md` beside the existing `.claude/settings.local.json` line | no — never generated | no | (was GB-U-14) |
| RW-2026-09-12-15 | adapt | H | `.claude/skills/spec/SKILL.md` Step 8 and `references/spec-template.md` §25, `.claude/skills/launch/SKILL.md` (gate before Stage 7 and before writing `active`), `.claude/skills/pre-mortem/SKILL.md` and its templates | no — portable prose | no | (was GSD-U-1) |
| RW-2026-09-12-16 | adapt | H | `.claude/skills/spec/SKILL.md` §19/§25 with `references/spec-template.md` and `references/tdd-guide.md`, `.claude/skills/user-stories/SKILL.md` and its two templates | no — portable prose | no | (was GSD-U-22) |
| RW-2026-09-12-17 | adapt | H | `.claude/skills/spec/SKILL.md` Step 9.5, `.claude/skills/pre-mortem/SKILL.md`, `.claude/skills/decision/SKILL.md` — glossed identifiers on first mention | no — portable prose | no | (was CE-U-1) |
| RW-2026-09-12-18 | adapt | H | `.claude/skills/spec/SKILL.md` Step 9.5 (decision-first issues), `.claude/skills/morning/SKILL.md` Step 6 (the Slack rendering keeps the decision lines) | no — portable prose | no | (was CE-U-2) |
| RW-2026-09-12-19 | adapt | H | `.claude/skills/decision/SKILL.md`, `.claude/skills/session-review/SKILL.md` — self-contained opening summary | no — portable prose | no | (was GB-U-4) |
| RW-2026-09-12-20 | adapt | H | `.claude/skills/refresh-goals/SKILL.md` Step 4, `.claude/skills/process-backlog/SKILL.md` Step 7 plus a rationalization-guard bullet, `.claude/skills/quarterly/SKILL.md` Step 3 pointer — 40% / 40-line shrink refusal, prose only (July KTD-5) | no — portable prose | no | heightened-review (curated-file writes), (was GSD-U-7) |
| RW-2026-09-12-21 | adapt | H | `.claude/skills/weekly/SKILL.md` (Steps 1b, 1c, 9), `.claude/skills/sprint-plan/SKILL.md` (Steps 3-4), `.claude/skills/morning/SKILL.md` Step 0, `.claude/skills/user-stories/references/task-from-story-template.md`, `AGENTS.md` task template | no — portable prose | no | (was GSD-U-2) |
| RW-2026-09-12-22 | adapt | H | `.claude/skills/process-backlog/SKILL.md` Step 3 (the slug rule), `.claude/skills/research-topic/SKILL.md` Step 2 (cites it; the old 50-character clause removed) | no — portable prose | no | (was GSD-U-6) |
| RW-2026-09-12-23 | adapt | H | `.claude/skills/validate-project/references/research-brief-template.md`, `.claude/skills/research-topic/references/research-brief-template.md`, `.claude/agents/deep-research.md`, `.claude/agents/batch-evaluator.md` — supported / refuted / insufficient dispositions | no — portable prose | no | (was GSD-U-15) |
| RW-2026-09-12-24 | adapt | H | `.claude/skills/meeting-sync/references/people-enrichment.md` steps 2-3, `.claude/skills/log-meeting/SKILL.md` Step 8 — attribution gate plus the untrusted-input block | no — portable prose | no | (was GB-U-11) |
| RW-2026-09-12-25 | adapt | H | `.claude/skills/meeting-sync/SKILL.md` and `references/people-enrichment.md`, `.claude/skills/meeting-prep/SKILL.md`, `.claude/skills/log-meeting/SKILL.md`, `.claude/skills/write/SKILL.md`, `.claude/skills/morning/SKILL.md`, `.claude/skills/quarterly/SKILL.md` Step 7b; `AGENTS.md` and `README.md` name the new verbs | no — portable prose | no | (was GB-U-19) |
| RW-2026-09-12-26 | adapt | H | `.claude/skills/cli-watch/SKILL.md` step 4, `.claude/skills/cli-watch/references/report-template.md` (`- Model roster:` line) — stop-and-note on a roster change | no — portable prose (no raw model id in a body, KTD10) | report-only | (was CE-U-16) |
| RW-2026-09-12-27 | adapt | H | `.claude/agents/batch-evaluator.md` (roster discipline, "Covered N of M"), `.claude/agents/system-health.md` (coverage graded off the two summary calls) | no — portable prose | no | (was GSD-U-25) |
| RW-2026-09-12-28 | adapt | H | `SECURITY.md` (new) §Instruction surfaces, `.claude/commands/analyze.md` (§2 bullet, §4 `Surface` column), `docs/data-handling.md` | no — portable prose; the command body cites `SECURITY.md` in backticks so no unresolvable link reaches the generated tree | no | (was GSD-U-13) |
| RW-2026-09-12-29 | adapt | H | `SECURITY.md` (new — reporting path, seven-row check table, no-CI sentence), `CONTRIBUTING.md` (PR-side note, ground-rules reporting bullet) | no — never generated | no | (was GB-U-18) |
| RW-2026-09-12-30 | adapt | H | `.github/pull_request_template.md` (new), `CONTRIBUTING.md` item 4 — intent, gate output, screenshot rule, security and agent disclosure | no — never generated | no | (was CE-U-14) |

## D. Deferred (recorded, post-initiative backlog — not silent skips)

| id | reason deferred |
|---|---|
| SP-01 | Rewriting all 30 skill descriptions to trigger-only form is a full content project; do it as its own gated pass with before/after routing evals (pairs with AS-01). |
| AS-01, SP-11 | Deterministic trigger/routing evals + skill-request smoke tests — valuable validator extensions; land after the modernized bar settles so the eval corpus (session-review prompts) reflects the new catalog. |
| AS-02 | Pressure-case behavioral evals — token-costing, LLM-judged; opt-in later. |
| CE-01 | Artifact-contract frontmatter across pipeline artifacts — touches every template + validator; deserves its own wave. |
| CE-02 | Return-to-caller envelopes for /launch internals — valuable once /launch orchestrates subagent stages formally. |
| CE-04 | Plan-immutability for spec WBS execution — adopt when a spec-executor skill exists. |
| CE-07, GS-03 | Learning-store upgrades (schemas, typed JSONL) — fold into a dedicated /session-review + /weekly redesign. GB-04 (friction log) left this row for §C on 2026-09-11, resolved by RW-2026-09-11-7. |
| CE-08 | Scratch-file payload channel for bulk fleets — adopt with the next batch-evaluator scale-up. |
| CE-11 | Capability probes in setup — setup already gains the automation offer this wave; probe framework later. |
| CE-14 | Skill-local personas for agent bodies — restructuring; needs its own design pass. |
| GS-01, GS-02, GS-10 | /launch review-posture upgrades (scope stance, auto-chain with reserved decisions, forcing questions) — batch into a /launch redesign wave. |
| GS-06 | Generator-injected shared preamble — after the marker mechanism (U5) has soaked. |
| GS-09 | Blast-radius stop heuristics — adopt with the next bulk-mutation workflow. |
| GS-11 | Skillify-style gated skill creation — pairs with /weekly proposal loop rework. |
| GSD-01, GSD-02, GSD-06 | STATE.md / continue-here / summary-frontmatter artifacts — a project-workspace evolution, own wave. |
| GSD-03, GSD-04, GSD-05 | Goal-backward criteria, verification abstention, drift repair — fold into /spec + validator after this initiative. |
| GSD-10 | Context-threshold monitor hook — hooks budget this initiative is the guard; revisit after. |
| GSD-11 | /next smart-entry router — cheap, but new-skill budget this wave went to the watchers. |
| GB-01, GB-02, GB-03, GB-09 | Filing-rules JSON, backlink law, RESOLVER, doctor JSON contract — knowledge-layer upgrades batched post-initiative. |
| SP-02, SP-05, SP-06, SP-07, SP-09, SP-10, SP-13, SP-17 | Authoring/method upgrades (skill TDD, bootstrap re-injection, forcing function, two-stage review, plan granularity, design gate, tool-map references, persuasion wording) — batch as a "skill-authoring standards" wave with SP-01. |
| CE-03 | Session-settled decision labels — adopt into `/decision` + `/spec` KTD sections as a dedicated convention pass (touches artifact templates). |
| GS-04 | Confidence-gated zero-noise review reporting — adopt into the review/audit agents alongside the deferred eval work (AS-01/SP-11), so the confidence bar and the routing evals land together. |
| AS-04 | Doubt-driven adversarial review (withhold-the-claim) — fold into `/pre-mortem` and the review loops with the SP-07 two-stage review in the skill-authoring-standards wave. |
| AS-08 | Standing Definition-of-Done reference cited by `/spec`/`/launch`/`/user-stories` — a knowledge/reference/ file + cross-refs; batch with the pipeline-artifact evolution. |
| AS-11 | Skill-authoring size lints (SKILL.md length, description shape) — warn-class validator additions; land after the eval-corpus settles (pairs with AS-01). |
| GS-07 | Trigger-phrase frontmatter for natural-language invocation — batch with the SP-01 trigger-only-description pass. |
| GSD-09 | Install-time per-host capability degradation in the generator — additive generator work after U5 has soaked (pairs with GS-06). |
| CE-06, CE-09 | Already available via the installed compound-engineering plugin — document usage when relevant; no re-implementation. |
| FW-2026-09-01 | Frontmatter-hook guard wiring plus a committed wrapper settings file — makes the guard present in every home by construction; heightened review of the July KTD-5 sentence ("wired by setup only in `settings.local.json`"). Deferred from the 2026-09-11 wave. |
| FW-2026-09-02 | SessionStart `home:` context line from `CLAUDE_CODE_REMOTE` / `CE_REPORT_ONLY`, replacing the skills' "Bash unavailable" structural check, which misclassifies cloud — KTD12 kept the 2026-09-11 wave to disclosure only. |
| FW-2026-09-03 | Secret-read guard hook returning `ask` when unmarked (RW-2026-09-11-26, recorded `document`) — needs a check-11 exemption plan and a shared bash-and-Python credential-pattern file; the two lists are kept identical by the parity test until then. |
| FW-2026-09-04 | Egress-sink scanner in the validator with a committed allowlist of today's four fetch-capable files — the 2026-09-11 receipts are self-attested (KTD7) and this is their independent check. |
| FW-2026-09-05 | `get_watcher_status` structured fields (`home`, `receipts`, `guard_denies_since_last_run`, `baseline_cursor`, `lock`) and a `/morning` token for guard denies — no new fields were added in the 2026-09-11 wave. |
| FW-2026-09-06 | Full SKILL.md restructure of `spec`, `prd`, `make-slides` with before/after routing evals — the RW-2026-09-11-9 first pass found nothing verbatim to move; SP-01 / AS-11 remain the owning deferrals and the `/weekly` before-measurement habit (RW-2026-09-11-18) is the prerequisite now in place. |
| FW-2026-09-07 | Wrapper `--allowed-tools` still lists `WebSearch` while the guard denies it — remove it from the plist and crontab templates in a setup-focused wave. |
| FW-2026-09-08 | `check_guard_wiring` reads only `type` and `command` — a full schema check of the hook entry (the 2026-09-11 wave added only the below-600 `timeout` notice). |
| RW-2026-09-12-31 (was GSD-U-21) | Opt-in pre-commit hook running `build_adapters.py --check` and the validator, offered by `setup.sh` — marked `document` by owner decision on 2026-09-12: interactive sessions stay hook-free (July KTD-5), and a validator run on every commit reverses that. The hashed adapter manifest (RW-2026-09-11-32) plus the same-commit regeneration rule in `core/CODING_STANDARDS.md` stay the mechanism; the residual gap is that between waves nothing mechanical stops a commit with stale adapters. Revisit only if a wave again lands with a stale manifest. |
| RW-2026-09-12-32 (was GB-U-20) | Non-Latin scripts preserved in slugs — the rule that landed (RW-2026-09-12-22) transliterates Latin diacritics and falls back to a dated slug otherwise, so a Cyrillic, Greek, or CJK title yields a dated filename rather than a broken or empty one. Preserving those scripts needs a transliteration table and a Unicode-aware tokenizer with no second consumer here; revisit if people pages carry non-Latin names in practice. |

## E. Not-applicable (ledger skips — reasoning lives on the ledger rows)

AS-13, AS-14, AS-15, GS-12, GSD-12 (machinery half), GB-12, GB-13, GB-14,
GB-15, SP-12, SP-14 — each records why the pattern doesn't fit this
system on its ledger row; no matrix action.

## Consolidation note

The U14 degradation-coverage join reads: section A/C rows with verdict
`adopt`/`adopt-partial` whose manifest id is classed `claude-native` and
whose target files are generated into the portable tree must name a
degradation mechanism in the `degradation` column (fence or renderer
rule). Rows marked `no — portable prose` are exempt by construction.
