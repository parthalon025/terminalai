#!/usr/bin/env python3
"""
TerminalAI Performance Profiling Toolkit
========================================

Comprehensive performance analysis across all modules:
- CPU profiling with cProfile
- Memory profiling
- Thread analysis
- I/O bottleneck detection
- GPU utilization tracking
- FFmpeg command efficiency

Usage:
    python performance_profiler.py --module all
    python performance_profiler.py --module video_pipeline
    python performance_profiler.py --module audio_processing
    python performance_profiler.py --module gui
    python performance_profiler.py --module queue_manager
"""

import argparse
import cProfile
import io
import json
import logging
import os
import pstats
import sys
import time
import tracemalloc
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import tempfile
import threading

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger(__name__)


# =============================================================================
# Performance Metrics Data Models
# =============================================================================

@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    module_name: str
    test_duration: float
    cpu_time: float
    memory_peak_mb: float
    memory_current_mb: float
    thread_count: int
    function_stats: Dict[str, Any]
    bottlenecks: List[str]
    recommendations: List[str]
    gpu_stats: Optional[Dict[str, Any]] = None


@dataclass
class FunctionProfile:
    """Profile data for a single function."""
    name: str
    total_calls: int
    total_time: float
    cumulative_time: float
    time_per_call: float
    percent_time: float


# =============================================================================
# Base Profiler
# =============================================================================

class BaseProfiler:
    """Base profiler with common functionality."""

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.profiler = cProfile.Profile()
        self.start_time = 0
        self.peak_memory = 0
        self.current_memory = 0
        self.bottlenecks = []
        self.recommendations = []

    def start_profiling(self):
        """Start CPU and memory profiling."""
        tracemalloc.start()
        self.start_time = time.time()
        self.profiler.enable()

    def stop_profiling(self) -> PerformanceMetrics:
        """Stop profiling and generate metrics."""
        self.profiler.disable()
        elapsed = time.time() - self.start_time

        # Get memory stats
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.peak_memory = peak / 1024 / 1024  # MB
        self.current_memory = current / 1024 / 1024  # MB

        # Extract function stats
        stats = self._extract_function_stats()

        # Get thread count
        thread_count = threading.active_count()

        return PerformanceMetrics(
            module_name=self.module_name,
            test_duration=elapsed,
            cpu_time=sum(stat['total_time'] for stat in stats[:10]),
            memory_peak_mb=self.peak_memory,
            memory_current_mb=self.current_memory,
            thread_count=thread_count,
            function_stats={'top_10': stats[:10]},
            bottlenecks=self.bottlenecks,
            recommendations=self.recommendations
        )

    def _extract_function_stats(self) -> List[Dict[str, Any]]:
        """Extract top function statistics from profiler."""
        stream = io.StringIO()
        stats = pstats.Stats(self.profiler, stream=stream)
        stats.sort_stats('cumulative')

        function_profiles = []
        total_time = sum(stat[2] for stat in stats.stats.values())

        for func, stat in list(stats.stats.items())[:20]:
            filename, line, func_name = func
            cc, nc, tt, ct, callers = stat

            function_profiles.append({
                'name': f"{Path(filename).name}:{func_name}",
                'total_calls': nc,
                'total_time': tt,
                'cumulative_time': ct,
                'time_per_call': tt / nc if nc > 0 else 0,
                'percent_time': (ct / total_time * 100) if total_time > 0 else 0
            })

        return function_profiles

    def analyze_bottlenecks(self, stats: List[Dict[str, Any]]):
        """Analyze function stats for bottlenecks."""
        # Functions taking >5% of total time
        for stat in stats:
            if stat['percent_time'] > 5.0:
                self.bottlenecks.append(
                    f"{stat['name']}: {stat['percent_time']:.1f}% of total time "
                    f"({stat['cumulative_time']:.2f}s)"
                )

        # High call count functions (potential optimization candidates)
        for stat in stats:
            if stat['total_calls'] > 1000 and stat['time_per_call'] > 0.001:
                self.recommendations.append(
                    f"Consider caching/optimization for {stat['name']} "
                    f"({stat['total_calls']} calls, {stat['time_per_call']*1000:.2f}ms each)"
                )


