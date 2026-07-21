#!/usr/bin/env bash

# PM Operating System Setup Script
# Creates directories, copies templates, and guides you through goals creation
#
# ┌─────────────────────────────────────────────────────────────────────┐
# │ AGENT INSTRUCTIONS                                                  │
# │                                                                     │
# │ If you are an AI agent (e.g. Claude Code) reading this file:        │
# │ Do NOT execute this script as bash. Instead, walk through the       │
# │ setup interactively using your tools. Use AskUserQuestion (or your  │
# │ equivalent interactive tool) to gather answers from the user.       │
# │                                                                     │
# │ Follow these steps:                                                 │
# │                                                                     │
# │ 1. CREATE WORKSPACE STRUCTURE                                       │
# │    - Ensure these directories exist:                                │
# │        tasks/, tasks/archive/                                       │
# │        projects/                                                    │
# │        knowledge/research/projects, knowledge/research/topics       │
# │        knowledge/meetings, knowledge/journals                       │
# │        knowledge/session-reviews, knowledge/decisions               │
# │        knowledge/people, knowledge/reference                        │
# │        knowledge/voice-samples                                      │
# │        knowledge/currency/reports/cli, knowledge/currency/reports/  │
# │        repo   (watcher state home — gitignored live state)          │
# │        library/{prompts,systems,skills,agents,commands}             │
# │    - AGENTS.md ships with the repo (no copy needed)                 │
# │    - If .gitignore doesn't exist, copy from core/templates/gitignore│
# │    - If BACKLOG.md doesn't exist, create it with a short intro      │
# │    - MIGRATION (guarded, idempotent): if knowledge/.granola-sync    │
# │      .json is tracked by git, untrack it with                       │
# │      `git rm --cached` (file stays on disk; never commit a          │
# │      tree-level removal on the user's behalf)                       │
# │    NOTE: the SessionStart hook (.claude/hooks/init-workspace.sh)    │
# │    creates the same set on every session — setup.sh is the manual   │
# │    fallback for users running the script directly.                  │
# │                                                                     │
# │ 2. ASK THE USER THESE 5 QUESTIONS (use AskUserQuestion if you      │
# │    have it, otherwise ask inline):                                  │
# │    Q1: "What's your current role?"                                  │
# │        Example: Product Manager, Senior Engineer, Founder, VP       │
# │    Q2: "What's your primary professional vision?                    │
# │         What are you building toward?"                              │
# │        Example: Become VP Product, Launch a successful product      │
# │    Q3: "In 12 months, what would make you think                     │
# │         'this was a successful year'?"                              │
# │        Example: Shipped 3 major features, Built a team of 10       │
# │    Q4: "What are your objectives for THIS QUARTER (next 90 days)?" │
# │        Example: Launch new feature, Improve activation by 20%      │
# │    Q5: "What are your top 3 priorities right now?                   │
# │         (Be brutally honest)"                                       │
# │        Example: 1. Ship Q1 roadmap, 2. Build thought leadership    │
# │                                                                     │
# │ 3. GENERATE GOALS.md                                                │
# │    Use the answers to populate GOALS.md following the template      │
# │    defined at the bottom of this script (search for "cat > GOALS") │
# │                                                                     │
# │ 4. OFFER TO INSTALL /make-slides DEPENDENCIES                       │
# │    Ask: "The /make-slides skill uses Playwright (HTML → PNG +       │
# │    Google Slides push). Install now? (~50MB npm + ~150MB Chromium   │
# │    if not cached)"                                                  │
# │    If yes and npm is available: run `npm install` at repo root      │
# │    (package.json declares playwright; postinstall runs              │
# │    `npx playwright install chromium`).                              │
# │    If skipped, the skill will install lazily on first use.          │
# │                                                                     │
# │ 5. OFFER AUTOMATION (never enabled by default — an explicit choice) │
# │    Present the four options from the SHARED AUTOMATION CHECKLIST    │
# │    below (search "AUTOMATION CHECKLIST" in this file) via           │
# │    AskUserQuestion, stating per option BEFORE selection: its        │
# │    prerequisites, its enforcement guarantee (per-home table in      │
# │    docs/capabilities.md), and its reporting reach. Rules:           │
# │    - Only report-only watcher runs are ever scheduled; full cycles  │
# │      are owner-typed and never schedulable.                         │
# │    - local (wrapper): write ~/Library/LaunchAgents/                 │
# │      com.personal-os.watch.plist (macOS; template below, search     │
# │      "LAUNCHD TEMPLATE") or print the crontab line (Linux); the     │
# │      invocation carries CE_REPORT_ONLY=1 + the restricted profile   │
# │      flags exactly as in the template. Wire the guard hook into     │
# │      .claude/settings.local.json (PreToolUse → report-only-guard.sh │
# │      — see .claude/hooks/report-only-guard.md for the JSON).        │
# │    - local (Desktop scheduled tasks): only offer if the Desktop app │
# │      is installed (/Applications/Claude.app); disclose the reduced  │
# │      guarantee (per-task dontAsk mode; no env marker — the guard    │
# │      stays inert for these runs; profile rests on dontAsk denies).  │
# │      Missing app → "enable later via Desktop → scheduled tasks".    │
# │    - /loop and in-session cron are NOT offered (no per-run          │
# │      enforcement, no marker — see docs/capabilities.md); mention    │
# │      them only if asked, labeled explicitly-degraded.               │
# │    - cloud: BEFORE selection show the disclosure checklist          │
# │      (prereqs: repo pushed to GitHub; claude.ai account with        │
# │      Claude Code on web, Pro/Max/Team/Enterprise; 2FA enabled and a │
# │      spend alert set). Disclose: repo + fetched content are         │
# │      processed on Anthropic infrastructure; transcripts are         │
# │      retained per account settings; runs bill against the           │
# │      subscription/usage credits; pushes are restricted to claude/*  │
# │      branches by default (keep that default); the GitHub grant      │
# │      stands until the owner revokes it; cloud reports do NOT land   │
# │      in the local repo — they surface via the routine transcript    │
# │      or by asking Claude to read the routine's results back.        │
# │      Then guide: run `/schedule` in Claude Code → routine prompt    │
# │      exactly "/repo-watch report-only" (thin prompt), cadence       │
# │      weekly, env var CE_REPORT_ONLY=1 in the routine's environment. │
# │    - hybrid: wrapper for /cli-watch + cloud for /repo-watch.        │
# │    - skip: schedule NOTHING; state "nothing is scheduled anywhere"  │
# │      in the summary and note the enable-later path (re-run setup    │
# │      or read .claude/hooks/report-only-guard.md).                   │
# │    - RE-RUN semantics (idempotent): detect a previous choice (the   │
# │      plist, the settings.local.json hook entry, or a routine the    │
# │      user reports); changing to skip = TEARDOWN: launchctl unload + │
# │      delete the plist, remove the hook entry, and walk the user     │
# │      through deleting the cloud routine AND revoking the GitHub     │
# │      grant (claude.ai → settings → connected repos). Never          │
# │      duplicate an existing schedule on re-run.                      │
# │                                                                     │
# │ 6. SUMMARIZE                                                        │
# │    Tell the user what was created and suggest next steps:           │
# │    - Review GOALS.md and refine as needed                           │
# │    - Read AGENTS.md to understand how the AI agent works            │
# │    - Start adding tasks or notes to BACKLOG.md                      │
# │    - Say `/process-backlog` to triage, or `/morning` to begin       │
# │    - State the automation posture chosen (including "skip: nothing  │
# │      scheduled anywhere") and how to change it later                │
# └─────────────────────────────────────────────────────────────────────┘

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

