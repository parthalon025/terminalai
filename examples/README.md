# Example Workflow Scripts

This directory contains ready-to-use shell scripts demonstrating common video processing workflows with TerminalAI. Each script is fully documented, beginner-friendly, and can be customized for your specific needs.

## Quick Start

### 1. Make Scripts Executable

```bash
# Linux/Mac
chmod +x examples/*.sh

# Windows (Git Bash or WSL)
chmod +x examples/*.sh
```

### 2. Run a Script

```bash
# Navigate to examples directory
cd examples/

# Run any script
./vhs_full_pipeline.sh input.mp4 output.mp4
```

## Available Scripts

### 1. VHS Full Pipeline (`vhs_full_pipeline.sh`)

**Complete VHS tape restoration with all processing stages.**

**Use case:** You have old VHS family videos that are interlaced, noisy, and low-resolution. You want to restore them to modern quality.

**Processing stages:**
1. DEINTERLACE - Remove combing artifacts (QTGMC or yadif)
2. DENOISE - Remove VHS tape noise
3. UPSCALE - AI upscaling (Real-ESRGAN or NVIDIA Maxine)
4. FACE RESTORE - Optional GFPGAN face enhancement
5. SHARPEN - Contrast adaptive sharpening
6. ENCODE - Hardware-accelerated H.265 output

**Usage:**
```bash
# Basic usage
./vhs_full_pipeline.sh input.avi output.mp4

# Process VHS tape to 4K
./vhs_full_pipeline.sh "family_1995.avi" "restored_1995_4K.mp4"
```

**Customization:**
Edit the script's `CONFIGURATION` section to adjust:
- Resolution (1080p, 1440p, 2160p/4K)
- Deinterlacing algorithm (yadif fast, QTGMC best)
- Face restoration (enable/disable, strength)
- Audio enhancement mode
- Encoder and quality settings

**When to use:**
- VHS tapes with interlacing
- Noisy analog footage
- Low-resolution home videos
- Videos needing comprehensive restoration

---

### 2. YouTube Batch (`youtube_batch.sh`)

**Download and process multiple YouTube videos in one workflow.**

**Use case:** You want to download a YouTube playlist or channel and upscale all videos to higher quality.

**Features:**
- Batch download from URL list file
- Automatic preset selection for YouTube content
- Sequential or parallel processing
- Resume capability for interrupted batches
- Quality selection (best, 1080p, 720p, etc.)

**Usage:**
```bash
# Single video
./youtube_batch.sh "https://youtube.com/watch?v=VIDEO_ID"

# Multiple videos from file
./youtube_batch.sh urls.txt

# Playlist download
./youtube_batch.sh "https://youtube.com/playlist?list=PLAYLIST_ID"
```

**URL file format (urls.txt):**
```
https://youtube.com/watch?v=VIDEO_ID_1
https://youtube.com/watch?v=VIDEO_ID_2
https://youtube.com/watch?v=VIDEO_ID_3
# Comments are ignored
```

**Customization:**
Edit the script's `CONFIGURATION` section to adjust:
- Download quality (best, 1080p, 720p)
- Upscaling settings (enable/disable, resolution)
- Parallel downloads/processing
- Keep or delete original downloads
- Audio enhancement

**When to use:**
- Downloading YouTube playlists
- Archiving YouTube channels
- Upscaling old YouTube videos
- Batch processing downloaded content

**Requirements:**
- `yt-dlp` installed: `pip install yt-dlp`

---

### 3. Audio Upmix Workflow (`audio_upmix_workflow.sh`)

**Extract, enhance, and upmix audio to 5.1/7.1 surround sound.**

**Use case:** You have a video with stereo or mono audio and want to create immersive 5.1 surround sound. Perfect for VHS dialogue restoration or creating theater-like audio.

**Processing stages:**
1. EXTRACT - Extract audio from video
2. ENHANCE - Noise reduction, EQ, normalization
3. UPMIX - Convert stereo to 5.1 or 7.1 surround
4. ENCODE - AC3, EAC3, DTS, or AAC format
5. MUX - Combine with video

**Upmix algorithms:**
- `simple` - Fast FFmpeg pan filter (★★☆☆☆)
- `surround` - FFmpeg surround filter (★★★☆☆)
- `prologic` - Dolby Pro Logic II decoder (★★★☆☆)
- `demucs` - AI stem separation - BEST quality (★★★★★, requires PyTorch)

**Usage:**
```bash
# Basic 5.1 upmix with voice enhancement
./audio_upmix_workflow.sh input.mp4 output_5.1.mp4

# VHS dialogue restoration
./audio_upmix_workflow.sh vhs_tape.avi enhanced_surround.mp4
```

**Customization:**
Edit the script's `CONFIGURATION` section to adjust:
- Enhancement mode (voice, music, aggressive)
- Upmix algorithm (simple, surround, prologic, demucs)
- Output layout (stereo, 5.1, 7.1)
- Audio format (AAC, AC3, EAC3, DTS, FLAC)
- Loudness normalization

**When to use:**
- VHS dialogue restoration (voice mode + prologic/demucs)
- Creating surround sound from stereo
- Audio noise reduction
- Normalizing audio loudness
- Converting audio formats

