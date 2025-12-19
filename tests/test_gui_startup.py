#!/usr/bin/env python3
"""
Test GUI Startup
================
Verify that the GUI can start without hanging during hardware detection.
"""

import logging
import sys
import time
import threading
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)

def test_gui_imports():
    """Test that GUI module can be imported and initialized."""
    logger.info("Testing GUI module import...")

    try:
        # Add path
        sys.path.insert(0, str(Path(__file__).parent / "vhs_upscaler"))

        start_time = time.time()

        # Import GUI module
        logger.info("Importing GUI module...")
        import gui

        elapsed = time.time() - start_time
        logger.info(f"GUI module imported in {elapsed:.2f} seconds")

        # Check if hardware detection is available
        logger.info(f"Hardware detection available: {gui.HAS_HARDWARE_DETECTION}")

        # Trigger hardware detection
        if gui.HAS_HARDWARE_DETECTION:
            logger.info("Triggering hardware detection...")
            detect_start = time.time()

            gui.AppState.detect_hardware_once()

            detect_elapsed = time.time() - detect_start
            logger.info(f"Hardware detection completed in {detect_elapsed:.2f} seconds")

            if gui.AppState.hardware:
                logger.info(f"Detected hardware: {gui.AppState.hardware.display_name}")
            else:
                logger.warning("No hardware detected (timeout or CPU-only)")

            if gui.AppState.optimal_config:
                logger.info(f"Optimal engine: {gui.AppState.optimal_config['upscale_engine']}")

        logger.info("GUI import and initialization test PASSED")
        return True

    except Exception as e:
        logger.error(f"GUI import test FAILED: {e}", exc_info=True)
        return False

def test_with_timeout():
    """Run test with timeout."""
    logger.info("Running GUI startup test with 30-second timeout...")

    result = {"completed": False, "success": False}

    def run_test():
        result["success"] = test_gui_imports()
        result["completed"] = True

    test_thread = threading.Thread(target=run_test, daemon=True)
    start_time = time.time()
    test_thread.start()
    test_thread.join(timeout=30.0)
    elapsed = time.time() - start_time

    if not result["completed"]:
        logger.error(f"\nTest FAILED - GUI startup HUNG after {elapsed:.1f} seconds")
        return False
    elif result["success"]:
        logger.info(f"\nAll tests PASSED in {elapsed:.2f} seconds")
        return True
    else:
        logger.error(f"\nTest completed with errors")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("GUI Startup Test")
    print("=" * 70)
    print()

    success = test_with_timeout()

    print()
    print("=" * 70)
    if success:
        print("RESULT: SUCCESS - GUI can start without hanging")
    else:
        print("RESULT: FAILURE - GUI has startup issues")
    print("=" * 70)

    sys.exit(0 if success else 1)
