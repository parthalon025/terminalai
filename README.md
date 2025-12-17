# TerminalAI - Video Processing Suite

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NVIDIA Maxine](https://img.shields.io/badge/NVIDIA-Maxine-76B900.svg)](https://developer.nvidia.com/maxine)

AI-powered video processing tools featuring YouTube downloading and VHS video upscaling using NVIDIA Maxine Video Effects SDK.

## Features

- **YouTube Video Downloader** - Download videos in best quality MP4 format
- **VHS Video Upscaler** - AI-powered upscaling for vintage footage (480i to 1080p/4K)
- **Modern Web GUI** - Beautiful Gradio-based interface with queue management
- **Batch Processing** - Process multiple videos with queue system
- **Watch Folder Mode** - Automatic processing of dropped files
- **Progress Tracking** - Real-time progress bars with ETA estimates

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/parthalon025/terminalai.git
cd terminalai

# Install dependencies
pip install -r vhs_upscaler/requirements.txt
```

### Download YouTube Videos

```bash
python download_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Upscale VHS Videos

```bash
# Launch web GUI (recommended)
python vhs_upscaler/gui.py

# Or use command line
python vhs_upscaler/vhs_upscale.py -i video.mp4 -o upscaled.mp4 --preset vhs
```

## Project Structure

```
terminalai/
├── download_youtube.py      # Standalone YouTube downloader
├── vhs_upscaler/            # VHS upscaling pipeline
│   ├── gui.py               # Web GUI (Gradio)
│   ├── vhs_upscale.py       # Main processing pipeline
│   ├── queue_manager.py     # Batch processing queue
│   ├── logger.py            # Verbose logging system
│   ├── config.yaml          # Configuration
│   ├── install.ps1          # Windows installer
│   ├── requirements.txt     # Python dependencies
│   └── scripts/             # Batch scripts
├── .gitignore
├── LICENSE
└── README.md
```

## Requirements

### Hardware
- **GPU**: NVIDIA RTX 20/30/40/50 series with Tensor Cores (for AI upscaling)
- **VRAM**: 8GB minimum, 16GB recommended for 4K
- **CPU**: Any modern multi-core processor (for FFmpeg processing)

### Software
- Python 3.10+
- FFmpeg (with NVENC support recommended)
- NVIDIA Maxine Video Effects SDK (for AI upscaling)
- yt-dlp (for YouTube downloads)

## Components

### 1. YouTube Downloader (`download_youtube.py`)

Simple, standalone script to download YouTube videos:

```bash
python download_youtube.py "https://youtu.be/VIDEO_ID" --output ./downloads
```

### 2. VHS Upscaler (`vhs_upscaler/`)

Full-featured video upscaling pipeline with:

- **Web GUI**: Modern interface at `http://localhost:7860`
- **CLI**: Command-line processing
- **Presets**: Optimized for VHS, DVD, webcam, etc.
- **Queue**: Batch processing with pause/resume
- **Logging**: Verbose logs with file output

See [vhs_upscaler/README.md](vhs_upscaler/README.md) for detailed documentation.

## Web GUI

Launch the modern web interface:

```bash
python vhs_upscaler/gui.py
```

Features:
- Single video processing with full options
- Batch processing (multiple URLs)
- Real-time queue monitoring
- Activity logs
- Configurable settings

## Dependencies

| Package | Purpose |
|---------|---------|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube video downloading |
| [Gradio](https://gradio.app/) | Modern web GUI |
| [PyYAML](https://pyyaml.org/) | Configuration files |
| [FFmpeg](https://ffmpeg.org/) | Video processing |
| [NVIDIA Maxine](https://developer.nvidia.com/maxine) | AI video effects |

## Configuration

Edit `vhs_upscaler/config.yaml`:

```yaml
maxine_path: "C:/path/to/maxine/bin"
ffmpeg_path: "ffmpeg"

defaults:
  resolution: 1080
  encoder: "hevc_nvenc"
  crf: 20
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [NVIDIA Maxine Video Effects SDK](https://developer.nvidia.com/maxine) - AI video upscaling
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloading
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [Gradio](https://gradio.app/) - Web interface framework

## Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](vhs_upscaler/README.md#troubleshooting) section
2. Search existing [Issues](https://github.com/parthalon025/terminalai/issues)
3. Open a new issue with detailed information
