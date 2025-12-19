#!/usr/bin/env python3
"""
TerminalAI Windows-Specific Installer
======================================
Handles PyTorch CUDA installation and Windows-specific dependency challenges.

Usage:
    python install_windows.py              # Interactive mode
    python install_windows.py --full       # Full installation
    python install_windows.py --audio      # Audio AI features
    python install_windows.py --faces      # Face restoration
    python install_windows.py --check      # Check installation status
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class WindowsInstaller:
    """Windows-specific installer with PyTorch CUDA support."""

    def __init__(self):
        self.system = platform.system()
        if self.system != "Windows":
            print("⚠ This installer is optimized for Windows.")
            print("  Use install.py for cross-platform installation.")
            response = input("Continue anyway? [y/N]: ")
            if response.lower() != 'y':
                sys.exit(0)

        self.python_version = sys.version_info
        self.errors = []
        self.warnings = []
        self.installed = []
        self.cuda_available = False
        self.cuda_version = None

    def log(self, message, level="INFO"):
        """Log installation progress."""
        prefix = {
            "INFO": "✓",
            "WARN": "⚠",
            "ERROR": "✗",
            "STEP": "→",
            "QUESTION": "?"
        }.get(level, "•")
        print(f"{prefix} {message}")

    def check_prerequisites(self):
        """Check system prerequisites."""
        self.log("Checking prerequisites...", "STEP")

        # Python version
        if self.python_version < (3, 10):
            self.errors.append(
                f"Python 3.10+ required, found {self.python_version.major}.{self.python_version.minor}"
            )
            return False

        self.log(f"Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")

        # Check pip
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                check=True,
                capture_output=True
            )
            self.log("pip available")
        except subprocess.CalledProcessError:
            self.errors.append("pip not found")
            return False

        return True

    def check_nvidia_gpu(self) -> bool:
        """Check for NVIDIA GPU and CUDA support."""
        self.log("Checking NVIDIA GPU...", "STEP")

        nvidia_smi = shutil.which("nvidia-smi")
        if not nvidia_smi:
            self.log("No NVIDIA GPU detected (CPU mode available)", "WARN")
            return False

        try:
            result = subprocess.run(
                [nvidia_smi, "--query-gpu=name,driver_version,compute_cap", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=True
            )
            gpu_info = result.stdout.strip().split(',')
            if gpu_info:
                gpu_name = gpu_info[0].strip()
                driver_version = gpu_info[1].strip() if len(gpu_info) > 1 else "unknown"
                compute_cap = gpu_info[2].strip() if len(gpu_info) > 2 else "unknown"

                self.log(f"GPU: {gpu_name}")
                self.log(f"Driver: {driver_version}")
                self.log(f"Compute Capability: {compute_cap}")

                # Determine CUDA version from driver
                try:
                    driver_major = int(driver_version.split('.')[0])
                    if driver_major >= 525:  # CUDA 12.x support
                        self.cuda_version = "cu121"
                        self.cuda_available = True
                        self.log("CUDA 12.1 compatible driver detected")
                    elif driver_major >= 450:  # CUDA 11.x support
                        self.cuda_version = "cu118"
                        self.cuda_available = True
                        self.log("CUDA 11.8 compatible driver detected")
                    else:
                        self.log("NVIDIA driver too old for CUDA support", "WARN")
                        return False
                except (ValueError, IndexError):
                    self.log("Could not determine CUDA version from driver", "WARN")
                    return False

                return True

        except subprocess.CalledProcessError:
            self.log("nvidia-smi failed - GPU may not be available", "WARN")
            return False

        return False

    def install_pytorch(self, force_cpu=False) -> bool:
        """
        Install PyTorch with appropriate CUDA support for Windows.

        This is the CRITICAL first step for all AI features.
        """
        self.log("Installing PyTorch...", "STEP")

        if force_cpu or not self.cuda_available:
            self.log("Installing CPU-only PyTorch")
            index_url = None
            packages = ["torch", "torchvision", "torchaudio"]
        else:
            self.log(f"Installing PyTorch with CUDA {self.cuda_version} support")
            # Official PyTorch Windows CUDA builds
            index_url = f"https://download.pytorch.org/whl/{self.cuda_version}"
            packages = ["torch", "torchvision", "torchaudio"]

        try:
            cmd = [sys.executable, "-m", "pip", "install"] + packages
            if index_url:
                cmd.extend(["--index-url", index_url])

            self.log(f"Command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            self.installed.append(f"PyTorch ({self.cuda_version if self.cuda_available else 'CPU'})")

            # Verify CUDA availability
            if not force_cpu and self.cuda_available:
                self._verify_pytorch_cuda()

            return True

        except subprocess.CalledProcessError as e:
            self.errors.append(f"PyTorch installation failed: {e}")
            return False

    def _verify_pytorch_cuda(self):
        """Verify PyTorch CUDA support after installation."""
        self.log("Verifying PyTorch CUDA support...", "STEP")

        try:
            result = subprocess.run(
                [
                    sys.executable, "-c",
                    "import torch; print(f'CUDA: {torch.cuda.is_available()}'); "
                    "print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}'); "
                    "print(f'PyTorch: {torch.__version__}')"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            self.log("PyTorch verification:")
            for line in result.stdout.strip().split('\n'):
                self.log(f"  {line}")

            if "CUDA: True" not in result.stdout:
                self.warnings.append("PyTorch installed but CUDA not available - using CPU")

        except subprocess.CalledProcessError as e:
            self.warnings.append(f"PyTorch verification failed: {e}")

    def install_base_package(self) -> bool:
        """Install TerminalAI base package."""
        self.log("Installing TerminalAI base package...", "STEP")

        try:
            cmd = [sys.executable, "-m", "pip", "install", "-e", "."]
            subprocess.run(cmd, check=True)
            self.installed.append("TerminalAI core")
            return True
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Base package installation failed: {e}")
            return False

    def install_audio_ai(self) -> bool:
        """Install audio AI features (Demucs, DeepFilterNet, AudioSR)."""
        self.log("Installing audio AI features...", "STEP")

        success = True

        # Install Demucs
        self.log("Installing Demucs (AI stem separation)...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "demucs>=4.0.0"],
                check=True,
                capture_output=True
            )
            self.installed.append("Demucs")
        except subprocess.CalledProcessError:
            self.warnings.append("Demucs installation failed (optional)")
            success = False

        # Install DeepFilterNet
        self.log("Installing DeepFilterNet (AI audio denoising)...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "deepfilternet>=0.5.0"],
                check=True,
                capture_output=True
            )
            self.installed.append("DeepFilterNet")
        except subprocess.CalledProcessError:
            self.warnings.append(
                "DeepFilterNet installation failed (may require Rust compiler)"
            )
            self.log("Install Rust from: https://www.rust-lang.org/tools/install", "WARN")
            success = False

        # Install AudioSR (optional, often fails on Windows)
        self.log("Installing AudioSR (AI audio upsampling) - optional...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "audiosr>=0.0.4"],
                check=True,
                capture_output=True,
                timeout=300  # 5 minute timeout
            )
            self.installed.append("AudioSR")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            self.warnings.append(
                "AudioSR installation failed (known Windows compatibility issues, optional)"
            )
            # Don't mark as failure since AudioSR is optional

        return success

    def install_face_restoration(self) -> bool:
        """Install GFPGAN/CodeFormer for face restoration."""
        self.log("Installing face restoration (GFPGAN)...", "STEP")

        # Install in correct order for Windows
        packages = [
            "opencv-python>=4.5.0",
            "basicsr>=1.4.2",
            "facexlib>=0.2.5",
            "gfpgan>=1.3.0"
        ]

        success = True
        for package in packages:
            package_name = package.split('>=')[0]
            self.log(f"Installing {package_name}...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                self.warnings.append(f"{package_name} installation failed")
                success = False

        if success:
            self.installed.append("GFPGAN face restoration")
        else:
            self.warnings.append("Face restoration installation incomplete")

        return success

    def install_vapoursynth(self) -> bool:
        """
        Install VapourSynth Python bindings.

        Note: VapourSynth runtime must be installed separately on Windows.
        """
        self.log("Installing VapourSynth Python bindings...", "STEP")

        self.log("Note: VapourSynth runtime must be installed separately", "WARN")
        self.log("Download from: https://github.com/vapoursynth/vapoursynth/releases", "WARN")

        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "vapoursynth"],
                check=True,
                capture_output=True
            )
            self.installed.append("VapourSynth Python bindings")
            return True
        except subprocess.CalledProcessError:
            self.warnings.append(
                "VapourSynth Python bindings installation failed (runtime may be missing)"
            )
            return False

    def check_ffmpeg(self) -> bool:
        """Check FFmpeg installation."""
        self.log("Checking FFmpeg...", "STEP")

        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            self.warnings.append("FFmpeg not found - required for video processing")
            self.log("Install FFmpeg with: winget install FFmpeg", "WARN")
            self.log("Or download from: https://ffmpeg.org/download.html", "WARN")
            return False

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
            self.warnings.append("FFmpeg found but not working")
            return False

    def download_models(self):
        """Download AI models."""
        self.log("Downloading AI models...", "STEP")

        # GFPGAN model
        if any("gfpgan" in item.lower() for item in self.installed):
            self.log("Downloading GFPGAN model...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "vhs_upscaler.face_restoration", "--download-model"],
                    check=True,
                    timeout=600  # 10 minute timeout
                )
                self.log("GFPGAN model downloaded")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                self.warnings.append("GFPGAN model download failed (can be done manually later)")

        # Demucs models (auto-downloaded on first use)
        if any("demucs" in item.lower() for item in self.installed):
            self.log("Demucs models will be downloaded automatically on first use")

    def run_verification(self):
        """Run verification script."""
        self.log("Running verification...", "STEP")

        verify_script = Path("scripts") / "verify_setup.py"
        if verify_script.exists():
            try:
                subprocess.run(
                    [sys.executable, str(verify_script)],
                    check=True
                )
            except subprocess.CalledProcessError:
                self.warnings.append("Verification script failed")
        else:
            self.log("Verification script not found", "WARN")

    def print_summary(self):
        """Print installation summary."""
        print("\n" + "=" * 80)
        print("Windows Installation Summary")
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
        print("  3. View full docs:    docs\\WINDOWS_INSTALLATION.md")

        if self.cuda_available:
            print("\n✓ CUDA GPU Acceleration Available!")
            print("  Your RTX GPU will be used for AI processing")
        else:
            print("\n⚠ CPU Mode")
            print("  GPU acceleration not available - processing will be slower")

        return True

    def interactive_install(self):
        """Interactive installation mode."""
        print("=" * 80)
        print("TerminalAI Windows Interactive Installer")
        print("=" * 80)
        print()

        self.log("This installer will guide you through setup", "INFO")
        print()

        # Check prerequisites
        if not self.check_prerequisites():
            self.log("Prerequisites check failed", "ERROR")
            return False

        # Check GPU
        has_gpu = self.check_nvidia_gpu()
        print()

        # Base package
        self.log("Installing base package (required)...", "STEP")
        if not self.install_base_package():
            self.log("Base installation failed", "ERROR")
            return False
        print()

        # PyTorch (needed for AI features)
        if has_gpu or input("Install PyTorch for AI features? [Y/n]: ").lower() != 'n':
            if not self.install_pytorch():
                self.log("PyTorch installation failed", "ERROR")
                if input("Continue without PyTorch? [y/N]: ").lower() != 'y':
                    return False
        print()

        # Audio AI
        if input("Install audio AI features (Demucs, DeepFilterNet)? [Y/n]: ").lower() != 'n':
            self.install_audio_ai()
        print()

        # Face restoration
        if input("Install face restoration (GFPGAN)? [Y/n]: ").lower() != 'n':
            self.install_face_restoration()
        print()

        # VapourSynth
        if input("Install VapourSynth (advanced deinterlacing)? [y/N]: ").lower() == 'y':
            self.install_vapoursynth()
        print()

        # FFmpeg check
        self.check_ffmpeg()
        print()

        # Download models
        if input("Download AI models now? [Y/n]: ").lower() != 'n':
            self.download_models()
        print()

        # Verification
        if input("Run verification script? [Y/n]: ").lower() != 'n':
            self.run_verification()
        print()

        return self.print_summary()

    def automated_install(self, install_type="basic"):
        """Automated installation."""
        print("=" * 80)
        print(f"TerminalAI Windows Automated Installer ({install_type})")
        print("=" * 80)
        print()

        if not self.check_prerequisites():
            return False

        has_gpu = self.check_nvidia_gpu()
        print()

        # Base
        if not self.install_base_package():
            return False
        print()

        # Install based on type
        if install_type in ["full", "audio", "faces"]:
            if has_gpu:
                self.install_pytorch()
            else:
                self.log("GPU not detected - skipping PyTorch", "WARN")
            print()

        if install_type in ["full", "audio"]:
            self.install_audio_ai()
            print()

        if install_type in ["full", "faces"]:
            self.install_face_restoration()
            print()

        if install_type == "full":
            self.install_vapoursynth()
            print()

        self.check_ffmpeg()
        print()

        if install_type == "full":
            self.download_models()
            print()

        self.run_verification()
        print()

        return self.print_summary()

    def check_status(self):
        """Check current installation status."""
        print("=" * 80)
        print("TerminalAI Installation Status")
        print("=" * 80)
        print()

        # Check each component
        components = {
            "Core Package": "vhs_upscaler",
            "PyTorch": "torch",
            "Demucs": "demucs",
            "DeepFilterNet": "deepfilternet",
            "AudioSR": "audiosr",
            "GFPGAN": "gfpgan",
            "BasicSR": "basicsr",
            "VapourSynth": "vapoursynth",
        }

        for name, module in components.items():
            try:
                result = subprocess.run(
                    [sys.executable, "-c", f"import {module}"],
                    capture_output=True,
                    check=True
                )
                self.log(f"{name}: Installed")
            except subprocess.CalledProcessError:
                self.log(f"{name}: Not installed", "WARN")

        print()

        # Check external tools
        self.check_ffmpeg()
        self.check_nvidia_gpu()
        print()

        # Run full verification
        self.run_verification()


def main():
    """Main installer entry point."""
    parser = argparse.ArgumentParser(
        description="TerminalAI Windows Installer with PyTorch CUDA Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Installation Types:
  interactive  Guided installation with prompts (default)
  basic        Core dependencies only
  full         All features (audio AI, face restoration, VapourSynth)
  audio        Audio AI features (Demucs, DeepFilterNet)
  faces        Face restoration (GFPGAN)

Examples:
  python install_windows.py                # Interactive mode
  python install_windows.py --full         # Full installation
  python install_windows.py --audio        # Audio AI only
  python install_windows.py --check        # Check installation status
        """
    )

    parser.add_argument(
        "--full",
        action="store_const",
        const="full",
        dest="install_type",
        help="Full installation with all features"
    )
    parser.add_argument(
        "--audio",
        action="store_const",
        const="audio",
        dest="install_type",
        help="Install audio AI features"
    )
    parser.add_argument(
        "--faces",
        action="store_const",
        const="faces",
        dest="install_type",
        help="Install face restoration"
    )
    parser.add_argument(
        "--basic",
        action="store_const",
        const="basic",
        dest="install_type",
        help="Basic installation only"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check installation status"
    )

    parser.set_defaults(install_type="interactive")
    args = parser.parse_args()

    installer = WindowsInstaller()

    if args.check:
        installer.check_status()
        sys.exit(0)

    if args.install_type == "interactive":
        success = installer.interactive_install()
    else:
        success = installer.automated_install(args.install_type)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
