#!/usr/bin/env python3
"""
Watch Folder Automation for TerminalAI

Monitors input directories for new video files and automatically processes them
with configurable presets. Supports multiple watch folders with different settings.

Usage:
    python scripts/watch_folder.py --config watch_config.yaml
    python scripts/watch_folder.py --input ~/Videos/to_process --output ~/Videos/processed --preset vhs

Features:
    - Real-time file monitoring with watchdog
    - Configurable processing presets per folder
    - Automatic move to output directory on completion
    - Error handling and retry logic
    - YAML configuration support
    - Multiple watch folder support
    - File pattern filtering (*.mp4, *.avi, etc.)
    - Graceful shutdown on Ctrl+C
"""

import argparse
import logging
import os
import sys
import time
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
except ImportError:
    print("ERROR: watchdog package not found. Install with: pip install watchdog")
    sys.exit(1)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vhs_upscaler.queue_manager import VideoQueue, QueueJob
from vhs_upscaler.logger import get_logger

logger = get_logger(__name__)


@dataclass
class WatchFolderConfig:
    """Configuration for a single watch folder."""

    input_dir: str
    output_dir: str
    preset: str = "vhs"
    patterns: List[str] = field(default_factory=lambda: ["*.mp4", "*.avi", "*.mkv", "*.mov"])
    resolution: int = 1080
    move_on_complete: bool = True
    delete_on_complete: bool = False
    retry_on_error: bool = True
    max_retries: int = 3

    # Advanced options (optional)
    encoder: Optional[str] = None
    crf: Optional[int] = None
    deinterlace: Optional[str] = None
    denoise: Optional[str] = None
    face_restore: bool = False
    audio_enhance: Optional[str] = None
    audio_upmix: Optional[str] = None

    def __post_init__(self):
        """Validate and normalize paths."""
        self.input_dir = os.path.abspath(os.path.expanduser(self.input_dir))
        self.output_dir = os.path.abspath(os.path.expanduser(self.output_dir))

        # Create directories if they don't exist
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)


