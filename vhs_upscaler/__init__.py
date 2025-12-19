"""
TerminalAI - VHS Video Upscaling Pipeline
==========================================
AI-powered video upscaling and audio enhancement for VHS-quality footage.

Features:
- Multiple AI upscale engines: RTX Video SDK, Real-ESRGAN, FFmpeg
- HDR10/HLG output support
- Audio enhancement with noise reduction and EQ
- Surround sound upmixing (5.1/7.1) with Demucs AI
- YouTube URL and local file support
- Watch folder automation
- Video queue with batch processing
- Modern web GUI (Gradio) with conditional advanced options
- Comprehensive logging and error handling
"""

__version__ = "1.5.1"
__author__ = "TerminalAI Contributors"

# Core queue management (always available)
from .queue_manager import VideoQueue, QueueJob, JobStatus
from .logger import get_logger, VHSLogger

# Audio processing (graceful fallback if dependencies missing)
try:
    from .audio_processor import (
        AudioProcessor,
        AudioConfig,
        AudioEnhanceMode,
        UpmixMode,
        AudioChannelLayout,
        AudioFormat,
    )
    HAS_AUDIO_PROCESSOR = True
except ImportError:
    HAS_AUDIO_PROCESSOR = False
    AudioProcessor = None
    AudioConfig = None
    AudioEnhanceMode = None
    UpmixMode = None
    AudioChannelLayout = None
    AudioFormat = None

# Hardware detection (optional)
try:
    from .hardware_detection import detect_hardware, get_optimal_config, HardwareInfo
    HAS_HARDWARE_DETECTION = True
except ImportError:
    HAS_HARDWARE_DETECTION = False
    detect_hardware = None
    get_optimal_config = None
    HardwareInfo = None

# Face restoration (optional)
try:
    from .face_restoration import FaceRestorer
    HAS_FACE_RESTORATION = True
except ImportError:
    HAS_FACE_RESTORATION = False
    FaceRestorer = None

# Notifications (optional)
try:
    from .notifications import NotificationManager
    HAS_NOTIFICATIONS = True
except ImportError:
    HAS_NOTIFICATIONS = False
    NotificationManager = None

# Presets (optional)
try:
    from .presets import get_preset_from_analysis, get_recommended_settings_from_analysis
    HAS_PRESETS = True
except (ImportError, ModuleNotFoundError):
    HAS_PRESETS = False
    get_preset_from_analysis = None
    get_recommended_settings_from_analysis = None

# Deinterlacing (optional)
try:
    from .deinterlace import DeinterlaceConfig, DeinterlaceMethod
    HAS_DEINTERLACE = True
except ImportError:
    HAS_DEINTERLACE = False
    DeinterlaceConfig = None
    DeinterlaceMethod = None

__all__ = [
    # Core classes (always available)
    "VideoQueue",
    "QueueJob",
    "JobStatus",
    "get_logger",
    "VHSLogger",
    # Audio processing (optional)
    "AudioProcessor",
    "AudioConfig",
    "AudioEnhanceMode",
    "UpmixMode",
    "AudioChannelLayout",
    "AudioFormat",
    # Hardware detection (optional)
    "detect_hardware",
    "get_optimal_config",
    "HardwareInfo",
    # Face restoration (optional)
    "FaceRestorer",
    # Notifications (optional)
    "NotificationManager",
    # Presets (optional)
    "get_preset_from_analysis",
    "get_recommended_settings_from_analysis",
    # Deinterlacing (optional)
    "DeinterlaceConfig",
    "DeinterlaceMethod",
    # Feature flags
    "HAS_AUDIO_PROCESSOR",
    "HAS_HARDWARE_DETECTION",
    "HAS_FACE_RESTORATION",
    "HAS_NOTIFICATIONS",
    "HAS_PRESETS",
    "HAS_DEINTERLACE",
]


