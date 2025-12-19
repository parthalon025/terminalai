#!/bin/bash
################################################################################
# TerminalAI One-Shot Installer
# Complete automated installation with all dependencies and tools
#
# Usage: curl -sSL https://raw.githubusercontent.com/parthalon025/terminalai/main/one_shot_install.sh | bash
#    or: ./one_shot_install.sh
#
# This script will:
#   - Install system dependencies (FFmpeg, build tools)
#   - Install Python 3.10+ if needed
#   - Install TerminalAI with all features
#   - Download and configure optional tools
#   - Verify installation
#   - Provide next steps
################################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Installation configuration
INSTALL_DIR="$HOME/terminalai"
PYTHON_MIN_VERSION="3.10"
INSTALL_FFMPEG=true
INSTALL_OPTIONAL=true
CREATE_SHORTCUTS=true

# Print functions
print_header() {
    echo -e "${BLUE}${BOLD}"
    echo "================================================================================"
    echo "$1"
    echo "================================================================================"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}→${NC} ${BOLD}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "  $1"
}

# Error handler
error_exit() {
    print_error "Installation failed: $1"
    print_info "Check the error message above for details"
    print_info "For help, see: https://github.com/parthalon025/terminalai/issues"
    exit 1
}

# Detect OS
detect_os() {
    print_step "Detecting operating system..."
    OS="$(uname -s)"
    case "${OS}" in
        Linux*)
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                OS_NAME=$NAME
                OS_VERSION=$VERSION_ID
            fi
            MACHINE="Linux"
            ;;
        Darwin*)
            MACHINE="Mac"
            OS_NAME="macOS"
            OS_VERSION=$(sw_vers -productVersion)
            ;;
        *)
            error_exit "Unsupported operating system: ${OS}"
            ;;
    esac
    print_success "OS: $MACHINE ($OS_NAME $OS_VERSION)"
}

# Check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check Python version
check_python() {
    print_step "Checking Python version..."

    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_warning "Python not found, will attempt to install"
        return 1
    fi

    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        print_warning "Python $PYTHON_VERSION found, but 3.10+ required"
        return 1
    fi

    print_success "Python $PYTHON_VERSION"
    return 0
}

# Install Python
install_python() {
    print_step "Installing Python 3.10+..."

    if [ "$MACHINE" == "Linux" ]; then
        if command_exists apt-get; then
            sudo apt-get update || true
            sudo apt-get install -y python3 python3-pip python3-venv || error_exit "Failed to install Python"
        elif command_exists dnf; then
            sudo dnf install -y python3 python3-pip || error_exit "Failed to install Python"
        elif command_exists yum; then
            sudo yum install -y python3 python3-pip || error_exit "Failed to install Python"
        else
            error_exit "Package manager not found. Please install Python 3.10+ manually"
        fi
    elif [ "$MACHINE" == "Mac" ]; then
        if command_exists brew; then
            brew install python@3.11 || error_exit "Failed to install Python"
        else
            error_exit "Homebrew not found. Install from https://brew.sh/"
        fi
    fi

    check_python || error_exit "Python installation failed"
}

# Install system dependencies
install_system_deps() {
    print_step "Installing system dependencies..."

    if [ "$MACHINE" == "Linux" ]; then
        if command_exists apt-get; then
            print_info "Installing packages via apt..."
            sudo apt-get update || true
            sudo apt-get install -y \
                ffmpeg \
                git \
                wget \
                curl \
                build-essential \
                libssl-dev \
                libffi-dev || print_warning "Some packages failed to install"
        elif command_exists dnf; then
            print_info "Installing packages via dnf..."
            sudo dnf install -y ffmpeg git wget curl gcc || print_warning "Some packages failed to install"
        elif command_exists yum; then
            print_info "Installing packages via yum..."
            sudo yum install -y ffmpeg git wget curl gcc || print_warning "Some packages failed to install"
        fi
    elif [ "$MACHINE" == "Mac" ]; then
        if command_exists brew; then
            print_info "Installing packages via Homebrew..."
            brew install ffmpeg git wget || print_warning "Some packages failed to install"
        else
            print_warning "Homebrew not found. Install from https://brew.sh/"
        fi
    fi

    print_success "System dependencies installed"
}

