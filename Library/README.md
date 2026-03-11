# Library

A personal catalog of reusable AI artifacts — prompts, system instructions, skills, agents, and commands collected across different coding tools. This is a reference collection, not a runtime dependency. Nothing reads from here automatically; you copy what you need into the tool you're using.

## Structure

```
Library/
├── prompts/      # Standalone, copy-paste-ready prompts
├── systems/      # System-level instructions (CLAUDE.md, rules, personas)
├── skills/       # SKILL.md files (Claude Code / Codex format)
├── agents/       # Agent definitions and configurations
└── commands/     # Slash commands
```

### Categories

| Folder | What goes here | Decision rule |
|--------|---------------|---------------|
| `prompts/` | Standalone reusable prompts | "I copy this into ChatGPT / Claude / Cursor" |
| `systems/` | System prompts that define behavior or persona | "This goes in CLAUDE.md, .cursorrules, or a system message" |
| `skills/` | Claude Code SKILL.md files | "This is a skill I've authored" |
| `agents/` | Agent configs (subagent definitions, personas, tool sets) | "This defines an autonomous agent's behavior" |
| `commands/` | Slash commands or command definitions | "This is triggered by a /command" |

**When in doubt, put it in `prompts/`.** That's the catch-all for anything that doesn't fit a more specific category.

## Adding an item

1. Create a folder: `Library/<category>/<descriptive-name>/`
2. Add the main file using the naming convention for that category (see below)
3. Include YAML frontmatter with at minimum: `title`, `description`, `tools`, `tags`, `created`

### File naming by category

| Category | Main file name |
|----------|---------------|
| `prompts/` | `prompt.md` |
| `systems/` | `system.md` |
| `skills/` | `SKILL.md` |
| `agents/` | `agent.md` |
| `commands/` | `command.md` |

### Frontmatter template

```yaml
---
title: Descriptive name
description: One-line summary of what it does and when to use it
tools: [claude-code, cursor, chatgpt]
tags: [code-review, debugging, rails]
created: YYYY-MM-DD
---
```

The body of the file is the actual prompt/skill/agent content — clean and ready to use.

## Examples

```
Library/
├── prompts/
│   └── deep-code-review/
│       └── prompt.md
├── systems/
│   └── productivity-assistant/
│       └── system.md
├── skills/
│   └── prd-generator/
│       └── SKILL.md
├── agents/
│   └── rails-reviewer/
│       └── agent.md
└── commands/
    └── morning-standup/
        └── command.md
```
