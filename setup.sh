#!/bin/bash
# Quick Setup Script for Linux/Mac
# Run this to set up and start the Autonomous Data Analyst Agent

echo "========================================="
echo "Autonomous Data Analyst Agent - Setup"
echo "========================================="
echo ""

# Check if Docker is running
echo "Checking Docker..."
if command -v docker &> /dev/null; then
    echo "✓ Docker found: $(docker --version)"
else
    echo "✗ Docker not found or not running"
    echo "Please install Docker and ensure it's running"
    echo "Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created (edit it to add API keys)"
else
    echo "✓ .env file exists"
fi

echo ""

# Build sandbox image
echo "Building sandbox Docker image..."
echo "(This may take 2-3 minutes on first run)"

if docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/; then
    echo "✓ Sandbox image built successfully"
else
    echo "✗ Failed to build sandbox image"
    exit 1
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""

# Ask user if they want to start
read -p "Start the application now? (Y/n): " start_app

if [ "$start_app" = "" ] || [ "$start_app" = "Y" ] || [ "$start_app" = "y" ]; then
    echo ""
    echo "Starting application with Docker Compose..."
    echo "(Press Ctrl+C to stop)"
    echo ""
    
    docker-compose up --build
else
    echo ""
    echo "To start the application later, run:"
    echo "  docker-compose up --build"
    echo ""
    echo "Access points:"
    echo "  Frontend:  http://localhost:8501"
    echo "  Backend:   http://localhost:8000"
    echo "  API Docs:  http://localhost:8000/docs"
    echo ""
fi
