#!/usr/bin/env python3
"""Run all test files individually to avoid pytest capture bug."""
import subprocess
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    test_dir = Path("tests")
    test_files = sorted(test_dir.glob("test_*.py"))

    passed = 0
    failed = 0
    errors = 0
    failed_files = []

    print(f"Found {len(test_files)} test files\n")

    for test_file in test_files:
        print(f"Running {test_file.name}... ", end="", flush=True)

        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
            capture_output=True,
            text=True
        )

        # Parse results
        output = result.stdout + result.stderr

        if "passed" in output:
            # Extract number of passed tests
            for line in output.split("\n"):
                if "passed" in line:
                    try:
                        # Extract numbers from summary line
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if "passed" in part and i > 0:
                                num = int(parts[i-1])
                                passed += num
                                print(f"✓ {num} passed")
                                break
                    except:
                        print("✓ passed")
                    break

        if "failed" in output or result.returncode != 0:
            failed_files.append((test_file.name, output))
            # Extract number of failed tests
            for line in output.split("\n"):
                if "failed" in line:
                    try:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if "failed" in part and i > 0:
                                num = int(parts[i-1])
                                failed += num
                                print(f"✗ {num} failed")
                                break
                    except:
                        print("✗ failed")
                    break
            else:
                if result.returncode != 0:
                    print(f"✗ ERROR (code {result.returncode})")
                    errors += 1

    print(f"\n{'='*70}")
    print(f"SUMMARY: {passed} passed, {failed} failed, {errors} errors")
    print(f"{'='*70}")

    if failed_files:
        print(f"\nFailed files ({len(failed_files)}):")
        for filename, output in failed_files:
            print(f"\n{filename}:")
            # Print last 30 lines of output
            lines = output.split("\n")
            for line in lines[-30:]:
                if line.strip():
                    print(f"  {line}")

    return 0 if failed == 0 and errors == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
