---
name: user-stories
description: |-
  Generates structured user stories with acceptance criteria from a project's PRD, using the "As a [role], I want [action], so that [benefit]" format with INVEST criteria. Use this skill whenever the user says "create user stories", "break this into stories", "decompose this PRD", "what should I build first", "user stories for X", or whenever a project has a PRD and is moving from evaluating to active — even if the user just says "let's start building X." Pass `--tasks` to also generate individual task files.
argument-hint: "<project-name> [--tasks]"
generated_from: .claude/skills/user-stories/SKILL.md
source_sha256: e5df4f276f4b7786fa58580875b66f50b0cbc27ca72e9e0f905f03dbb60af883
x_generated_note: "do not edit — regenerate with: uv run core/scripts/build_adapters.py"
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

Check the arguments provided when you were invoked for:
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
3. `projects/<project-name>/spec.md` (if exists — **the build task graph lives here**: §20 Work Breakdown Structure owns the stable `T-IDs`, and §2.1 maps each FR → module → tasks → tests. Consume these as the source of truth; do not re-derive a parallel decomposition.)
4. `projects/<project-name>/lean-canvas.md` (if exists — for customer segment context)

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

Read the template at `references/user-stories-template.md` and fill each section from the stories generated in Step 5 — it defines the full document structure (frontmatter, summary table, MVP/v1/Future scope sections grouped by epic, and the story map).

### Step 7: Save the Stories

Save to `projects/<project-name>/user-stories.md`.

### Step 8: Create Task Files (if --tasks flag)

If `--tasks` was passed, create individual task files in `tasks/` for each P0 and P1 story. Read the template at `references/task-from-story-template.md` and fill each section from the corresponding story — it defines the per-task frontmatter and the Context / User Story / Acceptance Criteria / Progress Log body.

**If `spec.md` has a §20 Work Breakdown Structure, materialize tasks FROM its `T-IDs`** rather than inventing a parallel decomposition: carry the spec's `T-ID`, exact file path, FR back-ref, and paired test into each task's Context, and respect the WBS dependency order. Only invent a task for a story with no matching WBS task — and flag those as candidates to add to the spec (suggest `/spec <name> --deepen`). The spec owns the dependency-ordered build graph; this skill adds the role/benefit + acceptance layer.

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

- **Spec owns the build task graph.** When `projects/<name>/spec.md` exists, its §20 Work Breakdown Structure is the source of truth for build tasks (stable `T-IDs`, dependency-ordered, test-paired). `--tasks` materializes those T-IDs into `tasks/` — it does not re-derive a parallel decomposition. User stories add the role/benefit + acceptance layer on top and trace to the spec's FRs/tasks. Run `/spec` before `/user-stories` so stories cite concrete tasks; stories with no matching WBS task get flagged to add to the spec.
- **No external calls:** This skill works entirely from local project files. No Perplexity needed.
- **XL stories:** Any story sized XL (> 8 hrs) should be flagged for splitting. Suggest how to break it down.
- **INVEST criteria:** Each story should be Independent, Negotiable, Valuable, Estimable, Small, Testable. Flag stories that violate these.
- **MVP discipline:** P0 should be the absolute minimum to validate the core value proposition. Be ruthless about scope.
