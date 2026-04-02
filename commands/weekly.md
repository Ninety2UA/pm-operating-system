---
description: "Weekly review — reflect on execution, pipeline movement, OKR progress, and plan next week"
argument-hint: "[quick]"
---

# Weekly Review

A 20-minute session reviewing execution, pipeline, and OKRs.

## Instructions

If the argument is "quick", condense to: what finished, what's blocked, top 3 next week.

### Step 1: Execution Review

Call `mcp__manager-ai__get_task_summary` for aggregate stats.

List tasks completed this week (status `d`). Group by goal/OKR alignment:
- How many tasks per goal
- Time invested vs estimated
- Sprint completion rate (if sprint plan exists in Knowledge/sprint-*.md)

### Step 2: Pipeline Review

Call `mcp__manager-ai__get_pipeline_status` and `mcp__manager-ai__get_project_summary`.

Report:
- How many projects moved stages this week
- Projects validated, lean canvases completed, GTM plans created
- Projects killed (positive metric — decisive focus)
- Pipeline bottlenecks (e.g., 85 ideas, 0 evaluating)

### Step 3: OKR Progress

Read `GOALS.md`. If OKRs exist, update the "Current" column:
- Show each KR with baseline → target → current → score
- Overall OKR score (target: 0.7 by end of quarter)
- Flag KRs that are falling behind

If no OKRs exist: "Run `/plan-okrs` to make your quarterly goals measurable."

### Step 4: Blockers & Stalled Work

Call `mcp__manager-ai__list_tasks` with `status: "b"` for blocked tasks.

Also flag:
- Projects that haven't moved pipeline stages in > 2 weeks
- Active projects with no task activity this week
- Started tasks (`s`) with no progress log updates

### Step 5: Plan Next Week

Suggest top priorities based on OKR gaps and pipeline state. Offer:
- "Run `/sprint-plan [hours]` for a full capacity-based plan."
- Specific pipeline targets: evaluate N ideas, complete N lean canvases

### Step 6: Update OKRs

Offer to update the "Current" column in GOALS.md OKR tables with this week's actuals.

### Step 7: Post to Slack (Optional)

After the review, ask: "Post weekly review to #os-progress?"

If yes, format a summary and post using `mcp__slack__slack_post_message` to #os-progress:
- Tasks completed this week (count, grouped by goal)
- Pipeline movement (projects advanced, projects killed)
- OKR scores (if they exist)
- Top 3 priorities for next week

Use Slack message formatting (bold, bullet points). If Slack MCP is unavailable, skip silently.
