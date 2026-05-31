# Using the PM Operating System with other AI tools

This system is authored for Claude Code, but it is built on three open standards, so it runs in **OpenAI Codex CLI**, **Cursor**, **Google Antigravity**, and other conformant tools with no per-tool rewrite:

- **`AGENTS.md`** — the operating manual. Read natively by Codex, Cursor, and Antigravity. (In Claude Code, `CLAUDE.md` imports it via `@AGENTS.md`.)
- **`.agents/skills/<name>/SKILL.md`** — the "Agent Skills" standard. Generated from the `.claude/` source by `core/scripts/build_adapters.py` and **committed** to the repo, so conformant tools auto-discover all skills (plus the 3 agents and the `analyze` command) with zero install step.
- **MCP** — the `manager-ai` server (`core/mcp/server.py`) provides the 10 task/project tools. Wire it into each tool's MCP config (below).

## Capability matrix

| Capability | Claude Code | Codex CLI | Antigravity | Cursor |
|---|---|---|---|---|
| MCP (`manager-ai`) | `.mcp.json` | `~/.codex/config.toml` | `~/.gemini/config/mcp_config.json` | `.cursor/mcp.json` |
| `AGENTS.md` context | via `CLAUDE.md` | native | native | native |
| Skills | `.claude/skills/` (source) | `.agents/skills/` | `.agents/skills/` | `.agents/skills/` |
| Per-skill `references/` | yes | yes | yes | yes |
| Subagents (separate context / background) | yes | partial | yes | yes |

> Also works with Windsurf, GitHub Copilot, and other tools that adopt the Agent Skills standard — they read the same `.agents/skills/` tree.

## Wiring the manager-ai MCP server

**Quick path — `install_for.py`** previews the config changes for every tool, then applies them:

```bash
uv run core/scripts/install_for.py                       # dry-run preview (all tools)
uv run core/scripts/install_for.py --tool codex --apply  # write ~/.codex/config.toml
uv run core/scripts/install_for.py --tool cursor --apply # write ~/.cursor/mcp.json
```

It splices Codex's TOML and merges Cursor's JSON **without touching other servers** (a timestamped `.bak` is made first), and prints the Antigravity block to paste (its config path varies by version). To wire by hand instead, use the blocks below.

Replace `/ABS/PATH/personal-os` with the absolute path to your clone. `MANAGER_AI_BASE_DIR` points the server at your workspace regardless of the tool's working directory, and the server already honors it (`core/mcp/server.py`). **Splice** these blocks into existing config — don't overwrite other servers.

### OpenAI Codex CLI — `~/.codex/config.toml`

```toml
[mcp_servers.manager-ai]
command = "uv"
args = ["--directory", "/ABS/PATH/personal-os/core/mcp", "run", "server.py"]
env = { MANAGER_AI_BASE_DIR = "/ABS/PATH/personal-os" }
```

Codex reads `AGENTS.md` from the repo root automatically and discovers skills from `.agents/skills/`. Nothing else to do.

### Cursor — `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global)

```json
{
  "mcpServers": {
    "manager-ai": {
      "command": "uv",
      "args": ["--directory", "/ABS/PATH/personal-os/core/mcp", "run", "server.py"],
      "env": { "MANAGER_AI_BASE_DIR": "/ABS/PATH/personal-os" }
    }
  }
}
```

Cursor reads `AGENTS.md` and loads skills from `.agents/skills/`. Note Cursor's ~40-active-tool ceiling across all MCP servers combined — `manager-ai` uses 10.

### Google Antigravity — `~/.gemini/config/mcp_config.json`

```json
{
  "mcpServers": {
    "manager-ai": {
      "command": "uv",
      "args": ["--directory", "/ABS/PATH/personal-os/core/mcp", "run", "server.py"],
      "env": {
        "MANAGER_AI_BASE_DIR": "/ABS/PATH/personal-os",
        "MCP_MODE": "stdio",
        "DISABLE_CONSOLE_OUTPUT": "true"
      }
    }
  }
}
```

Antigravity reads `AGENTS.md` and `.agents/skills/`. (Its config path/schema is newer — verify against current Antigravity docs; `MCP_MODE=stdio` + `DISABLE_CONSOLE_OUTPUT=true` keep stdio JSON-RPC clean.)

### Other servers (perplexity, granola, slack)

Optional, configured per tool the same way: `perplexity` and `slack` are stdio/remote servers; `granola` is the remote URL `https://mcp.granola.ai/mcp`. Skills refer to these by logical name, so name them `perplexity`, `granola`, and `slack` in your config for the instructions to read naturally.

## Native subagents (Cursor + Codex)

The 3 agents (`deep-research`, `batch-evaluator`, `system-health`) are generated into two extra **committed** trees so they can run as *real* subagents (separate context / background) where supported:

- **Cursor** → `.cursor/agents/<name>.md` — clean win; Cursor prioritizes the native subagent over the same-named skill. `deep-research`/`batch-evaluator` are marked `is_background: true`; `system-health` is `readonly: true`.
- **Codex** → `.codex/agents/<name>.toml` — works, but if the same-named skill intercepts dispatch it simply degrades to today's inline-skill behavior (no worse). `system-health` carries `sandbox_mode = "read-only"`.
- **Antigravity** → no static subagent file exists (subagents are spawned dynamically at runtime), so the agents run via the inline `.agents/skills/` version. Nothing to generate.

The agents stay in `.agents/skills/` regardless (that's how Antigravity + any non-subagent host gets them), so some duplication on Codex/Cursor is expected and resolved by each tool's precedence.

## Regenerating adapters

`.agents/skills/`, `.codex/agents/`, and `.cursor/agents/` are all **generated** from `.claude/`. After editing any skill, agent, or command, regenerate and commit:

```bash
uv run core/scripts/build_adapters.py           # regenerate all three trees
uv run core/scripts/build_adapters.py --check    # verify in sync (CI-friendly; exit 1 on drift)
```

Never hand-edit files under those trees — they are overwritten on the next run. `--check` also fails if any Claude-only token (`mcp__…`, `$ARGUMENTS`, `$CLAUDE_PROJECT_DIR`, `AskUserQuestion`, `.claude/skills/`) leaks into the generated output. The framework validator (`uv run core/scripts/validate.py`) runs this same check (check 38), so a single validate run also catches adapter drift.

## Known limitations

- **Subagents.** The 3 agents are emitted as native subagents for Cursor (`.cursor/agents/`) and Codex (`.codex/agents/`) — see the **Native subagents** section above — and remain inline `.agents/skills/` skills for Antigravity (no static subagent format) and any other host. `system-health` carries an explicit READ-ONLY instruction in its generated body, since the tool-allowlist enforcement it relies on in Claude Code isn't portable.
- **`make-slides`** points at helper scripts with skill-relative paths (e.g. `references/render.js`). Its Node/Playwright/Google-Slides flow assumes the script runs from the skill directory; adjust paths if your host uses a different working directory.
- **Cursor reads both trees.** Cursor discovers `.agents/skills/` (used here) and also recognizes `.claude/skills/`. Same-named skills should dedupe by precedence (`.agents/skills/` wins); if you ever see duplicates, that's the cause.
