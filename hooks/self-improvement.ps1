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
$learnUsed = $false
$transcriptPath = $hookData.transcript_path

if (-not $transcriptPath -or -not (Test-Path $transcriptPath -PathType Leaf)) {
    # No transcript path; skip suggestion
    exit 0
}

$lines = Get-Content $transcriptPath -Encoding UTF8
foreach ($line in $lines) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    try {
        $msg = $line | ConvertFrom-Json
        $content = $msg.content
        if ($content -is [array]) {
            $toolCallCount += ($content | Where-Object { $_.type -eq 'tool_use' }).Count
        }
        
        if ($msg.role -eq 'user') {
            $text = if ($content -is [string]) { $content }
                    elseif ($content -is [array]) { ($content | Where-Object { $_.type -eq 'text' } | ForEach-Object { $_.text }) -join '' }
                    else { '' }
            if ($text -match '/learn') { $learnUsed = $true }
        }
    } catch {
        continue
    }
}

if ($toolCallCount -ge 8 -and -not $learnUsed) {
    $msg = "Session insight: This session used $toolCallCount tool calls. " +
           "Suggest mentioning /learn to the user so they can capture reusable patterns."
    $output = [ordered]@{ systemMessage = $msg } | ConvertTo-Json -Compress
    Write-Output $output
}

exit 0
