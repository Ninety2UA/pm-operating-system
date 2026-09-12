---
name: spec
description: |-
  Generate a technical design spec (spec.md) — the HOW-only build contract an AI coding agent (or engineer) implements from alone: pinned tech stack + package manifest, module/file tree, C4 architecture, components & interfaces, a test-first Test List, a dependency-ordered task→sub-task Work Breakdown Structure, a Build Toolkit (which AI agents/skills/MCPs to use), and a Design & UI-UX tooling pipeline. Synthesizes the PRD; it does NOT restate it — it references prd.md §N and adds only build-deltas. Use when creating a spec, writing technical design, deciding tech stack, defining APIs/schemas, decomposing build tasks, or when a project needs a spec.md. Triggers on: "write spec for", "technical design for", "design doc", "architecture for", "how should I build X", "spec out the implementation", "tech spec", "break the build into tasks", "pick a stack for". Also use proactively when a project moves from ready to active and lacks a spec.md, or before /user-stories decomposition. Even if the user doesn't say "spec" — if they're asking HOW to build something a PRD has already defined, this skill applies. Do not use for product requirements (/prd), risk analysis (/pre-mortem), or business-model work (/lean-canvas). This skill is how-to-build, not what-or-why-to-build. Runs non-interactively by default (safe for automated batch calls from /launch); pass `--ask` for guided clarification + live tool/skill discovery + diagram rendering via structured questions. If spec.md already exists, pass `--deepen` to extend or `--rebuild` to replace (old version auto-archived; an in-progress spec is refused unless `--ask` confirms).
argument-hint: "<project-name> [--ask] [--deepen|--rebuild]"
generated_from: .claude/skills/spec/SKILL.md
source_sha256: b27217be5fbc54b98eca4c327ccdef85b518e55aa1c2a01dcc11f2c5c5415a52
x_generated_note: "do not edit — regenerate with: uv run core/scripts/build_adapters.py"
---

# Generate a Technical Design Spec

Create a **build contract** for a project — an engineer (or Claude Code acting as one) starts building from this document alone, without re-reading the PRD. The spec is two layers stacked: **Layer A** (narrative build trade-offs + the single riskiest *technical* decision) over **Layer B** (the machine-executable manifest + file tree + C4 + components + Test List + task graph an agent runs top-to-bottom).

**The one rule that keeps this from becoming an expanded PRD:** the PRD owns the PROBLEM (what/why); the spec owns the SOLUTION (how/how-to-build). *If a sentence would be equally true sitting in prd.md, it does not belong in spec.md — cut it and cite `prd.md §N`.* The §2 Build Delta table is where PRD needs get **linked, never copied**.

The skill is **automation-first**: running `/spec <name>` drafts a complete 29-section spec by inferring from `idea.md` + `prd.md` (+ richer artifacts if present), flagging low-confidence fields `[INFERRED]`. Pass `--ask` for guided clarification, live skill/MCP discovery, and Excalidraw diagram rendering.

## Quick Start

**Default (non-interactive — automation-safe):**
`/spec ad-spend-anomaly-detector`
Reads idea.md + prd.md (+ any artifacts), auto-infers system shape / tech stack / data model / interfaces / build tasks, drafts the 29-section spec to `projects/ad-spend-anomaly-detector/spec.md`, flags low-confidence inferences inline, emits `npx skills find` queries without running them, keeps diagrams as Mermaid, prints a summary, and returns.

**Opt-in interactive:**
`/spec ad-spend-anomaly-detector --ask`
Batches up to 4 clarifying questions (pre-filled from PRD + idea.md), MAY run live `skills.sh`/MCP-registry lookups, and offers to render §7/§8 diagrams as editable Excalidraw artifacts.

**Update existing spec:**
- `/spec <name> --deepen` — extends sparse sections, preserves decisions, bumps `revision`.
- `/spec <name> --rebuild` — archives prior spec to `spec.archived-YYYY-MM-DD.md` (`-rN` suffix on a same-day collision), drafts fresh; refuses softly when the spec is in progress unless `--ask` confirms (Step 3).

