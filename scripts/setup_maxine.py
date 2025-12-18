#!/usr/bin/env python3
"""
NVIDIA Maxine SDK Setup Helper
===============================
Configures NVIDIA Maxine SDK after manual download.
"""

import os
import shutil
import sys
import zipfile
from pathlib import Path


def find_maxine_zip():
    """Find Maxine SDK zip file in common locations."""
    search_paths = [
        Path.home() / "Downloads",
        Path.cwd(),
        Path.home() / "Desktop",
    ]

    print("Searching for Maxine SDK zip file...")
    for search_path in search_paths:
        if not search_path.exists():
            continue

        for file in search_path.glob("*Maxine*.zip"):
            print(f"  Found: {file}")
            return file

        for file in search_path.glob("*VideoEffects*.zip"):
            print(f"  Found: {file}")
            return file

    return None


def extract_maxine(zip_path: Path, dest_path: Path):
    """Extract Maxine SDK to destination."""
    print(f"\nExtracting {zip_path.name}...")
    print(f"  Destination: {dest_path}")

    dest_path.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_path)

    print("  Extraction complete!")
    return True


def find_maxine_bin(base_path: Path):
    """Find the bin directory containing VideoEffectsApp.exe."""
    # Common patterns in Maxine SDK structure
    search_patterns = [
        "*/bin/VideoEffectsApp.exe",
        "bin/VideoEffectsApp.exe",
        "*/*/bin/VideoEffectsApp.exe",
    ]

    for pattern in search_patterns:
        matches = list(base_path.glob(pattern))
        if matches:
            return matches[0].parent

    return None


def verify_maxine_structure(bin_path: Path):
    """Verify Maxine SDK has required files."""
    required_files = [
        "VideoEffectsApp.exe",
    ]

    required_dirs = [
        "models",
    ]

    print("\nVerifying Maxine SDK structure...")

    all_good = True
    for file in required_files:
        if (bin_path / file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ Missing: {file}")
            all_good = False

    for dir in required_dirs:
        if (bin_path / dir).exists():
            print(f"  ✓ {dir}/")
        else:
            print(f"  ✗ Missing: {dir}/")
            all_good = False

    return all_good


def set_environment_variable(maxine_path: Path):
    """Set MAXINE_HOME environment variable (Windows)."""
    if sys.platform != "win32":
        print("\nNote: This script is for Windows. Set MAXINE_HOME manually on Linux/Mac.")
        return

    print(f"\nSetting MAXINE_HOME environment variable...")
    print(f"  Path: {maxine_path}")

    # Set for current session
    os.environ["MAXINE_HOME"] = str(maxine_path.parent)

    # Set permanently using PowerShell
    try:
        import subprocess
        ps_command = f'[Environment]::SetEnvironmentVariable("MAXINE_HOME", "{maxine_path.parent}", "User")'
        subprocess.run(
            ["powershell", "-Command", ps_command],
            check=True,
            capture_output=True
        )
        print("  ✓ MAXINE_HOME set permanently for current user")
        print(f"    Value: {maxine_path.parent}")
    except Exception as e:
        print(f"  ⚠ Could not set permanently: {e}")
        print(f"    Please set MAXINE_HOME manually to: {maxine_path.parent}")

    return True


def update_config_yaml(maxine_bin_path: Path):
    """Update vhs_upscaler config.yaml with Maxine paths."""
    config_path = Path("vhs_upscaler/config.yaml")

    if not config_path.exists():
        print("\n⚠ config.yaml not found, skipping update")
        return

    print(f"\nUpdating {config_path}...")

    with open(config_path, 'r') as f:
        content = f.read()

    # Update maxine_path
    if 'maxine_path: ""' in content:
        content = content.replace(
            'maxine_path: ""',
            f'maxine_path: "{maxine_bin_path}"'
        )

    # Update model_dir
    model_dir = maxine_bin_path / "models"
    if 'model_dir: ""' in content:
        content = content.replace(
            'model_dir: ""',
            f'model_dir: "{model_dir}"'
        )

    with open(config_path, 'w') as f:
        f.write(content)

    print("  ✓ Config updated with Maxine paths")


def main():
    """Main setup flow."""
    print("=" * 60)
    print("NVIDIA Maxine SDK Setup Helper")
    print("=" * 60)
    print()

    # Step 1: Find or prompt for zip file
    zip_path = find_maxine_zip()

    if not zip_path:
        print("\n⚠ Could not find Maxine SDK zip file automatically.")
        print("\nPlease:")
        print("1. Download Maxine Video Effects SDK from:")
        print("   https://developer.nvidia.com/maxine-getting-started")
        print("2. Place the zip file in Downloads, Desktop, or current directory")
        print("3. Run this script again")
        print("\nOr provide the path manually:")

        user_input = input("Enter path to Maxine zip file (or press Enter to exit): ").strip()
        if not user_input:
            return

        zip_path = Path(user_input)
        if not zip_path.exists():
            print(f"Error: File not found: {zip_path}")
            return

    # Step 2: Extract to local NVIDIA directory
    dest_path = Path.home() / "AppData/Local/NVIDIA/Maxine"

    if dest_path.exists():
        print(f"\n⚠ Maxine already exists at {dest_path}")
        overwrite = input("Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Aborted.")
            return
        shutil.rmtree(dest_path)

    extract_maxine(zip_path, dest_path)

    # Step 3: Find bin directory
    bin_path = find_maxine_bin(dest_path)

    if not bin_path:
        print("\n✗ Could not find VideoEffectsApp.exe in extracted files")
        print(f"  Please check the structure of {dest_path}")
        return

    print(f"\n✓ Found Maxine SDK at: {bin_path}")

    # Step 4: Verify structure
    if not verify_maxine_structure(bin_path):
        print("\n⚠ Some required files are missing")
        cont = input("Continue anyway? (y/n): ").lower()
        if cont != 'y':
            return

    # Step 5: Set environment variable
    set_environment_variable(bin_path)

    # Step 6: Update config.yaml
    update_config_yaml(bin_path)

    # Step 7: Test
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. RESTART YOUR TERMINAL for environment variable to take effect")
    print("2. Run: python verify_setup.py")
    print("3. Test with: python -m vhs_upscaler.vhs_upscale --engine maxine")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
