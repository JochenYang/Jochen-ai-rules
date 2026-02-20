#!/bin/bash

# Generate detailed coverage report
# Usage: ./coverage-report.sh [--html] [--lcov] [-- Codecov] [--fail-under]

set -e

GENERATE_HTML=false
GENERATE_LCOV=false
UPLOAD_CODECOV=false
FAIL_UNDER=80

while [[ $# -gt 0 ]]; do
    case $1 in
        --html)
            GENERATE_HTML=true
            shift
            ;;
        --lcov)
            GENERATE_LCOV=true
            shift
            ;;
        --Codecov)
            UPLOAD_CODECOV=true
            shift
            ;;
        --fail-under)
            FAIL_UNDER="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

REPORT_DIR="coverage-report"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

generate_node_coverage() {
    echo "Generating Node.js coverage report..."

    if [ -f "package.json" ]; then
        local framework
        framework=$(grep -A5 '"dependencies"' package.json 2>/dev/null | grep -E '"(jest|vitest)"' | head -1 | sed 's/.*"\([^"]*\)".*/\1/')

        case $framework in
            vitest)
                npx vitest run --coverage
                ;;
            jest|*)
                npx jest --coverage --coverageReporters="json,lcov,text-summary"
                ;;
        esac
    fi
}

generate_python_coverage() {
    echo "Generating Python coverage report..."
    pytest --cov=. --cov-report=term-missing --cov-report=html:"$REPORT_DIR/$TIMESTAMP" --cov-report=lcov:"$REPORT_DIR/lcov.info"
}

generate_go_coverage() {
    echo "Generating Go coverage report..."
    go test -coverprofile="$REPORT_DIR/coverage.out" ./...
    go tool cover -func="$REPORT_DIR/coverage.out" -o "$REPORT_DIR/coverage.txt"
}

generate_java_coverage() {
    echo "Generating Java coverage report..."
    mvn jacoco:report
}

create_html_report() {
    echo "Creating HTML summary report..."

    local html_file="$REPORT_DIR/index.html"
    cat > "$html_file" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Coverage Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { display: inline-block; margin: 10px; padding: 15px; border-radius: 8px; background: #f5f5f5; }
        .metric h3 { margin: 0; color: #333; }
        .metric .value { font-size: 24px; font-weight: bold; }
        .high { color: #16a34a; }
        .medium { color: #ca8a04; }
        .low { color: #dc2626; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f5f5f5; }
    </style>
</head>
<body>
    <h1>Code Coverage Report</h1>
    <div id="metrics"></div>
    <div id="details"></div>
</body>
</html>
EOF

    echo "HTML report: $html_file"
}

generate_summary() {
    echo ""
    echo "========================================"
    echo "Coverage Summary"
    echo "========================================"

    if [ -f "coverage.json" ]; then
        local total_coverage
        total_coverage=$(grep -o '"percent_covered":[0-9.]*' coverage.json 2>/dev/null | sed 's/.*://' || echo "0")
        echo "Total Coverage: ${total_coverage}%"

        if (( $(echo "$total_coverage >= $FAIL_UNDER" | bc -l) )); then
            echo "Status: ✅ PASSED (threshold: ${FAIL_UNDER}%)"
        else
            echo "Status: ❌ FAILED (threshold: ${FAIL_UNDER}%)"
            exit 1
        fi
    fi

    echo ""
    echo "Report locations:"
    echo "  - HTML: $REPORT_DIR/index.html"
    echo "  - LCOV: $REPORT_DIR/lcov.info"

    if [ "$UPLOAD_CODECOV" = true ]; then
        echo "  - Codecov: Uploading..."
        if command -v codecov &> /dev/null; then
            codecov || echo "Codecov upload skipped"
        fi
    fi
}

main() {
    echo "Generating coverage report..."
    echo "========================================"

    if [ ! -d "$REPORT_DIR" ]; then
        mkdir -p "$REPORT_DIR"
    fi

    if [ -f "package.json" ]; then
        generate_node_coverage
    elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
        generate_python_coverage
    elif [ -f "go.mod" ]; then
        generate_go_coverage
    elif [ -f "pom.xml" ] || [ -f "build.gradle" ]; then
        generate_java_coverage
    else
        echo "No recognized project structure found"
        exit 1
    fi

    if [ "$GENERATE_HTML" = true ]; then
        create_html_report
    fi

    generate_summary
}

main
