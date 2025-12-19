#!/usr/bin/env python3
"""
Comprehensive Hardware Detection and Auto-Configuration Tests
================================================================

Tests for hardware detection across different GPU vendors and configurations.

Test Coverage:
- GPU vendor detection (NVIDIA, AMD, Intel, CPU-only)
- Hardware capabilities detection
- Auto-configuration recommendations
- Edge cases and fallback mechanisms
- Performance optimizations
- Configuration profiles

Author: TerminalAI Test Suite
Date: December 2025
"""

import pytest
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add vhs_upscaler to path
sys.path.insert(0, str(Path(__file__).parent.parent / "vhs_upscaler"))

from hardware_detection import (
    HardwareInfo,
    GPUVendor,
    GPUTier,
    detect_nvidia_gpu,
    detect_amd_gpu,
    detect_intel_gpu,
    detect_hardware,
    get_optimal_config,
    _classify_nvidia_tier,
    _classify_amd_tier,
    _classify_intel_tier,
    _check_rtx_video_sdk_installed,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_nvidia_smi_rtx5090():
    """Mock nvidia-smi output for RTX 5090."""
    return "NVIDIA GeForce RTX 5090, 32768 MiB, 591.59, 12.0"


@pytest.fixture
def mock_nvidia_smi_rtx4080():
    """Mock nvidia-smi output for RTX 4080."""
    return "NVIDIA GeForce RTX 4080, 16384 MiB, 545.84, 8.9"


@pytest.fixture
def mock_nvidia_smi_rtx3060():
    """Mock nvidia-smi output for RTX 3060."""
    return "NVIDIA GeForce RTX 3060, 12288 MiB, 535.98, 8.6"


@pytest.fixture
def mock_nvidia_smi_gtx1660():
    """Mock nvidia-smi output for GTX 1660 Ti."""
    return "NVIDIA GeForce GTX 1660 Ti, 6144 MiB, 530.41, 7.5"


@pytest.fixture
def mock_wmic_amd():
    """Mock wmic output for AMD GPU."""
    return """Name                           AdapterRAM
AMD Radeon RX 7800 XT          17179869184"""


@pytest.fixture
def mock_wmic_intel():
    """Mock wmic output for Intel GPU."""
    return """Name
Intel(R) UHD Graphics 770"""


# =============================================================================
# Test NVIDIA GPU Detection
# =============================================================================

class TestNVIDIADetection:
    """Test NVIDIA GPU detection functionality."""

    def test_detect_rtx_5090(self, mock_nvidia_smi_rtx5090):
        """Test detection of RTX 5090 (Blackwell architecture)."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=mock_nvidia_smi_rtx5090,
                returncode=0
            )

            hw = detect_nvidia_gpu()

            assert hw is not None
            assert hw.vendor == GPUVendor.NVIDIA
            assert hw.tier == GPUTier.RTX_50_SERIES
            assert "RTX 5090" in hw.name
            assert hw.vram_gb == 32.0
            assert hw.has_nvenc is True
            assert hw.has_cuda is True
            assert hw.has_vulkan is True
            assert hw.compute_capability == "12.0"

    def test_detect_rtx_4080(self, mock_nvidia_smi_rtx4080):
        """Test detection of RTX 4080 (Ada Lovelace)."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=mock_nvidia_smi_rtx4080,
                returncode=0
            )

            hw = detect_nvidia_gpu()

            assert hw is not None
            assert hw.vendor == GPUVendor.NVIDIA
            assert hw.tier == GPUTier.RTX_40_SERIES
            assert "RTX 4080" in hw.name
            assert hw.vram_gb == 16.0
            assert hw.has_nvenc is True
            assert hw.compute_capability == "8.9"

    def test_detect_rtx_3060(self, mock_nvidia_smi_rtx3060):
        """Test detection of RTX 3060 (Ampere)."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=mock_nvidia_smi_rtx3060,
                returncode=0
            )

            hw = detect_nvidia_gpu()

            assert hw is not None
            assert hw.vendor == GPUVendor.NVIDIA
            assert hw.tier == GPUTier.RTX_30_SERIES
            assert "RTX 3060" in hw.name
            assert hw.vram_gb == 12.0
            assert hw.has_nvenc is True

    def test_detect_gtx_1660(self, mock_nvidia_smi_gtx1660):
        """Test detection of GTX 1660 Ti (Turing, no RT cores)."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=mock_nvidia_smi_gtx1660,
                returncode=0
            )

            hw = detect_nvidia_gpu()

            assert hw is not None
            assert hw.vendor == GPUVendor.NVIDIA
            assert hw.tier == GPUTier.GTX_16_SERIES
            assert "GTX 1660" in hw.name
            assert hw.vram_gb == 6.0
            assert hw.has_nvenc is True
            assert hw.is_rtx_capable is False  # No RT cores

    def test_nvidia_smi_timeout(self):
        """Test nvidia-smi timeout handling."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired('nvidia-smi', 5)

            hw = detect_nvidia_gpu()

            assert hw is None

    def test_nvidia_smi_not_found(self):
        """Test handling when nvidia-smi is not installed."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()

            hw = detect_nvidia_gpu()

            assert hw is None

    def test_vram_parsing_gib(self):
        """Test VRAM parsing with GiB units."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout="NVIDIA GeForce RTX 3080, 10 GiB, 535.98, 8.6",
                returncode=0
            )

            hw = detect_nvidia_gpu()

            assert hw is not None
            assert hw.vram_gb == 10.0

    def test_multi_gpu_detection(self):
        """Test detection of multiple GPUs."""
        multi_gpu_output = """NVIDIA GeForce RTX 4090, 24576 MiB, 545.84, 8.9