class VideoFileHandler(FileSystemEventHandler):
    """Handles file system events for video files."""

    VIDEO_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".m4v", ".mpg", ".mpeg", ".wmv", ".flv"}

    def __init__(self, config: WatchFolderConfig, queue: VideoQueue):
        """
        Initialize the file handler.

        Args:
            config: Watch folder configuration
            queue: Video processing queue
        """
        super().__init__()
        self.config = config
        self.queue = queue
        self.processing_files: Set[str] = set()
        self.completed_files: Set[str] = set()
        self.failed_files: Dict[str, int] = {}  # filepath -> retry_count

        logger.info(f"Watching: {config.input_dir}")
        logger.info(f"Output: {config.output_dir}")
        logger.info(f"Preset: {config.preset}")

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return

        filepath = event.src_path

        # Check if it's a video file
        if not self._is_video_file(filepath):
            return

        # Wait for file to be fully written (avoid processing incomplete files)
        if not self._wait_for_file_ready(filepath):
            logger.warning(f"File not ready or disappeared: {filepath}")
            return

        # Check if already processed or in progress
        if filepath in self.processing_files or filepath in self.completed_files:
            logger.debug(f"Skipping already processed file: {filepath}")
            return

        logger.info(f"New video detected: {os.path.basename(filepath)}")
        self._process_video(filepath)

    def _is_video_file(self, filepath: str) -> bool:
        """Check if file is a video based on extension."""
        ext = os.path.splitext(filepath)[1].lower()
        return ext in self.VIDEO_EXTENSIONS

    def _wait_for_file_ready(self, filepath: str, timeout: int = 30) -> bool:
        """
        Wait for file to be fully written (file size stabilizes).

        Args:
            filepath: Path to file
            timeout: Maximum wait time in seconds

        Returns:
            True if file is ready, False otherwise
        """
        start_time = time.time()
        last_size = -1
        stable_count = 0

        while time.time() - start_time < timeout:
            try:
                if not os.path.exists(filepath):
                    return False

                current_size = os.path.getsize(filepath)

                if current_size == last_size:
                    stable_count += 1
                    if stable_count >= 3:  # Stable for 3 checks (3 seconds)
                        return True
                else:
                    stable_count = 0
                    last_size = current_size

                time.sleep(1)
            except (OSError, IOError):
                time.sleep(1)
                continue

        return False

    def _process_video(self, filepath: str):
        """
        Add video to processing queue.

        Args:
            filepath: Path to video file
        """
        try:
            self.processing_files.add(filepath)

            # Generate output filename
            basename = os.path.basename(filepath)
            name, ext = os.path.splitext(basename)
            output_filename = f"{name}_processed{ext}"
            output_path = os.path.join(self.config.output_dir, output_filename)

            # Build job arguments
            job_args = {
                "input_file": filepath,
                "output_file": output_path,
                "preset": self.config.preset,
                "resolution": self.config.resolution,
            }

            # Add optional advanced settings
            if self.config.encoder:
                job_args["encoder"] = self.config.encoder
            if self.config.crf is not None:
                job_args["crf"] = self.config.crf
            if self.config.deinterlace:
                job_args["deinterlace"] = self.config.deinterlace
            if self.config.denoise:
                job_args["denoise"] = self.config.denoise
            if self.config.face_restore:
                job_args["face_restore"] = True
            if self.config.audio_enhance:
                job_args["audio_enhance"] = self.config.audio_enhance
            if self.config.audio_upmix:
                job_args["audio_upmix"] = self.config.audio_upmix

            # Add to queue
            job = self.queue.add_job(**job_args)
            logger.info(f"Added to queue: {basename} (Job ID: {job.id})")

            # Monitor job completion
            self._monitor_job(job, filepath)

        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")
            self.processing_files.discard(filepath)

    def _monitor_job(self, job: QueueJob, filepath: str):
        """
        Monitor job completion and handle post-processing.

        Args:
            job: Queue job to monitor
            filepath: Original input file path
        """
        # This will be called by the queue's completion callback
        # For now, just mark as completed
        # TODO: Implement proper callback system
        pass

    def on_job_complete(self, job: QueueJob, filepath: str):
        """
        Handle job completion.

        Args:
            job: Completed job
            filepath: Original input file path
        """
        self.processing_files.discard(filepath)

        if job.status.name == "COMPLETED":
            logger.info(f"✓ Processing complete: {os.path.basename(filepath)}")
            self.completed_files.add(filepath)

            # Move or delete original file
            if self.config.delete_on_complete:
                try:
                    os.remove(filepath)
                    logger.info(f"Deleted original: {os.path.basename(filepath)}")
                except Exception as e:
                    logger.error(f"Error deleting {filepath}: {e}")
            elif self.config.move_on_complete:
                completed_dir = os.path.join(self.config.input_dir, "_completed")
                os.makedirs(completed_dir, exist_ok=True)
                try:
                    dest_path = os.path.join(completed_dir, os.path.basename(filepath))
                    os.rename(filepath, dest_path)
                    logger.info(f"Moved original to: {completed_dir}")
                except Exception as e:
                    logger.error(f"Error moving {filepath}: {e}")
        else:
            # Job failed
            logger.error(f"✗ Processing failed: {os.path.basename(filepath)}")
            retry_count = self.failed_files.get(filepath, 0)

            if self.config.retry_on_error and retry_count < self.config.max_retries:
                self.failed_files[filepath] = retry_count + 1
                logger.info(f"Retrying ({retry_count + 1}/{self.config.max_retries})...")
                time.sleep(5)  # Wait before retry
                self._process_video(filepath)
            else:
                # Move to failed directory
                failed_dir = os.path.join(self.config.input_dir, "_failed")
                os.makedirs(failed_dir, exist_ok=True)
                try:
                    dest_path = os.path.join(failed_dir, os.path.basename(filepath))
                    os.rename(filepath, dest_path)
                    logger.error(f"Moved failed file to: {failed_dir}")
                except Exception as e:
                    logger.error(f"Error moving failed file {filepath}: {e}")


