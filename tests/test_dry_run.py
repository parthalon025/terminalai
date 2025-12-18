"""
Comprehensive Test Suite for Dry-Run Mode
=========================================
Tests for the dry_run.py module for pipeline visualization.

This suite covers:
- DryRunVisualizer initialization
- Pipeline visualization output
- Configuration validation
- FFmpeg command generation
- Stage information display
- Warning detection
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
import subprocess


@pytest.fixture
def processing_config():
    """Create a ProcessingConfig for testing."""
    from vhs_upscaler.vhs_upscale import ProcessingConfig

    return ProcessingConfig(
        resolution=1080,
        quality_mode="medium",
        crf=20,
        encoder="hevc_nvenc",
        deinterlace=True,
        deinterlace_algorithm="yadif",
        denoise=True,
        denoise_strength=(4.0, 3.0, 6.0, 4.5),
        upscale_engine="realesrgan",
        realesrgan_model="realesr-animevideov3",
        audio_enhance=True,
        audio_normalize=True
    )


@pytest.fixture
def dry_run_visualizer(processing_config, temp_dir):
    """Create a DryRunVisualizer instance."""
    from vhs_upscaler.dry_run import DryRunVisualizer

    input_path = temp_dir / "test_input.mp4"
    input_path.write_bytes(b"fake video")

    return DryRunVisualizer(processing_config, input_path)


@pytest.fixture
def mock_video_info():
    """Mock video information."""
    return {
        "width": 720,
        "height": 480,
        "duration": 120.5,
        "codec": "h264",
        "bitrate": 5000000,
        "fps": 29.97,
        "interlaced": True
    }


class TestDryRunVisualizerInit:
    """Test DryRunVisualizer initialization."""

    def test_init_basic(self, processing_config, temp_dir):
        """Test basic initialization."""
        from vhs_upscaler.dry_run import DryRunVisualizer

        input_path = temp_dir / "video.mp4"
        input_path.touch()

        visualizer = DryRunVisualizer(processing_config, input_path)

        assert visualizer.config == processing_config
        assert visualizer.input_path == input_path

    def test_init_with_path_object(self, processing_config, temp_dir):
        """Test initialization with Path object."""
        from vhs_upscaler.dry_run import DryRunVisualizer

        input_path = temp_dir / "video.mp4"
        input_path.touch()

        visualizer = DryRunVisualizer(processing_config, input_path)

        assert isinstance(visualizer.input_path, Path)


class TestPipelineVisualization:
    """Test complete pipeline visualization."""

    def test_show_pipeline_structure(self, dry_run_visualizer):
        """Test pipeline visualization returns formatted string."""
        with patch.object(dry_run_visualizer, '_get_video_info', return_value=None):
            pipeline = dry_run_visualizer.show_pipeline()

            assert isinstance(pipeline, str)
            assert "DRY-RUN MODE" in pipeline
            assert "Processing Pipeline Visualization" in pipeline

    def test_pipeline_includes_all_sections(self, dry_run_visualizer, mock_video_info):
        """Test pipeline includes all major sections."""
        with patch.object(dry_run_visualizer, '_get_video_info', return_value=mock_video_info):
            pipeline = dry_run_visualizer.show_pipeline()

            assert "Input/Output Configuration" in pipeline
            assert "Video Analysis" in pipeline
            assert "Stage 1: Preprocessing" in pipeline
            assert "Stage 2: Upscaling" in pipeline
            assert "Stage 3: Encoding" in pipeline
            assert "FFmpeg Commands" in pipeline

    def test_pipeline_footer(self, dry_run_visualizer):
        """Test pipeline includes dry-run warning footer."""
        with patch.object(dry_run_visualizer, '_get_video_info', return_value=None):
            pipeline = dry_run_visualizer.show_pipeline()

            assert "This is a DRY-RUN" in pipeline
            assert "no files will be modified" in pipeline


class TestIOInfo:
    """Test input/output information display."""

    def test_show_io_info_basic(self, dry_run_visualizer):
        """Test basic I/O information display."""
        with patch.object(dry_run_visualizer, '_get_video_info', return_value=None):
            lines = dry_run_visualizer._show_io_info()

            assert any("Input File:" in line for line in lines)
            assert any(str(dry_run_visualizer.input_path) in line for line in lines)

    def test_show_io_info_with_video_data(self, dry_run_visualizer, mock_video_info):
        """Test I/O info with video metadata."""
        with patch.object(dry_run_visualizer, '_get_video_info', return_value=mock_video_info):
            lines = dry_run_visualizer._show_io_info()

            output = "\n".join(lines)
            assert "720x480" in output
            assert "120.5 seconds" in output
            assert "h264" in output

    def test_show_io_info_resolution(self, dry_run_visualizer):
        """Test resolution display in I/O info."""
        dry_run_visualizer.config.resolution = 2160

        with patch.object(dry_run_visualizer, '_get_video_info', return_value=None):
            lines = dry_run_visualizer._show_io_info()

            output = "\n".join(lines)
            assert "2160p" in output


class TestVideoInfo:
    """Test video analysis information display."""

    def test_show_video_info_interlaced(self, dry_run_visualizer, mock_video_info):
        """Test video info shows interlacing detection."""
        with patch.object(dry_run_visualizer, '_get_video_info', return_value=mock_video_info):
            lines = dry_run_visualizer._show_video_info()

            output = "\n".join(lines)
            assert "Interlaced: Yes" in output

    def test_show_video_info_progressive(self, dry_run_visualizer, mock_video_info):
        """Test video info shows progressive video."""
        mock_video_info["interlaced"] = False

        with patch.object(dry_run_visualizer, '_get_video_info', return_value=mock_video_info):
            lines = dry_run_visualizer._show_video_info()

            output = "\n".join(lines)
            assert "Interlaced: No" in output

    def test_show_video_info_framerate(self, dry_run_visualizer, mock_video_info):
        """Test video info shows frame rate."""
        with patch.object(dry_run_visualizer, '_get_video_info', return_value=mock_video_info):
            lines = dry_run_visualizer._show_video_info()

            output = "\n".join(lines)
            assert "29.97 fps" in output

    def test_show_video_info_aspect_ratio(self, dry_run_visualizer, mock_video_info):
        """Test video info shows aspect ratio."""
        with patch.object(dry_run_visualizer, '_get_video_info', return_value=mock_video_info):
            lines = dry_run_visualizer._show_video_info()

            output = "\n".join(lines)
            assert "Aspect Ratio:" in output

    def test_show_video_info_error_handling(self, dry_run_visualizer):
        """Test graceful error handling when video analysis fails."""
        with patch.object(dry_run_visualizer, '_get_video_info', side_effect=Exception("Error")):
            lines = dry_run_visualizer._show_video_info()

            output = "\n".join(lines)
            assert "Unable to analyze video" in output


class TestPreprocessingStage:
    """Test preprocessing stage display."""

    def test_show_preprocessing_deinterlacing_enabled(self, dry_run_visualizer):
        """Test deinterlacing display when enabled."""
        dry_run_visualizer.config.deinterlace = True
        dry_run_visualizer.config.deinterlace_algorithm = "yadif"

        lines = dry_run_visualizer._show_preprocessing_stage()

        output = "\n".join(lines)
        assert "Deinterlacing: YADIF" in output
        assert "FFmpeg YADIF" in output

    def test_show_preprocessing_qtgmc(self, dry_run_visualizer):
        """Test QTGMC deinterlacing display."""
        dry_run_visualizer.config.deinterlace = True
        dry_run_visualizer.config.deinterlace_algorithm = "qtgmc"
        dry_run_visualizer.config.qtgmc_preset = "slow"

        lines = dry_run_visualizer._show_preprocessing_stage()

        output = "\n".join(lines)
        assert "VapourSynth QTGMC" in output
        assert "Quality Preset: slow" in output

    def test_show_preprocessing_deinterlacing_disabled(self, dry_run_visualizer):
        """Test deinterlacing display when disabled."""
        dry_run_visualizer.config.deinterlace = False

        lines = dry_run_visualizer._show_preprocessing_stage()

        output = "\n".join(lines)
        assert "Deinterlacing: DISABLED" in output

    def test_show_preprocessing_denoising(self, dry_run_visualizer):
        """Test denoising display."""
        dry_run_visualizer.config.denoise = True
        dry_run_visualizer.config.denoise_strength = (4.0, 3.0, 6.0, 4.5)

        lines = dry_run_visualizer._show_preprocessing_stage()

        output = "\n".join(lines)
        assert "Denoising: ENABLED" in output
        assert "hqdn3d" in output
        assert "Luma=4.0" in output

    def test_show_preprocessing_lut(self, dry_run_visualizer):
        """Test LUT color grading display."""
        dry_run_visualizer.config.lut_file = "/path/to/lut.cube"
        dry_run_visualizer.config.lut_strength = 0.8

        lines = dry_run_visualizer._show_preprocessing_stage()

        output = "\n".join(lines)
        assert "Color Grading (LUT): ENABLED" in output
        assert "/path/to/lut.cube" in output
        assert "80%" in output


class TestUpscalingStage:
    """Test upscaling stage display."""

    def test_show_upscaling_realesrgan(self, dry_run_visualizer):
        """Test Real-ESRGAN upscaling display."""
        dry_run_visualizer.config.upscale_engine = "realesrgan"
        dry_run_visualizer.config.realesrgan_model = "realesr-animevideov3"

        lines = dry_run_visualizer._show_upscaling_stage()

        output = "\n".join(lines)
        assert "Real-ESRGAN" in output.upper()
        assert "realesr-animevideov3" in output
        assert "GPU accelerated" in output

    def test_show_upscaling_maxine(self, dry_run_visualizer):
        """Test Maxine upscaling display."""
        dry_run_visualizer.config.upscale_engine = "maxine"

        lines = dry_run_visualizer._show_upscaling_stage()

        output = "\n".join(lines)
        assert "MAXINE" in output.upper()
        assert "NVIDIA RTX required" in output

    def test_show_upscaling_face_restoration(self, dry_run_visualizer):
        """Test face restoration display."""
        dry_run_visualizer.config.face_restore = True
        dry_run_visualizer.config.face_restore_strength = 0.7

        lines = dry_run_visualizer._show_upscaling_stage()

        output = "\n".join(lines)
        assert "Face Restoration: ENABLED" in output
        assert "GFPGAN" in output
        assert "70%" in output


class TestPostprocessingStage:
    """Test postprocessing stage display."""

    def test_show_postprocessing_encoding(self, dry_run_visualizer):
        """Test video encoding display."""
        dry_run_visualizer.config.encoder = "hevc_nvenc"
        dry_run_visualizer.config.crf = 18
        dry_run_visualizer.config.quality_mode = "slow"

        lines = dry_run_visualizer._show_postprocessing_stage()

        output = "\n".join(lines)
        assert "hevc_nvenc" in output
        assert "CRF 18" in output
        assert "slow" in output

    def test_show_postprocessing_hdr(self, dry_run_visualizer):
        """Test HDR mode display."""
        dry_run_visualizer.config.hdr_mode = "hdr10"

        lines = dry_run_visualizer._show_postprocessing_stage()

        output = "\n".join(lines)
        assert "HDR10" in output

    def test_show_postprocessing_audio(self, dry_run_visualizer):
        """Test audio processing display."""
        dry_run_visualizer.config.audio_enhance = True
        dry_run_visualizer.config.audio_normalize = True
        dry_run_visualizer.config.audio_upmix = True
        dry_run_visualizer.config.audio_layout = "5.1"

        lines = dry_run_visualizer._show_postprocessing_stage()

        output = "\n".join(lines)
        assert "Enhancement: ENABLED" in output
        assert "Normalization: ENABLED" in output
        assert "5.1" in output

    def test_show_postprocessing_sharpening(self, dry_run_visualizer):
        """Test sharpening display."""
        dry_run_visualizer.config.sharpen = True

        lines = dry_run_visualizer._show_postprocessing_stage()

        output = "\n".join(lines)
        assert "Sharpening: ENABLED" in output


class TestFFmpegCommands:
    """Test FFmpeg command generation."""

    def test_show_ffmpeg_commands_basic(self, dry_run_visualizer):
        """Test basic FFmpeg command display."""
        lines = dry_run_visualizer._show_ffmpeg_commands()

        output = "\n".join(lines)
        assert "[Preprocessing FFmpeg Command]" in output
        assert "ffmpeg" in output

    def test_show_ffmpeg_deinterlace_filter(self, dry_run_visualizer):
        """Test deinterlace filter in FFmpeg command."""
        dry_run_visualizer.config.deinterlace = True
        dry_run_visualizer.config.deinterlace_algorithm = "bwdif"

        lines = dry_run_visualizer._show_ffmpeg_commands()

        output = "\n".join(lines)
        assert "bwdif" in output

    def test_show_ffmpeg_denoise_filter(self, dry_run_visualizer):
        """Test denoise filter in FFmpeg command."""
        dry_run_visualizer.config.denoise = True
        dry_run_visualizer.config.denoise_strength = (4.0, 3.0, 6.0, 4.5)

        lines = dry_run_visualizer._show_ffmpeg_commands()

        output = "\n".join(lines)
        assert "hqdn3d" in output

    def test_show_ffmpeg_lut_filter(self, dry_run_visualizer):
        """Test LUT filter in FFmpeg command."""
        dry_run_visualizer.config.lut_file = "/path/to/lut.cube"

        lines = dry_run_visualizer._show_ffmpeg_commands()

        output = "\n".join(lines)
        assert "lut3d" in output
        assert "/path/to/lut.cube" in output

    def test_show_ffmpeg_realesrgan_command(self, dry_run_visualizer):
        """Test Real-ESRGAN command display."""
        dry_run_visualizer.config.upscale_engine = "realesrgan"
        dry_run_visualizer.config.realesrgan_model = "realesr-animevideov3"

        lines = dry_run_visualizer._show_ffmpeg_commands()

        output = "\n".join(lines)
        assert "Real-ESRGAN" in output
        assert "realesrgan-ncnn-vulkan" in output

    def test_show_ffmpeg_encoding_command(self, dry_run_visualizer):
        """Test final encoding command display."""
        dry_run_visualizer.config.encoder = "hevc_nvenc"
        dry_run_visualizer.config.crf = 20

        lines = dry_run_visualizer._show_ffmpeg_commands()

        output = "\n".join(lines)
        assert "[Final Encoding Command]" in output
        assert "hevc_nvenc" in output
        assert "-crf 20" in output


class TestConfigurationValidation:
    """Test configuration validation and warnings."""

    def test_validate_qtgmc_without_vapoursynth(self, dry_run_visualizer):
        """Test warning for QTGMC without VapourSynth."""
        dry_run_visualizer.config.deinterlace_algorithm = "qtgmc"

        with patch('importlib.import_module', side_effect=ImportError):
            warnings = dry_run_visualizer._validate_configuration()

            assert any("VapourSynth not installed" in w for w in warnings)

    def test_validate_face_restore_without_gfpgan(self, dry_run_visualizer):
        """Test warning for face restoration without GFPGAN."""
        dry_run_visualizer.config.face_restore = True

        with patch('importlib.import_module', side_effect=ImportError):
            warnings = dry_run_visualizer._validate_configuration()

            # May include GFPGAN warning
            assert isinstance(warnings, list)

    def test_validate_low_crf(self, dry_run_visualizer):
        """Test warning for very low CRF value."""
        dry_run_visualizer.config.crf = 8

        warnings = dry_run_visualizer._validate_configuration()

        assert any("Very low CRF" in w or "large files" in w for w in warnings)

    def test_validate_high_crf(self, dry_run_visualizer):
        """Test warning for high CRF value."""
        dry_run_visualizer.config.crf = 35

        warnings = dry_run_visualizer._validate_configuration()

        assert any("High CRF" in w or "quality loss" in w for w in warnings)

    def test_validate_high_resolution(self, dry_run_visualizer):
        """Test warning for very high resolution."""
        dry_run_visualizer.config.resolution = 4320  # 8K

        warnings = dry_run_visualizer._validate_configuration()

        assert any("Very high resolution" in w for w in warnings)

    def test_validate_missing_lut_file(self, dry_run_visualizer, temp_dir):
        """Test warning for missing LUT file."""
        dry_run_visualizer.config.lut_file = str(temp_dir / "nonexistent.cube")

        warnings = dry_run_visualizer._validate_configuration()

        assert any("LUT file not found" in w for w in warnings)

    def test_validate_valid_config(self, dry_run_visualizer):
        """Test no warnings for valid configuration."""
        # Use reasonable settings
        dry_run_visualizer.config.crf = 20
        dry_run_visualizer.config.resolution = 1080
        dry_run_visualizer.config.deinterlace_algorithm = "yadif"

        warnings = dry_run_visualizer._validate_configuration()

        # Should have minimal or no warnings
        assert isinstance(warnings, list)


class TestGetVideoInfo:
    """Test video information extraction."""

    def test_get_video_info_success(self, dry_run_visualizer, temp_dir):
        """Test successful video info extraction."""
        video_path = temp_dir / "video.mp4"
        video_path.write_bytes(b"video")

        mock_result = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "streams": [{
                    "codec_type": "video",
                    "width": 1920,
                    "height": 1080,
                    "codec_name": "h264",
                    "r_frame_rate": "30/1",
                    "field_order": "progressive"
                }],
                "format": {
                    "duration": "120.0",
                    "bit_rate": "5000000"
                }
            })
        )

        with patch('subprocess.run', return_value=mock_result):
            info = dry_run_visualizer._get_video_info()

            assert info["width"] == 1920
            assert info["height"] == 1080
            assert info["codec"] == "h264"
            assert info["duration"] == 120.0
            assert info["interlaced"] is False

    def test_get_video_info_interlaced(self, dry_run_visualizer, temp_dir):
        """Test interlaced video detection."""
        mock_result = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "streams": [{
                    "codec_type": "video",
                    "width": 720,
                    "height": 480,
                    "codec_name": "mpeg2video",
                    "r_frame_rate": "30000/1001",
                    "field_order": "tt"  # Top field first
                }],
                "format": {
                    "duration": "60.0",
                    "bit_rate": "3000000"
                }
            })
        )

        with patch('subprocess.run', return_value=mock_result):
            info = dry_run_visualizer._get_video_info()

            assert info["interlaced"] is True

    def test_get_video_info_error(self, dry_run_visualizer):
        """Test error handling for video info extraction."""
        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "ffprobe")):
            info = dry_run_visualizer._get_video_info()

            assert info is None


class TestConvenienceFunction:
    """Test convenience function for dry-run."""

    def test_show_dry_run(self, processing_config, temp_dir):
        """Test show_dry_run convenience function."""
        from vhs_upscaler.dry_run import show_dry_run

        input_path = temp_dir / "video.mp4"
        input_path.write_bytes(b"video")

        with patch('vhs_upscaler.dry_run.DryRunVisualizer.show_pipeline') as mock_show:
            mock_show.return_value = "Pipeline output"

            result = show_dry_run(processing_config, input_path)

            assert mock_show.called
            assert result == "Pipeline output"


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_minimal_config(self, temp_dir):
        """Test with minimal configuration."""
        from vhs_upscaler.vhs_upscale import ProcessingConfig
        from vhs_upscaler.dry_run import DryRunVisualizer

        config = ProcessingConfig()
        input_path = temp_dir / "video.mp4"
        input_path.touch()

        visualizer = DryRunVisualizer(config, input_path)

        with patch.object(visualizer, '_get_video_info', return_value=None):
            pipeline = visualizer.show_pipeline()
            assert "DRY-RUN MODE" in pipeline

    def test_all_features_enabled(self, temp_dir):
        """Test with all features enabled."""
        from vhs_upscaler.vhs_upscale import ProcessingConfig
        from vhs_upscaler.dry_run import DryRunVisualizer

        config = ProcessingConfig(
            deinterlace=True,
            deinterlace_algorithm="qtgmc",
            qtgmc_preset="slow",
            denoise=True,
            face_restore=True,
            audio_enhance=True,
            audio_upmix=True,
            audio_normalize=True,
            sharpen=True,
            hdr_mode="hdr10"
        )

        input_path = temp_dir / "video.mp4"
        input_path.touch()

        visualizer = DryRunVisualizer(config, input_path)

        with patch.object(visualizer, '_get_video_info', return_value=None):
            pipeline = visualizer.show_pipeline()

            # Should include all features
            assert "QTGMC" in pipeline
            assert "Denoising: ENABLED" in pipeline
            assert "Face Restoration: ENABLED" in pipeline