ask_question() {
    local prompt="$1"
    local example="$2"
    local response=""

    # Print prompt to terminal (stderr so it's not captured)
    echo "" >&2
    echo "$prompt" >&2
    if [ -n "$example" ]; then
        echo -e "${BLUE}$example${NC}" >&2
    fi
    read -r response
    # Return answer to stdout (gets captured)
    echo "$response"
}

ask_multiline() {
    local prompt="$1"
    local response=""

    echo ""
    echo "$prompt"
    echo "(Type your answer, then press Ctrl+D when done)"
    echo ""
    response=$(cat)
    echo "$response"
}

# Start setup
clear
print_header "Welcome to PM Operating System Setup"

echo "This setup will help you:"
echo "  1. Create your workspace structure"
echo "  2. Define your goals and priorities"
echo "  3. Configure your AI assistant"
echo ""
echo "Takes about 2 minutes. Be honest and specific."
echo ""
read -p "Press Enter to begin..."

# Create directories
print_header "Creating Workspace"

WORKSPACE_DIRS=(
    "tasks"
    "tasks/archive"
    "projects"
    "knowledge/research/projects"
    "knowledge/research/topics"
    "knowledge/meetings"
    "knowledge/journals"
    "knowledge/session-reviews"
    "knowledge/decisions"
    "knowledge/people"
    "knowledge/reference"
    "knowledge/voice-samples"
    "knowledge/currency/reports/cli"
    "knowledge/currency/reports/repo"
    "library/prompts"
    "library/systems"
    "library/skills"
    "library/agents"
    "library/commands"
)