For a complete example, read `references/example-spec.md`.

## Instructions

### Step 1: Parse Arguments and Validate

Parse the arguments provided when you were invoked for: required `<project-name>`; optional `--ask`; optional `--deepen` OR `--rebuild` (mutually exclusive). Reject any project name containing `..`, `/`, or characters besides letters, numbers, and hyphens.

### Step 2: Pre-flight — Gather Context

Required inputs: `projects/<project-name>/idea.md` and `projects/<project-name>/prd.md` must exist. If `prd.md` is missing, refuse:

> No PRD found. Run `/prd <name>` first — `/spec` synthesizes a PRD into a technical design, it does not invent one.

Then read, skipping silently if absent: `prd.md` (required — primary), `idea.md` (required — context + `project_status`), `GOALS.md`, `lean-canvas.md`, `gtm-plan.md`, `pre-mortem.md` (→ §12/§18), `user-stories.md` (→ §8/§19/§20), `knowledge/research/projects/<project-name>.md`, and glob `knowledge/decisions/*<project-name>*` (existing ADRs → §23 `related_adrs`). Call the `get_project_artifacts` tool (manager-ai MCP server) to canonicalize what exists. Note missing-but-optional inputs at the top of the Step 10 summary.

### Step 3: Handle Existing spec.md (resume / deepen / rebuild)

If `projects/<project-name>/spec.md` exists:
- **`--rebuild`**: first decide whether the existing spec is **in progress**. It is when any one of these holds: a ticked `- [x] T###` line in its §20 WBS; a `tasks/*.md` whose `resource_refs` points under `projects/<project-name>/` and whose body cites one of this spec's T-IDs (T-IDs restart at `T001` per spec, so only tasks referencing this project's folder count); or `project_status: active` in `idea.md`. A freshly generated spec (no ticks, no consuming tasks, project not active) is never in progress.
  - **Not in progress:** copy to `spec.archived-YYYY-MM-DD.md` — on a same-day collision use `spec.archived-YYYY-MM-DD-rN.md`, where N is the archived spec's `revision` — draft fresh, set frontmatter `supersedes:`.
  - **In progress + no `--ask`:** refuse softly and stop: `"spec.md exists (revision N) and is in progress (<signal>). Pass --deepen, or pass --ask to confirm --rebuild."` Never archive an in-progress spec non-interactively.
  - **In progress + `--ask`:** confirm via the structured question (structured questions, one call): `Archive and rebuild (consuming tasks keep citing archived T-IDs) / Deepen instead / Skip`. Archive only on the first choice.
- **`--deepen`**: read existing, extend only sparse sections (< 5 lines or containing `[INFERRED]`), preserve decisions, bump `revision`, add a §27 Changelog row.
- **Default + `--ask`**: ask once `Deepen / Rebuild / Skip`; a `Rebuild` answer on an in-progress spec goes through the same confirmation as `--rebuild --ask` above.
- **Default + no `--ask`**: skip with soft flag: `"spec.md exists (revision N). Pass --deepen or --rebuild."` **Never clobber silently.** (RW-2026-09-11-3)

### Step 4: Clarifying Inputs (default non-interactive; `--ask` opt-in)

Four design slots must be filled before drafting: **system shape**, **tech stack**, **synchronicity**, **storage**.

**Default path (no flag — used by `/launch` and batch callers):** auto-infer each from idea.md Context (stack hints) + prd.md §5 Solution. Never block. Tag low-confidence slots `[INFERRED — low confidence, rerun with --ask to refine]` at point-of-use.

**Opt-in path (`--ask`):** call structured questions **once** with up to **4** batched questions (pre-filled; mark the best guess `(Recommended)`):
1. **System shape** — Web app · API/background service · CLI tool or personal-os skill · Native mobile/desktop.
2. **Tech stack** — TypeScript/Next.js on Vercel *(Rec. for web)* · Python (FastAPI/script/MCP) *(Rec. for skill/CLI)* · Swift/SwiftUI · Match a sibling project.
3. **Synchronicity** — Synchronous (<3s) · Async w/ ack · Batch/scheduled · Streaming.
4. **Storage & state** — Files in workspace (markdown+YAML) *(Rec. — house pattern)* · SQLite/DuckDB · Managed cloud DB · Stateless.

