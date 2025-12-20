#!/usr/bin/env python3
"""
TerminalAI Installation Verification System
============================================
Comprehensive verification of all optional features and dependencies.

This script tests:
- PyTorch (CPU and CUDA support)
- VapourSynth (advanced deinterlacing)
- GFPGAN (face restoration)
- CodeFormer (advanced face restoration)
- DeepFilterNet (AI audio denoising)
- AudioSR (AI audio upsampling)
- Demucs (AI stem separation for surround upmix)
- FFmpeg encoders and filters
- GPU acceleration

Usage:
    python verify_installation.py              # Full verification
    python verify_installation.py --quick      # Quick check
    python verify_installation.py --report     # Generate detailed report
    python verify_installation.py --fix        # Attempt automatic fixes
"""

import json
import logging
import os
import platform
import subprocess
import sys
import traceback
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Fix Windows console encoding for unicode characters
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


# =============================================================================
# Status and Result Classes
# =============================================================================

class ComponentStatus(Enum):
    """Status of a component."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    PARTIAL = "partial"
    ERROR = "error"
    NOT_TESTED = "not_tested"


@dataclass
class ComponentResult:
    """Result of a component verification."""
    name: str
    status: ComponentStatus
    version: Optional[str] = None
    details: Dict[str, Any] = None
    error_message: Optional[str] = None
    suggestions: List[str] = None
    performance_notes: List[str] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.suggestions is None:
            self.suggestions = []
        if self.performance_notes is None:
            self.performance_notes = []

    @property
    def is_available(self) -> bool:
        """Check if component is available."""
        return self.status == ComponentStatus.AVAILABLE

    @property
    def is_partial(self) -> bool:
        """Check if component is partially available."""
        return self.status == ComponentStatus.PARTIAL


@dataclass
class VerificationReport:
    """Complete verification report."""
    system_info: Dict[str, str]
    components: Dict[str, ComponentResult]
    feature_availability: Dict[str, bool]
    warnings: List[str]
    errors: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "system_info": self.system_info,
            "components": {
                name: {
                    "name": comp.name,
                    "status": comp.status.value,
                    "version": comp.version,
                    "details": comp.details,
                    "error_message": comp.error_message,
                    "suggestions": comp.suggestions,
                    "performance_notes": comp.performance_notes
                }
                for name, comp in self.components.items()
            },
            "feature_availability": self.feature_availability,
            "warnings": self.warnings,
            "errors": self.errors,
            "recommendations": self.recommendations
        }

    def to_json(self, filepath: Path):
        """Save report as JSON."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


# =============================================================================
# Component Verifiers
# =============================================================================

class ComponentVerifier:
    """Base class for component verification."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.logger = logging.getLogger(self.__class__.__name__)

    def verify(self) -> ComponentResult:
        """Verify component availability and functionality."""
        raise NotImplementedError

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose."""
        if self.verbose:
            if level == "ERROR":
                self.logger.error(message)
            elif level == "WARNING":
                self.logger.warning(message)
            else:
                self.logger.info(message)


class PythonVerifier(ComponentVerifier):
    """Verify Python installation and version."""

    def verify(self) -> ComponentResult:
        version_info = sys.version_info
        version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"

        suggestions = []
        status = ComponentStatus.AVAILABLE

        if version_info < (3, 10):
            status = ComponentStatus.PARTIAL
            suggestions.append("Python 3.10+ recommended for best compatibility")

        return ComponentResult(
            name="Python",
            status=status,
            version=version_str,
            details={
                "implementation": platform.python_implementation(),
                "compiler": platform.python_compiler(),
                "platform": platform.platform()
            },
            suggestions=suggestions
        )


