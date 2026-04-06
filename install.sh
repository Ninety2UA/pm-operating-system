#!/usr/bin/env bash

# PM Operating System - Bootstrap Installer
# Installs dependencies, sets up workspace, and configures the MCP server.
#
# Usage:
#   ./install.sh          Full install (dependencies + workspace + goals)
#   ./install.sh --deps   Install dependencies only
#   ./install.sh --skip-goals  Skip the interactive goals setup

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}ok${NC}  $1"; }
info() { echo -e "${BLUE}..${NC}  $1"; }
warn() { echo -e "${YELLOW}!!${NC}  $1"; }
fail() { echo -e "${RED}ERR${NC} $1"; exit 1; }

SKIP_GOALS=false
DEPS_ONLY=false

for arg in "$@"; do
  case "$arg" in
    --skip-goals) SKIP_GOALS=true ;;
    --deps)       DEPS_ONLY=true ;;
  esac
done

# ── 1. Check prerequisites ────────────────────────────────────────────

echo ""
echo "============================================================"
echo "  PM Operating System - Installer"
echo "============================================================"
echo ""

# Python 3.11+
if command -v python3 &>/dev/null; then
  PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
  PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
  if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 11 ]; then
    ok "Python $PY_VERSION"
  else
    fail "Python 3.11+ required (found $PY_VERSION). Install via: brew install python@3.13"
  fi
else
  fail "Python 3 not found. Install via: brew install python@3.13"
fi

# uv (Python package manager)
if command -v uv &>/dev/null; then
  ok "uv $(uv --version 2>/dev/null | head -1)"
else
  info "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  ok "uv installed"
fi

# git
if command -v git &>/dev/null; then
  ok "git $(git --version | awk '{print $3}')"
else
  fail "git not found. Install via: brew install git (macOS) or apt install git (Linux)"
fi

if [ "$DEPS_ONLY" = true ]; then
  echo ""
  ok "Dependencies verified."
  exit 0
fi

# ── 2. Install Python dependencies ────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
info "Installing MCP server dependencies..."
(cd "$SCRIPT_DIR/core/mcp" && uv sync --quiet)
ok "Python dependencies installed"

# ── 3. Set up workspace directories ───────────────────────────────────

echo ""
info "Creating workspace directories..."

DIRS=(
  Tasks
  Projects
  Knowledge/research/projects
  Knowledge/research/topics
  Knowledge/Meetings
  Knowledge/journals
  Knowledge/session-reviews
  Knowledge/decisions
  Knowledge/People
  Knowledge/Reference
  Library/prompts
  Library/systems
  Library/skills
  Library/agents
  Library/commands
)

for dir in "${DIRS[@]}"; do
  mkdir -p "$SCRIPT_DIR/$dir"
done
ok "Workspace directories ready"

# ── 4. Configure MCP server ───────────────────────────────────────────

if [ ! -f "$SCRIPT_DIR/.mcp.json" ]; then
  info "Creating .mcp.json from template..."
  # Replace relative path with absolute path for the current install location
  sed "s|\"./core/mcp\"|\"$SCRIPT_DIR/core/mcp\"|g; s|\".\"|\"$SCRIPT_DIR\"|g" \
    "$SCRIPT_DIR/.mcp.json.example" > "$SCRIPT_DIR/.mcp.json"
  ok ".mcp.json created with paths pointing to: $SCRIPT_DIR"
else
  info ".mcp.json already exists (skipping)"
fi

# ── 5. Create BACKLOG.md if missing ───────────────────────────────────

if [ ! -f "$SCRIPT_DIR/BACKLOG.md" ]; then
  cat > "$SCRIPT_DIR/BACKLOG.md" << 'EOF'
# Backlog

Drop raw notes or todos here. Say `/process-backlog` when you're ready for triage.
EOF
  ok "BACKLOG.md created"
fi

# ── 6. Verify MCP server ─────────────────────────────────────────────

echo ""
info "Verifying MCP server starts..."
MCP_PID=""
(cd "$SCRIPT_DIR/core/mcp" && MANAGER_AI_BASE_DIR="$SCRIPT_DIR" uv run server.py &>/dev/null) &
MCP_PID=$!
sleep 2

if kill -0 "$MCP_PID" 2>/dev/null; then
  ok "MCP server starts successfully"
  kill "$MCP_PID" 2>/dev/null
  wait "$MCP_PID" 2>/dev/null
else
  warn "MCP server may have issues. Run manually to debug:"
  warn "  cd core/mcp && MANAGER_AI_BASE_DIR=$SCRIPT_DIR uv run server.py"
fi

# ── 7. Interactive goals setup ────────────────────────────────────────

if [ "$SKIP_GOALS" = false ] && [ ! -f "$SCRIPT_DIR/GOALS.md" ]; then
  echo ""
  echo "============================================================"
  echo "  Set up your personal goals"
  echo "============================================================"
  echo ""
  echo "  Your goals drive task prioritization and daily focus."
  echo "  This takes about 2 minutes."
  echo ""
  read -p "  Run goals setup now? (Y/n) " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    bash "$SCRIPT_DIR/setup.sh"
  else
    info "Skipped. Run ./setup.sh later to create your GOALS.md"
  fi
fi

# ── 8. Summary ────────────────────────────────────────────────────────

echo ""
echo "============================================================"
echo "  Setup Complete"
echo "============================================================"
echo ""
echo "  Installed:"
echo "    - MCP server (manager-ai) with task/project management"
echo "    - Workspace directories (Tasks/, Projects/, Knowledge/)"
echo "    - .mcp.json configured for this directory"
echo ""
echo "  Next steps:"
echo ""
echo "  1. Open Claude Code in this directory"
echo "  2. Say: \"Read AGENTS.md and help me get organized\""
echo "  3. Drop ideas into BACKLOG.md, then run /process-backlog"
echo ""
echo "  Optional integrations (add to .mcp.json):"
echo "    - Granola    Meeting sync       https://granola.ai"
echo "    - Slack      Team messaging     https://mcp.slack.com"
echo "    - Perplexity AI-powered research https://perplexity.ai"
echo ""
ok "Happy shipping!"
echo ""