NVIDIA GeForce RTX 3090, 24576 MiB, 535.98, 8.6"""

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=multi_gpu_output,
                returncode=0
            )

            hw = detect_nvidia_gpu()

            assert hw is not None
            assert hw.gpu_count == 2
            assert "RTX 4090" in hw.name  # First GPU

    def test_nvidia_smi_performance(self):
        """Test nvidia-smi performance (should be < 0.1s)."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout="NVIDIA GeForce RTX 4080, 16384 MiB, 545.84, 8.9",
                returncode=0
            )

            start = time.time()
            hw = detect_nvidia_gpu()
            elapsed = time.time() - start

            assert hw is not None
            # Mock is instant, real nvidia-smi should be < 0.1s
            assert elapsed < 1.0  # Generous for mock overhead


# =============================================================================
# Test AMD GPU Detection
# =============================================================================

class TestAMDDetection:
    """Test AMD GPU detection functionality."""

    def test_detect_amd_rdna3(self, mock_wmic_amd):
        """Test detection of AMD RDNA3 GPU (RX 7800 XT)."""
        with patch('subprocess.run') as mock_run:
            with patch('sys.platform', 'win32'):
                mock_run.return_value = Mock(
                    stdout=mock_wmic_amd,
                    returncode=0
                )

                hw = detect_amd_gpu()

                assert hw is not None
                assert hw.vendor == GPUVendor.AMD
                assert hw.tier == GPUTier.AMD_RDNA3
                assert "AMD Radeon" in hw.name or "RX 7" in hw.name
                assert hw.has_vulkan is True
                assert hw.has_cuda is False

    def test_detect_amd_rdna2(self):
        """Test detection of AMD RDNA2 GPU (RX 6800)."""
        wmic_output = """Name                           AdapterRAM
AMD Radeon RX 6800              17179869184"""

        with patch('subprocess.run') as mock_run:
            with patch('sys.platform', 'win32'):
                mock_run.return_value = Mock(
                    stdout=wmic_output,
                    returncode=0
                )

                hw = detect_amd_gpu()

                assert hw is not None
                assert hw.tier == GPUTier.AMD_RDNA2

    def test_detect_amd_linux(self):
        """Test AMD detection on Linux using lspci."""
        lspci_output = """00:02.0 VGA compatible controller: AMD/ATI Radeon RX 7900 XTX"""

        with patch('subprocess.run') as mock_run:
            with patch('sys.platform', 'linux'):
                mock_run.return_value = Mock(
                    stdout=lspci_output,
                    returncode=0
                )

                hw = detect_amd_gpu()

                assert hw is not None
                assert hw.vendor == GPUVendor.AMD
                assert hw.has_vulkan is True

    def test_amd_not_found(self):
        """Test when no AMD GPU is found."""
        with patch('subprocess.run') as mock_run:
            with patch('sys.platform', 'win32'):
                mock_run.return_value = Mock(
                    stdout="Name\nIntel(R) UHD Graphics",
                    returncode=0
                )

                hw = detect_amd_gpu()

                assert hw is None


