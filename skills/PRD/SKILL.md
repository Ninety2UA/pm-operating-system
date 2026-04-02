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
  this skill applies.
allowed-tools: Read Write Edit Glob Bash mcp__perplexity__*
disable-model-invocation: true
argument-hint: "<project-name>"
---

# Generate a Product Requirements Document

Create a comprehensive PRD that serves as the authoritative spec for a project — aligning
stakeholder thinking and guiding what gets built. The PRD balances thoroughness with
practicality for a solo builder or small team.

## Instructions

### Step 1: Gather Context

1. Read `Projects/<project-name>/idea.md` for the project context and scope.
2. Read `GOALS.md` to understand how this project connects to broader goals and OKRs.
3. Check if `Knowledge/research/projects/<project-name>.md` exists — if so, read the
   validation brief for market context.
4. Check if `Projects/<project-name>/lean-canvas.md` exists — if so, use the business
   model insights.

If no idea.md exists, ask the user to describe the project before proceeding.

### Step 2: Research (if needed)

If the gathered context lacks market data or competitor insight, run a focused research
query using `perplexity_search` or `perplexity_ask`:
- Who are the target users and what problem are they experiencing?
- What existing solutions or competitors serve this space?
- What's the opportunity signal — are people searching for this, paying for alternatives?

Keep research lightweight — the PRD captures what to build, not a full market analysis
(that's what `/validate-project` is for).

### Step 3: Think Before Writing

Before drafting, work through these questions:
- What problem are we solving, and for whom?
- Why now — has something changed that makes this timely?
- How will we know it succeeded? What's the measurable outcome?
- What's the smallest version that delivers value?
- What assumptions are we making that could be wrong?

### Step 4: Write the PRD

Use the 8-section structure below. Be specific and data-driven where possible. Write for
clarity — short sentences, no jargon, accessible to anyone who reads it.

```markdown
---
title: "PRD: [Project Name]"
project: <project-name>
date: YYYY-MM-DD
status: draft
author: [User name from GOALS.md or git config]
---

# [Project Name] — Product Requirements Document

## 1. Summary

2-3 sentences: What is this product/feature? What does it do? Who is it for?

## 2. Background

- **Context:** What is this initiative about? What led to it?
- **Why now:** Has something changed — new technology, market shift, user pain?
- **Connection to goals:** Which goal or OKR from GOALS.md does this advance?

## 3. Objective

What's the objective and why does it matter?

**Key Results** (SMART format):
- KR1: [Measurable outcome with target and timeframe]
- KR2: [Measurable outcome with target and timeframe]
- KR3: [Measurable outcome with target and timeframe]

## 4. Target Users

Who are we building this for? Define by problem/job, not demographics.

| Segment | Problem/Job | Current Workaround | Pain Level |
|---------|------------|-------------------|------------|
| [Segment 1] | [What they need] | [How they cope today] | [High/Med/Low] |
| [Segment 2] | [What they need] | [How they cope today] | [High/Med/Low] |

**Primary segment:** [Which segment to focus on first and why]

## 5. Value Proposition

- What customer jobs/needs does this address?
- What will users gain that they don't have today?
- Which pains will they avoid?
- How is this better than existing alternatives?

## 6. Solution

### 6.1 Key Features

| Feature | Description | Priority | Effort |
|---------|------------|----------|--------|
| [Feature 1] | [What it does] | Must-have | [S/M/L] |
| [Feature 2] | [What it does] | Must-have | [S/M/L] |
| [Feature 3] | [What it does] | Nice-to-have | [S/M/L] |

### 6.2 User Flow

Describe the primary user journey from entry to value:
1. User arrives at [entry point]
2. User does [action]
3. System responds with [result]
4. User achieves [outcome]

### 6.3 Technical Considerations

Only if relevant — stack choices, API dependencies, data requirements,
infrastructure needs. Skip if not applicable for this project.

### 6.4 Assumptions

What we believe but haven't proven. Flag these clearly so they can be
validated before or during building.

- [Assumption 1] — risk if wrong: [impact]
- [Assumption 2] — risk if wrong: [impact]

## 7. Scope & Phases

### MVP (Phase 1)
What goes in the first shippable version? Be ruthless — the MVP should
deliver the core value proposition with minimum features.

- [Feature/capability included]
- [Feature/capability included]
- **Explicitly excluded:** [Things that feel important but aren't MVP]

### Phase 2+
What comes after the MVP proves the concept?

- [Enhancement 1]
- [Enhancement 2]

### Non-Goals
Things this project intentionally does NOT do:
- [Non-goal 1]
- [Non-goal 2]

## 8. Success Criteria

How will we know this worked? Link back to the Key Results in Section 3.

| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| [Metric 1] | [Current state] | [Goal] | [How to measure] |
| [Metric 2] | [Current state] | [Goal] | [How to measure] |
```

### Step 5: Adapt Depth to Project Stage

Not every project needs the same level of detail:

- **Idea stage** — Focus on sections 1-5 (problem, users, value). Keep solution high-level.
  Features can be bullet points, not detailed specs.
- **Evaluating stage** — Full PRD with all 8 sections. Solution section should be specific
  enough that someone could start building.
- **Active stage** — PRD should be complete and actionable. Features need acceptance
  criteria. User flows need detail.

Match the depth to where the project is in the pipeline. A 200-line PRD for an idea-stage
project is over-engineering. A 50-line PRD for an active project is under-specifying.

### Step 6: Save the PRD

Save to `Projects/<project-name>/prd.md`.

Ensure the `Projects/<project-name>/` directory exists (create with `mkdir -p` if needed).

### Step 7: Present Summary

After saving, present a concise summary:
- One-line project description
- Primary target user segment
- MVP scope (3-5 bullet points)
- Key assumptions to validate
- Suggested next step in the pipeline (e.g., "Run `/validate-project` to research the market"
  or "Run `/lean-canvas` to evaluate the business model")

## Quality Standards

- Every section should connect back to the user's problem — if a section doesn't serve
  the user, it doesn't belong in the PRD
- Flag assumptions explicitly rather than stating them as facts
- Use concrete numbers and specifics over vague language ("reduce load time by 50%"
  not "improve performance")
- The MVP section is the most important — be opinionated about what's in and what's out
- Keep the total PRD between 100-300 lines depending on project stage

## Notes

- PRDs are living documents — they evolve as the project progresses through the pipeline
- If a validation brief or lean canvas exists, incorporate their findings rather than
  repeating the research
- The PRD complements but doesn't replace the idea.md — idea.md captures the original
  spark, the PRD formalizes the spec
