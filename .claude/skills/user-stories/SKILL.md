---
name: user-stories
description: >
  Generates structured user stories with acceptance criteria from a project's
  PRD, using the "As a [role], I want [action], so that [benefit]" format
  with INVEST criteria. Use this skill whenever the user says "create user
  stories", "break this into stories", "decompose this PRD", "what should I
  build first", "user stories for X", or whenever a project has a PRD and is
  moving from evaluating to active — even if the user just says "let's start
  building X." Pass `--tasks` to also generate individual task files.
allowed-tools: Read Write Edit Glob
argument-hint: "<project-name> [--tasks]"
---

# User Stories

Generate structured user stories with acceptance criteria from a project's PRD, ready for sprint planning or task decomposition.

## Quick Start

User: `/user-stories ad-spend-anomaly-detector`
Result: Reads the PRD, generates prioritized user stories with acceptance criteria, saves to `projects/ad-spend-anomaly-detector/user-stories.md`.

User: `/user-stories ad-spend-anomaly-detector --tasks`
Result: Same as above, plus creates individual task files in `tasks/` for each P0/P1 story.

## Instructions

### Step 1: Parse Arguments

Check `$ARGUMENTS` for:
- A required `<project-name>`
- An optional `--tasks` flag (if present, also create task files from stories)

If no project name is provided, ask the user which project to decompose.

### Step 2: Validate Project Name

**Security check:** Reject any project name containing `..`, `/`, or non-alphanumeric characters besides hyphens.

Check if `projects/<project-name>/` exists. If not, list available projects.

### Step 3: Read Project Context

Read in order:
1. `projects/<project-name>/prd.md` (required — this is the primary input)
2. `projects/<project-name>/idea.md` (for context and goals alignment)
3. `projects/<project-name>/lean-canvas.md` (if exists — for customer segment context)

If no prd.md exists, stop and tell the user: "No PRD found. Run `/prd <project-name>` first to generate a product spec."

### Step 4: Check for Existing Stories

Check if `projects/<project-name>/user-stories.md` already exists.

If it does, ask the user: Overwrite or Skip.

### Step 5: Generate User Stories

From the PRD, extract every functional requirement, user flow, and feature. Convert each into a user story following this format:

PRD functional requirements use the format `FR-N [P-tier]: <behavior>` — preserve the P-tier from each FR as the corresponding user story's priority. Do not treat the `[P-tier]` tag as part of the behavior text.

For each story, assign:
- **Priority:** P0 (MVP-critical), P1 (important for v1), P2 (nice-to-have), P3 (future)
- **Size:** S (< 2 hrs), M (2-4 hrs), L (4-8 hrs), XL (> 8 hrs, should be split)
- **Acceptance criteria:** 2-5 testable conditions using Given/When/Then or checklist format

Group stories by epic (major feature area from the PRD).

### Step 6: Write the Stories Document

Read the template at `.claude/skills/user-stories/references/user-stories-template.md` and fill each section from the stories generated in Step 5 — it defines the full document structure (frontmatter, summary table, MVP/v1/Future scope sections grouped by epic, and the story map).

### Step 7: Save the Stories

Save to `projects/<project-name>/user-stories.md`.

### Step 8: Create Task Files (if --tasks flag)

If `--tasks` was passed, create individual task files in `tasks/` for each P0 and P1 story. Read the template at `.claude/skills/user-stories/references/task-from-story-template.md` and fill each section from the corresponding story — it defines the per-task frontmatter and the Context / User Story / Acceptance Criteria / Progress Log body.

### Step 9: Update Project Resource Refs

Add `projects/<project-name>/user-stories.md` to the idea.md `resource_refs` array.

### Step 10: Present Summary

Present:
- Total story count by priority
- MVP scope: number of P0 stories and estimated hours
- Story map overview
- If `--tasks`: list of created task files
- Suggested next step

## Notes

- **No external calls:** This skill works entirely from local project files. No Perplexity needed.
- **XL stories:** Any story sized XL (> 8 hrs) should be flagged for splitting. Suggest how to break it down.
- **INVEST criteria:** Each story should be Independent, Negotiable, Valuable, Estimable, Small, Testable. Flag stories that violate these.
- **MVP discipline:** P0 should be the absolute minimum to validate the core value proposition. Be ruthless about scope.
