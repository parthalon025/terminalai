"""
RTX Video SDK Utility Functions
===============================

SDK detection, GPU validation, and helper functions.
"""

import logging
import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from .models import GPUInfo, SDKInfo

logger = logging.getLogger(__name__)

# Expected SDK installation locations
SDK_SEARCH_PATHS = [
    # Environment variable (highest priority)
    lambda: Path(os.environ.get("RTX_VIDEO_SDK_HOME", "")),
    # Standard installation paths
    lambda: Path(os.environ.get("LOCALAPPDATA", "")) / "NVIDIA" / "RTXVideoSDK",
    lambda: Path("C:/Program Files/NVIDIA Corporation/RTX Video SDK"),
    lambda: Path("C:/Program Files/NVIDIA/RTXVideoSDK"),
    lambda: Path("C:/NVIDIA/RTXVideoSDK"),
    # User home locations
    lambda: Path.home() / "RTXVideoSDK",
    lambda: Path.home() / "NVIDIA" / "RTXVideoSDK",
]

# DLL names to search for
SDK_DLL_NAMES = [
    "NVVideoEffects.dll",
    "nvVideoEffects.dll",
    "NvVFX.dll",
]

# Minimum supported driver version
MIN_DRIVER_VERSION = "535.0"

# Minimum compute capability (RTX 20 series = Turing = 7.5)
MIN_COMPUTE_CAPABILITY = (7, 5)


def detect_sdk() -> Optional[Path]:
    """
    Detect RTX Video SDK installation.

    Searches common installation paths and environment variables.

    Returns:
        Path to SDK directory if found, None otherwise.
    """
    if platform.system() != "Windows":
        logger.debug("RTX Video SDK only supports Windows")
        return None

    for path_fn in SDK_SEARCH_PATHS:
        try:
            sdk_path = path_fn()
            if not sdk_path or not sdk_path.exists():
                continue

            # Check for SDK DLL in lib or bin directories
            for dll_name in SDK_DLL_NAMES:
                for subdir in ["lib", "bin", "lib64", ""]:
                    dll_path = sdk_path / subdir / dll_name if subdir else sdk_path / dll_name
                    if dll_path.exists():
                        logger.info(f"RTX Video SDK found at: {sdk_path}")
                        return sdk_path

        except Exception as e:
            logger.debug(f"Error checking SDK path: {e}")
            continue

    logger.debug("RTX Video SDK not found in standard locations")
    return None


def get_sdk_info(sdk_path: Optional[Path] = None) -> SDKInfo:
    """
    Get detailed information about SDK installation.

    Args:
        sdk_path: SDK directory path, or None to auto-detect

    Returns:
        SDKInfo with installation details
    """
    if sdk_path is None:
        sdk_path = detect_sdk()

    if sdk_path is None:
        return SDKInfo(
            path="",
            version="",
            dll_path="",
            models_path="",
            is_valid=False,
            error_message="SDK not found. Download from: https://developer.nvidia.com/rtx-video-sdk"
        )

    # Find DLL
    dll_path = ""
    for dll_name in SDK_DLL_NAMES:
        for subdir in ["lib", "bin", "lib64", ""]:
            candidate = sdk_path / subdir / dll_name if subdir else sdk_path / dll_name
            if candidate.exists():
                dll_path = str(candidate)
                break
        if dll_path:
            break

    if not dll_path:
        return SDKInfo(
            path=str(sdk_path),
            version="",
            dll_path="",
            models_path="",
            is_valid=False,
            error_message=f"SDK DLL not found in {sdk_path}"
        )

    # Find models directory
    models_path = ""
    for models_dir in ["models", "lib/models", "bin/models"]:
        candidate = sdk_path / models_dir
        if candidate.exists() and candidate.is_dir():
            models_path = str(candidate)
            break

    # Get version
    version = get_sdk_version(sdk_path)

    return SDKInfo(
        path=str(sdk_path),
        version=version or "unknown",
        dll_path=dll_path,
        models_path=models_path,
        is_valid=True,
    )


def get_sdk_version(sdk_path: Path) -> Optional[str]:
    """
    Get SDK version from version file or manifest.

    Args:
        sdk_path: SDK installation directory

    Returns:
        Version string if found, None otherwise
    """
    # Check version.txt
    version_file = sdk_path / "version.txt"
    if version_file.exists():
        try:
            return version_file.read_text().strip()
        except Exception:
            pass

    # Check version in manifest or readme
    for filename in ["manifest.json", "README.txt", "README.md"]:
        filepath = sdk_path / filename
        if filepath.exists():
            try:
                content = filepath.read_text()
                # Look for version pattern
                match = re.search(r"version[:\s]+v?(\d+\.\d+\.?\d*)", content, re.IGNORECASE)
                if match:
                    return match.group(1)
            except Exception:
                pass

    return None


