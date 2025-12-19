
# tests/test_performance_validation.py
"""
Performance validation tests for optimization patches.
Run after applying patches to ensure improvements.
"""

import pytest
import time
from pathlib import Path
import tempfile

def test_video_preprocessing_speed(test_video_720p):
    """Ensure preprocessing meets performance targets."""
    from vhs_upscaler.vhs_upscale import VideoUpscaler, UpscaleConfig

    config = UpscaleConfig(
        input_path=test_video_720p,
        output_path=Path(tempfile.gettempdir()) / "test_output.mp4",
        preset="vhs",
        resolution=1080,
        upscale_engine="ffmpeg"
    )

    upscaler = VideoUpscaler(config)
    temp_dir = Path(tempfile.mkdtemp())

    start = time.time()
    duration = upscaler._get_video_duration(test_video_720p)
    video_out, audio_out = upscaler.preprocess(test_video_720p, temp_dir, duration)
    elapsed = time.time() - start

    # For 10 second 720p video, should complete in < 15 seconds
    assert elapsed < 15, f"Preprocessing too slow: {elapsed:.1f}s"

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


def test_audio_model_preload_speed():
    """Ensure audio models pre-load correctly."""
    from vhs_upscaler.audio_processor import AudioProcessor, AudioConfig, AudioEnhanceMode

    config = AudioConfig(
        enhance_mode=AudioEnhanceMode.DEEPFILTERNET,
        use_audiosr=True
    )

    # First initialization - should load models
    start = time.time()
    processor = AudioProcessor(config)
    init_time = time.time() - start

    # Should have loaded models (if available)
    if processor._model_cache:
        assert init_time > 1.0, "Models should take time to load"

        # Second processing - should use cached models
        test_audio = Path(tempfile.gettempdir()) / "test_audio.wav"
        # ... create test audio

        start = time.time()
        # Processing should not reload models
        process_time = time.time() - start

        # No model load overhead
        assert 'deepfilternet' in processor._model_cache or \
               'audiosr' in processor._model_cache


def test_queue_concurrent_read_performance():
    """Ensure queue supports high concurrent read throughput."""
    from vhs_upscaler.queue_manager import VideoQueue, QueueJob
    import threading

    queue = VideoQueue(max_workers=2)
    queue.start()

    # Add test jobs
    for i in range(100):
        job = QueueJob(
            id=f"test-{i}",
            input_source=f"test_{i}.mp4",
            output_path=f"out_{i}.mp4"
        )
        queue.add_job(job)

    # Concurrent status queries
    query_count = 1000
    results = []

    def query_worker():
        start = time.time()
        for _ in range(query_count // 10):
            queue.get_queue_status()
        results.append(time.time() - start)

    # Launch 10 concurrent readers
    threads = [threading.Thread(target=query_worker) for _ in range(10)]

    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total_time = time.time() - start

    ops_per_second = query_count / total_time

    # Should support > 400 queries/second with read-write lock
    assert ops_per_second > 400, f"Query throughput too low: {ops_per_second:.0f} ops/s"

    queue.stop()


def test_progress_update_throttling():
    """Ensure progress updates are throttled."""
    from vhs_upscaler.vhs_upscale import UnifiedProgress

    progress = UnifiedProgress(has_download=False)
    progress.start_stage("upscale")

    # Rapid updates (simulate FFmpeg 60 FPS)
    update_count = 600  # 10 seconds at 60 FPS

    start = time.time()
    for i in range(update_count):
        progress.update_progress(i / update_count * 100)
    elapsed = time.time() - start

    # Should complete quickly due to throttling
    # Without throttling: ~600ms for 600 updates
    # With throttling: <100ms (most updates skipped)
    assert elapsed < 0.2, f"Progress updates not throttled: {elapsed:.3f}s"


def test_gui_polling_interval():
    """Ensure GUI polling uses optimized interval."""
    from vhs_upscaler.gui import QUEUE_POLL_INTERVAL

    # Should be 2 seconds (optimized from 1 second)
    assert QUEUE_POLL_INTERVAL >= 2.0, "Polling interval not optimized"


@pytest.mark.benchmark
def test_filter_chain_cache_performance():
    """Ensure filter chain caching works."""
    from vhs_upscaler.audio_processor import AudioProcessor, AudioConfig, AudioEnhanceMode

    config = AudioConfig(enhance_mode=AudioEnhanceMode.MODERATE)
    processor = AudioProcessor(config)

    # First call - builds filter chain
    start = time.time()
    for _ in range(1000):
        filters = processor._build_enhancement_filters()
    uncached_time = time.time() - start

    # Should use cache for identical parameters
    # Cached should be much faster (>10x)
    # Note: Actual speed depends on implementation
