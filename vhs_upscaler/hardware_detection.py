#!/usr/bin/env python3
"""
Hardware Detection and Auto-Configuration
==========================================
Automatically detect GPU capabilities and configure optimal processing settings.

Features:
- NVIDIA GPU detection (RTX series, GTX series, compute capability)
- AMD GPU detection (Radeon series)
- Intel GPU detection
- VRAM detection
- NVENC/hardware encoder availability
- RTX Video SDK installation check
- PyTorch CUDA availability
- Optimal configuration recommendation

Usage:
    from vhs_upscaler.hardware_detection import detect_hardware, get_optimal_config

    hw = detect_hardware()
    config = get_optimal_config(hw)
    print(f"Configured for: {hw.display_name}")
    print(f"Upscale engine: {config['upscale_engine']}")
"""

import logging
import os
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class GPUVendor(Enum):
    """GPU vendor types."""
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    CPU_ONLY = "cpu"


class GPUTier(Enum):
    """GPU performance tiers."""
    RTX_50_SERIES = "rtx_50"  # RTX 5090, 5080, 5070, etc.
    RTX_40_SERIES = "rtx_40"  # RTX 4090, 4080, 4070, etc.
    RTX_30_SERIES = "rtx_30"  # RTX 3090, 3080, 3070, 3060, etc.
    RTX_20_SERIES = "rtx_20"  # RTX 2080 Ti, 2070, 2060, etc.
    GTX_16_SERIES = "gtx_16"  # GTX 1660 Ti, 1650, etc.
    GTX_10_SERIES = "gtx_10"  # GTX 1080 Ti, 1070, 1060, etc.
    GTX_LEGACY = "gtx_legacy"  # GTX 900 series and older
    AMD_RDNA3 = "amd_rdna3"    # RX 7000 series
    AMD_RDNA2 = "amd_rdna2"    # RX 6000 series
    AMD_RDNA = "amd_rdna"      # RX 5000 series
    AMD_LEGACY = "amd_legacy"  # Older AMD cards
    INTEL_ARC = "intel_arc"    # Intel Arc series
    INTEL_INTEGRATED = "intel_integrated"  # Intel iGPU
    CPU_ONLY = "cpu_only"


@dataclass
class HardwareInfo:
    """Complete hardware detection results."""
    vendor: GPUVendor
    tier: GPUTier
    name: str
    vram_gb: float
    driver_version: Optional[str] = None
    cuda_version: Optional[str] = None
    compute_capability: Optional[str] = None

    # Capabilities
    has_nvenc: bool = False
    has_rtx_video_sdk: bool = False
    has_cuda: bool = False
    has_vulkan: bool = False

    # Additional info
    gpu_count: int = 1
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def display_name(self) -> str:
        """Human-readable GPU name for display."""
        if self.vendor == GPUVendor.CPU_ONLY:
            return "CPU (No GPU detected)"
        return f"{self.name} ({self.vram_gb:.0f}GB VRAM)"

    @property
    def supports_ai_upscaling(self) -> bool:
        """Check if GPU supports AI upscaling."""
        if self.vendor == GPUVendor.NVIDIA:
            # RTX 20+ series best with RTX Video SDK
            # GTX 10+ series good with Real-ESRGAN
            return self.tier in [
                GPUTier.RTX_50_SERIES, GPUTier.RTX_40_SERIES, GPUTier.RTX_30_SERIES, GPUTier.RTX_20_SERIES,
                GPUTier.GTX_16_SERIES, GPUTier.GTX_10_SERIES
            ]
        elif self.vendor in [GPUVendor.AMD, GPUVendor.INTEL]:
            # AMD/Intel can use Real-ESRGAN via Vulkan
            return True
        return False

    @property
    def supports_hardware_encoding(self) -> bool:
        """Check if GPU supports hardware video encoding."""
        return self.has_nvenc or self.vendor in [GPUVendor.AMD, GPUVendor.INTEL]

    @property
    def is_rtx_capable(self) -> bool:
        """Check if GPU supports RTX Video SDK."""
        return self.tier in [
            GPUTier.RTX_50_SERIES, GPUTier.RTX_40_SERIES, GPUTier.RTX_30_SERIES, GPUTier.RTX_20_SERIES
        ]


