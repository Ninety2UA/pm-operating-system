<div align="center">

![PM Operating System](docs/images/hero-banner.svg)

</div>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green" alt="License: MIT"></a>&nbsp;
  <a href="https://github.com/Ninety2UA/pm-operating-system/stargazers"><img src="https://img.shields.io/github/stars/Ninety2UA/pm-operating-system?style=social" alt="GitHub Stars"></a>&nbsp;
  <img src="https://img.shields.io/badge/Claude%20Code-Plugin-blueviolet" alt="Claude Code Plugin">&nbsp;
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white" alt="Python 3.11+">
</p>

<p align="center">
  <a href="#overview">Overview</a> &middot;
  <a href="#philosophy">Philosophy</a> &middot;
  <a href="#architecture">Architecture</a> &middot;
  <a href="#features">Features</a> &middot;
  <a href="#quick-start">Quick Start</a> &middot;
  <a href="#what-you-get">What You Get</a> &middot;
  <a href="#usage-examples">Usage</a> &middot;
  <a href="#configuration">Configuration</a>
</p>

---

## Overview

PM Operating System is a Claude Code plugin that gives your AI assistant a structured productivity layer. Instead of starting every session from scratch, your assistant knows your goals, tracks your tasks, evaluates your project ideas through a rigorous pipeline, and learns from each session to make the next one better.

**The workflow is simple:**

1. **Brain dump** into `BACKLOG.md` (no structure needed)
2. **Process** with `/process-backlog` to classify and deduplicate
3. **Evaluate** project ideas through a multi-stage pipeline (`/launch`)
4. **Execute** with daily standups, sprint plans, and weekly reviews
5. **Compound** knowledge across sessions, weeks, and quarters

---

## Philosophy

This project is built on a core insight from Andrej Karpathy's thinking about LLMs: that large language models are best understood not as chatbots, but as the **kernel of a new kind of operating system**.

