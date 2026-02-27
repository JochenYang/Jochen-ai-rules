#!/bin/bash
# Self-improvement Stop hook
# Reads JSON from stdin (Claude Code hook protocol)
# If session had 8+ tool calls, injects a /learn reminder via systemMessage
# Checks stop_hook_active to prevent infinite loops

cat | python3 -c "
import json, sys

try:
    data = json.loads(sys.stdin.read())
except Exception:
    sys.exit(0)

# Guard: prevent infinite loop
if data.get('stop_hook_active', False):
    sys.exit(0)

transcript_path = data.get('transcript_path', '')
tool_count = 0

if transcript_path:
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = json.load(f)
        for msg in transcript:
            content = msg.get('content', [])
            if isinstance(content, list):
                tool_count += sum(
                    1 for item in content
                    if isinstance(item, dict) and item.get('type') == 'tool_use'
                )
    except Exception:
        # Transcript unreadable; fall back to always suggesting
        tool_count = 99
else:
    sys.exit(0)

if tool_count >= 8:
    msg = (
        f'Session insight: This session used {tool_count} tool calls. '
        'Suggest mentioning /learn to the user so they can capture reusable patterns.'
    )
    print(json.dumps({'systemMessage': msg}))
"

exit 0
