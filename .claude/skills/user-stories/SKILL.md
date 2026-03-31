---
name: user-stories
description: >
  Generates structured user stories with acceptance criteria from a project's PRD.
  Breaks down a product spec into buildable, testable stories using the
  "As a [role], I want [action], so that [benefit]" format with INVEST criteria.
  Use when activating a project, "create user stories", "break this into stories",
  "decompose this PRD", "what should I build first", or when moving a project
  from evaluating to active.
allowed-tools: Read Write Edit Glob
argument-hint: "<project-name> [--tasks]"
---

# User Stories

Generate structured user stories with acceptance criteria from a project's PRD, ready for sprint planning or task decomposition.

## Quick Start

User: `/user-stories ad-spend-anomaly-detector`
Result: Reads the PRD, generates prioritized user stories with acceptance criteria, saves to `Projects/ad-spend-anomaly-detector/user-stories.md`.

User: `/user-stories ad-spend-anomaly-detector --tasks`
Result: Same as above, plus creates individual task files in `Tasks/` for each P0/P1 story.

## Instructions

### Step 1: Parse Arguments

Check `$ARGUMENTS` for:
- A required `<project-name>`
- An optional `--tasks` flag (if present, also create task files from stories)

If no project name is provided, ask the user which project to decompose.

### Step 2: Validate Project Name

**Security check:** Reject any project name containing `..`, `/`, or non-alphanumeric characters besides hyphens.

Check if `Projects/<project-name>/` exists. If not, list available projects.

### Step 3: Read Project Context

Read in order:
1. `Projects/<project-name>/prd.md` (required — this is the primary input)
2. `Projects/<project-name>/idea.md` (for context and goals alignment)
3. `Projects/<project-name>/lean-canvas.md` (if exists — for customer segment context)

If no prd.md exists, stop and tell the user: "No PRD found. Run `/PRD <project-name>` first to generate a product spec."

### Step 4: Check for Existing Stories

Check if `Projects/<project-name>/user-stories.md` already exists.

If it does, ask the user: Overwrite or Skip.

### Step 5: Generate User Stories

From the PRD, extract every functional requirement, user flow, and feature. Convert each into a user story following this format:

For each story, assign:
- **Priority:** P0 (MVP-critical), P1 (important for v1), P2 (nice-to-have), P3 (future)
- **Size:** S (< 2 hrs), M (2-4 hrs), L (4-8 hrs), XL (> 8 hrs, should be split)
- **Acceptance criteria:** 2-5 testable conditions using Given/When/Then or checklist format

Group stories by epic (major feature area from the PRD).

### Step 6: Write the Stories Document

```markdown
---
title: "User Stories — [Project Title]"
project: <project-name>
created_date: YYYY-MM-DD
total_stories: [N]
mvp_stories: [count of P0]
estimated_mvp_hours: [sum of P0 story sizes]
---

# User Stories — [Project Title]

## Summary

| Priority | Count | Estimated Hours |
|----------|-------|----------------|
| P0 (MVP) | [N] | [hours] |
| P1 (v1) | [N] | [hours] |
| P2 (nice-to-have) | [N] | [hours] |
| P3 (future) | [N] | [hours] |
| **Total** | **[N]** | **[hours]** |

## MVP Scope (P0 Stories)

Stories required for a minimum viable product. Build these first.

---

### Epic: [Feature Area 1]

#### Story 1.1: [Story title]
**As a** [user role],
**I want** [action/capability],
**so that** [benefit/outcome].

**Priority:** P0 | **Size:** M (3 hrs)

**Acceptance Criteria:**
- [ ] Given [context], when [action], then [expected result]
- [ ] Given [context], when [action], then [expected result]
- [ ] [Edge case or error handling requirement]

**Notes:** [Implementation hints, dependencies, or design considerations]

---

#### Story 1.2: [Story title]
...

---

### Epic: [Feature Area 2]
...

---

## v1 Scope (P1 Stories)

Stories that complete the full v1 experience but aren't required for MVP.

[Same format as above]

---

## Future Scope (P2-P3 Stories)

Stories for future iterations. Do not build these in v1.

[Same format as above]

---

## Story Map

Visual overview of the user journey and story coverage:

```
[User Journey Stage 1] → [Stage 2] → [Stage 3] → [Stage 4]
     │                      │            │            │
     ├─ Story 1.1 (P0)     ├─ 2.1 (P0)  ├─ 3.1 (P0)  ├─ 4.1 (P1)
     ├─ Story 1.2 (P0)     ├─ 2.2 (P1)  ├─ 3.2 (P1)  └─ 4.2 (P2)
     └─ Story 1.3 (P2)     └─ 2.3 (P2)  └─ 3.3 (P3)
```

---

**Suggested next step:** Run `/sprint-plan` to plan your first sprint from these stories, or `/pre-mortem <project-name>` to identify risks before building.
```

### Step 7: Save the Stories

Save to `Projects/<project-name>/user-stories.md`.

### Step 8: Create Task Files (if --tasks flag)

If `--tasks` was passed, create individual task files in `Tasks/` for each P0 and P1 story:

```yaml
---
title: "[Story title]"
category: technical
priority: [P0|P1]
status: n
created_date: YYYY-MM-DD
estimated_time: [minutes based on size]
resource_refs:
  - Projects/<project-name>/user-stories.md
  - Projects/<project-name>/prd.md
---

# [Story title]

## Context
Part of [Project Title] — [Epic name].
[Goal alignment from idea.md]

## User Story
As a [role], I want [action], so that [benefit].

## Acceptance Criteria
- [ ] [criterion 1]
- [ ] [criterion 2]
- [ ] [criterion 3]

## Progress Log
- YYYY-MM-DD: Created from user stories decomposition.
```

### Step 9: Update Project Resource Refs

Add `Projects/<project-name>/user-stories.md` to the idea.md `resource_refs` array.

### Step 10: Present Summary

Present:
- Total story count by priority
- MVP scope: number of P0 stories and estimated hours
- Story map overview
- If `--tasks`: list of created task files
- Suggested next step

## Notes

- **No external calls:** This skill works entirely from local project files. No Perplexity needed.
- **XL stories:** Any story sized XL (> 8 hrs) should be flagged for splitting. Suggest how to break it down.
- **INVEST criteria:** Each story should be Independent, Negotiable, Valuable, Estimable, Small, Testable. Flag stories that violate these.
- **MVP discipline:** P0 should be the absolute minimum to validate the core value proposition. Be ruthless about scope.
