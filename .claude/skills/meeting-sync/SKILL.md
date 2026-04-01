---
name: meeting-sync
description: >
  Sync new Granola meetings to local Knowledge folder. Use during morning
  planning, when user asks "what should I do today", "sync my meetings",
  "check for new meetings", or asks to review recent meetings.
allowed-tools: Read Write Edit Glob mcp__granola__*
argument-hint: "[--all | --skip]"
---

# Meeting Sync

Check for new Granola meetings and offer to sync them to your local Knowledge/Transcripts folder.

Uses the official Granola MCP server (`https://mcp.granola.ai/mcp`).

## Instructions

### Step 1: Check for New Meetings

Call `mcp__granola__list_meetings` to find recent meetings. If `Knowledge/.granola-sync.json` exists, read it to determine the last sync timestamp and filter to meetings after that date.

If `.granola-sync.json` doesn't exist, fetch the last 7 days of meetings.

### Step 2: Present Results

If new meetings are found, present them to the user:

```
I found X new meeting(s) since your last sync:

1. **Meeting Title** (Date)
2. **Meeting Title** (Date)
...

Add to Knowledge folder?
```

If no new meetings are found, say so and continue to the morning planning workflow.

### Step 3: Ask User for Selection

Use AskUserQuestion with these options:

| Option | Description |
|--------|-------------|
| Sync all | Add all new meetings to Knowledge/Transcripts |
| Select specific | Let user choose which meetings to sync |
| Skip for now | Continue without syncing |

If `--all` flag was passed, skip this step and sync all.
If `--skip` flag was passed, skip syncing entirely.

### Step 4: Sync Selected Meetings

For each meeting the user wants to sync:
1. Call `mcp__granola__get_meetings` with the meeting ID to get content and enhanced notes
2. Call `mcp__granola__get_meeting_transcript` with the meeting ID to get the raw transcript (paid plans only — skip gracefully if unavailable)
3. Write the meeting content to `Knowledge/Transcripts/YYYY-MM-DD_meeting-title.md` using the Write tool
4. Update `Knowledge/.granola-sync.json` with the new last-sync timestamp

Ensure `Knowledge/Transcripts/` directory exists before writing (SessionStart hook creates it).

### Step 5: Continue with Morning Flow

After syncing (or skipping), continue with the normal morning planning workflow:
- Check tasks
- Review priorities
- Suggest focus items for the day

**Suggested next step:** "Now let's plan your day — checking your tasks and pipeline."

## Additional Capabilities

The official Granola MCP also provides:

- `mcp__granola__query_granola_meetings` — Ask natural language questions across all your meeting notes (e.g., "What did we decide about pricing last week?"). Use this when the user asks about past meetings without specifying a specific one.
- `mcp__granola__list_meeting_folders` — Browse meeting folders (paid plans only). Use when the user wants to find meetings by folder/project.

## Example Flow

**User:** "What should I do today?"

**Claude:**
1. Calls `mcp__granola__list_meetings` to find recent meetings
2. "I found 3 new meetings since your last sync..."
3. Presents AskUserQuestion with sync options
4. User selects "Sync all" or specific meetings
5. Gets content via `get_meetings`, writes to Knowledge/Transcripts/
6. "Synced 3 meetings. Now for your day..."
7. Continues with task planning (morning standup workflow)

**User:** "What did we discuss about the Q2 roadmap?"

**Claude:**
1. Calls `mcp__granola__query_granola_meetings` with the question
2. Returns synthesized answer across all matching meetings

## Notes

- Only Granola meetings with notes/content are worth syncing
- Meetings marked "(no notes)" may be empty placeholders — skip these
- Sync state is tracked in `Knowledge/.granola-sync.json`
- Files are saved to `Knowledge/Transcripts/` with sanitized filenames (lowercase, hyphens, no special chars)
- `get_meeting_transcript` requires a paid Granola plan — skip gracefully on free plans
- If Granola MCP server is unavailable, skip meeting sync gracefully and proceed with morning planning
- Rate limit: ~100 requests/minute across all Granola tools
