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
import shutil
import subprocess
import sys
import tempfile
import webbrowser
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple

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
    print(f"{Colors.BLUE}[i] {text}{Colors.END}")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}[+] {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}[!] {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}[x] {text}{Colors.END}")

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

def find_sdk_zip_files() -> List[Tuple[Path, float]]:
    """
    Search for RTX Video SDK ZIP files in common download locations.

    Returns:
        List of tuples (path, size_mb) sorted by modification time (newest first)
    """
    search_paths = []

    # Add common download locations
    if platform.system() == 'Windows':
        # User's Downloads folder
        downloads = Path.home() / 'Downloads'
        if downloads.exists():
            search_paths.append(downloads)

        # Desktop
        desktop = Path.home() / 'Desktop'
        if desktop.exists():
            search_paths.append(desktop)

    # Current directory
    search_paths.append(Path.cwd())

    # Search patterns for SDK files
    patterns = [
        '*rtx*video*.zip',
        '*RTX*Video*.zip',
        '*RTXVideo*.zip',
        '*rtxvideo*.zip',
        '*video*effects*.zip',
        '*VideoEffects*.zip',
    ]

    found_files = []

    for search_path in search_paths:
        for pattern in patterns:
            try:
                for file_path in search_path.glob(pattern):
                    if file_path.is_file():
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        mtime = file_path.stat().st_mtime
                        found_files.append((file_path, size_mb, mtime))
            except Exception:
                continue

    # Remove duplicates and sort by modification time (newest first)
    unique_files = {}
    for file_path, size_mb, mtime in found_files:
        key = (file_path.resolve(), size_mb)
        if key not in unique_files or mtime > unique_files[key][2]:
            unique_files[key] = (file_path, size_mb, mtime)

    # Sort by modification time descending and return without mtime
    sorted_files = sorted(unique_files.values(), key=lambda x: x[2], reverse=True)
    return [(path, size) for path, size, _ in sorted_files]

