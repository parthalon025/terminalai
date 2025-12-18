"""
Unified video analyzer wrapper with multi-backend support.

This module provides a single interface for video analysis while supporting
multiple backends with automatic fallback:
  1. Python + OpenCV (best accuracy)
  2. Python Basic (no OpenCV)
  3. Bash script (portable)
  4. FFprobe only (minimal fallback)
"""

import json
import logging
import os
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Optional

from .models import (
    VideoAnalysis,
    ScanType,
    ContentType,
    NoiseLevel,
    SourceFormat,
)

logger = logging.getLogger(__name__)


class AnalyzerBackend(Enum):
    """Available analyzer backends."""
    PYTHON_OPENCV = "python_opencv"      # Full Python with OpenCV
    PYTHON_BASIC = "python_basic"        # Python without OpenCV
    BASH = "bash"                        # Shell script analyzer
    FFPROBE_ONLY = "ffprobe_only"        # Minimal fallback


class AnalyzerWrapper:
    """
    Unified wrapper for video analysis supporting multiple backends.

    Automatically detects available tools and uses the best option.
    Provides consistent VideoAnalysis output regardless of backend.

    Usage:
        wrapper = AnalyzerWrapper()  # Auto-detects backend
        analysis = wrapper.analyze("video.mp4")

        # Force specific backend
        wrapper = AnalyzerWrapper(force_backend=AnalyzerBackend.BASH)
        analysis = wrapper.analyze("video.mp4")
    """

    def __init__(self, force_backend: Optional[AnalyzerBackend] = None):
        """
        Initialize analyzer wrapper.

        Args:
            force_backend: Force specific backend (for testing or compatibility)
        """
        if force_backend:
            self.backend = force_backend
            logger.info(f"Forced analyzer backend: {self.backend.value}")
        else:
            self.backend = self._detect_backend()
            logger.info(f"Auto-detected analyzer backend: {self.backend.value}")

    def _detect_backend(self) -> AnalyzerBackend:
        """
        Auto-detect best available backend.

        Priority: Python+OpenCV > Python Basic > Bash > FFprobe-only

        Returns:
            Best available AnalyzerBackend
        """
        # Check for Python + OpenCV
        try:
            import cv2  # noqa: F401
            import numpy  # noqa: F401
            logger.debug("OpenCV detected - using Python+OpenCV backend")
            return AnalyzerBackend.PYTHON_OPENCV
        except ImportError:
            logger.debug("OpenCV not available")

        # Check for bash analyzer script
        bash_script = self._get_bash_script_path()
        if bash_script and bash_script.exists():
            # Verify it's executable (or can be run with bash)
            try:
                result = subprocess.run(
                    ["bash", str(bash_script), "--help"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 or "usage" in result.stdout.lower():
                    logger.debug(f"Bash analyzer found at {bash_script}")
                    return AnalyzerBackend.BASH
            except (FileNotFoundError, subprocess.TimeoutExpired):
                logger.debug("Bash not available or script not working")

        # Check for ffprobe (minimal fallback)
        if self._check_ffprobe():
            logger.debug("Using FFprobe-only backend (minimal analysis)")
            return AnalyzerBackend.FFPROBE_ONLY

        # No backend available - will raise error in analyze()
        logger.warning("No analyzer backend available!")
        return AnalyzerBackend.FFPROBE_ONLY

    def _get_bash_script_path(self) -> Optional[Path]:
        """Find bash analyzer script path."""
        # Look in scripts/ directory relative to project root
        script_candidates = [
            Path(__file__).parent.parent.parent / "scripts" / "video_analyzer.sh",
            Path("scripts/video_analyzer.sh"),
            Path.cwd() / "scripts" / "video_analyzer.sh",
        ]

        for script in script_candidates:
            if script.exists():
                return script

        return None

    def _check_ffprobe(self) -> bool:
        """Check if ffprobe is available."""
        try:
            subprocess.run(
                ["ffprobe", "-version"],
                capture_output=True,
                timeout=5
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def analyze(self, filepath: str) -> VideoAnalysis:
        """
        Run video analysis using best available backend.

        Args:
            filepath: Path to video file to analyze

        Returns:
            VideoAnalysis with complete analysis results

        Raises:
            FileNotFoundError: If video file doesn't exist
            RuntimeError: If no backend is available
        """
        filepath_obj = Path(filepath)
        if not filepath_obj.exists():
            raise FileNotFoundError(f"Video file not found: {filepath}")

        logger.info(f"Analyzing video: {filepath}")
        logger.info(f"Using backend: {self.backend.value}")

        if self.backend == AnalyzerBackend.PYTHON_OPENCV:
            return self._run_python_analyzer(filepath, use_opencv=True)
        elif self.backend == AnalyzerBackend.PYTHON_BASIC:
            return self._run_python_analyzer(filepath, use_opencv=False)
        elif self.backend == AnalyzerBackend.BASH:
            return self._run_bash_analyzer(filepath)
        elif self.backend == AnalyzerBackend.FFPROBE_ONLY:
            return self._run_basic_analysis(filepath)
        else:
            raise RuntimeError(f"Unknown backend: {self.backend}")

    def _run_python_analyzer(
        self,
        filepath: str,
        use_opencv: bool
    ) -> VideoAnalysis:
        """
        Execute Python video analyzer.

        Args:
            filepath: Video file path
            use_opencv: Whether OpenCV is available

        Returns:
            VideoAnalysis results
        """
        try:
            # Import video_analyzer module (will be created next)
            from . import video_analyzer

            analyzer = video_analyzer.VideoAnalyzer(use_opencv=use_opencv)
            analysis = analyzer.analyze(filepath)

            # Tag with backend info
            analysis.analyzer_backend = (
                "python_opencv" if use_opencv else "python_basic"
            )

            return analysis

        except ImportError as e:
            logger.error(f"Python analyzer not available: {e}")
            # Fall back to basic analysis
            return self._run_basic_analysis(filepath)

    def _run_bash_analyzer(self, filepath: str) -> VideoAnalysis:
        """
        Execute bash video analyzer script.

        Args:
            filepath: Video file path

        Returns:
            VideoAnalysis results parsed from JSON output
        """
        bash_script = self._get_bash_script_path()
        if not bash_script:
            logger.error("Bash analyzer script not found")
            return self._run_basic_analysis(filepath)

        try:
            # Run bash analyzer with --json-only flag
            result = subprocess.run(
                ["bash", str(bash_script), "--json-only", filepath],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if result.returncode != 0:
                logger.error(f"Bash analyzer failed: {result.stderr}")
                return self._run_basic_analysis(filepath)

            # Parse JSON output
            config_json = json.loads(result.stdout)
            analysis = self._parse_bash_output(config_json, filepath)
            analysis.analyzer_backend = "bash"

            return analysis

        except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error running bash analyzer: {e}")
            return self._run_basic_analysis(filepath)

    def _parse_bash_output(
        self,
        config_json: dict,
        filepath: str
    ) -> VideoAnalysis:
        """
        Convert bash analyzer JSON output to VideoAnalysis dataclass.

        Args:
            config_json: JSON output from bash analyzer
            filepath: Original video file path

        Returns:
            VideoAnalysis dataclass
        """
        # Map bash output to VideoAnalysis fields
        return VideoAnalysis(
            filepath=filepath,
            filename=Path(filepath).name,
            filesize_mb=config_json.get("filesize_mb", 0.0),
            duration_seconds=config_json.get("duration_seconds", 0.0),
            width=config_json.get("width", 0),
            height=config_json.get("height", 0),
            framerate=config_json.get("framerate", 0.0),
            framerate_fraction=config_json.get("framerate_fraction", ""),
            codec=config_json.get("codec", "unknown"),
            pixel_format=config_json.get("pixel_format", "unknown"),
            bitrate_kbps=config_json.get("bitrate_kbps", 0),
            scan_type=ScanType(config_json.get("scan_type", "unknown")),
            content_type=ContentType(config_json.get("content_type", "unknown")),
            source_format=SourceFormat(config_json.get("source_format", "unknown")),
            noise_level=NoiseLevel(config_json.get("noise_level", "medium")),
            estimated_quality_score=config_json.get("estimated_quality_score", 50.0),
            has_tracking_errors=config_json.get("has_tracking_errors", False),
            has_color_bleeding=config_json.get("has_color_bleeding", False),
            has_head_switching_noise=config_json.get("has_head_switching_noise", False),
            has_dropout_lines=config_json.get("has_dropout_lines", False),
            has_jitter=config_json.get("has_jitter", False),
            audio_codec=config_json.get("audio_codec"),
            audio_channels=config_json.get("audio_channels", 2),
            audio_sample_rate=config_json.get("audio_sample_rate", 44100),
            audio_bitrate_kbps=config_json.get("audio_bitrate_kbps", 128),
            recommended_tools=config_json.get("recommended_tools", []),
            recommended_settings=config_json.get("recommended_settings", {}),
            processing_notes=config_json.get("processing_notes", []),
            estimated_processing_time=config_json.get("estimated_processing_time", ""),
        )

    def _run_basic_analysis(self, filepath: str) -> VideoAnalysis:
        """
        Minimal analysis using only ffprobe.

        This is the fallback when no other backend is available.
        Provides basic metadata but no advanced analysis.

        Args:
            filepath: Video file path

        Returns:
            VideoAnalysis with basic metadata only
        """
        logger.info("Using minimal ffprobe-only analysis")

        try:
            # Get basic video info with ffprobe
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                filepath
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                raise RuntimeError(f"ffprobe failed: {result.stderr}")

            probe_data = json.loads(result.stdout)

            # Extract video stream
            video_stream = next(
                (s for s in probe_data.get("streams", []) if s["codec_type"] == "video"),
                {}
            )

            # Extract audio stream
            audio_stream = next(
                (s for s in probe_data.get("streams", []) if s["codec_type"] == "audio"),
                {}
            )

            format_info = probe_data.get("format", {})

            # Parse framerate
            fps_str = video_stream.get("r_frame_rate", "0/1")
            num, den = map(int, fps_str.split('/'))
            framerate = num / den if den != 0 else 0.0

            # Basic resolution-based source format detection
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))
            source_format = self._guess_source_format(width, height, framerate)

            # Create minimal VideoAnalysis
            return VideoAnalysis(
                filepath=filepath,
                filename=Path(filepath).name,
                filesize_mb=float(format_info.get("size", 0)) / (1024 * 1024),
                duration_seconds=float(format_info.get("duration", 0)),
                width=width,
                height=height,
                framerate=framerate,
                framerate_fraction=fps_str,
                codec=video_stream.get("codec_name", "unknown"),
                pixel_format=video_stream.get("pix_fmt", "unknown"),
                bitrate_kbps=int(video_stream.get("bit_rate", 0)) // 1000,
                scan_type=ScanType.UNKNOWN,  # Can't detect without idet filter
                content_type=ContentType.UNKNOWN,
                source_format=source_format,
                noise_level=NoiseLevel.MEDIUM,  # Default assumption
                estimated_quality_score=50.0,  # Unknown
                audio_codec=audio_stream.get("codec_name"),
                audio_channels=int(audio_stream.get("channels", 2)),
                audio_sample_rate=int(audio_stream.get("sample_rate", 44100)),
                audio_bitrate_kbps=int(audio_stream.get("bit_rate", 0)) // 1000,
                recommended_tools=["ffmpeg"],
                recommended_settings={"preset": "clean"},  # Safe default
                processing_notes=[
                    "Minimal analysis - consider using Python+OpenCV backend for better detection"
                ],
                analyzer_backend="ffprobe_only",
            )

        except Exception as e:
            logger.error(f"Basic analysis failed: {e}")
            raise RuntimeError(f"All analyzer backends failed: {e}")

    def _guess_source_format(
        self,
        width: int,
        height: int,
        framerate: float
    ) -> SourceFormat:
        """
        Guess source format from resolution and framerate.

        This is a simple heuristic-based detection for ffprobe-only backend.

        Args:
            width: Video width
            height: Video height
            framerate: Frames per second

        Returns:
            Best guess at SourceFormat
        """
        # VHS/DVD resolution
        if width == 720 and height in (480, 576):
            if abs(framerate - 29.97) < 0.1 or abs(framerate - 25.0) < 0.1:
                return SourceFormat.VHS  # Could be DVD too, but VHS is more common
            return SourceFormat.DVD

        # HD broadcast
        if width == 1920 and height == 1080:
            if abs(framerate - 59.94) < 0.1 or abs(framerate - 50.0) < 0.1:
                return SourceFormat.BROADCAST
            return SourceFormat.DIGITAL

        # 4K+
        if width >= 3840:
            return SourceFormat.DIGITAL

        return SourceFormat.UNKNOWN
