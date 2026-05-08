#!/bin/bash
# Stop / SubagentStop hook: validate code-reviewer Recommendation contract.
# Reads JSON from stdin (Claude Code hook protocol).
#
# Trigger: when the assistant's most recent message contains a Review/Recommendation
# section, ensure it ends with a machine-readable verdict:
#     Recommendation: SHIP | NEEDS WORK | BLOCKED
# If the section exists but the verdict is missing or malformed, block the stop
# so the orchestrator can ask the agent to emit a valid Recommendation.

cat | python3 -c "
import json, os, re, sys

try:
    data = json.loads(sys.stdin.read())
except Exception:
    sys.exit(0)

# Avoid infinite loops if our previous block already triggered.
if data.get('stop_hook_active'):
    sys.exit(0)

transcript_path = data.get('transcript_path')
if not transcript_path or not os.path.isfile(transcript_path):
    sys.exit(0)

# Tail the JSONL transcript and pull the last assistant text payload.
last_assistant_text = ''
try:
    with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
except Exception:
    sys.exit(0)

for line in reversed(lines):
    line = line.strip()
    if not line:
        continue
    try:
        entry = json.loads(line)
    except Exception:
        continue
    role = entry.get('role') or entry.get('type')
    if role != 'assistant':
        continue
    content = entry.get('content') or entry.get('message') or ''
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'text':
                parts.append(block.get('text', ''))
        content = '\\n'.join(parts)
    if isinstance(content, str) and content.strip():
        last_assistant_text = content
        break

if not last_assistant_text:
    sys.exit(0)

text = last_assistant_text

# Detection: only validate when this looks like a review output.
review_signals = [
    r'^##\s*Recommendation\s*$',
    r'^##\s*Review\b',
    r'^#\s*Code Review Report\b',
    r'\bcode-reviewer\b.*HANDOFF',
]
is_review = any(re.search(p, text, re.MULTILINE | re.IGNORECASE) for p in review_signals)
if not is_review:
    sys.exit(0)

# Validation: must contain canonical Recommendation verdict.
verdict_pattern = r'Recommendation\s*:?\s*\*{0,2}\s*(SHIP|NEEDS\s+WORK|BLOCKED)\s*\*{0,2}'
if re.search(verdict_pattern, text, re.IGNORECASE):
    sys.exit(0)

reason = (
    'Review output detected but the canonical Recommendation verdict is missing or malformed. '
    'Re-emit the review with a final line in this exact form:\\n'
    '    Recommendation: SHIP   | NEEDS WORK | BLOCKED\\n'
    'Choose exactly one value. Legacy wording (Pass / Request Changes / Block) is not parsed by the orchestrator.'
)
print(json.dumps({'decision': 'block', 'reason': reason}))
"

exit 0
