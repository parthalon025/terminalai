#!/usr/bin/env python3
"""
VHS Upscaler Web GUI
====================
Modern web-based interface for the VHS Upscaling Pipeline.
Built with Gradio for a clean, responsive user experience.

Features:
- File upload with drag-and-drop support
- Video preview thumbnails
- Dark mode toggle
- Real-time queue monitoring
- Batch processing support
"""

import gradio as gr
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import base64
import hashlib
import tempfile

# Fix Windows console encoding for unicode characters
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from queue_manager import VideoQueue, QueueJob, JobStatus
from logger import get_logger

# Import hardware detection
try:
    from hardware_detection import detect_hardware, get_optimal_config, HardwareInfo
    HAS_HARDWARE_DETECTION = True
except ImportError:
    HAS_HARDWARE_DETECTION = False

# Initialize logger
logger = get_logger(verbose=True, log_to_file=True)

# Version info
__version__ = "1.5.1"


# =============================================================================
# Global State
# =============================================================================

class AppState:
    """Global application state."""
    queue: Optional[VideoQueue] = None
    output_dir: Path = Path("./output")
    logs: List[str] = []
    max_logs: int = 100
    dark_mode: bool = False
    thumbnail_cache: Dict[str, str] = {}
    temp_dir: Path = Path(tempfile.gettempdir()) / "vhs_upscaler_temp"

    # Hardware detection cache
    hardware: Optional['HardwareInfo'] = None
    optimal_config: Optional[Dict[str, Any]] = None
    hardware_detected: bool = False

    @classmethod
    def detect_hardware_once(cls):
        """Detect hardware once and cache the result."""
        if not HAS_HARDWARE_DETECTION or cls.hardware_detected:
            return

        try:
            logger.info("Detecting hardware capabilities...")

            # Run detection with timeout to prevent hanging
            import threading
            detection_result = {"hardware": None, "config": None, "error": None}

            def run_detection():
                try:
                    detection_result["hardware"] = detect_hardware()
                    detection_result["config"] = get_optimal_config(detection_result["hardware"])
                except Exception as e:
                    detection_result["error"] = e

            detection_thread = threading.Thread(target=run_detection, daemon=True)
            detection_thread.start()
            detection_thread.join(timeout=10.0)  # 10 second timeout

            if detection_thread.is_alive():
                logger.error("Hardware detection timed out after 10 seconds")
                cls.add_log("Hardware detection timed out - using CPU fallback")
                cls.hardware_detected = True
                return

            if detection_result["error"]:
                raise detection_result["error"]

            cls.hardware = detection_result["hardware"]
            cls.optimal_config = detection_result["config"]
            cls.hardware_detected = True

            # Log detection results
            if cls.hardware:
                cls.add_log(f"Hardware detected: {cls.hardware.display_name}")
            if cls.optimal_config:
                cls.add_log(f"Optimal config: {cls.optimal_config['explanation']}")

                # Log warnings
                for warning in cls.optimal_config.get('warnings', []):
                    logger.warning(warning)

        except Exception as e:
            logger.error(f"Hardware detection failed: {e}")
            cls.add_log(f"Hardware detection error: {str(e)}")
            cls.hardware_detected = True  # Don't retry

    @classmethod
    def add_log(cls, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        cls.logs.append(f"[{timestamp}] {message}")
        if len(cls.logs) > cls.max_logs:
            cls.logs = cls.logs[-cls.max_logs:]

    @classmethod
    def toggle_dark_mode(cls) -> bool:
        """Toggle dark mode setting."""
        cls.dark_mode = not cls.dark_mode
        cls.add_log(f"Dark mode {'enabled' if cls.dark_mode else 'disabled'}")
        return cls.dark_mode

    @classmethod
    def get_thumbnail(cls, video_path: str) -> Optional[str]:
        """Get or generate thumbnail for video file."""
        if not video_path or not Path(video_path).exists():
            return None

        # Check cache
        path_hash = hashlib.md5(video_path.encode()).hexdigest()[:8]
        if path_hash in cls.thumbnail_cache:
            return cls.thumbnail_cache[path_hash]

        # Generate thumbnail using ffmpeg
        try:
            cls.temp_dir.mkdir(parents=True, exist_ok=True)
            thumb_path = cls.temp_dir / f"thumb_{path_hash}.jpg"

            if not thumb_path.exists():
                subprocess.run([
                    "ffmpeg", "-y", "-i", video_path,
                    "-ss", "00:00:01", "-vframes", "1",
                    "-vf", "scale=320:-1",
                    str(thumb_path)
                ], capture_output=True, timeout=10)

            if thumb_path.exists():
                with open(thumb_path, "rb") as f:
                    thumb_data = base64.b64encode(f.read()).decode()
                cls.thumbnail_cache[path_hash] = f"data:image/jpeg;base64,{thumb_data}"
                return cls.thumbnail_cache[path_hash]
        except Exception as e:
            logger.debug(f"Failed to generate thumbnail: {e}")

        return None


# =============================================================================
# Processing Functions
# =============================================================================

def process_job(job: QueueJob, progress_callback) -> bool:
    """Process a single job through the pipeline."""
    try:
        from vhs_upscale import (
            VHSUpscaler, ProcessingConfig, YouTubeDownloader
        )
    except ImportError as e:
        job.error_message = f"Failed to import processing modules: {e}"
        AppState.add_log(f"✗ Import error: {e}")
        return False

    AppState.add_log(f"Starting job: {job.input_source[:50]}...")

    try:
        # Detect if YouTube
        is_youtube = YouTubeDownloader.is_youtube_url(job.input_source)

        # Update status
        progress_callback(
            job,
            JobStatus.DOWNLOADING if is_youtube else JobStatus.PREPROCESSING,
            0, 0, "Initializing...", ""
        )

        # Build config
        config = ProcessingConfig(
            resolution=job.resolution,
            quality_mode=job.quality,
            crf=job.crf,
            preset=job.preset,
            encoder=job.encoder,
            # Video upscale options
            upscale_engine=getattr(job, 'upscale_engine', 'auto'),
            hdr_mode=getattr(job, 'hdr_mode', 'sdr'),
            realesrgan_model=getattr(job, 'realesrgan_model', 'realesrgan-x4plus'),
            realesrgan_denoise=getattr(job, 'realesrgan_denoise', 0.5),
            ffmpeg_scale_algo=getattr(job, 'ffmpeg_scale_algo', 'lanczos'),
            hdr_brightness=getattr(job, 'hdr_brightness', 400),
            color_depth=getattr(job, 'hdr_color_depth', 10),
            # RTX Video SDK options (v1.5.1+)
            rtxvideo_artifact_reduction=getattr(job, 'rtxvideo_artifact_reduction', True),
            rtxvideo_artifact_strength=getattr(job, 'rtxvideo_artifact_strength', 0.5),
            rtxvideo_hdr_conversion=getattr(job, 'rtxvideo_hdr', False),
            # Audio options
            audio_enhance=getattr(job, 'audio_enhance', 'none'),
            audio_upmix=getattr(job, 'audio_upmix', 'none'),
            audio_layout=getattr(job, 'audio_layout', 'original'),
            audio_format=getattr(job, 'audio_format', 'aac'),
            # Audio enhancement advanced
            audio_target_loudness=getattr(job, 'audio_target_loudness', -14.0),
            audio_noise_floor=getattr(job, 'audio_noise_floor', -20.0),
            # Demucs advanced
            demucs_model=getattr(job, 'demucs_model', 'htdemucs'),
            demucs_device=getattr(job, 'demucs_device', 'auto'),
            demucs_shifts=getattr(job, 'demucs_shifts', 1),
            # Surround advanced
            lfe_crossover=getattr(job, 'lfe_crossover', 120),
            center_mix=getattr(job, 'center_mix', 0.707),
            surround_delay=getattr(job, 'surround_delay', 15),
            # LUT color grading options
            lut_file=Path(getattr(job, 'lut_file', '')) if getattr(job, 'lut_file', None) else None,
            lut_strength=getattr(job, 'lut_strength', 1.0),
            # Face restoration options
            face_restore=getattr(job, 'face_restore', False),
            face_model=getattr(job, 'face_model', 'gfpgan'),
            face_restore_strength=getattr(job, 'face_restore_strength', 0.5),
            face_restore_upscale=getattr(job, 'face_restore_upscale', 2),
            # AudioSR options
            audio_sr_enabled=getattr(job, 'audio_sr_enabled', False),
            audio_sr_model=getattr(job, 'audio_sr_model', 'basic'),
            # Deinterlacing options
            deinterlace_algorithm=getattr(job, 'deinterlace_algorithm', 'yadif'),
            qtgmc_preset=getattr(job, 'qtgmc_preset', None),
        )

        # Validate optional features and warn if not available
        if config.face_restore:
            try:
                from vhs_upscale import HAS_FACE_RESTORATION
                if not HAS_FACE_RESTORATION:
                    AppState.add_log("⚠️ Face restoration requested but not available - feature will be skipped")
                    AppState.add_log("💡 To enable: pip install -e \".[faces]\" or pip install gfpgan opencv-python")
                    logger.warning("Face restoration requested but not available. Install with: pip install -e \".[faces]\"")
            except:
                AppState.add_log("⚠️ Face restoration not available - feature will be skipped")
                AppState.add_log("💡 To enable: pip install -e \".[faces]\" or pip install gfpgan opencv-python")

        if config.deinterlace_algorithm == "qtgmc":
            try:
                from vhs_upscale import HAS_DEINTERLACE
                if not HAS_DEINTERLACE:
                    AppState.add_log("⚠️ QTGMC deinterlacing requested but VapourSynth not available - falling back to yadif")
                    AppState.add_log("💡 To enable QTGMC: Install VapourSynth from https://github.com/vapoursynth/vapoursynth/releases")
                    logger.warning("QTGMC requested but VapourSynth not available. Falling back to yadif. Install VapourSynth: https://github.com/vapoursynth/vapoursynth/releases")
                    config.deinterlace_algorithm = "yadif"
            except:
                AppState.add_log("⚠️ QTGMC not available - falling back to yadif")
                AppState.add_log("💡 To enable QTGMC: Install VapourSynth from https://github.com/vapoursynth/vapoursynth/releases")
                config.deinterlace_algorithm = "yadif"

        # Apply preset
        if job.preset in VHSUpscaler.PRESETS:
            preset = VHSUpscaler.PRESETS[job.preset]
            config.deinterlace = preset.get("deinterlace", config.deinterlace)
            config.denoise = preset.get("denoise", config.denoise)
            config.denoise_strength = preset.get("denoise_strength", config.denoise_strength)

        # Create custom progress tracker that updates job
        class JobProgressTracker:
            def __init__(self, job, callback, is_youtube):
                self.job = job
                self.callback = callback
                self.is_youtube = is_youtube
                self.stages = ["download", "preprocess", "upscale", "postprocess"] if is_youtube else ["preprocess", "upscale", "postprocess"]
                self.current_idx = 0

            def start_stage(self, stage_key):
                for i, s in enumerate(self.stages):
                    if s == stage_key:
                        self.current_idx = i
                        break

                status_map = {
                    "download": JobStatus.DOWNLOADING,
                    "preprocess": JobStatus.PREPROCESSING,
                    "upscale": JobStatus.UPSCALING,
                    "postprocess": JobStatus.ENCODING,
                }
                status = status_map.get(stage_key, JobStatus.PREPROCESSING)

                overall = (self.current_idx / len(self.stages)) * 100
                self.callback(self.job, status, overall, 0, stage_key.title(), self.job.video_title)

            def update(self, progress):
                overall = ((self.current_idx + progress/100) / len(self.stages)) * 100
                self.callback(self.job, self.job.status, overall, progress, self.job.current_stage, self.job.video_title)

            def complete_stage(self):
                overall = ((self.current_idx + 1) / len(self.stages)) * 100
                self.callback(self.job, self.job.status, overall, 100, self.job.current_stage, self.job.video_title)

            def set_title(self, title):
                self.job.video_title = title

            def finish(self, success=True):
                pass

        # Initialize upscaler
        upscaler = VHSUpscaler(config)
        upscaler.progress = JobProgressTracker(job, progress_callback, is_youtube)

        # Process
        output_path = Path(job.output_path)
        success = upscaler.process(job.input_source, output_path)

        if success:
            AppState.add_log(f"✓ Completed: {output_path.name}")
        else:
            AppState.add_log(f"✗ Failed: {job.input_source[:50]}")

        return success

    except Exception as e:
        job.error_message = str(e)
        AppState.add_log(f"✗ Error: {str(e)}")
        logger.error(f"Job failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def initialize_queue():
    """Initialize the video queue."""
    if AppState.queue is None:
        AppState.queue = VideoQueue(
            processor_func=process_job,
            max_concurrent=1,
            auto_start=False,
            persistence_file=Path("queue_state.json")
        )


# =============================================================================
# GUI Helper Functions
# =============================================================================

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds <= 0:
        return "0:00:00"
    return str(timedelta(seconds=int(seconds)))


def get_video_info(video_path: str) -> Dict[str, Any]:
    """Extract video metadata using ffprobe."""
    info = {
        "duration": 0,
        "width": 0,
        "height": 0,
        "codec": "unknown",
        "fps": 0,
        "size": 0
    }

    if not video_path or not Path(video_path).exists():
        return info

    try:
        # Get file size
        info["size"] = Path(video_path).stat().st_size

        # Use ffprobe to get video info
        result = subprocess.run([
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            video_path
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            data = json.loads(result.stdout)

            # Get duration from format
            if "format" in data and "duration" in data["format"]:
                info["duration"] = float(data["format"]["duration"])

            # Get video stream info
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    info["width"] = stream.get("width", 0)
                    info["height"] = stream.get("height", 0)
                    info["codec"] = stream.get("codec_name", "unknown")

                    # Parse FPS
                    fps_str = stream.get("r_frame_rate", "0/1")
                    if "/" in fps_str:
                        num, den = fps_str.split("/")
                        if int(den) > 0:
                            info["fps"] = round(int(num) / int(den), 2)
                    break
    except Exception as e:
        logger.debug(f"Failed to get video info: {e}")

    return info


def handle_file_upload(file_obj) -> Tuple[str, str]:
    """Handle uploaded file and return path and preview info."""
    if file_obj is None:
        return "", ""

    # Gradio File returns a file path string
    file_path = file_obj if isinstance(file_obj, str) else file_obj.name

    if not file_path or not Path(file_path).exists():
        return "", "No file uploaded"

    # Get video info
    info = get_video_info(file_path)
    preview_html = f"""
    <div style="padding: 10px; background: #f5f5f5; border-radius: 8px;">
        <strong>Video Info:</strong><br/>
        Resolution: {info['width']}x{info['height']}<br/>
        Duration: {format_duration(info['duration'])}<br/>
        Codec: {info['codec']}<br/>
        FPS: {info['fps']}<br/>
        Size: {format_file_size(info['size'])}
    </div>
    """

    AppState.add_log(f"File uploaded: {Path(file_path).name}")
    return file_path, preview_html


def estimate_processing_time(info: Dict[str, Any], resolution: int) -> str:
    """Estimate processing time based on video info and target resolution."""
    if info["duration"] <= 0:
        return "Unknown"

    # Base estimate: 1 second of video = 2-10 seconds of processing
    # Depends on resolution scaling
    scale_factor = (resolution / max(info["height"], 480)) ** 2
    base_multiplier = 3  # Average processing multiplier

    estimated_seconds = info["duration"] * base_multiplier * scale_factor
    return format_duration(estimated_seconds)


def get_status_emoji(status: JobStatus) -> str:
    """Get emoji for job status."""
    return {
        JobStatus.PENDING: "⏳",
        JobStatus.DOWNLOADING: "⬇️",
        JobStatus.PREPROCESSING: "🔄",
        JobStatus.UPSCALING: "🚀",
        JobStatus.ENCODING: "💾",
        JobStatus.COMPLETED: "✅",
        JobStatus.FAILED: "❌",
        JobStatus.CANCELLED: "🚫",
    }.get(status, "❓")


def generate_output_path(input_source: str, resolution: int) -> str:
    """Generate output path for a video."""
    AppState.output_dir.mkdir(parents=True, exist_ok=True)

    # Extract filename from URL or path
    if "youtube.com" in input_source or "youtu.be" in input_source:
        base_name = f"youtube_{datetime.now():%Y%m%d_%H%M%S}"
    else:
        base_name = Path(input_source).stem

    output_name = f"{base_name}_{resolution}p.mp4"
    return str(AppState.output_dir / output_name)


# =============================================================================
# GUI Event Handlers
# =============================================================================

def add_to_queue(input_source: str, preset: str, resolution: int,
                 quality: int, crf: int, encoder: str,
                 upscale_engine: str = "auto", hdr_mode: str = "sdr",
                 realesrgan_model: str = "realesrgan-x4plus",
                 realesrgan_denoise: float = 0.5,
                 ffmpeg_scale_algo: str = "lanczos",
                 hdr_brightness: int = 400, hdr_color_depth: int = 10,
                 # RTX Video SDK options (v1.5.1+)
                 rtxvideo_artifact_reduction: bool = True,
                 rtxvideo_artifact_strength: float = 0.5,
                 rtxvideo_hdr: bool = False,
                 # Audio options
                 audio_enhance: str = "none", audio_upmix: str = "none",
                 audio_layout: str = "original", audio_format: str = "aac",
                 audio_target_loudness: float = -14.0, audio_noise_floor: float = -20.0,
                 demucs_model: str = "htdemucs", demucs_device: str = "auto",
                 demucs_shifts: int = 1, lfe_crossover: int = 120,
                 center_mix: float = 0.707, surround_delay: int = 15,
                 lut_file: str = "", lut_strength: float = 1.0,
                 face_restore: bool = False, face_model: str = "gfpgan",
                 face_restore_strength: float = 0.5,
                 face_restore_upscale: int = 2,
                 audio_sr_enabled: bool = False, audio_sr_model: str = "basic",
                 deinterlace_algorithm: str = "yadif", qtgmc_preset: str = "medium") -> Tuple[str, str]:
    """Add a video to the processing queue."""
    initialize_queue()

    if not input_source.strip():
        return "❌ Please enter a video file path or YouTube URL", get_queue_display()

    output_path = generate_output_path(input_source, resolution)

    job = AppState.queue.add_job(
        input_source=input_source.strip(),
        output_path=output_path,
        preset=preset,
        resolution=resolution,
        quality=quality,
        crf=crf,
        encoder=encoder,
        upscale_engine=upscale_engine,
        hdr_mode=hdr_mode,
        realesrgan_model=realesrgan_model,
        realesrgan_denoise=realesrgan_denoise,
        ffmpeg_scale_algo=ffmpeg_scale_algo,
        hdr_brightness=hdr_brightness,
        hdr_color_depth=hdr_color_depth,
        # RTX Video SDK options
        rtxvideo_artifact_reduction=rtxvideo_artifact_reduction,
        rtxvideo_artifact_strength=rtxvideo_artifact_strength,
        rtxvideo_hdr=rtxvideo_hdr,
        audio_enhance=audio_enhance,
        audio_upmix=audio_upmix,
        audio_layout=audio_layout,
        audio_format=audio_format,
        audio_target_loudness=audio_target_loudness,
        audio_noise_floor=audio_noise_floor,
        demucs_model=demucs_model,
        demucs_device=demucs_device,
        demucs_shifts=demucs_shifts,
        lfe_crossover=lfe_crossover,
        center_mix=center_mix,
        surround_delay=surround_delay,
        lut_file=lut_file if lut_file.strip() else None,
        lut_strength=lut_strength,
        face_restore=face_restore,
        face_model=face_model,
        face_restore_strength=face_restore_strength,
        face_restore_upscale=face_restore_upscale,
        audio_sr_enabled=audio_sr_enabled,
        audio_sr_model=audio_sr_model,
        deinterlace_algorithm=deinterlace_algorithm,
        qtgmc_preset=qtgmc_preset if qtgmc_preset != "none" else None
    )

    AppState.add_log(f"Added to queue: {input_source[:50]}...")

    return f"✅ Added to queue (ID: {job.id})", get_queue_display()


def add_multiple_to_queue(urls_text: str, preset: str, resolution: int,
                          quality: int, crf: int, encoder: str,
                          upscale_engine: str = "auto", hdr_mode: str = "sdr",
                          audio_enhance: str = "none", audio_upmix: str = "none",
                          audio_layout: str = "original", audio_format: str = "aac") -> Tuple[str, str]:
    """Add multiple videos to the queue (uses default advanced settings)."""
    initialize_queue()

    urls = [u.strip() for u in urls_text.strip().split('\n') if u.strip()]

    if not urls:
        return "❌ Please enter at least one URL or file path", get_queue_display()

    added = 0
    for url in urls:
        output_path = generate_output_path(url, resolution)
        AppState.queue.add_job(
            input_source=url,
            output_path=output_path,
            preset=preset,
            resolution=resolution,
            quality=quality,
            crf=crf,
            encoder=encoder,
            upscale_engine=upscale_engine,
            hdr_mode=hdr_mode,
            audio_enhance=audio_enhance,
            audio_upmix=audio_upmix,
            audio_layout=audio_layout,
            audio_format=audio_format
        )
        added += 1

    AppState.add_log(f"Added {added} videos to queue")

    return f"✅ Added {added} videos to queue", get_queue_display()


def start_queue() -> Tuple[str, str]:
    """Start processing the queue."""
    initialize_queue()
    AppState.queue.start_processing()
    AppState.add_log("Queue processing started")
    return "▶️ Processing started", get_queue_display()


def pause_queue() -> Tuple[str, str]:
    """Pause queue processing."""
    initialize_queue()
    AppState.queue.pause_processing()
    AppState.add_log("Queue processing paused")
    return "⏸️ Processing paused", get_queue_display()


def clear_completed() -> Tuple[str, str]:
    """Clear completed jobs from queue."""
    initialize_queue()
    AppState.queue.clear_completed()
    AppState.add_log("Cleared completed jobs")
    return "🗑️ Cleared completed jobs", get_queue_display()


def clear_all_queue() -> Tuple[str, str]:
    """Clear all jobs from queue (stops processing if active)."""
    initialize_queue()
    AppState.queue.pause_processing()
    AppState.queue.clear_all()
    AppState.add_log("Cleared all jobs from queue")
    return "🗑️ Cleared all jobs", get_queue_display()


def get_queue_display() -> str:
    """Generate HTML display of the queue."""
    initialize_queue()

    jobs = AppState.queue.get_all_jobs()
    stats = AppState.queue.get_queue_stats()

    if not jobs:
        return """
        <div style="text-align: center; padding: 40px; color: #666;">
            <h3>📭 Queue is empty</h3>
            <p>Add videos using the form above</p>
        </div>
        """

    html = f"""
    <div style="margin-bottom: 15px; padding: 10px; background: #f0f0f0; border-radius: 8px;">
        <strong>Queue Status:</strong>
        {stats['pending']} pending |
        {stats['processing']} processing |
        {stats['completed']} completed |
        {stats['failed']} failed
    </div>
    """

    for job in jobs:
        status_emoji = get_status_emoji(job.status)
        progress_bar = ""

        if job.status in (JobStatus.DOWNLOADING, JobStatus.PREPROCESSING,
                          JobStatus.UPSCALING, JobStatus.ENCODING):
            progress_bar = f"""
            <div style="background: #e0e0e0; border-radius: 4px; height: 8px; margin-top: 8px;">
                <div style="background: #4CAF50; width: {job.progress}%; height: 100%; border-radius: 4px;"></div>
            </div>
            <div style="font-size: 12px; color: #666; margin-top: 4px;">
                {job.current_stage}: {job.stage_progress:.1f}% | Overall: {job.progress:.1f}%
            </div>
            """

        title_display = job.video_title or job.input_source[:60]
        if len(title_display) > 60:
            title_display = title_display[:57] + "..."

        status_class = {
            JobStatus.COMPLETED: "color: #4CAF50;",
            JobStatus.FAILED: "color: #f44336;",
            JobStatus.CANCELLED: "color: #9e9e9e;",
        }.get(job.status, "color: #2196F3;")

        error_display = ""
        if job.error_message:
            error_display = f'<div style="color: #f44336; font-size: 12px; margin-top: 4px;">Error: {job.error_message}</div>'

        result_display = ""
        if job.status == JobStatus.COMPLETED:
            result_display = f"""
            <div style="font-size: 12px; color: #666; margin-top: 4px;">
                📁 {format_file_size(job.output_size)} | ⏱️ {format_duration(job.processing_time)}
            </div>
            """

        html += f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin-bottom: 10px; background: white;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <strong>{status_emoji} {title_display}</strong>
                    <div style="font-size: 12px; color: #888;">
                        ID: {job.id} | {job.resolution}p | {job.preset} | {job.encoder}
                    </div>
                </div>
                <div style="{status_class} font-weight: bold;">
                    {job.status.value.upper()}
                </div>
            </div>
            {progress_bar}
            {error_display}
            {result_display}
        </div>
        """

    return html


def get_logs_display() -> str:
    """Get formatted logs display."""
    if not AppState.logs:
        return "No logs yet..."
    return "\n".join(reversed(AppState.logs[-50:]))


def get_stats_display() -> str:
    """Generate HTML stats dashboard."""
    initialize_queue()

    stats = AppState.queue.get_queue_stats()
    jobs = AppState.queue.get_all_jobs()

    # Calculate total processing time and output size
    total_time = sum(j.processing_time for j in jobs if j.status == JobStatus.COMPLETED)
    total_size = sum(j.output_size for j in jobs if j.status == JobStatus.COMPLETED)

    # Processing rate
    is_processing = AppState.queue.is_processing()
    status_text = "🟢 Processing" if is_processing else "⏸️ Paused"
    status_color = "#10b981" if is_processing else "#6b7280"

    return f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" style="color: #3b82f6;">{stats['pending']}</div>
            <div class="stat-label">Pending</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #f59e0b;">{stats['processing']}</div>
            <div class="stat-label">Processing</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #10b981;">{stats['completed']}</div>
            <div class="stat-label">Completed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #ef4444;">{stats['failed']}</div>
            <div class="stat-label">Failed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{format_duration(total_time)}</div>
            <div class="stat-label">Total Time</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{format_file_size(total_size)}</div>
            <div class="stat-label">Output Size</div>
        </div>
    </div>
    <div style="text-align: center; padding: 10px; background: #f5f5f5; border-radius: 8px; margin-top: 10px;">
        <span style="color: {status_color}; font-weight: 600;">{status_text}</span>
        <span style="margin-left: 15px; color: #666;">Total Jobs: {stats['total']}</span>
    </div>
    """


def refresh_display() -> Tuple[str, str, str]:
    """Refresh the queue, stats, and logs display."""
    return get_queue_display(), get_stats_display(), get_logs_display()


def set_output_directory(path: str) -> str:
    """Set the output directory."""
    if path.strip():
        AppState.output_dir = Path(path.strip())
        AppState.output_dir.mkdir(parents=True, exist_ok=True)
        return f"✅ Output directory set to: {AppState.output_dir}"
    return "❌ Please enter a valid path"


# =============================================================================
# Build Gradio Interface
# =============================================================================

# =============================================================================
# Quick Fix Preset Configurations
# =============================================================================

def get_quick_fix_presets():
    """Returns quick-fix preset configurations that match best practices."""
    return {
        "vhs_home": {
            "name": "VHS Home Movies",
            "preset": "vhs",
            "resolution": 1080,
            "crf": 18,
            "encoder": "hevc_nvenc",
            "upscale_engine": "auto",
            "face_restore": True,
            "face_model": "gfpgan",
            "face_restore_strength": 0.5,
            "audio_enhance": "voice",
            "audio_upmix": "demucs",
            "audio_layout": "5.1",
            "audio_sr_enabled": True,
            "audio_sr_model": "speech",
            "deinterlace_algorithm": "yadif",
            "info": "Optimized for family VHS tapes with face restoration, AudioSR upsampling, and dialogue enhancement"
        },
        "vhs_noisy": {
            "name": "Noisy VHS",
            "preset": "vhs",
            "resolution": 1080,
            "crf": 18,
            "encoder": "hevc_nvenc",
            "upscale_engine": "realesrgan",
            "realesrgan_model": "realesrgan-x4plus",
            "realesrgan_denoise": 0.8,
            "face_restore": False,
            "audio_enhance": "aggressive",
            "deinterlace_algorithm": "qtgmc",
            "qtgmc_preset": "medium",
            "info": "Heavy denoising for damaged/noisy VHS tapes with QTGMC deinterlacing"
        },
        "dvd_rip": {
            "name": "DVD Rip",
            "preset": "dvd",
            "resolution": 1080,
            "crf": 20,
            "encoder": "hevc_nvenc",
            "upscale_engine": "auto",
            "face_restore": False,
            "audio_enhance": "light",
            "deinterlace_algorithm": "yadif",
            "info": "Light processing for DVD sources with minimal denoise"
        },
        "youtube_old": {
            "name": "Old YouTube",
            "preset": "youtube",
            "resolution": 1080,
            "crf": 20,
            "encoder": "hevc_nvenc",
            "upscale_engine": "realesrgan",
            "face_restore": False,
            "audio_enhance": "moderate",
            "info": "Deblocking and artifact removal for compressed YouTube videos"
        },
        "anime": {
            "name": "Anime/Animation",
            "preset": "clean",
            "resolution": 1080,
            "crf": 18,
            "encoder": "hevc_nvenc",
            "upscale_engine": "realesrgan",
            "realesrgan_model": "realesr-animevideov3",
            "face_restore": False,
            "audio_enhance": "none",
            "info": "Anime-optimized AI model for sharp lines and vibrant colors"
        },
        "webcam": {
            "name": "Webcam Footage",
            "preset": "webcam",
            "resolution": 1080,
            "crf": 20,
            "encoder": "hevc_nvenc",
            "upscale_engine": "auto",
            "face_restore": False,
            "audio_enhance": "voice",
            "info": "Heavy denoise for low-quality webcam footage, no deinterlacing"
        },
        "clean": {
            "name": "Clean Digital",
            "preset": "clean",
            "resolution": 1080,
            "crf": 18,
            "encoder": "hevc_nvenc",
            "upscale_engine": "auto",
            "face_restore": False,
            "audio_enhance": "none",
            "info": "Minimal processing for already clean high-quality sources"
        },
        "best_quality": {
            "name": "Best Quality (Slow)",
            "preset": "vhs",
            "resolution": 1080,
            "crf": 15,
            "quality": 0,
            "encoder": "libx265",
            "upscale_engine": "maxine",
            "face_restore": True,
            "face_model": "codeformer",
            "face_restore_strength": 0.7,
            "audio_enhance": "deepfilternet",
            "audio_upmix": "demucs",
            "audio_layout": "7.1",
            "audio_sr_enabled": True,
            "audio_sr_model": "speech",
            "deinterlace_algorithm": "qtgmc",
            "qtgmc_preset": "slow",
            "info": "Maximum quality settings - QTGMC deinterlace, Maxine upscale, CodeFormer faces, AudioSR + DeepFilterNet audio, 7.1 surround (very slow)"
        }
    }


def get_hardware_defaults() -> Dict[str, Any]:
    """Get optimal defaults based on detected hardware."""
    AppState.detect_hardware_once()

    if not AppState.optimal_config:
        # Fallback defaults for CPU-only
        return {
            "upscale_engine": "ffmpeg",
            "encoder": "libx265",
            "face_restore": False,
            "audio_upmix": "simple"
        }

    return AppState.optimal_config


def get_hardware_info_html() -> str:
    """Generate HTML display for hardware detection."""
    AppState.detect_hardware_once()

    if not AppState.hardware:
        return """
        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; border-radius: 4px; margin: 10px 0;">
            <strong>Hardware Detection:</strong> Unable to detect GPU. Using CPU-only mode.
        </div>
        """

    hw = AppState.hardware
    config = AppState.optimal_config

    # Color code based on GPU capability
    if hw.is_rtx_capable:
        bg_color = "#d1fae5"
        border_color = "#10b981"
        emoji = "✅"
        title_text = "Optimal Hardware Detected"
    elif hw.supports_ai_upscaling:
        bg_color = "#e0f2fe"
        border_color = "#3b82f6"
        emoji = "✓"
        title_text = "Good Hardware Detected"
    elif hw.vendor.value != "cpu":
        bg_color = "#fff3cd"
        border_color = "#ffc107"
        emoji = "⚠"
        title_text = "Limited Hardware"
    else:
        bg_color = "#fee2e2"
        border_color = "#ef4444"
        emoji = "ℹ"
        title_text = "CPU-Only Mode"

    # Build capabilities list
    capabilities = []
    if hw.supports_ai_upscaling:
        capabilities.append("AI Upscaling")
    if hw.supports_hardware_encoding:
        capabilities.append("Hardware Encoding")
    if hw.has_rtx_video_sdk:
        capabilities.append("RTX Video SDK")
    if hw.has_cuda:
        capabilities.append("CUDA")
    if not capabilities:
        capabilities.append("CPU-only Processing")

    capabilities_str = ", ".join(capabilities)

    # Build warnings list
    warnings_html = ""
    if config and config.get('warnings'):
        warnings_list = "<br/>".join([f"• {w}" for w in config['warnings'][:2]])  # Show max 2 warnings
        warnings_html = f"""
        <div style="margin-top: 8px; padding: 8px; background: rgba(255,193,7,0.1); border-radius: 4px; font-size: 12px;">
            {warnings_list}
        </div>
        """

    return f"""
    <div style="background: {bg_color}; border-left: 4px solid {border_color}; padding: 12px; border-radius: 4px; margin: 10px 0;">
        <strong>{emoji} {title_text}:</strong> {hw.display_name}<br/>
        <span style="font-size: 13px; color: #555;">
            <strong>Capabilities:</strong> {capabilities_str}<br/>
            <strong>Auto-Configuration:</strong> {config.get('upscale_engine', 'auto')} engine,
            {config.get('encoder', 'libx265')} encoder,
            {config.get('quality', 'good')} quality mode
        </span>
        {warnings_html}
    </div>
    """


def create_gui() -> gr.Blocks:
    """Create the Gradio interface."""

    # Detect hardware on startup
    AppState.detect_hardware_once()

    # Create custom theme for video processing application
    # Dark theme optimized for video work with cinematic color palette
    custom_theme = gr.themes.Soft(
        primary_hue="violet",        # Vibrant violet for primary actions
        secondary_hue="slate",        # Neutral slate for secondary elements
        neutral_hue="slate",          # Slate for backgrounds
        spacing_size="md",
        radius_size="lg",
        font=("Inter", "system-ui", "sans-serif"),
        font_mono=("Fira Code", "Consolas", "monospace")
    ).set(
        # Core colors - Deep dark backgrounds for video work
        body_background_fill="#0a0f1e",                    # Deep navy background
        body_background_fill_dark="#0a0f1e",
        background_fill_primary="#131b2e",                 # Primary container bg
        background_fill_primary_dark="#131b2e",
        background_fill_secondary="#1a2332",               # Secondary container bg
        background_fill_secondary_dark="#1a2332",

        # Text colors
        body_text_color="#e2e8f0",                         # Light slate text
        body_text_color_dark="#e2e8f0",
        body_text_color_subdued="#94a3b8",                 # Muted text
        body_text_color_subdued_dark="#94a3b8",

        # Borders
        border_color_primary="#2d3748",                    # Subtle borders
        border_color_primary_dark="#2d3748",

        # Buttons
        button_primary_background_fill="#7c3aed",          # Violet primary
        button_primary_background_fill_dark="#7c3aed",
        button_primary_background_fill_hover="#6d28d9",
        button_primary_background_fill_hover_dark="#6d28d9",
        button_primary_text_color="#ffffff",
        button_primary_text_color_dark="#ffffff",

        button_secondary_background_fill="#1e293b",
        button_secondary_background_fill_dark="#1e293b",
        button_secondary_background_fill_hover="#334155",
        button_secondary_background_fill_hover_dark="#334155",
        button_secondary_text_color="#e2e8f0",
        button_secondary_text_color_dark="#e2e8f0",

        # Inputs
        input_background_fill="#1a2332",
        input_background_fill_dark="#1a2332",
        input_background_fill_focus="#1e293b",
        input_background_fill_focus_dark="#1e293b",
        input_border_color="#2d3748",
        input_border_color_dark="#2d3748",
        input_border_color_focus="#7c3aed",
        input_border_color_focus_dark="#7c3aed",

        # Shadow
        shadow_drop="0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)",
        shadow_drop_lg="0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)",
    )

    # Enhanced CSS for modern cinematic look
    custom_css = """
    /* === GLOBAL STYLING === */
    * {
        font-feature-settings: "ss01", "ss02", "cv01", "cv03";
    }

    /* Main container */
    .gradio-container {
        max-width: 1400px !important;
        margin: 0 auto !important;
        background: linear-gradient(to bottom, #0a0f1e 0%, #131b2e 100%) !important;
    }

    /* === HEADER & TYPOGRAPHY === */
    .prose h1 {
        background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
        font-size: 2.5rem !important;
        letter-spacing: -0.025em;
        margin-bottom: 0.5rem !important;
    }

    .prose h3 {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 1.25rem;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }

    /* === TABS === */
    .tab-nav {
        background: #131b2e !important;
        border-bottom: 2px solid #2d3748 !important;
        padding: 0.5rem 0 0 0 !important;
    }

    .tab-nav button {
        font-size: 15px !important;
        font-weight: 500 !important;
        color: #94a3b8 !important;
        background: transparent !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        padding: 0.75rem 1.5rem !important;
        margin: 0 0.25rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
    }

    .tab-nav button:hover {
        color: #e2e8f0 !important;
        background: rgba(124, 58, 237, 0.1) !important;
        border-bottom-color: rgba(124, 58, 237, 0.5) !important;
    }

    .tab-nav button.selected {
        color: #a78bfa !important;
        background: rgba(124, 58, 237, 0.15) !important;
        border-bottom-color: #7c3aed !important;
    }

    /* === CARDS & CONTAINERS === */
    .block {
        border-radius: 12px !important;
        background: linear-gradient(135deg, #131b2e 0%, #1a2332 100%) !important;
        border: 1px solid #2d3748 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }

    .block:hover {
        border-color: #3d4b5f !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3) !important;
    }

    /* === BUTTONS === */
    button.primary, .primary-button {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 8px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.3) !important;
    }

    button.primary:hover, .primary-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 20px -5px rgba(124, 58, 237, 0.5) !important;
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
    }

    button.secondary, .secondary-button {
        background: #1e293b !important;
        border: 1px solid #3d4b5f !important;
        color: #e2e8f0 !important;
        font-weight: 500 !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }

    button.secondary:hover, .secondary-button:hover {
        background: #334155 !important;
        border-color: #4a5568 !important;
    }

    /* === STATUS INDICATORS === */
    .status-completed {
        color: #34d399;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(52, 211, 153, 0.3);
    }

    .status-processing {
        color: #60a5fa;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(96, 165, 250, 0.3);
        animation: pulse-glow 2s ease-in-out infinite;
    }

    .status-failed {
        color: #f87171;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(248, 113, 113, 0.3);
    }

    .status-pending {
        color: #94a3b8;
        font-weight: 500;
    }

    @keyframes pulse-glow {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    /* Progress bar animation */
    @keyframes progress-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    .progress-active {
        animation: progress-pulse 1.5s ease-in-out infinite;
    }

    /* Queue item styling */
    .queue-item {
        transition: all 0.2s ease;
        border-left: 4px solid transparent;
        background: var(--bg-card);
        border-radius: 8px;
        margin-bottom: 10px;
        padding: 12px;
    }
    .queue-item:hover {
        border-left-color: #667eea;
        background: var(--bg-secondary);
    }

    /* Version badge */
    .version-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }

    /* File upload zone */
    .upload-zone {
        border: 2px dashed var(--border-color);
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        transition: all 0.3s ease;
        background: var(--bg-secondary);
    }
    .upload-zone:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.05);
    }

    /* Video preview */
    .video-preview {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 12px var(--shadow-color);
    }

    /* Info cards */
    .info-card {
        background: var(--bg-secondary);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }

    /* Dark mode toggle */
    .dark-mode-toggle {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 1000;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .dark-mode-toggle:hover {
        transform: scale(1.1);
    }

    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 15px;
        margin: 15px 0;
    }
    .stat-card {
        background: var(--bg-secondary);
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .stat-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--text-primary);
    }
    .stat-label {
        font-size: 12px;
        color: var(--text-secondary);
        text-transform: uppercase;
    }

    /* Notification toast */
    .toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 8px;
        background: var(--bg-card);
        box-shadow: 0 4px 20px var(--shadow-color);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    }
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    """

    with gr.Blocks(
        title="VHS Upscaler"
    ) as app:

        # Header with version badge
        gr.Markdown(f"""
        # 🎬 VHS Video Upscaler
        ### AI-Powered Video Enhancement with RTX Video SDK <span class="version-badge">v{__version__}</span>

        Transform vintage VHS tapes, DVDs, and low-quality videos into stunning HD/4K using RTX GPU acceleration.
        Supports **YouTube URLs**, **local files**, and **drag-and-drop upload** with batch processing.
        """)

        # Hardware detection display
        hardware_info = gr.HTML(value=get_hardware_info_html(), elem_classes="hardware-info")

        # Mode toggle at the top
        with gr.Row():
            with gr.Column(scale=2):
                mode_toggle = gr.Radio(
                    choices=["🎯 Basic Mode", "⚙️ Advanced Mode"],
                    value="🎯 Basic Mode",
                    label="Interface Mode",
                    info="Basic Mode: Simple 3-click workflow. Advanced Mode: Full control over all settings."
                )
            with gr.Column(scale=1):
                gr.Markdown("""
                <div style="background: #e7f3ff; padding: 10px; border-radius: 6px; margin-top: 8px;">
                    <strong>Basic Mode:</strong> Perfect for beginners - just upload, pick a preset, and process!
                </div>
                """)

        with gr.Tabs():
            # =====================================================================
            # Tab 1: Single Video
            # =====================================================================
            with gr.TabItem("📹 Single Video", id=1):
                with gr.Row():
                    with gr.Column(scale=3):
                        # ==================== INPUT SECTION (Always visible) ====================
                        gr.Markdown("### 📥 Input Source")

                        # Tab group for input methods
                        with gr.Tabs() as input_tabs:
                            with gr.TabItem("📁 Upload File"):
                                file_upload = gr.File(
                                    label="Drag & Drop Video File",
                                    file_types=["video"],
                                    file_count="single",
                                    type="filepath",
                                    elem_classes="upload-zone"
                                )
                                file_preview = gr.HTML(
                                    value="<div class='info-card' style='text-align: center; padding: 20px;'><p style='color: #666; font-size: 14px;'>📤 Upload a video file to see details</p></div>",
                                    label="Video Info"
                                )

                            with gr.TabItem("🔗 URL / Path"):
                                input_source = gr.Textbox(
                                    label="Video Source",
                                    placeholder="https://youtube.com/watch?v=... or /path/to/video.mp4",
                                    info="Supports YouTube, local files (.mp4, .avi, .mkv, .mov, .vob)",
                                    lines=2
                                )

                        # Hidden textbox to hold the final input path
                        final_input = gr.Textbox(visible=False, value="")

                        # ==================== BASIC MODE UI ====================
                        with gr.Group(visible=True) as basic_mode_ui:
                            gr.Markdown("---")
                            gr.Markdown("### 🎯 Simple Preset Selection")
                            gr.Markdown("""
                            <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 12px; border-radius: 4px; margin: 10px 0;">
                                <strong>Pick your video type below:</strong> We'll automatically apply the best settings for optimal results.
                            </div>
                            """)

                            basic_preset = gr.Radio(
                                choices=[
                                    "📼 Old VHS tape (home movies, family recordings)",
                                    "💿 DVD movie",
                                    "📺 YouTube video",
                                    "🎥 Recent digital video (phone, camera)"
                                ],
                                value="📼 Old VHS tape (home movies, family recordings)",
                                label="What type of video are you restoring?",
                                info="⭐ Recommended: VHS tape for old home movies"
                            )

                            gr.Markdown("---")
                            basic_quality = gr.Radio(
                                choices=[
                                    "Good (Fast, smaller file)",
                                    "Better (Balanced)",
                                    "Best (Slow, larger file)"
                                ],
                                value="Better (Balanced)",
                                label="Output Quality",
                                info="'Better' is recommended for most videos"
                            )

                            gr.Markdown("---")
                            basic_process_btn = gr.Button(
                                "🚀 Process Video",
                                variant="primary",
                                size="lg",
                                elem_classes="primary"
                            )

                            gr.Markdown("""
                            <div style="background: #fef3c7; padding: 10px; border-radius: 6px; margin-top: 10px; font-size: 13px;">
                                <strong>💡 What will happen:</strong><br/>
                                • VHS: AI upscaling, face restoration, audio cleanup, surround sound<br/>
                                • DVD: Smart upscaling with light cleanup<br/>
                                • YouTube: Remove compression artifacts<br/>
                                • Digital: Minimal processing, just upscale
                            </div>
                            """)

                        # ==================== ADVANCED MODE UI ====================
                        with gr.Group(visible=False) as advanced_mode_ui:
                            # ==================== QUICK FIX PRESETS ====================
                            gr.Markdown("---")
                            gr.Markdown("### 🎯 Quick Fix Presets")
                            gr.Markdown("<p style='color: #666; font-size: 13px; margin-top: -10px;'>One-click optimal settings for common scenarios</p>")

                            with gr.Row():
                                btn_vhs_home = gr.Button("📼 VHS Home Movies", size="sm", variant="secondary", scale=1)
                                btn_vhs_noisy = gr.Button("🔊 Noisy VHS", size="sm", variant="secondary", scale=1)
                                btn_dvd_rip = gr.Button("💿 DVD Rip", size="sm", variant="secondary", scale=1)
                                btn_youtube_old = gr.Button("📺 Old YouTube", size="sm", variant="secondary", scale=1)
                            with gr.Row():
                                btn_anime = gr.Button("🎨 Anime", size="sm", variant="secondary", scale=1)
                                btn_webcam = gr.Button("🎥 Webcam", size="sm", variant="secondary", scale=1)
                                btn_clean = gr.Button("✨ Clean Digital", size="sm", variant="secondary", scale=1)
                                btn_best_quality = gr.Button("⭐ Best Quality (Slow)", size="sm", variant="primary", scale=1)

                            # ==================== BASIC SETTINGS ====================
                            gr.Markdown("---")
                            gr.Markdown("### ⚙️ Basic Settings")

                            # Get hardware-optimal defaults
                            hw_defaults = get_hardware_defaults()

                            with gr.Row():
                                preset = gr.Dropdown(
                                    choices=[
                                        ("VHS Tapes", "vhs"),
                                        ("DVD Movies", "dvd"),
                                        ("Webcam Videos", "webcam"),
                                        ("YouTube Videos", "youtube"),
                                        ("Clean/Modern Video", "clean"),
                                        ("Auto-Detect (Recommended)", "auto")
                                    ],
                                    value="vhs",
                                    label="What Type of Video Are You Restoring?",
                                    info="Chooses the best cleanup settings for your video source. VHS removes static and scan lines, DVD fixes compression artifacts.",
                                    scale=1
                                )
                                resolution = gr.Dropdown(
                                    choices=[
                                        ("720p (HD Ready - Smaller Files)", 720),
                                        ("1080p (Full HD - Recommended)", 1080),
                                        ("1440p (2K - For Large Screens)", 1440),
                                        ("2160p (4K - For 4K TVs)", 2160)
                                    ],
                                    value=1080,
                                    label="Output Resolution",
                                    info="1080p is perfect for most VHS and DVD restorations. Choose 4K only if you have a 4K TV. Higher resolution = longer processing time and larger files.",
                                    scale=1
                                )
                                upscale_engine = gr.Dropdown(
                                    choices=[
                                        ("Automatic (Recommended)", "auto"),
                                        ("NVIDIA RTX - Best Quality", "rtxvideo"),
                                        ("AI Upscaling - All GPUs", "realesrgan"),
                                        ("Basic - No GPU Required", "ffmpeg")
                                    ],
                                    value=hw_defaults.get('upscale_engine', 'auto'),
                                    label="Video Enhancement Method",
                                    info="How to improve video quality. Automatic selects the best option for your computer. RTX gives the best results but requires NVIDIA RTX 20-series or newer graphics card.",
                                    scale=1
                                )

                        # ==================== ADVANCED OPTIONS ====================
                        gr.Markdown("---")
                        with gr.Accordion("⚙️ Encoding & Quality Settings", open=False):
                            gr.Markdown("**Video Encoder & Quality Control**")
                            with gr.Row():
                                encoder = gr.Dropdown(
                                    choices=[
                                        ("Fast + Small Files (NVIDIA GPU)", "hevc_nvenc"),
                                        ("Fast + Compatible (NVIDIA GPU)", "h264_nvenc"),
                                        ("Slow + Small Files (Any Computer)", "libx265"),
                                        ("Slow + Compatible (Any Computer)", "libx264")
                                    ],
                                    value=hw_defaults.get('encoder', 'hevc_nvenc'),
                                    label="Encoding Speed & Compatibility",
                                    info="NVIDIA GPU options are 10-20× faster. First option creates smallest files. Second option works on more devices (older phones, TVs). Choose 'Any Computer' options if you don't have NVIDIA graphics card.",
                                    scale=2
                                )
                                quality = gr.Radio(
                                    choices=[
                                        ("Maximum Quality (Slower)", 0),
                                        ("Balanced (Faster)", 1)
                                    ],
                                    value=0 if hw_defaults.get('quality', 'good') == 'best' else 1,
                                    label="Processing Speed vs Quality",
                                    info="Maximum Quality takes longer but produces the best results. Balanced is faster while still maintaining good quality. Recommended: Maximum Quality for archival, Balanced for quick previews.",
                                    scale=1
                                )
                            with gr.Row():
                                crf = gr.Slider(
                                    minimum=15,
                                    maximum=28,
                                    value=20,
                                    step=1,
                                    label="Quality vs File Size Balance",
                                    info="Lower numbers = better quality but bigger files. 18-20 recommended for VHS/DVD (excellent quality, reasonable size). 15 for archival/preservation (huge files). 23-25 for web uploads (smaller files, good quality)."
                                )

                        with gr.Accordion("🎨 AI Upscaler Settings", open=False):
                            gr.Markdown("**Engine-specific settings appear below based on your AI Upscaler selection**")

                            # === Conditional: RTX Video SDK Options (v1.5.1+) ===
                            with gr.Group(visible=False) as rtxvideo_options:
                                gr.Markdown("""
                                <div style="background: #e7f3ff; border-left: 4px solid #2196F3; padding: 12px; border-radius: 4px; margin: 10px 0;">
                                    <strong>🚀 RTX Video SDK Settings</strong><br/>
                                    <span style="font-size: 13px; color: #555;">AI upscaling with artifact reduction and SDR-to-HDR conversion. Requires RTX 20 series GPU or newer.</span>
                                </div>
                                """)
                                with gr.Row():
                                    rtxvideo_artifact_reduction = gr.Checkbox(
                                        label="Remove Video Defects",
                                        value=True,
                                        info="Fixes blocky compression artifacts, static, and scan lines. Essential for VHS tapes and DVDs. Turn off only for modern, clean digital videos.",
                                        scale=1
                                    )
                                with gr.Row():
                                    rtxvideo_artifact_strength = gr.Slider(
                                        minimum=0.0, maximum=1.0, value=0.5, step=0.1,
                                        label="Cleanup Strength",
                                        info="How aggressively to remove defects. Old VHS tapes: 0.7-1.0 (maximum). DVDs: 0.3-0.5 (moderate). Slightly damaged: 0.1-0.2 (light touch).",
                                        visible=True
                                    )
                                with gr.Row():
                                    rtxvideo_hdr = gr.Checkbox(
                                        label="Convert to High Dynamic Range (HDR)",
                                        value=False,
                                        info="Makes videos look better on modern 4K HDR TVs with brighter highlights and richer colors. Turn OFF for: web uploads (YouTube, Vimeo), older TVs, or if you're unsure."
                                    )

                            # === Conditional: Real-ESRGAN Options ===
                            with gr.Group(visible=False) as realesrgan_options:
                                gr.Markdown("""
                                <div style="background: #fff3e0; border-left: 4px solid #ff9800; padding: 12px; border-radius: 4px; margin: 10px 0;">
                                    <strong>🎨 Real-ESRGAN Settings</strong><br/>
                                    <span style="font-size: 13px; color: #555;">Cross-platform AI upscaling for AMD, Intel, and NVIDIA GPUs. Excellent for noisy VHS footage.</span>
                                </div>
                                """)
                                with gr.Row():
                                    realesrgan_model = gr.Dropdown(
                                        choices=[
                                            ("Real People/VHS (Recommended)", "realesrgan-x4plus"),
                                            ("Anime/Cartoons - Sharp", "realesrgan-x4plus-anime"),
                                            ("Anime Series - Smooth", "realesr-animevideov3"),
                                            ("Photos/Clean Video", "realesrnet-x4plus")
                                        ],
                                        value="realesrgan-x4plus",
                                        label="What's in Your Video?",
                                        info="Choose based on video content. 'Real People' works for home videos, VHS tapes, and documentaries. 'Anime' options are for animated content only.",
                                        scale=2
                                    )
                                    realesrgan_denoise = gr.Slider(
                                        minimum=0, maximum=1, value=0.5, step=0.1,
                                        label="Static & Noise Removal",
                                        info="How much to clean up grainy/static footage. Old VHS tapes: 0.7-1.0 (heavy cleanup). DVDs: 0.3-0.5 (moderate). Clean videos or film grain: 0 (no cleanup).",
                                        scale=2
                                    )

                            # === Conditional: FFmpeg Upscale Options ===
                            with gr.Group(visible=False) as ffmpeg_options:
                                gr.Markdown("""
                                <div style="background: #f3f4f6; border-left: 4px solid #6b7280; padding: 12px; border-radius: 4px; margin: 10px 0;">
                                    <strong>🔧 FFmpeg Upscale Settings</strong><br/>
                                    <span style="font-size: 13px; color: #555;">CPU-based traditional upscaling. Use when no GPU is available or for clean sources.</span>
                                </div>
                                """)
                                with gr.Row():
                                    ffmpeg_scale_algo = gr.Dropdown(
                                        choices=[
                                            ("Sharp & Detailed (Recommended)", "lanczos"),
                                            ("Soft & Smooth", "bicubic"),
                                            ("Fast & Basic", "bilinear"),
                                            ("Balanced", "spline"),
                                            ("Pixel Art Only", "neighbor")
                                        ],
                                        value="lanczos",
                                        label="Upscaling Style",
                                        info="Sharp gives the best results for photos and videos. Soft creates a vintage film look. Choose Pixel Art ONLY for retro games/graphics.",
                                        scale=2
                                    )

                        with gr.Accordion("🌈 HDR & Color Settings", open=False):
                            with gr.Row():
                                hdr_mode = gr.Dropdown(
                                    choices=[
                                        ("Standard (Works Everywhere)", "sdr"),
                                        ("HDR for Modern TVs", "hdr10"),
                                        ("HDR for Broadcasting", "hlg")
                                    ],
                                    value="sdr",
                                    label="Display Type",
                                    info="Standard works on all devices (phones, computers, old TVs). Choose 'HDR for Modern TVs' only if you have a 4K HDR TV. Leave on Standard if unsure.",
                                    scale=1
                                )

                            # === Conditional: HDR Options ===
                            with gr.Group(visible=False) as hdr_options:
                                gr.Markdown("""
                                <div style="background: #fce7f3; border-left: 4px solid #ec4899; padding: 12px; border-radius: 4px; margin: 10px 0;">
                                    <strong>🎨 HDR Conversion Settings</strong><br/>
                                    <span style="font-size: 13px; color: #555;">Configure SDR to HDR conversion for modern TVs. Skip for web uploads or older displays.</span>
                                </div>
                                """)
                                with gr.Row():
                                    hdr_brightness = gr.Slider(
                                        minimum=100, maximum=1000, value=400, step=50,
                                        label="TV Brightness Level",
                                        info="Match your TV's brightness capability. Budget TVs: 400. Mid-range TVs: 600. Premium/OLED TVs: 1000. Check your TV's manual or box for 'peak brightness' or 'nits'.",
                                        scale=2
                                    )
                                    hdr_color_depth = gr.Radio(
                                        choices=[
                                            ("Standard (8-bit)", 8),
                                            ("High Quality (10-bit - Recommended for HDR)", 10)
                                        ],
                                        value=10,
                                        label="Color Quality",
                                        info="10-bit creates smoother color gradients and is required for HDR. Use 8-bit only for compatibility with very old devices.",
                                        scale=1
                                    )

                            # LUT Color Grading
                            gr.Markdown("---")
                            gr.Markdown("**🎨 LUT Color Grading** - Apply cinematic color grading with .cube LUT files")
                            with gr.Row():
                                lut_file = gr.Textbox(
                                    label="Color Grading File (Optional)",
                                    placeholder="Path to .cube color grading file (e.g., luts/vhs_restore.cube)",
                                    info="Advanced: Apply professional color corrections. Leave empty if you don't have a .cube file. Great for fixing faded VHS colors or adding cinematic looks."
                                )
                                lut_strength = gr.Slider(
                                    minimum=0.0, maximum=1.0, value=1.0, step=0.1,
                                    label="Color Grading Intensity",
                                    info="How strongly to apply color corrections. 1.0 for full effect (recommended). 0.5-0.7 for subtle touch-ups."
                                )

                        with gr.Accordion("👤 Face Restoration", open=False):
                            gr.Markdown("**AI-powered face enhancement using GFPGAN or CodeFormer**")
                            with gr.Row():
                                face_restore = gr.Checkbox(
                                    label="Enhance Faces with AI",
                                    value=False,
                                    info="Automatically improves blurry or damaged faces in home videos. Great for old family VHS tapes where faces are out of focus or degraded."
                                )
                                face_model = gr.Dropdown(
                                    choices=[
                                        ("Balanced (Faster)", "gfpgan"),
                                        ("Maximum Quality (Slower)", "codeformer")
                                    ],
                                    value="gfpgan",
                                    label="Face Enhancement Quality",
                                    info="Balanced works well for most videos. Choose Maximum Quality for important family memories or severely damaged faces."
                                )

                            # === Conditional: Face Restoration Options ===
                            with gr.Group(visible=False) as face_restore_options:
                                with gr.Row():
                                    face_restore_strength = gr.Slider(
                                        minimum=0.0, maximum=1.0, value=0.5, step=0.1,
                                        label="Face Enhancement Amount",
                                        info="How much to improve faces. 0.5 balances natural look with enhancement. 0.8-1.0 for very blurry or damaged faces. Lower values (0.2-0.4) for subtle improvements."
                                    )
                                    face_restore_upscale = gr.Radio(
                                        choices=[
                                            ("Normal - No Enlargement", 1),
                                            ("2× Larger (Recommended)", 2),
                                            ("4× Larger - For Distant Faces", 4)
                                        ],
                                        value=2,
                                        label="Face Enlargement",
                                        info="How much to enlarge faces for better detail. 2× recommended for normal home videos. Use 4× only if faces are very small or far away in the frame."
                                    )

                        with gr.Accordion("📼 Deinterlacing", open=False):
                            gr.Markdown("**Remove interlacing artifacts from VHS/DVD/broadcast sources**")
                            with gr.Row():
                                deinterlace_algorithm = gr.Dropdown(
                                    choices=[
                                        ("Fast & Good (Recommended)", "yadif"),
                                        ("Better Quality", "bwdif"),
                                        ("Alternative Better Quality", "w3fdif"),
                                        ("Maximum Quality (Very Slow)", "qtgmc")
                                    ],
                                    value="yadif",
                                    label="Scan Line Removal Method",
                                    info="Removes horizontal lines (combing) from VHS tapes and old camcorder footage. Fast & Good works for most videos. Use Maximum Quality for important archival projects."
                                )

                            # === Conditional: QTGMC Options ===
                            with gr.Group(visible=False) as qtgmc_options:
                                with gr.Row():
                                    qtgmc_preset = gr.Dropdown(
                                        choices=[
                                            ("Quick Preview", "draft"),
                                            ("Balanced (Recommended)", "medium"),
                                            ("High Quality", "slow"),
                                            ("Archival Quality (Very Slow)", "very_slow")
                                        ],
                                        value="medium",
                                        label="Deinterlacing Quality Level",
                                        info="Balanced gives excellent results for most VHS tapes. Use Archival Quality only for precious family memories or professional restoration projects."
                                    )

                        with gr.Accordion("🔊 Audio Processing", open=False):
                            gr.Markdown("""
                            <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 10px; border-radius: 4px; margin-bottom: 15px;">
                                <strong>Audio Enhancement & Upmixing</strong><br/>
                                <span style="font-size: 13px; color: #555;">Clean up audio, reduce noise, and create surround sound from stereo sources.</span>
                            </div>
                            """)

                            gr.Markdown("**Basic Audio Settings**")
                            with gr.Row():
                                audio_enhance = gr.Dropdown(
                                    choices=[
                                        ("No Cleanup", "none"),
                                        ("Light Cleanup", "light"),
                                        ("Moderate Cleanup", "moderate"),
                                        ("Heavy Cleanup", "aggressive"),
                                        ("Voice/Dialogue Focus", "voice"),
                                        ("Music Preservation", "music"),
                                        ("Maximum AI Cleanup (Best)", "deepfilternet")
                                    ],
                                    value="none",
                                    label="Background Noise Removal",
                                    info="Removes hiss, static, and background noise. VHS home videos: choose Voice Focus or Heavy Cleanup. Music/concerts: choose Music Preservation. Maximum AI Cleanup gives the best results but takes longer.",
                                    scale=2
                                )
                                audio_format = gr.Dropdown(
                                    choices=[
                                        ("AAC - Streaming & Mobile (Recommended)", "aac"),
                                        ("AC3 - DVD Standard", "ac3"),
                                        ("Enhanced AC3 - Home Theater 5.1", "eac3"),
                                        ("DTS - Premium Surround", "dts"),
                                        ("FLAC - Lossless Archival", "flac")
                                    ],
                                    value="aac",
                                    label="Audio Format",
                                    info="AAC recommended for most uses (YouTube, phones, computers). Enhanced AC3 for home theater surround sound. FLAC for archival preservation (largest files, perfect quality).",
                                    scale=1
                                )

                            with gr.Row():
                                audio_upmix = gr.Dropdown(
                                    choices=[
                                        ("Keep Original Audio", "none"),
                                        ("Basic Surround", "simple"),
                                        ("Enhanced Surround", "surround"),
                                        ("Dolby Pro Logic", "prologic"),
                                        ("AI Surround (Best Quality)", "demucs")
                                    ],
                                    value="none",
                                    label="Create Surround Sound",
                                    info="Converts stereo (2-speaker) to surround sound (5.1/7.1 speakers). AI Surround gives the best results. Dolby Pro Logic is good for movies. Keep Original for headphones or 2-speaker setups.",
                                    scale=2
                                )
                                audio_layout = gr.Dropdown(
                                    choices=[
                                        ("Keep Original", "original"),
                                        ("Stereo (2 Speakers/Headphones)", "stereo"),
                                        ("5.1 Surround (Home Theater)", "5.1"),
                                        ("7.1 Surround (Premium Theater)", "7.1"),
                                        ("Mono (Single Speaker)", "mono")
                                    ],
                                    value="original",
                                    label="Speaker Configuration",
                                    info="Choose based on your playback setup. 5.1 for home theater systems. Stereo for computers, phones, or headphones. Keep Original to preserve the video's original audio.",
                                    scale=1
                                )

                            gr.Markdown("---")
                            gr.Markdown("**AI Audio Enhancement**")
                            with gr.Row():
                                audio_sr_enabled = gr.Checkbox(
                                    label="Improve Audio Quality with AI",
                                    value=False,
                                    info="Uses AI to enhance low-quality audio. Great for VHS tapes and old recordings. Improves clarity and reduces muddiness."
                                )
                                audio_sr_model = gr.Dropdown(
                                    choices=[
                                        ("General Purpose", "basic"),
                                        ("Voice & Dialogue (VHS)", "speech"),
                                        ("Music & Concerts", "music")
                                    ],
                                    value="speech",
                                    label="Audio Enhancement Type",
                                    info="Choose based on audio content. Voice & Dialogue for home videos and VHS tapes. Music for concert recordings. General for mixed content.",
                                    visible=False,
                                    scale=2
                                )

                            # === Conditional: Audio Enhancement Options ===
                            with gr.Group(visible=False) as audio_enhance_options:
                                gr.Markdown("**🎚️ Advanced Audio Cleanup** - Fine-tune noise removal and volume normalization")
                                with gr.Row():
                                    audio_target_loudness = gr.Slider(
                                        minimum=-24, maximum=-9, value=-14, step=1,
                                        label="Volume Level",
                                        info="Sets overall volume. -14 recommended for YouTube and streaming. -16 for TV broadcasts. -23 for cinema (wider quiet-to-loud range). More negative = quieter."
                                    )
                                    audio_noise_floor = gr.Slider(
                                        minimum=-30, maximum=-10, value=-20, step=1,
                                        label="Noise Removal Threshold",
                                        info="How quiet a sound must be to remove it. VHS tapes with heavy hiss: -25 to -30. Light background noise: -15 to -20. Clean audio: -10. More negative = removes quieter sounds."
                                    )

                            # === Conditional: Demucs Options ===
                            with gr.Group(visible=False) as demucs_options:
                                gr.Markdown("**🤖 Demucs AI Stem Separation** - Best for movies/music with complex audio")
                                with gr.Row():
                                    demucs_model = gr.Dropdown(
                                        choices=[
                                            ("Balanced (Recommended)", "htdemucs"),
                                            ("Maximum Quality", "htdemucs_ft"),
                                            ("Alternative Model", "mdx_extra"),
                                            ("Alternative High Quality", "mdx_extra_q")
                                        ],
                                        value="htdemucs",
                                        label="AI Processing Quality",
                                        info="Balanced gives excellent results with reasonable speed. Choose Maximum Quality for important projects or severely damaged audio."
                                    )
                                    demucs_device = gr.Dropdown(
                                        choices=[
                                            ("Automatic (Recommended)", "auto"),
                                            ("Force GPU (If Available)", "cuda"),
                                            ("Force CPU (Slower)", "cpu")
                                        ],
                                        value="auto",
                                        label="Processing Hardware",
                                        info="Automatic uses your graphics card (GPU) if available for faster processing, otherwise uses regular processor (CPU). Leave on Automatic unless troubleshooting."
                                    )
                                with gr.Row():
                                    demucs_shifts = gr.Slider(
                                        minimum=0, maximum=5, value=1, step=1,
                                        label="Audio Processing Passes",
                                        info="How many times to process audio for better quality. 1 is optimal for most videos. 2-3 for higher quality (takes longer). 0 for quick preview."
                                    )

                            # === Conditional: Surround Options ===
                            with gr.Group(visible=False) as surround_options:
                                gr.Markdown("**🔊 Surround Sound Configuration** - Adjust speaker balance and placement")
                                with gr.Row():
                                    lfe_crossover = gr.Slider(
                                        minimum=60, maximum=200, value=120, step=10,
                                        label="Bass Frequency Cutoff",
                                        info="Which sounds go to the subwoofer. 80 for large home theater speakers. 120 for typical setups (recommended). 150-200 for small satellite speakers."
                                    )
                                    center_mix = gr.Slider(
                                        minimum=0.0, maximum=1.0, value=0.707, step=0.05,
                                        label="Dialogue Speaker Volume",
                                        info="Controls center speaker volume (where dialogue comes from). 0.707 is standard. 0.8-1.0 to boost dialogue for clearer voices. 0.5 for music-focused content."
                                    )
                                with gr.Row():
                                    surround_delay = gr.Slider(
                                        minimum=0, maximum=50, value=15, step=5,
                                        label="Rear Speaker Delay",
                                        info="Milliseconds to delay rear speakers for better spatial effect. 15-20 for movies (recommended). 0-5 for music. 30-50 for live concert recordings."
                                    )

                            # ==================== ACTION BUTTON (Advanced) ====================
                            gr.Markdown("---")
                            add_btn = gr.Button(
                                "➕ Add to Queue",
                                variant="primary",
                                size="lg",
                                elem_classes="primary"
                            )

                        # ==================== STATUS MESSAGE (Always visible) ====================
                        status_msg = gr.Textbox(
                            label="Status",
                            interactive=False,
                            show_label=False,
                            container=False
                        )

                    with gr.Column(scale=2):
                        # ==================== HELP SIDEBAR ====================
                        gr.Markdown("""
                        <div style="position: sticky; top: 20px;">

                        ### 📖 Quick Reference

                        <div style="background: #f9fafb; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <strong>🎯 Video Source Types</strong>
                        <ul style="margin: 10px 0; padding-left: 20px; font-size: 13px;">
                            <li><strong>VHS</strong> - Old VHS tapes (removes static, scan lines, noise)</li>
                            <li><strong>DVD</strong> - DVD movies (fixes compression, moderate cleanup)</li>
                            <li><strong>Webcam</strong> - Low-quality webcam recordings</li>
                            <li><strong>YouTube</strong> - Downloaded YouTube videos</li>
                            <li><strong>Clean</strong> - Modern high-quality videos</li>
                            <li><strong>Auto</strong> - Let the system detect automatically</li>
                        </ul>
                        </div>

                        <div style="background: #e7f3ff; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <strong>🚀 Enhancement Methods</strong>
                        <ul style="margin: 10px 0; padding-left: 20px; font-size: 13px;">
                            <li><strong>NVIDIA RTX</strong> - For RTX graphics cards (best quality, removes defects)</li>
                            <li><strong>AI Upscaling</strong> - Works on all graphics cards (great for noisy videos)</li>
                            <li><strong>Basic</strong> - For computers without graphics cards</li>
                            <li><strong>Automatic</strong> - Automatically picks the best option for you</li>
                        </ul>
                        </div>

                        <div style="background: #f0fdf4; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <strong>🔊 Audio Tips</strong>
                        <ul style="margin: 10px 0; padding-left: 20px; font-size: 13px;">
                            <li><strong>VHS Tapes</strong> → Voice Focus + AI Enhancement</li>
                            <li><strong>Very Noisy</strong> → Maximum AI Cleanup (best results)</li>
                            <li><strong>Movies</strong> → AI Surround Sound (creates 5.1)</li>
                            <li><strong>Music</strong> → Dolby Pro Logic or Keep Original</li>
                            <li><strong>Format</strong> → AAC for streaming, Enhanced AC3 for home theater</li>
                        </ul>
                        </div>

                        <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <strong>💡 Pro Tips</strong>
                        <ul style="margin: 10px 0; padding-left: 20px; font-size: 13px;">
                            <li><strong>Resolution</strong> - 1080p perfect for VHS and DVD</li>
                            <li><strong>Quality Setting</strong> - 20 gives excellent results</li>
                            <li><strong>File Size</strong> - Fast encoding creates 50% smaller files</li>
                            <li><strong>HDR</strong> - Only use for modern 4K HDR TVs</li>
                            <li><strong>Face Enhancement</strong> - Turn on for old family videos</li>
                        </ul>
                        </div>

                        <div style="background: #fce7f3; padding: 15px; border-radius: 8px;">
                        <strong>⚠️ No Graphics Card?</strong>
                        <p style="font-size: 13px; margin: 10px 0;">
                        • Use <strong>AI Upscaling</strong> (works on AMD/Intel graphics)<br/>
                        • Or <strong>Basic</strong> (no graphics card needed)<br/>
                        • Select <strong>Slow + Small Files</strong> encoding<br/>
                        • Processing will be slower but works on any computer!
                        </p>
                        </div>

                        </div>
                        """)

            # =====================================================================
            # Tab 2: Batch Processing
            # =====================================================================
            with gr.TabItem("📚 Batch Processing", id=2):
                gr.Markdown("### Add Multiple Videos")
                gr.Markdown("Enter one URL or file path per line:")

                batch_input = gr.Textbox(
                    label="Video URLs/Paths",
                    placeholder="https://youtube.com/watch?v=...\nhttps://youtu.be/...\n/path/to/video.mp4",
                    lines=8
                )

                with gr.Row():
                    batch_preset = gr.Dropdown(
                        choices=["vhs", "dvd", "webcam", "youtube", "clean", "auto"],
                        value="youtube",
                        label="Preset"
                    )
                    batch_resolution = gr.Dropdown(
                        choices=[720, 1080, 1440, 2160],
                        value=1080,
                        label="Resolution"
                    )
                    batch_quality = gr.Radio(choices=[0, 1], value=0, label="Quality")
                    batch_crf = gr.Slider(15, 28, value=20, step=1, label="CRF")
                with gr.Row():
                    batch_encoder = gr.Dropdown(
                        choices=["hevc_nvenc", "h264_nvenc", "libx265", "libx264"],
                        value="hevc_nvenc",
                        label="Encoder"
                    )
                    batch_engine = gr.Dropdown(
                        choices=["auto", "maxine", "realesrgan", "ffmpeg"],
                        value="auto",
                        label="Upscale Engine"
                    )
                    batch_hdr = gr.Dropdown(
                        choices=["sdr", "hdr10", "hlg"],
                        value="sdr",
                        label="HDR Mode"
                    )

                batch_add_btn = gr.Button("➕ Add All to Queue", variant="primary", size="lg")
                batch_status = gr.Textbox(label="Status", interactive=False)

            # =====================================================================
            # Tab 3: Queue
            # =====================================================================
            with gr.TabItem("📋 Queue", id=3):
                # Stats dashboard
                gr.Markdown("### Queue Overview")
                stats_display = gr.HTML(
                    value=get_stats_display(),
                    label="Statistics"
                )

                with gr.Row():
                    start_btn = gr.Button("▶️ Start Processing", variant="primary", size="lg")
                    pause_btn = gr.Button("⏸️ Pause", variant="secondary")
                    clear_btn = gr.Button("🗑️ Clear Completed", variant="secondary")
                    clear_all_btn = gr.Button("🗑️ Clear All", variant="stop")
                    refresh_btn = gr.Button("🔄 Refresh", variant="secondary")

                gr.Markdown("### Job Queue")
                queue_display = gr.HTML(
                    value=get_queue_display(),
                    label="Queue"
                )

                queue_status = gr.Textbox(label="Status", interactive=False, visible=False)

            # =====================================================================
            # Tab 4: Logs
            # =====================================================================
            with gr.TabItem("📜 Logs", id=4):
                logs_display = gr.Textbox(
                    value=get_logs_display(),
                    label="Activity Log",
                    lines=20,
                    max_lines=30,
                    interactive=False
                )
                logs_refresh_btn = gr.Button("🔄 Refresh Logs")

            # =====================================================================
            # Tab 5: Settings
            # =====================================================================
            with gr.TabItem("⚙️ Settings", id=5):
                gr.Markdown("### Output Settings")

                with gr.Row():
                    output_dir_input = gr.Textbox(
                        value=str(AppState.output_dir),
                        label="Output Directory",
                        info="Where processed videos will be saved"
                    )
                    output_dir_btn = gr.Button("Set Directory")

                output_dir_status = gr.Textbox(label="Status", interactive=False)

                gr.Markdown("---")
                gr.Markdown("### Appearance")

                with gr.Row():
                    dark_mode_checkbox = gr.Checkbox(
                        label="🌙 Dark Mode",
                        value=False,
                        info="Enable dark mode for easier viewing"
                    )
                    theme_status = gr.Textbox(
                        value="Light mode active",
                        label="Theme Status",
                        interactive=False
                    )

                gr.Markdown("---")
                gr.Markdown("### System Information")

                # Detect system info
                import platform

                gpu_info = "Not detected (install nvidia-ml-py for GPU info)"
                try:
                    import subprocess
                    result = subprocess.run(
                        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        gpu_info = result.stdout.strip()
                except:
                    pass

                ffmpeg_version = "Not found"
                try:
                    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        ffmpeg_version = result.stdout.split('\n')[0].split(' ')[2]
                except:
                    pass

                gr.Markdown(f"""
                | Component | Status |
                |-----------|--------|
                | **Python** | {sys.version.split()[0]} |
                | **Platform** | {platform.system()} {platform.release()} |
                | **GPU** | {gpu_info} |
                | **FFmpeg** | {ffmpeg_version} |
                | **Log Directory** | `logs/` |
                | **Queue State** | `queue_state.json` |
                """)

            # =====================================================================
            # Tab 6: About
            # =====================================================================
            with gr.TabItem("ℹ️ About", id=6):
                gr.Markdown(f"""
                ### About VHS Video Upscaler

                **Version:** {__version__}
                **License:** MIT (Open Source)

                ---

                #### Features
                - 🎬 **AI Upscaling** - NVIDIA Maxine SuperRes with artifact reduction
                - 📺 **VHS Restoration** - Optimized presets for vintage footage
                - ⬇️ **YouTube Integration** - Download and upscale in one step
                - 📋 **Queue System** - Batch process multiple videos
                - 📁 **Drag & Drop** - Easy file upload support
                - 👁️ **Video Preview** - See file info before processing
                - 🌙 **Dark Mode** - Easy on the eyes
                - 🚀 **GPU Accelerated** - RTX Tensor Core optimization

                ---

                #### Credits
                - [NVIDIA Maxine Video Effects SDK](https://developer.nvidia.com/maxine)
                - [yt-dlp](https://github.com/yt-dlp/yt-dlp)
                - [FFmpeg](https://ffmpeg.org/)
                - [Gradio](https://gradio.app/)

                ---

                #### Alternatives
                | Project | Best For |
                |---------|----------|
                | [Video2X](https://github.com/k4yt3x/video2x) | Anime upscaling, Real-ESRGAN |
                | [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) | Maximum quality (slower) |
                | [Topaz Video AI](https://www.topazlabs.com/) | Commercial, easy to use |

                ---

                **GitHub:** [github.com/parthalon025/terminalai](https://github.com/parthalon025/terminalai)
                """)

        # =====================================================================
        # Event Handlers
        # =====================================================================

        # Mode toggle handler
        def toggle_mode(mode):
            """Toggle between Basic and Advanced modes."""
            is_basic = "Basic" in mode
            return {
                basic_mode_ui: gr.update(visible=is_basic),
                advanced_mode_ui: gr.update(visible=not is_basic)
            }

        mode_toggle.change(
            fn=toggle_mode,
            inputs=[mode_toggle],
            outputs=[basic_mode_ui, advanced_mode_ui]
        )

        # Basic mode process button handler
        def process_basic_video(file_path, url_input, basic_preset_choice, basic_quality_choice):
            """Process video from basic mode with smart defaults."""
            # Map basic presets to configuration
            preset_map = {
                "📼 Old VHS tape (home movies, family recordings)": {
                    "preset": "vhs",
                    "resolution": 1080,
                    "upscale_engine": "auto",
                    "face_restore": True,
                    "audio_enhance": "voice",
                    "audio_upmix": "demucs",
                    "audio_layout": "5.1",
                    "audio_sr_enabled": True,
                    "audio_sr_model": "speech",
                    "encoder": "hevc_nvenc"
                },
                "💿 DVD movie": {
                    "preset": "dvd",
                    "resolution": 1080,
                    "upscale_engine": "auto",
                    "face_restore": False,
                    "audio_enhance": "light",
                    "audio_upmix": "prologic",
                    "audio_layout": "5.1",
                    "audio_sr_enabled": False,
                    "encoder": "hevc_nvenc"
                },
                "📺 YouTube video": {
                    "preset": "youtube",
                    "resolution": 1080,
                    "upscale_engine": "realesrgan",
                    "face_restore": False,
                    "audio_enhance": "moderate",
                    "audio_upmix": "none",
                    "audio_layout": "original",
                    "audio_sr_enabled": False,
                    "encoder": "hevc_nvenc"
                },
                "🎥 Recent digital video (phone, camera)": {
                    "preset": "clean",
                    "resolution": 1080,
                    "upscale_engine": "auto",
                    "face_restore": False,
                    "audio_enhance": "none",
                    "audio_upmix": "none",
                    "audio_layout": "original",
                    "audio_sr_enabled": False,
                    "encoder": "hevc_nvenc"
                }
            }

            # Map quality choices to CRF values
            quality_map = {
                "Good (Fast, smaller file)": 23,
                "Better (Balanced)": 20,
                "Best (Slow, larger file)": 18
            }

            config = preset_map.get(basic_preset_choice, preset_map["📼 Old VHS tape (home movies, family recordings)"])
            crf = quality_map.get(basic_quality_choice, 20)

            # Use file path if uploaded, otherwise URL
            source = file_path if file_path else url_input

            # Call add_to_queue with smart defaults
            return add_to_queue(
                input_source=source,
                preset=config["preset"],
                resolution=config["resolution"],
                quality=0,  # Best quality preset
                crf=crf,
                encoder=config["encoder"],
                upscale_engine=config["upscale_engine"],
                hdr_mode="sdr",  # Default to SDR
                realesrgan_model="realesrgan-x4plus",
                realesrgan_denoise=0.5,
                ffmpeg_scale_algo="lanczos",
                hdr_brightness=400,
                hdr_color_depth=10,
                rtxvideo_artifact_reduction=True,
                rtxvideo_artifact_strength=0.5,
                rtxvideo_hdr=False,
                audio_enhance=config["audio_enhance"],
                audio_upmix=config["audio_upmix"],
                audio_layout=config["audio_layout"],
                audio_format="aac",
                audio_target_loudness=-14.0,
                audio_noise_floor=-20.0,
                demucs_model="htdemucs",
                demucs_device="auto",
                demucs_shifts=1,
                lfe_crossover=120,
                center_mix=0.707,
                surround_delay=15,
                lut_file="",
                lut_strength=1.0,
                face_restore=config["face_restore"],
                face_model="gfpgan",
                face_restore_strength=0.5,
                face_restore_upscale=2,
                audio_sr_enabled=config["audio_sr_enabled"],
                audio_sr_model=config.get("audio_sr_model", "basic"),
                deinterlace_algorithm="yadif",
                qtgmc_preset="medium"
            )

        basic_process_btn.click(
            fn=process_basic_video,
            inputs=[final_input, input_source, basic_preset, basic_quality],
            outputs=[status_msg, queue_display]
        )

        # File upload handler
        def on_file_upload(file_path):
            if file_path:
                path, preview = handle_file_upload(file_path)
                return path, preview, path
            return "", "<div class='info-card'>Upload a video file to see preview info</div>", ""

        file_upload.change(
            fn=on_file_upload,
            inputs=[file_upload],
            outputs=[input_source, file_preview, final_input]
        )

        # URL input updates final_input
        input_source.change(
            fn=lambda x: x,
            inputs=[input_source],
            outputs=[final_input]
        )

        # Helper to get the right input source
        def add_video_to_queue(file_path, url_input, preset, resolution, quality, crf, encoder,
                               engine, hdr, model, esrgan_denoise, ffmpeg_algo,
                               hdr_bright, hdr_depth,
                               rtx_artifact_reduction, rtx_artifact_strength, rtx_hdr,
                               aud_enhance, aud_upmix, aud_layout, aud_format,
                               aud_loudness, aud_noise,
                               dem_model, dem_device, dem_shifts,
                               lfe_cross, cent_mix, surr_delay,
                               lut_path, lut_str, face_rest, face_mdl, face_str, face_up,
                               aud_sr_enabled, aud_sr_model,
                               deint_algo, qtgmc_pres):
            # Prefer file upload, fall back to URL/path input
            source = file_path if file_path else url_input
            return add_to_queue(
                source, preset, resolution, quality, crf, encoder,
                engine, hdr, model, esrgan_denoise, ffmpeg_algo,
                hdr_bright, hdr_depth,
                rtx_artifact_reduction, rtx_artifact_strength, rtx_hdr,
                aud_enhance, aud_upmix, aud_layout, aud_format,
                aud_loudness, aud_noise,
                dem_model, dem_device, dem_shifts,
                lfe_cross, cent_mix, surr_delay,
                lut_path, lut_str, face_rest, face_mdl, face_str, face_up,
                aud_sr_enabled, aud_sr_model,
                deint_algo, qtgmc_pres
            )

        # Single video - use combined handler
        add_btn.click(
            fn=add_video_to_queue,
            inputs=[
                final_input, input_source, preset, resolution, quality, crf, encoder,
                upscale_engine, hdr_mode, realesrgan_model, realesrgan_denoise, ffmpeg_scale_algo,
                hdr_brightness, hdr_color_depth,
                # RTX Video SDK options
                rtxvideo_artifact_reduction, rtxvideo_artifact_strength, rtxvideo_hdr,
                # Audio options
                audio_enhance, audio_upmix, audio_layout, audio_format,
                audio_target_loudness, audio_noise_floor,
                demucs_model, demucs_device, demucs_shifts,
                lfe_crossover, center_mix, surround_delay,
                lut_file, lut_strength, face_restore, face_model, face_restore_strength, face_restore_upscale,
                audio_sr_enabled, audio_sr_model,
                deinterlace_algorithm, qtgmc_preset
            ],
            outputs=[status_msg, queue_display]
        )

        # Batch - simplified (uses same audio settings from single tab as default)
        batch_add_btn.click(
            fn=add_multiple_to_queue,
            inputs=[batch_input, batch_preset, batch_resolution, batch_quality, batch_crf,
                    batch_encoder, batch_engine, batch_hdr,
                    audio_enhance, audio_upmix, audio_layout, audio_format],
            outputs=[batch_status, queue_display]
        )

        # Queue controls with stats update
        def start_queue_with_stats():
            result = start_queue()
            return result[0], result[1], get_stats_display()

        def pause_queue_with_stats():
            result = pause_queue()
            return result[0], result[1], get_stats_display()

        def clear_completed_with_stats():
            result = clear_completed()
            return result[0], result[1], get_stats_display()

        def clear_all_with_stats():
            result = clear_all_queue()
            return result[0], result[1], get_stats_display()

        start_btn.click(fn=start_queue_with_stats, outputs=[queue_status, queue_display, stats_display])
        pause_btn.click(fn=pause_queue_with_stats, outputs=[queue_status, queue_display, stats_display])
        clear_btn.click(fn=clear_completed_with_stats, outputs=[queue_status, queue_display, stats_display])
        clear_all_btn.click(fn=clear_all_with_stats, outputs=[queue_status, queue_display, stats_display])
        refresh_btn.click(fn=refresh_display, outputs=[queue_display, stats_display, logs_display])

        # Logs
        logs_refresh_btn.click(fn=get_logs_display, outputs=[logs_display])

        # Settings
        output_dir_btn.click(
            fn=set_output_directory,
            inputs=[output_dir_input],
            outputs=[output_dir_status]
        )

        # Dark mode toggle handler
        def toggle_theme(enabled):
            AppState.dark_mode = enabled
            status = "🌙 Dark mode active" if enabled else "☀️ Light mode active"
            AppState.add_log(f"Theme changed: {status}")
            return status

        dark_mode_checkbox.change(
            fn=toggle_theme,
            inputs=[dark_mode_checkbox],
            outputs=[theme_status]
        )

        # =====================================================================
        # Conditional Option Visibility Handlers
        # =====================================================================

        # Upscale engine options visibility
        def update_engine_options(engine):
            """Show/hide engine-specific options based on selection."""
            return {
                rtxvideo_options: gr.update(visible=(engine == "rtxvideo")),
                realesrgan_options: gr.update(visible=(engine == "realesrgan")),
                ffmpeg_options: gr.update(visible=(engine == "ffmpeg")),
            }

        upscale_engine.change(
            fn=update_engine_options,
            inputs=[upscale_engine],
            outputs=[rtxvideo_options, realesrgan_options, ffmpeg_options]
        )

        # HDR options visibility
        def update_hdr_options(mode):
            """Show HDR settings when HDR mode is enabled."""
            return gr.update(visible=(mode != "sdr"))

        hdr_mode.change(
            fn=update_hdr_options,
            inputs=[hdr_mode],
            outputs=[hdr_options]
        )

        # Audio enhancement options visibility
        def update_audio_enhance_options(enhance_mode):
            """Show enhancement settings when audio enhancement is enabled."""
            return gr.update(visible=(enhance_mode != "none"))

        audio_enhance.change(
            fn=update_audio_enhance_options,
            inputs=[audio_enhance],
            outputs=[audio_enhance_options]
        )

        # Demucs options visibility
        def update_demucs_options(upmix_mode):
            """Show Demucs settings when Demucs upmix is selected."""
            return gr.update(visible=(upmix_mode == "demucs"))

        audio_upmix.change(
            fn=update_demucs_options,
            inputs=[audio_upmix],
            outputs=[demucs_options]
        )

        # Surround options visibility
        def update_surround_options(layout):
            """Show surround settings when 5.1 or 7.1 layout is selected."""
            return gr.update(visible=(layout in ["5.1", "7.1"]))

        audio_layout.change(
            fn=update_surround_options,
            inputs=[audio_layout],
            outputs=[surround_options]
        )

        # AudioSR model visibility
        def update_audiosr_options(enabled):
            """Show AudioSR model dropdown when AudioSR is enabled."""
            return gr.update(visible=enabled)

        audio_sr_enabled.change(
            fn=update_audiosr_options,
            inputs=[audio_sr_enabled],
            outputs=[audio_sr_model]
        )

        # RTX Video artifact strength visibility
        def update_rtx_artifact_strength(enabled):
            """Show artifact strength slider when artifact reduction is enabled."""
            return gr.update(visible=enabled)

        rtxvideo_artifact_reduction.change(
            fn=update_rtx_artifact_strength,
            inputs=[rtxvideo_artifact_reduction],
            outputs=[rtxvideo_artifact_strength]
        )

        # Face restoration options visibility
        def update_face_restore_options(enabled):
            """Show face restoration settings when face restore is enabled."""
            return gr.update(visible=enabled)

        face_restore.change(
            fn=update_face_restore_options,
            inputs=[face_restore],
            outputs=[face_restore_options]
        )

        # QTGMC preset visibility
        def update_qtgmc_options(algorithm):
            """Show QTGMC preset dropdown when QTGMC algorithm is selected."""
            return gr.update(visible=(algorithm == "qtgmc"))

        deinterlace_algorithm.change(
            fn=update_qtgmc_options,
            inputs=[deinterlace_algorithm],
            outputs=[qtgmc_options]
        )

        # =====================================================================
        # Quick Fix Preset Click Handlers
        # =====================================================================

        def apply_quick_fix(preset_key):
            """Apply a quick-fix preset configuration to all GUI components."""
            presets = get_quick_fix_presets()
            config = presets.get(preset_key, {})

            # Return gr.update() for each component to update its value
            updates = {}
            updates["preset"] = gr.update(value=config.get("preset", "vhs"))
            updates["resolution"] = gr.update(value=config.get("resolution", 1080))
            updates["crf"] = gr.update(value=config.get("crf", 20))
            updates["quality"] = gr.update(value=config.get("quality", 0))
            updates["encoder"] = gr.update(value=config.get("encoder", "hevc_nvenc"))
            updates["upscale_engine"] = gr.update(value=config.get("upscale_engine", "auto"))
            updates["realesrgan_model"] = gr.update(value=config.get("realesrgan_model", "realesrgan-x4plus"))
            updates["realesrgan_denoise"] = gr.update(value=config.get("realesrgan_denoise", 0.5))
            updates["face_restore"] = gr.update(value=config.get("face_restore", False))
            updates["face_model"] = gr.update(value=config.get("face_model", "gfpgan"))
            updates["face_restore_strength"] = gr.update(value=config.get("face_restore_strength", 0.5))
            updates["audio_enhance"] = gr.update(value=config.get("audio_enhance", "none"))
            updates["audio_upmix"] = gr.update(value=config.get("audio_upmix", "none"))
            updates["audio_layout"] = gr.update(value=config.get("audio_layout", "original"))
            updates["audio_sr_enabled"] = gr.update(value=config.get("audio_sr_enabled", False))
            updates["audio_sr_model"] = gr.update(value=config.get("audio_sr_model", "basic"))
            updates["deinterlace_algorithm"] = gr.update(value=config.get("deinterlace_algorithm", "yadif"))
            updates["qtgmc_preset"] = gr.update(value=config.get("qtgmc_preset", "medium"))
            updates["status_msg"] = gr.update(value=f"✅ Applied: {config.get('info', config.get('name', 'Unknown preset'))}")

            return (
                updates["preset"], updates["resolution"], updates["crf"], updates["quality"],
                updates["encoder"], updates["upscale_engine"], updates["realesrgan_model"],
                updates["realesrgan_denoise"], updates["face_restore"], updates["face_model"],
                updates["face_restore_strength"], updates["audio_enhance"], updates["audio_upmix"],
                updates["audio_layout"], updates["audio_sr_enabled"], updates["audio_sr_model"],
                updates["deinterlace_algorithm"], updates["qtgmc_preset"], updates["status_msg"]
            )

        # Wire up each quick-fix button
        output_components = [
            preset, resolution, crf, quality, encoder, upscale_engine, realesrgan_model,
            realesrgan_denoise, face_restore, face_model, face_restore_strength, audio_enhance,
            audio_upmix, audio_layout, audio_sr_enabled, audio_sr_model,
            deinterlace_algorithm, qtgmc_preset, status_msg
        ]

        btn_vhs_home.click(fn=lambda: apply_quick_fix("vhs_home"), outputs=output_components)
        btn_vhs_noisy.click(fn=lambda: apply_quick_fix("vhs_noisy"), outputs=output_components)
        btn_dvd_rip.click(fn=lambda: apply_quick_fix("dvd_rip"), outputs=output_components)
        btn_youtube_old.click(fn=lambda: apply_quick_fix("youtube_old"), outputs=output_components)
        btn_anime.click(fn=lambda: apply_quick_fix("anime"), outputs=output_components)
        btn_webcam.click(fn=lambda: apply_quick_fix("webcam"), outputs=output_components)
        btn_clean.click(fn=lambda: apply_quick_fix("clean"), outputs=output_components)
        btn_best_quality.click(fn=lambda: apply_quick_fix("best_quality"), outputs=output_components)

        # Auto-refresh queue and stats every 2 seconds
        def auto_refresh():
            return get_queue_display(), get_stats_display()

        # Gradio 6.x uses different syntax for periodic updates
        try:
            # Try Gradio 6.x syntax - Timer with value parameter
            timer = gr.Timer(value=2)
            timer.tick(fn=auto_refresh, outputs=[queue_display, stats_display])
        except (AttributeError, TypeError):
            # If Timer doesn't work, use manual refresh button instead
            # Auto-refresh is not critical, users can manually refresh
            pass

    return app


# =============================================================================
# Main Entry Point
# =============================================================================

def _print_rtx_video_status():
    """Print RTX Video SDK status at startup."""
    import platform

    if platform.system() != "Windows":
        print("  AI Upscaler: Real-ESRGAN / FFmpeg (RTX Video requires Windows)")
        return

    try:
        from .rtx_video_sdk import is_rtx_video_available
        available, message = is_rtx_video_available()

        if available:
            print(f"  🚀 RTX Video SDK: Ready ({message})")
            print("     Select 'rtxvideo' for best AI upscaling quality")
        else:
            print("  ℹ️  RTX Video SDK: Not installed")
            print("     Run 'terminalai-setup-rtx' to set up (optional)")
            print("     Using Real-ESRGAN / FFmpeg as fallback")
    except ImportError:
        print("  AI Upscaler: Real-ESRGAN / FFmpeg")


def main():
    """Launch the GUI."""
    import argparse

    parser = argparse.ArgumentParser(description="VHS Upscaler Web GUI")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7860, help="Port to listen on")
    parser.add_argument("--share", action="store_true", help="Create public link")
    parser.add_argument("--output-dir", default="./output", help="Default output directory")
    parser.add_argument("--skip-wizard", action="store_true", help="Skip first-run wizard")
    parser.add_argument("--reset-wizard", action="store_true", help="Reset first-run wizard state")

    args = parser.parse_args()

    # Handle wizard reset
    if args.reset_wizard:
        try:
            from first_run_wizard import FirstRunManager
            FirstRunManager.reset()
            print("First-run wizard state reset. Next launch will show wizard.")
            return
        except ImportError:
            print("First-run wizard module not available")
            return

    # Check if first run and show wizard
    if not args.skip_wizard:
        try:
            from first_run_wizard import FirstRunManager, create_wizard_ui

            if FirstRunManager.is_first_run():
                print("\n" + "=" * 60)
                print("  🎬 TerminalAI - First Run Setup")
                print("=" * 60)
                print("  Launching setup wizard...")
                print("  This will download AI models and configure your system.")
                print("=" * 60 + "\n")

                # Launch wizard
                wizard = create_wizard_ui()
                wizard.launch(
                    server_name=args.host,
                    server_port=args.port,
                    share=False,
                    inbrowser=True
                )

                # Wizard will mark completion when user finishes
                # Now check if setup was completed
                if not FirstRunManager.is_first_run():
                    print("\nSetup complete! Launching main application...\n")
                else:
                    print("\nSetup incomplete. Run again to complete setup.\n")
                    return

        except ImportError as e:
            logger.debug(f"First-run wizard not available: {e}")
            # Continue to main app if wizard not available

    # Launch main application
    AppState.output_dir = Path(args.output_dir)
    AppState.output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("  🎬 VHS Upscaler Web GUI v1.5.1")
    print("=" * 60)
    print(f"  Output Directory: {AppState.output_dir.absolute()}")
    print("  Log Directory: logs/")

    # Check RTX Video SDK availability
    _print_rtx_video_status()

    print("=" * 60 + "\n")

    app = create_gui()
    app.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        inbrowser=True
    )


if __name__ == "__main__":
    main()
