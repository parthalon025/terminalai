#!/usr/bin/env python3
"""
TerminalAI Comprehensive Installer
===================================
Installs all requirements, dependencies, and optional tools.

Features:
    - Automatic Rust compiler installation for DeepFilterNet
    - PyTorch CUDA detection and installation
    - Platform-specific dependency handling (Windows/Linux/macOS)
    - Comprehensive error handling and fallback strategies
    - Installation verification and diagnostics

Usage:
    python install.py              # Basic installation
    python install.py --full       # Full installation with all features
    python install.py --dev        # Development installation
    python install.py --audio      # Install with audio AI features

Rust Auto-Installation:
    When --audio or --full is specified, the installer will:
    1. Check if Rust compiler is available
    2. If not found, automatically download and install rustup
    3. Windows: Downloads rustup-init.exe from https://win.rustup.rs/x86_64
    4. Linux/macOS: Uses curl | sh method from https://sh.rustup.rs
    5. Adds Rust to PATH for the current session
    6. Proceeds with DeepFilterNet installation

Requirements:
    - Python 3.10+
    - pip package manager
    - Internet connection for downloads
    - Windows: Administrator rights may be needed
    - Linux/macOS: curl for Rust installation
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


class TerminalAIInstaller:
    """Comprehensive installer for TerminalAI with all dependencies."""

    def __init__(self, install_type="basic"):
        self.install_type = install_type
        self.system = platform.system()
        self.errors = []
        self.warnings = []
        self.installed = []

    def log(self, message, level="INFO"):
        """Log installation progress."""
        prefix = {
            "INFO": "[OK]",
            "WARN": "[WARN]",
            "ERROR": "[ERROR]",
            "STEP": "==>"
        }.get(level, "*")
        try:
            print(f"{prefix} {message}")
        except UnicodeEncodeError:
            # Fallback for terminals with encoding issues
            print(f"{prefix} {message}".encode('ascii', 'replace').decode('ascii'))

    def check_python_version(self):
        """Verify Python version meets requirements."""
        self.log("Checking Python version...", "STEP")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 10):
            self.errors.append(
                f"Python 3.10+ required, found {version.major}.{version.minor}"
            )
            return False
        self.log(f"Python {version.major}.{version.minor}.{version.micro}")
        return True

    def check_pip(self):
        """Verify pip is available."""
        self.log("Checking pip...", "STEP")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                check=True,
                capture_output=True,
                text=True
            )
            self.log("pip is available")
            return True
        except subprocess.CalledProcessError:
            self.errors.append("pip not found - please install pip")
            return False

    def check_rust(self):
        """Check if Rust and Cargo are installed."""
        self.log("Checking Rust compiler...", "STEP")

        # Check for cargo (Rust package manager)
        cargo_path = shutil.which("cargo")
        rustc_path = shutil.which("rustc")

        if cargo_path and rustc_path:
            try:
                # Get Rust version
                result = subprocess.run(
                    ["rustc", "--version"],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=5
                )
                version = result.stdout.strip()
                self.log(f"Rust found: {version}")
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass

        self.log("Rust compiler not found", "WARN")
        return False

    def install_rust(self):
        """Install Rust compiler automatically."""
        self.log("Installing Rust compiler (required for DeepFilterNet)...", "STEP")

        try:
            if self.system == "Windows":
                # Windows: Download and run rustup-init.exe
                self.log("Downloading rustup-init.exe...")

                import urllib.request
                import tempfile

                # Download rustup-init
                rustup_url = "https://win.rustup.rs/x86_64"
                with tempfile.TemporaryDirectory() as temp_dir:
                    rustup_path = Path(temp_dir) / "rustup-init.exe"

                    try:
                        urllib.request.urlretrieve(rustup_url, rustup_path)
                        self.log("Downloaded rustup-init.exe")
                    except Exception as e:
                        self.errors.append(f"Failed to download rustup: {e}")
                        return False

                    # Run rustup-init with silent installation
                    self.log("Running rustup installer (this may take a few minutes)...")
                    try:
                        result = subprocess.run(
                            [str(rustup_path), "-y", "--default-toolchain", "stable"],
                            capture_output=True,
                            text=True,
                            timeout=600  # 10 minutes timeout
                        )

                        if result.returncode == 0:
                            self.log("Rust installed successfully")

                            # Update PATH for current session
                            cargo_bin = Path.home() / ".cargo" / "bin"
                            if cargo_bin.exists():
                                os.environ["PATH"] = f"{cargo_bin}{os.pathsep}{os.environ['PATH']}"
                                self.log(f"Added {cargo_bin} to PATH")

                            self.installed.append("Rust compiler and Cargo")
                            return True
                        else:
                            self.errors.append(f"Rustup installation failed: {result.stderr}")
                            return False

                    except subprocess.TimeoutExpired:
                        self.errors.append("Rust installation timed out (may still be running)")
                        return False
                    except Exception as e:
                        self.errors.append(f"Rust installation error: {e}")
                        return False

            else:
                # Linux/macOS: Use curl | sh method
                self.log("Running rustup installer via curl...")

                try:
                    # Download and run rustup script
                    curl_cmd = [
                        "curl", "--proto", "=https", "--tlsv1.2", "-sSf",
                        "https://sh.rustup.rs"
                    ]
                    sh_cmd = ["sh", "-s", "--", "-y"]

                    # Pipe curl output to sh
                    curl_proc = subprocess.Popen(
                        curl_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    sh_proc = subprocess.Popen(
                        sh_cmd,
                        stdin=curl_proc.stdout,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    curl_proc.stdout.close()

                    stdout, stderr = sh_proc.communicate(timeout=600)

                    if sh_proc.returncode == 0:
                        self.log("Rust installed successfully")

                        # Source cargo env for current session
                        cargo_env = Path.home() / ".cargo" / "env"
                        if cargo_env.exists():
                            # Update PATH
                            cargo_bin = Path.home() / ".cargo" / "bin"
                            os.environ["PATH"] = f"{cargo_bin}{os.pathsep}{os.environ['PATH']}"
                            self.log(f"Added {cargo_bin} to PATH")

                        self.installed.append("Rust compiler and Cargo")
                        return True
                    else:
                        self.errors.append(f"Rustup installation failed: {stderr}")
                        return False

                except subprocess.TimeoutExpired:
                    self.errors.append("Rust installation timed out (may still be running)")
                    return False
                except FileNotFoundError:
                    self.errors.append("curl not found - required for Rust installation on Linux/macOS")
                    return False
                except Exception as e:
                    self.errors.append(f"Rust installation error: {e}")
                    return False

        except Exception as e:
            self.errors.append(f"Unexpected error during Rust installation: {e}")
            return False

    def install_package(self):
        """Install TerminalAI package with appropriate extras."""
        self.log("Installing TerminalAI package...", "STEP")

        # First install base package + dev if requested
        extras = []
        if self.install_type in ["full", "dev"]:
            extras.append("dev")

        if extras:
            extras_str = f"[{','.join(extras)}]"
        else:
            extras_str = ""

        try:
            cmd = [sys.executable, "-m", "pip", "install", "-e", f".{extras_str}"]
            self.log(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            self.installed.append(f"TerminalAI package{extras_str}")
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Failed to install base package: {e}")
            return False

        # Install PyTorch with CUDA support FIRST (Windows-specific)
        if self.install_type in ["full", "audio"] and self.system == "Windows":
            self.log("Installing PyTorch with CUDA support (Windows)...", "STEP")
            if self._install_pytorch_windows():
                self.installed.append("PyTorch with CUDA support")
            else:
                self.warnings.append("PyTorch CUDA installation failed - audio AI will not work")

        # Try to install audio extras separately (optional, may fail on some platforms)
        if self.install_type in ["full", "audio"]:
            self.log("Attempting to install audio AI features...", "STEP")
            self.log("Note: Audio features require PyTorch (installed above)")
            try:
                # Install Demucs first (most stable)
                try:
                    cmd = [sys.executable, "-m", "pip", "install", "demucs>=4.0.0"]
                    subprocess.run(cmd, check=True, capture_output=True)
                    self.installed.append("demucs")
                except subprocess.CalledProcessError:
                    self.warnings.append("Failed to install demucs (optional)")

                # Install DeepFilterNet (requires Rust compiler)
                try:
                    # Check for Rust, install if missing
                    if not self.check_rust():
                        self.log("DeepFilterNet requires Rust compiler - installing...", "STEP")
                        if not self.install_rust():
                            self.warnings.append("Failed to install Rust - skipping deepfilternet")
                        else:
                            # Retry DeepFilterNet installation after Rust is installed
                            try:
                                cmd = [sys.executable, "-m", "pip", "install", "deepfilternet>=0.5.0"]
                                subprocess.run(cmd, check=True, capture_output=True, timeout=300)
                                self.installed.append("deepfilternet")
                            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                                self.warnings.append("Failed to install deepfilternet even with Rust installed")
                    else:
                        # Rust already available, install DeepFilterNet directly
                        cmd = [sys.executable, "-m", "pip", "install", "deepfilternet>=0.5.0"]
                        subprocess.run(cmd, check=True, capture_output=True, timeout=300)
                        self.installed.append("deepfilternet")
                except subprocess.CalledProcessError:
                    self.warnings.append("Failed to install deepfilternet (optional)")
                except subprocess.TimeoutExpired:
                    self.warnings.append("DeepFilterNet installation timed out (may still be building)")

                # Install AudioSR (optional, often fails on Windows)
                try:
                    cmd = [sys.executable, "-m", "pip", "install", "audiosr>=0.0.4"]
                    subprocess.run(cmd, check=True, capture_output=True, timeout=300)
                    self.installed.append("audiosr")
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    self.warnings.append("Failed to install audiosr (optional, known Windows issues)")
            except Exception as e:
                self.warnings.append(f"Audio features installation failed (optional): {e}")

        return True

    def _install_pytorch_windows(self):
        """
        Install PyTorch with CUDA support on Windows.
        Detects GPU hardware BEFORE downloading to install correct version.

        Returns:
            True if successful, False otherwise
        """
        # Detect NVIDIA GPU details using nvidia-smi (lightweight, no downloads)
        has_cuda = False
        cuda_version = None
        gpu_name = None
        compute_cap = None

        try:
            # Get GPU name, driver version, and compute capability
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,driver_version,compute_cap", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )

            if result.stdout.strip():
                parts = [p.strip() for p in result.stdout.strip().split(",")]
                gpu_name = parts[0] if len(parts) > 0 else None
                driver_version = parts[1] if len(parts) > 1 else None
                compute_cap = parts[2] if len(parts) > 2 else None

                self.log(f"Detected GPU: {gpu_name}")
                self.log(f"Driver: {driver_version}, Compute Capability: {compute_cap}")

                # Determine CUDA version based on Python version and GPU
                python_version = sys.version_info
                use_nightly = False

                # RTX 50 series requires PyTorch nightly with CUDA 12.8 for compute capability 12.0
                if gpu_name and "RTX 50" in gpu_name:
                    use_nightly = True
                    cuda_version = "cu128"
                    self.log(f"RTX 50 series detected - installing PyTorch nightly with CUDA 12.8 for sm_120 support")
                elif python_version.minor >= 13:
                    # Python 3.13+ requires newer PyTorch with cu124
                    cuda_version = "cu124"
                    self.log("Python 3.13+ detected - using CUDA 12.4 index")
                elif python_version.minor == 12:
                    # Python 3.12 works with cu121 or cu124
                    cuda_version = "cu121"
                    self.log("Python 3.12 detected - using CUDA 12.1 index")
                else:
                    # Python 3.10-3.11
                    cuda_version = "cu121"
                    self.log("Python 3.10/3.11 detected - using CUDA 12.1 index")

                has_cuda = True
                self.details["use_pytorch_nightly"] = use_nightly

        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            self.log("No NVIDIA GPU detected - installing CPU-only PyTorch", "WARN")
            self.log(f"Detection details: {e}", "DEBUG")

        # Install PyTorch with appropriate CUDA support
        try:
            if has_cuda and cuda_version:
                # Use nightly builds for RTX 50 series (compute capability 12.0)
                if self.details.get("use_pytorch_nightly", False):
                    index_url = f"https://download.pytorch.org/whl/nightly/{cuda_version}"
                    packages = ["torch", "torchvision", "torchaudio"]
                    self.log(f"Installing PyTorch NIGHTLY with CUDA {cuda_version} for {gpu_name}...")
                    self.log("(Nightly required for RTX 50 series sm_120 support)")
                else:
                    index_url = f"https://download.pytorch.org/whl/{cuda_version}"
                    packages = ["torch", "torchvision", "torchaudio"]
                    self.log(f"Installing PyTorch with CUDA {cuda_version} support for {gpu_name}...")
            else:
                index_url = None
                packages = ["torch", "torchvision", "torchaudio"]
                self.log("Installing CPU-only PyTorch...")

            cmd = [sys.executable, "-m", "pip", "install"] + packages
            if index_url:
                cmd.extend(["--index-url", index_url])

            subprocess.run(cmd, check=True, timeout=600)

            # Verify CUDA availability
            if has_cuda:
                try:
                    verify_cmd = [
                        sys.executable, "-c",
                        "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); "
                        "print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
                    ]
                    result = subprocess.run(verify_cmd, capture_output=True, text=True, timeout=10)
                    self.log(result.stdout.strip())

                    if "CUDA available: False" in result.stdout:
                        self.warnings.append(
                            "PyTorch installed but CUDA not available. "
                            "This may be due to driver/CUDA version mismatch."
                        )
                except Exception as e:
                    self.log(f"CUDA verification warning: {e}", "WARN")

            return True
        except subprocess.CalledProcessError as e:
            self.log(f"PyTorch installation failed: {e}", "ERROR")
            self.errors.append(f"PyTorch installation failed: {e}")
            return False
        except subprocess.TimeoutExpired:
            self.log("PyTorch installation timed out", "ERROR")
            self.errors.append("PyTorch installation timed out after 10 minutes")
            return False

    def check_ffmpeg(self):
        """Check if FFmpeg is installed."""
        self.log("Checking FFmpeg...", "STEP")
        ffmpeg_path = shutil.which("ffmpeg")
        ffprobe_path = shutil.which("ffprobe")

        if ffmpeg_path and ffprobe_path:
            try:
                result = subprocess.run(
                    ["ffmpeg", "-version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                version = result.stdout.split('\n')[0]
                self.log(f"FFmpeg found: {version}")
                return True
            except subprocess.CalledProcessError:
                pass

        self.warnings.append("FFmpeg not found - required for video processing")
        return False

    def check_build_tools(self):
        """
        Detect C/C++ build tools required for some Python packages.

        Returns:
            True if build tools are available, False otherwise
        """
        self.log("Checking C/C++ build tools...", "STEP")

        if self.system == "Windows":
            # Check for Visual Studio Build Tools or MSVC
            try:
                # Check if cl.exe is in PATH
                cl_path = shutil.which("cl")
                if cl_path:
                    self.log(f"MSVC compiler found: {cl_path}")
                    return True

                # Check common installation paths via vswhere
                vswhere_path = r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
                if os.path.exists(vswhere_path):
                    result = subprocess.run(
                        [vswhere_path, "-latest", "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        self.log("Visual Studio Build Tools found")
                        return True
            except Exception:
                pass

            self.log("Build tools not found (required for some packages)", "WARN")
            return False

        elif self.system == "Darwin":
            # Check for Xcode Command Line Tools
            try:
                result = subprocess.run(
                    ["xcode-select", "-p"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if result.returncode == 0:
                    self.log(f"Xcode Command Line Tools found: {result.stdout.strip()}")
                    return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.log("Xcode Command Line Tools not found", "WARN")
                return False

        else:  # Linux
            # Check for gcc, g++, make
            has_gcc = shutil.which("gcc") is not None
            has_gxx = shutil.which("g++") is not None
            has_make = shutil.which("make") is not None

            if has_gcc and has_gxx and has_make:
                try:
                    result = subprocess.run(
                        ["gcc", "--version"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    version = result.stdout.split('\n')[0]
                    self.log(f"Build tools found: {version}")
                    return True
                except subprocess.CalledProcessError:
                    pass

            missing = []
            if not has_gcc:
                missing.append("gcc")
            if not has_gxx:
                missing.append("g++")
            if not has_make:
                missing.append("make")

            if missing:
                self.log(f"Missing build tools: {', '.join(missing)}", "WARN")
                return False

        return False

    def install_build_tools(self):
        """
        Attempt to install missing build tools.

        Returns:
            True if installation succeeded or user should install manually
        """
        self.log("Installing C/C++ build tools...", "STEP")

        if self.system == "Windows":
            self.log("Build tools installation on Windows:", "WARN")
            self.log("Option 1 - Visual Studio Build Tools (recommended):", "WARN")
            self.log("  1. Download from: https://visualstudio.microsoft.com/downloads/", "WARN")
            self.log("  2. Run installer and select 'Desktop development with C++'", "WARN")
            self.log("  3. Restart terminal after installation", "WARN")
            self.log("", "WARN")
            self.log("Option 2 - Quick command (if winget available):", "WARN")
            self.log("  winget install Microsoft.VisualStudio.2022.BuildTools", "WARN")
            self.log("", "WARN")
            self.log("Note: Build tools are optional but needed for DeepFilterNet", "WARN")
            self.warnings.append("Build tools need manual installation on Windows")
            return True  # Don't fail installation, just warn

        elif self.system == "Darwin":
            self.log("Attempting to install Xcode Command Line Tools...")
            try:
                # Trigger installation dialog
                subprocess.run(
                    ["xcode-select", "--install"],
                    check=False  # May fail if already installed
                )
                self.log("Xcode Command Line Tools installation started", "WARN")
                self.log("Please follow the installation dialog and restart terminal", "WARN")
                return True
            except Exception as e:
                self.log(f"Failed to trigger installation: {e}", "ERROR")
                self.log("Install manually: xcode-select --install", "WARN")
                self.warnings.append("Build tools need manual installation")
                return True

        else:  # Linux
            self.log("Build tools can be installed with package manager:", "WARN")

            # Detect package manager
            if shutil.which("apt-get"):
                self.log("Debian/Ubuntu detected. Install with:", "WARN")
                self.log("  sudo apt-get update", "WARN")
                self.log("  sudo apt-get install build-essential", "WARN")

                # Attempt automatic installation if running as root
                if os.geteuid() == 0:
                    try:
                        self.log("Attempting automatic installation...")
                        subprocess.run(["apt-get", "update"], check=True)
                        subprocess.run(["apt-get", "install", "-y", "build-essential"], check=True)
                        self.log("Build tools installed successfully")
                        self.installed.append("build-essential")
                        return True
                    except subprocess.CalledProcessError as e:
                        self.log(f"Installation failed: {e}", "ERROR")
                        return False

            elif shutil.which("dnf"):
                self.log("Fedora/RHEL detected. Install with:", "WARN")
                self.log("  sudo dnf groupinstall 'Development Tools'", "WARN")

            elif shutil.which("yum"):
                self.log("CentOS/RHEL detected. Install with:", "WARN")
                self.log("  sudo yum groupinstall 'Development Tools'", "WARN")

            elif shutil.which("pacman"):
                self.log("Arch Linux detected. Install with:", "WARN")
                self.log("  sudo pacman -S base-devel", "WARN")

            else:
                self.log("Unknown Linux distribution", "WARN")
                self.log("Install gcc, g++, and make using your package manager", "WARN")

            self.warnings.append("Build tools need manual installation (requires sudo)")
            return True  # Don't fail, just warn

    def install_ffmpeg(self):
        """
        Attempt to install FFmpeg using system package manager.

        Returns:
            True if installation succeeded, False otherwise
        """
        self.log("Installing FFmpeg...", "STEP")

        if self.system == "Windows":
            # Check if winget is available
            if shutil.which("winget"):
                try:
                    self.log("Installing FFmpeg using winget...")
                    subprocess.run(
                        ["winget", "install", "FFmpeg", "--silent"],
                        check=True,
                        timeout=300  # 5 minute timeout
                    )
                    self.log("FFmpeg installed successfully")
                    self.installed.append("FFmpeg")

                    # Verify installation
                    if shutil.which("ffmpeg"):
                        return True
                    else:
                        self.log("FFmpeg installed but not in PATH. Restart terminal.", "WARN")
                        return True

                except subprocess.CalledProcessError as e:
                    self.log(f"winget installation failed: {e}", "ERROR")
                    self.log("Install manually:", "WARN")
                    self.log("  Download from: https://ffmpeg.org/download.html", "WARN")
                    self.log("  Or use: choco install ffmpeg (if Chocolatey installed)", "WARN")
                    return False
                except subprocess.TimeoutExpired:
                    self.log("Installation timed out", "ERROR")
                    return False
            else:
                self.log("winget not found. Install FFmpeg manually:", "WARN")
                self.log("  Download from: https://ffmpeg.org/download.html", "WARN")
                self.log("  Or install winget and run: winget install FFmpeg", "WARN")
                self.warnings.append("FFmpeg needs manual installation")
                return False

        elif self.system == "Darwin":
            # Check if brew is available
            if shutil.which("brew"):
                try:
                    self.log("Installing FFmpeg using Homebrew...")
                    subprocess.run(
                        ["brew", "install", "ffmpeg"],
                        check=True,
                        timeout=600  # 10 minute timeout (can be slow)
                    )
                    self.log("FFmpeg installed successfully")
                    self.installed.append("FFmpeg")
                    return True
                except subprocess.CalledProcessError as e:
                    self.log(f"Homebrew installation failed: {e}", "ERROR")
                    return False
                except subprocess.TimeoutExpired:
                    self.log("Installation timed out", "ERROR")
                    return False
            else:
                self.log("Homebrew not found. Install FFmpeg manually:", "WARN")
                self.log("  Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"", "WARN")
                self.log("  Then run: brew install ffmpeg", "WARN")
                self.warnings.append("FFmpeg needs manual installation")
                return False

        else:  # Linux
            package_installed = False

            # Try apt (Debian/Ubuntu)
            if shutil.which("apt-get"):
                self.log("Debian/Ubuntu detected. Installing FFmpeg with apt...", "WARN")

                if os.geteuid() == 0:  # Running as root
                    try:
                        subprocess.run(["apt-get", "update"], check=True)
                        subprocess.run(["apt-get", "install", "-y", "ffmpeg"], check=True)
                        self.log("FFmpeg installed successfully")
                        self.installed.append("FFmpeg")
                        package_installed = True
                    except subprocess.CalledProcessError as e:
                        self.log(f"Installation failed: {e}", "ERROR")
                else:
                    self.log("Run with sudo to auto-install, or install manually:", "WARN")
                    self.log("  sudo apt-get update", "WARN")
                    self.log("  sudo apt-get install ffmpeg", "WARN")

            # Try dnf (Fedora)
            elif shutil.which("dnf"):
                self.log("Fedora/RHEL detected. Install FFmpeg with:", "WARN")
                if os.geteuid() == 0:
                    try:
                        subprocess.run(["dnf", "install", "-y", "ffmpeg"], check=True)
                        self.log("FFmpeg installed successfully")
                        self.installed.append("FFmpeg")
                        package_installed = True
                    except subprocess.CalledProcessError as e:
                        self.log(f"Installation failed: {e}", "ERROR")
                else:
                    self.log("  sudo dnf install ffmpeg", "WARN")

            # Try yum (CentOS/older RHEL)
            elif shutil.which("yum"):
                self.log("CentOS/RHEL detected. Install FFmpeg with:", "WARN")
                if os.geteuid() == 0:
                    try:
                        subprocess.run(["yum", "install", "-y", "ffmpeg"], check=True)
                        self.log("FFmpeg installed successfully")
                        self.installed.append("FFmpeg")
                        package_installed = True
                    except subprocess.CalledProcessError as e:
                        self.log(f"Installation failed: {e}", "ERROR")
                else:
                    self.log("  sudo yum install ffmpeg", "WARN")

            # Try pacman (Arch)
            elif shutil.which("pacman"):
                self.log("Arch Linux detected. Install FFmpeg with:", "WARN")
                if os.geteuid() == 0:
                    try:
                        subprocess.run(["pacman", "-S", "--noconfirm", "ffmpeg"], check=True)
                        self.log("FFmpeg installed successfully")
                        self.installed.append("FFmpeg")
                        package_installed = True
                    except subprocess.CalledProcessError as e:
                        self.log(f"Installation failed: {e}", "ERROR")
                else:
                    self.log("  sudo pacman -S ffmpeg", "WARN")
            else:
                self.log("Unknown package manager. Install FFmpeg manually.", "WARN")

            if not package_installed and os.geteuid() != 0:
                self.warnings.append("FFmpeg needs manual installation (requires sudo)")
                return False

            return package_installed

    def check_system_dependencies(self):
        """
        Check and optionally install all system dependencies.

        This wrapper method checks:
        - Build tools (C/C++ compiler)
        - FFmpeg

        Returns:
            Dictionary with check results
        """
        self.log("\n" + "=" * 80, "INFO")
        self.log("SYSTEM DEPENDENCIES CHECK", "INFO")
        self.log("=" * 80 + "\n", "INFO")

        results = {
            "build_tools": False,
            "ffmpeg": False
        }

        # Check build tools
        results["build_tools"] = self.check_build_tools()
        if not results["build_tools"]:
            self.log("Attempting to install build tools...", "STEP")
            self.install_build_tools()
            # Re-check after installation attempt
            results["build_tools"] = self.check_build_tools()

        print()  # Spacing

        # Check FFmpeg
        results["ffmpeg"] = self.check_ffmpeg()
        if not results["ffmpeg"]:
            self.log("Attempting to install FFmpeg...", "STEP")
            if self.install_ffmpeg():
                # Re-check after installation
                results["ffmpeg"] = self.check_ffmpeg()

        self.log("\n" + "=" * 80, "INFO")
        self.log("SYSTEM DEPENDENCIES SUMMARY", "INFO")
        self.log("=" * 80, "INFO")
        self.log(f"Build Tools: {'[OK] Available' if results['build_tools'] else '[WARN] Missing (optional)'}", "INFO")
        self.log(f"FFmpeg:      {'[OK] Available' if results['ffmpeg'] else '[ERROR] Missing (required)'}", "INFO")
        self.log("=" * 80 + "\n", "INFO")

        if not results["ffmpeg"]:
            self.log("WARNING: FFmpeg is required for video processing!", "ERROR")
            self.log("The application will not work without FFmpeg.", "ERROR")

        if not results["build_tools"]:
            self.log("Note: Build tools are optional but needed for some features:", "WARN")
            self.log("  - DeepFilterNet (AI audio denoising)", "WARN")
            self.log("  - Packages with C/C++ extensions", "WARN")

        return results

    def install_optional_vapoursynth(self):
        """Install VapourSynth for advanced deinterlacing (optional)."""
        if self.install_type not in ["full"]:
            return

        self.log("Installing VapourSynth (optional)...", "STEP")
        try:
            # Try to install Python bindings
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "vapoursynth", "vapoursynth-havsfunc"],
                check=True,
                capture_output=True
            )
            self.installed.append("VapourSynth Python bindings")
            self.log("VapourSynth Python bindings installed")
            self.log("Note: VapourSynth runtime may need separate installation:", "WARN")
            self.log("  https://github.com/vapoursynth/vapoursynth/releases", "WARN")
        except subprocess.CalledProcessError:
            self.warnings.append("VapourSynth installation failed (optional)")

    def install_optional_realesrgan(self):
        """Install Real-ESRGAN for AI upscaling (optional)."""
        if self.install_type not in ["full"]:
            return

        self.log("Installing Real-ESRGAN (optional)...", "STEP")
        try:
            # Install opencv and numpy first (required by Real-ESRGAN)
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "opencv-python", "numpy"],
                check=True,
                capture_output=True
            )

            # Install facexlib (required by Real-ESRGAN)
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "facexlib"],
                check=True,
                capture_output=True
            )

            # Install Real-ESRGAN (will pull basicsr as dependency)
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "realesrgan"],
                check=True,
                capture_output=True,
                timeout=300
            )
            self.installed.append("Real-ESRGAN AI upscaling")
            self.log("Real-ESRGAN installed")
        except subprocess.CalledProcessError as e:
            self.warnings.append(f"Real-ESRGAN installation failed (optional): {e}")
        except subprocess.TimeoutExpired:
            self.warnings.append("Real-ESRGAN installation timed out (optional)")

    def install_optional_gfpgan(self):
        """Install GFPGAN for face restoration (optional)."""
        if self.install_type not in ["full"]:
            return

        self.log("Installing GFPGAN (optional)...", "STEP")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "gfpgan", "basicsr", "facexlib"],
                check=True,
                capture_output=True
            )
            self.installed.append("GFPGAN face restoration")
            self.log("GFPGAN installed")
        except subprocess.CalledProcessError:
            self.warnings.append("GFPGAN installation failed (optional)")

    def patch_basicsr_torchvision(self):
        """
        Patch basicsr to fix torchvision >= 0.17 compatibility.

        Issue: basicsr 1.4.2 imports from torchvision.transforms.functional_tensor
        which was removed in torchvision 0.17+.

        Solution: Add try/except fallback to import from functional instead.
        """
        self.log("Checking for basicsr torchvision compatibility patch...", "STEP")

        try:
            # Find basicsr installation directory
            result = subprocess.run(
                [sys.executable, "-c", "import basicsr; print(basicsr.__file__)"],
                capture_output=True,
                text=True,
                check=True
            )
            basicsr_init = result.stdout.strip()
            basicsr_dir = Path(basicsr_init).parent
            degradations_file = basicsr_dir / "data" / "degradations.py"

            if not degradations_file.exists():
                self.log("basicsr not installed or degradations.py not found - skipping patch")
                return

            # Read current content
            content = degradations_file.read_text(encoding='utf-8')

            # Check if already patched (idempotent check)
            if "Fix for torchvision >= 0.17" in content:
                self.log("basicsr already patched for torchvision >= 0.17")
                return

            # Apply patch: Replace line 8 with try/except fallback
            old_import = "from torchvision.transforms.functional_tensor import rgb_to_grayscale"
            new_import = """# Fix for torchvision >= 0.17 where functional_tensor was removed
