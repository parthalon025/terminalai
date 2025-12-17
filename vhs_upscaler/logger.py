"""
Logging Configuration for VHS Upscaler
======================================
Provides verbose logging with file output and colored console output.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import threading


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def format(self, record):
        # Add color to level name
        color = self.COLORS.get(record.levelname, '')
        record.levelname_colored = f"{color}{record.levelname:8}{self.RESET}"

        # Format the message
        formatted = super().format(record)
        return formatted


class VHSLogger:
    """
    Centralized logging for VHS Upscaler pipeline.

    Features:
    - Console output with colors
    - File logging with rotation
    - Stage-specific logging
    - Performance metrics
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,
                 log_dir: Optional[Path] = None,
                 console_level: int = logging.INFO,
                 file_level: int = logging.DEBUG,
                 log_to_file: bool = True):

        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        self.console_level = console_level
        self.file_level = file_level
        self.log_to_file = log_to_file

        # Create logger
        self.logger = logging.getLogger("vhs_upscaler")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers = []  # Clear existing handlers

        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_format = ColoredFormatter(
            '%(asctime)s │ %(levelname_colored)s │ %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

        # File handler
        if log_to_file:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            log_file = self.log_dir / f"vhs_upscaler_{datetime.now():%Y%m%d_%H%M%S}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(file_level)
            file_format = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
            self.log_file = log_file
        else:
            self.log_file = None

        # Stage timing
        self.stage_times = {}
        self.current_stage = None
        self.stage_start = None

    def set_level(self, level: int):
        """Set console logging level."""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(level)

    def start_stage(self, stage_name: str):
        """Mark the start of a processing stage."""
        self.current_stage = stage_name
        self.stage_start = datetime.now()
        self.logger.info(f"{'─' * 50}")
        self.logger.info(f"▶ Starting: {stage_name}")
        self.logger.debug(f"Stage '{stage_name}' started at {self.stage_start}")

    def end_stage(self, stage_name: str = None):
        """Mark the end of a processing stage."""
        stage = stage_name or self.current_stage
        if stage and self.stage_start:
            duration = (datetime.now() - self.stage_start).total_seconds()
            self.stage_times[stage] = duration
            self.logger.info(f"✓ Completed: {stage} ({duration:.2f}s)")
            self.logger.debug(f"Stage '{stage}' completed in {duration:.2f} seconds")
        self.current_stage = None
        self.stage_start = None

    def log_config(self, config: dict):
        """Log configuration settings."""
        self.logger.info("Configuration:")
        for key, value in config.items():
            self.logger.info(f"  {key}: {value}")

    def log_video_info(self, info: dict):
        """Log video metadata."""
        self.logger.info("Video Information:")
        for key in ['title', 'duration', 'resolution', 'codec', 'fps']:
            if key in info:
                self.logger.info(f"  {key}: {info[key]}")

    def log_progress(self, stage: str, percent: float, detail: str = ""):
        """Log progress update (debug level)."""
        msg = f"[{stage}] {percent:.1f}%"
        if detail:
            msg += f" - {detail}"
        self.logger.debug(msg)

    def log_command(self, cmd: list):
        """Log external command execution."""
        cmd_str = ' '.join(str(c) for c in cmd)
        self.logger.debug(f"Executing: {cmd_str}")

    def log_summary(self):
        """Log processing summary with timing."""
        self.logger.info("=" * 50)
        self.logger.info("Processing Summary:")
        total_time = sum(self.stage_times.values())
        for stage, duration in self.stage_times.items():
            pct = (duration / total_time * 100) if total_time > 0 else 0
            self.logger.info(f"  {stage}: {duration:.2f}s ({pct:.1f}%)")
        self.logger.info(f"  Total: {total_time:.2f}s")
        self.logger.info("=" * 50)

    def debug(self, msg: str): self.logger.debug(msg)
    def info(self, msg: str): self.logger.info(msg)
    def warning(self, msg: str): self.logger.warning(msg)
    def error(self, msg: str): self.logger.error(msg)
    def critical(self, msg: str): self.logger.critical(msg)


def get_logger(log_dir: Optional[Path] = None,
               verbose: bool = False,
               log_to_file: bool = True) -> VHSLogger:
    """Get or create the singleton logger instance."""
    level = logging.DEBUG if verbose else logging.INFO
    return VHSLogger(
        log_dir=log_dir,
        console_level=level,
        log_to_file=log_to_file
    )
