#!/bin/bash
# Build all optimized executor images for Codex.
# Run this on your EC2 instance (or wherever Docker runs).
#
# Usage: ./build-all.sh
#        ./build-all.sh cpp        # build only C++
#        ./build-all.sh java cpp   # build specific ones

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

declare -A IMAGES=(
    [cpp]="codex-cpp:latest"
    [java]="codex-java:latest"
    [python]="codex-python:latest"
    [javascript]="codex-javascript:latest"
)

# If args provided, build only those; otherwise build all
TARGETS=("${@:-${!IMAGES[@]}}")
if [ $# -eq 0 ]; then
    TARGETS=("${!IMAGES[@]}")
fi

for lang in "${TARGETS[@]}"; do
    image="${IMAGES[$lang]}"
    if [ -z "$image" ]; then
        echo "Unknown language: $lang (available: ${!IMAGES[*]})"
        continue
    fi
    echo "=== Building $image ==="
    docker build -t "$image" "$SCRIPT_DIR/$lang"
    echo "=== Done: $image ==="
    echo
done

echo "All images built:"
for lang in "${TARGETS[@]}"; do
    echo "  ${IMAGES[$lang]}"
done