**Requirements:**
- For Demucs AI upmix: `pip install torch torchaudio demucs`

---

### 4. Comparison Testing (`comparison_testing.sh`)

**Test multiple presets side-by-side to find the best settings.**

**Use case:** You're not sure which preset to use for your video. This script tests multiple presets on short clips and creates a comparison grid so you can choose the best one.

**Features:**
- Extract representative test clips
- Process same clips with different presets
- Create side-by-side comparison grid
- Generate quality comparison report
- Save time by testing on short clips first

**Usage:**
```bash
# Test all default presets (vhs, dvd, clean, youtube)
./comparison_testing.sh input.mp4

# Test specific presets with custom clip
./comparison_testing.sh input.mp4 --start 60 --duration 15 --presets vhs,dvd,clean

# Multi-clip comprehensive test
./comparison_testing.sh input.mp4 --multi-clip --clip-count 5

# 4K resolution test
./comparison_testing.sh input.mp4 --resolution 2160
```

**Output files:**
- `original.mp4` - Source clip
- `preset_vhs.mp4` - VHS preset result
- `preset_dvd.mp4` - DVD preset result
- `preset_clean.mp4` - Clean preset result
- `comparison_grid.mp4` - Side-by-side comparison video
- `comparison_report.txt` - Quality analysis report

**Customization:**
Edit the script's `CONFIGURATION` section to adjust:
- Clip start time and duration
- Presets to test
- Resolution and quality settings
- Grid layout (2x2, 2x3, etc.)
- Multi-clip mode

**When to use:**
- Before processing long videos
- Choosing optimal preset
- Comparing quality vs processing time
- Testing new settings
- Demonstrating processing improvements

**Preset selection guide:**
- `vhs` - Interlaced VHS tapes (deinterlace + heavy denoise)
- `dvd` - DVD rips (moderate deinterlace + denoise)
- `webcam` - Low-quality webcam footage (heavy denoise)
- `youtube` - Downloaded YouTube videos (light processing)
- `clean` - High-quality sources (minimal processing)

---

## Common Workflow Patterns

### Pattern 1: Test First, Then Process

Always test presets before processing long videos:

```bash
# Step 1: Test presets on short clip
./comparison_testing.sh long_video.mp4

# Step 2: Review comparison_grid.mp4 and choose best preset

# Step 3: Process full video with chosen preset
./vhs_full_pipeline.sh long_video.mp4 final_output.mp4
# (Edit PRESET="vhs" in the script first)
```

### Pattern 2: YouTube Playlist Workflow

Download and upscale entire YouTube playlists:

```bash
# Step 1: Create URL list file
cat > youtube_urls.txt << EOF
https://youtube.com/watch?v=VIDEO_1
https://youtube.com/watch?v=VIDEO_2
https://youtube.com/watch?v=VIDEO_3
EOF

# Step 2: Batch download and process
./youtube_batch.sh youtube_urls.txt
```

### Pattern 3: VHS Restoration + Surround Audio

Complete VHS restoration with 5.1 surround sound:

```bash
# Step 1: Process video with VHS pipeline
./vhs_full_pipeline.sh vhs_tape.avi restored_video.mp4

# Step 2: Add surround audio
./audio_upmix_workflow.sh restored_video.mp4 final_with_5.1.mp4
# (Set UPMIX_MODE="demucs" and ENHANCE_MODE="voice" in script)
```

### Pattern 4: Batch VHS Tape Processing

Process multiple VHS tapes with same settings:

```bash
# Step 1: Test on one representative tape
./comparison_testing.sh tape_sample.avi --presets vhs,dvd

# Step 2: Choose best preset (e.g., "vhs")

# Step 3: Edit vhs_full_pipeline.sh to set PRESET="vhs"

# Step 4: Process all tapes
for tape in *.avi; do
    ./vhs_full_pipeline.sh "$tape" "restored/$(basename "$tape" .avi)_restored.mp4"
done
```

---

## Script Customization Guide

### Editing Configuration

All scripts have a `CONFIGURATION` section at the top:

```bash
################################################################################
# CONFIGURATION
################################################################################

# Video Processing Settings
RESOLUTION="1080"                 # Change to 1440 or 2160 for 4K
PRESET="vhs"                      # Change to dvd, clean, youtube, webcam
ENGINE="auto"                     # Change to maxine, realesrgan, ffmpeg
```

**Steps to customize:**
1. Open script in text editor: `nano vhs_full_pipeline.sh`
2. Find the `CONFIGURATION` section
3. Edit values (follow comments for guidance)
4. Save and run: `./vhs_full_pipeline.sh input.mp4 output.mp4`

### Common Settings to Adjust

**Resolution:**
- `1080` - Full HD (fast, good quality)
- `1440` - 2K (balanced)
- `2160` - 4K (slow, best quality)

**Preset:**
- `vhs` - Heavy deinterlace + denoise
- `dvd` - Moderate processing
- `clean` - Minimal processing
- `youtube` - Light denoise for compressed content
- `webcam` - Heavy denoise, no deinterlace

