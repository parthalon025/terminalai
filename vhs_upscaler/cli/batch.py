"""
Batch subcommand - Process multiple videos sequentially.

This subcommand discovers all video files in a directory and processes them
sequentially with the same settings. Results are saved to an output directory
with consistent naming.

Usage:
    vhs-upscale batch input_folder/ output_folder/
    vhs-upscale batch input_folder/ output_folder/ -p vhs -r 2160
    vhs-upscale batch input_folder/ output_folder/ --pattern "*.avi"
"""

import argparse
import logging
import sys
import concurrent.futures
import time
from pathlib import Path
from typing import List, Optional, Tuple

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
)

logger = logging.getLogger(__name__)


# Common video file extensions
VIDEO_EXTENSIONS = {
    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
    '.m4v', '.mpg', '.mpeg', '.m2v', '.3gp', '.3g2', '.mxf',
    '.MP4', '.AVI', '.MKV', '.MOV', '.WMV', '.FLV', '.WEBM',
}


def setup_batch_parser(subparsers) -> argparse.ArgumentParser:
    """
    Create and configure the batch subcommand parser.

    Args:
        subparsers: Subparsers object from main argument parser

    Returns:
        Configured ArgumentParser for batch subcommand
    """
    parser = subparsers.add_parser(
        'batch',
        help='Process multiple videos in a folder sequentially',
        description="""
Batch process all videos in a folder with consistent settings.

This command discovers all video files in the input folder, processes them
sequentially, and saves results to the output folder. Each output file is
named based on the input filename with resolution suffix.

Supported formats: MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V, MPG, MPEG, etc.

Note: This is sequential processing. For parallel batch processing, use
the 'parallel-batch' command (Sprint 2).
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic batch processing:
    vhs-upscale batch ./input_videos/ ./output_videos/

  Process all VHS tapes to 4K:
    vhs-upscale batch ./vhs_tapes/ ./restored/ -p vhs -r 2160

  Process only AVI files:
    vhs-upscale batch ./input/ ./output/ --pattern "*.avi"

  Process with custom naming:
    vhs-upscale batch ./input/ ./output/ --suffix "restored"

  Skip existing outputs:
    vhs-upscale batch ./input/ ./output/ --skip-existing

  Resume interrupted batch:
    vhs-upscale batch ./input/ ./output/ --resume
        """
    )

    # Required arguments
    parser.add_argument(
        'input_folder',
        type=Path,
        help='Input folder containing video files'
    )

    parser.add_argument(
        'output_folder',
        type=Path,
        help='Output folder for processed videos'
    )

    # Batch-specific options
    batch_group = parser.add_argument_group(
        'Batch Options',
        'Control batch processing behavior'
    )

    batch_group.add_argument(
        '--pattern',
        default='*',
        help='File pattern for video discovery (e.g., "*.mp4", "*.avi") (default: all video files)'
    )

    batch_group.add_argument(
        '--recursive',
        action='store_true',
        help='Search for videos recursively in subfolders'
    )

    batch_group.add_argument(
        '--skip-existing',
        action='store_true',
        help='Skip videos that already have output files'
    )

    batch_group.add_argument(
        '--resume',
        action='store_true',
        help='Resume interrupted batch (skip existing outputs)'
    )

    batch_group.add_argument(
        '--suffix',
        default=None,
        help='Custom suffix for output files (default: resolution, e.g., "1080p")'
    )

    batch_group.add_argument(
        '--max-count',
        type=int,
        default=None,
        help='Maximum number of videos to process (for testing)'
    )

    batch_group.add_argument(
        '--parallel',
        type=int,
        default=1,
        help='Number of videos to process in parallel (default: 1 = sequential)'
    )

    # Add standard argument groups
    add_upscale_arguments(parser)
    add_processing_arguments(parser)
    add_audio_arguments(parser)
    add_advanced_arguments(parser)
    add_common_arguments(parser)

    return parser


def discover_videos(input_folder: Path, pattern: str = '*',
                    recursive: bool = False) -> List[Path]:
    """
    Discover video files in folder.

    Args:
        input_folder: Folder to search
        pattern: Glob pattern for files
        recursive: Search recursively

    Returns:
        List of video file paths
    """
    videos = []

    if recursive:
        glob_pattern = f"**/{pattern}"
    else:
        glob_pattern = pattern

    for path in input_folder.glob(glob_pattern):
        if path.is_file() and path.suffix in VIDEO_EXTENSIONS:
            videos.append(path)

    return sorted(videos)  # Sort for consistent order


def generate_output_path(input_path: Path, output_folder: Path,
                        resolution: int, suffix: Optional[str] = None) -> Path:
    """
    Generate output path for processed video.

    Args:
        input_path: Input video path
        output_folder: Output folder
        resolution: Target resolution
        suffix: Custom suffix (overrides resolution)

    Returns:
        Output path
    """
    if suffix:
        output_name = f"{input_path.stem}_{suffix}.mp4"
    else:
        output_name = f"{input_path.stem}_{resolution}p.mp4"

    return output_folder / output_name


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


def _process_video_job(args: Tuple[int, Path, Path, VHSUpscaler, bool]) -> Tuple[bool, str, str]:
    """
    Process a single video (worker function for parallel processing).

    Args:
        args: Tuple of (index, video_path, output_path, upscaler, verbose)

    Returns:
        Tuple of (success, video_name, error_message)
    """
    index, video, output_path, upscaler, verbose = args

    video_name = video.name
    start_time = time.time()

    try:
        logger.info(f"[{index}] Starting: {video_name}")
        success = upscaler.process(str(video), output_path)
        elapsed = time.time() - start_time

        if success:
            logger.info(f"[{index}] Completed: {video_name} ({elapsed:.1f}s)")
            return (True, video_name, "")
        else:
            logger.error(f"[{index}] Failed: {video_name}")
            return (False, video_name, "Processing failed")

    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = str(e)
        logger.error(f"[{index}] Error: {video_name} - {error_msg}", exc_info=verbose)
        return (False, video_name, error_msg)


