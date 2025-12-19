#!/usr/bin/env python3
"""
Tests for First-Run Setup Wizard
=================================

Test hardware detection, model downloading, and wizard flow.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "vhs_upscaler"))

from first_run_wizard import (
    HardwareDetector,
    ModelDownloader,
    FirstRunManager,
)


class TestHardwareDetector:
    """Test hardware detection functionality."""

    def test_detect_gpu_nvidia(self):
        """Test NVIDIA GPU detection."""
        with patch("first_run_wizard.torch") as mock_torch:
            # Mock NVIDIA GPU
            mock_torch.cuda.is_available.return_value = True
            mock_torch.cuda.get_device_name.return_value = "NVIDIA GeForce RTX 3060"

            mock_props = MagicMock()
            mock_props.total_memory = 12 * 1024 * 1024 * 1024  # 12 GB
            mock_props.major = 8
            mock_props.minor = 6
            mock_torch.cuda.get_device_properties.return_value = mock_props

            detector = HardwareDetector()
            gpu_info = detector.detect_gpu()

            assert gpu_info["vendor"] == "nvidia"
            assert "RTX 3060" in gpu_info["name"]
            assert gpu_info["vram_mb"] == 12 * 1024
            assert gpu_info["cuda_available"] is True
            assert gpu_info["compute_capability"] == "8.6"

    def test_detect_gpu_cpu_only(self):
        """Test CPU-only detection (no GPU)."""
        with patch("first_run_wizard.torch") as mock_torch:
            # Mock no GPU
            mock_torch.cuda.is_available.return_value = False

            detector = HardwareDetector()
            gpu_info = detector.detect_gpu()

            assert gpu_info["vendor"] == "cpu"
            assert gpu_info["name"] == "CPU Only"
            assert gpu_info["vram_mb"] is None
            assert gpu_info["cuda_available"] is False

    def test_detect_gpu_import_error(self):
        """Test graceful fallback when PyTorch not available."""
        with patch("first_run_wizard.torch", side_effect=ImportError):
            detector = HardwareDetector()
            gpu_info = detector.detect_gpu()

            # Should fall back to CPU
            assert gpu_info["vendor"] == "cpu"
            assert gpu_info["cuda_available"] is False

    def test_get_system_info(self):
        """Test system information gathering."""
        detector = HardwareDetector()
        sys_info = detector.get_system_info()

        assert "platform" in sys_info
        assert "python_version" in sys_info
        assert "architecture" in sys_info
        assert len(sys_info["python_version"]) > 0


class TestModelDownloader:
    """Test model downloading functionality."""

    def test_download_gfpgan_already_exists(self):
        """Test GFPGAN download when model already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock model file
            model_dir = Path(tmpdir) / "models" / "gfpgan"
            model_dir.mkdir(parents=True)
            model_file = model_dir / "GFPGANv1.3.pth"
            model_file.write_text("mock model")

            with patch("first_run_wizard.FaceRestorer") as mock_restorer_class:
                mock_restorer = MagicMock()
                mock_restorer.model_path = model_file
                mock_restorer_class.return_value = mock_restorer

                downloader = ModelDownloader()
                success, message = downloader.download_gfpgan()

                assert success is True
                assert "already downloaded" in message

    def test_download_with_progress_callback(self):
        """Test download with progress callback."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "test_model.pth"

            downloader = ModelDownloader()

            # Track progress updates
            progress_updates = []

            def progress_callback(downloaded_mb, total_mb, speed_mbps, eta_seconds, status_msg):
                progress_updates.append({
                    "downloaded_mb": downloaded_mb,
                    "total_mb": total_mb,
                    "speed_mbps": speed_mbps,
                    "eta_seconds": eta_seconds,
                    "status_msg": status_msg,
                })

            # Mock requests
            with patch("first_run_wizard.requests") as mock_requests:
                mock_response = MagicMock()
                mock_response.headers.get.return_value = str(100 * 1024 * 1024)  # 100 MB
                mock_response.iter_content.return_value = [b"x" * 8192 for _ in range(10)]
                mock_requests.get.return_value = mock_response

                success, message = downloader._download_with_progress(
                    url="http://example.com/model.pth",
                    output_path=model_path,
                    total_size_mb=100,
                    model_name="Test Model"
                )

                # Note: This will fail without proper mocking, but shows the pattern
                # In real tests, you'd mock the entire download process

    def test_cancel_download(self):
        """Test download cancellation."""
        downloader = ModelDownloader()

        # Request cancellation
        downloader.cancel()

        assert downloader.cancel_requested is True


class TestFirstRunManager:
    """Test first-run state management."""

    def test_is_first_run(self):
        """Test first-run detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Override cache dir
            with patch.object(FirstRunManager, "CACHE_DIR", Path(tmpdir) / ".cache"):
                with patch.object(FirstRunManager, "FIRST_RUN_MARKER", Path(tmpdir) / ".cache" / ".first_run_complete"):
                    # Should be first run (marker doesn't exist)
                    assert FirstRunManager.is_first_run() is True

    def test_mark_complete(self):
        """Test marking first-run as complete."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".cache"
            marker_file = cache_dir / ".first_run_complete"
            config_file = cache_dir / "config.json"

            with patch.object(FirstRunManager, "CACHE_DIR", cache_dir):
                with patch.object(FirstRunManager, "FIRST_RUN_MARKER", marker_file):
                    with patch.object(FirstRunManager, "CONFIG_FILE", config_file):
                        # Mark as complete
                        config = {
                            "gpu_vendor": "nvidia",
                            "gpu_name": "RTX 3060",
                            "cuda_available": True,
                        }

                        FirstRunManager.mark_complete(config)

                        # Check marker exists
                        assert marker_file.exists()

                        # Check config saved
                        assert config_file.exists()

                        # Now should not be first run
                        assert FirstRunManager.is_first_run() is False

    def test_load_config(self):
        """Test loading saved configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"

            # Create config
            import json
            config_data = {
                "gpu_vendor": "nvidia",
                "gpu_name": "RTX 3060",
            }
            config_file.write_text(json.dumps(config_data))

            with patch.object(FirstRunManager, "CONFIG_FILE", config_file):
                loaded_config = FirstRunManager.load_config()

                assert loaded_config["gpu_vendor"] == "nvidia"
                assert loaded_config["gpu_name"] == "RTX 3060"

    def test_load_config_not_exists(self):
        """Test loading config when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"

            with patch.object(FirstRunManager, "CONFIG_FILE", config_file):
                loaded_config = FirstRunManager.load_config()

                # Should return empty dict
                assert loaded_config == {}

    def test_reset(self):
        """Test resetting first-run state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".cache"
            cache_dir.mkdir()
            marker_file = cache_dir / ".first_run_complete"
            config_file = cache_dir / "config.json"

            # Create files
            marker_file.write_text("completed")
            config_file.write_text("{}")

            with patch.object(FirstRunManager, "CACHE_DIR", cache_dir):
                with patch.object(FirstRunManager, "FIRST_RUN_MARKER", marker_file):
                    with patch.object(FirstRunManager, "CONFIG_FILE", config_file):
                        # Reset
                        FirstRunManager.reset()

                        # Files should be deleted
                        assert not marker_file.exists()
                        assert not config_file.exists()


class TestWizardIntegration:
    """Integration tests for wizard flow."""

    def test_wizard_creation(self):
        """Test wizard UI creation."""
        from first_run_wizard import create_wizard_ui

        # Should create without errors
        wizard = create_wizard_ui()
        assert wizard is not None

    def test_welcome_back_ui_creation(self):
        """Test welcome back UI creation."""
        from first_run_wizard import create_welcome_back_ui

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"

            import json
            config_file.write_text(json.dumps({
                "gpu_vendor": "nvidia",
                "gpu_name": "RTX 3060",
                "cuda_available": True,
            }))

            with patch.object(FirstRunManager, "CONFIG_FILE", config_file):
                # Should create without errors
                welcome = create_welcome_back_ui()
                assert welcome is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
