---
name: discover-ideas
description: >
  Searches the web and social media for project ideas and trending opportunities
  across the user's goal domains. Use this skill whenever the user says "find
  ideas", "discover opportunities", "what should I build", "scan for trends",
  "find trending topics", "I need new ideas", "give me project suggestions",
  mentions feeling stuck for ideas, wants inspiration, asks about market
  trends, or says they want to explore new directions — even if they don't use
  the word "discover". Accepts optional topic argument to narrow focus.
allowed-tools: Read Write Edit Glob mcp__perplexity__*
argument-hint: "[topic] [--model quick|search|deep|reason]"
---

# Discover Ideas

Search the web and social media for project ideas and trending opportunities, then append structured findings to BACKLOG.md.

## Quick Start

User: `/discover-ideas`
Result: Reads GOALS.md, scans 4 domains (SaaS, AI/ML, consulting, Google Ads/UA) via Perplexity, appends 5-10 ideas to BACKLOG.md under `## Project Ideas`.

User: `/discover-ideas "AI agent frameworks"`
Result: Scans specifically for AI agent framework opportunities, appends findings to BACKLOG.md.

## Instructions

### Step 1: Parse Arguments

Check `$ARGUMENTS` for:
- An optional topic string (e.g., "AI agent frameworks")
- An optional `--model` flag (`quick`, `search`, `deep`, `reason`)

If no `--model` flag is provided, default to `mcp__perplexity__perplexity_search`.

Model flag routing:
- `--model quick` → use `mcp__perplexity__perplexity_ask`
- `--model search` → use `mcp__perplexity__perplexity_search`
- `--model deep` → use `mcp__perplexity__perplexity_research` (set `strip_thinking: true`)
- `--model reason` → use `mcp__perplexity__perplexity_reason` (set `strip_thinking: true`)

### Step 2: Determine Search Domains

If a topic was provided, use that as the search focus.

If no topic was provided, read `GOALS.md` and extract the user's current focus areas. Map to these search domains:
- **SaaS / product opportunities** — gaps in the market, underserved niches, trending tools
- **AI/ML trends** — new models, frameworks, techniques, use cases
- **Freelance / consulting** — problems companies are hiring for, pain points on forums
- **Google Ads / UA / performance marketing** — platform changes, industry shifts, new tools

### Step 3: Search via Perplexity

For each domain, call the selected Perplexity MCP tool with keyword-rich queries. Include social platform targeting in queries:

Example queries for `perplexity_search`:
- `"trending SaaS tools for marketing automation 2026 site:producthunt.com"`
- `"new AI agent frameworks 2026 site:reddit.com"`
- `"freelance consulting pain points digital marketing site:indiehackers.com"`
- `"Google Ads automation tools 2026 site:news.ycombinator.com"`

For `perplexity_ask` or `perplexity_research`, use natural language:
- `"What are the most promising SaaS opportunities in marketing technology in 2026? Include discussions from Reddit, Hacker News, and Indie Hackers."`

Do NOT ask for URLs in prompts — they are returned automatically in citations.

### Step 4: Collect and Deduplicate

Gather all results across domains. Remove duplicates or near-duplicates. Select the 5-10 strongest ideas based on signal strength and relevance to the user's goals.

### Step 5: Format and Append to BACKLOG.md

Read `BACKLOG.md`. Find the `## Project Ideas` section. Append a new subsection:

```markdown
### Discovered YYYY-MM-DD
- **Idea name** | Domain: SaaS/AI/Consulting/Marketing | Signal: Reddit r/PPC (12 threads) | Confidence: High/Med/Low
  Brief description of the opportunity and why it's relevant.
```

Write the updated BACKLOG.md.

### Step 6: Present Summary

Tell the user:
- How many ideas were added
- Top 3 most interesting findings with brief highlights
- Suggest: "Run 'process my backlog' to triage these into tasks or projects."

## Example Flow

**User:** `/discover-ideas`

**Claude:**
1. Reads GOALS.md — finds focus on AI skills, shipping products, acquiring clients
2. Searches 4 domains via `perplexity_search` with social targeting
3. Collects 14 raw results, deduplicates to 8 strong ideas
4. Appends to BACKLOG.md under `## Project Ideas > ### Discovered 2026-03-24`

**Claude responds:**
> Added 8 ideas to your backlog under ## Project Ideas.
>
> Top findings:
> - **AI Resume Screener API** — Multiple Reddit threads in r/recruitinghell asking for AI-powered screening. No dominant player yet. (High confidence)
> - **Google Ads Script Marketplace** — HN discussion about lack of curated Ads scripts. Your domain expertise fits. (Medium confidence)
> - **Freelance Proposal Generator** — Indie Hackers threads about proposal automation. Several founders validating the idea. (Medium confidence)
>
> Run "process my backlog" to triage these into tasks or projects.

## Follow-up Suggestions

After presenting results, suggest:
- "Run `process my backlog` to triage these into tasks or projects."
- "Run `/validate-project <top-idea>` to check market viability of the strongest idea."
- "Run `/prioritize` to rank these against your existing project pipeline."

## Notes

- If GOALS.md is empty or has no parseable domains, ask the user what domains to scan.
- If `## Project Ideas` section doesn't exist in BACKLOG.md, create it before appending.
- Results from Perplexity are not verified — treat as signals for exploration, not facts.
- Using `--model deep` changes behavior from broad scanning to fewer, deeper results across fewer domains. Cost is significantly higher (~$0.40 vs ~$0.04).
- Social platform coverage: Reddit and Hacker News have the strongest signal. X/Twitter coverage is weaker. Indie Hackers is good for validation signals.