# Clone or update repository
clone_repo() {
    print_step "Cloning TerminalAI repository..."

    if [ -d "$INSTALL_DIR" ]; then
        print_info "Directory exists, updating..."
        cd "$INSTALL_DIR"
        git pull origin main || error_exit "Failed to update repository"
    else
        print_info "Cloning to $INSTALL_DIR..."
        git clone https://github.com/parthalon025/terminalai.git "$INSTALL_DIR" || error_exit "Failed to clone repository"
        cd "$INSTALL_DIR"
    fi

    print_success "Repository ready"
}

# Install TerminalAI
install_terminalai() {
    print_step "Installing TerminalAI package..."

    cd "$INSTALL_DIR"

    # Upgrade pip
    $PYTHON_CMD -m pip install --upgrade pip || print_warning "Failed to upgrade pip"

    # Install package with all features
    print_info "Installing with all features (dev, audio)..."
    $PYTHON_CMD -m pip install -e ".[dev,audio]" || {
        print_warning "Full installation failed, trying basic installation..."
        $PYTHON_CMD -m pip install -e . || error_exit "Package installation failed"
    }

    print_success "TerminalAI package installed"
}

# Install optional features
install_optional_features() {
    if [ "$INSTALL_OPTIONAL" != "true" ]; then
        return
    fi

    print_step "Installing optional features..."

    # VapourSynth
    print_info "Installing VapourSynth Python bindings..."
    $PYTHON_CMD -m pip install vapoursynth vapoursynth-havsfunc 2>/dev/null || {
        print_warning "VapourSynth installation failed (optional)"
    }

    # GFPGAN
    print_info "Installing GFPGAN for face restoration..."
    $PYTHON_CMD -m pip install gfpgan basicsr facexlib 2>/dev/null || {
        print_warning "GFPGAN installation failed (optional)"
    }

    print_success "Optional features installed"
}

# Check GPU and drivers
check_gpu() {
    print_step "Checking GPU acceleration..."

    if command_exists nvidia-smi; then
        GPU_INFO=$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null | head -n1)
        if [ -n "$GPU_INFO" ]; then
            print_success "NVIDIA GPU: $GPU_INFO"
            print_info "GPU acceleration available"
        else
            print_warning "NVIDIA drivers may not be properly installed"
        fi
    else
        print_info "No NVIDIA GPU detected"
        print_info "CPU and AMD/Intel GPU upscaling available via Real-ESRGAN"
    fi
}

# Download Real-ESRGAN
download_realesrgan() {
    if command_exists realesrgan-ncnn-vulkan; then
        print_success "Real-ESRGAN already installed"
        return
    fi

    print_step "Downloading Real-ESRGAN..."

    REALESRGAN_VERSION="v0.2.5.0"

    if [ "$MACHINE" == "Linux" ]; then
        REALESRGAN_URL="https://github.com/xinntao/Real-ESRGAN/releases/download/${REALESRGAN_VERSION}/realesrgan-ncnn-vulkan-20220424-ubuntu.zip"
        REALESRGAN_DIR="$HOME/.local/bin"
    elif [ "$MACHINE" == "Mac" ]; then
        REALESRGAN_URL="https://github.com/xinntao/Real-ESRGAN/releases/download/${REALESRGAN_VERSION}/realesrgan-ncnn-vulkan-20220424-macos.zip"
        REALESRGAN_DIR="$HOME/.local/bin"
    else
        print_warning "Real-ESRGAN download not supported on this OS"
        return
    fi

    mkdir -p "$REALESRGAN_DIR"
    cd /tmp
    wget -q "$REALESRGAN_URL" -O realesrgan.zip || {
        print_warning "Failed to download Real-ESRGAN"
        return
    }

    unzip -q realesrgan.zip
    mv realesrgan-ncnn-vulkan "$REALESRGAN_DIR/" 2>/dev/null || true
    chmod +x "$REALESRGAN_DIR/realesrgan-ncnn-vulkan"
    rm realesrgan.zip

    # Add to PATH if not already
    if ! echo "$PATH" | grep -q "$REALESRGAN_DIR"; then
        echo "export PATH=\"\$PATH:$REALESRGAN_DIR\"" >> "$HOME/.bashrc"
        print_info "Added $REALESRGAN_DIR to PATH in .bashrc"
    fi

    print_success "Real-ESRGAN installed to $REALESRGAN_DIR"
}