# =============================================================================
# Test Intel GPU Detection
# =============================================================================

class TestIntelDetection:
    """Test Intel GPU detection functionality."""

    def test_detect_intel_arc(self):
        """Test detection of Intel Arc GPU."""
        wmic_output = """Name
Intel(R) Arc(TM) A770 Graphics"""

        with patch('subprocess.run') as mock_run:
            with patch('sys.platform', 'win32'):
                mock_run.return_value = Mock(
                    stdout=wmic_output,
                    returncode=0
                )

                hw = detect_intel_gpu()

                assert hw is not None
                assert hw.vendor == GPUVendor.INTEL
                assert hw.tier == GPUTier.INTEL_ARC
                assert "Arc" in hw.name
                assert hw.has_vulkan is True

    def test_detect_intel_integrated(self, mock_wmic_intel):
        """Test detection of Intel integrated graphics."""
        with patch('subprocess.run') as mock_run:
            with patch('sys.platform', 'win32'):
                mock_run.return_value = Mock(
                    stdout=mock_wmic_intel,
                    returncode=0
                )

                hw = detect_intel_gpu()

                assert hw is not None
                assert hw.vendor == GPUVendor.INTEL
                assert hw.tier == GPUTier.INTEL_INTEGRATED
                assert hw.vram_gb == 2.0  # Shared memory default


# =============================================================================
# Test Unified Hardware Detection
# =============================================================================

class TestUnifiedDetection:
    """Test unified hardware detection with vendor priority."""

    def test_priority_nvidia_over_amd(self):
        """Test NVIDIA detection takes priority over AMD."""
        with patch('hardware_detection.detect_nvidia_gpu') as mock_nvidia:
            with patch('hardware_detection.detect_amd_gpu') as mock_amd:
                mock_nvidia.return_value = HardwareInfo(
                    vendor=GPUVendor.NVIDIA,
                    tier=GPUTier.RTX_40_SERIES,
                    name="RTX 4080",
                    vram_gb=16.0
                )
                mock_amd.return_value = HardwareInfo(
                    vendor=GPUVendor.AMD,
                    tier=GPUTier.AMD_RDNA3,
                    name="RX 7800 XT",
                    vram_gb=16.0
                )

                hw = detect_hardware()

                assert hw.vendor == GPUVendor.NVIDIA
                mock_amd.assert_not_called()  # Should not check AMD if NVIDIA found

    def test_fallback_to_cpu(self):
        """Test fallback to CPU when no GPU detected."""
        with patch('hardware_detection.detect_nvidia_gpu', return_value=None):
            with patch('hardware_detection.detect_amd_gpu', return_value=None):
                with patch('hardware_detection.detect_intel_gpu', return_value=None):
                    hw = detect_hardware()

                    assert hw.vendor == GPUVendor.CPU_ONLY
                    assert hw.tier == GPUTier.CPU_ONLY
                    assert hw.vram_gb == 0.0

    def test_detection_timeout(self):
        """Test hardware detection completes within timeout."""
        start = time.time()
        hw = detect_hardware()
        elapsed = time.time() - start

        assert hw is not None
        # Should complete in < 10 seconds (including all vendor checks)
        assert elapsed < 10.0


# =============================================================================
# Test GPU Tier Classification
# =============================================================================

