#!/bin/bash
# Prompt linter UserPromptSubmit hook
# Reads JSON from stdin (Claude Code hook protocol).
# Triggers a clarification reminder when the prompt looks complex.
# Heuristic (after stripping fenced code blocks and URLs):
#   - English words > 50, OR
#   - CJK characters > 120, OR
#   - Total non-whitespace characters > 400.

cat | python3 -c "
import json, re, sys

try:
    data = json.loads(sys.stdin.read())
except Exception:
    sys.exit(0)

prompt = data.get('prompt', '')
if not prompt:
    sys.exit(0)

# Step 1: strip fenced code blocks and inline code to avoid inflating counts.
clean = re.sub(r'\`\`\`[\s\S]*?\`\`\`', ' ', prompt)
clean = re.sub(r'\`[^\`]*\`', ' ', clean)

# Step 2: strip URLs.
clean = re.sub(r'(?:https?|ftp|file)://\S+', ' ', clean)

# Step 3: count.
cjk_count = len(re.findall(r'[\u4e00-\u9fff]', clean))
word_count = len(re.findall(r'[A-Za-z][A-Za-z0-9_\\-]*', clean))
total_chars = len(re.sub(r'\s+', '', clean))

WORD_LIMIT = 50
CJK_LIMIT = 120
CHAR_LIMIT = 400

triggers = []
if word_count > WORD_LIMIT:
    triggers.append(f'{word_count} English words (>{WORD_LIMIT})')
if cjk_count > CJK_LIMIT:
    triggers.append(f'{cjk_count} Chinese characters (>{CJK_LIMIT})')
if total_chars > CHAR_LIMIT:
    triggers.append(f'{total_chars} non-whitespace characters (>{CHAR_LIMIT})')

if triggers:
    detail = ', '.join(triggers)
    msg = (
        f'Prompt complexity notice: detected {detail}. '
        'Before proceeding, restate the single most important outcome the user wants '
        'and confirm scope, constraints, and the first concrete step.'
    )
    print(json.dumps({'systemMessage': msg}))
"

exit 0
