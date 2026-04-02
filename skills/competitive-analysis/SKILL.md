---
name: competitive-analysis
description: >
  Performs deep competitive analysis for a project — maps competitor landscape,
  feature comparison matrix, pricing analysis, strengths/weaknesses, and
  differentiation strategy. Use when entering a market, "analyze competitors",
  "competitive analysis", "who are the competitors", "competitive landscape",
  "how do I differentiate", or when deciding positioning for a project.
allowed-tools: Read Write Edit Glob Bash mcp__perplexity__*
disable-model-invocation: true
argument-hint: "<project-name> [--model quick|deep|reason]"
---

# Competitive Analysis

Map the competitive landscape for a project with feature comparisons, pricing analysis, and differentiation strategy.

## Quick Start

User: `/competitive-analysis ad-spend-anomaly-detector`
Result: Researches competitors, builds feature matrix, analyzes pricing, identifies differentiation opportunities, saves to `Knowledge/research/projects/<name>-competitors.md`.

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

Check if `Projects/<project-name>/` exists.

### Step 3: Read Project Context

Read available project artifacts:
1. `Projects/<project-name>/idea.md`
2. `Projects/<project-name>/prd.md` (if exists)
3. `Projects/<project-name>/lean-canvas.md` (if exists)
4. `Knowledge/research/projects/<project-name>.md` (if exists — reuse competitor data)

Extract: product concept, target segment, key features, and any known competitors.

### Step 4: Check for Existing Analysis

Check if `Knowledge/research/projects/<project-name>-competitors.md` exists.

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

```markdown
---
title: "Competitive Analysis — [Project Title]"
project: <project-name>
created_date: YYYY-MM-DD
competitors_analyzed: [N]
---

# Competitive Analysis — [Project Title]

## Market Landscape

**Market category:** [What category does this compete in?]
**Market maturity:** [Emerging / Growing / Mature / Declining]
**Estimated market size:** [If data available]

### Competitor Map

| Competitor | Type | Target | Pricing | Founded | Funding |
|-----------|------|--------|---------|---------|---------|
| [Name] | Direct | [Who they serve] | [$/mo] | [Year] | [Bootstrap/Funded] |
| [Name] | Indirect | [Who they serve] | [$/mo] | [Year] | [Bootstrap/Funded] |
| [Name] | Potential | [Who they serve] | [$/mo] | [Year] | [Bootstrap/Funded] |

## Feature Comparison Matrix

| Feature | [Your Project] | [Competitor 1] | [Competitor 2] | [Competitor 3] |
|---------|:---:|:---:|:---:|:---:|
| [Feature 1] | Planned | Yes | Yes | No |
| [Feature 2] | Planned | No | Yes | Yes |
| [Feature 3] | Planned | No | No | No |
| **Price** | [Target] | [$X] | [$Y] | [$Z] |

**Legend:** Yes = has feature, No = missing, Partial = limited version, Planned = in your roadmap

## Competitor Deep Dives

### [Competitor 1 Name]
- **What they do well:** [Specific strengths]
- **Where they fall short:** [User complaints, missing features, bad UX]
- **User sentiment:** [Summary from reviews/forums]
- **Threat level:** [High/Medium/Low] — [Why]

### [Competitor 2 Name]
...

## Pricing Analysis

| Tier | [Comp 1] | [Comp 2] | [Comp 3] | Your Opportunity |
|------|----------|----------|----------|------------------|
| Free | [What's included] | [What's included] | [What's included] | [Your angle] |
| Mid | [$X — features] | [$Y — features] | [$Z — features] | [Your angle] |
| Enterprise | [$X — features] | [$Y — features] | [$Z — features] | [Your angle] |

**Pricing insight:** [Where is the market over/under-priced? What pricing model is underserved?]

## Gaps & Opportunities

| Gap | Evidence | Your Advantage |
|-----|----------|---------------|
| [Unserved need] | [Forum threads, complaints, missing features] | [How you can fill it] |
| [Underserved segment] | [Who competitors ignore] | [Why you can serve them] |
| [UX/DX gap] | [Common complaint] | [Your approach] |

## Differentiation Strategy

**Primary differentiator:** [The one thing that makes your project fundamentally different]
**Positioning:** "Unlike [main competitor], [your project] [key difference] for [target segment]"

**Moat-building opportunities:**
1. [How to build defensibility over time]
2. [Network effects, data advantages, community, integrations]

## Battlecard (Sales-Ready Summary)

### When a prospect mentions [Competitor 1]:
- **They say:** "[Competitor's pitch]"
- **You say:** "[Your counter-positioning]"
- **Proof point:** "[Evidence of your advantage]"

### When a prospect mentions [Competitor 2]:
...

---

**Suggested next step:** Run `/gtm-plan <project-name>` to plan your launch positioning, or update your `/lean-canvas` with these competitive insights.
```

### Step 7: Save the Analysis

Ensure `Knowledge/research/projects/` directory exists (create with `mkdir -p` if needed).

Save to `Knowledge/research/projects/<project-name>-competitors.md`.

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
