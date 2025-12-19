# Installation Verification Guide

Quick reference for using the TerminalAI installation verification system.

## Overview

The verification system (`verify_installation.py`) provides comprehensive testing of all optional features and dependencies, helping you identify and resolve installation issues.

## Quick Start

### Basic Usage

```bash
# Full verification with detailed output
python verify_installation.py

# Quick check (less verbose)
python verify_installation.py --quick

# Minimal output (just results)
python verify_installation.py --quiet

# Save detailed report to JSON
python verify_installation.py --report installation_report.json

# Show feature compatibility matrix
python verify_installation.py --matrix

# Check specific component
python verify_installation.py --check pytorch
```

### Integration with Python

```python
from verify_installation import get_available_features, check_component

# Get all available features
features = get_available_features()
print(f"GPU Acceleration: {features['gpu_acceleration']}")
print(f"Face Restoration: {features['face_restoration']}")
print(f"AI Audio: {features['ai_audio_denoising']}")

# Check specific component
result = check_component("pytorch")
if result.is_available:
    print(f"PyTorch {result.version} available")
    if result.details.get("cuda_available"):
        print("CUDA acceleration enabled")
else:
    print("PyTorch not available")
    for suggestion in result.suggestions:
        print(f"  - {suggestion}")
```

## Components Verified

### Core Components

| Component | Purpose | Required For |
|-----------|---------|--------------|
| Python | Runtime environment | Everything |
| FFmpeg | Video/audio processing | All video operations |
| GPU | Hardware acceleration | Fast processing |

### AI Processing

| Component | Purpose | GPU Required |
|-----------|---------|--------------|
| PyTorch | AI framework | Recommended |
| VapourSynth | Advanced deinterlacing | No |
| GFPGAN | Face restoration | Recommended |
| CodeFormer | Advanced face restoration | Highly recommended |

### Audio Enhancement

| Component | Purpose | GPU Required |
|-----------|---------|--------------|
| DeepFilterNet | AI audio denoising | Recommended |
| AudioSR | AI audio upsampling | Recommended |
| Demucs | AI stem separation | Essential |

## Feature Availability Matrix

The verification system checks these feature combinations:

### Basic Video Processing
- **Requirements:** FFmpeg
- **Optional:** GPU for hardware encoding
- **Status:** Always available if FFmpeg installed

### GPU Hardware Encoding
- **Requirements:** FFmpeg + NVIDIA GPU + NVENC drivers
- **Performance:** 5-10x faster than CPU
- **Status:** Check with `--check gpu`

### AI Upscaling
- **Requirements:** PyTorch (for some engines)
- **Optional:** CUDA GPU (100x faster)
- **Engines:** Maxine (NVIDIA), Real-ESRGAN (Vulkan), FFmpeg (CPU)
- **Status:** Check with `--check pytorch`

### Advanced Deinterlacing (QTGMC)
- **Requirements:** VapourSynth + havsfunc
- **Performance:** Slower but highest quality
- **Use Case:** VHS tapes, interlaced video
- **Status:** Check with `--check vapoursynth`

### Face Restoration
- **Requirements:** GFPGAN or CodeFormer + PyTorch
- **Optional:** CUDA GPU (essential for CodeFormer)
- **Quality:** CodeFormer > GFPGAN
- **Speed:** GFPGAN faster on CPU
- **Status:** Check with `--check gfpgan` or `--check codeformer`

### AI Audio Denoising
- **Requirements:** DeepFilterNet + PyTorch
- **Optional:** CUDA GPU
- **Use Case:** VHS audio, speech clarity
- **Status:** Check with `--check deepfilternet`

### AI Audio Upsampling
- **Requirements:** AudioSR + PyTorch
- **Optional:** CUDA GPU
- **Use Case:** Upsample 16kHz/22kHz to 48kHz
- **Status:** Check with `--check audiosr`

### AI Surround Upmix
- **Requirements:** Demucs + PyTorch
- **GPU:** ESSENTIAL (CPU impractically slow)
- **Quality:** Best surround upmix available
- **Status:** Check with `--check demucs`

## Understanding Results

### Component Status Codes

- **[OK]** - Component available and functional
- **[PARTIAL]** - Component available but missing features (e.g., CPU-only PyTorch)
- **[NOT INSTALLED]** - Component not found
- **[ERROR]** - Verification error occurred

