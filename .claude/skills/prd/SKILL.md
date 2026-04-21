---
name: prd
description: >
  Generate a Product Requirements Document for a project. Use when creating a PRD,
  writing product specs, documenting requirements for a new feature, or when a project
  needs a prd.md file. Triggers on: "create a prd", "write prd for", "plan this feature",
  "requirements for", "spec out", "product spec", "hypothesis for", "what should we build".
  Also use proactively during backlog processing when a new project is created and needs
  a PRD, or when an existing project lacks a prd.md. Even if the user doesn't say "PRD"
  explicitly — if they're describing a product idea with enough detail to spec out, this
  skill applies. Do not use for early brainstorming or idea capture — use idea.md for
  that. This skill applies when formalizing requirements, not exploring.
  Runs non-interactively by default (safe for automated batch calls from `/process-backlog`);
  pass `--ask` for guided clarification via `AskUserQuestion`.
allowed-tools: Read Write Edit Glob Bash mcp__perplexity__* AskUserQuestion
argument-hint: "<project-name> [--ask]"
---

# Generate a Product Requirements Document

Create a comprehensive PRD that serves as the authoritative spec for a project — aligning
thinking and guiding what gets built. The PRD balances thoroughness with practicality
for a solo builder or small team.

The skill is **automation-first**: running `/prd <name>` drafts a complete PRD by
inferring all required fields from `idea.md` + `GOALS.md`, with low-confidence fields
flagged inline. Pass `--ask` when you want guided clarification via `AskUserQuestion`.

## Quick Start

**Default (non-interactive — automation-safe):**
`/prd ad-spend-anomaly-detector`
Reads idea.md + existing artifacts, auto-infers hypothesis / goal / scope / segment /
riskiest assumption, drafts a 10-section PRD to `projects/ad-spend-anomaly-detector/prd.md`,
flags low-confidence inferences inline, prints a summary, and returns without blocking.

**Opt-in interactive:**
`/prd ad-spend-anomaly-detector --ask`
Calls `AskUserQuestion` once with up to 4 batched questions (pre-filled from idea.md
and GOALS.md so you confirm rather than retype), then drafts the PRD with your answers.

For a complete example, read `.claude/skills/prd/references/example-prd.md`.

## Instructions

### Step 1: Parse Arguments and Gather Context

Parse `$ARGUMENTS` for:
- Required `<project-name>`
- Optional `--ask` flag (triggers interactive clarification; default is non-interactive)

Reject any project name containing `..`, `/`, or characters besides letters, numbers,
and hyphens.

Then:
1. Read `projects/<project-name>/idea.md` for project context and scope.
2. Read `GOALS.md` to understand how this project connects to broader goals and OKRs.
3. Check if `knowledge/research/projects/<project-name>.md` exists — if so, read the
   validation brief for market context.
4. Check if `projects/<project-name>/lean-canvas.md` exists — if so, use its business
   model insights.

If no idea.md exists, refuse to proceed — the skill does not fabricate PRDs from
scratch. Tell the user to run `/process-backlog` or describe the project in a new
`idea.md` first.

### Step 2: Clarifying Inputs (default non-interactive; `--ask` opt-in)

The skill needs 5 slots filled before drafting: Hypothesis, Primary goal/OKR, Scope,
Primary user segment, Riskiest assumption.

**Default path (no flag — used by `/process-backlog` and other batch callers):**
Auto-infer each slot from `idea.md` + `GOALS.md`. Never block on user input.

1. **Hypothesis** — infer from idea.md Context / Scope / problem framing; fill the
   canonical template: "We believe [user] will [behavior] because [reason]; we'll know
   if [metric crosses threshold]."
2. **Primary goal/OKR** — match idea.md topic to an objective in `GOALS.md` by
   semantic similarity; format as `GOALS.md › [Objective] › [KR#]`.
3. **Scope** — default to "Moderate" unless idea.md explicitly indicates otherwise
   (e.g., "quick MVP" → Minimal, "full solution" → Full).
4. **Primary user segment** — extract from idea.md Target Users / Context; otherwise
   best-guess from the problem description.
5. **Riskiest assumption** — pick the single assumption whose failure would kill the
   project, drawn from signals in idea.md.

Any slot where inference confidence is low **must** be flagged inline in the PRD:

```
**Hypothesis:** We believe... — [INFERRED — low confidence, rerun with --ask to refine]
```

Use the same `[INFERRED — low confidence, rerun with --ask to refine]` suffix on any
other field that was guessed rather than confidently derived.

