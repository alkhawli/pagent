#!/usr/bin/env bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PAGENT Setup Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Docker
echo "Checking Docker..."
if command -v docker &> /dev/null; then
    docker_version=$(docker --version)
    echo "✅ Docker installed: $docker_version"
else
    echo "❌ Docker not found. Please install Docker Desktop."
    echo "   macOS: brew install --cask docker"
    echo "   Or download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check Docker is running
echo ""
echo "Checking Docker daemon..."
if docker info &> /dev/null; then
    echo "✅ Docker daemon is running"
else
    echo "❌ Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

# Check just
echo ""
echo "Checking just (command runner)..."
if command -v just &> /dev/null; then
    just_version=$(just --version)
    echo "✅ just installed: $just_version"
else
    echo "⚠️  just not found (optional but recommended)"
    echo "   Install: brew install just"
fi

# Check .env files
echo ""
echo "Checking environment files..."
if [ -f backend/.env ]; then
    echo "✅ backend/.env exists"

    # Check if credentials are configured
    if grep -q "your-username" backend/.env || grep -q "your-password" backend/.env; then
        echo "⚠️  Backend credentials not configured yet (still using placeholders)"
    else
        echo "✅ Backend credentials configured"
    fi
else
    echo "❌ backend/.env not found"
fi

if [ -f frontend/.env ]; then
    echo "✅ frontend/.env exists"
else
    echo "❌ frontend/.env not found"
fi

# Check ports
echo ""
echo "Checking if ports are available..."
if ! lsof -Pi :8020 -sTCP:LISTEN -t &> /dev/null; then
    echo "✅ Port 8020 (backend) is available"
else
    echo "⚠️  Port 8020 (backend) is already in use"
    lsof -Pi :8020 -sTCP:LISTEN
fi

if ! lsof -Pi :5173 -sTCP:LISTEN -t &> /dev/null; then
    echo "✅ Port 5173 (frontend) is available"
else
    echo "⚠️  Port 5173 (frontend) is already in use"
    lsof -Pi :5173 -sTCP:LISTEN
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Setup Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To start the application:"
echo "  1. Edit backend/.env with your credentials"
echo "  2. Run: just docker-up"
echo "  3. Open: http://localhost:5173"
echo ""
echo "For more details, see SETUP_CHECKLIST.md"
echo ""
