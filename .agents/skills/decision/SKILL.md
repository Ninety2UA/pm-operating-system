---
name: decision
description: |-
  Documents a decision with structured context, options considered, pros/cons, reversibility assessment, and rationale — saved to knowledge/decisions/ for future reference. Use this skill whenever the user says "I need to decide", "log this decision", "decision record", "ADR", "let's pick between X and Y", mentions a tough call, weighs options, frames a strategic/architectural choice they'll want to revisit, is about to commit to a path that's non-trivial to reverse, or wants to change an earlier recorded decision (a new record that amends the old one) — even if they don't explicitly ask to "log" it.
argument-hint: "<topic>"
generated_from: .claude/skills/decision/SKILL.md
source_sha256: b95f9a194167459a67f77ad92e30aa6169681d27e5a4f52ee5c01ab79bfd2387
x_generated_note: "do not edit — regenerate with: uv run core/scripts/build_adapters.py"
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

The reversibility rating is `easy`, `hard`, or `irreversible`, and anything above `easy` states a rationale that names the migration, the published contract, or the dependent system that makes the undo expensive. (RW-2026-09-12-15) "Hard to change" names nothing and does not count. Rate the decision, not the difficulty of the work, and rate `easy` when unsure — a log where every option reads irreversible warns about nothing.

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
amends: [knowledge/decisions/YYYY-MM-DD-topic-slug.md — optional, only when this record changes an earlier decision]
amended_by: [knowledge/decisions/YYYY-MM-DD-topic-slug.md — optional, set on the older record when a later one amends it]
---
# Decision: [Topic]

[Two or three sentences a reader who was not in the room can act on: what was decided, why, and what changes because of it. Write this before the sections below and keep it free of shorthand — it is the whole record for anyone skimming.]

## Context
[Why this decision needs to be made now. What's driving it. Gloss every identifier at its first mention — `Option B (hosted queue)`, `ADR-3 (SQLite over Postgres)`, the ledger row and its subject — and leave later mentions bare.]

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
**Chosen:** Option X ([name])

**Rationale:** [Why this option was selected over others, citing this decision's own constraints. Where the chosen option is not `easy` to reverse, the rationale names the migration, contract, or dependent system behind that rating. Gloss each identifier at its first mention here too.]

## Follow-up Actions
- [ ] [Action items that result from this decision]

## Review
[Leave empty — fill in when revisiting this decision later]
```

**Amending an earlier decision.** When the new decision changes, narrows, or reverses a record that is already `decided`, do not edit the old record's body: write the new record with `amends:` pointing at the old file, and in the same session add the reciprocal `amended_by:` line to the old record's frontmatter (a one-line frontmatter append; its options and rationale stay as written). Both sides land before Step 5 confirms — a one-way pointer is the failure the pair exists to prevent. The newest record in an amends chain is the one in force; the old record's `## Review` section is for revisit notes that do not change the decision. (RW-2026-09-11-23)

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

## Rationalization guard

A decision record carries at least two options, each with pros, cons, effort, and reversibility, plus a rationale that cites this decision's own constraints — no exceptions. Common rationalizations, pre-answered:

- *"There's really only one option — I'll skip the alternatives."* A record with one option is a note, not a decision; the rejected paths are what future-you needs when the context shifts. Name at least two, even if one is "do nothing".
- *"The user already decided — I'll just log the outcome."* The outcome without the options and the "why" is exactly the record this skill exists to prevent. Ask the three Step 1 questions anyway; it takes a minute.
- *"It's easily reversible, so it doesn't need a record."* Reversibility is an assessment to write down, not a reason to skip. Cheap-to-undo decisions are the ones that repeat, and the record is what lets `/weekly` surface the pattern.
- *"Let me see what the research says first, then form a view."* Position discipline runs the other way: freeze your own recommendation before consulting any external opinion.
- *"The record speaks for itself — the options are right there."* A reader arriving cold sees the options, not the call. Open the body with the summary paragraph: what was decided, why, what it changes. (RW-2026-09-12-19)
- *"The old decision changed — I'll update that record in place."* Rewriting a decided record erases what was believed at the time. Write a new record that amends it and add the reciprocal line to the old one. Red flag: a Write to `knowledge/decisions/` with fewer than two options, or a rationale that cites no constraint from this decision's own context. (RW-2026-09-11-16)

## Position discipline

Freeze your own recommendation — written, with reasoning — before consulting any external opinion (research, another model, a reviewer), so consensus cannot shape the first draft. And never issue a verdict you did not earn against this decision's own context: every option's pros/cons must cite the user's actual constraints, not generic tradeoffs. (CE-13)
