#!/usr/bin/env bash
# Initialize a pm-operating-system workspace in the user's project directory.
#
# Runs on every Claude Code SessionStart via hooks.json. Idempotent:
# directories are created with `mkdir -p`, files are only written when missing.
# Exits 0 unconditionally so a hook failure never blocks the session.
#
# Operates against $CLAUDE_PROJECT_DIR — the directory the user opened
# Claude Code in.

set +e  # never block the session on a hook error

if [ -z "$CLAUDE_PROJECT_DIR" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR" || exit 0

# Repo guard: only bootstrap if this looks like a personal-os workspace.
# We require TWO markers to reduce false positives — AGENTS.md alone is too
# generic (other repos use it for agent instructions). .mcp.json AND the
# core/mcp/server.py entry point together are personal-os-specific.
if [ ! -f AGENTS.md ] || [ ! -f .mcp.json ] || [ ! -f core/mcp/server.py ]; then
  exit 0
fi

# ── Workspace directories ──────────────────────────────────────────────

mkdir -p \
  tasks tasks/archive \
  projects \
  knowledge/research/projects \
  knowledge/research/topics \
  knowledge/meetings \
  knowledge/journals \
  knowledge/session-reviews \
  knowledge/decisions \
  knowledge/people \
  knowledge/reference \
  knowledge/voice-samples \
  knowledge/updates \
  knowledge/decks \
  library/prompts \
  library/systems \
  library/skills \
  library/agents \
  library/commands \
  2>/dev/null

# ── BACKLOG.md (capture inbox) ─────────────────────────────────────────

if [ ! -f BACKLOG.md ]; then
  cat > BACKLOG.md <<'EOF'
# Backlog

Drop raw notes, ideas, or todos here. No structure needed — one bullet per item.

When ready, say `/process-backlog` and the assistant will classify each item
into a task or project, check for duplicates, and ask about anything ambiguous.

## Inbox

EOF
fi

# ── GOALS.md (strategic memory) ────────────────────────────────────────

if [ ! -f GOALS.md ]; then
  cat > GOALS.md <<'EOF'
# Goals & Strategic Direction

> This file is your strategic memory. The assistant reads it every session to
> prioritize tasks and suggest what to work on. Run `/refresh-goals` for an
> interactive walkthrough that fills in the empty sections.

## Current Context

### What's your current role?


### What's your primary professional vision? What are you building toward?


## Success Criteria

### In 12 months, what would make you think "this was a successful year"?


### What's your 5-year north star? Where do you want to be?


## Current Focus Areas

### What are you actively working on right now?


### What are your objectives for THIS QUARTER (next 90 days)?


### What skills do you need to develop to achieve your vision?


### What key relationships or network do you need to build?


## Strategic Context

### What's currently blocking you or slowing you down?


### What opportunities are you exploring or considering?


## Priority Framework

When evaluating new tasks and commitments:

**P0 (Critical/Urgent)** — Must do THIS WEEK:
- Directly advances quarterly objectives
- Time-sensitive opportunities
- Critical stakeholder communication
- Immediate blockers to remove

**P1 (Important)** — This month:
- Builds key skills or expertise
- Advances product strategy
- Significant career development
- High-value learning opportunities

**P2 (Normal)** — Scheduled work:
- Supports broader objectives
- Maintains stakeholder relationships
- Operational efficiency
- General learning and exploration

**P3 (Low)** — Nice to have:
- Administrative tasks
- Speculative projects
- Activities without clear advancement value

## Top 3 Priorities Right Now

1.
2.
3.

---

**The assistant uses this document to prioritize tasks and suggest what to work
on each day.** Review and update weekly as priorities shift, or run
`/refresh-goals` for a guided refresh.
EOF
fi

# ── README placeholders so users understand the layout ─────────────────

if [ ! -f tasks/README.md ]; then
  cat > tasks/README.md <<'EOF'
# tasks/

Discrete, actionable items. One markdown file per task.

- **Format:** YAML frontmatter (title, category, priority, status) + Context, Next Actions, Progress Log
- **Status values:** `n` (not_started), `s` (started), `b` (blocked), `d` (done), `r` (recurring)
- **Lifecycle:** New tasks land here from `/process-backlog`. When done, they auto-archive to `tasks/archive/` after 30 days.

Use `/morning` to see the top 5, or ask "what's on my plate?"
EOF
fi

if [ ! -f projects/README.md ]; then
  cat > projects/README.md <<'EOF'
# projects/

Multi-step initiatives and ideas. One folder per project.

- **idea.md** — lightweight capture (created by `/process-backlog`)
- **prd.md** — full Product Requirements Doc (`/prd`)
- **lean-canvas.md** — business model (`/lean-canvas`)
- **gtm-plan.md** — go-to-market strategy (`/gtm-plan`)
- **pre-mortem.md** — risk analysis (`/pre-mortem`)
- **user-stories.md** — buildable stories (`/user-stories`)

Status flow: `idea → evaluating → ready → active → paused/archived`. Use `/launch <project-name>` to run the full evaluation pipeline.
EOF
fi

if [ ! -f knowledge/README.md ]; then
  cat > knowledge/README.md <<'EOF'
# knowledge/

Long-term memory: research, journals, decisions, meetings, people.

- **research/projects/** — `/validate-project` and `/competitive-analysis` output
- **research/topics/** — `/research-topic` briefs
- **journals/YYYY/MM/DD.md** — daily plans (saved by `/morning`)
- **journals/YYYY/weekly/WXX.md** — weekly reviews (`/weekly`)
- **session-reviews/** — `/session-review` artifacts
- **decisions/** — `/decision` records
- **meetings/YYYY/MM/DD.md** — synced from Granola via `/meeting-sync`
- **people/<name>.md** — auto-enriched contact profiles
- **reference/** — stable context (OKR history, system guides)
- **updates/YYYY-WXX[-audience].md** — outbound stakeholder memos (`/weekly-update`)
- **decks/** — rendered slide decks (`/make-slides`)
- **voice-guide.md** + **voice-samples/** — `/write` voice calibration

This folder compounds over time. Weekly and quarterly reviews mine it for patterns.
EOF
fi

exit 0
