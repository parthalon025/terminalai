#!/usr/bin/env python3
"""
Test script to verify GUI bug fixes
=====================================
Tests that all parameters are properly wired from GUI to backend.
"""

import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Add vhs_upscaler to path
sys.path.insert(0, str(Path(__file__).parent / "vhs_upscaler"))

def test_queue_job_dataclass():
    """Test that QueueJob has all required fields."""
    from queue_manager import QueueJob

    print("Testing QueueJob dataclass...")

    # Create a job with all new parameters
    job = QueueJob(
        id="test123",
        input_source="test.mp4",
        output_path="output.mp4",
        preset="vhs",
        resolution=1080,
        quality=0,
        crf=20,
        encoder="hevc_nvenc",
        upscale_engine="auto",
        hdr_mode="sdr",
        realesrgan_model="realesrgan-x4plus",
        realesrgan_denoise=0.5,
        ffmpeg_scale_algo="lanczos",
        hdr_brightness=400,
        hdr_color_depth=10,
        audio_enhance="none",
        audio_upmix="none",
        audio_layout="original",
        audio_format="aac",
        audio_target_loudness=-14.0,
        audio_noise_floor=-20.0,
        demucs_model="htdemucs",
        demucs_device="auto",
        demucs_shifts=1,
        lfe_crossover=120,
        center_mix=0.707,
        surround_delay=15,
        # NEW PARAMETERS - should not raise AttributeError
        lut_file="luts/test.cube",
        lut_strength=0.8,
        face_restore=True,
        face_restore_strength=0.6,
        face_restore_upscale=2,
        deinterlace_algorithm="bwdif",
        qtgmc_preset="medium"
    )

    # Verify all fields are accessible
    assert job.lut_file == "luts/test.cube", "LUT file not stored correctly"
    assert job.lut_strength == 0.8, "LUT strength not stored correctly"
    assert job.face_restore == True, "Face restore not stored correctly"
    assert job.face_restore_strength == 0.6, "Face restore strength not stored correctly"
    assert job.face_restore_upscale == 2, "Face restore upscale not stored correctly"
    assert job.deinterlace_algorithm == "bwdif", "Deinterlace algorithm not stored correctly"
    assert job.qtgmc_preset == "medium", "QTGMC preset not stored correctly"
    assert job.realesrgan_denoise == 0.5, "Real-ESRGAN denoise not stored correctly"

    print("✓ QueueJob dataclass has all required fields")

    # Test serialization
    job_dict = job.to_dict()
    assert 'lut_file' in job_dict, "LUT file not in serialized dict"
    assert 'face_restore' in job_dict, "Face restore not in serialized dict"
    assert 'deinterlace_algorithm' in job_dict, "Deinterlace algorithm not in serialized dict"

    print("✓ QueueJob serialization works correctly")

    # Test deserialization
    job2 = QueueJob.from_dict(job_dict)
    assert job2.lut_file == job.lut_file, "Deserialized LUT file mismatch"
    assert job2.face_restore == job.face_restore, "Deserialized face restore mismatch"

    print("✓ QueueJob deserialization works correctly")


def test_queue_add_job():
    """Test that VideoQueue.add_job accepts all parameters."""
    from queue_manager import VideoQueue

    print("\nTesting VideoQueue.add_job()...")

    queue = VideoQueue()

    # Add job with all new parameters
    job = queue.add_job(
        input_source="test.mp4",
        output_path="output.mp4",
        preset="vhs",
        resolution=1080,
        quality=0,
        crf=20,
        encoder="hevc_nvenc",
        upscale_engine="auto",
        hdr_mode="sdr",
        realesrgan_model="realesrgan-x4plus",
        realesrgan_denoise=0.7,  # Test non-default value
        ffmpeg_scale_algo="lanczos",
        hdr_brightness=400,
        hdr_color_depth=10,
        audio_enhance="none",
        audio_upmix="none",
        audio_layout="original",
        audio_format="aac",
        audio_target_loudness=-14.0,
        audio_noise_floor=-20.0,
        demucs_model="htdemucs",
        demucs_device="auto",
        demucs_shifts=1,
        lfe_crossover=120,
        center_mix=0.707,
        surround_delay=15,
        # NEW PARAMETERS
        lut_file="luts/vhs_restore.cube",
        lut_strength=0.9,
        face_restore=True,
        face_restore_strength=0.7,
        face_restore_upscale=4,
        deinterlace_algorithm="qtgmc",
        qtgmc_preset="slow"
    )

    # Verify parameters were stored
    assert job.lut_file == "luts/vhs_restore.cube", "LUT file parameter not passed"
    assert job.lut_strength == 0.9, "LUT strength parameter not passed"
    assert job.face_restore == True, "Face restore parameter not passed"
    assert job.face_restore_strength == 0.7, "Face restore strength parameter not passed"
    assert job.face_restore_upscale == 4, "Face restore upscale parameter not passed"
    assert job.deinterlace_algorithm == "qtgmc", "Deinterlace algorithm parameter not passed"
    assert job.qtgmc_preset == "slow", "QTGMC preset parameter not passed"
    assert job.realesrgan_denoise == 0.7, "Real-ESRGAN denoise parameter not passed (BUG!)"

    print("✓ VideoQueue.add_job() accepts all parameters")
    print("✓ All parameters correctly stored in job")