**Engine:**
- `auto` - Auto-select best available
- `maxine` - NVIDIA Maxine (best, requires RTX GPU)
- `realesrgan` - Real-ESRGAN (AMD/Intel/NVIDIA)
- `ffmpeg` - CPU-based (slowest, universal)

**Encoder:**
- `h265_nvenc` - H.265 GPU (best quality, smaller files)
- `h264_nvenc` - H.264 GPU (faster, compatible)
- `libx265` - H.265 CPU (slow, high quality)
- `libx264` - H.264 CPU (fast, compatible)

**CRF (Quality):**
- `18` - Very high quality (large files)
- `20` - High quality (recommended)
- `23` - Good quality (balanced)
- `28` - Lower quality (small files)

---

## Troubleshooting

### Script Won't Run

**Error: Permission denied**
```bash
# Make executable
chmod +x examples/*.sh
```

**Error: Command not found**
```bash
# On Windows, use Git Bash or WSL
# Or run with: bash vhs_full_pipeline.sh input.mp4 output.mp4
```

### Processing Errors

**Error: FFmpeg not found**
```bash
# Install FFmpeg
# Ubuntu/Debian: sudo apt install ffmpeg
# Mac: brew install ffmpeg
# Windows: Download from ffmpeg.org
```

**Error: yt-dlp not found**
```bash
pip install yt-dlp
```

**Error: Module not found**
```bash
# Install TerminalAI package
cd ..
pip install -e .
```

### Performance Issues

**Processing too slow**
- Use `ENGINE="ffmpeg"` for CPU-only processing
- Reduce `RESOLUTION` (e.g., 1080 instead of 2160)
- Use `ENCODER="h264_nvenc"` instead of `h265_nvenc`
- Set `QUALITY_MODE="fast"` instead of `high`

**Out of memory**
- Reduce resolution
- Process shorter clips
- Close other applications
- Use `KEEP_TEMP="false"` to save disk space

**GPU not detected**
- Check NVIDIA driver: `nvidia-smi`
- Install CUDA toolkit
- Use `ENGINE="realesrgan"` (supports AMD/Intel)
- Fallback to `ENGINE="ffmpeg"` (CPU-only)

---

## Advanced Usage

### Dry Run Mode

Preview processing pipeline without executing:

```bash
# Edit any script and add --dry-run flag to the command
# Example in vhs_full_pipeline.sh:
CMD="$CMD --dry-run"
```

### Verbose Logging

Enable detailed logging for debugging:

```bash
# In any script, set:
VERBOSE="true"
```

### Keep Temporary Files

Preserve intermediate files for inspection:

```bash
# In any script, set:
KEEP_TEMP="true"
```

### Custom Timestamps for Comparison

Test specific scenes in your video:

```bash
./comparison_testing.sh video.mp4 --start 30 --duration 10
./comparison_testing.sh video.mp4 --multi-clip --timestamps "30,90,150"
```

### Parallel Processing

Process multiple videos simultaneously:

```bash
# Edit youtube_batch.sh and set:
PARALLEL_PROCESSING="4"  # Process 4 videos at once
```

---

## Script Reference

### Command-Line Arguments

Most scripts support command-line overrides:

**vhs_full_pipeline.sh:**
```bash
./vhs_full_pipeline.sh input.mp4 output.mp4
```

**youtube_batch.sh:**
```bash
./youtube_batch.sh URL_OR_FILE
```

**audio_upmix_workflow.sh:**
```bash
./audio_upmix_workflow.sh input.mp4 output.mp4
```

**comparison_testing.sh:**
```bash
./comparison_testing.sh INPUT [OPTIONS]

Options:
  --start SECONDS         Start time for test clip
  --duration SECONDS      Clip duration
  --presets LIST          Comma-separated presets
  -r, --resolution RES    Target resolution
  --multi-clip            Extract multiple clips
  --no-grid               Skip comparison grid
  -o, --output DIR        Output directory
  -v, --verbose           Enable verbose logging
  -h, --help              Show help message
```

---

## Best Practices

1. **Always test first** - Use comparison_testing.sh before processing long videos
2. **Start with defaults** - Default settings work well for most content
3. **Adjust incrementally** - Change one setting at a time to see effects
4. **Keep originals** - Never delete source files until you verify output
5. **Use appropriate presets** - Match preset to source type (VHS, DVD, etc.)
6. **Monitor resources** - Check CPU/GPU usage and adjust parallel processing
7. **Read the logs** - Enable verbose mode to understand processing steps
8. **Document your settings** - Keep notes on what works for different content types

---

## Getting Help

**Documentation:**
- Main README: `../README.md`
- CLI Documentation: `../vhs_upscaler/cli/`
- Best Practices: `../BEST_PRACTICES.md`

**Support:**
- GitHub Issues: https://github.com/parthalon025/terminalai/issues
- Verbose logs: Add `VERBOSE="true"` to any script

**Contributing:**
- Share your custom scripts
- Report bugs or improvements
- Submit pull requests

---

## License

These example scripts are part of TerminalAI and are released under the MIT License.

See `../LICENSE` for details.