def validate_gpu() -> GPUInfo:
    """
    Validate that a compatible NVIDIA GPU is available.

    Checks for RTX 20 series or newer (Turing architecture, CC 7.5+).

    Returns:
        GPUInfo with GPU details and compatibility status.
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,compute_cap,memory.total,driver_version",
                "--format=csv,noheader,nounits"
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            parts = result.stdout.strip().split(", ")
            if len(parts) >= 4:
                name = parts[0].strip()
                compute_cap = tuple(map(int, parts[1].strip().split(".")))
                memory_mb = int(float(parts[2].strip()))
                driver_version = parts[3].strip()

                # RTX 20 series requires compute capability 7.5+
                is_supported = compute_cap >= MIN_COMPUTE_CAPABILITY

                # Also check driver version
                try:
                    driver_major = float(driver_version.split(".")[0])
                    min_driver_major = float(MIN_DRIVER_VERSION.split(".")[0])
                    if driver_major < min_driver_major:
                        is_supported = False
                        logger.warning(
                            f"Driver version {driver_version} is below minimum {MIN_DRIVER_VERSION}"
                        )
                except ValueError:
                    pass

                return GPUInfo(
                    name=name,
                    compute_capability=compute_cap,
                    memory_mb=memory_mb,
                    is_supported=is_supported,
                    driver_version=driver_version,
                )

    except FileNotFoundError:
        logger.warning("nvidia-smi not found - NVIDIA driver may not be installed")
    except subprocess.TimeoutExpired:
        logger.warning("nvidia-smi timed out")
    except Exception as e:
        logger.warning(f"GPU detection failed: {e}")

    return GPUInfo(
        name="Unknown",
        compute_capability=(0, 0),
        memory_mb=0,
        is_supported=False,
        driver_version="Unknown",
    )


def get_cuda_version() -> Optional[str]:
    """Get installed CUDA version."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    # Try nvcc
    try:
        result = subprocess.run(
            ["nvcc", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            match = re.search(r"release (\d+\.\d+)", result.stdout)
            if match:
                return match.group(1)
    except Exception:
        pass

    return None


def is_rtx_video_available() -> Tuple[bool, str]:
    """
    Check if RTX Video SDK is available and ready to use.

    Returns:
        Tuple of (is_available, message explaining status)
    """
    # Check platform
    if platform.system() != "Windows":
        return False, "RTX Video SDK only supports Windows 10/11"

    # Check SDK installation
    sdk_path = detect_sdk()
    if sdk_path is None:
        return False, (
            "RTX Video SDK not installed. "
            "Download from: https://developer.nvidia.com/rtx-video-sdk"
        )

    # Check GPU
    gpu_info = validate_gpu()
    if not gpu_info.is_supported:
        return False, (
            f"GPU not supported: {gpu_info.name}. "
            f"RTX Video SDK requires GeForce RTX 20 series or newer."
        )

    return True, f"RTX Video SDK ready ({gpu_info.name})"


def get_supported_resolutions() -> list:
    """Get list of supported output resolutions."""
    return [720, 1080, 1440, 2160, 4320]


def get_recommended_settings(input_width: int, input_height: int) -> dict:
    """
    Get recommended SDK settings based on input resolution.

    Args:
        input_width: Input video width
        input_height: Input video height

    Returns:
        Dict with recommended configuration values
    """
    # Determine appropriate scale factor
    if input_height <= 480:
        scale_factor = 4  # 480p -> 1920p (4x)
        target_resolution = 1080
    elif input_height <= 720:
        scale_factor = 2  # 720p -> 1440p (2x)
        target_resolution = 1440
    elif input_height <= 1080:
        scale_factor = 2  # 1080p -> 2160p (2x)
        target_resolution = 2160
    else:
        scale_factor = 2  # Keep at 2x for large inputs
        target_resolution = min(input_height * 2, 4320)

    return {
        "scale_factor": scale_factor,
        "target_resolution": target_resolution,
        "enable_artifact_reduction": input_height <= 720,  # More artifacts in lower res
        "artifact_strength": 0.7 if input_height <= 480 else 0.5,
    }