def validate_zip_file(zip_path: Path) -> bool:
    """
    Validate that the ZIP file is valid and contains SDK files.

    Args:
        zip_path: Path to the ZIP file

    Returns:
        True if valid, False otherwise
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Check for corruption
            bad_file = zf.testzip()
            if bad_file:
                print_error(f"Corrupt file in ZIP: {bad_file}")
                return False

            # Check for SDK files (look for DLL or key files)
            filenames = zf.namelist()
            has_dll = any('NVVideoEffects.dll' in f or 'nvVideoEffects.dll' in f.lower()
                         for f in filenames)
            has_lib = any('lib' in f.lower() or 'bin' in f.lower() for f in filenames)

            if not (has_dll or has_lib):
                print_warning("ZIP doesn't appear to contain RTX Video SDK files")
                return ask_yes_no("Continue anyway?", default=False)

            return True
    except zipfile.BadZipFile:
        print_error("File is not a valid ZIP archive")
        return False
    except Exception as e:
        print_error(f"Error validating ZIP: {e}")
        return False

def extract_sdk(zip_path: Path, target_dir: Path) -> bool:
    """
    Extract SDK ZIP file to target directory with progress.

    Security: Implements ZIP slip protection by validating all extracted paths
    to prevent path traversal attacks.

    Args:
        zip_path: Path to the ZIP file
        target_dir: Target installation directory

    Returns:
        True if successful, False otherwise
    """
    try:
        print_info(f"Extracting to {target_dir}...")

        with zipfile.ZipFile(zip_path, 'r') as zf:
            members = zf.namelist()
            total_files = len(members)

            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)

            # Resolve target directory to absolute path for security validation
            target_dir_resolved = target_dir.resolve()

            # Extract with progress and ZIP slip protection
            for i, member in enumerate(members, 1):
                # SECURITY: Validate extraction path to prevent ZIP slip vulnerability
                # This prevents malicious ZIP files from writing outside the target directory
                member_path = (target_dir / member).resolve()

                # Ensure the extracted file path is within the target directory
                try:
                    member_path.relative_to(target_dir_resolved)
                except ValueError:
                    print_error(f"Security: Blocked path traversal attempt: {member}")
                    print_error(f"  Attempted path: {member_path}")
                    print_error(f"  Target directory: {target_dir_resolved}")
                    return False

                # Additional check for absolute paths and parent directory references
                if member.startswith('/') or member.startswith('\\') or '..' in Path(member).parts:
                    print_error(f"Security: Blocked suspicious path in ZIP: {member}")
                    return False

                # Safe to extract
                zf.extract(member, target_dir)

                # Show progress every 10% or for small archives every file
                if total_files < 20 or i % max(1, total_files // 10) == 0:
                    percent = (i / total_files) * 100
                    print(f"\r  Progress: {percent:.0f}% ({i}/{total_files} files)", end='')

            print()  # New line after progress
            print_success(f"Extracted {total_files} files successfully!")
            return True

    except PermissionError:
        print_error("Permission denied. Try running as Administrator:")
        print("  1. Right-click Command Prompt or PowerShell")
        print("  2. Select 'Run as administrator'")
        print(f"  3. Run: python {Path(__file__).name}")
        return False
    except Exception as e:
        print_error(f"Extraction failed: {e}")
        return False

def set_environment_variable(name: str, value: str) -> bool:
    """
    Set system environment variable on Windows.

    Args:
        name: Variable name
        value: Variable value

    Returns:
        True if successful, False otherwise
    """
    if platform.system() != 'Windows':
        print_warning("Environment variable setting only supported on Windows")
        return False

    try:
        # Try to set permanently using setx
        result = subprocess.run(
            ['setx', name, value],
            capture_output=True,
            text=True,
            check=True
        )

        # Also set for current session
        os.environ[name] = value

        print_success(f"Environment variable {name} set successfully!")
        print_info("Note: You may need to restart applications to see the change")
        return True

    except subprocess.CalledProcessError as e:
        print_error(f"Failed to set environment variable: {e}")
        print_info("You can set it manually:")
        print(f"  setx {name} \"{value}\"")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def interactive_sdk_installation() -> bool:
    """
    Interactive SDK installation wizard.

    Returns:
        True if SDK was installed successfully, False otherwise
    """
    print_step("4a", "Automatic SDK Installation")
    print()
    print_info("Let's try to find and install the RTX Video SDK automatically!")
    print()

    # Step 1: Search for SDK files
    print("[1/5] Searching for RTX Video SDK ZIP files...")
    found_files = find_sdk_zip_files()

    selected_file: Optional[Path] = None

    if found_files:
        print_success(f"Found {len(found_files)} potential SDK file(s):")
        print()

        for i, (file_path, size_mb) in enumerate(found_files, 1):
            print(f"  {i}. {file_path.name}")
            print(f"     Location: {file_path.parent}")
            print(f"     Size: {size_mb:.1f} MB")
            print()

        # Let user choose
        while True:
            choice = input(f"{Colors.YELLOW}Select file number (1-{len(found_files)}) or 'm' for manual path: {Colors.END}").strip().lower()

            if choice == 'm':
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(found_files):
                    selected_file = found_files[idx][0]
                    break
                else:
                    print("Invalid number. Please try again.")
            except ValueError:
                print("Please enter a number or 'm'.")
    else:
        print_warning("No SDK files found in common locations")
        print_info("Searched: Downloads, Desktop, current directory")
        print()

    # Step 2: Manual path input if needed
    if selected_file is None:
        print("[2/5] Manual path input...")
        print()

        while True:
            path_input = input(f"{Colors.YELLOW}Enter path to SDK ZIP file (or 'q' to quit): {Colors.END}").strip()

            if path_input.lower() == 'q':
                return False

            # Remove quotes if present
            path_input = path_input.strip('"').strip("'")

            file_path = Path(path_input)

            # Handle relative paths
            if not file_path.is_absolute():
                file_path = Path.cwd() / file_path

            if not file_path.exists():
                print_error("File not found. Please check the path and try again.")
                continue

            if not file_path.is_file():
                print_error("Path is not a file.")
                continue

            if file_path.suffix.lower() != '.zip':
                print_warning("File doesn't have .zip extension")
                if not ask_yes_no("Continue anyway?", default=False):
                    continue

            selected_file = file_path
            break

    if selected_file is None:
        return False

    print_success(f"Selected: {selected_file.name}")
    print()

    # Step 3: Validate ZIP file
    print("[3/5] Validating ZIP file...")
    if not validate_zip_file(selected_file):
        print_error("ZIP file validation failed")
        return False

    print_success("ZIP file is valid!")
    print()

    # Step 4: Extract SDK
    print("[4/5] Extracting SDK...")

    # Default target directory
    default_target = Path('C:/Program Files/NVIDIA Corporation/RTX Video SDK')

    print_info(f"Default installation path: {default_target}")

    if default_target.exists():
        print_warning("Installation directory already exists!")
        if not ask_yes_no("Overwrite existing installation?", default=False):
            # Ask for custom path
            custom_path = input(f"{Colors.YELLOW}Enter custom installation path: {Colors.END}").strip()
            custom_path = custom_path.strip('"').strip("'")
            default_target = Path(custom_path)

    if not extract_sdk(selected_file, default_target):
        return False

    print()

    # Step 5: Set environment variable
    print("[5/5] Setting environment variable...")

    sdk_path_str = str(default_target)
    if not set_environment_variable('RTX_VIDEO_SDK_HOME', sdk_path_str):
        print_warning("Could not set environment variable automatically")
        print()
        print(f"{Colors.BOLD}Please set it manually:{Colors.END}")
        print(f"  setx RTX_VIDEO_SDK_HOME \"{sdk_path_str}\"")
        print()

        if not ask_yes_no("Continue to dependency installation?", default=True):
            return False

    print()
    print_success("SDK installation complete!")
    print()

    # Install Python dependencies
    if ask_yes_no("Install Python dependencies now?", default=True):
        install_python_dependencies()

        if ask_yes_no("Install CuPy for CUDA acceleration (optional)?", default=False):
            install_cuda_dependencies()

    # Final verification
    print()
    print_info("Verifying installation...")

    # Check if DLL exists
    dll_found = False
    for dll_dir in ['lib', 'bin', '']:
        dll_path = default_target / dll_dir / 'NVVideoEffects.dll' if dll_dir else default_target / 'NVVideoEffects.dll'
        if dll_path.exists():
            dll_found = True
            print_success(f"Found NVVideoEffects.dll at: {dll_path}")
            break

    if not dll_found:
        print_warning("Could not find NVVideoEffects.dll in standard locations")
        print_info("The SDK may need manual configuration")

    return True

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

    print_success(f"Platform: Windows 64-bit")

    # GPU check
    if requirements['gpu_name']:
        print_success(f"GPU: {requirements['gpu_name']}")
        print_success(f"Driver: {requirements['driver_version']}")

        if requirements['gpu_supported']:
            print_success("GPU supports RTX Video SDK (RTX 20 series or newer)")
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

    # Check if user wants automatic installation
    print_info("The RTX Video SDK can be installed automatically or manually.")
    print()
    print(f"{Colors.BOLD}Option 1 - Automatic Installation:{Colors.END}")
    print("  • Searches for downloaded SDK ZIP file")
    print("  • Extracts and configures automatically")
    print("  • Sets environment variables")
    print()
    print(f"{Colors.BOLD}Option 2 - Manual Installation:{Colors.END}")
    print("  • Downloads SDK from NVIDIA (requires account)")
    print("  • You install manually following instructions")
    print()

    if ask_yes_no("Try automatic installation?", default=True):
        # Attempt automatic installation
        if interactive_sdk_installation():
            # Success! Skip to summary
            print_header("Installation Complete!")
            print(f"""
{Colors.GREEN}RTX Video SDK is now installed and ready to use!{Colors.END}

