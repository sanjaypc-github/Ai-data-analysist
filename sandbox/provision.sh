#!/bin/bash
# Provision script to build the sandbox Docker image

set -e  # Exit on error

echo "========================================="
echo "Building ADA Sandbox Docker Image"
echo "========================================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Build the sandbox image
echo "Building sandbox image: ada-sandbox:latest"
docker build -f "$SCRIPT_DIR/Dockerfile.sandbox" -t ada-sandbox:latest "$SCRIPT_DIR"

echo ""
echo "✅ Sandbox image built successfully!"
echo ""
echo "Verify with: docker images | grep ada-sandbox"
echo ""
echo "The sandbox image includes:"
echo "  - Python 3.11"
echo "  - pandas, numpy, matplotlib"
echo "  - No network access when run"
echo "  - Non-root user for extra security"
echo ""
echo "To run the application:"
echo "  1. Start backend: cd backend && uvicorn app.main:app --reload"
echo "  2. Start frontend: cd frontend && streamlit run streamlit_app.py"
echo ""
