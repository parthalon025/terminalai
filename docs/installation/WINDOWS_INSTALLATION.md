# TerminalAI Windows Installation Guide

**Comprehensive installation guide for Windows with RTX 5080 GPU**

## System Information

- **OS**: Windows 10/11
- **Python**: 3.13.5 (detected)
- **GPU**: NVIDIA GeForce RTX 5080 (16GB VRAM, Compute 12.0)
- **NVIDIA Driver**: 591.59
- **CUDA Support**: Available

---

## Installation Strategy Overview

The installation is divided into **four tiers**:

1. **Tier 1: Core** (Required) - Base functionality
2. **Tier 2: GPU Acceleration** (Recommended) - RTX AI upscaling
3. **Tier 3: Audio AI** (Optional) - PyTorch-based audio processing
4. **Tier 4: Advanced Features** (Optional) - VapourSynth, face restoration

---

## Tier 1: Core Installation (Required)

### 1.1 Install Base Package

```bash
# Navigate to TerminalAI directory
cd D:\SSD\AI_Tools\terminalai

# Install core dependencies
pip install -e .

# Verify installation
python scripts\verify_setup.py
```

**Core Dependencies Installed**:
- `yt-dlp` - YouTube downloading
- `pyyaml` - Configuration management
- `gradio` - Web GUI interface

### 1.2 Install FFmpeg

FFmpeg is **required** for all video processing.

**Option A: Using winget (Recommended)**
```bash
winget install FFmpeg
```

**Option B: Manual Installation**
1. Download from: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH
4. Restart terminal/IDE

**Verify FFmpeg**:
```bash
ffmpeg -version
```

---

## Tier 2: GPU Acceleration (Recommended for RTX 5080)

### 2.1 NVIDIA Maxine SDK (Best AI Upscaling)

**Download and Install**:
1. Download Maxine Video Effects SDK: https://developer.nvidia.com/maxine
2. Extract to: `C:\Program Files\NVIDIA\Maxine`
3. Set environment variable:
   ```bash
   setx MAXINE_HOME "C:\Program Files\NVIDIA\Maxine"
   ```
4. Restart terminal

**Verify**:
```bash
python scripts\verify_setup.py
```

### 2.2 Real-ESRGAN (Alternative AI Upscaling)

**Download and Install**:
1. Download `realesrgan-ncnn-vulkan-windows.zip`: https://github.com/xinntao/Real-ESRGAN/releases
2. Extract to: `C:\Program Files\Real-ESRGAN`
3. Add to PATH: `C:\Program Files\Real-ESRGAN`

**Verify**:
```bash
realesrgan-ncnn-vulkan.exe -h
```

---

## Tier 3: Audio AI Features (Optional)

**Challenge**: PyTorch dependencies require specific Windows installation order.

### 3.1 Install PyTorch with CUDA Support (Critical First Step)

**IMPORTANT**: Install PyTorch **BEFORE** other audio packages to ensure CUDA compatibility.

**For RTX 5080 (CUDA 12.x compatible)**:
```bash
# Install PyTorch with CUDA 12.1 support (official Windows builds)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Verify CUDA Support**:
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}')"
```

Expected output:
```
PyTorch: 2.x.x+cu121
CUDA Available: True
CUDA Version: 12.1
```

### 3.2 Install Demucs (Surround Sound AI)

```bash
pip install demucs>=4.0.0
```

**Verify**:
```bash
python -c "import demucs; print('Demucs installed successfully')"
```

### 3.3 Install DeepFilterNet (AI Audio Denoising)

**Windows Installation Steps**:

1. **Install system dependencies** (if needed):
   ```bash
   # DeepFilterNet requires these packages
   pip install numpy scipy librosa
   ```

2. **Install DeepFilterNet**:
   ```bash
   pip install deepfilternet>=0.5.0
   ```

   **Alternative if pip fails** (build from source):
   ```bash
   # Install Rust compiler first (required for building)
   # Download from: https://www.rust-lang.org/tools/install

   # Then install from git
   pip install git+https://github.com/Rikorose/DeepFilterNet.git
   ```

**Verify**:
```bash
python -c "import deepfilternet; print('DeepFilterNet installed successfully')"
```

### 3.4 Install AudioSR (AI Audio Super-Resolution)

**Windows Installation**:

```bash
# AudioSR requires fairseq which can be tricky on Windows
pip install audiosr>=0.0.4
```

