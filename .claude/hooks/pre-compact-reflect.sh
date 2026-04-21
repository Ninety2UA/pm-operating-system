#!/usr/bin/env bash
# PreCompact hook — fires when the conversation is about to be compacted,
# which is a strong signal that this was a long / substantive session.
# Nudges the assistant to offer a /session-review before context gets
# summarised away. Exits 0 always so compaction is never blocked.
#
# Silent on short sessions where a review already exists for today.

set +e
[ -z "$CLAUDE_PROJECT_DIR" ] && exit 0
cd "$CLAUDE_PROJECT_DIR" || exit 0

TODAY_DIR="knowledge/session-reviews/$(date +%Y)/$(date +%m)"
TODAY_PREFIX="$(date +%d)_"

# If a session-review for today already exists, stay quiet.
if [ -d "$TODAY_DIR" ]; then
  if ls "$TODAY_DIR"/${TODAY_PREFIX}*.md >/dev/null 2>&1; then
    exit 0
  fi
fi

# Emit a single-line nudge. Output from a PreCompact hook is visible to the
# assistant in the compaction summary, which prompts the session-end ritual.
echo "💡 Session is long enough to compact — consider running /session-review to capture learnings before context is summarised."
exit 0
