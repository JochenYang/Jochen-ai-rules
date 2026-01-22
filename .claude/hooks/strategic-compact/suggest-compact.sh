#!/bin/bash
# Strategic Compact Hook - Suggest manual compaction at logical intervals
#
# Runs after Edit/Write operations to suggest context compaction
# before context window gets too full.

# Check if context is getting large (approximate based on session history)
SESSIONS_DIR="${HOME}/.claude/sessions"
TODAY=$(date '+%Y-%m-%d')
SESSION_FILE="${SESSIONS_DIR}/${TODAY}-session.tmp"

if [ -f "$SESSION_FILE" ]; then
  # Count completed items as rough context indicator
  completed_count=$(grep -c "^\- \[x\]" "$SESSION_FILE" 2>/dev/null || echo "0")

  # Suggest compaction after significant progress
  if [ "$completed_count" -ge 5 ] 2>/dev/null; then
    echo "[Hook] Consider running /compact to optimize context" >&2
    echo "[Hook] You've completed $completed_count items in this session" >&2
  fi
else
  # New session - no compaction needed yet
  :
fi
