# TerminalAI Dependency Analysis

**Comprehensive dependency tree and installation strategy for Windows RTX systems**

---

## Dependency Tree Overview

```
TerminalAI v1.5.0
├── Tier 1: CORE (Required)
│   ├── Python 3.10+ (3.13.5 detected)
│   ├── yt-dlp >= 2023.0.0
│   ├── pyyaml >= 6.0
│   ├── gradio >= 4.0.0
│   └── FFmpeg (external binary)
│
├── Tier 2: GPU ACCELERATION (Recommended for RTX)
│   ├── NVIDIA Driver 535+ (591.59 detected - ✓)
│   ├── NVENC Encoders (h264_nvenc, hevc_nvenc)
│   ├── NVIDIA Maxine SDK (optional, best quality)
│   └── Real-ESRGAN ncnn-vulkan (optional, good quality)
│
├── Tier 3: AUDIO AI (Optional, PyTorch-based)
│   ├── PyTorch >= 2.0.0 (CUDA 12.1 build)
│   │   ├── torch
│   │   ├── torchvision
│   │   └── torchaudio
│   ├── Demucs >= 4.0.0
│   │   └── requires: torch, torchaudio, numpy, scipy
│   ├── DeepFilterNet >= 0.5.0
│   │   ├── requires: torch, librosa, soundfile
│   │   └── build dependency: Rust compiler (for pyo3)
│   └── AudioSR >= 0.0.4 (optional, Windows issues)
│       ├── requires: torch, fairseq, librosa
│       └── warning: fairseq has known Windows build issues
│
└── Tier 4: ADVANCED FEATURES (Optional)
    ├── Face Restoration
    │   ├── torch >= 2.0.0 (same as Tier 3)
    │   ├── opencv-python >= 4.5.0
    │   ├── basicsr >= 1.4.2
    │   │   └── requires: torch, opencv, numpy, pillow, scipy, lmdb, yapf
    │   ├── facexlib >= 0.2.5
    │   │   └── requires: torch, opencv, numpy, scipy, numba
    │   └── gfpgan >= 1.3.0
    │       └── requires: basicsr, facexlib, realesrgan
    │
    └── Advanced Deinterlacing
        ├── VapourSynth (external runtime)
        ├── vapoursynth (Python bindings)
        └── vapoursynth-havsfunc (QTGMC filter)
```

---

## Critical Windows Installation Issues

### Issue 1: PyTorch CUDA Version Mismatch

**Problem**: Installing PyTorch via pip defaults to CPU-only on Windows.

**Solution**:
```bash
# WRONG (installs CPU-only):
pip install torch

# CORRECT (for RTX 5080 with CUDA 12.1):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**CUDA Version Selection**:
- NVIDIA Driver 591.59 → Supports CUDA 12.x
- PyTorch official builds: `cu121` (CUDA 12.1) or `cu118` (CUDA 11.8)
- Recommendation: Use `cu121` for latest features

### Issue 2: Installation Order Matters

**Problem**: Installing packages in wrong order causes dependency conflicts.

**Correct Order for Windows**:

1. **Base Package First**:
   ```bash
   pip install -e .
   ```

2. **PyTorch CUDA Next** (before any AI packages):
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

3. **Audio AI Packages**:
   ```bash
   pip install demucs
   pip install deepfilternet  # May require Rust
   pip install audiosr        # Optional, may fail
   ```

4. **Face Restoration Packages** (specific order):
   ```bash
   pip install opencv-python
   pip install basicsr
   pip install facexlib
   pip install gfpgan
   ```

### Issue 3: DeepFilterNet Requires Rust Compiler

**Problem**: DeepFilterNet uses PyO3 (Python-Rust bindings) which requires Rust compiler.

**Solution**:
```bash
# Install Rust first
# Download from: https://www.rust-lang.org/tools/install
# Run: rustup-init.exe

