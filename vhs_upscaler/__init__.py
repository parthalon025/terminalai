"""
VHS Video Upscaling Pipeline
============================
AI-powered video upscaling for VHS-quality footage using NVIDIA Maxine SDK.

Features:
- YouTube URL and local file support
- Watch folder automation
- Video queue with batch processing
- Modern web GUI (Gradio)
- Comprehensive logging
"""

__version__ = "1.0.0"
__author__ = "VHS Upscaler"

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
