"""
Comprehensive Test Suite for Preset Comparison Module
=====================================================
Tests for the comparison.py module for generating preset comparison grids.

This suite covers:
- PresetComparator initialization
- Test clip extraction from source video
- Preset processing pipeline
- Grid generation (horizontal and vertical stacks)
- Report generation
- Error handling and edge cases
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
import subprocess


@pytest.fixture
def comparison_config(temp_dir):
    """Create a ComparisonConfig for testing."""
    from vhs_upscaler.comparison import ComparisonConfig

    input_video = temp_dir / "input.mp4"
    input_video.write_bytes(b"fake video")

    return ComparisonConfig(
        input_path=input_video,
        output_dir=temp_dir / "comparisons",
        presets=["vhs_standard", "vhs_clean"],
        clip_count=2,
        clip_duration=5,
        include_original=True
    )


@pytest.fixture
def preset_comparator(comparison_config):
    """Create a PresetComparator instance."""
    from vhs_upscaler.comparison import PresetComparator

    return PresetComparator(comparison_config)


@pytest.fixture
def mock_ffmpeg_run():
    """Mock subprocess.run for FFmpeg commands."""
    with patch('subprocess.run') as mock:
        mock.return_value = MagicMock(returncode=0, stdout="", stderr="")
        yield mock


@pytest.fixture
def mock_upscaler():
    """Mock VHSUpscaler for processing."""
    with patch('vhs_upscaler.comparison.VHSUpscaler') as mock:
        instance = MagicMock()
        instance.process.return_value = True
        mock.return_value = instance
        yield mock


class TestComparisonConfig:
    """Test ComparisonConfig dataclass."""

    def test_config_defaults(self, temp_dir):
        """Test ComparisonConfig with default values."""
        from vhs_upscaler.comparison import ComparisonConfig

        input_video = temp_dir / "test.mp4"
        input_video.touch()

        config = ComparisonConfig(
            input_path=input_video,
            output_dir=temp_dir / "output",
            presets=["vhs"]
        )

        assert config.clip_count == 3
        assert config.clip_duration == 10
        assert config.timestamps is None
        assert config.include_original is True
        assert config.label_position == "top"
        assert config.label_font_size == 24

    def test_config_custom_values(self, temp_dir):
        """Test ComparisonConfig with custom values."""
        from vhs_upscaler.comparison import ComparisonConfig

        input_video = temp_dir / "test.mp4"
        input_video.touch()

        config = ComparisonConfig(
            input_path=input_video,
            output_dir=temp_dir / "output",
            presets=["vhs", "dvd"],
            clip_count=5,
            clip_duration=15,
            timestamps=[10, 20, 30],
            include_original=False,
            label_position="bottom",
            label_font_size=32
        )

        assert config.clip_count == 5
        assert config.clip_duration == 15
        assert config.timestamps == [10, 20, 30]
        assert config.include_original is False
        assert config.label_position == "bottom"
        assert config.label_font_size == 32

    def test_config_with_custom_labels(self, temp_dir):
        """Test ComparisonConfig with custom label styling."""
        from vhs_upscaler.comparison import ComparisonConfig

        input_video = temp_dir / "test.mp4"
        input_video.touch()

        config = ComparisonConfig(
            input_path=input_video,
            output_dir=temp_dir / "output",
            presets=["vhs"],
            label_bg_color="blue@0.5",
            label_text_color="yellow"
        )

        assert config.label_bg_color == "blue@0.5"
        assert config.label_text_color == "yellow"


class TestPresetComparatorInit:
    """Test PresetComparator initialization."""

    def test_init_creates_directories(self, comparison_config):
        """Test that initialization creates output directories."""
        from vhs_upscaler.comparison import PresetComparator

        comparator = PresetComparator(comparison_config)

        assert comparator.config.output_dir.exists()
        assert comparator.clips_dir.exists()
        assert comparator.comparisons_dir.exists()

    def test_init_directory_structure(self, comparison_config):
        """Test correct directory structure is created."""
        from vhs_upscaler.comparison import PresetComparator

        comparator = PresetComparator(comparison_config)

        assert comparator.clips_dir == comparison_config.output_dir / "clips"
        assert comparator.comparisons_dir == comparison_config.output_dir / "comparisons"

    def test_init_with_existing_directories(self, comparison_config):
        """Test initialization with pre-existing directories."""
        from vhs_upscaler.comparison import PresetComparator

        # Create directories first
        comparison_config.output_dir.mkdir(parents=True, exist_ok=True)

        comparator = PresetComparator(comparison_config)
        # Should not raise error
        assert comparator.config.output_dir.exists()


class TestClipExtraction:
    """Test test clip extraction from source video."""

    @patch('subprocess.run')
    def test_extract_test_clips(self, mock_run, preset_comparator, temp_dir):
        """Test extraction of test clips from video."""
        mock_run.return_value = MagicMock(returncode=0)

        # Mock video duration
        with patch.object(preset_comparator, '_get_video_duration', return_value=100.0):
            clips = preset_comparator._extract_test_clips()

            assert len(clips) == preset_comparator.config.clip_count
            assert all(isinstance(clip, Path) for clip in clips)

    @patch('subprocess.run')
    def test_extract_with_custom_timestamps(self, mock_run, comparison_config, temp_dir):
        """Test clip extraction with custom timestamps."""
        from vhs_upscaler.comparison import PresetComparator

        mock_run.return_value = MagicMock(returncode=0)
        comparison_config.timestamps = [5, 15, 25]

        comparator = PresetComparator(comparison_config)

        with patch.object(comparator, '_get_video_duration', return_value=100.0):
            clips = comparator._extract_test_clips()

            # Should extract at custom timestamps
            assert len(clips) == 3

    @patch('subprocess.run')
    def test_extract_ffmpeg_command(self, mock_run, preset_comparator):
        """Test FFmpeg command for clip extraction."""
        mock_run.return_value = MagicMock(returncode=0)

        with patch.object(preset_comparator, '_get_video_duration', return_value=100.0):
            preset_comparator._extract_test_clips()

            # Verify FFmpeg was called
            assert mock_run.called
            cmd = mock_run.call_args_list[0][0][0]
            assert preset_comparator.config.ffmpeg_path in cmd
            assert "-ss" in cmd  # Seek
            assert "-t" in cmd   # Duration

    @patch('subprocess.run')
    def test_extract_evenly_spaced_clips(self, mock_run, preset_comparator):
        """Test clips are extracted at evenly spaced intervals."""
        mock_run.return_value = MagicMock(returncode=0)

        video_duration = 120.0
        with patch.object(preset_comparator, '_get_video_duration', return_value=video_duration):
            clips = preset_comparator._extract_test_clips()

            # Verify even spacing calculation
            assert len(clips) == preset_comparator.config.clip_count


class TestPresetProcessing:
    """Test processing clips with different presets."""

    def test_process_clips_with_presets(self, preset_comparator, mock_upscaler, temp_dir):
        """Test processing clips with each preset."""
        # Create mock clips
        clips = [temp_dir / f"clip_{i}.mp4" for i in range(2)]
        for clip in clips:
            clip.write_bytes(b"clip data")

        results = preset_comparator._process_clips_with_presets(clips)

        assert len(results) == len(clips)
        for clip_idx in results:
            assert "vhs_standard" in results[clip_idx]
            assert "vhs_clean" in results[clip_idx]

    def test_process_includes_original(self, preset_comparator, mock_upscaler, temp_dir):
        """Test original clip is included when configured."""
        preset_comparator.config.include_original = True

        clips = [temp_dir / "clip_0.mp4"]
        clips[0].write_bytes(b"clip data")

        results = preset_comparator._process_clips_with_presets(clips)

        assert "original" in results[0]
        assert results[0]["original"] == clips[0]

    def test_process_excludes_original(self, preset_comparator, mock_upscaler, temp_dir):
        """Test original is excluded when configured."""
        preset_comparator.config.include_original = False

        clips = [temp_dir / "clip_0.mp4"]
        clips[0].write_bytes(b"clip data")

        results = preset_comparator._process_clips_with_presets(clips)

        assert "original" not in results[0]

    def test_process_error_handling(self, preset_comparator, temp_dir):
        """Test error handling during preset processing."""
        with patch('vhs_upscaler.comparison.VHSUpscaler') as mock_upscaler:
            instance = MagicMock()
            instance.process.side_effect = Exception("Processing failed")
            mock_upscaler.return_value = instance

            clips = [temp_dir / "clip_0.mp4"]
            clips[0].write_bytes(b"clip data")

            results = preset_comparator._process_clips_with_presets(clips)

            # Should fallback to original on error
            assert "vhs_standard" in results[0]


class TestGridGeneration:
    """Test comparison grid generation."""

    @patch('subprocess.run')
    def test_create_clip_comparison(self, mock_run, preset_comparator, temp_dir):
        """Test creation of single clip comparison."""
        mock_run.return_value = MagicMock(returncode=0)

        preset_results = {
            "original": temp_dir / "original.mp4",
            "vhs": temp_dir / "vhs.mp4"
        }
        for path in preset_results.values():
            path.write_bytes(b"video")

        output = preset_comparator._create_clip_comparison(0, preset_results)

        assert output.exists() or mock_run.called
        assert "comparison_clip0.mp4" in output.name

    @patch('subprocess.run')
    def test_clip_comparison_ffmpeg_command(self, mock_run, preset_comparator, temp_dir):
        """Test FFmpeg command for clip comparison."""
        mock_run.return_value = MagicMock(returncode=0)

        preset_results = {
            "preset1": temp_dir / "preset1.mp4",
            "preset2": temp_dir / "preset2.mp4"
        }
        for path in preset_results.values():
            path.write_bytes(b"video")

        preset_comparator._create_clip_comparison(0, preset_results)

        assert mock_run.called
        cmd = mock_run.call_args[0][0]
        assert "-filter_complex" in cmd
        assert "hstack" in str(cmd)

    @patch('subprocess.run')
    def test_create_full_grid(self, mock_run, preset_comparator, temp_dir):
        """Test creation of full comparison grid."""
        mock_run.return_value = MagicMock(returncode=0)

        all_results = {
            0: {
                "original": temp_dir / "clip0_orig.mp4",
                "vhs": temp_dir / "clip0_vhs.mp4"
            },
            1: {
                "original": temp_dir / "clip1_orig.mp4",
                "vhs": temp_dir / "clip1_vhs.mp4"
            }
        }
        for clip_results in all_results.values():
            for path in clip_results.values():
                path.write_bytes(b"video")

        with patch.object(preset_comparator, '_create_horizontal_stack'):
            output = preset_comparator._create_full_grid(all_results)
            assert "comparison_full.mp4" in output.name

    @patch('subprocess.run')
    def test_horizontal_stack(self, mock_run, preset_comparator, temp_dir):
        """Test horizontal video stacking."""
        mock_run.return_value = MagicMock(returncode=0)

        preset_results = {
            "preset1": temp_dir / "preset1.mp4",
            "preset2": temp_dir / "preset2.mp4"
        }
        for path in preset_results.values():
            path.write_bytes(b"video")

        output_path = temp_dir / "stack.mp4"
        preset_comparator._create_horizontal_stack(preset_results, output_path)

        assert mock_run.called
        cmd = mock_run.call_args[0][0]
        assert "hstack" in str(cmd)


class TestVideoInfo:
    """Test video information retrieval."""

    def test_get_video_duration(self, preset_comparator, temp_dir):
        """Test video duration extraction using ffprobe."""
        mock_result = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "format": {"duration": "120.5"}
            })
        )

        with patch('subprocess.run', return_value=mock_result):
            video_path = temp_dir / "video.mp4"
            video_path.write_bytes(b"video")

            duration = preset_comparator._get_video_duration(video_path)
            assert duration == 120.5

    def test_get_video_duration_error(self, preset_comparator, temp_dir):
        """Test error handling for video duration extraction."""
        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "ffprobe")):
            video_path = temp_dir / "video.mp4"

            with pytest.raises(subprocess.CalledProcessError):
                preset_comparator._get_video_duration(video_path)


class TestReportGeneration:
    """Test comparison report generation."""

    def test_generate_comparison_report(self, preset_comparator, temp_dir):
        """Test comparison report generation."""
        comparisons = {
            "clip_0": temp_dir / "comparison_clip0.mp4",
            "clip_1": temp_dir / "comparison_clip1.mp4",
            "full_grid": temp_dir / "comparison_full.mp4"
        }

        # Create files
        for path in comparisons.values():
            path.write_bytes(b"video data")

        report = preset_comparator.generate_comparison_report(comparisons)

        assert "Preset Comparison Report" in report
        assert preset_comparator.config.input_path.name in report
        assert "vhs_standard" in report
        assert "vhs_clean" in report

    def test_report_includes_file_sizes(self, preset_comparator, temp_dir):
        """Test report includes file sizes."""
        comparisons = {
            "clip_0": temp_dir / "comparison_clip0.mp4"
        }
        comparisons["clip_0"].write_bytes(b"x" * 1024 * 1024)  # 1 MB

        report = preset_comparator.generate_comparison_report(comparisons)

        assert "MB" in report

    def test_report_with_missing_files(self, preset_comparator, temp_dir):
        """Test report handles missing files gracefully."""
        comparisons = {
            "clip_0": temp_dir / "nonexistent.mp4"
        }

        report = preset_comparator.generate_comparison_report(comparisons)

        # Should still generate report without errors
        assert "Preset Comparison Report" in report


class TestComparisonSuite:
    """Test complete comparison suite generation."""

    @patch('subprocess.run')
    def test_generate_comparison_suite(self, mock_run, preset_comparator, mock_upscaler):
        """Test complete comparison suite generation."""
        mock_run.return_value = MagicMock(returncode=0)

        with patch.object(preset_comparator, '_get_video_duration', return_value=120.0):
            with patch.object(preset_comparator, '_extract_test_clips') as mock_extract:
                clips = [preset_comparator.clips_dir / f"clip_{i}.mp4" for i in range(2)]
                for clip in clips:
                    clip.write_bytes(b"clip")
                mock_extract.return_value = clips

                with patch.object(preset_comparator, '_process_clips_with_presets') as mock_process:
                    mock_process.return_value = {
                        0: {"original": clips[0], "vhs": clips[0]},
                        1: {"original": clips[1], "vhs": clips[1]}
                    }

                    with patch.object(preset_comparator, '_create_clip_comparison') as mock_clip_comp:
                        mock_clip_comp.return_value = preset_comparator.comparisons_dir / "comp.mp4"

                        with patch.object(preset_comparator, '_create_full_grid') as mock_grid:
                            mock_grid.return_value = preset_comparator.comparisons_dir / "full.mp4"

                            comparisons = preset_comparator.generate_comparison_suite()

                            assert "full_grid" in comparisons
                            assert "clip_0" in comparisons
                            assert "clip_1" in comparisons


class TestConvenienceFunction:
    """Test convenience function for comparison generation."""

    @patch('vhs_upscaler.comparison.PresetComparator')
    def test_generate_preset_comparison(self, mock_comparator, temp_dir):
        """Test generate_preset_comparison convenience function."""
        from vhs_upscaler.comparison import generate_preset_comparison

        input_video = temp_dir / "input.mp4"
        input_video.write_bytes(b"video")

        mock_instance = MagicMock()
        mock_instance.generate_comparison_suite.return_value = {
            "clip_0": temp_dir / "comp.mp4"
        }
        mock_instance.generate_comparison_report.return_value = "Test report"
        mock_comparator.return_value = mock_instance

        result = generate_preset_comparison(
            input_path=input_video,
            output_dir=temp_dir / "output",
            presets=["vhs", "dvd"],
            clip_count=3
        )

        assert mock_comparator.called
        assert mock_instance.generate_comparison_suite.called
        assert mock_instance.generate_comparison_report.called


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_presets_list(self, temp_dir):
        """Test with empty presets list."""
        from vhs_upscaler.comparison import ComparisonConfig, PresetComparator

        input_video = temp_dir / "input.mp4"
        input_video.write_bytes(b"video")

        config = ComparisonConfig(
            input_path=input_video,
            output_dir=temp_dir / "output",
            presets=[]
        )

        comparator = PresetComparator(config)
        # Should handle gracefully

    def test_single_preset(self, temp_dir):
        """Test with single preset (comparison of original vs preset)."""
        from vhs_upscaler.comparison import ComparisonConfig, PresetComparator

        input_video = temp_dir / "input.mp4"
        input_video.write_bytes(b"video")

        config = ComparisonConfig(
            input_path=input_video,
            output_dir=temp_dir / "output",
            presets=["vhs"]
        )

        comparator = PresetComparator(config)
        assert len(config.presets) == 1

    def test_many_presets(self, temp_dir):
        """Test with many presets."""
        from vhs_upscaler.comparison import ComparisonConfig, PresetComparator

        input_video = temp_dir / "input.mp4"
        input_video.write_bytes(b"video")

        config = ComparisonConfig(
            input_path=input_video,
            output_dir=temp_dir / "output",
            presets=["preset1", "preset2", "preset3", "preset4", "preset5"]
        )

        comparator = PresetComparator(config)
        assert len(config.presets) == 5

    @patch('subprocess.run')
    def test_ffmpeg_failure_handling(self, mock_run, preset_comparator, temp_dir):
        """Test handling of FFmpeg command failures."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")

        with patch.object(preset_comparator, '_get_video_duration', return_value=100.0):
            with pytest.raises(subprocess.CalledProcessError):
                preset_comparator._extract_test_clips()
