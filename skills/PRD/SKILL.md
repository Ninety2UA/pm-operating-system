---
name: PRD
description: >
  Generate a Product Requirements Document for a project. Use when creating a PRD,
  writing product specs, documenting requirements for a new feature, or when a project
  needs a prd.md file. Triggers on: "create a prd", "write prd for", "plan this feature",
  "requirements for", "spec out", "product spec", "what should we build". Also use
  proactively during backlog processing when a new project is created and needs a PRD,
  or when an existing project lacks a prd.md. Even if the user doesn't say "PRD"
  explicitly — if they're describing a product idea with enough detail to spec out,
  this skill applies. Do not use for early brainstorming or idea capture — use idea.md
  for that. This skill applies when formalizing requirements, not exploring.
allowed-tools: Read Write Edit Glob Bash mcp__perplexity__*
disable-model-invocation: true
user-invocable: true
argument-hint: "<project-name>"
---

# Generate a Product Requirements Document

Create a comprehensive PRD that serves as the authoritative spec for a project — aligning
stakeholder thinking and guiding what gets built. The PRD balances thoroughness with
practicality for a solo builder or small team.

## Quick Start

User: `/PRD ad-spend-anomaly-detector`
Result: Reads idea.md and existing artifacts, optionally asks clarifying questions,
writes a 10-section PRD to `Projects/ad-spend-anomaly-detector/prd.md`, and presents
a summary with suggested next pipeline step.

For a complete example, read `${CLAUDE_SKILL_DIR}/references/example-prd.md`.

## Instructions

### Step 1: Gather Context

1. Read `Projects/<project-name>/idea.md` for the project context and scope.
2. Read `GOALS.md` to understand how this project connects to broader goals and OKRs.
3. Check if `Knowledge/research/projects/<project-name>.md` exists — if so, read the
   validation brief for market context.
4. Check if `Projects/<project-name>/lean-canvas.md` exists — if so, use the business
   model insights.

If no idea.md exists, ask the user to describe the project before proceeding.

Reject any project name containing `..`, `/`, or characters besides letters, numbers,
and hyphens.

### Step 2: Clarifying Questions

If the project context is ambiguous, ask 3-5 essential questions with lettered options
for quick iteration. Focus on gaps in the gathered context:

```
1. What's the primary goal?
   A. Solve a specific user pain point
   B. Generate revenue / monetize
   C. Build portfolio / credibility
   D. Other: [please specify]

2. Who is the primary user?
   A. [Segment from idea.md]
   B. [Alternative segment]
   C. Both
   D. Not sure yet

3. What scope feels right for v1?
   A. Minimal — one core feature, ship fast
   B. Moderate — 3-5 features, solid MVP
   C. Full — comprehensive solution
```

This lets the user respond with "1A, 2B, 3A" for fast alignment. Skip this step if the
idea.md and existing artifacts provide clear answers.

### Step 3: Research (if needed)

If the gathered context lacks market data or competitor insight, run a focused research
query using `perplexity_search` or `perplexity_ask`:
- Who are the target users and what problem are they experiencing?
- What existing solutions or competitors serve this space?
- What's the opportunity signal — are people searching for this, paying for alternatives?

Keep research lightweight — the PRD captures what to build, not a full market analysis
(that's what `/validate-project` is for).

### Step 4: Think Before Writing

Before drafting, work through these questions:
- What problem are we solving, and for whom?
- Why now — has something changed that makes this timely?
- How will we know it succeeded? What's the measurable outcome?
- What's the smallest version that delivers value?
- What assumptions are we making that could be wrong?

### Step 5: Write the PRD

Read the PRD template at `${CLAUDE_SKILL_DIR}/references/prd-template.md` and fill in
each section. The template has 10 sections — use all of them, adapting depth to the
project's pipeline stage.

Write for clarity — short sentences, no jargon. Write so a non-technical reader can
follow along. If a sentence requires domain knowledge to parse, rewrite it.

### Step 6: Adapt Depth to Project Stage

Not every project needs the same level of detail:

- **Idea stage** — Focus on sections 1-5 (problem, users, value). Keep solution
  high-level. Features can be bullet points. User stories and functional requirements
  can be brief (2-3 each).
- **Evaluating stage** — Full PRD with all 10 sections. Solution section should be
  specific enough that someone could start building. Include 4-6 user stories.
- **Active stage** — PRD should be complete and actionable. Features need detailed
  acceptance criteria. User flows need specifics. Functional requirements should be
  exhaustive.

Match the depth to where the project is in the pipeline.

### Step 7: Save the PRD

Save to `Projects/<project-name>/prd.md`.

Ensure the `Projects/<project-name>/` directory exists (create with `mkdir -p` if needed).

### Step 8: Present Summary

After saving, present a concise summary:
- One-line project description
- Primary target user segment
- MVP scope (3-5 bullet points)
- Key assumptions to validate
- Suggested next step in the pipeline (e.g., "Run `/validate-project` to research
  the market" or "Run `/lean-canvas` to evaluate the business model")

## Quality Standards

- Every section should connect back to the user's problem — if a section doesn't serve
  the user, it doesn't belong in the PRD
- Flag assumptions explicitly rather than stating them as facts
- Use concrete numbers and specifics over vague language ("reduce load time by 50%"
  not "improve performance")
- The MVP section is the most important — be opinionated about what's in and what's out
- Write so a non-technical reader can follow — if a sentence requires domain knowledge
  to parse, rewrite it
- User stories must have verifiable acceptance criteria — "works correctly" is bad,
  "shows confirmation dialog before deleting" is good
- Functional requirements must be testable and unambiguous
- Keep the total PRD between 100-300 lines depending on project stage

## Checklist

Before saving the PRD, verify:

- [ ] Asked clarifying questions if context was ambiguous
- [ ] All 10 sections filled (or consciously skipped based on project stage)
- [ ] Key Results are measurable with targets and timeframes
- [ ] User stories are small, specific, with verifiable acceptance criteria
- [ ] Functional requirements are numbered and testable
- [ ] MVP scope is opinionated — clearly states what's in AND what's out
- [ ] Assumptions are flagged explicitly with risk-if-wrong
- [ ] Open questions capture genuine unknowns
- [ ] Contacts identified (even for solo projects: advisors, domain experts, early users)
- [ ] Saved to `Projects/<project-name>/prd.md`

## Notes

- PRDs are living documents — they evolve as the project progresses through the pipeline
- If a validation brief or lean canvas exists, incorporate their findings rather than
  repeating the research
- The PRD complements but doesn't replace the idea.md — idea.md captures the original
  spark, the PRD formalizes the spec
- User stories in the PRD are initial high-level stories — the `/user-stories` skill
  later decomposes these into detailed buildable stories when the project is activated
