"""
Analyze subcommand - Video characteristic analysis and reporting.

This subcommand analyzes video files to detect characteristics like scan type,
noise level, source format, and content type. Results can be used for manual
inspection or saved for later use with the upscale command.

Usage:
    vhs-upscale analyze input.mp4
    vhs-upscale analyze input.mp4 --save-analysis analysis.json
    vhs-upscale analyze input.mp4 --force-backend python
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

try:
    from ..analysis import AnalyzerWrapper, VideoAnalysis, AnalyzerBackend
    HAS_ANALYSIS = True
except ImportError:
    HAS_ANALYSIS = False

from .common import add_common_arguments

logger = logging.getLogger(__name__)


def setup_analyze_parser(subparsers) -> argparse.ArgumentParser:
    """
    Create and configure the analyze subcommand parser.

    Args:
        subparsers: Subparsers object from main argument parser

    Returns:
        Configured ArgumentParser for analyze subcommand
    """
    parser = subparsers.add_parser(
        'analyze',
        help='Analyze video characteristics without processing',
        description="""
Analyze video characteristics for intelligent processing decisions.

This command examines a video file and detects:
  - Scan type (progressive, interlaced, telecine)
  - Noise level (clean, low, medium, severe)
  - Source format (VHS, DVD, digital, broadcast)
  - Content type (live-action, animation, mixed)
  - Resolution, framerate, bitrate, codec
  - Quality score and recommendations

Analysis results can be saved to JSON and reused with --analysis-config
to skip re-analysis when processing the same video multiple times.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic analysis:
    vhs-upscale analyze input.mp4

  Save analysis for later:
    vhs-upscale analyze input.mp4 --save-analysis config.json
    vhs-upscale upscale input.mp4 -o output.mp4 --analysis-config config.json

  Force specific backend:
    vhs-upscale analyze input.mp4 --force-backend python

  Verbose mode with debugging:
    vhs-upscale analyze input.mp4 -v

Backends:
  python  - Full analysis using Python + OpenCV (best quality)
  bash    - Fast analysis using ffmpeg + awk (good quality)
  basic   - Minimal analysis using ffprobe only (fastest)
  auto    - Automatically select best available backend (default)
        """
    )

    # Required positional argument
    parser.add_argument(
        'input',
        type=Path,
        help='Input video file to analyze'
    )

    # Analysis-specific options
    parser.add_argument(
        '--save-analysis',
        type=Path,
        help='Export analysis results to JSON file for reuse with --analysis-config'
    )

    parser.add_argument(
        '--force-backend',
        choices=['python', 'bash', 'basic'],
        help='Force specific analyzer backend instead of auto-detection'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format (for scripting)'
    )

    parser.add_argument(
        '--recommend',
        action='store_true',
        help='Show recommended processing settings based on analysis'
    )

    # Common arguments
    add_common_arguments(parser)

    return parser


def handle_analyze(args: argparse.Namespace) -> int:
    """
    Handle the analyze subcommand execution.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    if not HAS_ANALYSIS:
        logger.error("Video analysis module not available.")
        logger.error("Install required dependencies: pip install opencv-python numpy")
        return 1

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Validate input file
    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        return 1

    if not args.input.is_file():
        logger.error(f"Input is not a file: {args.input}")
        return 1

    # Determine backend
    backend = None
    if args.force_backend:
        backend_map = {
            'python': AnalyzerBackend.PYTHON_OPENCV,
            'bash': AnalyzerBackend.BASH,
            'basic': AnalyzerBackend.FFPROBE_ONLY,
        }
        backend = backend_map[args.force_backend]
        logger.info(f"Using forced backend: {args.force_backend}")
    else:
        logger.info("Using auto-detected backend")

    # Create analyzer wrapper
    try:
        wrapper = AnalyzerWrapper(force_backend=backend)
        logger.info(f"Selected backend: {wrapper.get_backend_name()}")
    except Exception as e:
        logger.error(f"Failed to initialize analyzer: {e}")
        return 1

    # Run analysis
    try:
        logger.info(f"Analyzing video: {args.input}")
        analysis = wrapper.analyze(str(args.input))
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=args.verbose)
        return 1

    # Output results
    if args.json:
        # JSON output for scripting
        import json
        print(json.dumps(analysis.to_dict(), indent=2))
    else:
        # Human-readable summary
        print("\n" + analysis.get_summary())

    # Show recommendations if requested
    if args.recommend:
        try:
            from ..presets import get_preset_from_analysis, get_recommended_settings_from_analysis

            recommended_preset = get_preset_from_analysis(analysis)
            print("\n" + "=" * 60)
            print("RECOMMENDED SETTINGS")
            print("=" * 60)
            print(f"Preset: {recommended_preset}")

            try:
                recommended_settings = get_recommended_settings_from_analysis(analysis)
                print(f"\nRecommended resolution:")
                if analysis.width < 1280:
                    print("  1080p (upscale from SD)")
                elif analysis.width < 1920:
                    print("  1440p (upscale from 720p)")
                else:
                    print(f"  {analysis.height}p (minimal upscale)")

                print(f"\nRecommended command:")
                print(f"  vhs-upscale upscale {args.input} -o output.mp4 -p {recommended_preset}")

            except Exception as e:
                logger.warning(f"Failed to generate detailed recommendations: {e}")

        except ImportError:
            logger.warning("Preset module not available for recommendations")

    # Save analysis if requested
    if args.save_analysis:
        try:
            analysis.to_json(str(args.save_analysis))
            logger.info(f"Analysis saved to: {args.save_analysis}")
            print(f"\nTo reuse this analysis:")
            print(f"  vhs-upscale upscale {args.input} -o output.mp4 --analysis-config {args.save_analysis}")
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
            return 1

    return 0
