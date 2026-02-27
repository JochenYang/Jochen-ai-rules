# Self-improvement Stop hook
# Reads JSON from stdin (Claude Code hook protocol)
# If session had 8+ tool calls, injects a /learn reminder via systemMessage
# Checks stop_hook_active to prevent infinite loops

$ErrorActionPreference = 'SilentlyContinue'

# Read stdin line by line (ReadToEnd blocks in -File mode; ReadLine loop is reliable)
$lines = @()
while ($null -ne ($line = [Console]::In.ReadLine())) { $lines += $line }
$rawInput = $lines -join "`n"
try {
    $hookData = $rawInput | ConvertFrom-Json
} catch {
    exit 0
}

# Guard: prevent infinite loop (Stop hook called recursively)
if ($hookData.stop_hook_active -eq $true) {
    exit 0
}

# Count tool_use blocks in transcript to decide whether to suggest /learn
$toolCallCount = 0
$transcriptPath = $hookData.transcript_path

if ($transcriptPath -and (Test-Path $transcriptPath -PathType Leaf)) {
    try {
        $transcript = Get-Content $transcriptPath -Raw -Encoding UTF8 | ConvertFrom-Json
        foreach ($msg in $transcript) {
            $content = $msg.content
            if ($content -is [array]) {
                $toolCallCount += ($content | Where-Object { $_.type -eq 'tool_use' }).Count
            }
        }
    } catch {
        # Transcript unreadable; fall back to always suggesting /learn
        $toolCallCount = 99
    }
} else {
    # No transcript path; skip suggestion
    exit 0
}

if ($toolCallCount -ge 8) {
    $msg = "Session insight: This session used $toolCallCount tool calls. " +
           "Suggest mentioning /learn to the user so they can capture reusable patterns."
    $output = [ordered]@{ systemMessage = $msg } | ConvertTo-Json -Compress
    Write-Output $output
}

exit 0
