#!/bin/bash
# Build CodeCompacter inside Docker and copy the binary to ./dist/
# Requires Docker. Run this instead of build_linux.sh when the host
# Python lacks libpython3.13.so.1.0 (e.g. Debian trixie without python3.13-dev).
set -e

IMAGE=compacter-build
CONTAINER=compacter-extract

echo "==> Building Docker image..."
docker build -f Dockerfile.build -t $IMAGE .

echo "==> Extracting binary..."
mkdir -p dist
docker create --name $CONTAINER $IMAGE
docker cp $CONTAINER:/build/dist/CodeCompacter ./dist/CodeCompacter
docker rm $CONTAINER

echo ""
echo "Build complete: dist/CodeCompacter"
echo "Built against glibc 2.31 — runs on PuppyLinux and any system with glibc >= 2.31"
echo ""
echo "Verify drag-and-drop works before distributing:"
echo "  ./dist/CodeCompacter/CodeCompacter"
