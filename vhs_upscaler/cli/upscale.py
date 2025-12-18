"""
Upscale subcommand - Main video upscaling functionality.

This subcommand handles single video file upscaling with full control over
all processing parameters. It's the primary entry point for video enhancement.

Usage:
    vhs-upscale upscale input.mp4 -o output.mp4
    vhs-upscale upscale input.mp4 -o output.mp4 -r 2160 -p vhs
    vhs-upscale upscale "https://youtube.com/watch?v=..." -o output.mp4
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

try:
    from ..vhs_upscale import VHSUpscaler, ProcessingConfig
    from ..analysis import AnalyzerWrapper, VideoAnalysis, AnalyzerBackend
    from ..presets import get_preset_from_analysis, get_recommended_settings_from_analysis
    HAS_IMPORTS = True
except ImportError:
    HAS_IMPORTS = False

from .common import (
    add_upscale_arguments,
    add_processing_arguments,
    add_audio_arguments,
    add_advanced_arguments,
    add_analysis_arguments,
    add_common_arguments,
    add_output_argument,
)

logger = logging.getLogger(__name__)


def setup_upscale_parser(subparsers) -> argparse.ArgumentParser:
    """
    Create and configure the upscale subcommand parser.

    Args:
        subparsers: Subparsers object from main argument parser

    Returns:
        Configured ArgumentParser for upscale subcommand
    """
    parser = subparsers.add_parser(
        'upscale',
        help='Upscale a single video file with AI enhancement',
        description="""
Upscale and enhance a video file using AI-powered algorithms.

