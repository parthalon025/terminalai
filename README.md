<p align="center">
  <h1 align="center">🎬 TerminalAI - Video Processing Suite</h1>
  <p align="center">
    <strong>AI-powered VHS video upscaling and YouTube downloading with NVIDIA RTX acceleration</strong>
  </p>
</p>

<p align="center">
  <a href="https://github.com/parthalon025/terminalai/releases"><img src="https://img.shields.io/badge/version-1.5.0-blue?style=flat-square" alt="Version 1.5.0"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"></a>
  <a href="https://developer.nvidia.com/maxine"><img src="https://img.shields.io/badge/NVIDIA-Maxine-76B900?style=flat-square&logo=nvidia&logoColor=white" alt="NVIDIA Maxine"></a>
  <a href="https://gradio.app/"><img src="https://img.shields.io/badge/Gradio-Web_GUI-orange?style=flat-square" alt="Gradio"></a>
  <a href="https://github.com/sczhou/CodeFormer"><img src="https://img.shields.io/badge/CodeFormer-Face_Restoration-purple?style=flat-square" alt="CodeFormer"></a>
</p>

<p align="center">
  <a href="#-quick-install">Quick Install</a> •
  <a href="#-features">Features</a> •
  <a href="#-web-gui">Web GUI</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-requirements">Requirements</a>
</p>

---

## 🚀 Quick Install

### One-Shot Install (Fastest)

Complete automated setup - from zero to ready in one command:

```bash
# Linux/Mac - Downloads and installs everything automatically
curl -sSL https://raw.githubusercontent.com/parthalon025/terminalai/main/one_shot_install.sh | bash
```

This installer will:
- ✓ Install Python 3.10+ if needed
- ✓ Install FFmpeg and system dependencies
- ✓ Clone repository and install TerminalAI
- ✓ Install all optional features (VapourSynth, GFPGAN, audio AI)
- ✓ Download and configure Real-ESRGAN
- ✓ Create shortcuts and verify installation
- ✓ Take you from zero to fully operational in minutes

### Automated Installer (Alternative)

```bash
# Clone the repository
git clone https://github.com/parthalon025/terminalai.git
cd terminalai

# Run comprehensive installer
python install.py              # Basic installation
# OR
python install.py --full       # Full installation with all features
python install.py --dev        # Development installation
python install.py --audio      # With audio AI features (Demucs)
```

The installer will:
- ✓ Verify Python 3.10+ and pip
- ✓ Install TerminalAI package with dependencies
- ✓ Check for FFmpeg, NVIDIA GPU, Maxine SDK, Real-ESRGAN
- ✓ Install optional features (VapourSynth, GFPGAN) if --full
- ✓ Verify installation is working
- ✓ Provide next steps and recommendations

### Manual Install

```bash
# 1. Clone the repository
git clone https://github.com/parthalon025/terminalai.git
cd terminalai

# 2. Install package (choose one)
pip install -e .                    # Basic install
pip install -e ".[dev]"             # With dev tools
pip install -e ".[audio]"           # With audio AI (Demucs)
pip install -e ".[full]"            # Everything
```

### Launch the GUI

```bash
# Start the web interface
python -m vhs_upscaler.gui
# OR
python vhs_upscaler/gui.py
```

Opens automatically at **http://localhost:7860**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎬 **AI Video Upscaling** | Multiple engines: NVIDIA Maxine, Real-ESRGAN, FFmpeg |
| 📺 **VHS Restoration** | Optimized presets for vintage footage (deinterlace + denoise) |
| 🔊 **Audio Enhancement** | Noise reduction, EQ, loudness normalization |
| 🎵 **Surround Upmix** | Stereo to 5.1/7.1 with FFmpeg or Demucs AI |
| ⬇️ **YouTube Integration** | Download and upscale YouTube videos in one step |
| 📁 **Drag & Drop Upload** | Simply drag video files into the browser |
| 🌙 **Dark Mode** | Easy on the eyes with theme toggle |
| 📊 **Stats Dashboard** | Real-time queue statistics and progress |
| 📋 **Queue System** | Batch process multiple videos with pause/resume |
| 🚀 **GPU Accelerated** | RTX Tensor Core + NVENC hardware encoding |
| 🎨 **HDR Output** | Convert to HDR10 or HLG format |
| 🔍 **Intelligent Analysis** | Auto-detect video characteristics and recommend optimal settings |
| 👁️ **Watch Folder Automation** | Monitor directories and auto-process new videos |
| 🔊 **AI Audio Enhancement** | DeepFilterNet AI denoising and AudioSR upsampling |
| 👤 **Dual Face Restoration** | GFPGAN and CodeFormer for enhanced face quality |
| 📬 **Notifications** | Webhook and email alerts for job completion |
| 💻 **Works Without NVIDIA** | Real-ESRGAN supports AMD/Intel GPUs, FFmpeg for CPU-only |

### What's New in v1.5.0

- **AI Audio Enhancement** - DeepFilterNet and AudioSR Integration:
  - **DeepFilterNet AI Denoising**: Superior speech clarity compared to traditional FFmpeg filters
  - **AudioSR Upsampling**: AI-based audio super-resolution to 48kHz with speech/music models
  - **Automatic Fallbacks**: Gracefully falls back to FFmpeg when AI backends unavailable
  - **GPU Acceleration**: CUDA support for 5-10× faster processing
  - **Smart Pipeline**: AudioSR before upmixing, DeepFilterNet for enhancement
- **CodeFormer Face Restoration**:
  - Alternative to GFPGAN with ⭐⭐⭐⭐⭐ best-in-class quality
  - Adjustable fidelity weight (0.5-0.9) for quality/realism balance
  - Automatic model download and graceful fallback
  - CLI: `--face-model codeformer --face-fidelity 0.7`
- **Notification System**:
  - Webhook notifications (Discord, Slack, custom endpoints)
  - Email notifications via SMTP
  - Job completion and error alerts
  - Configurable via YAML with retry logic
- **Complete Documentation**:
  - 7 new quick-start guides (VHS, YouTube, Audio)
  - AudioSR integration guide (600+ lines)
  - CodeFormer integration guide (300+ lines)
  - 50+ new unit tests for reliability

### What's New in v1.4.x

- **Watch Folder Automation** (v1.4.5):
  - Monitor directories for new video files and auto-process them
  - Multi-folder support with individual presets per folder
  - Smart debouncing and lock file protection
  - Automatic retry logic for failed processing
  - YAML configuration with comprehensive options
  - See [Watch Folder Documentation](docs/WATCH_FOLDER.md)
- **Intelligent Video Analysis** (v1.4.3):
  - Auto-detect video characteristics (scan type, noise level, source format, content type)
  - Recommend optimal presets and settings based on analysis
  - Analyze-only mode to preview without processing
  - Save/load analysis configurations for batch workflows
  - Detect VHS artifacts (tracking errors, color bleeding, jitter)
- **Smart Advanced Options** (v1.4.0):
  - Conditional menus that show only relevant options based on your tool selection
  - Real-ESRGAN options appear only when Real-ESRGAN engine is selected
  - HDR options appear only when HDR mode is enabled
  - Audio/Surround options appear only when enhancement is enabled
  - Demucs AI options appear only when Demucs upmix is selected
- **Beginner-Friendly Tooltips** (v1.4.1):
  - Plain-English explanations for all options
  - No jargon - every setting explained in simple terms
  - Examples like "lanczos=sharpest (recommended), bicubic=smoother"
- **Content-Based Guidance** (v1.4.2):
  - "When to Use Each Option" help panel in the sidebar
  - Every tooltip includes USE/SKIP recommendations based on content type
  - Guidance for VHS, DVD, anime, clean sources, and more
  - Examples: "USE 0.7-1.0 for VHS (heavy noise), 0.3-0.5 for DVD"

### What's New in v1.3.0

