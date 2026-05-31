---
name: gtm-plan
description: |-
  Creates a Go-to-Market plan for a project — ICP, beachhead segment, positioning, channels, launch timeline, and growth loops. Use this skill whenever the user mentions launching, selling, positioning, distribution, channels, pricing strategy, "go to market plan", "how do I launch this", "who should I sell to", "GTM strategy", "plan launch for", or whenever a project has a validated business model and needs a launch strategy — even if they don't say "GTM" explicitly.
argument-hint: "<project-name> [--model quick|search|deep|reason]"
generated_from: .claude/skills/gtm-plan/SKILL.md
source_sha256: 578ea821b17bc5e3a470e08893bff6fd612c102e185daa9b389dd0c04b0e4bdc
x_generated_note: "do not edit — regenerate with: uv run core/scripts/build_adapters.py"
---

# Go-to-Market Plan

Generate a comprehensive go-to-market strategy for a project, covering ideal customer profile, beachhead segment, positioning, channels, and launch timeline.

## Quick Start

User: `/gtm-plan ad-spend-anomaly-detector`
Result: Reads project context and any existing lean canvas/validation brief, researches GTM approaches via Perplexity, produces a launch strategy, saves to `projects/ad-spend-anomaly-detector/gtm-plan.md`.

## Instructions

### Step 1: Parse Arguments

Check the arguments provided when you were invoked for:
- A required `<project-name>` (the project folder name under `projects/`)
- An optional `--model` flag (`quick`, `search`, `deep`, `reason`)

Default to the `perplexity_ask` tool (perplexity MCP server) if no `--model` flag.

Model flag routing (same as other skills):
- `--model quick` → the `perplexity_ask` tool (perplexity MCP server)
- `--model search` → the `perplexity_search` tool (perplexity MCP server)
- `--model deep` → the `perplexity_research` tool (perplexity MCP server) (set `strip_thinking: true`)
- `--model reason` → the `perplexity_reason` tool (perplexity MCP server) (set `strip_thinking: true`)

If no project name is provided, ask the user which project to plan.

### Step 2: Validate Project Name

**Security check:** Reject any project name containing `..`, `/`, or non-alphanumeric characters besides hyphens.

Check if `projects/<project-name>/` exists. If not, list available projects.

### Step 3: Read Project Context

Read all available project artifacts in order:
1. `projects/<project-name>/idea.md` (required)
2. `projects/<project-name>/prd.md` (if exists)
3. `projects/<project-name>/lean-canvas.md` (if exists — use for segments, channels, pricing)
4. `knowledge/research/projects/<project-name>.md` (if exists — use for competitor data)

If no lean canvas exists, warn: "No lean canvas found. Run `/lean-canvas <project-name>` first for a stronger GTM plan. Proceeding with available context."

### Step 4: Check for Existing Plan

Check if `projects/<project-name>/gtm-plan.md` already exists.

If it does, ask the user: Overwrite or Skip.

### Step 5: GTM Research Call

Call the selected Perplexity tool:

```
For a [product type] targeting [segment from lean canvas or idea.md], research:
(1) Most effective customer acquisition channels for this type of product (organic and paid),
(2) Successful launch strategies used by similar products (Product Hunt, communities, content marketing),
(3) Common pricing and packaging approaches for [market segment],
(4) Growth loops or viral mechanics that work in this space.
Focus on indie/solo launches and bootstrapped products since 2024.
```

### Step 6: Build the GTM Plan

Read the template at `references/gtm-plan-template.md` and fill each section from the project context (Step 3) and the research results (Step 5). The template has 8 sections: ICP, Beachhead, Positioning, Channels, Pricing, Growth Loops, Metrics/Timeline, Risks.

### Step 7: Save the Plan

Save to `projects/<project-name>/gtm-plan.md`.

### Step 8: Update Project Resource Refs

Add `projects/<project-name>/gtm-plan.md` to the idea.md `resource_refs` array.

### Step 8.5: Quality Flags (soft, non-blocking)

After saving, run the 8-item anti-patterns check from
`references/anti-patterns.md` against the plan you just
wrote. Print a structured review in this exact shape:

```
GTM-Plan Review: <project-name>

Completeness: X/8 sections populated
Issues (K):
  1. [#N <name>] <one-line description>. Fix: <specific suggestion>.
  2. [#N <name>] <one-line description>. Fix: <specific suggestion>.
Strengths:
  ✅ <at least one — what the plan does well>
Readiness: Ready for review | Minor gaps | Major gaps
Second-opinion trigger: No | Yes (<reason>)
```

**Readiness rubric (uniform across /prd, /spec, /gtm-plan, /pre-mortem):**
- `Ready for review` — 0 issues
- `Minor gaps` — 1–4 issues
- `Major gaps` — ≥5 issues

**Second-opinion trigger = Yes** if `Major gaps`.

If 0 issues, the Issues block renders `Issues: none`. Always emit at least one
Strength — if nothing stands out, name the single best-filled section.

**Do not block the save.** These are informational — the user decides whether to act on them.

### Step 9: Present Summary

Present:
- The beachhead segment (who to target first)
- Top 2 launch channels
- Pricing recommendation
- First milestone and timeline
- **Readiness verdict from Step 8.5** (Ready for review / Minor gaps / Major gaps)
- Any quality flags from Step 8.5
- Suggested next step with follow-up skill

## Notes

- **Cost:** ~$0.03 (quick) to $0.40 (deep).
- **Best after:** `/lean-canvas` (for segments, pricing, channels) and `/validate-project` (for competitor data). Works standalone with lighter output.
- **Focus:** Optimized for solo/indie launches and bootstrapped products, not enterprise GTM.
