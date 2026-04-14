---
name: quarterly
description: Run a 45-minute quarterly review — score OKRs against completion data, purge stale projects, refresh GOALS.md, set new OKRs informed by past calibration, update Claude memories, audit AGENTS.md against the quarter's learnings, and save a quarterly summary. Use this skill whenever the user mentions quarterly review, end of quarter, OKR scoring, planning the next quarter, runs `/quarterly`, or says anything like "how did Q2 go," "time to plan Q3," "score the OKRs," "strategic refresh," or "end-of-quarter reflection." Push toward this at quarter boundaries even if the user doesn't explicitly ask.
allowed-tools: Read Write Edit Glob Bash mcp__manager-ai__* mcp__plugin_slack_slack__*
argument-hint: "[quick]"
---

# Quarterly Review

A 45-minute system-level review covering OKRs, project pipeline health, goals refresh, and system learning.

If the argument is `quick`, condense to: OKR scores, projects to archive, top 3 next quarter priorities.

## Step 1: OKR scoring

Read `GOALS.md`. If OKRs exist, score each Key Result on a 0.0–1.0 scale:

- Read task completion data, pipeline movement, and any available metrics.
- For each KR: `Current / Target = Score`.
- Overall Objective score = average of its KRs.
- Target: 0.7 is well-calibrated (1.0 means goals were too easy).

Present:

```markdown
## Q[X] OKR Results
| Objective | Key Result | Target | Actual | Score |
|-----------|-----------|--------|--------|-------|
| ...       | ...       | ...    | ...    | 0.X   |

Overall: X.XX
```

After scoring, append the full quarter's OKR results to `knowledge/reference/okr-history.md`:

- Scored OKR table
- What Worked (approaches that led to hitting KRs)
- What Missed & Why (root causes for misses)
- Calibration Notes (were targets too ambitious/easy? what to adjust?)
- Update the "Patterns & Learnings" section at the top if new patterns emerge (e.g., "shipping KRs consistently hit, outreach KRs consistently miss")

This history compounds — future `/plan-okrs` runs read it to set better-calibrated targets.

If no OKRs exist: "No OKRs found. Run `/plan-okrs` to make next quarter measurable."

## Step 2: Weekly summary review

Read all weekly summaries from `knowledge/journals/YYYY/weekly/`. Aggregate across the quarter:

- Total tasks completed
- Average weekly completion rate (from plan-vs-actual data)
- Pipeline movement (projects advanced, projects archived)
- Recurring patterns flagged but not addressed
- Skills suggested by weekly reviews

If no weekly summaries exist, note this and skip to Step 3.

## Step 3: Project pipeline purge

Call `mcp__manager-ai__list_projects` to get all projects. Identify:

- Projects at `idea` status for 60+ days with no advancement
- Projects at `evaluating` status for 30+ days with no new artifacts
- Projects at `paused` status for 60+ days

Present candidates for archiving:

```markdown
## Archive Candidates
| Project | Status | Days Stale | Recommendation |
|---------|--------|-----------|----------------|
| ...     | idea   | 90        | Archive        |
| ...     | paused | 75        | Archive or resume |
```

Ask the user to confirm archiving. For confirmed projects, update their `idea.md` `project_status` to `archived` and add a Progress Log entry with the reason.

## Step 4: Prioritize remaining projects

After purging, run `/prioritize` on remaining active pipeline projects (evaluating, ready, active) to re-rank by impact.

## Step 5: Refresh goals

Invoke `/refresh-goals` to update `GOALS.md`:

- Fill any empty sections
- Update quarterly focus for the new quarter
- Verify top 3 priorities still reflect reality
- Update 12-month success criteria if they've shifted

## Step 6: Set new OKRs

Invoke `/plan-okrs` for the upcoming quarter, informed by:

- Last quarter's OKR scores (what was too ambitious, what was too easy)
- Updated goals from Step 5
- Current pipeline state from Steps 3–4

## Step 7: Memory maintenance

Review Claude Code memories:

- Read `MEMORY.md` from this project's memory directory (typically `~/.claude/projects/<encoded-cwd>/memory/MEMORY.md`) and every file it links to
- Flag memories that reference outdated information (old project statuses, completed goals)
- Propose updates or deletions for stale memories
- Save any new quarterly context as project memories

Also scan `knowledge/decisions/` for decisions made this quarter — patterns there often suggest new memories or AGENTS.md rules.

Present: "These memories need updating: [list]. Update them now?"

## Step 8: AGENTS.md audit

Review `AGENTS.md` against the quarter's learnings:

- Are the daily guidance rules still accurate?
- Are the categories still covering the work being done?
- Are there workflow patterns from weekly reviews that should be codified?
- Any rules that were added but haven't been useful?

Propose 0–3 specific AGENTS.md changes. Present for user approval. Never auto-apply.

## Step 9: Quarterly summary

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

## Step 10: Post to Slack (optional)

Ask: "Post quarterly review to #os-progress?"

If yes, format a concise summary: OKR scores, projects shipped/archived, top priorities for next quarter. Post via `mcp__plugin_slack_slack__slack_send_message`. If Slack MCP is unavailable, skip silently.
