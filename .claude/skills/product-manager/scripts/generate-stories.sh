#!/bin/bash

# User story generator from requirements
# Usage: ./generate-stories.sh --input <requirements-file>

set -e

INPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$INPUT_FILE" ]; then
    echo "Error: Input file required"
    echo "Usage: ./generate-stories.sh --input <requirements-file>"
    exit 1
fi

generate_stories() {
    local file="$1"

    if [ ! -f "$file" ]; then
        echo "File not found: $file"
        exit 1
    fi

    local content
    content=$(cat "$file")

    echo "# User Stories"
    echo ""
    echo "Generated: $(date +%Y-%m-%d)"
    echo ""

    echo "## Backlog"
    echo ""

    # Parse requirements and generate stories
    local story_id=1
    while IFS= read -r line; do
        if [[ "$line" =~ ^##\ (.*) ]]; then
            local feature="${BASH_REMATCH[1]}"
            echo "### $feature"
            echo ""
        elif [[ "$line" =~ ^-\ \[(Must|Should|Could)\]\ (.*) ]]; then
            local priority="${BASH_REMATCH[1]}"
            local requirement="${BASH_REMATCH[2]}"

            echo "**US-$story_id** (Priority: $priority)"
            echo ""
            echo '```'
            echo "As a user"
            echo "I want to $(echo "$requirement" | tr '[:upper:]' '[:lower:]')"
            echo "So that I can achieve my goals"
            echo '```'
            echo ""
            echo "**Acceptance Criteria:**"
            echo ""
            echo "- [ ] Criterion 1"
            echo "- [ ] Criterion 2"
            echo "- [ ] Criterion 3"
            echo ""
            ((story_id++))
        fi
    done < "$file"
}

generate_stories "$INPUT_FILE" > "user-stories.md"

echo "User stories generated: user-stories.md"
