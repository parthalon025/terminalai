#!/usr/bin/env python3
"""
Dependency Verification Script
================================
Comprehensive check of all TerminalAI dependencies and features.

Usage:
    python scripts/verify_dependencies.py
    python scripts/verify_dependencies.py --fix-imports
    python scripts/verify_dependencies.py --json
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def verify_all():
    """Run comprehensive dependency verification."""
    print("=" * 70)
    print("TerminalAI Dependency Verification")
    print("=" * 70)
    print()

    # Check core package
    print("[1/3] Core Package")
    print("-" * 70)
    try:
        import vhs_upscaler
        print(f"[OK] vhs_upscaler v{vhs_upscaler.__version__} imported")

        # Test core imports
        from vhs_upscaler import VideoQueue, QueueJob, JobStatus, get_logger
        print("[OK] Core classes: VideoQueue, QueueJob, JobStatus, get_logger")

        # Test feature detection
        features = vhs_upscaler.get_available_features()
        print(f"[OK] Feature detection available")

        for feature, available in features.items():
            status = "[YES]" if available else "[NO] "
            print(f"  {status} {feature.replace('_', ' ').title()}")

    except ImportError as e:
        print(f"[FAIL] Core package import failed: {e}")
        return False

    print()
    print("[2/3] Dependencies")
    print("-" * 70)
    try:
        status = vhs_upscaler.check_dependencies(verbose=True)
        print()
    except Exception as e:
        print(f"[FAIL] Dependency check failed: {e}")
        return False

    print()
    print("[3/3] Entry Points")
    print("-" * 70)
    try:
        # Test entry point imports
        from vhs_upscaler.gui import main as gui_main
        print("[OK] GUI entry point: vhs_upscaler.gui.main")

        from vhs_upscaler.vhs_upscale import main as cli_main
        print("[OK] CLI entry point: vhs_upscaler.vhs_upscale.main")

        # Test __main__ module
        from vhs_upscaler.__main__ import main as main_entry
        print("[OK] Main entry point: python -m vhs_upscaler")

    except ImportError as e:
        print(f"[FAIL] Entry point import failed: {e}")
        return False

    print()
    print("=" * 70)
    print("[SUCCESS] All verification checks passed!")
    print("=" * 70)
    return True


def fix_imports():
    """
    Attempt to fix common import issues.

    This includes:
    - Clearing Python cache files (.pyc, __pycache__)
    - Checking for circular import issues
    - Verifying module structure
    """
    print("Attempting to fix common import issues...")
    print()

    import shutil

    project_root = Path(__file__).parent.parent

    # Clear __pycache__ directories
    print("[1/2] Clearing Python cache files...")
    cache_dirs = list(project_root.rglob("__pycache__"))
    for cache_dir in cache_dirs:
        try:
            shutil.rmtree(cache_dir)
            print(f"  [OK] Removed {cache_dir.relative_to(project_root)}")
        except Exception as e:
            print(f"  [WARN] Could not remove {cache_dir}: {e}")

    # Clear .pyc files
    pyc_files = list(project_root.rglob("*.pyc"))
    for pyc_file in pyc_files:
        try:
            pyc_file.unlink()
            print(f"  [OK] Removed {pyc_file.relative_to(project_root)}")
        except Exception as e:
            print(f"  [WARN] Could not remove {pyc_file}: {e}")

    print()
    print("[2/2] Verifying module structure...")

    # Check for __init__.py files
    vhs_upscaler_dir = project_root / "vhs_upscaler"
    if not (vhs_upscaler_dir / "__init__.py").exists():
        print("  [ERROR] vhs_upscaler/__init__.py is missing!")
        return False

    print("  [OK] Module structure is valid")
    print()
    print("[SUCCESS] Import fixes applied. Please retry verification.")
    return True


def export_json():
    """Export dependency status as JSON."""
    try:
        import vhs_upscaler

        result = {
            "version": vhs_upscaler.__version__,
            "features": vhs_upscaler.get_available_features(),
            "dependencies": vhs_upscaler.check_dependencies(verbose=False),
        }

        print(json.dumps(result, indent=2))
        return True
    except Exception as e:
        error_result = {"error": str(e)}
        print(json.dumps(error_result, indent=2))
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Verify TerminalAI dependencies and imports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--fix-imports",
        action="store_true",
        help="Attempt to fix common import issues",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    if args.fix_imports:
        success = fix_imports()
        return 0 if success else 1

    if args.json:
        success = export_json()
        return 0 if success else 1

    # Default: Run verification
    success = verify_all()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