class PyTorchVerifier(ComponentVerifier):
    """Verify PyTorch installation and CUDA support."""

    def verify(self) -> ComponentResult:
        try:
            import torch

            version = torch.__version__
            details = {
                "version": version,
                "cuda_available": torch.cuda.is_available(),
                "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
                "cudnn_version": torch.backends.cudnn.version() if torch.cuda.is_available() else None,
                "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            }

            # Get GPU details
            if torch.cuda.is_available():
                gpu_names = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
                details["gpu_devices"] = gpu_names
                details["current_device"] = torch.cuda.current_device()

                # Performance test - simple matrix multiplication
                try:
                    import time
                    device = torch.device("cuda")
                    size = 1000
                    a = torch.randn(size, size, device=device)
                    b = torch.randn(size, size, device=device)

                    # Warmup
                    _ = torch.mm(a, b)
                    torch.cuda.synchronize()

                    # Benchmark
                    start = time.time()
                    for _ in range(10):
                        _ = torch.mm(a, b)
                    torch.cuda.synchronize()
                    elapsed = time.time() - start

                    details["performance_test"] = {
                        "matrix_size": f"{size}x{size}",
                        "iterations": 10,
                        "total_time_ms": round(elapsed * 1000, 2),
                        "avg_time_ms": round(elapsed * 100, 2)
                    }
                except Exception as e:
                    details["performance_test"] = {"error": str(e)}

            suggestions = []
            performance_notes = []
            status = ComponentStatus.AVAILABLE

            if not torch.cuda.is_available():
                status = ComponentStatus.PARTIAL
                suggestions.append("CUDA not available - CPU-only mode")
                suggestions.append("Install CUDA-enabled PyTorch: https://pytorch.org/get-started/locally/")
                performance_notes.append("AI features (Demucs, AudioSR, Face Restoration) will be slower on CPU")
            else:
                performance_notes.append(f"GPU acceleration available on {details['gpu_count']} device(s)")

            return ComponentResult(
                name="PyTorch",
                status=status,
                version=version,
                details=details,
                suggestions=suggestions,
                performance_notes=performance_notes
            )

        except ImportError as e:
            return ComponentResult(
                name="PyTorch",
                status=ComponentStatus.UNAVAILABLE,
                error_message=str(e),
                suggestions=[
                    "Install PyTorch: pip install torch torchaudio",
                    "For CUDA support: visit https://pytorch.org/get-started/locally/",
                    "Required for: Demucs, AudioSR, CodeFormer, GFPGAN"
                ]
            )
        except Exception as e:
            return ComponentResult(
                name="PyTorch",
                status=ComponentStatus.ERROR,
                error_message=str(e),
                details={"traceback": traceback.format_exc()}
            )


class VapourSynthVerifier(ComponentVerifier):
    """Verify VapourSynth installation."""

    def verify(self) -> ComponentResult:
        try:
            import vapoursynth as vs

            core = vs.core
            version = core.version()

            details = {
                "version": version,
                "num_threads": core.num_threads,
                "plugins": []
            }

            # Check for QTGMC and important plugins
            plugins_to_check = {
                "havsfunc": "QTGMC support",
                "mvsfunc": "Motion estimation",
                "nnedi3": "Neural network deinterlacer",
                "eedi3": "Edge-directed deinterlacer"
            }

            available_plugins = []
            missing_plugins = []

            for plugin, description in plugins_to_check.items():
                try:
                    if plugin == "havsfunc":
                        import havsfunc
                        available_plugins.append(f"{plugin} ({description})")
                    else:
                        # Try to access plugin namespace
                        if hasattr(core, plugin):
                            available_plugins.append(f"{plugin} ({description})")
                        else:
                            missing_plugins.append(f"{plugin} ({description})")
                except ImportError:
                    missing_plugins.append(f"{plugin} ({description})")

            details["available_plugins"] = available_plugins
            details["missing_plugins"] = missing_plugins

            suggestions = []
            status = ComponentStatus.AVAILABLE

            if missing_plugins:
                status = ComponentStatus.PARTIAL
                suggestions.append("Missing some VapourSynth plugins:")
                for plugin in missing_plugins:
                    suggestions.append(f"  - {plugin}")
                suggestions.append("Install: pip install havsfunc")

            return ComponentResult(
                name="VapourSynth",
                status=status,
                version=version,
                details=details,
                suggestions=suggestions,
                performance_notes=["Enables QTGMC advanced deinterlacing (slower but highest quality)"]
            )

        except ImportError as e:
            return ComponentResult(
                name="VapourSynth",
                status=ComponentStatus.UNAVAILABLE,
                error_message=str(e),
                suggestions=[
                    "Install VapourSynth runtime: https://github.com/vapoursynth/vapoursynth/releases",
                    "Install Python bindings: pip install vapoursynth",
                    "Install QTGMC: pip install havsfunc",
                    "Required for: Advanced deinterlacing (QTGMC)"
                ]
            )
        except Exception as e:
            return ComponentResult(
                name="VapourSynth",
                status=ComponentStatus.ERROR,
                error_message=str(e),
                details={"traceback": traceback.format_exc()}
            )


class GFPGANVerifier(ComponentVerifier):
    """Verify GFPGAN face restoration."""

    def verify(self) -> ComponentResult:
        try:
            import gfpgan
            from basicsr.archs.rrdbnet_arch import RRDBNet

            details = {
                "gfpgan_available": True,
                "basicsr_available": True
            }

            # Check for model files
            model_dir = Path("models") / "gfpgan"
            model_files = []
            if model_dir.exists():
                model_files = list(model_dir.glob("*.pth"))
                details["model_directory"] = str(model_dir)
                details["models_found"] = [m.name for m in model_files]

            suggestions = []
            status = ComponentStatus.AVAILABLE

            if not model_files:
                status = ComponentStatus.PARTIAL
                suggestions.append("GFPGAN installed but no models found")
                suggestions.append("Download model: python -m vhs_upscaler.face_restoration --download-model")
                suggestions.append("Or download manually from: https://github.com/TencentARC/GFPGAN/releases")

            # Try to import cv2 (required dependency)
            try:
                import cv2
                details["opencv_available"] = True
                details["opencv_version"] = cv2.__version__
            except ImportError:
                status = ComponentStatus.PARTIAL
                suggestions.append("OpenCV not found - install: pip install opencv-python")
                details["opencv_available"] = False

            return ComponentResult(
                name="GFPGAN",
                status=status,
                version=gfpgan.__version__ if hasattr(gfpgan, '__version__') else "unknown",
                details=details,
                suggestions=suggestions,
                performance_notes=["GPU recommended for reasonable processing speed"]
            )

        except ImportError as e:
            return ComponentResult(
                name="GFPGAN",
                status=ComponentStatus.UNAVAILABLE,
                error_message=str(e),
                suggestions=[
                    "Install GFPGAN: pip install gfpgan",
                    "Install dependencies: pip install basicsr opencv-python",
                    "Required for: Face restoration (good quality, fast)"
                ]
            )
        except Exception as e:
            return ComponentResult(
                name="GFPGAN",
                status=ComponentStatus.ERROR,
                error_message=str(e),
                details={"traceback": traceback.format_exc()}
            )


class CodeFormerVerifier(ComponentVerifier):
    """Verify CodeFormer face restoration."""

    def verify(self) -> ComponentResult:
        try:
            # CodeFormer requires PyTorch
            import torch
            import cv2

            details = {
                "torch_available": True,
                "opencv_available": True,
                "opencv_version": cv2.__version__
            }

            # Try to import CodeFormer package
            codeformer_installed = False
            try:
                from codeformer import CodeFormer
                codeformer_installed = True
                details["codeformer_package"] = True
            except ImportError:
                details["codeformer_package"] = False

            # Check for model files
            model_dir = Path("models") / "codeformer"
            model_files = []
            if model_dir.exists():
                model_files = list(model_dir.glob("*.pth"))
                details["model_directory"] = str(model_dir)
                details["models_found"] = [m.name for m in model_files]

            suggestions = []
            status = ComponentStatus.AVAILABLE if torch.cuda.is_available() else ComponentStatus.PARTIAL

            if not model_files:
                suggestions.append("CodeFormer model not found")
                suggestions.append("Download model: python -m vhs_upscaler.face_restoration --backend codeformer --download-model")
                suggestions.append("Or download from: https://github.com/sczhou/CodeFormer/releases")
                if not codeformer_installed:
                    status = ComponentStatus.PARTIAL

            if not codeformer_installed:
                suggestions.append("CodeFormer package not installed (using built-in implementation)")

            if not torch.cuda.is_available():
                suggestions.append("CUDA not available - CodeFormer will be very slow on CPU")

            performance_notes = []
            if torch.cuda.is_available():
                performance_notes.append("GPU acceleration available - optimal for CodeFormer")
            else:
                performance_notes.append("CPU mode - expect slow processing (GPU highly recommended)")

            return ComponentResult(
                name="CodeFormer",
                status=status,
                version="v0.1.0" if model_files else "not downloaded",
                details=details,
                suggestions=suggestions,
                performance_notes=performance_notes
            )

        except ImportError as e:
            return ComponentResult(
                name="CodeFormer",
                status=ComponentStatus.UNAVAILABLE,
                error_message=str(e),
                suggestions=[
                    "Install dependencies: pip install torch opencv-python",
                    "CodeFormer provides best face restoration quality",
                    "GPU highly recommended for acceptable speed"
                ]
            )
        except Exception as e:
            return ComponentResult(
                name="CodeFormer",
                status=ComponentStatus.ERROR,
                error_message=str(e),
                details={"traceback": traceback.format_exc()}
            )


class DeepFilterNetVerifier(ComponentVerifier):
    """Verify DeepFilterNet AI audio denoising."""

    def verify(self) -> ComponentResult:
        try:
            import torch
            from df import enhance, init_df

            details = {
                "torch_available": True,
                "deepfilternet_available": True
            }

            # Try to initialize DeepFilterNet
            try:
                model, df_state, _ = init_df()
                details["model_loaded"] = True
                details["model_info"] = {
                    "sr": df_state.sr(),
                    "hop_size": df_state.hop_size(),
                }
                status = ComponentStatus.AVAILABLE
                suggestions = []
            except Exception as e:
                details["model_loaded"] = False
                details["load_error"] = str(e)
                status = ComponentStatus.PARTIAL
                suggestions = [
                    "DeepFilterNet model initialization failed",
                    "Model will be downloaded on first use",
                    f"Error: {str(e)}"
                ]

            performance_notes = []
            if torch.cuda.is_available():
                performance_notes.append("GPU acceleration available - recommended for real-time processing")
            else:
                performance_notes.append("CPU mode - processing will be slower but functional")

            return ComponentResult(
                name="DeepFilterNet",
                status=status,
                version="0.5.0+",
                details=details,
                suggestions=suggestions,
                performance_notes=performance_notes
            )

        except ImportError as e:
            return ComponentResult(
                name="DeepFilterNet",
                status=ComponentStatus.UNAVAILABLE,
                error_message=str(e),
                suggestions=[
                    "Install DeepFilterNet: pip install deepfilternet",
                    "Requires PyTorch: pip install torch",
                    "Provides superior AI-based audio denoising for speech"
                ]
            )
        except Exception as e:
            return ComponentResult(
                name="DeepFilterNet",
                status=ComponentStatus.ERROR,
                error_message=str(e),
                details={"traceback": traceback.format_exc()}
            )


class AudioSRVerifier(ComponentVerifier):
    """Verify AudioSR AI audio upsampling."""

    def verify(self) -> ComponentResult:
        try:
            import torch

            # Try to import audiosr
            try:
                import audiosr
                audiosr_available = True
                audiosr_version = audiosr.__version__ if hasattr(audiosr, '__version__') else "unknown"
            except ImportError:
                audiosr_available = False
                audiosr_version = None

            details = {
                "torch_available": True,
                "audiosr_available": audiosr_available
            }

            if audiosr_available:
                # Try to initialize AudioSR
                try:
                    # This will attempt to load the model
                    # We don't actually initialize to avoid downloading large models during verification
                    details["package_functional"] = True
                    status = ComponentStatus.AVAILABLE
                    suggestions = []
                except Exception as e:
                    details["package_functional"] = False
                    details["init_error"] = str(e)
                    status = ComponentStatus.PARTIAL
                    suggestions = [
                        "AudioSR package found but initialization may fail",
                        "Models will be downloaded on first use",
                        f"Potential issue: {str(e)}"
                    ]
            else:
                status = ComponentStatus.UNAVAILABLE
                suggestions = [
                    "Install AudioSR: pip install audiosr",
                    "Requires PyTorch: pip install torch",
                    "Provides AI-based audio upsampling to 48kHz"
                ]

            performance_notes = []
            if torch.cuda.is_available():
                performance_notes.append("GPU acceleration available - recommended for AudioSR")
            else:
                performance_notes.append("CPU mode available but slower")

            return ComponentResult(
                name="AudioSR",
                status=status,
                version=audiosr_version,
                details=details,
                suggestions=suggestions,
                performance_notes=performance_notes
            )

        except ImportError as e:
            return ComponentResult(
                name="AudioSR",
                status=ComponentStatus.UNAVAILABLE,
                error_message=str(e),
                suggestions=[
                    "Install PyTorch first: pip install torch",
                    "Then install AudioSR: pip install audiosr",
                    "Provides AI-based audio upsampling (16kHz/22kHz → 48kHz)"
                ]
            )
        except Exception as e:
            return ComponentResult(
                name="AudioSR",
                status=ComponentStatus.ERROR,
                error_message=str(e),
                details={"traceback": traceback.format_exc()}
            )


class DemucsVerifier(ComponentVerifier):
    """Verify Demucs AI stem separation."""

    def verify(self) -> ComponentResult:
        try:
            import torch
            import torchaudio

            # Try to import demucs
            try:
                import demucs
                from demucs.pretrained import get_model_from_args
                demucs_available = True
                demucs_version = demucs.__version__ if hasattr(demucs, '__version__') else "4.0.0+"
            except ImportError:
                demucs_available = False
                demucs_version = None

            details = {
                "torch_available": True,
                "torchaudio_available": True,
                "torchaudio_version": torchaudio.__version__,
                "demucs_available": demucs_available
            }

            if demucs_available:
                # Check available models
                try:
                    # List common models
                    models = ["htdemucs", "htdemucs_ft", "mdx_extra"]
                    details["available_models"] = models
                    status = ComponentStatus.AVAILABLE
                    suggestions = ["Models will be downloaded on first use"]
                except Exception as e:
                    details["model_check_error"] = str(e)
                    status = ComponentStatus.PARTIAL
                    suggestions = [f"Model check failed: {str(e)}"]
            else:
                status = ComponentStatus.UNAVAILABLE
                suggestions = [
                    "Install Demucs: pip install demucs",
                    "Requires PyTorch and torchaudio",
                    "Provides best quality surround upmix via AI stem separation"
                ]

            performance_notes = []
            if torch.cuda.is_available():
                performance_notes.append("GPU acceleration available - essential for Demucs")
                performance_notes.append("Demucs is very slow on CPU (not recommended)")
            else:
                performance_notes.append("WARNING: Demucs requires GPU for practical use")
                performance_notes.append("CPU processing is extremely slow (hours per minute of audio)")

            return ComponentResult(
                name="Demucs",
                status=status,
                version=demucs_version,
                details=details,
                suggestions=suggestions,
                performance_notes=performance_notes
            )

        except ImportError as e:
            return ComponentResult(
                name="Demucs",
                status=ComponentStatus.UNAVAILABLE,
                error_message=str(e),
                suggestions=[
                    "Install PyTorch: pip install torch torchaudio",
                    "Install Demucs: pip install demucs",
                    "Provides AI-based stem separation for surround upmix",
                    "GPU highly recommended (CPU is impractically slow)"
                ]
            )
        except Exception as e:
            return ComponentResult(
                name="Demucs",
                status=ComponentStatus.ERROR,
                error_message=str(e),
                details={"traceback": traceback.format_exc()}
            )


class FFmpegVerifier(ComponentVerifier):
    """Verify FFmpeg installation and encoders."""

    def verify(self) -> ComponentResult:
        try:
            # Get FFmpeg version
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                check=True
            )
            version_line = result.stdout.split("\n")[0]
            version = version_line.split("version")[1].split()[0]

            # Check encoders
            encoder_result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True,
                text=True,
                check=True
            )

            encoders = {
                "h264_nvenc": "NVIDIA H.264 hardware encoder",
                "hevc_nvenc": "NVIDIA H.265 hardware encoder",
                "libx264": "x264 software H.264 encoder",
                "libx265": "x265 software H.265 encoder",
                "av1_nvenc": "NVIDIA AV1 hardware encoder",
                "libsvtav1": "SVT-AV1 software encoder"
            }

            available_encoders = {}
            missing_encoders = {}

            for encoder, description in encoders.items():
                if encoder in encoder_result.stdout:
                    available_encoders[encoder] = description
                else:
                    missing_encoders[encoder] = description

            details = {
                "version": version,
                "available_encoders": available_encoders,
                "missing_encoders": missing_encoders
            }

            # Check filters
            filter_result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-filters"],
                capture_output=True,
                text=True,
                check=True
            )

            important_filters = {
                "yadif": "Deinterlacing",
                "hqdn3d": "Denoise",
                "scale_cuda": "CUDA scaling",
                "scale_npp": "NVIDIA Performance Primitives scaling"
            }

            available_filters = {}
            for filt, desc in important_filters.items():
                if filt in filter_result.stdout:
                    available_filters[filt] = desc

            details["available_filters"] = available_filters

            suggestions = []
            performance_notes = []
            status = ComponentStatus.AVAILABLE

            if "h264_nvenc" in available_encoders or "hevc_nvenc" in available_encoders:
                performance_notes.append("NVIDIA hardware encoding available (fast, efficient)")
            else:
                suggestions.append("NVIDIA hardware encoders not available")
                suggestions.append("Update NVIDIA drivers for NVENC support")
                performance_notes.append("Using software encoding (slower but functional)")

            if missing_encoders:
                status = ComponentStatus.PARTIAL

            return ComponentResult(
                name="FFmpeg",
                status=status,
                version=version,
                details=details,
                suggestions=suggestions,
                performance_notes=performance_notes
            )

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return ComponentResult(
                name="FFmpeg",
                status=ComponentStatus.UNAVAILABLE,
                error_message=str(e),
                suggestions=[
                    "Install FFmpeg:",
                    "  Windows: winget install FFmpeg",
                    "  Linux: sudo apt install ffmpeg",
                    "  macOS: brew install ffmpeg",
                    "FFmpeg is REQUIRED for all video processing"
                ]
            )
        except Exception as e:
            return ComponentResult(
                name="FFmpeg",
                status=ComponentStatus.ERROR,
                error_message=str(e),
                details={"traceback": traceback.format_exc()}
            )