def detect_nvidia_gpu() -> Optional[HardwareInfo]:
    """
    Detect NVIDIA GPU using nvidia-smi.

    Returns:
        HardwareInfo if NVIDIA GPU found, None otherwise
    """
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version,compute_cap",
             "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )

        lines = result.stdout.strip().split("\n")
        if not lines or not lines[0]:
            return None

        # Parse first GPU
        parts = [p.strip() for p in lines[0].split(",")]
        if len(parts) < 3:
            return None

        name = parts[0]
        vram_str = parts[1]
        driver = parts[2]
        compute_cap = parts[3] if len(parts) > 3 else None

        # Parse VRAM (convert from MiB to GB)
        vram_gb = 0.0
        try:
            if "MiB" in vram_str:
                vram_gb = float(vram_str.replace("MiB", "").strip()) / 1024
            elif "GiB" in vram_str:
                vram_gb = float(vram_str.replace("GiB", "").strip())
            else:
                # Try as raw number (assume MB)
                vram_gb = float(vram_str) / 1024
        except ValueError:
            vram_gb = 8.0  # Default assumption

        # Determine tier from name
        tier = _classify_nvidia_tier(name)

        # Check NVENC support (GTX 10 series and newer)
        has_nvenc = tier in [
            GPUTier.RTX_50_SERIES, GPUTier.RTX_40_SERIES, GPUTier.RTX_30_SERIES, GPUTier.RTX_20_SERIES,
            GPUTier.GTX_16_SERIES, GPUTier.GTX_10_SERIES
        ]

        # Check RTX Video SDK installation
        has_rtx_sdk = _check_rtx_video_sdk_installed()

        # CUDA is available if NVIDIA GPU is detected (confirmed by nvidia-smi)
        # Don't import PyTorch during detection - let installer handle PyTorch installation
        has_cuda = True  # nvidia-smi success means CUDA driver is installed

        # Get CUDA version from nvidia-smi
        cuda_version = None
        try:
            cuda_result = subprocess.run(
                ["nvidia-smi", "--query-gpu=cuda_version", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            cuda_version = cuda_result.stdout.strip().split("\n")[0].strip()
        except Exception:
            pass

        return HardwareInfo(
            vendor=GPUVendor.NVIDIA,
            tier=tier,
            name=name,
            vram_gb=vram_gb,
            driver_version=driver,
            cuda_version=cuda_version,
            compute_capability=compute_cap,
            has_nvenc=has_nvenc,
            has_rtx_video_sdk=has_rtx_sdk,
            has_cuda=has_cuda,
            has_vulkan=True,  # NVIDIA cards support Vulkan
            gpu_count=len(lines),
            details={"raw_output": result.stdout}
        )

    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None
    except Exception as e:
        logger.debug(f"NVIDIA detection error: {e}")
        return None


def detect_amd_gpu() -> Optional[HardwareInfo]:
    """
    Detect AMD GPU using system tools.

    Returns:
        HardwareInfo if AMD GPU found, None otherwise
    """
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name,AdapterRAM"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )

            for line in result.stdout.split("\n"):
                if "AMD" in line or "Radeon" in line:
                    parts = line.strip().split()
                    name = " ".join([p for p in parts if not p.isdigit()])

                    # Try to extract VRAM
                    vram_gb = 8.0  # Default
                    try:
                        vram_bytes = int([p for p in parts if p.isdigit()][0])
                        vram_gb = vram_bytes / (1024**3)
                    except (IndexError, ValueError):
                        pass

                    tier = _classify_amd_tier(name)

                    return HardwareInfo(
                        vendor=GPUVendor.AMD,
                        tier=tier,
                        name=name.strip(),
                        vram_gb=vram_gb,
                        has_vulkan=True,
                        details={"detection_method": "wmic"}
                    )

        elif sys.platform in ["linux", "darwin"]:
            # Try lspci on Linux/Mac
            result = subprocess.run(
                ["lspci"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )

            for line in result.stdout.split("\n"):
                if "AMD" in line or "Radeon" in line:
                    name = line.split(":", 2)[-1].strip() if ":" in line else line.strip()
                    tier = _classify_amd_tier(name)

                    return HardwareInfo(
                        vendor=GPUVendor.AMD,
                        tier=tier,
                        name=name,
                        vram_gb=8.0,  # Can't easily detect on Linux
                        has_vulkan=True,
                        details={"detection_method": "lspci"}
                    )

    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    except Exception as e:
        logger.debug(f"AMD detection error: {e}")

    return None


def detect_intel_gpu() -> Optional[HardwareInfo]:
    """
    Detect Intel GPU using system tools.

    Returns:
        HardwareInfo if Intel GPU found, None otherwise
    """
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )

            for line in result.stdout.split("\n"):
                if "Intel" in line:
                    name = line.strip()
                    tier = _classify_intel_tier(name)

                    # Intel iGPU typically has shared memory
                    vram_gb = 2.0 if tier == GPUTier.INTEL_INTEGRATED else 8.0

                    return HardwareInfo(
                        vendor=GPUVendor.INTEL,
                        tier=tier,
                        name=name,
                        vram_gb=vram_gb,
                        has_vulkan=True,
                        details={"detection_method": "wmic"}
                    )

        elif sys.platform in ["linux", "darwin"]:
            result = subprocess.run(
                ["lspci"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )

            for line in result.stdout.split("\n"):
                if "Intel" in line and ("VGA" in line or "Graphics" in line):
                    name = line.split(":", 2)[-1].strip() if ":" in line else line.strip()
                    tier = _classify_intel_tier(name)
                    vram_gb = 2.0 if tier == GPUTier.INTEL_INTEGRATED else 8.0

                    return HardwareInfo(
                        vendor=GPUVendor.INTEL,
                        tier=tier,
                        name=name,
                        vram_gb=vram_gb,
                        has_vulkan=True,
                        details={"detection_method": "lspci"}
                    )

    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    except Exception as e:
        logger.debug(f"Intel detection error: {e}")

    return None


def detect_hardware() -> HardwareInfo:
    """
    Detect all available hardware and return best GPU.

    Priority: NVIDIA > AMD > Intel > CPU-only

    Returns:
        HardwareInfo object with detection results
    """
    try:
        # Try NVIDIA first (best support)
        logger.debug("Attempting NVIDIA GPU detection...")
        nvidia_gpu = detect_nvidia_gpu()
        if nvidia_gpu:
            logger.info(f"Detected: {nvidia_gpu.display_name}")
            return nvidia_gpu
        logger.debug("No NVIDIA GPU found")

        # Try AMD second
        logger.debug("Attempting AMD GPU detection...")
        amd_gpu = detect_amd_gpu()
        if amd_gpu:
            logger.info(f"Detected: {amd_gpu.display_name}")
            return amd_gpu
        logger.debug("No AMD GPU found")

        # Try Intel third
        logger.debug("Attempting Intel GPU detection...")
        intel_gpu = detect_intel_gpu()
        if intel_gpu:
            logger.info(f"Detected: {intel_gpu.display_name}")
            return intel_gpu
        logger.debug("No Intel GPU found")

        # Fallback to CPU-only
        logger.info("No GPU detected - using CPU-only mode")
        return HardwareInfo(
            vendor=GPUVendor.CPU_ONLY,
            tier=GPUTier.CPU_ONLY,
            name="CPU",
            vram_gb=0.0
        )
    except Exception as e:
        logger.error(f"Hardware detection failed with error: {e}", exc_info=True)
        # Return CPU-only fallback on any error
        return HardwareInfo(
            vendor=GPUVendor.CPU_ONLY,
            tier=GPUTier.CPU_ONLY,
            name="CPU",
            vram_gb=0.0
        )


def get_optimal_config(hw: HardwareInfo) -> Dict[str, Any]:
    """
    Get optimal configuration for detected hardware.

    Args:
        hw: HardwareInfo object from detect_hardware()

    Returns:
        Dictionary with recommended settings:
        - upscale_engine: 'rtxvideo', 'realesrgan', or 'ffmpeg'
        - encoder: 'hevc_nvenc', 'h264_nvenc', 'libx265', etc.
        - quality: 'best', 'balanced', or 'good'
        - face_restore: True/False
        - audio_upmix: 'demucs', 'surround', 'simple'
        - realesrgan_model: Model name for Real-ESRGAN
        - explanation: User-friendly explanation
        - warnings: List of warnings/limitations
    """
    config = {
        "upscale_engine": "ffmpeg",
        "encoder": "libx265",
        "quality": "good",
        "face_restore": False,
        "audio_upmix": "simple",
        "realesrgan_model": "realesrgan-x4plus",
        "explanation": "",
        "warnings": []
    }

    if hw.vendor == GPUVendor.NVIDIA:
        # RTX 50 series - Next-gen, best quality, all features
        if hw.tier == GPUTier.RTX_50_SERIES:
            config.update({
                "upscale_engine": "rtxvideo" if hw.has_rtx_video_sdk else "realesrgan",
                "encoder": "hevc_nvenc",
                "quality": "best",
                "face_restore": True,
                "audio_upmix": "demucs" if hw.has_cuda else "surround",
                "explanation": f"Using RTX 50 series for maximum quality. {hw.name} detected with {hw.vram_gb:.0f}GB VRAM."
            })
            if not hw.has_rtx_video_sdk:
                config["warnings"].append(
                    "RTX Video SDK not installed. Using Real-ESRGAN instead. "
                    "Install RTX Video SDK for best quality: terminalai-setup-rtx"
                )

        # RTX 40 series - Best quality, all features
        elif hw.tier == GPUTier.RTX_40_SERIES:
            config.update({
                "upscale_engine": "rtxvideo" if hw.has_rtx_video_sdk else "realesrgan",
                "encoder": "hevc_nvenc",
                "quality": "best",
                "face_restore": True,
                "audio_upmix": "demucs" if hw.has_cuda else "surround",
                "explanation": f"Using RTX 40 series for maximum quality. {hw.name} detected with {hw.vram_gb:.0f}GB VRAM."
            })
            if not hw.has_rtx_video_sdk:
                config["warnings"].append(
                    "RTX Video SDK not installed. Using Real-ESRGAN instead. "
                    "Install RTX Video SDK for best quality: terminalai-setup-rtx"
                )

        # RTX 30 series - Excellent quality
        elif hw.tier == GPUTier.RTX_30_SERIES:
            config.update({
                "upscale_engine": "rtxvideo" if hw.has_rtx_video_sdk else "realesrgan",
                "encoder": "hevc_nvenc",
                "quality": "best",
                "face_restore": True if hw.vram_gb >= 6 else False,
                "audio_upmix": "demucs" if hw.has_cuda and hw.vram_gb >= 8 else "surround",
                "explanation": f"Using RTX 30 series for excellent quality. {hw.name} with {hw.vram_gb:.0f}GB VRAM."
            })
            if not hw.has_rtx_video_sdk:
                config["warnings"].append(
                    "RTX Video SDK not installed. Install for best quality: terminalai-setup-rtx"
                )
            if hw.vram_gb < 6:
                config["warnings"].append(
                    "Limited VRAM - face restoration disabled to prevent out-of-memory errors"
                )

        # RTX 20 series - Very good quality
        elif hw.tier == GPUTier.RTX_20_SERIES:
            config.update({
                "upscale_engine": "rtxvideo" if hw.has_rtx_video_sdk else "realesrgan",
                "encoder": "hevc_nvenc",
                "quality": "balanced",
                "face_restore": True if hw.vram_gb >= 6 else False,
                "audio_upmix": "surround",
                "explanation": f"Using RTX 20 series for good quality. {hw.name} with {hw.vram_gb:.0f}GB VRAM."
            })
            if not hw.has_rtx_video_sdk:
                config["warnings"].append(
                    "RTX Video SDK not installed. Install for AI upscaling: terminalai-setup-rtx"
                )

        # GTX 16 series - Good quality
        elif hw.tier == GPUTier.GTX_16_SERIES:
            config.update({
                "upscale_engine": "realesrgan",
                "encoder": "h264_nvenc",
                "quality": "balanced",
                "face_restore": False,  # Slower on GTX, disabled for better performance
                "audio_upmix": "surround",
                "explanation": f"Using GTX 16 series with GPU encoding. {hw.name} with {hw.vram_gb:.0f}GB VRAM."
            })
            config["warnings"].append(
                "GTX 16 series doesn't support RTX Video SDK. Using Real-ESRGAN for AI upscaling."
            )
            if hw.vram_gb >= 8:
                config["warnings"].append(
                    "Face restoration disabled for better performance. Enable manually if needed."
                )

        # GTX 10 series - Decent quality
        elif hw.tier == GPUTier.GTX_10_SERIES:
            config.update({
                "upscale_engine": "realesrgan",
                "encoder": "h264_nvenc",
                "quality": "balanced",
                "face_restore": False,  # Too slow on GTX 10
                "audio_upmix": "simple",
                "explanation": f"Using GTX 10 series with GPU encoding. {hw.name} with {hw.vram_gb:.0f}GB VRAM."
            })
            config["warnings"].append(
                "GTX 10 series has limited AI processing power. Face restoration disabled for better performance."
            )

        # Legacy GTX - Basic
        else:
            config.update({
                "upscale_engine": "ffmpeg",
                "encoder": "h264_nvenc" if hw.has_nvenc else "libx264",
                "quality": "good",
                "face_restore": False,
                "audio_upmix": "simple",
                "explanation": f"Using legacy GPU with basic encoding. {hw.name}."
            })
            config["warnings"].append(
                "Legacy GPU detected. Limited AI features available. Consider upgrading for better quality."
            )

    elif hw.vendor == GPUVendor.AMD:
        # AMD RDNA 3 (RX 7000)
        if hw.tier == GPUTier.AMD_RDNA3:
            config.update({
                "upscale_engine": "realesrgan",
                "encoder": "libx265",  # AMD VCE encoding support varies
                "quality": "balanced",
                "face_restore": False,  # CUDA-only for now
                "audio_upmix": "surround",
                "explanation": f"Using AMD RDNA3 with Real-ESRGAN (Vulkan). {hw.name}."
            })
            config["warnings"].append(
                "AMD GPU detected. Using Vulkan-based Real-ESRGAN. Some CUDA-only features unavailable."
            )

        # AMD RDNA 2 (RX 6000)
        elif hw.tier == GPUTier.AMD_RDNA2:
            config.update({
                "upscale_engine": "realesrgan",
                "encoder": "libx265",
                "quality": "balanced",
                "face_restore": False,
                "audio_upmix": "simple",
                "explanation": f"Using AMD RDNA2 with Real-ESRGAN (Vulkan). {hw.name}."
            })
            config["warnings"].append(
                "AMD GPU detected. Real-ESRGAN available via Vulkan. CUDA features unavailable."
            )

        # Older AMD
        else:
            config.update({
                "upscale_engine": "ffmpeg",
                "encoder": "libx265",
                "quality": "good",
                "face_restore": False,
                "audio_upmix": "simple",
                "explanation": f"Using AMD GPU with CPU encoding. {hw.name}."
            })
            config["warnings"].append(
                "Older AMD GPU detected. Limited acceleration available."
            )

    elif hw.vendor == GPUVendor.INTEL:
        # Intel Arc
        if hw.tier == GPUTier.INTEL_ARC:
            config.update({
                "upscale_engine": "realesrgan",
                "encoder": "libx265",
                "quality": "balanced",
                "face_restore": False,
                "audio_upmix": "simple",
                "explanation": f"Using Intel Arc with Real-ESRGAN (Vulkan). {hw.name}."
            })
            config["warnings"].append(
                "Intel Arc GPU detected. Using Vulkan-based acceleration."
            )

        # Integrated GPU
        else:
            config.update({
                "upscale_engine": "ffmpeg",
                "encoder": "libx265",
                "quality": "good",
                "face_restore": False,
                "audio_upmix": "simple",
                "explanation": f"Using Intel integrated GPU with CPU encoding. {hw.name}."
            })
            config["warnings"].append(
                "Intel integrated GPU has limited performance. Processing will be slow."
            )

    else:  # CPU-only
        config.update({
            "upscale_engine": "ffmpeg",
            "encoder": "libx265",
            "quality": "good",
            "face_restore": False,
            "audio_upmix": "simple",
            "explanation": "No GPU detected. Using CPU-only mode (very slow)."
        })
        config["warnings"].extend([
            "No GPU detected. Processing will be VERY slow (10-50x slower).",
            "Consider using a system with GPU for practical use.",
            "AI features (upscaling, face restoration) unavailable."
        ])

    return config


def _classify_nvidia_tier(name: str) -> GPUTier:
    """Classify NVIDIA GPU tier from name."""
    name_upper = name.upper()

    if "RTX" in name_upper:
        if any(x in name_upper for x in ["5090", "5080", "5070", "5060"]):
            return GPUTier.RTX_50_SERIES
        elif any(x in name_upper for x in ["4090", "4080", "4070", "4060"]):
            return GPUTier.RTX_40_SERIES
        elif any(x in name_upper for x in ["3090", "3080", "3070", "3060"]):
            return GPUTier.RTX_30_SERIES
        elif any(x in name_upper for x in ["2080", "2070", "2060"]):
            return GPUTier.RTX_20_SERIES
    elif "GTX" in name_upper:
        if any(x in name_upper for x in ["1660", "1650"]):
            return GPUTier.GTX_16_SERIES
        elif any(x in name_upper for x in ["1080", "1070", "1060"]):
            return GPUTier.GTX_10_SERIES
        else:
            return GPUTier.GTX_LEGACY

    return GPUTier.GTX_LEGACY


def _classify_amd_tier(name: str) -> GPUTier:
    """Classify AMD GPU tier from name."""
    name_upper = name.upper()

    if "RX 7" in name_upper or "7900" in name_upper or "7800" in name_upper:
        return GPUTier.AMD_RDNA3
    elif "RX 6" in name_upper or "6900" in name_upper or "6800" in name_upper:
        return GPUTier.AMD_RDNA2
    elif "RX 5" in name_upper or "5700" in name_upper:
        return GPUTier.AMD_RDNA
    else:
        return GPUTier.AMD_LEGACY


def _classify_intel_tier(name: str) -> GPUTier:
    """Classify Intel GPU tier from name."""
    name_upper = name.upper()

    if "ARC" in name_upper:
        return GPUTier.INTEL_ARC
    else:
        return GPUTier.INTEL_INTEGRATED


def _check_rtx_video_sdk_installed() -> bool:
    """
    Check if RTX Video SDK is installed.

    Checks environment variables and common installation paths.
    Avoids importing RTX SDK module to prevent hanging.

    Returns:
        True if RTX Video SDK installation detected, False otherwise
    """
    try:
        # Check environment variable
        rtx_home = os.environ.get("RTX_VIDEO_SDK_HOME")
        if rtx_home and Path(rtx_home).exists():
            logger.debug(f"RTX Video SDK found via RTX_VIDEO_SDK_HOME: {rtx_home}")
            return True

        # Check common installation paths
        if sys.platform == "win32":
            common_paths = [
                Path("C:/Program Files/NVIDIA Corporation/NVIDIA RTX Video SDK"),
                Path("C:/Program Files/NVIDIA/RTX Video SDK"),
                Path.home() / "NVIDIA RTX Video SDK"
            ]
            for path in common_paths:
                if path.exists():
                    logger.debug(f"RTX Video SDK found at: {path}")
                    return True

        # Don't try importing RTX SDK module during detection
        # It can hang or be slow on initialization
        # Just check for file-based installation markers

        logger.debug("RTX Video SDK not found in common locations")
        return False

    except Exception as e:
        logger.debug(f"Error checking RTX Video SDK installation: {e}")
        return False


def _check_pytorch_cuda() -> bool:
    """
    Check if PyTorch with CUDA is available.

    Returns:
        True if PyTorch is installed and CUDA is available, False otherwise
    """
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            logger.debug(f"PyTorch CUDA available: {torch.version.cuda}")
        return cuda_available
    except ImportError:
        logger.debug("PyTorch not installed")
        return False
    except Exception as e:
        logger.debug(f"Error checking PyTorch CUDA: {e}")
        return False


def print_hardware_report(hw: HardwareInfo, config: Dict[str, Any]) -> None:
    """
    Print formatted hardware detection report.

    Args:
        hw: HardwareInfo object with detected hardware details
        config: Configuration dictionary from get_optimal_config()
    """
    print()
    print("=" * 70)
    print("Hardware Detection Report")
    print("=" * 70)
    print()

    print(f"GPU: {hw.display_name}")
    print(f"Vendor: {hw.vendor.value.upper()}")

    if hw.driver_version:
        print(f"Driver: {hw.driver_version}")
    if hw.cuda_version:
        print(f"CUDA: {hw.cuda_version}")
    if hw.compute_capability:
        print(f"Compute Capability: {hw.compute_capability}")

    print()
    print("Capabilities:")
    print(f"  AI Upscaling: {'Yes' if hw.supports_ai_upscaling else 'No'}")
    print(f"  Hardware Encoding: {'Yes' if hw.supports_hardware_encoding else 'No'}")
    print(f"  RTX Video SDK: {'Yes' if hw.has_rtx_video_sdk else 'No'}")
    print(f"  CUDA Acceleration: {'Yes' if hw.has_cuda else 'No'}")
    print(f"  Vulkan Support: {'Yes' if hw.has_vulkan else 'No'}")

    print()
    print("Recommended Configuration:")
    print(f"  Upscale Engine: {config['upscale_engine']}")
    print(f"  Video Encoder: {config['encoder']}")
    print(f"  Quality Mode: {config['quality']}")
    print(f"  Face Restoration: {'Enabled' if config['face_restore'] else 'Disabled'}")
    print(f"  Audio Upmix: {config['audio_upmix']}")

    if config.get('realesrgan_model'):
        print(f"  Real-ESRGAN Model: {config['realesrgan_model']}")

    print()
    print(f"Explanation: {config['explanation']}")

    if config['warnings']:
        print()
        print("Warnings:")
        for warning in config['warnings']:
            print(f"  - {warning}")

    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    # Self-test
    logging.basicConfig(level=logging.INFO)

    hw = detect_hardware()
    config = get_optimal_config(hw)
    print_hardware_report(hw, config)