for dir in "${WORKSPACE_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_info "Directory exists: $dir/"
    else
        mkdir -p "$dir"
        print_success "Created: $dir/"
    fi
done

# Copy template files
print_header "Setting Up Templates"

if [ -f "AGENTS.md" ]; then
    print_info "File exists: AGENTS.md"
else
    print_info "AGENTS.md not found — it ships with the repo"
fi

if [ ! -f ".gitignore" ] && [ -f "core/templates/gitignore" ]; then
    cp "core/templates/gitignore" ".gitignore"
    print_success "Copied: .gitignore"
else
    print_info "File exists: .gitignore (preserving your version)"
fi

# Migration (guarded, idempotent): the granola sync cursor is per-machine
# runtime state and must never be tracked. Untrack it only where it was
# tracked; the working file is preserved and no commit is made on the
# user's behalf — a pull must never delete an adopter's live cursor.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if git ls-files --error-unmatch knowledge/.granola-sync.json >/dev/null 2>&1; then
        git rm --cached --quiet knowledge/.granola-sync.json
        print_success "Untracked knowledge/.granola-sync.json (file kept on disk)"
    fi
fi

# Create BACKLOG.md
if [ ! -f "BACKLOG.md" ]; then
    cat > "BACKLOG.md" << 'EOF'
# Backlog

Drop raw notes, ideas, or todos here. No structure needed — one bullet per item.

When ready, say `/process-backlog` and the assistant will classify each item
into a task or project, check for duplicates, and ask about anything ambiguous.

## Inbox

EOF
    print_success "Created: BACKLOG.md"
else
    print_info "File exists: BACKLOG.md"
fi

# Goals creation
print_header "Building Your Personal Goals"

echo "Now let's create your GOALS.md - the heart of PM Operating System."
echo ""
echo "I'll ask you about your goals and priorities."
echo "This helps your AI agent make smarter decisions about task priorities."
echo ""
echo "Be honest and specific - this is for you, not anyone else."
echo "You can always edit GOALS.md later to refine your thinking."
echo ""
read -p "Ready to dive in? Press Enter to start..."

# Collect answers (keeping it short - 5 essential questions)

# Section 1: Current Situation
print_header "1. Current Situation"

ans_role=$(ask_question \
    "What's your current role?" \
    "Product Manager, Senior Engineer, Founder, VP Product")

# Section 2: Vision
print_header "2. Your Vision"

ans_vision=$(ask_question \
    "What's your primary professional vision? What are you building toward?" \
    "Become VP Product, Launch a successful product, Build a thriving consultancy")

# Section 3: Success This Year
print_header "3. Success This Year"

ans_success_12mo=$(ask_question \
    "In 12 months, what would make you think 'this was a successful year'?" \
    "Shipped 3 major features, Built a team of 10, Became recognized expert in my field")

# Section 4: This Quarter
print_header "4. This Quarter"

ans_q1_goals=$(ask_question \
    "What are your objectives for THIS QUARTER (next 90 days)?" \
    "Launch new feature, Improve activation by 20%, Build PM practice")

# Section 5: Top Priorities
print_header "5. Top Priorities"

ans_top3=$(ask_question \
    "What are your top 3 priorities right now? (Be brutally honest)" \
    "1. Ship Q1 roadmap, 2. Build thought leadership, 3. Develop AI product skills")

