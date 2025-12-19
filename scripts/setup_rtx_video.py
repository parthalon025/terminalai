#!/usr/bin/env python3
"""
RTX Video SDK Setup Wizard
==========================

Interactive setup wizard for NVIDIA RTX Video SDK integration.
Guides users through installation with explanations of benefits.

Usage:
    python scripts/setup_rtx_video.py

    # Or after pip install:
    python -m vhs_upscaler.setup_rtx
"""

import os
import platform
import subprocess
import sys
import webbrowser
from pathlib import Path

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text: str):
    """Print a styled header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_step(num: int, text: str):
    """Print a numbered step."""
    print(f"\n{Colors.BOLD}{Colors.GREEN}Step {num}:{Colors.END} {text}")

def ask_yes_no(prompt: str, default: bool = True) -> bool:
    """Ask a yes/no question."""
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        response = input(f"{Colors.YELLOW}{prompt}{suffix}{Colors.END}").strip().lower()
        if not response:
            return default
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no'):
            return False
        print("Please enter 'y' or 'n'")

def check_system_requirements() -> dict:
    """Check system requirements for RTX Video SDK."""
    results = {
        'platform': platform.system(),
        'is_windows': platform.system() == 'Windows',
        'is_64bit': platform.machine().endswith('64'),
        'python_version': sys.version_info[:2],
        'gpu_name': None,
        'gpu_supported': False,
        'driver_version': None,
        'sdk_installed': False,
        'sdk_path': None,
    }

    # Check GPU
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,compute_cap,driver_version',
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(', ')
            if len(parts) >= 3:
                results['gpu_name'] = parts[0].strip()
                compute_cap = tuple(map(int, parts[1].strip().split('.')))
                results['driver_version'] = parts[2].strip()
                # RTX 20 series = compute capability 7.5+
                results['gpu_supported'] = compute_cap >= (7, 5)
    except Exception:
        pass

    # Check for existing SDK installation
    sdk_paths = [
        Path(os.environ.get('RTX_VIDEO_SDK_HOME', '')),
        Path(os.environ.get('LOCALAPPDATA', '')) / 'NVIDIA' / 'RTXVideoSDK',
        Path('C:/Program Files/NVIDIA Corporation/RTX Video SDK'),
        Path('C:/NVIDIA/RTXVideoSDK'),
    ]

    for sdk_path in sdk_paths:
        if sdk_path.exists():
            # Check for DLL
            for dll_dir in ['lib', 'bin', '']:
                dll_path = sdk_path / dll_dir / 'NVVideoEffects.dll' if dll_dir else sdk_path / 'NVVideoEffects.dll'
                if dll_path.exists():
                    results['sdk_installed'] = True
                    results['sdk_path'] = str(sdk_path)
                    break
        if results['sdk_installed']:
            break

    return results

def print_benefits():
    """Print the benefits of RTX Video SDK."""
    print(f"""
{Colors.BOLD}🚀 Why RTX Video SDK?{Colors.END}

RTX Video SDK uses NVIDIA's AI-powered Tensor Cores to dramatically
improve video quality. Here's how it enhances your workflow:

{Colors.GREEN}┌─────────────────────────────────────────────────────────────┐
│  Feature                  │  Benefit for VHS/DVD Upscaling  │
├─────────────────────────────────────────────────────────────┤
│  🔍 Super Resolution      │  4x AI upscaling (480p → 4K)    │
│                           │  Sharp edges, preserved details │
├─────────────────────────────────────────────────────────────┤
│  🧹 Artifact Reduction    │  Removes VHS tracking errors    │
│                           │  Fixes compression blockyness   │
│                           │  Cleans color bleeding          │
├─────────────────────────────────────────────────────────────┤
│  🌈 HDR Conversion        │  SDR → HDR10 for modern TVs     │
│                           │  Expanded color gamut           │
│                           │  Better contrast & brightness   │
└─────────────────────────────────────────────────────────────┘{Colors.END}

{Colors.CYAN}Performance Comparison:{Colors.END}

  Engine          │ Quality │ Speed  │ GPU Support
  ────────────────┼─────────┼────────┼─────────────────
  RTX Video SDK   │ ⭐⭐⭐⭐⭐  │ Fast   │ RTX 20+ only
  Real-ESRGAN     │ ⭐⭐⭐⭐   │ Medium │ Any GPU (Vulkan)
  FFmpeg          │ ⭐⭐⭐    │ Slow   │ CPU (any system)

{Colors.YELLOW}Best For:{Colors.END}
  • VHS home videos with tracking issues and noise
  • DVD rips with compression artifacts
  • Low-bitrate YouTube downloads
  • Any footage you want to upscale to 4K HDR
""")

def print_installation_steps():
    """Print manual installation steps."""
    print(f"""
{Colors.BOLD}📥 RTX Video SDK Installation Steps{Colors.END}

{Colors.GREEN}Step 1:{Colors.END} Download the SDK
   Visit: {Colors.UNDERLINE}https://developer.nvidia.com/rtx-video-sdk{Colors.END}
   Click "Get Started" → Download SDK (requires NVIDIA Developer account)

{Colors.GREEN}Step 2:{Colors.END} Install the SDK
   Run the installer and note the installation path
   Default: C:\\Program Files\\NVIDIA Corporation\\RTX Video SDK

