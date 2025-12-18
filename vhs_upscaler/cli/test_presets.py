"""
Test presets subcommand - Generate comparison suite with multiple presets.

This subcommand extracts a clip from the source video and processes it with
multiple presets, creating a comparison suite to help users choose the best
preset for their content.

Usage:
    vhs-upscale test-presets input.mp4 -o output_folder/
    vhs-upscale test-presets input.mp4 -o output_folder/ --start 60
    vhs-upscale test-presets input.mp4 -o output_folder/ --presets vhs,dvd,clean
"""

import argparse
import logging
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

try:
    from ..vhs_upscale import VHSUpscaler, ProcessingConfig
    from ..comparison import PresetComparator, ComparisonConfig
    HAS_IMPORTS = True
except ImportError:
    HAS_IMPORTS = False

from .common import (
    add_upscale_arguments,
    add_advanced_arguments,
    add_common_arguments,
)

logger = logging.getLogger(__name__)


# Available presets
DEFAULT_TEST_PRESETS = ['vhs', 'dvd', 'webcam', 'clean', 'youtube']


def setup_test_presets_parser(subparsers) -> argparse.ArgumentParser:
    """
    Create and configure the test-presets subcommand parser.

    Args:
        subparsers: Subparsers object from main argument parser

    Returns:
        Configured ArgumentParser for test-presets subcommand
    """
    parser = subparsers.add_parser(
        'test-presets',
        help='Test multiple presets on a clip for comparison',
        description="""
Generate a comparison suite with multiple presets.

This command extracts a representative clip from your video and processes
it with multiple presets (VHS, DVD, webcam, clean, YouTube). Each preset
is saved as a separate file, allowing you to compare quality and choose
the best setting for your full video processing.

Perfect for testing before committing to a long upscale job.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Test all default presets:
    vhs-upscale test-presets input.mp4 -o test_results/

  Test specific presets:
    vhs-upscale test-presets input.mp4 -o test_results/ --presets vhs,dvd,clean

  Test specific segment:
    vhs-upscale test-presets input.mp4 -o test_results/ --start 120 --duration 15

  Test with 4K resolution:
    vhs-upscale test-presets input.mp4 -o test_results/ -r 2160

  Create comparison grid:
    vhs-upscale test-presets input.mp4 -o test_results/ --create-grid

Output files:
  test_results/original.mp4           - Source clip
  test_results/preset_vhs.mp4         - VHS preset result
  test_results/preset_dvd.mp4         - DVD preset result
  test_results/preset_clean.mp4       - Clean preset result
  test_results/comparison_grid.mp4    - 2x2 grid comparison (if --create-grid)
        """
    )

    # Required arguments
    parser.add_argument(
        'input',
        type=Path,
        help='Input video file'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        type=Path,
        help='Output folder for preset comparison files'
    )

    # Test presets specific options
    test_group = parser.add_argument_group(
        'Test Options',
        'Control preset testing behavior'
    )

    test_group.add_argument(
        '--presets',
        default=None,
        help=f'Comma-separated list of presets to test (default: all)'
             f'\nAvailable: {", ".join(DEFAULT_TEST_PRESETS)}'
    )

    test_group.add_argument(
        '--start',
        type=float,
        default=None,
        help='Start time in seconds (default: 25%% through video)'
    )

    test_group.add_argument(
        '--duration',
        type=float,
        default=10.0,
        help='Test clip duration in seconds (default: 10)'
    )

    test_group.add_argument(
        '--create-grid',
        action='store_true',
        help='Create a comparison grid video with all presets'
    )

    test_group.add_argument(
        '--grid-layout',
        default='2x2',
        choices=['2x2', '2x3', '3x2', '1x4', '4x1'],
        help='Grid layout for comparison (default: 2x2)'
    )

    test_group.add_argument(
        '--multi-clip',
        action='store_true',
        help='Extract multiple clips at different positions for comprehensive comparison'
    )

    test_group.add_argument(
        '--clip-count',
        type=int,
        default=3,
        help='Number of clips to extract for multi-clip mode (default: 3)'
    )

    test_group.add_argument(
        '--timestamps',
        default=None,
        help='Comma-separated custom timestamps in seconds for clip extraction (e.g., "30,90,150")'
    )

    # Add standard argument groups (limited set)
    add_upscale_arguments(parser)
    add_advanced_arguments(parser)
    add_common_arguments(parser)

    return parser


def get_video_duration(video_path: Path, ffmpeg_path: str = "ffmpeg") -> Optional[float]:
    """Get video duration in seconds using ffprobe."""
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


def extract_clip(input_path: Path, output_path: Path, start: float,
                 duration: float, ffmpeg_path: str = "ffmpeg") -> bool:
    """Extract a clip from video using ffmpeg."""
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

        logger.debug(f"Extracting clip: {start}s for {duration}s")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Clip extraction failed: {result.stderr}")
            return False

        return True

    except Exception as e:
        logger.error(f"Failed to extract clip: {e}")
        return False


