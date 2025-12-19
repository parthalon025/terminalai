#!/usr/bin/env python3
"""
Test Hardware Detection
=======================
Test script to verify GPU detection and auto-configuration.

Usage:
    python test_hardware_detection.py
"""

import sys
from pathlib import Path

# Add vhs_upscaler to path
sys.path.insert(0, str(Path(__file__).parent / "vhs_upscaler"))

from hardware_detection import detect_hardware, get_optimal_config, print_hardware_report


def main():
    """Run hardware detection test."""
    print("Testing Hardware Detection System")
    print("=" * 70)
    print()

    # Detect hardware
    print("Detecting hardware...")
    hw = detect_hardware()

    # Get optimal configuration
    print("Calculating optimal configuration...")
    config = get_optimal_config(hw)

    # Print formatted report
    print_hardware_report(hw, config)

    # Test configuration values
    print("Configuration Test:")
    print(f"  Upscale Engine: {config['upscale_engine']}")
    print(f"  Encoder: {config['encoder']}")
    print(f"  Quality: {config['quality']}")
    print(f"  Face Restore: {config['face_restore']}")
    print(f"  Audio Upmix: {config['audio_upmix']}")
    print()

    # Verify settings are reasonable
    errors = []

    if config['upscale_engine'] not in ['rtxvideo', 'realesrgan', 'ffmpeg', 'auto']:
        errors.append(f"Invalid upscale engine: {config['upscale_engine']}")

    if config['encoder'] not in ['hevc_nvenc', 'h264_nvenc', 'libx265', 'libx264']:
        errors.append(f"Invalid encoder: {config['encoder']}")

    if config['quality'] not in ['best', 'balanced', 'good']:
        errors.append(f"Invalid quality: {config['quality']}")

    if not isinstance(config['face_restore'], bool):
        errors.append(f"face_restore should be boolean, got: {type(config['face_restore'])}")

    if config['audio_upmix'] not in ['demucs', 'surround', 'simple', 'none']:
        errors.append(f"Invalid audio_upmix: {config['audio_upmix']}")

    if errors:
        print("ERRORS DETECTED:")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print("All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
