# TerminalAI Quick Start

**Get up and running in 5 minutes**

## Installation (One Command)

```bash
# Clone repository
git clone https://github.com/parthalon025/terminalai.git
cd terminalai

# Install EVERYTHING (all AI features included)
pip install -e .

# That's it! ✨
```

## What You Get

After installation, you have ALL features:

✅ AI Video Upscaling (Real-ESRGAN)
✅ Face Restoration (GFPGAN)
✅ AI Audio Enhancement (DeepFilterNet, AudioSR)
✅ Surround Sound Upmixing (Demucs AI)
✅ Watch Folder Automation
✅ Webhook/Email Notifications
✅ GPU Acceleration Support

**No additional steps needed. Everything works.**

## Prerequisites

**Required:**
- Python 3.10+ (recommended: 3.11)
- FFmpeg (install separately)

**Optional:**
- NVIDIA GPU (for GPU acceleration)

### Install FFmpeg

**Windows:**
```bash
winget install FFmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## Launch GUI

```bash
python -m vhs_upscaler.gui
```

Opens at **http://localhost:7860**

## Process Your First Video

1. Open GUI at http://localhost:7860
2. Drag video file into browser
3. Select "VHS" preset (or DVD, YouTube, etc.)
4. Click "Add to Queue"
5. Watch real-time progress

**Done!**

## GPU Acceleration (NVIDIA)

For NVIDIA GPUs, ensure PyTorch has CUDA support:

```bash
# Check CUDA support
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# If False, reinstall PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## Verify Installation

```bash
python verify_installation.py
```

Checks all features and provides diagnostics.

## Command Line Usage

```bash
# Basic upscale
python -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4 --preset vhs

# With AI upscaling
python -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4 --engine realesrgan

# With face restoration
python -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4 --face-enhance

# With AI audio
python -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4 --audio-enhance deepfilternet
```

## Troubleshooting

### ImportError: No module named 'torch'

```bash
pip install torch torchaudio
```

### CUDA not available

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### FFmpeg not found

```bash
# Windows
winget install FFmpeg

# Linux
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

## Documentation

- **README.md** - Full feature list
- **INSTALLATION.md** - Detailed installation guide
- **docs/installation/WINDOWS_INSTALLATION.md** - Windows-specific guide
- **docs/VERIFICATION_GUIDE.md** - Verification details

## Getting Help

- Issues: https://github.com/parthalon025/terminalai/issues
- Documentation: https://github.com/parthalon025/terminalai#readme
- Diagnostics: `python verify_installation.py --report diagnostic.json`

## Summary

**Before (Old System):**
```bash
pip install -e .  # Only basic features
pip install -e ".[audio]"  # Add audio
pip install -e ".[faces]"  # Add face restoration
# ... many more steps ...
```

**After (New System):**
```bash
pip install -e .  # Everything works! ✨
```

**That's the entire installation. Enjoy!**
