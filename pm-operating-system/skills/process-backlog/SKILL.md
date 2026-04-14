---
name: process-backlog
description: Turn BACKLOG.md into organized tasks and projects with duplicate detection (checks against existing tasks/ AND projects/), classify each item as task-vs-project, enforce goals alignment, warn on priority-limit overages, and clear the processed items from BACKLOG.md. Use this skill whenever the user says "clear my backlog," "process backlog," "triage my inbox," "sort out BACKLOG.md," runs `/process-backlog`, dumps new items into the backlog, or mentions the capture inbox. Push toward this whenever BACKLOG.md has unprocessed items and a session is ending.
allowed-tools: Read Write Edit Glob mcp__manager-ai__* mcp__plugin_slack_slack__*
---

# Process Backlog

Turn BACKLOG.md into organized tasks and projects with duplicate detection.

## Step 0: Scan Slack capture channel (optional)

If the Slack MCP is available, call `mcp__plugin_slack_slack__slack_read_channel` for `#os-backlog` to read recent messages.

Extract any actionable items from the messages and append them to `BACKLOG.md` before proceeding. If no new messages, or Slack unavailable, skip to Step 1.

## Step 1: Read backlog

Read `BACKLOG.md` and extract every actionable item (lines starting with `-`).

## Step 2: Check for duplicates

Call `mcp__manager-ai__process_backlog_with_dedup` with the extracted items. This checks against both existing `tasks/` and `projects/` for duplicates.

Review the results:

- **new_tasks** — ready to create
- **potential_duplicates** — show to user with similarity scores, ask whether to merge or create new
- **needs_clarification** — show ambiguity questions, ask user before creating

## Step 3: Classify each item

For items that pass dedup:

- **Single outcome, < ~2 hrs** → create a task file in `tasks/`.
- **Multi-step, exploratory, or not yet decided** → create a project folder:
  - Create `projects/<project-name>/idea.md` using the Project Template from AGENTS.md.
  - Invoke the `/PRD` skill to generate `projects/<project-name>/prd.md`.

## Step 4: Check priority limits

Call `mcp__manager-ai__check_priority_limits` before assigning P0/P1 to new items. If limits are exceeded (P0 > 3 or P1 > 7), warn the user and ask to downgrade or defer.

## Step 5: Goals alignment

Read `GOALS.md`. Ensure each new task/project references a relevant goal in its Context section. If no goal fits, ask the user whether to create a new goal or defer the item.

## Step 6: Present summary

Show:

- Tasks created (count, priorities)
- Projects created (count)
- Duplicates found and resolved
- Items that need clarification
- Current priority distribution

## Step 7: Clear backlog

After the user confirms, clear processed items from `BACKLOG.md`. Leave any items that were deferred or need clarification with a one-line note about why.
