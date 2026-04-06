---
name: meeting-sync
description: >
  Sync new Granola meetings to local Knowledge folder. Use during morning
  planning, when user asks "what should I do today", "sync my meetings",
  "check for new meetings", or asks to review recent meetings.
allowed-tools: Read Write Edit Glob Bash mcp__granola__*
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

Ensure `Knowledge/Transcripts/` directory exists (create with `mkdir -p` if needed).

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
| Create tasks | Create as Tasks/ files with meeting reference |
| Add to People | Append to attendee's Interaction History |
| Both | Create tasks AND note in People profiles |
| Skip | Don't track these |

If "Create tasks" or "Both": create task files in `Tasks/` using the standard template. Set `resource_refs` to the transcript file path. Set category based on content. Set priority to P2 unless the item is clearly urgent.

If "Add to People" or "Both": include the items in the People profile update (Step 4c).

### Step 4c: Update People Profiles (Auto-Enriched)

After syncing meetings, check `Knowledge/People/` for each meeting attendee. Each person gets their own file: `Knowledge/People/firstname-lastname.md`.

Read `Knowledge/People/_template.md` for the full profile structure.

**For NEW attendees** (no file exists in `Knowledge/People/`):

1. Create `Knowledge/People/firstname-lastname.md` using the template structure.

2. Analyze the synced meeting notes/transcript to infer and fill:
   - **Quick Facts:** Role, company, background (from how they were introduced)
   - **Communication Preferences:** Were they formal or casual? Did they prefer data or narrative? Did they drive discussion or listen? Async or sync? Mark inferred fields with "(inferred)".
   - **Decision-Making Style:** Did they decide quickly or need time? Ask for data? Want options? Defer to others?
   - **Meeting Guidelines:** What did they lead with? What got their attention? What bored them?
   - **Key Topics & Priorities:** What did they care about most in the meeting?
   - **How to Build Trust / What Damages Trust:** Any cues from the meeting about what they value?
   - **Interaction History:** Add this meeting as the first entry using the **rich format** below.

3. Enrich from email history using the `gws` CLI:
   ```bash
   gws gmail users messages list --params '{"userId": "me", "q": "from:<name> OR to:<name>", "maxResults": 5}' --format json
   ```
   Then fetch the top messages to analyze:
   - Tone and formality level in their emails
   - Response speed patterns (quick responder or slow?)
   - How they structure communication (bullet points? long prose? one-liners?)
   - What topics they email about vs. discuss in meetings
   
   If no email history exists or gws is unavailable, skip gracefully.

4. Set `auto_enriched: true` in the frontmatter.

**For EXISTING attendees** (file already exists):

1. Add a new entry to `## Interaction History` using the **rich format** below
2. Update `last_interaction` in frontmatter
3. If the meeting transcript reveals NEW information about their communication style, decision-making, or preferences — update the relevant sections. Don't overwrite manually-entered content.
4. If the profile is still thin (mostly "(inferred)" or empty sections) and email history is available, run gws enrichment.

**Rich Interaction History format:**

Instead of just "Met on date about topic", write entries that capture what matters for future prep:

```markdown
- YYYY-MM-DD: **[Meeting Title]** — [2-3 line summary of key discussion points]. Decisions: [what was decided]. Committed to: [action items with owner]. Follow-up: [what to revisit next time].
```

Example:
```markdown
- 2026-04-03: **Q2 Roadmap Review** — Discussed prioritization of AI features vs. platform stability. Sarah pushed for stability first, citing 3 customer escalations. Decisions: defer AI assistant to Q3, focus Q2 on reliability. Committed to: I'll draft revised timeline by Friday; Sarah will share escalation data. Follow-up: check if revised timeline works for engineering capacity.
```

This format feeds directly into `/meeting-prep` — richer history means better preparation for next time.

**For GROUP dynamics** (optional):

If the meeting had 3+ attendees who work together regularly, consider creating or updating a group dynamics file (e.g., `Knowledge/People/_team-engineering.md`) capturing:
- How team members interact with each other
- Who defers to whom
- Communication patterns within the group
- How to facilitate alignment across the group

This keeps profiles growing richer with each meeting — communication patterns, decision-making style, and relationship context all compound over time.

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