# Restart terminal, then:
pip install deepfilternet
```

**Alternative**: Use pre-built wheels if available on PyPI for your Python version.

### Issue 4: AudioSR Windows Compatibility

**Problem**: AudioSR depends on `fairseq` which has build issues on Windows.

**Status**: **OPTIONAL** - Can be skipped without losing core functionality.

**Workaround**:
- Use DeepFilterNet for audio denoising instead
- AudioSR is only for AI-based upsampling (48kHz)
- Not critical for video processing workflow

### Issue 5: VapourSynth Runtime vs Python Package

**Problem**: VapourSynth Python package alone is not enough on Windows.

**Solution**:
1. Install VapourSynth **runtime** first (installer or portable)
   - Download: https://github.com/vapoursynth/vapoursynth/releases
2. Then install Python bindings:
   ```bash
   pip install vapoursynth
   ```

**Note**: VapourSynth is optional - FFmpeg's `yadif` deinterlacing works well for most cases.

### Issue 6: Python 3.13 Compatibility

**Current Status**:
- Python 3.13.5 detected
- Core packages: ✓ Compatible
- PyTorch: ✓ Official builds available
- GFPGAN/BasicSR: ⚠️ Limited testing
- VapourSynth: ⚠️ May not have Python 3.13 builds

**Recommendation**:
- Core + Audio AI: Use Python 3.13
- If Tier 4 fails: Create Python 3.11 venv for advanced features

---

## Dependency Installation Matrix

| Package | Windows Compatible | CUDA Required | Build Tools Needed | Notes |
|---------|-------------------|---------------|-------------------|-------|
| **Core** |
| yt-dlp | ✓ | - | - | Pure Python |
| pyyaml | ✓ | - | - | Pure Python |
| gradio | ✓ | - | - | Web framework |
| **GPU** |
| NVIDIA Maxine | ✓ | ✓ | - | Windows binaries |
| Real-ESRGAN | ✓ | - | - | Vulkan-based, AMD/Intel compatible |
| **Audio AI** |
| torch (CPU) | ✓ | - | - | Official Windows builds |
| torch (CUDA) | ✓ | ✓ | - | Use `--index-url` for CUDA builds |
| demucs | ✓ | ✓ (optional) | - | Works on CPU or CUDA |
| deepfilternet | ⚠️ | ✓ (optional) | Rust | Requires Rust compiler |
| audiosr | ❌ | ✓ | C++ | Known Windows issues (fairseq) |
| **Face Restoration** |
| opencv-python | ✓ | - | - | Pre-built Windows wheels |
| basicsr | ✓ | ✓ (optional) | - | Works on CPU or CUDA |
| facexlib | ✓ | ✓ (optional) | - | Works on CPU or CUDA |
| gfpgan | ✓ | ✓ (optional) | - | Works on CPU or CUDA |
| **Advanced** |
| vapoursynth | ⚠️ | - | C++ | Requires runtime installer |

**Legend**:
- ✓ = Fully compatible
- ⚠️ = Works but requires extra steps
- ❌ = Known issues, skip recommended

---

## RTX 5080 Specific Optimizations

Your system configuration:
- **GPU**: NVIDIA GeForce RTX 5080
- **VRAM**: 16GB
- **Compute Capability**: 12.0
- **Driver**: 591.59

### Optimal Configuration

**PyTorch Settings**:
```python
# In code or environment
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

**Recommended Batch Sizes**:
- GFPGAN: Process 1 frame at a time (already implemented)
- Demucs: Default chunk size works well with 16GB VRAM
- DeepFilterNet: Automatic chunking

**NVENC Encoding**:
- Use `hevc_nvenc` for H.265 (better compression)
- Use `h264_nvenc` for H.264 (better compatibility)
- Both fully supported on RTX 5080

---

## Installation Size Estimates

| Component | Download Size | Installed Size | Notes |
|-----------|---------------|----------------|-------|
| **Core** |
| Base package | <1 MB | ~5 MB | Python code only |
| FFmpeg | ~120 MB | ~250 MB | Windows binary |
| **GPU** |
| NVIDIA Maxine | ~500 MB | ~1 GB | Video Effects SDK |
| Real-ESRGAN | ~50 MB | ~100 MB | Vulkan binary |
| **Audio AI** |
| PyTorch (CUDA 12.1) | ~2.5 GB | ~5 GB | Large CUDA libraries |
| Demucs | ~10 MB | ~20 MB | Python package only |
| Demucs models | ~800 MB | ~2 GB | htdemucs, downloaded on first use |
| DeepFilterNet | ~5 MB | ~10 MB | + Rust runtime |
| DeepFilterNet models | ~30 MB | ~50 MB | Auto-downloaded |
| **Face Restoration** |
| OpenCV | ~50 MB | ~100 MB | Pre-built wheels |
| GFPGAN + deps | ~100 MB | ~200 MB | Python packages |
| GFPGAN model | ~350 MB | ~350 MB | GFPGANv1.3.pth |
| **Advanced** |
| VapourSynth | ~30 MB | ~60 MB | Runtime + Python |

