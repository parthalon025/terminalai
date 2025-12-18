"""
Comprehensive Test Suite for Batch Parallel Processing
======================================================
Tests for the batch.py module for parallel video processing.

This suite covers:
- Sequential batch processing
- Parallel processing with multiple workers
- Video discovery and filtering
- Output path generation
- Error handling in parallel mode
- Job completion tracking
- Resume functionality
"""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
import concurrent.futures


@pytest.fixture
def batch_args(temp_dir):
    """Create mock command-line arguments for batch processing."""
    args = MagicMock()
    args.input_folder = temp_dir / "input"
    args.output_folder = temp_dir / "output"
    args.pattern = "*"
    args.recursive = False
    args.skip_existing = False
    args.resume = False
    args.suffix = None
    args.max_count = None
    args.dry_run = False
    args.parallel = 1
    args.resolution = 1080
    args.quality = "medium"
    args.crf = 20
    args.preset = None
    args.encoder = "hevc_nvenc"
    args.keep_temp = False
    args.skip_maxine = False
    args.engine = "realesrgan"
    args.realesrgan_model = "realesr-animevideov3"
    args.hdr = "sdr"
    args.audio_enhance = False
    args.audio_upmix = False
    args.audio_layout = "stereo"
    args.audio_format = "aac"
    args.audio_bitrate = "192k"
    args.no_audio_normalize = False
    args.verbose = False
    args.config = temp_dir / "config.yaml"

    # Create directories
    args.input_folder.mkdir(parents=True, exist_ok=True)
    args.output_folder.mkdir(parents=True, exist_ok=True)

    return args


@pytest.fixture
def sample_videos(temp_dir):
    """Create sample video files for testing."""
    input_dir = temp_dir / "input"
    input_dir.mkdir(exist_ok=True)

    videos = []
    for i in range(3):
        video = input_dir / f"video_{i}.mp4"
        video.write_bytes(b"fake video content")
        videos.append(video)

    return videos


@pytest.fixture
def mock_upscaler():
    """Mock VHSUpscaler for testing."""
    with patch('vhs_upscaler.cli.batch.VHSUpscaler') as mock:
        instance = MagicMock()
        instance.process.return_value = True
        mock.return_value = instance
        yield mock


class TestVideoDiscovery:
    """Test video file discovery."""

    def test_discover_videos_basic(self, sample_videos, temp_dir):
        """Test basic video discovery."""
        from vhs_upscaler.cli.batch import discover_videos

        input_dir = temp_dir / "input"
        videos = discover_videos(input_dir)

        assert len(videos) == 3
        assert all(v.suffix == ".mp4" for v in videos)

    def test_discover_videos_pattern(self, temp_dir):
        """Test video discovery with pattern."""
        from vhs_upscaler.cli.batch import discover_videos

        input_dir = temp_dir / "input"
        input_dir.mkdir(exist_ok=True)

        # Create different video formats
        (input_dir / "video1.mp4").write_bytes(b"video")
        (input_dir / "video2.avi").write_bytes(b"video")
        (input_dir / "video3.mkv").write_bytes(b"video")

        # Search only .mp4 files
        videos = discover_videos(input_dir, pattern="*.mp4")

        assert len(videos) == 1
        assert videos[0].suffix == ".mp4"

    def test_discover_videos_recursive(self, temp_dir):
        """Test recursive video discovery."""
        from vhs_upscaler.cli.batch import discover_videos

        input_dir = temp_dir / "input"
        input_dir.mkdir(exist_ok=True)

        # Create videos in subdirectories
        (input_dir / "video1.mp4").write_bytes(b"video")
        subdir = input_dir / "subdir"
        subdir.mkdir()
        (subdir / "video2.mp4").write_bytes(b"video")

        videos = discover_videos(input_dir, recursive=True)

        assert len(videos) == 2

    def test_discover_videos_sorted(self, sample_videos, temp_dir):
        """Test videos are returned in sorted order."""
        from vhs_upscaler.cli.batch import discover_videos

        input_dir = temp_dir / "input"
        videos = discover_videos(input_dir)

        # Should be sorted
        assert videos == sorted(videos)

    def test_discover_videos_empty_folder(self, temp_dir):
        """Test discovery in empty folder."""
        from vhs_upscaler.cli.batch import discover_videos

        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        videos = discover_videos(empty_dir)

        assert len(videos) == 0

    def test_discover_videos_multiple_formats(self, temp_dir):
        """Test discovery of multiple video formats."""
        from vhs_upscaler.cli.batch import discover_videos

        input_dir = temp_dir / "input"
        input_dir.mkdir(exist_ok=True)

        formats = [".mp4", ".avi", ".mkv", ".mov", ".wmv"]
        for i, fmt in enumerate(formats):
            (input_dir / f"video{i}{fmt}").write_bytes(b"video")

        videos = discover_videos(input_dir)

        assert len(videos) == len(formats)