**Opt-in path (`--ask` passed):** Call `AskUserQuestion` **once** with up to **4**
batched questions, each pre-filled from idea.md + GOALS.md so the user confirms
rather than retypes. The `AskUserQuestion` schema caps each call at 4 questions and
each question at 4 options (the tool auto-provides a free-text "Other" slot — do
not add it manually):

1. **Hypothesis** — 3 AI-drafted options + "Draft best guess, I'll revise" (4 total).
2. **Primary goal/OKR** — top-3 most-relevant `GOALS.md` objectives + "Not in GOALS.md
   (flag for refresh)" (4 total).
3. **Scope** — Minimal / Moderate / Full / Unsure (4 total).
4. **Primary user segment** — top-2 segments from idea.md + "Both" + "Unsure" (4 total).

**Riskiest assumption is not its own question** — to stay within the 4-question cap,
the LLM always auto-infers it from the other 4 answers plus idea.md signals. If the
inference confidence is low, flag it inline: `**Riskiest assumption:** [one sentence]
— [INFERRED — low confidence, rerun with --ask after refining earlier slots]`.

Never skip the write — the skill always produces a PRD file, even if every field ends
up inferred.

### Step 3: Research (only when `--ask` was passed)

Research is gated **strictly** by the `--ask` flag — that flag is the only observable
signal the skill has to tell an interactive run apart from a batch invocation by
`/process-backlog` or any other automated caller. **If `--ask` was not passed, skip
this step entirely** — no Perplexity calls, no network latency, no cost.

If `--ask` was passed AND the gathered context lacks market data or competitor
insight, you MAY run a focused research query using `perplexity_search` or
`perplexity_ask`:
- Who are the target users and what problem are they experiencing?
- What existing solutions or competitors serve this space?
- What's the opportunity signal — are people searching for this, paying for
  alternatives?

