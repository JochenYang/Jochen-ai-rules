#!/bin/bash
# Self-improvement injection hook
# If >= 8 tool calls in a session, append optimization hint

count=${CLAUDE_TOOL_CALL_COUNT:-0}

if [ "$count" -ge 8 ]; then
    echo "💡 Tip: Consider using /learn to extract patterns from this session for future reuse."
fi
