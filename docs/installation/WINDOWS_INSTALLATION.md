# TerminalAI Windows Installation Guide

**Simplified complete installation for Windows 10/11**

## Quick Install (Recommended)

The installation has been **completely simplified**. One command now installs everything:

```bash
cd D:\SSD\AI_Tools\terminalai
pip install -e .
```

That's it! All AI features are now included automatically.

## What You Get

After running `pip install -e .`, you have:

- ✅ AI Video Upscaling (Real-ESRGAN)
- ✅ Face Restoration (GFPGAN)
- ✅ AI Audio Enhancement (DeepFilterNet, AudioSR)
- ✅ Surround Sound Upmixing (Demucs AI)
- ✅ Watch Folder Automation
- ✅ Webhook/Email Notifications
- ✅ GPU Acceleration Support
- ✅ All processing features

**No more "Feature not available" errors!**

## System Requirements

### Minimum
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.10, 3.11, or 3.12 (recommended: 3.11)
- **RAM**: 8GB (16GB recommended for 4K)
- **Storage**: 15GB for dependencies + models
- **FFmpeg**: Required (see below)

### Recommended for GPU Acceleration
- **GPU**: NVIDIA RTX 2060 or better
- **VRAM**: 6GB+ (8GB+ for 4K)
- **NVIDIA Driver**: 535+ (latest recommended)
- **CUDA**: 12.1+ (included with PyTorch)

## Installation Steps

### Step 1: Install Python

**Option A: Using winget (Recommended)**
```bash
winget install Python.Python.3.11
```

**Option B: Download Installer**
- Download from: https://www.python.org/downloads/
- Install Python 3.11.x (most compatible)
- ✅ Check "Add Python to PATH" during installation

**Verify:**
```bash
python --version
# Should show: Python 3.11.x
```

### Step 2: Install FFmpeg (Required)

**Option A: Using winget (Easiest)**
```bash
winget install FFmpeg
```

**Option B: Manual Installation**
1. Download from: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH:
   - Open "Environment Variables"
   - Edit "Path" under System Variables
   - Add `C:\ffmpeg\bin`
   - Click OK and restart terminal

**Verify:**
```bash
ffmpeg -version
```

### Step 3: Install TerminalAI (Includes ALL Features)

```bash
# Navigate to TerminalAI directory
cd D:\SSD\AI_Tools\terminalai

# Install EVERYTHING (one command)
pip install -e .
```

This installs:
- yt-dlp, pyyaml, gradio (core)
- torch, torchaudio (PyTorch AI)
- opencv-python, numpy (video processing)
- demucs, deepfilternet, audiosr (AI audio)
- gfpgan, basicsr, facexlib (face restoration)
- realesrgan (AI upscaling)
- watchdog (folder monitoring)
- requests (notifications)
- nvidia-ml-py (GPU detection)

**Automatic Compatibility Patches:**
- basicsr torchvision >= 0.17 compatibility fix (applied automatically)

**Installation time:** 10-20 minutes (PyTorch is large)

### Step 4: Ensure CUDA Support (For NVIDIA GPUs)

If you have an NVIDIA GPU, ensure PyTorch has CUDA support:

```bash
# Check current PyTorch
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

If it says `False`, reinstall PyTorch with CUDA:

```bash
# Uninstall current PyTorch
pip uninstall torch torchvision torchaudio -y

# Install with CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify CUDA is working
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0)}')"
```

Expected output:
```
CUDA: True, Device: NVIDIA GeForce RTX 5080
```

### Step 5: Verify Installation

```bash
python verify_installation.py
```

This checks:
- Python version
- FFmpeg availability
- GPU detection
- PyTorch CUDA support
- All AI dependencies
- Feature availability

### Step 6: Launch the GUI

```bash
python -m vhs_upscaler.gui
```

Opens at **http://localhost:7860**

## Optional: RTX Video SDK (Best Quality)

For RTX 20+ GPUs, install RTX Video SDK for superior AI upscaling:

### Step 1: Download RTX Video SDK

1. Visit: https://developer.nvidia.com/rtx-video-sdk
2. Download RTX Video SDK 1.1.0+
3. Extract to: `C:\Program Files\NVIDIA\RTX_Video_SDK`

### Step 2: Run Setup Wizard

```bash
terminalai-setup-rtx
```

This will:
- Detect RTX Video SDK installation
- Configure paths
- Test video processing
- Verify GPU compatibility

### Step 3: Verify

```bash
python -c "from vhs_upscaler.rtx_video import check_rtx_video_sdk; print(check_rtx_video_sdk())"
```

See `docs/installation/INSTALL_RTX_VIDEO_SDK.md` for detailed RTX Video SDK setup.

## Optional: CUDA Acceleration

For even faster processing with CuPy:

```bash
pip install -e ".[cuda]"
```

This installs CuPy for faster GPU array operations.

## Optional: Development Tools

For development and testing:

```bash
pip install -e ".[dev]"
```

Includes pytest, pytest-cov, black, ruff.

## Troubleshooting

### ImportError: No module named 'torch'

**Cause:** PyTorch installation failed or incomplete.

**Solution:**
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### ImportError: No module named 'cv2'

**Cause:** OpenCV not installed.

**Solution:**
```bash
pip install opencv-python
```

### GFPGAN not working

**Cause:** Face restoration dependencies missing or torchvision compatibility issue.

**Solution:**
```bash
pip install gfpgan basicsr facexlib opencv-python

