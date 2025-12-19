#!/usr/bin/env python
"""Test programmatic API usage for vhs_upscaler package."""

import pytest


def test_package_import():
    """Test that vhs_upscaler package can be imported."""
    import vhs_upscaler
    assert hasattr(vhs_upscaler, '__version__')


def test_queue_api():
    """Test VideoQueue and QueueJob API."""
    from vhs_upscaler import VideoQueue, QueueJob, JobStatus

    # Create queue
    queue = VideoQueue()
    assert queue is not None

    # Test job creation
    job = QueueJob(
        id="test-001",
        input_source="/path/to/input.mp4",
        output_path="/path/to/output.mp4",
        preset="vhs",
        resolution=1080
    )
    assert job.id == "test-001"
    assert job.input_source == "/path/to/input.mp4"
    assert job.status == JobStatus.PENDING

    # Test status enum values exist
    assert hasattr(JobStatus, 'PENDING')
    assert hasattr(JobStatus, 'PREPROCESSING')
    assert hasattr(JobStatus, 'COMPLETED')
    assert hasattr(JobStatus, 'FAILED')


def test_logger_api():
    """Test logger API."""
    from vhs_upscaler import get_logger

    logger = get_logger(__name__)
    assert logger is not None

    # Test that logger has standard methods
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'debug')
    assert hasattr(logger, 'warning')
    assert hasattr(logger, 'error')
