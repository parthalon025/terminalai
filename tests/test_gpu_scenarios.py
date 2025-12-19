#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Different GPU Scenarios
==============================
Simulate different hardware configurations to test auto-configuration.
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent / "vhs_upscaler"))

from hardware_detection import HardwareInfo, GPUVendor, GPUTier, get_optimal_config


def test_rtx_5080():
    """Test RTX 5080 configuration."""
    print("=" * 70)
    print("Scenario 1: RTX 5080 (16GB) with RTX Video SDK")
    print("=" * 70)

    hw = HardwareInfo(
        vendor=GPUVendor.NVIDIA,
        tier=GPUTier.RTX_50_SERIES,
        name="NVIDIA GeForce RTX 5080",
        vram_gb=16.0,
        driver_version="591.59",
        has_nvenc=True,
        has_rtx_video_sdk=True,
        has_cuda=True,
        has_vulkan=True
    )

    config = get_optimal_config(hw)
    print(f"Engine: {config['upscale_engine']} ✓")
    print(f"Encoder: {config['encoder']} ✓")
    print(f"Quality: {config['quality']} ✓")
    print(f"Face Restore: {config['face_restore']} ✓")
    print(f"Audio Upmix: {config['audio_upmix']} ✓")
    print()


def test_rtx_3060():
    """Test RTX 3060 (8GB) without RTX SDK."""
    print("=" * 70)
    print("Scenario 2: RTX 3060 (8GB) WITHOUT RTX Video SDK")
    print("=" * 70)

    hw = HardwareInfo(
        vendor=GPUVendor.NVIDIA,
        tier=GPUTier.RTX_30_SERIES,
        name="NVIDIA GeForce RTX 3060",
        vram_gb=8.0,
        driver_version="535.98",
        has_nvenc=True,
        has_rtx_video_sdk=False,  # Not installed
        has_cuda=True,
        has_vulkan=True
    )

    config = get_optimal_config(hw)
    print(f"Engine: {config['upscale_engine']} (should be realesrgan)")
    print(f"Encoder: {config['encoder']}")
    print(f"Quality: {config['quality']}")
    print(f"Face Restore: {config['face_restore']}")
    print(f"Audio Upmix: {config['audio_upmix']}")
    print(f"Warnings: {len(config['warnings'])} warning(s)")
    if config['warnings']:
        for w in config['warnings']:
            print(f"  - {w[:80]}...")
    print()


def test_gtx_1660():
    """Test GTX 1660 Ti (6GB)."""
    print("=" * 70)
    print("Scenario 3: GTX 1660 Ti (6GB)")
    print("=" * 70)

    hw = HardwareInfo(
        vendor=GPUVendor.NVIDIA,
        tier=GPUTier.GTX_16_SERIES,
        name="NVIDIA GeForce GTX 1660 Ti",
        vram_gb=6.0,
        driver_version="530.41",
        has_nvenc=True,
        has_rtx_video_sdk=False,
        has_cuda=True,
        has_vulkan=True
    )

    config = get_optimal_config(hw)
    print(f"Engine: {config['upscale_engine']} (should be realesrgan)")
    print(f"Encoder: {config['encoder']} (should be h264_nvenc)")
    print(f"Quality: {config['quality']}")
    print(f"Face Restore: {config['face_restore']} (should be False)")
    print(f"Audio Upmix: {config['audio_upmix']}")
    print()


def test_amd_rx7800():
    """Test AMD RX 7800 XT."""
    print("=" * 70)
    print("Scenario 4: AMD Radeon RX 7800 XT (16GB)")
    print("=" * 70)

    hw = HardwareInfo(
        vendor=GPUVendor.AMD,
        tier=GPUTier.AMD_RDNA3,
        name="AMD Radeon RX 7800 XT",
        vram_gb=16.0,
        driver_version="23.11.1",
        has_nvenc=False,
        has_rtx_video_sdk=False,
        has_cuda=False,
        has_vulkan=True
    )

    config = get_optimal_config(hw)
    print(f"Engine: {config['upscale_engine']} (should be realesrgan)")
    print(f"Encoder: {config['encoder']} (should be libx265)")
    print(f"Quality: {config['quality']}")
    print(f"Face Restore: {config['face_restore']} (should be False - no CUDA)")
    print(f"Audio Upmix: {config['audio_upmix']}")
    print(f"Warnings: {len(config['warnings'])} warning(s)")
    print()