- **Audio Enhancement** (all FREE, no GPU required):
  - Noise reduction, EQ, compression presets
  - Voice mode optimized for VHS dialogue
  - Music mode preserves dynamics
  - Loudness normalization (EBU R128)
- **Surround Sound Upmix**:
  - Stereo → 5.1 or 7.1 surround
  - Multiple algorithms: simple, surround, Pro Logic II
  - **Demucs AI** stem separation for best quality upmix
- **Audio Output Formats**: AAC, AC3, EAC3, DTS, FLAC

### What's New in v1.2.0

- **Multiple Upscale Engines**:
  - **NVIDIA Maxine** - Best quality for RTX GPUs
  - **Real-ESRGAN** - Works on AMD, Intel, and NVIDIA GPUs via Vulkan
  - **FFmpeg** - CPU-only fallback for any system
- **HDR Output**: Convert SDR videos to HDR10 or HLG format
- **Auto Engine Detection**: Automatically selects best available engine
- **Real-ESRGAN Models**: Choose from multiple AI models for different content types

### What's New in v1.1.0

- **File Upload**: Drag-and-drop video files directly into the GUI
- **Video Preview**: See metadata before processing (resolution, duration, fps, size)
- **Dark Mode**: Toggle dark theme in Settings
- **Stats Dashboard**: Track pending/completed/failed jobs with totals
- **Improved UI**: Better CSS styling with animations
- **90+ Unit Tests**: Comprehensive test coverage

---

## 🖥️ Web GUI

The modern Gradio web interface provides:

| Tab | Function |
|-----|----------|
| 📹 **Single Video** | Upload file or enter URL with full options + smart advanced menus |
| 📚 **Batch Processing** | Add multiple URLs at once |
| 📋 **Queue** | Monitor progress with stats dashboard |
| 📜 **Logs** | Real-time activity logging |
| ⚙️ **Settings** | Output directory, dark mode toggle |
| ℹ️ **About** | System info and alternatives |

**New in v1.4:** Conditional advanced options appear based on your selections - no clutter from irrelevant settings. Each option includes beginner-friendly explanations and "when to use" guidance based on your content type (VHS, DVD, anime, etc.).

```
┌─────────────────────────────────────────────────────────────┐
│  🎬 VHS Video Upscaler                           v1.4.2     │
│  AI-Powered Video Enhancement with NVIDIA Maxine            │
├─────────────────────────────────────────────────────────────┤
│  📹 Single │ 📚 Batch │ 📋 Queue │ 📜 Logs │ ⚙️ Settings    │
├─────────────────────────────────────────────────────────────┤
│  ┌─ Upload File ──────────┐ ┌─ URL / Path ─────────────┐   │
│  │  [Drag & Drop Video]   │ │ [youtube.com/watch?v=...]│   │
│  │  Resolution: 1920x1080 │ └───────────────────────────┘   │
│  │  Duration: 0:05:30     │                                 │
│  │  Codec: h264 @ 30fps   │  Preset: [vhs ▼]               │
│  └────────────────────────┘  Engine: [realesrgan ▼]        │
│                              Resolution: [1080p ▼]         │
│  ┌─ Real-ESRGAN Options ─┐  ┌─ When to Use ───────────┐   │
│  │  Model: [x4plus ▼]    │  │ VHS → Real-ESRGAN       │   │
│  │  Denoise: [0.7]       │  │ DVD → Maxine/FFmpeg     │   │
│  └───────────────────────┘  │ Anime → anime model     │   │
│                              └─────────────────────────┘   │
│  [➕ Add to Queue]                                          │
│                                                             │
│  ┌─ Stats ──────────────────────────────────────────────┐  │
│  │ Pending: 2 │ Processing: 1 │ Completed: 5 │ Failed: 0│  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Processing Pipeline

See how your video flows through each enhancement stage:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   INPUT      │     │  PREPROCESS  │     │  AI UPSCALE  │     │   ENCODE     │
│              │────▶│              │────▶│              │────▶│              │
│ VHS/DVD/MP4  │     │ Deinterlace  │     │ Maxine/ESRGAN│     │ HEVC/H.264   │
│ YouTube URL  │     │ Denoise      │     │ or FFmpeg    │     │ HDR (opt.)   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                      │
┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│   OUTPUT     │     │ AUDIO ENCODE │     │ AUDIO PROC   │◀───────────┘
│              │◀────│              │◀────│              │
│ Final Video  │     │ AAC/AC3/FLAC │     │ Enhance/Upmix│
│ Ready to Use │     │ 5.1/7.1 Mix  │     │ Demucs AI    │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Analysis Workflow

See how intelligent analysis guides your processing decisions:

```
┌─────────────────────────────────────────────────────────────────┐
│                     ANALYSIS WORKFLOW                           │
└─────────────────────────────────────────────────────────────────┘

       ┌──────────────┐
       │ Input Video  │
       └──────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │  --analyze-only │  ◀── Inspect characteristics
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │   Analysis Report                   │
    │ ----------------------------------- │
    │ • Scan type: interlaced_tff         │
    │ • Source: VHS                       │
    │ • Noise level: HIGH                 │
    │ • Quality score: 45/100             │
    │ • Artifacts: color bleeding, jitter │
    │                                     │
    │ Recommended: vhs_heavy preset       │
    │ Settings: denoise=0.8, deinterlace  │
    └────────┬────────────────────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
┌──────────┐   ┌─────────────┐
│ --auto-  │   │ Manual      │
│ detect   │   │ Settings    │
└────┬─────┘   └──────┬──────┘
     │                │
     └────────┬───────┘
              ▼
       ┌──────────────┐
       │  Processing  │
       │  (optimized) │
       └──────┬───────┘
              ▼
       ┌──────────────┐
       │ Best Quality │
       │   Output     │
       └──────────────┘
```

---

## 📖 Usage

### CLI Subcommand Structure

TerminalAI v1.4+ uses a modern subcommand architecture for better organization:

```bash
vhs-upscale <subcommand> [options]
```

**Available Subcommands:**

| Subcommand | Purpose | Example |
|------------|---------|---------|
| `upscale` | Process a single video | `vhs-upscale upscale video.mp4 -o output.mp4` |
| `analyze` | Analyze video characteristics | `vhs-upscale analyze video.mp4` |
| `preview` | Generate preview clip | `vhs-upscale preview video.mp4 -o preview.mp4` |
| `batch` | Process multiple videos | `vhs-upscale batch input_folder/ output_folder/` |
| `test-presets` | Compare multiple presets | `vhs-upscale test-presets video.mp4 -o tests/` |

**Legacy Syntax (Still Supported):**
```bash
# Old syntax with -i/--input flag still works
vhs-upscale -i video.mp4 -o output.mp4 -p vhs
```

### Recommended Workflow

For best results, analyze your video first to get optimal settings:

```bash
# Step 1: Analyze your video
vhs-upscale analyze video.mp4

# Step 2: Process with auto-detected settings
vhs-upscale upscale video.mp4 -o output.mp4 --auto-detect

# Alternative: One-step with auto-detect
vhs-upscale upscale video.mp4 -o output.mp4 --auto-detect
```

This ensures the right preset and settings for your specific video.

### GUI Mode (Recommended)

```bash
python -m vhs_upscaler.gui
```

### Command Line Examples

**Basic Upscaling:**
```bash
# Upscale VHS tape to 1080p
vhs-upscale upscale video.mp4 -o upscaled.mp4 --preset vhs

# Upscale to 4K
vhs-upscale upscale video.mp4 -o upscaled_4k.mp4 -r 2160

# Use Real-ESRGAN (no NVIDIA required)
vhs-upscale upscale video.mp4 -o out.mp4 --engine realesrgan

# Output as HDR10
vhs-upscale upscale video.mp4 -o out_hdr.mp4 --hdr hdr10

