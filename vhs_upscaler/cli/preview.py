"""
Preview subcommand - Generate before/after comparison clips.

This subcommand extracts a short clip from the source video, processes it,
and creates a side-by-side comparison for quality evaluation before committing
to processing the entire video.

Usage:
    vhs-upscale preview input.mp4 -o preview.mp4
    vhs-upscale preview input.mp4 -o preview.mp4 --start 60 --duration 10
    vhs-upscale preview input.mp4 -o preview.mp4 -p vhs --no-comparison
"""

import argparse
import logging
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

try:
    from ..vhs_upscale import VHSUpscaler, ProcessingConfig
    HAS_IMPORTS = True
except ImportError:
    HAS_IMPORTS = False

from .common import (
    add_upscale_arguments,
    add_processing_arguments,
    add_audio_arguments,
    add_advanced_arguments,
    add_common_arguments,
    add_output_argument,
)

logger = logging.getLogger(__name__)


def setup_preview_parser(subparsers) -> argparse.ArgumentParser:
    """
    Create and configure the preview subcommand parser.

    Args:
        subparsers: Subparsers object from main argument parser

    Returns:
        Configured ArgumentParser for preview subcommand
    """
    parser = subparsers.add_parser(
        'preview',
        help='Generate before/after comparison preview clip',
        description="""
Generate a preview comparison clip for quality evaluation.

This command extracts a short segment from the source video, processes it
with the selected settings, and creates a side-by-side comparison video.
Perfect for testing different presets and settings before processing the
entire video.

The preview defaults to 10 seconds starting from 25% through the video
(to avoid intro/credits and capture representative content).
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Quick preview with defaults:
    vhs-upscale preview input.mp4 -o preview.mp4

  Preview specific segment:
    vhs-upscale preview input.mp4 -o preview.mp4 --start 60 --duration 15

  Test VHS preset:
    vhs-upscale preview input.mp4 -o preview.mp4 -p vhs

  Preview without comparison (processed only):
    vhs-upscale preview input.mp4 -o preview.mp4 --no-comparison

  Preview with vertical split:
    vhs-upscale preview input.mp4 -o preview.mp4 --vertical

  Extract to 4K with HDR:
    vhs-upscale preview input.mp4 -o preview.mp4 -r 2160 --hdr hdr10
        """
    )

    # Required arguments
    parser.add_argument(
        'input',
        type=Path,
        help='Input video file'
    )
    add_output_argument(parser, required=True)

    # Preview-specific options
    preview_group = parser.add_argument_group(
        'Preview Options',
        'Control preview clip extraction and comparison'
    )

    preview_group.add_argument(
        '--start',
        type=float,
        default=None,
        help='Start time in seconds (default: 25%% through video for representative content)'
    )

    preview_group.add_argument(
        '--duration',
        type=float,
        default=10.0,
        help='Preview clip duration in seconds (default: 10)'
    )

    preview_group.add_argument(
        '--no-comparison',
        action='store_true',
        help='Output processed clip only, skip side-by-side comparison'
    )

    preview_group.add_argument(
        '--vertical',
        action='store_true',
        help='Use vertical split (top/bottom) instead of horizontal (left/right)'
    )

    preview_group.add_argument(
        '--original-left',
        action='store_true',
        help='Put original on left/top (default: processed on left/top)'
    )

    # Add standard argument groups
    add_upscale_arguments(parser)
    add_processing_arguments(parser)
    add_audio_arguments(parser)
    add_advanced_arguments(parser)
    add_common_arguments(parser)

    return parser


