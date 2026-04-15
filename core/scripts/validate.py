#!/usr/bin/env python3
"""Exhaustive framework validator for personal-os.

Runs every check I can think of. Exits 0 if clean, 1 if any issues.
"""
import os, re, sys, json, subprocess
from pathlib import Path
try:
    import yaml
except ImportError:
    print("Need pyyaml"); sys.exit(2)

ROOT = Path("/Users/dbenger/personal-os")
MEMORY = Path("/Users/dbenger/.claude/projects/-Users-dbenger-personal-os/memory")

issues = []
def fail(cat, msg): issues.append((cat, msg))
def ok(cat, msg): pass  # silent on pass

# ─── 1. SKILL.md frontmatter ──────────────────────────────────────
skill_names = set()
skill_descriptions = {}
for skill_md in sorted((ROOT / ".claude/skills").glob("*/SKILL.md")):
    content = skill_md.read_text()
    rel = skill_md.relative_to(ROOT)
    if not content.startswith("---"):
        fail("skill-fm", f"{rel}: no frontmatter fence"); continue
    try:
        body_parts = content.split("---", 2)
        fm = yaml.safe_load(body_parts[1])
        if not isinstance(fm, dict):
            fail("skill-fm", f"{rel}: frontmatter not dict"); continue
        name = fm.get("name")
        desc = fm.get("description", "")
        if not name: fail("skill-fm", f"{rel}: missing name")
        if not desc: fail("skill-fm", f"{rel}: missing description")
        if name and name != skill_md.parent.name:
            fail("skill-fm", f"{rel}: name '{name}' != folder '{skill_md.parent.name}'")
        skill_names.add(name or skill_md.parent.name)
        skill_descriptions[name] = desc
    except yaml.YAMLError as e:
        fail("skill-fm", f"{rel}: YAML parse: {e}")

# ─── 2. Agent frontmatter ─────────────────────────────────────────
agent_names = set()
for agent_md in sorted((ROOT / ".claude/agents").glob("*.md")):
    content = agent_md.read_text()
    rel = agent_md.relative_to(ROOT)
    if not content.startswith("---"):
        fail("agent-fm", f"{rel}: no frontmatter"); continue
    try:
        body_parts = content.split("---", 2)
        fm = yaml.safe_load(body_parts[1])
        name = fm.get("name")
        if not name: fail("agent-fm", f"{rel}: missing name")
        tools = fm.get("tools")
        if not tools: fail("agent-fm", f"{rel}: missing tools")
        elif not isinstance(tools, list):
            fail("agent-fm", f"{rel}: tools must be list")
        if name and name != agent_md.stem:
            fail("agent-fm", f"{rel}: name '{name}' != filename '{agent_md.stem}'")
        agent_names.add(name or agent_md.stem)
    except yaml.YAMLError as e:
        fail("agent-fm", f"{rel}: YAML parse: {e}")

# ─── 3. Command frontmatter ───────────────────────────────────────
command_names = set()
for cmd_md in sorted((ROOT / ".claude/commands").glob("*.md")):
    content = cmd_md.read_text()
    rel = cmd_md.relative_to(ROOT)
    if not content.startswith("---"):
        fail("cmd-fm", f"{rel}: no frontmatter"); continue
    try:
        fm = yaml.safe_load(content.split("---", 2)[1])
        if not fm.get("description"):
            fail("cmd-fm", f"{rel}: missing description")
        command_names.add(cmd_md.stem)
    except yaml.YAMLError as e:
        fail("cmd-fm", f"{rel}: YAML parse: {e}")

# ─── 4. Skill references/ integrity ───────────────────────────────
for skill_dir in sorted((ROOT / ".claude/skills").iterdir()):
    if not skill_dir.is_dir(): continue
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists(): continue
    body = skill_md.read_text()
    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        for ref_file in refs_dir.rglob("*"):
            if ref_file.is_file() and not ref_file.name.startswith("."):
                rel_name = ref_file.relative_to(skill_dir).as_posix()
                bare = ref_file.name
                # Accept reference by full relative path OR bare filename
                if rel_name not in body and bare not in body:
                    fail("skill-ref-orphan", f"{skill_dir.name}/{rel_name} not referenced in SKILL.md")
    # Scripts in skill dir (not references/)
    for script in list(skill_dir.glob("*.py")) + list(skill_dir.glob("*.sh")) + list(skill_dir.glob("*.js")):
        if script.name not in body:
            fail("skill-ref-orphan", f"{skill_dir.name}/{script.name} script not referenced")

