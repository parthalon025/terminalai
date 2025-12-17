<p align="center">
  <h1 align="center">🎬 TerminalAI - Video Processing Suite</h1>
  <p align="center">
    <strong>AI-powered VHS video upscaling and YouTube downloading with NVIDIA RTX acceleration</strong>
  </p>
</p>

<p align="center">
  <a href="https://github.com/parthalon025/terminalai/releases"><img src="https://img.shields.io/badge/version-1.1.0-blue?style=flat-square" alt="Version 1.1.0"></a>
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
| 🎬 **AI Video Upscaling** | NVIDIA Maxine SuperRes - upscale to 1080p or 4K |
| 📺 **VHS Restoration** | Optimized presets for vintage footage (deinterlace + denoise) |
| ⬇️ **YouTube Integration** | Download and upscale YouTube videos in one step |
| 📁 **Drag & Drop Upload** | Simply drag video files into the browser |
| 🌙 **Dark Mode** | Easy on the eyes with theme toggle |
| 📊 **Stats Dashboard** | Real-time queue statistics and progress |
| 📋 **Queue System** | Batch process multiple videos with pause/resume |
| 👁️ **Video Preview** | See file info (resolution, duration, codec) before processing |
| 🚀 **GPU Accelerated** | RTX Tensor Core + NVENC hardware encoding |

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
| 📹 **Single Video** | Upload file or enter URL with full options |
| 📚 **Batch Processing** | Add multiple URLs at once |
| 📋 **Queue** | Monitor progress with stats dashboard |
| 📜 **Logs** | Real-time activity logging |
| ⚙️ **Settings** | Output directory, dark mode toggle |
| ℹ️ **About** | System info and alternatives |

```
┌─────────────────────────────────────────────────────────────┐
│  🎬 VHS Video Upscaler                           v1.1.0     │
│  AI-Powered Video Enhancement with NVIDIA Maxine            │
├─────────────────────────────────────────────────────────────┤
│  📹 Single │ 📚 Batch │ 📋 Queue │ 📜 Logs │ ⚙️ Settings    │
├─────────────────────────────────────────────────────────────┤
│  ┌─ Upload File ──────────┐ ┌─ URL / Path ─────────────┐   │
│  │  [Drag & Drop Video]   │ │ [youtube.com/watch?v=...]│   │
│  │  Resolution: 1920x1080 │ └───────────────────────────┘   │
│  │  Duration: 0:05:30     │                                 │
│  │  Codec: h264 @ 30fps   │  Preset: [vhs ▼]               │
│  └────────────────────────┘  Resolution: [1080p ▼]         │
│                                                             │
│  [➕ Add to Queue]                                          │
│                                                             │
│  ┌─ Stats ──────────────────────────────────────────────┐  │
│  │ Pending: 2 │ Processing: 1 │ Completed: 5 │ Failed: 0│  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
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
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | Input video file or URL | Required |
| `-o, --output` | Output video file | Required |
| `-r, --resolution` | Target height (720/1080/1440/2160) | 1080 |
| `-p, --preset` | vhs/dvd/webcam/youtube/clean | vhs |
| `--crf` | Quality (lower=better, 15-28) | 20 |
| `--encoder` | hevc_nvenc/h264_nvenc/libx265 | hevc_nvenc |
| `-v, --verbose` | Verbose logging | Off |

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

## 💻 Requirements

### Hardware

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **GPU** | RTX 2060 (Tensor Cores) | RTX 3080+ |
| **VRAM** | 6GB | 12GB+ for 4K |
| **RAM** | 8GB | 16GB+ |
| **Storage** | 10GB free | SSD recommended |

### Software

- **Python** 3.10+
- **NVIDIA Driver** 535+
- **FFmpeg** with NVENC support
- **NVIDIA Maxine Video Effects SDK** (for AI upscaling)

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
