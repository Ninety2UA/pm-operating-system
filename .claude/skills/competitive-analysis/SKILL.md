---
name: competitive-analysis
description: >
  Performs deep competitive analysis for a project — maps competitor landscape,
  feature comparison matrix, pricing analysis, strengths/weaknesses, and
  differentiation strategy. Use this skill whenever the user mentions
  competitors, market positioning, differentiation, "analyze competitors",
  "competitive analysis", "who are the competitors", "competitive landscape",
  "how do I differentiate", "who else is doing this", "battlecards", or is
  deciding positioning for a project — even if they just say "look into the
  competition."
allowed-tools: Read Write Edit Glob mcp__perplexity__*
argument-hint: "<project-name> [--model quick|search|deep|reason]"
---

# Competitive Analysis

Map the competitive landscape for a project with feature comparisons, pricing analysis, and differentiation strategy.

## Quick Start

User: `/competitive-analysis ad-spend-anomaly-detector`
Result: Researches competitors, builds feature matrix, analyzes pricing, identifies differentiation opportunities, saves to `knowledge/research/projects/<name>-competitors.md`.

## Instructions

### Step 1: Parse Arguments

Check `$ARGUMENTS` for:
- A required `<project-name>`
- An optional `--model` flag (`quick`, `search`, `deep`, `reason`)

Default to `mcp__perplexity__perplexity_research` (deep) — competitive analysis needs depth.

Model flag routing:
- `--model quick` → `mcp__perplexity__perplexity_ask`
- `--model search` → `mcp__perplexity__perplexity_search`
- `--model deep` → `mcp__perplexity__perplexity_research` (set `strip_thinking: true`)
- `--model reason` → `mcp__perplexity__perplexity_reason` (set `strip_thinking: true`)

### Step 2: Validate Project Name

**Security check:** Reject names containing `..`, `/`, or non-alphanumeric characters besides hyphens.

Check if `projects/<project-name>/` exists.

### Step 3: Read Project Context

Read available project artifacts:
1. `projects/<project-name>/idea.md`
2. `projects/<project-name>/prd.md` (if exists)
3. `projects/<project-name>/lean-canvas.md` (if exists)
4. `knowledge/research/projects/<project-name>.md` (if exists — reuse competitor data)

Extract: product concept, target segment, key features, and any known competitors.

### Step 4: Check for Existing Analysis

Check if `knowledge/research/projects/<project-name>-competitors.md` exists.

If it does, ask: Overwrite or Skip.

### Step 5: Competitor Research

**Call 1 — Competitor Discovery:**
```
Find all products and tools that compete with "[project concept: 2-sentence summary]".
Include: (1) direct competitors with similar features, (2) indirect competitors solving
the same problem differently, (3) potential competitors (companies that could easily
add this feature). For each, provide: name, URL, pricing, target audience, key features,
and year founded/launched. Focus on products active since 2024.
```

**Call 2 — Feature & Pricing Deep Dive:**
```
For these competitors in the [market segment] space: [list top 5-8 from Call 1].
Compare: (1) feature sets — what does each include and exclude,
(2) pricing tiers and models, (3) user reviews and common complaints,
(4) recent product updates or pivots. Include data from G2, Capterra,
Product Hunt, and user forums.
```

Use `perplexity_ask` with `search_domain_filter: ["g2.com", "capterra.com", "producthunt.com"]` for Call 2 if the primary model is `perplexity_research`.

### Step 6: Build the Analysis

Read the template at `.claude/skills/competitive-analysis/references/competitive-analysis-template.md` and fill each section from the competitor research in Step 5 — it defines the full analysis structure (market landscape, competitor map, feature matrix, deep dives, pricing analysis, gaps, differentiation strategy, and battlecard).

### Step 7: Save the Analysis

Ensure `knowledge/research/projects/` directory exists (create with `mkdir -p` if needed).

Save to `knowledge/research/projects/<project-name>-competitors.md`.

### Step 8: Update Project Resource Refs

Add the analysis path to idea.md `resource_refs`.

### Step 9: Present Summary

Present:
- Number of competitors identified (direct, indirect, potential)
- Top competitive threat and why
- Biggest gap/opportunity found
- Differentiation recommendation
- Suggested next step

## Notes

- **Cost:** ~$0.40-0.60 (default deep, two calls). Use `--model quick` for ~$0.05.
- **Complement to /validate-project:** Validation does broad market research; this does deep competitive focus. Use both for full picture.
- **Battlecard:** The battlecard section is designed for consulting pitches and sales conversations.
- **Citation accuracy:** Perplexity citations are ~37% inaccurate. For pricing data, verify manually before making business decisions.
