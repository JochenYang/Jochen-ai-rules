#!/bin/bash

# Code linter and static analyzer
# Usage: ./lint-code.sh [--fix] [--format] [--language]

set -e

AUTO_FIX=false
FORMAT_ONLY=false
LANGUAGE="auto"

while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            AUTO_FIX=true
            shift
            ;;
        --format)
            FORMAT_ONLY=true
            shift
            ;;
        --language)
            LANGUAGE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

run_eslint() {
    if ! command -v eslint &> /dev/null; then
        echo "ESLint not found. Run: npm install -D eslint"
        return
    fi

    if [ "$AUTO_FIX" = true ]; then
        eslint . --ext .js,.ts,.jsx,.tsx --fix
    else
        eslint . --ext .js,.ts,.jsx,.tsx
    fi
}

run_prettier() {
    if ! command -v prettier &> /dev/null; then
        echo "Prettier not found. Run: npm install -D prettier"
        return
    fi

    if [ "$FORMAT_ONLY" = true ]; then
        prettier --write .
    else
        prettier --check .
    fi
}

run_black() {
    if ! command -v black &> /dev/null; then
        echo "Black not found. Run: pip install black"
        return
    fi

    if [ "$AUTO_FIX" = true ]; then
        black .
    else
        black --check .
    fi
}

run_flake8() {
    if ! command -v flake8 &> /dev/null; then
        echo "Flake8 not found. Run: pip install flake8"
        return
    fi

    flake8 .
}

run_mypy() {
    if ! command -v mypy &> /dev/null; then
        echo "Mypy not found. Run: pip install mypy"
        return
    fi

    mypy .
}

run_golangci_lint() {
    if ! command -v golangci-lint &> /dev/null; then
        echo "golangci-lint not found. Install from: https://golangci-lint.run/"
        return
    fi

    golangci-lint run
}

run_sonar_scanner() {
    if [ -f "sonar-project.properties" ]; then
        sonar-scanner
    else
        echo "No sonar-project.properties found"
    fi
}

detect_language() {
    if [ "$LANGUAGE" != "auto" ]; then
        echo "$LANGUAGE"
        return
    fi

    if [ -f "package.json" ]; then
        echo "javascript"
    elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
        echo "python"
    elif [ -f "go.mod" ]; then
        echo "go"
    elif [ -f "pom.xml" ] || [ -f "build.gradle" ]; then
        echo "java"
    else
        echo "unknown"
    fi
}

main() {
    echo "Running code linter..."
    echo "Language: $(detect_language)"
    echo "Auto-fix: $AUTO_FIX"
    echo "========================================"

    case $(detect_language) in
        javascript|typescript)
            if [ "$FORMAT_ONLY" = true ]; then
                run_prettier
            else
                run_eslint
                run_prettier
            fi
            ;;
        python)
            if [ "$FORMAT_ONLY" = true ]; then
                run_black
            else
                run_flake8
                run_black
                run_mypy
            fi
            ;;
        go)
            run_golangci_lint
            ;;
        *)
            echo "No linter configured for detected language"
            echo "Running available linters..."

            command -v eslint &> /dev/null && run_eslint
            command -v black &> /dev/null && run_black
            command -v flake8 &> /dev/null && run_flake8
            command -v golangci-lint &> /dev/null && run_golangci_lint
            ;;
    esac

    echo "========================================"
    echo "Linting completed."
}

main
