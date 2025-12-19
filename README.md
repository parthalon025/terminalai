<p align="center">
  <h1 align="center">🎬 TerminalAI - Professional Video Restoration Suite</h1>
  <p align="center">
    <strong>AI-powered video upscaling and restoration with NVIDIA RTX Video SDK, Real-ESRGAN, AI audio enhancement, and batch processing automation</strong>
  </p>
  <p align="center">
    <em>Transform VHS tapes, DVDs, and vintage footage into crystal-clear 4K video with professional-grade AI restoration</em>
  </p>
</p>

<p align="center">
  <a href="https://github.com/parthalon025/terminalai/releases"><img src="https://img.shields.io/badge/version-1.5.1-blue?style=flat-square" alt="Version 1.5.1"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10--3.13-blue?style=flat-square&logo=python&logoColor=white" alt="Python 3.10-3.13"></a>
  <a href="https://download.pytorch.org/whl/cu121"><img src="https://img.shields.io/badge/CUDA-12.1%2F12.8-76B900?style=flat-square&logo=nvidia&logoColor=white" alt="CUDA 12.1/12.8"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"></a>
  <a href="https://developer.nvidia.com/rtx-video-sdk"><img src="https://img.shields.io/badge/RTX_Video_SDK-Supported-76B900?style=flat-square&logo=nvidia&logoColor=white" alt="RTX Video SDK"></a>
  <a href="https://gradio.app/"><img src="https://img.shields.io/badge/Gradio-Web_GUI-orange?style=flat-square" alt="Gradio"></a>
</p>

<p align="center">
  <a href="#-quick-install">Quick Install</a> •
  <a href="#-features">Features</a> •
  <a href="#-whats-new">What's New</a> •
  <a href="#-web-gui">Web GUI</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-requirements">Requirements</a>
</p>

---

## 🚀 Quick Install

### Windows (Recommended for RTX GPUs)

Complete automated installation with RTX Video SDK support:

```bash
# Clone repository
git clone https://github.com/parthalon025/terminalai.git
cd terminalai

# Run automated Windows installer
python install_windows.py --full

# Launch GUI
python -m vhs_upscaler.gui
```

The Windows installer automatically:
- Detects Python 3.10-3.13 (recommends 3.12 for RTX 50 series)
- Installs PyTorch with CUDA 12.1/12.8 support
- Configures all AI features (Real-ESRGAN, GFPGAN, CodeFormer, DeepFilterNet, AudioSR, Demucs)
- Detects RTX GPU and offers RTX Video SDK setup
- Verifies installation and provides next steps

See [Windows Installation Guide](docs/installation/WINDOWS_INSTALLATION.md) for details.

### Manual Installation (All Platforms)

```bash
# 1. Clone repository
git clone https://github.com/parthalon025/terminalai.git
cd terminalai

# 2. Install with all features
pip install -e .

# 3. For NVIDIA GPUs: Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 4. Launch GUI
python -m vhs_upscaler.gui
```

Opens automatically at **http://localhost:7860**

---

## ✨ Features

### Core Video Processing

| Feature | Description | Requirements |
|---------|-------------|--------------|
| 🎬 **RTX Video SDK** | NVIDIA's latest AI upscaling with Super Resolution + Artifact Reduction + HDR | RTX 20/30/40/50 series |
| 🤖 **Real-ESRGAN AI** | Cross-platform AI upscaling (supports AMD, Intel, NVIDIA) | Vulkan GPU |
| 📺 **VHS Restoration** | Optimized presets for vintage footage with deinterlacing + denoise | FFmpeg |
| 🎞️ **Batch Processing** | Queue multiple videos with parallel processing support | - |
| 🎨 **HDR Conversion** | SDR to HDR10/HLG with tone mapping | - |
| 🎯 **Hardware Encoding** | NVENC, QuickSync, AMF acceleration for fast encoding | GPU |

### AI Enhancement

