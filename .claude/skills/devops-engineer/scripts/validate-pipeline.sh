#!/bin/bash

# CI/CD pipeline validator
# Usage: ./validate-pipeline.sh --file <pipeline-file>

set -e

PIPELINE_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --file)
            PIPELINE_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$PIPELINE_FILE" ]; then
    echo "Error: Pipeline file required"
    echo "Usage: ./validate-pipeline.sh --file <pipeline-file>"
    exit 1
fi

validate_github_actions() {
    local file="$1"

    echo "Validating GitHub Actions workflow..."

    # Check required fields
    if ! grep -q "on:" "$file"; then
        echo "❌ Missing 'on' trigger"
        return 1
    fi

    # Check job structure
    if ! grep -q "jobs:" "$file"; then
        echo "❌ Missing 'jobs' section"
        return 1
    fi

    # Check runs-on
    if ! grep -q "runs-on:" "$file"; then
        echo "❌ Missing 'runs-on' in jobs"
        return 1
    fi

    # Check for potential issues
    if grep -q "GITHUB_TOKEN" "$file" && ! grep -q "permissions:" "$file"; then
        echo "⚠️  Using GITHUB_TOKEN without explicit permissions"
    fi

    # Check for secrets exposure
    if grep -q '\${{ secrets\.[A-Z_]* }}' "$file"; then
        echo "✓ Secrets referenced correctly"
    fi

    echo "✓ GitHub Actions workflow validated"
    return 0
}

validate_gitlab_ci() {
    local file="$1"

    echo "Validating GitLab CI pipeline..."

    # Check stages
    if ! grep -q "stages:" "$file"; then
        echo "❌ Missing 'stages' section"
        return 1
    fi

    # Check job definitions
    if ! grep -E "^\s+[a-z]+:" "$file" | head -1 | grep -q .; then
        echo "❌ No job definitions found"
        return 1
    fi

    # Check for image
    if ! grep -q "image:" "$file"; then
        echo "⚠️  No default image specified"
    fi

    echo "✓ GitLab CI pipeline validated"
    return 0
}

validate_jenkinsfile() {
    local file="$1"

    echo "Validating Jenkinsfile..."

    # Check for pipeline block
    if ! grep -q "pipeline {" "$file"; then
        echo "❌ Missing 'pipeline' block"
        return 1
    fi

    # Check for agent
    if ! grep -q "agent " "$file"; then
        echo "⚠️  No agent specified"
    fi

    # Check for stages
    if ! grep -q "stages {" "$file"; then
        echo "❌ Missing 'stages' block"
        return 1
    fi

    echo "✓ Jenkinsfile validated"
    return 0
}

detect_pipeline_type() {
    local file="$1"

    if grep -q "github.com" "$file" || [[ "$file" == *.yml ]] || [[ "$file" == *.yaml ]]; then
        if grep -q "on:" "$file"; then
            echo "github-actions"
        elif grep -q "stages:" "$file"; then
            echo "gitlab-ci"
        fi
    elif [[ "$file" == "Jenkinsfile" ]]; then
        echo "jenkins"
    fi
}

main() {
    echo "CI/CD Pipeline Validator"
    echo "========================================"
    echo "File: $PIPELINE_FILE"
    echo ""

    if [ ! -f "$PIPELINE_FILE" ]; then
        echo "❌ File not found: $PIPELINE_FILE"
        exit 1
    fi

    local pipeline_type
    pipeline_type=$(detect_pipeline_type "$PIPELINE_FILE")

    case $pipeline_type in
        github-actions)
            validate_github_actions "$PIPELINE_FILE"
            ;;
        gitlab-ci)
            validate_gitlab_ci "$PIPELINE_FILE"
            ;;
        jenkins)
            validate_jenkinsfile "$PIPELINE_FILE"
            ;;
        *)
            echo "⚠️  Unknown pipeline type"
            echo "Attempting basic validation..."

            if grep -q "on:" "$PIPELINE_FILE"; then
                validate_github_actions "$PIPELINE_FILE"
            elif grep -q "stages:" "$PIPELINE_FILE"; then
                validate_gitlab_ci "$PIPELINE_FILE"
            else
                echo "❌ Could not validate pipeline format"
                exit 1
            fi
            ;;
    esac
}

main
