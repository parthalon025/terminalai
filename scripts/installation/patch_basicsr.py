#!/usr/bin/env python3
"""
Standalone basicsr Torchvision Compatibility Patcher

Patches basicsr 1.4.2 to fix torchvision >= 0.17 compatibility.
Can be run independently of the main installer.

Usage:
    python patch_basicsr.py
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from install import TerminalAIInstaller


def main():
    """Run the basicsr patch standalone."""
    print("=" * 80)
    print("basicsr Torchvision Compatibility Patcher")
    print("=" * 80)
    print()

    installer = TerminalAIInstaller(install_type="full")
    installer.patch_basicsr_torchvision()

    print()
    print("=" * 80)

    if installer.installed:
        print("[OK] Patch Applied Successfully")
        for item in installer.installed:
            print(f"  - {item}")
    elif installer.warnings:
        print("[WARN] Patch Skipped or Failed")
        for warning in installer.warnings:
            print(f"  - {warning}")
    else:
        print("[INFO] No Action Needed")
        print("  - basicsr not installed or already patched")

    print("=" * 80)

    # Return 0 if successful or no action needed, 1 if errors
    return 0 if not installer.errors else 1


if __name__ == "__main__":
    sys.exit(main())
