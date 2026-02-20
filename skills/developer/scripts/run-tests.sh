#!/bin/bash

# Test Runner Script
# Usage: bash scripts/run-tests.sh --help

set -e

show_help() {
  cat << EOF
Test Runner Script

Usage: bash scripts/run-tests.sh [OPTIONS]

Options:
  --type <type>         Test type (unit|integration|e2e|all) (default: all)
  --coverage            Generate coverage report
  --watch               Run tests in watch mode
  --verbose             Verbose output
  --help, -h            Show this help message

Examples:
  bash scripts/run-tests.sh --type unit --coverage
  bash scripts/run-tests.sh --type e2e
  bash scripts/run-tests.sh --watch
  bash scripts/run-tests.sh --type all --coverage --verbose

Test Types:
  unit          Unit tests (fast, isolated)
  integration   Integration tests (database, API)
  e2e           End-to-end tests (full user flows)
  all           Run all test types

What this script does:
  ✅ Detects test framework (Jest/Vitest/Pytest/Go test)
  ✅ Runs appropriate test commands
  ✅ Generates coverage reports
  ✅ Provides clear test results summary

Requirements:
  - Test framework installed (Jest/Vitest/Pytest/etc)
  - Test files in standard locations
  - Package.json scripts configured (for JS/TS)
EOF
}

# Parse arguments
TEST_TYPE="all"
COVERAGE=false
WATCH=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --help|-h)
      show_help
      exit 0
      ;;
    --type)
      TEST_TYPE="$2"
      shift 2
      ;;
    --coverage)
      COVERAGE=true
      shift
      ;;
    --watch)
      WATCH=true
      shift
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "🧪 Running tests: $TEST_TYPE"

# Detect test framework
if [ -f "package.json" ]; then
  if grep -q "vitest" package.json; then
    FRAMEWORK="vitest"
  elif grep -q "jest" package.json; then
    FRAMEWORK="jest"
  else
    FRAMEWORK="unknown"
  fi
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
  FRAMEWORK="pytest"
elif [ -f "go.mod" ]; then
  FRAMEWORK="go"
else
  echo "❌ Could not detect test framework"
  exit 1
fi

echo "📦 Detected framework: $FRAMEWORK"

# Build test command
case $FRAMEWORK in
  vitest)
    CMD="npx vitest"
    [ "$WATCH" = true ] && CMD="$CMD --watch" || CMD="$CMD run"
    [ "$COVERAGE" = true ] && CMD="$CMD --coverage"
    [ "$VERBOSE" = true ] && CMD="$CMD --reporter=verbose"
    
    case $TEST_TYPE in
      unit) CMD="$CMD --testPathPattern=unit" ;;
      integration) CMD="$CMD --testPathPattern=integration" ;;
      e2e) CMD="$CMD --testPathPattern=e2e" ;;
      all) ;;
    esac
    ;;
  
  jest)
    CMD="npx jest"
    [ "$WATCH" = true ] && CMD="$CMD --watch"
    [ "$COVERAGE" = true ] && CMD="$CMD --coverage"
    [ "$VERBOSE" = true ] && CMD="$CMD --verbose"
    
    case $TEST_TYPE in
      unit) CMD="$CMD --testPathPattern=unit" ;;
      integration) CMD="$CMD --testPathPattern=integration" ;;
      e2e) CMD="$CMD --testPathPattern=e2e" ;;
      all) ;;
    esac
    ;;
  
  pytest)
    CMD="pytest"
    [ "$COVERAGE" = true ] && CMD="$CMD --cov=. --cov-report=html"
    [ "$VERBOSE" = true ] && CMD="$CMD -v"
    
    case $TEST_TYPE in
      unit) CMD="$CMD tests/unit" ;;
      integration) CMD="$CMD tests/integration" ;;
      e2e) CMD="$CMD tests/e2e" ;;
      all) CMD="$CMD tests/" ;;
    esac
    ;;
  
  go)
    CMD="go test"
    [ "$COVERAGE" = true ] && CMD="$CMD -cover -coverprofile=coverage.out"
    [ "$VERBOSE" = true ] && CMD="$CMD -v"
    CMD="$CMD ./..."
    ;;
  
  *)
    echo "❌ Unsupported test framework"
    exit 1
    ;;
esac

echo "🚀 Running: $CMD"
echo ""

# Run tests
eval $CMD
TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo "✅ All tests passed!"
else
  echo "❌ Tests failed with exit code $TEST_EXIT_CODE"
fi

# Show coverage report location
if [ "$COVERAGE" = true ]; then
  echo ""
  echo "📊 Coverage report generated:"
  if [ "$FRAMEWORK" = "vitest" ] || [ "$FRAMEWORK" = "jest" ]; then
    echo "  Open: coverage/index.html"
  elif [ "$FRAMEWORK" = "pytest" ]; then
    echo "  Open: htmlcov/index.html"
  elif [ "$FRAMEWORK" = "go" ]; then
    echo "  Run: go tool cover -html=coverage.out"
  fi
fi

exit $TEST_EXIT_CODE

