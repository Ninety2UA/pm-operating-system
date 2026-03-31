# Weekly Review Workflow

> **Note:** This workflow is now also available as the `/weekly` command, which integrates with the MCP server for structured task and pipeline queries. This file remains as a reference.

A 20-minute session to reflect on progress across execution, pipeline, and OKRs.

## When to Do It

- Friday afternoon (reflect while fresh)
- Sunday evening (prep for the week)
- Monday morning (start week with clarity)

## The Prompts

### Step 1: Review Completed Work

```
What did I accomplish this week?
```

**Three layers of review:**

**Execution Review:**
- List tasks completed this week (status changed to `d`)
- Group by goal alignment
- Note time invested vs. estimated

**Pipeline Review:**
- How many projects moved stages this week?
- Projects validated, lean canvases completed, GTM plans created
- Projects killed (this is a positive metric — decisive focus)

**Sprint Review (if sprint plan exists):**
- Planned items vs. completed items
- Was the sprint goal achieved?
- Velocity data: planned hours vs. actual

**Example response:**

This week you completed 8 tasks and moved 3 projects through the pipeline:

**By Goal Alignment:**
- O1 (Ship products): 4 tasks — data model, CSV parser, basic UI, deploy
- O2 (Build pipeline): 2 tasks — LinkedIn update, partnership email
- Admin: 2 tasks

**Pipeline Movement:**
- Validated: creative-performance-heatmap (Strong market signal)
- Lean Canvas: ad-spend-anomaly-detector (Strong viability)
- Killed: slack-tone-analyzer (Weak business model — saved you ~2 weeks)

**Sprint:** 6/8 planned items completed (75%). Sprint goal partially achieved.

---

### Step 2: Check OKR Progress

```
How am I tracking against my OKRs?
```

If OKRs exist in GOALS.md, update the "Current" column and assess:

| Objective | Key Result | Baseline | Target | Current | Score | Status |
|-----------|-----------|----------|--------|---------|-------|--------|
| O1: Ship products | Products launched | 0 | 5 | 2 | 0.4 | At risk |
| O1: Ship products | Ideas evaluated | 0 | 15 | 8 | 0.53 | On track |
| O1: Ship products | Ideas killed | 0 | 5 | 3 | 0.6 | On track |
| O2: Build pipeline | Clients acquired | 0 | 3 | 1 | 0.33 | At risk |
| O2: Build pipeline | Inbound leads | 0 | 10 | 4 | 0.4 | At risk |

**Overall OKR score: 0.45** (target: 0.7 by end of quarter)

**Recommendations:**
- O1 KR1 (products launched) needs acceleration — activate a ready project this week
- O2 is behind — prioritize client-facing work next week

If no OKRs exist, suggest: "Run `/plan-okrs` to make your quarterly goals measurable."

---

### Step 3: Identify Blockers

```
What's blocked or stalled?
```

**Blocked tasks:**
- Tasks with status `b` and how long they've been blocked
- Suggested unblocking actions

**Stalled projects:**
- Projects that haven't moved pipeline stages in > 2 weeks
- Active projects with no task activity this week

**Pipeline bottlenecks:**
- Many projects stuck at one stage? (e.g., 15 ideas, 0 evaluating)
  → Suggest batch evaluation: "Run `/prioritize` to pick the top 5 to evaluate"

---

### Step 4: Plan Next Week

```
Help me plan next week. What should my top priorities be?
```

**Use `/sprint-plan` for detailed weekly planning.** Quick version:

**Must do (P0/P1):**
1. [Top priority based on OKR gaps]
2. [Unblock stuck items]
3. [Pipeline movement — advance 2-3 projects]

**Should do (P2):**
4. [Next most impactful items]
5. [Maintenance/admin]

**Pipeline targets for next week:**
- Evaluate [N] project ideas
- Complete [N] lean canvases
- Kill or advance [N] projects through pipeline

**Suggested sprint goal:**
> "[One sentence: what will be true at the end of next week?]"

Run `/sprint-plan [hours]` for a full capacity-based plan.

---

### Step 5: Update OKRs (if applicable)

After reviewing, offer to update the "Current" column in GOALS.md OKR tables with this week's actuals.

---

## Quick Version (5 minutes)

If you're short on time:

```
Quick weekly review: What did I finish, what's blocked, what's most important next week?
```

## Follow-up Suggestions

After the weekly review, suggest the most impactful next action:
- If OKRs are behind: "Focus next week's sprint on [specific KR]. Run `/sprint-plan --project [name]`."
- If pipeline is stalled: "Run `/prioritize` to pick top projects, then `/lean-canvas` on the winner."
- If many ideas but no evaluations: "Commit to evaluating 1 project/day this week. Start with `/validate-project [top priority]`."
- If at end of quarter: "Run `/plan-okrs` to set next quarter's objectives based on what you learned."
- If roadmap feels unclear: "Run `/outcome-roadmap --save` to see your work mapped to outcomes."

## Tips

- Block 20 minutes on your calendar for this
- Do it in a quiet space, not between meetings
- Be honest about what's stalled — it's data, not judgment
- Update GOALS.md if priorities have shifted
- The pipeline review is just as important as the task review
