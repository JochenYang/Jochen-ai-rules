#!/bin/bash
# Danger guard PreToolUse hook
# Reads JSON from stdin (Claude Code hook protocol).
# Inspects Bash tool invocations and either denies catastrophic commands or
# asks for explicit user confirmation on irreversible / publish / force ops.
#
# Output contract: https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/hooks
#   hookSpecificOutput.permissionDecision: "allow" | "deny" | "ask"

cat | python3 -c "
import json, re, sys

try:
    data = json.loads(sys.stdin.read())
except Exception:
    sys.exit(0)

tool_name = data.get('tool_name', '')
if tool_name != 'Bash':
    sys.exit(0)

cmd = (data.get('tool_input') or {}).get('command', '') or ''

# Normalise: collapse whitespace so 'git  push   --force' still matches.
norm = re.sub(r'\s+', ' ', cmd.strip())

# Step 1: hard-deny catastrophic patterns (no recovery path).
DENY_PATTERNS = [
    (r'\brm\s+(-[a-zA-Z]*[rR][a-zA-Z]*\s+)+(/|~|/\*|\*)(\s|$|[;&|])', 'rm -rf against root, home, or wildcard'),
    (r':\(\)\s*\{\s*:\|:&\s*\};:', 'fork bomb'),
    (r'\bcurl\b[^|]*\|\s*(bash|sh|zsh)\b', 'curl piped to shell'),
    (r'\bwget\b[^|]*\|\s*(bash|sh|zsh)\b', 'wget piped to shell'),
    (r'\bmkfs\.[a-z0-9]+\b', 'mkfs format'),
    (r'\bdd\s+if=.+of=/dev/(sd|nvme|hd)', 'dd to raw disk'),
    (r'>\s*/dev/sd[a-z]', 'write to raw disk device'),
    (r'\bDROP\s+DATABASE\b', 'DROP DATABASE'),
]
for pattern, label in DENY_PATTERNS:
    if re.search(pattern, norm, re.IGNORECASE):
        print(json.dumps({
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': f'Blocked: {label}. This command is irreversible and not allowed without explicit owner override.'
            }
        }))
        sys.exit(0)

# Step 2: ask for confirmation on irreversible / publish / force ops.
ASK_PATTERNS = [
    (r'\bgit\s+push\b.*\s(--force|-f)\b', 'git push --force'),
    (r'\bgit\s+push\b.*--force-with-lease\b', 'git push --force-with-lease'),
    (r'\bgit\s+reset\s+--hard\b', 'git reset --hard'),
    (r'\bgit\s+clean\s+-[a-z]*[fdx][a-z]*', 'git clean -fdx'),
    (r'\bgit\s+checkout\s+\.\b', 'git checkout . (discards working tree)'),
    (r'\bgit\s+branch\s+-D\b', 'git branch -D (force delete)'),
    (r'\b(npm|yarn|pnpm)\s+publish\b', 'package publish'),
    (r'\bchmod\s+-R\s+[0-7]*7[0-7]*7[0-7]*7', 'chmod -R 777'),
    (r'\bsudo\s+rm\b', 'sudo rm'),
    (r'\bTRUNCATE\s+TABLE\b', 'TRUNCATE TABLE'),
    (r'\bDELETE\s+FROM\b(?!.*\bWHERE\b)', 'DELETE FROM without WHERE'),
    (r'\bkubectl\s+delete\s+(ns|namespace|pv|pvc)\b', 'kubectl delete namespace/pv/pvc'),
    (r'\bdocker\s+system\s+prune\b.*-a', 'docker system prune -a'),
    (r'\bterraform\s+(destroy|apply\s+--auto-approve)\b', 'terraform destroy / auto-approve'),
]
for pattern, label in ASK_PATTERNS:
    if re.search(pattern, norm, re.IGNORECASE):
        print(json.dumps({
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'ask',
                'permissionDecisionReason': f'Confirm intent: detected {label}. This operation is irreversible or affects shared state. Reply with explicit approval to proceed.'
            }
        }))
        sys.exit(0)
"

exit 0