# Set empty placeholders for sections user can fill in later
ans_company=""
ans_vision_why=""
ans_success_5yr=""
ans_current_focus=""
ans_q1_metrics=""
ans_skills=""
ans_relationships=""
ans_challenges=""
ans_opportunities=""

# Generate GOALS.md
print_header "Generating Your GOALS.md"

CURRENT_DATE=$(date +"%B %d, %Y")

cat > "GOALS.md" << EOF
# Goals & Strategic Direction

*Last updated: ${CURRENT_DATE}*

## Current Context

### What's your current role?
${ans_role}${ans_company:+ at }${ans_company}

### What's your primary professional vision? What are you building toward?
${ans_vision}

${ans_vision_why:+**Why this matters:**
${ans_vision_why}}

## Success Criteria

### In 12 months, what would make you think 'this was a successful year'?
${ans_success_12mo}

### What's your 5-year north star? Where do you want to be?
${ans_success_5yr}

## Current Focus Areas

### What are you actively working on right now?
${ans_current_focus}

### What are your objectives for THIS QUARTER (next 90 days)?
${ans_q1_goals}

${ans_q1_metrics:+**How will you measure success on those quarterly objectives?**
${ans_q1_metrics}}

### What skills do you need to develop to achieve your vision?
${ans_skills}

### What key relationships or network do you need to build?
${ans_relationships}

## Strategic Context

### What's currently blocking you or slowing you down?
${ans_challenges}

### What opportunities are you exploring or considering?
${ans_opportunities}

## Priority Framework

When evaluating new tasks and commitments:

**P0 (Critical/Urgent)** - Must do THIS WEEK:
- Directly advances quarterly objectives
- Time-sensitive opportunities
- Critical stakeholder communication
- Immediate blockers to remove

**P1 (Important)** - This month:
- Builds key skills or expertise
- Advances product strategy
- Significant career development
- High-value learning opportunities

**P2 (Normal)** - Scheduled work:
- Supports broader objectives
- Maintains stakeholder relationships
- Operational efficiency
- General learning and exploration

**P3 (Low)** - Nice to have:
- Administrative tasks
- Speculative projects
- Activities without clear advancement value

## What are your top 3 priorities right now?

${ans_top3}

---

**Your AI assistant uses this document to prioritize tasks and suggest what to work on each day.**

*Review and update this weekly as your priorities shift.*

EOF

print_success "Created: GOALS.md"

# ── Optional: Install Node deps for /make-slides ──────────────────────
print_header "Optional: /make-slides dependencies"

echo "The /make-slides skill builds presentation decks as HTML/CSS and"
echo "optionally pushes them to Google Slides. It requires Playwright."
echo ""
echo "Install now?"
echo "  - playwright npm package (~50MB)"
echo "  - Chromium browser (~150MB, skipped if already cached)"
echo ""
read -p "Install Playwright? [Y/n] " install_pw
install_pw=${install_pw:-Y}

if [[ "$install_pw" =~ ^[Yy] ]]; then
    if command -v npm >/dev/null 2>&1; then
        print_info "Running: npm install (this may take a minute)..."
        if npm install --no-audit --no-fund; then
            print_success "Playwright installed — /make-slides is ready"
        else
            print_warning "npm install failed — check Node.js version (requires >=18)"
            print_info "You can retry later by running 'npm install' in this directory"
        fi
    else
        print_warning "npm not found — install Node.js 18+ from https://nodejs.org"
        print_info "After installing Node, run 'npm install' in this directory to enable /make-slides"
    fi
else
    print_info "Skipped. You can install later with 'npm install' in this directory"
    print_info "The /make-slides skill will also prompt to install on first use"
fi

