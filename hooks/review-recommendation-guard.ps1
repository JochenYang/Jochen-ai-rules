# Stop / SubagentStop hook: validate code-reviewer Recommendation contract.
# Reads JSON from stdin (Claude Code hook protocol).
#
# Trigger: when the assistant's most recent message contains a Review/Recommendation
# section, ensure it ends with a machine-readable verdict:
#     Recommendation: SHIP | NEEDS WORK | BLOCKED
# If the section exists but the verdict is missing or malformed, block the stop.

$ErrorActionPreference = 'SilentlyContinue'

$lines = @()
while ($null -ne ($line = [Console]::In.ReadLine())) { $lines += $line }
$rawInput = $lines -join "`n"
try {
    $hookData = $rawInput | ConvertFrom-Json
} catch {
    exit 0
}

# Avoid infinite loops if our previous block already triggered.
if ($hookData.stop_hook_active) { exit 0 }

$transcriptPath = $hookData.transcript_path
if (-not $transcriptPath -or -not (Test-Path -LiteralPath $transcriptPath -PathType Leaf)) { exit 0 }

# Tail the JSONL transcript and pull the last assistant text payload.
$entries = Get-Content -LiteralPath $transcriptPath -Encoding UTF8
[Array]::Reverse($entries)

$lastAssistantText = ''
foreach ($raw in $entries) {
    $trim = $raw.Trim()
    if (-not $trim) { continue }
    try {
        $entry = $trim | ConvertFrom-Json
    } catch { continue }
    $role = if ($entry.role) { $entry.role } else { $entry.type }
    if ($role -ne 'assistant') { continue }

    $content = if ($entry.content) { $entry.content } else { $entry.message }
    if ($content -is [System.Array]) {
        $parts = @()
        foreach ($block in $content) {
            if ($block.type -eq 'text' -and $block.text) { $parts += [string]$block.text }
        }
        $content = $parts -join "`n"
    }
    if ($content -is [string] -and $content.Trim()) {
        $lastAssistantText = [string]$content
        break
    }
}

if (-not $lastAssistantText) { exit 0 }

# Detection: only validate when this looks like a review output.
$signals = @(
    '(?m)^##\s*Recommendation\s*$',
    '(?im)^##\s*Review\b',
    '(?im)^#\s*Code Review Report\b',
    '(?i)\bcode-reviewer\b.*HANDOFF'
)
$isReview = $false
foreach ($p in $signals) {
    if ([regex]::IsMatch($lastAssistantText, $p)) { $isReview = $true; break }
}
if (-not $isReview) { exit 0 }

# Validation: must contain canonical Recommendation verdict.
$verdict = '(?i)Recommendation\s*:?\s*\*{0,2}\s*(SHIP|NEEDS\s+WORK|BLOCKED)\s*\*{0,2}'
if ([regex]::IsMatch($lastAssistantText, $verdict)) { exit 0 }

$reason = "Review output detected but the canonical Recommendation verdict is missing or malformed. " +
          "Re-emit the review with a final line in this exact form:`n" +
          "    Recommendation: SHIP | NEEDS WORK | BLOCKED`n" +
          "Choose exactly one value. Legacy wording (Pass / Request Changes / Block) is not parsed by the orchestrator."

$output = [ordered]@{ decision = 'block'; reason = $reason } | ConvertTo-Json -Compress
Write-Output $output
exit 0
