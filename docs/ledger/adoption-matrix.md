# Adoption Matrix — 2026-07-20

The single gateable decision artifact merging the capability manifest
(`docs/capabilities.md`, U1) and the mining ledger
(`2026-07-20-ecosystem-mining.md`, U2). Implementation waves execute from
this file only; every wave-C/D/E/F change traces back to a row here.

**Gate record:** wave approvals in this run are executed under the owner's
standing instruction of 2026-07-20 ("complete the plan end-to-end,
iterate until perfect"); the initiative lands on a feature branch and the
pull request is the owner's final merge gate. Heightened-review rows are
additionally flagged in the PR description for explicit owner eyes.

**Row contract:** decision rows are markdown table rows keyed by a
manifest `id` or ledger ID in the first cell. Columns: source | verdict |
wave | target files | degradation rule | unattended | tags. Verdicts:
`adopt`, `adopt-partial`, `document`, `defer`, `not-applicable`.
`degradation` = yes → the mechanism that keeps generated adapters clean
(KEEP_FIELDS drop, fenced section with fallback, or renderer map).

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

## D. Deferred (recorded, post-initiative backlog — not silent skips)

| id | reason deferred |
|---|---|
| SP-01 | Rewriting all 30 skill descriptions to trigger-only form is a full content project; do it as its own gated pass with before/after routing evals (pairs with AS-01). |
| AS-01, SP-11 | Deterministic trigger/routing evals + skill-request smoke tests — valuable validator extensions; land after the modernized bar settles so the eval corpus (session-review prompts) reflects the new catalog. |
| AS-02 | Pressure-case behavioral evals — token-costing, LLM-judged; opt-in later. |
| CE-01 | Artifact-contract frontmatter across pipeline artifacts — touches every template + validator; deserves its own wave. |
| CE-02 | Return-to-caller envelopes for /launch internals — valuable once /launch orchestrates subagent stages formally. |
| CE-04 | Plan-immutability for spec WBS execution — adopt when a spec-executor skill exists. |
| CE-07, GS-03, GB-04 | Learning-store upgrades (schemas, typed JSONL, friction log) — fold into a dedicated /session-review + /weekly redesign. |
| CE-08 | Scratch-file payload channel for bulk fleets — adopt with the next batch-evaluator scale-up. |
| CE-10 | Generated-output install manifest — additive generator work; after U5 settles. |
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