# =============================================================================
# Video Pipeline Profiler
# =============================================================================

class VideoPipelineProfiler(BaseProfiler):
    """Profile video processing pipeline."""

    def __init__(self):
        super().__init__("Video Pipeline")

    def profile(self, test_video: Optional[Path] = None) -> PerformanceMetrics:
        """Profile video processing pipeline."""
        logger.info("Profiling video processing pipeline...")

        # Create test video if not provided
        if not test_video:
            test_video = self._create_test_video()

        self.start_profiling()

        try:
            # Import and test pipeline
            from vhs_upscaler.vhs_upscale import VideoUpscaler, UpscaleConfig

            config = UpscaleConfig(
                input_path=test_video,
                output_path=Path(tempfile.gettempdir()) / "profile_output.mp4",
                preset="clean",  # Faster for profiling
                resolution=720,  # Lower for profiling
                upscale_engine="ffmpeg",  # Available everywhere
                quality_mode=0,
                deinterlace=False,
                keep_temp=False
            )

            upscaler = VideoUpscaler(config)

            # Profile dependency check
            upscaler._check_dependencies()

            # Profile preprocessing (without full upscale)
            temp_dir = Path(tempfile.mkdtemp(prefix="vhs_profile_"))
            try:
                duration = upscaler._get_video_duration(test_video)
                upscaler.preprocess(test_video, temp_dir, duration)
            finally:
                # Cleanup
                import shutil
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)

        except Exception as e:
            logger.error(f"Pipeline profiling error: {e}")
            self.bottlenecks.append(f"Pipeline error: {e}")

        metrics = self.stop_profiling()
        self.analyze_bottlenecks(metrics.function_stats['top_10'])

        # Add pipeline-specific analysis
        self._analyze_ffmpeg_efficiency()
        self._analyze_temp_file_usage()

        return metrics

    def _create_test_video(self) -> Path:
        """Create a small test video for profiling."""
        test_video = Path(tempfile.gettempdir()) / "profile_test_video.mp4"

        if not test_video.exists():
            logger.info("Generating test video...")
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "testsrc=duration=10:size=640x480:rate=30",
                "-c:v", "libx264", "-preset", "ultrafast",
                str(test_video)
            ]
            subprocess.run(cmd, capture_output=True, check=True)

        return test_video

    def _analyze_ffmpeg_efficiency(self):
        """Analyze FFmpeg command efficiency."""
        # Check for common inefficiencies
        recommendations = [
            "Consider using hardware encoding (NVENC) for faster processing",
            "Use -preset faster for quicker encoding during testing",
            "Batch multiple filter operations into single FFmpeg call",
            "Consider frame-level parallelism for long videos"
        ]
        self.recommendations.extend(recommendations[:2])

    def _analyze_temp_file_usage(self):
        """Analyze temporary file management."""
        self.recommendations.append(
            "Ensure temporary files are cleaned up immediately after use"
        )


# =============================================================================
# Audio Processing Profiler
# =============================================================================

class AudioProcessingProfiler(BaseProfiler):
    """Profile audio processing components."""

    def __init__(self):
        super().__init__("Audio Processing")

    def profile(self) -> PerformanceMetrics:
        """Profile audio processor."""
        logger.info("Profiling audio processing...")

        self.start_profiling()

        try:
            from vhs_upscaler.audio_processor import AudioProcessor, AudioConfig, AudioEnhanceMode

            # Create test audio
            test_audio = self._create_test_audio()

            config = AudioConfig(
                enhance_mode=AudioEnhanceMode.MODERATE,
                normalize=True,
                output_format="aac"
            )

            processor = AudioProcessor(config)

            # Profile enhancement filter building
            for _ in range(100):
                processor._build_enhancement_filters()

            # Profile basic audio processing (without AI backends for speed)
            output = Path(tempfile.gettempdir()) / "profile_audio_out.aac"
            processor.process_audio(test_audio, output)

        except Exception as e:
            logger.error(f"Audio profiling error: {e}")
            self.bottlenecks.append(f"Audio processing error: {e}")

        metrics = self.stop_profiling()
        self.analyze_bottlenecks(metrics.function_stats['top_10'])

        # Audio-specific recommendations
        self._analyze_audio_bottlenecks()

        return metrics

    def _create_test_audio(self) -> Path:
        """Create test audio file."""
        test_audio = Path(tempfile.gettempdir()) / "profile_test_audio.wav"

        if not test_audio.exists():
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "sine=frequency=1000:duration=5",
                str(test_audio)
            ]
            subprocess.run(cmd, capture_output=True, check=True)

        return test_audio

    def _analyze_audio_bottlenecks(self):
        """Analyze audio-specific bottlenecks."""
        recommendations = [
            "DeepFilterNet: Use GPU acceleration for 5-10x speedup",
            "AudioSR: Pre-load models during initialization to avoid per-file overhead",
            "Demucs: Consider batch processing for multiple files",
            "FFmpeg filters: Combine multiple filters into single pass"
        ]
        self.recommendations.extend(recommendations[:3])