def create_comparison_grid(video_paths: List[Path], labels: List[str],
                          output_path: Path, layout: str = '2x2',
                          ffmpeg_path: str = "ffmpeg") -> bool:
    """
    Create a comparison grid from multiple videos.

    Args:
        video_paths: List of video file paths
        labels: List of labels for each video
        output_path: Output grid video path
        layout: Grid layout (e.g., '2x2', '2x3')
        ffmpeg_path: Path to ffmpeg

    Returns:
        True if successful
    """
    try:
        rows, cols = map(int, layout.split('x'))
        expected_count = rows * cols

        if len(video_paths) > expected_count:
            logger.warning(f"Grid layout {layout} supports {expected_count} videos, "
                          f"but {len(video_paths)} provided. Using first {expected_count}.")
            video_paths = video_paths[:expected_count]
            labels = labels[:expected_count]

        # Build ffmpeg filter for grid
        # Add text labels to each video
        labeled_streams = []
        inputs = []

        for i, (path, label) in enumerate(zip(video_paths, labels)):
            inputs.extend(["-i", str(path)])
            # Add text overlay
            labeled_streams.append(
                f"[{i}:v]drawtext=text='{label}':fontsize=24:fontcolor=white:"
                f"box=1:boxcolor=black@0.5:boxborderw=5:x=10:y=10[v{i}]"
            )

        # Build grid layout
        if layout == '2x2':
            filter_complex = ";".join(labeled_streams) + \
                            f";[v0][v1]hstack[top];[v2][v3]hstack[bottom];[top][bottom]vstack[v]"
        elif layout == '2x3':
            filter_complex = ";".join(labeled_streams) + \
                            f";[v0][v1][v2]hstack=inputs=3[top];[v3][v4][v5]hstack=inputs=3[bottom];" \
                            f"[top][bottom]vstack[v]"
        elif layout == '1x4':
            filter_complex = ";".join(labeled_streams) + \
                            f";[v0][v1][v2][v3]hstack=inputs=4[v]"
        elif layout == '4x1':
            filter_complex = ";".join(labeled_streams) + \
                            f";[v0][v1][v2][v3]vstack=inputs=4[v]"
        else:
            logger.error(f"Unsupported grid layout: {layout}")
            return False

        cmd = [
            ffmpeg_path,
            *inputs,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "fast",
            "-y",
            str(output_path)
        ]

        logger.info(f"Creating comparison grid ({layout})")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Grid creation failed: {result.stderr}")
            return False

        return True

    except Exception as e:
        logger.error(f"Failed to create comparison grid: {e}")
        return False


def load_config(config_path: Path) -> dict:
    """Load configuration from YAML file."""
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


def handle_multi_clip_comparison(args: argparse.Namespace, presets: List[str],
                                 file_config: dict, ffmpeg_path: str) -> int:
    """
    Handle multi-clip comparison mode using the comparison module.

    This mode extracts multiple clips from different positions in the video
    and processes each with all specified presets, creating a comprehensive
    comparison suite.

    Args:
        args: Parsed command-line arguments
        presets: List of preset names to test
        file_config: Configuration loaded from file
        ffmpeg_path: Path to ffmpeg executable

    Returns:
        Exit code (0 = success, 1 = error)
    """
    logger.info("Multi-clip comparison mode enabled")

    # Parse custom timestamps if provided
    timestamps = None
    if args.timestamps:
        try:
            timestamps = [float(t.strip()) for t in args.timestamps.split(',')]
            logger.info(f"Using custom timestamps: {timestamps}")
        except ValueError as e:
            logger.error(f"Invalid timestamps format: {e}")
            return 1

    # Create comparison configuration
    comparison_config = ComparisonConfig(
        input_path=args.input,
        output_dir=args.output,
        presets=presets,
        clip_count=args.clip_count,
        clip_duration=int(args.duration),
        timestamps=timestamps,
        include_original=True,
        ffmpeg_path=ffmpeg_path,
        keep_individual_clips=args.keep_temp
    )

    # Generate comparison suite
    try:
        logger.info("Starting comprehensive preset comparison...")
        comparator = PresetComparator(comparison_config)
        comparisons = comparator.generate_comparison_suite()

        # Generate and save report
        report = comparator.generate_comparison_report(comparisons)
        report_path = args.output / "comparison_report.txt"
        report_path.write_text(report)

        print("\n" + report)

        return 0

    except Exception as e:
        logger.error(f"Multi-clip comparison failed: {e}", exc_info=args.verbose)
        return 1


