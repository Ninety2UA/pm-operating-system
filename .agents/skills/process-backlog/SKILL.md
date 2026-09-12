---
name: process-backlog
description: |-
  Turn BACKLOG.md into organized tasks and projects with duplicate detection (checks against existing tasks/ AND projects/), classify each item as task-vs-project, enforce goals alignment, warn on priority-limit overages, and clear the processed items from BACKLOG.md. Use this skill whenever the user says "clear my backlog," "process backlog," "triage my inbox," "sort out BACKLOG.md," runs `/process-backlog`, dumps new items into the backlog, or mentions the capture inbox. Push toward this whenever BACKLOG.md has unprocessed items and a session is ending.
generated_from: .claude/skills/process-backlog/SKILL.md
source_sha256: d8157cbff7baabd0d68ff1d035876770ae3563b8e31ced191d067ef086c0471e
x_generated_note: "do not edit — regenerate with: uv run core/scripts/build_adapters.py"
---

# Process Backlog

Turn BACKLOG.md into organized tasks and projects with duplicate detection.

## Step 0: Scan Slack capture channel (optional)

If the Slack MCP is available, call the `slack_read_channel` tool (Slack MCP server) for `#os-backlog` to read recent messages.

Extract any actionable items from the messages and append them to `BACKLOG.md` before proceeding. If no new messages, or Slack unavailable, skip to Step 1.

## Step 1: Read backlog

Read `BACKLOG.md` and extract every actionable item (lines starting with `-`).

## Step 2: Check for duplicates

Call the `process_backlog_with_dedup` tool (manager-ai MCP server) with the extracted items. This checks against both existing `tasks/` and `projects/` for duplicates.

Review the results:

- **new_tasks** — ready to create
- **potential_duplicates** — show to user with similarity scores, ask whether to merge or create new
- **needs_clarification** — show ambiguity questions, ask user before creating
- **unreadable** — files the server could not parse

Print any `unreadable` paths before a single file is created, with "these could not be checked for duplicates". A task or project the server could not read is missing from the comparison, not absent from the workspace, so a duplicate can hide behind one. Fix them or say so, then continue. (RW-2026-09-12-1)

## Step 3: Classify each item

For items that pass dedup:

- **Single outcome, < ~2 hrs** → create a task file in `tasks/`.
- **Multi-step, exploratory, or not yet decided** → create a project folder:
  - Create `projects/<project-name>/idea.md` using the Project Template from AGENTS.md.
  - Invoke the `/prd` skill to generate `projects/<project-name>/prd.md`.
    - `/prd` defaults to non-interactive auto-inference. For backlog items with <1 paragraph of context, most PRD sections will be flagged `[INFERRED]` — tell the user to re-run `/prd <project-name> --ask` later to refine, or pass `--ask` directly here if the item needs clarification up-front.

**File slug rule.** Both `tasks/<slug>.md` and `projects/<slug>/` take their name from the item's title through these steps, in this order; `/research-topic` cites this rule rather than restating it:

1. Lowercase.
2. Transliterate Latin diacritics — German conventions first (`ä` to `ae`, `ö` to `oe`, `ü` to `ue`, `ß` to `ss`), then decompose what is left and drop the combining marks, so "café" becomes "cafe" and "über" becomes "ueber" rather than "ber".
3. Replace each run of characters outside `a-z0-9` with a single hyphen.
4. Cut to 60 characters.
5. Strip leading and trailing hyphens after the cut, never before it — a cut that lands on a separator puts one back.
6. If the slug is now empty (punctuation only, emoji only, or a script step 2 does not cover), fall back to `YYYY-MM-DD-item-N`, where N is the item's position in this run.
7. If that path already exists, append `-2`, then `-3`: the Step 2 dedup is semantic and will not catch two distinct items whose titles truncate to the same slug.

Scripts beyond Latin diacritics are out of scope; a title written in one takes the step 6 fallback. (RW-2026-09-12-22)


## Step 4: Check priority limits

Call the `check_priority_limits` tool (manager-ai MCP server) before assigning P0/P1 to new items. If limits are exceeded (P0 > 3 or P1 > 7), warn the user and ask to downgrade or defer.

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

This clear is the one sanctioned wholesale shrink of a curated file, and only after the user's confirmation in this session. Everywhere else, before replacing a curated file wholesale, compare line counts — the current file's and the replacement's, never bytes — and when the current file has 40 or more lines and the replacement has fewer than 40% of them, stop, show both counts, and ask. The rule is advisory: it judges one write at a time and cannot see erosion spread across several. (RW-2026-09-12-20)

## Rationalization guard

- *"This item is obvious — I'll skip the duplicate check."* The dedup call is one tool invocation; a duplicate project costs weeks. Always run it.
- *"The user is busy — I'll guess the priority instead of asking."* The STOP-and-ask rule for missing context/priority exists because a wrong P0 pollutes every daily plan. Batch the questions and ask once.
- *"I'll create the project now and generate the PRD later."* A project without its PRD stalls at the first pipeline gate; generate it as part of this flow.
- *"The file's structure is a mess — I'll just rewrite it."* That is how a hundred curated lines become twelve with nobody noticing. Count the lines of both versions first, and when the replacement falls under the 40% bar, show both counts and ask. The BACKLOG clear in Step 7 is the only shrink that needs no such check.