# ─── 5. Project idea.md frontmatter ───────────────────────────────
valid_statuses = {"idea", "evaluating", "ready", "active", "paused", "archived"}
valid_priorities = {"P0", "P1", "P2", "P3"}
valid_categories = {"technical", "outreach", "research", "writing", "content", "admin", "personal", "other"}
for idea in sorted((ROOT / "projects").glob("*/idea.md")):
    rel = idea.relative_to(ROOT)
    content = idea.read_text()
    if not content.startswith("---"):
        fail("project-fm", f"{rel}: no frontmatter"); continue
    try:
        fm = yaml.safe_load(content.split("---", 2)[1])
        status = fm.get("project_status")
        cat = fm.get("category")
        pri = fm.get("priority")
        if status not in valid_statuses:
            fail("project-fm", f"{rel}: invalid status '{status}'")
        if cat not in valid_categories:
            fail("project-fm", f"{rel}: invalid category '{cat}'")
        if pri not in valid_priorities:
            fail("project-fm", f"{rel}: invalid priority '{pri}'")
    except yaml.YAMLError as e:
        fail("project-fm", f"{rel}: YAML parse: {e}")

# ─── 6. Task frontmatter (if any) ─────────────────────────────────
valid_task_statuses = {"n", "s", "b", "d", "r"}
for tsk in sorted((ROOT / "tasks").glob("*.md")):
    if tsk.name in ("README.md",) or tsk.name.startswith("."): continue
    rel = tsk.relative_to(ROOT)
    content = tsk.read_text()
    if not content.startswith("---"):
        fail("task-fm", f"{rel}: no frontmatter"); continue
    try:
        fm = yaml.safe_load(content.split("---", 2)[1])
        if fm.get("status") not in valid_task_statuses:
            fail("task-fm", f"{rel}: invalid status")
        if fm.get("priority") not in valid_priorities:
            fail("task-fm", f"{rel}: invalid priority")
    except yaml.YAMLError as e:
        fail("task-fm", f"{rel}: YAML parse: {e}")

# ─── 7. CLAUDE.md lists vs reality ────────────────────────────────
claude_md = (ROOT / "CLAUDE.md").read_text()
# Command list
for m in re.finditer(r"^- `/([a-z-]+)", claude_md, re.M):
    cmd = m.group(1)
    if cmd not in command_names and cmd not in skill_names:
        fail("claude-md-cmd", f"/CLAUDE.md lists /{cmd} — no matching command or skill")
# Skill list
claude_skill_section = claude_md.split("## Skills")[1].split("## Agents")[0] if "## Skills" in claude_md else ""
for m in re.finditer(r"^- \*\*([a-z-]+)\*\*", claude_skill_section, re.M):
    s = m.group(1)
    if s not in skill_names and s not in command_names:
        fail("claude-md-skill", f"CLAUDE.md lists skill **{s}** — no matching skill")
# Agent list
claude_agent_section = claude_md.split("## Agents")[1] if "## Agents" in claude_md else ""
for m in re.finditer(r"^- \*\*([a-z-]+)\*\*", claude_agent_section, re.M):
    a = m.group(1)
    if a not in agent_names:
        fail("claude-md-agent", f"CLAUDE.md lists agent **{a}** — no matching agent")

# ─── 8. MCP tool references in skill/agent bodies ─────────────────
DOCUMENTED_MCP_TOOLS = {
    "mcp__manager-ai__list_tasks", "mcp__manager-ai__get_task_summary",
    "mcp__manager-ai__check_priority_limits", "mcp__manager-ai__prune_completed_tasks",
    "mcp__manager-ai__list_projects", "mcp__manager-ai__get_pipeline_status",
    "mcp__manager-ai__get_project_artifacts", "mcp__manager-ai__get_project_summary",
    "mcp__manager-ai__get_system_status", "mcp__manager-ai__process_backlog_with_dedup",
}
for md_file in list((ROOT / ".claude/skills").rglob("*.md")) + list((ROOT / ".claude/agents").glob("*.md")) + list((ROOT / ".claude/commands").glob("*.md")):
    content = md_file.read_text()
    for m in re.finditer(r"mcp__manager-ai__[a-z_]+", content):
        tool = m.group(0)
        if tool not in DOCUMENTED_MCP_TOOLS:
            fail("mcp-ref", f"{md_file.relative_to(ROOT)}: unknown manager-ai tool '{tool}'")

