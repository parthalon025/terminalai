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
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Optional, List

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    from .audio_processor import AudioProcessor, AudioConfig, AudioEnhanceMode, UpmixMode, AudioChannelLayout, AudioFormat
    HAS_AUDIO_PROCESSOR = True
except ImportError:
    HAS_AUDIO_PROCESSOR = False

try:
    from .analysis import AnalyzerWrapper, VideoAnalysis, AnalyzerBackend
    from .presets import get_preset_from_analysis, get_recommended_settings_from_analysis
    HAS_ANALYSIS = True
except ImportError:
    HAS_ANALYSIS = False

try:
    from .face_restoration import FaceRestorer
    HAS_FACE_RESTORATION = True
except ImportError:
    HAS_FACE_RESTORATION = False

try:
    from .deinterlace import DeinterlaceProcessor, DeinterlaceEngine
    HAS_DEINTERLACE = True
except ImportError:
    HAS_DEINTERLACE = False

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

        # Build progress bar (ASCII-safe for Windows console)
        bar_width = 40
        filled = int(bar_width * overall / 100)
        bar = "#" * filled + "-" * (bar_width - filled)

        # Stage indicators (ASCII-safe)
        stage_dots = ""
        for i, (_, name) in enumerate(self.active_stages):
            if i < self.current_stage_idx:
                stage_dots += "*"  # Completed
            elif i == self.current_stage_idx:
                stage_dots += ">"  # In progress
            else:
                stage_dots += "."  # Pending

        # Build output line (use | instead of │ for ASCII compatibility)
        line = f"\r{stage_dots} [{bar}] {overall:5.1f}% | {stage_name}: {self.stage_progress:5.1f}%"
        if eta_str:
            line += f" | {eta_str}"

        # Pad to clear previous content
        line = line.ljust(120)
        try:
            print(line, end="", flush=True)
        except UnicodeEncodeError:
            # Fallback if encoding still fails
            pass

    def finish(self, success: bool = True):
        """Display final status."""
        elapsed = time.time() - self.start_time
        status = "[OK] Complete" if success else "[FAILED] Failed"
        # Use ASCII-safe output for Windows console compatibility
        try:
            print(f"\n\n{status} in {timedelta(seconds=int(elapsed))}")
            if self.video_title:
                print(f"Video: {self.video_title}")
        except UnicodeEncodeError:
            # Fallback for encoding issues
            print(f"\n\n{status} in {int(elapsed)} seconds")
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
    maxine_path: str = ""  # DEPRECATED: Use rtxvideo engine instead
    model_dir: str = ""  # DEPRECATED: Use rtxvideo engine instead
    ffmpeg_path: str = "ffmpeg"
    resolution: int = 1080
    quality_mode: int = 0  # 0 = best quality, 1 = performance
    crf: int = 20
    preset: str = "vhs"
    deinterlace: bool = True
    deinterlace_algorithm: str = "yadif"  # yadif, bwdif, w3fdif, qtgmc
    qtgmc_preset: Optional[str] = None  # draft, medium, slow, very_slow (for QTGMC only)
    denoise: bool = True
    denoise_strength: tuple = (3, 2, 3, 2)  # hqdn3d parameters
    encoder: str = "hevc_nvenc"
    nvenc_preset: str = "p7"
    keep_temp: bool = False
    skip_maxine: bool = False  # DEPRECATED: For testing without Maxine
    # Video upscale options
    upscale_engine: str = "auto"  # auto, rtxvideo, realesrgan, ffmpeg (maxine deprecated)
    realesrgan_path: str = ""  # Path to realesrgan-ncnn-vulkan
    realesrgan_model: str = "realesrgan-x4plus"  # Model name
    realesrgan_denoise: float = 0.5  # 0-1 denoise strength for Real-ESRGAN
    ffmpeg_scale_algo: str = "lanczos"  # lanczos, bicubic, bilinear, spline, neighbor
    hdr_mode: str = "sdr"  # sdr, hdr10, hlg
    hdr_brightness: int = 400  # Peak brightness in nits for HDR
    color_depth: int = 10  # 8 or 10 bit
    # RTX Video SDK options (v1.5.1+)
    rtxvideo_sdk_path: str = ""  # Path to RTX Video SDK (auto-detected if empty)
    rtxvideo_artifact_reduction: bool = True  # Enable artifact reduction
    rtxvideo_artifact_strength: float = 0.5  # 0.0-1.0 strength
    rtxvideo_hdr_conversion: bool = False  # Enable SDR to HDR10 conversion
    # Audio processing options
    audio_enhance: str = "none"  # none, light, moderate, aggressive, voice, music
    audio_upmix: str = "none"  # none, simple, surround, prologic, demucs
    audio_layout: str = "original"  # original, stereo, 5.1, 7.1, mono
    audio_format: str = "aac"  # aac, ac3, eac3, dts, flac
    audio_bitrate: str = "192k"
    audio_normalize: bool = True
    # Audio enhancement advanced options
    audio_target_loudness: float = -14.0  # LUFS target (-24 to -9)
    audio_noise_floor: float = -20.0  # dB noise floor (-30 to -10)
    # Demucs advanced options
    demucs_model: str = "htdemucs"  # htdemucs, htdemucs_ft, mdx_extra, mdx_extra_q
    demucs_device: str = "auto"  # auto, cuda, cpu
    demucs_shifts: int = 1  # 0-5, more = better quality, slower
    # Surround advanced options
    lfe_crossover: int = 120  # Hz (60-200)
    center_mix: float = 0.707  # 0-1, 0.707 = -3dB
    surround_delay: int = 15  # ms (0-50)
    # LUT (Look-Up Table) color grading options
    lut_file: Optional[Path] = None  # Path to .cube LUT file
    lut_strength: float = 1.0  # 0.0-1.0 blend intensity
    # Face restoration options (GFPGAN)
    face_restore: bool = False  # Enable AI face restoration
    face_restore_strength: float = 0.5  # 0.0-1.0 restoration strength
    face_restore_upscale: int = 2  # Upscale factor (1, 2, or 4)


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

    # Available upscale engines with priority (rtxvideo is preferred, maxine deprecated)
    UPSCALE_ENGINES = ["rtxvideo", "realesrgan", "ffmpeg", "maxine"]

    def __init__(self, config: ProcessingConfig, progress: UnifiedProgress = None):
        self.config = config
        self.progress = progress
        self.available_engines = []
        self._validate_dependencies()
        self._detect_upscale_engine()

    def _validate_dependencies(self):
        """Verify all required tools are available."""
        # Check FFmpeg (required)
        try:
            result = subprocess.run(
                [self.config.ffmpeg_path, "-version"],
                capture_output=True, text=True, check=True
            )
            logger.debug(f"FFmpeg found: {result.stdout.split(chr(10))[0]}")
            self.available_engines.append("ffmpeg")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("FFmpeg not found. Install from https://ffmpeg.org")

        # Check RTX Video SDK (preferred, Windows only)
        try:
            from .rtx_video_sdk import is_rtx_video_available
            is_available, message = is_rtx_video_available()
            if is_available:
                self.available_engines.append("rtxvideo")
                logger.info(f"RTX Video SDK: {message}")
            else:
                logger.debug(f"RTX Video SDK not available: {message}")
        except ImportError:
            logger.debug("RTX Video SDK module not available")

        # Check Real-ESRGAN ncnn-vulkan
        realesrgan_exe = self._find_realesrgan()
        if realesrgan_exe:
            self.config.realesrgan_path = str(realesrgan_exe)
            self.available_engines.append("realesrgan")
            logger.debug(f"Real-ESRGAN found: {realesrgan_exe}")

        # Check NVIDIA Maxine (DEPRECATED - kept for backwards compatibility)
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
            logger.debug("NVIDIA Maxine found (deprecated - use rtxvideo instead)")

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

        # Auto-select best available engine (rtxvideo preferred, maxine deprecated)
        priority = ["rtxvideo", "realesrgan", "ffmpeg", "maxine"]
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
        """Pre-process video: deinterlace, denoise, LUT color grading, extract audio."""
        self.progress.start_stage("preprocess")

        video_out = temp_dir / "prepped_video.mp4"
        audio_out = temp_dir / "audio.aac"

        # Handle deinterlacing with multi-engine support
        working_video = input_path
        if self.config.deinterlace:
            deinterlace_algo = self.config.deinterlace_algorithm.lower()

            # QTGMC requires separate processing with VapourSynth
            if deinterlace_algo == "qtgmc" and HAS_DEINTERLACE:
                logger.info(f"Deinterlacing with QTGMC (preset: {self.config.qtgmc_preset or 'medium'})")
                try:
                    deinterlacer = DeinterlaceProcessor(DeinterlaceEngine.QTGMC)
                    deinterlaced_video = temp_dir / "deinterlaced.mp4"

                    # Detect field order (TFF/BFF)
                    tff = True  # Default to TFF
                    if self._is_interlaced(input_path):
                        # Try to detect field order
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
                            field_order = data.get("streams", [{}])[0].get("field_order", "tt")
                            tff = field_order != "bb"  # bb = bottom field first
                        except:
                            pass

                    deinterlacer.deinterlace(
                        input_path,
                        deinterlaced_video,
                        preset=self.config.qtgmc_preset or "medium",
                        tff=tff
                    )
                    working_video = deinterlaced_video
                    logger.info("QTGMC deinterlacing complete")

                except Exception as e:
                    logger.warning(f"QTGMC deinterlacing failed: {e}, falling back to yadif")
                    deinterlace_algo = "yadif"

            elif deinterlace_algo == "qtgmc" and not HAS_DEINTERLACE:
                logger.warning("QTGMC requested but deinterlace module not available, falling back to yadif")
                deinterlace_algo = "yadif"

        # Build video filter chain for remaining processing
        vf_filters = []

        # Add FFmpeg-based deinterlacing if not using QTGMC
        if self.config.deinterlace and working_video == input_path:
            deinterlace_algo = self.config.deinterlace_algorithm.lower()
            if deinterlace_algo == "bwdif":
                vf_filters.append("bwdif=1")  # Better motion compensation
            elif deinterlace_algo == "w3fdif":
                vf_filters.append("w3fdif")  # Better detail preservation
            else:  # yadif (default fallback)
                vf_filters.append("yadif=1")  # Fast, good quality

        # Denoise filter
        if self.config.denoise:
            ds = self.config.denoise_strength
            vf_filters.append(f"hqdn3d={ds[0]}:{ds[1]}:{ds[2]}:{ds[3]}")

        # Apply LUT color grading (after denoise, before upscale)
        if self.config.lut_file and self.config.lut_file.exists():
            # SECURITY: Escape special characters in file path to prevent command injection
            # FFmpeg filter strings can execute arbitrary commands if not properly escaped
            lut_path = str(self.config.lut_file).replace("\\", "/")  # FFmpeg needs forward slashes

            # Escape single quotes and backslashes for FFmpeg filter syntax
            # This prevents filter chain injection through malicious file paths
            lut_path_escaped = lut_path.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

            # Additional validation: Reject paths with suspicious characters
            suspicious_chars = [';', '|', '&', '$', '`', '\n', '\r']
            if any(char in lut_path for char in suspicious_chars):
                logger.warning(f"Rejecting LUT file with suspicious characters: {lut_path}")
                logger.warning("LUT path must not contain: ; | & $ ` newlines")
            else:
                if self.config.lut_strength < 1.0:
                    # Blend LUT with original using colorchannelmixer
                    # Formula: output = original * (1 - strength) + lut * strength
                    strength = self.config.lut_strength
                    inv_strength = 1.0 - strength
                    # Use split and blend to mix original and LUT-transformed video
                    vf_filters.append(
                        f"split[main][lut];"
                        f"[lut]lut3d='{lut_path_escaped}'[graded];"
                        f"[main][graded]blend=all_mode=normal:all_opacity={strength}"
                    )
                else:
                    # Apply LUT at full strength
                    vf_filters.append(f"lut3d='{lut_path_escaped}'")
                logger.info(f"Applying LUT: {self.config.lut_file.name} (strength: {self.config.lut_strength})")

        vf_string = ",".join(vf_filters) if vf_filters else "null"

        # Process video (use GPU encoding if available)
        use_nvenc = self.config.encoder in ["hevc_nvenc", "h264_nvenc"]
        if use_nvenc:
            # Don't use hwaccel for decoding when applying CPU filters
            # The NVENC encoder will still use GPU
            video_cmd = [
                self.config.ffmpeg_path,
                "-y", "-i", str(working_video),
                "-vf", vf_string,
                "-an",
                "-c:v", "h264_nvenc",
                "-preset", "p4",
                "-cq", "18",
                "-progress", "pipe:1",
                str(video_out)
            ]
        else:
            video_cmd = [
                self.config.ffmpeg_path,
                "-y", "-i", str(working_video),
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

        # Read stderr in separate thread to prevent pipe deadlock
        stderr_lines = []
        def read_stderr():
            for line in process.stderr:
                stderr_lines.append(line)

        import threading
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stderr_thread.start()

        # Read progress from stdout
        for line in process.stdout:
            if line.startswith("out_time_ms="):
                try:
                    ms = int(line.split("=")[1])
                    if duration > 0:
                        self.progress.update((ms / 1000000) / duration * 100)
                except:
                    pass

        process.wait()
        stderr_thread.join(timeout=1)

        if process.returncode != 0:
            error_output = ''.join(stderr_lines)
            raise RuntimeError(f"Pre-processing failed: {error_output}")

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

        if engine == "rtxvideo":
            output_path = self._upscale_rtxvideo(input_path, temp_dir)
        elif engine == "realesrgan":
            output_path = self._upscale_realesrgan(input_path, temp_dir)
        elif engine == "maxine":
            # DEPRECATED: Kept for backwards compatibility
            logger.warning("Maxine engine is deprecated. Consider using 'rtxvideo' instead.")
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

        # Use GPU encoding if available
        use_nvenc = self.config.encoder in ["hevc_nvenc", "h264_nvenc"]
        if use_nvenc:
            # Use hwupload_cuda to convert from CPU to CUDA format for scaling
            cmd = [
                self.config.ffmpeg_path,
                "-y", "-i", str(input_path),
                "-vf", f"hwupload_cuda,scale_cuda=-2:{self.config.resolution}",
                "-an",  # No audio (audio is handled in final encoding)
                "-c:v", "h264_nvenc",
                "-preset", "p4",
                "-cq", "18",
                "-progress", "pipe:1",
                str(output_path)
            ]
        else:
            cmd = [
                self.config.ffmpeg_path,
                "-y", "-i", str(input_path),
                "-vf", f"scale=-2:{self.config.resolution}:flags=lanczos",
                "-an",  # No audio (audio is handled in final encoding)
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

        # Read stderr in separate thread to prevent pipe deadlock
        import threading
        stderr_output = []
        def read_stderr():
            for line in process.stderr:
                stderr_output.append(line)  # Capture stderr for error checking

        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stderr_thread.start()

        # Read progress from stdout
        for line in process.stdout:
            if line.startswith("out_time_ms="):
                try:
                    ms = int(line.split("=")[1])
                    if duration > 0:
                        self.progress.update((ms / 1000000) / duration * 100)
                except:
                    pass

        process.wait()
        stderr_thread.join(timeout=1)

        # Check if FFmpeg failed
        if process.returncode != 0:
            error_msg = ''.join(stderr_output[-20:])  # Last 20 lines of stderr
            raise RuntimeError(f"FFmpeg upscaling failed with code {process.returncode}: {error_msg}")

        # Verify the output file is valid
        if not output_path.exists() or output_path.stat().st_size < 1000:
            raise RuntimeError(f"Upscaling produced invalid output file")

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

    def _upscale_rtxvideo(self, input_path: Path, temp_dir: Path) -> Path:
        """
        RTX Video SDK upscaling (requires RTX 20+ GPU).

        Uses NVIDIA's RTX Video SDK for AI-powered upscaling with:
        - Super Resolution (up to 4x upscaling)
        - Artifact Reduction (removes compression artifacts)
        - Optional HDR conversion (SDR to HDR10)

        Args:
            input_path: Input video file
            temp_dir: Temporary directory for processing

        Returns:
            Path to upscaled video file
        """
        from .rtx_video_sdk import RTXVideoProcessor, RTXVideoConfig, HDRFormat

        output_path = temp_dir / "upscaled.mp4"

        # Determine scale factor based on target resolution
        video_info = self._get_video_info(input_path)
        input_height = video_info.get("height", 480) if video_info else 480

        if self.config.resolution >= input_height * 3:
            scale_factor = 4
        else:
            scale_factor = 2

        # Configure RTX Video SDK
        rtx_config = RTXVideoConfig(
            enable_super_resolution=True,
            enable_artifact_reduction=self.config.rtxvideo_artifact_reduction,
            enable_hdr_conversion=self.config.rtxvideo_hdr_conversion,
            scale_factor=scale_factor,
            target_resolution=self.config.resolution,
            artifact_strength=self.config.rtxvideo_artifact_strength,
            hdr_format=HDRFormat.HDR10 if self.config.rtxvideo_hdr_conversion else HDRFormat.SDR,
            peak_brightness=self.config.hdr_brightness,
            sdk_path=self.config.rtxvideo_sdk_path or "",
        )

        # Create processor with progress callback
        processor = RTXVideoProcessor(
            config=rtx_config,
            ffmpeg_path=self.config.ffmpeg_path,
            progress_callback=lambda p: self.progress.update(p) if self.progress else None,
        )

        # Process video
        logger.info(f"RTX Video SDK: Upscaling to {self.config.resolution}p (scale: {scale_factor}x)")
        logger.info(f"  Artifact Reduction: {self.config.rtxvideo_artifact_reduction}")
        logger.info(f"  HDR Conversion: {self.config.rtxvideo_hdr_conversion}")

        success = processor.process_video(
            input_path=input_path,
            output_path=output_path,
            preserve_audio=False,  # Audio handled separately in pipeline
        )

        if not success:
            logger.warning("RTX Video SDK upscaling failed, falling back to FFmpeg")
            return self._upscale_ffmpeg(input_path, temp_dir)

        return output_path

    def _get_video_info(self, input_path: Path) -> Optional[dict]:
        """Get video metadata."""
        cmd = [
            "ffprobe", "-v", "quiet",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate",
            "-of", "json",
            str(input_path)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            stream = data.get("streams", [{}])[0]
            return {
                "width": int(stream.get("width", 0)),
                "height": int(stream.get("height", 0)),
                "fps": stream.get("r_frame_rate", "30/1"),
            }
        except Exception:
            return None

    def _upscale_maxine(self, input_path: Path, temp_dir: Path) -> Path:
        """
        NVIDIA Maxine upscaling (DEPRECATED - use rtxvideo instead).

        Kept for backwards compatibility. New projects should use the
        'rtxvideo' engine which provides RTX Video SDK integration.
        """
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

    def _apply_face_restoration(self, input_path: Path, temp_dir: Path) -> Path:
        """
        Apply GFPGAN face restoration to video.

        Args:
            input_path: Input video file
            temp_dir: Temporary directory for processing

        Returns:
            Path to video with restored faces
        """
        if not HAS_FACE_RESTORATION:
            logger.warning("Face restoration module not available, skipping")
            return input_path

        output_path = temp_dir / "face_restored.mp4"

        try:
            logger.info("Applying GFPGAN face restoration...")
            logger.info(f"  Strength: {self.config.face_restore_strength}")
            logger.info(f"  Upscale: {self.config.face_restore_upscale}x")

            # Initialize face restorer
            restorer = FaceRestorer(ffmpeg_path=self.config.ffmpeg_path)

            # Check if GFPGAN is actually available
            if not restorer.has_gfpgan:
                logger.warning("GFPGAN not properly installed, skipping face restoration")
                logger.info("To enable face restoration:")
                logger.info("  1. pip install gfpgan basicsr opencv-python torch")
                logger.info("  2. Download model: vhs-upscale --download-gfpgan-model")
                return input_path

            # Apply face restoration
            restorer.restore_faces(
                input_path=input_path,
                output_path=output_path,
                upscale=self.config.face_restore_upscale,
                weight=self.config.face_restore_strength,
                only_center_face=False,
                aligned=False
            )

            logger.info("Face restoration complete")
            return output_path

        except Exception as e:
            logger.error(f"Face restoration failed: {e}")
            logger.warning("Continuing without face restoration")
            return input_path

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

    def _process_audio(self, input_path: Path, output_path: Path):
        """Process audio with enhancement and/or upmixing."""
        if not HAS_AUDIO_PROCESSOR:
            logger.warning("Audio processor not available, skipping audio enhancement")
            return

        # Build audio config from processing config
        audio_config = AudioConfig(
            enhance_mode=AudioEnhanceMode(self.config.audio_enhance),
            upmix_mode=UpmixMode(self.config.audio_upmix),
            output_layout=AudioChannelLayout(self.config.audio_layout),
            output_format=AudioFormat(self.config.audio_format),
            output_bitrate=self.config.audio_bitrate,
            normalize=self.config.audio_normalize,
        )

        processor = AudioProcessor(audio_config, self.config.ffmpeg_path)
        processor.process(input_path, output_path)
        logger.info(f"Audio processed: enhance={self.config.audio_enhance}, "
                    f"upmix={self.config.audio_upmix}, layout={self.config.audio_layout}")

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

        # Audio processing
        if audio_path and audio_path.exists():
            # Check if audio processing is needed
            needs_audio_processing = (
                self.config.audio_enhance != "none" or
                self.config.audio_upmix != "none" or
                self.config.audio_layout != "original"
            )

            if needs_audio_processing and HAS_AUDIO_PROCESSOR:
                # Process audio separately with AudioProcessor
                processed_audio = output_path.parent / f"{output_path.stem}_audio_processed.wav"
                self._process_audio(audio_path, processed_audio)
                cmd.extend(["-i", str(processed_audio)])
                cmd.extend(["-map", "0:v", "-map", "2:a"])  # Map processed audio

                # Set audio codec based on layout
                if self.config.audio_layout in ["5.1", "7.1"]:
                    cmd.extend(["-c:a", self.config.audio_format, "-b:a", "640k"])
                else:
                    cmd.extend(["-c:a", self.config.audio_format, "-b:a", self.config.audio_bitrate])
            else:
                # Standard audio passthrough/encoding
                cmd.extend(["-c:a", self.config.audio_format, "-b:a", self.config.audio_bitrate])
        else:
            cmd.extend(["-an"])

        cmd.extend(["-progress", "pipe:1", str(output_path)])

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Read stderr in separate thread to prevent pipe deadlock
        import threading
        stderr_lines = []
        def read_stderr():
            for line in process.stderr:
                stderr_lines.append(line)

        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stderr_thread.start()

        # Read progress from stdout
        for line in process.stdout:
            if line.startswith("out_time_ms="):
                try:
                    ms = int(line.split("=")[1])
                    if duration > 0:
                        self.progress.update((ms / 1000000) / duration * 100)
                except:
                    pass

        process.wait()
        stderr_thread.join(timeout=1)

        if process.returncode != 0:
            error_output = ''.join(stderr_lines)
            raise RuntimeError(f"Post-processing failed: {error_output}")

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

            # Stage 2.5: Face Restoration (if enabled)
            if self.config.face_restore:
                upscaled_video = self._apply_face_restoration(upscaled_video, temp_dir)

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


def main_legacy():
    """
    Legacy main function for backwards compatibility.

    This function implements the original flat CLI argument structure.
    It's called when legacy arguments (-i/--input) are detected.
    """
    parser = argparse.ArgumentParser(
        description="VHS Video Upscaler - Accepts files or YouTube URLs (Legacy Mode)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Legacy Examples:
  Local file:    python vhs_upscale.py -i video.mp4 -o upscaled.mp4
  YouTube:       python vhs_upscale.py -i "https://youtube.com/watch?v=..." -o out.mp4
  Watch folder:  python vhs_upscale.py --watch -i ./input -o ./output
  4K output:     python vhs_upscale.py -i video.mp4 -o out.mp4 -r 2160
  HDR output:    python vhs_upscale.py -i video.mp4 -o out.mp4 --hdr hdr10
  No NVIDIA:     python vhs_upscale.py -i video.mp4 -o out.mp4 --engine realesrgan
  5.1 audio:     python vhs_upscale.py -i video.mp4 -o out.mp4 --audio-layout 5.1 --audio-upmix surround
  Clean audio:   python vhs_upscale.py -i video.mp4 -o out.mp4 --audio-enhance voice

New Subcommand Syntax (recommended):
  vhs-upscale upscale video.mp4 -o upscaled.mp4
  vhs-upscale analyze video.mp4
  vhs-upscale preview video.mp4 -o preview.mp4
  vhs-upscale batch input_folder/ output_folder/
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

    # Audio processing options
    parser.add_argument("--audio-enhance", default="none",
                        choices=["none", "light", "moderate", "aggressive", "voice", "music"],
                        help="Audio enhancement: none, light, moderate, aggressive, voice, music")
    parser.add_argument("--audio-upmix", default="none",
                        choices=["none", "simple", "surround", "prologic", "demucs"],
                        help="Surround upmix: none, simple, surround (FFmpeg), prologic, demucs (AI)")
    parser.add_argument("--audio-layout", default="original",
                        choices=["original", "stereo", "5.1", "7.1", "mono"],
                        help="Output audio layout (default: original)")
    parser.add_argument("--audio-format", default="aac",
                        choices=["aac", "ac3", "eac3", "dts", "flac"],
                        help="Output audio format (default: aac)")
    parser.add_argument("--audio-bitrate", default="192k",
                        help="Audio bitrate (default: 192k, use 640k for 5.1)")
    parser.add_argument("--no-audio-normalize", action="store_true",
                        help="Disable audio loudness normalization")

    # LUT color grading options
    parser.add_argument("--lut", type=Path,
                        help="Apply LUT color grading (.cube file)")
    parser.add_argument("--lut-strength", type=float, default=1.0,
                        help="LUT blend strength 0.0-1.0 (default: 1.0)")

    # Face restoration options
    parser.add_argument("--face-restore", action="store_true",
                        help="Enable GFPGAN AI face restoration")
    parser.add_argument("--face-restore-strength", type=float, default=0.5,
                        help="Face restoration strength 0.0-1.0 (default: 0.5)")
    parser.add_argument("--face-restore-upscale", type=int, default=2, choices=[1, 2, 4],
                        help="Face restoration upscale factor (default: 2)")

    # Deinterlacing options
    parser.add_argument("--deinterlace-algorithm", default="yadif",
                        choices=["yadif", "bwdif", "w3fdif", "qtgmc"],
                        help="Deinterlacing algorithm: yadif (fast), bwdif (better motion), "
                             "w3fdif (better detail), qtgmc (best quality, requires VapourSynth)")
    parser.add_argument("--qtgmc-preset", default=None,
                        choices=["draft", "medium", "slow", "very_slow"],
                        help="QTGMC quality preset (only for --deinterlace-algorithm qtgmc)")

    parser.add_argument("--config", type=Path, default=Path("config.yaml"),
                        help="Config file path")
    parser.add_argument("--keep-temp", action="store_true",
                        help="Keep temporary files")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output")

    # Video analysis options
    parser.add_argument("--analyze-only", action="store_true",
                        help="Analyze video and print report without processing")
    parser.add_argument("--auto-detect", action="store_true",
                        help="Auto-detect optimal settings based on video analysis")
    parser.add_argument("--analysis-config", type=Path,
                        help="Load pre-analyzed configuration JSON file")
    parser.add_argument("--save-analysis", type=Path,
                        help="Export analysis results to JSON file")
    parser.add_argument("--force-backend", choices=["python", "bash", "basic"],
                        help="Force specific analyzer backend (for testing)")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # ========================================================================
    # Video Analysis Integration
    # ========================================================================
    if args.analyze_only or args.auto_detect or args.analysis_config:
        if not HAS_ANALYSIS:
            logger.error("Video analysis module not available. Install required dependencies.")
            sys.exit(1)

        # Determine which file to analyze
        analyze_path = args.input

        # Skip download for YouTube URLs in analyze mode
        if YouTubeDownloader.is_youtube_url(args.input):
            if args.analyze_only:
                logger.error("Cannot analyze YouTube URLs directly. Download the video first.")
                sys.exit(1)
            # For auto-detect, we'll download first then analyze
            logger.info("YouTube URL detected - will download before analysis")

        # Load or run analysis
        analysis = None

        if args.analysis_config:
            # Load pre-analyzed config
            logger.info(f"Loading analysis config from {args.analysis_config}")
            analysis = VideoAnalysis.from_json(str(args.analysis_config))
            logger.info("Analysis loaded successfully")

        elif args.analyze_only or args.auto_detect:
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
            wrapper = AnalyzerWrapper(force_backend=backend)
            analysis = wrapper.analyze(analyze_path)

            # Print analysis report
            print("\n" + analysis.get_summary())

            # Save if requested
            if args.save_analysis:
                analysis.to_json(str(args.save_analysis))
                logger.info(f"Analysis saved to {args.save_analysis}")

            # Exit if analyze-only mode
            if args.analyze_only:
                sys.exit(0)

        # Apply analysis recommendations for auto-detect mode
        if args.auto_detect and analysis:
            logger.info("Applying recommended settings from analysis...")

            # Get recommended preset
            recommended_preset = get_preset_from_analysis(analysis)
            logger.info(f"Recommended preset: {recommended_preset}")

            # Override args with recommendations
            args.preset = recommended_preset

            # Get detailed settings
            recommended_settings = get_recommended_settings_from_analysis(analysis)

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
    is_youtube = YouTubeDownloader.is_youtube_url(args.input)
    if is_youtube and args.preset == "vhs" and not args.auto_detect:
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

    # If output_path is a directory, generate filename
    if output_path.is_dir() or (not output_path.suffix and not output_path.exists()):
        # Extract filename from input
        input_path = Path(args.input)
        base_name = input_path.stem
        output_filename = f"{base_name}_{args.resolution}p.mp4"
        output_path = output_path / output_filename

    if args.watch:
        upscaler.watch_folder(Path(args.input), output_path.parent)
    else:
        success = upscaler.process(args.input, output_path)
        sys.exit(0 if success else 1)


def main():
    """
    Main entry point with subcommand support.

    Implements modern CLI architecture with subcommands:
      - upscale: Process a single video
      - analyze: Analyze video characteristics
      - preview: Generate comparison preview
      - batch: Process multiple videos
      - test-presets: Test multiple presets

    Maintains backwards compatibility by detecting legacy arguments
    (-i/--input) and routing to main_legacy().
    """
    # Check for legacy mode (backwards compatibility)
    # If -i or --input is in arguments, use legacy parser
    if '-i' in sys.argv or '--input' in sys.argv:
        logger.info("Legacy argument mode detected, using backwards-compatible parser")
        return main_legacy()

    # Modern subcommand-based CLI
    try:
        from .cli import (
            setup_upscale_parser,
            setup_analyze_parser,
            setup_preview_parser,
            setup_batch_parser,
            setup_test_presets_parser,
            handle_upscale,
            handle_analyze,
            handle_preview,
            handle_batch,
            handle_test_presets,
        )
    except ImportError as e:
        logger.error(f"Failed to import CLI modules: {e}")
        logger.error("Falling back to legacy mode")
        return main_legacy()

    # Create main parser with subcommands
    parser = argparse.ArgumentParser(
        prog='vhs-upscale',
        description='VHS Video Upscaler - AI-powered video enhancement',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Upscale a video:
    vhs-upscale upscale input.mp4 -o output.mp4 -p vhs -r 2160

  Analyze video first:
    vhs-upscale analyze input.mp4 --recommend

  Generate preview:
    vhs-upscale preview input.mp4 -o preview.mp4 --start 60

  Batch process folder:
    vhs-upscale batch ./input_videos/ ./output_videos/ -p vhs

  Test multiple presets:
    vhs-upscale test-presets input.mp4 -o test_results/

For more help on a specific subcommand:
  vhs-upscale <subcommand> --help

Legacy syntax (deprecated but supported):
  vhs-upscale -i input.mp4 -o output.mp4 -p vhs
        """
    )

    # Add version argument
    parser.add_argument(
        '--version',
        action='version',
        version='VHS Upscaler v1.4.2 (CLI v2.0.0)'
    )

    # Create subparsers
    subparsers = parser.add_subparsers(
        dest='subcommand',
        title='Available subcommands',
        description='Use these commands for different operations',
        help='Subcommand to execute'
    )

    # Setup each subcommand parser
    setup_upscale_parser(subparsers)
    setup_analyze_parser(subparsers)
    setup_preview_parser(subparsers)
    setup_batch_parser(subparsers)
    setup_test_presets_parser(subparsers)

    # Parse arguments
    args = parser.parse_args()

    # If no subcommand provided, show help
    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    # Dispatch to appropriate handler
    handlers = {
        'upscale': handle_upscale,
        'analyze': handle_analyze,
        'preview': handle_preview,
        'batch': handle_batch,
        'test-presets': handle_test_presets,
    }

    handler = handlers.get(args.subcommand)
    if handler:
        exit_code = handler(args)
        sys.exit(exit_code)
    else:
        logger.error(f"Unknown subcommand: {args.subcommand}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
