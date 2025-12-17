"""
Unit Tests for GUI Helper Functions
===================================
Tests for format_file_size, format_duration, get_status_emoji, etc.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import timedelta

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "vhs_upscaler"))


class TestFormatFileSize:
    """Tests for format_file_size function."""

    def test_zero_bytes(self):
        from vhs_upscaler.gui import format_file_size
        assert format_file_size(0) == "0 B"

    def test_bytes(self):
        from vhs_upscaler.gui import format_file_size
        assert format_file_size(500) == "500.0 B"

    def test_kilobytes(self):
        from vhs_upscaler.gui import format_file_size
        result = format_file_size(1024)
        assert "KB" in result
        assert "1.0" in result

    def test_megabytes(self):
        from vhs_upscaler.gui import format_file_size
        result = format_file_size(1024 * 1024 * 5)  # 5 MB
        assert "MB" in result
        assert "5.0" in result

    def test_gigabytes(self):
        from vhs_upscaler.gui import format_file_size
        result = format_file_size(1024 * 1024 * 1024 * 2)  # 2 GB
        assert "GB" in result
        assert "2.0" in result

    def test_terabytes(self):
        from vhs_upscaler.gui import format_file_size
        result = format_file_size(1024 * 1024 * 1024 * 1024 * 3)  # 3 TB
        assert "TB" in result
        assert "3.0" in result


class TestFormatDuration:
    """Tests for format_duration function."""

    def test_zero_seconds(self):
        from vhs_upscaler.gui import format_duration
        assert format_duration(0) == "0:00:00"

    def test_negative_seconds(self):
        from vhs_upscaler.gui import format_duration
        assert format_duration(-10) == "0:00:00"

    def test_seconds_only(self):
        from vhs_upscaler.gui import format_duration
        result = format_duration(45)
        assert "0:00:45" in result

    def test_minutes_and_seconds(self):
        from vhs_upscaler.gui import format_duration
        result = format_duration(125)  # 2 min 5 sec
        assert "0:02:05" in result

    def test_hours(self):
        from vhs_upscaler.gui import format_duration
        result = format_duration(3661)  # 1 hour 1 min 1 sec
        assert "1:01:01" in result

    def test_float_truncation(self):
        from vhs_upscaler.gui import format_duration
        result = format_duration(90.7)  # Should round down
        assert "0:01:30" in result


class TestGetStatusEmoji:
    """Tests for get_status_emoji function."""

    def test_pending_status(self):
        from vhs_upscaler.gui import get_status_emoji, JobStatus
        assert get_status_emoji(JobStatus.PENDING) == "⏳"

    def test_downloading_status(self):
        from vhs_upscaler.gui import get_status_emoji, JobStatus
        assert get_status_emoji(JobStatus.DOWNLOADING) == "⬇️"

    def test_preprocessing_status(self):
        from vhs_upscaler.gui import get_status_emoji, JobStatus
        assert get_status_emoji(JobStatus.PREPROCESSING) == "🔄"

    def test_upscaling_status(self):
        from vhs_upscaler.gui import get_status_emoji, JobStatus
        assert get_status_emoji(JobStatus.UPSCALING) == "🚀"

    def test_encoding_status(self):
        from vhs_upscaler.gui import get_status_emoji, JobStatus
        assert get_status_emoji(JobStatus.ENCODING) == "💾"

    def test_completed_status(self):
        from vhs_upscaler.gui import get_status_emoji, JobStatus
        assert get_status_emoji(JobStatus.COMPLETED) == "✅"

    def test_failed_status(self):
        from vhs_upscaler.gui import get_status_emoji, JobStatus
        assert get_status_emoji(JobStatus.FAILED) == "❌"

    def test_cancelled_status(self):
        from vhs_upscaler.gui import get_status_emoji, JobStatus
        assert get_status_emoji(JobStatus.CANCELLED) == "🚫"


class TestGenerateOutputPath:
    """Tests for generate_output_path function."""

    def test_local_file_path(self, temp_dir):
        from vhs_upscaler.gui import generate_output_path, AppState

        AppState.output_dir = temp_dir

        result = generate_output_path("/path/to/my_video.mp4", 1080)
        assert "my_video_1080p.mp4" in result
        assert str(temp_dir) in result

    def test_youtube_url(self, temp_dir):
        from vhs_upscaler.gui import generate_output_path, AppState

        AppState.output_dir = temp_dir

        result = generate_output_path("https://youtube.com/watch?v=abc123", 1080)
        assert "youtube_" in result
        assert "_1080p.mp4" in result

    def test_youtu_be_short_url(self, temp_dir):
        from vhs_upscaler.gui import generate_output_path, AppState

        AppState.output_dir = temp_dir

        result = generate_output_path("https://youtu.be/abc123", 720)
        assert "youtube_" in result
        assert "_720p.mp4" in result

    def test_different_resolutions(self, temp_dir):
        from vhs_upscaler.gui import generate_output_path, AppState

        AppState.output_dir = temp_dir

        for res in [720, 1080, 1440, 2160]:
            result = generate_output_path("/video.mp4", res)
            assert f"_{res}p.mp4" in result


class TestAppState:
    """Tests for AppState class."""

    def test_add_log(self, mock_app_state):
        mock_app_state.add_log("Test message")
        assert len(mock_app_state.logs) == 1
        assert "Test message" in mock_app_state.logs[0]

    def test_log_timestamp(self, mock_app_state):
        mock_app_state.add_log("Test message")
        # Check timestamp format [HH:MM:SS]
        assert "[" in mock_app_state.logs[0]
        assert "]" in mock_app_state.logs[0]
        assert ":" in mock_app_state.logs[0]

    def test_log_max_limit(self, mock_app_state):
        mock_app_state.max_logs = 5
        for i in range(10):
            mock_app_state.add_log(f"Message {i}")

        assert len(mock_app_state.logs) == 5
        # Should keep the most recent logs
        assert "Message 9" in mock_app_state.logs[-1]

    def test_toggle_dark_mode(self, mock_app_state):
        initial_mode = mock_app_state.dark_mode
        result = mock_app_state.toggle_dark_mode()

        assert result != initial_mode
        assert mock_app_state.dark_mode == result


class TestGetVideoInfo:
    """Tests for get_video_info function."""

    def test_nonexistent_file(self):
        from vhs_upscaler.gui import get_video_info

        result = get_video_info("/nonexistent/file.mp4")
        assert result["duration"] == 0
        assert result["width"] == 0
        assert result["height"] == 0

    def test_empty_path(self):
        from vhs_upscaler.gui import get_video_info

        result = get_video_info("")
        assert result["duration"] == 0

    def test_none_path(self):
        from vhs_upscaler.gui import get_video_info

        result = get_video_info(None)
        assert result["duration"] == 0


class TestHandleFileUpload:
    """Tests for handle_file_upload function."""

    def test_none_input(self):
        from vhs_upscaler.gui import handle_file_upload

        path, preview = handle_file_upload(None)
        assert path == ""
        assert preview == ""

    def test_valid_file_path(self, sample_video_path, mock_app_state):
        from vhs_upscaler.gui import handle_file_upload

        path, preview = handle_file_upload(sample_video_path)
        assert path == sample_video_path
        assert "Video Info" in preview

    def test_nonexistent_file(self, mock_app_state):
        from vhs_upscaler.gui import handle_file_upload

        path, preview = handle_file_upload("/nonexistent/file.mp4")
        assert path == ""
        assert "No file uploaded" in preview


class TestEstimateProcessingTime:
    """Tests for estimate_processing_time function."""

    def test_zero_duration(self):
        from vhs_upscaler.gui import estimate_processing_time

        info = {"duration": 0, "height": 480}
        result = estimate_processing_time(info, 1080)
        assert result == "Unknown"

    def test_negative_duration(self):
        from vhs_upscaler.gui import estimate_processing_time

        info = {"duration": -10, "height": 480}
        result = estimate_processing_time(info, 1080)
        assert result == "Unknown"

    def test_valid_estimation(self):
        from vhs_upscaler.gui import estimate_processing_time

        info = {"duration": 60, "height": 480}  # 1 minute video
        result = estimate_processing_time(info, 1080)
        assert result != "Unknown"
        # Should return a time string
        assert ":" in result
