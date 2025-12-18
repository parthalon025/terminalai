#!/usr/bin/env python3
"""
Test script for the deinterlace module.

This script demonstrates and tests the deinterlacing functionality,
including VapourSynth QTGMC and FFmpeg filter support.

Usage:
    python test_deinterlace.py --check-setup
    python test_deinterlace.py --test-ffmpeg input.mp4 output.mp4
    python test_deinterlace.py --test-qtgmc input.mp4 output.mp4
    python test_deinterlace.py --compare-all input.mp4 output_dir/
"""

import argparse
import logging
import sys
from pathlib import Path

from deinterlace import (
    DeinterlaceProcessor,
    DeinterlaceEngine,
    test_deinterlace_setup
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def check_setup():
    """Check and display deinterlacing setup status."""
    print("\n" + "=" * 70)
    print("  Deinterlacing Setup Check")
    print("=" * 70)

    results = test_deinterlace_setup()

    print("\nComponent Availability:")
    print(f"  FFmpeg:        {'✓ Available' if results['ffmpeg_available'] else '✗ Not found'}")
    print(f"  VapourSynth:   {'✓ Available' if results['vapoursynth_available'] else '✗ Not found'}")
    print(f"  vspipe:        {'✓ Available' if results['vspipe_available'] else '✗ Not found'}")

    print("\nAvailable Deinterlace Engines:")
    if results['available_engines']:
        for engine in results['available_engines']:
            marker = "→" if engine == results['recommended_engine'] else " "
            print(f"  {marker} {engine}")
    else:
        print("  None available - FFmpeg not found!")

    if results['recommended_engine']:
        print(f"\nRecommended Engine: {results['recommended_engine']}")
    else:
        print("\nNo deinterlacing engines available!")
        print("Install FFmpeg to enable deinterlacing.")

    # Detailed VapourSynth check
    if results['vapoursynth_available']:
        print("\nVapourSynth Details:")
        try:
            import vapoursynth as vs
            print(f"  Version: {vs.core.version()}")

            # Check for QTGMC dependencies
            print("\n  Required plugins:")
            plugins = ['ffms2', 'lsmas', 'bs']
            for plugin in plugins:
                try:
                    hasattr(vs.core, plugin)
                    print(f"    {plugin}: ✓")
                except:
                    print(f"    {plugin}: ✗")

            # Check for havsfunc
            try:
                import havsfunc
                print(f"  havsfunc: ✓ Available")
            except ImportError:
                print(f"  havsfunc: ✗ Not found (required for QTGMC)")
                print("    Install with: pip install havsfunc")

        except Exception as e:
            print(f"  Error checking details: {e}")
    else:
        print("\nTo enable QTGMC (best quality):")
        print("  1. Install VapourSynth: https://github.com/vapoursynth/vapoursynth")
        print("  2. Install havsfunc: pip install havsfunc")
        print("  3. Install a source plugin (ffms2 recommended)")

    print("\n" + "=" * 70)


def test_engine(engine_name: str, input_path: Path, output_path: Path, preset: str = "medium"):
    """Test a specific deinterlacing engine."""
    print(f"\n{'=' * 70}")
    print(f"  Testing {engine_name.upper()} Deinterlacing")
    print(f"{'=' * 70}")

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return False

    # Create engine
    try:
        engine = DeinterlaceEngine[engine_name.upper()]
    except KeyError:
        logger.error(f"Unknown engine: {engine_name}")
        logger.info(f"Available: {[e.value for e in DeinterlaceEngine]}")
        return False

    # Create processor
    processor = DeinterlaceProcessor(engine)

    # Display capabilities
    caps = processor.get_capabilities()
    print(f"\nProcessor Configuration:")
    print(f"  Selected engine: {caps['engine']}")
    print(f"  VapourSynth: {'Available' if caps['has_vapoursynth'] else 'Not available'}")
    print(f"  vspipe: {'Available' if caps['has_vspipe'] else 'Not available'}")

    # Progress callback
    def progress_callback(percent):
        print(f"\rProgress: {percent:5.1f}%", end="", flush=True)

    # Execute deinterlacing
    try:
        print(f"\nProcessing: {input_path.name}")
        print(f"Output: {output_path}")
        print(f"Preset: {preset} (QTGMC only)")
        print()

        success = processor.deinterlace(
            input_path=input_path,
            output_path=output_path,
            preset=preset,
            tff=True,  # Assume top field first (most NTSC VHS)
            progress_callback=progress_callback
        )

        print()  # New line after progress
        if success:
            print(f"\n✓ Deinterlacing complete: {output_path}")
            print(f"  Output size: {output_path.stat().st_size / (1024*1024):.1f} MB")
            return True
        else:
            print(f"\n✗ Deinterlacing failed")
            return False

    except Exception as e:
        print(f"\n✗ Error: {e}")
        logger.exception("Deinterlacing failed")
        return False


def compare_all_engines(input_path: Path, output_dir: Path, preset: str = "medium"):
    """Compare all available deinterlacing engines."""
    print(f"\n{'=' * 70}")
    print(f"  Comparing All Deinterlacing Engines")
    print(f"{'=' * 70}")

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return False

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get available engines
    available = DeinterlaceProcessor.list_available_engines()
    print(f"\nAvailable engines: {', '.join(available)}")
    print(f"Input: {input_path}")
    print(f"Output directory: {output_dir}")

    results = {}

    # Test each engine
    for engine_name in available:
        output_file = output_dir / f"{input_path.stem}_{engine_name}.mp4"

        print(f"\n{'-' * 70}")
        print(f"Testing: {engine_name}")
        print(f"{'-' * 70}")

        import time
        start_time = time.time()

        success = test_engine(engine_name, input_path, output_file, preset)

        elapsed = time.time() - start_time

        results[engine_name] = {
            'success': success,
            'output_file': output_file if success else None,
            'elapsed_time': elapsed,
            'output_size': output_file.stat().st_size if success and output_file.exists() else 0
        }

    # Print comparison summary
    print(f"\n{'=' * 70}")
    print(f"  Comparison Summary")
    print(f"{'=' * 70}")

    print(f"\n{'Engine':<15} {'Status':<10} {'Time':<12} {'Size (MB)':<12} {'Output File'}")
    print("-" * 70)

    for engine_name, result in results.items():
        status = "✓ Success" if result['success'] else "✗ Failed"
        elapsed = f"{result['elapsed_time']:.1f}s"
        size = f"{result['output_size'] / (1024*1024):.1f}" if result['output_size'] > 0 else "N/A"
        output = result['output_file'].name if result['output_file'] else "N/A"

        print(f"{engine_name:<15} {status:<10} {elapsed:<12} {size:<12} {output}")

    print("\nRecommendations:")
    print("  yadif:  Fast, good quality baseline (always available)")
    print("  bwdif:  Better motion compensation than yadif")
    print("  w3fdif: Better detail preservation")
    print("  qtgmc:  Best quality, slowest (requires VapourSynth)")

    print(f"\n{'=' * 70}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Test VHS Upscaler deinterlacing functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Check setup status:
    python test_deinterlace.py --check-setup

  Test FFmpeg filter:
    python test_deinterlace.py --test-ffmpeg interlaced.mp4 output_yadif.mp4

  Test QTGMC:
    python test_deinterlace.py --test-qtgmc interlaced.mp4 output_qtgmc.mp4 --preset slow

  Compare all engines:
    python test_deinterlace.py --compare-all interlaced.mp4 comparison_output/

  Specific engine test:
    python test_deinterlace.py --engine bwdif -i input.mp4 -o output.mp4
        """
    )

    parser.add_argument("--check-setup", action="store_true",
                        help="Check deinterlacing setup and display available engines")

    parser.add_argument("--test-ffmpeg", nargs=2, metavar=("INPUT", "OUTPUT"),
                        help="Test FFmpeg deinterlacing (yadif)")

    parser.add_argument("--test-qtgmc", nargs=2, metavar=("INPUT", "OUTPUT"),
                        help="Test QTGMC deinterlacing (VapourSynth)")

    parser.add_argument("--compare-all", nargs=2, metavar=("INPUT", "OUTPUT_DIR"),
                        help="Compare all available engines")

    parser.add_argument("--engine", choices=["yadif", "bwdif", "w3fdif", "qtgmc"],
                        help="Specific engine to test")

    parser.add_argument("-i", "--input", type=Path,
                        help="Input video file")

    parser.add_argument("-o", "--output", type=Path,
                        help="Output video file or directory")

    parser.add_argument("--preset", default="medium",
                        choices=["draft", "medium", "slow", "very_slow", "placebo"],
                        help="QTGMC quality preset (default: medium)")

    parser.add_argument("--bff", action="store_true",
                        help="Use bottom field first (default is top field first)")

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine action
    if args.check_setup:
        check_setup()

    elif args.test_ffmpeg:
        input_path = Path(args.test_ffmpeg[0])
        output_path = Path(args.test_ffmpeg[1])
        test_engine("yadif", input_path, output_path, args.preset)

    elif args.test_qtgmc:
        input_path = Path(args.test_qtgmc[0])
        output_path = Path(args.test_qtgmc[1])
        test_engine("qtgmc", input_path, output_path, args.preset)

    elif args.compare_all:
        input_path = Path(args.compare_all[0])
        output_dir = Path(args.compare_all[1])
        compare_all_engines(input_path, output_dir, args.preset)

    elif args.engine and args.input and args.output:
        test_engine(args.engine, args.input, args.output, args.preset)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
