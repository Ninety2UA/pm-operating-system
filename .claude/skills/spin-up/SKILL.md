---
name: spin-up
description: >
  Scaffold a project's CLAUDE.md so any future Claude Code session opened in
  that project directory has full context — links to PRD/lean-canvas/user-stories,
  goal alignment, recommended skills for the current pipeline stage, and the
  Context Management delegation rule. Use this skill whenever the user says
  "spin up a project", "scaffold CLAUDE.md", "set up project context",
  "initialize the project workspace", "make this project Claude-ready",
  promotes a project to active status, or starts working in a project repo
  for the first time. Push toward this whenever a project moves from `ready`
  to `active` and lacks a CLAUDE.md.
allowed-tools: Read Write Edit Glob Bash mcp__manager-ai__*
argument-hint: "<project-name>"
---

# Spin Up — Project CLAUDE.md Scaffolder

Generate a `projects/<name>/CLAUDE.md` so future Claude Code sessions opened in that project directory load with full context — artifact links, pipeline stage, goal alignment, recommended skills, and context-management defaults.

## When to Use

- Project just promoted to `active` and lacks a CLAUDE.md
- User opening a project repo for focused work and wants Claude to know the context
- Existing `projects/<name>/CLAUDE.md` is stale and needs regeneration

## Instructions

### Step 1: Resolve target project

Parse the argument as `<project-name>`. Reject any name containing `..`, `/`, or characters besides letters, numbers, and hyphens.

If the argument is missing, ask: **"Which project? (e.g., `ad-spend-anomaly-detector`)"**

Verify `projects/<project-name>/` exists. If not, ask the user whether to create it or pick an existing project.

### Step 2: Read existing context

Read whatever exists (skip silently if missing):

- `projects/<project-name>/idea.md` — title, scope, status
- `projects/<project-name>/prd.md` — full spec
- `projects/<project-name>/lean-canvas.md` — business model
- `projects/<project-name>/user-stories.md` — decomposed stories
- `projects/<project-name>/gtm-plan.md`, `pre-mortem.md`, `competitive-analysis.md`
- `GOALS.md` — to find the goal/OKR this project advances

Extract: title, one-line description, current `project_status`, `priority`, `category`, the relevant goal name.

### Step 3: Determine recommended next skills

Based on `project_status` and which artifacts are missing:

| Stage | Missing | Recommend |
|---|---|---|
| `idea` | `prd.md` | `/prd <name>` |
| `evaluating` | `lean-canvas.md` | `/lean-canvas <name>` |
| `evaluating` | `validation brief` | `/validate-project <name>` |
| `evaluating` | `competitive-analysis.md` | `/competitive-analysis <name>` |
| `evaluating` | `gtm-plan.md` | `/gtm-plan <name>` |
| `ready` | `pre-mortem.md` | `/pre-mortem <name>` |
| `ready` | `user-stories.md` | `/user-stories <name> --tasks` |
| `active` | sprint plan | `/sprint-plan` |

Pick the 2–3 most relevant.

### Step 4: Check for existing CLAUDE.md

If `projects/<project-name>/CLAUDE.md` exists, read it.

- If it already has a `## Context Management` section AND the artifact links are current → tell user it's up-to-date, ask if they want to regenerate anyway.
- If it's stale or missing the section → proceed and overwrite (after confirming).

### Step 5: Generate CLAUDE.md

Write to `projects/<project-name>/CLAUDE.md`:

```markdown
# [Project Title]

[One-line description from idea.md or prd.md]

**Status:** [project_status] | **Priority:** [P0–P3] | **Category:** [category]
**Advances goal:** [Goal name from GOALS.md, with OKR if relevant]

## Artifacts

- [PRD](./prd.md) — full spec _(if exists)_
- [Lean Canvas](./lean-canvas.md) — business model _(if exists)_
- [Validation Brief](../../knowledge/research/projects/[name].md) — market research _(if exists)_
- [Competitive Analysis](./competitive-analysis.md) — landscape map _(if exists)_
- [GTM Plan](./gtm-plan.md) — go-to-market strategy _(if exists)_
- [Pre-Mortem](./pre-mortem.md) — risk analysis _(if exists)_
- [User Stories](./user-stories.md) — buildable decomposition _(if exists)_
- [Idea](./idea.md) — original capture

_(Omit lines for artifacts that don't exist.)_

## Recommended Next Skills

Based on current pipeline stage (`[stage]`):

- `/[skill-1] [name]` — [why]
- `/[skill-2] [name]` — [why]

## Context Management

Context is your most valuable resource. Proactively delegate exploration, research, and verbose operations to subagents (Agent tool) instead of bloating the main conversation.

**Default to spawning a subagent for:**
- Reading 3+ files to answer one question
- Web research, doc lookups, library investigation
- Codebase exploration that produces verbose output
- Any task where only the summary matters

**Stay in main context for:**
- Direct file edits the user requested
- Short, targeted reads (1–2 specific files)
- Conversations requiring iterative back-and-forth
- Markdown writing/editing the user is reviewing live

**Rule of thumb:** If a task will read >3 files or produce output the user doesn't need verbatim, delegate and return a summary.

## When Working In This Directory

- Append progress to `idea.md`'s Progress Log on each meaningful update
- Keep this CLAUDE.md current — re-run `/spin-up [name]` when artifacts change
- Cross-reference back to `../../GOALS.md` when scoping decisions

## Parent System

This project lives inside the personal-os workspace. The root `AGENTS.md` and `CLAUDE.md` (two levels up) define the broader operating model — task pipelines, daily/weekly/quarterly rhythms, and the full skill catalog.
```

### Step 6: Confirm

Show the user the file path, the inferred status/goal/skills, and offer:

> Done — `projects/[name]/CLAUDE.md` is now scaffolded.
>
> When you next open this project directory in Claude Code, it'll load with the artifact links, pipeline stage, and recommended skills.
>
> Want me to update the project's `idea.md` Progress Log with a "spun up CLAUDE.md" entry?

## Notes

- Never overwrite an existing CLAUDE.md without explicit confirmation.
- If the project has no `idea.md` AND no `prd.md`, stop and ask the user to capture a basic description first — there's nothing to scaffold from.
- For projects with their own external git repo (e.g., a code repo at a different path), offer to also scaffold a CLAUDE.md there with the same template adapted for code work.
