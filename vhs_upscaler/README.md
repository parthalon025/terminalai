# VHS Video Upscaling Pipeline

AI-powered video upscaling optimized for VHS-quality footage (480i) upscaled to 1080p+ using NVIDIA Maxine Video Effects SDK.

## Features

- **🎬 YouTube & Local Files** — Process videos from URLs or local files
- **🖥️ Modern Web GUI** — Beautiful Gradio-based interface
- **📋 Video Queue** — Batch processing with queue management
- **📊 Verbose Logging** — Detailed logs with file output
- **👁️ Watch folder automation** — Drop files in `/input`, get processed files in `/output`
- **🔧 Pre-processing** — Deinterlace (yadif), temporal denoise (hqdn3d), audio extraction
- **🚀 AI Upscaling** — NVIDIA Maxine SuperRes with artifact reduction
- **💾 Post-processing** — NVENC hardware encoding (H.265/H.264), audio remux
- **⚙️ Presets** — Optimized settings for VHS, DVD, webcam sources
- **📈 Progress tracking** — Real-time progress with ETA estimates

## Quick Start

### Option 1: Web GUI (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the web interface
python gui.py
```

The browser will open automatically at `http://localhost:7860`

### Option 2: Command Line

```bash
# From YouTube URL
python vhs_upscale.py -i "https://youtube.com/watch?v=VIDEO_ID" -o output.mp4

# From local file
python vhs_upscale.py -i video.mp4 -o upscaled.mp4 --preset vhs
```

## Web GUI Features

The modern web interface provides:

- **Single Video Tab** — Process one video with full options
- **Batch Processing Tab** — Add multiple URLs at once
- **Queue Tab** — Monitor and control processing queue
- **Logs Tab** — View real-time activity logs
- **Settings Tab** — Configure output directory

### Screenshots

```
┌─────────────────────────────────────────────────────────────┐
│  🎬 VHS Video Upscaler                                      │
│  AI-Powered Video Enhancement with NVIDIA Maxine            │
├─────────────────────────────────────────────────────────────┤
│  📹 Single Video │ 📚 Batch │ 📋 Queue │ 📜 Logs │ ⚙️ Settings │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Video Source: [https://youtube.com/watch?v=...           ] │
│                                                             │
│  Preset: [vhs ▼]    Resolution: [1080 ▼]                    │
│                                                             │
│  [➕ Add to Queue]                                          │
│                                                             │
│  ┌─ Queue ─────────────────────────────────────────────┐    │
│  │ ⬇️ Downloading: Video Title                         │    │
│  │ [████████████░░░░░░░░░░░░░░░] 45% | ETA: 0:02:30    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Requirements

### Hardware
- **GPU**: NVIDIA RTX 30/40/50 series (Tensor cores required)
- **VRAM**: 8GB minimum, 16GB recommended for 4K output
- **OS**: Windows 10/11 (Maxine SDK is Windows-only)

### Software
- Python 3.8+
- NVIDIA Driver 535+
- FFmpeg (with NVENC support)
- NVIDIA Maxine Video Effects SDK

## Installation

### 1. Run the installer

```powershell
# Open PowerShell as Administrator
.\install.ps1
```

This will:
- Check for NVIDIA GPU and drivers
- Install FFmpeg if missing
- Guide you through Maxine SDK download
- Configure environment variables

### 2. Manual Maxine SDK Download

The installer will open the download page. You need an NVIDIA account (free):

1. Visit: https://catalog.ngc.nvidia.com/orgs/nvidia/teams/maxine/resources/maxine_video_effects
2. Sign in / Create NVIDIA account
3. Download "Video Effects SDK"
4. Extract to the path shown by installer

### 3. Install Python dependencies

```bash
pip install pyyaml
```

### 4. Verify installation

```bash
python vhs_upscale.py --help
```

## Usage

### Single File Processing

```bash
# Basic usage (1080p output)
python vhs_upscale.py -i old_vhs_tape.mp4 -o restored.mp4

# With VHS preset (default)
python vhs_upscale.py -i video.mp4 -o out.mp4 --preset vhs

# 4K output
python vhs_upscale.py -i video.mp4 -o out_4k.mp4 --resolution 2160

