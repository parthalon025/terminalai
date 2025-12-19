# basicsr Torchvision Compatibility Patch

## Overview

The installer automatically patches basicsr 1.4.2 to fix compatibility issues with torchvision >= 0.17.

## The Problem

basicsr 1.4.2 imports `rgb_to_grayscale` from `torchvision.transforms.functional_tensor`, which was removed in torchvision 0.17+:

```python
# Line 8 in basicsr/data/degradations.py (original)
from torchvision.transforms.functional_tensor import rgb_to_grayscale
```

This causes an ImportError when using modern PyTorch/torchvision versions.

## The Solution

The installer automatically patches the import to use a try/except fallback:

```python
# Fix for torchvision >= 0.17 where functional_tensor was removed
try:
    from torchvision.transforms.functional import rgb_to_grayscale
except ImportError:
    from torchvision.transforms.functional_tensor import rgb_to_grayscale
```

This ensures compatibility with both old and new torchvision versions.

## When the Patch is Applied

The patch is automatically applied during:
- `python install.py --full` (full installation)
- After installing Real-ESRGAN or GFPGAN (which install basicsr as a dependency)

## Patch Behavior

**Idempotent**: Safe to run multiple times - won't re-patch if already patched.

**Graceful Fallback**: If basicsr is not installed, the patch is silently skipped.

**Non-Critical**: Patching failures are logged as warnings but don't stop installation.

## Manual Patching

If you need to manually apply the patch:

```python
from scripts.installation.install import TerminalAIInstaller

installer = TerminalAIInstaller(install_type="full")
installer.patch_basicsr_torchvision()
```

Or edit the file directly at:
```
site-packages/basicsr/data/degradations.py
```

## Verification

To verify the patch was applied:

```python
import basicsr
from pathlib import Path

basicsr_dir = Path(basicsr.__file__).parent
degradations_file = basicsr_dir / "data" / "degradations.py"
content = degradations_file.read_text()

if "Fix for torchvision >= 0.17" in content:
    print("✓ Patch applied successfully")
else:
    print("✗ Patch not applied")
```

## Affected Features

This patch is required for:
- GFPGAN face restoration
- Real-ESRGAN AI upscaling (Python bindings)
- CodeFormer face restoration

Without the patch, these features will fail with ImportError when using torchvision >= 0.17.

## Related Issues

- torchvision removed `functional_tensor` module in v0.17
- basicsr 1.4.2 hasn't been updated to support new torchvision
- See: https://github.com/pytorch/vision/issues/6753
