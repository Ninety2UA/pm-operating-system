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
argument-hint: "[--all | --skip]"
---

# Meeting Sync

Check for new Granola meetings and offer to sync them to your local knowledge/meetings folder.

Uses the official Granola MCP server (`https://mcp.granola.ai/mcp`).

## Instructions

### Step 1: Check for New Meetings

Call `mcp__granola__list_meetings` to find recent meetings. If `knowledge/.granola-sync.json` exists, read it to determine the last sync timestamp and filter to meetings after that date.

If `.granola-sync.json` doesn't exist, fetch the last 7 days of meetings.

### Step 2: Present Results

If new meetings are found, present them to the user:

```
I found X new meeting(s) since your last sync:

1. **Meeting Title** (Date)
2. **Meeting Title** (Date)
...

Add to knowledge folder?
```

If no new meetings are found, say so and continue to the morning planning workflow.

### Step 3: Ask User for Selection

Use AskUserQuestion with these options:

| Option | Description |
|--------|-------------|
| Sync all | Add all new meetings to knowledge/meetings |
| Select specific | Let user choose which meetings to sync |
| Skip for now | Continue without syncing |

If `--all` flag was passed, skip this step and sync all.
If `--skip` flag was passed, skip syncing entirely.

### Step 4: Sync Selected Meetings

For each meeting the user wants to sync:
1. Call `mcp__granola__get_meetings` with the meeting ID to get content and enhanced notes
2. Call `mcp__granola__get_meeting_transcript` with the meeting ID to get the raw transcript (paid plans only — skip gracefully if unavailable)
3. Write the meeting content to `knowledge/meetings/YYYY/MM/DD.md` using the Write tool (append if multiple meetings on the same day, separated by `---`)
4. Update `knowledge/.granola-sync.json` with the new last-sync timestamp

Ensure the date-nested directory exists (create with `mkdir -p knowledge/meetings/YYYY/MM/` if needed).

### Step 4b: Extract Action Items

After syncing, scan the enhanced notes of each synced meeting for action items and commitments.

**What to look for:**
- Explicit action items or next steps sections in Granola's enhanced notes
- Phrases: "will do", "action item", "follow up", "committed to", "need to", "by [date]"
- Unchecked checkboxes (`- [ ]`)

**For each extracted item, determine:**
- **Owner:** Who committed? (me vs. them vs. unclear)
- **Description:** What needs to be done
- **Due date:** If mentioned, otherwise leave blank
- **Source meeting:** Title and date

**Present extracted items to the user:**

```
I found X action items from [Meeting Title]:

**For you:**
1. [Action] — due: [date or "not specified"]
2. [Action]

**For them ([Name]):**
1. [Action]

**Unclear owner:**
1. [Action]
```

Use AskUserQuestion with these options for each group:

| Option | Description |
|--------|-------------|
| Create tasks | Create as tasks/ files with meeting reference |
| Add to People | Append to attendee's Interaction History |
| Both | Create tasks AND note in People profiles |
| Skip | Don't track these |

If "Create tasks" or "Both": create task files in `tasks/` using the standard template. Set `resource_refs` to the transcript file path. Set category based on content. Set priority to P2 unless the item is clearly urgent.

If "Add to People" or "Both": include the items in the People profile update (Step 4c).

### Step 4c: Update People Profiles (Auto-Enriched)

For each attendee encountered, enrich `knowledge/people/<name>.md` following the procedure at `${CLAUDE_PLUGIN_ROOT}/skills/meeting-sync/references/people-enrichment.md`. That reference covers interaction history format, gws email lookup, and group dynamics.

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
5. Gets content via `get_meetings`, writes to knowledge/meetings/
6. "Synced 3 meetings. Now for your day..."
7. Continues with task planning (morning standup workflow)

**User:** "What did we discuss about the Q2 roadmap?"

**Claude:**
1. Calls `mcp__granola__query_granola_meetings` with the question
2. Returns synthesized answer across all matching meetings

## Notes

- Only Granola meetings with notes/content are worth syncing
- Meetings marked "(no notes)" may be empty placeholders — skip these
- Sync state is tracked in `knowledge/.granola-sync.json`
- Files are saved to `knowledge/meetings/` with sanitized filenames (lowercase, hyphens, no special chars)
- `get_meeting_transcript` requires a paid Granola plan — skip gracefully on free plans
- If Granola MCP server is unavailable, skip meeting sync gracefully and proceed with morning planning
- Rate limit: ~100 requests/minute across all Granola tools
