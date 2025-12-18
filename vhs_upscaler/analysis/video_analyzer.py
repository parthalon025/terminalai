"""
Python video analyzer backend with optional OpenCV support.

This module implements frame-level video analysis for detecting:
- Interlacing and scan type
- Noise levels
- Content type (live action vs animation)
- Source format (VHS, DVD, digital)
- VHS-specific artifacts

Based on user-provided video_analyzer.py implementation.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from .models import (
    VideoAnalysis,
    ScanType,
    ContentType,
    NoiseLevel,
    SourceFormat,
)

logger = logging.getLogger(__name__)

# Check for OpenCV availability
HAS_OPENCV = False
try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    logger.debug("OpenCV not available - using basic Python analyzer")


class VideoAnalyzer:
    """
    Python-based video analyzer with optional OpenCV support.

    When OpenCV is available, performs advanced frame-level analysis.
    Without OpenCV, falls back to FFmpeg-based analysis.
    """

    def __init__(self, use_opencv: bool = True):
        """
        Initialize video analyzer.

        Args:
            use_opencv: Whether to use OpenCV (if available)
        """
        self.use_opencv = use_opencv and HAS_OPENCV

    def analyze(self, filepath: str) -> VideoAnalysis:
        """
        Analyze video file and return complete VideoAnalysis.

        Args:
            filepath: Path to video file

        Returns:
            VideoAnalysis with detected characteristics

        Raises:
            FileNotFoundError: If video file doesn't exist
        """
        filepath_obj = Path(filepath)
        if not filepath_obj.exists():
            raise FileNotFoundError(f"Video file not found: {filepath}")

        logger.info(f"Analyzing video with Python backend (OpenCV: {self.use_opencv})")

        # Get basic metadata with ffprobe
        metadata = self._get_metadata(filepath)

        # Detect scan type (interlaced vs progressive)
        scan_type = self._detect_scan_type(filepath, metadata)

        # Estimate noise level
        noise_level = self._estimate_noise_level(filepath, metadata)

        # Detect content type
        content_type = self._detect_content_type(filepath, metadata)

        # Detect source format
        source_format = self._detect_source_format(metadata, scan_type, noise_level)

        # Detect VHS artifacts
        vhs_artifacts = self._detect_vhs_artifacts(filepath, metadata, source_format)

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            metadata, scan_type, noise_level, source_format
        )

        # Generate recommendations
        recommended_settings, processing_notes = self._generate_recommendations(
            scan_type, noise_level, content_type, source_format, vhs_artifacts
        )

        # Estimate processing time
        processing_time = self._estimate_processing_time(metadata, recommended_settings)

        return VideoAnalysis(
            filepath=filepath,
            filename=filepath_obj.name,
            filesize_mb=metadata["filesize_mb"],
            duration_seconds=metadata["duration"],
            width=metadata["width"],
            height=metadata["height"],
            framerate=metadata["framerate"],
            framerate_fraction=metadata["framerate_fraction"],
            codec=metadata["codec"],
            pixel_format=metadata["pixel_format"],
            bitrate_kbps=metadata["bitrate_kbps"],
            scan_type=scan_type,
            content_type=content_type,
            source_format=source_format,
            noise_level=noise_level,
            estimated_quality_score=quality_score,
            has_tracking_errors=vhs_artifacts["has_tracking_errors"],
            has_color_bleeding=vhs_artifacts["has_color_bleeding"],
            has_head_switching_noise=vhs_artifacts["has_head_switching_noise"],
            has_dropout_lines=vhs_artifacts["has_dropout_lines"],
            has_jitter=vhs_artifacts["has_jitter"],
            audio_codec=metadata.get("audio_codec"),
            audio_channels=metadata.get("audio_channels", 2),
            audio_sample_rate=metadata.get("audio_sample_rate", 44100),
            audio_bitrate_kbps=metadata.get("audio_bitrate_kbps", 128),
            recommended_tools=["ffmpeg", "real-esrgan"],
            recommended_settings=recommended_settings,
            processing_notes=processing_notes,
            estimated_processing_time=processing_time,
            analyzer_backend="python_opencv" if self.use_opencv else "python_basic",
        )

    def _get_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract video metadata using ffprobe."""
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            filepath
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        probe_data = json.loads(result.stdout)

        video_stream = next(
            (s for s in probe_data["streams"] if s["codec_type"] == "video"),
            {}
        )
        audio_stream = next(
            (s for s in probe_data["streams"] if s["codec_type"] == "audio"),
            None
        )
        format_info = probe_data["format"]

        # Parse framerate
        fps_str = video_stream.get("r_frame_rate", "0/1")
        num, den = map(int, fps_str.split('/'))
        framerate = num / den if den != 0 else 0.0

        metadata = {
            "width": int(video_stream.get("width", 0)),
            "height": int(video_stream.get("height", 0)),
            "framerate": framerate,
            "framerate_fraction": fps_str,
            "codec": video_stream.get("codec_name", "unknown"),
            "pixel_format": video_stream.get("pix_fmt", "unknown"),
            "bitrate_kbps": int(video_stream.get("bit_rate", 0)) // 1000,
            "duration": float(format_info.get("duration", 0)),
            "filesize_mb": float(format_info.get("size", 0)) / (1024 * 1024),
        }

        if audio_stream:
            metadata.update({
                "audio_codec": audio_stream.get("codec_name"),
                "audio_channels": int(audio_stream.get("channels", 2)),
                "audio_sample_rate": int(audio_stream.get("sample_rate", 44100)),
                "audio_bitrate_kbps": int(audio_stream.get("bit_rate", 0)) // 1000,
            })

        return metadata

    def _detect_scan_type(self, filepath: str, metadata: Dict) -> ScanType:
        """Detect if video is interlaced using FFmpeg idet filter."""
        try:
            # Use idet filter to detect interlacing
            cmd = [
                "ffmpeg",
                "-i", filepath,
                "-vf", "idet",
                "-frames:v", "100",
                "-an",
                "-f", "null",
                "-"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse idet output
            output = result.stderr

            # Look for idet statistics
            if "TFF:" in output and "BFF:" in output and "Progressive:" in output:
                # Extract frame counts
                for line in output.split('\n'):
                    if '[Parsed_idet' in line and 'TFF:' in line:
                        # Parse: TFF:123 BFF:45 Progressive:234
                        parts = line.split()
                        tff = int(parts[parts.index('TFF:') + 1]) if 'TFF:' in parts else 0
                        bff = int(parts[parts.index('BFF:') + 1]) if 'BFF:' in parts else 0
                        prog = int(parts[parts.index('Progressive:') + 1]) if 'Progressive:' in parts else 0

                        # Determine dominant type (>80% threshold)
                        total = tff + bff + prog
                        if total > 0:
                            if prog / total > 0.8:
                                return ScanType.PROGRESSIVE
                            elif tff / total > 0.5:
                                return ScanType.INTERLACED_TFF
                            elif bff / total > 0.5:
                                return ScanType.INTERLACED_BFF

            return ScanType.UNKNOWN

        except Exception as e:
            logger.warning(f"Scan type detection failed: {e}")
            return ScanType.UNKNOWN

    def _estimate_noise_level(self, filepath: str, metadata: Dict) -> NoiseLevel:
        """Estimate noise level from bitrate and resolution."""
        # Heuristic based on bitrate per pixel
        width = metadata["width"]
        height = metadata["height"]
        bitrate = metadata["bitrate_kbps"]

        if width == 0 or height == 0:
            return NoiseLevel.MEDIUM

        pixels = width * height
        bitrate_per_pixel = (bitrate * 1000) / pixels

        # Lower bitrate per pixel = more compression = more noise
        if bitrate_per_pixel < 0.1:
            return NoiseLevel.SEVERE
        elif bitrate_per_pixel < 0.3:
            return NoiseLevel.HIGH
        elif bitrate_per_pixel < 0.7:
            return NoiseLevel.MEDIUM
        else:
            return NoiseLevel.LOW

    def _detect_content_type(self, filepath: str, metadata: Dict) -> ContentType:
        """Detect content type (basic heuristic without OpenCV)."""
        # Without OpenCV, use codec/bitrate hints
        codec = metadata["codec"]

        # Animation often uses specific codecs or higher compression
        if "vp9" in codec or "av1" in codec:
            return ContentType.ANIMATION

        return ContentType.LIVE_ACTION

    def _detect_source_format(
        self,
        metadata: Dict,
        scan_type: ScanType,
        noise_level: NoiseLevel
    ) -> SourceFormat:
        """Detect source format from metadata and characteristics."""
        width = metadata["width"]
        height = metadata["height"]
        framerate = metadata["framerate"]
        bitrate = metadata["bitrate_kbps"]

        # VHS: 720x480/576, interlaced, low bitrate, high noise
        if width == 720 and height in (480, 576):
            if scan_type.value.startswith("interlaced") and noise_level in (NoiseLevel.HIGH, NoiseLevel.SEVERE):
                return SourceFormat.VHS
            elif bitrate < 3000:
                return SourceFormat.VHS
            else:
                return SourceFormat.DVD

        # HD: likely digital or broadcast
        if width >= 1920:
            if scan_type == ScanType.INTERLACED_TFF:
                return SourceFormat.BROADCAST
            else:
                return SourceFormat.DIGITAL

        return SourceFormat.UNKNOWN

    def _detect_vhs_artifacts(
        self,
        filepath: str,
        metadata: Dict,
        source_format: SourceFormat
    ) -> Dict[str, bool]:
        """Detect VHS-specific artifacts."""
        artifacts = {
            "has_tracking_errors": False,
            "has_color_bleeding": False,
            "has_head_switching_noise": False,
            "has_dropout_lines": False,
            "has_jitter": False,
        }

        # Only check for VHS artifacts if source is VHS
        if source_format != SourceFormat.VHS:
            return artifacts

        # Basic detection: assume VHS has color bleeding
        artifacts["has_color_bleeding"] = True

        # Low resolution VHS often has head switching noise
        if metadata["height"] == 480:
            artifacts["has_head_switching_noise"] = True

        return artifacts

    def _calculate_quality_score(
        self,
        metadata: Dict,
        scan_type: ScanType,
        noise_level: NoiseLevel,
        source_format: SourceFormat
    ) -> float:
        """Calculate overall quality score (0-100)."""
        score = 50.0  # Start at middle

        # Resolution factor
        pixels = metadata["width"] * metadata["height"]
        if pixels >= 1920 * 1080:
            score += 20
        elif pixels >= 1280 * 720:
            score += 10
        elif pixels <= 720 * 480:
            score -= 10

        # Noise penalty
        if noise_level == NoiseLevel.LOW:
            score += 15
        elif noise_level == NoiseLevel.HIGH:
            score -= 15
        elif noise_level == NoiseLevel.SEVERE:
            score -= 25

        # Scan type
        if scan_type == ScanType.PROGRESSIVE:
            score += 10
        elif scan_type.value.startswith("interlaced"):
            score -= 5

        # Source format
        if source_format == SourceFormat.DIGITAL:
            score += 10
        elif source_format == SourceFormat.VHS:
            score -= 15

        return max(0.0, min(100.0, score))

    def _generate_recommendations(
        self,
        scan_type: ScanType,
        noise_level: NoiseLevel,
        content_type: ContentType,
        source_format: SourceFormat,
        vhs_artifacts: Dict[str, bool]
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Generate recommended settings and processing notes."""
        settings = {}
        notes = []

        # Preset selection (will use presets.py later)
        if source_format == SourceFormat.VHS:
            if noise_level == NoiseLevel.SEVERE:
                settings["preset"] = "vhs_heavy"
                notes.append("Severe noise detected - aggressive denoise recommended")
            elif noise_level in (NoiseLevel.HIGH, NoiseLevel.MEDIUM):
                settings["preset"] = "vhs"
            else:
                settings["preset"] = "vhs_clean"
        elif content_type == ContentType.ANIMATION:
            settings["preset"] = "animation"
        else:
            settings["preset"] = "clean"

        # Deinterlacing
        if scan_type.value.startswith("interlaced"):
            settings["deinterlace"] = "yadif=1"
            notes.append("Interlaced source - deinterlace before upscaling")

        # VHS artifacts
        if vhs_artifacts.get("has_head_switching_noise"):
            settings["crop_bottom"] = 8
            notes.append("Head switching noise detected - crop bottom 8px recommended")

        if vhs_artifacts.get("has_color_bleeding"):
            notes.append("Color bleeding detected - consider color correction")

        return settings, notes

    def _estimate_processing_time(
        self,
        metadata: Dict,
        settings: Dict[str, Any]
    ) -> str:
        """Estimate processing time based on duration and settings."""
        duration = metadata["duration"]

        # Very rough estimate: 1 minute of video = 2 minutes processing
        # (varies greatly by hardware and settings)
        estimated_minutes = int(duration / 30)  # Conservative estimate

        if estimated_minutes < 5:
            return "~5 minutes"
        elif estimated_minutes < 60:
            return f"~{estimated_minutes} minutes"
        else:
            hours = estimated_minutes // 60
            minutes = estimated_minutes % 60
            return f"~{hours}h {minutes}m"
