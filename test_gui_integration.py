#!/usr/bin/env python3
"""
GUI Integration Test Script
============================
Validates GUI optimizations and conditional visibility controls.

Usage:
    python test_gui_integration.py

This script verifies:
- GUI module imports correctly
- All conditional visibility handlers are present
- Quick Fix presets are configured
- Event handlers are wired properly
"""

import sys
from pathlib import Path

# Add vhs_upscaler to path
sys.path.insert(0, str(Path(__file__).parent / "vhs_upscaler"))

def test_imports():
    """Test that GUI module imports successfully."""
    print("Testing GUI module imports...")
    try:
        import gui
        print(f"  [PASS] GUI module imported (version {gui.__version__})")
        return True
    except Exception as e:
        print(f"  [FAIL] Import error: {e}")
        return False


def test_conditional_groups():
    """Test that all conditional groups are defined."""
    print("\nTesting conditional visibility groups...")

    expected_groups = [
        'rtxvideo_options',
        'realesrgan_options',
        'ffmpeg_options',
        'hdr_options',
        'face_restore_options',
        'qtgmc_options',
        'audio_enhance_options',
        'demucs_options',
        'surround_options',
        'audio_sr_model',
        'rtxvideo_artifact_strength'
    ]

    # Read GUI file and check for group definitions
    gui_path = Path(__file__).parent / "vhs_upscaler" / "gui.py"
    with open(gui_path, 'r', encoding='utf-8') as f:
        content = f.read()

    found_groups = []
    missing_groups = []

    for group in expected_groups:
        # Check for group definition patterns
        if f'as {group}' in content or f'{group} =' in content:
            found_groups.append(group)
            print(f"  [PASS] Found group: {group}")
        else:
            missing_groups.append(group)
            print(f"  [FAIL] Missing group: {group}")

    if not missing_groups:
        print(f"\n  [PASS] All {len(expected_groups)} conditional groups found")
        return True
    else:
        print(f"\n  [FAIL] Missing {len(missing_groups)} groups")
        return False


def test_event_handlers():
    """Test that all event handlers are defined."""
    print("\nTesting event handler functions...")

    expected_handlers = [
        'update_engine_options',
        'update_hdr_options',
        'update_audio_enhance_options',
        'update_demucs_options',
        'update_surround_options',
        'update_audiosr_options',
        'update_rtx_artifact_strength',
        'update_face_restore_options',
        'update_qtgmc_options'
    ]

    # Read GUI file
    gui_path = Path(__file__).parent / "vhs_upscaler" / "gui.py"
    with open(gui_path, 'r', encoding='utf-8') as f:
        content = f.read()

    found_handlers = []
    missing_handlers = []

    for handler in expected_handlers:
        if f'def {handler}' in content:
            found_handlers.append(handler)
            print(f"  [PASS] Found handler: {handler}")
        else:
            missing_handlers.append(handler)
            print(f"  [FAIL] Missing handler: {handler}")

    if not missing_handlers:
        print(f"\n  [PASS] All {len(expected_handlers)} event handlers found")
        return True
    else:
        print(f"\n  [FAIL] Missing {len(missing_handlers)} handlers")
        return False


def test_quick_fix_presets():
    """Test that Quick Fix presets are configured."""
    print("\nTesting Quick Fix presets...")

    try:
        import gui
        presets = gui.get_quick_fix_presets()

        expected_presets = [
            'vhs_home',
            'vhs_noisy',
            'dvd_rip',
            'youtube_old',
            'anime',
            'webcam',
            'clean',
            'best_quality'
        ]

        found_presets = []
        missing_presets = []

        for preset in expected_presets:
            if preset in presets:
                config = presets[preset]
                # Verify preset has required fields
                required_fields = ['name', 'preset', 'resolution', 'info']
                if all(field in config for field in required_fields):
                    found_presets.append(preset)
                    print(f"  [PASS] Preset: {preset} - {config['name']}")
                else:
                    print(f"  [WARN] Preset {preset} missing required fields")
            else:
                missing_presets.append(preset)
                print(f"  [FAIL] Missing preset: {preset}")

        if not missing_presets:
            print(f"\n  [PASS] All {len(expected_presets)} Quick Fix presets configured")
            return True
        else:
            print(f"\n  [FAIL] Missing {len(missing_presets)} presets")
            return False
    except Exception as e:
        print(f"  [FAIL] Error loading presets: {e}")
        return False


def test_accordions():
    """Test that all accordions are defined."""
    print("\nTesting accordion organization...")

    # Check for accordion patterns (with or without emoji)
    expected_accordions = [
        'Encoding & Quality Settings',
        'AI Upscaler Settings',
        'HDR & Color Settings',
        'Face Restoration',
        'Deinterlacing',
        'Audio Processing'
    ]

    # Read GUI file
    gui_path = Path(__file__).parent / "vhs_upscaler" / "gui.py"
    with open(gui_path, 'r', encoding='utf-8') as f:
        content = f.read()

    found_accordions = []
    missing_accordions = []

    for accordion in expected_accordions:
        # Check if accordion text appears anywhere (with or without emoji prefix)
        if accordion in content:
            found_accordions.append(accordion)
            print(f"  [PASS] Found accordion: {accordion}")
        else:
            missing_accordions.append(accordion)
            print(f"  [FAIL] Missing accordion: {accordion}")

    if not missing_accordions:
        print(f"\n  [PASS] All {len(expected_accordions)} accordions defined")
        return True
    else:
        print(f"\n  [FAIL] Missing {len(missing_accordions)} accordions")
        return False


def test_gui_creation():
    """Test that GUI can be created without errors."""
    print("\nTesting GUI creation...")

    try:
        import gui
        # Don't actually launch, just create the interface
        app = gui.create_gui()
        print("  [PASS] GUI created successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Error creating GUI: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 70)
    print("GUI INTEGRATION TEST SUITE")
    print("=" * 70)

    tests = [
        ("Import Test", test_imports),
        ("Conditional Groups", test_conditional_groups),
        ("Event Handlers", test_event_handlers),
        ("Quick Fix Presets", test_quick_fix_presets),
        ("Accordions", test_accordions),
        ("GUI Creation", test_gui_creation)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  [ERROR] Test '{name}' crashed: {e}")
            results.append((name, False))

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    print(f"\nTotal: {passed}/{total} tests passed ({passed*100//total}%)")

    if passed == total:
        print("\n[SUCCESS] All tests passed! GUI optimizations verified.")
        print("\nNext steps:")
        print("  1. Run: python -m vhs_upscaler.gui")
        print("  2. Test conditional visibility manually")
        print("  3. Test Quick Fix presets")
        print("  4. Submit a test job")
        return 0
    else:
        print(f"\n[FAILURE] {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