# ─── 9. AGENTS.md workspace paths exist ───────────────────────────
# Proper tree-parser: track parent path via indentation depth
agents_md = (ROOT / "AGENTS.md").read_text()
workspace_block = re.search(r"## Workspace Shape\s+```(.+?)```", agents_md, re.S)
if workspace_block:
    lines = workspace_block.group(1).splitlines()
    # First non-empty line declares the root ("project/")
    stack = []  # list of (depth, name)
    for line in lines:
        # Preserve comment for output-detection, but separate code part
        parts = re.split(r"\s#\s*", line, 1)
        code = parts[0]
        comment = parts[1] if len(parts) > 1 else ""
        m = re.search(r"^(.*?)[├└]── ([a-zA-Z0-9_./-]+?)/?(\s|$)", code)
        if not m:
            continue
        prefix = m.group(1)
        name = m.group(2)
        depth = len(prefix) // 4
        stack = stack[:depth]
        stack.append(name)
        full = "/".join(stack)
        if any(c in full for c in "<>*"):
            continue
        # Skip placeholder path segments (YYYY, MM, DD, WXX, etc.)
        if re.search(r"\b(YYYY|MM|DD|WXX|HH|SS)\b", full):
            continue
        # Skip project-scoped artifacts
        if re.match(r"^projects/", full) and full != "projects":
            continue
        # Skip paths whose comment marks them as skill output (lazy-created on first use)
        if "output" in comment.lower():
            continue
        target = ROOT / full
        if not target.exists():
            fail("agents-ws", f"AGENTS.md lists '{full}' — not found on disk")

# ─── 10. Hooks registered in settings.json ────────────────────────
try:
    settings = json.loads((ROOT / ".claude/settings.json").read_text())
    hooks = settings.get("hooks", {})
    for event, configs in hooks.items():
        for cfg in configs:
            for hk in cfg.get("hooks", []):
                cmd = hk.get("command", "")
                m = re.search(r"\$CLAUDE_PROJECT_DIR/([^\s]+)", cmd)
                if m:
                    script = ROOT / m.group(1)
                    if not script.exists():
                        fail("hook", f"settings.json hook references {m.group(1)} — missing")
                    elif not os.access(script, os.X_OK):
                        fail("hook", f"{m.group(1)}: not executable")
except Exception as e:
    fail("hook", f"settings.json error: {e}")

# ─── 11. Orphan hooks ─────────────────────────────────────────────
hooks_dir = ROOT / ".claude/hooks"
if hooks_dir.exists():
    referenced = (ROOT / ".claude/settings.json").read_text()
    for h in hooks_dir.iterdir():
        if h.is_file() and h.name not in referenced:
            fail("hook-orphan", f".claude/hooks/{h.name} not referenced in settings.json")

# ─── 12. Memory files exist ───────────────────────────────────────
mem_index = (MEMORY / "MEMORY.md").read_text()
for m in re.finditer(r"\]\(([^)]+\.md)\)", mem_index):
    link = m.group(1)
    if not (MEMORY / link).exists():
        fail("memory", f"MEMORY.md links {link} — missing")

# Memory file frontmatter
for mf in sorted(MEMORY.glob("*.md")):
    if mf.name == "MEMORY.md": continue
    content = mf.read_text()
    if not content.startswith("---"):
        fail("memory-fm", f"{mf.name}: no frontmatter"); continue
    try:
        fm = yaml.safe_load(content.split("---", 2)[1])
        for k in ("name", "description", "type"):
            if not fm.get(k):
                fail("memory-fm", f"{mf.name}: missing {k}")
    except yaml.YAMLError as e:
        fail("memory-fm", f"{mf.name}: YAML parse: {e}")

# ─── 13. .mcp.json sanity ─────────────────────────────────────────
try:
    mcp = json.loads((ROOT / ".mcp.json").read_text())
    for name, cfg in mcp.get("mcpServers", {}).items():
        cmd = cfg.get("command")
        if cmd and cmd not in ("npx",) and "/" not in cmd:
            # Check binary on PATH
            r = subprocess.run(["which", cmd], capture_output=True, text=True)
            if r.returncode != 0:
                fail("mcp", f"{name}: command '{cmd}' not on PATH")
except Exception as e:
    fail("mcp", f".mcp.json error: {e}")

# ─── 14. core/mcp/server.py tool count ────────────────────────────
server_py = (ROOT / "core/mcp/server.py").read_text()
tool_decls = re.findall(r"types\.Tool\(\s*name=\"([a-z_]+)\"", server_py)
if len(tool_decls) != len(DOCUMENTED_MCP_TOOLS):
    fail("mcp-count", f"server.py registers {len(tool_decls)} tools, AGENTS.md documents {len(DOCUMENTED_MCP_TOOLS)}")
