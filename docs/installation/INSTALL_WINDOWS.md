# TerminalAI Windows Installation Guide

Complete installation guide for Windows 10/11 with NVIDIA RTX GPU support.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Install (Recommended)](#quick-install-recommended)
- [Manual Installation](#manual-installation)
- [Installation Options](#installation-options)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Prerequisites

### Required

1. **Windows 10/11** (64-bit)
2. **Python 3.10 or higher**
   - Download: https://www.python.org/downloads/
   - Or install via winget: `winget install Python.Python.3.13`
   - **Important**: Check "Add Python to PATH" during installation
3. **FFmpeg** (required for all video processing)
   - Install via winget: `winget install FFmpeg`
   - Or download: https://ffmpeg.org/download.html

### Recommended (for GPU acceleration)

1. **NVIDIA RTX GPU** (RTX 2060 or better)
2. **NVIDIA Driver 535+**
   - Download: https://www.nvidia.com/drivers
   - Check current driver: `nvidia-smi`

### Optional (for best quality)

1. **NVIDIA Maxine SDK** - Best AI upscaling for RTX GPUs
   - Download: https://developer.nvidia.com/maxine-getting-started
2. **Real-ESRGAN** - AI upscaling for AMD/Intel/NVIDIA
   - Download: https://github.com/xinntao/Real-ESRGAN/releases

## Quick Install (Recommended)

### Option 1: Full Installation (All Features)

Open **PowerShell** as Administrator and run:

```powershell
# Navigate to TerminalAI directory
cd D:\SSD\AI_Tools\terminalai

# Run full installation
.\install_windows.ps1 -Full
```

This installs:
- Core TerminalAI package
- PyTorch with CUDA support
- All audio processing (Demucs, DeepFilterNet, AudioSR)
- Face restoration (GFPGAN, CodeFormer)
- VapourSynth for QTGMC deinterlacing
- Watch folder automation
- Development tools

**Installation time**: ~10-20 minutes (depending on internet speed)

### Option 2: Basic Installation

For a minimal installation without optional features:

```powershell
.\install_windows.ps1
```

This installs only:
- Core TerminalAI package
- Gradio web interface
- YouTube downloader (yt-dlp)

## Manual Installation

If you prefer manual control or the automated script fails:

### Step 1: Install Python Dependencies

```bash
# Basic installation
pip install -e .

# OR with specific feature sets
pip install -e ".[audio]"      # Audio processing
pip install -e ".[faces]"      # Face restoration
pip install -e ".[full]"       # Everything
```

### Step 2: Install PyTorch (for AI features)

**With CUDA support** (NVIDIA GPU):

```bash
# For CUDA 12.6 (Driver 570+)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu126

# For CUDA 12.4 (Driver 550+)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu124

# For CUDA 12.1 (Driver 530+)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**CPU-only** (no NVIDIA GPU):

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**Check your CUDA compatibility**:
```bash
nvidia-smi  # Check driver version
```

| Driver Version | CUDA Version | Install Command |
|----------------|--------------|-----------------|
| 570+ | 12.6 | `cu126` |
| 550+ | 12.4 | `cu124` |
| 530+ | 12.1 | `cu121` |
| 520+ | 11.8 | `cu118` |

### Step 3: Install Optional Features

**Audio Processing**:
```bash
pip install demucs deepfilternet audiosr
```

**Face Restoration**:
```bash
pip install gfpgan basicsr facexlib opencv-python
```

**Watch Folder Automation**:
```bash
pip install watchdog requests
```

### Step 4: Install VapourSynth (Optional)

For highest quality QTGMC deinterlacing:

1. Download VapourSynth installer: https://github.com/vapoursynth/vapoursynth/releases
2. Run installer (use default options)
3. Install Python packages:
   ```bash
   pip install vapoursynth havsfunc
   ```

## Installation Options

The `install_windows.ps1` script supports multiple options:

```powershell
# Full installation (recommended)
.\install_windows.ps1 -Full

# Audio processing only
.\install_windows.ps1 -Audio

# Face restoration only
.\install_windows.ps1 -Faces

# VapourSynth for QTGMC
.\install_windows.ps1 -VapourSynth

# Watch folder automation
.\install_windows.ps1 -Automation

# Development environment
.\install_windows.ps1 -Dev

# CPU-only (no CUDA)
.\install_windows.ps1 -Full -CPUOnly

# Combine options
.\install_windows.ps1 -Audio -Faces -VapourSynth

# Verbose output
.\install_windows.ps1 -Full -Verbose
```

### What Gets Installed?

| Option | Components | Size | Time |
|--------|------------|------|------|
| **Basic** | TerminalAI, Gradio, yt-dlp | ~200 MB | 2 min |
| **-Audio** | + PyTorch, Demucs, DeepFilterNet, AudioSR | ~4 GB | 8 min |
| **-Faces** | + PyTorch, GFPGAN, CodeFormer, OpenCV | ~3 GB | 7 min |
| **-VapourSynth** | + VapourSynth, HAVSFunc | ~100 MB | 3 min |
| **-Full** | All of the above | ~5 GB | 15 min |

## Verification

After installation, verify everything is working:

### Automated Verification

```bash
python verify_setup.py
```

This checks:
- Python version
- FFmpeg availability
- NVIDIA GPU and CUDA
- All installed packages
- PyTorch CUDA support
- VapourSynth installation
- Maxine SDK configuration
- Real-ESRGAN availability

**Example output**:
```
═══════════════════════════════════════════════════════════
         VERIFICATION SUMMARY
═══════════════════════════════════════════════════════════

Total Checks: 25
Passed: 23
Warnings: 2

Success Rate: 92.0%

✓ Excellent! TerminalAI is ready to use.

Next Steps:
  1. Launch Web GUI: python -m vhs_upscaler.gui
  2. Process a video: python -m vhs_upscaler.vhs_upscale -i video.mp4 -o output.mp4
```

### Manual Verification

Test core functionality:

```bash
# Test web GUI
python -m vhs_upscaler.gui

# Test video processing (requires input video)
python -m vhs_upscaler.vhs_upscale -i sample.mp4 -o test_output.mp4 -p vhs

# Check PyTorch CUDA
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

# Check installed packages
pip list | findstr /I "torch gradio demucs gfpgan vapoursynth"
```

## Troubleshooting

### Installation Script Fails

**Error**: "Execution policy error"

**Solution**: Allow script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Error**: "pip not found"

**Solution**: Ensure Python is in PATH:
```bash
python -m ensurepip --upgrade
python -m pip --version
```

### PyTorch CUDA Not Available

**Error**: `torch.cuda.is_available()` returns `False`

**Solutions**:

1. **Check NVIDIA driver**:
   ```bash
   nvidia-smi
   ```
   Update if driver < 530.

2. **Reinstall PyTorch with correct CUDA version**:
   ```bash
   # Uninstall current PyTorch
   pip uninstall torch torchaudio

   # Reinstall with matching CUDA
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

3. **Check CUDA installation**:
   - PyTorch includes CUDA runtime, no separate CUDA toolkit needed
   - Ensure you're using the CUDA index URL, not the CPU-only version

### VapourSynth Installation Fails

**Error**: "7-Zip not found"

**Solution**: Install 7-Zip:
```bash
winget install 7zip.7zip
```

Or download VapourSynth installer manually:
1. Download: https://github.com/vapoursynth/vapoursynth/releases
2. Run installer
3. `pip install vapoursynth havsfunc`

### FFmpeg Not Found

**Error**: "ffmpeg: command not found"

**Solution**: Install FFmpeg and add to PATH:

```bash
# Option 1: winget
winget install FFmpeg

# Option 2: Chocolatey
choco install ffmpeg

# Option 3: Manual
# 1. Download: https://ffmpeg.org/download.html
# 2. Extract to C:\ffmpeg
# 3. Add C:\ffmpeg\bin to PATH environment variable
```

**Verify FFmpeg**:
```bash
ffmpeg -version
```

### Out of Memory Errors

**Error**: "CUDA out of memory"

**Solutions**:

1. **Reduce target resolution**:
   ```bash
   # Use 1080p instead of 4K
   python -m vhs_upscaler.vhs_upscale -i video.mp4 -o output.mp4 -r 1080
   ```

2. **Use CPU mode**:
   ```bash
   python -m vhs_upscaler.vhs_upscale -i video.mp4 -o output.mp4 --engine ffmpeg --encoder libx265
   ```

3. **Close other GPU applications** (browsers, games, etc.)

### Disk Space Issues

**Error**: "No space left on device"

**Solutions**:

1. **Free up disk space** (TerminalAI needs ~10GB for temp files during processing)

2. **Change temp directory**:
   ```bash
   # Set temp directory to different drive
   set TEMP=D:\temp
   set TMP=D:\temp
   ```

3. **Clean up after processing**:
   - Temporary files are automatically removed
   - Check `logs/` directory for old logs

## Next Steps

### 1. Launch the Web GUI

```bash
python -m vhs_upscaler.gui
```

Opens at: http://localhost:7860

### 2. Process Your First Video

**Command Line**:
```bash
# VHS restoration
python -m vhs_upscaler.vhs_upscale -i old_vhs.mp4 -o restored.mp4 -p vhs

# YouTube download and upscale
python -m vhs_upscaler.vhs_upscale -i "https://youtube.com/watch?v=VIDEO_ID" -o upscaled.mp4

# Full features (v1.5.0)
python -m vhs_upscaler.vhs_upscale \
  -i family_video.mp4 \
  -o restored.mp4 \
  --preset vhs \
  --face-restore --face-model codeformer \
  --audio-enhance deepfilternet \
  --audio-sr --audiosr-model speech \
  -r 1080
```

**Web GUI**:
1. Open http://localhost:7860
2. Upload video or paste YouTube URL
3. Select preset (vhs, dvd, clean, etc.)
4. Click "Add to Queue"
5. Monitor progress in Queue tab

### 3. Explore Advanced Features

**Video Analysis**:
```bash
# Analyze video characteristics
python -m vhs_upscaler.vhs_upscale analyze video.mp4

# Auto-detect optimal settings
python -m vhs_upscaler.vhs_upscale upscale video.mp4 -o output.mp4 --auto-detect
```

**Batch Processing**:
```bash
# Process all videos in a folder
python -m vhs_upscaler.vhs_upscale batch ./input_videos/ ./output_videos/
```

**Watch Folder Automation**:
```bash
# Auto-process videos as they appear
python scripts/watch_folder.py --config watch_config.yaml
```

## Additional Resources

- **Main Documentation**: [README.md](README.md)
- **Best Practices**: [BEST_PRACTICES.md](BEST_PRACTICES.md)
- **Deinterlacing Guide**: [vhs_upscaler/DEINTERLACE_QUICKSTART.md](vhs_upscaler/DEINTERLACE_QUICKSTART.md)
- **GitHub Issues**: https://github.com/parthalon025/terminalai/issues

## Getting Help

If you encounter issues:

1. **Run verification**: `python verify_setup.py --verbose`
2. **Check logs**: `logs/vhs_upscaler_*.log`
3. **Enable verbose mode**: Add `-v` flag to commands
4. **Search issues**: https://github.com/parthalon025/terminalai/issues
5. **Create issue**: Include error message, OS, GPU, and verification report

## System Requirements Summary

### Minimum

- Windows 10/11 (64-bit)
- Python 3.10+
- 8 GB RAM
- 10 GB free disk space
- FFmpeg

### Recommended

- Windows 11
- Python 3.13
- 16+ GB RAM
- SSD with 50+ GB free
- NVIDIA RTX 3080+ (12+ GB VRAM)
- NVIDIA Driver 535+
- Maxine SDK or Real-ESRGAN

### For 4K Processing

- 32+ GB RAM
- NVIDIA RTX 4080+ (16+ GB VRAM)
- NVMe SSD
- CUDA 12.1+

---

**Version**: 1.0
**Last Updated**: 2025-12-18
**Compatible with**: TerminalAI v1.5.0+
