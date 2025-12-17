#!/usr/bin/env python3
"""
VHS Video Upscaling Pipeline
============================
AI-powered video upscaling optimized for VHS-quality footage using NVIDIA Maxine SDK.

Features:
- Watch folder automation
- Pre-processing: deinterlace, denoise, audio extraction
- AI upscaling via NVIDIA Maxine SuperRes
- Post-processing: NVENC encoding, audio remux
- Configurable presets for VHS, DVD, webcam sources

Usage:
    python vhs_upscale.py --input video.mp4 --output upscaled.mp4
    python vhs_upscale.py --watch --input ./input --output ./output
    python vhs_upscale.py --preset vhs --resolution 1080 --input video.mp4
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
import yaml
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingConfig:
    """Configuration for video processing pipeline."""
    maxine_path: str = ""
    model_dir: str = ""
    ffmpeg_path: str = "ffmpeg"
    resolution: int = 1080
    quality_mode: int = 0  # 0 = best quality, 1 = performance
    crf: int = 20
    preset: str = "vhs"
    deinterlace: bool = True
    denoise: bool = True
    denoise_strength: tuple = (3, 2, 3, 2)  # hqdn3d parameters
    encoder: str = "hevc_nvenc"
    nvenc_preset: str = "p7"
    keep_temp: bool = False


class ProgressTracker:
    """Track and display processing progress."""

    def __init__(self, total_files: int = 1):
        self.total_files = total_files
        self.current_file = 0
        self.current_stage = ""
        self.stage_progress = 0.0
        self.start_time = time.time()
        self.file_start_time = time.time()

    def set_stage(self, stage: str, file_num: int = None):
        self.current_stage = stage
        self.stage_progress = 0.0
        if file_num:
            self.current_file = file_num
            self.file_start_time = time.time()
        self._display()

    def update(self, progress: float):
        self.stage_progress = min(progress, 100.0)
        self._display()

    def _display(self):
        elapsed = time.time() - self.file_start_time
        eta = self._estimate_eta(elapsed)
        bar_width = 30
        filled = int(bar_width * self.stage_progress / 100)
        bar = "█" * filled + "░" * (bar_width - filled)

        status = f"\r[{self.current_file}/{self.total_files}] {self.current_stage}: [{bar}] {self.stage_progress:.1f}%"
        if eta:
            status += f" | ETA: {eta}"
        print(status, end="", flush=True)

    def _estimate_eta(self, elapsed: float) -> str:
        if self.stage_progress <= 0:
            return ""
        remaining = (elapsed / self.stage_progress) * (100 - self.stage_progress)
        return str(timedelta(seconds=int(remaining)))

    def complete_stage(self):
        self.stage_progress = 100.0
        self._display()
        print()  # New line


class VHSUpscaler:
    """Main upscaling pipeline orchestrator."""

    PRESETS = {
        "vhs": {
            "deinterlace": True,
            "denoise": True,
            "denoise_strength": (3, 2, 3, 2),
            "quality_mode": 0,
        },
        "dvd": {
            "deinterlace": True,
            "denoise": True,
            "denoise_strength": (2, 1, 2, 1),
            "quality_mode": 0,
        },
        "webcam": {
            "deinterlace": False,
            "denoise": True,
            "denoise_strength": (4, 3, 4, 3),
            "quality_mode": 1,
        },
        "clean": {
            "deinterlace": False,
            "denoise": False,
            "quality_mode": 0,
        }
    }

    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.progress = ProgressTracker()
        self._validate_dependencies()

    def _validate_dependencies(self):
        """Verify all required tools are available."""
        # Check FFmpeg
        try:
            result = subprocess.run(
                [self.config.ffmpeg_path, "-version"],
                capture_output=True, text=True, check=True
            )
            logger.debug(f"FFmpeg found: {result.stdout.split(chr(10))[0]}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("FFmpeg not found. Install from https://ffmpeg.org")

        # Check Maxine VideoEffectsApp
        maxine_exe = Path(self.config.maxine_path) / "VideoEffectsApp.exe"
        if not maxine_exe.exists():
            # Try environment variable
            maxine_home = os.environ.get("MAXINE_HOME", "")
            if maxine_home:
                maxine_exe = Path(maxine_home) / "bin" / "VideoEffectsApp.exe"
                if maxine_exe.exists():
                    self.config.maxine_path = str(Path(maxine_home) / "bin")
                    self.config.model_dir = str(Path(maxine_home) / "bin" / "models")

            if not maxine_exe.exists():
                raise RuntimeError(
                    f"NVIDIA Maxine VideoEffectsApp not found at {maxine_exe}\n"
                    "Run install.ps1 or set MAXINE_HOME environment variable."
                )
        logger.debug(f"Maxine SDK found: {maxine_exe}")

    def _get_video_info(self, input_path: Path) -> dict:
        """Extract video metadata using FFprobe."""
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            str(input_path)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            return json.loads(result.stdout)
        except Exception as e:
            logger.warning(f"Could not get video info: {e}")
            return {}

    def _is_interlaced(self, video_info: dict) -> bool:
        """Detect if video is interlaced."""
        for stream in video_info.get("streams", []):
            if stream.get("codec_type") == "video":
                field_order = stream.get("field_order", "progressive")
                return field_order not in ("progressive", "unknown")
        return False

    def preprocess(self, input_path: Path, temp_dir: Path) -> tuple[Path, Optional[Path]]:
        """
        Pre-process video: deinterlace, denoise, extract audio.

        Returns:
            Tuple of (processed_video_path, audio_path or None)
        """
        self.progress.set_stage("Pre-processing")

        video_out = temp_dir / "prepped_video.mp4"
        audio_out = temp_dir / "audio.aac"

        # Build video filter chain
        vf_filters = []

        if self.config.deinterlace:
            vf_filters.append("yadif=1")

        if self.config.denoise:
            ds = self.config.denoise_strength
            vf_filters.append(f"hqdn3d={ds[0]}:{ds[1]}:{ds[2]}:{ds[3]}")

        vf_string = ",".join(vf_filters) if vf_filters else "null"

        # Process video (without audio)
        video_cmd = [
            self.config.ffmpeg_path,
            "-y", "-i", str(input_path),
            "-vf", vf_string,
            "-an",  # No audio
            "-c:v", "libx264",
            "-crf", "15",  # High quality intermediate
            "-preset", "fast",
            "-progress", "pipe:1",
            str(video_out)
        ]

        logger.debug(f"Pre-process command: {' '.join(video_cmd)}")

        process = subprocess.Popen(
            video_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Monitor progress from FFmpeg
        duration = None
        for line in process.stdout:
            if "Duration:" in line:
                # Parse duration
                pass
            elif line.startswith("out_time_ms="):
                try:
                    ms = int(line.split("=")[1])
                    if duration:
                        self.progress.update((ms / 1000000) / duration * 100)
                except:
                    pass

        process.wait()
        if process.returncode != 0:
            stderr = process.stderr.read()
            raise RuntimeError(f"Pre-processing failed: {stderr}")

        # Extract audio
        audio_cmd = [
            self.config.ffmpeg_path,
            "-y", "-i", str(input_path),
            "-vn",  # No video
            "-c:a", "copy",
            str(audio_out)
        ]

        try:
            subprocess.run(audio_cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError:
            # No audio track or extraction failed
            audio_out = None
            logger.warning("No audio track extracted")

        self.progress.complete_stage()
        return video_out, audio_out if audio_out and audio_out.exists() else None

    def upscale(self, input_path: Path, temp_dir: Path) -> Path:
        """
        Apply NVIDIA Maxine SuperRes upscaling.
        """
        self.progress.set_stage("AI Upscaling (Maxine SuperRes)")

        output_path = temp_dir / "upscaled.mp4"
        maxine_exe = Path(self.config.maxine_path) / "VideoEffectsApp.exe"

        cmd = [
            str(maxine_exe),
            "--progress",
            "--effect=SuperRes",
            f"--mode={self.config.quality_mode}",
            f"--model_dir={self.config.model_dir}",
            f"--in_file={input_path}",
            f"--resolution={self.config.resolution}",
            f"--out_file={output_path}"
        ]

        logger.debug(f"Maxine command: {' '.join(cmd)}")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Parse Maxine progress output
        for line in process.stdout:
            line = line.strip()
            if "%" in line:
                try:
                    # Extract percentage from output
                    pct = float(line.split("%")[0].split()[-1])
                    self.progress.update(pct)
                except:
                    pass
            logger.debug(f"Maxine: {line}")

        process.wait()
        if process.returncode != 0:
            raise RuntimeError(f"Maxine upscaling failed with code {process.returncode}")

        if not output_path.exists():
            raise RuntimeError("Maxine did not produce output file")

        self.progress.complete_stage()
        return output_path

    def postprocess(self, video_path: Path, audio_path: Optional[Path], output_path: Path):
        """
        Post-process: remux audio, encode with NVENC.
        """
        self.progress.set_stage("Post-processing (NVENC encoding)")

        cmd = [
            self.config.ffmpeg_path,
            "-y",
            "-i", str(video_path),
        ]

        # Add audio input if available
        if audio_path and audio_path.exists():
            cmd.extend(["-i", str(audio_path)])

        # Video encoding with NVENC
        cmd.extend([
            "-c:v", self.config.encoder,
            "-preset", self.config.nvenc_preset,
            "-cq", str(self.config.crf),
        ])

        # Audio handling
        if audio_path and audio_path.exists():
            cmd.extend(["-c:a", "copy"])
        else:
            cmd.extend(["-an"])

        cmd.extend(["-progress", "pipe:1", str(output_path)])

        logger.debug(f"Post-process command: {' '.join(cmd)}")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        for line in process.stdout:
            if line.startswith("out_time_ms="):
                try:
                    # Update progress (approximate)
                    ms = int(line.split("=")[1])
                    self.progress.update(min(95, ms / 10000000 * 100))
                except:
                    pass

        process.wait()
        if process.returncode != 0:
            stderr = process.stderr.read()
            raise RuntimeError(f"Post-processing failed: {stderr}")

        self.progress.complete_stage()

    def process_video(self, input_path: Path, output_path: Path) -> bool:
        """
        Process a single video through the complete pipeline.
        """
        logger.info(f"Processing: {input_path.name}")
        start_time = time.time()

        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp(prefix="vhs_upscale_"))

        try:
            # Validate input
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")

            video_info = self._get_video_info(input_path)

            # Auto-detect interlacing if not explicitly set
            if self.config.preset == "auto":
                self.config.deinterlace = self._is_interlaced(video_info)

            # Stage 1: Pre-processing
            prepped_video, audio = self.preprocess(input_path, temp_dir)

            # Stage 2: AI Upscaling
            upscaled_video = self.upscale(prepped_video, temp_dir)

            # Stage 3: Post-processing
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.postprocess(upscaled_video, audio, output_path)

            elapsed = time.time() - start_time
            logger.info(f"Complete: {output_path.name} ({timedelta(seconds=int(elapsed))})")
            return True

        except Exception as e:
            logger.error(f"Failed to process {input_path.name}: {e}")
            return False

        finally:
            # Cleanup temp files
            if not self.config.keep_temp and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def watch_folder(self, input_dir: Path, output_dir: Path, interval: int = 5):
        """
        Watch a folder for new video files and process them automatically.
        """
        logger.info(f"Watching folder: {input_dir}")
        logger.info(f"Output folder: {output_dir}")
        logger.info("Press Ctrl+C to stop")

        processed = set()
        video_extensions = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".m4v", ".mpg", ".mpeg"}

        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            while True:
                # Find new video files
                for file_path in input_dir.iterdir():
                    if file_path.suffix.lower() in video_extensions:
                        if file_path not in processed:
                            # Generate output filename
                            output_name = f"{file_path.stem}_upscaled{file_path.suffix}"
                            output_path = output_dir / output_name

                            # Process the video
                            success = self.process_video(file_path, output_path)
                            processed.add(file_path)

                            if success:
                                # Optionally move processed file
                                processed_dir = input_dir / "processed"
                                processed_dir.mkdir(exist_ok=True)
                                shutil.move(str(file_path), str(processed_dir / file_path.name))

                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Watch mode stopped")


def load_config(config_path: Path) -> dict:
    """Load configuration from YAML file."""
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    return {}


def main():
    parser = argparse.ArgumentParser(
        description="VHS Video Upscaling Pipeline - NVIDIA Maxine powered",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Single file:     python vhs_upscale.py -i video.mp4 -o upscaled.mp4
  With preset:     python vhs_upscale.py -i video.mp4 -o out.mp4 --preset vhs
  Watch folder:    python vhs_upscale.py --watch -i ./input -o ./output
  4K output:       python vhs_upscale.py -i video.mp4 -o out.mp4 --resolution 2160
        """
    )

    parser.add_argument("-i", "--input", required=True,
                        help="Input video file or folder (with --watch)")
    parser.add_argument("-o", "--output", required=True,
                        help="Output video file or folder (with --watch)")
    parser.add_argument("-r", "--resolution", type=int, default=1080,
                        choices=[720, 1080, 1440, 2160],
                        help="Target resolution height (default: 1080)")
    parser.add_argument("-q", "--quality", type=int, default=0,
                        choices=[0, 1],
                        help="Quality mode: 0=best, 1=performance (default: 0)")
    parser.add_argument("-p", "--preset", default="vhs",
                        choices=["vhs", "dvd", "webcam", "clean", "auto"],
                        help="Processing preset (default: vhs)")
    parser.add_argument("--watch", action="store_true",
                        help="Watch folder mode - monitor input folder for new files")
    parser.add_argument("--crf", type=int, default=20,
                        help="Output quality CRF (lower=better, default: 20)")
    parser.add_argument("--encoder", default="hevc_nvenc",
                        choices=["hevc_nvenc", "h264_nvenc", "libx265", "libx264"],
                        help="Output encoder (default: hevc_nvenc)")
    parser.add_argument("--config", type=Path, default=Path("config.yaml"),
                        help="Configuration file path")
    parser.add_argument("--keep-temp", action="store_true",
                        help="Keep temporary files for debugging")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load config file
    file_config = load_config(args.config)

    # Build processing config
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
    )

    # Apply preset
    if args.preset in VHSUpscaler.PRESETS:
        preset = VHSUpscaler.PRESETS[args.preset]
        config.deinterlace = preset.get("deinterlace", config.deinterlace)
        config.denoise = preset.get("denoise", config.denoise)
        config.denoise_strength = preset.get("denoise_strength", config.denoise_strength)
        config.quality_mode = preset.get("quality_mode", config.quality_mode)

    # Initialize upscaler
    try:
        upscaler = VHSUpscaler(config)
    except RuntimeError as e:
        logger.error(str(e))
        sys.exit(1)

    # Run
    input_path = Path(args.input)
    output_path = Path(args.output)

    if args.watch:
        upscaler.watch_folder(input_path, output_path)
    else:
        success = upscaler.process_video(input_path, output_path)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