# DVD source
python vhs_upscale.py -i dvd_rip.mp4 -o restored.mp4 --preset dvd
```

### Watch Folder Mode

```bash
# Monitor folder for new files
python vhs_upscale.py --watch -i ./input -o ./output

# Files dropped in ./input will be processed automatically
# Processed originals move to ./input/processed/
```

### Using Batch Scripts

```batch
:: Quick VHS to 1080p
scripts\upscale_vhs_1080p.bat video.mp4

:: DVD to 4K
scripts\upscale_dvd_4k.bat dvd_rip.mp4

:: Start watch folder
scripts\watch_folder.bat
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | Input video file or folder | Required |
| `-o, --output` | Output video file or folder | Required |
| `-r, --resolution` | Target height (720/1080/1440/2160) | 1080 |
| `-q, --quality` | Mode: 0=best, 1=performance | 0 |
| `-p, --preset` | vhs/dvd/webcam/clean/auto | vhs |
| `--watch` | Enable watch folder mode | Off |
| `--crf` | Output quality (lower=better) | 20 |
| `--encoder` | hevc_nvenc/h264_nvenc/libx265 | hevc_nvenc |
| `--config` | Custom config file path | config.yaml |
| `--keep-temp` | Keep temp files for debugging | Off |
| `-v, --verbose` | Verbose logging | Off |

## Presets

| Preset | Best For | Deinterlace | Denoise |
|--------|----------|-------------|---------|
| `vhs` | VHS tapes (480i, heavy noise) | Yes | Strong |
| `dvd` | DVD rips (480p/576p) | Yes | Moderate |
| `webcam` | Old webcam footage | No | Strong |
| `clean` | Already clean sources | No | None |
| `auto` | Unknown sources | Auto-detect | Light |

## Configuration

Edit `config.yaml` to customize defaults:

```yaml
# Set Maxine SDK path if not auto-detected
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
Input → Deinterlace (yadif) → Denoise (hqdn3d) → Extract Audio
```

### 2. AI Upscaling (NVIDIA Maxine)
```
VideoEffectsApp.exe --effect=SuperRes --mode=0 --resolution=1080
```
- SuperRes includes artifact reduction (better than basic Upscale)
- Mode 0 = Maximum quality (uses more VRAM)
- Leverages RTX Tensor cores

### 3. Post-Processing (FFmpeg + NVENC)
```
Upscaled Video + Original Audio → HEVC NVENC (CRF 20) → Final Output
```

## Troubleshooting

### "Maxine VideoEffectsApp not found"
1. Run `install.ps1` again
2. Or set `MAXINE_HOME` environment variable to SDK install path
3. Or edit `config.yaml` with full path

### "NVENC encoder not found"
- Ensure NVIDIA drivers are 535+
- Try `--encoder libx265` as fallback (slower, CPU-based)

### Poor output quality
- Try `--quality 0` (best quality mode)
- Lower CRF: `--crf 18`
- Ensure source isn't too degraded (Maxine can't create detail from nothing)

### Out of VRAM (4K upscaling)
- Close other GPU applications
- Use `--quality 1` (performance mode)
- Process at 1440p instead: `--resolution 1440`

### Audio sync issues
- Original audio is preserved without re-encoding
- If sync issues persist, try: `ffmpeg -i output.mp4 -itsoffset 0.1 -i output.mp4 -map 1:v -map 0:a -c copy fixed.mp4`

## Performance

Typical processing times on RTX 5080 (16GB):

| Source | Target | Time (per min of video) |
|--------|--------|------------------------|
| 480i VHS | 1080p | ~45 seconds |
| 480p DVD | 1080p | ~30 seconds |
| 480i VHS | 4K | ~90 seconds |

## Files

```
vhs_upscaler/
├── install.ps1          # Automated setup script
├── vhs_upscale.py       # Main processing script
├── config.yaml          # Configuration file
├── README.md            # This file
└── scripts/
    ├── upscale_vhs_1080p.bat
    ├── upscale_vhs_4k.bat
    ├── upscale_dvd_1080p.bat
    ├── upscale_dvd_4k.bat
    └── watch_folder.bat
```

## License

MIT License - Use freely for personal and commercial projects.

## Credits

- [NVIDIA Maxine Video Effects SDK](https://developer.nvidia.com/maxine)
- [FFmpeg](https://ffmpeg.org/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (for YouTube downloading)
