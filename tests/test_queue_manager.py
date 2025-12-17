"""
Tests for Queue Manager
=======================
Tests for VideoQueue, QueueJob, and JobStatus functionality.
"""

import pytest
import sys
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import threading

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "vhs_upscaler"))


class TestJobStatus:
    """Tests for JobStatus enum."""

    def test_all_statuses_exist(self):
        from vhs_upscaler.queue_manager import JobStatus

        statuses = [
            JobStatus.PENDING,
            JobStatus.DOWNLOADING,
            JobStatus.PREPROCESSING,
            JobStatus.UPSCALING,
            JobStatus.ENCODING,
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED
        ]
        assert len(statuses) == 8

    def test_status_values(self):
        from vhs_upscaler.queue_manager import JobStatus

        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"


class TestQueueJob:
    """Tests for QueueJob dataclass."""

    def test_job_creation(self):
        from vhs_upscaler.queue_manager import QueueJob, JobStatus

        job = QueueJob(
            id="test123",
            input_source="/path/to/video.mp4",
            output_path="/path/to/output.mp4"
        )

        assert job.id == "test123"
        assert job.input_source == "/path/to/video.mp4"
        assert job.status == JobStatus.PENDING

    def test_job_defaults(self):
        from vhs_upscaler.queue_manager import QueueJob

        job = QueueJob(
            id="test",
            input_source="/video.mp4",
            output_path="/output.mp4"
        )

        assert job.preset == "vhs"
        assert job.resolution == 1080
        assert job.quality == 0
        assert job.crf == 20
        assert job.encoder == "hevc_nvenc"
        assert job.progress == 0.0

    def test_job_to_dict(self, sample_job):
        result = sample_job.to_dict()

        assert isinstance(result, dict)
        assert result["id"] == "test123"
        assert result["input_source"] == "/path/to/video.mp4"
        assert result["status"] == "pending"

    def test_job_from_dict(self):
        from vhs_upscaler.queue_manager import QueueJob

        data = {
            "id": "from_dict",
            "input_source": "/video.mp4",
            "output_path": "/output.mp4",
            "preset": "dvd",
            "resolution": 720,
            "status": "completed"
        }

        job = QueueJob.from_dict(data)
        assert job.id == "from_dict"
        assert job.preset == "dvd"
        assert job.resolution == 720


