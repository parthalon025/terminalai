#!/usr/bin/env python3
"""
VHS Video Upscaling Pipeline
============================
AI-powered video upscaling for VHS-quality footage using NVIDIA Maxine SDK.

Accepts local video files OR YouTube URLs as input.

Usage:
    python vhs_upscale.py -i video.mp4 -o upscaled.mp4
    python vhs_upscale.py -i "https://youtube.com/watch?v=..." -o upscaled.mp4
    python vhs_upscale.py --watch -i ./input -o ./output
"""

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import threading
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Optional, List

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Progress Display
# ============================================================================

class UnifiedProgress:
    """
    Unified progress tracker with visual progress bar.
    Shows overall pipeline progress and current stage.
    """

    STAGES = [
        ("download", "Downloading"),
        ("preprocess", "Pre-processing"),
        ("upscale", "AI Upscaling"),
        ("postprocess", "Encoding"),
    ]

    def __init__(self, has_download: bool = False):
        self.has_download = has_download
        self.active_stages = self.STAGES if has_download else self.STAGES[1:]
        self.current_stage_idx = 0
        self.stage_progress = 0.0
        self.start_time = time.time()
        self.stage_start_time = time.time()
        self.video_title = ""
        self.lock = threading.Lock()

    def set_title(self, title: str):
        """Set the video title for display."""
        self.video_title = title[:50] + "..." if len(title) > 50 else title

    def start_stage(self, stage_key: str):
        """Start a new processing stage."""
        with self.lock:
            for idx, (key, _) in enumerate(self.active_stages):
                if key == stage_key:
                    self.current_stage_idx = idx
                    break
            self.stage_progress = 0.0
            self.stage_start_time = time.time()
            self._render()

    def update(self, progress: float):
        """Update current stage progress (0-100)."""
        with self.lock:
            self.stage_progress = min(max(progress, 0), 100)
            self._render()

    def complete_stage(self):
        """Mark current stage as complete."""
        with self.lock:
            self.stage_progress = 100.0
            self._render()
            print()  # New line after stage completion

    def _calculate_overall_progress(self) -> float:
        """Calculate overall pipeline progress."""
        total_stages = len(self.active_stages)
        completed = self.current_stage_idx
        current = self.stage_progress / 100.0
        return ((completed + current) / total_stages) * 100

    def _render(self):
        """Render the progress display."""
        overall = self._calculate_overall_progress()
        stage_name = self.active_stages[self.current_stage_idx][1]

        # Time calculations
        elapsed = time.time() - self.start_time
        stage_elapsed = time.time() - self.stage_start_time

        # ETA estimation
        eta_str = ""
        if self.stage_progress > 5:
            stage_remaining = (stage_elapsed / self.stage_progress) * (100 - self.stage_progress)
            # Rough estimate for remaining stages
            remaining_stages = len(self.active_stages) - self.current_stage_idx - 1
            total_remaining = stage_remaining + (remaining_stages * stage_elapsed * 100 / max(self.stage_progress, 1))
            eta_str = f"ETA: {timedelta(seconds=int(total_remaining))}"

        # Build progress bar
        bar_width = 40
        filled = int(bar_width * overall / 100)
        bar = "█" * filled + "▒" * (bar_width - filled)

        # Stage indicators
        stage_dots = ""
        for i, (_, name) in enumerate(self.active_stages):
            if i < self.current_stage_idx:
                stage_dots += "●"  # Completed
            elif i == self.current_stage_idx:
                stage_dots += "◐"  # In progress
            else:
                stage_dots += "○"  # Pending

        # Build output line
        line = f"\r{stage_dots} [{bar}] {overall:5.1f}% │ {stage_name}: {self.stage_progress:5.1f}%"
        if eta_str:
            line += f" │ {eta_str}"

        # Pad to clear previous content
        line = line.ljust(120)
        print(line, end="", flush=True)

    def finish(self, success: bool = True):
        """Display final status."""
        elapsed = time.time() - self.start_time
        status = "✓ Complete" if success else "✗ Failed"
        print(f"\n\n{status} in {timedelta(seconds=int(elapsed))}")
        if self.video_title:
            print(f"Video: {self.video_title}")


