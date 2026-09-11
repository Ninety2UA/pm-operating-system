---
name: discover-ideas
description: |-
  Searches the web and social media for project ideas and trending opportunities across the user's goal domains. Use this skill whenever the user says "find ideas", "discover opportunities", "what should I build", "scan for trends", "find trending topics", "I need new ideas", "give me project suggestions", mentions feeling stuck for ideas, wants inspiration, asks about market trends, or says they want to explore new directions — even if they don't use the word "discover". Accepts optional topic argument to narrow focus. Also use when the user brings one specific idea and asks whether to capture it, scope it, or evaluate it — the skill opens with a spike / bounded / architectural triage that lets small ideas skip the pipeline.
argument-hint: "[topic] [--model quick|search|deep|reason]"
generated_from: .claude/skills/discover-ideas/SKILL.md
source_sha256: 9315288b221ee781b8c93483e026088aaa1bdef0bb9b42812522d29a871ab9fb
x_generated_note: "do not edit — regenerate with: uv run core/scripts/build_adapters.py"
---

# Discover Ideas

Search the web and social media for project ideas and trending opportunities, then append structured findings to BACKLOG.md.

## Quick Start

User: `/discover-ideas`
Result: Reads GOALS.md, scans 4 domains (SaaS, AI/ML, consulting, Google Ads/UA) via Perplexity, appends 5-10 ideas to BACKLOG.md under `## Project Ideas`.

User: `/discover-ideas "AI agent frameworks"`
Result: Scans specifically for AI agent framework opportunities, appends findings to BACKLOG.md.

User: `/discover-ideas "a Google Ads script that pauses campaigns when a landing page returns 5xx"`
Result: No scan. Triaged as a **spike**; after the owner approves, one line is appended to BACKLOG.md and the skill stops.

## Instructions

### Step 1: Triage the entry (three paths)

Decide what the owner brought before touching any file.

- **No idea in hand** (bare invocation, or a domain or trend phrase to scan): continue to Step 2 and run the scan. The triage below applies again in Step 7 to any finding the owner wants to act on.
- **An idea in hand** (the argument or the conversation describes a specific thing to build, try, or change): classify it on one of three paths, and say which path you picked and why.

| Path | Fits when | Write | Then |
|---|---|---|---|
| **Spike** | Single outcome, testable in under ~2 hours, or a hunch with no scope yet | One line under `## Project Ideas` in `BACKLOG.md` (idea, why, signal) | Stop. No idea.md, no research. |
| **Bounded** | Clear scope and a known user, more than one sitting of work, no open market question | `projects/<slug>/idea.md` only (Context, Scope, Progress Log per the project template; `project_status: idea`) | Stop. The PRD and every later artifact wait for `/process-backlog` or `/launch`. |
| **Architectural** | New product line, new market, or anything that would change `GOALS.md` or an OKR | Nothing here | Hand off to the full pipeline: `/process-backlog` creates the project and its PRD, then `/launch <slug>` runs the gates. |

Every path ends the same way: present the path, the exact file and the lines you intend to write, and wait for the owner's approval. Nothing is written — not even the one backlog line — before a yes. A path is a proposal, not a verdict: if the owner disagrees, reclassify and present again. When you cannot tell an idea from a scan topic, ask one question instead of guessing. (RW-2026-09-11-19)

### Step 2: Parse Arguments

Check the arguments provided when you were invoked for:
- An optional topic string (e.g., "AI agent frameworks")
- An optional `--model` flag (`quick`, `search`, `deep`, `reason`)

If no `--model` flag is provided, default to the `perplexity_search` tool (perplexity MCP server).

Model flag routing:
- `--model quick` → use the `perplexity_ask` tool (perplexity MCP server)
- `--model search` → use the `perplexity_search` tool (perplexity MCP server)
- `--model deep` → use the `perplexity_research` tool (perplexity MCP server) (set `strip_thinking: true`)
- `--model reason` → use the `perplexity_reason` tool (perplexity MCP server) (set `strip_thinking: true`)

### Step 3: Determine Search Domains

If a topic was provided, use that as the search focus.

If no topic was provided, read `GOALS.md` and extract the user's current focus areas. Map to these search domains:
- **SaaS / product opportunities** — gaps in the market, underserved niches, trending tools
- **AI/ML trends** — new models, frameworks, techniques, use cases
- **Freelance / consulting** — problems companies are hiring for, pain points on forums
- **Google Ads / UA / performance marketing** — platform changes, industry shifts, new tools

### Step 4: Search via Perplexity

For each domain, call the selected Perplexity MCP tool with keyword-rich queries. Include social platform targeting in queries:

Example queries for `perplexity_search`:
- `"trending SaaS tools for marketing automation 2026 site:producthunt.com"`
- `"new AI agent frameworks 2026 site:reddit.com"`
- `"freelance consulting pain points digital marketing site:indiehackers.com"`
- `"Google Ads automation tools 2026 site:news.ycombinator.com"`

For `perplexity_ask` or `perplexity_research`, use natural language:
- `"What are the most promising SaaS opportunities in marketing technology in 2026? Include discussions from Reddit, Hacker News, and Indie Hackers."`

Do NOT ask for URLs in prompts — they are returned automatically in citations.

### Step 5: Collect and Deduplicate

Gather all results across domains. Remove duplicates or near-duplicates. Select the 5-10 strongest ideas based on signal strength and relevance to the user's goals.

### Step 6: Format and Append to BACKLOG.md

Read `BACKLOG.md`. Find the `## Project Ideas` section. Append a new subsection:

```markdown
### Discovered YYYY-MM-DD
- **Idea name** | Domain: SaaS/AI/Consulting/Marketing | Signal: Reddit r/PPC (12 threads) | Confidence: High/Med/Low
  Brief description of the opportunity and why it's relevant.
```

Write the updated BACKLOG.md.

### Step 7: Present Summary

Tell the user:
- How many ideas were added
- Top 3 most interesting findings with brief highlights
- Suggest: "Run 'process my backlog' to triage these into tasks or projects."
- Offer the Step 1 triage for any finding the owner wants to act on now: spike (it is already a backlog line — nothing more), bounded (write its idea.md after approval), or architectural (hand off to the pipeline).

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
- "Want any of these triaged now? Spike stays a backlog line, bounded gets an idea.md, architectural goes to the pipeline."
- "Run `/validate-project <top-idea>` to check market viability of the strongest idea."
- "Run `/prioritize` to rank these against your existing project pipeline."

## Notes

- If GOALS.md is empty or has no parseable domains, ask the user what domains to scan.
- If `## Project Ideas` section doesn't exist in BACKLOG.md, create it before appending.
- Results from Perplexity are not verified — treat as signals for exploration, not facts.
- Using `--model deep` changes behavior from broad scanning to fewer, deeper results across fewer domains. Cost is significantly higher (~$0.40 vs ~$0.04).
- Social platform coverage: Reddit and Hacker News have the strongest signal. X/Twitter coverage is weaker. Indie Hackers is good for validation signals.
