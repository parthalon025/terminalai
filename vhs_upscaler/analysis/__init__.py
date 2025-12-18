"""
Video analysis module for intelligent video characteristic detection.

This module provides a unified interface for analyzing videos using multiple
backends (Python+OpenCV, Bash, or FFprobe-only) with automatic fallback.

Key components:
- VideoAnalysis: Complete analysis results dataclass
- AnalyzerWrapper: Unified interface with backend auto-detection
- Enums: ScanType, ContentType, NoiseLevel, SourceFormat

Usage:
    from vhs_upscaler.analysis import AnalyzerWrapper, VideoAnalysis

    wrapper = AnalyzerWrapper()  # Auto-detects best backend
    analysis = wrapper.analyze("video.mp4")
    print(analysis.get_summary())
"""

from .models import (
    VideoAnalysis,
    ScanType,
    ContentType,
    NoiseLevel,
    SourceFormat,
)
from .analyzer_wrapper import AnalyzerWrapper, AnalyzerBackend

__all__ = [
    'VideoAnalysis',
    'ScanType',
    'ContentType',
    'NoiseLevel',
    'SourceFormat',
    'AnalyzerWrapper',
    'AnalyzerBackend',
]

__version__ = '1.0.0'
