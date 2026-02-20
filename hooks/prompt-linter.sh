#!/bin/bash
# Conditional prompt linter
# If prompt > 50 words, check if desired outcome is clear

prompt="${CLAUDE_USER_PROMPT:-}"
wordCount=$(echo "$prompt" | wc -w)

if [ "$wordCount" -gt 50 ]; then
    echo "💡 Note: Your prompt has $wordCount words. Consider clarifying: What specific outcome do you want?"
fi
