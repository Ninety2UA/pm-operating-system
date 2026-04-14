---
name: sprint-plan
description: >
  Creates a weekly sprint plan at 70% capacity from current tasks and user
  stories — selects stories, identifies dependencies and risks, produces a
  day-by-day schedule saved to knowledge/sprint-WXX.md. Use this skill
  whenever the user says "plan my sprint", "what should I build this week",
  "weekly plan", "sprint planning", mentions feeling behind, has tasks
  piling up without a plan, or at the start of the week — even if they just
  say "what should I work on."
allowed-tools: Read Write Edit Glob
argument-hint: "[hours-available] [--project <name>]"
---

# Sprint Plan

Create a focused weekly sprint plan from current tasks and user stories, using capacity-based planning at 70%.

## Quick Start

User: `/sprint-plan`
Result: Reads all tasks/ and active project user stories, estimates capacity, selects sprint stories, saves plan.

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
- Use Glob for `tasks/*.md` and read all task files
- Filter to status `n` (not started) and `s` (started)
- Note any `b` (blocked) tasks and their blockers

**User Stories (if --project specified):**
- Read `projects/<project-name>/user-stories.md`
- Pull P0 and P1 stories not yet completed

**User Stories (if no --project):**
- Use Glob for `projects/*/user-stories.md`
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

Read the template at `${CLAUDE_PLUGIN_ROOT}/skills/sprint-plan/references/sprint-plan-template.md` and fill each section from the tasks, stories, capacity, and selected sprint items gathered in Steps 2-4.

### Step 6: Save the Sprint Plan

Save to `knowledge/sprint-YYYY-MM-DD.md` (using the Monday date of the sprint week).

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
- **Re-planning:** It's fine to re-run mid-week if priorities shifted. The old plan stays in knowledge/ as a record.
- **Complement to morning standup:** Sprint plan sets the week; morning standup sets the day within that plan.
