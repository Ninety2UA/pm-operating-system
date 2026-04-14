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
