#!/usr/bin/env python3
"""
Test GUI Hardware Detection
============================
Test that the GUI's hardware detection wrapper works without hanging.
"""

import logging
import sys
import time
import threading
from pathlib import Path

# Add vhs_upscaler to path
sys.path.insert(0, str(Path(__file__).parent / "vhs_upscaler"))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)

def test_gui_hardware_detection():
    """Test the GUI's AppState.detect_hardware_once() method."""
    logger.info("Testing GUI hardware detection wrapper...")

    try:
        # Import GUI module
        from gui import AppState, HAS_HARDWARE_DETECTION

        logger.info(f"HAS_HARDWARE_DETECTION: {HAS_HARDWARE_DETECTION}")

        if not HAS_HARDWARE_DETECTION:
            logger.warning("Hardware detection not available in GUI")
            return True  # Not a failure, just not available

        # Reset state for testing
        AppState.hardware_detected = False
        AppState.hardware = None
        AppState.optimal_config = None

        start_time = time.time()
        logger.info("Calling AppState.detect_hardware_once()...")

        # This should complete quickly or timeout gracefully
        AppState.detect_hardware_once()

        elapsed = time.time() - start_time
        logger.info(f"Detection completed in {elapsed:.2f} seconds")

        # Check results
        if AppState.hardware:
            logger.info(f"Hardware: {AppState.hardware.display_name}")
        else:
            logger.warning("No hardware detected (CPU-only or timeout)")

        if AppState.optimal_config:
            logger.info(f"Config: {AppState.optimal_config['explanation']}")

        logger.info("GUI hardware detection test PASSED")
        return True

    except Exception as e:
        logger.error(f"GUI hardware detection test FAILED: {e}", exc_info=True)
        return False

def test_with_timeout():
    """Run test with timeout to detect hanging."""
    logger.info("Running GUI test with 20-second timeout...")

    result = {"completed": False, "success": False}

    def run_test():
        result["success"] = test_gui_hardware_detection()
        result["completed"] = True

    test_thread = threading.Thread(target=run_test, daemon=True)
    start_time = time.time()
    test_thread.start()
    test_thread.join(timeout=20.0)
    elapsed = time.time() - start_time

    if not result["completed"]:
        logger.error(f"\nTest FAILED - GUI detection HUNG after {elapsed:.1f} seconds")
        return False
    elif result["success"]:
        logger.info(f"\nAll tests PASSED in {elapsed:.2f} seconds")
        return True
    else:
        logger.error(f"\nTest completed but with errors")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("GUI Hardware Detection Test")
    print("=" * 70)
    print()

    success = test_with_timeout()

    print()
    print("=" * 70)
    if success:
        print("RESULT: SUCCESS - GUI hardware detection working")
    else:
        print("RESULT: FAILURE - GUI hardware detection has issues")
    print("=" * 70)

    sys.exit(0 if success else 1)