def get_available_features():
    """
    Get a dictionary of available features based on installed dependencies.

    Returns:
        dict: Feature availability flags
    """
    return {
        "audio_processing": HAS_AUDIO_PROCESSOR,
        "hardware_detection": HAS_HARDWARE_DETECTION,
        "face_restoration": HAS_FACE_RESTORATION,
        "notifications": HAS_NOTIFICATIONS,
        "presets": HAS_PRESETS,
        "deinterlacing": HAS_DEINTERLACE,
    }


def check_dependencies(verbose=False):
    """
    Check which optional dependencies are available.

    Args:
        verbose: Print detailed status messages

    Returns:
        dict: Dependency availability status
    """
    status = {}

    # Core dependencies
    try:
        import gradio
        status["gradio"] = True
        if verbose:
            print(f"[OK] Gradio {gradio.__version__} available")
    except ImportError:
        status["gradio"] = False
        if verbose:
            print("[MISS] Gradio not available")

    try:
        import torch
        status["torch"] = True
        if verbose:
            print(f"[OK] PyTorch {torch.__version__} available")
            if torch.cuda.is_available():
                print(f"  |-- CUDA {torch.version.cuda} available")
    except ImportError:
        status["torch"] = False
        if verbose:
            print("[MISS] PyTorch not available")

    # Optional AI dependencies
    try:
        import cv2
        status["opencv"] = True
        if verbose:
            print(f"[OK] OpenCV {cv2.__version__} available")
    except ImportError:
        status["opencv"] = False
        if verbose:
            print("[MISS] OpenCV not available")

    try:
        import demucs
        status["demucs"] = True
        if verbose:
            print("[OK] Demucs (AI audio stem separation)")
    except ImportError:
        status["demucs"] = False
        if verbose:
            print("[MISS] Demucs not available")

    try:
        import df
        status["deepfilternet"] = True
        if verbose:
            print("[OK] DeepFilterNet (AI audio denoising)")
    except ImportError:
        status["deepfilternet"] = False
        if verbose:
            print("[MISS] DeepFilterNet not available")

    try:
        import audiosr
        status["audiosr"] = True
        if verbose:
            print("[OK] AudioSR (AI audio upsampling)")
    except ImportError:
        status["audiosr"] = False
        if verbose:
            print("[MISS] AudioSR not available")

    try:
        import gfpgan
        status["gfpgan"] = True
        if verbose:
            print("[OK] GFPGAN (face restoration)")
    except ImportError:
        status["gfpgan"] = False
        if verbose:
            print("[MISS] GFPGAN not available")

    try:
        import basicsr
        status["basicsr"] = True
        if verbose:
            print("[OK] BasicSR (super-resolution)")
    except ImportError:
        status["basicsr"] = False
        if verbose:
            print("[MISS] BasicSR not available")

    try:
        import realesrgan
        status["realesrgan"] = True
        if verbose:
            print("[OK] Real-ESRGAN (AI upscaling)")
    except ImportError:
        status["realesrgan"] = False
        if verbose:
            print("[MISS] Real-ESRGAN not available")

    # GPU libraries (nvidia-ml-py replaces deprecated pynvml)
    try:
        import pynvml as nvidia_smi  # nvidia-ml-py provides this
        status["nvidia_ml"] = True
        if verbose:
            print("[OK] NVIDIA ML (GPU monitoring)")
    except ImportError:
        status["nvidia_ml"] = False
        if verbose:
            print("[MISS] NVIDIA ML not available")

    return status


def print_system_info():
    """Print comprehensive system and dependency information."""
    import sys
    import platform

    print(f"TerminalAI v{__version__}")
    print("=" * 60)
    print(f"Python: {sys.version.split()[0]} ({platform.platform()})")
    print()

    print("Core Features:")
    print("-" * 60)
    features = get_available_features()
    for feature, available in features.items():
        status = "[YES]" if available else "[NO] "
        print(f"{status} {feature.replace('_', ' ').title()}")

    print()
    print("Dependencies:")
    print("-" * 60)
    check_dependencies(verbose=True)
