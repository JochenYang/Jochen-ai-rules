#!/bin/bash

# Security vulnerability scanner
# Usage: ./security-scan.sh [--full] [--dependencies] [--secrets] [--sast]

set -e

SCAN_TYPE="full"
OUTPUT_FORMAT="text"

while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            SCAN_TYPE="full"
            shift
            ;;
        --dependencies)
            SCAN_TYPE="dependencies"
            shift
            ;;
        --secrets)
            SCAN_TYPE="secrets"
            shift
            ;;
        --sast)
            SCAN_TYPE="sast"
            shift
            ;;
        --json)
            OUTPUT_FORMAT="json"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

scan_node_dependencies() {
    echo "Scanning Node.js dependencies for vulnerabilities..."

    if command -v npm &> /dev/null; then
        if [ "$OUTPUT_FORMAT" = "json" ]; then
            npm audit --json 2>/dev/null | jq '.' > security-report.json
        else
            npm audit
        fi
    fi

    if command -v snyk &> /dev/null; then
        snyk test --json="$OUTPUT_FORMAT" > snyk-report.json 2>&1 || true
    fi
}

scan_python_dependencies() {
    echo "Scanning Python dependencies for vulnerabilities..."

    if command -v pip-audit &> /dev/null; then
        pip-audit --format "$OUTPUT_FORMAT"
    elif command -v safety &> /dev/null; then
        safety check --output "$OUTPUT_FORMAT"
    else
        echo "No Python security scanner found. Install: pip-audit or safety"
    fi
}

scan_secrets() {
    echo "Scanning for secrets and sensitive data..."

    local patterns=(
        "api_key"
        "secret"
        "password"
        "token"
        "private_key"
        "credential"
    )

    if command -v trufflehog &> /dev/null; then
        trufflehog filesystem . --no-verification --json > secrets-report.json 2>&1 || true
    elif command -v git-secrets &> /dev/null; then
        git-secrets --scan -r .
    else
        echo "No secrets scanner found. Install: trufflehog or git-secrets"
        echo "Common patterns to check manually:"
        for pattern in "${patterns[@]}"; do
            echo "  - $pattern"
        done
    fi
}

scan_sast() {
    echo "Running static application security testing..."

    if command -v eslint &> /dev/null; then
        eslint . --ext .js,.ts,.jsx,.tsx --format "$OUTPUT_FORMAT"
    fi

    if command -v bandit &> /dev/null; then
        bandit -r . -f "$OUTPUT_FORMAT"
    fi

    if command -v semgrep &> /dev/null;
        semgrep --config=auto .
    then
        :
    fi
}

run_full_scan() {
    echo "Running comprehensive security scan..."
    echo "========================================"

    scan_node_dependencies
    scan_python_dependencies
    scan_secrets
    scan_sast

    echo "========================================"
    echo "Security scan completed. Check generated reports."
}

main() {
    case $SCAN_TYPE in
        full)
            run_full_scan
            ;;
        dependencies)
            scan_node_dependencies
            scan_python_dependencies
            ;;
        secrets)
            scan_secrets
            ;;
        sast)
            scan_sast
            ;;
    esac
}

main