# ============================================================================
# YouTube Downloader
# ============================================================================

class YouTubeDownloader:
    """Download videos from YouTube using yt-dlp."""

    # Patterns to detect YouTube URLs
    URL_PATTERNS = [
        r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(https?://)?(www\.)?youtu\.be/[\w-]+',
        r'(https?://)?(www\.)?youtube\.com/shorts/[\w-]+',
        r'(https?://)?m\.youtube\.com/watch\?v=[\w-]+',
    ]

    def __init__(self, progress: UnifiedProgress):
        self.progress = progress
        self._validate_ytdlp()

    def _validate_ytdlp(self):
        """Check if yt-dlp is available."""
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True, text=True, check=True
            )
            logger.debug(f"yt-dlp version: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "yt-dlp not found. Install with: pip install yt-dlp"
            )

    @classmethod
    def is_youtube_url(cls, input_str: str) -> bool:
        """Check if input string is a YouTube URL."""
        for pattern in cls.URL_PATTERNS:
            if re.match(pattern, input_str):
                return True
        return False

    def get_video_info(self, url: str) -> dict:
        """Get video metadata without downloading."""
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-download",
            url
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            logger.warning(f"Could not get video info: {e}")
            return {}

    def download(self, url: str, output_dir: Path) -> Path:
        """
        Download YouTube video to specified directory.
        Returns path to downloaded file.
        """
        self.progress.start_stage("download")

        # Get video info first
        info = self.get_video_info(url)
        title = info.get("title", "video")
        self.progress.set_title(title)

        logger.info(f"Downloading: {title}")

        # Sanitize filename
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:100]
        output_template = str(output_dir / f"{safe_title}.%(ext)s")

        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", output_template,
            "--no-playlist",
            "--newline",  # Progress on new lines for parsing
            "--progress-template", "%(progress._percent_str)s",
            url
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        output_file = None
        for line in process.stdout:
            line = line.strip()

            # Parse progress percentage
            if "%" in line:
                try:
                    # Handle formats like "  50.0%" or "50%"
                    pct_str = line.replace("%", "").strip()
                    pct = float(pct_str)
                    self.progress.update(pct)
                except ValueError:
                    pass

            # Capture output filename
            if "[download] Destination:" in line:
                output_file = Path(line.split("Destination:")[-1].strip())
            elif "[Merger]" in line and "Merging formats into" in line:
                # Get merged output file
                match = re.search(r'"([^"]+)"', line)
                if match:
                    output_file = Path(match.group(1))

            logger.debug(f"yt-dlp: {line}")

        process.wait()

        if process.returncode != 0:
            raise RuntimeError(f"Download failed with code {process.returncode}")

        # Find the output file if not captured
        if not output_file or not output_file.exists():
            # Look for mp4 files in output directory
            mp4_files = list(output_dir.glob("*.mp4"))
            if mp4_files:
                output_file = max(mp4_files, key=lambda p: p.stat().st_mtime)
            else:
                raise RuntimeError("Could not find downloaded file")

        self.progress.complete_stage()
        return output_file


# ============================================================================
# Processing Configuration
# ============================================================================

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
    skip_maxine: bool = False  # For testing without Maxine
    # New options for non-NVIDIA and HDR
    upscale_engine: str = "auto"  # auto, maxine, realesrgan, ffmpeg
    realesrgan_path: str = ""  # Path to realesrgan-ncnn-vulkan
    realesrgan_model: str = "realesrgan-x4plus"  # Model name
    hdr_mode: str = "sdr"  # sdr, hdr10, hlg
    hdr_brightness: int = 200  # Peak brightness in nits for HDR
    color_depth: int = 8  # 8 or 10 bit


