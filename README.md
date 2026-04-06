<p align="center">
  <strong style="font-size: 2em;">PM Operating System</strong>
</p>

<h1 align="center">PM Operating System</h1>

<p align="center">
  <strong>Your AI-powered productivity system for Claude Code</strong><br>
  Turn brain dumps into organized, goal-driven work. Evaluate projects, run standups, and compound knowledge across sessions.
</p>

<p align="center">
  <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/"><img src="https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-orange" alt="License"></a>
  <a href="https://github.com/Ninety2UA/pm-operating-system/stargazers"><img src="https://img.shields.io/github/stars/Ninety2UA/pm-operating-system?style=social" alt="GitHub Stars"></a>
  <img src="https://img.shields.io/badge/Claude%20Code-Plugin-blueviolet" alt="Claude Code Plugin">
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

> "It's not just about text generation. Think about it more like an operating system." -- Andrej Karpathy, [Intro to Large Language Models (2023)](https://www.youtube.com/watch?v=zjkBMFhNj_g)

In his [Stanford talk](https://www.youtube.com/watch?v=c3b-JASoPi0) and subsequent writing, Karpathy describes a future where the LLM sits at the center, orchestrating tools, managing memory, and maintaining context across interactions. The model reads your files, understands your goals, uses tools to take action, and gets better over time.

**PM Operating System implements this vision literally:**

- **GOALS.md** is your strategic context. The LLM reads it every session to prioritize your work.
- **Skills** are specialized capabilities the LLM can invoke (market validation, risk analysis, sprint planning).
- **Commands** are recurring workflows (morning standup, weekly review, quarterly scoring).
- **Agents** are autonomous sub-processes that run in the background (deep research, batch evaluation, system diagnostics).
- **The MCP server** gives the LLM structured tools for task and project management with deduplication.
- **Knowledge/** is the LLM's long-term memory, compounding from daily journals to weekly reviews to quarterly assessments.

The result: each session makes the next one more effective. Your assistant does not start from zero; it starts from everything it has learned about you, your goals, and your work.

---

## Architecture

```mermaid
graph TD
    subgraph Input
        BACKLOG[BACKLOG.md<br>Raw brain dump]
    end

    subgraph Processing
        PROCESS["/process-backlog<br>Classify + dedup"]
    end

    subgraph Work Items
        TASKS["Tasks/<br>Single outcomes (< 2 hrs)"]
        PROJECTS["Projects/<br>Multi-step initiatives"]
    end

    subgraph "Project Pipeline (/launch)"
        VALIDATE[/validate-project]
        LEAN[/lean-canvas]
        GTM[/gtm-plan]
        COMPETE[/competitive-analysis]
        RISK[/pre-mortem]
        STORIES[/user-stories]
    end

    subgraph "Execution Loop"
        MORNING["/morning<br>Daily standup"]
        SPRINT["/sprint-plan<br>Weekly capacity"]
        WEEKLY["/weekly<br>Review + patterns"]
        QUARTERLY["/quarterly<br>OKR scoring"]
    end

    subgraph "Knowledge Layer"
        JOURNALS[Knowledge/journals/]
        RESEARCH[Knowledge/research/]
        PEOPLE[Knowledge/People/]
    end

    subgraph "MCP Server"
        MCP["manager-ai<br>10 tools + dedup"]
    end

    BACKLOG --> PROCESS
    PROCESS --> TASKS
    PROCESS --> PROJECTS
    PROJECTS --> VALIDATE
    VALIDATE --> LEAN
    LEAN --> GTM
    GTM --> COMPETE
    COMPETE --> RISK
    RISK --> STORIES
    STORIES --> TASKS
    TASKS --> MORNING
    MORNING --> SPRINT
    SPRINT --> WEEKLY
    WEEKLY --> QUARTERLY
    MORNING -.->|saves| JOURNALS
    WEEKLY -.->|reads| JOURNALS
    QUARTERLY -.->|scores| JOURNALS
    VALIDATE -.->|saves| RESEARCH
    MCP -.->|manages| TASKS
    MCP -.->|manages| PROJECTS
```

---

## Features

- **19 skills** covering every stage from ideation to execution
- **6 slash commands** for daily, weekly, and quarterly workflows
- **3 autonomous agents** for background research, batch evaluation, and system diagnostics
- **MCP server** with fuzzy deduplication for tasks and projects
- **Goal-driven prioritization** with P0-P3 levels tied to your strategic objectives
- **Project pipeline** with Go/No-Go gates at each evaluation stage
- **Compounding knowledge** from daily journals to weekly reviews to quarterly OKR scoring
- **Smart backlog processing** that classifies items and catches duplicates automatically
- **Optional integrations** for Granola (meetings), Slack (messaging), and Perplexity (research)

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
mkdir -p Tasks Projects Knowledge/{research/projects,research/topics,Transcripts,journals,session-reviews,decisions,People,Reference}

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

---

## What You Get

<details>
<summary><strong>Skills Reference (19 skills)</strong></summary>

### Ideation and Discovery

| Skill | Description |
|-------|-------------|
| `/discover-ideas` | Search the web for project ideas and trending opportunities |
| `/research-topic` | Deep research on any topic with web and social media signals |

### Project Evaluation Pipeline

| Skill | Description |
|-------|-------------|
| `/validate-project` | Research and validate a project idea against market reality |
| `/lean-canvas` | Create a Lean Canvas business model for a project idea |
| `/gtm-plan` | Go-to-market plan with ICP, beachhead segment, and channels |
| `/competitive-analysis` | Map competitor landscape with strengths, gaps, and positioning |
| `/pre-mortem` | Risk analysis that imagines the project has failed and works backward |

### Execution and Planning

| Skill | Description |
|-------|-------------|
| `/PRD` | Generate a Product Requirements Document for a project |
| `/user-stories` | Decompose a PRD into structured user stories with acceptance criteria |
| `/sprint-plan` | Create a weekly sprint plan from current tasks and user stories |
| `/plan-okrs` | Create or refresh measurable OKRs aligned to your goals |
| `/outcome-roadmap` | Generate an outcome-focused roadmap from active projects |
| `/prioritize` | Rank projects or tasks using ICE/RICE frameworks |

### Analysis and Review

| Skill | Description |
|-------|-------------|
| `/ab-test` | Analyze A/B test results with statistical rigor |
| `/decision` | Document a decision with structured context, options, and rationale |
| `/session-review` | Capture session learnings, prompts, and patterns for weekly analysis |
| `/refresh-goals` | Review and fill gaps in GOALS.md through conversation |

### Integrations

| Skill | Description |
|-------|-------------|
| `/meeting-sync` | Sync Granola meetings to local Knowledge folder |
| `/meeting-prep` | Prepare context for an upcoming meeting from People, transcripts, and tasks |

</details>

<details>
<summary><strong>Commands Reference (6 commands)</strong></summary>

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
|   +-- plugin.json            # Plugin manifest
|
|-- skills/                    # 19 specialized skills
|   |-- PRD/SKILL.md
|   |-- validate-project/SKILL.md
|   |-- lean-canvas/SKILL.md
|   |-- ...
|   +-- session-review/SKILL.md
|
|-- commands/                  # 6 slash commands
|   |-- morning.md
|   |-- weekly.md
|   |-- quarterly.md
|   |-- launch.md
|   |-- process-backlog.md
|   +-- write.md
|
|-- agents/                    # 3 autonomous agents
|   |-- deep-research.md
|   |-- batch-evaluator.md
|   +-- system-health.md
|
|-- core/
|   |-- mcp/
|   |   |-- server.py          # MCP server (10 tools + dedup)
|   |   +-- pyproject.toml
|   |-- templates/
|   |   |-- AGENTS.md          # AI instruction template
|   |   +-- config.yaml
|   +-- integrations/
|       +-- granola/            # Granola meeting sync setup
|
|-- hooks/
|   +-- hooks.json             # Session hooks (directory creation)
|
|-- Knowledge/                 # Long-term memory (per-user, gitignored)
|-- Tasks/                     # Active tasks (per-user, gitignored)
|-- Projects/                  # Project pipeline (per-user, gitignored)
|-- Library/                   # Reusable artifact catalog
|
|-- AGENTS.md                  # AI assistant instructions
|-- GOALS.md                   # Your personal goals (generated by setup.sh)
|-- BACKLOG.md                 # Raw capture inbox
|-- setup.sh                   # Interactive goals setup
|-- install.sh                 # Full bootstrap installer
|-- .mcp.json.example          # MCP config template
+-- GOALS.example.md           # Example goals file
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
# 1. Drop raw notes into BACKLOG.md
# 2. Run the processor
/process-backlog
```

The processor reads every item, checks for duplicates against existing tasks and projects, classifies each item (task vs. project), and asks for clarification on anything ambiguous.

### Launching a Project Through the Pipeline

```
/launch my-project-name
```

Runs the full evaluation pipeline with a Go/No-Go gate after each stage:

1. `/validate-project` -- Market research and validation brief
2. `/lean-canvas` -- Business model viability
3. `/gtm-plan` -- Go-to-market strategy
4. `/competitive-analysis` -- Competitor landscape
5. `/pre-mortem` -- Risk analysis (what could go wrong?)
6. `/user-stories` -- Decompose into buildable stories

Skip ahead with `--from`:

```
/launch my-project --from gtm-plan
```

### Weekly Review

```
/weekly
```

Compiles a shipping summary, reads journals for plan-vs-actual patterns, reviews session learnings, and proposes improvements to your workflow.

---

## The Compounding Loop

The system learns through three nested loops:

```
Daily (/morning)
  Saves plans to Knowledge/journals/
  Next morning reads yesterday's actuals
  Memories persist across sessions

    Weekly (/weekly)
    Compiles what shipped from completed tasks
    Reads journals for plan-vs-actual patterns
    Reads session reviews for recurring prompts
    Proposes new commands/skills

        Quarterly (/quarterly)
        Scores OKRs on a 0.0-1.0 scale
        Archives stale projects
        Refreshes GOALS.md
        Audits system health
```

Each layer feeds the next. Daily execution patterns inform weekly strategy. Weekly patterns inform quarterly goal-setting. The system gets smarter the more you use it.

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

**MCP Tools Available:**

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

### Optional Integrations

<details>
<summary><strong>Granola (Meeting Sync)</strong></summary>

Syncs meeting notes and transcripts from [Granola](https://granola.ai) into `Knowledge/Transcripts/`.

1. Install the Granola desktop app and create an account
2. Add to your `.mcp.json`:
```json
{
  "granola": {
    "type": "http",
    "url": "https://mcp.granola.ai/mcp"
  }
}
```
3. Use `/meeting-sync` during your morning standup or anytime

</details>

<details>
<summary><strong>Slack</strong></summary>

Post standups, read channels, and search message history.

1. Add to your `.mcp.json`:
```json
{
  "slack": {
    "type": "http",
    "url": "https://mcp.slack.com/mcp"
  }
}
```
2. Authenticate via OAuth when first used

</details>

<details>
<summary><strong>Perplexity (Research)</strong></summary>

Powers the research capabilities of `/validate-project`, `/competitive-analysis`, `/research-topic`, `/discover-ideas`, and `/gtm-plan`.

Install the Perplexity MCP server following their documentation, then add the configuration to your `.mcp.json`.

</details>

<details>
<summary><strong>Google Workspace (gws CLI)</strong></summary>

Optional Gmail and Calendar integration for enriching meeting prep with email history.

Install the [gws CLI](https://github.com/nicholasgasior/gws) and configure OAuth credentials at `~/.config/gws/client_secret.json`.

</details>

### Customization

- **Add skills:** Create `skills/<skill-name>/SKILL.md` with frontmatter (`name`, `description`, `allowed-tools`)
- **Add commands:** Create `commands/<command-name>.md` with frontmatter (`description`, `argument-hint`)
- **Add agents:** Create `agents/<agent-name>.md` with frontmatter (`name`, `description`, `model`, `tools`)
- **Modify behavior:** Edit `AGENTS.md` to change prioritization rules, categories, interaction style, or daily guidance

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

This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

Copyright 2026 Dominik Benger. You may view, use, modify, and share with attribution for non-commercial purposes. Commercial sale is not permitted, but you may use it internally for work and business.

---

## Acknowledgments

- **[Andrej Karpathy](https://karpathy.ai/)** for the "LLM OS" vision that inspired this project's architecture. His [Intro to Large Language Models](https://www.youtube.com/watch?v=zjkBMFhNj_g) talk and [Stanford CS229](https://www.youtube.com/watch?v=c3b-JASoPi0) lectures articulate the idea that LLMs are best understood as operating system kernels, not chatbots.
- **[Aman Khan](https://github.com/amanaiproduct)** for the original personal-os framework that this project builds upon.
- **[Anthropic](https://anthropic.com)** and the Claude Code team for building the plugin system that makes this possible.