def get_video_duration(video_path: Path, ffmpeg_path: str = "ffmpeg") -> Optional[float]:
    """
    Get video duration in seconds using ffprobe.

    Args:
        video_path: Path to video file
        ffmpeg_path: Path to ffmpeg/ffprobe

    Returns:
        Duration in seconds, or None if failed
    """
    ffprobe_path = ffmpeg_path.replace("ffmpeg", "ffprobe")

    try:
        result = subprocess.run(
            [
                ffprobe_path,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(video_path)
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        logger.warning(f"Failed to get video duration: {e}")
        return None


def extract_clip(input_path: Path, output_path: Path, start: float, duration: float,
                 ffmpeg_path: str = "ffmpeg") -> bool:
    """
    Extract a clip from video using ffmpeg.

    Args:
        input_path: Source video path
        output_path: Output clip path
        start: Start time in seconds
        duration: Clip duration in seconds
        ffmpeg_path: Path to ffmpeg

    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = [
            ffmpeg_path,
            "-ss", str(start),
            "-i", str(input_path),
            "-t", str(duration),
            "-c", "copy",
            "-y",
            str(output_path)
        ]

        logger.info(f"Extracting clip: {start}s for {duration}s")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Clip extraction failed: {result.stderr}")
            return False

        return True

    except Exception as e:
        logger.error(f"Failed to extract clip: {e}")
        return False


def create_comparison(original: Path, processed: Path, output: Path,
                      vertical: bool = False, original_first: bool = False,
                      ffmpeg_path: str = "ffmpeg") -> bool:
    """
    Create side-by-side comparison video.

    Args:
        original: Original video path
        processed: Processed video path
        output: Output comparison video path
        vertical: Use vertical split instead of horizontal
        original_first: Put original on left/top instead of processed
        ffmpeg_path: Path to ffmpeg

    Returns:
        True if successful, False otherwise
    """
    try:
        # Build filter based on orientation
        if vertical:
            # Top/bottom split
            if original_first:
                filter_complex = "[0:v][1:v]vstack[v]"
            else:
                filter_complex = "[1:v][0:v]vstack[v]"
        else:
            # Left/right split
            if original_first:
                filter_complex = "[0:v][1:v]hstack[v]"
            else:
                filter_complex = "[1:v][0:v]hstack[v]"

        cmd = [
            ffmpeg_path,
            "-i", str(original),
            "-i", str(processed),
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "1:a?",  # Use processed audio if available
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "192k",
            "-y",
            str(output)
        ]

        logger.info("Creating side-by-side comparison")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Comparison creation failed: {result.stderr}")
            return False

        return True

    except Exception as e:
        logger.error(f"Failed to create comparison: {e}")
        return False


def handle_preview(args: argparse.Namespace) -> int:
    """
    Handle the preview subcommand execution.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    if not HAS_IMPORTS:
        logger.error("Failed to import required modules")
        return 1

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate input
    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        return 1

    # Load config for ffmpeg path
    try:
        import yaml
        if args.config.exists():
            with open(args.config) as f:
                file_config = yaml.safe_load(f) or {}
        else:
            file_config = {}
    except:
        file_config = {}

    ffmpeg_path = file_config.get("ffmpeg_path", "ffmpeg")

    # Determine start time
    start_time = args.start
    if start_time is None:
        # Auto-select 25% through video
        duration = get_video_duration(args.input, ffmpeg_path)
        if duration:
            start_time = duration * 0.25
            logger.info(f"Auto-selected start time: {start_time:.1f}s (25% through video)")
        else:
            start_time = 30.0  # Fallback
            logger.info(f"Using fallback start time: {start_time}s")

    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Extract source clip
        source_clip = temp_path / "source_clip.mp4"
        if not extract_clip(args.input, source_clip, start_time, args.duration, ffmpeg_path):
            logger.error("Failed to extract source clip")
            return 1

        # Build processing config
        config = ProcessingConfig(
            maxine_path=file_config.get("maxine_path", ""),
            model_dir=file_config.get("model_dir", ""),
            ffmpeg_path=ffmpeg_path,
            resolution=args.resolution,
            quality_mode=args.quality,
            crf=args.crf,
            preset=args.preset,
            encoder=args.encoder,
            keep_temp=args.keep_temp,
            skip_maxine=args.skip_maxine,
            upscale_engine=args.engine,
            realesrgan_path=file_config.get("realesrgan_path", ""),
            realesrgan_model=args.realesrgan_model,
            hdr_mode=args.hdr,
            audio_enhance=args.audio_enhance,
            audio_upmix=args.audio_upmix,
            audio_layout=args.audio_layout,
            audio_format=args.audio_format,
            audio_bitrate=args.audio_bitrate,
            audio_normalize=not args.no_audio_normalize,
        )

        # Apply preset
        if hasattr(VHSUpscaler, 'PRESETS') and args.preset in VHSUpscaler.PRESETS:
            preset = VHSUpscaler.PRESETS[args.preset]
            config.deinterlace = preset.get("deinterlace", config.deinterlace)
            config.denoise = preset.get("denoise", config.denoise)
            config.denoise_strength = preset.get("denoise_strength", config.denoise_strength)
            config.quality_mode = preset.get("quality_mode", config.quality_mode)

        # Process clip
        try:
            upscaler = VHSUpscaler(config)
            processed_clip = temp_path / "processed_clip.mp4"

            logger.info("Processing preview clip...")
            success = upscaler.process(str(source_clip), processed_clip)

            if not success:
                logger.error("Preview processing failed")
                return 1

        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=args.verbose)
            return 1

        # Create output
        if args.no_comparison:
            # Just copy processed clip to output
            import shutil
            shutil.copy2(processed_clip, args.output)
            logger.info(f"Preview saved to: {args.output}")
        else:
            # Create comparison video
            if not create_comparison(
                source_clip,
                processed_clip,
                args.output,
                vertical=args.vertical,
                original_first=args.original_left,
                ffmpeg_path=ffmpeg_path
            ):
                logger.error("Failed to create comparison video")
                return 1

            logger.info(f"Comparison preview saved to: {args.output}")

    logger.info("Preview generation complete")
    return 0
