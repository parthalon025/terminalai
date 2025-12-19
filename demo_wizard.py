#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
First-Run Wizard Demo
=====================

Quick demo script to test the wizard without launching the full GUI.
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

from first_run_wizard import (
    HardwareDetector,
    FirstRunManager,
    create_wizard_ui,
)


def demo_hardware_detection():
    """Demo hardware detection."""
    print("\n" + "=" * 60)
    print("  Hardware Detection Demo")
    print("=" * 60 + "\n")

    detector = HardwareDetector()

    # Detect GPU
    print("Detecting GPU...")
    gpu_info = detector.detect_gpu()

    print(f"\nGPU Information:")
    print(f"  Vendor: {gpu_info['vendor']}")
    print(f"  Name: {gpu_info['name']}")
    print(f"  VRAM: {gpu_info['vram_mb']} MB" if gpu_info['vram_mb'] else "  VRAM: N/A")
    print(f"  CUDA Available: {gpu_info['cuda_available']}")
    if gpu_info['compute_capability']:
        print(f"  Compute Capability: {gpu_info['compute_capability']}")

    # System info
    print(f"\nSystem Information:")
    sys_info = detector.get_system_info()
    for key, value in sys_info.items():
        print(f"  {key}: {value}")

    # Recommendation
    print(f"\nRecommendation:")
    if gpu_info["vendor"] == "nvidia":
        print("  [OK] Your system supports GPU-accelerated processing!")
        print("  [OK] AI models will run significantly faster on your GPU.")
        print("  [OK] Hardware-accelerated encoding (NVENC) available.")
    elif gpu_info["vendor"] in ["amd", "intel"]:
        print("  [WARNING] GPU detected but CUDA not available.")
        print("  [INFO] AI models will run on CPU (slower but functional).")
    else:
        print("  [INFO] No GPU detected - using CPU only.")
        print("  [INFO] Processing will be slower but fully functional.")

    print("\n" + "=" * 60 + "\n")


def demo_wizard_state():
    """Demo wizard state management."""
    print("\n" + "=" * 60)
    print("  Wizard State Demo")
    print("=" * 60 + "\n")

    print("Checking wizard state...")

    if FirstRunManager.is_first_run():
        print("  Status: First run - wizard will be shown")
        print(f"  Cache directory: {FirstRunManager.CACHE_DIR}")
        print(f"  Marker file: {FirstRunManager.FIRST_RUN_MARKER}")
    else:
        print("  Status: Returning user - wizard will be skipped")
        print(f"  Saved configuration:")

        config = FirstRunManager.load_config()
        for key, value in config.items():
            print(f"    {key}: {value}")

    print("\n" + "=" * 60 + "\n")


def demo_launch_wizard():
    """Launch the wizard UI."""
    print("\n" + "=" * 60)
    print("  Launching First-Run Wizard")
    print("=" * 60 + "\n")

    print("Creating wizard UI...")
    wizard = create_wizard_ui()

    print("Wizard created successfully!")
    print("\nLaunching in browser...")
    print("Press Ctrl+C to stop the server.\n")

    wizard.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        inbrowser=True
    )


def main():
    """Main demo menu."""
    import argparse

    parser = argparse.ArgumentParser(description="First-Run Wizard Demo")
    parser.add_argument(
        "action",
        choices=["detect", "state", "launch", "reset", "all"],
        help="Demo action to perform"
    )

    args = parser.parse_args()

    if args.action == "detect":
        demo_hardware_detection()

    elif args.action == "state":
        demo_wizard_state()

    elif args.action == "launch":
        demo_launch_wizard()

    elif args.action == "reset":
        print("Resetting wizard state...")
        FirstRunManager.reset()
        print("[OK] Wizard state reset. Next launch will show wizard.")

    elif args.action == "all":
        demo_hardware_detection()
        demo_wizard_state()

        response = input("\nLaunch wizard UI? (y/N): ")
        if response.lower() == "y":
            demo_launch_wizard()


if __name__ == "__main__":
    main()
