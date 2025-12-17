#!/usr/bin/env python3
"""
VHS Upscaler Web GUI
====================
Modern web-based interface for the VHS Upscaling Pipeline.
Built with Gradio for a clean, responsive user experience.
"""

import gradio as gr
import json
import os
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Tuple
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from queue_manager import VideoQueue, QueueJob, JobStatus
from logger import get_logger, VHSLogger

# Initialize logger
logger = get_logger(verbose=True, log_to_file=True)


# =============================================================================
# Global State
# =============================================================================

class AppState:
    """Global application state."""
    queue: Optional[VideoQueue] = None
    output_dir: Path = Path("./output")
    logs: List[str] = []
    max_logs: int = 100

    @classmethod
    def add_log(cls, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        cls.logs.append(f"[{timestamp}] {message}")
        if len(cls.logs) > cls.max_logs:
            cls.logs = cls.logs[-cls.max_logs:]


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
            skip_maxine=True,  # For testing; remove in production
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
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    return str(timedelta(seconds=int(seconds)))


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
                 quality: int, crf: int, encoder: str) -> Tuple[str, str]:
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
        encoder=encoder
    )

    AppState.add_log(f"Added to queue: {input_source[:50]}...")

    return f"✅ Added to queue (ID: {job.id})", get_queue_display()


def add_multiple_to_queue(urls_text: str, preset: str, resolution: int,
                          quality: int, crf: int, encoder: str) -> Tuple[str, str]:
    """Add multiple videos to the queue."""
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
            encoder=encoder
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


def refresh_display() -> Tuple[str, str]:
    """Refresh the queue and logs display."""
    return get_queue_display(), get_logs_display()


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

    # Custom CSS for modern look
    custom_css = """
    .gradio-container {
        max-width: 1200px !important;
    }
    .tab-nav button {
        font-size: 16px !important;
    }
    .prose h1 {
        color: #1976D2 !important;
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

        # Header
        gr.Markdown("""
        # 🎬 VHS Video Upscaler
        ### AI-Powered Video Enhancement with NVIDIA Maxine

        Upload local files or paste YouTube URLs to upscale videos to HD/4K quality.
        """)

        with gr.Tabs():
            # =====================================================================
            # Tab 1: Single Video
            # =====================================================================
            with gr.TabItem("📹 Single Video", id=1):
                with gr.Row():
                    with gr.Column(scale=2):
                        input_source = gr.Textbox(
                            label="Video Source",
                            placeholder="Enter file path or YouTube URL...",
                            info="Supports: youtube.com, youtu.be, local .mp4/.avi/.mkv files"
                        )

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
                            encoder = gr.Dropdown(
                                choices=["hevc_nvenc", "h264_nvenc", "libx265", "libx264"],
                                value="hevc_nvenc",
                                label="Encoder",
                                info="NVENC for GPU acceleration, libx for CPU"
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
                    batch_encoder = gr.Dropdown(
                        choices=["hevc_nvenc", "h264_nvenc", "libx265", "libx264"],
                        value="hevc_nvenc",
                        label="Encoder"
                    )

                batch_add_btn = gr.Button("➕ Add All to Queue", variant="primary", size="lg")
                batch_status = gr.Textbox(label="Status", interactive=False)

            # =====================================================================
            # Tab 3: Queue
            # =====================================================================
            with gr.TabItem("📋 Queue", id=3):
                with gr.Row():
                    start_btn = gr.Button("▶️ Start", variant="primary")
                    pause_btn = gr.Button("⏸️ Pause", variant="secondary")
                    clear_btn = gr.Button("🗑️ Clear Done", variant="secondary")
                    refresh_btn = gr.Button("🔄 Refresh", variant="secondary")

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
                gr.Markdown("### System Information")
                gr.Markdown(f"""
                - **Log Directory:** `logs/`
                - **Queue State:** `queue_state.json`
                - **Python Version:** {sys.version.split()[0]}
                """)

        # =====================================================================
        # Event Handlers
        # =====================================================================

        # Single video
        add_btn.click(
            fn=add_to_queue,
            inputs=[input_source, preset, resolution, quality, crf, encoder],
            outputs=[status_msg, queue_display]
        )

        # Batch
        batch_add_btn.click(
            fn=add_multiple_to_queue,
            inputs=[batch_input, batch_preset, batch_resolution, batch_quality, batch_crf, batch_encoder],
            outputs=[batch_status, queue_display]
        )

        # Queue controls
        start_btn.click(fn=start_queue, outputs=[queue_status, queue_display])
        pause_btn.click(fn=pause_queue, outputs=[queue_status, queue_display])
        clear_btn.click(fn=clear_completed, outputs=[queue_status, queue_display])
        refresh_btn.click(fn=refresh_display, outputs=[queue_display, logs_display])

        # Logs
        logs_refresh_btn.click(fn=get_logs_display, outputs=[logs_display])

        # Settings
        output_dir_btn.click(
            fn=set_output_directory,
            inputs=[output_dir_input],
            outputs=[output_dir_status]
        )

        # Auto-refresh queue every 2 seconds
        app.load(fn=get_queue_display, outputs=[queue_display], every=2)

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