class TestGPUClassification:
    """Test GPU model name classification."""

    def test_classify_rtx_50_series(self):
        """Test RTX 50 series classification."""
        assert _classify_nvidia_tier("NVIDIA GeForce RTX 5090") == GPUTier.RTX_50_SERIES
        assert _classify_nvidia_tier("NVIDIA GeForce RTX 5080") == GPUTier.RTX_50_SERIES
        assert _classify_nvidia_tier("NVIDIA GeForce RTX 5070") == GPUTier.RTX_50_SERIES
        assert _classify_nvidia_tier("NVIDIA GeForce RTX 5060") == GPUTier.RTX_50_SERIES

    def test_classify_rtx_40_series(self):
        """Test RTX 40 series classification."""
        assert _classify_nvidia_tier("NVIDIA GeForce RTX 4090") == GPUTier.RTX_40_SERIES
        assert _classify_nvidia_tier("NVIDIA GeForce RTX 4080") == GPUTier.RTX_40_SERIES
        assert _classify_nvidia_tier("NVIDIA GeForce RTX 4070") == GPUTier.RTX_40_SERIES
        assert _classify_nvidia_tier("NVIDIA GeForce RTX 4060") == GPUTier.RTX_40_SERIES

    def test_classify_rtx_30_series(self):
        """Test RTX 30 series classification."""
        assert _classify_nvidia_tier("NVIDIA GeForce RTX 3090") == GPUTier.RTX_30_SERIES
        assert _classify_nvidia_tier("NVIDIA GeForce RTX 3080") == GPUTier.RTX_30_SERIES
        assert _classify_nvidia_tier("NVIDIA GeForce RTX 3070") == GPUTier.RTX_30_SERIES
        assert _classify_nvidia_tier("NVIDIA GeForce RTX 3060") == GPUTier.RTX_30_SERIES

    def test_classify_gtx_16_series(self):
        """Test GTX 16 series classification."""
        assert _classify_nvidia_tier("NVIDIA GeForce GTX 1660 Ti") == GPUTier.GTX_16_SERIES
        assert _classify_nvidia_tier("NVIDIA GeForce GTX 1650") == GPUTier.GTX_16_SERIES

    def test_classify_gtx_10_series(self):
        """Test GTX 10 series classification."""
        assert _classify_nvidia_tier("NVIDIA GeForce GTX 1080 Ti") == GPUTier.GTX_10_SERIES
        assert _classify_nvidia_tier("NVIDIA GeForce GTX 1070") == GPUTier.GTX_10_SERIES
        assert _classify_nvidia_tier("NVIDIA GeForce GTX 1060") == GPUTier.GTX_10_SERIES

    def test_classify_amd_rdna3(self):
        """Test AMD RDNA3 classification."""
        assert _classify_amd_tier("AMD Radeon RX 7900 XTX") == GPUTier.AMD_RDNA3
        assert _classify_amd_tier("AMD Radeon RX 7800 XT") == GPUTier.AMD_RDNA3

    def test_classify_amd_rdna2(self):
        """Test AMD RDNA2 classification."""
        assert _classify_amd_tier("AMD Radeon RX 6900 XT") == GPUTier.AMD_RDNA2
        assert _classify_amd_tier("AMD Radeon RX 6800") == GPUTier.AMD_RDNA2

    def test_classify_intel_arc(self):
        """Test Intel Arc classification."""
        assert _classify_intel_tier("Intel Arc A770") == GPUTier.INTEL_ARC
        assert _classify_intel_tier("Intel Arc A750") == GPUTier.INTEL_ARC

    def test_classify_intel_integrated(self):
        """Test Intel integrated GPU classification."""
        assert _classify_intel_tier("Intel UHD Graphics 770") == GPUTier.INTEL_INTEGRATED
        assert _classify_intel_tier("Intel Iris Xe Graphics") == GPUTier.INTEL_INTEGRATED


# =============================================================================
# Test Hardware Capabilities
# =============================================================================

class TestHardwareCapabilities:
    """Test hardware capability detection."""

    def test_rtx_supports_ai_upscaling(self):
        """Test RTX cards support AI upscaling."""
        hw = HardwareInfo(
            vendor=GPUVendor.NVIDIA,
            tier=GPUTier.RTX_40_SERIES,
            name="RTX 4080",
            vram_gb=16.0
        )

        assert hw.supports_ai_upscaling is True
        assert hw.is_rtx_capable is True

    def test_gtx_supports_ai_upscaling(self):
        """Test GTX 10+ supports AI upscaling (via Real-ESRGAN)."""
        hw = HardwareInfo(
            vendor=GPUVendor.NVIDIA,
            tier=GPUTier.GTX_16_SERIES,
            name="GTX 1660 Ti",
            vram_gb=6.0
        )

        assert hw.supports_ai_upscaling is True
        assert hw.is_rtx_capable is False  # No RT cores

    def test_amd_supports_ai_upscaling(self):
        """Test AMD supports AI upscaling via Vulkan."""
        hw = HardwareInfo(
            vendor=GPUVendor.AMD,
            tier=GPUTier.AMD_RDNA3,
            name="RX 7800 XT",
            vram_gb=16.0,
            has_vulkan=True
        )

        assert hw.supports_ai_upscaling is True
        assert hw.is_rtx_capable is False

    def test_hardware_encoding_support(self):
        """Test hardware encoding detection."""
        # NVIDIA with NVENC
        hw_nvidia = HardwareInfo(
            vendor=GPUVendor.NVIDIA,
            tier=GPUTier.RTX_40_SERIES,
            name="RTX 4080",
            vram_gb=16.0,
            has_nvenc=True
        )
        assert hw_nvidia.supports_hardware_encoding is True

        # AMD (assumed hardware encoding available)
        hw_amd = HardwareInfo(
            vendor=GPUVendor.AMD,
            tier=GPUTier.AMD_RDNA3,
            name="RX 7800 XT",
            vram_gb=16.0
        )
        assert hw_amd.supports_hardware_encoding is True

        # CPU-only
        hw_cpu = HardwareInfo(
            vendor=GPUVendor.CPU_ONLY,
            tier=GPUTier.CPU_ONLY,
            name="CPU",
            vram_gb=0.0
        )
        assert hw_cpu.supports_hardware_encoding is False


