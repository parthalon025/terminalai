<p align="center">
  <h1 align="center">🎬 TerminalAI - Video Processing Suite</h1>
  <p align="center">
    <strong>AI-powered VHS video upscaling and YouTube downloading with NVIDIA RTX acceleration</strong>
  </p>
</p>

<p align="center">
  <a href="https://github.com/parthalon025/terminalai/releases"><img src="https://img.shields.io/badge/version-1.4.2-blue?style=flat-square" alt="Version 1.4.2"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"></a>
  <a href="https://developer.nvidia.com/maxine"><img src="https://img.shields.io/badge/NVIDIA-Maxine-76B900?style=flat-square&logo=nvidia&logoColor=white" alt="NVIDIA Maxine"></a>
  <a href="https://gradio.app/"><img src="https://img.shields.io/badge/Gradio-Web_GUI-orange?style=flat-square" alt="Gradio"></a>
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

### One-Line Install (Recommended)

```bash
# Clone and install in one command
git clone https://github.com/parthalon025/terminalai.git && cd terminalai && pip install -e .
```

### Or Step by Step

```bash
# 1. Clone the repository
git clone https://github.com/parthalon025/terminalai.git
cd terminalai

# 2. Install (choose one method)
pip install -e .              # Recommended: editable install
# OR
pip install -r requirements.txt  # Just dependencies
```

### Using Install Scripts

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh         # Standard install
./install.sh --dev   # With dev dependencies
```

**Windows (PowerShell):**
```powershell
# Allow script execution (run once)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

.\install.ps1        # Standard install
.\install.ps1 -Dev   # With dev dependencies
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
| 💻 **Works Without NVIDIA** | Real-ESRGAN supports AMD/Intel GPUs, FFmpeg for CPU-only |

### What's New in v1.4.x

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

---

## 📖 Usage

### GUI Mode (Recommended)

```bash
python -m vhs_upscaler.gui
```

### Command Line

```bash
# Download YouTube video
python download_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Upscale VHS tape to 1080p
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o upscaled.mp4 --preset vhs

# Upscale to 4K
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o upscaled_4k.mp4 -r 2160

# Watch folder mode (auto-process new files)
python -m vhs_upscaler.vhs_upscale --watch -i ./input -o ./output

# Use Real-ESRGAN (no NVIDIA required)
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 --engine realesrgan

# Output as HDR10
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out_hdr.mp4 --hdr hdr10

# CPU-only mode (no GPU required)
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 --engine ffmpeg --encoder libx265
```

### Real-World Examples

**Example 1: Old Family VHS Tape**
```bash
# Best settings for grainy VHS home videos with dialogue
python -m vhs_upscaler.vhs_upscale \
  -i "family_christmas_1995.mp4" \
  -o "family_christmas_1995_restored.mp4" \
  --preset vhs \
  --engine realesrgan \
  --realesrgan-denoise 0.8 \
  --audio-enhance voice \
  -r 1080
```
*Result: Removes VHS noise, enhances dialogue clarity, upscales to 1080p*

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

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | Input video file or URL | Required |
| `-o, --output` | Output video file | Required |
| `-r, --resolution` | Target height (720/1080/1440/2160) | 1080 |
| `-p, --preset` | vhs/dvd/webcam/youtube/clean | vhs |
| `--crf` | Quality (lower=better, 15-28) | 20 |
| `--encoder` | hevc_nvenc/h264_nvenc/libx265/libx264 | hevc_nvenc |
| `--engine` | Upscale engine: auto/maxine/realesrgan/ffmpeg | auto |
| `--hdr` | HDR mode: sdr/hdr10/hlg | sdr |
| `--realesrgan-model` | Real-ESRGAN model selection | realesrgan-x4plus |
| `--audio-enhance` | Audio enhancement: none/light/moderate/aggressive/voice/music | none |
| `--audio-upmix` | Surround upmix: none/simple/surround/prologic/demucs | none |
| `--audio-layout` | Output layout: original/stereo/5.1/7.1/mono | original |
| `--audio-format` | Audio format: aac/ac3/eac3/dts/flac | aac |
| `-v, --verbose` | Verbose logging | Off |

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

## 🎯 Quick Decision Guide

**What type of video do you have?** Follow the flowchart:

```
                        ┌─────────────────────┐
                        │  What's your source? │
                        └──────────┬──────────┘
                                   │
        ┌──────────────┬───────────┼───────────┬──────────────┐
        ▼              ▼           ▼           ▼              ▼
   ┌─────────┐   ┌─────────┐ ┌─────────┐ ┌─────────┐   ┌─────────┐
   │   VHS   │   │   DVD   │ │  Anime  │ │ YouTube │   │  Clean  │
   │  Tape   │   │  Rip    │ │ Cartoon │ │ Download│   │  HD/4K  │
   └────┬────┘   └────┬────┘ └────┬────┘ └────┬────┘   └────┬────┘
        │              │           │           │              │
        ▼              ▼           ▼           ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│preset: vhs   │ │preset:dvd│ │preset:   │ │preset:   │ │preset:   │
│engine:       │ │engine:   │ │clean     │ │youtube   │ │clean     │
│ realesrgan   │ │ maxine   │ │engine:   │ │engine:   │ │engine:   │
│denoise: 0.8  │ │          │ │realesrgan│ │ auto     │ │ maxine   │
│audio: voice  │ │          │ │model:    │ │          │ │          │
└──────────────┘ └──────────┘ │ anime    │ └──────────┘ └──────────┘
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
yt-dlp>=2023.0.0    # YouTube downloading
pyyaml>=6.0         # Configuration
gradio>=4.0.0       # Web interface
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