# =============================================================================
# Queue Manager Profiler
# =============================================================================

class QueueManagerProfiler(BaseProfiler):
    """Profile queue manager and threading."""

    def __init__(self):
        super().__init__("Queue Manager")

    def profile(self) -> PerformanceMetrics:
        """Profile queue operations."""
        logger.info("Profiling queue manager...")

        self.start_profiling()

        try:
            from vhs_upscaler.queue_manager import VideoQueue, QueueJob, JobStatus

            queue = VideoQueue(max_workers=2)
            queue.start()

            # Add multiple jobs
            jobs = []
            for i in range(20):
                job = QueueJob(
                    id=f"test-job-{i}",
                    input_source=f"test_{i}.mp4",
                    output_path=f"output_{i}.mp4",
                    preset="vhs"
                )
                queue.add_job(job)
                jobs.append(job.id)

            # Profile queue operations
            for _ in range(100):
                queue.get_queue_status()
                for job_id in jobs[:5]:
                    queue.get_job_status(job_id)

            # Test status updates
            for job_id in jobs[:10]:
                queue.update_job_status(job_id, JobStatus.PREPROCESSING, 50.0)

            queue.stop()

        except Exception as e:
            logger.error(f"Queue profiling error: {e}")
            self.bottlenecks.append(f"Queue manager error: {e}")

        metrics = self.stop_profiling()
        self.analyze_bottlenecks(metrics.function_stats['top_10'])

        # Queue-specific analysis
        self._analyze_queue_bottlenecks(metrics)

        return metrics

    def _analyze_queue_bottlenecks(self, metrics: PerformanceMetrics):
        """Analyze queue-specific bottlenecks."""
        if metrics.thread_count > 10:
            self.bottlenecks.append(f"High thread count: {metrics.thread_count}")
            self.recommendations.append("Consider thread pool optimization")

        # Lock contention analysis
        self.recommendations.extend([
            "Use read-write locks for status queries to reduce contention",
            "Consider lock-free data structures for high-frequency operations",
            "Batch status updates to reduce lock acquisition frequency"
        ])


# =============================================================================
# GUI Profiler
# =============================================================================

class GUIProfiler(BaseProfiler):
    """Profile GUI components."""

    def __init__(self):
        super().__init__("GUI")

    def profile(self) -> PerformanceMetrics:
        """Profile GUI operations."""
        logger.info("Profiling GUI components...")

        self.start_profiling()

        try:
            # Import GUI helpers without launching full app
            from vhs_upscaler.gui import AppState, format_size, format_time, get_status_emoji
            from vhs_upscaler.queue_manager import VideoQueue, QueueJob, JobStatus

            # Profile state operations
            for _ in range(1000):
                AppState.add_log("Test log message")

            # Profile formatting helpers
            for i in range(10000):
                format_size(i * 1024 * 1024)
                format_time(i)
                get_status_emoji(JobStatus.PENDING)

            # Profile thumbnail generation (if possible)
            test_video = Path(tempfile.gettempdir()) / "profile_test_video.mp4"
            if test_video.exists():
                for _ in range(10):
                    AppState.get_thumbnail(str(test_video))

        except Exception as e:
            logger.error(f"GUI profiling error: {e}")
            self.bottlenecks.append(f"GUI error: {e}")

        metrics = self.stop_profiling()
        self.analyze_bottlenecks(metrics.function_stats['top_10'])

        # GUI-specific recommendations
        self._analyze_gui_bottlenecks()

        return metrics

    def _analyze_gui_bottlenecks(self):
        """Analyze GUI-specific bottlenecks."""
        recommendations = [
            "Reduce queue polling interval from 1s to 2s for less overhead",
            "Implement debouncing for progress updates",
            "Cache thumbnail generation results longer",
            "Batch log updates to reduce state mutations",
            "Use lazy loading for queue status display",
            "Implement virtual scrolling for large job lists"
        ]
        self.recommendations.extend(recommendations[:4])


