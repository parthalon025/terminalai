#!/usr/bin/env python3
"""
Verify basicsr Torchvision Compatibility Patch

Checks if the patch has been applied and if basicsr works correctly.

Usage:
    python verify_basicsr_patch.py
"""

import sys
from pathlib import Path


def main():
    """Verify the basicsr patch status."""
    print("=" * 80)
    print("basicsr Torchvision Compatibility Patch Verification")
    print("=" * 80)
    print()

    # Check if basicsr is installed
    try:
        import basicsr
        print("[OK] basicsr is installed")
        print(f"    Location: {basicsr.__file__}")
    except ImportError:
        print("[INFO] basicsr is not installed")
        print("    This is expected if you haven't installed GFPGAN or Real-ESRGAN")
        print("    No patch needed.")
        return 0

    # Check if degradations.py exists
    basicsr_dir = Path(basicsr.__file__).parent
    degradations_file = basicsr_dir / "data" / "degradations.py"

    if not degradations_file.exists():
        print("[ERROR] degradations.py not found")
        print(f"    Expected at: {degradations_file}")
        return 1

    print(f"[OK] degradations.py found at: {degradations_file}")

    # Check if patch is applied
    content = degradations_file.read_text(encoding='utf-8')

    if "Fix for torchvision >= 0.17" in content:
        print("[OK] Patch is applied")
        print("    basicsr is compatible with torchvision >= 0.17")
    else:
        print("[WARN] Patch is NOT applied")
        print("    basicsr may fail with torchvision >= 0.17")
        print()
        print("To apply the patch, run:")
        print("    python scripts/installation/patch_basicsr.py")
        return 1

    # Test import
    print()
    print("Testing basicsr import...")
    try:
        from basicsr.data.degradations import rgb_to_grayscale
        print("[OK] rgb_to_grayscale import successful")
        print("    basicsr is working correctly")
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        print("    Patch may not be working correctly")
        return 1

    # Check torchvision version
    print()
    print("Checking torchvision version...")
    try:
        import torchvision
        version = torchvision.__version__
        print(f"[OK] torchvision version: {version}")

        # Parse version
        major, minor = map(int, version.split('.')[:2])
        if major > 0 or (major == 0 and minor >= 17):
            print("    Using torchvision >= 0.17 (patch required and working)")
        else:
            print("    Using torchvision < 0.17 (patch not strictly required but harmless)")
    except ImportError:
        print("[WARN] torchvision not installed")

    print()
    print("=" * 80)
    print("[OK] Verification Complete - basicsr is ready to use!")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