for t in tool_decls:
    full = f"mcp__manager-ai__{t}"
    if full not in DOCUMENTED_MCP_TOOLS:
        fail("mcp-count", f"server.py registers '{t}' — not in AGENTS.md list")
for t in DOCUMENTED_MCP_TOOLS:
    short = t.replace("mcp__manager-ai__", "")
    if short not in tool_decls:
        fail("mcp-count", f"AGENTS.md documents '{t}' — server.py does not register")

# ─── 15. Setup.sh / init-workspace.sh syntax ──────────────────────
for script in [ROOT / "setup.sh", ROOT / ".claude/hooks/init-workspace.sh"]:
    if script.exists():
        r = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
        if r.returncode != 0:
            fail("shell-syntax", f"{script.relative_to(ROOT)}: {r.stderr.strip()}")

# ─── 16. Gitkeep sentinels for empty dirs ─────────────────────────
for sub in ["library/prompts", "library/systems", "library/skills", "library/agents", "library/commands"]:
    p = ROOT / sub
    if p.exists() and not list(p.iterdir()):
        fail("empty-dir", f"{sub}/ is empty and has no .gitkeep")

# ─── 17. Broken markdown links in tracked docs ────────────────────
tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.md"],
                         capture_output=True, text=True).stdout.splitlines()
for rel in tracked:
    fpath = ROOT / rel
    if not fpath.exists(): continue
    content = fpath.read_text()
    # Strip fenced code blocks — links inside them are template/example, not real refs
    stripped = re.sub(r"```.*?```", "", content, flags=re.S)
    stripped = re.sub(r"`[^`\n]+`", "", stripped)  # inline code too
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", stripped):
        link = m.group(2)
        if link.startswith(("http://", "https://", "mailto:", "#")): continue
        if link.startswith("/"): continue
        if any(c in link for c in "[]<>{}"): continue
        if link in ("URL", "url", "path", "filename"): continue
        target_path = link.split("#", 1)[0]
        if not target_path: continue
        target = (fpath.parent / target_path).resolve()
        if not target.exists():
            fail("md-link", f"{rel}: broken link '{link}'")

# ─── 18. TODO / NEEDS UPDATE / FIXME markers in tracked docs ──────
# Only match top-level standalone markers, not placeholder-bracketed tokens
for rel in tracked:
    fpath = ROOT / rel
    if not fpath.exists(): continue
    if rel in ("GOALS.md",): continue
    content = fpath.read_text()
    for i, line in enumerate(content.splitlines(), 1):
        # Match FIXME/TODO/NEEDS UPDATE — NOT inside square brackets (placeholders)
        for marker in ("FIXME", "TODO:", "[NEEDS UPDATE]"):
            if marker in line:
                # Skip if it's a template instruction example
                if rel.endswith("refresh-goals/SKILL.md") and "NEEDS UPDATE" in line:
                    continue  # intentional reference to the marker itself
                fail("todo-marker", f"{rel}:{i}: {line.strip()[:80]}")
                break

# ─── 19. Tracked .DS_Store / node_modules ─────────────────────────
for rel in tracked:
    if ".DS_Store" in rel or rel.startswith("node_modules/"):
        fail("git-noise", f"tracked but should be ignored: {rel}")

# ─── 20. Empty tracked sentinel files sanity ──────────────────────
# Nothing to check here for now.

# ─── 21. .claude/settings.local.json sanity ───────────────────────
try:
    local = json.loads((ROOT / ".claude/settings.local.json").read_text())
    for perm in local.get("permissions", {}).get("allow", []):
        # Just verify parseable; detailed validation hard
        pass
except Exception as e:
    fail("local-settings", f"settings.local.json: {e}")

# ─── 22. Python deps (core/requirements.txt) ──────────────────────
req = (ROOT / "core/mcp/pyproject.toml")
if req.exists():
    # pyproject exists; pyyaml and mcp should be in there
    txt = req.read_text()
    for dep in ("mcp", "pyyaml"):
        if dep not in txt.lower():
            fail("deps", f"core/mcp/pyproject.toml: missing '{dep}'")

# ─── 23. Slash-command references in skill/agent/command bodies ──
# Only match explicit invocations like "/skill-name" with following space/end/argument
all_invokables = skill_names | command_names
slash_re = re.compile(r"(?<![A-Za-z/])/([a-z][a-z0-9-]{2,})(?=[\s`.,)\]'\"]|$)", re.M)
for md in list((ROOT / ".claude/skills").rglob("*.md")) + list((ROOT / ".claude/agents").glob("*.md")) + list((ROOT / ".claude/commands").glob("*.md")):
    content = md.read_text()
    # Strip code blocks to avoid false positives from example paths
    stripped = re.sub(r"```.*?```", "", content, flags=re.S)
    stripped = re.sub(r"`[^`\n]+`", "", stripped)
    for m in slash_re.finditer(stripped):
        cmd = m.group(1)
        # Common false-positives: paths like /Users, /tmp, /opt, /etc
        if cmd in ("users", "tmp", "opt", "etc", "var", "usr", "bin", "home", "mnt", "root", "dev", "sys", "proc", "private"):
            continue
        if cmd not in all_invokables:
            fail("slash-ref", f"{md.relative_to(ROOT)}: /{cmd} referenced but no matching skill/command")