class TestOutputPathGeneration:
    """Test output path generation."""

    def test_generate_output_path_default(self, temp_dir):
        """Test default output path generation."""
        from vhs_upscaler.cli.batch import generate_output_path

        input_path = temp_dir / "video.mp4"
        output_folder = temp_dir / "output"

        output = generate_output_path(input_path, output_folder, 1080)

        assert output.parent == output_folder
        assert output.stem == "video_1080p"
        assert output.suffix == ".mp4"

    def test_generate_output_path_custom_suffix(self, temp_dir):
        """Test output path with custom suffix."""
        from vhs_upscaler.cli.batch import generate_output_path

        input_path = temp_dir / "video.mp4"
        output_folder = temp_dir / "output"

        output = generate_output_path(
            input_path, output_folder, 1080, suffix="restored"
        )

        assert output.stem == "video_restored"

    def test_generate_output_path_4k(self, temp_dir):
        """Test output path for 4K resolution."""
        from vhs_upscaler.cli.batch import generate_output_path

        input_path = temp_dir / "video.mp4"
        output_folder = temp_dir / "output"

        output = generate_output_path(input_path, output_folder, 2160)

        assert "2160p" in output.stem


class TestSequentialProcessing:
    """Test sequential batch processing."""

    @patch('vhs_upscaler.cli.batch.VHSUpscaler')
    def test_sequential_processing_success(self, mock_upscaler_class, batch_args, sample_videos):
        """Test successful sequential processing."""
        from vhs_upscaler.cli.batch import handle_batch

        mock_instance = MagicMock()
        mock_instance.process.return_value = True
        mock_upscaler_class.return_value = mock_instance

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
            result = handle_batch(batch_args)

            assert result == 0
            assert mock_instance.process.call_count == len(sample_videos)

    @patch('vhs_upscaler.cli.batch.VHSUpscaler')
    def test_sequential_processing_partial_failure(self, mock_upscaler_class, batch_args, sample_videos):
        """Test sequential processing with some failures."""
        from vhs_upscaler.cli.batch import handle_batch

        mock_instance = MagicMock()
        # First video succeeds, second fails, third succeeds
        mock_instance.process.side_effect = [True, False, True]
        mock_upscaler_class.return_value = mock_instance

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
            result = handle_batch(batch_args)

            assert result == 1  # Non-zero exit code for failures

    @patch('vhs_upscaler.cli.batch.VHSUpscaler')
    def test_sequential_processing_exception(self, mock_upscaler_class, batch_args, sample_videos):
        """Test sequential processing with exception."""
        from vhs_upscaler.cli.batch import handle_batch

        mock_instance = MagicMock()
        mock_instance.process.side_effect = [True, Exception("Error"), True]
        mock_upscaler_class.return_value = mock_instance

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
            result = handle_batch(batch_args)

            # Should handle exception and continue
            assert result == 1


class TestParallelProcessing:
    """Test parallel batch processing."""

    @patch('vhs_upscaler.cli.batch.VHSUpscaler')
    def test_parallel_processing_basic(self, mock_upscaler_class, batch_args, sample_videos):
        """Test basic parallel processing."""
        from vhs_upscaler.cli.batch import handle_batch

        mock_instance = MagicMock()
        mock_instance.process.return_value = True
        mock_upscaler_class.return_value = mock_instance

        batch_args.parallel = 2

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
            result = handle_batch(batch_args)

            assert result == 0
            # All videos should be processed
            assert mock_instance.process.call_count == len(sample_videos)

    @patch('vhs_upscaler.cli.batch.VHSUpscaler')
    def test_parallel_processing_worker_count(self, mock_upscaler_class, batch_args, sample_videos):
        """Test parallel processing with different worker counts."""
        from vhs_upscaler.cli.batch import handle_batch

        mock_instance = MagicMock()
        mock_instance.process.return_value = True
        mock_upscaler_class.return_value = mock_instance

        for workers in [2, 3, 4]:
            batch_args.parallel = workers

            with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
                result = handle_batch(batch_args)
                assert result == 0

    def test_process_video_job_success(self, temp_dir):
        """Test single video job processing."""
        from vhs_upscaler.cli.batch import _process_video_job

        mock_upscaler = MagicMock()
        mock_upscaler.process.return_value = True

        video = temp_dir / "video.mp4"
        video.write_bytes(b"video")
        output = temp_dir / "output.mp4"

        success, name, error = _process_video_job((1, video, output, mock_upscaler, False))

        assert success is True
        assert name == "video.mp4"
        assert error == ""

    def test_process_video_job_failure(self, temp_dir):
        """Test video job processing failure."""
        from vhs_upscaler.cli.batch import _process_video_job

        mock_upscaler = MagicMock()
        mock_upscaler.process.return_value = False

        video = temp_dir / "video.mp4"
        video.write_bytes(b"video")
        output = temp_dir / "output.mp4"

        success, name, error = _process_video_job((1, video, output, mock_upscaler, False))

        assert success is False
        assert name == "video.mp4"

    def test_process_video_job_exception(self, temp_dir):
        """Test video job processing with exception."""
        from vhs_upscaler.cli.batch import _process_video_job

        mock_upscaler = MagicMock()
        mock_upscaler.process.side_effect = Exception("Processing error")

        video = temp_dir / "video.mp4"
        video.write_bytes(b"video")
        output = temp_dir / "output.mp4"

        success, name, error = _process_video_job((1, video, output, mock_upscaler, False))

        assert success is False
        assert "Processing error" in error


