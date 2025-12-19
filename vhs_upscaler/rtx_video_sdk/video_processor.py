"""
RTX Video SDK Video Processor
=============================

High-level video processing pipeline using RTX Video SDK.
Handles complete video files with frame extraction, processing, and reassembly.
"""

import json
import logging
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Callable, Optional

from .models import RTXVideoConfig, ProcessingStats, HDRFormat
from .sdk_wrapper import RTXVideoWrapper

logger = logging.getLogger(__name__)


class RTXVideoProcessor:
    """
    Complete video processing pipeline using RTX Video SDK.

    Handles:
    - Frame extraction from input video
    - Batch processing through SDK
    - Video reassembly with audio
    - Progress reporting

    Example:
        config = RTXVideoConfig(
            enable_super_resolution=True,
            scale_factor=4,
            target_resolution=1080
        )

        processor = RTXVideoProcessor(config)
        success = processor.process_video("input.mp4", "output.mp4")
    """

    def __init__(
        self,
        config: RTXVideoConfig,
        ffmpeg_path: str = "ffmpeg",
        ffprobe_path: str = "ffprobe",
        progress_callback: Optional[Callable[[float], None]] = None,
    ):
        """
        Initialize video processor.

        Args:
            config: RTX Video SDK configuration
            ffmpeg_path: Path to FFmpeg executable
            ffprobe_path: Path to FFprobe executable
            progress_callback: Function called with progress percentage (0-100)
        """
        self.config = config
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
        self.progress_callback = progress_callback
        self._wrapper: Optional[RTXVideoWrapper] = None
        self._stats = ProcessingStats()

    @property
    def stats(self) -> ProcessingStats:
        """Get processing statistics."""
        return self._stats

    def process_video(
        self,
        input_path: Path,
        output_path: Path,
        preserve_audio: bool = True,
    ) -> bool:
        """
        Process complete video file.

        Args:
            input_path: Input video file
            output_path: Output video file
            preserve_audio: Whether to preserve original audio track

        Returns:
            True if processing successful.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        logger.info("RTX Video SDK Processing")
        logger.info(f"  Input: {input_path}")
        logger.info(f"  Output: {output_path}")
        logger.info(f"  Scale: {self.config.scale_factor}x")
        logger.info(f"  Target: {self.config.target_resolution}p")
        logger.info(f"  Artifact Reduction: {self.config.enable_artifact_reduction}")
        logger.info(f"  HDR Conversion: {self.config.enable_hdr_conversion}")

        # Get input video info
        video_info = self._get_video_info(input_path)
        if not video_info:
            logger.error("Failed to get video info")
            return False

        self._stats.input_resolution = (video_info["width"], video_info["height"])
        self._stats.total_frames = video_info.get("frame_count", 0)

        # Calculate output resolution
        scale = self.config.target_resolution / video_info["height"]
        out_width = int(video_info["width"] * scale)
        out_height = self.config.target_resolution
        self._stats.output_resolution = (out_width, out_height)

        # Initialize SDK
        self._wrapper = RTXVideoWrapper(self.config)
        if not self._wrapper.initialize():
            logger.error("Failed to initialize RTX Video SDK")
            return False

        start_time = time.time()

        try:
            with tempfile.TemporaryDirectory(prefix="rtxvideo_") as temp_dir:
                temp_path = Path(temp_dir)

                # Stage 1: Extract frames
                self._report_progress(0, "Extracting frames...")
                frames_dir = temp_path / "frames"
                frames_dir.mkdir()

                if not self._extract_frames(input_path, frames_dir, video_info):
                    return False

                # Stage 2: Process frames through SDK
                self._report_progress(10, "Processing frames with RTX Video SDK...")
                processed_dir = temp_path / "processed"
                processed_dir.mkdir()

                if not self._process_frames(frames_dir, processed_dir):
                    return False

                # Stage 3: Reassemble video
                self._report_progress(90, "Reassembling video...")
                temp_video = temp_path / "temp_video.mp4"

                if not self._reassemble_video(
                    processed_dir,
                    temp_video,
                    video_info,
                ):
                    return False

                # Stage 4: Mux audio (if preserving)
                self._report_progress(95, "Finalizing...")
                if preserve_audio and video_info.get("has_audio"):
                    if not self._mux_audio(temp_video, input_path, output_path):
                        return False
                else:
                    # Just copy/move the video
                    import shutil
                    shutil.move(str(temp_video), str(output_path))

            self._stats.processing_time_seconds = time.time() - start_time
            if self._stats.processed_frames > 0:
                self._stats.avg_frame_time_ms = (
                    self._stats.processing_time_seconds * 1000 / self._stats.processed_frames
                )

            self._report_progress(100, "Complete!")
            logger.info(f"Processing complete in {self._stats.processing_time_seconds:.1f}s")
            logger.info(f"  Frames: {self._stats.processed_frames}")
            logger.info(f"  FPS: {self._stats.frames_per_second:.1f}")
            return True

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return False

        finally:
            if self._wrapper:
                self._wrapper.cleanup()

    def _get_video_info(self, video_path: Path) -> Optional[dict]:
        """Get video metadata using ffprobe."""
        try:
            cmd = [
                self.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(video_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            # Find video stream
            video_stream = None
            has_audio = False
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video" and video_stream is None:
                    video_stream = stream
                elif stream.get("codec_type") == "audio":
                    has_audio = True

            if not video_stream:
                logger.error("No video stream found")
                return None

            # Parse frame rate
            fps_str = video_stream.get("r_frame_rate", "30/1")
            try:
                num, den = map(int, fps_str.split("/"))
                fps = num / den if den else 30.0
            except ValueError:
                fps = 30.0

            # Get frame count
            frame_count = int(video_stream.get("nb_frames", 0))
            if frame_count == 0:
                # Estimate from duration
                duration = float(data.get("format", {}).get("duration", 0))
                frame_count = int(duration * fps)

            return {
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "fps": fps,
                "frame_count": frame_count,
                "duration": float(data.get("format", {}).get("duration", 0)),
                "has_audio": has_audio,
                "codec": video_stream.get("codec_name", "unknown"),
                "pix_fmt": video_stream.get("pix_fmt", "yuv420p"),
            }

        except subprocess.CalledProcessError as e:
            logger.error(f"ffprobe failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ffprobe output: {e}")
            return None

    def _extract_frames(
        self,
        input_path: Path,
        frames_dir: Path,
        video_info: dict,
    ) -> bool:
        """Extract video frames to PNG files."""
        logger.debug(f"Extracting frames to {frames_dir}")

        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", str(input_path),
            "-qscale:v", "1",
            "-qmin", "1",
            "-qmax", "1",
            "-vsync", "0",
            str(frames_dir / "frame_%08d.png"),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug(f"Extracted frames to {frames_dir}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Frame extraction failed: {e.stderr}")
            return False

    def _process_frames(
        self,
        input_dir: Path,
        output_dir: Path,
    ) -> bool:
        """Process frames through RTX Video SDK."""
        try:
            import cv2
        except ImportError:
            logger.error("OpenCV (cv2) is required for frame processing")
            return False

        frame_files = sorted(input_dir.glob("frame_*.png"))
        total_frames = len(frame_files)

        if total_frames == 0:
            logger.error("No frames found to process")
            return False

        logger.debug(f"Processing {total_frames} frames")
        self._stats.total_frames = total_frames

        for i, frame_path in enumerate(frame_files):
            try:
                # Read frame
                frame = cv2.imread(str(frame_path))
                if frame is None:
                    logger.warning(f"Failed to read frame: {frame_path}")
                    self._stats.skipped_frames += 1
                    continue

                # Process through SDK
                processed = self._wrapper.process_frame(frame)

                # Save processed frame
                output_path = output_dir / frame_path.name
                cv2.imwrite(str(output_path), processed)

                self._stats.processed_frames += 1

                # Report progress (10-90% range for processing)
                progress = 10 + (i + 1) / total_frames * 80
                self._report_progress(progress, f"Processing frame {i+1}/{total_frames}")

            except Exception as e:
                logger.warning(f"Failed to process frame {frame_path.name}: {e}")
                self._stats.skipped_frames += 1
                # Copy original frame as fallback
                import shutil
                shutil.copy(str(frame_path), str(output_dir / frame_path.name))

        return self._stats.processed_frames > 0

    def _reassemble_video(
        self,
        frames_dir: Path,
        output_path: Path,
        video_info: dict,
    ) -> bool:
        """Reassemble frames into video."""
        fps = video_info.get("fps", 30.0)

        # Determine pixel format and encoder
        pix_fmt = "yuv420p"
        encoder = "hevc_nvenc"
        encoder_opts = ["-preset", "p7", "-cq", "18"]

        if self.config.enable_hdr_conversion:
            pix_fmt = "yuv420p10le"
            encoder_opts.extend([
                "-colorspace", "bt2020nc",
                "-color_primaries", "bt2020",
                "-color_trc", "smpte2084",  # PQ for HDR10
            ])

        cmd = [
            self.ffmpeg_path,
            "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%08d.png"),
            "-c:v", encoder,
            *encoder_opts,
            "-pix_fmt", pix_fmt,
            str(output_path),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug(f"Reassembled video to {output_path}")
            return True
        except subprocess.CalledProcessError as e:
            # Fallback to software encoder
            logger.warning(f"NVENC failed, trying software encoder: {e.stderr}")
            cmd[cmd.index("hevc_nvenc")] = "libx265"
            cmd = [arg for arg in cmd if arg not in ["-preset", "p7", "-cq"]]
            cmd.extend(["-crf", "18"])

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                return True
            except subprocess.CalledProcessError as e2:
                logger.error(f"Video reassembly failed: {e2.stderr}")
                return False

    def _mux_audio(
        self,
        video_path: Path,
        audio_source: Path,
        output_path: Path,
    ) -> bool:
        """Mux audio from source into output video."""
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", str(video_path),
            "-i", str(audio_source),
            "-map", "0:v:0",
            "-map", "1:a:0?",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output_path),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug(f"Muxed audio to {output_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"Audio mux failed, copying video only: {e.stderr}")
            import shutil
            shutil.move(str(video_path), str(output_path))
            return True

    def _report_progress(self, percentage: float, message: str = ""):
        """Report progress to callback if set."""
        if self.progress_callback:
            self.progress_callback(percentage)
        if message:
            logger.debug(f"[{percentage:.0f}%] {message}")
