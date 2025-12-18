#!/usr/bin/env python3
"""
TerminalAI Setup Verification
==============================
Checks all dependencies and system capabilities.
"""

import subprocess
import sys
from pathlib import Path

# Fix Windows console encoding for unicode characters
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def check_python():
    """Check Python version."""
    version = sys.version_info
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
    if version < (3, 10):
        print("  [WARN] Warning: Python 3.10+ recommended")
        return False
    return True


def check_package():
    """Check if terminalai package is installed."""
    try:
        import vhs_upscaler
        print("[OK] terminalai package installed")
        return True
    except ImportError:
        print("[FAIL] terminalai package not found")
        print("  Run: pip install -e .")
        return False


def check_ffmpeg():
    """Check FFmpeg installation."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.split("\n")[0].split("version")[1].split()[0]
        print(f"[OK] FFmpeg {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[FAIL] FFmpeg not found")
        print("  Install: https://ffmpeg.org")
        return False


def check_nvidia_gpu():
    """Check for NVIDIA GPU."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=True
        )
        gpu_info = result.stdout.strip()
        print(f"[OK] NVIDIA GPU: {gpu_info}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[WARN] No NVIDIA GPU detected (CPU mode available)")
        return False


def check_nvenc():
    """Check for NVENC encoder support."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            check=True
        )
        has_h264 = "h264_nvenc" in result.stdout
        has_hevc = "hevc_nvenc" in result.stdout

        if has_h264 and has_hevc:
            print("[OK] NVENC encoders available (h264_nvenc, hevc_nvenc)")
            return True
        elif has_h264 or has_hevc:
            print("[WARN] Partial NVENC support")
            return True
        else:
            print("[WARN] NVENC not available (CPU encoding available)")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_maxine():
    """Check for NVIDIA Maxine SDK."""
    import os
    maxine_home = os.environ.get("MAXINE_HOME")
    if maxine_home:
        maxine_exe = Path(maxine_home) / "bin" / "VideoEffectsApp.exe"
        if maxine_exe.exists():
            print(f"[OK] NVIDIA Maxine SDK found at {maxine_home}")
            return True

    print("[WARN] NVIDIA Maxine SDK not found (Real-ESRGAN/FFmpeg available)")
    print("  Download: https://developer.nvidia.com/maxine")
    return False


def check_realesrgan():
    """Check for Real-ESRGAN."""
    import shutil
    exe = shutil.which("realesrgan-ncnn-vulkan")
    if exe:
        print(f"[OK] Real-ESRGAN found at {exe}")
        return True

    print("[WARN] Real-ESRGAN not found (Maxine/FFmpeg available)")
    print("  Download: https://github.com/xinntao/Real-ESRGAN/releases")
    return False


def check_directories():
    """Check output and logs directories."""
    output_dir = Path("output")
    logs_dir = Path("logs")

    if output_dir.exists() and logs_dir.exists():
        print(f"[OK] Directories: output/ and logs/")
        return True

    print("[WARN] Creating directories...")
    output_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    return True


def main():
    """Run all checks."""
    print("=" * 60)
    print("TerminalAI Setup Verification")
    print("=" * 60)
    print()

    checks = [
        ("Python", check_python),
        ("Package", check_package),
        ("FFmpeg", check_ffmpeg),
        ("NVIDIA GPU", check_nvidia_gpu),
        ("NVENC Encoders", check_nvenc),
        ("NVIDIA Maxine", check_maxine),
        ("Real-ESRGAN", check_realesrgan),
        ("Directories", check_directories),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            results.append((name, False))
        print()

    print("=" * 60)
    print("Summary")
    print("=" * 60)

    required = ["Python", "Package", "FFmpeg"]
    optional = ["NVIDIA GPU", "NVENC Encoders", "NVIDIA Maxine", "Real-ESRGAN"]

    required_ok = all(result for name, result in results if name in required)

    if required_ok:
        print("[OK] Core requirements satisfied")
        print()
        print("You can run:")
        print("  python -m vhs_upscaler.gui                    # Launch web GUI")
        print("  python -m vhs_upscaler.vhs_upscale --help     # CLI help")
    else:
        print("[FAIL] Missing required dependencies")
        print("  Please install missing requirements above")

    print()

    # GPU recommendations
    gpu_available = any(result for name, result in results if name == "NVIDIA GPU")
    if gpu_available:
        print("GPU Acceleration: ENABLED")
        maxine = any(result for name, result in results if name == "NVIDIA Maxine")
        realesrgan = any(result for name, result in results if name == "Real-ESRGAN")

        if maxine:
            print("  Recommended engine: --engine maxine (best quality)")
        elif realesrgan:
            print("  Recommended engine: --engine realesrgan (good quality)")
        else:
            print("  Available engine: --engine ffmpeg (basic)")
    else:
        print("GPU Acceleration: DISABLED")
        print("  Available engine: --engine ffmpeg --encoder libx265 (CPU)")

    print()


if __name__ == "__main__":
    main()