# ─── 24. Agent tools are all valid Claude Code or MCP tools ──────
VALID_CC_TOOLS = {
    "Read", "Write", "Edit", "Glob", "Grep", "Bash", "WebFetch", "WebSearch",
    "Agent", "NotebookRead", "NotebookEdit", "TodoWrite", "KillShell", "BashOutput",
    "TaskCreate", "TaskUpdate", "TaskList", "TaskGet", "TaskOutput", "TaskStop",
    "Monitor", "AskUserQuestion", "CronCreate", "CronDelete", "CronList",
    "SendMessage", "RemoteTrigger", "TeamCreate", "TeamDelete",
    "EnterPlanMode", "ExitPlanMode", "EnterWorktree", "ExitWorktree",
    "ScheduleWakeup", "ToolSearch", "Skill", "ListMcpResourcesTool", "ReadMcpResourceTool",
    "LS",
}
for agent_md in sorted((ROOT / ".claude/agents").glob("*.md")):
    content = agent_md.read_text()
    fm = yaml.safe_load(content.split("---", 2)[1])
    for t in fm.get("tools", []):
        if t.startswith("mcp__"):
            if t not in DOCUMENTED_MCP_TOOLS and not t.startswith("mcp__perplexity__") and not t.startswith("mcp__granola__"):
                fail("agent-tool", f"{agent_md.name}: tool '{t}' not a known MCP tool")
        elif t not in VALID_CC_TOOLS:
            fail("agent-tool", f"{agent_md.name}: tool '{t}' not a valid Claude Code tool")

# ─── 25. Hook events are valid ───────────────────────────────────
VALID_HOOK_EVENTS = {"PreToolUse", "PostToolUse", "Stop", "SubagentStop",
                     "SessionStart", "SessionEnd", "UserPromptSubmit",
                     "PreCompact", "Notification"}
try:
    settings = json.loads((ROOT / ".claude/settings.json").read_text())
    for event in settings.get("hooks", {}):
        if event not in VALID_HOOK_EVENTS:
            fail("hook-event", f"settings.json: unknown event '{event}'")
except Exception:
    pass

# ─── 26. .mcp.json env-var refs are sensible ──────────────────────
try:
    mcp = json.loads((ROOT / ".mcp.json").read_text())
    for name, cfg in mcp.get("mcpServers", {}).items():
        # env refs inside values like ${VAR}
        for k, v in (cfg.get("env") or {}).items():
            if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
                var = v[2:-1]
                if var not in os.environ and var != "MANAGER_AI_BASE_DIR":
                    # Only warn for perplexity api key etc.
                    if "API_KEY" in var or "TOKEN" in var:
                        fail("mcp-env", f".mcp.json: {name}.env.{k}={v} — env var '{var}' not set")
except Exception:
    pass

# ─── 27. MCP server actually starts ──────────────────────────────
# Run a quick import test, not a full boot (boot would hang waiting for stdin)
r = subprocess.run(
    ["uv", "run", "python3", "-c", "import sys; sys.path.insert(0, '.'); import server; print('ok')"],
    cwd=str(ROOT / "core/mcp"),
    capture_output=True, text=True, timeout=30,
)
if r.returncode != 0 or "ok" not in r.stdout:
    fail("mcp-boot", f"core/mcp/server.py import failed: {r.stderr[:200]}")

# ─── Output ──────────────────────────────────────────────────────
if not issues:
    print("✓ ALL CHECKS PASS")
    sys.exit(0)
else:
    by_cat = {}
    for cat, msg in issues:
        by_cat.setdefault(cat, []).append(msg)
    for cat in sorted(by_cat):
        print(f"\n=== {cat} ({len(by_cat[cat])}) ===")
        for msg in by_cat[cat][:50]:
            print(f"  • {msg}")
        if len(by_cat[cat]) > 50:
            print(f"  ... +{len(by_cat[cat]) - 50} more")
    print(f"\nTOTAL: {len(issues)} issues in {len(by_cat)} categories")
    sys.exit(1)