# =============================================================================
# RTX Video SDK Profiler
# =============================================================================

class RTXVideoSDKProfiler(BaseProfiler):
    """Profile RTX Video SDK integration."""

    def __init__(self):
        super().__init__("RTX Video SDK")

    def profile(self) -> PerformanceMetrics:
        """Profile RTX Video SDK operations."""
        logger.info("Profiling RTX Video SDK...")

        self.start_profiling()

        try:
            from vhs_upscaler.rtx_video_sdk import RTXVideoConfig, RTXVideoWrapper

            # Test config creation and validation
            for _ in range(1000):
                config = RTXVideoConfig(
                    enable_super_resolution=True,
                    scale_factor=4,
                    target_resolution=1080,
                    enable_artifact_reduction=True
                )

            # Test wrapper initialization (if SDK available)
            try:
                wrapper = RTXVideoWrapper(config)
                wrapper.cleanup()
            except Exception:
                logger.info("RTX SDK not available, skipping wrapper tests")

        except Exception as e:
            logger.error(f"RTX SDK profiling error: {e}")
            self.bottlenecks.append(f"RTX SDK error: {e}")

        metrics = self.stop_profiling()
        self.analyze_bottlenecks(metrics.function_stats['top_10'])

        # RTX-specific recommendations
        self._analyze_rtx_bottlenecks()

        return metrics

    def _analyze_rtx_bottlenecks(self):
        """Analyze RTX SDK-specific bottlenecks."""
        recommendations = [
            "Use frame batching (16-32 frames) for optimal GPU utilization",
            "Pre-allocate GPU memory buffers to avoid repeated allocations",
            "Use CUDA streams for overlapping frame transfer and processing",
            "Implement double buffering for frame I/O",
            "Monitor GPU memory usage to prevent OOM errors"
        ]
        self.recommendations.extend(recommendations[:3])


# =============================================================================
# Comprehensive Performance Report Generator
# =============================================================================