Keep research lightweight — the PRD captures what to build, not a full market
analysis (that's what `/validate-project` is for). If the user wants deeper research
on a direct non-`--ask` invocation, tell them to rerun with `--ask` or use
`/validate-project` first.

### Step 4: Think Before Writing

Before drafting, work through these questions:
- What problem are we solving, and for whom?
- Why now — has something changed that makes this timely?
- How will we know it succeeded? What's the measurable outcome?
- What's the smallest version that delivers value?
- What assumptions are we making that could be wrong?
- What's the riskiest assumption, and how will MVP test it?
- Which requirements are **P0** (kill-the-release), **P1** (important), **P2**
  (nice-to-have)?

### Step 5: Write the PRD

Read the PRD template at `.claude/skills/prd/references/prd-template.md` and fill in
each section. The template has 10 top-level sections — use all of them, adapting depth
to the project's pipeline stage per the Step 6 rubric.

Before writing, read `.claude/skills/prd/references/anti-patterns.md` and actively
avoid each of the 12 patterns.

Write for clarity — short sentences, no jargon. Write so a non-technical reader can
follow along. If a sentence requires domain knowledge to parse, rewrite it.

### Step 6: Adapt Depth to Project Stage

Read the `project_status` from idea.md frontmatter (idea / evaluating / ready / active)
and use this rubric:

| Stage | Lines | Features | FRs | Stories |
|---|---|---|---|---|
| idea | 80–150 | 3–5 | 3–5 | 2–3 |
| evaluating | 150–250 | 4–6 | 6–10 | 4–6 |
| active (incl. ready) | 200–300 | 5–8 | 10–15 | 6–10 |

At **idea** stage, Section 5.5 Technical Considerations may be skipped, and Section 8
Evidence may use just the single gap-flag line if no evidence exists yet.

At **evaluating** stage, all sections filled. MVP Entry / Exit / Kill criteria
required.

At **active** stage (incl. `ready`), Section 5.3 User Stories and 5.4 Functional
Requirements get full detail; acceptance criteria must be Given/When/Then-style or
explicit checklist conditions.

### Step 7: Save the PRD

Save to `projects/<project-name>/prd.md`.

Ensure the `projects/<project-name>/` directory exists (create with `mkdir -p` if
needed).

### Step 7.5: Quality Flags (soft, non-blocking)

After saving, run the 12-item anti-patterns check from
`.claude/skills/prd/references/anti-patterns.md` against the PRD you just wrote.
Print a structured review in this exact shape:

```
PRD Review: <project-name>

Completeness: X/10 sections populated (plus any conscious skips per Step 6)
Issues (K):
  1. [#N <name>] <one-line description>. Fix: <specific suggestion>.
  2. [#N <name>] <one-line description>. Fix: <specific suggestion>.
Strengths:
  ✅ <at least one — what the PRD does well>
Readiness: Ready for review | Minor gaps | Major gaps
Second-opinion trigger: No | Yes (<reason>)
```

**Readiness rubric (uniform across /prd, /spec, /gtm-plan, /pre-mortem):**
- `Ready for review` — 0 issues
- `Minor gaps` — 1–4 issues
- `Major gaps` — ≥5 issues

**Second-opinion trigger = Yes** if `Major gaps`, OR if the PRD describes an AI/LLM
surface but ships without at least one `[INFERRED]` flag on the AI behavior contract
slot (a signal the downstream `/spec` will need `--ask`).

If 0 issues, the Issues block renders `Issues: none`. Always emit at least one
Strength — if nothing stands out, name the single best-filled section.

**Do not block the save.** These are informational — the user decides whether to act
on them.

### Step 8: Present Summary

Present a concise summary:
- One-line project description
- Primary target user segment
- MVP scope (3-5 bullet points)
- Key assumptions to validate
- **Readiness verdict from Step 7.5** (Ready for review / Minor gaps / Major gaps)
- Any quality flags printed in Step 7.5
- Suggested next step in the pipeline (e.g., "Run `/validate-project` to research the
  market", "Run `/lean-canvas` to evaluate the business model", or "Run `/prd <name>
  --ask`" if confidence is low)

## Quality Standards

- Every section should connect back to the user's problem — if a section doesn't serve
  the user, it doesn't belong in the PRD.
- Flag assumptions explicitly rather than stating them as facts.
- Use concrete numbers and specifics over vague language ("reduce load time by 50%",
  not "improve performance").
- The MVP section is the most important — be opinionated about what's in and what's
  out.
- Write so a non-technical reader can follow — if a sentence requires domain knowledge
  to parse, rewrite it.
- User stories must have verifiable acceptance criteria — "works correctly" is bad,
  "shows confirmation dialog before deleting" is good.
- Functional requirements must be testable and unambiguous.
- **Each functional requirement tagged `[P0]`, `[P1]`, or `[P2]` inline** — format
  `FR-N [P-tier]: <behavior>`.
- **Success metrics split into `### 7a. Leading indicators` and `### 7b. Lagging
  indicators`** (periods match the template's exact heading form), each with a
  Frequency column.
- **Open Questions each carry an `[Owner: eng / user-research / data / self]` prefix.**
- Keep the total PRD within the stage band per Step 6.

## Checklist

Before saving the PRD, verify:

- [ ] Parsed `--ask` flag correctly (interactive only when passed)
- [ ] All 10 sections filled (or consciously skipped per Step 6 stage rubric)
- [ ] Section 1 contains a `**Hypothesis:**` line at the top
- [ ] Section 2 cites the primary Goal/OKR as a bullet (`GOALS.md › ... › KR#`)
- [ ] Key Results are measurable with targets and timeframes
- [ ] User stories are small, specific, with verifiable acceptance criteria, each
      carrying a `**Tied to FR:**` line
- [ ] Functional requirements are formatted `FR-N [P0|P1|P2]: <behavior>`
- [ ] Each assumption has a `tested-in-MVP: yes/no + method` column
- [ ] MVP scope is opinionated — "Won't build" list is non-empty and tags
      `(permanent)` vs Phase-2-deferred items
- [ ] MVP has explicit `Entry criteria`, `Exit criteria`, `Kill criteria`
- [ ] Success metrics split into Leading (7a) and Lagging (7b) with a Frequency column
- [ ] Section 8 Evidence has real bullets OR the explicit gap-flag line
- [ ] Each open question carries `[Owner: …]` prefix
- [ ] Contacts identified with a "Why them" column (specific reason they're listed)
- [ ] Saved to `projects/<project-name>/prd.md`
- [ ] Line count within stage band per Step 6 rubric
- [ ] Soft quality flags printed in Step 7.5 (if any)

## Notes

- PRDs are living documents — they evolve as the project progresses through the
  pipeline.
- If a validation brief or lean canvas exists, incorporate their findings rather than
  repeating the research.
- The PRD complements but doesn't replace the idea.md — idea.md captures the original
  spark, the PRD formalizes the spec.
- User stories in the PRD are initial high-level stories — the `/user-stories` skill
  later decomposes these into detailed buildable stories when the project is
  activated.
- **PRD does not duplicate adjacent skills:** no TAM / market-size analysis (that's
  `/validate-project`), no cost / revenue or pricing tiers (`/lean-canvas`), no
  channel / launch timeline (`/gtm-plan`), no failure-mode matrix (`/pre-mortem`).
  Link to those artifacts when they exist; summarize each in one line at most.
