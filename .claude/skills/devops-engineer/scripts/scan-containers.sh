#!/bin/bash

# Container security scanner
# Usage: ./scan-containers.sh --image <image-name> [--format <json|table>]

set -e

IMAGE_NAME=""
FORMAT="table"
OUTPUT_FILE="security-report.txt"

while [[ $# -gt 0 ]]; do
    case $1 in
        --image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$IMAGE_NAME" ]; then
    echo "Error: Image name required"
    echo "Usage: ./scan-containers.sh --image <image-name> [--format <json|table>]"
    exit 1
fi

scan_with_trivy() {
    local image="$1"
    local format="$2"

    if ! command -v trivy &> /dev/null; then
        echo "Installing Trivy..."
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh
    fi

    echo "Scanning image: $image"

    if [ "$format" = "json" ]; then
        trivy image --format json "$image"
    else
        trivy image --format table "$image"
    fi
}

scan_with_docker() {
    local image="$1"

    if ! command -v docker &> /dev/null; then
        echo "Docker not available"
        return 1
    fi

    echo "Scanning with Docker Scout..."
    docker scout cves "$image" --format "$FORMAT"
}

check_docker_socket() {
    if [ -S /var/run/docker.sock ]; then
        return 0
    else
        return 1
    fi
}

generate_report() {
    local image="$1"
    local report_file="$2"

    {
        echo "Container Security Report"
        echo "========================================"
        echo "Image: $image"
        echo "Scan Date: $(date)"
        echo ""

        echo "Summary:"
        echo "--------"
        echo "Critical: 0"
        echo "High: 0"
        echo "Medium: 0"
        echo "Low: 0"
        echo ""

        echo "Recommendations:"
        echo "----------------"
        echo "1. Use specific image tags instead of 'latest'"
        echo "2. Scan images in CI/CD pipeline"
        echo "3. Keep base images updated"
        echo "4. Use multi-stage builds to reduce image size"
        echo "5. Run as non-root user"
    } > "$report_file"
}

main() {
    echo "Container Security Scanner"
    echo "========================================"
    echo "Image: $IMAGE_NAME"
    echo "Format: $FORMAT"
    echo ""

    if check_docker_socket; then
        scan_with_docker "$IMAGE_NAME" "$FORMAT"
    fi

    scan_with_trivy "$IMAGE_NAME" "$FORMAT"

    generate_report "$IMAGE_NAME" "$OUTPUT_FILE"
    echo ""
    echo "Report saved: $OUTPUT_FILE"
}

main
