"""
Pytest Configuration and Fixtures
=================================
Shared fixtures and configuration for all tests.
"""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "vhs_upscaler"))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_video_path(temp_dir):
    """Create a mock video file path."""
    video_path = temp_dir / "test_video.mp4"
    # Create empty file
    video_path.touch()
    return str(video_path)


@pytest.fixture
def mock_queue():
    """Create a mock VideoQueue instance."""
    from vhs_upscaler.queue_manager import VideoQueue, QueueJob, JobStatus

    with patch.object(VideoQueue, '__init__', lambda self, **kwargs: None):
        queue = VideoQueue()
        queue._jobs = []
        queue._lock = MagicMock()
        queue._processing = False
        queue._paused = False

        # Mock methods
        queue.get_all_jobs = MagicMock(return_value=[])
        queue.get_queue_stats = MagicMock(return_value={
            'total': 0,
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'failed': 0,
            'cancelled': 0
        })
        queue.is_processing = MagicMock(return_value=False)
        queue.add_job = MagicMock()
        queue.start_processing = MagicMock()
        queue.pause_processing = MagicMock()
        queue.clear_completed = MagicMock()

        yield queue


@pytest.fixture
def mock_app_state(mock_queue, temp_dir):
    """Setup mock application state."""
    from vhs_upscaler.gui import AppState

    original_queue = AppState.queue
    original_output_dir = AppState.output_dir
    original_logs = AppState.logs.copy()

    AppState.queue = mock_queue
    AppState.output_dir = temp_dir
    AppState.logs = []
    AppState.dark_mode = False

    yield AppState

    # Restore
    AppState.queue = original_queue
    AppState.output_dir = original_output_dir
    AppState.logs = original_logs


@pytest.fixture
def sample_job():
    """Create a sample QueueJob for testing."""
    from vhs_upscaler.queue_manager import QueueJob, JobStatus

    return QueueJob(
        id="test123",
        input_source="/path/to/video.mp4",
        output_path="/path/to/output.mp4",
        preset="vhs",
        resolution=1080,
        quality=0,
        crf=20,
        encoder="hevc_nvenc",
        status=JobStatus.PENDING,
        progress=0.0,
        stage_progress=0.0,
        current_stage="",
        error_message="",
        video_title="Test Video"
    )


@pytest.fixture
def completed_job():
    """Create a completed job for testing."""
    from vhs_upscaler.queue_manager import QueueJob, JobStatus

    return QueueJob(
        id="comp456",
        input_source="/path/to/video.mp4",
        output_path="/path/to/output.mp4",
        preset="dvd",
        resolution=1080,
        quality=0,
        crf=20,
        encoder="hevc_nvenc",
        status=JobStatus.COMPLETED,
        progress=100.0,
        stage_progress=100.0,
        current_stage="Completed",
        error_message="",
        video_title="Completed Video",
        output_size=1024 * 1024 * 500,  # 500 MB
        processing_time=3600  # 1 hour
    )