### Example Output

```
PyTorch:
  [OK] v2.0.1
    cuda_available: True
    gpu_count: 1
    gpu_devices: ['NVIDIA GeForce RTX 3080']
    💡 GPU acceleration available on 1 device(s)
    ⚡ Optimal configuration for AI processing

VapourSynth:
  [PARTIAL]
    Missing: havsfunc (QTGMC support)
    💡 Install: pip install havsfunc

GFPGAN:
  [PARTIAL]
    GFPGAN installed but no models found
    💡 Download model: python -m vhs_upscaler.face_restoration --download-model
```

## Verification Report Structure

When saved with `--report`, the JSON contains:

```json
{
  "system_info": {
    "platform": "Windows-10-10.0.19045-SP0",
    "python_version": "3.10.11",
    "machine": "AMD64"
  },
  "components": {
    "PyTorch": {
      "status": "available",
      "version": "2.0.1",
      "details": {
        "cuda_available": true,
        "gpu_count": 1
      },
      "suggestions": [],
      "performance_notes": ["GPU acceleration available"]
    }
  },
  "feature_availability": {
    "basic_video_processing": true,
    "gpu_acceleration": true,
    "ai_upscaling": true,
    "face_restoration": true
  },
  "warnings": [],
  "errors": [],
  "recommendations": []
}
```

## Common Workflows

### Pre-Installation Check

Before installing optional features, check what's available:

```bash
python verify_installation.py --quick
```

### Post-Installation Verification

After installing new components:

```bash
# Verify specific component
python verify_installation.py --check pytorch

# Full verification
python verify_installation.py
```

### Troubleshooting

When features don't work:

```bash
# Full diagnostic report
python verify_installation.py --report diagnostic.json

# Check specific component
python verify_installation.py --check demucs
```

Include `diagnostic.json` in bug reports.

### CI/CD Integration

Use verification in automated testing:

```bash
# Exit code 0 if core requirements met, 1 otherwise
python verify_installation.py --quiet
echo $?  # 0 = success, 1 = failure
```

```python
# In test scripts
from verify_installation import get_available_features

features = get_available_features()

# Skip tests if features unavailable
import pytest

@pytest.mark.skipif(not features['gpu_acceleration'],
                    reason="GPU not available")
def test_gpu_encoding():
    # Test GPU features
    pass

@pytest.mark.skipif(not features['face_restoration'],
                    reason="GFPGAN not installed")
def test_face_restoration():
    # Test face restoration
    pass
```

## Performance Testing

The verification system includes basic performance tests:

### PyTorch CUDA Performance

Runs matrix multiplication benchmark on GPU:

```
PyTorch:
  [OK] v2.0.1
    performance_test:
      matrix_size: 1000x1000
      iterations: 10
      avg_time_ms: 2.5
```

- **Good:** < 5ms per iteration
- **Acceptable:** 5-20ms
- **Slow:** > 20ms (check GPU utilization)

### Interpreting Performance Results

- Fast performance indicates GPU working correctly
- Slow performance may indicate:
  - GPU not being used (check CUDA availability)
  - GPU under load from other processes
  - Driver issues

## Integration Examples

### In Application Code

```python
from verify_installation import check_component

# Determine which face restoration backend to use
gfpgan = check_component("gfpgan")
codeformer = check_component("codeformer")

if codeformer.is_available and codeformer.details.get("cuda_available"):
    backend = "codeformer"  # Best quality, GPU available
elif gfpgan.is_available:
    backend = "gfpgan"  # Good quality, CPU acceptable
else:
    backend = None  # Skip face restoration

# Determine audio enhancement
deepfilternet = check_component("deepfilternet")
if deepfilternet.is_available:
    audio_mode = "deepfilternet"  # AI denoising
else:
    audio_mode = "moderate"  # FFmpeg-based
```

### In GUI

```python
from verify_installation import get_available_features

features = get_available_features()

# Show/hide UI elements based on availability
if features['face_restoration']:
    show_face_restoration_options()
else:
    hide_face_restoration_options()
    show_install_tip("Install GFPGAN for face restoration")

if features['ai_surround_upmix']:
    enable_demucs_upmix()
else:
    disable_demucs_upmix()
    if not features['gpu_acceleration']:
        show_warning("Demucs requires GPU")
```

### Feature Detection Function