# ── Automation offer (R5: explicit choice, never a default) ───────────
#
# AUTOMATION CHECKLIST — the single source both setup halves render.
# Options (report-only watcher runs ONLY; full cycles are owner-typed,
# never schedulable):
#   1) local-wrapper  — launchd/cron runs `claude -p "/cli-watch report-only"`
#      weekly under the restricted profile (CE_REPORT_ONLY=1,
#      --permission-mode dontAsk, --disallowedTools Bash) + guard hook in
#      .claude/settings.local.json.
#      Prereqs: claude CLI on PATH; machine awake at the schedule time.
#      Enforcement: FULL (per-run profile + env marker; see
#      docs/capabilities.md per-home table). Reports: repo-visible under
#      knowledge/currency/reports/.
#   2) local-desktop  — Claude Desktop scheduled task (app must be open).
#      Prereqs: Desktop app installed. Enforcement: PARTIAL (per-task
#      dontAsk mode; no env marker, guard inert) — reduced guarantee,
#      disclosed. Reports: repo-visible.
#   3) cloud          — claude.ai routine running "/repo-watch report-only"
#      (≥1h cadence; weekly suggested). Prereqs: repo pushed to GitHub;
#      claude.ai account with Claude Code on web (Pro/Max/Team/Enterprise);
#      2FA enabled; spend alert set. Disclosure: processed on Anthropic
#      infrastructure; transcripts retained; billed to the subscription;
#      pushes limited to claude/* branches (keep that default); the GitHub
#      grant stands until YOU revoke it; reports surface via the routine
#      transcript or read-back — NOT as local repo files.
#   4) skip           — nothing scheduled anywhere. Enable later by
#      re-running setup.
# NOT offered as enforced homes: /loop and in-session cron (no per-run
# tool scoping, no scheduled-origin marker — docs/capabilities.md).
# Teardown on re-run: unload+delete the plist, remove the hook entry,
# delete the cloud routine AND revoke its GitHub grant.

PLIST_PATH="$HOME/Library/LaunchAgents/com.personal-os.watch.plist"

write_launchd_plist() {
    # LAUNCHD TEMPLATE — weekly Monday 09:17 local, report-only profile.
    local repo_dir="$1" claude_bin="$2"
    mkdir -p "$HOME/Library/LaunchAgents"
    cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.personal-os.watch</string>
  <key>WorkingDirectory</key><string>${repo_dir}</string>
  <key>EnvironmentVariables</key><dict>
    <key>CE_REPORT_ONLY</key><string>1</string>
  </dict>
  <key>ProgramArguments</key><array>
    <string>${claude_bin}</string>
    <string>-p</string>
    <string>/cli-watch report-only</string>
    <string>--permission-mode</string><string>dontAsk</string>
    <string>--disallowedTools</string><string>Bash</string>
    <string>--allowed-tools</string>
    <string>Read Glob Grep WebSearch WebFetch Write Edit Skill</string>
  </array>
  <key>StartCalendarInterval</key><dict>
    <key>Weekday</key><integer>1</integer>
    <key>Hour</key><integer>9</integer>
    <key>Minute</key><integer>17</integer>
  </dict>
  <key>StandardOutPath</key><string>${repo_dir}/knowledge/currency/launchd.out.log</string>
  <key>StandardErrorPath</key><string>${repo_dir}/knowledge/currency/launchd.err.log</string>
</dict></plist>
PLIST
}

print_header "Automation (optional — nothing runs unless you choose it)"

echo "The currency watchers (/cli-watch, /repo-watch) can run scheduled"
echo "REPORT-ONLY cycles: they read their baseline, fetch only the delta,"
echo "write a dated report, and stop. They never modify the repo; adopting"
echo "anything always remains a manual, owner-run step."
echo ""
echo "  1) local-wrapper — launchd/cron + claude CLI (full enforcement:"
echo "     per-run restricted profile + guard marker; repo-visible reports)"
echo "  2) local-desktop — Claude Desktop scheduled task (partial"
echo "     enforcement: per-task dontAsk, no guard marker — disclosed)"
echo "  3) cloud — claude.ai routine (runs on Anthropic infrastructure;"
echo "     billed to your plan; GitHub grant until revoked; reports in the"
echo "     routine transcript, NOT local files; needs GitHub push + 2FA +"
echo "     a spend alert)"
echo "  4) skip — schedule nothing (enable later by re-running setup)"
echo ""

