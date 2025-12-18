#!/usr/bin/env python3
"""
TerminalAI Comprehensive Installer
===================================
Installs all requirements, dependencies, and optional tools.

Usage:
    python install.py              # Basic installation
    python install.py --full       # Full installation with all features
    python install.py --dev        # Development installation
    python install.py --audio      # Install with audio AI features
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
            "INFO": "✓",
            "WARN": "⚠",
            "ERROR": "✗",
            "STEP": "→"
        }.get(level, "•")
        print(f"{prefix} {message}")

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

    def install_package(self):
        """Install TerminalAI package with appropriate extras."""
        self.log("Installing TerminalAI package...", "STEP")

        extras = []
        if self.install_type in ["full", "dev"]:
            extras.append("dev")
        if self.install_type in ["full", "audio"]:
            extras.append("audio")

        if extras:
            extras_str = f"[{','.join(extras)}]"
        else:
            extras_str = ""

        try:
            cmd = [sys.executable, "-m", "pip", "install", "-e", f".{extras_str}"]
            self.log(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            self.installed.append(f"TerminalAI package{extras_str}")
            return True
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Failed to install package: {e}")
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
        self.log("Install FFmpeg:", "WARN")
        if self.system == "Windows":
            self.log("  winget install FFmpeg", "WARN")
            self.log("  or download from: https://ffmpeg.org/download.html", "WARN")
        elif self.system == "Darwin":
            self.log("  brew install ffmpeg", "WARN")
        else:  # Linux
            self.log("  sudo apt install ffmpeg  # Debian/Ubuntu", "WARN")
            self.log("  sudo dnf install ffmpeg  # Fedora", "WARN")
        return False

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
            print("\n✓ Successfully Installed:")
            for item in self.installed:
                print(f"  • {item}")

        if self.warnings:
            print("\n⚠ Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")

        if self.errors:
            print("\n✗ Errors:")
            for error in self.errors:
                print(f"  • {error}")
            print("\nInstallation completed with errors!")
            return False

        print("\n" + "=" * 80)
        print("✓ Installation Complete!")
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
            ("Installing package", self.install_package),
            ("Checking FFmpeg", self.check_ffmpeg),
            ("Checking NVIDIA GPU", self.check_nvidia_gpu),
            ("Checking Maxine SDK", self.check_maxine_sdk),
            ("Checking Real-ESRGAN", self.check_realesrgan),
        ]

        if self.install_type == "full":
            steps.extend([
                ("Installing VapourSynth", self.install_optional_vapoursynth),
                ("Installing GFPGAN", self.install_optional_gfpgan),
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
  full     Install all optional features (VapourSynth, GFPGAN, audio AI)
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
