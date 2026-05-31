---
name: morning
description: |-
  Run a 5-minute morning check-in that syncs meetings, reviews the top 5 tasks and any blocked work, advances one pipeline project, checks OKR alignment, and saves the plan to today's journal. Use this skill whenever the user says "good morning," asks what's on their plate today, wants to plan their day, runs `/morning`, asks for a standup, or mentions starting their work day — even if they don't explicitly ask for a "standup." Push toward this at the start of a work session when no plan has been saved yet for the current date.
argument-hint: "[quick]"
generated_from: .claude/skills/morning/SKILL.md
source_sha256: 0eb9739efed74d51ee758d5fb975943b2780879045035bd8f9e03667e0f6057c
x_generated_note: "do not edit — regenerate with: uv run core/scripts/build_adapters.py"
---

# Morning Standup

Run a 5-minute morning check-in across execution, pipeline, and goals.

If the argument is `quick`, skip meeting sync and pipeline — show only the top 5 tasks.

## Step 0: Review yesterday's journal

Check if a journal entry exists for yesterday at `knowledge/journals/YYYY/MM/DD.md`. If it does:

- Read the Actuals section to see what was completed vs. planned.
- Note any unfinished tasks that should carry forward.
- Mention briefly: "Yesterday you planned X tasks, completed Y. Carrying forward: [unfinished items]."

If no journal exists for yesterday, skip silently.

## Step 0b: Weekly theme

Check the day of the week.

- **Monday:** Ask "What's your focus theme for this week?" Save the answer as a `## Weekly Theme` line in today's journal (Step 7).
- **Tuesday–Friday:** Compute this week's Monday date (formula: today's date minus `(ISO-weekday − 1)` days, where Mon=1, Tue=2, … Fri=5). Read the journal at `knowledge/journals/YYYY/MM/DD.md` for that date and pull the `## Weekly Theme` line. Display it at the top of the standup: "This week's theme: [theme]." Carry it into today's journal.

If no Monday journal exists (e.g., holiday), check the most recent weekday journal for a theme. If none found, skip silently.

## Step 1: Sync meetings (if Granola available)

Invoke the `/meeting-sync` skill to check for unsynced Granola meetings. If the Granola MCP server is unavailable, skip silently.

## Step 2: Execution layer

Call the `list_tasks` tool (manager-ai MCP server) with `status: "n,s"` to get active tasks. Present the top 5 by priority, showing for each:

- Priority and estimated time
- Goal/OKR alignment
- Any blockers

If the MCP server is unavailable, read `tasks/*.md` directly.

## Step 2b: Waiting on (dependency table)

Call the `list_tasks` tool (manager-ai MCP server) with `status: "b"` to get all blocked tasks.

For each, read the task file and extract:

- Task title
- `blocked_by` from frontmatter (if present) — who/what is blocking
- `blocked_since` from frontmatter (if present) — when it was blocked
- If frontmatter fields are missing, scan the Progress Log for the most recent blocker note

Present as a table:

```markdown
## Waiting On
| Task | Blocked by | Since | Next action |
|------|-----------|-------|-------------|
| Task name | Person/thing | YYYY-MM-DD | Suggested escalation |
```

Suggest a "Next action" based on age:

- < 3 days: "Check in"
- 3–7 days: "Follow up directly"
- \> 7 days: "Escalate or unblock yourself"

If no tasks are blocked, skip this section.

## Step 3: Pipeline layer

Call the `get_pipeline_status` tool (manager-ai MCP server) to see project distribution. Then call the `get_project_artifacts` tool (manager-ai MCP server) for the highest-priority project that needs advancement.

Suggest **one project** to advance today (15 min):

- `idea` with no validation → `/validate-project <name>`
- `evaluating` with validation, no lean canvas → `/lean-canvas <name>`
- `evaluating` with lean canvas, no GTM plan → `/gtm-plan <name>`
- `evaluating` with GTM plan, no competitive analysis → `/competitive-analysis <name>` (optional)
- `evaluating` with GTM plan, no pre-mortem → `/pre-mortem <name>`
- `ready` with pre-mortem, no user stories → `/user-stories <name>`
- `active` with no tasks → `/user-stories <name> --tasks`

## Step 4: OKR check

Read `GOALS.md`. If OKRs exist, note which OKR today's suggested tasks advance. Flag if nothing maps to an OKR.

## Step 5: Suggest next action

- No sprint plan this week → "Run `/sprint-plan` to plan your week."
- No OKRs → "Run `/plan-okrs` to make goals measurable."
- Many projects stuck at `idea` → "Run `/prioritize` to rank your project ideas."

## Step 6: Post to Slack (optional)

Ask: "Post this standup summary to #os-progress?"

If yes, format a concise message and post using the `slack_send_message` tool (Slack MCP server) to `#os-progress`:

- Date
- Top 3 focus tasks (one line each, with priority)
- Pipeline project being advanced today
- Blockers (if any)

If Slack MCP is unavailable, skip silently.

## Step 7: Save daily journal

Save today's standup output as a journal entry at `knowledge/journals/YYYY/MM/DD.md`. Create the directory structure if it doesn't exist.

Use this exact template:

```markdown
---
date: YYYY-MM-DD
planned_tasks: [count]
completed_tasks: 0
---
# YYYY-MM-DD

## Weekly Theme
[theme from Step 0b, if set]

## Plan
1. [Priority] task-name — goal alignment
2. [Priority] task-name — goal alignment
3. [Priority] task-name — goal alignment
4. [Priority] task-name — goal alignment
5. [Priority] task-name — goal alignment

Pipeline: [suggested pipeline project and skill]

## Actuals
- Completed:
- Blocked:
- Unplanned work:

## Notes

## Session Reflections
```

Fill the Plan section with the 5 focus tasks from Step 2 and the pipeline project from Step 3. Leave Actuals, Notes, and Session Reflections empty — these get filled throughout the day or during the next morning's Step 0.

## Time-of-day awareness

Factor in the current time when suggesting tasks:

- **Morning (9am–12pm):** Outreach, emails, stakeholder tasks first
- **Afternoon (2pm–5pm):** Deep work — building, writing, analysis
- **End of day (5pm+):** Quick admin, status updates, planning tomorrow