Never skip the write — the skill always produces a spec, even if every slot is inferred.

### Step 5: Surface Assumptions (→ §4)

Extract critical technical assumptions: expected scale, latency tolerance, cost ceiling, team shape, distribution, data sensitivity, integration obligations (Slack / Granola / manager-ai MCP / OAuth). Each becomes a §4 row (assumption / source / risk if wrong / validation method — name the test that validates it where possible). Tag low-confidence ones `[INFERRED — …]`.

### Step 6: Research (gated strictly by `--ask`)

Gated **strictly** by `--ask` — the only signal that tells an interactive run apart from a batch invocation. **If `--ask` was not passed, skip this step entirely** — no Perplexity calls, no live `skills.sh`/MCP-registry lookups, no network. This gate also covers the §21 Build Toolkit marketplace discovery and §22 generator-doc lookups.

If `--ask` was passed AND the stack/tooling is genuinely open, you MAY run focused `perplexity_ask` queries on current best patterns (one call, one paragraph each), and MAY hit `skills.sh` / `registry.modelcontextprotocol.io` to resolve §21 tool rows. In-repo skill/MCP recommendations are deterministic and ALWAYS emit regardless of this gate.

### Step 6.5: Capability & Design-Surface Detection (→ §21, §22)

Derive the build capability list from prd.md §5 + the inferred §7 architecture — look for: UI, web scraping, deployment, database, diagrams, file parsing, scheduling, LLM/model calls, auth. Map each capability to an **in-repo skill first** (UI→`/ui-ux-pro-max`, diagrams→`/excalidraw`, Next deploy→`/vercel:deploy`, scrape→`firecrawl`, QA→`/code-review`+`/verify`+`/run`, slides→`/make-slides`); queue a marketplace `npx skills find "<capability>"` query only for genuine gaps. Set `ui_pipeline` frontmatter from `system_shape`: web-app/mobile-app → a design pipeline (default `v0+shadcn`, or `excalidraw` for wireframe-only); api-service / cli-skill / background-job / mcp-server → `none`.

### Step 7: Think Before Writing

**Phase 0 — Capability map (multi-capability PRDs only; → §6, §20).** Before the file tree (item 3) and the build order (item 6), test whether `prd.md` §5 bundles several independently testable capabilities: distinct consumers or data, acceptance criteria that cluster into groups, or one capability that could be cut without rewriting the others. If it does, head §6 with a capability map and derive the file tree and the §20 phases from it:

| Module id | Owns (FRs) | Depends on | Build order |
|---|---|---|---|
| `csv-ingest` | FR-1 | — | 1 |
| `anomaly-detect` | FR-2, FR-3 | `csv-ingest` | 2 |

Module ids are stable kebab-case, assigned once and never renamed (`--deepen` appends rows, it never reorders); dependencies are one-way with no cycles — when two modules need each other, split the shared piece into a third module; each §20 task's trailing note names its module id. On the default path emit the map flagged `[INFERRED]` and never block; on `--ask`, confirm it with one structured question (`Approve / Merge two modules / Split a module / Reorder`) before drafting §6. A single-capability PRD skips Phase 0 entirely — do not emit a one-row map. (RW-2026-09-11-2)

