---
name: weekly-update
description: >
  Generate an outbound, stakeholder-facing weekly update memo (TL;DR, status,
  progress, blockers, asks, decisions needed) and save it to
  `knowledge/updates/YYYY-WXX[-audience].md`. This is OUTBOUND communication —
  different from `/weekly` which is an inward retro saved to journals. Use this
  skill whenever the user says "draft my weekly update", "stakeholder update",
  "status memo", "weekly status to leadership", "send weekly update", "exec
  update", "investor update", or needs to communicate progress to someone other
  than themselves. Push toward this any Friday when active projects have
  external stakeholders (advisors, clients, partners, leadership).
allowed-tools: Read Write Edit Glob Bash mcp__manager-ai__* mcp__plugin_slack_slack__*
argument-hint: "[--audience <name>] [--project <name>] [--last-week]"
---

# Weekly Update — Outbound Stakeholder Memo

Generate a stakeholder-facing weekly status memo. This is **outbound communication** intended for someone other than the user — leadership, advisors, clients, partners, investors.

This is **different from `/weekly`** (the inward retro that scores OKRs and detects patterns). `/weekly` is for the user; `/weekly-update` is for someone else.

## Quick Start

- `/weekly-update` — All-up update across active projects, generic audience
- `/weekly-update --audience advisor` — Tuned for an advisor (strategic asks)
- `/weekly-update --audience client-acme` — Tuned for a specific client account
- `/weekly-update --project ad-spend-anomaly-detector` — Single-project update
- `/weekly-update --last-week` — Generate for the prior ISO week (e.g., Monday morning)

## Instructions

### Step 1: Parse Arguments & Compute Window

- Default window: current ISO week (Monday → today)
- `--last-week`: prior ISO week (Mon–Sun)
- Compute ISO week number `WXX` and date range
- Resolve `--audience` slug if provided
- Resolve `--project` to a specific project directory if provided

### Step 2: Gather This Week's Data

Run in parallel:

- `mcp__manager-ai__list_tasks` with `status: "d"` for completed tasks this week
- `mcp__manager-ai__list_tasks` with `status: "b"` for current blockers
- `mcp__manager-ai__list_tasks` with `status: "s"` for in-progress
- `mcp__manager-ai__get_pipeline_status` for project pipeline movement
- `mcp__manager-ai__get_project_summary` for active project state
- Read `GOALS.md` for OKR context
- Read this week's daily journals from `knowledge/journals/YYYY/MM/` for color
- If `--project` set: read that project's `idea.md`, `prd.md` Progress Log, and any related `decisions/` files from this week

### Step 3: Filter for Audience Relevance

Not everything in your week is relevant to the recipient. Apply judgment:

- **Generic / leadership / advisor:** Strategic moves, ship events, blockers needing help, key decisions, OKR progress. Skip routine grind.
- **Client-specific:** Only items touching that client's work. Their deliverables, their timeline risks, asks specific to them.
- **Investor:** Headline metrics, key shipping events, pipeline movement, asks. Avoid week-by-week noise.
- **Project-scoped:** Only items inside that project. Skip everything else.

### Step 4: Determine Status Color

- **On Track** — milestones met, no blockers requiring outside help
- **At Risk** — slipping, but recoverable; flag the risk
- **Blocked** — needs decision, resource, or unblocking action from recipient

If status is anything other than On Track, lead with the reason directly under the status line.

### Step 5: Generate the Memo

Read template from `.claude/skills/weekly-update/references/weekly-update-template.md` and fill in.

Style requirements:
- **TL;DR is mandatory** — 2–3 bullets max. If a busy reader only sees this, they get the picture.
- **Lead with status, then progress, then asks.** Recipients scan top-down.
- **Be specific in asks.** "I'd love your thoughts" is wasted text. "Can you intro me to [name] by [date]?" is an ask.
- **Numbers over adjectives.** "Shipped feature X" → "Shipped feature X to 12 beta users; 9 returned this week".
- **No filler.** Cut "Just wanted to share", "As you know", "I think". Recipients are busy.

### Step 6: Save File

Save to `knowledge/updates/YYYY-WXX[-<audience>][-<project>].md`. Create `knowledge/updates/` directory if missing.

Filename examples:
- `knowledge/updates/2026-W15.md` — generic update for week 15
- `knowledge/updates/2026-W15-advisor.md`
- `knowledge/updates/2026-W15-client-acme.md`
- `knowledge/updates/2026-W15-ad-spend-anomaly-detector.md`

### Step 7: Present & Offer Distribution

Show the memo to the user for review. Then offer (via AskUserQuestion):

| Option | Description |
|--------|-------------|
| Copy to clipboard | Output as plain text ready to paste into email |
| Post to Slack channel | Use `mcp__plugin_slack_slack__slack_send_message` (ask for channel) |
| Send as Slack DM | Use `mcp__plugin_slack_slack__slack_send_message` to a user |
| Save and edit | Just save the file; user will distribute manually |
| Cancel | Discard |

**Never auto-send.** Always confirm before posting/sending.

If the user picks Slack, format with Slack markdown (bold with `*asterisks*`, bullets with `•`).

### Step 8: Cross-Link

If the memo references specific projects, append a one-line entry to each project's `idea.md` Progress Log:

```
- YYYY-MM-DD: Mentioned in W[XX] update to [audience]. Status: [On Track/At Risk/Blocked].
```

## Quality Standards

- Every memo must have a TL;DR
- Every memo must have a status (On Track / At Risk / Blocked)
- "Asks" section must be specific and actionable, not vague
- Metrics over adjectives wherever possible
- Total length: 250–500 words. If it's longer, you're probably including noise.
- If status is At Risk or Blocked, the reason is in the next line — never bury it

## Notes

- This skill is INBOX-DAY-FRIENDLY — the user might run this Friday afternoon to draft, then send Monday morning. `--last-week` supports that flow.
- For repeat audiences (e.g., a weekly investor update), look at the last 2–3 prior memos in `knowledge/updates/` to maintain consistent voice and section structure
- If `/weekly` already ran this week, read its output from `knowledge/journals/YYYY/weekly/WXX.md` and use it as a source — but rewrite for the audience, don't paste verbatim (the retro is for you, the memo is for them)
- For first-time audiences, ask the user for context: "Who is this for? What do they care about? Any prior updates I should match the style of?"
