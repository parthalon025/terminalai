# VHS Video Upscaling Pipeline v1.1.0

AI-powered video upscaling optimized for VHS-quality footage (480i) upscaled to 1080p+ using NVIDIA Maxine Video Effects SDK.

## Features

### Core Features
- **🎬 YouTube & Local Files** - Process videos from URLs or local files
- **🖥️ Modern Web GUI** - Beautiful Gradio-based interface with dark mode
- **📁 Drag & Drop** - Upload files by dragging into the browser
- **👁️ Video Preview** - See file info before processing
- **📋 Video Queue** - Batch processing with queue management
- **📊 Stats Dashboard** - Track progress and completed jobs
- **📜 Verbose Logging** - Detailed logs with file output

### Processing Features
- **🔧 Pre-processing** - Deinterlace (yadif), temporal denoise (hqdn3d), audio extraction
- **🚀 AI Upscaling** - NVIDIA Maxine SuperRes with artifact reduction
- **💾 Post-processing** - NVENC hardware encoding (H.265/H.264), audio remux
- **⚙️ Presets** - Optimized settings for VHS, DVD, webcam sources
- **📈 Progress tracking** - Real-time progress with ETA estimates

## Quick Start

### Option 1: Web GUI (Recommended)

```bash
# From the project root
python -m vhs_upscaler.gui

# Or directly
python gui.py
```

The browser will open automatically at `http://localhost:7860`

### Option 2: Command Line

```bash
# From YouTube URL
python vhs_upscale.py -i "https://youtube.com/watch?v=VIDEO_ID" -o output.mp4

# From local file
python vhs_upscale.py -i video.mp4 -o upscaled.mp4 --preset vhs

# 4K output
python vhs_upscale.py -i video.mp4 -o upscaled_4k.mp4 -r 2160
```

## Web GUI Features (v1.1.0)

The modern web interface provides:

| Tab | Description |
|-----|-------------|
| **📹 Single Video** | Upload file or enter URL with full options |
| **📚 Batch Processing** | Add multiple URLs at once |
| **📋 Queue** | Monitor and control processing with stats |
| **📜 Logs** | View real-time activity logs |
| **⚙️ Settings** | Configure output directory, dark mode |
| **ℹ️ About** | System info and alternatives |

### New in v1.1.0
- **File Upload**: Drag-and-drop video files directly
- **Video Preview**: See resolution, duration, codec, fps before processing
- **Dark Mode**: Toggle in Settings
- **Stats Dashboard**: Pending/Processing/Completed/Failed counts
- **Processing Time Estimation**: ETA based on video duration

## Requirements

### Hardware
- **GPU**: NVIDIA RTX 20/30/40/50 series (Tensor cores required)
- **VRAM**: 6GB minimum, 12GB+ for 4K output
- **OS**: Windows 10/11 (Maxine SDK), Linux (FFmpeg fallback)

### Software
- Python 3.10+
- NVIDIA Driver 535+
- FFmpeg (with NVENC support)
- NVIDIA Maxine Video Effects SDK (optional)

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | Input video file or folder | Required |
| `-o, --output` | Output video file or folder | Required |
| `-r, --resolution` | Target height (720/1080/1440/2160) | 1080 |
| `-q, --quality` | Mode: 0=best, 1=performance | 0 |
| `-p, --preset` | vhs/dvd/webcam/clean/auto | vhs |
| `--watch` | Enable watch folder mode | Off |
| `--crf` | Output quality (lower=better, 15-28) | 20 |
| `--encoder` | hevc_nvenc/h264_nvenc/libx265 | hevc_nvenc |
| `-v, --verbose` | Verbose logging | Off |

## Presets

| Preset | Best For | Deinterlace | Denoise |
|--------|----------|-------------|---------|
| `vhs` | VHS tapes (480i, heavy noise) | Yes | Strong |
| `dvd` | DVD rips (480p/576p) | Yes | Moderate |
| `webcam` | Old webcam footage | No | Strong |
| `youtube` | YouTube downloads | No | Light |
| `clean` | Already clean sources | No | None |
| `auto` | Unknown sources | Auto-detect | Light |

## Configuration

Edit `config.yaml` to customize defaults:

```yaml
maxine_path: "C:/Users/You/AppData/Local/NVIDIA/Maxine/bin"

defaults:
  resolution: 1080
  quality_mode: 0
  encoder: "hevc_nvenc"
  crf: 20
```

## Pipeline Stages

### 1. Pre-Processing (FFmpeg)
```
Input -> Deinterlace (yadif) -> Denoise (hqdn3d) -> Extract Audio
```

### 2. AI Upscaling (NVIDIA Maxine)
```
VideoEffectsApp.exe --effect=SuperRes --mode=0 --resolution=1080
```

### 3. Post-Processing (FFmpeg + NVENC)
```
Upscaled Video + Original Audio -> HEVC NVENC (CRF 20) -> Final Output
```

## Troubleshooting

### "Maxine VideoEffectsApp not found"
1. Set `MAXINE_HOME` environment variable
2. Or edit `config.yaml` with full path

### "NVENC encoder not found"
- Ensure NVIDIA drivers are 535+
- Try `--encoder libx265` as fallback (slower, CPU-based)

### Poor output quality
- Use `--quality 0` (best quality mode)
- Lower CRF: `--crf 18`

### Out of VRAM (4K upscaling)
- Close other GPU applications
- Use `--quality 1` (performance mode)
- Process at 1440p instead: `--resolution 1440`

## Files

```
vhs_upscaler/
├── gui.py              # Gradio web interface (v1.1.0)
├── vhs_upscale.py      # Main processing script
├── queue_manager.py    # Batch queue system
├── logger.py           # Logging system
├── config.yaml         # Configuration file
├── install.ps1         # Windows installer
└── scripts/            # Batch scripts
```

## License

MIT License - Use freely for personal and commercial projects.

## Credits

- [NVIDIA Maxine Video Effects SDK](https://developer.nvidia.com/maxine)
- [FFmpeg](https://ffmpeg.org/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Gradio](https://gradio.app/)