try:
    from torchvision.transforms.functional import rgb_to_grayscale
except ImportError:
    from torchvision.transforms.functional_tensor import rgb_to_grayscale"""

            if old_import in content:
                patched_content = content.replace(old_import, new_import)

                # Write patched content
                degradations_file.write_text(patched_content, encoding='utf-8')

                # Verify patch worked
                verify_content = degradations_file.read_text(encoding='utf-8')
                if "Fix for torchvision >= 0.17" in verify_content:
                    self.log("Successfully patched basicsr for torchvision >= 0.17")
                    self.installed.append("basicsr torchvision compatibility patch")
                else:
                    self.warnings.append("basicsr patch verification failed")
            else:
                # Import line not found or already modified
                self.log("basicsr import line not found or already modified - skipping patch")

        except subprocess.CalledProcessError:
            # basicsr not installed
            self.log("basicsr not installed - skipping patch")
        except Exception as e:
            self.warnings.append(f"basicsr patching failed (non-critical): {e}")

    def check_nvidia_gpu(self):
        """Check for NVIDIA GPU availability."""
        self.log("Checking for NVIDIA GPU...", "STEP")

        if self.system == "Windows":
            nvidia_smi = shutil.which("nvidia-smi")
        else:
            nvidia_smi = shutil.which("nvidia-smi") or "/usr/bin/nvidia-smi"

        if nvidia_smi and os.path.exists(nvidia_smi):
            try:
                result = subprocess.run(
                    [nvidia_smi, "--query-gpu=name,driver_version", "--format=csv,noheader"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                gpu_info = result.stdout.strip().split(',')
                if gpu_info:
                    self.log(f"NVIDIA GPU found: {gpu_info[0].strip()}")
                    if len(gpu_info) > 1:
                        self.log(f"Driver version: {gpu_info[1].strip()}")
                    return True
            except subprocess.CalledProcessError:
                pass

        self.log("No NVIDIA GPU detected - GPU acceleration unavailable", "WARN")
        return False

    def check_maxine_sdk(self):
        """Check if NVIDIA Maxine SDK is installed."""
        self.log("Checking NVIDIA Maxine SDK...", "STEP")

        maxine_env = os.environ.get("MAXINE_HOME")
        if maxine_env and os.path.exists(maxine_env):
            self.log(f"Maxine SDK found at: {maxine_env}")
            return True

        # Check common installation locations
        common_paths = [
            r"C:\Program Files\NVIDIA Corporation\NVIDIA Video Effects",
            r"C:\Program Files\NVIDIA\Maxine",
            "/opt/nvidia/maxine",
            str(Path.home() / "NVIDIA" / "Maxine")
        ]

        for path in common_paths:
            if os.path.exists(path):
                self.log(f"Maxine SDK found at: {path}")
                self.log(f"Set MAXINE_HOME environment variable: {path}", "WARN")
                return True

        self.log("Maxine SDK not found (optional - best AI upscaling)", "WARN")
        self.log("Download from: https://developer.nvidia.com/maxine", "WARN")
        return False

    def check_realesrgan(self):
        """Check if Real-ESRGAN is installed."""
        self.log("Checking Real-ESRGAN...", "STEP")

        realesrgan = shutil.which("realesrgan-ncnn-vulkan")
        if not realesrgan and self.system == "Windows":
            realesrgan = shutil.which("realesrgan-ncnn-vulkan.exe")

        if realesrgan:
            self.log(f"Real-ESRGAN found: {realesrgan}")
            return True

        self.log("Real-ESRGAN not found (optional - AI upscaling)", "WARN")
        self.log("Download from: https://github.com/xinntao/Real-ESRGAN/releases", "WARN")
        return False

    def create_config(self):
        """Create default configuration file if it doesn't exist."""
        self.log("Checking configuration...", "STEP")

        config_path = Path("vhs_upscaler") / "config.yaml"
        if config_path.exists():
            self.log("Configuration file already exists")
            return True

        self.log("Default configuration will be created on first run")
        return True

    def verify_installation(self):
        """Verify the installation is working."""
        self.log("Verifying installation...", "STEP")

        try:
            # Test package import
            result = subprocess.run(
                [sys.executable, "-c", "from vhs_upscaler import VideoQueue, QueueJob, JobStatus; print('OK')"],
                capture_output=True,
                text=True,
                check=True
            )
            if "OK" in result.stdout:
                self.log("Package import successful")
            else:
                self.warnings.append("Package import verification unclear")
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Package import failed: {e}")
            return False

        # Test CLI entry point
        try:
            subprocess.run(
                [sys.executable, "-m", "vhs_upscaler.vhs_upscale", "--help"],
                capture_output=True,
                check=True,
                timeout=5
            )
            self.log("CLI entry point working")
        except subprocess.CalledProcessError:
            self.warnings.append("CLI entry point check failed")
        except subprocess.TimeoutExpired:
            self.warnings.append("CLI entry point check timed out")

        return True

    def print_summary(self):
        """Print installation summary."""
        print("\n" + "=" * 80)
        print("Installation Summary")
        print("=" * 80)

        if self.installed:
            print("\n[OK] Successfully Installed:")
            for item in self.installed:
                print(f"  - {item}")

        if self.warnings:
            print("\n[WARN] Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if self.errors:
            print("\n[ERROR] Errors:")
            for error in self.errors:
                print(f"  - {error}")
            print("\nInstallation completed with errors!")
            return False

        print("\n" + "=" * 80)
        print("[OK] Installation Complete!")
        print("=" * 80)

        print("\nNext Steps:")
        print("  1. Launch GUI:        python -m vhs_upscaler.gui")
        print("  2. Process video:     python -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4")
        print("  3. Run verification:  python scripts/verify_setup.py")
        print("\nDocumentation:")
        print("  • Quick Start:        README.md")
        print("  • Full Guide:         docs/DEPLOYMENT.md")
        print("  • Troubleshooting:    docs/DEPLOYMENT.md#troubleshooting")

        return True

    def run(self):
        """Run the complete installation process."""
        print("=" * 80)
        print("TerminalAI Comprehensive Installer")
        print(f"Installation Type: {self.install_type.upper()}")
        print("=" * 80)
        print()

        steps = [
            ("Checking Python", self.check_python_version),
            ("Checking pip", self.check_pip),
            ("Checking system dependencies", self.check_system_dependencies),
            ("Installing package", self.install_package),
            ("Checking NVIDIA GPU", self.check_nvidia_gpu),
            ("Checking Maxine SDK", self.check_maxine_sdk),
            ("Checking Real-ESRGAN", self.check_realesrgan),
        ]

        if self.install_type == "full":
            steps.extend([
                ("Installing VapourSynth", self.install_optional_vapoursynth),
                ("Installing Real-ESRGAN", self.install_optional_realesrgan),
                ("Installing GFPGAN", self.install_optional_gfpgan),
                ("Patching basicsr", self.patch_basicsr_torchvision),
            ])

        steps.extend([
            ("Creating config", self.create_config),
            ("Verifying installation", self.verify_installation),
        ])

        for step_name, step_func in steps:
            try:
                step_func()
            except Exception as e:
                self.errors.append(f"{step_name} failed: {e}")
            print()

        return self.print_summary()


def main():
    """Main installer entry point."""
    parser = argparse.ArgumentParser(
        description="TerminalAI Comprehensive Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Installation Types:
  basic    Install core dependencies only (default)
  full     Install all optional features (VapourSynth, Real-ESRGAN, GFPGAN, audio AI)
  dev      Install with development tools (pytest, black, ruff)
  audio    Install with audio AI features (Demucs, PyTorch)

Examples:
  python install.py              # Basic installation
  python install.py --full       # Full installation
  python install.py --dev        # Development installation
  python install.py --audio      # With audio AI features
        """
    )

    parser.add_argument(
        "--full",
        action="store_const",
        const="full",
        dest="install_type",
        help="Install all optional features"
    )
    parser.add_argument(
        "--dev",
        action="store_const",
        const="dev",
        dest="install_type",
        help="Install with development tools"
    )
    parser.add_argument(
        "--audio",
        action="store_const",
        const="audio",
        dest="install_type",
        help="Install with audio AI features"
    )

    parser.set_defaults(install_type="basic")
    args = parser.parse_args()

    installer = TerminalAIInstaller(install_type=args.install_type)
    success = installer.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
