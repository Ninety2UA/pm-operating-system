---
description: "Run a project through the full evaluation pipeline — validate → lean canvas → GTM → pre-mortem → user stories"
argument-hint: "<project-name> [--from <stage>]"
---

# Launch Pipeline

Chain the full evaluation pipeline for a project. Each step produces an artifact and asks for Go/No-Go before proceeding.

## Instructions

### Step 1: Parse Arguments

- Required: `<project-name>` — the folder name under Projects/
- Optional: `--from <stage>` — start from a specific stage (skip earlier ones)

Valid stages: `validate`, `lean-canvas`, `competitive`, `gtm`, `pre-mortem`, `user-stories`

### Step 2: Check Current State

Call `mcp__manager-ai__get_project_artifacts` for the project. Determine which artifacts already exist and where to start.

If `--from` is specified, start there. Otherwise, start from the first missing artifact.

Present: "Project **[name]** has: idea ✓, prd ✓, validation ✗. Starting from validation."

### Step 3: Run Pipeline Stages

Execute each stage in order. After each, present the key findings and ask **Go / No-Go / Skip**:

**Stage 1: Validate**
- Invoke `/validate-project <project-name>`
- Present: Market exists? Competitors? Opportunity strength?
- Go/No-Go: "Does this market opportunity justify further evaluation?"

**Stage 2: Lean Canvas**
- Invoke `/lean-canvas <project-name>`
- Present: Business model strength? Revenue model? Key risk?
- Go/No-Go: "Is this business model viable enough to plan a launch?"

**Stage 3: Competitive Analysis** (optional)
- Invoke `/competitive-analysis <project-name>`
- Present: Top threats? Key gaps? Differentiation opportunity?
- Go/No-Go: "Can you differentiate enough to compete?"

**Stage 4: GTM Plan**
- Invoke `/gtm-plan <project-name>`
- Present: Beachhead segment? Top channels? Pricing?
- Go/No-Go: "Is the go-to-market plan realistic for your resources?"

**Stage 5: Pre-mortem**
- Invoke `/pre-mortem <project-name>`
- Present: Critical risks? Top 3 actions? Go/No-Go recommendation?
- Go/No-Go: "Are the risks acceptable? Ready to build?"

**Stage 6: User Stories**
- Invoke `/user-stories <project-name> --tasks`
- Present: MVP scope, story count, estimated hours
- "Project is now active. Run `/sprint-plan` to plan your first sprint."

### Step 4: Update Project Status

After each Go decision, update the project's `idea.md` frontmatter:
- After Stage 1 (Validate): `project_status: evaluating`
- After Stage 5 (Pre-mortem Go): `project_status: ready`
- After Stage 6 (User Stories): `project_status: active`

### No-Go Handling

If user says No-Go at any stage:
- Ask: "Archive this project, or pause for later?"
- Archive: Set `project_status: archived`, note reason in Progress Log
- Pause: Set `project_status: paused`, note reason in Progress Log
- Suggest: "Run `/prioritize` to pick a stronger project to evaluate."

## Notes

- Each stage takes 5-15 minutes depending on depth
- The full pipeline takes 30-60 minutes for one project
- You can run `/launch <name> --from gtm` to resume where you left off
- Competitive analysis is optional — skip if the market is clearly uncontested