| Feature | Technology | Quality | GPU Acceleration |
|---------|-----------|---------|------------------|
| 👤 **Face Restoration** | CodeFormer + GFPGAN | ⭐⭐⭐⭐⭐ | CUDA |
| 🔊 **Audio Denoising** | DeepFilterNet AI | ⭐⭐⭐⭐⭐ | CUDA (optional) |
| 🎵 **Audio Upsampling** | AudioSR (48kHz) | ⭐⭐⭐⭐ | CUDA |
| 🎼 **Surround Upmix** | Demucs AI (stereo → 5.1/7.1) | ⭐⭐⭐⭐⭐ | CUDA |

### Automation & Integration

| Feature | Description |
|---------|-------------|
| 📁 **Watch Folders** | Auto-process new videos from monitored directories |
| ⬇️ **YouTube Integration** | Download and upscale in one step (yt-dlp) |
| 📬 **Notifications** | Discord, Slack webhooks + email alerts |
| 🎉 **First-Run Wizard** | Interactive setup with hardware detection and model downloads |
| 🔍 **Hardware Detection** | Automatic GPU detection and optimal settings configuration |
| 🌙 **Cinema Dark Theme** | Modern UI with Discord Blue accents (#5865f2) |
| 📊 **Real-time Progress** | Live processing status with ETA and statistics |

### Universal Compatibility

| Platform | GPU Support | Quality |
|----------|-------------|---------|
| **NVIDIA RTX 50/40/30/20** | RTX Video SDK + NVENC + CUDA | ⭐⭐⭐⭐⭐ Best |
| **NVIDIA GTX 10/16 series** | Real-ESRGAN + NVENC | ⭐⭐⭐⭐ Great |
| **AMD RDNA3/2** | Real-ESRGAN (Vulkan) | ⭐⭐⭐⭐ Great |
| **Intel Arc** | Real-ESRGAN + QuickSync | ⭐⭐⭐⭐ Great |
| **CPU Only** | FFmpeg upscaling | ⭐⭐⭐ Good |

---

## 🆕 What's New

### v1.5.1 (December 2025) - RTX Video SDK Integration

**RTX Video SDK - Best-in-Class AI Upscaling** (RTX 20+ GPUs):
- **Super Resolution**: AI-powered 4x upscaling with edge/texture refinement
- **Artifact Reduction**: Removes VHS tracking errors, compression blockyness, color bleeding
- **SDR to HDR10**: Automatic tone mapping for modern TVs
- **Setup Wizard**: Run `terminalai-setup-rtx` for guided installation
- Download SDK: [developer.nvidia.com/rtx-video-sdk](https://developer.nvidia.com/rtx-video-sdk)

**Maxine Deprecated**: Legacy NVIDIA Maxine support archived in favor of RTX Video SDK

**First-Run Wizard** 🎉:
- Interactive guided setup on first launch
- Automatic hardware detection (NVIDIA/AMD/Intel GPU)
- Real-time model download progress (speed, ETA, percentage)
- Pre-configured optimal settings based on your hardware
- Clear GPU capability banners with color coding
- See [First Run Wizard Guide](docs/FIRST_RUN_WIZARD.md)

**Hardware Detection** 🔍:
- Smart GPU detection with vendor-specific optimization
- VRAM detection and resolution recommendations
- Feature availability warnings (RTX Video SDK, NVENC, CUDA)
- Color-coded status: Green (optimal), Blue (good), Yellow (limited), Red (CPU-only)
- See [Hardware Detection Guide](docs/HARDWARE_DETECTION.md)

**GUI Redesign**:
- Cinema-grade dark theme (#0a0e1a background)
- Discord Blue accents (#5865f2) for professional appearance
- Hardware-accelerated animations with 60fps smoothness
- WCAG 2.1 AA accessibility compliance
- Improved tooltips and user guidance

### v1.5.0 (December 2025) - AI Audio & Automation

**AI Audio Enhancement**:
- **DeepFilterNet**: State-of-the-art AI denoising for crystal-clear speech
- **AudioSR**: AI-based audio super-resolution to 48kHz with speech/music models
- **Automatic Fallbacks**: Gracefully degrades to FFmpeg when AI unavailable
- **GPU Acceleration**: 5-10× faster processing with CUDA

**Enhanced Face Restoration**:
- **CodeFormer**: Best-in-class face restoration (alternative to GFPGAN)
- Adjustable fidelity weight (0.5-0.9) for quality/realism balance
- Automatic model download with progress tracking
- See [CodeFormer Integration Guide](docs/guides/CODEFORMER_INTEGRATION.md)

**Automation & Notifications**:
- Watch folder monitoring for automatic video processing
- Discord/Slack webhook notifications
- Email alerts via SMTP
- Job completion and error notifications

**Documentation**:
- 7 new quick-start guides (VHS, YouTube, Audio)
- [AudioSR Integration Guide](docs/guides/AUDIOSR_INTEGRATION.md) (600+ lines)
- [CodeFormer Guide](docs/guides/CODEFORMER_INTEGRATION.md) (300+ lines)
- 50+ new unit tests for reliability

### v1.4.x - Enhanced Processing

**Watch Folder Automation** (v1.4.5):
- Monitor directories for new files and auto-process
- Multi-folder support with per-folder presets
- Smart debouncing and lock file protection

**Intelligent Video Analysis** (v1.4.3):
- Auto-detect scan type, noise level, source format
- Recommend optimal presets and settings
- Save/load analysis configs for batch workflows
- Detect VHS artifacts (tracking errors, color bleeding)

**Smart UI Improvements** (v1.4.0):
- Conditional advanced options based on selections
- Beginner-friendly tooltips with plain-English explanations
- Content-based guidance for different video types

---

## 🖥️ Web GUI

Modern Gradio interface with professional workflow:

```
┌─────────────────────────────────────────────────────────────┐
│  🎬 TerminalAI Video Restoration Suite         v1.5.1       │
│  RTX Video SDK + AI Audio + Face Restoration                │
├─────────────────────────────────────────────────────────────┤
│  📹 Single │ 📚 Batch │ 📋 Queue │ 📜 Logs │ ⚙️ Settings     │
├─────────────────────────────────────────────────────────────┤
│  ┌─ Upload Video ──────────┐ ┌─ YouTube URL ────────────┐  │
│  │  [Drag & Drop Here]     │ │ [youtube.com/watch?v=...] │  │
│  │  1920×1080, 29.97fps    │ └───────────────────────────┘  │
│  │  h264 codec, 500MB      │                                │
│  └─────────────────────────┘  Preset: [vhs ▼]              │
│                               Engine: [rtxvideo ▼]          │
│  ┌─ RTX Video Options ──────┐  Resolution: [1080p ▼]       │
│  │  ✓ Artifact Reduction    │  Encoder: [hevc_nvenc ▼]    │
│  │    Strength: [0.5]       │  Quality: [Best ▼]          │
│  │  ✓ SDR to HDR10          │                              │
│  └──────────────────────────┘  [➕ Add to Queue]            │
│                                                             │
│  ┌─ Hardware Status ─────────────────────────────────────┐ │
│  │ 🟢 RTX 5080 - 16GB VRAM | Optimal for 4K AI Upscaling │ │
│  │ ✓ RTX Video SDK | ✓ NVENC | ✓ CUDA 12.8               │ │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ Queue Statistics ────────────────────────────────────┐ │
│  │ Pending: 2 │ Processing: 1 │ Done: 15 │ Failed: 0     │ │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### GUI Tabs

| Tab | Function |
|-----|----------|
| 📹 **Single Video** | Upload or URL input with full processing options |
| 📚 **Batch Processing** | Add multiple videos with shared settings |
| 📋 **Queue** | Real-time progress monitoring with pause/resume |
| 📜 **Logs** | Detailed processing logs with filtering |
| ⚙️ **Settings** | Output directory, dark mode, notifications |
| ℹ️ **About** | System info, GPU detection, feature availability |

### Processing Pipeline Visualization

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   INPUT      │     │  PREPROCESS  │     │  AI UPSCALE  │     │   OUTPUT     │
│              │────▶│              │────▶│              │────▶│              │
│ VHS/DVD/MP4  │     │ Deinterlace  │     │ RTX Video SDK│     │ HEVC/H.264   │
│ YouTube URL  │     │ Denoise      │     │ or Real-ESRGAN│     │ HDR10 (opt)  │
│ Drag & Drop  │     │ Color Fix    │     │ or FFmpeg    │     │ 1080p/4K     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                       │
┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│ AUDIO OUTPUT │     │ AUDIO ENCODE │     │ AI AUDIO     │◀───────────┘
│              │◀────│              │◀────│              │
│ Final Video  │     │ AAC/AC3/FLAC │     │ DeepFilterNet│
│ Ready to Use │     │ 5.1/7.1 Mix  │     │ AudioSR      │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## 📖 Usage

### Launch GUI (Recommended)

```bash
python -m vhs_upscaler.gui
# Opens at http://localhost:7860
```

### Command Line Examples

**Basic VHS Restoration with RTX Video SDK:**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "family_vhs_1995.mp4" \
  -o "restored_1995.mp4" \
  --preset vhs \
  --engine rtxvideo \
  --rtxvideo-artifact-reduction \
  --rtxvideo-hdr \
  -r 1080
```

**AI-Enhanced VHS with Face Restoration (v1.5.0 Features):**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "family_christmas.mp4" \
  -o "restored_christmas.mp4" \
  --preset vhs \
  --engine realesrgan \
  --face-restore --face-model codeformer --face-fidelity 0.7 \
  --audio-enhance deepfilternet \
  --audio-sr --audiosr-model speech \
  -r 1080
```

**DVD to 4K HDR with Surround Sound:**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "movie_dvd.mkv" \
  -o "movie_4k_hdr.mkv" \
  --preset dvd \
  --engine rtxvideo \
  --rtxvideo-hdr \
  --audio-upmix demucs \
  --audio-layout 5.1 \
  --audio-format eac3 \
  -r 2160
```

**Anime Upscaling to 4K:**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "anime_episode.mp4" \
  -o "anime_4k.mp4" \
  --preset clean \
  --engine realesrgan \
  --realesrgan-model realesrgan-x4plus-anime \
  -r 2160
```

**YouTube Download and Enhance:**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=VIDEO_ID" \
  -o "youtube_enhanced.mp4" \
  --preset youtube \
  --engine auto \
  -r 1080
```

**CPU-Only Processing (No GPU Required):**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "video.mp4" \
  -o "upscaled.mp4" \
  --preset vhs \
  --engine ffmpeg \
  --encoder libx265 \
  -r 1080
```

### Common Options Reference

**Core Options:**
- `-i, --input`: Input video file or YouTube URL
- `-o, --output`: Output video file path
- `-r, --resolution`: Target height (720/1080/1440/2160)
- `-p, --preset`: vhs/dvd/webcam/youtube/clean
- `--encoder`: hevc_nvenc/h264_nvenc/libx265/libx264

**RTX Video SDK Options:**
- `--engine rtxvideo`: Enable RTX Video SDK upscaling
- `--rtxvideo-artifact-reduction`: Enable artifact reduction
- `--rtxvideo-artifact-strength <0.0-1.0>`: Artifact reduction strength (default: 0.5)
- `--rtxvideo-hdr`: Enable SDR to HDR10 conversion

**Real-ESRGAN Options:**
- `--engine realesrgan`: Use Real-ESRGAN AI upscaling
- `--realesrgan-model`: x4plus, x4plus-anime, animevideov3
- `--realesrgan-denoise <0.0-1.0>`: Denoise strength (default: 0.5)

**AI Audio Options (v1.5.0):**
- `--audio-enhance deepfilternet`: AI audio denoising
- `--audio-sr`: Enable AudioSR upsampling to 48kHz
- `--audiosr-model`: speech, music, basic
- `--audio-upmix demucs`: AI surround upmix (stereo → 5.1/7.1)
- `--audio-layout`: stereo, 5.1, 7.1

**Face Restoration Options (v1.5.0):**
- `--face-restore`: Enable face restoration
- `--face-model`: codeformer, gfpgan
- `--face-fidelity <0.5-0.9>`: CodeFormer fidelity (default: 0.7)

**HDR Options:**
- `--hdr hdr10`: Convert to HDR10
- `--hdr hlg`: Convert to HLG
- `--hdr-brightness <nits>`: Peak brightness (default: 400)

See full CLI reference: `python -m vhs_upscaler.vhs_upscale --help`

---

## ⚙️ Presets

Built-in presets optimized for different source types:

| Preset | Source Type | Deinterlace | Denoise | Best For |
|--------|-------------|-------------|---------|----------|
| **vhs** | 480i VHS tapes | ✅ Yes (YADIF) | Strong (hqdn3d 3,2,3,2) | Home videos, VHS recordings |
| **dvd** | 480p/576p DVDs | ✅ Yes | Moderate (hqdn3d 2,1,2,1) | DVD rips, broadcast captures |
| **webcam** | Low-quality webcam | ❌ No | Strong (hqdn3d 4,3,4,3) | Old webcam footage |
| **youtube** | YouTube downloads | ❌ No | Light | Downloaded web videos |
| **clean** | High-quality sources | ❌ No | None | Already clean HD/4K content |

**Custom Presets**: Edit `vhs_upscaler/config.yaml` to add your own presets.

---

## 💻 Requirements

### Hardware

| Component | Minimum | Recommended | Best |
|-----------|---------|-------------|------|
| **GPU** | None (CPU fallback) | GTX 1660 Ti | RTX 4080/5080 |
| **VRAM** | - | 6GB | 16GB+ |
| **RAM** | 8GB | 16GB | 32GB+ |
| **Storage** | 10GB free | 50GB SSD | 100GB+ NVMe SSD |
| **CPU** | 4 cores | 8 cores | 16+ cores |

**GPU Compatibility:**
- NVIDIA RTX 20/30/40/50 series: RTX Video SDK + NVENC + CUDA ⭐⭐⭐⭐⭐
- NVIDIA GTX 10/16 series: Real-ESRGAN + NVENC ⭐⭐⭐⭐
- AMD RDNA2/3: Real-ESRGAN (Vulkan) ⭐⭐⭐⭐
- Intel Arc: Real-ESRGAN + QuickSync ⭐⭐⭐⭐
- CPU Only: FFmpeg upscaling ⭐⭐⭐

### Software

**Required:**
- **Python**: 3.10, 3.11, 3.12, or 3.13
  - Python 3.12 recommended for RTX 50 series (CUDA 12.8 support)
  - Python 3.13 has limited AI package compatibility
- **FFmpeg**: Latest version (5.0+)

**Optional (for best quality):**
- **NVIDIA Driver**: 535+ (for RTX features)
- **CUDA**: 12.1 or 12.8 (included with PyTorch)
- **RTX Video SDK**: 1.1.0+ (download from NVIDIA)
- **Real-ESRGAN ncnn-vulkan**: For AMD/Intel GPU upscaling

### Python Dependencies

Core dependencies (auto-installed):
```
yt-dlp>=2023.0.0       # YouTube downloading
pyyaml>=6.0            # Configuration
gradio>=4.0.0          # Web interface
torch>=2.0.0           # PyTorch for AI
torchaudio>=2.0.0      # Audio processing
opencv-python>=4.8.0   # Video processing
numpy>=1.24.0          # Array operations
watchdog>=3.0.0        # Watch folder automation
requests>=2.28.0       # HTTP notifications
nvidia-ml-py>=12.0.0   # GPU detection
```

AI features (optional, auto-installed with `--full`):
```
demucs>=4.0.0          # AI surround upmix
deepfilternet>=0.5.0   # AI audio denoising
audiosr>=0.0.4         # AI audio upsampling
gfpgan>=1.3.0          # Face restoration
facexlib>=0.2.5        # Face detection
realesrgan>=0.3.0      # AI upscaling
```

---

## 🔧 Installation Options

### Option 1: Automated Windows Installer (Recommended)

```bash
python install_windows.py --full
```

Features:
- Automatic Python version detection
- PyTorch with CUDA 12.1/12.8 installation
- All AI features configured
- RTX Video SDK setup wizard
- Verification and diagnostics

### Option 2: Quick Install (All Platforms)

```bash
pip install -e .
```

Installs all features automatically.

### Option 3: Selective Installation

```bash
# Base installation only
pip install -e .

# Add CUDA acceleration
pip install -e ".[cuda]"

# Add audio AI features
pip install -e ".[audio]"

# Add face restoration
pip install -e ".[face]"

# Add development tools
pip install -e ".[dev]"
```

### Option 4: Manual PyTorch CUDA Setup

For NVIDIA GPUs, ensure PyTorch has CUDA support:

```bash
# CUDA 12.1 (RTX 20/30/40 series)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# CUDA 12.8 (RTX 50 series with Python 3.12+)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Verify CUDA
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

---

## 🧪 Testing

Run comprehensive test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=vhs_upscaler --cov-report=html

# Run specific test category
pytest tests/test_gui*.py -v
pytest tests/test_audio*.py -v
pytest tests/test_rtx*.py -v
```

**Test Coverage**: 160+ tests covering GUI, queue management, audio processing, RTX Video SDK integration, and more.

---

## 🔧 Troubleshooting

### Common Issues

<details>
<summary><b>RTX Video SDK not detected</b></summary>

**Solution:**
1. Download RTX Video SDK from [developer.nvidia.com/rtx-video-sdk](https://developer.nvidia.com/rtx-video-sdk)
2. Run setup wizard: `terminalai-setup-rtx`
3. Verify GPU: RTX 20 series or newer required
4. Check driver: NVIDIA Driver 535+ required

</details>

<details>
<summary><b>CUDA not available / PyTorch not using GPU</b></summary>

**Solution:**
```bash
# Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

</details>

<details>
<summary><b>FFmpeg not found</b></summary>

**Solution:**
```bash
# Windows (winget)
winget install FFmpeg

# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install ffmpeg

# Verify
ffmpeg -version
```

</details>

<details>
<summary><b>AI features not working (DeepFilterNet, AudioSR, CodeFormer)</b></summary>

**Solution:**
```bash
# Reinstall AI dependencies
pip install demucs deepfilternet gfpgan facexlib realesrgan

# AudioSR may require older numpy
pip install "numpy<2" audiosr

# Verify
python -c "import deepfilternet; print('DeepFilterNet OK')"
python -c "import gfpgan; print('GFPGAN OK')"
```

</details>

<details>
<summary><b>Out of memory errors (CUDA/VRAM)</b></summary>

**Solution:**
- Reduce resolution: Use 1080p instead of 4K
- Use CPU mode: `--engine ffmpeg`
- Close other GPU applications
- Enable CPU mode for Demucs: `--demucs-device cpu`

**VRAM Requirements:**
| Resolution | Minimum VRAM | Recommended |
|------------|--------------|-------------|
| 720p | 2GB | 4GB |
| 1080p | 4GB | 6GB |
| 1440p | 6GB | 8GB |
| 2160p (4K) | 8GB | 12GB+ |

</details>

<details>
<summary><b>Slow processing / Not using GPU</b></summary>

**Solutions:**
1. Check CUDA PyTorch installation
2. Use GPU encoder: `--encoder hevc_nvenc`
3. Enable GPU upscaling: `--engine rtxvideo` or `--engine realesrgan`
4. Check GPU usage: `nvidia-smi`

</details>

### Diagnostic Commands

```bash
# System information
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None"}')"

# FFmpeg check
ffmpeg -version

# GPU check (NVIDIA)
nvidia-smi

# Feature verification
python scripts/installation/verify_installation.py

# Component check
python scripts/installation/verify_installation.py --check pytorch
python scripts/installation/verify_installation.py --check gfpgan
python scripts/installation/verify_installation.py --check gpu
```

**For more help:**
- [Windows Installation Guide](docs/installation/WINDOWS_INSTALLATION.md)
- [Installation Troubleshooting](docs/installation/INSTALLATION_TROUBLESHOOTING.md)
- [Verification Guide](docs/installation/VERIFICATION_GUIDE.md)
- [GitHub Issues](https://github.com/parthalon025/terminalai/issues)

---

## 📁 Project Structure

```
terminalai/
├── vhs_upscaler/              # Main package
│   ├── gui.py                 # Gradio web interface
│   ├── vhs_upscale.py         # Core processing pipeline
│   ├── queue_manager.py       # Batch queue system
│   ├── audio_processor.py     # AI audio processing
│   ├── face_restoration.py    # CodeFormer + GFPGAN
│   ├── notifications.py       # Webhooks + email alerts
│   ├── hardware_detection.py  # GPU detection and configuration
│   ├── first_run_wizard.py    # Interactive first-run setup
│   ├── rtx_video_sdk/         # RTX Video SDK Python wrapper
│   │   ├── __init__.py        # SDK initialization
│   │   ├── ctypes_wrapper.py  # DLL bindings
│   │   └── upscaler.py        # Upscaling implementation
│   └── config.yaml            # Default configuration
├── scripts/
│   ├── watch_folder.py        # Watch folder automation
│   └── installation/
│       ├── verify_installation.py  # Verification system
│       ├── install_windows.py      # Windows automated installer
│       └── patch_basicsr.py        # Compatibility patches
├── tests/                     # Test suite (160+ tests)
│   ├── test_gui*.py
│   ├── test_audio*.py
│   ├── test_rtx*.py
│   └── test_hardware*.py
├── docs/                      # Documentation
│   ├── installation/          # Installation guides
│   ├── guides/                # Feature guides
│   └── releases/              # Changelog
├── install_windows.py         # Windows installer
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Package configuration
└── README.md                  # This file
```

---

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `pytest tests/ -v`
4. Format code: `black vhs_upscaler/ tests/`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open Pull Request

**Development Setup:**
```bash
pip install -e ".[dev]"
pytest tests/ -v
black vhs_upscaler/ tests/ --check
ruff check vhs_upscaler/ tests/
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

**Free and open source** - use for personal or commercial projects.

---

## 🙏 Acknowledgments

**Core Technologies:**
- [NVIDIA RTX Video SDK](https://developer.nvidia.com/rtx-video-sdk) - State-of-the-art AI video enhancement
- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) - AI image/video super-resolution
- [CodeFormer](https://github.com/sczhou/CodeFormer) - Robust face restoration
- [DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) - Real-time AI audio denoising
- [AudioSR](https://github.com/haoheliu/versatile_audio_super_resolution) - Audio super-resolution
- [Demucs](https://github.com/facebookresearch/demucs) - AI audio source separation
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube/video downloading
- [FFmpeg](https://ffmpeg.org/) - Video/audio processing foundation
- [Gradio](https://gradio.app/) - Web interface framework

**Special Thanks:**
- NVIDIA for RTX Video SDK and GPU acceleration
- Tencent ARC Lab for Real-ESRGAN and CodeFormer
- All open-source contributors

---

## 🌟 Star History

If you find TerminalAI useful, please consider starring the repository!

---

<p align="center">
  <strong>Transform your vintage videos into stunning 4K with professional AI restoration</strong><br>
  Made with ❤️ by the TerminalAI community
</p>

<p align="center">
  <a href="https://github.com/parthalon025/terminalai">GitHub</a> •
  <a href="https://github.com/parthalon025/terminalai/issues">Issues</a> •
  <a href="docs/">Documentation</a> •
  <a href="docs/releases/CHANGELOG.md">Changelog</a>
</p>
