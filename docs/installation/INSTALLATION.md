# TerminalAI Installation Guide

**Complete installation guide for all platforms**

## Quick Install

The installation has been simplified - running `pip install -e .` now installs ALL features automatically.

```bash
git clone https://github.com/parthalon025/terminalai.git
cd terminalai
pip install -e .
```

That's it! You now have:
- AI Video Upscaling (Real-ESRGAN)
- Face Restoration (GFPGAN)
- AI Audio Enhancement (DeepFilterNet, AudioSR)
- Surround Sound Upmixing (Demucs AI)
- Watch Folder Automation
- Webhook/Email Notifications
- GPU Acceleration Support
- All processing features

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux, or macOS
- **Python**: 3.10, 3.11, or 3.12 (**NOT 3.13** - see [PYTHON_VERSION_NOTICE.md](PYTHON_VERSION_NOTICE.md))
- **RAM**: 8GB (16GB recommended for 4K processing)
- **Storage**: 10GB for dependencies + models
- **FFmpeg**: Required (install separately, see below)

**IMPORTANT:** Python 3.13 is not compatible due to dependency issues. Use Python 3.11 (recommended).

### Recommended for Best Performance
- **GPU**: NVIDIA RTX 2060 or better (for GPU-accelerated AI)
- **CUDA**: 12.1+ for CUDA acceleration
- **VRAM**: 6GB+ for AI upscaling, 8GB+ for 4K
- **CPU**: 6+ cores for CPU processing

## Installation Steps

### 1. Install Python 3.11 (Recommended)

**IMPORTANT:** Use Python 3.11 or 3.12. Python 3.13 is not compatible.

**Windows:**
```bash
winget install Python.Python.3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**macOS:**
```bash
brew install python@3.11
```

**Verify:**
```bash
python --version
# Should show: Python 3.11.x or 3.12.x (NOT 3.13.x)
```

### 2. Install FFmpeg (Required)

FFmpeg is required for all video processing.

**Windows:**
```bash
winget install FFmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Verify:**
```bash
ffmpeg -version
```

### 3. Install TerminalAI

```bash
# Clone repository
git clone https://github.com/parthalon025/terminalai.git
cd terminalai

# Install (includes ALL features)
pip install -e .
```

This will install:
- Core dependencies (yt-dlp, pyyaml, gradio)
- PyTorch and torchaudio (AI processing)
- OpenCV (video processing)
- Demucs (AI audio separation)
- DeepFilterNet (AI audio denoising)
- AudioSR (AI audio upsampling)
- GFPGAN (face restoration)
- basicsr, facexlib (AI support libraries)
- Real-ESRGAN (AI video upscaling)
- watchdog (folder monitoring)
- requests (notifications)
- nvidia-ml-py (GPU detection)

### 4. Verify Installation

```bash
python verify_installation.py
```

This checks:
- Python version
- FFmpeg availability
- GPU detection (NVIDIA)
- PyTorch CUDA support
- All AI dependencies
- Feature availability

### 5. Launch the GUI

```bash
python -m vhs_upscaler.gui
```

Opens at **http://localhost:7860**

## Optional Components

### CUDA Acceleration (Faster GPU Processing)

For NVIDIA GPUs with CUDA 12.1+:

```bash
pip install -e ".[cuda]"
```

This installs CuPy for faster GPU array operations.

### Development Tools

For development and testing:

```bash
pip install -e ".[dev]"
```

Includes:
- pytest (testing)
- pytest-cov (coverage)
- black (formatting)
- ruff (linting)

### Development + CUDA

```bash
pip install -e ".[dev-cuda]"
```

## Platform-Specific Notes

### Windows

**PyTorch CUDA Support:**

For NVIDIA GPU acceleration, ensure PyTorch is installed with CUDA support:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Then reinstall TerminalAI:
```bash
pip install -e .
```

**NVIDIA Driver:**

Install the latest NVIDIA driver from: https://www.nvidia.com/drivers

Recommended: Driver 535+ for RTX GPUs

**RTX Video SDK (Optional, Best Quality):**

For RTX 20+ GPUs, install RTX Video SDK for superior AI upscaling:

1. Download from: https://developer.nvidia.com/rtx-video-sdk
2. Run setup wizard: `terminalai-setup-rtx`
3. See `docs/installation/INSTALL_RTX_VIDEO_SDK.md` for details