# CPU-only mode (no GPU required)
vhs-upscale upscale video.mp4 -o out.mp4 --engine ffmpeg --encoder libx265
```

**Video Analysis:**
```bash
# Analyze video characteristics
vhs-upscale analyze video.mp4

# Get recommendations with detailed report
vhs-upscale analyze video.mp4 --recommend

# Save analysis for later use
vhs-upscale analyze video.mp4 --save analysis.json

# Process using saved analysis
vhs-upscale upscale video.mp4 -o output.mp4 --analysis-config analysis.json
```

**Preview Generation:**
```bash
# Generate 10-second preview clip
vhs-upscale preview video.mp4 -o preview.mp4

# Preview from specific timestamp
vhs-upscale preview video.mp4 -o preview.mp4 --start 120

# Longer preview (30 seconds)
vhs-upscale preview video.mp4 -o preview.mp4 --duration 30
```

**Batch Processing:**
```bash
# Process all videos in a folder
vhs-upscale batch ./input_videos/ ./output_videos/

# Process with specific preset and resolution
vhs-upscale batch ./vhs_tapes/ ./restored/ -p vhs -r 2160

# Process only AVI files
vhs-upscale batch ./input/ ./output/ --pattern "*.avi"

# Parallel processing (4 videos at once)
vhs-upscale batch ./input/ ./output/ --parallel 4

# Resume interrupted batch
vhs-upscale batch ./input/ ./output/ --resume
```

**Watch Folder Automation:**
```bash
# Monitor folder and auto-process new videos
python scripts/watch_folder.py --config watch_config.yaml

# Verbose mode with logging
python scripts/watch_folder.py --verbose --log-file watch.log

# Example: Auto-process YouTube downloads
# 1. Download videos to watched folder
yt-dlp --output "input/youtube/%(title)s.%(ext)s" "https://youtube.com/playlist?list=..."

# 2. Watch folder config automatically processes them
# See docs/WATCH_FOLDER.md for configuration details
```

**Preset Testing:**
```bash
# Test all presets on a clip
vhs-upscale test-presets video.mp4 -o test_results/

# Test specific presets
vhs-upscale test-presets video.mp4 -o test_results/ --presets vhs,dvd,clean

# Create comparison grid
vhs-upscale test-presets video.mp4 -o test_results/ --create-grid

# Multi-clip comprehensive comparison
vhs-upscale test-presets video.mp4 -o test_results/ --multi-clip --clip-count 5
```

### Real-World Examples

**Example 1: Old Family VHS Tape (NEW: v1.5.0 Features)**
```bash
# Best settings for grainy VHS home videos with dialogue - using all new AI features
python -m vhs_upscaler.vhs_upscale \
  -i "family_christmas_1995.mp4" \
  -o "family_christmas_1995_restored.mp4" \
  --preset vhs \
  --engine realesrgan \
  --realesrgan-denoise 0.8 \
  --face-restore --face-model codeformer --face-fidelity 0.7 \
  --audio-enhance deepfilternet \
  --audio-sr --audiosr-model speech \
  -r 1080
```
*Result: AI face restoration, DeepFilterNet audio denoising, AudioSR upsampling to 48kHz, upscales to 1080p*

**Example 2: DVD Movie Backup**
```bash
# Clean up a DVD rip for home theater with surround sound
python -m vhs_upscaler.vhs_upscale \
  -i "movie_dvd_rip.mkv" \
  -o "movie_hd.mkv" \
  --preset dvd \
  --engine maxine \
  --audio-upmix demucs \
  --audio-layout 5.1 \
  --audio-format eac3 \
  -r 1080
```
*Result: Upscales to HD, creates AI-powered 5.1 surround from stereo*

**Example 3: Anime Collection**
```bash
# Upscale old anime with appropriate model
python -m vhs_upscaler.vhs_upscale \
  -i "anime_episode.mp4" \
  -o "anime_episode_4k.mp4" \
  --preset clean \
  --engine realesrgan \
  --realesrgan-model realesrgan-x4plus-anime \
  -r 2160
```
*Result: 4K upscale optimized for animated content*

**Example 4: YouTube Archive for HDR TV**
```bash
# Download and enhance for HDR playback
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=example" \
  -o "video_hdr.mp4" \
  --preset youtube \
  --hdr hdr10 \
  --hdr-brightness 600 \
  -r 2160
```
*Result: Downloads, upscales to 4K HDR10 for modern TVs*

**Example 5: No GPU / Laptop Processing**
```bash
# Process on any computer without GPU
python -m vhs_upscaler.vhs_upscale \
  -i "video.mp4" \
  -o "video_upscaled.mp4" \
  --preset vhs \
  --engine ffmpeg \
  --encoder libx265 \
  -r 720
```
*Result: CPU-only processing, works on any system*

### Deinterlacing Options

TerminalAI supports 4 deinterlacing algorithms optimized for different scenarios:

| Algorithm | Speed | Quality | Best For | Requires |
|-----------|-------|---------|----------|----------|
| **YADIF** | ⚡⚡⚡ Fast | ⭐⭐⭐ Good | VHS, general use | FFmpeg (built-in) |
| **BWDIF** | ⚡⚡ Medium | ⭐⭐⭐⭐ Better | Fast motion, sports | FFmpeg (built-in) |
| **W3FDIF** | ⚡⚡ Medium | ⭐⭐⭐⭐ Better | Detail preservation | FFmpeg (built-in) |
| **QTGMC** | ⚡ Slow | ⭐⭐⭐⭐⭐ Best | Archival quality | VapourSynth + plugins |

**When to Use Each:**

- **YADIF (Yet Another DeInterlacing Filter)**: Default choice for most VHS/DVD content. Fast, efficient, good quality.
  ```bash
  vhs-upscale upscale video.mp4 -o output.mp4 --deinterlace-algorithm yadif
  ```

- **BWDIF (Bob Weaver DeInterlacing Filter)**: Better motion compensation than YADIF. Use for sports, action scenes, or content with fast camera movement.
  ```bash
  vhs-upscale upscale video.mp4 -o output.mp4 --deinterlace-algorithm bwdif
  ```

- **W3FDIF (Weston 3 Field DeInterlacing Filter)**: Better edge/detail preservation. Use for static scenes with fine details like text or architecture.
  ```bash
  vhs-upscale upscale video.mp4 -o output.mp4 --deinterlace-algorithm w3fdif
  ```

- **QTGMC (Quality Time based deinterlacing using Motion Compensation)**: Highest quality, slowest processing. Use for archival preservation or when quality is paramount. Requires VapourSynth installation.
  ```bash
  # QTGMC with different quality presets
  vhs-upscale upscale video.mp4 -o output.mp4 --deinterlace-algorithm qtgmc --qtgmc-preset medium
  vhs-upscale upscale video.mp4 -o output.mp4 --deinterlace-algorithm qtgmc --qtgmc-preset slow
  vhs-upscale upscale video.mp4 -o output.mp4 --deinterlace-algorithm qtgmc --qtgmc-preset very_slow
  ```

**Performance vs Quality Trade-offs:**

```
Processing Time          Quality                   Use Case
─────────────────────────────────────────────────────────────────
YADIF:     ████░░░░░░    ███████░░░░     Everyday VHS restoration
BWDIF:     ██████░░░░    ████████░░░     Sports, fast motion
W3FDIF:    ██████░░░░    ████████░░░     Detail-heavy content
QTGMC:     ██████████    ██████████      Archival, best quality

█ = Time/Quality units (more = longer/better)
```

**Auto-Detection:**
The `analyze` subcommand automatically detects interlacing and recommends the appropriate algorithm:
```bash
vhs-upscale analyze video.mp4 --recommend
```

### Dry-Run Mode

Validate your processing pipeline before executing with `--dry-run`:

```bash
# Preview what will be processed without actually processing
vhs-upscale upscale video.mp4 -o output.mp4 --dry-run