**Total Size Estimates**:
- **Minimal** (Core only): ~400 MB
- **Recommended** (Core + GPU + Audio): ~10 GB
- **Full** (All features): ~15 GB

---

## Dependency Version Constraints

### Minimum Versions (pyproject.toml)

```toml
[project]
requires-python = ">=3.10"

dependencies = [
    "yt-dlp>=2023.0.0",
    "pyyaml>=6.0",
    "gradio>=4.0.0",
]

[project.optional-dependencies]
audio = [
    "demucs>=4.0.0",
    "torch>=2.0.0",
    "torchaudio>=2.0.0",
    "deepfilternet>=0.5.0",
    "audiosr>=0.0.4",
]

faces = [
    "gfpgan>=1.3.0",
    "basicsr>=1.4.2",
    "facexlib>=0.2.5",
]
```

### Tested Versions (Windows RTX 5080)

- Python: 3.13.5
- PyTorch: 2.8.0+cu121
- Demucs: 4.0.0
- GFPGAN: 1.3.8
- BasicSR: 1.4.2
- OpenCV: 4.10.0

---

## Troubleshooting Dependency Issues

### "No module named 'torch'"

**Cause**: PyTorch not installed or wrong environment.

**Fix**:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### "torch.cuda.is_available() returns False"

**Cause**: CPU-only PyTorch installed or driver issue.

**Fix**:
```bash
# Uninstall CPU version
pip uninstall torch torchvision torchaudio

# Reinstall CUDA version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

### "error: can't find Rust compiler"

**Cause**: DeepFilterNet requires Rust for PyO3 bindings.

**Fix**:
```bash
# Install Rust from: https://www.rust-lang.org/tools/install
# Restart terminal
pip install deepfilternet
```

### "ImportError: DLL load failed" (OpenCV)

**Cause**: Missing Visual C++ Redistributables.

**Fix**:
```bash
# Install Visual C++ Redistributables:
# https://aka.ms/vs/17/release/vc_redist.x64.exe

# Or reinstall OpenCV
pip install --force-reinstall opencv-python
```

### "fairseq installation failed" (AudioSR)

**Cause**: fairseq has Windows build issues.

**Fix**: **Skip AudioSR** - it's optional. Use DeepFilterNet instead.

### "VapourSynth not found"

**Cause**: VapourSynth runtime not installed.

**Fix**:
1. Install runtime: https://github.com/vapoursynth/vapoursynth/releases
2. Then: `pip install vapoursynth`

---

## Dependency Update Strategy

### Safe Updates

Core packages can usually be updated safely:
```bash
pip install --upgrade yt-dlp pyyaml gradio
```

### Cautious Updates

PyTorch and AI packages should be updated carefully:
```bash
# Check for updates but don't auto-upgrade
pip list --outdated | findstr "torch demucs gfpgan"

# Update with testing
pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
python scripts\verify_setup.py
```

### Lock File

For production, consider creating `requirements-lock.txt`:
```bash
pip freeze > requirements-lock.txt
```

---

## Alternative Installation Methods

### Method 1: Conda (Not Recommended for This Project)

**Pros**: Better dependency resolution
**Cons**: Slower, larger, PyPI packages not always available

### Method 2: Virtual Environment (Recommended)

```bash
# Create venv
python -m venv venv_terminalai

# Activate
venv_terminalai\Scripts\activate

# Install
python install_windows.py --full
```

### Method 3: Docker (Advanced)

Not currently supported on Windows with GPU, but could be implemented.

---

## Summary

**Windows RTX 5080 Installation Checklist**:

- [x] Python 3.13.5 installed
- [x] NVIDIA Driver 591.59 (CUDA 12.x compatible)
- [ ] FFmpeg installed and in PATH
- [ ] PyTorch with CUDA 12.1 installed
- [ ] Demucs installed (optional)
- [ ] DeepFilterNet installed (optional, requires Rust)
- [ ] GFPGAN installed (optional)
- [ ] NVIDIA Maxine SDK installed (optional, best quality)
- [ ] Real-ESRGAN installed (optional, good quality)

**Critical Installation Order**:
1. Base package (`pip install -e .`)
2. PyTorch CUDA (`pip install torch --index-url ...`)
3. Audio AI (Demucs, DeepFilterNet)
4. Face restoration (opencv → basicsr → facexlib → gfpgan)
5. VapourSynth runtime → Python bindings

**Use the Windows installer for automated setup**:
```bash
python install_windows.py --full
```

Or follow the detailed guide:
```bash
docs\WINDOWS_INSTALLATION.md
```
