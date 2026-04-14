---
name: plan-okrs
description: >
  Creates or refreshes measurable OKRs (Objectives and Key Results) aligned
  with GOALS.md — converts informal objectives into structured OKRs with
  baselines, targets, and owners, informed by past OKR calibration history.
  Use this skill whenever the user mentions OKRs, quarterly goals, "make my
  goals measurable", "set quarterly goals", "plan OKRs", "create OKRs", when
  GOALS.md has objectives without key results, or during quarterly planning —
  even if they don't use the word "OKR."
allowed-tools: Read Write Edit Glob
argument-hint: "[quarter, e.g. Q2-2026]"
---

# Plan OKRs

Convert informal goals into structured, measurable OKRs with baselines, targets, and tracking.

## Quick Start

User: `/plan-okrs`
Result: Reads GOALS.md, generates 2-3 Objectives with 3-4 Key Results each, presents for review, updates GOALS.md with structured OKR section.

User: `/plan-okrs Q2-2026`
Result: Same, but scoped to a specific quarter.

## Instructions

### Step 1: Parse Arguments

Check `$ARGUMENTS` for an optional quarter identifier (e.g., `Q2-2026`).

If not provided, determine the current quarter from today's date.

### Step 2: Read Current Goals & OKR History

Read `GOALS.md` to extract:
- Professional vision
- 12-month success criteria
- Quarterly objectives (informal)
- Top 3 priorities
- Any existing OKRs (if this is a refresh)

Read `knowledge/reference/okr-history.md` to learn from past quarters:
- Which KR categories consistently hit vs. miss
- Calibration notes (were past targets too ambitious or too easy?)
- Patterns (e.g., "shipping KRs always hit, outreach KRs always miss")

Use this history to set better-calibrated targets. If past outreach KRs missed at 0.3, don't set the same ambitious target — either adjust the target or change the approach.

### Step 3: Read Current State

Gather data for baselining:
- Use Glob for `tasks/*.md` — count by status and priority
- Use Glob for `projects/*/idea.md` — count by project_status
- Check for any `active` projects and their progress
- Look at completed tasks for velocity data

### Step 4: Generate OKRs

Create 2-3 Objectives from the user's goals. Each Objective should:
- Be qualitative and inspiring (not a metric)
- Be achievable in the quarter
- Align directly with the professional vision

For each Objective, create 3-4 Key Results that:
- Are quantitative and measurable
- Have a clear baseline (where are we now?) and target (where do we want to be?)
- Follow the format: "[Verb] [metric] from [baseline] to [target]"
- Are ambitious but achievable (aim for ~70% completion as well-calibrated)

### Step 5: Present for Review

Present the draft OKRs and ask the user to confirm, adjust targets, or reword objectives before saving.

Use this format for presentation:

```
**O1: [Objective]**
  KR1: [Key Result] — Baseline: [X] → Target: [Y]
  KR2: [Key Result] — Baseline: [X] → Target: [Y]
  KR3: [Key Result] — Baseline: [X] → Target: [Y]

**O2: [Objective]**
  ...
```

Ask: "Do these look right? Adjust any targets or wording before I save?"

### Step 6: Write OKRs to GOALS.md

After user confirmation, add or replace the OKR section in GOALS.md:

```markdown
## OKRs — [Quarter]

*Last updated: YYYY-MM-DD*

### O1: [Objective]
| Key Result | Baseline | Target | Current | Status |
|-----------|----------|--------|---------|--------|
| [KR1 description] | [X] | [Y] | [X] | Not started |
| [KR2 description] | [X] | [Y] | [X] | Not started |
| [KR3 description] | [X] | [Y] | [X] | Not started |

### O2: [Objective]
| Key Result | Baseline | Target | Current | Status |
|-----------|----------|--------|---------|--------|
| [KR1 description] | [X] | [Y] | [X] | Not started |
| [KR2 description] | [X] | [Y] | [X] | Not started |
| [KR3 description] | [X] | [Y] | [X] | Not started |

### O3: [Objective]
| Key Result | Baseline | Target | Current | Status |
|-----------|----------|--------|---------|--------|
| [KR1 description] | [X] | [Y] | [X] | Not started |
| [KR2 description] | [X] | [Y] | [X] | Not started |
| [KR3 description] | [X] | [Y] | [X] | Not started |

**Scoring guide:** 0.0-0.3 = red (off track), 0.4-0.6 = yellow (at risk), 0.7-1.0 = green (on track). Target 0.7 average = well-calibrated OKRs.
```

### Step 7: Present Summary

Present:
- Number of Objectives and Key Results created
- The single most important KR to focus on this week
- Suggest: "Your weekly review now tracks OKR progress. Run your morning standup to see today's priorities aligned to these OKRs."

## OKR Quality Checklist

Before saving, verify each OKR against:
- [ ] Objectives are qualitative and inspiring, not metrics
- [ ] Key Results are quantitative with clear numbers
- [ ] Each KR has a realistic baseline (not zero unless truly starting fresh)
- [ ] Targets are ambitious but not impossible (~70% achievable)
- [ ] No more than 3 Objectives (focus beats breadth)
- [ ] No more than 4 KRs per Objective
- [ ] Every KR can be measured without ambiguity
- [ ] OKRs align with the user's 12-month success criteria

## Example OKRs for This User

Based on GOALS.md context:

```
O1: Become a recognized product builder in my space
  KR1: Ship products from 0 to 3 launched MVPs
  KR2: Increase portfolio projects with live demos from 0 to 5
  KR3: Publish technical write-ups from 0 to 4 posts

O2: Build a profitable consulting pipeline
  KR1: Grow inbound leads from 0 to 10 qualified leads
  KR2: Acquire paying clients from 0 to 3
  KR3: Generate consulting revenue from $0 to $X

O3: Develop deep product expertise
  KR1: Complete product projects from 0 to 5 end-to-end builds
  KR2: Evaluate project ideas through full pipeline from 0 to 15 evaluated
  KR3: Kill non-viable projects (decisive focus) from 0 to 5 killed
```

## Notes

- **No external calls:** Works entirely from local files.
- **Refresh cadence:** Re-run monthly to update "Current" column. The weekly review should reference OKRs but not modify them.
- **70% rule:** If all OKRs score 1.0, the targets were too easy. If all score < 0.3, they were unrealistic. Aim for 0.7 average.
- **Killing is a KR:** Including "kill N projects" as a KR is intentional — it rewards decisive focus over idea hoarding.
