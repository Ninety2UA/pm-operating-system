@AGENTS.md

## Commands

- `/morning [quick]` — Morning standup with meeting sync, tasks, pipeline, OKRs, journal save
- `/weekly [quick]` — Weekly review with plan-vs-actual analysis, session pattern detection, learning extraction
- `/quarterly [quick]` — Quarterly review: OKR scoring, project purge, goals refresh, system audit
- `/process-backlog` — Process BACKLOG.md with duplicate detection
- `/write <content-type> <topic>` — Generate content in your authentic voice
- `/launch <project-name> [--from <stage>]` — Full evaluation pipeline with Go/No-Go gates
- `/analyze <github-url or local-path>` — Deep compatibility analysis of an external repo against our system

## Skills

Every skill listed here is invokable as `/<skill-name>` (skill-as-command convention). The `## Commands` section above highlights the primary daily workflows — they're skills too.

- **prd** — Generate Product Requirements Document for a project
- **spin-up** — Scaffold a project's CLAUDE.md (artifact links, stage, recommended skills, context-mgmt rule)
- **meeting-sync** — Sync Granola meetings to knowledge/meetings
- **meeting-prep** — Pre-meeting context gathering from People, transcripts, and tasks
- **log-meeting** — Manual meeting note artifact (1on1 / interview / one-off / standup) for non-Granola meetings
- **weekly-update** — Outbound stakeholder weekly memo (different from `/weekly` internal retro)
- **make-slides** — Build 1920x1080 HTML/CSS slides with Playwright render loop; optional `--google-slides` push via gws CLI
- **validate-project** — Market research and validation brief
- **lean-canvas** — Business model evaluation
- **competitive-analysis** — Competitor landscape mapping
- **gtm-plan** — Go-to-market strategy
- **pre-mortem** — Risk analysis before building
- **spec** — Synthesize PRD + project artifacts into a comprehensive 23-section technical design spec
- **user-stories** — Decompose PRD into buildable stories
- **sprint-plan** — Weekly capacity-based sprint planning
- **plan-okrs** — Create measurable OKRs
- **outcome-roadmap** — Outcome-focused project roadmap
- **prioritize** — Rank projects with ICE/RICE frameworks
- **discover-ideas** — Scan for project opportunities
- **research-topic** — Deep research briefs
- **ab-test** — Statistical A/B test analysis
- **session-review** — Capture session learnings, prompts, and patterns for weekly analysis
- **refresh-goals** — Review and fill gaps in GOALS.md through conversation
- **decision** — Structured decision record with options, rationale, and follow-ups
- **morning**, **weekly**, **quarterly**, **process-backlog**, **write**, **launch** — listed in `## Commands` above

## Agents

- **deep-research** — Background multi-source research, saves briefs to knowledge/
- **batch-evaluator** — Parallel project evaluation with comparative ranking
- **system-health** — Diagnostic scan of tasks, projects, goals, and backlog

## Framework Self-Audit

- **`core/scripts/validate.py`** — run `uv run core/scripts/validate.py` to check the framework for drift (frontmatter issues, broken cross-refs, MCP tool parity, workspace shape). Useful after bulk edits to skills/agents or before a release.
