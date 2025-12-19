#!/usr/bin/env python3
"""
RTX Video SDK Setup Module
==========================

Run with: python -m vhs_upscaler.setup_rtx

This provides an interactive setup wizard for RTX Video SDK.
"""

import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
if scripts_dir.exists():
    sys.path.insert(0, str(scripts_dir))

def main():
    """Run the RTX Video SDK setup wizard."""
    try:
        from scripts.setup_rtx_video import main as wizard_main
        wizard_main()
    except ImportError:
        # Fallback: run inline version
        _run_inline_setup()

def _run_inline_setup():
    """Inline setup when scripts module not available."""
    import os
    import platform
    import subprocess
    import webbrowser

    print("\n" + "="*60)
    print("RTX Video SDK Setup".center(60))
    print("="*60 + "\n")

    # Check platform
    if platform.system() != "Windows":
        print(f"❌ RTX Video SDK only supports Windows.")
        print(f"   Your platform: {platform.system()}")
        print("\n   TerminalAI will use Real-ESRGAN or FFmpeg instead.")
        return

    # Check for existing installation
    sdk_paths = [
        os.environ.get('RTX_VIDEO_SDK_HOME', ''),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'NVIDIA', 'RTXVideoSDK'),
        r'C:\Program Files\NVIDIA Corporation\RTX Video SDK',
        r'C:\NVIDIA\RTXVideoSDK',
    ]

    for path in sdk_paths:
        if path and os.path.exists(path):
            print(f"✓ RTX Video SDK found at: {path}")
            print("\n  You're all set! Select 'rtxvideo' in the GUI.")
            return

    print("RTX Video SDK not detected.\n")
    print("To install:")
    print("  1. Visit: https://developer.nvidia.com/rtx-video-sdk")
    print("  2. Download and install the SDK")
    print("  3. Set RTX_VIDEO_SDK_HOME environment variable")
    print("  4. Restart TerminalAI\n")

    response = input("Open download page in browser? [Y/n]: ").strip().lower()
    if response in ('', 'y', 'yes'):
        webbrowser.open("https://developer.nvidia.com/rtx-video-sdk")

if __name__ == "__main__":
    main()
