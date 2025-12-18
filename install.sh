#!/bin/bash
# TerminalAI Complete Installation Script
# Installs all modules, tools, and dependencies
# Usage: ./install.sh [--full|--dev|--audio]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation mode (default: full)
INSTALL_MODE="${1:---full}"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}TerminalAI Complete Installation${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_step() {
    echo -e "${BLUE}→${NC} $1"
}

# Check if running on supported OS
print_step "Checking operating system..."
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Cygwin;;
    MINGW*)     MACHINE=MinGw;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

if [ "$MACHINE" == "UNKNOWN:${OS}" ]; then
    print_error "Unsupported operating system: ${OS}"
    print_warning "Please use install.py for manual installation"
    exit 1
fi

print_status "Operating System: $MACHINE"
echo ""

# Check Python version
print_step "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    print_error "Python 3.10+ required, found $PYTHON_VERSION"
    exit 1
fi

print_status "Python $PYTHON_VERSION"
echo ""

# Check pip
print_step "Checking pip..."
if ! python3 -m pip --version &> /dev/null; then
    print_error "pip not found. Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi
print_status "pip is available"
echo ""

# Upgrade pip
print_step "Upgrading pip..."
python3 -m pip install --upgrade pip
print_status "pip upgraded"
echo ""

# Install TerminalAI package
print_step "Installing TerminalAI package..."
case "$INSTALL_MODE" in
    --full)
        print_status "Installing with ALL features (full)"
        python3 -m pip install -e ".[dev,audio]"
        ;;
    --dev)
        print_status "Installing with development tools"
        python3 -m pip install -e ".[dev]"
        ;;
    --audio)
        print_status "Installing with audio AI features"
        python3 -m pip install -e ".[audio]"
        ;;
    *)
        print_status "Installing basic package"
        python3 -m pip install -e .
        ;;
esac
print_status "TerminalAI package installed"
echo ""

# Install system dependencies based on OS
print_step "Checking system dependencies..."

# FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    print_warning "FFmpeg not found. Attempting to install..."

    if [ "$MACHINE" == "Linux" ]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y ffmpeg
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y ffmpeg
        elif command -v yum &> /dev/null; then
            sudo yum install -y ffmpeg
        else
            print_error "Package manager not found. Please install FFmpeg manually:"
            print_warning "  https://ffmpeg.org/download.html"
        fi
    elif [ "$MACHINE" == "Mac" ]; then
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            print_error "Homebrew not found. Please install FFmpeg manually:"
            print_warning "  brew install ffmpeg"
            print_warning "  or download from https://ffmpeg.org/download.html"
        fi
    fi
else
    FFMPEG_VERSION=$(ffmpeg -version | head -n1)
    print_status "FFmpeg found: $FFMPEG_VERSION"
fi
echo ""

# Install optional features for --full mode
if [ "$INSTALL_MODE" == "--full" ]; then
    print_step "Installing optional features..."

    # VapourSynth (for advanced deinterlacing)
    print_step "Installing VapourSynth Python bindings..."
    python3 -m pip install vapoursynth vapoursynth-havsfunc 2>/dev/null || {
        print_warning "VapourSynth installation failed (optional)"
        print_warning "VapourSynth runtime may need separate installation:"
        print_warning "  https://github.com/vapoursynth/vapoursynth/releases"
    }

    # GFPGAN (for face restoration)
    print_step "Installing GFPGAN for face restoration..."
    python3 -m pip install gfpgan basicsr facexlib 2>/dev/null || {
        print_warning "GFPGAN installation failed (optional)"
    }

    echo ""
fi

# Check for NVIDIA GPU
print_step "Checking for NVIDIA GPU..."
if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader | head -n1)
    print_status "NVIDIA GPU found: $GPU_INFO"

    # Check for Maxine SDK
    print_step "Checking for NVIDIA Maxine SDK..."
    if [ -n "$MAXINE_HOME" ] && [ -d "$MAXINE_HOME" ]; then
        print_status "Maxine SDK found at: $MAXINE_HOME"
    else
        print_warning "Maxine SDK not found (optional - best AI upscaling)"
        print_warning "Download from: https://developer.nvidia.com/maxine"
        print_warning "Set MAXINE_HOME environment variable after installation"
    fi
else
    print_warning "No NVIDIA GPU detected - GPU acceleration unavailable"
    print_warning "CPU and AMD/Intel GPU upscaling still available via Real-ESRGAN"
fi
echo ""

# Check for Real-ESRGAN
print_step "Checking for Real-ESRGAN..."
if command -v realesrgan-ncnn-vulkan &> /dev/null; then
    REALESRGAN_PATH=$(which realesrgan-ncnn-vulkan)
    print_status "Real-ESRGAN found: $REALESRGAN_PATH"
else
    print_warning "Real-ESRGAN not found (optional - AI upscaling)"
    print_warning "Download from: https://github.com/xinntao/Real-ESRGAN/releases"
    print_warning "Add to PATH after installation"
fi
echo ""

# Verify installation
print_step "Verifying installation..."
if python3 -c "from vhs_upscaler import VideoQueue, QueueJob, JobStatus" 2>/dev/null; then
    print_status "Package import successful"
else
    print_error "Package import failed"
    exit 1
fi

if python3 -m vhs_upscaler.vhs_upscale --help &>/dev/null; then
    print_status "CLI entry point working"
else
    print_warning "CLI entry point check failed"
fi
echo ""

# Create desktop shortcut (optional, Linux only)
if [ "$MACHINE" == "Linux" ] && [ -d "$HOME/.local/share/applications" ]; then
    print_step "Creating desktop shortcut..."
    DESKTOP_FILE="$HOME/.local/share/applications/terminalai.desktop"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=TerminalAI
Comment=AI-powered video upscaling and processing
Exec=python3 -m vhs_upscaler.gui
Icon=video
Terminal=false
Categories=AudioVideo;Video;
EOF
    chmod +x "$DESKTOP_FILE"
    print_status "Desktop shortcut created"
    echo ""
fi

# Print summary
echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Next Steps:"
echo "  1. Launch GUI:        python3 -m vhs_upscaler.gui"
echo "  2. Process video:     python3 -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4"
echo "  3. Run verification:  python3 scripts/verify_setup.py"
echo ""
echo "Documentation:"
echo "  • Quick Start:        README.md"
echo "  • Full Guide:         docs/DEPLOYMENT.md"
echo "  • Troubleshooting:    docs/DEPLOYMENT.md#troubleshooting"
echo ""
echo "Optional Tools (if not installed):"
if ! command -v nvidia-smi &> /dev/null; then
    echo "  • NVIDIA Drivers:     https://www.nvidia.com/drivers"
fi
if [ -z "$MAXINE_HOME" ]; then
    echo "  • Maxine SDK:         https://developer.nvidia.com/maxine"
fi
if ! command -v realesrgan-ncnn-vulkan &> /dev/null; then
    echo "  • Real-ESRGAN:        https://github.com/xinntao/Real-ESRGAN/releases"
fi
echo ""

# Final status
print_status "All core modules and tools installed successfully!"
echo ""
