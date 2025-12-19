#!/usr/bin/env python3
"""
Tests for Installation Verification System
===========================================

Tests the verify_installation.py module and component verifiers.
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock

# Add parent directory and scripts/installation to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "installation"))

from verify_installation import (
    ComponentStatus,
    ComponentResult,
    VerificationReport,
    PythonVerifier,
    FFmpegVerifier,
    PyTorchVerifier,
    VapourSynthVerifier,
    GFPGANVerifier,
    CodeFormerVerifier,
    DeepFilterNetVerifier,
    AudioSRVerifier,
    DemucsVerifier,
    GPUVerifier,
    InstallationVerifier,
    get_available_features,
    check_component
)


class TestComponentResult(unittest.TestCase):
    """Test ComponentResult dataclass."""

    def test_create_basic_result(self):
        """Test creating basic component result."""
        result = ComponentResult(
            name="TestComponent",
            status=ComponentStatus.AVAILABLE,
            version="1.0.0"
        )

        self.assertEqual(result.name, "TestComponent")
        self.assertEqual(result.status, ComponentStatus.AVAILABLE)
        self.assertEqual(result.version, "1.0.0")
        self.assertTrue(result.is_available)
        self.assertFalse(result.is_partial)

    def test_result_with_details(self):
        """Test result with detailed information."""
        result = ComponentResult(
            name="TestComponent",
            status=ComponentStatus.PARTIAL,
            version="1.0.0",
            details={"key": "value"},
            suggestions=["Install missing dependency"],
            performance_notes=["GPU recommended"]
        )

        self.assertEqual(result.details["key"], "value")
        self.assertEqual(len(result.suggestions), 1)
        self.assertEqual(len(result.performance_notes), 1)
        self.assertTrue(result.is_partial)

    def test_unavailable_result(self):
        """Test unavailable component result."""
        result = ComponentResult(
            name="TestComponent",
            status=ComponentStatus.UNAVAILABLE,
            error_message="Component not found"
        )

        self.assertFalse(result.is_available)
        self.assertEqual(result.error_message, "Component not found")


class TestPythonVerifier(unittest.TestCase):
    """Test Python version verification."""

    def test_python_verification(self):
        """Test Python version check."""
        verifier = PythonVerifier(verbose=False)
        result = verifier.verify()

        self.assertEqual(result.name, "Python")
        # Should always have Python available when running tests
        self.assertIn(result.status, [ComponentStatus.AVAILABLE, ComponentStatus.PARTIAL])
        self.assertIsNotNone(result.version)
        self.assertIn("platform", result.details)


class TestFFmpegVerifier(unittest.TestCase):
    """Test FFmpeg verification."""

    @patch('subprocess.run')
    def test_ffmpeg_available(self, mock_run):
        """Test FFmpeg when available."""
        # Mock FFmpeg version output
        mock_version = Mock()
        mock_version.stdout = "ffmpeg version 6.0 Copyright (c) 2000-2023"
        mock_version.returncode = 0

        # Mock encoders output
        mock_encoders = Mock()
        mock_encoders.stdout = """
        V..... h264_nvenc           NVIDIA NVENC H.264 encoder
        V..... hevc_nvenc           NVIDIA NVENC hevc encoder
        V..... libx264              libx264 H.264
        V..... libx265              libx265 H.265
        """
        mock_encoders.returncode = 0

        # Mock filters output
        mock_filters = Mock()
        mock_filters.stdout = """
        ... yadif               Deinterlace
        ... hqdn3d              Denoise
        ... scale_cuda          CUDA scale
        """
        mock_filters.returncode = 0

        mock_run.side_effect = [mock_version, mock_encoders, mock_filters]

        verifier = FFmpegVerifier(verbose=False)
        result = verifier.verify()

        self.assertEqual(result.name, "FFmpeg")
        self.assertIn(result.status, [ComponentStatus.AVAILABLE, ComponentStatus.PARTIAL])
        self.assertIsNotNone(result.version)
        self.assertIn("available_encoders", result.details)
        self.assertIn("h264_nvenc", result.details["available_encoders"])

    @patch('subprocess.run')
    def test_ffmpeg_missing(self, mock_run):
        """Test FFmpeg when not installed."""
        mock_run.side_effect = FileNotFoundError()

        verifier = FFmpegVerifier(verbose=False)
        result = verifier.verify()

        self.assertEqual(result.status, ComponentStatus.UNAVAILABLE)
        self.assertGreater(len(result.suggestions), 0)


class TestPyTorchVerifier(unittest.TestCase):
    """Test PyTorch verification."""

    @patch('verify_installation.ComponentVerifier.verify')
    def test_pytorch_not_installed(self, mock_verify):
        """Test PyTorch when not installed."""
        verifier = PyTorchVerifier(verbose=False)

        # Mock import error
        with patch.dict('sys.modules', {'torch': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'torch'")):
                result = verifier.verify()

        # Result should indicate unavailable or error
        self.assertIn(result.status, [ComponentStatus.UNAVAILABLE, ComponentStatus.ERROR])

    def test_pytorch_import_real(self):
        """Test actual PyTorch import (may pass or fail based on installation)."""
        verifier = PyTorchVerifier(verbose=False)
        result = verifier.verify()

        # Should return a valid result regardless of installation status
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "PyTorch")
        self.assertIsInstance(result.status, ComponentStatus)


class TestVapourSynthVerifier(unittest.TestCase):
    """Test VapourSynth verification."""

    def test_vapoursynth_verification(self):
        """Test VapourSynth check."""
        verifier = VapourSynthVerifier(verbose=False)
        result = verifier.verify()

        self.assertEqual(result.name, "VapourSynth")
        self.assertIsInstance(result.status, ComponentStatus)

        # If unavailable, should have suggestions
        if result.status == ComponentStatus.UNAVAILABLE:
            self.assertGreater(len(result.suggestions), 0)


class TestGPUVerifier(unittest.TestCase):
    """Test GPU detection."""

    @patch('subprocess.run')
    def test_nvidia_gpu_detected(self, mock_run):
        """Test NVIDIA GPU detection."""
        mock_result = Mock()
        mock_result.stdout = "NVIDIA GeForce RTX 3080, 10240 MiB, 535.98, 12.2"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        verifier = GPUVerifier(verbose=False)
        result = verifier.verify()

        self.assertEqual(result.name, "GPU")
        self.assertEqual(result.status, ComponentStatus.AVAILABLE)
        self.assertIn("nvidia_gpus", result.details)

    @patch('subprocess.run')
    def test_no_gpu(self, mock_run):
        """Test when no GPU is detected."""
        mock_run.side_effect = FileNotFoundError()

        verifier = GPUVerifier(verbose=False)
        result = verifier.verify()

        self.assertEqual(result.name, "GPU")
        # Should be unavailable or partial
        self.assertIn(result.status, [ComponentStatus.UNAVAILABLE, ComponentStatus.PARTIAL])


class TestVerificationReport(unittest.TestCase):
    """Test verification report generation."""

    def test_create_report(self):
        """Test creating verification report."""
        system_info = {
            "platform": "test-platform",
            "python_version": "3.10.0"
        }

        components = {
            "Python": ComponentResult(
                name="Python",
                status=ComponentStatus.AVAILABLE,
                version="3.10.0"
            )
        }

        feature_availability = {
            "basic_video_processing": True,
            "gpu_acceleration": False
        }

        report = VerificationReport(
            system_info=system_info,
            components=components,
            feature_availability=feature_availability,
            warnings=["Test warning"],
            errors=[],
            recommendations=["Test recommendation"]
        )

        self.assertEqual(len(report.components), 1)
        self.assertEqual(len(report.warnings), 1)
        self.assertEqual(len(report.recommendations), 1)

    def test_report_to_dict(self):
        """Test converting report to dictionary."""
        system_info = {"platform": "test"}
        components = {
            "Test": ComponentResult(
                name="Test",
                status=ComponentStatus.AVAILABLE
            )
        }

        report = VerificationReport(
            system_info=system_info,
            components=components,
            feature_availability={},
            warnings=[],
            errors=[],
            recommendations=[]
        )

        report_dict = report.to_dict()

        self.assertIn("system_info", report_dict)
        self.assertIn("components", report_dict)
        self.assertIn("feature_availability", report_dict)

    def test_report_to_json(self, tmp_path=None):
        """Test saving report as JSON."""
        if tmp_path is None:
            import tempfile
            tmp_dir = tempfile.mkdtemp()
            tmp_path = Path(tmp_dir)

        system_info = {"platform": "test"}
        components = {}

        report = VerificationReport(
            system_info=system_info,
            components=components,
            feature_availability={},
            warnings=[],
            errors=[],
            recommendations=[]
        )

        json_file = tmp_path / "test_report.json"
        report.to_json(json_file)

        self.assertTrue(json_file.exists())

        # Verify JSON is valid
        with open(json_file) as f:
            data = json.load(f)
            self.assertIn("system_info", data)


class TestInstallationVerifier(unittest.TestCase):
    """Test main installation verifier."""

    def test_get_system_info(self):
        """Test system information collection."""
        verifier = InstallationVerifier(verbose=False)
        info = verifier.get_system_info()

        self.assertIn("platform", info)
        self.assertIn("python_version", info)
        self.assertIn("system", info)

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        verifier = InstallationVerifier(verbose=False)

        components = {
            "FFmpeg": ComponentResult(
                name="FFmpeg",
                status=ComponentStatus.UNAVAILABLE
            ),
            "PyTorch": ComponentResult(
                name="PyTorch",
                status=ComponentStatus.AVAILABLE,
                version="2.0.0"
            )
        }

        features = {
            "basic_video_processing": False,
            "gpu_acceleration": True
        }

        recommendations = verifier._generate_recommendations(components, features)

        # Should recommend installing FFmpeg
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any("FFmpeg" in rec for rec in recommendations))


class TestFeatureDetectionAPI(unittest.TestCase):
    """Test feature detection API functions."""

    def test_get_available_features(self):
        """Test get_available_features function."""
        features = get_available_features()

        self.assertIsInstance(features, dict)
        self.assertIn("basic_video_processing", features)
        self.assertIn("gpu_acceleration", features)

        # Values should be boolean
        for value in features.values():
            self.assertIsInstance(value, bool)

    def test_check_component_valid(self):
        """Test checking valid component."""
        result = check_component("python")

        self.assertEqual(result.name, "Python")
        self.assertIsInstance(result.status, ComponentStatus)

    def test_check_component_invalid(self):
        """Test checking invalid component."""
        result = check_component("nonexistent_component")

        self.assertEqual(result.status, ComponentStatus.ERROR)
        self.assertIn("Unknown component", result.error_message)


class TestIntegration(unittest.TestCase):
    """Integration tests for full verification flow."""

    def test_full_verification_runs(self):
        """Test that full verification completes without crashing."""
        verifier = InstallationVerifier(verbose=False)

        try:
            report = verifier.verify_all(quick=True)
            self.assertIsInstance(report, VerificationReport)
            self.assertGreater(len(report.components), 0)
        except Exception as e:
            self.fail(f"Full verification should not raise exception: {e}")

    def test_component_verifiers_complete(self):
        """Test that all verifiers complete successfully."""
        verifiers = [
            ("Python", PythonVerifier(verbose=False)),
            ("FFmpeg", FFmpegVerifier(verbose=False)),
            ("GPU", GPUVerifier(verbose=False)),
            ("PyTorch", PyTorchVerifier(verbose=False)),
        ]

        for name, verifier in verifiers:
            try:
                result = verifier.verify()
                self.assertIsInstance(result, ComponentResult)
                self.assertEqual(result.name, name)
            except Exception as e:
                self.fail(f"{name} verifier should not raise exception: {e}")


class TestErrorHandling(unittest.TestCase):
    """Test error handling in verification."""

    def test_verifier_handles_exceptions(self):
        """Test that verifiers handle exceptions gracefully."""
        verifier = PyTorchVerifier(verbose=False)

        # Even if import fails, should return ERROR status, not crash
        try:
            result = verifier.verify()
            self.assertIsInstance(result, ComponentResult)
        except Exception as e:
            self.fail(f"Verifier should handle exceptions internally: {e}")

    def test_missing_subprocess_command(self):
        """Test handling of missing external commands."""
        with patch('subprocess.run', side_effect=FileNotFoundError()):
            verifier = FFmpegVerifier(verbose=False)
            result = verifier.verify()

            self.assertEqual(result.status, ComponentStatus.UNAVAILABLE)
            self.assertIsNotNone(result.error_message)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