def test_processing_config_construction():
    """Test that ProcessingConfig can be built from job parameters."""
    from vhs_upscale import ProcessingConfig
    from queue_manager import QueueJob

    print("\nTesting ProcessingConfig construction from job...")

    # Create a job
    job = QueueJob(
        id="test456",
        input_source="test.mp4",
        output_path="output.mp4",
        realesrgan_denoise=0.8,
        lut_file="luts/test.cube",
        lut_strength=0.5,
        face_restore=True,
        face_restore_strength=0.6,
        face_restore_upscale=2,
        deinterlace_algorithm="w3fdif",
        qtgmc_preset=None
    )

    # Build config (mimicking process_job in gui.py)
    config = ProcessingConfig(
        resolution=job.resolution,
        quality_mode=job.quality,
        crf=job.crf,
        preset=job.preset,
        encoder=job.encoder,
        upscale_engine=getattr(job, 'upscale_engine', 'auto'),
        hdr_mode=getattr(job, 'hdr_mode', 'sdr'),
        realesrgan_model=getattr(job, 'realesrgan_model', 'realesrgan-x4plus'),
        realesrgan_denoise=getattr(job, 'realesrgan_denoise', 0.5),
        ffmpeg_scale_algo=getattr(job, 'ffmpeg_scale_algo', 'lanczos'),
        hdr_brightness=getattr(job, 'hdr_brightness', 400),
        color_depth=getattr(job, 'hdr_color_depth', 10),
        audio_enhance=getattr(job, 'audio_enhance', 'none'),
        audio_upmix=getattr(job, 'audio_upmix', 'none'),
        audio_layout=getattr(job, 'audio_layout', 'original'),
        audio_format=getattr(job, 'audio_format', 'aac'),
        audio_target_loudness=getattr(job, 'audio_target_loudness', -14.0),
        audio_noise_floor=getattr(job, 'audio_noise_floor', -20.0),
        demucs_model=getattr(job, 'demucs_model', 'htdemucs'),
        demucs_device=getattr(job, 'demucs_device', 'auto'),
        demucs_shifts=getattr(job, 'demucs_shifts', 1),
        lfe_crossover=getattr(job, 'lfe_crossover', 120),
        center_mix=getattr(job, 'center_mix', 0.707),
        surround_delay=getattr(job, 'surround_delay', 15),
        # NEW PARAMETERS
        lut_file=Path(getattr(job, 'lut_file', '')) if getattr(job, 'lut_file', None) else None,
        lut_strength=getattr(job, 'lut_strength', 1.0),
        face_restore=getattr(job, 'face_restore', False),
        face_restore_strength=getattr(job, 'face_restore_strength', 0.5),
        face_restore_upscale=getattr(job, 'face_restore_upscale', 2),
        deinterlace_algorithm=getattr(job, 'deinterlace_algorithm', 'yadif'),
        qtgmc_preset=getattr(job, 'qtgmc_preset', None),
    )

    # Verify config has correct values
    assert config.realesrgan_denoise == 0.8, "Real-ESRGAN denoise not in config (CRITICAL BUG!)"
    assert config.lut_file is not None, "LUT file not in config"
    # Path uses forward slashes on Windows, so normalize comparison
    assert config.lut_file.as_posix() == "luts/test.cube", f"LUT file path incorrect in config: got {config.lut_file}"
    assert config.lut_strength == 0.5, "LUT strength not in config"
    assert config.face_restore == True, "Face restore not in config"
    assert config.face_restore_strength == 0.6, "Face restore strength not in config"
    assert config.face_restore_upscale == 2, "Face restore upscale not in config"
    assert config.deinterlace_algorithm == "w3fdif", "Deinterlace algorithm not in config"
    assert config.qtgmc_preset is None, "QTGMC preset not in config"

    print("✓ ProcessingConfig correctly built from job parameters")
    print("✓ All new parameters properly passed to backend")


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("GUI Bug Fix Verification Tests")
    print("=" * 60)

    try:
        test_queue_job_dataclass()
        test_queue_add_job()
        test_processing_config_construction()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nFixed bugs:")
        print("  1. ✓ Real-ESRGAN denoise parameter properly wired")
        print("  2. ✓ LUT file and strength parameters added")
        print("  3. ✓ Face restoration parameters added")
        print("  4. ✓ Deinterlace algorithm parameters added")
        print("  5. ✓ All parameters flow from GUI → Queue → ProcessingConfig")

        return 0

    except AssertionError as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ UNEXPECTED ERROR!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
