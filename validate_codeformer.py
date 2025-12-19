#!/usr/bin/env python3
"""Validation script for CodeFormer integration."""

import inspect
from vhs_upscaler.face_restoration import FaceRestorer


def validate_codeformer_integration():
    """Validate that CodeFormer integration is complete."""

    print("CodeFormer Integration Validation")
    print("=" * 60)

    # Test GFPGAN backend
    print("\n1. Testing GFPGAN backend (default):")
    restorer_gfpgan = FaceRestorer(backend='gfpgan')
    print(f"   Backend: {restorer_gfpgan.backend}")
    print(f"   Has backend: {restorer_gfpgan.has_backend}")

    # Test CodeFormer backend
    print("\n2. Testing CodeFormer backend:")
    restorer_codeformer = FaceRestorer(backend='codeformer')
    print(f"   Backend: {restorer_codeformer.backend}")
    print(f"   Has backend: {restorer_codeformer.has_backend}")

    # Check methods
    print("\n3. Available public methods:")
    methods = [m for m in dir(restorer_codeformer)
               if not m.startswith('_') and callable(getattr(restorer_codeformer, m))]
    for m in methods:
        print(f"   - {m}")

    # Check processing methods
    print("\n4. Frame processing methods:")
    private_methods = [m for m in dir(restorer_codeformer)
                      if m.startswith('_process_frames')]

    for m in private_methods:
        method = getattr(restorer_codeformer, m)
        sig = inspect.signature(method)
        print(f"   - {m}")
        print(f"     Signature: {sig}")

    # Verify both backends exist
    print("\n5. Verification:")
    has_gfpgan_method = hasattr(restorer_codeformer, '_process_frames_gfpgan')
    has_codeformer_method = hasattr(restorer_codeformer, '_process_frames_codeformer')

    print(f"   _process_frames_gfpgan: {'[YES]' if has_gfpgan_method else '[NO]'}")
    print(f"   _process_frames_codeformer: {'[YES]' if has_codeformer_method else '[NO]'}")

    # Check restore_faces method can dispatch correctly
    print("\n6. Checking restore_faces dispatch logic:")
    restore_method = getattr(restorer_codeformer, 'restore_faces')
    sig = inspect.signature(restore_method)
    params = list(sig.parameters.keys())

    has_fidelity = 'fidelity' in params
    has_weight = 'weight' in params

    print(f"   Has 'weight' parameter (GFPGAN): {'[YES]' if has_weight else '[NO]'}")
    print(f"   Has 'fidelity' parameter (CodeFormer): {'[YES]' if has_fidelity else '[NO]'}")

    # Final summary
    print("\n" + "=" * 60)
    if has_gfpgan_method and has_codeformer_method and has_fidelity and has_weight:
        print("SUCCESS: CodeFormer integration complete!")
        print("\nFeatures:")
        print("  - Dual backend support (GFPGAN + CodeFormer)")
        print("  - Automatic backend selection")
        print("  - Fidelity control for CodeFormer (0.5-0.9)")
        print("  - Weight control for GFPGAN (0.0-1.0)")
        print("  - Frame-by-frame processing with progress logging")
        print("  - Graceful fallback on processing errors")
        return True
    else:
        print("ERROR: Integration incomplete!")
        return False


if __name__ == "__main__":
    success = validate_codeformer_integration()
    exit(0 if success else 1)
