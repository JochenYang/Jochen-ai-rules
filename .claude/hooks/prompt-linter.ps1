# Conditional prompt linter
# If prompt > 50 words, check if desired outcome is clear

$prompt = $env:CLAUDE_USER_PROMPT
$wordCount = ($prompt -split '\s+').Count

if ($wordCount -gt 50) {
    Write-Host "💡 Note: Your prompt has $wordCount words. Consider clarifying: What specific outcome do you want?"
}
