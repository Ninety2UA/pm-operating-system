#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Wire the manager-ai MCP server into another AI tool's config.

Targets OpenAI Codex CLI, Cursor, and Google Antigravity. The generated
`.agents/skills/` tree + `AGENTS.md` are already read natively by these tools,
so this only handles the one manual step: registering the MCP server.

DRY-RUN BY DEFAULT — preview only. Pass --apply to write; a timestamped `.bak`
of any existing config is made first. Codex's TOML is spliced as text (existing
tables/comments preserved); Cursor's JSON is merged (other servers preserved);
Antigravity's config path varies by version, so its block is printed for you to
paste rather than auto-written.

Usage:
  uv run core/scripts/install_for.py                       # dry-run, all tools
  uv run core/scripts/install_for.py --tool codex --apply  # write Codex config
  uv run core/scripts/install_for.py --tool cursor --apply
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import sys
from pathlib import Path

_env_root = os.environ.get("PERSONAL_OS_ROOT", "").strip()
ROOT = Path(_env_root).resolve() if _env_root else Path(__file__).resolve().parents[2]
REPO = str(ROOT)
SERVER_DIR = f"{REPO}/core/mcp"

CODEX_CONFIG = Path.home() / ".codex" / "config.toml"
CURSOR_CONFIG = Path.home() / ".cursor" / "mcp.json"
ANTIGRAVITY_CONFIG = Path.home() / ".gemini" / "config" / "mcp_config.json"


# ── Building blocks ──────────────────────────────────────────────────────────
def codex_block() -> str:
    return (
        "[mcp_servers.manager-ai]\n"
        'command = "uv"\n'
        f'args = ["--directory", "{SERVER_DIR}", "run", "server.py"]\n'
        f'env = {{ MANAGER_AI_BASE_DIR = "{REPO}" }}\n'
    )


def mcp_json_entry(extra_env: dict | None = None) -> dict:
    env = {"MANAGER_AI_BASE_DIR": REPO}
    if extra_env:
        env.update(extra_env)
    return {
        "command": "uv",
        "args": ["--directory", SERVER_DIR, "run", "server.py"],
        "env": env,
    }


def _indent(text: str, n: int = 6) -> str:
    pad = " " * n
    return "\n".join(pad + line for line in text.splitlines())


def backup(path: Path) -> Path:
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = path.with_suffix(path.suffix + f".bak.{ts}")
    shutil.copy2(path, bak)
    return bak


# ── Per-tool installers ──────────────────────────────────────────────────────
def install_codex(apply: bool) -> None:
    print(f"\n## Codex CLI → {CODEX_CONFIG}")
    block = codex_block()
    existing = CODEX_CONFIG.read_text() if CODEX_CONFIG.exists() else ""
    # Match the existing [mcp_servers.manager-ai] table up to the next top-level
    # table header (^[) or EOF — so we replace only that block, nothing else.
    pat = re.compile(r"(?ms)^\[mcp_servers\.manager-ai\][^\n]*\n.*?(?=^\[|\Z)")
    if pat.search(existing):
        new = pat.sub(lambda m: block + "\n", existing)
        action = "replace existing [mcp_servers.manager-ai] block"
    elif existing.strip():
        new = existing.rstrip() + "\n\n" + block
        action = "append [mcp_servers.manager-ai] (existing tables preserved)"
    else:
        new = block
        action = "create config with [mcp_servers.manager-ai]"
    print(f"   action: {action}")
    print(_indent(block))
    _write(CODEX_CONFIG, new, apply)


def install_cursor(apply: bool) -> None:
    print(f"\n## Cursor → {CURSOR_CONFIG}")
    text = CURSOR_CONFIG.read_text() if CURSOR_CONFIG.exists() else ""
    try:
        data = json.loads(text) if text.strip() else {}
    except json.JSONDecodeError as e:
        print(f"   ✗ existing {CURSOR_CONFIG} is not valid JSON ({e}); fix it first.", file=sys.stderr)
        return
    servers = data.setdefault("mcpServers", {})
    action = "replace" if "manager-ai" in servers else "add"
    servers["manager-ai"] = mcp_json_entry()
    new = json.dumps(data, indent=2) + "\n"
    print(f"   action: {action} mcpServers['manager-ai'] (other servers preserved)")
    print(_indent(json.dumps({"manager-ai": servers["manager-ai"]}, indent=2)))
    _write(CURSOR_CONFIG, new, apply)


def install_antigravity(apply: bool) -> None:
    # Antigravity's MCP config path varies by version — print, don't auto-write.
    cfg = {"mcpServers": {"manager-ai": mcp_json_entry(
        {"MCP_MODE": "stdio", "DISABLE_CONSOLE_OUTPUT": "true"})}}
    print(f"\n## Antigravity → {ANTIGRAVITY_CONFIG}  (verify path against current docs)")
    print("   Paste this into your Antigravity MCP config (auto-write skipped — path varies):")
    print(_indent(json.dumps(cfg, indent=2)))


def _write(path: Path, content: str, apply: bool) -> None:
    if not apply:
        print("   (dry-run — nothing written; re-run with --apply)")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"   backup: {backup(path)}")
    path.write_text(content)
    print(f"   ✓ wrote {path}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Wire manager-ai MCP into Codex/Cursor/Antigravity")
    ap.add_argument("--tool", choices=["codex", "cursor", "antigravity", "all"], default="all")
    ap.add_argument("--apply", action="store_true", help="actually write configs (default: dry-run)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    if not (ROOT / "core" / "mcp" / "server.py").exists():
        print(f"ERROR: {ROOT}/core/mcp/server.py not found (set PERSONAL_OS_ROOT?)", file=sys.stderr)
        return 2

    print(f"personal-os repo: {REPO}")
    if not args.apply:
        print("(DRY-RUN — preview only. Re-run with --apply to write; a .bak is made first.)")

    installers = {"codex": install_codex, "cursor": install_cursor, "antigravity": install_antigravity}
    for tool in (["codex", "cursor", "antigravity"] if args.tool == "all" else [args.tool]):
        installers[tool](args.apply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
