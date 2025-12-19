"""
RTX Video SDK Data Models
=========================

Defines configuration classes, enums, and data structures for RTX Video SDK.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


class EffectType(Enum):
    """Available RTX Video SDK effects."""
    SUPER_RESOLUTION = "SuperRes"
    ARTIFACT_REDUCTION = "ArtifactReduction"
    HDR_CONVERSION = "HDR"
    UPSCALE_PIPELINE = "UpscalePipeline"  # Combined SR + AR


class HDRFormat(Enum):
    """HDR output format options."""
    SDR = "sdr"
    HDR10 = "hdr10"
    HLG = "hlg"


class ScaleFactor(Enum):
    """Supported upscale factors."""
    X1_33 = 1.33  # 4/3x
    X1_5 = 1.5
    X2 = 2
    X3 = 3
    X4 = 4


class Precision(Enum):
    """Computation precision modes."""
    FP16 = "fp16"
    FP32 = "fp32"


@dataclass
class GPUInfo:
    """Information about detected NVIDIA GPU."""
    name: str
    compute_capability: tuple
    memory_mb: int
    is_supported: bool
    driver_version: str
    cuda_version: str = ""

    def __str__(self) -> str:
        status = "✓ Supported" if self.is_supported else "✗ Not supported"
        return (
            f"{self.name} (CC {self.compute_capability[0]}.{self.compute_capability[1]}, "
            f"{self.memory_mb}MB VRAM) - {status}"
        )


@dataclass
class SDKInfo:
    """Information about RTX Video SDK installation."""
    path: str
    version: str
    dll_path: str
    models_path: str
    is_valid: bool
    error_message: str = ""


@dataclass
class RTXVideoConfig:
    """
    Configuration for RTX Video SDK processing.

    Attributes:
        enable_super_resolution: Enable AI upscaling
        enable_artifact_reduction: Enable compression artifact removal
        enable_hdr_conversion: Enable SDR to HDR10 conversion
        scale_factor: Upscaling factor (2 or 4)
        target_resolution: Target output height (720, 1080, 1440, 2160)
        artifact_strength: Artifact reduction strength (0.0-1.0)
        hdr_format: Output HDR format (sdr, hdr10, hlg)
        peak_brightness: HDR peak brightness in nits (100-1000)
        gpu_id: GPU device ID for multi-GPU systems
        precision: Computation precision (fp16, fp32)
        sdk_path: Override SDK installation path
        model_path: Override models directory path
    """

    # Effect toggles
    enable_super_resolution: bool = True
    enable_artifact_reduction: bool = True
    enable_hdr_conversion: bool = False

    # Super Resolution options
    scale_factor: int = 4  # 2 or 4
    target_resolution: int = 1080  # 720, 1080, 1440, 2160

    # Artifact Reduction options
    artifact_strength: float = 0.5  # 0.0-1.0

    # HDR options
    hdr_format: HDRFormat = field(default=HDRFormat.SDR)
    peak_brightness: int = 400  # nits (100-1000)
    hdr_saturation: float = 1.0  # 0.5-2.0

    # Processing options
    gpu_id: int = 0
    precision: Precision = field(default=Precision.FP16)
    batch_size: int = 1  # Frames to process in parallel

    # SDK paths (auto-detected if empty)
    sdk_path: str = ""
    model_path: str = ""

    # Advanced options
    preserve_10bit: bool = True  # Preserve 10-bit input if present
    use_cuda_graphs: bool = True  # Enable CUDA graph optimization

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []

        if self.scale_factor not in [2, 4]:
            errors.append(f"scale_factor must be 2 or 4, got {self.scale_factor}")

        if self.target_resolution not in [720, 1080, 1440, 2160, 4320]:
            errors.append(f"target_resolution must be 720/1080/1440/2160/4320")

        if not 0.0 <= self.artifact_strength <= 1.0:
            errors.append(f"artifact_strength must be 0.0-1.0")

        if not 100 <= self.peak_brightness <= 1000:
            errors.append(f"peak_brightness must be 100-1000 nits")

        if not 0.5 <= self.hdr_saturation <= 2.0:
            errors.append(f"hdr_saturation must be 0.5-2.0")

        return errors

    def get_effect_type(self) -> EffectType:
        """Determine which SDK effect to use based on config."""
        if self.enable_super_resolution and self.enable_artifact_reduction:
            return EffectType.UPSCALE_PIPELINE
        elif self.enable_super_resolution:
            return EffectType.SUPER_RESOLUTION
        elif self.enable_artifact_reduction:
            return EffectType.ARTIFACT_REDUCTION
        elif self.enable_hdr_conversion:
            return EffectType.HDR_CONVERSION
        else:
            return EffectType.SUPER_RESOLUTION  # Default


@dataclass
class ProcessingStats:
    """Statistics from video processing."""
    total_frames: int = 0
    processed_frames: int = 0
    skipped_frames: int = 0
    input_resolution: tuple = (0, 0)
    output_resolution: tuple = (0, 0)
    processing_time_seconds: float = 0.0
    avg_frame_time_ms: float = 0.0
    gpu_memory_peak_mb: int = 0

    @property
    def frames_per_second(self) -> float:
        """Calculate processing FPS."""
        if self.processing_time_seconds > 0:
            return self.processed_frames / self.processing_time_seconds
        return 0.0