```python
def get_optimal_settings():
    """Determine optimal settings based on available features."""
    features = get_available_features()
    pytorch = check_component("pytorch")
    gpu = check_component("gpu")

    settings = {
        "encoder": "libx265",  # Default CPU
        "upscale_engine": "ffmpeg",
        "deinterlace_mode": "yadif",
        "audio_enhance": "moderate"
    }

    # Upgrade settings based on availability
    if features['hardware_encoding']:
        settings["encoder"] = "hevc_nvenc"  # GPU encoding

    if features['gpu_acceleration'] and pytorch.details.get("cuda_available"):
        settings["upscale_engine"] = "maxine"  # Best quality

    if features['advanced_deinterlacing']:
        settings["deinterlace_mode"] = "qtgmc"  # Best quality

    if features['ai_audio_denoising']:
        settings["audio_enhance"] = "deepfilternet"  # AI denoising

    return settings
```

## Tips and Best Practices

### Before Processing Videos

1. **Run verification first:**
   ```bash
   python verify_installation.py
   ```

2. **Check GPU status if processing is slow:**
   ```bash
   python verify_installation.py --check gpu
   nvidia-smi  # Monitor GPU usage
   ```

3. **Verify models downloaded:**
   - GFPGAN models: `ls models/gfpgan/`
   - CodeFormer models: `ls models/codeformer/`

### When Installing New Features

1. **Verify before:**
   ```bash
   python verify_installation.py --check pytorch
   # Shows: [NOT INSTALLED]
   ```

2. **Install:**
   ```bash
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Verify after:**
   ```bash
   python verify_installation.py --check pytorch
   # Shows: [OK] v2.0.1
   #   cuda_available: True
   ```

### Troubleshooting Workflow

1. **Run full verification:**
   ```bash
   python verify_installation.py --report issue.json
   ```

2. **Check specific failing component:**
   ```bash
   python verify_installation.py --check component_name
   ```

3. **Review suggestions:**
   - Each component provides installation suggestions
   - Follow suggestions in order

4. **Consult troubleshooting guide:**
   - See `docs/INSTALLATION_TROUBLESHOOTING.md`
   - Search for specific error messages

## Exit Codes

The verification script returns:

- **0** - Core requirements satisfied (Python + FFmpeg)
- **1** - Core requirements missing

Use in scripts:

```bash
#!/bin/bash
python verify_installation.py --quiet

if [ $? -eq 0 ]; then
    echo "Ready to process videos"
    python -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4
else
    echo "Please install required dependencies first"
    exit 1
fi
```

## API Reference

### Functions

#### `get_available_features() -> Dict[str, bool]`

Returns dictionary of feature availability without verbose output.

**Returns:**
- `basic_video_processing`: FFmpeg available
- `gpu_acceleration`: NVIDIA GPU detected
- `hardware_encoding`: NVENC available
- `ai_upscaling`: PyTorch or GPU available for AI upscaling
- `advanced_deinterlacing`: VapourSynth + QTGMC available
- `face_restoration`: GFPGAN or CodeFormer available
- `ai_audio_denoising`: DeepFilterNet available
- `ai_audio_upsampling`: AudioSR available
- `ai_surround_upmix`: Demucs available

#### `check_component(component_name: str) -> ComponentResult`

Check specific component and return detailed results.

**Parameters:**
- `component_name`: python, pytorch, vapoursynth, gfpgan, codeformer, deepfilternet, audiosr, demucs, ffmpeg, gpu

**Returns:** `ComponentResult` with:
- `name`: Component name
- `status`: ComponentStatus enum
- `version`: Version string (if available)
- `details`: Dict with component-specific details
- `suggestions`: List of installation suggestions
- `performance_notes`: List of performance-related notes

### Classes

#### `ComponentStatus` (Enum)

- `AVAILABLE`: Component fully functional
- `PARTIAL`: Component available but missing features
- `UNAVAILABLE`: Component not installed
- `ERROR`: Verification error
- `NOT_TESTED`: Not yet tested

#### `ComponentResult` (Dataclass)

Result of component verification with detailed information.

#### `VerificationReport` (Dataclass)

Complete verification report with system info, components, features, and recommendations.

## See Also

- **Troubleshooting Guide:** `docs/INSTALLATION_TROUBLESHOOTING.md`
- **Main README:** `README.md`
- **Test Suite:** `tests/test_installation_verification.py`
