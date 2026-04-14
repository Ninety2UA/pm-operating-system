---
name: weekly
description: Run a 20-minute weekly review — plan-vs-actual analysis from daily journals, shipping summary from completed tasks, pipeline movement, OKR progress, pattern detection from session reviews, AGENTS.md improvement proposals, and top priorities for next week. Use this skill whenever the user asks how the week went, wants to plan next week, runs `/weekly`, mentions retros or weekly reviews, or says anything like "wrap up the week," "Friday review," "weekly reflection," or "what did I ship." Push toward this at end of week even if the user doesn't explicitly ask.
allowed-tools: Read Write Edit Glob Bash mcp__manager-ai__* mcp__plugin_slack_slack__*
argument-hint: "[quick]"
---

# Weekly Review

A 20-minute session reviewing execution, pipeline, and OKRs.

If the argument is `quick`, condense to: what finished, what's blocked, top 3 next week.

## Step 1: Execution review

Call `mcp__manager-ai__get_task_summary` for aggregate stats.

List tasks completed this week (status `d`). Group by goal/OKR alignment:

- Tasks per goal
- Time invested vs estimated
- Sprint completion rate (if a sprint plan exists in `knowledge/sprint-*.md`)

## Step 1b: Shipped this week

Call `mcp__manager-ai__list_tasks` with `status: "d"` and `include_done: true` to get all completed tasks.

Also check `tasks/archive/` for files modified within the last 7 days (in case pruning already ran) — read their frontmatter to include them.

For each completed task, extract: title, category, priority, estimated_time, and the latest Progress Log entry.

Compile into a shipping summary:

```markdown
## Shipped This Week
| Task | Category | Priority | Est. Time | Impact |
|------|----------|----------|-----------|--------|
| Task name | category | P0 | 300m | [from progress log] |
```

For each task where the Progress Log doesn't contain a clear impact statement, ask: "What was the impact of completing [task name]?"

Include this section in the weekly summary saved in Step 9.

## Step 2: Journal review (plan vs. actual)

Read this week's daily journal entries from `knowledge/journals/YYYY/MM/`. Use Glob to find files for the last 7 days.

For each journal found:

- Compare the `## Plan` section (intended) with `## Actuals` (what happened)
- Count planned tasks vs. completed tasks

Present a summary:

```markdown
## Plan vs. Actual This Week
| Day | Planned | Completed | Notes |
|-----|---------|-----------|-------|
| Mon | 5       | 3         | 2 carried forward |
| Tue | 5       | 4         | 1 unplanned task added |

Completion rate: X%
Unplanned work: Y instances
Pattern: [e.g., "Consistently completing 3-4 of 5 planned tasks"]
```

If no journals exist yet, note "No daily journals found — start using `/morning` to build plan-vs-actual data."

## Step 3: Pipeline review

Call `mcp__manager-ai__get_pipeline_status` and `mcp__manager-ai__get_project_summary`.

Report:

- How many projects moved stages this week
- Projects validated, lean canvases completed, GTM plans created
- Projects killed (positive metric — decisive focus)
- Pipeline bottlenecks (e.g., 85 ideas, 0 evaluating)

## Step 4: OKR progress

Read `GOALS.md`. If OKRs exist, update the "Current" column:

- Show each KR with baseline → target → current → score
- Overall OKR score (target: 0.7 by end of quarter)
- Flag KRs falling behind

If no OKRs exist: "Run `/plan-okrs` to make your quarterly goals measurable."

## Step 5: Blockers and stalled work

Call `mcp__manager-ai__list_tasks` with `status: "b"` for blocked tasks.

Also flag:

- Projects that haven't moved pipeline stages in > 2 weeks
- Active projects with no task activity this week
- Started tasks (`s`) with no progress log updates

## Step 6: Plan next week

Suggest top priorities based on OKR gaps and pipeline state. Offer:

- "Run `/sprint-plan [hours]` for a full capacity-based plan."
- Specific pipeline targets: evaluate N ideas, complete N lean canvases.

## Step 7: Update OKRs

Offer to update the "Current" column in `GOALS.md` OKR tables with this week's actuals.

## Step 8: Learning extraction

Read this week's session reviews from `knowledge/session-reviews/YYYY/MM/`. Use Glob to find files for the last 7 days.

### 8a: Recurring prompts analysis

Across all session reviews, look at `## User Prompts (Verbatim)` sections. Identify:

- **Repeated prompts** — similar requests made 2+ times across sessions
- **Prompts that required workarounds** — user asked for something that doesn't exist as a skill

For each recurring pattern, suggest:

- "You asked [prompt] X times this week. Consider creating a `/skill-name` skill for this."
- "You ran [skill-A then skill-B then skill-C] as a chain X times. Consider creating a `/chained-skill` that automates this sequence."

### 8b: Missing capabilities

Across all session reviews, read `## Missing Capabilities` sections. Aggregate:

- What capabilities were missing across multiple sessions?
- Which suggestions appeared more than once?

Present: "Based on this week's sessions, these capabilities are missing: [list]. Want me to create any of these as skills?"

### 8c: AGENTS.md improvement proposals

Based on journal patterns and session review analysis:

- If completion rate is consistently low — propose adjusting daily guidance.
- If certain task categories dominate — propose updating priority guidelines.
- If specific workflows emerged that aren't documented — propose adding them.

Present 0–2 specific AGENTS.md changes. **Never auto-apply.** Always present for user approval.

### 8d: Memory maintenance

Read `MEMORY.md` from this project's memory directory (typically `~/.claude/projects/<encoded-cwd>/memory/MEMORY.md`) and check the linked memory files for:

- Stale memories that should be updated (project states that changed)
- New feedback worth saving (patterns confirmed this week)

Also scan `knowledge/decisions/` for decisions made this week — surface them in the review and look for repeat patterns worth codifying.

Propose updates: "Memory X is outdated — want me to update it?"

## Step 9: Save weekly summary

Save the full weekly review output to `knowledge/journals/YYYY/weekly/WXX.md` where `XX` is the ISO week number. Create the directory if needed.

Include:

- Tasks completed and completion rate
- Pipeline movement
- OKR scores (if they exist)
- Patterns detected from journals and session reviews
- Skills suggested
- AGENTS.md proposals (accepted or rejected)
- Top priorities for next week

This file becomes input for `/quarterly` reviews and long-term trend analysis.

## Step 10: Post to Slack (optional)

Ask: "Post weekly review to #os-progress?"

If yes, format a summary and post using `mcp__plugin_slack_slack__slack_send_message` to `#os-progress`:

- Tasks completed this week (count, grouped by goal)
- Pipeline movement (projects advanced, projects killed)
- OKR scores (if they exist)
- Top 3 priorities for next week

Use Slack message formatting (bold, bullet points). If Slack MCP is unavailable, skip silently.
