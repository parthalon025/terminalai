#!/usr/bin/env python3
"""
TerminalAI Setup Script
========================
Handles installation with automatic compatibility patches.

Features:
- Python 3.10-3.13 compatibility
- Automatic basicsr torchvision patch
- Dependency version validation
- Post-install verification
"""

import sys
import subprocess
from pathlib import Path


def apply_basicsr_patch():
    """
    Apply compatibility patch for basicsr with torchvision >= 0.17.

    This fixes the deprecated import:
    from torchvision.transforms.functional_tensor import rgb_to_grayscale

    Replaced with:
    from torchvision.transforms.functional import rgb_to_grayscale
    """
    try:
        import basicsr
        basicsr_path = Path(basicsr.__file__).parent
        degradations_file = basicsr_path / "data" / "degradations.py"

        if not degradations_file.exists():
            print(f"[INFO] BasicSR degradations.py not found at {degradations_file}")
            return False

        # Read file
        content = degradations_file.read_text(encoding="utf-8")

        # Check if already patched
        if "from torchvision.transforms.functional import rgb_to_grayscale" in content:
            print("[OK] BasicSR already patched for torchvision >= 0.17")
            return True

        # Check if patch needed
        if "from torchvision.transforms.functional_tensor import rgb_to_grayscale" not in content:
            print("[INFO] BasicSR patch not needed (different version)")
            return True

        # Apply patch
        patched_content = content.replace(
            "from torchvision.transforms.functional_tensor import rgb_to_grayscale",
            """try:
    from torchvision.transforms.functional import rgb_to_grayscale
except ImportError:
    from torchvision.transforms.functional_tensor import rgb_to_grayscale"""
        )

        # Write patched file
        degradations_file.write_text(patched_content, encoding="utf-8")
        print("[OK] BasicSR patched for torchvision >= 0.17")
        return True

    except ImportError:
        print("[INFO] BasicSR not installed, skipping patch")
        return True
    except Exception as e:
        print(f"[WARN] Failed to patch BasicSR: {e}")
        return False


def check_python_version():
    """Verify Python version is supported."""
    version = sys.version_info
    if version < (3, 10):
        print(f"[ERROR] Python {version.major}.{version.minor} is not supported")
        print("[ERROR] Please use Python 3.10 or newer")
        sys.exit(1)
    elif version >= (3, 14):
        print(f"[WARN] Python {version.major}.{version.minor} is untested")
        print("[WARN] Recommended: Python 3.10-3.13")
    else:
        print(f"[OK] Python {version.major}.{version.minor} is supported")


def check_numpy_version():
    """Check numpy version for AI package compatibility."""
    try:
        import numpy as np
        version = np.__version__
        major = int(version.split('.')[0])

        if major >= 2:
            print(f"[WARN] NumPy {version} detected (2.x)")
            print("[WARN] AI packages may not be compatible with NumPy 2.x")
            print("[WARN] Consider: pip install 'numpy<2.0'")
            return False
        else:
            print(f"[OK] NumPy {version} is compatible")
            return True
    except ImportError:
        print("[INFO] NumPy not installed yet")
        return True


def post_install():
    """Run post-installation tasks."""
    print("\n" + "=" * 60)
    print("TerminalAI Post-Install Checks")
    print("=" * 60 + "\n")

    # Check Python version
    check_python_version()

    # Check NumPy version
    check_numpy_version()

    # Apply patches
    print("\nApplying compatibility patches...")
    apply_basicsr_patch()

    print("\n" + "=" * 60)
    print("Installation complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Verify installation: python -m vhs_upscaler --info")
    print("  2. Launch GUI: python -m vhs_upscaler")
    print("  3. See README.md for usage examples")
    print()


if __name__ == "__main__":
    # Run setuptools installation
    from setuptools import setup

    # Read version from package
    version = "1.5.1"

    # Standard setup
    setup(
        name="terminalai",
        version=version,
    )

    # Post-install tasks
    post_install()