Decide, in order:
1. **System shape** — routes the whole spec.
2. **Tech stack + manifest** — name specific libraries with **pinned majors** (§5); for each major, name 2 rejected alternatives.
3. **Module/file tree** (§6) — emit BEFORE the WBS so every task's file path resolves.
4. **Data model + interfaces** (§9–§11) — entities, signatures, payloads as concrete shapes, not prose.
5. **Test List FIRST** (§19) — derive one test per P0 acceptance criterion from prd.md §5.4 + user-stories **before** choosing implementation modules. Tests are the executable form of the requirements.
6. **Build order** (§20 WBS) — slice P0 FRs into Setup → Foundational → M1 walking skeleton → M2 MVP → M3, each impl task paired to a test ordered before it.
7. **Toolchain & design pipeline** (§21/§22) — map each §7 component to an in-repo skill, then a marketplace query; set `ui_pipeline`.
8. **Observability & failure** (§12/§16) — EARS error scenarios, what you log, how you know it works.
9. **AI surface detection** — grep `idea.md` + `prd.md` (case-insensitive) for: `LLM`, `Claude`, `GPT`, `OpenAI`, `Anthropic`, `prompt`, `AI-assisted`, `model call`, `embedding`, `chat completion`, `system prompt`. If any match → `ai_surface: true` → §18.A filled with 5 Good / 5 Bad / 6 Reject + cost/latency budget. If no match → §18.A renders `N/A — no model-call surface in MVP`. Never omit.

No `TBD`, `TK`, or `…`. If you can't decide, write `[INFERRED — low confidence, rerun with --ask]` with the best guess so a human can still build against it.

**Minimum-solution check (§20, run while writing the WBS):** for every implementation task, prefer the first option in this order that satisfies the FR: (1) existing project behavior or pattern, (2) the standard library, (3) a native platform capability, (4) an already-installed dependency (one in the §5 manifest), (5) new code. A task that lands on a later option when an earlier one suffices is **over-scoped**: keep the task, append `_(over-scope: prefer <option>)_` to its line, and list it in the Step 9.5 review and the Step 10 summary. This check never reduces requested scope, never overrides a locked decision (a §23 ADR, a Step 4 answer, or a PRD FR), and never drops required security, validation, error-handling, or verification tasks. (RW-2026-09-11-30)

### Step 8: Write the Spec

Read the template at `references/spec-template.md` and fill each of the **29 sections** (§0–§28). For the format-heavy sections, read the matching guide first: `references/wbs-guide.md` (§20), `references/tdd-guide.md` (§19), `references/tech-manifest-guide.md` (§5/§6), `references/tooling-catalog.md` (§21), `references/ears-primer.md` (§12/§18.A). Before writing, read `references/anti-patterns.md` and actively avoid each of the **18** patterns.

**Reference-not-restate (the core instruction):** for §2 Build Delta, do **not** restate FR text — emit only `FR-id (ref prd.md §5.4) → target module/file → interface signature → WBS task IDs → tests`. For §3, demote product goals to a one-line `> Intent: prd.md §3` pointer and spend the section on engineering Non-Goals. Any line that re-explains *what/why* a feature exists belongs in the PRD — cut it and cite.

**Stage-scaling (key off PRD depth, not the status label):** emit the **full** spec — pinned manifest, file tree, Test List, ≥12-task WBS, full toolkit/design tables — whenever `prd.md` is a full PRD (has a §5.4 Functional Requirements section, or is more than ~100 lines). Emit the **thin skeleton** (§0–§4 + §7 Context-level + §25 one-liners; render §5/§6/§19/§20/§21/§22 as `N/A — populated once the PRD is built out`) ONLY when `prd.md` is an idea-stage *speclet* (the 4-slot version with no FRs). Rationale: projects often sit at `project_status: idea` while carrying a full PRD + artifacts — scale off what the PRD actually contains so a rich PRD always yields a rich spec.

**One-way doors (§23 → §25):** every §23 ADR carries `**Reversibility:** easy | hard | irreversible — <rationale>`, and the rationale names the migration, contract, or dependent system that makes the undo expensive — "hard to change" is not a rationale, and unsure rates `easy`, because a spec that rates everything irreversible gates nothing. (RW-2026-09-12-15) The rating is on the decision the task implements, not on how hard the work is. For an `irreversible` rating the ADR's `**Confirmation:**` field names the gate that must clear before the dependent task starts, and the §25 milestone holding that task gains the acceptance line `one-way door ADR-n confirmed`. This skill records and places the door and never stops for one; the confirmation beat fires in `/launch`, where a human is present.