# Dry-run batch processing
vhs-upscale batch ./input/ ./output/ --dry-run

# Test preset configuration
vhs-upscale upscale video.mp4 -o output.mp4 -p vhs --dry-run
```

**What Dry-Run Shows:**
- Complete processing pipeline visualization
- All filters that will be applied
- Input/output configuration
- Estimated file sizes
- Any configuration warnings or errors

**Example Output:**
```
DRY RUN MODE - No processing will occur
═══════════════════════════════════════════════════════════════

Input:  video.mp4 (720x480, 29.97fps, 500MB)
Output: output.mp4 (1920x1080, HEVC)

Processing Pipeline:
  1. Deinterlace (YADIF)
  2. Denoise (hqdn3d=3:2:3:2)
  3. AI Upscale (Real-ESRGAN x4plus)
  4. Encode (hevc_nvenc, CRF 20)
  5. Audio (enhance: voice, layout: stereo)

Estimated output size: ~1.2GB
Estimated processing time: 15-20 minutes

Pipeline validation: OK
```

### Parallel Batch Processing

Process multiple videos simultaneously to maximize hardware utilization:

```bash
# Process 4 videos in parallel
vhs-upscale batch ./input/ ./output/ --parallel 4

# Maximum parallelism (use all CPU cores)
vhs-upscale batch ./input/ ./output/ --parallel 8
```

**Performance Benefits:**

| Parallel Workers | Time for 10 Videos | GPU Usage | CPU Usage |
|------------------|-------------------|-----------|-----------|
| 1 (sequential) | 100 minutes | 50-70% | 20-30% |
| 2 workers | 55 minutes | 80-95% | 40-50% |
| 4 workers | 30 minutes | 95-100% | 70-80% |
| 8 workers | 25 minutes* | 100% | 90-100% |

*Diminishing returns beyond 4 workers on most systems

**Resource Considerations:**

```bash
# Check your system resources before parallel processing
# GPU: nvidia-smi (NVIDIA) or check Task Manager
# RAM: Multiply video count × ~4GB per process

# Safe default for most systems (2 workers)
vhs-upscale batch ./input/ ./output/ --parallel 2

# High-end workstation (RTX 4090, 64GB RAM)
vhs-upscale batch ./input/ ./output/ --parallel 6

# Server/render farm
vhs-upscale batch ./input/ ./output/ --parallel 12
```

**Best Practices:**
- **GPU-bound tasks** (AI upscaling): Limit to 2-4 workers
- **CPU-bound tasks** (FFmpeg encoding): Match CPU core count
- **RAM**: Ensure 4-8GB free per worker
- **Storage**: Use SSD for temporary files when processing multiple 4K videos

### LUT Color Grading

Apply professional color grading using 3D LUT files (.cube, .3dl):

**Basic LUT Application:**
```bash
# Apply LUT at full strength
vhs-upscale upscale video.mp4 -o output.mp4 --lut colorgrade.cube

# Apply LUT with 50% strength (subtle)
vhs-upscale upscale video.mp4 -o output.mp4 --lut colorgrade.cube --lut-strength 0.5

# Apply LUT with 25% strength (very subtle)
vhs-upscale upscale video.mp4 -o output.mp4 --lut colorgrade.cube --lut-strength 0.25
```

**Supported Formats:**
- `.cube` - Cube LUT (most common, Premiere/DaVinci Resolve standard)
- `.3dl` - 3D LUT (legacy format)

**Using LUTs with Presets:**
```bash
# VHS restoration with cinematic LUT
vhs-upscale upscale vhs_video.mp4 -o output.mp4 -p vhs --lut cinematic.cube

# DVD upscale with color correction LUT
vhs-upscale upscale dvd_rip.mp4 -o output.mp4 -p dvd --lut color_fix.cube --lut-strength 0.7
```

**Common LUT Use Cases:**

| Use Case | LUT Type | Strength | Example |
|----------|----------|----------|---------|
| Film emulation | Cinematic LUT | 0.8-1.0 | Kodak, Fuji film stocks |
| Color correction | Technical LUT | 1.0 | Fix color casts, white balance |
| Creative grading | Look LUT | 0.5-0.8 | Teal & orange, vintage |
| Broadcast compliance | Conversion LUT | 1.0 | Rec.709, Rec.2020 |

**Where to Find LUTs:**
- Free: [RocketStock Free LUTs](https://www.rocketstock.com/free-after-effects-templates/35-free-luts-for-color-grading-videos/)
- Professional: [LUTs.io](https://luts.io/), [Color Grading Central](https://colorgradingcentral.com/)
- Create your own: DaVinci Resolve, Adobe SpeedGrade

**Example Workflow:**
```bash
# Test different LUTs with test-presets
vhs-upscale test-presets video.mp4 -o lut_tests/ --lut film_look.cube --create-grid

# Process full video with chosen LUT
vhs-upscale upscale video.mp4 -o final.mp4 -p vhs --lut film_look.cube --lut-strength 0.8
```

### Face Restoration (GFPGAN)

AI-powered face restoration for VHS home videos and old footage with people:

**Basic Face Restoration:**
```bash
# Enable face restoration with default settings
vhs-upscale upscale video.mp4 -o output.mp4 --face-restore

# Adjust restoration strength
vhs-upscale upscale video.mp4 -o output.mp4 --face-restore --face-restore-strength 0.7

# Higher upscale factor for face regions
vhs-upscale upscale video.mp4 -o output.mp4 --face-restore --face-restore-upscale 4
```

**When to Use Face Restoration:**

✅ **USE for:**
- VHS home videos with family/friends
- Old interview footage
- Wedding/event videos with people
- Low-quality webcam recordings with faces
- Vintage TV shows/movies with close-ups

❌ **SKIP for:**
- Landscape/nature videos (no faces)
- Sports with distant figures
- Animated content
- Already-HD content
- Videos where faces are very small in frame

**Settings and Strength:**

| Strength | Effect | Best For |
|----------|--------|----------|
| 0.3 | Subtle enhancement | Already decent quality |
| 0.5 | Balanced (default) | General VHS restoration |
| 0.7 | Strong enhancement | Heavy degradation |
| 1.0 | Maximum | Severely damaged footage |

**Upscale Factor:**

```bash
# 1x = No upscaling (just face enhancement)
vhs-upscale upscale video.mp4 -o output.mp4 --face-restore --face-restore-upscale 1

# 2x = 2× upscale for face regions (default, balanced)
vhs-upscale upscale video.mp4 -o output.mp4 --face-restore --face-restore-upscale 2

# 4x = 4× upscale for face regions (maximum quality, slower)
vhs-upscale upscale video.mp4 -o output.mp4 --face-restore --face-restore-upscale 4
```

**Auto-Detection with Analysis:**
```bash
# Automatically enable face restoration if faces are detected
vhs-upscale upscale video.mp4 -o output.mp4 --auto-detect
```

The analyzer detects faces in sample frames and recommends face restoration if appropriate.

**Installation:**
Face restoration requires additional dependencies:
```bash
# Install GFPGAN and dependencies
pip install gfpgan basicsr opencv-python torch

# Download GFPGAN model (automatic on first use)
# Model is cached in ~/.cache/gfpgan/
```

**Example Workflow:**
```bash
# Test face restoration on a clip first
vhs-upscale preview video.mp4 -o test_face.mp4 --face-restore --face-restore-strength 0.5

# If satisfied, process full video
vhs-upscale upscale video.mp4 -o final.mp4 -p vhs --face-restore --face-restore-strength 0.5

# Combine with other enhancements
vhs-upscale upscale video.mp4 -o final.mp4 -p vhs \
  --face-restore --face-restore-strength 0.6 \
  --audio-enhance voice \
  --lut vintage.cube --lut-strength 0.3
