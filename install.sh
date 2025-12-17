#!/bin/bash
# TerminalAI Quick Install Script
# ================================
# Usage: ./install.sh [--dev]

set -e

echo "======================================"
echo "  TerminalAI Video Upscaler Installer"
echo "======================================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python 3.10+ required (found $PYTHON_VERSION)"
    exit 1
fi
echo "✓ Python $PYTHON_VERSION detected"

# Check for FFmpeg
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version | head -n1 | cut -d' ' -f3)
    echo "✓ FFmpeg $FFMPEG_VERSION detected"
else
    echo "⚠ FFmpeg not found - please install FFmpeg"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
fi

# Check for NVIDIA GPU (optional)
if command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n1)
    echo "✓ NVIDIA GPU: $GPU_NAME"
else
    echo "⚠ NVIDIA GPU not detected (AI upscaling requires RTX GPU)"
fi

echo ""
echo "Installing Python dependencies..."

# Install based on argument
if [ "$1" == "--dev" ]; then
    echo "Installing with development dependencies..."
    pip install -e ".[dev]"
else
    pip install -e .
fi

echo ""
echo "======================================"
echo "  Installation Complete!"
echo "======================================"
echo ""
echo "To start the GUI:"
echo "  python -m vhs_upscaler.gui"
echo ""
echo "Or use command line:"
echo "  python -m vhs_upscaler.vhs_upscale -i video.mp4 -o output.mp4"
echo ""

# Run tests if dev install
if [ "$1" == "--dev" ]; then
    echo "Running tests..."
    pytest tests/ -v --tb=short
fi