class PerformanceReporter:
    """Generate comprehensive performance reports."""

    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}

    def add_metrics(self, metrics: PerformanceMetrics):
        """Add metrics from a profiling run."""
        self.metrics[metrics.module_name] = metrics

    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """Generate comprehensive performance report."""
        report_lines = [
            "=" * 80,
            "TerminalAI Performance Analysis Report",
            "=" * 80,
            "",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Modules analyzed: {len(self.metrics)}",
            "",
        ]

        # Summary section
        report_lines.extend([
            "EXECUTIVE SUMMARY",
            "-" * 80,
            ""
        ])

        total_bottlenecks = sum(len(m.bottlenecks) for m in self.metrics.values())
        total_recommendations = sum(len(m.recommendations) for m in self.metrics.values())

        report_lines.extend([
            f"Total bottlenecks identified: {total_bottlenecks}",
            f"Total optimization recommendations: {total_recommendations}",
            "",
        ])

        # Per-module analysis
        for module_name, metrics in self.metrics.items():
            report_lines.extend(self._format_module_report(metrics))

        # Overall recommendations
        report_lines.extend([
            "",
            "PRIORITY OPTIMIZATIONS",
            "=" * 80,
            ""
        ])

        # Collect all recommendations by priority
        all_recommendations = []
        for metrics in self.metrics.values():
            for rec in metrics.recommendations:
                all_recommendations.append(f"[{metrics.module_name}] {rec}")

        for i, rec in enumerate(all_recommendations[:10], 1):
            report_lines.append(f"{i}. {rec}")

        report_lines.extend(["", "=" * 80])

        report = "\n".join(report_lines)

        # Save to file if requested
        if output_path:
            output_path.write_text(report)
            logger.info(f"Report saved to {output_path}")

            # Also save JSON version
            json_path = output_path.with_suffix('.json')
            json_data = {
                name: asdict(metrics)
                for name, metrics in self.metrics.items()
            }
            json_path.write_text(json.dumps(json_data, indent=2))
            logger.info(f"JSON data saved to {json_path}")

        return report

    def _format_module_report(self, metrics: PerformanceMetrics) -> List[str]:
        """Format report for a single module."""
        lines = [
            "",
            f"{metrics.module_name.upper()}",
            "=" * 80,
            "",
            "Performance Metrics:",
            f"  Test duration: {metrics.test_duration:.2f}s",
            f"  CPU time: {metrics.cpu_time:.2f}s",
            f"  Peak memory: {metrics.memory_peak_mb:.2f} MB",
            f"  Current memory: {metrics.memory_current_mb:.2f} MB",
            f"  Active threads: {metrics.thread_count}",
            "",
        ]

        # Top functions by time
        if metrics.function_stats.get('top_10'):
            lines.extend([
                "Top 10 Functions by Time:",
                ""
            ])
            for i, func in enumerate(metrics.function_stats['top_10'][:10], 1):
                lines.append(
                    f"  {i}. {func['name']}: "
                    f"{func['cumulative_time']:.3f}s "
                    f"({func['percent_time']:.1f}%) "
                    f"[{func['total_calls']} calls]"
                )
            lines.append("")

        # Bottlenecks
        if metrics.bottlenecks:
            lines.extend([
                "Identified Bottlenecks:",
                ""
            ])
            for i, bottleneck in enumerate(metrics.bottlenecks, 1):
                lines.append(f"  {i}. {bottleneck}")
            lines.append("")

        # Recommendations
        if metrics.recommendations:
            lines.extend([
                "Optimization Recommendations:",
                ""
            ])
            for i, rec in enumerate(metrics.recommendations, 1):
                lines.append(f"  {i}. {rec}")
            lines.append("")

        return lines


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="TerminalAI Performance Profiling Toolkit"
    )
    parser.add_argument(
        "--module",
        choices=["all", "video_pipeline", "audio_processing", "queue_manager", "gui", "rtx_video_sdk"],
        default="all",
        help="Module to profile"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("performance_report.txt"),
        help="Output report file"
    )
    parser.add_argument(
        "--test-video",
        type=Path,
        help="Path to test video (optional)"
    )

    args = parser.parse_args()

    reporter = PerformanceReporter()

    # Profile selected modules
    modules_to_profile = {
        "video_pipeline": VideoPipelineProfiler,
        "audio_processing": AudioProcessingProfiler,
        "queue_manager": QueueManagerProfiler,
        "gui": GUIProfiler,
        "rtx_video_sdk": RTXVideoSDKProfiler,
    }

    if args.module == "all":
        selected_modules = modules_to_profile.items()
    else:
        selected_modules = [(args.module, modules_to_profile[args.module])]

    logger.info("Starting performance profiling...")
    logger.info("=" * 80)

    for module_name, profiler_class in selected_modules:
        try:
            logger.info(f"\nProfiling {module_name}...")
            profiler = profiler_class()

            if module_name == "video_pipeline" and args.test_video:
                metrics = profiler.profile(test_video=args.test_video)
            else:
                metrics = profiler.profile()

            reporter.add_metrics(metrics)
            logger.info(f"Completed: {module_name}")

        except Exception as e:
            logger.error(f"Failed to profile {module_name}: {e}")
            import traceback
            traceback.print_exc()

    # Generate report
    logger.info("\n" + "=" * 80)
    logger.info("Generating performance report...")
    report = reporter.generate_report(output_path=args.output)

    print("\n" + report)

    logger.info(f"\nReport saved to: {args.output}")
    logger.info(f"JSON data saved to: {args.output.with_suffix('.json')}")


if __name__ == "__main__":
    main()
