---
name: decision
description: >
  Documents a decision with structured context, options considered, pros/cons,
  reversibility assessment, and rationale — saved to knowledge/decisions/ for
  future reference. Use this skill whenever the user says "I need to decide",
  "log this decision", "decision record", "ADR", "let's pick between X and Y",
  mentions a tough call, weighs options, frames a strategic/architectural
  choice they'll want to revisit, or is about to commit to a path that's
  non-trivial to reverse — even if they don't explicitly ask to "log" it.
allowed-tools: Read Write Edit Glob
argument-hint: "<topic>"
---

# Decision Log

Create a structured decision record for future reference.

## Instructions

### Step 1: Gather Context

Ask the user (if not already clear from conversation):
1. **What decision needs to be made?** (the core question)
2. **What's driving this?** (deadline, blocker, opportunity, dependency)
3. **What options are you considering?** (at least 2)

If the decision relates to a project, read the project's idea.md and any relevant artifacts for context.

### Step 2: Structure the Decision

For each option, assess:
- **Pros** — what you gain
- **Cons** — what you lose or risk
- **Effort** — how much work is involved
- **Reversibility** — can you undo this if it's wrong?

### Step 3: Write the Decision Record

Create the directory if needed: `knowledge/decisions/`

Save to: `knowledge/decisions/YYYY-MM-DD-topic-slug.md`

Use this format:

```markdown
---
date: YYYY-MM-DD
topic: [Decision topic]
status: decided  # decided | deferred | revisit
decision: [Which option was chosen]
project: [project-name, if applicable]
revisit_date: [YYYY-MM-DD, if applicable]
---
# Decision: [Topic]

## Context
[Why this decision needs to be made now. What's driving it.]

## Options Considered

### Option A: [Name]
- **Pros:** [list]
- **Cons:** [list]
- **Effort:** [low/medium/high]
- **Reversibility:** [easy/hard/irreversible]

### Option B: [Name]
- **Pros:** [list]
- **Cons:** [list]
- **Effort:** [low/medium/high]
- **Reversibility:** [easy/hard/irreversible]

## Decision
**Chosen:** [Option X]

**Rationale:** [Why this option was selected over others]

## Follow-up Actions
- [ ] [Action items that result from this decision]

## Review
[Leave empty — fill in when revisiting this decision later]
```

### Step 4: Link to Project

If the decision relates to a project:
- Add a `resource_refs` entry in the project's idea.md pointing to the decision file
- Add a Progress Log entry noting the decision was made

### Step 5: Confirm

Tell the user where the decision was saved and any follow-up actions identified.

## Notes

- Keep decisions concise. The goal is to capture the "why" so future-you understands the reasoning.
- For deferred decisions, set a `revisit_date` and status `deferred`.
- `/weekly` and `/quarterly` scan `knowledge/decisions/` for recent decisions and surface repeat patterns.
- If you notice the user making the same type of decision repeatedly, suggest codifying it as a rule in AGENTS.md.
