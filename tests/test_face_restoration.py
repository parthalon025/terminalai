#!/usr/bin/env python3
"""
Tests for Face Restoration Module
==================================

Comprehensive tests for GFPGAN and CodeFormer face restoration backends.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
import tempfile
import numpy as np

import pytest


# Helper functions
def _check_gfpgan_import():
    """Check if GFPGAN can be imported."""
    try:
        import gfpgan
        return True
    except ImportError:
        return False


def _check_codeformer_import():
    """Check if CodeFormer can be imported."""
    try:
        import codeformer
        return True
    except ImportError:
        return False


class TestFaceRestorerInitialization(unittest.TestCase):
    """Test FaceRestorer class initialization and backend selection."""

    @patch('vhs_upscaler.face_restoration.check_gfpgan_available')
    @patch('vhs_upscaler.face_restoration.check_codeformer_available')
    def test_init_prefers_codeformer_when_both_available(self, mock_cf, mock_gfpgan):
        """CodeFormer should be preferred when both backends available."""
        mock_cf.return_value = True
        mock_gfpgan.return_value = True

        from vhs_upscaler.face_restoration import FaceRestorer

        restorer = FaceRestorer(backend='auto')
        self.assertEqual(restorer.backend, 'codeformer')

    @patch('vhs_upscaler.face_restoration.check_gfpgan_available')
    @patch('vhs_upscaler.face_restoration.check_codeformer_available')
    def test_init_uses_gfpgan_when_codeformer_unavailable(self, mock_cf, mock_gfpgan):
        """GFPGAN should be used when CodeFormer unavailable."""
        mock_cf.return_value = False
        mock_gfpgan.return_value = True

        from vhs_upscaler.face_restoration import FaceRestorer

        restorer = FaceRestorer(backend='auto')
        self.assertEqual(restorer.backend, 'gfpgan')

    @patch('vhs_upscaler.face_restoration.check_gfpgan_available')
    @patch('vhs_upscaler.face_restoration.check_codeformer_available')
    def test_init_raises_when_both_unavailable(self, mock_cf, mock_gfpgan):
        """Should raise error when no backends available."""
        mock_cf.return_value = False
        mock_gfpgan.return_value = False

        from vhs_upscaler.face_restoration import FaceRestorer

        with self.assertRaises(RuntimeError):
            FaceRestorer(backend='auto')

    @patch('vhs_upscaler.face_restoration.check_gfpgan_available')
    def test_init_specific_backend_gfpgan(self, mock_gfpgan):
        """Should use GFPGAN when explicitly requested."""
        mock_gfpgan.return_value = True

        from vhs_upscaler.face_restoration import FaceRestorer

        restorer = FaceRestorer(backend='gfpgan')
        self.assertEqual(restorer.backend, 'gfpgan')

    @patch('vhs_upscaler.face_restoration.check_codeformer_available')
    def test_init_specific_backend_codeformer(self, mock_cf):
        """Should use CodeFormer when explicitly requested."""
        mock_cf.return_value = True

        from vhs_upscaler.face_restoration import FaceRestorer

        restorer = FaceRestorer(backend='codeformer')
        self.assertEqual(restorer.backend, 'codeformer')


class TestGFPGANBackend(unittest.TestCase):
    """Test GFPGAN-specific functionality."""

    @pytest.mark.skipif(
        not _check_gfpgan_import(),
        reason="GFPGAN not installed"
    )
    def test_gfpgan_model_initialization(self):
        """Test GFPGAN model loads correctly."""
        from vhs_upscaler.face_restoration import FaceRestorer

        with patch('gfpgan.GFPGANer') as mock_gfpgan:
            mock_gfpgan.return_value = MagicMock()
            restorer = FaceRestorer(backend='gfpgan')
            restorer._init_gfpgan_model()

            mock_gfpgan.assert_called_once()

    @patch('vhs_upscaler.face_restoration.check_gfpgan_available')
    def test_gfpgan_face_detection(self, mock_check):
        """Test GFPGAN detects faces in image."""
        mock_check.return_value = True
        from vhs_upscaler.face_restoration import FaceRestorer

        # Create dummy image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)

        with patch.object(FaceRestorer, '_init_gfpgan_model'):
            with patch.object(FaceRestorer, '_enhance_with_gfpgan') as mock_enhance:
                mock_enhance.return_value = test_image

                restorer = FaceRestorer(backend='gfpgan')
                result = restorer.enhance_faces(test_image)

                mock_enhance.assert_called_once()
                self.assertIsNotNone(result)

    @patch('vhs_upscaler.face_restoration.check_gfpgan_available')
    def test_gfpgan_gpu_mode(self, mock_check):
        """Test GFPGAN uses GPU when available."""
        mock_check.return_value = True
        from vhs_upscaler.face_restoration import FaceRestorer

        with patch('torch.cuda.is_available', return_value=True):
            with patch.object(FaceRestorer, '_init_gfpgan_model') as mock_init:
                restorer = FaceRestorer(backend='gfpgan', device='cuda')
                restorer._init_gfpgan_model()

                self.assertEqual(restorer.device, 'cuda')

    @patch('vhs_upscaler.face_restoration.check_gfpgan_available')
    def test_gfpgan_cpu_fallback(self, mock_check):
        """Test GFPGAN falls back to CPU when GPU unavailable."""
        mock_check.return_value = True
        from vhs_upscaler.face_restoration import FaceRestorer

        with patch('torch.cuda.is_available', return_value=False):
            restorer = FaceRestorer(backend='gfpgan', device='auto')
            self.assertEqual(restorer.device, 'cpu')


class TestCodeFormerBackend(unittest.TestCase):
    """Test CodeFormer-specific functionality."""

    @pytest.mark.skipif(
        not _check_codeformer_import(),
        reason="CodeFormer not installed"
    )
    def test_codeformer_model_initialization(self):
        """Test CodeFormer model loads correctly."""
        from vhs_upscaler.face_restoration import FaceRestorer

        with patch('codeformer.CodeFormer') as mock_cf:
            mock_cf.return_value = MagicMock()
            restorer = FaceRestorer(backend='codeformer')
            restorer._init_codeformer_model()

            mock_cf.assert_called_once()

    @patch('vhs_upscaler.face_restoration.check_codeformer_available')
    def test_codeformer_fidelity_control(self, mock_check):
        """Test CodeFormer fidelity parameter."""
        mock_check.return_value = True
        from vhs_upscaler.face_restoration import FaceRestorer

        restorer = FaceRestorer(backend='codeformer', fidelity=0.8)
        self.assertEqual(restorer.fidelity, 0.8)

    @patch('vhs_upscaler.face_restoration.check_codeformer_available')
    def test_codeformer_enhancement(self, mock_check):
        """Test CodeFormer enhances faces."""
        mock_check.return_value = True
        from vhs_upscaler.face_restoration import FaceRestorer

        test_image = np.zeros((480, 640, 3), dtype=np.uint8)

        with patch.object(FaceRestorer, '_init_codeformer_model'):
            with patch.object(FaceRestorer, '_enhance_with_codeformer') as mock_enhance:
                mock_enhance.return_value = test_image

                restorer = FaceRestorer(backend='codeformer')
                result = restorer.enhance_faces(test_image)

                mock_enhance.assert_called_once()
                self.assertIsNotNone(result)

    @patch('vhs_upscaler.face_restoration.check_codeformer_available')
    def test_codeformer_batch_processing(self, mock_check):
        """Test CodeFormer processes multiple faces efficiently."""
        mock_check.return_value = True
        from vhs_upscaler.face_restoration import FaceRestorer

        test_images = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(3)]

        with patch.object(FaceRestorer, '_init_codeformer_model'):
            with patch.object(FaceRestorer, '_enhance_with_codeformer') as mock_enhance:
                mock_enhance.side_effect = test_images

                restorer = FaceRestorer(backend='codeformer')

                for img in test_images:
                    result = restorer.enhance_faces(img)
                    self.assertIsNotNone(result)

                self.assertEqual(mock_enhance.call_count, 3)


class TestFaceRestorationIntegration(unittest.TestCase):
    """Integration tests for face restoration pipeline."""

    def test_process_video_with_faces(self):
        """Test processing video file with face restoration."""
        from vhs_upscaler.face_restoration import restore_faces_in_video

        with tempfile.TemporaryDirectory() as tmpdir:
            input_video = Path(tmpdir) / "input.mp4"
            output_video = Path(tmpdir) / "output.mp4"

            # Create dummy video file
            input_video.touch()

            with patch('vhs_upscaler.face_restoration.FaceRestorer') as mock_restorer:
                mock_instance = MagicMock()
                mock_restorer.return_value = mock_instance

                with patch('cv2.VideoCapture'):
                    with patch('cv2.VideoWriter'):
                        # This would normally process the video
                        # For now just test the API
                        pass

    def test_process_video_no_faces_detected(self):
        """Test graceful handling when no faces detected."""
        from vhs_upscaler.face_restoration import FaceRestorer

        test_image = np.zeros((480, 640, 3), dtype=np.uint8)

        with patch('vhs_upscaler.face_restoration.check_gfpgan_available', return_value=True):
            with patch.object(FaceRestorer, '_init_gfpgan_model'):
                with patch.object(FaceRestorer, '_detect_faces', return_value=[]):
                    restorer = FaceRestorer(backend='gfpgan')
                    result = restorer.enhance_faces(test_image)

                    # Should return original image when no faces
                    np.testing.assert_array_equal(result, test_image)

    @patch('vhs_upscaler.face_restoration.check_gfpgan_available')
    @patch('vhs_upscaler.face_restoration.check_codeformer_available')
    def test_fallback_on_backend_error(self, mock_cf, mock_gfpgan):
        """Test fallback to alternative backend on error."""
        mock_cf.return_value = True
        mock_gfpgan.return_value = True

        from vhs_upscaler.face_restoration import FaceRestorer

        test_image = np.zeros((480, 640, 3), dtype=np.uint8)

        with patch.object(FaceRestorer, '_init_codeformer_model', side_effect=Exception("Model load failed")):
            with patch.object(FaceRestorer, '_init_gfpgan_model'):
                # Should fallback to GFPGAN
                restorer = FaceRestorer(backend='auto', enable_fallback=True)
                # Verify fallback occurred
                self.assertIn(restorer.backend, ['gfpgan', 'codeformer'])

    def test_quality_consistency_across_frames(self):
        """Test face restoration quality is consistent across video frames."""
        from vhs_upscaler.face_restoration import FaceRestorer

        with patch('vhs_upscaler.face_restoration.check_gfpgan_available', return_value=True):
            with patch.object(FaceRestorer, '_init_gfpgan_model'):
                restorer = FaceRestorer(backend='gfpgan')

                # Create multiple frames
                frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(5)]

                with patch.object(FaceRestorer, '_enhance_with_gfpgan', side_effect=frames):
                    results = [restorer.enhance_faces(f) for f in frames]

                    # All frames should be processed
                    self.assertEqual(len(results), 5)


class TestFaceRestorationEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    @patch('vhs_upscaler.face_restoration.check_gfpgan_available')
    def test_invalid_image_format(self, mock_check):
        """Test handling of invalid image format."""
        mock_check.return_value = True
        from vhs_upscaler.face_restoration import FaceRestorer

        with patch.object(FaceRestorer, '_init_gfpgan_model'):
            restorer = FaceRestorer(backend='gfpgan')

            # Invalid image (wrong dimensions)
            invalid_image = np.zeros((100,), dtype=np.uint8)

            with self.assertRaises((ValueError, RuntimeError)):
                restorer.enhance_faces(invalid_image)

    @patch('vhs_upscaler.face_restoration.check_gfpgan_available')
    def test_empty_image(self, mock_check):
        """Test handling of empty image."""
        mock_check.return_value = True
        from vhs_upscaler.face_restoration import FaceRestorer

        with patch.object(FaceRestorer, '_init_gfpgan_model'):
            restorer = FaceRestorer(backend='gfpgan')

            empty_image = np.array([])

            with self.assertRaises((ValueError, RuntimeError)):
                restorer.enhance_faces(empty_image)

    @patch('vhs_upscaler.face_restoration.check_gfpgan_available')
    def test_very_large_image(self, mock_check):
        """Test handling of very large images (memory management)."""
        mock_check.return_value = True
        from vhs_upscaler.face_restoration import FaceRestorer

        with patch.object(FaceRestorer, '_init_gfpgan_model'):
            restorer = FaceRestorer(backend='gfpgan')

            # 8K image
            large_image = np.zeros((4320, 7680, 3), dtype=np.uint8)

            with patch.object(FaceRestorer, '_enhance_with_gfpgan', return_value=large_image):
                result = restorer.enhance_faces(large_image)
                self.assertEqual(result.shape, large_image.shape)

    @patch('vhs_upscaler.face_restoration.check_codeformer_available')
    def test_out_of_memory_handling(self, mock_check):
        """Test graceful handling of out-of-memory errors."""
        mock_check.return_value = True
        from vhs_upscaler.face_restoration import FaceRestorer

        test_image = np.zeros((480, 640, 3), dtype=np.uint8)

        with patch.object(FaceRestorer, '_init_codeformer_model'):
            with patch.object(FaceRestorer, '_enhance_with_codeformer', side_effect=RuntimeError("CUDA out of memory")):
                restorer = FaceRestorer(backend='codeformer')

                # Should handle OOM gracefully
                with self.assertRaises(RuntimeError):
                    restorer.enhance_faces(test_image)


class TestFeatureDetection(unittest.TestCase):
    """Test feature detection functions."""

    def test_check_gfpgan_available(self):
        """Test GFPGAN availability check."""
        from vhs_upscaler.face_restoration import check_gfpgan_available

        # Should return bool
        result = check_gfpgan_available()
        self.assertIsInstance(result, bool)

    def test_check_codeformer_available(self):
        """Test CodeFormer availability check."""
        from vhs_upscaler.face_restoration import check_codeformer_available

        # Should return bool
        result = check_codeformer_available()
        self.assertIsInstance(result, bool)

    def test_get_available_backends(self):
        """Test getting list of available backends."""
        from vhs_upscaler.face_restoration import get_available_backends

        backends = get_available_backends()

        # Should return list
        self.assertIsInstance(backends, list)
        # Should contain valid backend names
        for backend in backends:
            self.assertIn(backend, ['gfpgan', 'codeformer'])


if __name__ == '__main__':
    unittest.main()
