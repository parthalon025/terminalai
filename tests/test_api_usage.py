#!/usr/bin/env python
"""Test programmatic API usage for vhs_upscaler package."""

import sys

# Test 1: Package import
print("Test 1: Package Import")
try:
    import vhs_upscaler
    print(f"✓ vhs_upscaler imported successfully")
    print(f"  Version: {vhs_upscaler.__version__}")
except Exception as e:
    print(f"✗ Failed to import vhs_upscaler: {e}")
    sys.exit(1)

# Test 2: Queue API
print("\nTest 2: Queue API")
try:
    from vhs_upscaler import VideoQueue, QueueJob, JobStatus

    # Create queue
    queue = VideoQueue()
    print(f"✓ VideoQueue created successfully")

    # Test job creation
    job = QueueJob(
        id="test-001",
        input_source="/path/to/input.mp4",
        output_path="/path/to/output.mp4",
        preset="vhs",
        resolution=1080
    )
    print(f"✓ QueueJob created successfully")
    print(f"  Job ID: {job.id}")
    print(f"  Status: {job.status}")

    # Test status enum
    print(f"✓ JobStatus enum accessible:")
    print(f"  PENDING = {JobStatus.PENDING}")
    print(f"  PROCESSING = {JobStatus.PROCESSING}")
    print(f"  COMPLETED = {JobStatus.COMPLETED}")
    print(f"  FAILED = {JobStatus.FAILED}")

except Exception as e:
    print(f"✗ Queue API failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Logger API
print("\nTest 3: Logger API")
try:
    from vhs_upscaler import get_logger

    logger = get_logger(__name__)
    logger.info("Test log message")
    print(f"✓ Logger API works")

except Exception as e:
    print(f"✗ Logger API failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# All tests passed
print("\n" + "="*60)
print("ALL PROGRAMMATIC API TESTS PASSED ✓")
print("="*60)
print("\nThe vhs_upscaler package is ready for programmatic use.")
print("\nExample usage:")
print("  from vhs_upscaler import VideoQueue, QueueJob")
print("  queue = VideoQueue()")
print("  job = queue.add_job(input_path, output_path, ...)")
print("  # Process jobs...")
