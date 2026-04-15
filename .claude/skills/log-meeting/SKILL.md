---
name: log-meeting
description: >
  Create a structured meeting note artifact for meetings not captured by Granola
  (manual notes, walk-and-talks, phone calls, in-person meetings, team standups)
  using a type-specific template (1on1, interview, one-off, standup). Use this
  skill whenever the user says "log a meeting", "capture meeting notes", "I
  just had a 1:1 with X", "log my interview with X", "log today's standup",
  "took notes from a call", "create a meeting file", or wants to record a
  meeting that won't be auto-synced from Granola. For Granola-captured meetings
  use `/meeting-sync` instead. For pre-meeting briefings use `/meeting-prep`.
allowed-tools: Read Write Edit Glob Bash
argument-hint: "<type:1on1|interview|one-off|standup> <person-team-or-topic>"
---

# Log Meeting — Manual Meeting Note Artifact

Create a structured note file for meetings that aren't captured automatically by Granola. Four sub-types: `1on1`, `interview`, `one-off`, `standup`.

## When to Use

- Manual capture of a 1:1 (recurring or ad-hoc) when Granola wasn't recording
- User research interview notes (qualitative research, customer discovery)
- Generic one-off meeting (vendor call, partner intro, kickoff, stakeholder sync)
- Team standup notes (Sprint context + per-person updates) — *different from `/morning` which is YOUR personal day plan*

For meetings already in Granola → use `/meeting-sync`.
For pre-meeting prep briefings → use `/meeting-prep`.
For your own daily plan (not a team meeting) → use `/morning`.

## Instructions

### Step 1: Parse Arguments

Extract `<type>` and `<person-team-or-topic>`.

- Valid types: `1on1`, `interview`, `one-off`, `standup`
- Normalize person/team/topic to lowercase-hyphenated for the filename slug
- Reject any slug containing `..`, `/`, or characters besides letters, numbers, hyphens
- For `standup` with no team specified, use `standup` as the slug (file becomes `DD-standup.md`)

If type or person/topic is missing, ask:

> What type? `1on1` | `interview` | `one-off` | `standup`
> Who, what team, or what topic is the meeting about?

### Step 2: Compute File Path

`knowledge/meetings/YYYY/MM/DD-<type>-<slug>.md` based on today's date.

If the user mentions the meeting was on a different date, use that date instead — confirm with them.

Create directory with `mkdir -p` if missing.

If file already exists at that path, append `-2`, `-3`, etc. to the slug rather than overwriting.

### Step 3: Gather Light Context

For `1on1`:
- Check `knowledge/people/<slug>.md` — if exists, pull last interaction date and 1-line role/style
- Check most recent prior 1:1 file (Glob `knowledge/meetings/*/*/*-1on1-<slug>.md`) for the previous date

For `interview`:
- Ask which research project this interview belongs to (check `projects/` for active research projects, or `knowledge/research/projects/`)
- Ask for participant role and segment if not obvious

For `one-off`:
- Ask the meeting purpose in one line if not given
- Ask attendees if not given
- If multiple attendees from the same group/team, check `knowledge/people/` for an existing group profile (e.g., `engineering-leads.md`, `acme-account-team.md`) and link it

For `standup`:
- Ask the team/pod name if not given (used in slug)
- Ask the sprint name + sprint goal if not obvious from prior standup files
- Look for the most recent prior standup for this team (Glob `knowledge/meetings/*/*/*-standup-<team>.md`) and pull the previous day's commitments to seed today's "Yesterday" sections
- If a group profile exists for the team (`knowledge/people/<team>.md`), link it

### Step 4: Load Template & Pre-fill

Read the appropriate template from `.claude/skills/log-meeting/references/`:

- `1on1` → `1on1-template.md`
- `interview` → `interview-template.md`
- `one-off` → `one-off-template.md`
- `standup` → `standup-template.md`

Pre-fill:
- Date (today, or user-specified)
- Person/topic
- For 1:1: link to People profile, link to previous 1:1
- For interview: link to research project
- For one-off: attendees if known

Leave the body sections empty for the user to fill in (or fill from conversation if they're dictating notes now).

### Step 5: Save File

Write to the computed path.

### Step 6: Offer Follow-ups

Present:

> Logged to `knowledge/meetings/YYYY/MM/DD-<type>-<slug>.md`.
>
> Want me to:
> - Open this file for editing?
> - Extract action items into tasks (after you fill in the notes)?
> - Update the People profile for [name]?
> - Run `/meeting-prep <name>` for a related upcoming meeting?

If the user is dictating notes now (rather than logging after the fact), offer to fill the file with their dictation as they go.

### Step 7: Action Item Extraction (if user fills notes during this session)

After the user has populated the file's notes section, scan for action items:

- Explicit "Action Items" section bullets
- Phrases: "will do", "follow up", "committed to", "need to", "by [date]"
- Unchecked checkboxes (`- [ ]`)

Group by owner (me / them / unclear). Use AskUserQuestion:

| Option | Description |
|--------|-------------|
| Create tasks | Write `tasks/` files with this meeting as `resource_refs` |
| Add to People | Append to attendee's Interaction History |
| Both | Both |
| Skip | Drop these |

### Step 8: People Profile Touch-up

If the meeting was a 1:1 or one-off with a named person and `knowledge/people/<slug>.md` exists, append a one-line entry to its `## Interaction History` section:

```
- YYYY-MM-DD: **[Meeting Title]** — [1-line summary]. Decisions: [...]. Committed to: [...].
```

Update the `last_interaction` field in frontmatter.

If no profile exists, offer to create one using `knowledge/people/_template.md`.

## Notes

- Date-nested filename pattern (`YYYY/MM/DD-<type>-<slug>.md`) keeps the same flat-by-date browsing as Granola syncs
- Do NOT overwrite existing meeting files — append a numeric suffix
- Action item extraction only runs if the user actually populates the notes during the session — otherwise they'll do it later
- For recurring 1:1s, the previous-meeting link in the 1on1 template gives Claude an anchor for "since last time" framing
- For standups, link to the prior day's standup file at the top so "Yesterday" sections cross-reference cleanly
- All four templates include `## Follow-up Notes` and `## Learnings` sections — encourage the user to come back and append dated follow-ups as situations evolve, and surface learnings worth promoting to AGENTS.md, decisions, or memory
- For meetings involving a *group* of people, check whether a group profile exists at `knowledge/people/<group>.md` (template at `knowledge/people/_group-template.md`) — link it in the file rather than re-describing the group inline