This is the primary command for processing individual videos. It supports:
  - Local video files (MP4, AVI, MKV, MOV, etc.)
  - YouTube URLs (automatically downloads)
  - Multiple AI upscaling engines (NVIDIA Maxine, Real-ESRGAN, FFmpeg)
  - HDR output (HDR10, HLG)
  - Audio enhancement and surround upmixing
  - Automatic quality detection and optimization
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic upscale:
    vhs-upscale upscale input.mp4 -o output.mp4

  VHS to 4K with preset:
    vhs-upscale upscale vhs_tape.mp4 -o restored.mp4 -r 2160 -p vhs

  YouTube download and upscale:
    vhs-upscale upscale "https://youtube.com/watch?v=..." -o output.mp4

  Auto-detect optimal settings:
    vhs-upscale upscale input.mp4 -o output.mp4 --auto-detect

  HDR output with 5.1 audio:
    vhs-upscale upscale input.mp4 -o output.mp4 --hdr hdr10 \\
                --audio-layout 5.1 --audio-upmix surround

  Clean audio for voice:
    vhs-upscale upscale interview.mp4 -o output.mp4 --audio-enhance voice

  Non-NVIDIA GPU (AMD/Intel):
    vhs-upscale upscale input.mp4 -o output.mp4 --engine realesrgan
        """
    )

    # Required positional argument
    parser.add_argument(
        'input',
        type=str,
        help='Input video file path or YouTube URL'
    )

    # Add argument groups
    add_output_argument(parser, required=True)
    add_upscale_arguments(parser)
    add_processing_arguments(parser)
    add_audio_arguments(parser)
    add_analysis_arguments(parser)
    add_advanced_arguments(parser)
    add_common_arguments(parser)

    # Watch folder mode (special mode)
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Watch folder mode: monitor input folder for new videos and process automatically'
    )

    return parser


def load_config(config_path: Path) -> dict:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    if not config_path.exists():
        return {}

    try:
        import yaml
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        logger.warning("PyYAML not installed, skipping config file")
        return {}
    except Exception as e:
        logger.warning(f"Failed to load config file: {e}")
        return {}


def handle_upscale(args: argparse.Namespace) -> int:
    """
    Handle the upscale subcommand execution.

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
        logger.debug("Verbose logging enabled")

    # Import here to avoid circular imports
    from ..vhs_upscale import YouTubeDownloader

    # Video Analysis Integration
    analysis = None
    if args.auto_detect or args.analysis_config:
        try:
            from ..analysis import AnalyzerWrapper, VideoAnalysis, AnalyzerBackend
            HAS_ANALYSIS = True
        except ImportError:
            logger.error("Video analysis module not available. Install required dependencies.")
            return 1

        # Determine which file to analyze
        analyze_path = args.input

        # Skip download for YouTube URLs in analyze mode
        if YouTubeDownloader.is_youtube_url(args.input):
            if args.auto_detect:
                logger.info("YouTube URL detected - will download before analysis")
            # For auto-detect with YouTube, we'll download first then analyze
        elif args.analysis_config:
            # Load pre-analyzed config
            logger.info(f"Loading analysis config from {args.analysis_config}")
            try:
                analysis = VideoAnalysis.from_json(str(args.analysis_config))
                logger.info("Analysis loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load analysis config: {e}")
                return 1

        if args.auto_detect and not args.analysis_config:
            # Run analysis
            logger.info("Starting video analysis...")

            # Determine backend
            backend = None
            if args.force_backend:
                backend_map = {
                    "python": AnalyzerBackend.PYTHON_OPENCV,
                    "bash": AnalyzerBackend.BASH,
                    "basic": AnalyzerBackend.FFPROBE_ONLY,
                }
                backend = backend_map[args.force_backend]

            # Create wrapper and analyze
            try:
                wrapper = AnalyzerWrapper(force_backend=backend)
                analysis = wrapper.analyze(analyze_path)

                # Print analysis report
                print("\n" + analysis.get_summary())

                # Save if requested
                if args.save_analysis:
                    analysis.to_json(str(args.save_analysis))
                    logger.info(f"Analysis saved to {args.save_analysis}")

            except Exception as e:
                logger.error(f"Video analysis failed: {e}")
                logger.warning("Continuing with default settings")
                analysis = None

        # Apply analysis recommendations for auto-detect mode
        if args.auto_detect and analysis:
            logger.info("Applying recommended settings from analysis...")

            # Get recommended preset
            recommended_preset = get_preset_from_analysis(analysis)
            logger.info(f"Recommended preset: {recommended_preset}")

            # Override args with recommendations
            args.preset = recommended_preset

            # Get detailed settings
            try:
                recommended_settings = get_recommended_settings_from_analysis(analysis)
            except Exception as e:
                logger.warning(f"Failed to get detailed recommendations: {e}")
                recommended_settings = {}

            # Apply resolution based on source
            if analysis.width < 1280:
                # SD source: upscale to 1080p
                args.resolution = 1080
            elif analysis.width < 1920:
                # 720p source: upscale to 1080p or 1440p
                args.resolution = 1440
            else:
                # Already HD: minimal upscale
                args.resolution = analysis.height

            logger.info(f"Target resolution: {args.resolution}p")
            logger.info("Analysis recommendations applied")

    # Auto-detect YouTube and switch preset
    is_youtube = False
    try:
        is_youtube = YouTubeDownloader.is_youtube_url(args.input)
        if is_youtube and args.preset == "vhs" and not args.auto_detect:
            args.preset = "youtube"
            logger.info("Auto-selected 'youtube' preset for URL input")
    except:
        pass

    # Load config
    file_config = load_config(args.config)

    # Build ProcessingConfig
    config = ProcessingConfig(
        maxine_path=file_config.get("maxine_path", ""),
        model_dir=file_config.get("model_dir", ""),
        ffmpeg_path=file_config.get("ffmpeg_path", "ffmpeg"),
        resolution=args.resolution,
        quality_mode=args.quality,
        crf=args.crf,
        preset=args.preset,
        encoder=args.encoder,
        keep_temp=args.keep_temp,
        skip_maxine=args.skip_maxine,
        # Video options
        upscale_engine=args.engine,
        realesrgan_path=file_config.get("realesrgan_path", ""),
        realesrgan_model=args.realesrgan_model,
        hdr_mode=args.hdr,
        # Audio options
        audio_enhance=args.audio_enhance,
        audio_upmix=args.audio_upmix,
        audio_layout=args.audio_layout,
        audio_format=args.audio_format,
        audio_bitrate=args.audio_bitrate,
        audio_normalize=not args.no_audio_normalize,
        # LUT color grading
        lut_file=args.lut if hasattr(args, 'lut') else None,
        lut_strength=args.lut_strength if hasattr(args, 'lut_strength') else 1.0,
        # Face restoration
        face_restore=args.face_restore if hasattr(args, 'face_restore') else False,
        face_restore_strength=args.face_restore_strength if hasattr(args, 'face_restore_strength') else 0.5,
        face_restore_upscale=args.face_restore_upscale if hasattr(args, 'face_restore_upscale') else 2,
        # Deinterlacing
        deinterlace_algorithm=args.deinterlace_algorithm if hasattr(args, 'deinterlace_algorithm') else "yadif",
        qtgmc_preset=args.qtgmc_preset if hasattr(args, 'qtgmc_preset') else None,
    )

    # Apply preset overrides
    if hasattr(VHSUpscaler, 'PRESETS') and args.preset in VHSUpscaler.PRESETS:
        preset = VHSUpscaler.PRESETS[args.preset]
        config.deinterlace = preset.get("deinterlace", config.deinterlace)
        config.denoise = preset.get("denoise", config.denoise)
        config.denoise_strength = preset.get("denoise_strength", config.denoise_strength)
        config.quality_mode = preset.get("quality_mode", config.quality_mode)

    # Create upscaler instance
    try:
        upscaler = VHSUpscaler(config)
    except RuntimeError as e:
        logger.error(f"Failed to initialize upscaler: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error initializing upscaler: {e}")
        return 1

    # Prepare output path
    output_path = Path(args.output)

    # If output_path is a directory, generate filename
    if output_path.is_dir() or (not output_path.suffix and not output_path.exists()):
        # Extract filename from input
        input_path = Path(args.input)
        base_name = input_path.stem
        output_filename = f"{base_name}_{args.resolution}p.mp4"
        output_path = output_path / output_filename
        logger.info(f"Output will be saved to: {output_path}")

    # Dry-run mode: Show pipeline without executing
    if args.dry_run:
        logger.info("DRY-RUN MODE: Showing processing pipeline...")
        try:
            from ..dry_run import show_dry_run

            # Set output path in config for visualization
            config.output_path = output_path

            # Show pipeline
            pipeline = show_dry_run(config, Path(args.input))
            print("\n" + pipeline)

            return 0

        except Exception as e:
            logger.error(f"Failed to generate dry-run visualization: {e}", exc_info=args.verbose)
            return 1

    # Execute processing
    try:
        if args.watch:
            # Watch folder mode
            logger.info(f"Starting watch folder mode: {args.input} -> {output_path.parent}")
            upscaler.watch_folder(Path(args.input), output_path.parent)
            return 0
        else:
            # Single file processing
            logger.info(f"Processing: {args.input} -> {output_path}")
            success = upscaler.process(args.input, output_path)
            return 0 if success else 1

    except KeyboardInterrupt:
        logger.warning("Processing interrupted by user")
        return 130  # Standard Unix exit code for SIGINT
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=args.verbose)
        return 1