```

**Performance Impact:**
- Processing time: +30-50% for videos with faces
- VRAM usage: +2-4GB
- Works best with NVIDIA GPU (CUDA support)
- CPU fallback available but significantly slower

### Video Analysis

Analyze videos to understand their characteristics and get optimal settings recommendations.

**Analyze a Video**
```bash
# Get detailed analysis report (new subcommand syntax)
vhs-upscale analyze video.mp4

# Legacy syntax
python -m vhs_upscaler.vhs_upscale -i video.mp4 --analyze-only
```

Output includes:
- Technical specs (resolution, framerate, codec, bitrate)
- Detected characteristics (scan type, noise level, source format)
- VHS artifacts detection (tracking errors, color bleeding, jitter)
- Recommended preset and settings
- Estimated processing time

**Auto-Detect Settings**
```bash
# Automatically apply recommended settings (new syntax)
vhs-upscale upscale video.mp4 -o output.mp4 --auto-detect

# Legacy syntax
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o output.mp4 --auto-detect
```

**Save Analysis for Later**
```bash
# Analyze once, use multiple times (new syntax)
vhs-upscale analyze video.mp4 --save video_analysis.json

# Process using saved analysis
vhs-upscale upscale video.mp4 -o output.mp4 --analysis-config video_analysis.json
```

**Batch Processing Workflow**
```bash
# Analyze all videos and save configs
for video in *.mp4; do
  vhs-upscale analyze "$video" --save "${video%.mp4}_analysis.json"
done

# Review analysis reports, then process overnight
for config in *_analysis.json; do
  video="${config%_analysis.json}.mp4"
  vhs-upscale upscale "$video" -o "upscaled_$video" --analysis-config "$config"
done
```

### CLI Options Reference

**Core Options:**

| Option | Description | Default | Available In |
|--------|-------------|---------|--------------|
| `-o, --output` | Output video file or folder | Required | upscale, preview, batch, test-presets |
| `-r, --resolution` | Target height (720/1080/1440/2160) | 1080 | All subcommands |
| `-p, --preset` | vhs/dvd/webcam/youtube/clean/auto | vhs | All subcommands |
| `-q, --quality` | Quality mode: 0=best, 1=fast | 0 | All subcommands |
| `--crf` | Constant Rate Factor (0-51, lower=better) | 20 | All subcommands |
| `--encoder` | hevc_nvenc/h264_nvenc/libx265/libx264 | hevc_nvenc | All subcommands |
| `-v, --verbose` | Enable verbose logging | Off | All subcommands |
| `--dry-run` | Show pipeline without executing | Off | upscale, batch |

**Upscale Engine Options:**

| Option | Description | Default | Values |
|--------|-------------|---------|--------|
| `--engine` | Upscaling engine selection | auto | auto, maxine, realesrgan, ffmpeg |
| `--realesrgan-model` | Real-ESRGAN AI model | realesrgan-x4plus | x4plus, x4plus-anime, animevideov3 |
| `--realesrgan-denoise` | Real-ESRGAN denoise strength | 0.5 | 0.0-1.0 |
| `--ffmpeg-scale-algo` | FFmpeg scaling algorithm | lanczos | lanczos, bicubic, bilinear, spline |

**Deinterlacing Options:**

| Option | Description | Default | Values |
|--------|-------------|---------|--------|
| `--deinterlace-algorithm` | Deinterlacing filter | yadif | yadif, bwdif, w3fdif, qtgmc |
| `--qtgmc-preset` | QTGMC quality preset (qtgmc only) | medium | draft, medium, slow, very_slow |

**Audio Processing Options:**

| Option | Description | Default | Values |
|--------|-------------|---------|--------|
| `--audio-enhance` | Audio enhancement mode | none | none, light, moderate, aggressive, voice, music |
| `--audio-upmix` | Surround upmix mode | none | none, simple, surround, prologic, demucs |
| `--audio-layout` | Output channel layout | original | original, stereo, 5.1, 7.1, mono |
| `--audio-format` | Output audio codec | aac | aac, ac3, eac3, dts, flac |
| `--audio-bitrate` | Audio bitrate | 192k | Any (use 640k for 5.1/7.1) |
| `--no-audio-normalize` | Disable loudness normalization | Off | Flag |
| `--audio-target-loudness` | Target LUFS for normalization | -14.0 | -24.0 to -9.0 |

**HDR and Color Options:**

| Option | Description | Default | Values |
|--------|-------------|---------|--------|
| `--hdr` | HDR output mode | sdr | sdr, hdr10, hlg |
| `--hdr-brightness` | Peak brightness in nits (HDR) | 400 | 100-10000 |
| `--color-depth` | Output color bit depth | 10 | 8, 10 |
| `--lut` | Apply 3D LUT file for color grading | None | Path to .cube/.3dl file |
| `--lut-strength` | LUT blend strength | 1.0 | 0.0-1.0 |

**Face Restoration Options:**

| Option | Description | Default | Values |
|--------|-------------|---------|--------|
| `--face-restore` | Enable GFPGAN face restoration | Off | Flag |
| `--face-restore-strength` | Face restoration intensity | 0.5 | 0.0-1.0 |
| `--face-restore-upscale` | Face upscale factor | 2 | 1, 2, 4 |

**Analysis Options:**

| Option | Description | Default | Values |
|--------|-------------|---------|--------|
| `--auto-detect` | Auto-detect optimal settings | Off | Flag |
| `--analysis-config` | Load pre-analyzed configuration | None | Path to JSON file |
| `--save-analysis` | Export analysis results | None | Path to JSON file |
| `--force-backend` | Force specific analyzer backend | Auto | python, bash, basic |

**Batch Options:**

| Option | Description | Default | Values |
|--------|-------------|---------|--------|
| `--parallel` | Number of parallel workers | 1 | 1-16 |
| `--pattern` | File pattern for discovery | * | Glob pattern (*.mp4, *.avi) |
| `--recursive` | Search subfolders recursively | Off | Flag |
| `--skip-existing` | Skip already processed videos | Off | Flag |
| `--resume` | Resume interrupted batch | Off | Flag |
| `--max-count` | Limit number of videos | None | Integer |

**Test Presets Options:**

| Option | Description | Default | Values |
|--------|-------------|---------|--------|
| `--presets` | Comma-separated preset list | All | vhs,dvd,webcam,clean,youtube |
| `--start` | Start time for test clip | 25% | Seconds (float) |
| `--duration` | Test clip duration | 10.0 | Seconds (float) |
| `--create-grid` | Create comparison grid | Off | Flag |
| `--grid-layout` | Grid arrangement | 2x2 | 2x2, 2x3, 3x2, 1x4, 4x1 |
| `--multi-clip` | Extract multiple clips | Off | Flag |
| `--clip-count` | Number of clips (multi-clip) | 3 | Integer |
| `--timestamps` | Custom clip timestamps | Auto | Comma-separated seconds |

**Advanced Demucs Options:**

| Option | Description | Default | Values |
|--------|-------------|---------|--------|
| `--demucs-model` | Demucs AI model | htdemucs | htdemucs, htdemucs_ft, mdx_extra |
| `--demucs-device` | Processing device | auto | auto, cuda, cpu |
| `--demucs-shifts` | Processing quality passes | 1 | 0-5 (higher=better/slower) |
| `--lfe-crossover` | LFE crossover frequency (Hz) | 120 | 60-200 |
| `--center-mix` | Center channel mix level | 0.707 | 0.0-1.0 |
| `--surround-delay` | Surround delay (ms) | 15 | 0-50 |

**System Options:**

| Option | Description | Default | Values |
|--------|-------------|---------|--------|
| `--config` | Configuration file path | config.yaml | Path to YAML file |
| `--keep-temp` | Keep temporary files | Off | Flag |
| `--gpu-id` | GPU device ID (multi-GPU) | 0 | Integer |

### Upscale Engines

| Engine | GPU Required | Quality | Speed | Best For |
|--------|--------------|---------|-------|----------|
| **maxine** | NVIDIA RTX | ⭐⭐⭐⭐⭐ | Fast | RTX users |
| **realesrgan** | AMD/Intel/NVIDIA | ⭐⭐⭐⭐ | Medium | Non-NVIDIA GPUs |
| **ffmpeg** | None (CPU) | ⭐⭐⭐ | Slow | Any system |

### Audio Enhancement

| Mode | Best For | Description |
|------|----------|-------------|
| **none** | Clean audio | No processing |
| **light** | General cleanup | Gentle highpass + compression |
| **moderate** | Noisy recordings | Noise reduction + EQ |
| **aggressive** | Very noisy | Heavy noise removal |
| **voice** | VHS dialogue | Optimized for speech |
| **music** | Music content | Preserves dynamics |

### Surround Upmix

| Mode | Description | Quality |
|------|-------------|---------|
| **none** | Keep original channels | N/A |
| **simple** | Basic channel mapping | ⭐⭐ |
| **surround** | FFmpeg surround filter | ⭐⭐⭐ |
| **prologic** | Dolby Pro Logic II decode | ⭐⭐⭐ |
| **demucs** | AI stem separation (requires `demucs` package) | ⭐⭐⭐⭐⭐ |

---

## ⚙️ Presets

| Preset | Source Type | Deinterlace | Denoise | Best For |
|--------|-------------|-------------|---------|----------|
| `vhs` | 480i VHS tapes | ✅ Yes | Strong | Old home videos |
| `dvd` | 480p/576p DVDs | ✅ Yes | Moderate | DVD rips |
| `webcam` | Low-quality webcam | ❌ No | Strong | Old webcam footage |
| `youtube` | YouTube downloads | ❌ No | Light | Downloaded videos |
| `clean` | Already clean | ❌ No | None | High-quality sources |

---

## 🔬 Preset Comparison with test-presets

The `test-presets` subcommand helps you choose the optimal preset for your content by generating side-by-side comparisons.

### Basic Preset Testing

```bash
# Test all presets on a representative clip
vhs-upscale test-presets video.mp4 -o test_results/

