---
description: "Quarterly review — score OKRs, purge stale projects, refresh goals, audit system"
argument-hint: "[quick]"
---

# Quarterly Review

A 45-minute system-level review covering OKRs, project pipeline health, goals refresh, and system learning.

## Instructions

If the argument is "quick", condense to: OKR scores, projects to archive, top 3 next quarter priorities.

### Step 1: OKR Scoring

Read `GOALS.md`. If OKRs exist, score each Key Result on a 0.0-1.0 scale:
- Read task completion data, pipeline movement, and any metrics available
- For each KR: `Current / Target = Score`
- Overall Objective score = average of its KRs
- Target: 0.7 is well-calibrated (1.0 means goals were too easy)

Present:
```
## Q[X] OKR Results
| Objective | Key Result | Target | Actual | Score |
|-----------|-----------|--------|--------|-------|
| ...       | ...       | ...    | ...    | 0.X   |

Overall: X.XX
```

**After scoring, append the full quarter's OKR results to `knowledge/reference/okr-history.md`:**
- Scored OKR table
- What Worked (approaches that led to hitting KRs)
- What Missed & Why (root causes for misses)
- Calibration Notes (were targets too ambitious/easy? what to adjust?)
- Update the "Patterns & Learnings" section at the top if new patterns emerge (e.g., "shipping KRs consistently hit, outreach KRs consistently miss")

This history compounds — future `/plan-okrs` reads it to set better-calibrated targets.

If no OKRs exist: "No OKRs found. Run `/plan-okrs` to make next quarter measurable."

### Step 2: Weekly Summary Review

Read all weekly summaries from `knowledge/journals/YYYY/weekly/`. Aggregate across the quarter:
- Total tasks completed
- Average weekly completion rate (from plan-vs-actual data)
- Pipeline movement (how many projects advanced, how many archived)
- Recurring patterns that were flagged but not addressed
- Commands/skills that were suggested by weekly reviews

If no weekly summaries exist, note this and skip to Step 3.

### Step 3: Project Pipeline Purge

Call `mcp__manager-ai__list_projects` to get all projects. Identify:
- Projects at `idea` status for 60+ days with no advancement
- Projects at `evaluating` status for 30+ days with no new artifacts
- Projects at `paused` status for 60+ days

Present candidates for archiving:
```
## Archive Candidates
| Project | Status | Days Stale | Recommendation |
|---------|--------|-----------|----------------|
| ...     | idea   | 90        | Archive        |
| ...     | paused | 75        | Archive or resume |
```

Ask user to confirm archiving. For confirmed projects, update their idea.md `project_status` to `archived` and add a Progress Log entry with the reason.

### Step 4: Prioritize Remaining Projects

After purging, run `/prioritize` on remaining active pipeline projects (evaluating, ready, active) to re-rank by impact.

### Step 5: Refresh Goals

Invoke `/refresh-goals` to update GOALS.md:
- Fill any empty sections
- Update quarterly focus for the new quarter
- Verify top 3 priorities still reflect reality
- Update 12-month success criteria if they've shifted

### Step 6: Set New OKRs

Invoke `/plan-okrs` for the upcoming quarter, informed by:
- Last quarter's OKR scores (what was too ambitious, too easy)
- Updated goals from Step 5
- Current pipeline state from Step 3-4

### Step 7: Memory Maintenance

Review Claude Code memories:
- Read all memory files from the memory directory
- Flag memories that reference outdated information (old project statuses, completed goals)
- Propose updates or deletions for stale memories
- Save any new quarterly context as project memories

Present: "These memories need updating: [list]. Update them now?"

### Step 8: AGENTS.md Audit

Review AGENTS.md against the quarter's learnings:
- Are the daily guidance rules still accurate?
- Are the categories still covering the work being done?
- Are there workflow patterns from weekly reviews that should be codified?
- Any rules that were added but haven't been useful?

Propose 0-3 specific AGENTS.md changes. Present for user approval. Never auto-apply.

### Step 9: Quarterly Summary

Save the full quarterly review to `knowledge/journals/YYYY/quarterly/QX.md`.

Include:
- OKR scores
- Projects archived and why
- Pipeline health summary
- Goals changes made
- New OKRs set
- AGENTS.md changes accepted
- Memory updates made
- Key learnings from the quarter

### Step 10: Post to Slack (Optional)

Ask: "Post quarterly review to #os-progress?"

If yes, format a concise summary: OKR scores, projects shipped/archived, top priorities for next quarter.