**Failing direction (§19 → §25):** every automated §19 Test List row states in its `fails when` column the observable signal that shows the check did its work — a non-zero exit, a named string in the output, a missing line. (RW-2026-09-12-16) The authoring test is: if this command were silently doing nothing, what in its output would tell me? With no answer, fix the command instead of inventing a signal. Manual-lane rows carry `manual` instead, which is this system's own escape and never a licence to leave an automated row bare. Reject whole-value placeholders (`TBD`, `TODO`, `N/A`, `none`, `unknown`, `?`, `-`, any case) and bare restatements that carry no information (`the command fails`, `it errors`). Each §25 Acceptance & Verification command carries the same signal as `→ fails when: <signal>`, or is marked `manual:`.

Sections render `N/A — <justification>` when inapplicable (e.g., `§22: N/A — no user-facing UI; interface contracts in §11`). Never omit sections. Write for clarity — JSON blocks for payloads, Markdown tables for data, Mermaid for diagrams. Opinionated over vague.

**Diagrams (§7/§8):** Mermaid by default (batch-safe). On the `--ask` path, OFFER to render the C4 + runtime diagrams as editable Excalidraw artifacts via `/excalidraw` into `projects/<project-name>/diagrams/` (requires the canvas server on :3000 — if it's not up, note that and keep Mermaid). Link any rendered artifacts in §28.

### Step 9: Save the Spec

Save to `projects/<project-name>/spec.md`. Append it to the `resource_refs:` array in `idea.md` (create the array if absent). Emit any substantial §23 MADR decisions as `knowledge/decisions/YYYY-MM-DD-<project-name>-<slug>.md` (project-scoped + dated — collision-free across projects, and found by the Step 2 `*<project-name>*` glob) and list them in frontmatter `related_adrs`. Do **not** update `project_status` — that remains `/launch`'s responsibility.

### Step 9.5: Quality Flags (soft, non-blocking)

After saving, run these checks and print a structured review. **Do not block the save** — these are informational.

**(1) Coverage Check** (run first): assert every `prd.md §5.4` FR appears in the §2 Build Delta table AND has ≥1 §20 WBS task AND (for P0) ≥1 §19 test. Print `Coverage: N/M PRD FRs traced to component+task+test`.

**(2) PRD-echo Check:** flag if >20% of spec lines restate PRD what/why (a line that would read the same in prd.md). The §2 Build Delta table is the structural control; this ratio is the backstop.

**(3) Constitution conformance:** flag any tech choice that deviates from the §1 house defaults without a §1.1 Complexity-Tracking row + a §23 ADR.

**(4) Anti-patterns scan:** the 18-item check from `references/anti-patterns.md`.

**(5) Over-scope scan:** list every §20 task carrying an `over-scope` tag with its preferred option (Step 7 minimum-solution check). The scan reports; it never edits scope. Render each entry as `T### (task title)` so the line reads without a lookup. (RW-2026-09-12-17)

**(6) One-way door placement:** flag every §23 ADR rated `irreversible` whose `**Confirmation:**` names no gate, or whose named gate has no matching acceptance line in the §25 milestone holding the dependent task. (RW-2026-09-12-15) Report the gap; never rewrite the rating.

**(7) Failing-direction coverage:** count the automated §19 rows and §25 commands that state a failing direction, list the ids that state none, and flag any value that is a placeholder or a restatement. (RW-2026-09-12-16) Quote the row as written — never author the signal on the spec's behalf, because a prescribed one is copied verbatim and carries no information.

```
Spec Review: <project-name>

Coverage: N/M PRD FRs traced to component+task+test  (P0: X/Y)
Completeness: X/29 sections populated (N/A-with-justification counts as populated)
Over-scoped: K tasks (T### (task title) → prefer <option>, …) | none
One-way doors: K irreversible ADRs (ADR-n (title) → confirmed at <gate>, …) | none
Failing direction stated: N of M automated rows
Issues (K):
  1. [#N <name>] <what it costs if this ships unchanged — no bare identifier>. Fix: <one sentence of intent>. Basis: <at most two sentences>.
Strengths:
  ✅ <at least one — what the spec does well>
Readiness: Ready for review | Minor gaps | Major gaps
Second-opinion trigger: No | Yes (<reason>)
```

**Readiness rubric (uniform across /prd, /spec, /gtm-plan, /pre-mortem):** `Ready for review` — 0 issues · `Minor gaps` — 1–4 · `Major gaps` — ≥5.

**Second-opinion trigger = Yes** if `Major gaps`, OR P0 Coverage <100%, OR the spec describes an AI/LLM surface but §18.A is absent / ships <5 Good / <5 Bad / <6 Reject, OR §21/§22 names a code generator without a §19 generated-code-review lane + §18 SAST control.

Each Issues line is decision-first: the opening sentence is the cost of leaving the finding as it stands and carries no bare identifier, the Fix is one sentence of intent, and the Basis is at most two sentences with the full trace available on request. (RW-2026-09-12-18) Gloss every document identifier at its first mention in a line — `ADR-3 (SQLite over Postgres)`, `T012 (parse CSV header)`, `FR-2 (anomaly severity)` — and leave later mentions in that line bare; when the title has fallen out of context, re-read the section rather than print a bare id. (RW-2026-09-12-17)

If 0 issues, render `Issues: none`. Always emit ≥1 Strength.

### Step 10: Present Summary

Print: one-line project description · system shape (§0) · primary stack one-liner (frontmatter `primary_stack`) · P0 components (§10) · WBS task count + first milestone · INFERRED count + top 3 inferred slots · **Coverage + Readiness verdict (Step 9.5)** · any quality flags · over-scoped task count (Step 9.5) · the one-way doors: each irreversible §23 ADR as `ADR-n (title)` with the gate that confirms it, or `none` · failing-direction coverage (Step 9.5) · suggested next step:
- `project_status == ready`/`active` → `"Run /user-stories <name> --tasks — it will consume this spec's WBS T-IDs."`
- 3+ INFERRED → `"Consider /spec <name> --ask to firm up the inferred choices (and run live skill/MCP discovery)."`
- stories exist → `"Run /sprint-plan to pick this week's slice from the spec's WBS."`

## Quality Standards

- The spec is a **synthesis artifact** — it does not restate the PRD. Link `prd.md §N` and add only build-relevant detail. *If a sentence would be equally true in the PRD, cut it.*
- Every build section names target **file path(s)**, an explicit **Out-of-Scope** line (§3), and (for milestones) a closing **executable acceptance check** (§25).
- Every P0 FR maps to ≥1 named **test authored before** its implementation file (§19 → §20).
- A stack is named only with a **pinned, registry-verifiable manifest** (§5) + a **≥6-path file tree** (§6) — never libraries-in-prose.
- Every tech choice deviating from the §1 house stack has a §23 MADR ADR; every external service in §13 carries rate limits, auth, and failure behavior.
- The §21 Build Toolkit names ≥1 build agent, ≥1 in-repo skill, required MCP servers (fully-qualified `Server: tool`), and a `find-skills` pointer per capability gap. §21/§22 rows are build-deltas — a row copyable verbatim into another project is too generic.
- If §21/§22 names a code-generating tool, §19 MUST have a generated-code-review lane and §18 the SAST + package-existence control.
- No section is empty: filled, `N/A — <justification>`, or `[INFERRED]`. Milestones (§25) use relative timeframes, not calendar dates.

## Checklist

Before saving, verify:

- [ ] Parsed `--ask` / `--deepen` / `--rebuild` correctly
- [ ] `idea.md` + `prd.md` present; refused gracefully if `prd.md` missing
- [ ] Handled existing `spec.md` (archived rebuild, `-rN` suffix on a same-day collision / in-progress rebuild refused without `--ask`, confirmed with it / revision-bumped deepen / preserved with soft flag)
- [ ] All 29 sections present (filled or `N/A — justification`); stage-scaled per `project_status`
- [ ] Frontmatter has every required field incl. `upstream_prd`, `build_agent`, `ui_pipeline`, `primary_stack`, `confidence`, `inferred_count`, `system_shape`
- [ ] §2 Build Delta references prd.md FRs WITHOUT restating them; §2.1 maps every P0 FR → module + task + test
- [ ] §3 product goals are a one-line back-reference; engineering Non-Goals are non-empty
- [ ] §5 every dependency pinned (major) with a manifest excerpt; no libraries-in-prose
- [ ] §6 file tree has ≥6 real paths; every §20 task path resolves to a node
- [ ] Phase 0 capability map heads §6 for a multi-capability PRD (stable kebab-case ids, one-way deps, no cycles, build order) — skipped entirely for a single capability
- [ ] §7 C4 (Context + Container min) with protocol-labeled edges (or `N/A — single binary`)
- [ ] §1 Build Constitution present; every deviation has a §1.1 row + §23 ADR
- [ ] §19 Test List: every P0 acceptance criterion → ≥1 named test ordered before its impl task
- [ ] §19 every automated row and §25 command states its failing direction or is marked manual
- [ ] §20 WBS ≥12 tasks (active stage) with stable T-IDs, file path + FR back-ref + paired test per impl task, `[P]` markers, per-milestone Checkpoints, dependency graph
- [ ] §20 minimum-solution check run: over-scoped tasks tagged and reported; requested scope and locked decisions untouched
- [ ] §21 Build Toolkit gate met (agent + in-repo skills + MCP `Server: tool` + find-skills pointers, all traceable)
- [ ] §22 Design pipeline present (or justified `N/A` for headless); generated-code review lane exists if a generator is named
- [ ] §18.A AI Behavior Contract filled (5/5/6 + budget) if AI surface detected, else `N/A — no model-call surface`
- [ ] §23 MADR ≥3 records with Confirmation/revisit-when; substantial ones emitted to `knowledge/decisions/`
- [ ] §23 every ADR rated easy/hard/irreversible with a rationale naming the migration, contract, or dependent system; every irreversible one names its gate and has the matching §25 acceptance line
- [ ] §25 every milestone ends in an executable Acceptance & Verification command
- [ ] Saved to `projects/<project-name>/spec.md`; `idea.md` `resource_refs` updated; `project_status` NOT changed
- [ ] Step 9.5 Coverage + soft flags printed

## Notes

- Specs are living documents — use `--deepen` after new artifacts (pre-mortem, user-stories) land.
- **Spec owns the build task graph.** §20 emits stable `T-IDs`; `/user-stories --tasks` and `/sprint-plan` **consume** them as the decomposition source of truth rather than re-deriving. Run `/spec` **before** `/user-stories` so stories cite concrete tasks/components.
- Spec does NOT duplicate adjacent skills: no product requirements (PRD), no risk matrix (pre-mortem), no business model (lean-canvas), no channel strategy (gtm-plan). Link and summarize in one line max.
- `/launch` inserts `/spec` as a non-blocking stage between `/pre-mortem` and `/user-stories`. You can also run `/spec` standalone whenever.

## Rationalization guard

The Spec Rule (every spec.md comes from this skill; updates via `--deepen`/`--rebuild`) has no exceptions:

- *"It's just a small tech note — I'll add it to spec.md directly."* Direct edits break revision archiving and drift from the 29-section contract. Use `--deepen`.
- *"The PRD already implies the stack."* Implication is not a pinned manifest. The spec exists to remove every such inference from build time.
- *"Time pressure — skip the Test List this once."* The Test List is what makes the WBS executable test-first; without it the spec is a summary, not a build contract.

## For consumers of a generated spec

A finished spec.md is long by design. Do not read it end-to-end to act on it: scan the section headings first, read §1 (Overview) and the section your task cites, and pull other sections only when referenced. (CE-05)
