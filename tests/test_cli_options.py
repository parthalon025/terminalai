#!/usr/bin/env python3
"""
Comprehensive CLI Option Test Suite for VHS Upscaler
Tests all CLI options with a short video clip to verify functionality
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Test configuration
INPUT_VIDEO = r"D:\SSD\Home Videos\Justin_4th_Birthday_June_1991_92\Justin_4th_Birthday_June_1991_92\Justin_4th_Birthday_June_1991_92_00001.mp4"
OUTPUT_DIR = Path(r"D:\SSD\Home Videos\Justin_4th_Birthday_June_1991_92\test_output")
LOG_DIR = Path("test_logs")

# Create directories
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Test suite definition
TESTS = [
    # Basic tests
    {
        "name": "01_baseline_vhs_1080p",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "1080", "-p", "vhs", "--encoder", "hevc_nvenc"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_1080p.mp4"
    },

    # Resolution tests
    {
        "name": "02_resolution_720p",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "720", "-p", "vhs", "--encoder", "hevc_nvenc"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_720p.mp4"
    },
    {
        "name": "03_resolution_1440p",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "1440", "-p", "vhs", "--encoder", "hevc_nvenc"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_1440p.mp4"
    },

    # Preset tests
    {
        "name": "04_preset_dvd",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "1080", "-p", "dvd", "--encoder", "hevc_nvenc"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_1080p.mp4"
    },
    {
        "name": "05_preset_clean",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "1080", "-p", "clean", "--encoder", "hevc_nvenc"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_1080p.mp4"
    },

    # Encoder tests
    {
        "name": "06_encoder_h264_nvenc",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "1080", "-p", "vhs", "--encoder", "h264_nvenc"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_1080p.mp4"
    },
    {
        "name": "07_encoder_libx265",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "1080", "-p", "vhs", "--encoder", "libx265"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_1080p.mp4"
    },
    {
        "name": "08_encoder_libx264",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "1080", "-p", "vhs", "--encoder", "libx264"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_1080p.mp4"
    },

    # Quality tests
    {
        "name": "09_quality_fast",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "1080", "-p", "vhs", "-q", "1", "--encoder", "hevc_nvenc"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_1080p.mp4"
    },
    {
        "name": "10_crf_15",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "1080", "-p", "vhs", "--crf", "15", "--encoder", "hevc_nvenc"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_1080p.mp4"
    },

    # Audio enhancement tests
    {
        "name": "11_audio_enhance_voice",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "1080", "-p", "vhs", "--audio-enhance", "voice", "--encoder", "hevc_nvenc"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_1080p.mp4"
    },
    {
        "name": "12_audio_format_ac3",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "1080", "-p", "vhs", "--audio-format", "ac3", "--encoder", "hevc_nvenc"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_1080p.mp4"
    },

    # Advanced options
    {
        "name": "13_keep_temp",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "1080", "-p", "vhs", "--keep-temp", "--encoder", "hevc_nvenc"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_1080p.mp4"
    },
    {
        "name": "14_verbose",
        "args": ["-i", INPUT_VIDEO, "-o", str(OUTPUT_DIR), "-r", "1080", "-p", "vhs", "-v", "--encoder", "hevc_nvenc"],
        "expected_output": OUTPUT_DIR / "Justin_4th_Birthday_June_1991_92_00001_1080p.mp4"
    },
]


def run_test(test):
    """Run a single test and return results."""
    print(f"\n{'='*70}")
    print(f"TEST: {test['name']}")
    print(f"{'='*70}")

    # Clean up previous output
    if test['expected_output'].exists():
        test['expected_output'].unlink()

    # Build command
    cmd = [sys.executable, "-m", "vhs_upscaler.vhs_upscale"] + test['args']

    # Run test
    log_file = LOG_DIR / f"{test['name']}.log"
    start_time = datetime.now()

    try:
        with open(log_file, "w") as log:
            result = subprocess.run(
                cmd,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=600,  # 10 minute timeout
                text=True
            )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Check result
        if result.returncode == 0 and test['expected_output'].exists():
            file_size = test['expected_output'].stat().st_size / (1024 * 1024)  # MB
            print(f"[PASS] ({duration:.1f}s, {file_size:.1f} MB)")
            return {
                "name": test['name'],
                "status": "PASSED",
                "duration": duration,
                "file_size_mb": file_size,
                "log": str(log_file)
            }
        else:
            print(f"[FAIL] (exit code: {result.returncode})")
            print(f"  Log: {log_file}")
            return {
                "name": test['name'],
                "status": "FAILED",
                "duration": duration,
                "exit_code": result.returncode,
                "log": str(log_file)
            }

    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] (>10 minutes)")
        return {
            "name": test['name'],
            "status": "TIMEOUT",
            "log": str(log_file)
        }
    except Exception as e:
        print(f"[ERROR] {e}")
        return {
            "name": test['name'],
            "status": "ERROR",
            "error": str(e),
            "log": str(log_file)
        }


def main():
    """Run all tests and generate report."""
    print("="*70)
    print("VHS UPSCALER CLI COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Input video: {INPUT_VIDEO}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Total tests: {len(TESTS)}")
    print(f"Log directory: {LOG_DIR}")

    results = []
    for i, test in enumerate(TESTS, 1):
        print(f"\n[{i}/{len(TESTS)}]", end=" ")
        result = run_test(test)
        results.append(result)

    # Generate summary report
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for r in results if r['status'] == 'PASSED')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    timeout = sum(1 for r in results if r['status'] == 'TIMEOUT')
    errors = sum(1 for r in results if r['status'] == 'ERROR')

    print(f"Total: {len(results)}")
    print(f"[+] Passed: {passed}")
    print(f"[-] Failed: {failed}")
    print(f"[T] Timeout: {timeout}")
    print(f"[!] Errors: {errors}")

    # Detailed results
    if failed + timeout + errors > 0:
        print("\nFAILED/TIMEOUT/ERROR TESTS:")
        for r in results:
            if r['status'] != 'PASSED':
                print(f"  - {r['name']}: {r['status']}")
                print(f"    Log: {r['log']}")

    # Save report
    report_file = LOG_DIR / f"test_report_{datetime.now():%Y%m%d_%H%M%S}.txt"
    with open(report_file, "w") as f:
        f.write("VHS UPSCALER CLI TEST REPORT\n")
        f.write("="*70 + "\n\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Total tests: {len(results)}\n")
        f.write(f"Passed: {passed}\n")
        f.write(f"Failed: {failed}\n")
        f.write(f"Timeout: {timeout}\n")
        f.write(f"Errors: {errors}\n\n")

        f.write("DETAILED RESULTS:\n")
        f.write("-"*70 + "\n")
        for r in results:
            f.write(f"\nTest: {r['name']}\n")
            f.write(f"Status: {r['status']}\n")
            if 'duration' in r:
                f.write(f"Duration: {r['duration']:.1f}s\n")
            if 'file_size_mb' in r:
                f.write(f"Output size: {r['file_size_mb']:.1f} MB\n")
            if 'exit_code' in r:
                f.write(f"Exit code: {r['exit_code']}\n")
            if 'error' in r:
                f.write(f"Error: {r['error']}\n")
            f.write(f"Log: {r['log']}\n")

    print(f"\nFull report saved to: {report_file}")

    # Exit with appropriate code
    sys.exit(0 if (failed + timeout + errors) == 0 else 1)


if __name__ == "__main__":
    main()