# ============================================================================
# VHS Upscaler Pipeline
# ============================================================================

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
        },
        "youtube": {
            "deinterlace": False,
            "denoise": False,
            "denoise_strength": (1, 1, 1, 1),
            "quality_mode": 0,
        }
    }

    # Available upscale engines with priority
    UPSCALE_ENGINES = ["maxine", "realesrgan", "ffmpeg"]

    def __init__(self, config: ProcessingConfig, progress: UnifiedProgress = None):
        self.config = config
        self.progress = progress
        self.available_engines = []
        self._validate_dependencies()
        self._detect_upscale_engine()

    def _validate_dependencies(self):
        """Verify all required tools are available."""
        # Check FFmpeg
        try:
            result = subprocess.run(
                [self.config.ffmpeg_path, "-version"],
                capture_output=True, text=True, check=True
            )
            logger.debug(f"FFmpeg found: {result.stdout.split(chr(10))[0]}")
            self.available_engines.append("ffmpeg")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("FFmpeg not found. Install from https://ffmpeg.org")

        # Check NVIDIA Maxine
        maxine_exe = Path(self.config.maxine_path) / "VideoEffectsApp.exe"
        if not maxine_exe.exists():
            maxine_home = os.environ.get("MAXINE_HOME", "")
            if maxine_home:
                maxine_exe = Path(maxine_home) / "bin" / "VideoEffectsApp.exe"
                if maxine_exe.exists():
                    self.config.maxine_path = str(Path(maxine_home) / "bin")
                    self.config.model_dir = str(Path(maxine_home) / "bin" / "models")
        if maxine_exe.exists():
            self.available_engines.append("maxine")
            logger.debug("NVIDIA Maxine found")

        # Check Real-ESRGAN ncnn-vulkan
        realesrgan_exe = self._find_realesrgan()
        if realesrgan_exe:
            self.config.realesrgan_path = str(realesrgan_exe)
            self.available_engines.append("realesrgan")
            logger.debug(f"Real-ESRGAN found: {realesrgan_exe}")

    def _find_realesrgan(self) -> Optional[Path]:
        """Find Real-ESRGAN ncnn-vulkan executable."""
        # Check config path first
        if self.config.realesrgan_path:
            exe = Path(self.config.realesrgan_path)
            if exe.exists():
                return exe

        # Common executable names
        exe_names = [
            "realesrgan-ncnn-vulkan",
            "realesrgan-ncnn-vulkan.exe",
            "realesrgan",
        ]

        # Check PATH
        for name in exe_names:
            exe = shutil.which(name)
            if exe:
                return Path(exe)

        # Check common install locations
        common_paths = [
            Path.home() / "realesrgan-ncnn-vulkan",
            Path("/usr/local/bin"),
            Path("/opt/realesrgan"),
            Path("C:/Program Files/realesrgan-ncnn-vulkan"),
            Path(os.environ.get("REALESRGAN_HOME", "")),
        ]

        for base_path in common_paths:
            if not base_path.exists():
                continue
            for name in exe_names:
                exe = base_path / name
                if exe.exists():
                    return exe

        return None

    def _detect_upscale_engine(self):
        """Auto-detect best available upscale engine."""
        if self.config.upscale_engine != "auto":
            if self.config.upscale_engine not in self.available_engines:
                logger.warning(
                    f"Requested engine '{self.config.upscale_engine}' not available. "
                    f"Available: {', '.join(self.available_engines)}"
                )
                self.config.upscale_engine = "ffmpeg"
            return

        # Auto-select best available engine
        priority = ["maxine", "realesrgan", "ffmpeg"]
        for engine in priority:
            if engine in self.available_engines:
                self.config.upscale_engine = engine
                logger.info(f"Auto-selected upscale engine: {engine}")
                return

        self.config.upscale_engine = "ffmpeg"

    def get_available_engines(self) -> List[str]:
        """Return list of available upscale engines."""
        return self.available_engines.copy()

    def _get_video_duration(self, input_path: Path) -> float:
        """Get video duration in seconds."""
        cmd = [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "json",
            str(input_path)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            return float(data.get("format", {}).get("duration", 0))
        except:
            return 0

    def _is_interlaced(self, input_path: Path) -> bool:
        """Detect if video is interlaced."""
        cmd = [
            "ffprobe", "-v", "quiet",
            "-select_streams", "v:0",
            "-show_entries", "stream=field_order",
            "-of", "json",
            str(input_path)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            streams = data.get("streams", [])
            if streams:
                field_order = streams[0].get("field_order", "progressive")
                return field_order not in ("progressive", "unknown")
        except:
            pass
        return False

    def preprocess(self, input_path: Path, temp_dir: Path, duration: float) -> tuple:
        """Pre-process video: deinterlace, denoise, extract audio."""
        self.progress.start_stage("preprocess")

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

        # Process video
        video_cmd = [
            self.config.ffmpeg_path,
            "-y", "-i", str(input_path),
            "-vf", vf_string,
            "-an",
            "-c:v", "libx264",
            "-crf", "15",
            "-preset", "fast",
            "-progress", "pipe:1",
            str(video_out)
        ]

        process = subprocess.Popen(
            video_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        for line in process.stdout:
            if line.startswith("out_time_ms="):
                try:
                    ms = int(line.split("=")[1])
                    if duration > 0:
                        self.progress.update((ms / 1000000) / duration * 100)
                except:
                    pass

        process.wait()
        if process.returncode != 0:
            raise RuntimeError(f"Pre-processing failed: {process.stderr.read()}")

        # Extract audio
        audio_cmd = [
            self.config.ffmpeg_path,
            "-y", "-i", str(input_path),
            "-vn", "-c:a", "copy",
            str(audio_out)
        ]
        subprocess.run(audio_cmd, capture_output=True)

        self.progress.complete_stage()
        return video_out, audio_out if audio_out.exists() else None

    def upscale(self, input_path: Path, temp_dir: Path) -> Path:
        """Apply AI upscaling using selected engine."""
        self.progress.start_stage("upscale")

        output_path = temp_dir / "upscaled.mp4"
        engine = self.config.upscale_engine

        # Handle legacy skip_maxine flag
        if self.config.skip_maxine and engine == "maxine":
            engine = "realesrgan" if "realesrgan" in self.available_engines else "ffmpeg"

        logger.info(f"Using upscale engine: {engine}")

        if engine == "realesrgan":
            output_path = self._upscale_realesrgan(input_path, temp_dir)
        elif engine == "maxine":
            output_path = self._upscale_maxine(input_path, temp_dir)
        else:
            output_path = self._upscale_ffmpeg(input_path, temp_dir)

        if not output_path.exists():
            raise RuntimeError("Upscaling failed to produce output")

        self.progress.complete_stage()
        return output_path

    def _upscale_ffmpeg(self, input_path: Path, temp_dir: Path) -> Path:
        """FFmpeg-based upscaling (works on any hardware)."""
        output_path = temp_dir / "upscaled.mp4"

        cmd = [
            self.config.ffmpeg_path,
            "-y", "-i", str(input_path),
            "-vf", f"scale=-2:{self.config.resolution}:flags=lanczos",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "slow",
            "-progress", "pipe:1",
            str(output_path)
        ]

        duration = self._get_video_duration(input_path)
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        for line in process.stdout:
            if line.startswith("out_time_ms="):
                try:
                    ms = int(line.split("=")[1])
                    if duration > 0:
                        self.progress.update((ms / 1000000) / duration * 100)
                except:
                    pass

        process.wait()
        return output_path

    def _upscale_realesrgan(self, input_path: Path, temp_dir: Path) -> Path:
        """Real-ESRGAN ncnn-vulkan upscaling (works on AMD/Intel/NVIDIA GPUs)."""
        frames_dir = temp_dir / "frames"
        upscaled_dir = temp_dir / "upscaled_frames"
        frames_dir.mkdir(exist_ok=True)
        upscaled_dir.mkdir(exist_ok=True)

        output_path = temp_dir / "upscaled.mp4"

        # Get video info
        duration = self._get_video_duration(input_path)
        fps = self._get_video_fps(input_path)

        # Extract frames
        logger.info("Extracting frames for Real-ESRGAN...")
        extract_cmd = [
            self.config.ffmpeg_path, "-y", "-i", str(input_path),
            "-qscale:v", "1", "-qmin", "1", "-qmax", "1", "-vsync", "0",
            str(frames_dir / "frame%08d.png")
        ]
        subprocess.run(extract_cmd, capture_output=True, check=True)

        # Count frames
        frame_files = list(frames_dir.glob("*.png"))
        total_frames = len(frame_files)
        logger.info(f"Extracted {total_frames} frames")

        # Determine scale factor based on target resolution
        # Real-ESRGAN typically does 4x, so we may need to resize after
        scale = 4 if self.config.resolution >= 2160 else 4

        # Run Real-ESRGAN
        logger.info("Running Real-ESRGAN upscaling...")
        realesrgan_cmd = [
            self.config.realesrgan_path,
            "-i", str(frames_dir),
            "-o", str(upscaled_dir),
            "-n", self.config.realesrgan_model,
            "-s", str(scale),
        ]

        process = subprocess.Popen(
            realesrgan_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

        processed = 0
        for line in process.stdout:
            # Real-ESRGAN outputs progress like "0.00%", "1.23%", etc.
            if "%" in line:
                try:
                    pct = float(line.split("%")[0].split()[-1])
                    self.progress.update(pct)
                except:
                    pass
            # Also count processed frames from output
            if "done" in line.lower() or ".png" in line:
                processed += 1
                self.progress.update((processed / total_frames) * 100)

        process.wait()
        if process.returncode != 0:
            raise RuntimeError("Real-ESRGAN upscaling failed")

        # Reassemble video with target resolution
        logger.info("Reassembling video...")
        assemble_cmd = [
            self.config.ffmpeg_path, "-y",
            "-framerate", str(fps),
            "-i", str(upscaled_dir / "frame%08d.png"),
            "-vf", f"scale=-2:{self.config.resolution}:flags=lanczos",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "slow",
            "-pix_fmt", "yuv420p",
            str(output_path)
        ]
        subprocess.run(assemble_cmd, capture_output=True, check=True)

        return output_path

    def _upscale_maxine(self, input_path: Path, temp_dir: Path) -> Path:
        """NVIDIA Maxine upscaling (requires RTX GPU)."""
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

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

        for line in process.stdout:
            if "%" in line:
                try:
                    pct = float(line.split("%")[0].split()[-1])
                    self.progress.update(pct)
                except:
                    pass

        process.wait()
        return output_path

    def _get_video_fps(self, input_path: Path) -> float:
        """Get video frame rate."""
        cmd = [
            "ffprobe", "-v", "quiet",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate",
            "-of", "json",
            str(input_path)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            fps_str = data.get("streams", [{}])[0].get("r_frame_rate", "30/1")
            num, den = map(int, fps_str.split("/"))
            return num / den if den != 0 else 30.0
        except:
            return 30.0

    def _build_hdr_filter(self) -> str:
        """Build FFmpeg filter for HDR conversion."""
        if self.config.hdr_mode == "sdr":
            return ""

        # HDR10 conversion filter
        if self.config.hdr_mode == "hdr10":
            return (
                "zscale=t=linear:npl=100,format=gbrpf32le,"
                "zscale=p=bt2020:t=bt2020-10:m=bt2020nc:r=tv,"
                "format=yuv420p10le"
            )

        # HLG conversion filter
        if self.config.hdr_mode == "hlg":
            return (
                "zscale=t=linear:npl=100,format=gbrpf32le,"
                "zscale=p=bt2020:t=arib-std-b67:m=bt2020nc:r=tv,"
                "format=yuv420p10le"
            )

        return ""

    def postprocess(self, video_path: Path, audio_path: Optional[Path],
                    output_path: Path, duration: float):
        """Post-process: encode with optional HDR and remux audio."""
        self.progress.start_stage("postprocess")

        cmd = [self.config.ffmpeg_path, "-y", "-i", str(video_path)]

        if audio_path and audio_path.exists():
            cmd.extend(["-i", str(audio_path)])

        # Build video filter chain
        vf_filters = []
        hdr_filter = self._build_hdr_filter()
        if hdr_filter:
            vf_filters.append(hdr_filter)

        if vf_filters:
            cmd.extend(["-vf", ",".join(vf_filters)])

        # Select encoder and pixel format based on HDR mode
        encoder = self.config.encoder
        pix_fmt = "yuv420p"

        if self.config.hdr_mode != "sdr":
            # HDR requires 10-bit encoding
            pix_fmt = "yuv420p10le"
            # Use x265 for HDR if NVENC not available for 10-bit
            if encoder == "hevc_nvenc":
                # Check if NVENC supports 10-bit (most modern cards do)
                cmd.extend(["-profile:v", "main10"])
            elif encoder == "libx265":
                cmd.extend(["-profile:v", "main10"])

        cmd.extend([
            "-c:v", encoder,
            "-preset", self.config.nvenc_preset,
            "-cq", str(self.config.crf),
            "-pix_fmt", pix_fmt,
        ])

        # Add HDR metadata if needed
        if self.config.hdr_mode == "hdr10":
            cmd.extend([
                "-color_primaries", "bt2020",
                "-color_trc", "smpte2084",
                "-colorspace", "bt2020nc",
            ])
        elif self.config.hdr_mode == "hlg":
            cmd.extend([
                "-color_primaries", "bt2020",
                "-color_trc", "arib-std-b67",
                "-colorspace", "bt2020nc",
            ])

        if audio_path and audio_path.exists():
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        else:
            cmd.extend(["-an"])

        cmd.extend(["-progress", "pipe:1", str(output_path)])

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        for line in process.stdout:
            if line.startswith("out_time_ms="):
                try:
                    ms = int(line.split("=")[1])
                    if duration > 0:
                        self.progress.update((ms / 1000000) / duration * 100)
                except:
                    pass

        process.wait()
        if process.returncode != 0:
            raise RuntimeError(f"Post-processing failed: {process.stderr.read()}")

        self.progress.complete_stage()

    def process(self, input_source: str, output_path: Path) -> bool:
        """
        Process video from file or YouTube URL.
        """
        start_time = time.time()
        temp_dir = Path(tempfile.mkdtemp(prefix="vhs_upscale_"))
        is_youtube = YouTubeDownloader.is_youtube_url(input_source)

        # Initialize progress tracker
        self.progress = UnifiedProgress(has_download=is_youtube)

        print("\n" + "=" * 60)
        print("  VHS Upscaler Pipeline")
        print("=" * 60)
        print(f"  Input:      {'YouTube URL' if is_youtube else input_source}")
        print(f"  Output:     {output_path}")
        print(f"  Resolution: {self.config.resolution}p")
        print(f"  Preset:     {self.config.preset}")
        print("=" * 60 + "\n")

        try:
            # Stage 0: Download if YouTube URL
            if is_youtube:
                downloader = YouTubeDownloader(self.progress)
                input_path = downloader.download(input_source, temp_dir)
            else:
                input_path = Path(input_source)
                if not input_path.exists():
                    raise FileNotFoundError(f"Input file not found: {input_path}")
                self.progress.set_title(input_path.stem)

            # Get video duration for progress
            duration = self._get_video_duration(input_path)

            # Auto-detect interlacing
            if self.config.preset == "auto":
                self.config.deinterlace = self._is_interlaced(input_path)

            # Stage 1: Pre-processing
            prepped_video, audio = self.preprocess(input_path, temp_dir, duration)

            # Stage 2: AI Upscaling
            upscaled_video = self.upscale(prepped_video, temp_dir)

            # Stage 3: Post-processing
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.postprocess(upscaled_video, audio, output_path, duration)

            self.progress.finish(success=True)
            print(f"Output: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.progress.finish(success=False)
            return False

        finally:
            if not self.config.keep_temp and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def watch_folder(self, input_dir: Path, output_dir: Path, interval: int = 5):
        """Watch folder for new files."""
        logger.info(f"Watching: {input_dir}")
        logger.info(f"Output:   {output_dir}")
        logger.info("Press Ctrl+C to stop\n")

        processed = set()
        extensions = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"}

        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            while True:
                for file_path in input_dir.iterdir():
                    if file_path.suffix.lower() in extensions and file_path not in processed:
                        output_name = f"{file_path.stem}_upscaled.mp4"
                        output_path = output_dir / output_name

                        success = self.process(str(file_path), output_path)
                        processed.add(file_path)

                        if success:
                            processed_dir = input_dir / "processed"
                            processed_dir.mkdir(exist_ok=True)
                            shutil.move(str(file_path), str(processed_dir / file_path.name))

                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nWatch mode stopped")


# ============================================================================
# Main Entry Point
# ============================================================================

def load_config(config_path: Path) -> dict:
    """Load configuration from YAML file."""
    if HAS_YAML and config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    return {}


def main():
    parser = argparse.ArgumentParser(
        description="VHS Video Upscaler - Accepts files or YouTube URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Local file:    python vhs_upscale.py -i video.mp4 -o upscaled.mp4
  YouTube:       python vhs_upscale.py -i "https://youtube.com/watch?v=..." -o out.mp4
  Watch folder:  python vhs_upscale.py --watch -i ./input -o ./output
  4K output:     python vhs_upscale.py -i video.mp4 -o out.mp4 -r 2160
  HDR output:    python vhs_upscale.py -i video.mp4 -o out.mp4 --hdr hdr10
  No NVIDIA:     python vhs_upscale.py -i video.mp4 -o out.mp4 --engine realesrgan
        """
    )

    parser.add_argument("-i", "--input", required=True,
                        help="Input video file or YouTube URL")
    parser.add_argument("-o", "--output", required=True,
                        help="Output video file or folder (with --watch)")
    parser.add_argument("-r", "--resolution", type=int, default=1080,
                        choices=[720, 1080, 1440, 2160],
                        help="Target resolution (default: 1080)")
    parser.add_argument("-q", "--quality", type=int, default=0,
                        choices=[0, 1],
                        help="Quality: 0=best, 1=fast (default: 0)")
    parser.add_argument("-p", "--preset", default="vhs",
                        choices=["vhs", "dvd", "webcam", "clean", "youtube", "auto"],
                        help="Processing preset (default: vhs)")
    parser.add_argument("--watch", action="store_true",
                        help="Watch folder mode")
    parser.add_argument("--crf", type=int, default=20,
                        help="Output quality CRF (default: 20)")
    parser.add_argument("--encoder", default="hevc_nvenc",
                        choices=["hevc_nvenc", "h264_nvenc", "libx265", "libx264"],
                        help="Output encoder (default: hevc_nvenc)")
    parser.add_argument("--skip-maxine", action="store_true",
                        help="Use FFmpeg upscaling instead of Maxine (deprecated, use --engine)")

    # New options for engine and HDR
    parser.add_argument("--engine", default="auto",
                        choices=["auto", "maxine", "realesrgan", "ffmpeg"],
                        help="Upscaling engine: auto (detect best), maxine (NVIDIA RTX), "
                             "realesrgan (AMD/Intel/NVIDIA), ffmpeg (any CPU)")
    parser.add_argument("--hdr", default="sdr",
                        choices=["sdr", "hdr10", "hlg"],
                        help="HDR mode: sdr (standard), hdr10 (HDR10), hlg (HLG broadcast)")
    parser.add_argument("--realesrgan-model", default="realesrgan-x4plus",
                        choices=["realesrgan-x4plus", "realesrgan-x4plus-anime",
                                 "realesr-animevideov3", "realesrnet-x4plus"],
                        help="Real-ESRGAN model (default: realesrgan-x4plus)")

    parser.add_argument("--config", type=Path, default=Path("config.yaml"),
                        help="Config file path")
    parser.add_argument("--keep-temp", action="store_true",
                        help="Keep temporary files")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Auto-detect YouTube and switch preset
    is_youtube = YouTubeDownloader.is_youtube_url(args.input)
    if is_youtube and args.preset == "vhs":
        args.preset = "youtube"
        logger.info("Auto-selected 'youtube' preset for URL input")

    # Load config
    file_config = load_config(args.config)

    # Build config
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
        # New options
        upscale_engine=args.engine,
        realesrgan_path=file_config.get("realesrgan_path", ""),
        realesrgan_model=args.realesrgan_model,
        hdr_mode=args.hdr,
    )

    # Apply preset
    if args.preset in VHSUpscaler.PRESETS:
        preset = VHSUpscaler.PRESETS[args.preset]
        config.deinterlace = preset.get("deinterlace", config.deinterlace)
        config.denoise = preset.get("denoise", config.denoise)
        config.denoise_strength = preset.get("denoise_strength", config.denoise_strength)
        config.quality_mode = preset.get("quality_mode", config.quality_mode)

    # Run
    try:
        upscaler = VHSUpscaler(config)
    except RuntimeError as e:
        logger.error(str(e))
        sys.exit(1)

    output_path = Path(args.output)

    if args.watch:
        upscaler.watch_folder(Path(args.input), output_path)
    else:
        success = upscaler.process(args.input, output_path)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
