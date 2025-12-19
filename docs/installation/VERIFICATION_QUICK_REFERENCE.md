# Installation Verification - Quick Reference

One-page reference for the TerminalAI installation verification system.

## Quick Commands

```bash
# Full verification
python verify_installation.py

# Quick check (less verbose)
python verify_installation.py --quick

# Minimal output
python verify_installation.py --quiet

# Check specific component
python verify_installation.py --check pytorch

# Generate JSON report
python verify_installation.py --report diagnostic.json

# Show feature matrix
python verify_installation.py --matrix
```

## Component Status Symbols

- `[OK]` - Available and functional
- `[PARTIAL]` - Available but missing features (e.g., CPU-only PyTorch)
- `[NOT INSTALLED]` - Component not found
- `[ERROR]` - Verification error

## Components Verified

| Component | Purpose | Required For |
|-----------|---------|--------------|
| Python | Runtime | Everything |
| FFmpeg | Video/audio processing | All video operations |
| GPU | Hardware acceleration | Fast processing |
| PyTorch | AI framework | AI features (Demucs, AudioSR, Face Restoration) |
| VapourSynth | Advanced filters | QTGMC deinterlacing |
| GFPGAN | Face restoration | Face enhancement (fast) |
| CodeFormer | Face restoration | Face enhancement (best quality) |
| DeepFilterNet | AI denoising | Audio noise reduction |
| AudioSR | AI upsampling | Audio quality enhancement |
| Demucs | Stem separation | Surround upmix |

## Features Detected

| Feature | Components Required |
|---------|---------------------|
| basic_video_processing | FFmpeg |
| gpu_acceleration | NVIDIA GPU |
| hardware_encoding | FFmpeg + GPU + NVENC |
| ai_upscaling | PyTorch or GPU |
| advanced_deinterlacing | VapourSynth + havsfunc |
| face_restoration | GFPGAN or CodeFormer + PyTorch |
| ai_audio_denoising | DeepFilterNet + PyTorch |
| ai_audio_upsampling | AudioSR + PyTorch |
| ai_surround_upmix | Demucs + PyTorch |

## Quick Installation Commands

### PyTorch (CPU)
```bash
pip install torch torchaudio
```

### PyTorch (CUDA 11.8)
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### PyTorch (CUDA 12.1)
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### VapourSynth
```bash
# Install runtime: https://github.com/vapoursynth/vapoursynth/releases
pip install vapoursynth havsfunc
```

### Face Restoration
```bash
# GFPGAN (faster, good quality)
pip install gfpgan basicsr opencv-python

# CodeFormer (slower, best quality)
# PyTorch required, models auto-download
```

### Audio Enhancement
```bash
pip install deepfilternet  # AI denoising
pip install audiosr        # AI upsampling
pip install demucs         # AI stem separation
```

## Python API

### Get Feature Availability
```python
from verify_installation import get_available_features

features = get_available_features()
print(f"GPU: {features['gpu_acceleration']}")
print(f"Face Restoration: {features['face_restoration']}")
```

### Check Specific Component
```python
from verify_installation import check_component

result = check_component('pytorch')
if result.is_available:
    print(f"PyTorch {result.version}")
    if result.details.get('cuda_available'):
        print("CUDA enabled")
else:
    print("PyTorch not available")
    for suggestion in result.suggestions:
        print(f"  - {suggestion}")
```

### Conditional Feature Usage
```python
features = get_available_features()

if features['hardware_encoding']:
    encoder = "hevc_nvenc"
else:
    encoder = "libx265"

if features['advanced_deinterlacing']:
    deinterlace = "qtgmc"
else:
    deinterlace = "yadif"
```

## Common Issues & Quick Fixes

### PyTorch CUDA Not Available
```bash
# Check current version
python -c "import torch; print(torch.__version__)"

# Install CUDA version
pip uninstall torch torchaudio
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### GFPGAN Model Not Found
```bash
python -m vhs_upscaler.face_restoration --download-model
```

### VapourSynth Missing QTGMC
```bash
pip install havsfunc
```

### Demucs Extremely Slow
```bash
# Verify GPU available
python verify_installation.py --check gpu

# If no GPU, don't use Demucs (100x slower on CPU)
# Use simpler upmix: --upmix-mode surround
```

## Troubleshooting Workflow

1. Run verification:
   ```bash
   python verify_installation.py --report issue.json
   ```

2. Check specific failing component:
   ```bash
   python verify_installation.py --check component_name
   ```

3. Review suggestions in output

4. Consult full guide:
   - `docs/INSTALLATION_TROUBLESHOOTING.md`

## Verification Report Structure

```json
{
  "system_info": {
    "platform": "Windows-11",
    "python_version": "3.10.11"
  },
  "components": {
    "PyTorch": {
      "status": "available",
      "version": "2.0.1",
      "details": {
        "cuda_available": true
      }
    }
  },
  "feature_availability": {
    "gpu_acceleration": true,
    "face_restoration": true
  },
  "recommendations": [...]
}
```

## CI/CD Integration

```bash
#!/bin/bash
python verify_installation.py --quiet
if [ $? -eq 0 ]; then
    echo "Core requirements satisfied"
    # Run tests or processing
else
    echo "Missing required dependencies"
    exit 1
fi
```

## Exit Codes

- `0` - Core requirements met (Python + FFmpeg)
- `1` - Core requirements missing

## Performance Checks

### GPU Benchmark
```bash
python verify_installation.py --check pytorch
# Look for: performance_test results
# Good: < 5ms per iteration
# Slow: > 20ms (check GPU usage)
```

### Monitor GPU Usage
```bash
# NVIDIA
nvidia-smi -l 1

# Check NVENC availability
ffmpeg -encoders | grep nvenc
```

## Documentation Links

- **Full Guide:** `docs/VERIFICATION_GUIDE.md`
- **Troubleshooting:** `docs/INSTALLATION_TROUBLESHOOTING.md`
- **Documentation Index:** `docs/README.md`
- **Main README:** `README.md`

## Support

Include in bug reports:
1. Verification report: `python verify_installation.py --report diagnostic.json`
2. Full error message
3. Steps to reproduce

---

**Quick Start:** `python verify_installation.py`

**Full Documentation:** `docs/VERIFICATION_GUIDE.md`