# Apply torchvision compatibility patch (automatic in full installation)
python scripts/installation/patch_basicsr.py
```

**Note:** The full installer (`python install.py --full`) automatically patches basicsr for torchvision >= 0.17 compatibility.

### DeepFilterNet errors

**Cause:** May require Rust compiler on some systems.

**Solution:**

1. Install Rust: https://www.rust-lang.org/tools/install
2. Restart terminal
3. Reinstall:
   ```bash
   pip install deepfilternet
   ```

### AudioSR not found

**Cause:** AudioSR installation issues (known on some Windows systems).

**Solution:**

AudioSR is optional and can be skipped. Other audio features will still work:
```bash
# Skip AudioSR if it fails - not critical
pip uninstall audiosr
```

### CUDA out of memory

**Cause:** VRAM insufficient for current resolution.

**Solution:**

- Reduce resolution (480p → 1080p instead of 4K)
- Close other GPU-intensive applications
- Use CPU mode (slower but works)

### FFmpeg not found

**Cause:** FFmpeg not in PATH.

**Solution:**

```bash
# Reinstall FFmpeg
winget install FFmpeg

# Restart terminal/IDE
# Verify
ffmpeg -version
```

### Slow processing

**Cause:** Using CPU instead of GPU.

**Solutions:**

1. **Ensure CUDA PyTorch:**
   ```bash
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

2. **Enable hardware encoding:**
   - Select "h264_nvenc" encoder in GUI (NVIDIA)
   - Requires NVIDIA driver 535+

3. **Use GPU upscaling:**
   - Select Real-ESRGAN in GUI
   - Or install RTX Video SDK (best quality)

## Python Version Compatibility

**Recommended:** Python 3.11 (most stable)

**Compatibility Matrix:**
- **Python 3.10**: ✅ Fully compatible
- **Python 3.11**: ✅ Fully compatible (recommended)
- **Python 3.12**: ✅ Compatible
- **Python 3.13**: ⚠️ Some dependencies may have issues

If using Python 3.13 and encountering issues:

```bash
# Create Python 3.11 virtual environment
py -3.11 -m venv venv_py311

# Activate
venv_py311\Scripts\activate

# Install TerminalAI
pip install -e .
```

## Verification Checklist

After installation, verify these features work:

```bash
# Run comprehensive verification
python verify_installation.py

# Check specific features
python verify_installation.py --check pytorch
python verify_installation.py --check gfpgan
python verify_installation.py --check gpu

# Get available features JSON
python -c "from verify_installation import get_available_features; import json; print(json.dumps(get_available_features(), indent=2))"
```

Expected output:
```json
{
  "video_processing": true,
  "gpu_acceleration": true,
  "hardware_encoding": true,
  "ai_upscaling": true,
  "deinterlacing": true,
  "face_restoration": true,
  "ai_audio_processing": true,
  "surround_upmix": true,
  "watch_folder": true
}
```

## Common Issues

### Issue 1: PyTorch Not Using GPU

**Symptom:**
```
torch.cuda.is_available() = False
```

**Solution:**
```bash
# Uninstall CPU-only PyTorch
pip uninstall torch torchvision torchaudio -y

# Install CUDA version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

### Issue 2: Dependencies Conflict

**Symptom:**
```
ERROR: pip's dependency resolver does not currently take into account...
```

**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Reinstall
pip install -e . --upgrade
```

### Issue 3: Missing DLL Errors

**Symptom:**
```
ImportError: DLL load failed while importing _torch_cuda
```

**Solution:**

Install Visual C++ Redistributable:
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Install and restart

### Issue 4: Permission Errors

**Symptom:**
```
ERROR: Could not install packages due to an OSError: [WinError 5] Access is denied
```

**Solution:**

Run as administrator or use `--user` flag:
```bash
pip install -e . --user
```

## Next Steps

1. **Launch GUI:**
   ```bash
   python -m vhs_upscaler.gui
   ```

2. **Test Processing:**
   - Drag a video file into the browser
   - Select "VHS" preset
   - Click "Add to Queue"
   - Watch real-time progress

3. **Explore Features:**
   - Try AI upscaling (Real-ESRGAN)
   - Enable face restoration (GFPGAN)
   - Test AI audio enhancement (DeepFilterNet)
   - Try surround upmix (Demucs AI)

4. **Read Documentation:**
   - `README.md` - Feature overview
   - `INSTALLATION.md` - Detailed installation
   - `docs/VERIFICATION_GUIDE.md` - Verification details
   - `docs/installation/INSTALLATION_TROUBLESHOOTING.md` - Troubleshooting

## Getting Help

- **Issues:** https://github.com/parthalon025/terminalai/issues
- **Documentation:** https://github.com/parthalon025/terminalai#readme
- **Diagnostics:** Run `python verify_installation.py --report diagnostic.json`

## Summary

**Before (Old System):**
- Multiple tiers of installation
- Optional dependency groups confusing
- Features failed at runtime
- Complex Windows-specific steps

**After (New System):**
- One command: `pip install -e .`
- Everything included automatically
- No runtime errors
- Simple, straightforward

**Install command:**
```bash
pip install -e .  # That's it!
```

**Time estimate:** 15-25 minutes total