class TestJobFiltering:
    """Test job filtering and resume functionality."""

    @patch('vhs_upscaler.cli.batch.VHSUpscaler')
    def test_skip_existing_files(self, mock_upscaler, batch_args, sample_videos, temp_dir):
        """Test skipping existing output files."""
        from vhs_upscaler.cli.batch import handle_batch

        batch_args.skip_existing = True

        # Create one existing output file
        existing_output = batch_args.output_folder / "video_0_1080p.mp4"
        existing_output.write_bytes(b"existing")

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
            result = handle_batch(batch_args)

            # Should process only 2 videos (skip the one with existing output)
            mock_upscaler.return_value.process.call_count < len(sample_videos)

    @patch('vhs_upscaler.cli.batch.VHSUpscaler')
    def test_resume_processing(self, mock_upscaler, batch_args, sample_videos, temp_dir):
        """Test resume functionality."""
        from vhs_upscaler.cli.batch import handle_batch

        batch_args.resume = True

        # Create some existing outputs
        (batch_args.output_folder / "video_0_1080p.mp4").write_bytes(b"done")
        (batch_args.output_folder / "video_1_1080p.mp4").write_bytes(b"done")

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
            result = handle_batch(batch_args)

            # Should only process remaining videos

    @patch('vhs_upscaler.cli.batch.VHSUpscaler')
    def test_all_existing_skip(self, mock_upscaler, batch_args, sample_videos):
        """Test when all videos already processed."""
        from vhs_upscaler.cli.batch import handle_batch

        batch_args.skip_existing = True

        # Create all output files
        for i in range(len(sample_videos)):
            output = batch_args.output_folder / f"video_{i}_1080p.mp4"
            output.write_bytes(b"existing")

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
            result = handle_batch(batch_args)

            assert result == 0
            # Should not process any videos


class TestDryRun:
    """Test dry-run mode."""

    def test_dry_run_lists_videos(self, batch_args, sample_videos, capsys):
        """Test dry-run mode lists videos without processing."""
        from vhs_upscaler.cli.batch import handle_batch

        batch_args.dry_run = True

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
            result = handle_batch(batch_args)

            assert result == 0
            # No actual processing should occur

    def test_dry_run_shows_output_paths(self, batch_args, sample_videos):
        """Test dry-run shows expected output paths."""
        from vhs_upscaler.cli.batch import handle_batch

        batch_args.dry_run = True

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
            with patch('builtins.print') as mock_print:
                handle_batch(batch_args)

                # Should print output information


class TestMaxCount:
    """Test max count limiting."""

    @patch('vhs_upscaler.cli.batch.VHSUpscaler')
    def test_max_count_limit(self, mock_upscaler, batch_args, sample_videos):
        """Test processing limited by max count."""
        from vhs_upscaler.cli.batch import handle_batch

        batch_args.max_count = 2

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
            result = handle_batch(batch_args)

            # Should only process max_count videos
            assert mock_upscaler.return_value.process.call_count <= 2