{Colors.CYAN}Next Steps:{Colors.END}

  1. Restart TerminalAI (important for environment variables)
  2. Launch the GUI: python -m vhs_upscaler.gui
  3. Select 'rtxvideo' as the AI Upscaler
  4. Enjoy AI-powered 4K upscaling! 🎬

{Colors.YELLOW}Verification:{Colors.END}

  Check that RTX_VIDEO_SDK_HOME is set:
    echo %RTX_VIDEO_SDK_HOME%

  Should output: C:\\Program Files\\NVIDIA Corporation\\RTX Video SDK
""")
            print_success("Setup wizard complete!")
            return
        else:
            print()
            print_warning("Automatic installation was not completed")
            print_info("Falling back to manual installation instructions...")
            print()

    # Manual installation path
    print_step("4b", "Manual SDK Installation")
    print()
    print_info("The RTX Video SDK must be downloaded from NVIDIA's website.")
    print_info("This requires a free NVIDIA Developer account.")
    print()

    print_installation_steps()

    if ask_yes_no("Open the download page in your browser?"):
        open_download_page()
        print()
        print_info("After downloading and installing the SDK:")
        print("  1. Run this wizard again for automatic setup")
        print("  2. Or set RTX_VIDEO_SDK_HOME environment variable manually")
        print("  3. Restart TerminalAI")
        print("  4. Select 'rtxvideo' as the AI Upscaler")

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