{Colors.GREEN}Step 3:{Colors.END} Set Environment Variable
   Option A - System Settings:
     1. Press Win+X → System → Advanced System Settings
     2. Click "Environment Variables"
     3. Add new System Variable:
        Name:  RTX_VIDEO_SDK_HOME
        Value: C:\\Program Files\\NVIDIA Corporation\\RTX Video SDK

   Option B - Command Line (temporary):
     set RTX_VIDEO_SDK_HOME=C:\\Program Files\\NVIDIA Corporation\\RTX Video SDK

{Colors.GREEN}Step 4:{Colors.END} Verify Installation
   Restart TerminalAI and check the engine dropdown -
   "rtxvideo" should now be available!
""")

def install_python_dependencies():
    """Install Python dependencies for RTX Video SDK."""
    print_info("Installing Python dependencies for RTX Video SDK...")

    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'numpy>=1.24.0', 'opencv-python>=4.8.0'],
            check=True
        )
        print_success("Python dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install dependencies. Try manually:")
        print("  pip install numpy opencv-python")
        return False

def install_cuda_dependencies():
    """Install CUDA dependencies for better performance."""
    print_info("Installing CuPy for CUDA acceleration...")

    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'cupy-cuda12x>=12.0.0'],
            check=True
        )
        print_success("CuPy installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print_warning("CuPy installation failed. RTX Video SDK will still work,")
        print("         but with slightly less performance.")
        return False

def open_download_page():
    """Open the RTX Video SDK download page."""
    url = "https://developer.nvidia.com/rtx-video-sdk"
    print_info(f"Opening {url} in your browser...")
    webbrowser.open(url)

def main():
    """Main setup wizard."""
    print_header("RTX Video SDK Setup Wizard")

    print("""
Welcome to the RTX Video SDK setup wizard!

This will help you set up NVIDIA's AI-powered video enhancement
for the best possible VHS/DVD upscaling quality.
""")

    # Check system requirements
    print_step(1, "Checking system requirements...")
    requirements = check_system_requirements()

    # Platform check
    if not requirements['is_windows']:
        print_error(f"RTX Video SDK only supports Windows.")
        print_info(f"Your platform: {requirements['platform']}")
        print_info("TerminalAI will use Real-ESRGAN or FFmpeg instead.")
        print_info("These still provide excellent upscaling on your system!")
        return

    if not requirements['is_64bit']:
        print_error("RTX Video SDK requires 64-bit Windows.")
        return

    print_success(f"Platform: Windows 64-bit ✓")

    # GPU check
    if requirements['gpu_name']:
        print_success(f"GPU: {requirements['gpu_name']}")
        print_success(f"Driver: {requirements['driver_version']}")

        if requirements['gpu_supported']:
            print_success("GPU supports RTX Video SDK (RTX 20 series or newer) ✓")
        else:
            print_warning("GPU does not support RTX Video SDK (requires RTX 20+)")
            print_info("TerminalAI will use Real-ESRGAN instead, which also")
            print_info("provides excellent AI upscaling on your GPU!")

            if not ask_yes_no("Continue anyway to see installation steps?", default=False):
                return
    else:
        print_warning("Could not detect NVIDIA GPU")
        print_info("Make sure NVIDIA drivers are installed.")

    # Check if SDK is already installed
    if requirements['sdk_installed']:
        print_success(f"RTX Video SDK already installed at:")
        print_success(f"  {requirements['sdk_path']}")
        print()
        print_success("You're all set! RTX Video SDK is ready to use.")
        print_info("Select 'rtxvideo' as the AI Upscaler in the GUI.")
        return

    # Show benefits
    print_step(2, "Understanding the benefits...")
    if ask_yes_no("Would you like to see what RTX Video SDK offers?"):
        print_benefits()

    # Install Python dependencies
    print_step(3, "Installing Python dependencies...")
    if ask_yes_no("Install required Python packages (numpy, opencv)?"):
        install_python_dependencies()

        if ask_yes_no("Install CuPy for CUDA acceleration (optional, better performance)?", default=False):
            install_cuda_dependencies()

    # SDK Installation
    print_step(4, "RTX Video SDK Installation")
    print()
    print_info("The RTX Video SDK must be downloaded from NVIDIA's website.")
    print_info("This requires a free NVIDIA Developer account.")
    print()

    print_installation_steps()

    if ask_yes_no("Open the download page in your browser?"):
        open_download_page()
        print()
        print_info("After installing the SDK:")
        print("  1. Set the RTX_VIDEO_SDK_HOME environment variable")
        print("  2. Restart TerminalAI")
        print("  3. Select 'rtxvideo' as the AI Upscaler")

    # Summary
    print_header("Setup Summary")

    print(f"""
{Colors.GREEN}What's Next:{Colors.END}

  1. Download RTX Video SDK from NVIDIA Developer portal
  2. Install the SDK (note the installation path)
  3. Set RTX_VIDEO_SDK_HOME environment variable
  4. Restart TerminalAI
  5. Enjoy AI-powered 4K upscaling! 🎬

{Colors.CYAN}Without RTX Video SDK:{Colors.END}

  TerminalAI will automatically use these alternatives:
  • Real-ESRGAN - AI upscaling for any GPU (AMD/Intel/NVIDIA)
  • FFmpeg - CPU-based upscaling (works everywhere)

{Colors.YELLOW}Need Help?{Colors.END}

  • Documentation: https://github.com/parthalon025/terminalai
  • RTX Video SDK: https://developer.nvidia.com/rtx-video-sdk
""")

    print_success("Setup wizard complete!")

if __name__ == "__main__":
    main()