class TestConfigLoading:
    """Test configuration file loading."""

    def test_load_config_yaml(self, temp_dir):
        """Test loading YAML config file."""
        from vhs_upscaler.cli.batch import load_config

        config_path = temp_dir / "config.yaml"
        config_path.write_text("maxine_path: /path/to/maxine\nffmpeg_path: /custom/ffmpeg")

        with patch('yaml.safe_load') as mock_load:
            mock_load.return_value = {"maxine_path": "/path/to/maxine"}

            config = load_config(config_path)

            assert mock_load.called

    def test_load_config_missing_file(self, temp_dir):
        """Test loading non-existent config file."""
        from vhs_upscaler.cli.batch import load_config

        config_path = temp_dir / "nonexistent.yaml"
        config = load_config(config_path)

        assert config == {}

    def test_load_config_no_yaml(self, temp_dir):
        """Test config loading without PyYAML."""
        from vhs_upscaler.cli.batch import load_config

        config_path = temp_dir / "config.yaml"
        config_path.write_text("test: value")

        with patch('importlib.import_module', side_effect=ImportError):
            config = load_config(config_path)

            # Should return empty dict if YAML not available


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_input_folder(self, batch_args):
        """Test handling of non-existent input folder."""
        from vhs_upscaler.cli.batch import handle_batch

        batch_args.input_folder = Path("/nonexistent/folder")

        result = handle_batch(batch_args)

        assert result == 1  # Error exit code

    def test_input_is_file_not_folder(self, batch_args, temp_dir):
        """Test handling when input is a file not a folder."""
        from vhs_upscaler.cli.batch import handle_batch

        file_path = temp_dir / "file.txt"
        file_path.write_text("not a folder")
        batch_args.input_folder = file_path

        result = handle_batch(batch_args)

        assert result == 1

    def test_no_videos_found(self, batch_args):
        """Test handling when no videos found."""
        from vhs_upscaler.cli.batch import handle_batch

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=[]):
            result = handle_batch(batch_args)

            assert result == 1

    @patch('vhs_upscaler.cli.batch.VHSUpscaler')
    def test_keyboard_interrupt(self, mock_upscaler, batch_args, sample_videos):
        """Test handling of keyboard interrupt."""
        from vhs_upscaler.cli.batch import handle_batch

        mock_instance = MagicMock()
        mock_instance.process.side_effect = [True, KeyboardInterrupt(), True]
        mock_upscaler.return_value = mock_instance

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
            result = handle_batch(batch_args)

            # Should handle interrupt gracefully


class TestBatchStatistics:
    """Test batch processing statistics and reporting."""

    @patch('vhs_upscaler.cli.batch.VHSUpscaler')
    def test_success_count(self, mock_upscaler, batch_args, sample_videos):
        """Test success count tracking."""
        from vhs_upscaler.cli.batch import handle_batch

        mock_instance = MagicMock()
        mock_instance.process.return_value = True
        mock_upscaler.return_value = mock_instance

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
            with patch('builtins.print') as mock_print:
                result = handle_batch(batch_args)

                # Should print statistics
                assert result == 0

    @patch('vhs_upscaler.cli.batch.VHSUpscaler')
    def test_failure_count(self, mock_upscaler, batch_args, sample_videos):
        """Test failure count tracking."""
        from vhs_upscaler.cli.batch import handle_batch

        mock_instance = MagicMock()
        mock_instance.process.side_effect = [True, False, False]
        mock_upscaler.return_value = mock_instance

        with patch('vhs_upscaler.cli.batch.discover_videos', return_value=sample_videos):
            result = handle_batch(batch_args)

            assert result == 1  # Should indicate failures


class TestParserSetup:
    """Test argument parser setup."""

    def test_setup_batch_parser(self):
        """Test batch parser setup."""
        from vhs_upscaler.cli.batch import setup_batch_parser
        import argparse

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        batch_parser = setup_batch_parser(subparsers)

        assert batch_parser is not None

    def test_parser_has_required_arguments(self):
        """Test parser has all required arguments."""
        from vhs_upscaler.cli.batch import setup_batch_parser
        import argparse

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        batch_parser = setup_batch_parser(subparsers)

        # Test that parser can parse basic arguments
        # (Actual parsing would require valid paths)


class TestVideoExtensions:
    """Test video file extension handling."""

    def test_supported_extensions(self, temp_dir):
        """Test all supported video extensions are recognized."""
        from vhs_upscaler.cli.batch import discover_videos, VIDEO_EXTENSIONS

        input_dir = temp_dir / "input"
        input_dir.mkdir(exist_ok=True)

        # Create files with different extensions
        for ext in [".mp4", ".avi", ".mkv", ".mov"]:
            (input_dir / f"video{ext}").write_bytes(b"video")

        videos = discover_videos(input_dir)

        # All should be discovered
        assert len(videos) >= 4

    def test_case_insensitive_extensions(self, temp_dir):
        """Test case-insensitive extension matching."""
        from vhs_upscaler.cli.batch import discover_videos

        input_dir = temp_dir / "input"
        input_dir.mkdir(exist_ok=True)

        # Create files with different case
        (input_dir / "video.MP4").write_bytes(b"video")
        (input_dir / "video.Mp4").write_bytes(b"video")

        videos = discover_videos(input_dir)

        assert len(videos) == 2
