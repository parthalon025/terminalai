# Installation Troubleshooting Guide

Comprehensive troubleshooting for TerminalAI optional features and dependencies.

## Table of Contents

1. [Quick Diagnosis](#quick-diagnosis)
2. [PyTorch Issues](#pytorch-issues)
3. [VapourSynth Issues](#vapoursynth-issues)
4. [GFPGAN Issues](#gfpgan-issues)
5. [CodeFormer Issues](#codeformer-issues)
6. [DeepFilterNet Issues](#deepfilternet-issues)
7. [AudioSR Issues](#audiosr-issues)
8. [Demucs Issues](#demucs-issues)
9. [GPU Issues](#gpu-issues)
10. [FFmpeg Issues](#ffmpeg-issues)

---

## Quick Diagnosis

Run the installation verification script to identify issues:

```bash
# Full verification with detailed output
python verify_installation.py

# Quick check
python verify_installation.py --quick

# Save report for bug reports
python verify_installation.py --report installation_report.json

# Check specific component
python verify_installation.py --check pytorch
python verify_installation.py --check gfpgan
```

---

## PyTorch Issues

### Issue: PyTorch Not Found

**Error:**
```
[UNAVAILABLE] PyTorch
ModuleNotFoundError: No module named 'torch'
```

**Solution:**
```bash
# Install PyTorch (CPU version)
pip install torch torchaudio

# Or for CUDA 11.8
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Or for CUDA 12.1
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Verify Installation:**
```bash
python -c "import torch; print(torch.__version__)"
```

### Issue: CUDA Not Available

**Symptoms:**
```
torch.cuda.is_available() = False
```

**Diagnosis:**
```bash
# Check NVIDIA driver
nvidia-smi

# Check PyTorch CUDA version
python -c "import torch; print(f'CUDA: {torch.version.cuda}')"
```

**Solutions:**

1. **Wrong PyTorch Version:**
   ```bash
   # Uninstall CPU version
   pip uninstall torch torchaudio

   # Install CUDA version (match your CUDA version)
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

2. **CUDA Driver Mismatch:**
   - Check CUDA version: `nvidia-smi` (top right)
   - Install matching PyTorch version from https://pytorch.org/get-started/locally/

3. **NVIDIA Driver Too Old:**
   - Update NVIDIA drivers: https://www.nvidia.com/drivers
   - Minimum: 450+ for CUDA 11, 525+ for CUDA 12

### Issue: Out of Memory (OOM) Errors

**Error:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**

1. **Reduce Batch Size:**
   - For face restoration: Process fewer frames at once
   - For Demucs: Use smaller segments

2. **Free GPU Memory:**
   ```python
   import torch
   torch.cuda.empty_cache()
   ```

3. **Use CPU:**
   ```bash
   # Force CPU mode
   export CUDA_VISIBLE_DEVICES=""
   ```

4. **Monitor GPU Usage:**
   ```bash
   # Watch GPU memory in real-time
   watch -n 1 nvidia-smi
   ```

---

## VapourSynth Issues

### Issue: VapourSynth Not Found

**Error:**
```
[UNAVAILABLE] VapourSynth
ModuleNotFoundError: No module named 'vapoursynth'
```

**Solution:**

**Windows:**
1. Download VapourSynth installer: https://github.com/vapoursynth/vapoursynth/releases
2. Install VapourSynth runtime
3. Install Python bindings:
   ```bash
   pip install vapoursynth
   ```

**Linux:**
```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:djcj/vapoursynth
sudo apt update
sudo apt install vapoursynth python3-vapoursynth

# Or build from source
pip install vapoursynth
```

**macOS:**
```bash
brew install vapoursynth
pip install vapoursynth
```

**Verify:**
```bash
python -c "import vapoursynth; print(vapoursynth.core.version())"
```

### Issue: QTGMC Not Available

**Error:**
```
[PARTIAL] VapourSynth
Missing: havsfunc (QTGMC support)
```

**Solution:**
```bash
pip install havsfunc
```

**Verify:**
```python
import vapoursynth as vs
import havsfunc
print("QTGMC available")
```

### Issue: VapourSynth Plugins Missing

**Error:**
```
vapoursynth.Error: Failed to load plugin
```

**Common Missing Plugins:**

1. **NNEDI3:**
   - Windows: Download from http://github.com/dubhater/vapoursynth-nnedi3/releases
   - Place DLL in VapourSynth plugins folder

2. **EEDI3:**
   - Windows: Download from http://github.com/HomeOfVapourSynthEvolution/VapourSynth-EEDI3/releases

3. **Check Plugin Directory:**
   ```python
   import vapoursynth as vs
   print(vs.core.plugins())
   ```

---

## GFPGAN Issues

### Issue: GFPGAN Not Installed

**Error:**
```
[UNAVAILABLE] GFPGAN
ModuleNotFoundError: No module named 'gfpgan'
```

**Solution:**
```bash
# Install GFPGAN and dependencies
pip install gfpgan basicsr opencv-python torch
```

**Verify:**
```bash
python -c "import gfpgan; print('GFPGAN OK')"
```

### Issue: GFPGAN Model Not Found

**Error:**
```
[PARTIAL] GFPGAN
GFPGAN installed but no models found
```

**Solution:**
```bash
# Download model automatically
python -m vhs_upscaler.face_restoration --download-model

# Or manual download
mkdir -p models/gfpgan
cd models/gfpgan
wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth
```

**Model Sizes:**
- GFPGANv1.3.pth: ~332 MB
- GFPGANv1.4.pth: ~348 MB

**Verify Model:**
```bash
ls -lh models/gfpgan/
```

### Issue: BasicSR Import Error

**Error:**
```
ImportError: cannot import name 'RRDBNet' from 'basicsr.archs.rrdbnet_arch'
```

**Solution:**
```bash
# Reinstall BasicSR
pip uninstall basicsr
pip install basicsr==1.4.2
```

### Issue: OpenCV Not Found

**Error:**
```
ModuleNotFoundError: No module named 'cv2'
```

**Solution:**
```bash
pip install opencv-python
```

---

## CodeFormer Issues

### Issue: CodeFormer Dependencies Missing

**Error:**
```
[UNAVAILABLE] CodeFormer
ModuleNotFoundError: No module named 'torch'
```

**Solution:**
```bash
# Install dependencies
pip install torch opencv-python

# Optional: Install CodeFormer package
pip install codeformer
```

### Issue: CodeFormer Model Not Found

**Error:**
```
[PARTIAL] CodeFormer
CodeFormer model not found
```

**Solution:**
```bash
# Download model
python -m vhs_upscaler.face_restoration --backend codeformer --download-model

# Or manual download
mkdir -p models/codeformer
cd models/codeformer
wget https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth
```

**Model Size:**
- codeformer.pth: ~360 MB

### Issue: CodeFormer Very Slow

**Symptoms:**
- Processing takes hours for short videos
- CPU usage at 100%

**Diagnosis:**
```bash
python verify_installation.py --check pytorch
# Check: cuda_available: false
```

**Solutions:**

1. **Install CUDA PyTorch:**
   ```bash
   pip uninstall torch
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Verify GPU Usage:**
   ```bash
   # Run CodeFormer and check GPU usage
   nvidia-smi -l 1
   ```

3. **CPU Mode Workaround:**
   - Process only key frames
   - Use GFPGAN instead (faster on CPU)
   - Consider cloud GPU (Google Colab, AWS)

---

## DeepFilterNet Issues

### Issue: DeepFilterNet Not Installed

**Error:**
```
[UNAVAILABLE] DeepFilterNet
ModuleNotFoundError: No module named 'df'
```

**Solution:**
```bash
# Install DeepFilterNet
pip install deepfilternet torch
```

**Verify:**
```bash
python -c "from df import enhance, init_df; print('DeepFilterNet OK')"
```

### Issue: DeepFilterNet Model Download Fails

**Error:**
```
Failed to download DeepFilterNet model
```

**Solutions:**

1. **Manual Model Download:**
   ```bash
   # Models auto-download on first use
   # Ensure internet connection available
   ```

2. **Proxy Issues:**
   ```bash
   # Set proxy if needed
   export HTTP_PROXY="http://proxy:port"
   export HTTPS_PROXY="http://proxy:port"
   ```

3. **Offline Installation:**
   - Download model from: https://github.com/Rikorose/DeepFilterNet/releases
   - Place in appropriate cache directory

### Issue: DeepFilterNet Audio Distortion

**Symptoms:**
- Processed audio sounds distorted or metallic
- Voices sound robotic

**Solutions:**

1. **Reduce Enhancement Strength:**
   - Use "moderate" instead of "aggressive" mode
   - Adjust filter parameters

2. **Check Sample Rate:**
   - DeepFilterNet works best at 48kHz
   - Ensure audio is resampled correctly

3. **Use Different Mode:**
   - Try FFmpeg enhancement for music content
   - DeepFilterNet optimized for speech

---

## AudioSR Issues

### Issue: AudioSR Not Installed

**Error:**
```
[UNAVAILABLE] AudioSR
ModuleNotFoundError: No module named 'audiosr'
```

**Solution:**
```bash
pip install audiosr torch torchaudio
```

**Verify:**
```bash
python -c "import audiosr; print('AudioSR OK')"
```

### Issue: AudioSR Model Download Fails

**Error:**
```
Error downloading AudioSR model
```

**Solutions:**

1. **Check Disk Space:**
   - AudioSR models are large (500MB+)
   - Ensure 2GB+ free space

2. **Network Issues:**
   - Models download from HuggingFace
   - Check firewall settings
   - Try manual download:
     ```bash
     # Models stored in ~/.cache/huggingface/
     ```

3. **Use Different Model:**
   ```bash
   # Try smaller model
   --audiosr-model basic  # Instead of speech/music
   ```

### Issue: AudioSR CUDA Out of Memory

**Error:**
```
RuntimeError: CUDA out of memory (AudioSR)
```

**Solutions:**

1. **Process Shorter Segments:**
   - Split audio into chunks
   - Process sequentially

2. **Use CPU:**
   ```bash
   --audiosr-device cpu
   ```

3. **Reduce Sample Rate:**
   - Target 44.1kHz instead of 48kHz if acceptable

---

## Demucs Issues

### Issue: Demucs Not Installed

**Error:**
```
[UNAVAILABLE] Demucs
ModuleNotFoundError: No module named 'demucs'
```

**Solution:**
```bash
pip install demucs torch torchaudio
```

**Verify:**
```bash
python -c "import demucs; print('Demucs OK')"
```

### Issue: Demucs Extremely Slow

**Symptoms:**
- Processing 1 minute takes hours
- CPU at 100%, GPU idle

**Diagnosis:**
```bash
python verify_installation.py --check demucs
# Check GPU availability
```

**Solutions:**

1. **Install CUDA PyTorch:**
   ```bash
   pip uninstall torch torchaudio
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Force GPU Usage:**
   ```bash
   python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
   ```

3. **Don't Use Demucs on CPU:**
   - Demucs is IMPRACTICAL on CPU (100x slower)
   - Use simpler upmix algorithms instead:
     ```bash
     --upmix-mode surround  # Instead of demucs
     ```

### Issue: Demucs Model Download Fails

**Error:**
```
Failed to download Demucs model
```

**Solutions:**

1. **Manual Download:**
   ```bash
   # Models download automatically on first use
   # Size: 1-3GB depending on model
   ```

2. **Use Smaller Model:**
   ```bash
   --demucs-model htdemucs  # Instead of htdemucs_ft
   ```

3. **Check Cache:**
   ```bash
   # Models stored in ~/.cache/torch/hub/
   ls -lh ~/.cache/torch/hub/
   ```

---

## GPU Issues

### Issue: NVIDIA GPU Not Detected

**Error:**
```
[UNAVAILABLE] GPU
No NVIDIA GPU detected
```

**Diagnosis:**
```bash
# Check driver installation
nvidia-smi

# Check device manager (Windows)
# Should show NVIDIA GPU under Display Adapters
```

**Solutions:**

1. **Install/Update NVIDIA Drivers:**
   - Windows: https://www.nvidia.com/drivers
   - Linux:
     ```bash
     # Ubuntu
     sudo ubuntu-drivers autoinstall
     # Or
     sudo apt install nvidia-driver-535
     ```

2. **Verify GPU:**
   ```bash
   nvidia-smi --query-gpu=name,driver_version --format=csv
   ```

3. **Optimus/Hybrid Graphics (Laptops):**
   - Ensure application using dedicated GPU
   - Windows: NVIDIA Control Panel → Manage 3D Settings
   - Linux: `prime-select nvidia`

### Issue: NVENC Not Available

**Error:**
```
[PARTIAL] FFmpeg
NVIDIA hardware encoders not available
```

**Solutions:**

1. **Update NVIDIA Drivers:**
   - NVENC requires driver 418.81+ (Linux) or 445.87+ (Windows)
   - Current driver: check `nvidia-smi`

2. **Check GPU Support:**
   - Not all NVIDIA GPUs support NVENC
   - Check: https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix

3. **Rebuild FFmpeg (Linux):**
   ```bash
   # FFmpeg may not be compiled with NVENC support
   ffmpeg -encoders | grep nvenc
   # Should show h264_nvenc, hevc_nvenc
   ```

4. **Use Software Encoding:**
   ```bash
   --encoder libx265  # Instead of hevc_nvenc
   ```

---

## FFmpeg Issues

### Issue: FFmpeg Not Found

**Error:**
```
[UNAVAILABLE] FFmpeg
FileNotFoundError: ffmpeg not found
```

**Solutions:**

**Windows:**
```bash
# Using winget
winget install FFmpeg

# Or download from https://ffmpeg.org/download.html
# Add to PATH
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch
sudo pacman -S ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Verify:**
```bash
ffmpeg -version
```

### Issue: FFmpeg Missing Codecs

**Error:**
```
Unknown encoder 'libx265'
```

**Solutions:**

1. **Install Full FFmpeg:**
   ```bash
   # Ubuntu - enable universe repository
   sudo add-apt-repository universe
   sudo apt update
   sudo apt install ffmpeg
   ```

2. **Build from Source (Linux):**
   ```bash
   # With all codecs
   git clone https://git.ffmpeg.org/ffmpeg.git
   cd ffmpeg
   ./configure --enable-gpl --enable-libx264 --enable-libx265 --enable-nonfree
   make -j$(nproc)
   sudo make install
   ```

3. **Static Build (Alternative):**
   - Download: https://johnvansickle.com/ffmpeg/ (Linux)
   - Download: https://www.gyan.dev/ffmpeg/builds/ (Windows)

### Issue: FFmpeg CUDA Filters Missing

**Error:**
```
No such filter: 'scale_cuda'
```

**Cause:**
- FFmpeg not compiled with CUDA support

**Solutions:**

1. **Install CUDA-Enabled FFmpeg:**
   ```bash
   # Windows: Download from https://github.com/BtbN/FFmpeg-Builds/releases
   # Look for "cuda" in filename
   ```

2. **Use CPU Filters:**
   ```bash
   # scale instead of scale_cuda
   # yadif instead of yadif_cuda
   ```

3. **Build with CUDA (Linux):**
   ```bash
   # Install CUDA toolkit first
   ./configure --enable-cuda --enable-cuvid --enable-nvenc --enable-nonfree
   make -j$(nproc)
   ```

---

## Common Error Patterns

### DLL Load Failed (Windows)

**Error:**
```
ImportError: DLL load failed while importing _C: The specified module could not be found.
```

**Solutions:**

1. **Install Visual C++ Redistributables:**
   - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Install both x64 and x86 versions

2. **Update Windows:**
   ```bash
   # Windows Update may have required components
   ```

### Permission Denied Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **Run as Administrator (Windows):**
   - Right-click → Run as Administrator

2. **Check File Permissions (Linux):**
   ```bash
   chmod +x script.py
   sudo chown -R $USER:$USER models/
   ```

3. **Virtual Environment:**
   ```bash
   # Create venv to avoid permission issues
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -e .
   ```

### Import Errors After Installation

**Error:**
```
ModuleNotFoundError after pip install
```

**Solutions:**

1. **Check Python Version:**
   ```bash
   # Ensure using correct Python
   python --version
   which python  # Linux/Mac
   where python  # Windows
   ```

2. **Reinstall in Correct Environment:**
   ```bash
   # Activate correct environment first
   pip install --force-reinstall package_name
   ```

3. **Clear pip Cache:**
   ```bash
   pip cache purge
   pip install --no-cache-dir package_name
   ```

---

## Performance Optimization

### Slow Processing

**General Tips:**

1. **Use GPU Acceleration:**
   - Verify: `python verify_installation.py --check gpu`
   - Install CUDA PyTorch if unavailable

2. **Hardware Encoding:**
   - Use NVENC for NVIDIA GPUs
   - Check: `ffmpeg -encoders | grep nvenc`

3. **Reduce Quality Settings:**
   - Lower CRF (18→23)
   - Smaller upscale factor (4x→2x)

4. **Process in Parallel:**
   - Use batch processing features
   - Multiple videos simultaneously

### High Memory Usage

**Solutions:**

1. **Process Shorter Segments:**
   - Split video into chunks
   - Process and reassemble

2. **Reduce Concurrent Jobs:**
   - Process fewer videos simultaneously
   - Adjust worker count in config

3. **Close Other Applications:**
   - Free system RAM
   - Free GPU memory

---

## Getting Help

### Collect Diagnostic Information

```bash
# Generate full report
python verify_installation.py --report diagnostic.json

# Check system info
python verify_installation.py

# Check specific component
python verify_installation.py --check pytorch
```

### Report Issues

Include in bug reports:
1. Installation verification output
2. Full error message and traceback
3. System information (OS, Python version, GPU)
4. Steps to reproduce

### Additional Resources

- **TerminalAI Documentation:** `docs/README.md`
- **FFmpeg Documentation:** https://ffmpeg.org/documentation.html
- **PyTorch Forums:** https://discuss.pytorch.org/
- **VapourSynth Forum:** https://forum.doom9.org/forumdisplay.php?f=82
- **GitHub Issues:** https://github.com/your-repo/terminalai/issues

---

## Quick Reference: Installation Commands

```bash
# Core requirements
pip install -e .

# All features
pip install torch torchaudio
pip install vapoursynth havsfunc
pip install gfpgan basicsr opencv-python
pip install deepfilternet audiosr demucs

# Individual features
pip install torch torchaudio              # PyTorch (AI features)
pip install vapoursynth havsfunc          # VapourSynth (QTGMC)
pip install gfpgan basicsr opencv-python  # GFPGAN
pip install deepfilternet                 # AI audio denoising
pip install audiosr                       # AI audio upsampling
pip install demucs                        # AI surround upmix

# Verification
python verify_installation.py
```
