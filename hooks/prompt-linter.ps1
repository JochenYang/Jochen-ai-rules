# Prompt linter UserPromptSubmit hook
# Reads JSON from stdin (Claude Code hook protocol)
# If user prompt exceeds 50 words, injects a clarification reminder via systemMessage

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

$prompt = $hookData.prompt
if (-not $prompt) {
    exit 0
}

# Count non-empty words
$wordCount = ($prompt -split '\s+' | Where-Object { $_ -ne '' }).Count

if ($wordCount -gt 50) {
    $msg = "Prompt complexity notice: The user's prompt contains $wordCount words. " +
           "Before proceeding, confirm the single most important outcome they want from this request."
    $output = [ordered]@{ systemMessage = $msg } | ConvertTo-Json -Compress
    Write-Output $output
}

exit 0