# This creates:
# - original.mp4 (source clip)
# - preset_vhs.mp4
# - preset_dvd.mp4
# - preset_webcam.mp4
# - preset_clean.mp4
# - preset_youtube.mp4
```

### Comparison Grid Generation

Create a visual grid to compare all presets at once:

```bash
# Generate 2x2 comparison grid
vhs-upscale test-presets video.mp4 -o test_results/ --create-grid

# Creates comparison_grid.mp4 with labeled side-by-side videos
```

**Grid Layout Options:**

| Layout | Videos | Best For |
|--------|--------|----------|
| `2x2` | 4 presets | Standard comparison |
| `2x3` | 6 presets | All presets + original |
| `1x4` | 4 presets | Horizontal comparison |
| `4x1` | 4 presets | Vertical comparison |

```bash
# Custom grid layout
vhs-upscale test-presets video.mp4 -o test_results/ --create-grid --grid-layout 2x3
```

### Multi-Clip Comprehensive Comparison

Test presets across multiple clips from different parts of the video for thorough evaluation:

```bash
# Extract and test 5 clips at different positions
vhs-upscale test-presets video.mp4 -o test_results/ --multi-clip --clip-count 5

# Creates:
# - clip_0001/ (beginning of video)
# - clip_0002/ (25% through)
# - clip_0003/ (50% through)
# - clip_0004/ (75% through)
# - clip_0005/ (end of video)
# Each folder contains all preset variations
```

**Custom Timestamps:**
```bash
# Test specific scenes you care about
vhs-upscale test-presets video.mp4 -o test_results/ \
  --multi-clip --timestamps "30,120,240,480"

# Tests at 30s, 2min, 4min, and 8min marks
```

### Test-Presets Workflow

**Step 1: Generate comparisons**
```bash
vhs-upscale test-presets family_vhs.mp4 -o vhs_tests/ --create-grid
```

**Step 2: Review outputs**
- Watch `comparison_grid.mp4` to see all presets side-by-side
- Check individual preset files for detail
- Read `comparison_report.txt` (multi-clip mode) for recommendations

**Step 3: Process with chosen preset**
```bash
# Based on comparison, use the best preset
vhs-upscale upscale family_vhs.mp4 -o final.mp4 -p vhs
```

### Preset Selection Guide

**After running test-presets, look for:**

| Observation | Recommended Preset | Reason |
|-------------|-------------------|--------|
| Strong interlacing artifacts | `vhs` or `dvd` | Deinterlacing enabled |
| Heavy noise/grain | `vhs` or `webcam` | Strong denoise |
| Moderate noise, film grain | `dvd` | Balanced denoise |
| Compression artifacts | `youtube` | Light processing |
| Already good quality | `clean` | Minimal processing |
| Can't decide | `auto` + `--auto-detect` | Let AI choose |

**Example Comparison Scenarios:**

```bash
# Scenario 1: Old family VHS tape
vhs-upscale test-presets family_1990.mp4 -o tests/ --presets vhs,dvd --create-grid
# Compare: VHS (strong denoise) vs DVD (moderate denoise)
# Likely winner: vhs

# Scenario 2: DVD backup
vhs-upscale test-presets movie_dvd.mp4 -o tests/ --presets dvd,clean --create-grid
# Compare: DVD (deinterlace) vs Clean (no processing)
# Likely winner: dvd if interlaced, clean if progressive

# Scenario 3: YouTube download
vhs-upscale test-presets downloaded.mp4 -o tests/ --presets youtube,clean --create-grid
# Compare: YouTube (light denoise) vs Clean (none)
# Likely winner: depends on download quality

# Scenario 4: Not sure about source
vhs-upscale test-presets unknown.mp4 -o tests/ --create-grid --multi-clip
# Test all presets on multiple clips
# Review comparison_report.txt for AI recommendations
```

### Advanced Preset Testing

**Test with different resolutions:**
```bash
# Test 1080p vs 4K output
vhs-upscale test-presets video.mp4 -o tests_1080/ -r 1080 --create-grid
vhs-upscale test-presets video.mp4 -o tests_4k/ -r 2160 --create-grid
```

**Test with different engines:**
```bash
# Compare Real-ESRGAN models
vhs-upscale test-presets video.mp4 -o tests_x4plus/ --engine realesrgan --realesrgan-model realesrgan-x4plus
vhs-upscale test-presets video.mp4 -o tests_anime/ --engine realesrgan --realesrgan-model realesrgan-x4plus-anime
```

**Test with different deinterlacing:**
```bash
# Compare deinterlacing algorithms
vhs-upscale test-presets interlaced.mp4 -o tests_yadif/ -p vhs --deinterlace-algorithm yadif
vhs-upscale test-presets interlaced.mp4 -o tests_bwdif/ -p vhs --deinterlace-algorithm bwdif
vhs-upscale test-presets interlaced.mp4 -o tests_qtgmc/ -p vhs --deinterlace-algorithm qtgmc
```

---

## 🎯 Quick Decision Guide

**Not sure what settings to use?** Start with analysis:

```
                    ┌──────────────────────────┐
                    │   New to upscaling?      │
                    └──────────┬───────────────┘
                               │
                               ▼
                    ┌──────────────────────────┐
                    │  vhs-upscale analyze     │  ◀── Recommended for beginners
                    │  Get AI recommendations  │
                    └──────────┬───────────────┘
                               │
                               ▼
                    ┌──────────────────────────┐
                    │  What's your source?     │
                    └──────────┬───────────────┘
                               │
        ┌──────────────┬───────────┼───────────┬──────────────┐
        ▼              ▼           ▼           ▼              ▼
   ┌─────────┐   ┌─────────┐ ┌─────────┐ ┌─────────┐   ┌─────────┐
   │   VHS   │   │   DVD   │ │  Anime  │ │ YouTube │   │  Clean  │
   │  Tape   │   │  Rip    │ │ Cartoon │ │ Download│   │  HD/4K  │
   └────┬────┘   └────┬────┘ └────┬────┘ └────┬────┘   └────┬────┘
        │              │           │           │              │
        ▼              ▼           ▼           ▼              ▼
