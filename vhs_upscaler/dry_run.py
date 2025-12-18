"""
Dry-run mode for pipeline visualization.

Shows the complete processing pipeline without executing it, including:
- All processing stages and their configuration
- FFmpeg commands that would be executed
- Expected file sizes and processing estimates
- Validation of settings and dependencies
"""

import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class DryRunVisualizer:
    """
    Visualize processing pipeline without execution.

    Shows exactly what would happen during processing, including all commands,
    filters, and processing stages. Useful for validating settings before
    committing to full processing.
    """

    def __init__(self, config, input_path: Path):
        """
        Initialize dry-run visualizer.

        Args:
            config: ProcessingConfig object
            input_path: Input video path
        """
        self.config = config
        self.input_path = input_path

    def show_pipeline(self) -> str:
        """
        Generate and return complete pipeline visualization.

        Returns:
            Formatted string showing complete pipeline
        """
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("DRY-RUN MODE: Processing Pipeline Visualization")
        lines.append("=" * 80)
        lines.append("")

        # Input/Output info
        lines.extend(self._show_io_info())
        lines.append("")

        # Video analysis info
        lines.extend(self._show_video_info())
        lines.append("")

        # Processing stages
        lines.extend(self._show_preprocessing_stage())
        lines.append("")

        lines.extend(self._show_upscaling_stage())
        lines.append("")

        lines.extend(self._show_postprocessing_stage())
        lines.append("")

        # FFmpeg commands
        lines.append("=" * 80)
        lines.append("FFmpeg Commands (Estimated)")
        lines.append("=" * 80)
        lines.append("")
        lines.extend(self._show_ffmpeg_commands())
        lines.append("")

        # Validation warnings
        warnings = self._validate_configuration()
        if warnings:
            lines.append("=" * 80)
            lines.append("Configuration Warnings")
            lines.append("=" * 80)
            lines.append("")
            for warning in warnings:
                lines.append(f"  [WARNING] {warning}")
            lines.append("")

        # Footer
        lines.append("=" * 80)
        lines.append("This is a DRY-RUN - no files will be modified")
        lines.append("Remove --dry-run flag to execute processing")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _show_io_info(self) -> List[str]:
        """Show input/output information."""
        lines = ["Input/Output Configuration:"]
        lines.append(f"  Input File: {self.input_path}")

        if hasattr(self.config, 'output_path'):
            lines.append(f"  Output File: {self.config.output_path}")

        # Get input video info
        try:
            info = self._get_video_info()
            if info:
                lines.append(f"  Input Resolution: {info['width']}x{info['height']}")
                lines.append(f"  Input Duration: {info['duration']:.1f} seconds")
                lines.append(f"  Input Codec: {info['codec']}")
                lines.append(f"  Input Bitrate: {info['bitrate'] / 1000000:.1f} Mbps")
        except:
            pass

        # Show output specs
        if hasattr(self.config, 'resolution'):
            lines.append(f"  Target Resolution: {self.config.resolution}p")

        return lines

    def _show_video_info(self) -> List[str]:
        """Show video analysis information."""
        lines = ["Video Analysis:"]

        try:
            info = self._get_video_info()
            if info:
                # Detect interlacing
                is_interlaced = info.get('interlaced', False)
                lines.append(f"  Interlaced: {'Yes' if is_interlaced else 'No'}")

                # Frame rate
                if 'fps' in info:
                    lines.append(f"  Frame Rate: {info['fps']:.2f} fps")

                # Aspect ratio
                if 'width' in info and 'height' in info:
                    aspect = info['width'] / info['height']
                    lines.append(f"  Aspect Ratio: {aspect:.2f}:1")
        except:
            lines.append("  [Unable to analyze video - processing will detect automatically]")

        return lines

    def _show_preprocessing_stage(self) -> List[str]:
        """Show preprocessing stage details."""
        lines = ["Stage 1: Preprocessing"]
        lines.append("-" * 80)

        # Deinterlacing
        if self.config.deinterlace:
            algo = self.config.deinterlace_algorithm
            lines.append(f"  [1.1] Deinterlacing: {algo.upper()}")

            if algo == "qtgmc":
                preset = self.config.qtgmc_preset or "medium"
                lines.append(f"        Engine: VapourSynth QTGMC")
                lines.append(f"        Quality Preset: {preset}")
                lines.append(f"        Processing: Separate pass (highest quality)")
            elif algo == "bwdif":
                lines.append(f"        Engine: FFmpeg BWDIF")
                lines.append(f"        Processing: In filter chain (better motion compensation)")
            elif algo == "w3fdif":
                lines.append(f"        Engine: FFmpeg W3FDIF")
                lines.append(f"        Processing: In filter chain (better detail preservation)")
            else:  # yadif
                lines.append(f"        Engine: FFmpeg YADIF")
                lines.append(f"        Processing: In filter chain (fast, good quality)")
        else:
            lines.append(f"  [1.1] Deinterlacing: DISABLED")

        # Denoising
        if self.config.denoise:
            ds = self.config.denoise_strength
            lines.append(f"  [1.2] Denoising: ENABLED")
            lines.append(f"        Algorithm: hqdn3d")
            lines.append(f"        Strength: Luma={ds[0]}, Chroma={ds[1]}, "
                        f"Temporal Luma={ds[2]}, Temporal Chroma={ds[3]}")
        else:
            lines.append(f"  [1.2] Denoising: DISABLED")

        # LUT color grading
        if hasattr(self.config, 'lut_file') and self.config.lut_file:
            lines.append(f"  [1.3] Color Grading (LUT): ENABLED")
            lines.append(f"        LUT File: {self.config.lut_file}")
            if hasattr(self.config, 'lut_strength'):
                lines.append(f"        Strength: {self.config.lut_strength * 100:.0f}%")
        else:
            lines.append(f"  [1.3] Color Grading (LUT): DISABLED")

        # Audio extraction
        lines.append(f"  [1.4] Audio Extraction: ENABLED")
        lines.append(f"        Format: AAC")

        return lines

    def _show_upscaling_stage(self) -> List[str]:
        """Show upscaling stage details."""
        lines = ["Stage 2: Upscaling"]
        lines.append("-" * 80)

        engine = self.config.upscale_engine
        lines.append(f"  [2.1] Upscaling Engine: {engine.upper()}")

        if engine == "realesrgan":
            lines.append(f"        Model: {self.config.realesrgan_model}")
            lines.append(f"        Target Resolution: {self.config.resolution}p")
            lines.append(f"        Processing: GPU accelerated")
        elif engine == "maxine":
            lines.append(f"        Model: NVIDIA Maxine Video Super Resolution")
            lines.append(f"        Target Resolution: {self.config.resolution}p")
            lines.append(f"        Processing: GPU accelerated (NVIDIA RTX required)")
        else:
            lines.append(f"        Processing: FFmpeg scale filter (fallback)")
            lines.append(f"        Target Resolution: {self.config.resolution}p")

        # Face restoration
        if hasattr(self.config, 'face_restore') and self.config.face_restore:
            lines.append(f"  [2.2] Face Restoration: ENABLED")
            lines.append(f"        Model: GFPGAN v1.3")
            strength = getattr(self.config, 'face_restore_strength', 0.5)
            lines.append(f"        Strength: {strength * 100:.0f}%")
            lines.append(f"        Processing: Separate pass (blended with upscaled video)")
        else:
            lines.append(f"  [2.2] Face Restoration: DISABLED")

        return lines

    def _show_postprocessing_stage(self) -> List[str]:
        """Show postprocessing stage details."""
        lines = ["Stage 3: Encoding & Finalization"]
        lines.append("-" * 80)

        # Sharpening
        if hasattr(self.config, 'sharpen') and self.config.sharpen:
            lines.append(f"  [3.1] Sharpening: ENABLED")
            lines.append(f"        Filter: unsharp")
        else:
            lines.append(f"  [3.1] Sharpening: DISABLED")

        # Encoding
        lines.append(f"  [3.2] Video Encoding:")
        lines.append(f"        Codec: {self.config.encoder}")
        lines.append(f"        Quality: CRF {self.config.crf}")
        lines.append(f"        Preset: {self.config.quality_mode}")

        # HDR
        if self.config.hdr_mode and self.config.hdr_mode != "sdr":
            lines.append(f"        HDR Mode: {self.config.hdr_mode.upper()}")
        else:
            lines.append(f"        HDR Mode: SDR (Standard Dynamic Range)")

        # Audio
        lines.append(f"  [3.3] Audio Processing:")

        if self.config.audio_enhance:
            lines.append(f"        Enhancement: ENABLED")

        if self.config.audio_upmix:
            lines.append(f"        Upmix: {self.config.audio_layout}")

        if hasattr(self.config, 'audio_format'):
            lines.append(f"        Format: {self.config.audio_format}")

        if hasattr(self.config, 'audio_bitrate'):
            lines.append(f"        Bitrate: {self.config.audio_bitrate}")

        if self.config.audio_normalize:
            lines.append(f"        Normalization: ENABLED")

        return lines

    def _show_ffmpeg_commands(self) -> List[str]:
        """Show estimated FFmpeg commands."""
        lines = []

        # Preprocessing command (approximate)
        lines.append("[Preprocessing FFmpeg Command]")
        cmd_parts = [str(self.config.ffmpeg_path), "-i", str(self.input_path)]

        # Build filter chain
        filters = []

        # Deinterlacing (FFmpeg-based only)
        if self.config.deinterlace:
            algo = self.config.deinterlace_algorithm
            if algo == "bwdif":
                filters.append("bwdif=1")
            elif algo == "w3fdif":
                filters.append("w3fdif")
            elif algo == "yadif":
                filters.append("yadif=1")

        # Denoising
        if self.config.denoise:
            ds = self.config.denoise_strength
            filters.append(f"hqdn3d={ds[0]}:{ds[1]}:{ds[2]}:{ds[3]}")

        # LUT
        if hasattr(self.config, 'lut_file') and self.config.lut_file:
            filters.append(f"lut3d=file='{self.config.lut_file}'")

        if filters:
            cmd_parts.extend(["-vf", ",".join(filters)])

        cmd_parts.extend(["-an", "prepped_video.mp4"])
        lines.append("  " + " ".join(str(part) for part in cmd_parts))
        lines.append("")

        # Upscaling command
        if self.config.upscale_engine == "realesrgan":
            lines.append("[Real-ESRGAN Upscaling Command]")
            lines.append(f"  realesrgan-ncnn-vulkan -i prepped_video.mp4 "
                        f"-o upscaled_video.mp4 -n {self.config.realesrgan_model}")
            lines.append("")

        # Encoding command
        lines.append("[Final Encoding Command]")
        cmd_parts = [
            str(self.config.ffmpeg_path),
            "-i", "upscaled_video.mp4",
            "-i", "audio.aac",
            "-c:v", str(self.config.encoder),
            "-crf", str(self.config.crf),
            "-preset", str(self.config.quality_mode),
            "-c:a", "copy",
            "-y", "output.mp4"
        ]
        lines.append("  " + " ".join(cmd_parts))

        return lines

    def _validate_configuration(self) -> List[str]:
        """Validate configuration and return warnings."""
        warnings = []

        # Check QTGMC availability
        if self.config.deinterlace_algorithm == "qtgmc":
            try:
                import vapoursynth
            except ImportError:
                warnings.append("QTGMC requested but VapourSynth not installed - will fall back to yadif")

        # Check GFPGAN availability
        if hasattr(self.config, 'face_restore') and self.config.face_restore:
            try:
                import gfpgan
            except ImportError:
                warnings.append("Face restoration requested but GFPGAN not installed")

        # Check Maxine availability
        if self.config.upscale_engine == "maxine" and not self.config.skip_maxine:
            if not self.config.maxine_path or not Path(self.config.maxine_path).exists():
                warnings.append("Maxine engine selected but maxine_path not configured or invalid")

        # Check Real-ESRGAN availability
        if self.config.upscale_engine == "realesrgan":
            if not self.config.realesrgan_path:
                warnings.append("Real-ESRGAN engine selected but realesrgan_path not configured")

        # Check LUT file
        if hasattr(self.config, 'lut_file') and self.config.lut_file:
            if not Path(self.config.lut_file).exists():
                warnings.append(f"LUT file not found: {self.config.lut_file}")

        # Check CRF value
        if self.config.crf < 10:
            warnings.append(f"Very low CRF ({self.config.crf}) will produce very large files")
        elif self.config.crf > 30:
            warnings.append(f"High CRF ({self.config.crf}) may produce noticeable quality loss")

        # Check resolution
        if self.config.resolution > 2160:
            warnings.append(f"Very high resolution ({self.config.resolution}p) requires significant processing time and disk space")

        return warnings

    @staticmethod
    def _parse_framerate(fps_str: str) -> float:
        """Safely parse framerate fraction (e.g., '30000/1001' -> 29.97)."""
        try:
            if '/' in fps_str:
                num, den = fps_str.split('/', 1)
                num_val = int(num)
                den_val = int(den)
                return num_val / den_val if den_val != 0 else 0.0
            else:
                return float(fps_str)
        except (ValueError, ZeroDivisionError):
            return 0.0

    def _get_video_info(self) -> Optional[Dict]:
        """Get video information using ffprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                "-show_format",
                str(self.input_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            import json
            data = json.loads(result.stdout)

            # Find video stream
            video_stream = None
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    video_stream = stream
                    break

            if not video_stream:
                return None

            # Extract info
            info = {
                "width": video_stream.get("width", 0),
                "height": video_stream.get("height", 0),
                "codec": video_stream.get("codec_name", "unknown"),
                "duration": float(data.get("format", {}).get("duration", 0)),
                "bitrate": int(data.get("format", {}).get("bit_rate", 0)),
                "fps": self._parse_framerate(video_stream.get("r_frame_rate", "0/1")),
                "interlaced": video_stream.get("field_order", "progressive") != "progressive"
            }

            return info

        except Exception as e:
            logger.debug(f"Failed to get video info: {e}")
            return None


def show_dry_run(config, input_path: Path) -> str:
    """
    Show dry-run visualization for processing pipeline.

    Args:
        config: ProcessingConfig object
        input_path: Input video path

    Returns:
        Formatted pipeline visualization string
    """
    visualizer = DryRunVisualizer(config, input_path)
    return visualizer.show_pipeline()