### Linux

**CUDA Support:**

For NVIDIA GPU acceleration:

```bash
# Install NVIDIA drivers
sudo ubuntu-drivers autoinstall

# Install CUDA toolkit (optional, PyTorch includes CUDA runtime)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install cuda-toolkit-12-1
```

**System Dependencies:**

Some dependencies may require system libraries:

```bash
sudo apt install libsm6 libxext6 libxrender-dev libgomp1
```

### macOS

**Note:** CUDA acceleration is not available on macOS (NVIDIA GPUs not supported by recent macOS).

PyTorch will use CPU or Metal Performance Shaders (MPS) on Apple Silicon.

**Apple Silicon (M1/M2/M3):**

PyTorch supports MPS acceleration:

```python
# Will automatically use MPS if available
import torch
print(torch.backends.mps.is_available())  # True on Apple Silicon
```

## Troubleshooting

### ImportError: No module named 'torch'

**Solution:**
```bash
pip install torch torchaudio
```

### ImportError: No module named 'cv2'

**Solution:**
```bash
pip install opencv-python
```

### GFPGAN not working

**Solution:**
```bash
pip install gfpgan basicsr facexlib
```

### DeepFilterNet errors

**Solution:**
```bash
pip install deepfilternet torch torchaudio
```

### AudioSR not found

**Solution:**
```bash
pip install audiosr torch torchaudio
```

### FFmpeg not found

**Solution:**

Ensure FFmpeg is in your PATH:

**Windows:**
```bash
winget install FFmpeg
# Restart terminal
```

**Linux:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### CUDA out of memory

**Solution:**

Reduce batch size or resolution. For 6GB VRAM:
- Process 480p → 1080p (safe)
- For 4K output, process in chunks

### Slow processing on CPU

**Solution:**

1. Install CUDA-enabled PyTorch (NVIDIA GPUs):
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

2. Use GPU-accelerated upscaling:
   - Real-ESRGAN (NVIDIA/AMD/Intel)
   - RTX Video SDK (NVIDIA RTX 20+)

3. Enable hardware encoding:
   - Select NVENC encoder in GUI (NVIDIA)
   - Select QSV encoder (Intel)
   - Select AMF encoder (AMD)

## Verification Checklist

After installation, verify these work:

```bash
# Run comprehensive verification
python verify_installation.py

# Check specific features
python verify_installation.py --check pytorch
python verify_installation.py --check gfpgan
python verify_installation.py --check gpu

# Get available features
python -c "from verify_installation import get_available_features; print(get_available_features())"
```

Expected output:
```
{
    "video_processing": true,
    "gpu_acceleration": true,  # If NVIDIA GPU present
    "hardware_encoding": true,  # If GPU supports NVENC/QSV/AMF
    "ai_upscaling": true,
    "deinterlacing": true,
    "face_restoration": true,
    "ai_audio_processing": true,
    "surround_upmix": true,
    "watch_folder": true
}
```

## Next Steps

1. **Launch GUI:**
   ```bash
   python -m vhs_upscaler.gui
   ```

2. **Process a video:**
   - Drag video file into browser
   - Select preset (VHS, DVD, etc.)
   - Click "Add to Queue"
   - Watch real-time progress

3. **Explore features:**
   - Try AI upscaling (Real-ESRGAN)
   - Test face restoration (GFPGAN)
   - Enable AI audio enhancement (DeepFilterNet)
   - Try surround upmix (Demucs AI)

4. **Read documentation:**
   - `README.md` - Feature overview
   - `docs/VERIFICATION_GUIDE.md` - Verification details
   - `docs/installation/INSTALLATION_TROUBLESHOOTING.md` - Troubleshooting
   - `CLAUDE.md` - Development guide

## Getting Help

- **Issues:** https://github.com/parthalon025/terminalai/issues
- **Documentation:** https://github.com/parthalon025/terminalai#readme
- **Verification:** Run `python verify_installation.py --report diagnostic.json`

## Summary

**Before (Old System):**
- Base install had minimal features
- Users got "Feature not available" errors
- Required manual installation of optional features
- Confusing dependency groups

**After (New System):**
- Single `pip install -e .` gets EVERYTHING
- All AI features work out of the box
- Only optional: dev tools and CUDA acceleration
- No runtime errors from missing dependencies

**Install command:**
```bash
pip install -e .  # Everything works!
```
