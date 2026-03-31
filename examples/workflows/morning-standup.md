# Morning Standup Workflow

A 5-minute check-in to set your daily focus across execution and pipeline movement.

## The Prompt

```
What should I work on today?
```

## What This Workflow Covers

The morning standup has three layers:

### Layer 1: Execution Tasks (from Tasks/)

Pull the top 3 priority tasks (P0/P1, status `n` or `s`). For each, show:
- Priority and estimated time
- Goal alignment (which OKR or GOALS.md objective it advances)
- Any blockers

### Layer 2: Pipeline Movement (from Projects/)

Check all projects and suggest **one project to advance** through the evaluation pipeline today. This is the daily 15-minute evaluation habit.

Pipeline stages and the next skill to run:
- `idea` with no validation → suggest `/validate-project <name>`
- `idea` with validation but no lean canvas → suggest `/lean-canvas <name>`
- `evaluating` with lean canvas but no competitive analysis → suggest `/competitive-analysis <name>` (optional)
- `evaluating` with lean canvas but no GTM plan → suggest `/gtm-plan <name>`
- `evaluating` with GTM plan but no pre-mortem → suggest `/pre-mortem <name>` (moves to `ready`)
- `ready` with pre-mortem but no user stories → suggest `/user-stories <name>`
- `active` with no tasks in Tasks/ → flag for decomposition via `/user-stories <name> --tasks`

Pick the highest-priority project that needs the least work to advance.

### Layer 3: OKR Check (from GOALS.md)

If OKRs exist in GOALS.md, briefly note which OKR today's suggested tasks advance. Flag if today's work doesn't move any OKR needle.

## Example Conversation

**You:** What should I work on today?

**Claude:**

**Today's Focus**

*Execution (from Tasks/):*
1. **[P0] Finish LinkedIn update** (60 min) — Supports O2: Build consulting pipeline
2. **[P1] Creative analytics data model** (90 min) — Supports O1: Ship products
3. **[P1] Reply to partnership inquiry** (15 min) — Supports O2: Acquire clients

*Pipeline Movement (15 min):*
- **ad-spend-anomaly-detector** has a completed lean canvas (Strong viability)
  → Next step: `/gtm-plan ad-spend-anomaly-detector` to plan your launch

*OKR Progress:*
- O1 (Ship products): KR1 at 2/5 shipped — today's data model task advances this
- O2 (Build pipeline): KR2 at 1/3 clients — LinkedIn + reply advance this

*Blocked:* "API integration spec" — waiting on engineering estimates (5 days). Follow up today?

Want me to help you get started on any of these?

---

## Variations

### When You're Overwhelmed

```
I'm overwhelmed. What's the ONE thing I should focus on?
```

### When You Have Limited Time

```
I only have 2 hours before meetings. What can I realistically finish?
```

### When You Need Context

```
Remind me what I was working on yesterday and what's next.
```

### When You Want to Focus on Pipeline

```
Which project should I evaluate today?
```

### When You Want Sprint Context

```
What's left in my sprint this week?
```

## Follow-up Suggestions

After presenting the standup, always suggest one natural next action:
- If no sprint plan exists for this week: "Run `/sprint-plan` to plan your week."
- If no OKRs exist: "Run `/plan-okrs` to make your goals measurable."
- If many projects are stuck at `idea`: "Run `/prioritize` to rank your project ideas."
- If a project just completed evaluation: "Run `/user-stories <name> --tasks` to start building."

## Tips

- Do this first thing, before checking email/Slack
- Keep it under 5 minutes — pick and start
- The pipeline movement suggestion is optional but builds momentum over time
- If you're stuck deciding, ask Claude to pick for you