class TestVideoQueue:
    """Tests for VideoQueue class."""

    def test_queue_initialization(self, temp_dir):
        from vhs_upscaler.queue_manager import VideoQueue

        queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        assert queue is not None
        assert not queue.is_processing()

    def test_add_job(self, temp_dir):
        from vhs_upscaler.queue_manager import VideoQueue

        queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        job = queue.add_job(
            input_source="/video.mp4",
            output_path="/output.mp4",
            preset="vhs",
            resolution=1080
        )

        assert job is not None
        assert job.input_source == "/video.mp4"
        assert len(queue.get_all_jobs()) == 1

    def test_get_queue_stats(self, temp_dir):
        from vhs_upscaler.queue_manager import VideoQueue

        queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        # Add some jobs
        queue.add_job("/video1.mp4", "/output1.mp4")
        queue.add_job("/video2.mp4", "/output2.mp4")

        stats = queue.get_queue_stats()

        assert stats["total"] == 2
        assert stats["pending"] == 2
        assert stats["processing"] == 0
        assert stats["completed"] == 0

    def test_clear_completed(self, temp_dir):
        from vhs_upscaler.queue_manager import VideoQueue, JobStatus

        queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        # Add job and manually mark as completed
        job = queue.add_job("/video.mp4", "/output.mp4")
        job.status = JobStatus.COMPLETED

        queue.clear_completed()

        # Should have 0 jobs after clearing
        assert len(queue.get_all_jobs()) == 0

    def test_cancel_job(self, temp_dir):
        from vhs_upscaler.queue_manager import VideoQueue, JobStatus

        queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        job = queue.add_job("/video.mp4", "/output.mp4")
        result = queue.cancel_job(job.id)

        assert result is True
        assert job.status == JobStatus.CANCELLED

    def test_get_job_by_id(self, temp_dir):
        from vhs_upscaler.queue_manager import VideoQueue

        queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        job = queue.add_job("/video.mp4", "/output.mp4")
        retrieved = queue.get_job(job.id)

        assert retrieved is not None
        assert retrieved.id == job.id

    def test_get_nonexistent_job(self, temp_dir):
        from vhs_upscaler.queue_manager import VideoQueue

        queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        result = queue.get_job("nonexistent")
        assert result is None

    def test_persistence_save(self, temp_dir):
        from vhs_upscaler.queue_manager import VideoQueue

        persistence_file = temp_dir / "queue.json"

        queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=persistence_file
        )

        queue.add_job("/video.mp4", "/output.mp4")
        queue.save_state()

        assert persistence_file.exists()

        # Verify content
        with open(persistence_file) as f:
            data = json.load(f)
        assert len(data["jobs"]) == 1

    def test_persistence_load(self, temp_dir):
        from vhs_upscaler.queue_manager import VideoQueue

        persistence_file = temp_dir / "queue.json"

        # Create initial queue and save
        queue1 = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=persistence_file
        )
        queue1.add_job("/video.mp4", "/output.mp4")
        queue1.save_state()

        # Create new queue and load
        queue2 = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=persistence_file
        )

        assert len(queue2.get_all_jobs()) == 1

    def test_start_and_pause_processing(self, temp_dir):
        from vhs_upscaler.queue_manager import VideoQueue

        queue = VideoQueue(
            processor_func=MagicMock(return_value=True),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        queue.start_processing()
        assert queue.is_processing()

        queue.pause_processing()
        # Give time for the queue to recognize pause
        time.sleep(0.1)
        # Note: is_processing may still return True until current job finishes

    def test_add_jobs_batch(self, temp_dir):
        from vhs_upscaler.queue_manager import VideoQueue

        queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        jobs_data = [
            {"input_source": "/video1.mp4", "output_path": "/output1.mp4"},
            {"input_source": "/video2.mp4", "output_path": "/output2.mp4"},
            {"input_source": "/video3.mp4", "output_path": "/output3.mp4"}
        ]

        jobs = queue.add_jobs_batch(jobs_data)

        assert len(jobs) == 3
        assert len(queue.get_all_jobs()) == 3


class TestGUIQueueIntegration:
    """Integration tests for GUI queue operations."""

    def test_add_to_queue_empty_input(self, temp_dir):
        from vhs_upscaler.gui import add_to_queue, AppState
        from vhs_upscaler.queue_manager import VideoQueue

        AppState.queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        status, display = add_to_queue("", "vhs", 1080, 0, 20, "hevc_nvenc")
        assert "Please enter" in status

    def test_add_to_queue_whitespace_input(self, temp_dir):
        from vhs_upscaler.gui import add_to_queue, AppState
        from vhs_upscaler.queue_manager import VideoQueue

        AppState.queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        status, display = add_to_queue("   ", "vhs", 1080, 0, 20, "hevc_nvenc")
        assert "Please enter" in status

    def test_add_to_queue_valid_input(self, temp_dir):
        from vhs_upscaler.gui import add_to_queue, AppState
        from vhs_upscaler.queue_manager import VideoQueue

        AppState.output_dir = temp_dir
        AppState.queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        status, display = add_to_queue("/video.mp4", "vhs", 1080, 0, 20, "hevc_nvenc")
        assert "Added to queue" in status

    def test_add_multiple_to_queue_empty(self, temp_dir):
        from vhs_upscaler.gui import add_multiple_to_queue, AppState
        from vhs_upscaler.queue_manager import VideoQueue

        AppState.queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        status, display = add_multiple_to_queue("", "vhs", 1080, 0, 20, "hevc_nvenc")
        assert "Please enter" in status

    def test_add_multiple_to_queue_valid(self, temp_dir):
        from vhs_upscaler.gui import add_multiple_to_queue, AppState
        from vhs_upscaler.queue_manager import VideoQueue

        AppState.output_dir = temp_dir
        AppState.queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        urls = "/video1.mp4\n/video2.mp4\n/video3.mp4"
        status, display = add_multiple_to_queue(urls, "vhs", 1080, 0, 20, "hevc_nvenc")
        assert "Added 3 videos" in status

    def test_start_queue(self, temp_dir):
        from vhs_upscaler.gui import start_queue, AppState
        from vhs_upscaler.queue_manager import VideoQueue

        AppState.queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        status, display = start_queue()
        assert "started" in status.lower()

    def test_pause_queue(self, temp_dir):
        from vhs_upscaler.gui import pause_queue, AppState
        from vhs_upscaler.queue_manager import VideoQueue

        AppState.queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        status, display = pause_queue()
        assert "paused" in status.lower()

    def test_clear_completed_queue(self, temp_dir):
        from vhs_upscaler.gui import clear_completed, AppState
        from vhs_upscaler.queue_manager import VideoQueue

        AppState.queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        status, display = clear_completed()
        assert "Cleared" in status


class TestQueueDisplayGeneration:
    """Tests for queue display HTML generation."""

    def test_empty_queue_display(self, temp_dir):
        from vhs_upscaler.gui import get_queue_display, AppState
        from vhs_upscaler.queue_manager import VideoQueue

        AppState.queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        html = get_queue_display()
        assert "Queue is empty" in html

    def test_queue_with_jobs_display(self, temp_dir):
        from vhs_upscaler.gui import get_queue_display, AppState
        from vhs_upscaler.queue_manager import VideoQueue

        AppState.queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )
        AppState.queue.add_job("/video.mp4", "/output.mp4")

        html = get_queue_display()
        assert "Queue Status" in html
        assert "pending" in html.lower()

    def test_stats_display(self, temp_dir):
        from vhs_upscaler.gui import get_stats_display, AppState
        from vhs_upscaler.queue_manager import VideoQueue

        AppState.queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )

        html = get_stats_display()
        assert "Pending" in html
        assert "Completed" in html
        assert "Processing" in html