if [ -f "$PLIST_PATH" ]; then
    print_info "Existing schedule detected: $PLIST_PATH"
    read -p "Keep it (k), or tear it down (t)? [k/t] " keep_or_teardown
    if [[ "$keep_or_teardown" =~ ^[Tt] ]]; then
        launchctl unload "$PLIST_PATH" 2>/dev/null || true
        rm -f "$PLIST_PATH"
        print_success "Removed the launchd schedule (nothing scheduled locally now)"
        print_info "If you also created a cloud routine: delete it at claude.ai/code/routines"
        print_info "AND revoke its GitHub grant (claude.ai settings → connected repos)."
    fi
fi

read -p "Choose automation [1-4, default 4]: " auto_choice
auto_choice=${auto_choice:-4}

case "$auto_choice" in
    1)
        CLAUDE_BIN="$(command -v claude || true)"
        if [ -z "$CLAUDE_BIN" ]; then
            print_warning "claude CLI not found on PATH — install Claude Code first, then re-run setup"
        elif [ "$(uname)" = "Darwin" ]; then
            write_launchd_plist "$(pwd)" "$CLAUDE_BIN"
            launchctl unload "$PLIST_PATH" 2>/dev/null || true
            if launchctl load "$PLIST_PATH"; then
                print_success "Scheduled: weekly /cli-watch report-only (Mon 09:17, launchd)"
                print_info "Guard hook: wire it per .claude/hooks/report-only-guard.md into .claude/settings.local.json"
                print_info "Teardown any time: re-run setup and choose teardown, or: launchctl unload $PLIST_PATH && rm $PLIST_PATH"
            else
                print_warning "launchctl load failed — plist written to $PLIST_PATH; load it manually"
            fi
        else
            print_info "Linux: add this crontab line (crontab -e):"
            echo "  17 9 * * 1 cd $(pwd) && CE_REPORT_ONLY=1 $CLAUDE_BIN -p '/cli-watch report-only' --permission-mode dontAsk --disallowedTools Bash --allowed-tools 'Read Glob Grep WebSearch WebFetch Write Edit Skill'"
        fi
        ;;
    2)
        if [ -d "/Applications/Claude.app" ]; then
            print_info "In the Claude Desktop app: Scheduled tasks → New task →"
            print_info "  prompt: /cli-watch report-only   (thin prompt — the skill holds the logic)"
            print_info "  working folder: $(pwd) · permission mode: dontAsk · cadence: weekly"
            print_warning "Reduced guarantee (disclosed): Desktop tasks carry no scheduled-origin marker, so the guard hook stays inert for them; enforcement rests on the per-task dontAsk mode."
        else
            print_info "Claude Desktop not found — enable later via the Desktop app's Scheduled tasks once installed."
        fi
        ;;
    3)
        echo ""
        print_warning "Cloud disclosure (read before proceeding):"
        echo "  - Your repo and everything fetched are processed on Anthropic infrastructure."
        echo "  - Run transcripts are retained per your claude.ai account settings."
        echo "  - Runs bill against your subscription/usage credits."
        echo "  - Keep the default claude/* branch-push restriction for this repo."
        echo "  - The GitHub grant stands until YOU revoke it (claude.ai settings)."
        echo "  - Reports surface in the routine transcript or by asking Claude to read"
        echo "    them back — they do NOT land as files in this local repo."
        echo "  Prerequisites: repo pushed to GitHub; claude.ai account with Claude Code"
        echo "  on the web (Pro/Max/Team/Enterprise); 2FA enabled; a spend alert set."
        print_info "Then, inside Claude Code, run /schedule with prompt exactly:"
        print_info "  /repo-watch report-only    (weekly; set CE_REPORT_ONLY=1 in the routine's environment)"
        print_info "Teardown later: delete the routine at claude.ai/code/routines AND revoke the GitHub grant."
        ;;
    *)
        print_success "Skip: nothing is scheduled anywhere (no cron, no launchd job, no Desktop task, no cloud routine)."
        print_info "Enable later by re-running ./setup.sh"
        ;;
esac

# Final summary
print_header "Setup Complete!"

echo "PM Operating System is ready to use."
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Review GOALS.md and refine as needed"
echo "2. Read AGENTS.md to understand how your AI agent works"
echo "3. Drop raw notes or todos into BACKLOG.md"
echo "4. Run /process-backlog to triage, or /morning to start your day"
echo ""
print_success "Happy organizing!"
echo ""
