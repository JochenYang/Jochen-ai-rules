#!/bin/bash

# Run all tests with coverage report
# Usage: ./run-tests.sh [--unit] [--integration] [--e2e] [--coverage]

set -e

REPORT_DIR="coverage-report"
COVERAGE_THRESHOLD=80

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --e2e)
            TEST_TYPE="e2e"
            shift
            ;;
        --coverage)
            GENERATE_COVERAGE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

detect_test_framework() {
    if [ -f "package.json" ]; then
        echo "node"
    elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
        echo "python"
    elif [ -f "pom.xml" ] || [ -f "build.gradle" ]; then
        echo "java"
    elif [ -f "go.mod" ]; then
        echo "go"
    fi
}

run_node_tests() {
    local framework
    framework=$(grep -A5 '"dependencies"' package.json 2>/dev/null | grep -E '"(jest|vitest|mocha)"' | head -1 | sed 's/.*"\([^"]*\)".*/\1/')

    case $framework in
        jest|vitest)
            if [ "$GENERATE_COVERAGE" = true ]; then
                npx ${framework:-jest} --coverage --coverageThreshold.global."${COVERAGE_THRESHOLD}"
            else
                npx ${framework:-jest}
            fi
            ;;
        mocha)
            npx mocha --recursive
            ;;
        *)
            npx jest --coverage
            ;;
    esac
}

run_python_tests() {
    if [ "$GENERATE_COVERAGE" = true ]; then
        pytest --cov=. --cov-report=term-missing --cov-report=html:"$REPORT_DIR"
    else
        pytest
    fi
}

run_java_tests() {
    mvn test -DskipTests=false
}

run_go_tests() {
    go test -v -coverprofile=coverage.out ./...
}

main() {
    echo "Running tests..."
    echo "Framework: $(detect_test_framework)"

    case $(detect_test_framework) in
        node)
            run_node_tests
            ;;
        python)
            run_python_tests
            ;;
        java)
            run_java_tests
            ;;
        go)
            run_go_tests
            ;;
        *)
            echo "No recognized test framework found"
            exit 1
            ;;
    esac

    if [ "$GENERATE_COVERAGE" = true ]; then
        echo "Coverage report generated in: $REPORT_DIR"
    fi
}

main
