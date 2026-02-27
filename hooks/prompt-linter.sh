#!/bin/bash
# Prompt linter UserPromptSubmit hook
# Reads JSON from stdin (Claude Code hook protocol)
# If user prompt exceeds 50 words, injects a clarification reminder via systemMessage

cat | python3 -c "
import json, sys

try:
    data = json.loads(sys.stdin.read())
except Exception:
    sys.exit(0)

prompt = data.get('prompt', '')
if not prompt:
    sys.exit(0)

words = [w for w in prompt.split() if w]
word_count = len(words)

if word_count > 50:
    msg = (
        f'Prompt complexity notice: The user\\'s prompt contains {word_count} words. '
        'Before proceeding, confirm the single most important outcome they want from this request.'
    )
    print(json.dumps({'systemMessage': msg}))
"

exit 0
