# TerminalAI Installation Summary

**Quick reference for Windows RTX 5080 installation**

---

## System Status

- **OS**: Windows 10/11
- **Python**: 3.13.5 ✓
- **GPU**: NVIDIA GeForce RTX 5080 (16GB VRAM) ✓
- **Driver**: 591.59 (CUDA 12.x compatible) ✓
- **FFmpeg**: 8.0 ✓

---

## Quick Install (Recommended)

### Option 1: Windows-Specific Installer (Best for RTX)

```bash
# Interactive mode with prompts
python install_windows.py

# Or automated full install
python install_windows.py --full
```

**Features**:
- Auto-detects RTX 5080 and installs CUDA PyTorch
- Handles Windows-specific dependency order
- Provides detailed troubleshooting

### Option 2: Cross-Platform Installer (Updated)

```bash
# Full installation with Windows PyTorch support
python install.py --full

# Audio AI only
python install.py --audio
```

---

## Manual Installation (Step-by-Step)

### Step 1: Core (Required) - 5 minutes

```bash
# Install base package
pip install -e .

# Verify
python -c "import vhs_upscaler; print('Core installed')"
```

### Step 2: PyTorch with CUDA (For AI Features) - 10 minutes

```bash
# CRITICAL: Install PyTorch with CUDA FIRST
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify CUDA support
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"
```

**Expected output**:
```
CUDA: True, Device: NVIDIA GeForce RTX 5080
```

### Step 3: Audio AI (Optional) - 15 minutes

```bash
# Install Demucs (surround upmixing)
pip install demucs>=4.0.0

# Install DeepFilterNet (AI denoising) - may require Rust
pip install deepfilternet>=0.5.0

# Skip AudioSR if it fails (known Windows issues)
pip install audiosr>=0.0.4
```

### Step 4: Face Restoration (Optional) - 10 minutes

```bash
# Install in this exact order
pip install opencv-python>=4.5.0
pip install basicsr>=1.4.2
pip install facexlib>=0.2.5
pip install gfpgan>=1.3.0

# Download GFPGAN model (~350MB)
python -m vhs_upscaler.face_restoration --download-model
```

### Step 5: GPU Upscaling Engines (Optional) - 20 minutes

**NVIDIA Maxine** (Best quality for RTX):
1. Download: https://developer.nvidia.com/maxine
2. Extract to: `C:\Program Files\NVIDIA\Maxine`
3. Set environment variable:
   ```bash
   setx MAXINE_HOME "C:\Program Files\NVIDIA\Maxine"
   ```

**Real-ESRGAN** (Good quality, works on AMD/Intel too):
1. Download: https://github.com/xinntao/Real-ESRGAN/releases
2. Extract `realesrgan-ncnn-vulkan.exe` to PATH

---

## Verification

```bash
# Quick check
python scripts\verify_setup.py

# Detailed check
python install_windows.py --check
```

---

## What You Can Do Now

### Launch GUI

```bash
python -m vhs_upscaler.gui
```

**GUI Features**:
- Upload videos (drag-and-drop)
- Select presets (VHS, DVD, YouTube)
- Configure upscaling (Maxine/Real-ESRGAN/FFmpeg)
- Enable audio enhancement and surround upmixing
- Face restoration toggle
- Batch processing queue
- Real-time progress tracking

### CLI Processing

**Basic upscaling**:
```bash
python -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4 --preset vhs
```

**With GPU AI upscaling**:
```bash
python -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4 --engine maxine --preset vhs
```

**Full feature test** (if all installed):
```bash
python -m vhs_upscaler.vhs_upscale \
  -i old_vhs.mp4 \
  -o restored.mp4 \
  --preset vhs \
  --engine maxine \
  --resolution 1080p \
  --enhance-audio moderate \
  --upmix-audio demucs \
  --restore-faces
```

---

## Installation Tiers

### Tier 1: Minimal (Works Now) ✓

**Status**: READY
- Core package installed
- FFmpeg available
- CPU-based processing

**Capabilities**:
- YouTube downloading
- FFmpeg upscaling (CPU)
- Basic deinterlacing
- NVENC GPU encoding

### Tier 2: GPU Acceleration (Recommended)

**Status**: Drivers ready, engines needed
- RTX 5080 detected ✓
- NVENC encoders available ✓
- Maxine SDK: Not installed
- Real-ESRGAN: Not installed

