#!/usr/bin/env python3
"""
Test Hardware Detection Fix
============================
Verify that hardware detection completes without hanging.
"""

import logging
import sys
import time
from pathlib import Path

# Add vhs_upscaler to path
sys.path.insert(0, str(Path(__file__).parent / "vhs_upscaler"))

# Set up logging to see all messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)

def test_hardware_detection():
    """Test hardware detection with timeout."""
    logger.info("Starting hardware detection test...")

    try:
        from hardware_detection import detect_hardware, get_optimal_config

        start_time = time.time()
        logger.info("Calling detect_hardware()...")

        hw = detect_hardware()

        elapsed = time.time() - start_time
        logger.info(f"Detection completed in {elapsed:.2f} seconds")

        if hw:
            logger.info(f"Detected: {hw.display_name}")
            logger.info(f"Vendor: {hw.vendor.value}")
            logger.info(f"Tier: {hw.tier.value}")
            logger.info(f"VRAM: {hw.vram_gb:.1f} GB")
            logger.info(f"Has CUDA: {hw.has_cuda}")
            logger.info(f"Has NVENC: {hw.has_nvenc}")
            logger.info(f"Has RTX SDK: {hw.has_rtx_video_sdk}")

            # Test optimal config
            logger.info("\nGetting optimal config...")
            config = get_optimal_config(hw)
            logger.info(f"Upscale engine: {config['upscale_engine']}")
            logger.info(f"Encoder: {config['encoder']}")
            logger.info(f"Quality: {config['quality']}")
            logger.info(f"Explanation: {config['explanation']}")

            if config.get('warnings'):
                logger.warning("Warnings:")
                for warning in config['warnings']:
                    logger.warning(f"  - {warning}")
        else:
            logger.error("detect_hardware() returned None")

        logger.info("\nTest PASSED - Hardware detection completed successfully")
        return True

    except ImportError as e:
        logger.error(f"Import failed: {e}")
        logger.error("Make sure hardware_detection.py is in vhs_upscaler/")
        return False
    except Exception as e:
        logger.error(f"Test FAILED: {e}", exc_info=True)
        return False

def test_with_timeout():
    """Test hardware detection with timeout to detect hanging."""
    import threading

    logger.info("Running hardware detection with 15-second timeout...")

    result = {"completed": False, "success": False}

    def run_test():
        result["success"] = test_hardware_detection()
        result["completed"] = True

    test_thread = threading.Thread(target=run_test, daemon=True)
    start_time = time.time()
    test_thread.start()
    test_thread.join(timeout=15.0)
    elapsed = time.time() - start_time

    if not result["completed"]:
        logger.error(f"\nTest FAILED - Hardware detection HUNG after {elapsed:.1f} seconds")
        logger.error("The detection did not complete within the timeout period")
        return False
    elif result["success"]:
        logger.info(f"\nAll tests PASSED in {elapsed:.2f} seconds")
        return True
    else:
        logger.error(f"\nTest FAILED - Detection completed but with errors")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Hardware Detection Fix Test")
    print("=" * 70)
    print()

    success = test_with_timeout()

    print()
    print("=" * 70)
    if success:
        print("RESULT: SUCCESS - Hardware detection is working properly")
    else:
        print("RESULT: FAILURE - Hardware detection has issues")
    print("=" * 70)

    sys.exit(0 if success else 1)
