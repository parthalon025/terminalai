<p align="center">
  <h1 align="center">🎬 TerminalAI - Video Processing Suite</h1>
  <p align="center">
    <strong>AI-powered VHS video upscaling and YouTube downloading with NVIDIA RTX acceleration</strong>
  </p>
</p>

<p align="center">
  <a href="https://github.com/parthalon025/terminalai/releases"><img src="https://img.shields.io/github/v/release/parthalon025/terminalai?style=flat-square&color=blue" alt="Release"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"></a>
  <a href="https://developer.nvidia.com/maxine"><img src="https://img.shields.io/badge/NVIDIA-Maxine-76B900?style=flat-square&logo=nvidia&logoColor=white" alt="NVIDIA Maxine"></a>
  <a href="https://gradio.app/"><img src="https://img.shields.io/badge/Gradio-Web_GUI-orange?style=flat-square" alt="Gradio"></a>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-web-gui">Web GUI</a> •
  <a href="#-requirements">Requirements</a> •
  <a href="#-alternatives">Alternatives</a>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎬 **AI Video Upscaling** | NVIDIA Maxine SuperRes with artifact reduction - up to 4K output |
| 📺 **VHS Restoration** | Optimized presets for vintage footage (deinterlace + denoise) |
| ⬇️ **YouTube Integration** | Download and upscale YouTube videos in one step |
| 🖥️ **Modern Web GUI** | Beautiful Gradio interface with dark mode support |
| 📋 **Queue System** | Batch process multiple videos with pause/resume |
| 👁️ **Watch Folder** | Automatic processing when files are dropped |
| 🚀 **GPU Accelerated** | RTX Tensor Core + NVENC hardware encoding |
| 📊 **Progress Tracking** | Real-time progress bars with ETA estimates |

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/parthalon025/terminalai.git
cd terminalai

# Install Python dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### Launch Web GUI (Recommended)

```bash
python vhs_upscaler/gui.py
```

Opens automatically at `http://localhost:7860`

### Command Line Usage

```bash
# Download YouTube video
python download_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Upscale VHS tape to 1080p
python vhs_upscaler/vhs_upscale.py -i video.mp4 -o upscaled.mp4 --preset vhs

# Upscale to 4K
python vhs_upscaler/vhs_upscale.py -i video.mp4 -o upscaled_4k.mp4 -r 2160

# Watch folder mode (auto-process new files)
python vhs_upscaler/vhs_upscale.py --watch -i ./input -o ./output
```

## 🖥️ Web GUI

The modern Gradio web interface provides:

- **Single Video** - Process one video with full options
- **Batch Processing** - Add multiple URLs at once
- **Queue Manager** - Monitor and control processing
- **Activity Logs** - Real-time logging display
- **Settings** - Configure output directory
- **About** - System info and alternatives

```
┌─────────────────────────────────────────────────────────────┐
│  🎬 VHS Video Upscaler                           v1.0.0    │
│  AI-Powered Video Enhancement with NVIDIA Maxine           │
├─────────────────────────────────────────────────────────────┤
│  📹 Single │ 📚 Batch │ 📋 Queue │ 📜 Logs │ ⚙️ Settings   │
├─────────────────────────────────────────────────────────────┤
│  Video: [https://youtube.com/watch?v=...               ]   │
│  Preset: [vhs ▼]    Resolution: [1080p ▼]                  │
│  [➕ Add to Queue]                                          │
│  ┌─ Queue ─────────────────────────────────────────────┐   │
│  │ ⬇️ Downloading: Video Title                         │   │
│  │ [████████████░░░░░░░░░░░░░░] 45% │ ETA: 0:02:30     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Project Structure

```
terminalai/
├── download_youtube.py      # Standalone YouTube downloader
├── vhs_upscaler/            # Main upscaling package
│   ├── gui.py               # Gradio web interface
│   ├── vhs_upscale.py       # Processing pipeline
│   ├── queue_manager.py     # Batch queue system
│   ├── logger.py            # Verbose logging
│   ├── config.yaml          # Configuration
│   ├── install.ps1          # Windows installer
│   └── scripts/             # Batch scripts
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Package config
├── LICENSE                  # MIT License
└── README.md
```

## 💻 Requirements

### Hardware

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **GPU** | RTX 2060 (Tensor Cores) | RTX 3080+ |
| **VRAM** | 6GB | 12GB+ for 4K |
| **RAM** | 8GB | 16GB+ |
| **Storage** | 10GB free | SSD recommended |

### Software

- **Python** 3.10+ (required for Gradio)
- **NVIDIA Driver** 535+
- **FFmpeg** with NVENC support
- **NVIDIA Maxine Video Effects SDK** (for AI upscaling)
- **yt-dlp** (for YouTube downloads)

## ⚙️ Presets

| Preset | Source Type | Deinterlace | Denoise | Best For |
|--------|-------------|-------------|---------|----------|
| `vhs` | 480i VHS tapes | ✅ Yes | Strong | Old home videos |
| `dvd` | 480p/576p DVDs | ✅ Yes | Moderate | DVD rips |
| `webcam` | Low-quality webcam | ❌ No | Strong | Old webcam footage |
| `youtube` | YouTube downloads | ❌ No | Light | Downloaded videos |
| `clean` | Already clean | ❌ No | None | High-quality sources |
| `auto` | Unknown | Auto-detect | Auto | Mixed content |

## 🔄 Alternatives

Choose the right tool for your needs:

| Project | Speed | Quality | Best For | Open Source |
|---------|-------|---------|----------|-------------|
| **TerminalAI** | ⚡ Fast | Good | VHS/DVD restoration, YouTube | ✅ Yes |
| [Video2X](https://github.com/k4yt3x/video2x) | Medium | Excellent | Anime, Real-ESRGAN | ✅ Yes |
| [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) | Slow | Best | Maximum quality | ✅ Yes |
| [Topaz Video AI](https://www.topazlabs.com/) | Medium | Excellent | Easy to use | ❌ Commercial |
| [RTX Upscaler](https://github.com/abus-aikorea/rtx-upscaler) | Fast | Good | Similar to TerminalAI | ⚠️ Trial Limited |

**When to use TerminalAI:**
- You have VHS tapes or DVDs to restore
- You want to download + upscale YouTube videos
- You need batch processing with queue management
- You have an NVIDIA RTX GPU

## 🔧 Configuration

Edit `vhs_upscaler/config.yaml`:

```yaml
# NVIDIA Maxine SDK path (auto-detected if MAXINE_HOME is set)
maxine_path: "C:/path/to/maxine/bin"
ffmpeg_path: "ffmpeg"

defaults:
  resolution: 1080
  encoder: "hevc_nvenc"
  crf: 20
  quality_mode: 0  # 0=best, 1=fast
```

## 🤝 Contributing

Contributions are welcome! See our [Contributing Guide](CONTRIBUTING.md).

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [NVIDIA Maxine Video Effects SDK](https://developer.nvidia.com/maxine) - AI video upscaling
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloading
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [Gradio](https://gradio.app/) - Web interface framework
- [Video2X](https://github.com/k4yt3x/video2x) - Inspiration for features

---

<p align="center">
  <b>Keywords:</b> VHS upscaling, video restoration, AI video enhancement, NVIDIA Maxine, RTX video super resolution,
  YouTube downloader, video upscaler, 480p to 1080p, 480p to 4K, deinterlace, denoise, NVENC encoding,
  batch video processing, Python video tools, Gradio GUI, analog video digitization, vintage video restoration
</p>

<p align="center">
  Made with ❤️ by the TerminalAI community
</p>
