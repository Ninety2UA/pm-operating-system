---
description: "Process BACKLOG.md — classify items, detect duplicates, create tasks and projects"
argument-hint: "(no arguments)"
---

# Process Backlog

Turn BACKLOG.md into organized tasks and projects with duplicate detection.

## Instructions

### Step 0: Scan Slack Capture Channel (Optional)

If Slack MCP is available, call `mcp__slack__slack_get_channel_history` for `#os-backlog` to read recent messages.

Extract any actionable items from the messages and append them to `BACKLOG.md` before proceeding. If no new messages or Slack unavailable, skip to Step 1.

### Step 1: Read Backlog

Read `BACKLOG.md` and extract every actionable item (lines starting with `-`).

### Step 2: Check for Duplicates

Call `mcp__manager-ai__process_backlog_with_dedup` with the extracted items. This checks against BOTH existing Tasks/ AND Projects/ for duplicates.

Review the results:
- **new_tasks**: Ready to create
- **potential_duplicates**: Show to user with similarity scores, ask whether to merge or create new
- **needs_clarification**: Show ambiguity questions, ask user before creating

### Step 3: Classify Each Item

For items that pass dedup:
- **Single outcome, < ~2 hrs** → create task file in `Tasks/`
- **Multi-step, exploratory, or not yet decided** → create project folder:
  - Create `Projects/<project-name>/idea.md` using the Project Template
  - Invoke the `/PRD` skill to generate `Projects/<project-name>/prd.md`

### Step 4: Check Priority Limits

Call `mcp__manager-ai__check_priority_limits` before assigning P0/P1 to new items. If limits are exceeded, warn the user.

### Step 5: Goals Alignment

Read `GOALS.md`. Ensure each new task/project references a relevant goal in its Context section. If no goal fits, ask the user.

### Step 6: Present Summary

Show:
- Tasks created (count, priorities)
- Projects created (count)
- Duplicates found and resolved
- Items that need clarification
- Current priority distribution

### Step 7: Clear Backlog

After user confirms, clear processed items from BACKLOG.md.
