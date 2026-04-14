---
name: lean-canvas
description: >
  Creates a Lean Canvas business model for a project idea — problem, solution,
  key metrics, cost structure, revenue streams, unfair advantage, channels,
  customer segments, and value proposition. Use this skill whenever the user
  mentions business models, monetization, pricing strategy, customer segments,
  "create lean canvas", "business model for", "is this viable as a business",
  or wants to sanity-check whether a project can be a real business — even if
  they don't say "lean canvas" explicitly. Push toward this before committing
  build effort to a project that hasn't had its business model examined.
allowed-tools: Read Write Edit Glob mcp__perplexity__*
argument-hint: "<project-name> [--model quick|search|deep|reason]"
---

# Lean Canvas

Generate a Lean Canvas business model evaluation for an existing project idea, combining project context with market research.

## Quick Start

User: `/lean-canvas campaign-optimizer-simulation`
Result: Reads the project's idea.md and prd.md, researches market via Perplexity, produces a 9-block Lean Canvas, saves to `projects/campaign-optimizer-simulation/lean-canvas.md`.

## Instructions

### Step 1: Parse Arguments

Check `$ARGUMENTS` for:
- A required `<project-name>` (the project folder name under `projects/`)
- An optional `--model` flag (`quick`, `search`, `deep`, `reason`)

If no `--model` flag is provided, default to `mcp__perplexity__perplexity_ask`.

Model flag routing:
- `--model quick` → use `mcp__perplexity__perplexity_ask`
- `--model search` → use `mcp__perplexity__perplexity_search`
- `--model deep` → use `mcp__perplexity__perplexity_research` (set `strip_thinking: true`)
- `--model reason` → use `mcp__perplexity__perplexity_reason` (set `strip_thinking: true`)

If no project name is provided, ask the user which project to evaluate.

### Step 2: Validate Project Name

**Security check:** Reject any project name containing `..`, `/`, or non-alphanumeric characters besides hyphens. Respond: "Invalid project name. Use the project folder name only (e.g., 'campaign-optimizer-simulation')."

Check if `projects/<project-name>/` exists. If not, use Glob to list available projects under `projects/*/idea.md` and present them.

### Step 3: Read Project Context

Read `projects/<project-name>/idea.md`.

If `projects/<project-name>/prd.md` exists, read it too.

If `knowledge/research/projects/<project-name>.md` exists, read the validation brief for market data — this saves a Perplexity call and provides richer context.

Extract: title, context, scope, target audience, and any competitive data.

### Step 4: Check for Existing Canvas

Check if `projects/<project-name>/lean-canvas.md` already exists.

If it does, ask the user:
- **Overwrite**: Replace with fresh canvas
- **Skip**: Keep existing and abort

### Step 5: Market Research Call

Call the selected Perplexity tool to gather business model intelligence:

```
For the product concept "[project title]: [2-sentence summary from idea.md]", research:
(1) How similar products monetize — pricing models, revenue streams, price points,
(2) Customer acquisition channels used by competitors in this space,
(3) Key cost drivers for building and running this type of product,
(4) What unfair advantages successful competitors have built (network effects, data moats, brand).
Focus on products launched or updated since 2024.
```

If a validation brief already exists with competitor/market data, use it as primary source and make a lighter Perplexity call focused only on monetization and channels.

### Step 6: Build the Lean Canvas

Using the project context and research, fill in all 9 blocks. Read the template at `.claude/skills/lean-canvas/references/lean-canvas-template.md` and fill each section from the project context and research.

### Step 7: Save the Canvas

Save to `projects/<project-name>/lean-canvas.md`.

### Step 8: Update Project Resource Refs

Read `projects/<project-name>/idea.md` frontmatter. Add `projects/<project-name>/lean-canvas.md` to the `resource_refs` array.

Handle these cases:
- `resource_refs: []` → replace with the new path
- `resource_refs:` with existing items → append
- No `resource_refs` key → add after last frontmatter field

### Step 9: Present Summary

Present:
- One-line viability verdict (Strong / Moderate / Weak)
- The unique value proposition
- Revenue model and estimated price point
- The single biggest risk
- Suggested next step:
  - If Strong: "Run `/gtm-plan <project-name>` to plan your go-to-market."
  - If Moderate: "Run `/pre-mortem <project-name>` to stress-test risks before proceeding."
  - If Weak: "Consider killing this idea or pivoting the model. Run `/prioritize` to compare against other projects."

## Notes

- **Cost:** ~$0.03 (quick/default) to $0.40 (deep).
- **Dependency:** Works best after `/validate-project` has been run — reuses the research brief. Works standalone too.
- **Honesty policy:** If the business model is weak, say so clearly. Killing a bad idea early saves weeks of wasted effort. Never inflate viability to be encouraging.
- **Data sensitivity:** Only project summaries are sent to Perplexity, not full PRD implementation details.
