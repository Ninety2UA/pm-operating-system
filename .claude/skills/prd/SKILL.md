---
name: prd
model: inherit
effort: high
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

**Every section earns its place — a PRD nobody reads is worthless. It's your voice in the
room when you're not there. Be crisp, not complete: cut anything that doesn't help someone
decide or build.**

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

Then read `.claude/skills/prd/references/good-vs-bad.md` — it shows the bad→good form of
a Hypothesis, Problem/Evidence, Success Metric, and Scope line. Match the "good" column:
specific, numeric, falsifiable.

### Step 5: Write the PRD

Read the PRD template at `.claude/skills/prd/references/prd-template.md` and fill in
each section. The template has 10 top-level sections — use all of them at the
`evaluating` and `active` stages. **At the `idea` stage, emit only the lightweight
speclet subset defined in Step 6, not all 10 sections.** Adapt depth to the project's
pipeline stage per the Step 6 rubric.

Before writing, read both `.claude/skills/prd/references/anti-patterns.md` (avoid each
of the 12 patterns) and `.claude/skills/prd/references/good-vs-bad.md` (match the
"good" column for each section).

Write for clarity — short sentences, no jargon. Write so a non-technical reader can
follow along. If a sentence requires domain knowledge to parse, rewrite it.

### Step 6: Adapt Depth to Project Stage

Read the `project_status` from idea.md frontmatter (idea / evaluating / ready / active)
and use this rubric:

| Stage | Lines | Output |
|---|---|---|
| idea | 30–60 | **Speclet** — frontmatter + the 4 slots below. Not all 10 sections. |
| evaluating | 150–250 | Full template; 4–6 features, 6–10 FRs, 4–6 stories. |
| active (incl. ready) | 200–300 | Full template; 5–8 features, 10–15 FRs, 6–10 stories. |

At **idea** stage, do **not** draft a full PRD — a committed spec for an uncommitted idea
is wasted work. Emit a **speclet**: the YAML frontmatter (with `stage: idea`) plus only
these four slots:
1. **§1 Hypothesis** — the canonical "We believe…" line.
2. **§2 Problem / Background** — the problem, who has it, and the `GOALS.md › Objective ›
   KR#` link.
3. **Riskiest assumption** — the single assumption whose failure kills the idea.
4. **What we'd need to believe** — 2–4 bullets that must hold for this to be worth
   pursuing (these become the validation checklist).

Sections 3–10 are intentionally omitted until the project is promoted to `evaluating`,
which triggers the full template. Use the "Idea-stage speclet" block at the top of
prd-template.md as the exact shape.

At **evaluating** stage, all 10 sections filled. MVP Entry / Exit / Kill criteria
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

Completeness: X/10 sections populated (or N/4 speclet slots at the idea stage; plus any conscious skips per Step 6)
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

**Adversarial pass (interactive only):** When `Second-opinion trigger: Yes` **and**
`--ask` was passed, offer one role-based re-read via a single structured question with
options — **Skeptic** (attack the riskiest assumption and evidence gaps), **Engineer**
(probe feasibility and hidden/orphan FRs), **Designer** (probe the user flow and whether
the §4 workarounds are realistic), **Skip**. On a non-Skip choice, re-read the PRD through
that lens and **append** a short `Adversarial pass (<role>): <2–4 findings>` block to the
printed review — do **not** rewrite `prd.md`. On the default non-interactive path (no
`--ask`), never offer this — just print the `Second-opinion trigger` line as before.

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
- **Workarounds are proof of pain** — every entry in the §4 *Current Workaround* column
  should surface as a concrete §8 Evidence bullet. A workaround a user already built is
  the cheapest evidence the problem is real.
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
- **Success metrics split into `### 7a. Leading indicators`, `### 7b. Lagging
  indicators`, and `### 7c. Guardrail metrics`** (periods match the template's exact
  heading form), each with a Frequency column. 7c names counter-metrics that must not
  degrade (latency, error rate, cost) with a threshold instead of a target.
- **Open Questions each carry an `[Owner: eng / user-research / data / self]` prefix.**
- Keep the total PRD within the stage band per Step 6.

## Checklist

Before saving the PRD, verify:

- [ ] Parsed `--ask` flag correctly (interactive only when passed)
- [ ] At `evaluating`/`active`: all 10 sections filled (or consciously skipped per the
      Step 6 rubric). At `idea`: the 4 speclet slots filled (§1 Hypothesis, §2
      Problem/goal link, Riskiest assumption, What we'd need to believe) — items marked
      (evaluating+) below are N/A for a speclet.
- [ ] Section 1 contains a `**Hypothesis:**` line at the top
- [ ] Section 2 cites the primary Goal/OKR as a bullet (`GOALS.md › ... › KR#`)
- [ ] (evaluating+) Key Results are measurable with targets and timeframes
- [ ] (evaluating+) User stories are small, specific, with verifiable acceptance
      criteria, each carrying a `**Tied to FR:**` line
- [ ] (evaluating+) Functional requirements are formatted `FR-N [P0|P1|P2]: <behavior>`
- [ ] (evaluating+) Each assumption has a `tested-in-MVP: yes/no + method` column
- [ ] (evaluating+) MVP scope is opinionated — "Won't build" list is non-empty and tags
      `(permanent)` vs Phase-2-deferred items
- [ ] (evaluating+) MVP has explicit `Entry criteria`, `Exit criteria`, `Kill criteria`
- [ ] (evaluating+) Success metrics split into Leading (7a) and Lagging (7b) with a
      Frequency column; Guardrail (7c) added where the change could regress latency /
      error rate / cost
- [ ] (evaluating+) Section 8 Evidence has real bullets OR the explicit gap-flag line
- [ ] (evaluating+) Each open question carries `[Owner: …]` prefix
- [ ] (evaluating+) Contacts identified with a "Why them" column (specific reason listed)
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

## Rationalization guard

The PRD Rule (every prd.md is generated by this skill, never written manually) has no exceptions. Common rationalizations, pre-answered:

- *"It's a tiny project — a manual PRD is faster."* Speed is not the point; consistency of structure is what makes 100+ PRDs comparable and pipeline-scorable.
- *"The user described it fully; I'll just transcribe."* Transcription skips the sections that force product thinking (guardrail metrics, adversarial review). Run the skill.
- *"I'll write it now and backfill with the skill later."* Later never comes, and a manual file poisons duplicate detection. Red flag: an Edit/Write call targeting `prd.md` outside this skill is a violation, not a shortcut.