**Capabilities (when installed)**:
- AI upscaling (2x-4x better quality)
- Faster processing with GPU
- Better detail preservation

### Tier 3: Audio AI (Optional)

**Status**: PyTorch installed, audio packages needed
- PyTorch 2.8.0 (CUDA ready) ✓
- Demucs: Not installed
- DeepFilterNet: Not installed

**Capabilities (when installed)**:
- AI audio denoising
- Surround sound upmixing (stereo → 5.1/7.1)
- Speech enhancement for VHS dialogue

### Tier 4: Face Restoration (Optional)

**Status**: Not installed
- GFPGAN: Not installed
- Models: Not downloaded

**Capabilities (when installed)**:
- AI face enhancement for talking heads
- Better detail in VHS portraits
- Improved facial features

---

## Known Issues and Solutions

### Issue: "torch.cuda.is_available() returns False"

**Solution**:
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Issue: "DeepFilterNet requires Rust compiler"

**Solution**:
1. Install Rust: https://www.rust-lang.org/tools/install
2. Restart terminal
3. `pip install deepfilternet`

### Issue: "AudioSR installation fails"

**Solution**: Skip it - AudioSR is optional and has Windows compatibility issues. Use DeepFilterNet instead.

### Issue: "VapourSynth not found"

**Solution**:
1. Install VapourSynth runtime: https://github.com/vapoursynth/vapoursynth/releases
2. Then: `pip install vapoursynth`

**Note**: VapourSynth is optional - FFmpeg yadif works for most cases.

---

## Next Steps by Use Case

### Use Case 1: Upscale VHS Home Videos

**Required**:
- Tier 1 (Core) ✓
- Tier 2 (Maxine or Real-ESRGAN) - Install one

**Optional but Recommended**:
- Tier 3 (Audio AI) - For dialogue clarity
- Tier 4 (Face Restoration) - For talking heads

**Installation**:
```bash
# Install Maxine SDK (manual download)
# Or install Real-ESRGAN (easier)

# For audio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install demucs deepfilternet

# For faces
pip install opencv-python basicsr facexlib gfpgan
python -m vhs_upscaler.face_restoration --download-model
```

### Use Case 2: YouTube Video Enhancement

**Required**:
- Tier 1 (Core) ✓

**Optional**:
- Tier 2 (GPU upscaling) - For quality boost
- Tier 3 (Audio AI) - For better audio

**Installation**:
```bash
# Minimal - already works!
# Just run: python -m vhs_upscaler.gui
```

### Use Case 3: Professional Video Restoration

**Required**:
- All tiers (full installation)

**Installation**:
```bash
python install_windows.py --full
```

---

## Documentation

- **Quick Start**: `README.md`
- **Windows Guide**: `docs/WINDOWS_INSTALLATION.md` (detailed)
- **Dependency Analysis**: `docs/DEPENDENCY_ANALYSIS.md` (technical)
- **This Summary**: `INSTALLATION_SUMMARY.md` (you are here)
- **Deployment**: `docs/DEPLOYMENT.md` (advanced topics)

---

## Installation Time Estimates

| Component | Time | Size |
|-----------|------|------|
| Core | 2-5 min | 400 MB |
| PyTorch CUDA | 5-10 min | 2.5 GB |
| Audio AI | 10-15 min | 3 GB (with models) |
| Face Restoration | 5-10 min | 600 MB |
| Maxine SDK | 10-15 min | 1 GB |
| Real-ESRGAN | 2-5 min | 100 MB |
| **Total (Full)** | **30-60 min** | **~8 GB** |

---

## Support

**Verification**:
```bash
python scripts\verify_setup.py
```

**Check specific features**:
```bash
# PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Demucs
python -c "import demucs; print('OK')"

# GFPGAN
python -c "import gfpgan; print('OK')"
```

**Logs**:
```bash
type logs\terminalai.log
```

**Get help**:
- GitHub Issues: https://github.com/parthalon025/terminalai/issues
- Documentation: `docs/` directory

---

## Summary

**Current Status**: Ready for basic use
- Core features working ✓
- GPU encoding available ✓
- AI features need installation

**Recommended Next Step**:
```bash
python install_windows.py --full
```

This will install all features with proper Windows/CUDA handling.

**Or start using now**:
```bash
python -m vhs_upscaler.gui
```

Your RTX 5080 will provide GPU-accelerated encoding even without AI upscaling engines installed!
