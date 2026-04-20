---
name: spec
description: >
  Generate a technical design spec (spec.md) synthesizing a project's PRD, idea,
  and any available evaluation artifacts into one authoritative build-ready
  document — architecture, data model, interfaces, tech stack with rejected
  alternatives, and assumption ledger. Use when creating a spec, writing
  technical design, documenting architecture, deciding tech stack, defining
  APIs/schemas, or when a project needs a spec.md file. Triggers on: "write
  spec for", "technical design for", "design doc", "architecture for", "how
  should I build X", "spec out the implementation", "tech spec", "design this
  system", "pick a stack for". Also use proactively when a project moves from
  ready to active and lacks a spec.md, or when an engineer needs build
  direction before /user-stories decomposition. Even if the user doesn't say
  "spec" explicitly — if they're asking how to build something a PRD has
  already defined, this skill applies. Do not use for product requirements
  (that's /prd), risk analysis (/pre-mortem), or business-model work
  (/lean-canvas). This skill is how-to-build, not what-or-why-to-build.
  Runs non-interactively by default (safe for automated batch calls from
  /launch); pass `--ask` for guided clarification via AskUserQuestion.
  If spec.md already exists, pass `--deepen` to extend or `--rebuild` to
  replace (old version auto-archived).
allowed-tools: Read Write Edit Glob Bash mcp__perplexity__* mcp__manager-ai__get_project_artifacts AskUserQuestion
argument-hint: "<project-name> [--ask] [--deepen|--rebuild]"
---

# Generate a Technical Design Spec

Create a comprehensive technical spec that serves as the build contract for a project — an engineer (or Claude Code acting as one) should be able to start building from this document alone. Spec synthesizes PRD + evaluation artifacts; it does not restate them.

The skill is **automation-first**: running `/spec <name>` drafts a complete 23-section spec by inferring from `idea.md` + `prd.md` (+ any richer artifacts that exist), with low-confidence fields flagged `[INFERRED]`. Pass `--ask` for guided clarification via `AskUserQuestion`.

## Quick Start

**Default (non-interactive — automation-safe):**
`/spec ad-spend-anomaly-detector`
Reads idea.md + prd.md + any evaluation artifacts, auto-infers system shape / tech stack / data model / interfaces, drafts a 23-section spec to `projects/ad-spend-anomaly-detector/spec.md`, flags low-confidence inferences inline, prints a summary, and returns.

**Opt-in interactive:**
`/spec ad-spend-anomaly-detector --ask`
Calls `AskUserQuestion` once with 4 batched questions (pre-filled from PRD + idea.md), then drafts with your answers.

**Update existing spec:**
- `/spec ad-spend-anomaly-detector --deepen` — extends sparse sections, preserves decisions, bumps `revision`.
- `/spec ad-spend-anomaly-detector --rebuild` — archives prior spec to `spec.archived-YYYY-MM-DD.md`, drafts fresh.

For a complete example, read `.claude/skills/spec/references/example-spec.md`.

## Instructions

### Step 1: Parse Arguments and Validate

Parse `$ARGUMENTS` for:
- Required `<project-name>`
- Optional `--ask` flag (triggers interactive clarification; default is non-interactive)
- Optional `--deepen` OR `--rebuild` flag (mutually exclusive; controls behavior when `spec.md` already exists)

Reject any project name containing `..`, `/`, or characters besides letters, numbers, and hyphens.

### Step 2: Pre-flight — Gather Context

Check required inputs:
1. `projects/<project-name>/idea.md` must exist.
2. `projects/<project-name>/prd.md` must exist.

If `prd.md` is missing, refuse with:

> No PRD found. Run `/prd <name>` first — `/spec` synthesizes a PRD into a technical design, it does not invent one.

Then read inputs in this order, skipping silently if absent:
1. `projects/<project-name>/prd.md` (required — primary input)
2. `projects/<project-name>/idea.md` (required — context + `project_status`)
3. `GOALS.md` (goal alignment check)
4. `projects/<project-name>/lean-canvas.md` (cost constraints, customer segment)
5. `projects/<project-name>/gtm-plan.md` (channels, launch timeline)
6. `projects/<project-name>/pre-mortem.md` (technical risks → spec mitigations)
7. `projects/<project-name>/user-stories.md` (acceptance shapes the API layer)
8. `knowledge/research/projects/<project-name>.md` (competitor stack signals)
9. Glob `knowledge/decisions/*<project-name>*` (any existing ADRs)

Call `mcp__manager-ai__get_project_artifacts` to canonicalize what exists. Note missing-but-optional inputs at the top of the Step 10 summary.

### Step 3: Handle Existing spec.md (resume / deepen / rebuild)

If `projects/<project-name>/spec.md` exists:

- **`--rebuild`**: copy existing to `spec.archived-YYYY-MM-DD.md`, then draft fresh. Set frontmatter `supersedes: projects/<name>/spec.archived-YYYY-MM-DD.md`.
- **`--deepen`**: read existing spec, identify sparse sections (< 5 lines or containing `[INFERRED]`), extend only those. Preserve decisions already made. Bump `revision` counter. Add a row to §22 Changelog.
- **Default (no flag) + `--ask`**: call `AskUserQuestion` once: `Deepen / Rebuild / Skip`. Proceed per answer.
- **Default (no flag) + no `--ask`**: skip with soft flag: `"spec.md exists (revision N). Pass --deepen to extend or --rebuild to replace."` **Never clobber silently.**

### Step 4: Clarifying Inputs (default non-interactive; `--ask` opt-in)

The skill needs 4 top-level design slots filled before drafting: **system shape**, **tech stack**, **synchronicity**, **storage**.

**Default path (no flag — used by `/launch` and batch callers):**
Auto-infer each slot from idea.md Context (stack hints) + prd.md §5 Solution (surface, integrations, data). Never block on user input. Tag low-confidence slots `[INFERRED — low confidence, rerun with --ask to refine]` at point-of-use in the spec.

**Opt-in path (`--ask` passed):** Call `AskUserQuestion` **once** with up to **4** batched questions, each pre-filled from PRD + idea.md so the user confirms rather than retypes. Mark the LLM's best-guess option with `(Recommended)`:

1. **System shape**
   - Web app (browser-hosted UI)
   - API / background service (no UI)
   - CLI tool or personal-os skill *(Recommended when stack hints suggest)*
   - Native mobile or desktop app

2. **Tech stack direction**
   - TypeScript / Next.js on Vercel *(Recommended for web)*
   - Python (FastAPI / script / MCP wrapper) *(Recommended for skill/CLI)*
   - Swift / SwiftUI (iOS-first)
   - Match the stack already used by a sibling project in this workspace

3. **Synchronicity**
   - Synchronous — user waits for result (<3s) *(Recommended for tools)*
   - Async with immediate ack — result arrives via Slack / email / journal
   - Batch / scheduled — runs on cron, user reviews output
   - Streaming — incremental output as it generates

4. **Storage & state**
   - Files in this workspace (markdown + YAML frontmatter) *(Recommended — house pattern)*
   - SQLite / DuckDB (local single-file DB)
   - Managed cloud DB (Postgres via Neon / Supabase / Vercel)
   - Stateless — no persistence beyond caller context

Never skip the write — the skill always produces a spec file, even if every slot ends up inferred.

### Step 5: Surface Assumptions

Before drafting, extract critical technical assumptions from inputs. Cover at minimum:
- Expected scale (users, requests/day, data volume)
- Latency tolerance (real-time vs batch vs async-ok)
- Cost ceiling (hobby-free vs per-customer-economic)
- Team shape (solo vs team handoff)
- Distribution (web / mobile / CLI / API / embedded)
- Data sensitivity (public / user-owned / regulated)
- Integration obligations (existing Slack / Granola / manager-ai MCP, OAuth providers)

Each becomes a row in §2 Assumptions Ledger (what / source / risk if wrong / validation method). Tag low-confidence assumptions `[INFERRED — low confidence, rerun with --ask to refine]` at point-of-use.

### Step 6: Research (gated strictly by `--ask`)

Research is gated **strictly** by the `--ask` flag — that flag is the only observable signal the skill has to tell an interactive run apart from a batch invocation by `/launch` or another automated caller. **If `--ask` was not passed, skip this step entirely** — no Perplexity calls, no network latency, no cost.

If `--ask` was passed AND the stack direction is genuinely open, you MAY run one focused `perplexity_ask` query on current best patterns for the chosen domain (e.g., "best 2026 stack for an iOS-first meeting assistant shipping in 4 weeks"). Keep it to one call, one paragraph of synthesis.

### Step 7: Think Before Writing

Decide, in order:
1. **System shape** — CLI, web app, API service, background job, MCP server, skill-pack extension. This routes the whole spec.
2. **Data model** — entities, in what store, with what identity.
3. **Interfaces** — for each user-facing surface, sketch the contract (HTTP routes + JSON payloads / CLI args / tool schemas) concretely, not in prose.
4. **Tech stack** — name specific libraries/versions. For each major choice, name 2 rejected alternatives and why.
5. **Build order** — slice the P0 FRs into M1 walking skeleton → M2 MVP → M3 polish.
6. **Observability & failure** — what you log, how you know it works, how it fails.

No `TBD`, `TK`, or `…` anywhere. If you can't decide, write `[INFERRED — low confidence, rerun with --ask]` with the best guess so a human can still build against it.

### Step 8: Write the Spec

Read the template at `.claude/skills/spec/references/spec-template.md` and fill in each of the 23 sections.

Before writing, read `.claude/skills/spec/references/anti-patterns.md` and actively avoid each of the 10 patterns.

Sections render `N/A — <justification>` when inapplicable (e.g., `§10 External Integrations: N/A — no external services, pure local CLI`). Never omit sections.

Write for clarity — short sentences, concrete formats: API payloads as JSON blocks, data model as Markdown tables, architecture as Mermaid. Opinionated over vague.

### Step 9: Save the Spec

Save to `projects/<project-name>/spec.md`.

Append `projects/<project-name>/spec.md` to the `resource_refs:` array in `projects/<project-name>/idea.md` (create the array if absent).

Do **not** update `project_status` — that remains `/launch`'s responsibility.

### Step 9.5: Quality Flags (soft, non-blocking)

After saving, run the 10-item anti-patterns check from `.claude/skills/spec/references/anti-patterns.md` against the spec you just wrote. Print any violations as soft flags:

```
⚠ Quality flags (3):
  - #3 Tech choice without justification: §7 names "Next.js" without citing a rejected alternative
  - #4 Missing rejected alternatives: only 1 ADR entry in §18 — minimum expectation is 3
  - #9 Low-confidence inferences shipped unrefined: 4 INFERRED tags present;
       consider `/spec <name> --ask`
```

**Do not block the save.** These are informational — the user decides whether to act on them.

### Step 10: Present Summary

Print a concise summary:
- One-line project description
- System shape chosen (from §7.1)
- Primary stack one-liner (from frontmatter `primary_stack`)
- P0 components (from §7 architecture component table)
- INFERRED count + top 3 inferred slots
- Any quality flags from Step 9.5
- Suggested next step:
  - `user-stories.md` missing → `"Run /user-stories <name> --tasks to decompose this spec."`
  - 3+ INFERRED tags → `"Consider /spec <name> --ask to firm up the inferred choices."`
  - `project_status == ready` or `active` and stories exist → `"Run /sprint-plan to pick this week's slice."`

## Quality Standards

- The spec is a **synthesis artifact** — it does not restate the PRD. Link back to `prd.md §N` and add only build-relevant detail.
- Every tech choice has at least one rejected alternative in §18 (the ADR section).
- Every external service in §10 carries rate limits, auth method, and failure behavior.
- No section is empty: either filled, rendered `N/A — <justification>`, or flagged `[INFERRED]`.
- Assumption confidence is explicit — the frontmatter `confidence` field is `high | mixed | low` based on `inferred_count`.
- First-week tasks (§20) are code-producing — the first two may be setup, every task after must generate visible artifacts.
- Milestones (§19) use relative timeframes (week 1-2), not calendar dates.

## Checklist

Before saving, verify:

- [ ] Parsed `--ask` / `--deepen` / `--rebuild` flags correctly
- [ ] `idea.md` and `prd.md` confirmed present; refused gracefully if `prd.md` missing
- [ ] Handled existing `spec.md` (rebuilt with archive, deepened with revision bump, or preserved with soft flag)
- [ ] All 23 sections present (either filled or `N/A — justification`)
- [ ] Frontmatter includes every required field (title, project, date, status, author, stage, revision, confidence, inferred_count, system_shape, primary_stack, sources)
- [ ] §2 Assumptions Ledger has ≥1 row per assumption slot (scale, latency, cost, team, distribution, data, integrations)
- [ ] §7 Architecture has a Mermaid diagram (or `N/A — single binary` with justification)
- [ ] §9 API contracts use JSON blocks for payloads, not prose
- [ ] §10 Integrations include rate limits + auth + failure behavior
- [ ] §18 ADR has ≥3 rejected alternatives with "revisit when" triggers
- [ ] §19 Milestones use relative timeframes, not calendar dates
- [ ] §20 First-week tasks have ≥5 entries, ordered by dependency
- [ ] Saved to `projects/<project-name>/spec.md`
- [ ] `idea.md` `resource_refs` updated
- [ ] `project_status` NOT changed
- [ ] Soft quality flags printed in Step 9.5 (if any)

## Notes

- Specs are living documents — use `--deepen` to extend after new artifacts (pre-mortem, user-stories) land.
- Spec does NOT duplicate adjacent skills: no product requirements (PRD), no risk matrix (pre-mortem), no business model (lean-canvas), no channel strategy (gtm-plan). Link and summarize in one line max.
- `/spec` complements `/user-stories` — spec locks the architecture, user-stories decompose behavior into buildable increments. Run `/spec` **before** `/user-stories` so stories can cite concrete components.
- `/launch` inserts `/spec` as a non-blocking stage between `/pre-mortem` and `/user-stories`. You can also run `/spec` standalone whenever.