def _process_parallel(videos: List[Path], output_folder: Path, resolution: int,
                      suffix: Optional[str], upscaler: VHSUpscaler,
                      max_workers: int, verbose: bool) -> Tuple[int, int]:
    """
    Process videos in parallel using ThreadPoolExecutor.

    Args:
        videos: List of video paths
        output_folder: Output folder
        resolution: Target resolution
        suffix: Custom suffix
        upscaler: Upscaler instance
        max_workers: Number of parallel workers
        verbose: Verbose logging

    Returns:
        Tuple of (success_count, failed_count)
    """
    success_count = 0
    failed_count = 0

    # Prepare jobs
    jobs = []
    for i, video in enumerate(videos, 1):
        output_path = generate_output_path(video, output_folder, resolution, suffix)
        jobs.append((i, video, output_path, upscaler, verbose))

    # Process with ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        futures = {executor.submit(_process_video_job, job): job for job in jobs}

        # Process completions as they finish
        for future in concurrent.futures.as_completed(futures):
            job = futures[future]
            index, video, output_path, _, _ = job

            try:
                success, video_name, error_msg = future.result()

                if success:
                    success_count += 1
                    print(f"[{index}/{len(videos)}] SUCCESS: {video_name}")
                else:
                    failed_count += 1
                    print(f"[{index}/{len(videos)}] FAILED: {video_name}")
                    if error_msg:
                        print(f"  Error: {error_msg}")

            except Exception as e:
                failed_count += 1
                print(f"[{index}/{len(videos)}] FAILED: {video.name} - {str(e)}")

            print("-" * 60)

    return success_count, failed_count


def handle_batch(args: argparse.Namespace) -> int:
    """
    Handle the batch subcommand execution.

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

    # Validate input folder
    if not args.input_folder.exists():
        logger.error(f"Input folder not found: {args.input_folder}")
        return 1

    if not args.input_folder.is_dir():
        logger.error(f"Input path is not a folder: {args.input_folder}")
        return 1

    # Create output folder if needed
    args.output_folder.mkdir(parents=True, exist_ok=True)

    # Discover videos
    logger.info(f"Discovering videos in: {args.input_folder}")
    videos = discover_videos(args.input_folder, args.pattern, args.recursive)

    if not videos:
        logger.error(f"No video files found matching pattern: {args.pattern}")
        return 1

    logger.info(f"Found {len(videos)} video file(s)")

    # Apply max count if specified
    if args.max_count:
        videos = videos[:args.max_count]
        logger.info(f"Limited to {len(videos)} video(s) (--max-count)")

    # Filter existing if resume/skip-existing
    if args.resume or args.skip_existing:
        filtered_videos = []
        for video in videos:
            output_path = generate_output_path(
                video, args.output_folder, args.resolution, args.suffix
            )
            if not output_path.exists():
                filtered_videos.append(video)
            else:
                logger.info(f"Skipping (exists): {video.name} -> {output_path.name}")

        videos = filtered_videos
        logger.info(f"{len(videos)} video(s) remaining after filtering")

        if not videos:
            logger.info("All videos already processed")
            return 0

    # Dry run - just list what would be processed
    if args.dry_run:
        print("\nVideos to process:")
        print("=" * 60)
        for i, video in enumerate(videos, 1):
            output_path = generate_output_path(
                video, args.output_folder, args.resolution, args.suffix
            )
            print(f"{i:3d}. {video.name}")
            print(f"      -> {output_path.name}")
        print(f"\nTotal: {len(videos)} video(s)")
        return 0

    # Build processing config
    file_config = load_config(args.config)

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

    # Create upscaler
    try:
        upscaler = VHSUpscaler(config)
    except RuntimeError as e:
        logger.error(f"Failed to initialize upscaler: {e}")
        return 1

    # Process videos (sequential or parallel)
    success_count = 0
    failed_count = 0

    logger.info(f"\nStarting batch processing ({len(videos)} videos)")
    if args.parallel > 1:
        logger.info(f"Parallel mode: {args.parallel} workers")
    print("=" * 60)

    if args.parallel > 1:
        # Parallel processing
        success_count, failed_count = _process_parallel(
            videos, args.output_folder, args.resolution, args.suffix,
            upscaler, args.parallel, args.verbose
        )
    else:
        # Sequential processing
        for i, video in enumerate(videos, 1):
            output_path = generate_output_path(
                video, args.output_folder, args.resolution, args.suffix
            )

            logger.info(f"[{i}/{len(videos)}] Processing: {video.name}")
            logger.info(f"  Output: {output_path.name}")

            try:
                success = upscaler.process(str(video), output_path)
                if success:
                    success_count += 1
                    logger.info(f"  Success")
                else:
                    failed_count += 1
                    logger.error(f"  Failed")

            except KeyboardInterrupt:
                logger.warning("\nBatch processing interrupted by user")
                break
            except Exception as e:
                failed_count += 1
                logger.error(f"  Error: {e}", exc_info=args.verbose)

            print("-" * 60)

    # Summary
    print("\n" + "=" * 60)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Total videos: {len(videos)}")
    print(f"Successful:   {success_count}")
    print(f"Failed:       {failed_count}")
    print(f"Output:       {args.output_folder}")

    return 0 if failed_count == 0 else 1
