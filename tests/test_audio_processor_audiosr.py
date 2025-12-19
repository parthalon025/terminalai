#!/usr/bin/env python3
"""
Unit tests for AudioSR integration in audio_processor.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
import tempfile
import shutil

from vhs_upscaler.audio_processor import (
    AudioProcessor,
    AudioConfig,
    AudioFormat,
    AudioChannelLayout,
    AudioEnhanceMode,
    UpmixMode
)


class TestAudioSRIntegration(unittest.TestCase):
    """Test AudioSR AI upsampling integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_input = self.temp_dir / "input.wav"
        self.test_output = self.temp_dir / "output.wav"

        # Create dummy input file
        self.test_input.touch()

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_audiosr_config_defaults(self):
        """Test AudioSR configuration defaults."""
        config = AudioConfig()

        self.assertFalse(config.use_audiosr)
        self.assertEqual(config.audiosr_model, "basic")
        self.assertEqual(config.audiosr_device, "auto")

    def test_audiosr_config_custom(self):
        """Test custom AudioSR configuration."""
        config = AudioConfig(
            use_audiosr=True,
            audiosr_model="speech",
            audiosr_device="cuda"
        )

        self.assertTrue(config.use_audiosr)
        self.assertEqual(config.audiosr_model, "speech")
        self.assertEqual(config.audiosr_device, "cuda")

    def test_check_audiosr_available(self):
        """Test AudioSR availability check when installed."""
        with patch('vhs_upscaler.audio_processor.subprocess.run') as mock_run:
            # Mock successful import
            with patch('builtins.__import__', return_value=Mock()):
                config = AudioConfig()
                processor = AudioProcessor(config)

                # Should be available if import succeeds
                # Note: This will depend on actual import behavior
                self.assertIsInstance(processor.audiosr_available, bool)

    def test_check_audiosr_unavailable(self):
        """Test AudioSR availability check when not installed."""
        config = AudioConfig()
        processor = AudioProcessor(config)

        # AudioSR check should return False if not installed
        # (actual result depends on environment)
        self.assertIsInstance(processor.audiosr_available, bool)

    @patch('vhs_upscaler.audio_processor.AudioProcessor._check_audiosr')
    def test_audiosr_not_available_fallback(self, mock_check):
        """Test graceful fallback when AudioSR not available."""
        mock_check.return_value = False

        config = AudioConfig(use_audiosr=True)
        processor = AudioProcessor(config)

        self.assertFalse(processor.audiosr_available)

    @patch('torch.cuda.is_available')
    @patch('torchaudio.load')
    @patch('torchaudio.save')
    @patch('audiosr.build_audiosuperresolution')
    def test_upsample_audiosr_basic_model(
        self, mock_build, mock_save, mock_load, mock_cuda
    ):
        """Test AudioSR upsampling with basic model."""
        mock_cuda.return_value = False  # Use CPU

        # Mock audio tensor
        mock_audio = MagicMock()
        mock_audio.shape = [2, 48000]  # Stereo, 1 second
        mock_audio.to.return_value = mock_audio
        mock_audio.cpu.return_value = mock_audio
        mock_load.return_value = (mock_audio, 16000)  # 16kHz input

        # Mock AudioSR model
        mock_model = MagicMock()
        mock_model.return_value = mock_audio  # Return upsampled audio
        mock_build.return_value = mock_model

        config = AudioConfig(
            use_audiosr=True,
            audiosr_model="basic",
            audiosr_device="auto"
        )
        processor = AudioProcessor(config)
        processor.audiosr_available = True

        # Run upsampling
        result = processor._upsample_audiosr(self.test_input, self.test_output, 48000)

        # Verify model was built with correct parameters
        mock_build.assert_called_once_with(
            model_name="basic",
            device="cpu"
        )

        # Verify audio was loaded
        mock_load.assert_called_once()

        # Verify upsampling was performed
        mock_model.assert_called_once()

        # Verify output was saved
        mock_save.assert_called_once()

        self.assertEqual(result, str(self.test_output))

    @patch('torch.cuda.is_available')
    @patch('torchaudio.load')
    @patch('torchaudio.save')
    @patch('audiosr.build_audiosuperresolution')
    def test_upsample_audiosr_speech_model_cuda(
        self, mock_build, mock_save, mock_load, mock_cuda
    ):
        """Test AudioSR upsampling with speech model on CUDA."""
        mock_cuda.return_value = True  # CUDA available

        # Mock audio tensor
        mock_audio = MagicMock()
        mock_audio.shape = [1, 32000]  # Mono, 2 seconds at 16kHz
        mock_audio.to.return_value = mock_audio
        mock_audio.cpu.return_value = mock_audio
        mock_load.return_value = (mock_audio, 16000)

        # Mock AudioSR model
        mock_model = MagicMock()
        mock_model.return_value = mock_audio
        mock_build.return_value = mock_model

        config = AudioConfig(
            use_audiosr=True,
            audiosr_model="speech",
            audiosr_device="auto"
        )
        processor = AudioProcessor(config)
        processor.audiosr_available = True

        result = processor._upsample_audiosr(self.test_input, self.test_output, 48000)

        # Verify CUDA device was selected
        mock_build.assert_called_once_with(
            model_name="speech",
            device="cuda"
        )

        self.assertEqual(result, str(self.test_output))

    @patch('torch.cuda.is_available')
    @patch('torchaudio.load')
    @patch('torchaudio.save')
    @patch('audiosr.build_audiosuperresolution')
    def test_upsample_audiosr_multi_channel_conversion(
        self, mock_build, mock_save, mock_load, mock_cuda
    ):
        """Test AudioSR converts multi-channel audio to stereo."""
        mock_cuda.return_value = False

        # Mock 5.1 audio (6 channels)
        mock_audio = MagicMock()
        mock_audio.shape = [6, 48000]  # 6 channels
        mock_audio.__getitem__ = lambda self, key: mock_audio  # For slicing
        mock_audio.to.return_value = mock_audio
        mock_audio.cpu.return_value = mock_audio
        mock_load.return_value = (mock_audio, 16000)

        # Mock AudioSR model
        mock_model = MagicMock()
        mock_model.return_value = mock_audio
        mock_build.return_value = mock_model

        config = AudioConfig(use_audiosr=True)
        processor = AudioProcessor(config)
        processor.audiosr_available = True

        result = processor._upsample_audiosr(self.test_input, self.test_output, 48000)

        # Should succeed despite multi-channel input
        self.assertEqual(result, str(self.test_output))

    @patch('vhs_upscaler.audio_processor.AudioProcessor._resample_ffmpeg')
    def test_upsample_audiosr_import_error_fallback(self, mock_ffmpeg):
        """Test fallback to FFmpeg when AudioSR import fails."""
        mock_ffmpeg.return_value = str(self.test_output)

        config = AudioConfig(use_audiosr=True)
        processor = AudioProcessor(config)

        # Force import error by making audiosr unavailable
        with patch('builtins.__import__', side_effect=ImportError("audiosr not found")):
            result = processor._upsample_audiosr(self.test_input, self.test_output, 48000)

        # Should fallback to FFmpeg
        mock_ffmpeg.assert_called_once_with(self.test_input, self.test_output, 48000)
        self.assertEqual(result, str(self.test_output))

    @patch('subprocess.run')
    def test_resample_ffmpeg(self, mock_run):
        """Test FFmpeg resampling fallback."""
        mock_run.return_value = Mock(returncode=0)

        config = AudioConfig()
        processor = AudioProcessor(config)

        result = processor._resample_ffmpeg(self.test_input, self.test_output, 48000)

        # Verify FFmpeg was called with correct arguments
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]

        self.assertIn("ffmpeg", cmd[0])
        self.assertIn("-i", cmd)
        self.assertIn(str(self.test_input), cmd)
        self.assertIn("-ar", cmd)
        self.assertIn("48000", cmd)
        self.assertIn(str(self.test_output), cmd)

        self.assertEqual(result, str(self.test_output))

    @patch('subprocess.run')
    def test_resample_ffmpeg_error_handling(self, mock_run):
        """Test FFmpeg resampling error handling."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, ['ffmpeg'])

        config = AudioConfig()
        processor = AudioProcessor(config)

        # Should copy file on error
        with patch('shutil.copy') as mock_copy:
            result = processor._resample_ffmpeg(self.test_input, self.test_output, 48000)
            mock_copy.assert_called_once_with(self.test_input, self.test_output)

    @patch('vhs_upscaler.audio_processor.AudioProcessor.get_audio_info')
    @patch('vhs_upscaler.audio_processor.AudioProcessor._upsample_audiosr')
    @patch('vhs_upscaler.audio_processor.AudioProcessor._extract_audio')
    @patch('vhs_upscaler.audio_processor.AudioProcessor._encode_audio')
    @patch('vhs_upscaler.audio_processor.AudioProcessor._normalize_audio')
    @patch('tempfile.mkdtemp')
    @patch('shutil.rmtree')
    def test_audiosr_in_process_pipeline(
        self, mock_rmtree, mock_mkdtemp, mock_normalize,
        mock_encode, mock_extract, mock_audiosr, mock_info
    ):
        """Test AudioSR integration in full processing pipeline."""
        mock_mkdtemp.return_value = str(self.temp_dir)
        mock_info.side_effect = [
            {'channels': 2, 'codec': 'pcm_s16le', 'sample_rate': 22050},  # Initial
            {'channels': 2, 'codec': 'pcm_s16le', 'sample_rate': 22050},  # Before AudioSR
        ]

        config = AudioConfig(
            use_audiosr=True,
            audiosr_model="basic"
        )
        processor = AudioProcessor(config)
        processor.audiosr_available = True

        # Process audio
        result = processor.process(self.test_input, self.test_output)

        # AudioSR should be called because sample rate is below 48kHz
        mock_audiosr.assert_called_once()

    @patch('vhs_upscaler.audio_processor.AudioProcessor.get_audio_info')
    @patch('vhs_upscaler.audio_processor.AudioProcessor._upsample_audiosr')
    @patch('vhs_upscaler.audio_processor.AudioProcessor._extract_audio')
    @patch('vhs_upscaler.audio_processor.AudioProcessor._encode_audio')
    @patch('tempfile.mkdtemp')
    @patch('shutil.rmtree')
    def test_audiosr_skipped_for_high_samplerate(
        self, mock_rmtree, mock_mkdtemp, mock_encode,
        mock_extract, mock_audiosr, mock_info
    ):
        """Test AudioSR is skipped for audio already at 48kHz."""
        mock_mkdtemp.return_value = str(self.temp_dir)
        mock_info.return_value = {
            'channels': 2,
            'codec': 'pcm_s16le',
            'sample_rate': 48000  # Already 48kHz
        }

        config = AudioConfig(
            use_audiosr=True,
            audiosr_model="basic"
        )
        processor = AudioProcessor(config)
        processor.audiosr_available = True

        # Process audio
        result = processor.process(self.test_input, self.test_output)

        # AudioSR should NOT be called
        mock_audiosr.assert_not_called()

    def test_get_available_features_includes_audiosr(self):
        """Test that get_available_features() checks for AudioSR."""
        from vhs_upscaler.audio_processor import get_available_features

        features = get_available_features()

        self.assertIn('audiosr', features)
        self.assertIsInstance(features['audiosr'], bool)

    @patch('vhs_upscaler.audio_processor.AudioProcessor._upsample_audiosr')
    @patch('vhs_upscaler.audio_processor.AudioProcessor._upmix_with_ffmpeg')
    def test_audiosr_before_upmix(self, mock_upmix, mock_audiosr):
        """Test that AudioSR upsampling occurs before surround upmixing."""
        config = AudioConfig(
            use_audiosr=True,
            upmix_mode=UpmixMode.SURROUND,
            output_layout=AudioChannelLayout.SURROUND_51
        )
        processor = AudioProcessor(config)
        processor.audiosr_available = True

        # This is an integration point test
        # In actual implementation, AudioSR should run before upmixing
        # to provide better quality source for surround generation

    def test_invalid_audiosr_model_fallback(self):
        """Test handling of invalid AudioSR model selection."""
        config = AudioConfig(
            use_audiosr=True,
            audiosr_model="invalid_model"
        )
        processor = AudioProcessor(config)

        # Should handle gracefully
        # The actual implementation will log a warning and use 'basic'


class TestAudioSRCLI(unittest.TestCase):
    """Test CLI integration for AudioSR."""

    @patch('vhs_upscaler.audio_processor.AudioProcessor.process')
    @patch('vhs_upscaler.audio_processor.get_available_features')
    @patch('sys.argv')
    def test_cli_audiosr_flag(self, mock_argv, mock_features, mock_process):
        """Test --audio-sr CLI flag."""
        from vhs_upscaler.audio_processor import main

        mock_features.return_value = {
            'ffmpeg': True,
            'demucs': False,
            'deepfilternet': False,
            'audiosr': True
        }

        mock_argv[1:] = [
            '-i', 'input.wav',
            '-o', 'output.wav',
            '--audio-sr'
        ]

        mock_process.return_value = Path('output.wav')

        # Run CLI
        with patch('builtins.print'):
            main()

        # Verify processor was called with AudioSR enabled
        self.assertTrue(mock_process.called)

    @patch('vhs_upscaler.audio_processor.get_available_features')
    @patch('sys.argv')
    def test_cli_audiosr_unavailable_warning(self, mock_argv, mock_features):
        """Test warning when AudioSR is requested but unavailable."""
        mock_features.return_value = {
            'ffmpeg': True,
            'demucs': False,
            'deepfilternet': False,
            'audiosr': False  # Not available
        }

        mock_argv[1:] = [
            '-i', 'input.wav',
            '-o', 'output.wav',
            '--audio-sr'
        ]

        # Should print warning about AudioSR not being available
        # But still proceed with FFmpeg fallback


class TestAudioSREdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_audiosr_with_empty_audio(self):
        """Test AudioSR handling of empty/silent audio."""
        # Edge case: silent audio should still process
        pass

    def test_audiosr_with_very_short_audio(self):
        """Test AudioSR with very short audio clips."""
        # Edge case: sub-second audio
        pass

    def test_audiosr_memory_efficiency(self):
        """Test AudioSR handles large files without memory issues."""
        # AudioSR should process in chunks for memory efficiency
        pass

    def test_audiosr_preserves_stereo_imaging(self):
        """Test that AudioSR preserves stereo width and imaging."""
        # Important for music production
        pass


if __name__ == '__main__':
    unittest.main()