┌────────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│vhs-upscale     │ │vhs-upscale│ │vhs-upscale│ │vhs-upscale│ │vhs-upscale│
│upscale video   │ │upscale    │ │upscale    │ │upscale    │ │upscale    │
│-o out.mp4      │ │video      │ │video      │ │video      │ │video      │
│-p vhs          │ │-o out.mp4 │ │-o out.mp4 │ │-o out.mp4 │ │-o out.mp4 │
│--engine        │ │-p dvd     │ │-p clean   │ │-p youtube │ │-p clean   │
│ realesrgan     │ │--engine   │ │--engine   │ │--engine   │ │--engine   │
│--audio-enhance │ │ maxine    │ │realesrgan │ │ auto      │ │ maxine    │
│ voice          │ │           │ │--realesrgan│ │          │ │           │
│--face-restore  │ │--audio-   │ │ -model    │ │           │ │           │
└────────────────┘ │ upmix     │ │ anime     │ └──────────┘ └──────────┘
                   │ demucs    │ └──────────┘
                   │--audio-   │
                   │ layout 5.1│
                   └──────────┘
```

### Quick Reference Card

| Your Content | Preset | Engine | Audio | Resolution |
|--------------|--------|--------|-------|------------|
| VHS home videos | `vhs` | `realesrgan` | `voice` | 1080p |
| VHS music/concert | `vhs` | `realesrgan` | `music` | 1080p |
| DVD movie | `dvd` | `maxine` or `auto` | `demucs` + 5.1 | 1080p |
| Old anime | `clean` | `realesrgan` (anime model) | `none` | 2160p |
| YouTube download | `youtube` | `auto` | `none` | 1080p |
| Already HD/clean | `clean` | `maxine` | `none` | same or 2160p |
| No GPU available | any | `ffmpeg` | any | 720p-1080p |

### Expected Quality Improvements

```
Source Quality          After Processing         Improvement
─────────────────────────────────────────────────────────────
VHS (240-480i)    ──▶   1080p HD               ████████░░ 80%
├─ Noise/grain    ──▶   Clean, sharp           ████████░░ 80%
├─ Muffled audio  ──▶   Clear dialogue         ███████░░░ 70%
└─ Interlacing    ──▶   Smooth motion          █████████░ 90%

DVD (480p)        ──▶   1080p/4K               ███████░░░ 70%
├─ Compression    ──▶   Reduced artifacts      ██████░░░░ 60%
└─ Stereo audio   ──▶   5.1 Surround           ████████░░ 80%

YouTube (720p)    ──▶   1080p/4K               █████░░░░░ 50%
└─ Already OK     ──▶   Slightly sharper       ████░░░░░░ 40%

Clean HD          ──▶   4K                     ███░░░░░░░ 30%
└─ Upscale only   ──▶   Larger resolution      ███░░░░░░░ 30%
```

*Higher bars = more noticeable improvement. VHS benefits most from processing.*

---

## 💻 Requirements

### Hardware

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **GPU** | None required* | RTX 3080+ |
| **VRAM** | 2GB (Real-ESRGAN) | 12GB+ for 4K |
| **RAM** | 8GB | 16GB+ |
| **Storage** | 10GB free | SSD recommended |

*GPU is optional - FFmpeg engine works on CPU only

### Software

- **Python** 3.10+
- **FFmpeg** (required)

### Optional (for better quality/speed)

- **NVIDIA Driver** 535+ (for NVENC encoder)
- **NVIDIA Maxine SDK** (for best AI upscaling on RTX)
- **Real-ESRGAN ncnn-vulkan** (for AI upscaling on AMD/Intel/NVIDIA)
  - Download: [github.com/xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN/releases)

### Python Dependencies

```
# Core dependencies (required)
yt-dlp>=2023.0.0    # YouTube downloading
pyyaml>=6.0         # Configuration
gradio>=4.0.0       # Web interface

# Optional AI audio features (v1.5.0+)
deepfilternet>=0.5.0  # AI audio denoising
audiosr>=0.0.4        # AI audio upsampling

# Optional face restoration alternatives (v1.5.0+)
codeformer            # Enhanced face restoration

# Optional automation features
watchdog>=3.0.0       # Watch folder automation
requests              # Webhook notifications
```

---

## 📦 Project Structure

```
terminalai/
├── vhs_upscaler/           # Main package
│   ├── gui.py              # Gradio web interface
│   ├── vhs_upscale.py      # Processing pipeline
│   ├── queue_manager.py    # Batch queue system
│   ├── logger.py           # Logging system
│   └── config.yaml         # Configuration
├── tests/                  # Test suite (90+ tests)
│   ├── test_gui_helpers.py
│   ├── test_gui_integration.py
│   └── test_queue_manager.py
├── download_youtube.py     # Standalone downloader
├── install.sh              # Linux/Mac installer
├── install.ps1             # Windows installer
├── requirements.txt        # Dependencies
├── pyproject.toml          # Package config
└── README.md
```

---

## 🧪 Testing

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=vhs_upscaler
```

**Test Coverage:** 90+ tests covering GUI helpers, queue management, and integration.

---

## 🔧 Configuration

Edit `vhs_upscaler/config.yaml`:

```yaml
# NVIDIA Maxine SDK path (auto-detected if MAXINE_HOME is set)
maxine_path: "C:/path/to/maxine/bin"

defaults:
  resolution: 1080
  encoder: "hevc_nvenc"
  crf: 20
  quality_mode: 0  # 0=best, 1=fast
```

---

## 🔧 Troubleshooting

### Common Errors and Solutions

<details>
<summary><b>❌ "FFmpeg not found" or "ffmpeg: command not found"</b></summary>

**What happened:** FFmpeg is not installed or not in your system PATH.

**Why it matters:** FFmpeg is required for all video processing operations.

**Solutions:**

```bash
# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install ffmpeg

# Linux (Fedora)
sudo dnf install ffmpeg

# macOS
brew install ffmpeg

# Windows (with winget)
winget install FFmpeg

# Windows (with chocolatey)
choco install ffmpeg
```

**Verify installation:**
```bash
ffmpeg -version
# Should show: ffmpeg version 5.x or higher
```

</details>

<details>
<summary><b>❌ "CUDA out of memory" or "RuntimeError: CUDA error"</b></summary>

**What happened:** Your GPU doesn't have enough VRAM for the selected operation.

**Why it matters:** AI upscaling (especially 4K) requires significant GPU memory.

**Solutions:**

| Resolution | Minimum VRAM | Recommended |
|------------|--------------|-------------|
| 720p | 2GB | 4GB |
| 1080p | 4GB | 6GB |
| 1440p | 6GB | 8GB |
| 2160p (4K) | 8GB | 12GB+ |

```bash
# Option 1: Use lower resolution
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 -r 1080  # Instead of 2160

# Option 2: Use CPU-based processing (slower but works)
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 --engine ffmpeg

# Option 3: Close other GPU applications
# Close browsers, games, other video editors before processing
```

**Check your VRAM:**
```bash
# NVIDIA
nvidia-smi

# Look for "Memory-Usage" - if close to max, reduce resolution
```

</details>

<details>
<summary><b>❌ "No NVIDIA GPU detected" or "hevc_nvenc encoder not found"</b></summary>

**What happened:** NVIDIA hardware encoding requires an NVIDIA GPU with NVENC support.

**Why it matters:** hevc_nvenc and h264_nvenc are GPU-accelerated encoders that only work on NVIDIA cards.

