"""
Unit tests for watch folder automation system.

Tests the watch_folder.py script functionality including:
- File detection and filtering
- Configuration loading
- Queue integration
- File handling (move/delete on completion)
- Retry logic
- Multiple folder support
"""

import os
import sys
import tempfile
import time
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.watch_folder import (
    WatchFolderConfig,
    VideoFileHandler,
    WatchFolderManager,
    load_config,
    create_example_config
)
from vhs_upscaler.queue_manager import VideoQueue, QueueJob, JobStatus


class TestWatchFolderConfig:
    """Test WatchFolderConfig dataclass."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = WatchFolderConfig(
            input_dir="/tmp/input",
            output_dir="/tmp/output"
        )
        
        assert config.preset == "vhs"
        assert config.resolution == 1080
        assert config.move_on_complete is True
        assert config.delete_on_complete is False
        assert config.retry_on_error is True
        assert config.max_retries == 3

    def test_config_path_expansion(self, tmp_path):
        """Test path expansion and normalization."""
        config = WatchFolderConfig(
            input_dir=str(tmp_path / "input"),
            output_dir=str(tmp_path / "output")
        )
        
        # Paths should be absolute
        assert os.path.isabs(config.input_dir)
        assert os.path.isabs(config.output_dir)

    def test_config_directory_creation(self, tmp_path):
        """Test that directories are created on initialization."""
        input_dir = tmp_path / "new_input"
        output_dir = tmp_path / "new_output"
        
        config = WatchFolderConfig(
            input_dir=str(input_dir),
            output_dir=str(output_dir)
        )
        
        assert input_dir.exists()
        assert output_dir.exists()

    def test_config_custom_settings(self):
        """Test custom configuration settings."""
        config = WatchFolderConfig(
            input_dir="/tmp/input",
            output_dir="/tmp/output",
            preset="dvd",
            resolution=2160,
            encoder="hevc_nvenc",
            crf=18,
            face_restore=True,
            audio_enhance="voice"
        )
        
        assert config.preset == "dvd"
        assert config.resolution == 2160
        assert config.encoder == "hevc_nvenc"
        assert config.crf == 18
        assert config.face_restore is True
        assert config.audio_enhance == "voice"


class TestVideoFileHandler:
    """Test VideoFileHandler class."""

    @pytest.fixture
    def config(self, tmp_path):
        """Create test configuration."""
        return WatchFolderConfig(
            input_dir=str(tmp_path / "input"),
            output_dir=str(tmp_path / "output"),
            preset="vhs"
        )

    @pytest.fixture
    def queue(self):
        """Create mock queue."""
        return Mock(spec=VideoQueue)

    @pytest.fixture
    def handler(self, config, queue):
        """Create VideoFileHandler instance."""
        return VideoFileHandler(config, queue)

    def test_is_video_file(self, handler):
        """Test video file detection."""
        assert handler._is_video_file("/path/to/video.mp4") is True
        assert handler._is_video_file("/path/to/video.avi") is True
        assert handler._is_video_file("/path/to/video.mkv") is True
        assert handler._is_video_file("/path/to/video.mov") is True
        
        assert handler._is_video_file("/path/to/image.jpg") is False
        assert handler._is_video_file("/path/to/audio.mp3") is False
        assert handler._is_video_file("/path/to/document.txt") is False

    def test_is_video_file_case_insensitive(self, handler):
        """Test video file detection is case insensitive."""
        assert handler._is_video_file("/path/to/VIDEO.MP4") is True
        assert handler._is_video_file("/path/to/Video.AVI") is True
        assert handler._is_video_file("/path/to/movie.MKV") is True

    def test_process_video_adds_to_queue(self, handler, config, queue, tmp_path):
        """Test that processing a video adds it to the queue."""
        # Create test video file
        video_file = tmp_path / "input" / "test_video.mp4"
        video_file.write_text("fake video content")
        
        # Mock queue.add_job to return a job
        mock_job = Mock(spec=QueueJob)
        mock_job.id = "test-job-123"
        queue.add_job.return_value = mock_job
        
        # Process video
        handler._process_video(str(video_file))
        
        # Verify queue.add_job was called
        assert queue.add_job.called
        call_args = queue.add_job.call_args[1]
        assert call_args["input_file"] == str(video_file)
        assert call_args["preset"] == "vhs"
        assert call_args["resolution"] == 1080

    def test_process_video_with_advanced_options(self, config, queue, tmp_path):
        """Test processing with advanced configuration options."""
        config.encoder = "hevc_nvenc"
        config.crf = 18
        config.face_restore = True
        config.audio_enhance = "voice"
        
        handler = VideoFileHandler(config, queue)
        
        video_file = tmp_path / "input" / "test.mp4"
        video_file.write_text("fake video")
        
        mock_job = Mock(spec=QueueJob)
        mock_job.id = "test-job"
        queue.add_job.return_value = mock_job
        
        handler._process_video(str(video_file))
        
        call_args = queue.add_job.call_args[1]
        assert call_args["encoder"] == "hevc_nvenc"
        assert call_args["crf"] == 18
        assert call_args["face_restore"] is True
        assert call_args["audio_enhance"] == "voice"

    def test_on_job_complete_success(self, handler, config, tmp_path):
        """Test successful job completion handling."""
        video_file = tmp_path / "input" / "test.mp4"
        video_file.write_text("fake video")
        
        mock_job = Mock(spec=QueueJob)
        mock_job.status = Mock()
        mock_job.status.name = "COMPLETED"
        
        handler.processing_files.add(str(video_file))
        handler.on_job_complete(mock_job, str(video_file))
        
        # File should be removed from processing set
        assert str(video_file) not in handler.processing_files
        
        # File should be added to completed set
        assert str(video_file) in handler.completed_files
        
        # Original should be moved to _completed directory
        completed_dir = tmp_path / "input" / "_completed"
        assert completed_dir.exists()

    def test_on_job_complete_failure_with_retry(self, handler, config, tmp_path):
        """Test failed job with retry enabled."""
        config.retry_on_error = True
        config.max_retries = 3
        
        video_file = tmp_path / "input" / "test.mp4"
        video_file.write_text("fake video")
        
        mock_job = Mock(spec=QueueJob)
        mock_job.status = Mock()
        mock_job.status.name = "FAILED"
        
        handler.processing_files.add(str(video_file))
        
        with patch.object(handler, '_process_video') as mock_process:
            handler.on_job_complete(mock_job, str(video_file))
            
            # Should retry
            assert handler.failed_files[str(video_file)] == 1
            mock_process.assert_called_once_with(str(video_file))

    def test_on_job_complete_failure_max_retries(self, handler, config, tmp_path):
        """Test failed job after max retries."""
        config.retry_on_error = True
        config.max_retries = 2
        
        video_file = tmp_path / "input" / "test.mp4"
        video_file.write_text("fake video")
        
        mock_job = Mock(spec=QueueJob)
        mock_job.status = Mock()
        mock_job.status.name = "FAILED"
        
        handler.processing_files.add(str(video_file))
        handler.failed_files[str(video_file)] = 2  # Already at max retries
        
        handler.on_job_complete(mock_job, str(video_file))
        
        # File should be moved to _failed directory
        failed_dir = tmp_path / "input" / "_failed"
        assert failed_dir.exists()

    def test_delete_on_complete(self, config, queue, tmp_path):
        """Test delete_on_complete option."""
        config.delete_on_complete = True
        config.move_on_complete = False
        
        handler = VideoFileHandler(config, queue)
        
        video_file = tmp_path / "input" / "test.mp4"
        video_file.write_text("fake video")
        
        mock_job = Mock(spec=QueueJob)
        mock_job.status = Mock()
        mock_job.status.name = "COMPLETED"
        
        handler.processing_files.add(str(video_file))
        handler.on_job_complete(mock_job, str(video_file))
        
        # File should be deleted
        assert not video_file.exists()


class TestWatchFolderManager:
    """Test WatchFolderManager class."""

    @pytest.fixture
    def configs(self, tmp_path):
        """Create test configurations."""
        return [
            WatchFolderConfig(
                input_dir=str(tmp_path / "input1"),
                output_dir=str(tmp_path / "output1"),
                preset="vhs"
            ),
            WatchFolderConfig(
                input_dir=str(tmp_path / "input2"),
                output_dir=str(tmp_path / "output2"),
                preset="dvd"
            )
        ]

    def test_manager_initialization(self, configs):
        """Test manager initializes with multiple configs."""
        manager = WatchFolderManager(configs)
        
        assert len(manager.configs) == 2
        assert isinstance(manager.queue, VideoQueue)
        assert len(manager.observers) == 0  # Not started yet
        assert len(manager.handlers) == 0

    @patch('scripts.watch_folder.Observer')
    def test_manager_start(self, mock_observer_class, configs):
        """Test manager starts observers for all configs."""
        mock_observer = Mock()
        mock_observer_class.return_value = mock_observer
        
        manager = WatchFolderManager(configs)
        
        # Mock the infinite loop
        with patch('time.sleep', side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                manager.start()
        
        # Should create observer for each config
        assert mock_observer_class.call_count == 2
        assert mock_observer.schedule.call_count == 2
        assert mock_observer.start.call_count == 2

    def test_process_existing_files(self, configs, tmp_path):
        """Test processing existing files in watch folders."""
        # Create existing video files
        input1 = tmp_path / "input1"
        (input1 / "existing1.mp4").write_text("fake video 1")
        (input1 / "existing2.avi").write_text("fake video 2")
        (input1 / "not_video.txt").write_text("text file")
        
        manager = WatchFolderManager(configs)
        
        # Mock handler._process_video
        with patch.object(VideoFileHandler, '_process_video') as mock_process:
            manager.process_existing_files()
            
            # Should process only video files
            assert mock_process.call_count == 2


class TestConfigLoading:
    """Test configuration file loading."""

    def test_load_config_from_yaml(self, tmp_path):
        """Test loading configuration from YAML file."""
        config_file = tmp_path / "test_config.yaml"
        
        config_data = {
            'watch_folders': [
                {
                    'input_dir': str(tmp_path / "input1"),
                    'output_dir': str(tmp_path / "output1"),
                    'preset': 'vhs',
                    'resolution': 1080,
                },
                {
                    'input_dir': str(tmp_path / "input2"),
                    'output_dir': str(tmp_path / "output2"),
                    'preset': 'dvd',
                    'resolution': 2160,
                    'face_restore': True,
                }
            ]
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        configs = load_config(str(config_file))
        
        assert len(configs) == 2
        assert configs[0].preset == "vhs"
        assert configs[0].resolution == 1080
        assert configs[1].preset == "dvd"
        assert configs[1].resolution == 2160
        assert configs[1].face_restore is True

    def test_create_example_config(self, tmp_path):
        """Test creating example configuration file."""
        config_file = tmp_path / "example_config.yaml"
        
        create_example_config(str(config_file))
        
        assert config_file.exists()
        
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'watch_folders' in data
        assert len(data['watch_folders']) >= 1
        assert 'input_dir' in data['watch_folders'][0]
        assert 'output_dir' in data['watch_folders'][0]
        assert 'preset' in data['watch_folders'][0]


class TestFileReadyDetection:
    """Test file ready detection logic."""

    @pytest.fixture
    def handler(self, tmp_path):
        """Create handler with temp directories."""
        config = WatchFolderConfig(
            input_dir=str(tmp_path / "input"),
            output_dir=str(tmp_path / "output")
        )
        queue = Mock(spec=VideoQueue)
        return VideoFileHandler(config, queue)

    def test_wait_for_file_ready_stable_size(self, handler, tmp_path):
        """Test file ready detection with stable file size."""
        test_file = tmp_path / "input" / "test.mp4"
        test_file.write_text("complete file content")
        
        # File size is stable, should return True quickly
        result = handler._wait_for_file_ready(str(test_file), timeout=5)
        assert result is True

    def test_wait_for_file_ready_missing_file(self, handler, tmp_path):
        """Test file ready detection with missing file."""
        test_file = tmp_path / "input" / "nonexistent.mp4"
        
        # File doesn't exist, should return False
        result = handler._wait_for_file_ready(str(test_file), timeout=3)
        assert result is False

    @patch('time.sleep')
    @patch('os.path.getsize')
    def test_wait_for_file_ready_growing_file(self, mock_getsize, mock_sleep, handler, tmp_path):
        """Test file ready detection with growing file."""
        test_file = tmp_path / "input" / "test.mp4"
        test_file.write_text("initial content")
        
        # Simulate growing file sizes
        mock_getsize.side_effect = [100, 200, 300, 400, 400, 400, 400]
        
        result = handler._wait_for_file_ready(str(test_file), timeout=10)
        
        # Should wait for stable size
        assert result is True
        assert mock_sleep.call_count >= 3


class TestOutputFilenameGeneration:
    """Test output filename generation."""

    def test_output_filename_preserves_extension(self, tmp_path):
        """Test that output filename preserves input extension."""
        config = WatchFolderConfig(
            input_dir=str(tmp_path / "input"),
            output_dir=str(tmp_path / "output")
        )
        queue = Mock(spec=VideoQueue)
        handler = VideoFileHandler(config, queue)
        
        video_file = tmp_path / "input" / "my_video.mp4"
        video_file.write_text("fake")
        
        mock_job = Mock(spec=QueueJob)
        mock_job.id = "test"
        queue.add_job.return_value = mock_job
        
        handler._process_video(str(video_file))
        
        call_args = queue.add_job.call_args[1]
        output_file = call_args["output_file"]
        
        assert output_file.endswith("_processed.mp4")
        assert str(tmp_path / "output") in output_file

    def test_output_filename_different_extensions(self, tmp_path):
        """Test output filename generation for different video formats."""
        config = WatchFolderConfig(
            input_dir=str(tmp_path / "input"),
            output_dir=str(tmp_path / "output")
        )
        queue = Mock(spec=VideoQueue)
        handler = VideoFileHandler(config, queue)
        
        mock_job = Mock(spec=QueueJob)
        mock_job.id = "test"
        queue.add_job.return_value = mock_job
        
        for ext in ['.mp4', '.avi', '.mkv', '.mov']:
            video_file = tmp_path / "input" / f"video{ext}"
            video_file.write_text("fake")
            
            handler._process_video(str(video_file))
            
            call_args = queue.add_job.call_args[1]
            output_file = call_args["output_file"]
            
            assert output_file.endswith(f"_processed{ext}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