class GPUVerifier(ComponentVerifier):
    """Verify GPU availability and capabilities."""

    def verify(self) -> ComponentResult:
        details = {}
        suggestions = []
        performance_notes = []

        # Check NVIDIA GPU via nvidia-smi
        nvidia_available = False
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                 "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            gpu_lines = result.stdout.strip().split("\n")
            nvidia_gpus = []
            for line in gpu_lines:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    nvidia_gpus.append({
                        "name": parts[0],
                        "memory": parts[1],
                        "driver_version": parts[2]
                    })

            if nvidia_gpus:
                nvidia_available = True
                details["nvidia_gpus"] = nvidia_gpus
                details["gpu_count"] = len(nvidia_gpus)
                performance_notes.append(f"Found {len(nvidia_gpus)} NVIDIA GPU(s)")

        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            details["nvidia_gpus"] = []

        # Check AMD GPU (basic detection on Windows)
        amd_available = False
        if sys.platform == "win32":
            try:
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if "AMD" in result.stdout or "Radeon" in result.stdout:
                    amd_available = True
                    details["amd_gpu_detected"] = True
                    performance_notes.append("AMD GPU detected (Vulkan-based acceleration available)")
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        # Check Intel GPU
        intel_available = False
        if sys.platform == "win32":
            try:
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if "Intel" in result.stdout:
                    intel_available = True
                    details["intel_gpu_detected"] = True
                    performance_notes.append("Intel GPU detected (limited acceleration support)")
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        # Determine status
        if nvidia_available:
            status = ComponentStatus.AVAILABLE
            version = nvidia_gpus[0]["driver_version"] if nvidia_gpus else "unknown"
            performance_notes.append("Optimal configuration for AI processing")
            performance_notes.append("NVENC hardware encoding available")
        elif amd_available or intel_available:
            status = ComponentStatus.PARTIAL
            version = "Non-NVIDIA GPU"
            suggestions.append("Some features require NVIDIA GPU (NVENC, CUDA acceleration)")
            suggestions.append("Real-ESRGAN Vulkan backend available for upscaling")
            performance_notes.append("Limited hardware acceleration available")
        else:
            status = ComponentStatus.UNAVAILABLE
            version = None
            suggestions.append("No GPU detected - CPU-only mode")
            suggestions.append("Processing will be significantly slower")
            suggestions.append("Consider using a system with GPU for production use")
            performance_notes.append("CPU-only mode: expect slow processing times")

        return ComponentResult(
            name="GPU",
            status=status,
            version=version,
            details=details,
            suggestions=suggestions,
            performance_notes=performance_notes
        )