**Solutions:**

```bash
# Option 1: Use CPU encoding instead (works on any system)
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 --encoder libx265

# Option 2: Use libx264 for better compatibility
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 --encoder libx264
```

**Encoder comparison:**
| Encoder | GPU Required | Speed | Quality | Compatibility |
|---------|--------------|-------|---------|---------------|
| hevc_nvenc | NVIDIA | ⚡ Fast | ⭐⭐⭐⭐ | Modern devices |
| h264_nvenc | NVIDIA | ⚡ Fast | ⭐⭐⭐ | Most devices |
| libx265 | None (CPU) | 🐢 Slow | ⭐⭐⭐⭐⭐ | Modern devices |
| libx264 | None (CPU) | 🐢 Medium | ⭐⭐⭐⭐ | Everything |

</details>

<details>
<summary><b>❌ "Real-ESRGAN not found" or "realesrgan-ncnn-vulkan: command not found"</b></summary>

**What happened:** Real-ESRGAN executable is not installed or not in PATH.

**Why it matters:** Real-ESRGAN provides high-quality AI upscaling for AMD/Intel/NVIDIA GPUs.

**Solutions:**

1. **Download Real-ESRGAN:**
   - Go to: https://github.com/xinntao/Real-ESRGAN/releases
   - Download the version for your OS (e.g., `realesrgan-ncnn-vulkan-v0.2.0-windows.zip`)
   - Extract to a folder (e.g., `C:\Tools\realesrgan` or `/opt/realesrgan`)

2. **Add to PATH:**
   ```bash
   # Linux/Mac - add to ~/.bashrc or ~/.zshrc
   export PATH="$PATH:/opt/realesrgan"

   # Windows - add via System Properties > Environment Variables
   # Or use PowerShell:
   $env:PATH += ";C:\Tools\realesrgan"
   ```

3. **Or use alternative engines:**
   ```bash
   # Use NVIDIA Maxine (if you have RTX GPU)
   python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 --engine maxine

   # Use FFmpeg (works everywhere, no GPU needed)
   python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 --engine ffmpeg
   ```

</details>

<details>
<summary><b>❌ "YouTube download failed" or "yt-dlp: ERROR"</b></summary>

**What happened:** YouTube blocks or changes their API frequently, breaking downloaders.

**Why it matters:** yt-dlp needs regular updates to keep working with YouTube.

**Solutions:**

```bash
# Update yt-dlp to latest version
pip install --upgrade yt-dlp

# If still failing, try with cookies (for age-restricted content)
python -m vhs_upscaler.vhs_upscale -i "https://youtube.com/watch?v=VIDEO_ID" -o out.mp4

# Common error: "Video unavailable"
# → Video may be private, deleted, or region-locked
# → Try a VPN or different video

# Common error: "Sign in to confirm your age"
# → Export cookies from your browser:
# → Use browser extension "Get cookies.txt"
# → Place cookies.txt in working directory
```

**Rate limiting:** If you get "HTTP Error 429", wait 10-15 minutes before retrying.

</details>

<details>
<summary><b>❌ "Demucs failed" or "torch not found"</b></summary>

**What happened:** Demucs AI audio separation requires PyTorch and the demucs package.

**Why it matters:** Demucs provides the best quality stereo-to-surround conversion.

**Solutions:**

```bash
# Install demucs and dependencies
pip install demucs torch torchaudio

# If CUDA errors, install CPU-only PyTorch:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Or use simpler upmix methods (no extra dependencies):
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 --audio-upmix surround
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 --audio-upmix prologic
```

**Memory issues with Demucs:**
```bash
# Use CPU mode if GPU memory is limited
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 \
  --audio-upmix demucs --demucs-device cpu

# Reduce quality passes for faster processing
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 \
  --audio-upmix demucs --demucs-shifts 0
```

</details>

<details>
<summary><b>❌ "Permission denied" or "Access denied"</b></summary>

**What happened:** The program can't read/write files due to permission issues.

**Why it matters:** Processing requires read access to input and write access to output location.

**Solutions:**

```bash
# Linux/Mac - check file permissions
ls -la video.mp4
# If you don't own the file:
sudo chown $USER video.mp4

# Check output directory is writable
ls -la /path/to/output/
# Create directory if needed:
mkdir -p /path/to/output

# Windows - run as administrator if needed
# Or change output to a user-writable location:
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o ~/Videos/output.mp4
```

**Common Windows issue:** Output path in Program Files or System folders.
→ Use Documents, Videos, or Desktop instead.

</details>

<details>
<summary><b>❌ "Output file is 0 bytes" or "Encoding failed"</b></summary>

**What happened:** The encoding process failed silently or was interrupted.

**Why it matters:** Incomplete processing results in corrupted or empty output files.

**Solutions:**

```bash
# Enable verbose logging to see what went wrong
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 -v

# Check logs in the logs/ directory
cat logs/vhs_upscaler_*.log

# Common causes:
# 1. Disk full - check available space
df -h  # Linux/Mac
# 2. Corrupted input file - try playing in VLC first
# 3. Unsupported codec - convert input first:
ffmpeg -i input.mkv -c:v libx264 -c:a aac temp.mp4
```

**If encoding keeps failing:**
```bash
# Try different encoder
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 --encoder libx264

# Try lower quality (uses less memory)
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 --crf 28

# Try lower resolution
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 -r 720
```

</details>

<details>
<summary><b>❌ GUI won't start or "Gradio error"</b></summary>

**What happened:** The web interface failed to initialize.

**Why it matters:** The GUI requires Gradio and a free network port.

**Solutions:**

```bash
# Update Gradio
pip install --upgrade gradio

# Check if port 7860 is in use
# Linux/Mac:
lsof -i :7860
# Windows:
netstat -ano | findstr 7860

# Use a different port
python -m vhs_upscaler.gui --port 7861

# If firewall blocking, try localhost only
python -m vhs_upscaler.gui --host 127.0.0.1
```

**Browser issues:**
- Clear browser cache and cookies
- Try incognito/private mode
- Try a different browser

</details>

### Diagnostic Commands

Run these commands to help diagnose issues:

```bash
# Check Python version (need 3.10+)
python --version

# Check FFmpeg
ffmpeg -version

# Check NVIDIA GPU and driver
nvidia-smi

# Check available disk space
df -h  # Linux/Mac
wmic logicaldisk get size,freespace,caption  # Windows

# Check installed packages
pip list | grep -E "(gradio|yt-dlp|torch|demucs)"

# Test basic video processing
ffmpeg -i input.mp4 -t 5 -c copy test_output.mp4

# Check GPU memory usage
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

### Getting Help

If you're still stuck:

1. **Check logs:** `logs/vhs_upscaler_*.log`
2. **Run with verbose:** Add `-v` flag to see detailed output
3. **Search issues:** https://github.com/parthalon025/terminalai/issues
4. **Create issue:** Include error message, OS, GPU, and steps to reproduce

---

## 🔄 Alternatives

| Project | Speed | Quality | Best For | Open Source |
|---------|-------|---------|----------|-------------|
| **TerminalAI** | ⚡ Fast | Good | VHS/DVD restoration | ✅ Yes |
| [Video2X](https://github.com/k4yt3x/video2x) | Medium | Excellent | Anime, Real-ESRGAN | ✅ Yes |
| [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) | Slow | Best | Maximum quality | ✅ Yes |
| [Topaz Video AI](https://www.topazlabs.com/) | Medium | Excellent | Easy to use | ❌ Commercial |

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Run tests (`pytest tests/`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing`)
6. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [NVIDIA Maxine Video Effects SDK](https://developer.nvidia.com/maxine)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg](https://ffmpeg.org/)
- [Gradio](https://gradio.app/)

---

<p align="center">
  Made with ❤️ by the TerminalAI community
</p>
