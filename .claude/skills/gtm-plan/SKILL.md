---
name: gtm-plan
description: >
  Creates a Go-to-Market plan for a project — ICP, beachhead segment,
  positioning, channels, launch timeline, and growth loops.
  Use when planning how to launch and sell a product, "go to market plan",
  "how do I launch this", "who should I sell to", "GTM strategy",
  "plan launch for", or when a project has a validated business model
  and needs a launch strategy.
allowed-tools: Read Write Edit Glob mcp__perplexity__*
argument-hint: "<project-name> [--model quick|deep|reason]"
---

# Go-to-Market Plan

Generate a comprehensive go-to-market strategy for a project, covering ideal customer profile, beachhead segment, positioning, channels, and launch timeline.

## Quick Start

User: `/gtm-plan ad-spend-anomaly-detector`
Result: Reads project context and any existing lean canvas/validation brief, researches GTM approaches via Perplexity, produces a launch strategy, saves to `Projects/ad-spend-anomaly-detector/gtm-plan.md`.

## Instructions

### Step 1: Parse Arguments

Check `$ARGUMENTS` for:
- A required `<project-name>` (the project folder name under `Projects/`)
- An optional `--model` flag (`quick`, `search`, `deep`, `reason`)

Default to `mcp__perplexity__perplexity_ask` if no `--model` flag.

Model flag routing (same as other skills):
- `--model quick` → `mcp__perplexity__perplexity_ask`
- `--model search` → `mcp__perplexity__perplexity_search`
- `--model deep` → `mcp__perplexity__perplexity_research` (set `strip_thinking: true`)
- `--model reason` → `mcp__perplexity__perplexity_reason` (set `strip_thinking: true`)

If no project name is provided, ask the user which project to plan.

### Step 2: Validate Project Name

**Security check:** Reject any project name containing `..`, `/`, or non-alphanumeric characters besides hyphens.

Check if `Projects/<project-name>/` exists. If not, list available projects.

### Step 3: Read Project Context

Read all available project artifacts in order:
1. `Projects/<project-name>/idea.md` (required)
2. `Projects/<project-name>/prd.md` (if exists)
3. `Projects/<project-name>/lean-canvas.md` (if exists — use for segments, channels, pricing)
4. `Knowledge/research/projects/<project-name>.md` (if exists — use for competitor data)

If no lean canvas exists, warn: "No lean canvas found. Run `/lean-canvas <project-name>` first for a stronger GTM plan. Proceeding with available context."

### Step 4: Check for Existing Plan

Check if `Projects/<project-name>/gtm-plan.md` already exists.

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

```markdown
---
title: "GTM Plan — [Project Title]"
project: <project-name>
created_date: YYYY-MM-DD
---

# Go-to-Market Plan — [Project Title]

## 1. Ideal Customer Profile (ICP)

**Who:** [Job title, company size, industry]
**Pain:** [The specific problem they're trying to solve]
**Current solution:** [What they use today and why it's insufficient]
**Budget:** [What they currently pay or would pay]
**Where they hang out:** [Communities, forums, events, publications]

## 2. Beachhead Segment

The first, narrowest segment to win completely before expanding.

**Segment:** [e.g., "Solo Google Ads consultants managing 5-20 accounts"]
**Why them first:**
- Burning pain: [Why this problem is acute for them]
- Reachable: [How you can access them directly]
- Willingness to pay: [Evidence they'll pay for a solution]
- Word-of-mouth potential: [Why they'll tell others]

**Size estimate:** [Rough TAM for this segment]

## 3. Positioning

**Category:** [What market category does this compete in?]
**For** [target segment] **who** [have this problem],
**[product name]** is a [product category]
**that** [key benefit].
**Unlike** [primary alternative],
**we** [key differentiator].

**Key messages (by audience):**
| Audience | Message | Channel |
|----------|---------|---------|
| [Early adopters] | [Technical value prop] | [Where to say it] |
| [Decision makers] | [Business value prop] | [Where to say it] |
| [End users] | [Ease/speed value prop] | [Where to say it] |

## 4. Channel Strategy

### Pre-launch (Weeks -4 to 0)
- [ ] [Build waitlist / landing page]
- [ ] [Seed content in target communities]
- [ ] [Reach out to N potential beta users]
- [ ] [Prepare launch assets]

### Launch (Week 0)
- [ ] [Primary launch channel — e.g., Product Hunt, HN Show, community post]
- [ ] [Secondary channels — social, newsletter, cross-posts]
- [ ] [Direct outreach to ICP list]

### Post-launch (Weeks 1-8)
- [ ] [Content marketing cadence]
- [ ] [Community engagement plan]
- [ ] [Paid acquisition experiments (if budget)]
- [ ] [Partnership/integration opportunities]

## 5. Pricing & Packaging

**Model:** [From lean canvas or researched]
**Tiers:**
| Tier | Price | Includes | Target |
|------|-------|----------|--------|
| Free | $0 | [Limited features] | [Lead gen / activation] |
| Pro | $X/mo | [Full features] | [Power users] |
| Team | $Y/mo | [Collaboration] | [Teams] |

**Launch pricing:** [Any introductory offers, lifetime deals, early-bird pricing]

## 6. Growth Loops

**Primary loop:** [The main mechanism for sustainable growth]
```
[User action] → [Value created] → [New user attracted] → [Repeat]
```

**Secondary loops:**
- [Content loop: User creates → shares → attracts → converts]
- [Integration loop: User connects → data flows → team adopts]
- [Community loop: User asks → gets helped → helps others → community grows]

## 7. Success Metrics & Timeline

| Milestone | Target | Timeframe |
|-----------|--------|-----------|
| Landing page live | - | Week -4 |
| Beta users onboarded | [N] users | Week -2 |
| Public launch | - | Week 0 |
| First paying customer | $1 revenue | Week 2 |
| Product-market fit signal | [metric] | Week 8 |
| Break-even | $X MRR | Month [N] |

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| [Nobody signs up] | High | [Pre-validate with landing page test] |
| [Free users don't convert] | Medium | [Tighten free tier, add conversion triggers] |
| [Competitor launches similar] | Medium | [Speed to market, niche deeper] |

---

**Suggested next step:** Run `/pre-mortem <project-name>` to stress-test risks, or `/user-stories <project-name>` to decompose into buildable stories.
```

### Step 7: Save the Plan

Save to `Projects/<project-name>/gtm-plan.md`.

### Step 8: Update Project Resource Refs

Add `Projects/<project-name>/gtm-plan.md` to the idea.md `resource_refs` array.

### Step 9: Present Summary

Present:
- The beachhead segment (who to target first)
- Top 2 launch channels
- Pricing recommendation
- First milestone and timeline
- Suggested next step with follow-up skill

## Notes

- **Cost:** ~$0.03 (quick) to $0.40 (deep).
- **Best after:** `/lean-canvas` (for segments, pricing, channels) and `/validate-project` (for competitor data). Works standalone with lighter output.
- **Focus:** Optimized for solo/indie launches and bootstrapped products, not enterprise GTM.
