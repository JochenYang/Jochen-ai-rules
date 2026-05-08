# Prompt linter UserPromptSubmit hook
# Reads JSON from stdin (Claude Code hook protocol).
# Triggers a clarification reminder when the prompt looks complex.
# Heuristic (after stripping fenced code blocks and URLs):
#   - English words > 50, OR
#   - CJK characters > 120, OR
#   - Total non-whitespace characters > 400.

$ErrorActionPreference = 'SilentlyContinue'

# Read stdin (ReadToEnd blocks in -File mode; ReadLine loop is reliable).
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

# Step 1: strip fenced code blocks and inline code.
$clean = [regex]::Replace($prompt, '(?s)```.*?```', ' ')
$clean = [regex]::Replace($clean, '`[^`]*`', ' ')

# Step 2: strip URLs.
$clean = [regex]::Replace($clean, '(?:https?|ftp|file)://\S+', ' ')

# Step 3: counts.
$cjkCount   = ([regex]::Matches($clean, '[\u4e00-\u9fff]')).Count
$wordCount  = ([regex]::Matches($clean, '[A-Za-z][A-Za-z0-9_\-]*')).Count
$totalChars = ([regex]::Replace($clean, '\s+', '')).Length

$wordLimit = 50
$cjkLimit  = 120
$charLimit = 400

$triggers = @()
if ($wordCount  -gt $wordLimit) { $triggers += "$wordCount English words (>$wordLimit)" }
if ($cjkCount   -gt $cjkLimit)  { $triggers += "$cjkCount Chinese characters (>$cjkLimit)" }
if ($totalChars -gt $charLimit) { $triggers += "$totalChars non-whitespace characters (>$charLimit)" }

if ($triggers.Count -gt 0) {
    $detail = $triggers -join ', '
    $msg = "Prompt complexity notice: detected $detail. " +
           "Before proceeding, restate the single most important outcome the user wants " +
           "and confirm scope, constraints, and the first concrete step."
    $output = [ordered]@{ systemMessage = $msg } | ConvertTo-Json -Compress
    Write-Output $output
}

exit 0