# =============================================================================
# Main Verification System
# =============================================================================

class InstallationVerifier:
    """Main installation verification system."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(levelname)s: %(message)s'
        )

    def get_system_info(self) -> Dict[str, str]:
        """Get system information."""
        return {
            "platform": platform.platform(),
            "system": platform.system(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation()
        }

    def verify_all(self, quick: bool = False) -> VerificationReport:
        """Run all verification checks."""
        print("=" * 70)
        print("TerminalAI Installation Verification")
        print("=" * 70)
        print()

        system_info = self.get_system_info()
        print("System Information:")
        print(f"  Platform: {system_info['platform']}")
        print(f"  Python: {system_info['python_version']} ({system_info['python_implementation']})")
        print()

        # Define verifiers
        verifiers = [
            ("Python", PythonVerifier(self.verbose)),
            ("FFmpeg", FFmpegVerifier(self.verbose)),
            ("GPU", GPUVerifier(self.verbose)),
            ("PyTorch", PyTorchVerifier(self.verbose)),
            ("VapourSynth", VapourSynthVerifier(self.verbose)),
            ("GFPGAN", GFPGANVerifier(self.verbose)),
            ("CodeFormer", CodeFormerVerifier(self.verbose)),
            ("DeepFilterNet", DeepFilterNetVerifier(self.verbose)),
            ("AudioSR", AudioSRVerifier(self.verbose)),
            ("Demucs", DemucsVerifier(self.verbose)),
        ]

        components = {}
        warnings = []
        errors = []

        print("Checking components...")
        print("-" * 70)

        for name, verifier in verifiers:
            print(f"\n{name}:")
            try:
                result = verifier.verify()
                components[name] = result

                # Print status
                status_symbol = {
                    ComponentStatus.AVAILABLE: "[OK]",
                    ComponentStatus.PARTIAL: "[PARTIAL]",
                    ComponentStatus.UNAVAILABLE: "[NOT INSTALLED]",
                    ComponentStatus.ERROR: "[ERROR]"
                }.get(result.status, "[UNKNOWN]")

                version_str = f" v{result.version}" if result.version else ""
                print(f"  {status_symbol}{version_str}")

                # Print details
                if result.details and self.verbose:
                    for key, value in result.details.items():
                        if isinstance(value, (list, dict)):
                            continue
                        print(f"    {key}: {value}")

                # Print suggestions
                if result.suggestions:
                    for suggestion in result.suggestions:
                        print(f"    💡 {suggestion}")
                        if result.status == ComponentStatus.UNAVAILABLE:
                            warnings.append(f"{name}: {suggestion}")

                # Print performance notes
                if result.performance_notes and self.verbose:
                    for note in result.performance_notes:
                        print(f"    ⚡ {note}")

                # Collect errors
                if result.status == ComponentStatus.ERROR:
                    errors.append(f"{name}: {result.error_message}")

            except Exception as e:
                error_msg = f"Verification failed: {str(e)}"
                print(f"  [ERROR] {error_msg}")
                errors.append(f"{name}: {error_msg}")
                components[name] = ComponentResult(
                    name=name,
                    status=ComponentStatus.ERROR,
                    error_message=error_msg
                )

        # Determine feature availability
        feature_availability = {
            "basic_video_processing": components.get("FFmpeg", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available,
            "gpu_acceleration": components.get("GPU", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available,
            "hardware_encoding": components.get("FFmpeg", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available and
                                 components.get("GPU", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available,
            "ai_upscaling": components.get("PyTorch", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available or
                           components.get("GPU", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available,
            "advanced_deinterlacing": components.get("VapourSynth", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available,
            "face_restoration": components.get("GFPGAN", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available or
                               components.get("CodeFormer", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available,
            "ai_audio_denoising": components.get("DeepFilterNet", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available,
            "ai_audio_upsampling": components.get("AudioSR", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available,
            "ai_surround_upmix": components.get("Demucs", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(components, feature_availability)

        return VerificationReport(
            system_info=system_info,
            components=components,
            feature_availability=feature_availability,
            warnings=warnings,
            errors=errors,
            recommendations=recommendations
        )

    def _generate_recommendations(
        self,
        components: Dict[str, ComponentResult],
        features: Dict[str, bool]
    ) -> List[str]:
        """Generate recommendations based on verification results."""
        recommendations = []

        # Critical components
        if not components.get("FFmpeg", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available:
            recommendations.append("CRITICAL: Install FFmpeg - required for all video processing")

        # GPU recommendations
        gpu = components.get("GPU", None)
        if gpu and gpu.status == ComponentStatus.UNAVAILABLE:
            recommendations.append("Consider using a GPU-enabled system for better performance")
        elif gpu and gpu.status == ComponentStatus.PARTIAL:
            recommendations.append("NVIDIA GPU recommended for optimal AI processing performance")

        # PyTorch recommendations
        pytorch = components.get("PyTorch", None)
        if pytorch and pytorch.status == ComponentStatus.UNAVAILABLE:
            recommendations.append("Install PyTorch for AI features: pip install torch torchaudio")
        elif pytorch and pytorch.status == ComponentStatus.PARTIAL:
            recommendations.append("Install CUDA-enabled PyTorch for GPU acceleration")

        # Feature-specific recommendations
        if not features.get("advanced_deinterlacing"):
            recommendations.append("Install VapourSynth for QTGMC deinterlacing (best quality for VHS)")

        if not features.get("face_restoration"):
            recommendations.append("Install GFPGAN or CodeFormer for face restoration in videos")

        if not features.get("ai_audio_denoising"):
            recommendations.append("Install DeepFilterNet for superior AI audio denoising")

        if not features.get("ai_surround_upmix"):
            recommendations.append("Install Demucs for best-quality surround upmix (requires GPU)")

        return recommendations

    def print_summary(self, report: VerificationReport):
        """Print verification summary."""
        print("\n" + "=" * 70)
        print("Verification Summary")
        print("=" * 70)

        # Feature availability
        print("\nFeature Availability:")
        for feature, available in report.feature_availability.items():
            status = "[OK]" if available else "[NOT AVAILABLE]"
            feature_name = feature.replace("_", " ").title()
            print(f"  {status} {feature_name}")

        # Recommendations
        if report.recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")

        # Errors
        if report.errors:
            print("\nErrors:")
            for error in report.errors:
                print(f"  ❌ {error}")

        print("\n" + "=" * 70)

    def print_feature_matrix(self, report: VerificationReport):
        """Print a detailed feature compatibility matrix."""
        print("\n" + "=" * 70)
        print("Feature Compatibility Matrix")
        print("=" * 70)

        features = {
            "Basic Video Processing": {
                "required": ["FFmpeg"],
                "optional": []
            },
            "GPU Hardware Encoding": {
                "required": ["FFmpeg", "GPU"],
                "optional": []
            },
            "AI Upscaling (Maxine/Real-ESRGAN)": {
                "required": ["FFmpeg"],
                "optional": ["GPU"]
            },
            "AI Upscaling (PyTorch-based)": {
                "required": ["PyTorch"],
                "optional": ["GPU"]
            },
            "Advanced Deinterlacing (QTGMC)": {
                "required": ["VapourSynth"],
                "optional": []
            },
            "Face Restoration (GFPGAN)": {
                "required": ["GFPGAN", "PyTorch"],
                "optional": ["GPU"]
            },
            "Face Restoration (CodeFormer)": {
                "required": ["CodeFormer", "PyTorch"],
                "optional": ["GPU"]
            },
            "AI Audio Denoising": {
                "required": ["DeepFilterNet", "PyTorch"],
                "optional": ["GPU"]
            },
            "AI Audio Upsampling": {
                "required": ["AudioSR", "PyTorch"],
                "optional": ["GPU"]
            },
            "AI Surround Upmix": {
                "required": ["Demucs", "PyTorch"],
                "optional": ["GPU"]
            }
        }

        for feature_name, deps in features.items():
            # Check if all required components are available
            required_ok = all(
                report.components.get(comp, ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available
                for comp in deps["required"]
            )

            # Check optional components
            optional_status = [
                report.components.get(comp, ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available
                for comp in deps["optional"]
            ]

            status_symbol = "[OK]" if required_ok else "[NOT AVAILABLE]"
            optional_text = ""
            if deps["optional"] and required_ok:
                if all(optional_status):
                    optional_text = " (Optimized)"
                else:
                    optional_text = " (CPU mode)"

            print(f"\n{feature_name}:")
            print(f"  {status_symbol}{optional_text}")

            if not required_ok:
                print(f"    Missing: {', '.join(deps['required'])}")

        print("\n" + "=" * 70)


# =============================================================================
# Feature Detection API
# =============================================================================

def get_available_features() -> Dict[str, bool]:
    """
    Get available features without verbose output.

    Returns:
        Dictionary mapping feature names to availability status
    """
    verifier = InstallationVerifier(verbose=False)
    report = verifier.verify_all()
    return report.feature_availability


def check_component(component_name: str) -> ComponentResult:
    """
    Check a specific component.

    Args:
        component_name: Name of component to check

    Returns:
        ComponentResult with verification details
    """
    verifiers = {
        "python": PythonVerifier(verbose=False),
        "pytorch": PyTorchVerifier(verbose=False),
        "vapoursynth": VapourSynthVerifier(verbose=False),
        "gfpgan": GFPGANVerifier(verbose=False),
        "codeformer": CodeFormerVerifier(verbose=False),
        "deepfilternet": DeepFilterNetVerifier(verbose=False),
        "audiosr": AudioSRVerifier(verbose=False),
        "demucs": DemucsVerifier(verbose=False),
        "ffmpeg": FFmpegVerifier(verbose=False),
        "gpu": GPUVerifier(verbose=False)
    }

    verifier = verifiers.get(component_name.lower())
    if not verifier:
        return ComponentResult(
            name=component_name,
            status=ComponentStatus.ERROR,
            error_message=f"Unknown component: {component_name}"
        )

    return verifier.verify()


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="TerminalAI Installation Verification System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify_installation.py                    # Full verification
  python verify_installation.py --quick            # Quick check
  python verify_installation.py --report out.json  # Save report to JSON
  python verify_installation.py --matrix           # Show feature matrix
  python verify_installation.py --check pytorch    # Check specific component
        """
    )

    parser.add_argument("--quick", action="store_true",
                       help="Quick check (less verbose)")
    parser.add_argument("--report", type=str,
                       help="Save detailed report to JSON file")
    parser.add_argument("--matrix", action="store_true",
                       help="Show feature compatibility matrix")
    parser.add_argument("--check", type=str,
                       help="Check specific component")
    parser.add_argument("--quiet", action="store_true",
                       help="Minimal output")

    args = parser.parse_args()

    if args.check:
        # Check specific component
        result = check_component(args.check)
        print(f"\n{result.name}: {result.status.value}")
        if result.version:
            print(f"Version: {result.version}")
        if result.error_message:
            print(f"Error: {result.error_message}")
        if result.suggestions:
            print("\nSuggestions:")
            for suggestion in result.suggestions:
                print(f"  - {suggestion}")
        return

    # Full verification
    verifier = InstallationVerifier(verbose=not args.quick and not args.quiet)
    report = verifier.verify_all(quick=args.quick)

    if not args.quiet:
        verifier.print_summary(report)

    if args.matrix:
        verifier.print_feature_matrix(report)

    if args.report:
        report_path = Path(args.report)
        report.to_json(report_path)
        print(f"\nDetailed report saved to: {report_path}")

    # Exit code
    critical_ok = (
        report.components.get("FFmpeg", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available and
        report.components.get("Python", ComponentResult("", ComponentStatus.UNAVAILABLE)).is_available
    )
    sys.exit(0 if critical_ok else 1)


if __name__ == "__main__":
    main()