> *"Think about it more like an operating system."*
>
> -- Andrej Karpathy, [Intro to Large Language Models (2023)](https://www.youtube.com/watch?v=zjkBMFhNj_g)

In his [Stanford talk](https://www.youtube.com/watch?v=c3b-JASoPi0) and subsequent writing, Karpathy describes a future where the LLM sits at the center, orchestrating tools, managing memory, and maintaining context across interactions. The model reads your files, understands your goals, uses tools to take action, and gets better over time.

**PM Operating System implements this vision literally:**

| LLM OS Concept | How It Works Here |
|---|---|
| **Strategic memory** | `GOALS.md` is read every session to prioritize your work |
| **Specialized capabilities** | 19 skills the LLM can invoke (validation, risk analysis, sprint planning) |
| **Recurring workflows** | 6 commands for daily standups, weekly reviews, quarterly scoring |
| **Autonomous sub-processes** | 3 agents that run in the background (research, evaluation, diagnostics) |
| **Structured tool use** | MCP server with 10 tools for task and project management |
| **Long-term memory** | `knowledge/` compounds from daily journals to quarterly assessments |

The result: each session makes the next one more effective. Your assistant does not start from zero; it starts from everything it has learned about you, your goals, and your work.

---

## Architecture

### System Overview

<div align="center">

![System Overview — BACKLOG.md flows through /process-backlog into Tasks and Projects, managed by the MCP server](docs/images/system-overview.svg)

</div>

### Project Pipeline

When a project enters the pipeline via `/launch`, it passes through six evaluation stages with a Go/No-Go gate after each:

<div align="center">

![Project Pipeline — Validate, Lean Canvas, GTM Plan, Competitive, Pre-Mortem, User Stories](docs/images/project-pipeline.svg)

</div>

> Each stage produces a markdown artifact saved to the project folder. Skip ahead with `/launch my-project --from gtm-plan`.

### The Compounding Loop

The system learns through three nested feedback loops. Each layer feeds the next.

<div align="center">

![The Compounding Loop — Daily feeds Weekly feeds Quarterly feeds back to Daily](docs/images/compounding-loop.svg)

</div>

---

## Features

| Category | What You Get |
|---|---|
| **Skills** | 19 specialized skills covering ideation, validation, planning, and execution |
| **Commands** | 6 slash commands for daily, weekly, and quarterly workflows |
| **Agents** | 3 autonomous agents for deep research, batch evaluation, and system diagnostics |
| **MCP Server** | 10 tools with fuzzy deduplication for tasks and projects |
| **Prioritization** | Goal-driven P0-P3 levels tied to your strategic objectives |
| **Pipeline** | Project evaluation with Go/No-Go gates at each stage |
| **Knowledge** | Compounding loops from daily journals to quarterly OKR scoring |
| **Integrations** | Optional: Granola (meetings), Slack (messaging), Perplexity (research) |

---

## Quick Start

### Option 1: Install as a Claude Code Plugin

```
/plugin marketplace add https://github.com/Ninety2UA/pm-operating-system.git
/plugin install pm-operating-system@pm-operating-system
```

> **Note on auth:** the HTTPS URL form above works without any setup. The shorter form `/plugin marketplace add Ninety2UA/pm-operating-system` only works if your local git is configured with GitHub SSH keys — otherwise you'll see `Permission denied (publickey)`.

Then run the setup to create your goals:

```bash
./setup.sh
```

### Option 2: Clone and Bootstrap

```bash
git clone https://github.com/Ninety2UA/pm-operating-system.git
cd pm-operating-system
./install.sh
```

The install script will:
- Verify Python 3.11+ and install `uv` if needed
- Install MCP server dependencies
- Create workspace directories
- Walk you through an interactive goals setup
- Verify everything works

### Option 3: Manual Setup

```bash
# Clone
git clone https://github.com/Ninety2UA/pm-operating-system.git
cd pm-operating-system

# Install MCP server dependencies
cd pm-operating-system/core/mcp && uv sync && cd ../../..

# Create workspace
mkdir -p tasks projects knowledge/{research/projects,research/topics,Meetings,journals,session-reviews,decisions,People,Reference}

# Set your goals
./setup.sh
```

> **Note:** `.mcp.json` lives inside `pm-operating-system/` and uses `${CLAUDE_PLUGIN_ROOT}` so it works automatically when installed as a Claude Code plugin. Option 2 is provided for contributors who want to edit the plugin locally — install your local clone as a plugin with `/plugin marketplace add /path/to/your/clone` then `/plugin install pm-operating-system@pm-operating-system`.

### Prerequisites

| Tool | Version | Required | Install |
|------|---------|----------|---------|
| Python | 3.11+ | Yes | `brew install python@3.13` |
| uv | latest | Yes | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| git | any | Yes | `brew install git` |
| Claude Code | latest | Yes | [claude.ai/download](https://claude.ai/download) |
| Node.js / npm | 18+ | For Perplexity | `brew install node` |
| gws | latest | For Google Workspace | `brew tap nicholasgasior/gws && brew install gws` |

---

## What You Get

<details>
<summary><strong>Skills Reference (19 skills)</strong></summary>

<br>

**Ideation and Discovery**

| Skill | Description |
|-------|-------------|
| `/discover-ideas` | Search the web for project ideas and trending opportunities |
| `/research-topic` | Deep research on any topic with web and social media signals |

**Project Evaluation Pipeline**

| Skill | Description |
|-------|-------------|
| `/validate-project` | Research and validate a project idea against market reality |
| `/lean-canvas` | Create a Lean Canvas business model for a project idea |
| `/gtm-plan` | Go-to-market plan with ICP, beachhead segment, and channels |
| `/competitive-analysis` | Map competitor landscape with strengths, gaps, and positioning |
| `/pre-mortem` | Risk analysis that imagines the project has failed and works backward |

**Execution and Planning**

| Skill | Description |
|-------|-------------|
| `/PRD` | Generate a Product Requirements Document for a project |
| `/user-stories` | Decompose a PRD into structured user stories with acceptance criteria |
| `/sprint-plan` | Create a weekly sprint plan from current tasks and user stories |
| `/plan-okrs` | Create or refresh measurable OKRs aligned to your goals |
| `/outcome-roadmap` | Generate an outcome-focused roadmap from active projects |
| `/prioritize` | Rank projects or tasks using ICE/RICE frameworks |

**Analysis and Review**

| Skill | Description |
|-------|-------------|
| `/ab-test` | Analyze A/B test results with statistical rigor |
| `/decision` | Document a decision with structured context, options, and rationale |
| `/session-review` | Capture session learnings, prompts, and patterns for weekly analysis |
| `/refresh-goals` | Review and fill gaps in GOALS.md through conversation |

**Integrations**

| Skill | Description |
|-------|-------------|
| `/meeting-sync` | Sync Granola meetings to local knowledge folder |
| `/meeting-prep` | Prepare context for an upcoming meeting from People, transcripts, and tasks |

</details>

<details>
<summary><strong>Commands Reference (6 commands)</strong></summary>

<br>

| Command | Description | Usage |
|---------|-------------|-------|
| `/morning` | Daily standup with meeting sync, top tasks, pipeline, OKRs, and journal save | `/morning` or `/morning quick` |
| `/weekly` | Weekly review with plan-vs-actual analysis, session patterns, and learning extraction | `/weekly` or `/weekly quick` |
| `/quarterly` | Quarterly review: OKR scoring, project purge, goals refresh, system audit | `/quarterly` or `/quarterly quick` |
| `/process-backlog` | Process BACKLOG.md with duplicate detection against existing tasks and projects | `/process-backlog` |
| `/launch` | Full evaluation pipeline with Go/No-Go gates at each stage | `/launch my-project` or `/launch my-project --from gtm-plan` |
| `/write` | Generate content (blog posts, emails, social) in your authentic voice | `/write blog-post AI trends` |

</details>

<details>
<summary><strong>Agents Reference (3 agents)</strong></summary>

<br>

| Agent | Description | When to Use |
|-------|-------------|-------------|
| **deep-research** | Multi-source background research using Perplexity. Saves briefs to knowledge/research/. | When you need thorough investigation of a topic, market, or technology |
| **batch-evaluator** | Parallel project evaluation with comparative ranking across 5 criteria. | When you have multiple project ideas to evaluate at once |
| **system-health** | Diagnostic scan of tasks, projects, goals, and backlog for issues. | When things feel off and you want a system-wide health check |

</details>

---

## Project Structure

```
pm-operating-system/                 (marketplace repo root)
|
|-- .claude-plugin/
|   +-- marketplace.json         Marketplace manifest (points at the plugin below)
|
|-- pm-operating-system/             (THE PLUGIN)
|   |-- .claude-plugin/
|   |   +-- plugin.json          Plugin manifest
|   |
|   |-- skills/                  25 skills (19 original + 6 former commands)
|   |   |-- morning/SKILL.md
|   |   |-- weekly/SKILL.md
|   |   |-- launch/SKILL.md
|   |   |-- PRD/SKILL.md
|   |   |-- validate-project/SKILL.md
|   |   +-- ...                  (20 more)
|   |
|   |-- agents/                  3 autonomous agents
|   |   |-- deep-research.md
|   |   |-- batch-evaluator.md
|   |   +-- system-health.md
|   |
|   |-- core/
|   |   +-- mcp/                 manager-ai MCP server (10 tools + dedup)
|   |
|   |-- hooks/
|   |   +-- hooks.json           Session hooks (workspace bootstrap)
|   |
|   |-- AGENTS.md                AI assistant instructions
|   |-- CLAUDE.md                Plugin-side context
|   |-- library/                 Reusable artifact catalog
|   +-- .mcp.json                MCP server manifest
|
|-- knowledge/                   Long-term memory (per-user, gitignored)
|-- tasks/                       Active tasks (per-user, gitignored)
|-- projects/                    Project pipeline (per-user, gitignored)
|-- GOALS.md                     Your personal goals (per-user, gitignored)
|-- BACKLOG.md                   Raw capture inbox (per-user, gitignored)
|
|-- README.md                    This file (repo-level docs)
|-- LICENSE
|-- docs/                        GitHub Pages site
|-- setup.sh                     Interactive goals setup
+-- install.sh                   Optional bootstrap installer (git clone path)
```

---

## Usage Examples

### Morning Standup

```
/morning
```

Your assistant will:
1. Sync any new meetings from Granola (if configured)
2. Show your top 5 tasks sorted by priority
3. Flag blocked tasks and suggest unblocking actions
4. Recommend one project to advance through the pipeline today
5. Note which OKRs today's work advances
6. Save the daily plan to `knowledge/journals/YYYY/MM/DD.md`

### Processing Your Backlog

```
/process-backlog
```

The processor reads every item in `BACKLOG.md`, checks for duplicates against existing tasks and projects, classifies each item (task vs. project), and asks for clarification on anything ambiguous.

### Launching a Project Through the Pipeline

```
/launch my-project-name
```

Runs the full evaluation pipeline with a Go/No-Go gate after each stage:

| Stage | Skill | Output |
|-------|-------|--------|
| 1 | `/validate-project` | Market research and validation brief |
| 2 | `/lean-canvas` | Business model viability |
| 3 | `/gtm-plan` | Go-to-market strategy |
| 4 | `/competitive-analysis` | Competitor landscape |
| 5 | `/pre-mortem` | Risk analysis |
| 6 | `/user-stories` | Decomposed buildable stories |

Skip ahead: `/launch my-project --from gtm-plan`

### Weekly Review

```
/weekly
```

Compiles a shipping summary, reads journals for plan-vs-actual patterns, reviews session learnings, and proposes improvements to your workflow.

---

## Configuration

### MCP Server (Required)

The manager-ai MCP server provides 10 tools for task and project management. It is wired up in the committed `pm-operating-system/.mcp.json` — no manual configuration needed when the plugin is installed:

```json
{
  "mcpServers": {
    "manager-ai": {
      "command": "uv",
      "args": ["--directory", "${CLAUDE_PLUGIN_ROOT}/core/mcp", "run", "server.py"],
      "env": {
        "MANAGER_AI_BASE_DIR": "/path/to/pm-operating-system"
      }
    }
  }
}
```

<details>
<summary><strong>MCP Tools Reference (10 tools)</strong></summary>

<br>

| Tool | Description |
|------|-------------|
| `list_tasks` | Query tasks with filters (priority, status, category) |
| `get_task_summary` | Priority/category/status counts with time estimates |
| `check_priority_limits` | Alerts if P0 > 3 or P1 > 7 |
| `prune_completed_tasks` | Archive done tasks older than 30 days |
| `list_projects` | Query projects with filters (status, priority, category) |
| `get_pipeline_status` | Count of projects at each pipeline stage |
| `get_project_artifacts` | Check which evaluation artifacts exist |
| `get_project_summary` | Aggregate project stats and artifact coverage |
| `get_system_status` | Full dashboard (tasks + projects + backlog) |
| `process_backlog_with_dedup` | Deduplicate backlog items against existing work |

</details>

### Optional Integrations

These integrations are optional but unlock powerful capabilities. Install whichever ones you need.

<details>
<summary><strong>Perplexity (AI-Powered Research)</strong></summary>

<br>

Powers the research capabilities of `/validate-project`, `/competitive-analysis`, `/research-topic`, `/discover-ideas`, and `/gtm-plan`. Without Perplexity, these skills will not have access to live web data.

**Install:**

```bash
npm install -g @nicepkg/perplexity-mcp
```

**Configure** — the Perplexity entry is already wired up in `.mcp.json` (runs via `npx -y @nicepkg/perplexity-mcp`). No manual edit needed.

**Set your API key** — get one from [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api), then:

```bash
export PERPLEXITY_API_KEY="pplx-..."
```

Add this to your `~/.zshrc` or `~/.bashrc` to persist across sessions.

**Available tools:**

| Tool | Purpose | Cost | Speed |
|------|---------|------|-------|
| `perplexity_search` | Finding URLs, facts, recent news | ~$0.04 | Fast |
| `perplexity_ask` | Quick AI-answered questions with citations | ~$0.03 | Fast |
| `perplexity_research` | In-depth multi-source investigation | ~$0.40 | 30s+ |
| `perplexity_reason` | Complex analysis with step-by-step logic | ~$0.40 | 30s+ |

</details>

<details>
<summary><strong>Slack (Team Messaging)</strong></summary>

<br>

Post standups to channels, read message history, search across workspaces, and draft announcements. Used by `/morning`, `/weekly`, and `/write` commands.

**Install** — use the Claude Code plugin (recommended):

```
/plugin install slack
```

This installs the Slack MCP server **and** high-level skills like `/slack:summarize-channel`, `/slack:find-discussions`, and `/slack:standup`.

You will be prompted to authenticate via OAuth on first use.

**Available tools:** `slack_send_message`, `slack_read_channel`, `slack_search_public`, `slack_search_channels`, `slack_read_thread`, and more.

</details>

<details>
<summary><strong>Granola (Meeting Sync)</strong></summary>

<br>

Syncs meeting notes and transcripts from [Granola](https://granola.ai) into `knowledge/meetings/`. Used by the `/meeting-sync` skill during your morning standup.

**Prerequisites:**
- Granola desktop app installed
- Granola paid plan (required for MCP access)

**Configure** — the Granola entry is already wired up in `.mcp.json` (HTTP MCP at `https://mcp.granola.ai/mcp`). You will be prompted to authenticate on first use. See [Granola MCP setup guide](https://www.granola.ai/blog/granola-mcp) for details.

**Usage:** Run `/meeting-sync` during your morning standup or anytime to pull in recent meetings.

**Available tools:** `list_meetings`, `get_meetings`, `get_meeting_transcript`, `query_granola_meetings`, `list_meeting_folders`

</details>

<details>
<summary><strong>Google Workspace (gws CLI)</strong></summary>

<br>

Gmail and Calendar integration for enriching `/meeting-prep` with email history, checking your calendar in `/morning`, and searching past correspondence.

**Install:**

```bash
# macOS
brew tap nicholasgasior/gws
brew install gws

# Or from source
go install github.com/nicholasgasior/gws@latest
```

**Authenticate:**

1. Create a Google Cloud project and enable the Gmail, Calendar, and Drive APIs
2. Download the OAuth client credentials JSON
3. Run the initial auth:

```bash
gws gmail users messages list --params '{"userId": "me", "maxResults": 1}'
```

This will open a browser for OAuth consent. Credentials are stored at `~/.config/gws/`.

**Example commands:**

```bash
# List recent emails
gws gmail users messages list --params '{"userId": "me", "maxResults": 10}'

# Check today's calendar
gws calendar events list --params '{"calendarId": "primary", "timeMin": "2026-04-06T00:00:00Z", "timeMax": "2026-04-06T23:59:59Z"}'
```

> **Note:** `gws` is a CLI tool, not an MCP server. The AI assistant calls it via shell commands.

</details>

### Customization

| What | How |
|------|-----|
| Add a skill | Create `pm-operating-system/skills/<name>/SKILL.md` with frontmatter (`name`, `description`). Descriptions should enumerate explicit trigger phrases so Claude auto-invokes reliably. |
| Add an agent | Create `pm-operating-system/agents/<name>.md` with frontmatter (`name`, `description`, `model`, `tools`) |
| Change behavior | Edit `pm-operating-system/AGENTS.md` to modify prioritization rules, categories, or interaction style |
| Add MCP server | Edit `pm-operating-system/.mcp.json` — use `${CLAUDE_PLUGIN_ROOT}` for intra-plugin paths |

---

## Releases

Tagged releases and binaries: [github.com/Ninety2UA/pm-operating-system/releases](https://github.com/Ninety2UA/pm-operating-system/releases).

### v2.2.0 — 2026-04-14

**Plugin restructure + skill overhaul — aligned with Anthropic's plugin and skill-creator conventions.**

This release fixes the last install blocker (repos must have plugin content in a subdirectory, not at the repo root), converts all 6 commands to skills so the plugin has one consistent component type, and brings every skill up to skill-creator best practices.

- **Fixed** — `/plugin install` now succeeds. Previous releases couldn't actually be installed because `.claude-plugin/marketplace.json` had `"source": "."` which Claude Code rejects. Plugin content now lives in `pm-operating-system/` subdirectory, following the pattern used by `anthropics/knowledge-work-plugins`.
- **Changed** — All 6 commands (`/morning`, `/weekly`, `/quarterly`, `/launch`, `/process-backlog`, `/write`) converted from `commands/*.md` to `skills/*/SKILL.md`. User invocation (`/name`) is unchanged.
- **Improved** — Every skill's description rewritten with explicit trigger-phrase enumeration and a "push" clause (e.g. "even if the user doesn't say 'X' explicitly"). Improves auto-invocation reliability across all 25 skills.
- **Improved** — 9 skills with inline templates >65 lines now use progressive disclosure: templates moved to `references/<name>-template.md` and loaded on demand. SKILL.md bodies are now uniformly under 160 lines.
- **Added** — `allowed-tools` frontmatter on the 6 former commands for consistency with the older skills.
- **Removed** — `user-invocable: true` from `meeting-prep` (non-standard Claude Code frontmatter field).

**Breaking change for repo-local developers:** The plugin content is no longer at the repo root. If you were running Claude Code directly from the repo (project-local mode), install as a plugin instead:

```
/plugin marketplace add https://github.com/Ninety2UA/pm-operating-system.git
/plugin install pm-operating-system@pm-operating-system
```

If you previously added the marketplace and hit the `v2.1.0` or `v2.1.1` schema errors, remove the stale entry first:
```
/plugin marketplace remove Ninety2UA-pm-operating-system
```

### v2.1.1 — 2026-04-14

**Hotfix: `/plugin marketplace add` now actually clones + registers.**

v2.1.0 fixed the committed `.mcp.json` but two install-path issues remained: the repo was missing `.claude-plugin/marketplace.json` (required by Claude Code to treat a repo as a plugin marketplace), and the documented install command used the SSH form which fails without GitHub SSH keys configured.

- **Fixed** — Added `.claude-plugin/marketplace.json` as a single-plugin marketplace manifest with `"source": "."`. Claude Code now recognizes the repo as a valid marketplace.
- **Fixed** — README Option 1 and FAQ now document the HTTPS clone URL (`https://github.com/Ninety2UA/pm-operating-system.git`), which works without SSH keys. The shorter `Owner/Repo` form still works if you have SSH keys configured.

### v2.1.0 — 2026-04-14

**Distribution fix: the Claude Code plugin install path now actually works.**

Before this release, `/plugin install pm-operating-system@pm-operating-system` completed but shipped zero MCP tools, because `.mcp.json` was gitignored. Plugin-install users silently lost `manager-ai`, `perplexity`, and `granola`.

- **Fixed** — README install command. Option 1 previously advertised `/install <repo>`, which is not a real Claude Code slash command. Corrected to the two-step marketplace flow using the HTTPS clone URL (works without SSH keys configured).
- **Fixed** — `.mcp.json` is now committed at the repo root with `${CLAUDE_PLUGIN_ROOT}`-based paths, matching the convention used by Anthropic's official plugins.
- **Changed** — `MANAGER_AI_BASE_DIR` defaults to `"."` (CWD) rather than a hard-coded absolute path, so the plugin works from any working directory.
- **Removed** — `.mcp.json.example` (redundant with the tracked `.mcp.json`), plus the MCP-config block in `install.sh` (no longer needed).
- **Improved** — Perplexity and Granola docs. The `mcpServers` entries are wired up in `.mcp.json` by default; you just install the CLI/desktop app and set your API key / auth.

**Migration for existing users:** If you were running the repo in Option 2 mode (gitignored `.mcp.json` with absolute paths from `install.sh`'s sed rewrite), delete the local copy (`rm .mcp.json`) and pull the committed version. To use `manager-ai` going forward, install as a plugin: `/plugin marketplace add https://github.com/Ninety2UA/pm-operating-system.git` then `/plugin install pm-operating-system@pm-operating-system`.

### v2.0.0 — Initial release

Public debut of the plugin architecture: goal-driven task management, project pipeline evaluation, compounding knowledge loops (daily journals → weekly reviews → quarterly OKR scoring), custom `manager-ai` MCP server with 10 tools, and integration with Perplexity, Slack, and Granola. See [git history](https://github.com/Ninety2UA/pm-operating-system/commits/main) for per-commit detail.

---

## Contributing

Contributions are welcome. Please:

- Do not include personal information in commits
- Keep additions generic and configurable
- Follow the existing patterns for skills, commands, and agents
- Include documentation for new features
- Test that `install.sh` still works after your changes

---

## License

MIT — open source, free to use for any purpose. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **[Andrej Karpathy](https://karpathy.ai/)** for the "LLM OS" vision that inspired this project's architecture. His [Intro to Large Language Models](https://www.youtube.com/watch?v=zjkBMFhNj_g) talk and [Stanford CS229](https://www.youtube.com/watch?v=c3b-JASoPi0) lectures articulate the idea that LLMs are best understood as operating system kernels, not chatbots.
- **[Aman Khan](https://github.com/amanaiproduct)** for the original personal-os framework that this project builds upon.
