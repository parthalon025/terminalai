"""
TerminalAI - VHS Video Upscaling Pipeline
==========================================
AI-powered video upscaling and audio enhancement for VHS-quality footage.

Features:
- Multiple AI upscale engines: NVIDIA Maxine, Real-ESRGAN, FFmpeg
- HDR10/HLG output support
- Audio enhancement with noise reduction and EQ
- Surround sound upmixing (5.1/7.1) with Demucs AI
- YouTube URL and local file support
- Watch folder automation
- Video queue with batch processing
- Modern web GUI (Gradio) with conditional advanced options
- Comprehensive logging and error handling
"""

__version__ = "1.4.2"
__author__ = "TerminalAI Contributors"

from .vhs_upscale import VHSUpscaler, ProcessingConfig, YouTubeDownloader
from .queue_manager import VideoQueue, QueueJob, JobStatus
from .logger import get_logger, VHSLogger

__all__ = [
    "VHSUpscaler",
    "ProcessingConfig",
    "YouTubeDownloader",
    "VideoQueue",
    "QueueJob",
    "JobStatus",
    "get_logger",
    "VHSLogger",
]
