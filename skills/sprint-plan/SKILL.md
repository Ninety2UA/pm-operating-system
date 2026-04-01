---
name: sprint-plan
description: >
  Creates a weekly sprint plan from current tasks and user stories.
  Plans at 70% capacity, selects stories, identifies dependencies and risks.
  Use when planning the week, "plan my sprint", "what should I build this week",
  "weekly plan", "sprint planning", or at the start of each week to structure
  execution.
allowed-tools: Read Write Edit Glob
argument-hint: "[hours-available] [--project <name>]"
---

# Sprint Plan

Create a focused weekly sprint plan from current tasks and user stories, using capacity-based planning at 70%.

## Quick Start

User: `/sprint-plan`
Result: Reads all Tasks/ and active project user stories, estimates capacity, selects sprint stories, saves plan.

User: `/sprint-plan 20 --project ad-spend-anomaly-detector`
Result: Plans a sprint with 20 available hours, focused on a specific project's user stories.

## Instructions

### Step 1: Parse Arguments

Check `$ARGUMENTS` for:
- An optional hours number (e.g., `20`) — total available deep work hours this week
- An optional `--project <name>` flag to focus sprint on a specific project's stories

If no hours provided, default to 15 hours (a realistic week for someone with a day job and meetings).

### Step 2: Gather Current State

Read the following in parallel:

**Tasks:**
- Use Glob for `Tasks/*.md` and read all task files
- Filter to status `n` (not started) and `s` (started)
- Note any `b` (blocked) tasks and their blockers

**User Stories (if --project specified):**
- Read `Projects/<project-name>/user-stories.md`
- Pull P0 and P1 stories not yet completed

**User Stories (if no --project):**
- Use Glob for `Projects/*/user-stories.md`
- Read any that exist and pull uncompleted P0/P1 stories

**Goals:**
- Read `GOALS.md` for current priorities and quarterly objectives

### Step 3: Calculate Capacity

```
Total available hours: [from args or default 15]
Planning capacity (70%): [total × 0.7]
Buffer (30%): [total × 0.3] — for interruptions, meetings, unplanned work
```

Why 70%: Planning at 100% capacity guarantees failure. The 30% buffer absorbs reality.

### Step 4: Select Sprint Items

Prioritize items in this order:
1. **Blocked items** that can be unblocked — highest ROI (unblocks future work)
2. **In-progress tasks** (status `s`) — finish what you started
3. **P0 tasks and stories** — critical path items
4. **P1 tasks and stories** — important items that fit remaining capacity
5. **Quick wins** (< 30 min items) — momentum builders

Fill the sprint backlog up to 70% capacity. Do NOT overfill.

If there are more P0 items than capacity allows, flag this as a planning problem and ask the user to cut scope or extend the timeline.

### Step 5: Write the Sprint Plan

```markdown
---
title: "Sprint — Week of YYYY-MM-DD"
created_date: YYYY-MM-DD
capacity_hours: [total]
planned_hours: [70% allocation]
buffer_hours: [30% buffer]
sprint_goal: "[One sentence: what will be true at the end of this week?]"
---

# Sprint — Week of YYYY-MM-DD

## Sprint Goal
> [One sentence describing the most important outcome for this week]

## Capacity

| | Hours |
|---|------|
| Total available | [N] |
| Planned (70%) | [N × 0.7] |
| Buffer (30%) | [N × 0.3] |

## Sprint Backlog

### Must Complete (P0)

| # | Item | Source | Est. | Status |
|---|------|--------|------|--------|
| 1 | [Task/story title] | [Tasks/ or Project] | [hrs] | [n/s] |
| 2 | [Task/story title] | [Tasks/ or Project] | [hrs] | [n/s] |

### Should Complete (P1)

| # | Item | Source | Est. | Status |
|---|------|--------|------|--------|
| 3 | [Task/story title] | [Tasks/ or Project] | [hrs] | [n/s] |
| 4 | [Task/story title] | [Tasks/ or Project] | [hrs] | [n/s] |

### Stretch Goals (if buffer unused)

| # | Item | Source | Est. |
|---|------|--------|------|
| 5 | [Task/story title] | [Tasks/ or Project] | [hrs] |

**Total planned: [X] hrs / [Y] hrs capacity**

## Daily Breakdown (Suggested)

| Day | Focus | Items | Hours |
|-----|-------|-------|-------|
| Mon | [Theme] | #1, #3 | [N] |
| Tue | [Theme] | #1 (cont), #4 | [N] |
| Wed | [Theme] | #2 | [N] |
| Thu | [Theme] | #2 (cont), #5 | [N] |
| Fri | [Wrap-up] | Review, buffer | [N] |

## Dependencies & Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| [Blocked item X needs Y] | Could lose [N] hrs | [Follow up with Z on Monday] |
| [Story may be larger than estimated] | Overrun by [N] hrs | [Timebox to [N] hrs, cut scope if needed] |

## Blocked Items (Not in Sprint)

| Item | Blocker | Action Needed |
|------|---------|---------------|
| [Task title] | [What's blocking it] | [Who to contact / what to do] |

---

## Pipeline Check

Projects that need attention this week (from Projects/ with status `evaluating` or `active`):

| Project | Status | Next Skill to Run |
|---------|--------|-------------------|
| [name] | evaluating | `/lean-canvas` |
| [name] | active, no stories | `/user-stories` |

---

**End of sprint:** Run `/sprint-review` or update task statuses and review what shipped vs. planned.
```

### Step 6: Save the Sprint Plan

Save to `Tasks/sprint-YYYY-MM-DD.md` (using the Monday date of the sprint week).

### Step 7: Present Summary

Present:
- Sprint goal (one sentence)
- Number of items selected and total planned hours vs. capacity
- Today's suggested focus (first 1-2 items)
- Any blocked items that need immediate attention
- Pipeline projects that need skill runs this week

## Notes

- **No external calls:** Works entirely from local files.
- **Overcommitment guard:** If the user tries to plan at 100% capacity, push back. "Planning at 100% guarantees you'll miss targets. Let's plan at 70% and use the buffer for reality."
- **Re-planning:** It's fine to re-run mid-week if priorities shifted. The old plan stays in Tasks/ as a record.
- **Complement to morning standup:** Sprint plan sets the week; morning standup sets the day within that plan.
