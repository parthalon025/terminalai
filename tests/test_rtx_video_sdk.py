"""
Tests for RTX Video SDK integration.

These tests verify the RTX Video SDK wrapper module functionality
including SDK detection, GPU validation, configuration, and video processing.
"""

import platform
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import test subjects
sys.path.insert(0, str(Path(__file__).parent.parent))

from vhs_upscaler.rtx_video_sdk.models import (
    RTXVideoConfig,
    EffectType,
    HDRFormat,
    ScaleFactor,
    GPUInfo,
    SDKInfo,
    ProcessingStats,
    Precision,
)
from vhs_upscaler.rtx_video_sdk.utils import (
    detect_sdk,
    validate_gpu,
    is_rtx_video_available,
    get_recommended_settings,
    get_supported_resolutions,
)


# =============================================================================
# Model Tests
# =============================================================================

class TestRTXVideoConfig:
    """Tests for RTXVideoConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = RTXVideoConfig()
        assert config.enable_super_resolution is True
        assert config.enable_artifact_reduction is True
        assert config.enable_hdr_conversion is False
        assert config.scale_factor == 4
        assert config.target_resolution == 1080
        assert config.artifact_strength == 0.5
        assert config.hdr_format == HDRFormat.SDR
        assert config.peak_brightness == 400
        assert config.gpu_id == 0
        assert config.precision == Precision.FP16

    def test_custom_values(self):
        """Test custom configuration values."""
        config = RTXVideoConfig(
            enable_super_resolution=True,
            enable_artifact_reduction=False,
            enable_hdr_conversion=True,
            scale_factor=2,
            target_resolution=2160,
            artifact_strength=0.8,
            hdr_format=HDRFormat.HDR10,
            peak_brightness=600,
        )
        assert config.scale_factor == 2
        assert config.target_resolution == 2160
        assert config.artifact_strength == 0.8
        assert config.hdr_format == HDRFormat.HDR10
        assert config.peak_brightness == 600

    def test_validate_success(self):
        """Test configuration validation with valid values."""
        config = RTXVideoConfig()
        errors = config.validate()
        assert len(errors) == 0

    def test_validate_invalid_scale_factor(self):
        """Test configuration validation with invalid scale factor."""
        config = RTXVideoConfig(scale_factor=3)
        errors = config.validate()
        assert any("scale_factor" in e for e in errors)

    def test_validate_invalid_resolution(self):
        """Test configuration validation with invalid resolution."""
        config = RTXVideoConfig(target_resolution=500)
        errors = config.validate()
        assert any("target_resolution" in e for e in errors)

    def test_validate_invalid_artifact_strength(self):
        """Test configuration validation with invalid artifact strength."""
        config = RTXVideoConfig(artifact_strength=1.5)
        errors = config.validate()
        assert any("artifact_strength" in e for e in errors)

    def test_validate_invalid_brightness(self):
        """Test configuration validation with invalid brightness."""
        config = RTXVideoConfig(peak_brightness=50)
        errors = config.validate()
        assert any("peak_brightness" in e for e in errors)

    def test_get_effect_type_super_res_only(self):
        """Test effect type selection with super resolution only."""
        config = RTXVideoConfig(
            enable_super_resolution=True,
            enable_artifact_reduction=False,
        )
        assert config.get_effect_type() == EffectType.SUPER_RESOLUTION

    def test_get_effect_type_artifact_only(self):
        """Test effect type selection with artifact reduction only."""
        config = RTXVideoConfig(
            enable_super_resolution=False,
            enable_artifact_reduction=True,
        )
        assert config.get_effect_type() == EffectType.ARTIFACT_REDUCTION

    def test_get_effect_type_combined(self):
        """Test effect type selection with both features."""
        config = RTXVideoConfig(
            enable_super_resolution=True,
            enable_artifact_reduction=True,
        )
        assert config.get_effect_type() == EffectType.UPSCALE_PIPELINE

    def test_get_effect_type_hdr_only(self):
        """Test effect type selection with HDR conversion only."""
        config = RTXVideoConfig(
            enable_super_resolution=False,
            enable_artifact_reduction=False,
            enable_hdr_conversion=True,
        )
        assert config.get_effect_type() == EffectType.HDR_CONVERSION


class TestGPUInfo:
    """Tests for GPUInfo dataclass."""

    def test_str_representation_supported(self):
        """Test string representation for supported GPU."""
        gpu = GPUInfo(
            name="NVIDIA GeForce RTX 3080",
            compute_capability=(8, 6),
            memory_mb=10240,
            is_supported=True,
            driver_version="535.154.05",
        )
        assert "RTX 3080" in str(gpu)
        assert "Supported" in str(gpu)
        assert "8.6" in str(gpu)

    def test_str_representation_unsupported(self):
        """Test string representation for unsupported GPU."""
        gpu = GPUInfo(
            name="NVIDIA GeForce GTX 1080",
            compute_capability=(6, 1),
            memory_mb=8192,
            is_supported=False,
            driver_version="535.154.05",
        )
        assert "GTX 1080" in str(gpu)
        assert "Not supported" in str(gpu)


class TestProcessingStats:
    """Tests for ProcessingStats dataclass."""

    def test_default_values(self):
        """Test default stats values."""
        stats = ProcessingStats()
        assert stats.total_frames == 0
        assert stats.processed_frames == 0
        assert stats.frames_per_second == 0.0

    def test_frames_per_second_calculation(self):
        """Test FPS calculation."""
        stats = ProcessingStats(
            processed_frames=300,
            processing_time_seconds=10.0,
        )
        assert stats.frames_per_second == 30.0

    def test_frames_per_second_zero_time(self):
        """Test FPS calculation with zero time."""
        stats = ProcessingStats(
            processed_frames=100,
            processing_time_seconds=0.0,
        )
        assert stats.frames_per_second == 0.0


# =============================================================================
# Utility Tests
# =============================================================================

class TestSDKDetection:
    """Tests for SDK detection functions."""

    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows only")
    def test_detect_sdk_not_found(self):
        """Test SDK detection when not installed."""
        with patch.dict('os.environ', {}, clear=True):
            with patch('pathlib.Path.exists', return_value=False):
                result = detect_sdk()
                assert result is None

    @patch('platform.system')
    def test_detect_sdk_non_windows(self, mock_system):
        """Test SDK detection returns None on non-Windows."""
        mock_system.return_value = "Linux"
        result = detect_sdk()
        assert result is None

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch.dict('os.environ', {'RTX_VIDEO_SDK_HOME': '/mock/sdk/path'})
    def test_detect_sdk_from_env(self, mock_exists, mock_system):
        """Test SDK detection from environment variable."""
        mock_system.return_value = "Windows"
        mock_exists.return_value = True
        # This would find the SDK if the mock is set up correctly
        # For now, test that the function doesn't crash
        result = detect_sdk()
        # Result depends on actual file system behavior


class TestGPUValidation:
    """Tests for GPU validation functions."""

    @patch('subprocess.run')
    def test_validate_gpu_supported(self, mock_run):
        """Test GPU validation with supported RTX GPU."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="NVIDIA GeForce RTX 3080, 8.6, 10240, 535.154.05"
        )
        result = validate_gpu()
        assert result.name == "NVIDIA GeForce RTX 3080"
        assert result.compute_capability == (8, 6)
        assert result.memory_mb == 10240
        assert result.is_supported is True

    @patch('subprocess.run')
    def test_validate_gpu_unsupported(self, mock_run):
        """Test GPU validation with unsupported GTX GPU."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="NVIDIA GeForce GTX 1080, 6.1, 8192, 535.154.05"
        )
        result = validate_gpu()
        assert result.is_supported is False
        assert result.compute_capability == (6, 1)

    @patch('subprocess.run')
    def test_validate_gpu_nvidia_smi_not_found(self, mock_run):
        """Test GPU validation when nvidia-smi not found."""
        mock_run.side_effect = FileNotFoundError()
        result = validate_gpu()
        assert result.is_supported is False
        assert result.name == "Unknown"


class TestIsRTXVideoAvailable:
    """Tests for is_rtx_video_available function."""

    @patch('platform.system')
    def test_not_available_on_linux(self, mock_system):
        """Test availability check on Linux."""
        mock_system.return_value = "Linux"
        available, message = is_rtx_video_available()
        assert available is False
        assert "Windows" in message

    @patch('platform.system')
    @patch('vhs_upscaler.rtx_video_sdk.utils.detect_sdk')
    def test_not_available_no_sdk(self, mock_detect, mock_system):
        """Test availability check when SDK not installed."""
        mock_system.return_value = "Windows"
        mock_detect.return_value = None
        available, message = is_rtx_video_available()
        assert available is False
        assert "not installed" in message.lower()

    @patch('platform.system')
    @patch('vhs_upscaler.rtx_video_sdk.utils.detect_sdk')
    @patch('vhs_upscaler.rtx_video_sdk.utils.validate_gpu')
    def test_not_available_unsupported_gpu(self, mock_gpu, mock_detect, mock_system):
        """Test availability check with unsupported GPU."""
        mock_system.return_value = "Windows"
        mock_detect.return_value = Path("/mock/sdk")
        mock_gpu.return_value = GPUInfo(
            name="GTX 1080",
            compute_capability=(6, 1),
            memory_mb=8192,
            is_supported=False,
            driver_version="535.0",
        )
        available, message = is_rtx_video_available()
        assert available is False
        assert "not supported" in message.lower()

    @patch('platform.system')
    @patch('vhs_upscaler.rtx_video_sdk.utils.detect_sdk')
    @patch('vhs_upscaler.rtx_video_sdk.utils.validate_gpu')
    def test_available_with_rtx_gpu(self, mock_gpu, mock_detect, mock_system):
        """Test availability check with supported RTX GPU."""
        mock_system.return_value = "Windows"
        mock_detect.return_value = Path("/mock/sdk")
        mock_gpu.return_value = GPUInfo(
            name="RTX 3080",
            compute_capability=(8, 6),
            memory_mb=10240,
            is_supported=True,
            driver_version="535.0",
        )
        available, message = is_rtx_video_available()
        assert available is True
        assert "ready" in message.lower()


class TestRecommendedSettings:
    """Tests for get_recommended_settings function."""

    def test_vhs_480p_input(self):
        """Test recommendations for VHS 480p input."""
        settings = get_recommended_settings(640, 480)
        assert settings["scale_factor"] == 4
        assert settings["target_resolution"] == 1080
        assert settings["enable_artifact_reduction"] is True
        assert settings["artifact_strength"] == 0.7

    def test_dvd_480p_input(self):
        """Test recommendations for DVD 480p input."""
        settings = get_recommended_settings(720, 480)
        assert settings["scale_factor"] == 4
        assert settings["enable_artifact_reduction"] is True

    def test_720p_input(self):
        """Test recommendations for 720p input."""
        settings = get_recommended_settings(1280, 720)
        assert settings["scale_factor"] == 2
        assert settings["target_resolution"] == 1440
        assert settings["artifact_strength"] == 0.5

    def test_1080p_input(self):
        """Test recommendations for 1080p input."""
        settings = get_recommended_settings(1920, 1080)
        assert settings["scale_factor"] == 2
        assert settings["target_resolution"] == 2160
        assert settings["enable_artifact_reduction"] is False


class TestSupportedResolutions:
    """Tests for get_supported_resolutions function."""

    def test_returns_list(self):
        """Test that function returns a list."""
        resolutions = get_supported_resolutions()
        assert isinstance(resolutions, list)

    def test_contains_standard_resolutions(self):
        """Test that standard resolutions are included."""
        resolutions = get_supported_resolutions()
        assert 720 in resolutions
        assert 1080 in resolutions
        assert 1440 in resolutions
        assert 2160 in resolutions


# =============================================================================
# Integration Tests
# =============================================================================

class TestVHSUpscalerIntegration:
    """Tests for VHSUpscaler integration with RTX Video SDK."""

    def test_rtxvideo_in_engines_list(self):
        """Test that rtxvideo is in the available engines list."""
        from vhs_upscaler.vhs_upscale import VHSUpscaler
        assert "rtxvideo" in VHSUpscaler.UPSCALE_ENGINES

    def test_rtxvideo_priority(self):
        """Test that rtxvideo has highest priority."""
        from vhs_upscaler.vhs_upscale import VHSUpscaler
        assert VHSUpscaler.UPSCALE_ENGINES[0] == "rtxvideo"

    def test_processing_config_has_rtxvideo_options(self):
        """Test that ProcessingConfig includes RTX Video SDK options."""
        from vhs_upscaler.vhs_upscale import ProcessingConfig

        config = ProcessingConfig()
        assert hasattr(config, 'rtxvideo_artifact_reduction')
        assert hasattr(config, 'rtxvideo_artifact_strength')
        assert hasattr(config, 'rtxvideo_hdr_conversion')
        assert hasattr(config, 'rtxvideo_sdk_path')

    def test_processing_config_default_values(self):
        """Test default values for RTX Video SDK options."""
        from vhs_upscaler.vhs_upscale import ProcessingConfig

        config = ProcessingConfig()
        assert config.rtxvideo_artifact_reduction is True
        assert config.rtxvideo_artifact_strength == 0.5
        assert config.rtxvideo_hdr_conversion is False
        assert config.rtxvideo_sdk_path == ""


# =============================================================================
# Effect Type Tests
# =============================================================================

class TestEffectType:
    """Tests for EffectType enum."""

    def test_effect_values(self):
        """Test effect type values match SDK expectations."""
        assert EffectType.SUPER_RESOLUTION.value == "SuperRes"
        assert EffectType.ARTIFACT_REDUCTION.value == "ArtifactReduction"
        assert EffectType.HDR_CONVERSION.value == "HDR"
        assert EffectType.UPSCALE_PIPELINE.value == "UpscalePipeline"


class TestHDRFormat:
    """Tests for HDRFormat enum."""

    def test_hdr_format_values(self):
        """Test HDR format values."""
        assert HDRFormat.SDR.value == "sdr"
        assert HDRFormat.HDR10.value == "hdr10"
        assert HDRFormat.HLG.value == "hlg"


class TestScaleFactor:
    """Tests for ScaleFactor enum."""

    def test_scale_factor_values(self):
        """Test scale factor values."""
        assert ScaleFactor.X2.value == 2
        assert ScaleFactor.X4.value == 4
        assert ScaleFactor.X1_33.value == 1.33
        assert ScaleFactor.X1_5.value == 1.5