**If installation fails**, AudioSR has known Windows compatibility issues. You can skip it and use other audio features.

**Verify (if installed)**:
```bash
python -c "import audiosr; print('AudioSR installed successfully')"
```

### 3.5 Complete Audio Install Command

**Recommended Order (Windows)**:
```bash
# 1. PyTorch with CUDA first
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 2. Demucs
pip install demucs>=4.0.0

# 3. DeepFilterNet (may require Rust compiler)
pip install deepfilternet>=0.5.0

# 4. AudioSR (optional, skip if fails)
pip install audiosr>=0.0.4
```

---

## Tier 4: Advanced Features (Optional)

### 4.1 GFPGAN / CodeFormer (Face Restoration)

**Installation Order** (critical for Windows):

1. **Install PyTorch first** (from Tier 3.1 if not done):
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

2. **Install OpenCV**:
   ```bash
   pip install opencv-python>=4.5.0
   ```

3. **Install BasicSR**:
   ```bash
   pip install basicsr>=1.4.2
   ```

4. **Install FaceXLib**:
   ```bash
   pip install facexlib>=0.2.5
   ```

5. **Install GFPGAN**:
   ```bash
   pip install gfpgan>=1.3.0
   ```

**Verify**:
```bash
python -c "import gfpgan; print('GFPGAN installed successfully')"
```

**Download GFPGAN Model**:
```bash
python -m vhs_upscaler.face_restoration --download-model
```

### 4.2 VapourSynth (Advanced Deinterlacing)

**Windows VapourSynth Installation**:

1. **Download VapourSynth installer**: https://github.com/vapoursynth/vapoursynth/releases
   - Get `VapourSynth64-Portable-Rxx.7z` or installer
   - Recommended: R65 or later

2. **Install VapourSynth**:
   - Run installer or extract portable version
   - Default install location: `C:\Program Files\VapourSynth`

3. **Add to PATH** (if using portable):
   ```bash
   setx PATH "%PATH%;C:\Program Files\VapourSynth"
   ```

4. **Install Python bindings**:
   ```bash
   pip install vapoursynth
   ```

5. **Install HAVSFUNC (for QTGMC)**:
   ```bash
   pip install vapoursynth-havsfunc
   ```

**Verify**:
```bash
python -c "import vapoursynth; print(f'VapourSynth {vapoursynth.__version__}')"
```

**Note**: VapourSynth on Windows can be complex. If installation fails, you can still use FFmpeg's `yadif` deinterlacing (built-in).

---

## Installation Verification

### Comprehensive Check

```bash
python scripts\verify_setup.py
```

### Check Specific Features

**Check PyTorch CUDA**:
```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

**Check Audio AI**:
```bash
python -c "import demucs; print('Demucs: OK')"
python -c "import deepfilternet; print('DeepFilterNet: OK')"
python -c "import audiosr; print('AudioSR: OK')"
```

**Check Face Restoration**:
```bash
python -c "import gfpgan; print('GFPGAN: OK')"
```

**Check VapourSynth**:
```bash
python -c "import vapoursynth; print('VapourSynth: OK')"
```

---

## Automated Installation Script

Use the enhanced installer:

```bash
# Basic installation
python install.py

# Full installation (attempts all features)
python install.py --full

# Audio AI only
python install.py --audio

# Face restoration only
python install.py --faces

# Development tools
python install.py --dev
```

---

## Common Installation Issues

### Issue 1: PyTorch Not Using CUDA

**Symptom**: `torch.cuda.is_available()` returns `False`

**Solution**:
1. Uninstall existing PyTorch:
   ```bash
   pip uninstall torch torchvision torchaudio
   ```

2. Reinstall with CUDA support:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

3. Verify NVIDIA driver:
   ```bash
   nvidia-smi
   ```

### Issue 2: DeepFilterNet Build Errors

**Symptom**: `error: can't find Rust compiler`

**Solution**:
1. Install Rust compiler: https://www.rust-lang.org/tools/install
2. Restart terminal
3. Retry DeepFilterNet installation

### Issue 3: AudioSR Installation Fails

**Symptom**: `fairseq` or `librosa` build errors

**Solution**:
- AudioSR has known Windows compatibility issues
- **Skip AudioSR** and use DeepFilterNet for audio enhancement instead
- AudioSR is optional and not required for core functionality

### Issue 4: GFPGAN Import Error

