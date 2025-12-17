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
import os
import sys
import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import tempfile
import base64
import hashlib

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from queue_manager import VideoQueue, QueueJob, JobStatus
from logger import get_logger, VHSLogger

# Initialize logger
logger = get_logger(verbose=True, log_to_file=True)

# Version info
__version__ = "1.4.0"


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
    from vhs_upscale import (
        VHSUpscaler, ProcessingConfig, YouTubeDownloader, UnifiedProgress
    )

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
        )

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
                 audio_enhance: str = "none", audio_upmix: str = "none",
                 audio_layout: str = "original", audio_format: str = "aac",
                 audio_target_loudness: float = -14.0, audio_noise_floor: float = -20.0,
                 demucs_model: str = "htdemucs", demucs_device: str = "auto",
                 demucs_shifts: int = 1, lfe_crossover: int = 120,
                 center_mix: float = 0.707, surround_delay: int = 15) -> Tuple[str, str]:
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
        surround_delay=surround_delay
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

def create_gui() -> gr.Blocks:
    """Create the Gradio interface."""

    # Custom CSS for modern look with dark mode support
    custom_css = """
    /* CSS Variables for theming */
    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f5f5f5;
        --bg-card: #ffffff;
        --text-primary: #1a1a1a;
        --text-secondary: #666666;
        --border-color: #e0e0e0;
        --shadow-color: rgba(0,0,0,0.08);
        --accent-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --success-color: #10b981;
        --error-color: #ef4444;
        --warning-color: #f59e0b;
        --info-color: #3b82f6;
    }

    /* Dark mode variables */
    .dark {
        --bg-primary: #1a1a2e;
        --bg-secondary: #16213e;
        --bg-card: #0f3460;
        --text-primary: #e4e4e4;
        --text-secondary: #a0a0a0;
        --border-color: #2a2a4a;
        --shadow-color: rgba(0,0,0,0.3);
    }

    /* Container styling */
    .gradio-container {
        max-width: 1200px !important;
        margin: 0 auto !important;
        background: var(--bg-primary) !important;
    }

    /* Header gradient */
    .prose h1 {
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
    }

    /* Tab styling */
    .tab-nav button {
        font-size: 15px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    .tab-nav button:hover {
        transform: translateY(-2px) !important;
    }

    /* Card-like sections */
    .block {
        border-radius: 12px !important;
        box-shadow: 0 2px 8px var(--shadow-color) !important;
        background: var(--bg-card) !important;
    }

    /* Button enhancements */
    .primary {
        background: var(--accent-gradient) !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    .primary:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }

    /* Secondary button */
    .secondary {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        transition: all 0.2s ease !important;
    }

    /* Status badges */
    .status-completed { color: var(--success-color); font-weight: 600; }
    .status-processing { color: var(--info-color); font-weight: 600; }
    .status-failed { color: var(--error-color); font-weight: 600; }
    .status-pending { color: var(--text-secondary); }

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
        title="VHS Upscaler",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
        ),
        css=custom_css
    ) as app:

        # Header with version badge
        gr.Markdown(f"""
        # 🎬 VHS Video Upscaler
        ### AI-Powered Video Enhancement with NVIDIA Maxine <span class="version-badge">v{__version__}</span>

        Transform vintage VHS tapes, DVDs, and low-quality videos into stunning HD/4K using RTX GPU acceleration.
        Supports **YouTube URLs**, **local files**, and **drag-and-drop upload** with batch processing.
        """)

        with gr.Tabs():
            # =====================================================================
            # Tab 1: Single Video
            # =====================================================================
            with gr.TabItem("📹 Single Video", id=1):
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("### Input Source")

                        # Tab group for input methods
                        with gr.Tabs():
                            with gr.TabItem("📁 Upload File"):
                                file_upload = gr.File(
                                    label="Drag & Drop Video File",
                                    file_types=["video"],
                                    file_count="single",
                                    type="filepath"
                                )
                                file_preview = gr.HTML(
                                    value="<div class='info-card'>Upload a video file to see preview info</div>",
                                    label="Video Info"
                                )

                            with gr.TabItem("🔗 URL / Path"):
                                input_source = gr.Textbox(
                                    label="Video Source",
                                    placeholder="Enter file path or YouTube URL...",
                                    info="Supports: youtube.com, youtu.be, local .mp4/.avi/.mkv files"
                                )

                        # Hidden textbox to hold the final input path
                        final_input = gr.Textbox(visible=False, value="")

                        with gr.Row():
                            preset = gr.Dropdown(
                                choices=["vhs", "dvd", "webcam", "youtube", "clean", "auto"],
                                value="vhs",
                                label="Preset",
                                info="Processing preset based on source type"
                            )
                            resolution = gr.Dropdown(
                                choices=[720, 1080, 1440, 2160],
                                value=1080,
                                label="Resolution",
                                info="Target output resolution"
                            )

                        with gr.Accordion("⚙️ Advanced Options", open=False):
                            with gr.Row():
                                quality = gr.Radio(
                                    choices=[0, 1],
                                    value=0,
                                    label="Quality Mode",
                                    info="0 = Best quality, 1 = Performance"
                                )
                                crf = gr.Slider(
                                    minimum=15,
                                    maximum=28,
                                    value=20,
                                    step=1,
                                    label="CRF (Quality)",
                                    info="Lower = better quality, larger file"
                                )
                            with gr.Row():
                                encoder = gr.Dropdown(
                                    choices=["hevc_nvenc", "h264_nvenc", "libx265", "libx264"],
                                    value="hevc_nvenc",
                                    label="Encoder",
                                    info="NVENC for GPU acceleration, libx for CPU"
                                )
                                upscale_engine = gr.Dropdown(
                                    choices=["auto", "maxine", "realesrgan", "ffmpeg"],
                                    value="auto",
                                    label="Upscale Engine",
                                    info="auto=best available, maxine=NVIDIA RTX, realesrgan=any GPU, ffmpeg=CPU only"
                                )
                            with gr.Row():
                                hdr_mode = gr.Dropdown(
                                    choices=["sdr", "hdr10", "hlg"],
                                    value="sdr",
                                    label="HDR Mode",
                                    info="sdr=standard, hdr10=HDR10, hlg=HLG broadcast"
                                )

                            # === Conditional: Real-ESRGAN Options ===
                            with gr.Group(visible=False) as realesrgan_options:
                                gr.Markdown("**🎨 Real-ESRGAN Settings**")
                                with gr.Row():
                                    realesrgan_model = gr.Dropdown(
                                        choices=["realesrgan-x4plus", "realesrgan-x4plus-anime",
                                                 "realesr-animevideov3", "realesrnet-x4plus"],
                                        value="realesrgan-x4plus",
                                        label="Model",
                                        info="x4plus=general, anime=animation, animevideo=video"
                                    )
                                    realesrgan_denoise = gr.Slider(
                                        minimum=0, maximum=1, value=0.5, step=0.1,
                                        label="Denoise Strength",
                                        info="0=no denoise, 1=max denoise"
                                    )

                            # === Conditional: FFmpeg Upscale Options ===
                            with gr.Group(visible=False) as ffmpeg_options:
                                gr.Markdown("**🔧 FFmpeg Upscale Settings**")
                                with gr.Row():
                                    ffmpeg_scale_algo = gr.Dropdown(
                                        choices=["lanczos", "bicubic", "bilinear", "spline", "neighbor"],
                                        value="lanczos",
                                        label="Scaling Algorithm",
                                        info="lanczos=best quality, bicubic=balanced"
                                    )

                            # === Conditional: HDR Options ===
                            with gr.Group(visible=False) as hdr_options:
                                gr.Markdown("**🎨 HDR Settings**")
                                with gr.Row():
                                    hdr_brightness = gr.Slider(
                                        minimum=100, maximum=1000, value=400, step=50,
                                        label="Peak Brightness (nits)",
                                        info="Target peak brightness for HDR"
                                    )
                                    hdr_color_depth = gr.Radio(
                                        choices=[8, 10],
                                        value=10,
                                        label="Color Depth (bits)",
                                        info="10-bit required for true HDR"
                                    )

                        with gr.Accordion("🔊 Audio Options", open=False):
                            gr.Markdown("*Enhance audio and/or convert to surround sound*")
                            with gr.Row():
                                audio_enhance = gr.Dropdown(
                                    choices=["none", "light", "moderate", "aggressive", "voice", "music"],
                                    value="none",
                                    label="Audio Enhancement",
                                    info="none=skip, voice=dialogue, music=preserve dynamics"
                                )
                                audio_upmix = gr.Dropdown(
                                    choices=["none", "simple", "surround", "prologic", "demucs"],
                                    value="none",
                                    label="Surround Upmix",
                                    info="demucs=AI stem separation (best quality)"
                                )
                            with gr.Row():
                                audio_layout = gr.Dropdown(
                                    choices=["original", "stereo", "5.1", "7.1", "mono"],
                                    value="original",
                                    label="Output Layout",
                                    info="Target audio channel layout"
                                )
                                audio_format = gr.Dropdown(
                                    choices=["aac", "ac3", "eac3", "dts", "flac"],
                                    value="aac",
                                    label="Audio Format",
                                    info="eac3/ac3 for 5.1, dts for high quality"
                                )

                            # === Conditional: Audio Enhancement Options ===
                            with gr.Group(visible=False) as audio_enhance_options:
                                gr.Markdown("**🎚️ Enhancement Settings**")
                                with gr.Row():
                                    audio_target_loudness = gr.Slider(
                                        minimum=-24, maximum=-9, value=-14, step=1,
                                        label="Target Loudness (LUFS)",
                                        info="-14=streaming, -16=broadcast, -23=cinema"
                                    )
                                    audio_noise_floor = gr.Slider(
                                        minimum=-30, maximum=-10, value=-20, step=1,
                                        label="Noise Floor (dB)",
                                        info="Lower=more aggressive noise removal"
                                    )

                            # === Conditional: Demucs Options ===
                            with gr.Group(visible=False) as demucs_options:
                                gr.Markdown("**🤖 Demucs AI Settings**")
                                with gr.Row():
                                    demucs_model = gr.Dropdown(
                                        choices=["htdemucs", "htdemucs_ft", "mdx_extra", "mdx_extra_q"],
                                        value="htdemucs",
                                        label="Model",
                                        info="htdemucs=fast, htdemucs_ft=best quality, mdx=alternative"
                                    )
                                    demucs_device = gr.Dropdown(
                                        choices=["auto", "cuda", "cpu"],
                                        value="auto",
                                        label="Device",
                                        info="auto=detect GPU, cuda=force GPU, cpu=force CPU"
                                    )
                                with gr.Row():
                                    demucs_shifts = gr.Slider(
                                        minimum=0, maximum=5, value=1, step=1,
                                        label="Shifts",
                                        info="More shifts=better quality, slower (0=fastest)"
                                    )

                            # === Conditional: Surround Options ===
                            with gr.Group(visible=False) as surround_options:
                                gr.Markdown("**🔊 Surround Settings**")
                                with gr.Row():
                                    lfe_crossover = gr.Slider(
                                        minimum=60, maximum=200, value=120, step=10,
                                        label="LFE Crossover (Hz)",
                                        info="Low frequency cutoff for subwoofer"
                                    )
                                    center_mix = gr.Slider(
                                        minimum=0.0, maximum=1.0, value=0.707, step=0.05,
                                        label="Center Mix Level",
                                        info="0.707=-3dB (standard), 1.0=full"
                                    )
                                with gr.Row():
                                    surround_delay = gr.Slider(
                                        minimum=0, maximum=50, value=15, step=5,
                                        label="Surround Delay (ms)",
                                        info="Delay for rear channels (creates depth)"
                                    )

                        add_btn = gr.Button("➕ Add to Queue", variant="primary", size="lg")
                        status_msg = gr.Textbox(label="Status", interactive=False)

                    with gr.Column(scale=1):
                        gr.Markdown("### 📋 Presets Guide")
                        gr.Markdown("""
                        | Preset | Best For |
                        |--------|----------|
                        | **vhs** | VHS tapes (480i, heavy noise) |
                        | **dvd** | DVD rips (480p/576p) |
                        | **webcam** | Old webcam footage |
                        | **youtube** | YouTube downloads |
                        | **clean** | Already clean sources |
                        | **auto** | Auto-detect settings |
                        """)

                        gr.Markdown("### 💡 Quick Tips")
                        gr.Markdown("""
                        - Use **hevc_nvenc** for best compression
                        - Lower **CRF** = better quality, larger files
                        - **1080p** is ideal for most VHS content

                        **No NVIDIA GPU?**
                        - Use **realesrgan** engine (AMD/Intel)
                        - Use **ffmpeg** for CPU-only upscaling

                        **Audio Enhancement:**
                        - **voice** - Best for VHS/dialogue
                        - **music** - Preserves dynamics
                        - **demucs** - AI upmix (best 5.1)
                        - Use **eac3** for 5.1 surround
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
                import shutil

                gpu_info = "Not detected (install pynvml for GPU info)"
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
                               aud_enhance, aud_upmix, aud_layout, aud_format,
                               aud_loudness, aud_noise,
                               dem_model, dem_device, dem_shifts,
                               lfe_cross, cent_mix, surr_delay):
            # Prefer file upload, fall back to URL/path input
            source = file_path if file_path else url_input
            return add_to_queue(
                source, preset, resolution, quality, crf, encoder,
                engine, hdr, model, esrgan_denoise, ffmpeg_algo,
                hdr_bright, hdr_depth,
                aud_enhance, aud_upmix, aud_layout, aud_format,
                aud_loudness, aud_noise,
                dem_model, dem_device, dem_shifts,
                lfe_cross, cent_mix, surr_delay
            )

        # Single video - use combined handler
        add_btn.click(
            fn=add_video_to_queue,
            inputs=[
                final_input, input_source, preset, resolution, quality, crf, encoder,
                upscale_engine, hdr_mode, realesrgan_model, realesrgan_denoise, ffmpeg_scale_algo,
                hdr_brightness, hdr_color_depth,
                audio_enhance, audio_upmix, audio_layout, audio_format,
                audio_target_loudness, audio_noise_floor,
                demucs_model, demucs_device, demucs_shifts,
                lfe_crossover, center_mix, surround_delay
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

        start_btn.click(fn=start_queue_with_stats, outputs=[queue_status, queue_display, stats_display])
        pause_btn.click(fn=pause_queue_with_stats, outputs=[queue_status, queue_display, stats_display])
        clear_btn.click(fn=clear_completed_with_stats, outputs=[queue_status, queue_display, stats_display])
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
                realesrgan_options: gr.update(visible=(engine == "realesrgan")),
                ffmpeg_options: gr.update(visible=(engine == "ffmpeg")),
            }

        upscale_engine.change(
            fn=update_engine_options,
            inputs=[upscale_engine],
            outputs=[realesrgan_options, ffmpeg_options]
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

        # Auto-refresh queue and stats every 2 seconds
        def auto_refresh():
            return get_queue_display(), get_stats_display()

        app.load(fn=auto_refresh, outputs=[queue_display, stats_display], every=2)

    return app


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Launch the GUI."""
    import argparse

    parser = argparse.ArgumentParser(description="VHS Upscaler Web GUI")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7860, help="Port to listen on")
    parser.add_argument("--share", action="store_true", help="Create public link")
    parser.add_argument("--output-dir", default="./output", help="Default output directory")

    args = parser.parse_args()

    AppState.output_dir = Path(args.output_dir)
    AppState.output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("  🎬 VHS Upscaler Web GUI")
    print("=" * 60)
    print(f"  Output Directory: {AppState.output_dir.absolute()}")
    print(f"  Log Directory: logs/")
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