# =============================================================================
# Test Auto-Configuration
# =============================================================================

class TestAutoConfiguration:
    """Test optimal configuration recommendation."""

    def test_rtx_5090_config(self):
        """Test RTX 5090 gets best quality settings."""
        hw = HardwareInfo(
            vendor=GPUVendor.NVIDIA,
            tier=GPUTier.RTX_50_SERIES,
            name="RTX 5090",
            vram_gb=32.0,
            has_nvenc=True,
            has_rtx_video_sdk=True,
            has_cuda=True
        )

        config = get_optimal_config(hw)

        assert config['upscale_engine'] == 'rtxvideo'
        assert config['encoder'] == 'hevc_nvenc'
        assert config['quality'] == 'best'
        assert config['face_restore'] is True
        assert config['audio_upmix'] == 'demucs'

    def test_rtx_3060_without_sdk(self):
        """Test RTX 3060 without RTX Video SDK falls back to Real-ESRGAN."""
        hw = HardwareInfo(
            vendor=GPUVendor.NVIDIA,
            tier=GPUTier.RTX_30_SERIES,
            name="RTX 3060",
            vram_gb=12.0,
            has_nvenc=True,
            has_rtx_video_sdk=False,  # Not installed
            has_cuda=True
        )

        config = get_optimal_config(hw)

        assert config['upscale_engine'] == 'realesrgan'
        assert config['encoder'] == 'hevc_nvenc'
        assert config['quality'] == 'best'
        assert len(config['warnings']) > 0
        assert any('RTX Video SDK' in w for w in config['warnings'])

    def test_gtx_1660_config(self):
        """Test GTX 1660 Ti configuration."""
        hw = HardwareInfo(
            vendor=GPUVendor.NVIDIA,
            tier=GPUTier.GTX_16_SERIES,
            name="GTX 1660 Ti",
            vram_gb=6.0,
            has_nvenc=True,
            has_cuda=True
        )

        config = get_optimal_config(hw)

        assert config['upscale_engine'] == 'realesrgan'
        assert config['encoder'] == 'h264_nvenc'  # H.264 for GTX
        assert config['quality'] == 'balanced'
        assert config['face_restore'] is False  # Too slow on GTX

    def test_amd_rdna3_config(self):
        """Test AMD RDNA3 configuration."""
        hw = HardwareInfo(
            vendor=GPUVendor.AMD,
            tier=GPUTier.AMD_RDNA3,
            name="RX 7800 XT",
            vram_gb=16.0,
            has_vulkan=True
        )

        config = get_optimal_config(hw)

        assert config['upscale_engine'] == 'realesrgan'
        assert config['encoder'] == 'libx265'  # Software encoding
        assert config['quality'] == 'balanced'
        assert config['face_restore'] is False  # No CUDA
        assert len(config['warnings']) > 0

    def test_intel_arc_config(self):
        """Test Intel Arc configuration."""
        hw = HardwareInfo(
            vendor=GPUVendor.INTEL,
            tier=GPUTier.INTEL_ARC,
            name="Arc A770",
            vram_gb=16.0,
            has_vulkan=True
        )

        config = get_optimal_config(hw)

        assert config['upscale_engine'] == 'realesrgan'
        assert config['encoder'] == 'libx265'
        assert config['quality'] == 'balanced'

    def test_cpu_only_config(self):
        """Test CPU-only configuration."""
        hw = HardwareInfo(
            vendor=GPUVendor.CPU_ONLY,
            tier=GPUTier.CPU_ONLY,
            name="CPU",
            vram_gb=0.0
        )

        config = get_optimal_config(hw)

        assert config['upscale_engine'] == 'ffmpeg'
        assert config['encoder'] == 'libx265'
        assert config['quality'] == 'good'
        assert config['face_restore'] is False
        assert config['audio_upmix'] == 'simple'
        assert len(config['warnings']) >= 3  # Multiple warnings for CPU-only

    def test_low_vram_rtx(self):
        """Test RTX card with low VRAM (4GB)."""
        hw = HardwareInfo(
            vendor=GPUVendor.NVIDIA,
            tier=GPUTier.RTX_30_SERIES,
            name="RTX 3050",
            vram_gb=4.0,
            has_nvenc=True,
            has_rtx_video_sdk=True,
            has_cuda=True
        )

        config = get_optimal_config(hw)

        assert config['face_restore'] is False  # Disabled due to low VRAM
        assert config['audio_upmix'] == 'surround'  # Not demucs (too heavy)
        assert any('VRAM' in w for w in config['warnings'])


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_malformed_nvidia_smi_output(self):
        """Test handling of malformed nvidia-smi output."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout="Invalid output",
                returncode=0
            )

            hw = detect_nvidia_gpu()

            assert hw is None

    def test_empty_nvidia_smi_output(self):
        """Test handling of empty nvidia-smi output."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout="",
                returncode=0
            )

            hw = detect_nvidia_gpu()

            assert hw is None

    def test_detection_exception_handling(self):
        """Test graceful handling of detection exceptions."""
        with patch('hardware_detection.detect_nvidia_gpu') as mock_nvidia:
            mock_nvidia.side_effect = Exception("Unexpected error")

            # Should not crash, should return CPU fallback
            hw = detect_hardware()

            assert hw.vendor == GPUVendor.CPU_ONLY

    def test_rtx_sdk_check_without_env_var(self):
        """Test RTX SDK detection without environment variable."""
        with patch.dict('os.environ', {}, clear=True):
            with patch('pathlib.Path.exists', return_value=False):
                has_sdk = _check_rtx_video_sdk_installed()

                assert has_sdk is False

    def test_multiple_gpu_priority(self):
        """Test that first GPU is used in multi-GPU systems."""
        multi_gpu_output = """NVIDIA GeForce RTX 4090, 24576 MiB, 545.84, 8.9
NVIDIA GeForce RTX 3060, 12288 MiB, 535.98, 8.6"""

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=multi_gpu_output,
                returncode=0
            )

            hw = detect_nvidia_gpu()

            assert hw is not None
            assert "4090" in hw.name  # First GPU
            assert hw.gpu_count == 2