def handle_test_presets(args: argparse.Namespace) -> int:
    """
    Handle the test-presets subcommand execution.

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

    # Create output folder
    args.output.mkdir(parents=True, exist_ok=True)

    # Parse presets to test
    if args.presets:
        presets_to_test = [p.strip() for p in args.presets.split(',')]
    else:
        presets_to_test = DEFAULT_TEST_PRESETS

    logger.info(f"Testing presets: {', '.join(presets_to_test)}")

    # Load config
    file_config = load_config(args.config)
    ffmpeg_path = file_config.get("ffmpeg_path", "ffmpeg")

    # Check if multi-clip mode is enabled
    if args.multi_clip:
        return handle_multi_clip_comparison(args, presets_to_test, file_config, ffmpeg_path)

    # Determine start time
    start_time = args.start
    if start_time is None:
        duration = get_video_duration(args.input, ffmpeg_path)
        if duration:
            start_time = duration * 0.25
            logger.info(f"Auto-selected start time: {start_time:.1f}s (25% through video)")
        else:
            start_time = 30.0
            logger.info(f"Using fallback start time: {start_time}s")

    # Extract source clip
    source_clip_path = args.output / "original.mp4"
    logger.info("Extracting source clip...")

    if not extract_clip(args.input, source_clip_path, start_time, args.duration, ffmpeg_path):
        logger.error("Failed to extract source clip")
        return 1

    logger.info(f"Source clip saved: {source_clip_path}")

    # Process with each preset
    processed_videos = []
    preset_labels = []
    success_count = 0
    failed_count = 0

    for i, preset in enumerate(presets_to_test, 1):
        logger.info(f"[{i}/{len(presets_to_test)}] Testing preset: {preset}")

        output_preset_path = args.output / f"preset_{preset}.mp4"

        # Build config for this preset
        config = ProcessingConfig(
            maxine_path=file_config.get("maxine_path", ""),
            model_dir=file_config.get("model_dir", ""),
            ffmpeg_path=ffmpeg_path,
            resolution=args.resolution,
            quality_mode=args.quality,
            crf=args.crf,
            preset=preset,
            encoder=args.encoder,
            keep_temp=args.keep_temp,
            skip_maxine=args.skip_maxine,
            upscale_engine=args.engine,
            realesrgan_path=file_config.get("realesrgan_path", ""),
            realesrgan_model=args.realesrgan_model,
            hdr_mode=args.hdr,
            audio_enhance="none",  # Skip audio for test clips
            audio_upmix="none",
            audio_layout="original",
            audio_format="aac",
            audio_bitrate="192k",
            audio_normalize=True,
        )

        # Apply preset
        if hasattr(VHSUpscaler, 'PRESETS') and preset in VHSUpscaler.PRESETS:
            preset_dict = VHSUpscaler.PRESETS[preset]
            config.deinterlace = preset_dict.get("deinterlace", config.deinterlace)
            config.denoise = preset_dict.get("denoise", config.denoise)
            config.denoise_strength = preset_dict.get("denoise_strength", config.denoise_strength)
            config.quality_mode = preset_dict.get("quality_mode", config.quality_mode)

        # Process
        try:
            upscaler = VHSUpscaler(config)
            success = upscaler.process(str(source_clip_path), output_preset_path)

            if success:
                success_count += 1
                logger.info(f"  Saved: {output_preset_path.name}")
                processed_videos.append(output_preset_path)
                preset_labels.append(preset.upper())
            else:
                failed_count += 1
                logger.error(f"  Processing failed")

        except Exception as e:
            failed_count += 1
            logger.error(f"  Error: {e}", exc_info=args.verbose)

    # Create comparison grid if requested
    if args.create_grid and processed_videos:
        logger.info("Creating comparison grid...")

        # Add original to grid
        all_videos = [source_clip_path] + processed_videos
        all_labels = ['ORIGINAL'] + preset_labels

        grid_output = args.output / "comparison_grid.mp4"

        if create_comparison_grid(all_videos, all_labels, grid_output,
                                 args.grid_layout, ffmpeg_path):
            logger.info(f"Comparison grid saved: {grid_output}")
        else:
            logger.error("Failed to create comparison grid")

    # Summary
    print("\n" + "=" * 60)
    print("PRESET TEST COMPLETE")
    print("=" * 60)
    print(f"Presets tested:   {len(presets_to_test)}")
    print(f"Successful:       {success_count}")
    print(f"Failed:           {failed_count}")
    print(f"Output folder:    {args.output}")
    print("\nGenerated files:")
    print(f"  - original.mp4 (source clip)")
    for preset in presets_to_test:
        preset_file = args.output / f"preset_{preset}.mp4"
        if preset_file.exists():
            print(f"  - preset_{preset}.mp4")
    if args.create_grid:
        grid_file = args.output / "comparison_grid.mp4"
        if grid_file.exists():
            print(f"  - comparison_grid.mp4")

    return 0 if failed_count == 0 else 1
