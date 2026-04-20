---
name: launch
description: Run a specific project through the full evaluation pipeline — validate → lean canvas → GTM → competitive analysis → pre-mortem → spec → user stories — with a Go/No-Go gate after each evaluation stage and project-status updates as the project moves through idea → evaluating → ready → active. Use this skill whenever the user wants to evaluate, validate, or launch a specific project end-to-end, runs `/launch <project-name>`, or says anything like "run the pipeline on X," "full evaluation of Y," "is Z worth building," or "take this project through the evaluation flow." Starts from the first missing artifact unless `--from <stage>` is specified.
allowed-tools: Read Write Edit Glob Bash mcp__manager-ai__* mcp__plugin_slack_slack__*
argument-hint: "<project-name> [--from <stage>]"
---

# Launch Pipeline

Chain the full evaluation pipeline for a project. Each step produces an artifact and asks for Go/No-Go before proceeding.

## Step 1: Parse arguments

- Required: `<project-name>` — the folder name under `projects/`.
- Optional: `--from <stage>` — start from a specific stage (skip earlier ones).

Valid stages: `validate`, `lean-canvas`, `competitive`, `gtm`, `pre-mortem`, `spec`, `user-stories`.

## Step 2: Check current state

Call `mcp__manager-ai__get_project_artifacts` for the project. Determine which artifacts already exist and where to start.

If `--from` is specified, start there. Otherwise, start from the first missing artifact.

Present: "Project **[name]** has: idea ✓, prd ✓, validation ✗. Starting from validation."

## Step 3: Run pipeline stages

Execute each stage in order. After each, present the key findings and ask **Go / No-Go / Skip**.

**Stage 1: Validate**
- Invoke `/validate-project <project-name>`.
- Present: Market exists? Competitors? Opportunity strength?
- Go/No-Go: "Does this market opportunity justify further evaluation?"

**Stage 2: Lean Canvas**
- Invoke `/lean-canvas <project-name>`.
- Present: Business model strength? Revenue model? Key risk?
- Go/No-Go: "Is this business model viable enough to plan a launch?"

**Stage 3: GTM Plan**
- Invoke `/gtm-plan <project-name>`.
- Present: Beachhead segment? Top channels? Pricing?
- Go/No-Go: "Is the go-to-market plan realistic for your resources?"

**Stage 4: Competitive Analysis** (optional — skip if the market is clearly uncontested)
- Invoke `/competitive-analysis <project-name>`.
- Present: Top threats? Key gaps? Differentiation opportunity?
- No blocking Go/No-Go. Present findings and continue.

**Stage 5: Pre-mortem**
- Invoke `/pre-mortem <project-name>`.
- Present: Critical risks? Top 3 actions? Go/No-Go recommendation?
- Go/No-Go: "Are the risks acceptable? Ready to build?"

**Stage 6: Spec**
- Invoke `/spec <project-name>`.
- Present: System shape, chosen stack, P0 components, INFERRED count.
- No blocking Go/No-Go — spec is the build contract, not a kill-decision gate. Continue to Stage 7.

**Stage 7: User Stories**
- Invoke `/user-stories <project-name> --tasks`.
- Present: MVP scope, story count, estimated hours.
- "Project is now active. Run `/sprint-plan` to plan your first sprint."

## Step 4: Update project status

After each Go decision, update the project's `idea.md` frontmatter:

- After Stage 1 (Validate): `project_status: evaluating`
- After Stage 5 (Pre-mortem Go): `project_status: ready`
- After Stage 7 (User Stories): `project_status: active`

Stage 6 (Spec) does not change `project_status` — the project remains `ready` until Stage 7 completes.

## No-Go handling

If the user says No-Go at any stage:

- Ask: "Archive this project, or pause for later?"
- Archive: Set `project_status: archived`, note reason in Progress Log.
- Pause: Set `project_status: paused`, note reason in Progress Log.
- Suggest: "Run `/prioritize` to pick a stronger project to evaluate."

## Step 5: Post decision to Slack (optional)

After a final Go or No-Go decision, ask: "Post this decision to #os-progress?"

- Go: "[Project Name] — GO. Moving to [status]. [One-line MVP scope]."
- No-Go: "[Project Name] — NO-GO. [Archived/Paused]. Reason: [one line]."

Use `mcp__plugin_slack_slack__slack_send_message` to `#os-progress`. If Slack MCP is unavailable, skip silently.

## Notes

- Each stage takes 5–15 minutes depending on depth.
- The full pipeline takes 30–60 minutes for one project.
- Resume where you left off with `/launch <name> --from gtm`.
- Competitive analysis is optional — skip if the market is clearly uncontested.
