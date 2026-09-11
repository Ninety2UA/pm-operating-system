---
name: weekly
description: |-
  Run a 20-minute weekly review — plan-vs-actual analysis from daily journals, shipping summary from completed tasks, pipeline movement, OKR progress, pattern detection from session reviews, AGENTS.md improvement proposals, and top priorities for next week. Use this skill whenever the user asks how the week went, wants to plan next week, runs `/weekly`, mentions retros or weekly reviews, or says anything like "wrap up the week," "Friday review," "weekly reflection," or "what did I ship." Push toward this at end of week even if the user doesn't explicitly ask.
argument-hint: "[quick]"
generated_from: .claude/skills/weekly/SKILL.md
source_sha256: 3a69fa39900a6fe23d58a2a3f3fc7ceff5e0f892fb5c931c76b7db082d226102
x_generated_note: "do not edit — regenerate with: uv run core/scripts/build_adapters.py"
---

# Weekly Review

A 20-minute session reviewing execution, pipeline, and OKRs.

If the argument is `quick`, condense to: what finished, what's blocked, top 3 next week.

## Step 1: Execution review

Call the `get_task_summary` tool (manager-ai MCP server) for aggregate stats.

List tasks completed this week (status `d`). Group by goal/OKR alignment:

- Tasks per goal
- Time invested vs estimated
- Sprint completion rate (if a sprint plan exists in `knowledge/sprint-*.md`)

## Step 1b: Shipped this week

Call the `list_tasks` tool (manager-ai MCP server) with `status: "d"` and `include_done: true` to get all completed tasks.

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

Call the `get_pipeline_status` tool (manager-ai MCP server) and the `get_project_summary` tool (manager-ai MCP server).

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

## Step 4b: Currency drift roll-up

Aggregate the week's framework currency (read-only, silent-degrade like the morning step): call the `get_watcher_status` tool (manager-ai MCP server) (fallback: newest completed reports under `knowledge/currency/reports/*/`). Report: days since each watcher last ran, undecided candidates accumulating, and — if a watcher hasn't produced a completed report in over 14 days while automation is meant to be active — flag it as drift to investigate. Skip silently if no currency data exists.

## Step 5: Blockers and stalled work

Call the `list_tasks` tool (manager-ai MCP server) with `status: "b"` for blocked tasks.

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

If a pattern points at an existing skill that misled or cost effort rather than at a missing one, it is a rewrite candidate, not a new-skill candidate — 8c applies before anything is proposed.

### 8b: Missing capabilities

Across all session reviews, read `## Missing Capabilities` sections. Aggregate:

- What capabilities were missing across multiple sessions?
- Which suggestions appeared more than once?

Present: "Based on this week's sessions, these capabilities are missing: [list]. Want me to create any of these as skills?"

Also read every `## Skill gaps` section: which skill's guidance was wrong or missing, the excerpt that misled, and what was done instead. Count how many sessions each skill appears in. These are rewrite candidates and go through 8c.

### 8c: Before-measurement for rewrites

A proposal to rewrite or restructure an existing skill must carry a before-measurement taken from this week's evidence, not from impression:

- **What it costs or misses today** — figures from the journals or session reviews: how many sessions hit the gap (`## Skill gaps` and `## What Didn't Work` entries), how many retries or manual workarounds each cost, or which output the skill produced that the owner then corrected.
- **The source lines** — the review or journal files the figures came from, so the owner can check them.
- **The one number the rewrite should move** — so next week's review can take the after-measurement and say whether the rewrite worked.

No before-measurement, no rewrite proposal: record the pattern under carried-over findings (Step 9) and measure it next week. New-skill proposals from 8a and 8b need none — there is nothing to measure yet. (RW-2026-09-11-18)

### 8d: AGENTS.md improvement proposals

Based on journal patterns and session review analysis:

- If completion rate is consistently low — propose adjusting daily guidance.
- If certain task categories dominate — propose updating priority guidelines.
- If specific workflows emerged that aren't documented — propose adding them.

Present 0–2 specific AGENTS.md changes. **Never auto-apply.** Always present for user approval.

### 8e: Memory maintenance

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
- Skills suggested, and rewrite proposals with their before-measurement
- AGENTS.md proposals (accepted or rejected)
- Top priorities for next week

Segment the findings (patterns, blockers, skill gaps, proposals) into two blocks and keep them apart in the file:

```markdown
## Findings
### This week (new: N)
- [finding first seen in this week's journals or session reviews]

### Carried over (open: M)
- [W36] [finding already listed in an earlier weekly summary and still open]
```

Build the carried-over block from the previous `WXX.md`: its carried-over block plus its this-week block, minus anything the owner addressed or dismissed since, each tagged with the week it first appeared. A finding leaves the list only on the owner's say-so, never because it stopped being mentioned. Put the two counts in the summary header so `/quarterly` reads them without re-deriving. (RW-2026-09-11-25)

This file becomes input for `/quarterly` reviews and long-term trend analysis.

## Step 10: Post to Slack (optional)

Ask: "Post weekly review to #os-progress?"

If yes, format a summary and post using the `slack_send_message` tool (Slack MCP server) to `#os-progress`:

- Tasks completed this week (count, grouped by goal)
- Pipeline movement (projects advanced, projects killed)
- OKR scores (if they exist)
- Top 3 priorities for next week

Use Slack message formatting (bold, bullet points). If Slack MCP is unavailable, skip silently.
