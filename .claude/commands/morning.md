---
description: "Morning standup — sync meetings, review tasks, advance pipeline, check OKRs"
argument-hint: "[quick]"
---

# Morning Standup

Run a 5-minute morning check-in across execution, pipeline, and goals.

## Instructions

If the argument is "quick", skip meeting sync and pipeline — just show top 3 tasks.

### Step 1: Sync Meetings (if Granola available)

Invoke the `/meeting-sync` skill to check for unsynced Granola meetings. If the MCP server is unavailable, skip silently.

### Step 2: Execution Layer

Call `mcp__manager-ai__list_tasks` with `status: "n,s"` to get active tasks. Present the top 3 by priority:

For each task show:
- Priority and estimated time
- Goal/OKR alignment
- Any blockers

If the MCP server is unavailable, read Tasks/*.md directly.

### Step 3: Pipeline Layer

Call `mcp__manager-ai__get_pipeline_status` to see project distribution. Then call `mcp__manager-ai__get_project_artifacts` for the highest-priority project that needs advancement.

Suggest **one project** to advance today (15 min):
- `idea` with no validation → `/validate-project <name>`
- `evaluating` with validation, no lean canvas → `/lean-canvas <name>`
- `evaluating` with lean canvas, no competitive analysis → `/competitive-analysis <name>` (optional)
- `evaluating` with lean canvas, no GTM plan → `/gtm-plan <name>`
- `evaluating` with GTM plan, no pre-mortem → `/pre-mortem <name>`
- `ready` with pre-mortem, no user stories → `/user-stories <name>`
- `active` with no tasks → `/user-stories <name> --tasks`

### Step 4: OKR Check

Read `GOALS.md`. If OKRs exist, briefly note which OKR today's suggested tasks advance. Flag if nothing maps to an OKR.

### Step 5: Suggest Next Action

- No sprint plan this week → "Run `/sprint-plan` to plan your week."
- No OKRs → "Run `/plan-okrs` to make goals measurable."
- Many projects stuck at `idea` → "Run `/prioritize` to rank your project ideas."

### Time-of-Day Awareness

Factor in time when suggesting tasks:
- **Morning (9am-12pm):** Outreach, emails, stakeholder tasks first
- **Afternoon (2pm-5pm):** Deep work — building, writing, analysis
- **End of day (5pm+):** Quick admin, status updates, planning tomorrow
