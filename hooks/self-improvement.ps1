# Self-improvement injection hook
# If >= 8 tool calls in a session, append optimization hint

$hint = @"
💡 Tip: Consider using /learn to extract patterns from this session for future reuse.
"@

$count = $env:CLAUDE_TOOL_CALL_COUNT
if ($count -ge 8) {
    Write-Host $hint
}
