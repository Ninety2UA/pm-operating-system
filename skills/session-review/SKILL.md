---
name: session-review
description: >
  Review the current session: capture user prompts, tools used, workflow chains,
  what worked, what didn't, and patterns noticed. Use at end of significant sessions,
  when user asks to review the session, or when prompted by session-end reflection.
allowed-tools: Read Write Edit Glob Bash
---

# Session Review

Capture a structured review of the current Claude Code session for pattern analysis and system improvement.

## When to Use

- End of significant work sessions (backlog processing, project evaluation, sprint planning)
- When the user asks: "review this session", "what did we do?", "save session learnings"
- When prompted by the session-end reflection rule in AGENTS.md

## Instructions

### Step 1: Reflect on the Session

Review the full conversation context. Extract:

1. **User prompts (verbatim)** — every substantive request the user made, quoted exactly. This is the most important section. These feed the weekly pattern analysis that suggests new commands and skills.
2. **What was accomplished** — concrete outcomes (files created, tasks processed, decisions made)
3. **Commands, skills, and tools used** — which /commands, /skills, and MCP tools were invoked
4. **Workflow chains** — sequences of actions that were run together (e.g., "/validate-project then /lean-canvas then /gtm-plan")
5. **What worked well** — approaches that were efficient or got good results
6. **What didn't work** — friction points, retries, confusion, dead ends
7. **Patterns noticed** — repeated questions, missing capabilities, workflow bottlenecks
8. **Missing capabilities** — things the user asked for that required workarounds or manual steps. These are candidates for new commands, skills, or MCP tools.

### Step 2: Determine Session Type and Judgement

**Session type** (pick the most fitting):
- `backlog-processing` — processing BACKLOG.md items
- `project-evaluation` — running pipeline skills on a project
- `sprint-planning` — capacity planning and task selection
- `task-management` — creating, updating, or reviewing tasks
- `research` — using Perplexity or deep research agents
- `content-creation` — writing, drafting, or content generation
- `system-improvement` — modifying AGENTS.md, skills, commands, or the system itself
- `general` — mixed or doesn't fit above categories

**Suggested judgement:**
- `success` — user got what they needed, no significant friction
- `partial` — some progress but gaps remain, or user had to correct course
- `failure` — task not completed or went significantly wrong
- `pending` — use when uncertain; default if unsure

### Step 3: Write the Review File

Create the directory if needed: `knowledge/session-reviews/YYYY/MM/`

Save to: `knowledge/session-reviews/YYYY/MM/DD_session-type.md`

If multiple reviews exist for the same day and type, append a number: `DD_session-type-2.md`

Use this format:

```markdown
---
date: YYYY-MM-DD
session_type: [type from Step 2]
judgement: [suggested judgement]
commands_used: [list]
skills_used: [list]
tools_used: [list of MCP tools]
reviewed: false
---
# Session Review: [Brief Description]

## User Prompts (Verbatim)
- "[exact prompt 1]"
- "[exact prompt 2]"
- "[exact prompt 3]"

## What Was Accomplished
- [outcome 1]
- [outcome 2]

## Workflow Chains
[command/skill] -> [command/skill] -> [command/skill]
- Context: [why this chain was used]

## What Worked
- [positive observation]

## What Didn't Work
- [friction point or issue]

## Patterns Noticed
- [recurring behavior, repeated question, or workflow bottleneck]

## Missing Capabilities
- [thing the user needed that doesn't exist as a command/skill/tool yet]
- Suggested: [what command/skill could be created]

## Session Reflection
[one-line takeaway]
```

### Step 4: Append to Daily Journal

If a journal exists for today at `knowledge/journals/YYYY/MM/DD.md`, append a one-line entry under `## Session Reflections`:

```
- [HH:MM] [session-type]: [one-line takeaway]
```

### Step 5: Confirm

Tell the user:
- Where the review was saved
- Key patterns or missing capabilities identified
- Suggest: "Run `/weekly` at end of week to analyze patterns across sessions"

## Notes

- Keep reviews concise. The goal is pattern data, not a transcript.
- The `## User Prompts (Verbatim)` section is the highest-value part. Be thorough here.
- Don't include trivial prompts like "yes", "ok", "continue". Capture the substantive requests.
- `## Missing Capabilities` directly feeds the weekly pattern analysis that suggests new commands/skills.
- Reviews are read by `/weekly` command for pattern analysis across the week's sessions.