# Create shortcuts
create_shortcuts() {
    if [ "$CREATE_SHORTCUTS" != "true" ]; then
        return
    fi

    print_step "Creating shortcuts..."

    # Desktop shortcut (Linux)
    if [ "$MACHINE" == "Linux" ] && [ -d "$HOME/.local/share/applications" ]; then
        DESKTOP_FILE="$HOME/.local/share/applications/terminalai.desktop"
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=TerminalAI
Comment=AI-powered video upscaling and processing
Exec=$PYTHON_CMD -m vhs_upscaler.gui
Path=$INSTALL_DIR
Icon=video
Terminal=false
Categories=AudioVideo;Video;
EOF
        chmod +x "$DESKTOP_FILE"
        print_success "Desktop shortcut created"
    fi

    # Launcher script
    LAUNCHER="$HOME/.local/bin/terminalai"
    mkdir -p "$HOME/.local/bin"
    cat > "$LAUNCHER" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
$PYTHON_CMD -m vhs_upscaler.gui "\$@"
EOF
    chmod +x "$LAUNCHER"
    print_success "Command-line launcher created: terminalai"
}

# Verify installation
verify_installation() {
    print_step "Verifying installation..."

    cd "$INSTALL_DIR"

    # Test import
    if $PYTHON_CMD -c "from vhs_upscaler import VideoQueue, QueueJob, JobStatus" 2>/dev/null; then
        print_success "Package import successful"
    else
        print_error "Package import failed"
        return 1
    fi

    # Test CLI
    if $PYTHON_CMD -m vhs_upscaler.vhs_upscale --help &>/dev/null; then
        print_success "CLI entry point working"
    else
        print_warning "CLI entry point check failed"
    fi

    # Test FFmpeg
    if command_exists ffmpeg; then
        print_success "FFmpeg available"
    else
        print_warning "FFmpeg not found"
    fi

    return 0
}

# Print final instructions
print_instructions() {
    print_header "Installation Complete!"

    echo ""
    echo -e "${GREEN}${BOLD}✓ TerminalAI is ready to use!${NC}"
    echo ""
    echo -e "${BOLD}Quick Start:${NC}"
    echo ""
    echo -e "  ${BLUE}1.${NC} Launch GUI:"
    echo -e "     ${BOLD}terminalai${NC}  or  ${BOLD}python3 -m vhs_upscaler.gui${NC}"
    echo ""
    echo -e "  ${BLUE}2.${NC} Process a video:"
    echo -e "     ${BOLD}cd $INSTALL_DIR${NC}"
    echo -e "     ${BOLD}python3 -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4${NC}"
    echo ""
    echo -e "  ${BLUE}3.${NC} Verify setup:"
    echo -e "     ${BOLD}python3 scripts/verify_setup.py${NC}"
    echo ""
    echo -e "${BOLD}Documentation:${NC}"
    echo -e "  • Quick Start:      ${INSTALL_DIR}/README.md"
    echo -e "  • Full Guide:       ${INSTALL_DIR}/docs/DEPLOYMENT.md"
    echo -e "  • Troubleshooting:  ${INSTALL_DIR}/docs/DEPLOYMENT.md#troubleshooting"
    echo ""

    # Optional tools
    local optional_needed=false

    if ! command_exists nvidia-smi; then
        if [ "$optional_needed" == "false" ]; then
            echo -e "${BOLD}Optional Enhancements:${NC}"
            optional_needed=true
        fi
        echo -e "  • NVIDIA Drivers: https://www.nvidia.com/drivers"
    fi

    if [ -z "$MAXINE_HOME" ] && command_exists nvidia-smi; then
        if [ "$optional_needed" == "false" ]; then
            echo -e "${BOLD}Optional Enhancements:${NC}"
            optional_needed=true
        fi
        echo -e "  • Maxine SDK (best AI upscaling): https://developer.nvidia.com/maxine"
    fi

    if [ "$optional_needed" == "true" ]; then
        echo ""
    fi

    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
}

# Main installation flow
main() {
    print_header "TerminalAI One-Shot Installer"

    echo ""
    print_info "This will install TerminalAI with all dependencies and tools."
    print_info "Installation directory: $INSTALL_DIR"
    echo ""

    detect_os
    echo ""

    check_python || install_python
    echo ""

    install_system_deps
    echo ""

    clone_repo
    echo ""

    install_terminalai
    echo ""

    install_optional_features
    echo ""

    check_gpu
    echo ""

    if [ "$INSTALL_OPTIONAL" == "true" ]; then
        download_realesrgan
        echo ""
    fi

    create_shortcuts
    echo ""

    verify_installation || error_exit "Installation verification failed"
    echo ""

    print_instructions
}

# Run installation
main "$@"
