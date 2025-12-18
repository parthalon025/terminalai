# TerminalAI Utility Scripts

This directory contains utility scripts for setup, verification, and analysis.

## Scripts Overview

### Setup Scripts

#### `setup_maxine.py`
Setup and configure NVIDIA Maxine SDK for AI upscaling.

**Usage:**
```bash
python scripts/setup_maxine.py
```

**Features:**
- Downloads NVIDIA Maxine SDK
- Configures environment variables
- Verifies GPU compatibility
- Tests Maxine functionality

**Requirements:**
- NVIDIA RTX GPU (20/30/40 series)
- NVIDIA Driver 535+
- Windows or Linux

**Note:** The NVIDIA Maxine installer (~747 MB) is not included in the repository due to GitHub's 100 MB file size limit. Download it manually from:
- [NVIDIA Developer Portal](https://www.nvidia.com/en-us/geforce/broadcasting/broadcast-sdk/resources/)
- Place in `scripts/` directory before running setup

---

#### `verify_setup.py`
Comprehensive environment verification tool.

**Usage:**
```bash
python scripts/verify_setup.py
```

**Checks:**
- Python version and dependencies
- FFmpeg installation and codecs
- GPU availability (NVIDIA, AMD, Intel)
- Maxine SDK (if installed)
- Real-ESRGAN (if installed)
- Audio processing dependencies (Demucs, PyTorch)
- Write permissions

**Output:**
- Detailed report of available features
- Missing dependency warnings
- Recommended actions

---

### Download Scripts

#### `download_youtube.py`
Standalone YouTube video downloader using yt-dlp.

**Usage:**
```bash
# Download single video
python scripts/download_youtube.py "https://youtube.com/watch?v=VIDEO_ID"

# Download with custom quality
python scripts/download_youtube.py "https://youtube.com/watch?v=VIDEO_ID" --quality 1080p

# Download playlist
python scripts/download_youtube.py "https://youtube.com/playlist?list=PLAYLIST_ID"
```

**Options:**
- `--quality` - Video quality (480p, 720p, 1080p, 2160p, best)
- `--output` - Output directory
- `--format` - Video format (mp4, mkv, webm)

**Features:**
- Playlist support
- Quality selection
- Metadata extraction
- Progress tracking
- Resume downloads

---

### Analysis Scripts

#### `video_analyzer.sh`
Bash-based video analyzer for systems without Python/OpenCV.

**Usage:**
```bash
# Analyze video
bash scripts/video_analyzer.sh input.mp4

# Save analysis to JSON
bash scripts/video_analyzer.sh input.mp4 > analysis.json
```

**Detects:**
- Scan type (progressive/interlaced)
- Video resolution and framerate
- Codec information
- Noise level estimation
- Source format hints
- Duration and file size

**Requirements:**
- FFmpeg with ffprobe
- jq (JSON processor)
- Bash 4.0+

**Output Format:**
JSON compatible with Python analyzer wrapper

---

### Utility Scripts

#### `generate_luts.py`
Generate color grading LUT files for video processing.

**Usage:**
```bash
# Generate all default LUTs
python scripts/generate_luts.py

# Generate specific LUT
python scripts/generate_luts.py --type vhs_restore

# Custom LUT parameters
python scripts/generate_luts.py --type custom --warmth 1.2 --saturation 1.1
```

**LUT Types:**
- `vhs_restore` - Restore VHS color characteristics
- `warm_vintage` - Warm, vintage film look
- `cool_modern` - Cool, modern color grading
- `custom` - Custom color grading with parameters

**Output:**
Generates `.cube` files in `luts/` directory

---

## Installation

All scripts are standalone but require the base TerminalAI environment:

```bash
# Install TerminalAI with dev dependencies
pip install -e ".[dev]"

# For Maxine setup (Windows/NVIDIA only)
python scripts/setup_maxine.py

# Verify installation
python scripts/verify_setup.py
```

## Integration

These scripts can be called from:
- Command line (manual execution)
- TerminalAI main application
- External automation tools
- CI/CD pipelines

## Adding New Scripts

When adding utility scripts:

1. **Follow naming convention**: `action_target.py` (e.g., `download_youtube.py`)
2. **Include shebang**: `#!/usr/bin/env python3` or `#!/usr/bin/env bash`
3. **Add documentation**: Docstrings and comments
4. **Update this README**: Add usage instructions
5. **Make executable**: `chmod +x scripts/new_script.py`
6. **Add tests**: Create `tests/test_script.py` if applicable

## Troubleshooting

### Script Not Found
```bash
# Make sure you're in the project root
cd terminalai

# Or use absolute path
python "D:\SSD\AI_Tools\terminalai\scripts\verify_setup.py"
```

### Permission Denied (Linux/Mac)
```bash
chmod +x scripts/*.py scripts/*.sh
```

### Import Errors
```bash
# Install in editable mode
pip install -e .

# Or run from project root
cd terminalai
python scripts/verify_setup.py
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on adding new scripts.

---

For issues or questions, see the main [README](../README.md) or open an [issue](https://github.com/parthalon025/terminalai/issues).
