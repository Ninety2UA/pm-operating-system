---
name: refresh-goals
description: >
  Reviews and fills gaps in GOALS.md through conversational questions,
  refreshing quarterly focus, top 3 priorities, and 12-month success
  criteria. Use this skill whenever the user says "refresh goals", "my goals
  are stale", "update GOALS.md", "I need to rethink my goals", "quarterly
  goal refresh", "fill in my north star", when GOALS.md has empty sections,
  at the start of a new quarter, or when the user expresses uncertainty
  about direction — even if they don't explicitly ask to refresh goals.
allowed-tools: Read Write Edit
argument-hint: "[--section <section-name>]"
---

# Refresh Goals

Interactively review GOALS.md, identify blank or outdated sections, and fill them through conversation.

## Instructions

### Step 1: Read Current State

Read `GOALS.md`. For each section, check if it's empty or contains only placeholder text.

Track which sections need attention:
- Current Context (role, vision)
- Success Criteria (12-month, 5-year)
- Current Focus Areas (active work, quarterly objectives, skills, relationships)
- Strategic Context (blockers, opportunities)
- Priority Framework (P0-P3 definitions)
- Top 3 priorities

### Step 2: Present Gap Report

Show the user which sections are complete vs. empty:

```
## GOALS.md Health Check

Complete:
- Current role: Product Manager & Data Analyst/Builder
- Vision: Launch successful product + Build thriving consultancy
- 12-month success: [filled]
- Quarterly focus: [filled]
- Priority framework: [filled]
- Top 3 priorities: [filled]

Needs attention:
- 5-year north star: EMPTY
- What you're actively working on: EMPTY
- Skills to develop: EMPTY
- Key relationships to build: EMPTY
- What's blocking you: EMPTY
- Opportunities you're exploring: EMPTY
```

### Step 3: Fill Gaps Conversationally

For each empty section, ask a focused question. Batch related questions together (max 3 at a time).

**5-year north star:**
"Where do you want to be in 5 years? Think big — role, income, reputation, lifestyle."

**Active work:**
"What are you actively working on RIGHT NOW? Not goals — actual current projects and tasks."

**Skills to develop:**
"What skills do you need to develop to hit your 12-month targets? Think about gaps between where you are and where you need to be."

**Key relationships:**
"Who do you need in your network to succeed? Think: mentors, collaborators, potential clients, industry contacts."

**Blockers:**
"What's currently blocking you or slowing you down? Be honest — time, skills, resources, clarity, motivation?"

**Opportunities:**
"What opportunities are you exploring or considering right now? New markets, partnerships, technologies, pivots?"

### Step 4: Update GOALS.md

After getting answers, update GOALS.md with the user's responses. Keep their voice and phrasing — don't rewrite into corporate speak.

Update the "Last updated" date at the top.

### Step 5: Verify Priority Alignment

After filling gaps, check:
- Do the top 3 priorities still align with the updated goals?
- Does the priority framework still make sense with new context?
- Are there obvious gaps between goals and current active work?

If misalignment found, flag it: "Your top 3 priorities mention X, but your active work is focused on Y. Want to adjust?"

### Step 6: Suggest Next Steps

Based on the refreshed goals:
- "Run `/plan-okrs` to create measurable key results for this quarter"
- "Run `/prioritize` to rank your 105+ project ideas against these updated goals"
- "Run `/outcome-roadmap --save` to map projects to your goals"

## Notes

- Run this quarterly, or whenever priorities shift significantly
- Keep answers in the user's own words — don't polish or formalize
- If the user doesn't have an answer for a section, that's fine — note it as "TBD" rather than forcing an answer
- Update the Claude Code memory (`project_system_state.md`) if GOALS.md state changes significantly
