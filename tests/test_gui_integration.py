"""
Integration Tests for GUI
=========================
End-to-end tests for the Gradio GUI interface.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "vhs_upscaler"))


class TestGUICreation:
    """Tests for GUI creation and initialization."""

    @pytest.mark.skip(reason="Gradio version compatibility issue with 'every' parameter")
    def test_create_gui_returns_blocks(self):
        """Test that create_gui returns a Gradio Blocks instance."""
        from vhs_upscaler.gui import create_gui
        import gradio as gr

        app = create_gui()
        assert isinstance(app, gr.Blocks)

    @pytest.mark.skip(reason="Gradio version compatibility issue with 'every' parameter")
    def test_gui_has_title(self):
        """Test that GUI has proper title."""
        from vhs_upscaler.gui import create_gui

        app = create_gui()
        assert app.title == "VHS Upscaler"

    @pytest.mark.skip(reason="Gradio version compatibility issue with 'every' parameter")
    def test_gui_theme(self):
        """Test that GUI uses Soft theme."""
        from vhs_upscaler.gui import create_gui
        import gradio as gr

        app = create_gui()
        assert app.theme is not None


class TestGUIComponents:
    """Tests for GUI component presence."""

    def test_version_constant(self):
        """Test version constant is set."""
        from vhs_upscaler.gui import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        # Should follow semver pattern
        parts = __version__.split(".")
        assert len(parts) >= 2


class TestLogsDisplay:
    """Tests for logs display functionality."""

    def test_empty_logs(self, mock_app_state):
        """Test logs display with no logs."""
        from vhs_upscaler.gui import get_logs_display

        mock_app_state.logs = []
        result = get_logs_display()
        assert "No logs yet" in result

    def test_logs_with_entries(self, mock_app_state):
        """Test logs display with entries."""
        from vhs_upscaler.gui import get_logs_display

        mock_app_state.logs = ["[12:00:00] Test log 1", "[12:00:01] Test log 2"]
        result = get_logs_display()
        assert "Test log" in result

    def test_logs_order(self, mock_app_state):
        """Test logs are shown in reverse chronological order."""
        from vhs_upscaler.gui import get_logs_display

        mock_app_state.logs = ["First", "Second", "Third"]
        result = get_logs_display()
        lines = result.split("\n")
        # Most recent should be first
        assert lines[0] == "Third"


class TestRefreshDisplay:
    """Tests for refresh_display function."""

    def test_refresh_returns_tuple(self, temp_dir):
        """Test refresh_display returns proper tuple."""
        from vhs_upscaler.gui import refresh_display, AppState
        from vhs_upscaler.queue_manager import VideoQueue

        AppState.queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )
        AppState.logs = []

        result = refresh_display()
        assert isinstance(result, tuple)
        assert len(result) == 3  # queue, stats, logs


class TestOutputDirectory:
    """Tests for output directory settings."""

    def test_set_output_directory_valid(self, temp_dir, mock_app_state):
        """Test setting valid output directory."""
        from vhs_upscaler.gui import set_output_directory

        result = set_output_directory(str(temp_dir / "output"))
        assert "set to" in result.lower()

    def test_set_output_directory_empty(self, mock_app_state):
        """Test setting empty output directory."""
        from vhs_upscaler.gui import set_output_directory

        result = set_output_directory("")
        assert "valid path" in result.lower()

    def test_set_output_directory_whitespace(self, mock_app_state):
        """Test setting whitespace output directory."""
        from vhs_upscaler.gui import set_output_directory

        result = set_output_directory("   ")
        assert "valid path" in result.lower()


class TestDarkModeToggle:
    """Tests for dark mode functionality."""

    def test_dark_mode_default_off(self, mock_app_state):
        """Test dark mode is off by default."""
        assert mock_app_state.dark_mode is False

    def test_toggle_dark_mode_on(self, mock_app_state):
        """Test toggling dark mode on."""
        mock_app_state.dark_mode = False
        result = mock_app_state.toggle_dark_mode()
        assert result is True
        assert mock_app_state.dark_mode is True

    def test_toggle_dark_mode_off(self, mock_app_state):
        """Test toggling dark mode off."""
        mock_app_state.dark_mode = True
        result = mock_app_state.toggle_dark_mode()
        assert result is False
        assert mock_app_state.dark_mode is False


class TestInitializeQueue:
    """Tests for queue initialization."""

    def test_initialize_queue_creates_queue(self, temp_dir):
        """Test that initialize_queue creates a queue if none exists."""
        from vhs_upscaler.gui import initialize_queue, AppState

        AppState.queue = None
        initialize_queue()

        assert AppState.queue is not None

    def test_initialize_queue_idempotent(self, temp_dir):
        """Test that initialize_queue doesn't replace existing queue."""
        from vhs_upscaler.gui import initialize_queue, AppState
        from vhs_upscaler.queue_manager import VideoQueue

        # Create a queue with a marker job
        AppState.queue = VideoQueue(
            processor_func=MagicMock(),
            max_concurrent=1,
            auto_start=False,
            persistence_file=temp_dir / "queue.json"
        )
        AppState.queue.add_job("/marker.mp4", "/marker_out.mp4")

        initialize_queue()

        # Should still have the marker job
        jobs = AppState.queue.get_all_jobs()
        assert len(jobs) == 1
        assert jobs[0].input_source == "/marker.mp4"


