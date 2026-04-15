---
name: meeting-prep
description: >
  Prepares context for an upcoming meeting by gathering relevant history from
  knowledge/people/, open action items, prior meeting transcripts via Granola,
  and relationship context. Use this skill whenever the user says "prep for my
  meeting with", "what should I know before my call with", "meeting prep",
  names a person before a meeting ("I'm about to talk to X"), references an
  upcoming 1on1, customer call, or review — even if they name a person without
  explicitly requesting prep.
allowed-tools: Read Glob Grep mcp__granola__*
argument-hint: "<person-name> [--type 1on1|review|planning|customer]"
---

# Meeting Prep

Gather pre-meeting context from People profiles, past transcripts, open tasks, and goals — then output a focused prep document.

## Quick Start

**User:** `/meeting-prep sarah-martinez`
**Output:** Prep doc with Sarah's communication style, last 3 interactions, open items, and suggested talking points.

**User:** `/meeting-prep acme-corp --type customer`
**Output:** Customer context, past meeting history, open commitments, and a "Do NOT Promise" reminder section.

## Instructions

### Step 1: Parse Arguments

Extract the person name or meeting subject from the argument. Normalize to lowercase-hyphenated form for file lookups.

If `--type` is provided, use it to shape the output (see Step 6). Default type is `1on1`.

Reject any argument containing `..`, `/`, or non-alphanumeric characters besides hyphens.

### Step 2: Look Up Person Profile

Check `knowledge/people/<person-name>.md`. If it exists, read it fully — extract:
- Communication preferences (how to present information)
- Decision-making style (what they need to decide)
- Meeting guidelines (what to lead with)
- Key topics and priorities (what they care about)
- Last interaction date and topic

If no profile exists, note this gap and proceed — the prep will rely on transcript history and tasks.

### Step 3: Search Past Meeting History

Search `knowledge/meetings/` for files mentioning this person:

1. Use Glob to find `knowledge/meetings/*<person-name>*` (direct matches)
2. Use Grep to search transcript content for the person's full name across all `knowledge/meetings/*.md` files
3. Query `mcp__granola__query_granola_meetings` with: "meetings with [person name]" to find recent context not yet synced

Collect the **3 most recent** meetings. For each, extract:
- Date and title
- Key discussion points
- Decisions made
- Open action items or commitments (look for `- [ ]` patterns and phrases like "will do", "action item", "follow up", "committed to", "need to")

### Step 4: Check Open Tasks

Search `tasks/` for any task referencing this person or related projects:

1. Use Grep to search `tasks/*.md` for the person's name
2. Note any tasks with status `n` (not started) or `s` (started) that relate to shared work

### Step 5: Check Goals Alignment

Read `GOALS.md` and identify any goals or OKRs relevant to the topics found in Steps 2-4. This helps frame the meeting around strategic priorities.

### Step 6: Generate Prep Document

Output a prep document directly to the user (do not save to file). Format based on meeting type:

#### Type: 1on1 (default)

```markdown
# Prep: 1:1 with [Name]
**Date:** [today or next meeting date]
**Their style:** [1-line from Communication Preferences]

## Relationship Context
[2-3 lines from People profile — role, what they care about, how to work with them]

## Last 3 Interactions
- [Date]: [Topic] — [Key outcome or open item]
- [Date]: [Topic] — [Key outcome or open item]
- [Date]: [Topic] — [Key outcome or open item]

## Open Items
- [ ] [Action from previous meetings — owner: me/them]
- [ ] [Related task from tasks/]

## Suggested Talking Points
1. [Follow up on open item X]
2. [Update on relevant goal/OKR progress]
3. [Topic from their key priorities]

## Goals Alignment
- [Which OKR this meeting advances]
```

#### Type: customer

Same structure plus:

```markdown
## Customer Context
- **Account:** [company, contract details if known]
- **Health:** [any signals from past meetings]

## Do NOT Promise
- [Remind: no commitments on timelines, pricing, or features without checking first]
```

#### Type: review

Same structure plus:

```markdown
## Review Context
- **What's being reviewed:** [project/PRD/design]
- **Decision needed:** [what needs to be decided]
- **Pre-read:** [link to relevant artifact in projects/]
```

#### Type: planning

Same structure plus:

```markdown
## Planning Context
- **Sprint/period:** [current sprint or quarter]
- **Capacity:** [any known constraints]
- **Backlog items:** [relevant items from BACKLOG.md]
```

### Step 7: Flag Gaps

If any of these are missing, flag them at the bottom:

- No People profile exists → "Consider creating a profile after this meeting"
- No past transcripts found → "First recorded meeting — pay extra attention to their communication style"
- Open items with no owner → "Clarify ownership during the meeting"

## Notes

- This skill is read-only — it does not create or modify files
- If the person name doesn't match any profile or transcript, ask the user to clarify
- For group meetings with multiple people, run prep for the most important attendee or the meeting host
- Keep the prep document concise — aim for scannable output, not exhaustive dumps
- If Granola MCP is unavailable, skip Step 3's query and rely on local transcripts only

## Related Skills

- `/meeting-sync` — pull Granola-captured meetings into `knowledge/meetings/`
- `/log-meeting` — create a structured note artifact for meetings that aren't in Granola (1on1 / interview / one-off). Pair with `/meeting-prep` when you want both a briefing and a notes file ready before a meeting.