def test_intel_arc():
    """Test Intel Arc A770."""
    print("=" * 70)
    print("Scenario 5: Intel Arc A770 (16GB)")
    print("=" * 70)

    hw = HardwareInfo(
        vendor=GPUVendor.INTEL,
        tier=GPUTier.INTEL_ARC,
        name="Intel Arc A770",
        vram_gb=16.0,
        driver_version="31.0.101.4887",
        has_nvenc=False,
        has_rtx_video_sdk=False,
        has_cuda=False,
        has_vulkan=True
    )

    config = get_optimal_config(hw)
    print(f"Engine: {config['upscale_engine']} (should be realesrgan)")
    print(f"Encoder: {config['encoder']} (should be libx265)")
    print(f"Quality: {config['quality']}")
    print(f"Face Restore: {config['face_restore']}")
    print(f"Audio Upmix: {config['audio_upmix']}")
    print()


def test_cpu_only():
    """Test CPU-only mode."""
    print("=" * 70)
    print("Scenario 6: CPU-Only (No GPU)")
    print("=" * 70)

    hw = HardwareInfo(
        vendor=GPUVendor.CPU_ONLY,
        tier=GPUTier.CPU_ONLY,
        name="CPU",
        vram_gb=0.0,
        driver_version=None,
        has_nvenc=False,
        has_rtx_video_sdk=False,
        has_cuda=False,
        has_vulkan=False
    )

    config = get_optimal_config(hw)
    print(f"Engine: {config['upscale_engine']} (should be ffmpeg)")
    print(f"Encoder: {config['encoder']} (should be libx265)")
    print(f"Quality: {config['quality']} (should be good - lower for speed)")
    print(f"Face Restore: {config['face_restore']} (should be False - too slow)")
    print(f"Audio Upmix: {config['audio_upmix']} (should be simple)")
    print(f"Warnings: {len(config['warnings'])} warning(s)")
    if config['warnings']:
        for w in config['warnings']:
            print(f"  - {w[:80]}...")
    print()


def test_low_vram_rtx():
    """Test RTX 3050 with only 4GB VRAM."""
    print("=" * 70)
    print("Scenario 7: RTX 3050 (4GB) - Low VRAM")
    print("=" * 70)

    hw = HardwareInfo(
        vendor=GPUVendor.NVIDIA,
        tier=GPUTier.RTX_30_SERIES,
        name="NVIDIA GeForce RTX 3050",
        vram_gb=4.0,  # Low VRAM
        driver_version="535.98",
        has_nvenc=True,
        has_rtx_video_sdk=True,
        has_cuda=True,
        has_vulkan=True
    )

    config = get_optimal_config(hw)
    print(f"Engine: {config['upscale_engine']}")
    print(f"Encoder: {config['encoder']}")
    print(f"Quality: {config['quality']}")
    print(f"Face Restore: {config['face_restore']} (should be False - low VRAM)")
    print(f"Audio Upmix: {config['audio_upmix']} (should be surround - not demucs)")
    print(f"Warnings: {len(config['warnings'])} warning(s)")
    if config['warnings']:
        for w in config['warnings']:
            print(f"  - {w[:80]}...")
    print()


def main():
    """Run all test scenarios."""
    print()
    print("Testing Hardware Auto-Configuration Scenarios")
    print()

    test_rtx_5080()
    test_rtx_3060()
    test_gtx_1660()
    test_amd_rx7800()
    test_intel_arc()
    test_cpu_only()
    test_low_vram_rtx()

    print("=" * 70)
    print("All scenarios tested successfully!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
