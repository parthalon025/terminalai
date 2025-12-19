#!/usr/bin/env python3
"""
TerminalAI Setup Verification Script
=====================================
Comprehensive post-installation verification for Windows systems.
Tests all components, dependencies, and optional features.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_success(msg: str):
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} {msg}")


def print_error(msg: str):
    print(f"{Colors.FAIL}✗{Colors.ENDC} {msg}")


def print_warning(msg: str):
    print(f"{Colors.WARNING}⚠{Colors.ENDC} {msg}")


def print_info(msg: str):
    print(f"{Colors.OKCYAN}ℹ{Colors.ENDC} {msg}")


def print_section(msg: str):
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{msg.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


@dataclass
class VerificationResult:
    """Stores results of a verification check."""
    name: str
    status: bool
    version: Optional[str] = None
    error: Optional[str] = None
    details: Optional[str] = None
    severity: str = "error"  # "error", "warning", "info"


class SetupVerifier:
    """Comprehensive setup verification for TerminalAI."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[VerificationResult] = []

    def add_result(self, result: VerificationResult):
        """Add verification result to the list."""
        self.results.append(result)

        # Print result
        symbol = "✓" if result.status else ("⚠" if result.severity == "warning" else "✗")
        color = Colors.OKGREEN if result.status else (Colors.WARNING if result.severity == "warning" else Colors.FAIL)

        msg = f"{color}{symbol}{Colors.ENDC} {result.name}"
        if result.version:
            msg += f" ({Colors.OKCYAN}{result.version}{Colors.ENDC})"
        if not result.status and result.error and self.verbose:
            msg += f"\n    {Colors.FAIL}Error: {result.error}{Colors.ENDC}"
        if result.details and self.verbose:
            msg += f"\n    {Colors.OKBLUE}Details: {result.details}{Colors.ENDC}"

        print(msg)

    def check_python_version(self):
        """Verify Python version is 3.10+."""
        try:
            version = sys.version.split()[0]
            major, minor = map(int, version.split('.')[:2])

            if major >= 3 and minor >= 10:
                self.add_result(VerificationResult(
                    name="Python Version",
                    status=True,
                    version=version,
                    details=f"Python {version} meets minimum requirement (3.10+)"
                ))
                return True
            else:
                self.add_result(VerificationResult(
                    name="Python Version",
                    status=False,
                    version=version,
                    error=f"Python 3.10+ required, found {version}"
                ))
                return False
        except Exception as e:
            self.add_result(VerificationResult(
                name="Python Version",
                status=False,
                error=str(e)
            ))
            return False

    def check_package(self, package_name: str, import_name: Optional[str] = None,
                      optional: bool = False) -> bool:
        """Check if a Python package is installed."""
        if import_name is None:
            import_name = package_name

        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'unknown')

            self.add_result(VerificationResult(
                name=package_name,
                status=True,
                version=version,
                severity="info" if optional else "error"
            ))
            return True
        except ImportError as e:
            severity = "warning" if optional else "error"
            self.add_result(VerificationResult(
                name=package_name,
                status=False,
                error=str(e),
                severity=severity,
                details=f"Install with: pip install {package_name}"
            ))
            return False

    def check_command(self, command: str, version_flag: str = "--version",
                     optional: bool = False) -> bool:
        """Check if a command-line tool is available."""
        try:
            result = subprocess.run(
                [command, version_flag],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0] if result.stdout else "installed"
                self.add_result(VerificationResult(
                    name=command,
                    status=True,
                    version=version,
                    severity="info" if optional else "error"
                ))
                return True
            else:
                raise Exception("Command returned non-zero exit code")

        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            severity = "warning" if optional else "error"
            self.add_result(VerificationResult(
                name=command,
                status=False,
                error=str(e),
                severity=severity,
                details=f"Make sure {command} is installed and in PATH"
            ))
            return False

    def check_nvidia_gpu(self):
        """Check NVIDIA GPU and CUDA support."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                gpu_info = result.stdout.strip().split(',')
                gpu_name = gpu_info[0].strip()
                driver_version = gpu_info[1].strip()

                self.add_result(VerificationResult(
                    name="NVIDIA GPU",
                    status=True,
                    version=f"{gpu_name} (Driver {driver_version})",
                    details="GPU acceleration available"
                ))
                return True, gpu_name, driver_version
            else:
                raise Exception("nvidia-smi returned error")

        except Exception as e:
            self.add_result(VerificationResult(
                name="NVIDIA GPU",
                status=False,
                error=str(e),
                severity="warning",
                details="GPU acceleration not available - will use CPU fallback"
            ))
            return False, None, None

    def check_pytorch_cuda(self):
        """Check PyTorch CUDA availability."""
        try:
            import torch
            cuda_available = torch.cuda.is_available()

            if cuda_available:
                cuda_version = torch.version.cuda
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"

                self.add_result(VerificationResult(
                    name="PyTorch CUDA",
                    status=True,
                    version=f"CUDA {cuda_version}",
                    details=f"{gpu_count} GPU(s) available: {gpu_name}"
                ))
                return True
            else:
                self.add_result(VerificationResult(
                    name="PyTorch CUDA",
                    status=False,
                    error="CUDA not available in PyTorch",
                    severity="warning",
                    details="AI audio features will run on CPU (slower)"
                ))
                return False

        except ImportError:
            self.add_result(VerificationResult(
                name="PyTorch CUDA",
                status=False,
                error="PyTorch not installed",
                severity="warning"
            ))
            return False

    def check_vapoursynth(self):
        """Check VapourSynth installation."""
        try:
            import vapoursynth as vs
            core = vs.core

            version = core.version()
            self.add_result(VerificationResult(
                name="VapourSynth",
                status=True,
                version=version,
                details="QTGMC deinterlacing available"
            ))

            # Check for HAVSFunc (QTGMC)
            try:
                import havsfunc
                self.add_result(VerificationResult(
                    name="HAVSFunc (QTGMC)",
                    status=True,
                    severity="info"
                ))
            except ImportError:
                self.add_result(VerificationResult(
                    name="HAVSFunc (QTGMC)",
                    status=False,
                    error="HAVSFunc not installed",
                    severity="warning",
                    details="Install with: pip install havsfunc"
                ))

            return True

        except ImportError as e:
            self.add_result(VerificationResult(
                name="VapourSynth",
                status=False,
                error=str(e),
                severity="warning",
                details="QTGMC deinterlacing not available (YADIF/BWDIF still work)"
            ))
            return False

    def check_maxine_sdk(self):
        """Check NVIDIA Maxine SDK installation."""
        # Check environment variable
        maxine_home = os.environ.get('MAXINE_HOME')

        if maxine_home:
            maxine_path = Path(maxine_home)
            exe_path = maxine_path / 'bin' / 'VideoEffectsApp.exe'

            if exe_path.exists():
                self.add_result(VerificationResult(
                    name="NVIDIA Maxine SDK",
                    status=True,
                    version=str(maxine_path),
                    details="Best AI upscaling available for RTX GPUs"
                ))
                return True
            else:
                self.add_result(VerificationResult(
                    name="NVIDIA Maxine SDK",
                    status=False,
                    error=f"VideoEffectsApp.exe not found at {exe_path}",
                    severity="warning",
                    details="Download from: https://developer.nvidia.com/maxine"
                ))
                return False
        else:
            self.add_result(VerificationResult(
                name="NVIDIA Maxine SDK",
                status=False,
                error="MAXINE_HOME environment variable not set",
                severity="warning",
                details="Real-ESRGAN or FFmpeg will be used instead"
            ))
            return False

    def check_realesrgan(self):
        """Check Real-ESRGAN installation."""
        try:
            result = subprocess.run(
                ["realesrgan-ncnn-vulkan", "-h"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.add_result(VerificationResult(
                    name="Real-ESRGAN",
                    status=True,
                    details="AI upscaling available (works on AMD/Intel/NVIDIA)"
                ))
                return True
            else:
                raise Exception("Command failed")

        except Exception:
            self.add_result(VerificationResult(
                name="Real-ESRGAN",
                status=False,
                error="realesrgan-ncnn-vulkan not found",
                severity="warning",
                details="Download from: https://github.com/xinntao/Real-ESRGAN/releases"
            ))
            return False

    def check_audio_features(self):
        """Check audio processing features."""
        print_section("Audio Processing Features")

        self.check_package("demucs", optional=True)
        self.check_package("deepfilternet", "df", optional=True)
        self.check_package("audiosr", optional=True)

    def check_face_restoration(self):
        """Check face restoration features."""
        print_section("Face Restoration Features")

        self.check_package("gfpgan", optional=True)
        self.check_package("basicsr", optional=True)
        self.check_package("facexlib", optional=True)
        self.check_package("opencv-python", "cv2", optional=True)

        # CodeFormer is special - may not be installed via pip
        try:
            import codeformer
            self.add_result(VerificationResult(
                name="CodeFormer",
                status=True,
                severity="info"
            ))
        except ImportError:
            self.add_result(VerificationResult(
                name="CodeFormer",
                status=False,
                error="Not installed",
                severity="info",
                details="Will auto-download on first use"
            ))

    def check_automation_features(self):
        """Check automation features."""
        print_section("Automation Features")

        self.check_package("watchdog", optional=True)
        self.check_package("requests", optional=True)

    def run_full_verification(self):
        """Run complete verification suite."""
        print(f"\n{Colors.BOLD}TerminalAI Setup Verification{Colors.ENDC}")
        print(f"{Colors.OKBLUE}{'='*60}{Colors.ENDC}\n")

        # Core system checks
        print_section("System Requirements")
        self.check_python_version()
        self.check_command("ffmpeg", optional=False)

        # GPU checks
        print_section("GPU Support")
        gpu_available, gpu_name, driver = self.check_nvidia_gpu()
        if gpu_available:
            self.check_pytorch_cuda()

        # Core packages
        print_section("Core TerminalAI Components")
        self.check_package("vhs_upscaler")
        self.check_package("gradio")
        self.check_package("yt-dlp", "yt_dlp")
        self.check_package("yaml", "yaml")

        # PyTorch (if needed for audio/faces)
        print_section("AI Frameworks")
        self.check_package("torch", optional=True)
        self.check_package("torchaudio", optional=True)

        # Upscaling engines
        print_section("Video Upscaling Engines")
        self.check_maxine_sdk()
        self.check_realesrgan()

        # Deinterlacing
        print_section("Advanced Deinterlacing")
        self.check_vapoursynth()

        # Optional features
        self.check_audio_features()
        self.check_face_restoration()
        self.check_automation_features()

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print verification summary."""
        print_section("Verification Summary")

        total = len(self.results)
        passed = sum(1 for r in self.results if r.status)
        errors = sum(1 for r in self.results if not r.status and r.severity == "error")
        warnings = sum(1 for r in self.results if not r.status and r.severity == "warning")

        success_rate = (passed / total * 100) if total > 0 else 0

        print(f"Total Checks: {total}")
        print(f"{Colors.OKGREEN}Passed: {passed}{Colors.ENDC}")
        if errors > 0:
            print(f"{Colors.FAIL}Errors: {errors}{Colors.ENDC}")
        if warnings > 0:
            print(f"{Colors.WARNING}Warnings: {warnings}{Colors.ENDC}")

        print(f"\nSuccess Rate: {success_rate:.1f}%")

        if success_rate >= 90:
            print_success("Excellent! TerminalAI is ready to use.")
        elif success_rate >= 70:
            print_warning("Good! Core features available, some optional features missing.")
        elif success_rate >= 50:
            print_warning("Partial setup. Core features should work.")
        else:
            print_error("Installation incomplete. Please check errors above.")

        # Next steps
        print("\n" + Colors.BOLD + "Next Steps:" + Colors.ENDC)

        if errors > 0:
            print("\n" + Colors.FAIL + "Critical Issues:" + Colors.ENDC)
            for result in self.results:
                if not result.status and result.severity == "error":
                    print(f"  • Fix {result.name}: {result.details or result.error}")

        if warnings > 0:
            print("\n" + Colors.WARNING + "Optional Features:" + Colors.ENDC)
            print("  Some optional features are not available.")
            print("  Run with --verbose to see installation instructions.")

        print("\n" + Colors.OKGREEN + "Getting Started:" + Colors.ENDC)
        print("  1. Launch Web GUI:")
        print("     python -m vhs_upscaler.gui")
        print("\n  2. Process a video:")
        print("     python -m vhs_upscaler.vhs_upscale -i video.mp4 -o output.mp4 -p vhs")
        print("\n  3. Analyze a video:")
        print("     python -m vhs_upscaler.vhs_upscale analyze video.mp4")

    def export_report(self, filename: str = "verification_report.json"):
        """Export verification results to JSON."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "python_version": sys.version,
                "platform": sys.platform,
            },
            "results": [asdict(r) for r in self.results],
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results if r.status),
                "errors": sum(1 for r in self.results if not r.status and r.severity == "error"),
                "warnings": sum(1 for r in self.results if not r.status and r.severity == "warning"),
            }
        }

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        print_info(f"Verification report saved: {filename}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="TerminalAI Setup Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify_setup.py              # Run verification
  python verify_setup.py --verbose    # Detailed output
  python verify_setup.py --export     # Save JSON report
        """
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output with detailed error messages'
    )
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export verification report to JSON'
    )
    parser.add_argument(
        '--report-file',
        default='verification_report.json',
        help='Output file for JSON report (default: verification_report.json)'
    )

    args = parser.parse_args()

    # Run verification
    verifier = SetupVerifier(verbose=args.verbose)
    verifier.run_full_verification()

    # Export report if requested
    if args.export:
        verifier.export_report(args.report_file)

    # Exit with appropriate code
    errors = sum(1 for r in verifier.results if not r.status and r.severity == "error")
    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
