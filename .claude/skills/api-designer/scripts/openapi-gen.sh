#!/bin/bash

# OpenAPI specification generator
# Usage: ./openapi-gen.sh [--input <path>] [--output <path>] [--format <json|yaml>]

set -e

INPUT_DIR="src"
OUTPUT_FILE="docs/openapi.yaml"
FORMAT="yaml"
TITLE="API Documentation"
VERSION="1.0.0"

if [[ "$1" == "--help" ]]; then
    echo "Usage: ./openapi-gen.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --input <path>     Input directory (default: src)"
    echo "  --output <path>    Output file (default: docs/openapi.yaml)"
    echo "  --format <format>  Output format: json or yaml (default: yaml)"
    echo "  --title <title>    API title (default: API Documentation)"
    echo "  --version <ver>    API version (default: 1.0.0)"
    echo "  --help             Show this help message"
    exit 0
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT_DIR="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --title)
            TITLE="$2"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

generate_from_express() {
    echo "Generating OpenAPI from Express routes..."

    if command -v tsoa &> /dev/null; then
        npx tsoa spec --basePath "/api/v1"
        return
    fi

    if command -v swagger-jsdoc &> /dev/null; then
        npx swagger-jsdoc -d swaggerDef.js -o "$OUTPUT_FILE"
        return
    fi

    echo "No OpenAPI generator found. Install: tsoa or swagger-jsdoc"
}

generate_from_controllers() {
    echo "Scanning controllers in: $INPUT_DIR"

    local paths=""

    for file in $(find "$INPUT_DIR" -name "*.js" -o -name "*.ts" 2>/dev/null); do
        if grep -q "router\.\(get\|post\|put\|patch\|delete\)" "$file" 2>/dev/null; then
            local route_path
            route_path=$(grep -oP "router\.\w+\s*\(\s*['\"][^'\"]+['\"]" "$file" | head -1 | sed "s/router\.\w*\s*['\"]//")

            if [ -n "$route_path" ]; then
                paths="${paths}
  ${route_path}:
    get:
      summary: Get ${route_path}
      responses:
        '200':
          description: Successful response"
            fi
        fi
    done

    echo "$paths"
}

create_openapi_doc() {
    local paths="$1"

    cat > "$OUTPUT_FILE" << EOF
openapi: 3.0.3
info:
  title: $TITLE
  version: $VERSION
  description: Auto-generated API documentation

servers:
  - url: /api/v1
    description: API v1

paths:
${paths}

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    Error:
      type: object
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: object
EOF
}

main() {
    echo "OpenAPI Generator"
    echo "========================================"
    echo "Input: $INPUT_DIR"
    echo "Output: $OUTPUT_FILE"
    echo "Format: $FORMAT"
    echo ""

    if [ -f "package.json" ] && grep -q "express\|fastify" package.json 2>/dev/null; then
        generate_from_express
    else
        local paths
        paths=$(generate_from_controllers)
        create_openapi_doc "$paths"
    fi

    echo ""
    echo "OpenAPI spec generated: $OUTPUT_FILE"

    if [ "$FORMAT" = "json" ]; then
        if command -v yq &> /dev/null; then
            yq eval -o json "$OUTPUT_FILE" > "${OUTPUT_FILE%.yaml}.json"
            echo "JSON version created: ${OUTPUT_FILE%.yaml}.json"
        fi
    fi
}

main