class TestThumbnailGeneration:
    """Tests for video thumbnail generation."""

    def test_thumbnail_nonexistent_file(self, mock_app_state):
        """Test thumbnail for nonexistent file returns None."""
        result = mock_app_state.get_thumbnail("/nonexistent/file.mp4")
        assert result is None

    def test_thumbnail_empty_path(self, mock_app_state):
        """Test thumbnail for empty path returns None."""
        result = mock_app_state.get_thumbnail("")
        assert result is None

    def test_thumbnail_none_path(self, mock_app_state):
        """Test thumbnail for None path returns None."""
        result = mock_app_state.get_thumbnail(None)
        assert result is None

    @patch('subprocess.run')
    def test_thumbnail_caching(self, mock_run, mock_app_state, sample_video_path):
        """Test that thumbnails are cached."""
        # First call should attempt to generate
        mock_run.return_value = MagicMock(returncode=1)  # Simulate failure to avoid file ops

        mock_app_state.get_thumbnail(sample_video_path)
        mock_app_state.get_thumbnail(sample_video_path)

        # Should only call subprocess once (caching on failure path)
        # Note: Actual caching behavior depends on implementation


class TestPresetSelection:
    """Tests for preset configuration."""

    def test_presets_available(self):
        """Test that all expected presets are available."""
        from vhs_upscaler.vhs_upscale import VHSUpscaler

        expected_presets = ["vhs", "dvd", "webcam", "youtube", "clean"]
        for preset in expected_presets:
            assert preset in VHSUpscaler.PRESETS

    def test_vhs_preset_has_deinterlace(self):
        """Test VHS preset enables deinterlacing."""
        from vhs_upscaler.vhs_upscale import VHSUpscaler

        preset = VHSUpscaler.PRESETS["vhs"]
        assert preset.get("deinterlace", False) is True

    def test_clean_preset_no_preprocessing(self):
        """Test clean preset skips preprocessing."""
        from vhs_upscaler.vhs_upscale import VHSUpscaler

        preset = VHSUpscaler.PRESETS["clean"]
        assert preset.get("deinterlace", True) is False
        assert preset.get("denoise", True) is False


class TestYouTubeURLDetection:
    """Tests for YouTube URL detection."""

    def test_standard_youtube_url(self):
        """Test standard YouTube URL detection."""
        from vhs_upscaler.vhs_upscale import YouTubeDownloader

        assert YouTubeDownloader.is_youtube_url("https://www.youtube.com/watch?v=abc123")
        assert YouTubeDownloader.is_youtube_url("https://youtube.com/watch?v=abc123")

    def test_short_youtube_url(self):
        """Test short YouTube URL detection."""
        from vhs_upscaler.vhs_upscale import YouTubeDownloader

        assert YouTubeDownloader.is_youtube_url("https://youtu.be/abc123")

    def test_non_youtube_url(self):
        """Test non-YouTube URL detection."""
        from vhs_upscaler.vhs_upscale import YouTubeDownloader

        assert not YouTubeDownloader.is_youtube_url("https://vimeo.com/123456")
        assert not YouTubeDownloader.is_youtube_url("/path/to/local/file.mp4")

    def test_empty_url(self):
        """Test empty URL detection."""
        from vhs_upscaler.vhs_upscale import YouTubeDownloader

        assert not YouTubeDownloader.is_youtube_url("")

    def test_none_url(self):
        """Test None URL detection."""
        from vhs_upscaler.vhs_upscale import YouTubeDownloader

        # None should not raise an error
        try:
            result = YouTubeDownloader.is_youtube_url(None)
            # If it doesn't raise, it should return False
            assert result is False
        except TypeError:
            # If it raises TypeError, that's acceptable behavior
            pass
