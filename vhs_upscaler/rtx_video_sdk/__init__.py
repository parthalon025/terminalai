"""
RTX Video SDK Python Wrapper
============================

Provides Python bindings for NVIDIA RTX Video SDK features:
- Super Resolution (AI upscaling with artifact reduction)
- SDR to HDR10 conversion

Requirements:
- Windows 10/11 64-bit
- GeForce RTX 20 series or newer (Turing/Ampere/Ada/Blackwell)
- RTX Video SDK v1.1.0+ installed

Installation:
    Download from: https://developer.nvidia.com/rtx-video-sdk
    Set RTX_VIDEO_SDK_HOME environment variable to SDK path

Usage:
    from vhs_upscaler.rtx_video_sdk import RTXVideoProcessor, RTXVideoConfig

    config = RTXVideoConfig(
        enable_super_resolution=True,
        enable_artifact_reduction=True,
        scale_factor=4,
    )
    processor = RTXVideoProcessor(config)
    processor.process_video("input.mp4", "output.mp4")
"""

from .models import (
    RTXVideoConfig,
    EffectType,
    GPUInfo,
    HDRFormat,
    ScaleFactor,
)
from .sdk_wrapper import RTXVideoWrapper
from .video_processor import RTXVideoProcessor
from .utils import (
    detect_sdk,
    validate_gpu,
    get_sdk_version,
    is_rtx_video_available,
)

__all__ = [
    # Configuration
    "RTXVideoConfig",
    "EffectType",
    "GPUInfo",
    "HDRFormat",
    "ScaleFactor",
    # Core classes
    "RTXVideoWrapper",
    "RTXVideoProcessor",
    # Utilities
    "detect_sdk",
    "validate_gpu",
    "get_sdk_version",
    "is_rtx_video_available",
]

__version__ = "1.0.0"
