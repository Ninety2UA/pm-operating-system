<p align="center">
  <img src="docs/images/hero-banner.svg" alt="PM Operating System" width="100%">
</p>

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
| **Long-term memory** | `Knowledge/` compounds from daily journals to quarterly assessments |

The result: each session makes the next one more effective. Your assistant does not start from zero; it starts from everything it has learned about you, your goals, and your work.

---

## Architecture

### System Overview

<p align="center">
  <img src="docs/images/system-overview.svg" alt="System Overview — BACKLOG.md flows through /process-backlog into Tasks and Projects, managed by the MCP server" width="100%">
</p>

### Project Pipeline

When a project enters the pipeline via `/launch`, it passes through six evaluation stages with a Go/No-Go gate after each:

<p align="center">
  <img src="docs/images/project-pipeline.svg" alt="Project Pipeline — Validate, Lean Canvas, GTM Plan, Competitive, Pre-Mortem, User Stories" width="100%">
</p>

> Each stage produces a markdown artifact saved to the project folder. Skip ahead with `/launch my-project --from gtm-plan`.

### The Compounding Loop

The system learns through three nested feedback loops. Each layer feeds the next.

<p align="center">
  <img src="docs/images/compounding-loop.svg" alt="The Compounding Loop — Daily feeds Weekly feeds Quarterly feeds back to Daily" width="100%">
</p>

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
/install Ninety2UA/pm-operating-system
```

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
- Configure `.mcp.json`
- Walk you through an interactive goals setup
- Verify everything works

### Option 3: Manual Setup

```bash
# Clone
git clone https://github.com/Ninety2UA/pm-operating-system.git
cd pm-operating-system

# Install MCP server dependencies
cd core/mcp && uv sync && cd ../..

# Create workspace
mkdir -p Tasks Projects Knowledge/{research/projects,research/topics,Meetings,journals,session-reviews,decisions,People,Reference}

# Configure MCP (edit paths to match your install location)
cp .mcp.json.example .mcp.json

# Set your goals
./setup.sh
```

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
| `/meeting-sync` | Sync Granola meetings to local Knowledge folder |
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
| **deep-research** | Multi-source background research using Perplexity. Saves briefs to Knowledge/research/. | When you need thorough investigation of a topic, market, or technology |
| **batch-evaluator** | Parallel project evaluation with comparative ranking across 5 criteria. | When you have multiple project ideas to evaluate at once |
| **system-health** | Diagnostic scan of tasks, projects, goals, and backlog for issues. | When things feel off and you want a system-wide health check |

</details>

---

## Project Structure

```
pm-operating-system/
|
|-- .claude-plugin/
|   +-- plugin.json              Plugin manifest
|
|-- skills/                      19 specialized skills
|   |-- PRD/SKILL.md
|   |-- validate-project/SKILL.md
|   |-- lean-canvas/SKILL.md
|   |-- gtm-plan/SKILL.md
|   |-- competitive-analysis/SKILL.md
|   |-- pre-mortem/SKILL.md
|   |-- user-stories/SKILL.md
|   |-- sprint-plan/SKILL.md
|   +-- ...
|
|-- commands/                    6 slash commands
|   |-- morning.md
|   |-- weekly.md
|   |-- quarterly.md
|   |-- launch.md
|   |-- process-backlog.md
|   +-- write.md
|
|-- agents/                      3 autonomous agents
|   |-- deep-research.md
|   |-- batch-evaluator.md
|   +-- system-health.md
|
|-- core/
|   |-- mcp/
|   |   |-- server.py            MCP server (10 tools + dedup)
|   |   +-- pyproject.toml
|   |-- templates/
|   |   |-- AGENTS.md            AI instruction template
|   |   +-- config.yaml
|   +-- integrations/
|       +-- granola/              Granola meeting sync setup
|
|-- hooks/
|   +-- hooks.json               Session hooks (directory creation)
|
|-- Knowledge/                   Long-term memory (per-user, gitignored)
|-- Tasks/                       Active tasks (per-user, gitignored)
|-- Projects/                    Project pipeline (per-user, gitignored)
|-- Library/                     Reusable artifact catalog
|
|-- AGENTS.md                    AI assistant instructions
|-- GOALS.md                     Your personal goals (generated by setup.sh)
|-- BACKLOG.md                   Raw capture inbox
|-- setup.sh                     Interactive goals setup
|-- install.sh                   Full bootstrap installer
|-- .mcp.json.example            MCP config template
+-- GOALS.example.md             Example goals file
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
6. Save the daily plan to `Knowledge/journals/YYYY/MM/DD.md`

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

The manager-ai MCP server provides 10 tools for task and project management. It is configured automatically by `install.sh`, or manually via `.mcp.json`:

```json
{
  "mcpServers": {
    "manager-ai": {
      "command": "uv",
      "args": ["--directory", "/path/to/pm-operating-system/core/mcp", "run", "server.py"],
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

**Configure** — add to your `.mcp.json` under `mcpServers`:

```json
"perplexity": {
  "command": "npx",
  "args": ["-y", "@nicepkg/perplexity-mcp"]
}
```

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

Syncs meeting notes and transcripts from [Granola](https://granola.ai) into `Knowledge/Meetings/`. Used by the `/meeting-sync` skill during your morning standup.

**Prerequisites:**
- Granola desktop app installed
- Granola paid plan (required for MCP access)

**Configure** — add to your `.mcp.json` under `mcpServers`:

```json
"granola": {
  "type": "http",
  "url": "https://mcp.granola.ai/mcp"
}
```

You will be prompted to authenticate on first use. See [Granola MCP setup guide](https://www.granola.ai/blog/granola-mcp) for details.

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
| Add a skill | Create `skills/<name>/SKILL.md` with frontmatter (`name`, `description`, `allowed-tools`) |
| Add a command | Create `commands/<name>.md` with frontmatter (`description`, `argument-hint`) |
| Add an agent | Create `agents/<name>.md` with frontmatter (`name`, `description`, `model`, `tools`) |
| Change behavior | Edit `AGENTS.md` to modify prioritization rules, categories, or interaction style |

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
