---
name: meeting-sync
description: >
  Syncs new Granola meetings into knowledge/meetings/ organized by date,
  enriches knowledge/people/ with interaction history, and cross-references
  action items to tasks. Use this skill whenever the user says "sync my
  meetings", "pull in new Granola meetings", "update my meeting notes",
  "check for new meetings", "sync Granola", or mentions recent meetings that
  haven't been captured — even if they don't explicitly request a sync.
allowed-tools: Read Write Edit Glob Bash mcp__granola__*
argument-hint: "[--all | --skip | --since YYYY-MM-DD]"
---

# Meeting Sync

Pull recent Granola meetings into local markdown via the official Granola MCP server (`https://mcp.granola.ai/mcp`), then enrich People profiles and extract action items.

## Tool Surface

The official Granola MCP exposes these tools (post-authentication):

- `mcp__granola__list_meetings` — list recent meetings with metadata
- `mcp__granola__get_meetings` — fetch full content + enhanced notes for one or more meeting IDs
- `mcp__granola__get_meeting_transcript` — fetch raw transcript (paid plan only)
- `mcp__granola__list_meeting_folders` — browse meeting folders (paid plan only)
- `mcp__granola__query_granola_meetings` — natural-language Q&A across all meetings

If a call returns an auth error, the MCP server disconnects and the tools become unavailable until the user re-authenticates via Claude Settings → Connectors → Granola (or the manual `authenticate` flow).

## Instructions

### Step 0: Granola auth pre-flight

Before doing anything else, verify the Granola MCP is authenticated:

- Try `mcp__granola__list_meetings` with a tiny window (e.g. `limit: 1`). If it succeeds, proceed.
- If the call fails with an auth error, OR the only Granola tools exposed are `authenticate` / `complete_authentication`, the user is NOT authenticated. Stop the sync and tell the user:

  > "Granola isn't authenticated in Claude. Open Claude Settings → Connectors → Granola to authenticate, OR call `mcp__granola__authenticate` → follow the flow → `mcp__granola__complete_authentication`. Re-run `/meeting-sync` after auth succeeds."

- Do NOT attempt to sync without auth; failing deep inside Step 4 after partial work wastes tokens and leaves `knowledge/.granola-sync.json` in an inconsistent state.

### Step 1: Determine Sync Window

Read `knowledge/.granola-sync.json` if it exists — use `last_sync` as the cutoff. Otherwise default to the last 7 days. If `--since YYYY-MM-DD` was passed, use that.

### Step 2: List Recent Meetings

Call `mcp__granola__list_meetings` with the cutoff. Filter to meetings with notes/content (skip placeholders).

If the call fails with auth error, tell the user: "Granola MCP requires re-authentication. Open Claude Settings → Connectors → Granola, or run the manual auth flow."

If no new meetings are found, tell the user and skip to Step 7.

### Step 3: Present & Confirm

```
I found N new meeting(s) since YYYY-MM-DD:

1. **Title** (Date) — N attendees, N min
2. **Title** (Date) — N attendees, N min
...

Add to knowledge folder?
```

Use AskUserQuestion (skip if `--all` or `--skip` was passed):

| Option | Description |
|--------|-------------|
| Sync all | Add every meeting |
| Select specific | Pick which to sync |
| Skip for now | Continue without syncing |

### Step 4: Fetch Content for Selected Meetings

For each selected meeting:

1. Call `mcp__granola__get_meetings` with the meeting ID(s) — returns title, attendees, time, enhanced notes.
2. Call `mcp__granola__get_meeting_transcript` with the meeting ID — paid plan only. If it errors with "subscription required", proceed without transcript.
3. Compute path `knowledge/meetings/YYYY/MM/DD.md` from the meeting date. Create the directory with `mkdir -p` if missing.
4. If the file already exists, append the new meeting block separated by `---` (one file per day, multiple meetings allowed).
5. Write a block in this format:

```markdown
---
date: YYYY-MM-DD
time: HH:MM
title: <meeting title>
attendees: <comma-separated names>
duration_min: <number>
granola_id: <id>
---

## Enhanced Notes
<content from get_meetings>

## Transcript
<content from get_meeting_transcript, or "(transcript unavailable — requires paid plan)">
```

### Step 5: Update Sync Cursor

Write `knowledge/.granola-sync.json`:

```json
{
  "last_sync": "<today's date in YYYY-MM-DD>",
  "synced_count": <N>,
  "synced_ids": ["<id>", ...]
}
```

### Step 6: Extract & Route Action Items

Walk the enhanced notes of each synced meeting for action items. Look for:
- Explicit "Action Items" or "Next Steps" sections
- Phrases: "will do", "action item", "follow up", "committed to", "need to", "by [date]"
- Unchecked checkboxes (`- [ ]`)

Group by owner (me / them / unclear):

```
**For you:**
1. <action> — due: <date>

**For them (<Name>):**
1. <action>

**Unclear owner:**
1. <action>
```

Use AskUserQuestion per group:

| Option | Description |
|--------|-------------|
| Create tasks | Write tasks/ files with meeting reference in resource_refs |
| Add to People | Append to attendee's Interaction History (Step 7) |
| Both | Both |
| Skip | Drop these |

For "Create tasks" / "Both": create files in `tasks/` using the standard task template. `category` inferred from action verb. `priority: P2` unless clearly urgent. `resource_refs` points at the meeting file.

### Step 7: Update People Profiles

For each attendee, enrich `knowledge/people/<firstname-lastname>.md` following the procedure at `.claude/skills/meeting-sync/references/people-enrichment.md`. The reference covers the People template structure, gws email enrichment, and group dynamics.

### Step 8: Continue

Suggest: "Now let's plan your day — checking your tasks and pipeline."

## Additional Capabilities

- **Natural-language queries:** When the user asks about past meetings without specifying one (e.g., "What did we decide about pricing last week?"), call `mcp__granola__query_granola_meetings` instead of syncing — it answers across all meetings.
- **Folder browsing:** When the user wants to find meetings by folder/project, call `mcp__granola__list_meeting_folders` (paid plan only).

## Notes

- Sync state lives at `knowledge/.granola-sync.json`. Delete to force a full re-sync.
- `get_meeting_transcript` requires a paid Granola plan — degrade gracefully on free plans.
- If the MCP server is unreachable or auth expires, skip gracefully and proceed with morning planning.
- Date-nest meeting files (`knowledge/meetings/YYYY/MM/DD.md`) so weekly/quarterly reviews can scan by date range.