class WatchFolderManager:
    """Manages multiple watch folders."""

    def __init__(self, configs: List[WatchFolderConfig]):
        """
        Initialize the watch folder manager.

        Args:
            configs: List of watch folder configurations
        """
        self.configs = configs
        self.queue = VideoQueue()
        self.observers: List[Observer] = []
        self.handlers: List[VideoFileHandler] = []

    def start(self):
        """Start watching all configured folders."""
        logger.info(f"Starting watch folder manager with {len(self.configs)} folder(s)")

        for config in self.configs:
            observer = Observer()
            handler = VideoFileHandler(config, self.queue)

            observer.schedule(handler, config.input_dir, recursive=False)
            observer.start()

            self.observers.append(observer)
            self.handlers.append(handler)

            logger.info(f"✓ Watching: {config.input_dir}")

        logger.info("Watch folder manager started. Press Ctrl+C to stop.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping watch folder manager...")
            self.stop()

    def stop(self):
        """Stop watching all folders."""
        for observer in self.observers:
            observer.stop()
            observer.join()

        logger.info("Watch folder manager stopped.")

    def process_existing_files(self):
        """Process any existing files in watch folders (one-time scan)."""
        logger.info("Scanning for existing files...")

        for config, handler in zip(self.configs, self.handlers):
            for filename in os.listdir(config.input_dir):
                filepath = os.path.join(config.input_dir, filename)

                if os.path.isfile(filepath) and handler._is_video_file(filepath):
                    logger.info(f"Found existing file: {filename}")
                    handler._process_video(filepath)


def load_config(config_file: str) -> List[WatchFolderConfig]:
    """
    Load watch folder configurations from YAML file.

    Args:
        config_file: Path to YAML config file

    Returns:
        List of WatchFolderConfig objects
    """
    with open(config_file, 'r') as f:
        data = yaml.safe_load(f)

    configs = []
    for folder_config in data.get('watch_folders', []):
        configs.append(WatchFolderConfig(**folder_config))

    return configs


def create_example_config(output_path: str):
    """Create an example configuration file."""
    example_config = {
        'watch_folders': [
            {
                'input_dir': '~/Videos/vhs_to_process',
                'output_dir': '~/Videos/vhs_processed',
                'preset': 'vhs',
                'resolution': 1080,
                'move_on_complete': True,
                'delete_on_complete': False,
                'retry_on_error': True,
                'max_retries': 3,
                'face_restore': True,
                'audio_enhance': 'voice',
                'audio_upmix': 'demucs',
            },
            {
                'input_dir': '~/Videos/youtube_to_process',
                'output_dir': '~/Videos/youtube_processed',
                'preset': 'youtube',
                'resolution': 1080,
                'move_on_complete': True,
            }
        ]
    }

    with open(output_path, 'w') as f:
        yaml.dump(example_config, f, default_flow_style=False, indent=2)

    logger.info(f"Created example config: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Watch folders for new videos and automatically process them",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Watch folder with config file
  python scripts/watch_folder.py --config watch_config.yaml

  # Watch single folder
  python scripts/watch_folder.py --input ~/Videos/to_process --output ~/Videos/processed --preset vhs

  # Process existing files then watch
  python scripts/watch_folder.py --config watch_config.yaml --process-existing

  # Generate example config
  python scripts/watch_folder.py --create-config watch_config.yaml
        """
    )

    parser.add_argument('--config', '-c', help='YAML configuration file')
    parser.add_argument('--input', '-i', help='Input directory to watch')
    parser.add_argument('--output', '-o', help='Output directory for processed videos')
    parser.add_argument('--preset', '-p', default='vhs', help='Processing preset (default: vhs)')
    parser.add_argument('--resolution', '-r', type=int, default=1080, help='Output resolution (default: 1080)')
    parser.add_argument('--process-existing', action='store_true', help='Process existing files before watching')
    parser.add_argument('--create-config', help='Create example config file and exit')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create example config if requested
    if args.create_config:
        create_example_config(args.create_config)
        return

    # Load configurations
    configs = []

    if args.config:
        if not os.path.exists(args.config):
            logger.error(f"Config file not found: {args.config}")
            sys.exit(1)
        configs = load_config(args.config)
    elif args.input and args.output:
        configs = [WatchFolderConfig(
            input_dir=args.input,
            output_dir=args.output,
            preset=args.preset,
            resolution=args.resolution
        )]
    else:
        parser.print_help()
        logger.error("\nError: Either --config or both --input and --output are required")
        sys.exit(1)

    if not configs:
        logger.error("No watch folders configured")
        sys.exit(1)

    # Start manager
    manager = WatchFolderManager(configs)

    if args.process_existing:
        manager.process_existing_files()

    manager.start()


if __name__ == "__main__":
    main()
