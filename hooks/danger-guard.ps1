# Danger guard PreToolUse hook
# Reads JSON from stdin (Claude Code hook protocol).
# Inspects Bash tool invocations and either denies catastrophic commands or
# asks for explicit user confirmation on irreversible / publish / force ops.

$ErrorActionPreference = 'SilentlyContinue'

$lines = @()
while ($null -ne ($line = [Console]::In.ReadLine())) { $lines += $line }
$rawInput = $lines -join "`n"
try {
    $hookData = $rawInput | ConvertFrom-Json
} catch {
    exit 0
}

if ($hookData.tool_name -ne 'Bash') { exit 0 }

$cmd = ''
if ($hookData.tool_input -and $hookData.tool_input.command) {
    $cmd = [string]$hookData.tool_input.command
}
if (-not $cmd) { exit 0 }

# Normalise whitespace so 'git  push   --force' still matches.
$norm = [regex]::Replace($cmd.Trim(), '\s+', ' ')

function Emit-Decision($decision, $reason) {
    $payload = [ordered]@{
        hookSpecificOutput = [ordered]@{
            hookEventName            = 'PreToolUse'
            permissionDecision       = $decision
            permissionDecisionReason = $reason
        }
    }
    Write-Output ($payload | ConvertTo-Json -Compress -Depth 5)
}

# Step 1: hard-deny catastrophic patterns.
$denyPatterns = @(
    @{ p = '\brm\s+(-[a-zA-Z]*[rR][a-zA-Z]*\s+)+(/|~|/\*|\*)(\s|$|[;&|])'; label = 'rm -rf against root, home, or wildcard' },
    @{ p = ':\(\)\s*\{\s*:\|:&\s*\};:';                   label = 'fork bomb' },
    @{ p = '\bcurl\b[^|]*\|\s*(bash|sh|zsh)\b';           label = 'curl piped to shell' },
    @{ p = '\bwget\b[^|]*\|\s*(bash|sh|zsh)\b';           label = 'wget piped to shell' },
    @{ p = '\bmkfs\.[a-z0-9]+\b';                          label = 'mkfs format' },
    @{ p = '\bdd\s+if=.+of=/dev/(sd|nvme|hd)';             label = 'dd to raw disk' },
    @{ p = '>\s*/dev/sd[a-z]';                             label = 'write to raw disk device' },
    @{ p = '\bDROP\s+DATABASE\b';                          label = 'DROP DATABASE' }
)
foreach ($rule in $denyPatterns) {
    if ([regex]::IsMatch($norm, $rule.p, 'IgnoreCase')) {
        Emit-Decision 'deny' "Blocked: $($rule.label). This command is irreversible and not allowed without explicit owner override."
        exit 0
    }
}

# Step 2: ask for confirmation on irreversible / publish / force ops.
$askPatterns = @(
    @{ p = '\bgit\s+push\b.*\s(--force|-f)\b';            label = 'git push --force' },
    @{ p = '\bgit\s+push\b.*--force-with-lease\b';        label = 'git push --force-with-lease' },
    @{ p = '\bgit\s+reset\s+--hard\b';                    label = 'git reset --hard' },
    @{ p = '\bgit\s+clean\s+-[a-z]*[fdx][a-z]*';          label = 'git clean -fdx' },
    @{ p = '\bgit\s+checkout\s+\.\b';                     label = 'git checkout . (discards working tree)' },
    @{ p = '\bgit\s+branch\s+-D\b';                       label = 'git branch -D (force delete)' },
    @{ p = '\b(npm|yarn|pnpm)\s+publish\b';               label = 'package publish' },
    @{ p = '\bchmod\s+-R\s+[0-7]*7[0-7]*7[0-7]*7';        label = 'chmod -R 777' },
    @{ p = '\bsudo\s+rm\b';                               label = 'sudo rm' },
    @{ p = '\bTRUNCATE\s+TABLE\b';                        label = 'TRUNCATE TABLE' },
    @{ p = '\bDELETE\s+FROM\b(?!.*\bWHERE\b)';            label = 'DELETE FROM without WHERE' },
    @{ p = '\bkubectl\s+delete\s+(ns|namespace|pv|pvc)\b'; label = 'kubectl delete namespace/pv/pvc' },
    @{ p = '\bdocker\s+system\s+prune\b.*-a';             label = 'docker system prune -a' },
    @{ p = '\bterraform\s+(destroy|apply\s+--auto-approve)\b'; label = 'terraform destroy / auto-approve' }
)
foreach ($rule in $askPatterns) {
    if ([regex]::IsMatch($norm, $rule.p, 'IgnoreCase')) {
        Emit-Decision 'ask' "Confirm intent: detected $($rule.label). This operation is irreversible or affects shared state. Reply with explicit approval to proceed."
        exit 0
    }
}

exit 0