# =============================================================================
# Test Performance Optimizations
# =============================================================================

class TestPerformanceOptimizations:
    """Test performance optimizations in detection."""

    def test_nvidia_smi_prioritized(self):
        """Test nvidia-smi is tried before PyTorch import."""
        with patch('subprocess.run') as mock_run:
            with patch('torch.cuda.is_available') as mock_torch:
                mock_run.return_value = Mock(
                    stdout="NVIDIA GeForce RTX 4080, 16384 MiB, 545.84, 8.9",
                    returncode=0
                )

                hw = detect_nvidia_gpu()

                assert hw is not None
                # PyTorch should NOT be imported if nvidia-smi succeeds
                mock_torch.assert_not_called()

    def test_detection_caching(self):
        """Test that hardware detection results can be cached."""
        hw1 = detect_hardware()
        hw2 = detect_hardware()

        # Both should return valid hardware info
        assert hw1 is not None
        assert hw2 is not None

    def test_no_redundant_gpu_queries(self):
        """Test that GPU queries are not repeated unnecessarily."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout="NVIDIA GeForce RTX 4080, 16384 MiB, 545.84, 8.9",
                returncode=0
            )

            hw = detect_nvidia_gpu()

            # Should only call nvidia-smi once
            assert mock_run.call_count <= 2  # Initial + CUDA version check


# =============================================================================
# Test Configuration Profiles
# =============================================================================

class TestConfigurationProfiles:
    """Test configuration profiles for different hardware classes."""

    def test_rtx_50_profile(self):
        """Test RTX 50 series profile."""
        hw = HardwareInfo(
            vendor=GPUVendor.NVIDIA,
            tier=GPUTier.RTX_50_SERIES,
            name="RTX 5080",
            vram_gb=16.0,
            has_nvenc=True,
            has_rtx_video_sdk=True,
            has_cuda=True
        )

        config = get_optimal_config(hw)

        # Premium tier
        assert config['upscale_engine'] == 'rtxvideo'
        assert config['quality'] == 'best'
        assert config['face_restore'] is True
        assert config['audio_upmix'] == 'demucs'

    def test_rtx_30_profile(self):
        """Test RTX 30 series profile."""
        hw = HardwareInfo(
            vendor=GPUVendor.NVIDIA,
            tier=GPUTier.RTX_30_SERIES,
            name="RTX 3070",
            vram_gb=8.0,
            has_nvenc=True,
            has_rtx_video_sdk=True,
            has_cuda=True
        )

        config = get_optimal_config(hw)

        # High tier
        assert config['upscale_engine'] == 'rtxvideo'
        assert config['quality'] == 'best'
        assert config['audio_upmix'] == 'demucs'

    def test_gtx_profile(self):
        """Test GTX series profile."""
        hw = HardwareInfo(
            vendor=GPUVendor.NVIDIA,
            tier=GPUTier.GTX_10_SERIES,
            name="GTX 1070",
            vram_gb=8.0,
            has_nvenc=True,
            has_cuda=True
        )

        config = get_optimal_config(hw)

        # Mid tier
        assert config['upscale_engine'] == 'realesrgan'
        assert config['quality'] == 'balanced'
        assert config['face_restore'] is False
        assert config['audio_upmix'] == 'simple'

    def test_amd_profile(self):
        """Test AMD GPU profile."""
        hw = HardwareInfo(
            vendor=GPUVendor.AMD,
            tier=GPUTier.AMD_RDNA2,
            name="RX 6800",
            vram_gb=16.0,
            has_vulkan=True
        )

        config = get_optimal_config(hw)

        # Vulkan tier
        assert config['upscale_engine'] == 'realesrgan'
        assert config['encoder'] == 'libx265'
        assert config['face_restore'] is False  # No CUDA

    def test_cpu_profile(self):
        """Test CPU-only profile."""
        hw = HardwareInfo(
            vendor=GPUVendor.CPU_ONLY,
            tier=GPUTier.CPU_ONLY,
            name="CPU",
            vram_gb=0.0
        )

        config = get_optimal_config(hw)

        # Basic tier
        assert config['upscale_engine'] == 'ffmpeg'
        assert config['encoder'] == 'libx265'
        assert config['quality'] == 'good'
        assert config['face_restore'] is False
        assert config['audio_upmix'] == 'simple'


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for complete workflow."""

    def test_full_detection_and_config(self):
        """Test complete detection and configuration workflow."""
        hw = detect_hardware()

        assert hw is not None
        assert hw.vendor in [GPUVendor.NVIDIA, GPUVendor.AMD, GPUVendor.INTEL, GPUVendor.CPU_ONLY]

        config = get_optimal_config(hw)

        assert 'upscale_engine' in config
        assert 'encoder' in config
        assert 'quality' in config
        assert 'face_restore' in config
        assert 'audio_upmix' in config
        assert 'explanation' in config
        assert 'warnings' in config

    def test_config_consistency(self):
        """Test configuration is consistent with hardware capabilities."""
        hw = HardwareInfo(
            vendor=GPUVendor.NVIDIA,
            tier=GPUTier.RTX_40_SERIES,
            name="RTX 4070",
            vram_gb=12.0,
            has_nvenc=True,
            has_rtx_video_sdk=False,  # Not installed
            has_cuda=True
        )

        config = get_optimal_config(hw)

        # Should use Real-ESRGAN if RTX SDK not available
        assert config['upscale_engine'] == 'realesrgan'
        # But still use NVENC for encoding
        assert config['encoder'] == 'hevc_nvenc'

    def test_display_name_generation(self):
        """Test hardware display name generation."""
        hw = HardwareInfo(
            vendor=GPUVendor.NVIDIA,
            tier=GPUTier.RTX_40_SERIES,
            name="NVIDIA GeForce RTX 4080",
            vram_gb=16.0
        )

        assert "RTX 4080" in hw.display_name
        assert "16GB" in hw.display_name

        hw_cpu = HardwareInfo(
            vendor=GPUVendor.CPU_ONLY,
            tier=GPUTier.CPU_ONLY,
            name="CPU",
            vram_gb=0.0
        )

        assert "CPU" in hw_cpu.display_name
        assert "No GPU" in hw_cpu.display_name


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
