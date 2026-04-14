---
name: pre-mortem
description: >
  Runs a pre-mortem risk analysis on a project — imagines the project has
  already failed 6 months out and works backward to identify what went
  wrong. Produces a ranked risk matrix with mitigations and a Go/No-Go
  recommendation. Use this skill whenever the user mentions "what could go
  wrong", "risk analysis", "pre-mortem", "stress test this project",
  "failure modes", shows enthusiasm for building without having examined
  failure modes, or is about to move a project from evaluating to active —
  even if they don't say "pre-mortem."
allowed-tools: Read Write Edit Glob
argument-hint: "<project-name>"
---

# Pre-mortem

Imagine the project has failed 6 months from now. Work backward to identify why, then create a ranked risk matrix with concrete mitigations.

## Quick Start

User: `/pre-mortem campaign-optimizer-simulation`
Result: Reads all project artifacts, generates a pre-mortem analysis with ranked risks and mitigations, saves to `projects/campaign-optimizer-simulation/pre-mortem.md`.

## Instructions

### Step 1: Parse Arguments

Check `$ARGUMENTS` for a required `<project-name>`.

If no project name is provided, ask the user which project to analyze.

### Step 2: Validate Project Name

**Security check:** Reject any project name containing `..`, `/`, or non-alphanumeric characters besides hyphens.

Check if `projects/<project-name>/` exists. If not, list available projects.

### Step 3: Read Project Context

Read all available project artifacts:
1. `projects/<project-name>/idea.md` (required)
2. `projects/<project-name>/prd.md` (if exists)
3. `projects/<project-name>/lean-canvas.md` (if exists — key source for business risks)
4. `projects/<project-name>/gtm-plan.md` (if exists — key source for market risks)
5. `projects/<project-name>/user-stories.md` (if exists — key source for execution risks)
6. `knowledge/research/projects/<project-name>.md` (if exists — competitor/market risks)

The more artifacts available, the richer the pre-mortem. Minimum requirement is idea.md.

### Step 4: Check for Existing Pre-mortem

Check if `projects/<project-name>/pre-mortem.md` already exists.

If it does, ask the user: Overwrite or Skip.

### Step 5: Generate Pre-mortem

Imagine it is 6 months from now and the project has **completely failed**. Generate failure scenarios across these risk categories:

1. **Market risk** — Nobody wants this. The problem isn't real or painful enough.
2. **Competition risk** — A competitor launched something better, faster, or free.
3. **Execution risk** — Took too long to build. Scope crept. Never shipped.
4. **Technical risk** — Key technical assumption was wrong. Architecture doesn't scale.
5. **Business model risk** — Users came but nobody paid. Pricing was wrong.
6. **Distribution risk** — Couldn't reach the target audience. Channels didn't work.
7. **Team/resource risk** — Solo founder burnout. Not enough time alongside day job.
8. **Timing risk** — Market shifted. Platform changed APIs. Regulation changed.

For each category, generate 1-3 specific failure scenarios grounded in the project's actual context (not generic risks).

### Step 6: Write the Pre-mortem

Read the template at `.claude/skills/pre-mortem/references/pre-mortem-template.md` and fill each section from the project context and failure scenarios generated in Step 5.

### Step 7: Save the Pre-mortem

Save to `projects/<project-name>/pre-mortem.md`.

### Step 8: Update Project Resource Refs

Add `projects/<project-name>/pre-mortem.md` to the idea.md `resource_refs` array.

### Step 9: Present Summary

Present:
- Total risks identified and severity breakdown
- Top 3 critical/high risks with one-line descriptions
- Go / No-Go recommendation
- Top 3 actions before building
- Suggested next step

## Notes

- **No external calls:** This skill works entirely from local project files. No Perplexity needed.
- **Honesty over encouragement:** A pre-mortem that finds no critical risks is useless. Push hard to find real failure modes.
- **Kill conditions:** Every critical risk should have a kill condition — a concrete signal that means "stop working on this." This prevents sunk-cost thinking.
- **Best timing:** Run after lean canvas and GTM plan are done (more data = better risks), but before user stories and sprint planning (no point planning execution for a doomed project).
