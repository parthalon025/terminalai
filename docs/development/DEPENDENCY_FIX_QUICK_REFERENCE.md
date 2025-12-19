# Dependency Fix Quick Reference
**TerminalAI v1.5.1** | **Updated:** 2025-12-19

## Quick Verification Commands

```bash
# System information
python -m vhs_upscaler --info

# Check dependencies
python -m vhs_upscaler --check-deps

# Full verification
python scripts/verify_dependencies.py

# JSON export
python scripts/verify_dependencies.py --json

# Fix import issues
python scripts/verify_dependencies.py --fix-imports
```

## Feature Detection API

```python
from vhs_upscaler import get_available_features, HAS_AUDIO_PROCESSOR

# Get all features
features = get_available_features()
print(features)
# {
#   'audio_processing': True,
#   'hardware_detection': True,
#   'face_restoration': True,
#   'notifications': False,
#   'presets': True,
#   'deinterlacing': False
# }

# Check specific feature
if HAS_AUDIO_PROCESSOR:
    from vhs_upscaler import AudioProcessor
    # Use audio features
```

## Installation Quick Reference

### Core Installation
```bash
pip install -e .
```

### With PyTorch CUDA
```bash
# RTX 40/30/20 series
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# RTX 50 series
pip install torch torchvision torchaudio --pre --index-url https://download.pytorch.org/whl/nightly/cu128
```

### Optional Features
```bash
pip install -e ".[audio]"      # AI audio (Demucs)
pip install -e ".[face]"       # Face restoration
pip install -e ".[upscaling]"  # Real-ESRGAN
pip install -e ".[full]"       # All features
pip install -e ".[dev]"        # Development tools
```

## Common Issues & Fixes

### NumPy 2.x Installed
```bash
pip install "numpy<2.0"
```

### Import Errors After Update
```bash
python scripts/verify_dependencies.py --fix-imports
```

### basicsr Import Errors
```bash
python setup.py  # Re-run to apply patches
```

### Missing Features
```bash
python -m vhs_upscaler --check-deps  # See what's missing
pip install -e ".[full]"             # Install all features
```

## Entry Points

| Command | Description |
|---------|-------------|
| `python -m vhs_upscaler` | Launch GUI (default) |
| `python -m vhs_upscaler --info` | System information |
| `python -m vhs_upscaler --check-deps` | Check dependencies |
| `python -m vhs_upscaler --cli` | CLI upscaler |
| `python -m vhs_upscaler.gui` | GUI direct |
| `python -m vhs_upscaler.vhs_upscale` | CLI direct |

## Python Version Compatibility

| Python | Status | Notes |
|--------|--------|-------|
| 3.10 | ✅ Fully Supported | Stable |
| 3.11 | ✅ Recommended | Best performance |
| 3.12 | ✅ Fully Supported | Requires torch>=2.2.2 |
| 3.13 | ✅ Supported | Auto-patched |
| 3.14+ | ⚠️ Untested | May work |

## Critical Version Constraints

```
numpy>=1.24.0,<2.0          # Must be <2.0
torch>=2.0.0                # 2.2.2+ for Python 3.12+
gradio>=4.0.0,<7.0          # Pin to 6.x
nvidia-ml-py>=12.0.0        # Replaces pynvml
```

## Feature Flags Reference

```python
from vhs_upscaler import (
    HAS_AUDIO_PROCESSOR,      # Audio enhancement available
    HAS_HARDWARE_DETECTION,   # GPU detection available
    HAS_FACE_RESTORATION,     # Face restoration available
    HAS_NOTIFICATIONS,        # Webhook/email notifications
    HAS_PRESETS,              # Preset system available
    HAS_DEINTERLACE,          # Deinterlacing available
)
```

## Files Modified

- ✅ `vhs_upscaler/__init__.py` - Enhanced feature detection
- ✅ `vhs_upscaler/__main__.py` - Created entry point
- ✅ `requirements.txt` - Version constraints
- ✅ `pyproject.toml` - Dependencies
- ✅ `setup.py` - Auto-patches
- ✅ `scripts/verify_dependencies.py` - Verification tool

## Testing Commands

```bash
# Run all tests
pytest tests/ -v

# Test specific module
pytest tests/test_queue_manager.py -v

# Test with coverage
pytest tests/ --cov=vhs_upscaler --cov-report=html
```

## Graceful Degradation Pattern

```python
# Pattern used throughout codebase
try:
    from .module import Feature
    HAS_FEATURE = True
except ImportError:
    HAS_FEATURE = False
    Feature = None  # Prevent AttributeError

# Usage in code
if HAS_FEATURE:
    feature = Feature()
else:
    # Fallback or skip
    pass
```

## Summary

**Status:** All dependency and import issues fixed ✅

**Key Improvements:**
- Graceful degradation for optional features
- Clear feature detection API
- Comprehensive verification tools
- Python 3.10-3.13 compatibility
- Automatic patches applied
- All entry points working

**Documentation:**
- Full details: `docs/development/DEPENDENCY_FIX_SUMMARY.md`
- This guide: `docs/development/DEPENDENCY_FIX_QUICK_REFERENCE.md`