**Symptom**: `ModuleNotFoundError: No module named 'basicsr'`

**Solution**:
```bash
# Install in correct order
pip install opencv-python
pip install basicsr
pip install facexlib
pip install gfpgan
```

### Issue 5: VapourSynth Not Found

**Symptom**: `ImportError: No module named 'vapoursynth'`

**Solution**:
1. Ensure VapourSynth runtime is installed (not just Python package)
2. Download installer from: https://github.com/vapoursynth/vapoursynth/releases
3. Install runtime, then Python bindings:
   ```bash
   pip install vapoursynth
   ```

---

## Python 3.13 Compatibility Notes

**Current Status**: Python 3.13.5 detected

**Compatibility Matrix**:
- **Core (Tier 1)**: ✅ Fully compatible
- **PyTorch (Tier 3)**: ✅ Compatible (official Windows builds available)
- **GFPGAN/BasicSR (Tier 4)**: ⚠️ May have issues, test carefully
- **VapourSynth (Tier 4)**: ⚠️ Limited Python 3.13 builds, use 3.11/3.12 if needed

**Recommendation**: If Tier 4 features fail, consider creating a **Python 3.11 virtual environment**:

```bash
# Create venv with Python 3.11
py -3.11 -m venv venv_py311

# Activate
venv_py311\Scripts\activate

# Install TerminalAI
pip install -e .
```

---

## Installation Success Criteria

After successful installation, you should have:

### Tier 1 (Core) ✅
- [x] FFmpeg working
- [x] TerminalAI package installed
- [x] Gradio GUI launches

### Tier 2 (GPU Acceleration) ✅
- [x] NVIDIA driver detected (591.59)
- [x] NVENC encoders available
- [ ] Maxine SDK installed (optional)
- [ ] Real-ESRGAN installed (optional)

### Tier 3 (Audio AI) ⚠️
- [x] PyTorch with CUDA support
- [ ] Demucs installed
- [ ] DeepFilterNet installed
- [ ] AudioSR installed (optional, skip if fails)

### Tier 4 (Advanced) ⚠️
- [ ] GFPGAN installed
- [ ] GFPGAN models downloaded
- [ ] VapourSynth installed (optional)

---

## Next Steps

1. **Launch GUI**:
   ```bash
   python -m vhs_upscaler.gui
   ```

2. **Test CLI**:
   ```bash
   python -m vhs_upscaler.vhs_upscale --help
   ```

3. **Download AI Models** (if using Maxine/GFPGAN):
   ```bash
   # GFPGAN model
   python -m vhs_upscaler.face_restoration --download-model

   # Demucs models (auto-downloaded on first use)
   python -c "from demucs.pretrained import get_model; get_model('htdemucs')"
   ```

4. **Test Video Processing**:
   ```bash
   # Basic test (FFmpeg upscaling)
   python -m vhs_upscaler.vhs_upscale -i test.mp4 -o output.mp4 --preset vhs

   # GPU test (with Maxine/Real-ESRGAN if installed)
   python -m vhs_upscaler.vhs_upscale -i test.mp4 -o output.mp4 --engine auto
   ```

---

## Support and Troubleshooting

**Documentation**:
- Main README: `README.md`
- Deployment Guide: `docs/DEPLOYMENT.md`
- This Guide: `docs/WINDOWS_INSTALLATION.md`

**Verification Script**:
```bash
python scripts\verify_setup.py
```

**Enhanced Installer**:
```bash
python install_windows.py --help
```

**Check Logs**:
```bash
type logs\terminalai.log
```

---

## Summary

**Recommended Installation Path for RTX 5080 Windows**:

```bash
# 1. Core (Required)
pip install -e .

# 2. PyTorch with CUDA (for all AI features)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. Audio AI (recommended)
pip install demucs deepfilternet

# 4. Face Restoration (optional)
pip install opencv-python basicsr facexlib gfpgan

# 5. Download AI models
python -m vhs_upscaler.face_restoration --download-model

# 6. Verify everything
python scripts\verify_setup.py
```

**Time Estimate**:
- Core: 2-5 minutes
- PyTorch: 5-10 minutes (large download)
- Audio AI: 10-15 minutes
- Face Restoration: 5-10 minutes
- Model Downloads: 10-20 minutes (GFPGAN ~350MB, Demucs ~2GB)

**Total**: ~30-60 minutes for full installation
