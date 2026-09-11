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
- **spec** — Synthesize PRD + project artifacts into a comprehensive 29-section, build-ready technical spec (pinned tech stack/manifest, file tree, C4 architecture, test-first Test List, dependency-ordered task→sub-task WBS, AI build-toolkit + design-tooling recommendations) — references the PRD, never restates it
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
- **cli-watch** — Platform currency watcher: classify Claude Code/Anthropic changes since the baseline into a dated decision report (report-only schedulable; `full` owner-run)
- **repo-watch** — Ecosystem currency watcher: per-repo deltas over the registered external repos with adopt/adapt/skip candidate lines (registry seeded with the six mined repos; report-only schedulable)
- **morning**, **weekly**, **quarterly**, **process-backlog**, **write**, **launch** — listed in `## Commands` above

## Agents

- **deep-research** — Background multi-source research, saves briefs to knowledge/
- **batch-evaluator** — Parallel project evaluation with comparative ranking
- **system-health** — Diagnostic scan of tasks, projects, goals, and backlog

## Framework Self-Audit

- **`core/scripts/validate.py`** — run `uv run core/scripts/validate.py` to check the framework for drift (frontmatter issues, broken cross-refs, MCP tool parity, workspace shape, pipeline artifact conformance, external CLI deps, bidirectional skill registry, MCP handler presence, BACKLOG.md structure, stale lock files, PIPELINE_STAGES parity, BOM, secret-bypass lint, backup coverage, adapter manifest). Inline `# /// script` metadata auto-installs pyyaml. Useful after bulk edits to skills/agents or before a release. Non-blocking warnings are reported separately from hard failures; the documented classes are listed below.
- **`core/scripts/build_adapters.py`** — run `uv run core/scripts/build_adapters.py` to (re)generate the committed cross-tool adapters from the `.claude/` source: `.agents/skills/` (skills + agents + commands — the Agent Skills standard) plus native subagents `.codex/agents/*.toml` + `.cursor/agents/*.md`. Run after editing any skill/agent/command; `--check` verifies they're in sync and free of Claude-only tokens (CI-friendly, exit 1 on drift). The validator's check 38 runs this same check. Every build writes `.agents/skills.lock.json` (a manifest of generated paths and content hashes) and refuses to overwrite or remove a file it cannot prove it generated; `--force` overrides, and a refusal leaves `--check` red until the file is moved or forced.
- **`core/scripts/install_for.py`** — run `uv run core/scripts/install_for.py [--tool codex|cursor|antigravity|all] [--apply]` to wire the manager-ai MCP server into another tool's config (dry-run by default; splices Codex TOML / merges Cursor JSON without clobbering other servers, backs up first; prints the Antigravity block to paste). Setup details: `docs/portability.md`.
- **`core/scripts/tests/`** — run `uv run --with pytest --with pyyaml pytest core/scripts/tests/ -q` for the framework's pytest suite (validator checks, adapter build, currency helpers, the guard drill). A behavior-bearing change ships its test in the same commit.
- **`claude plugin validate .`** — run it from the repo root for Claude Code's built-in frontmatter check over the bare `.claude/skills` directory; it reports any SKILL.md whose frontmatter fails to parse (verified passing 2026-09-11). Complementary to the validator, which does not run it.
- **Built-in skill audit** — the `/skill-doctor` command (interactive only, typed inside a session) reports which loaded skills went unused and what they cost in context, so the catalog can be pruned. Complementary to the validator, which does not run it.
- **Non-blocking warning classes** — the validator's documented warn-class findings are `pipeline-artifact`, `external-dep` (external CLI deps not on PATH), `lock-hygiene`, `ledger-link`, `live-registry`, `secret-bypass`, `backup-coverage`, and the `guard-wiring` timeout notice. Green means zero hard failures with warnings only in these classes; a warning in any other class is drift to fix, not noise. Environment notices such as a missing memory directory or `.mcp.json` describe the install, not the framework.
- **Framework tests must be able to fail** — before adding a test under `core/scripts/tests/`, name the production change that would break it; derive expected values by hand, never from the code under test; never assert by grepping a skill's or script's own text (that only proves the source is the source) — run the artifact and check its output or side effect. Doc-only changes earn no tests and say so in the PR. Full criteria: `core/CODING_STANDARDS.md`. (RW-2026-09-11-17)
