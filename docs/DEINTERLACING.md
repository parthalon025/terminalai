# Deinterlacing Guide

Complete guide to deinterlacing in VHS Upscaler, covering FFmpeg filters and VapourSynth QTGMC.

## Table of Contents

1. [Overview](#overview)
2. [Deinterlacing Engines](#deinterlacing-engines)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Preset Configuration](#preset-configuration)
6. [Field Order Detection](#field-order-detection)
7. [Quality Comparison](#quality-comparison)
8. [Performance Considerations](#performance-considerations)
9. [Troubleshooting](#troubleshooting)

## Overview

Interlaced video (common in VHS, broadcast, and older cameras) stores each frame as two fields (odd and even scan lines). Deinterlacing reconstructs progressive frames for modern displays.

**Why deinterlace?**
- Removes "combing" artifacts on motion
- Enables proper upscaling (AI models expect progressive input)
- Improves visual quality on progressive displays

**VHS Upscaler supports 4 engines:**
1. **yadif** - FFmpeg built-in (fast, reliable baseline)
2. **bwdif** - FFmpeg built-in (better motion handling)
3. **w3fdif** - FFmpeg built-in (better detail preservation)
4. **qtgmc** - VapourSynth (best quality, requires installation)

## Deinterlacing Engines

### yadif (Yet Another Deinterlacing Filter)

**Pros:**
- Always available with FFmpeg
- Fast processing (~5-10x realtime)
- Good quality for most content
- Low memory usage

**Cons:**
- Basic motion compensation
- Can show artifacts on fast motion
- Less detail preservation than advanced methods

**Best for:**
- Quick previews
- Batch processing
- Non-critical content
- When QTGMC not available

**FFmpeg filter string:** `yadif=1:-1` (bob deinterlacing, auto field order)

### bwdif (Bob Weaver Deinterlacing Filter)

**Pros:**
- Better motion compensation than yadif
- Similar speed to yadif
- Cleaner edges
- Included with FFmpeg

**Cons:**
- Still not as good as QTGMC
- May introduce slight softness

**Best for:**
- DVD sources
- Broadcast content
- General purpose deinterlacing
- When speed is important

**FFmpeg filter string:** `bwdif=1:-1` (bob deinterlacing, auto field order)

### w3fdif (Weston 3 Field Deinterlacing Filter)

**Pros:**
- Excellent detail preservation
- Good for static scenes
- Included with FFmpeg

**Cons:**
- Less sophisticated motion handling
- Can show artifacts on complex motion

**Best for:**
- Content with fine details
- Mostly static scenes
- Animation

**FFmpeg filter string:** `w3fdif=1:tff` (complex filter, top field first)

### qtgmc (Quality Time-based Motion Compensation)

**Pros:**
- Best quality available
- Sophisticated motion analysis
- Minimal artifacts
- Excellent temporal noise reduction
- Industry standard for archival work

**Cons:**
- Requires VapourSynth + havsfunc
- Much slower (~0.2-2x realtime depending on preset)
- Higher memory usage
- More complex setup

**Best for:**
- VHS restoration projects
- High-value archival content
- Clean VHS sources
- When quality is priority over speed

**QTGMC Presets:**
- `Draft`: ~5-10x realtime - Fast preview
- `Medium`: ~1-2x realtime - **Recommended default**
- `Slow`: ~0.5-1x realtime - High quality
- `Very Slow`: ~0.2-0.5x realtime - Very high quality
- `Placebo`: ~0.1-0.2x realtime - Maximum quality (diminishing returns)

## Installation

### FFmpeg Filters (yadif, bwdif, w3fdif)

These are built into FFmpeg. If you have FFmpeg installed, you have these filters.

```bash
# Verify FFmpeg installation
ffmpeg -version

# List available filters
ffmpeg -filters | grep deinterlace
```

### VapourSynth QTGMC

#### Windows

1. **Install VapourSynth**
   ```
   Download from: https://github.com/vapoursynth/vapoursynth/releases
   Run installer (includes Python bindings and vspipe)
   ```

2. **Install havsfunc**
   ```bash
   pip install havsfunc
   ```

3. **Install source plugin (ffms2 recommended)**
   ```
   Download: https://github.com/FFMS/ffms2/releases
   Extract ffms2.dll to: C:\Program Files\VapourSynth\plugins\
   ```

4. **Verify installation**
   ```bash
   python vhs_upscaler/test_deinterlace.py --check-setup
   ```

#### Linux (Ubuntu/Debian)

```bash
# Install VapourSynth
sudo apt update
sudo apt install vapoursynth python3-vapoursynth ffms2

# Install havsfunc
pip install havsfunc

# Verify
python vhs_upscaler/test_deinterlace.py --check-setup
```

#### Linux (Arch)

```bash
# Install from official repos
sudo pacman -S vapoursynth python-vapoursynth ffms2

# Install havsfunc
pip install havsfunc
```

#### macOS

```bash
# Using Homebrew
brew install vapoursynth ffms2

# Install havsfunc
pip install havsfunc
```

## Usage

### Python API

```python
from pathlib import Path
from vhs_upscaler.deinterlace import DeinterlaceProcessor, DeinterlaceEngine

# Create processor with desired engine
processor = DeinterlaceProcessor(engine=DeinterlaceEngine.QTGMC)

# Deinterlace video
processor.deinterlace(
    input_path=Path("interlaced_vhs.mp4"),
    output_path=Path("progressive_vhs.mp4"),
    preset="medium",      # QTGMC preset (ignored for FFmpeg filters)
    tff=True,            # Top field first
    progress_callback=lambda p: print(f"Progress: {p:.1f}%")
)

# Check capabilities
caps = processor.get_capabilities()
print(f"Available engines: {caps['available_engines']}")
```

### Command Line (Test Script)

```bash
# Check setup
python vhs_upscaler/test_deinterlace.py --check-setup

# Test specific engine
python vhs_upscaler/test_deinterlace.py --engine qtgmc -i input.mp4 -o output.mp4 --preset slow

# Compare all engines
python vhs_upscaler/test_deinterlace.py --compare-all input.mp4 output_dir/
```

### Standalone VapourSynth Script

For manual control or batch processing:

```bash
# 1. Edit the template
cp vhs_upscaler/vapoursynth_scripts/qtgmc_deinterlace.vpy my_script.vpy
# Edit INPUT_VIDEO_PATH, FIELD_ORDER, QTGMC_PRESET in my_script.vpy

# 2. Process with vspipe
vspipe --y4m my_script.vpy - | ffmpeg -i pipe: -c:v libx264 -crf 18 output.mp4

# 3. Or process specific frame range
vspipe --y4m --start 100 --end 200 my_script.vpy - | ffmpeg -i pipe: output.mp4
```

## Preset Configuration

The `presets.py` module now includes deinterlacing algorithm selection:

```python
PRESETS = {
    "vhs_clean": {
        "deinterlace_algorithm": "qtgmc",  # Use QTGMC for best quality
        "qtgmc_preset": "medium",          # Balanced quality/speed
        # ... other settings
    },
    "vhs_standard": {
        "deinterlace_algorithm": "bwdif",  # Good balance
        "qtgmc_preset": None,              # Not using QTGMC
        # ... other settings
    },
    "dvd_interlaced": {
        "deinterlace_algorithm": "bwdif",  # Fast, good for DVD
        "qtgmc_preset": None,
        # ... other settings
    },
}
```

**Preset Recommendations:**

| Source Type | Recommended Engine | QTGMC Preset | Reasoning |
|-------------|-------------------|--------------|-----------|
| VHS Heavy | qtgmc | slow | Best restoration for degraded sources |
| VHS Clean | qtgmc | medium | Balance quality/speed for good VHS |
| VHS Standard | bwdif | - | Fast processing for typical VHS |
| DVD Interlaced | bwdif | - | DVD already clean, don't need QTGMC |
| Broadcast 1080i | bwdif | - | HD content, yadif/bwdif sufficient |
| Progressive | None | - | No deinterlacing needed |

## Field Order Detection

### Automatic Detection with ffprobe

```bash
# Check field order
ffprobe -v quiet -select_streams v:0 -show_entries stream=field_order -of csv=p=0 input.mp4
```

**Output meanings:**
- `progressive` - No interlacing
- `tt` / `top` - Top field first (TFF)
- `bb` / `bottom` - Bottom field first (BFF)
- `unknown` - Can't determine (assume TFF for NTSC, BFF for PAL)

### Common Field Orders

| Format | Field Order | TFF Flag |
|--------|-------------|----------|
| NTSC VHS | TFF | True |
| PAL VHS | BFF | False |
| NTSC DVD | TFF | True |
| PAL DVD | BFF | False |
| HD 1080i (USA) | TFF | True |
| HD 1080i (Europe) | BFF | False |

### Visual Field Order Detection

If ffprobe returns "unknown", examine a frame with motion:

1. **Extract frame with motion:**
   ```bash
   ffmpeg -i input.mp4 -vf "select=gte(n\,100)" -vframes 1 frame.png
   ```

2. **Look for combing pattern:**
   - If combing is more visible on top edge = **TFF**
   - If combing is more visible on bottom edge = **BFF**

3. **Try both and compare:**
   ```bash
   # Test TFF
   python test_deinterlace.py --engine qtgmc -i input.mp4 -o test_tff.mp4

   # Test BFF
   python test_deinterlace.py --engine qtgmc -i input.mp4 -o test_bff.mp4 --bff

   # Compare - correct one will have less combing
   ```

## Quality Comparison

### Visual Quality Ranking

1. **QTGMC (Slow/Very Slow)** - Best overall, cleanest motion
2. **QTGMC (Medium)** - Excellent quality, reasonable speed
3. **QTGMC (Draft)** - Good quality, fast
4. **bwdif** - Good quality, very fast
5. **w3fdif** - Good for static scenes, fast
6. **yadif** - Baseline quality, very fast

### Speed Comparison (Rough Estimates)

| Engine | Processing Speed | Relative Speed |
|--------|-----------------|----------------|
| yadif | ~10x realtime | 1.0x (baseline) |
| bwdif | ~8x realtime | 0.8x |
| w3fdif | ~8x realtime | 0.8x |
| QTGMC Draft | ~5x realtime | 0.5x |
| QTGMC Medium | ~1-2x realtime | 0.1-0.2x |
| QTGMC Slow | ~0.5-1x realtime | 0.05-0.1x |
| QTGMC Very Slow | ~0.2-0.5x realtime | 0.02-0.05x |

*Speeds vary based on resolution, hardware, and content complexity*

### When to Use Each Engine

**Use yadif when:**
- Processing hundreds of videos
- Quick previews needed
- Content is not critical
- VapourSynth not available

**Use bwdif when:**
- DVD or broadcast content
- Balance of quality and speed needed
- Batch processing moderate amounts
- VapourSynth not available

**Use w3fdif when:**
- Lots of fine detail (text, patterns)
- Mostly static scenes
- Animation or graphics

**Use QTGMC when:**
- Archival/restoration work
- High-value VHS content
- Clean VHS sources
- Time is not critical
- Best possible quality needed

## Performance Considerations

### QTGMC Optimization

1. **Test with Draft preset first**
   - Verify settings before committing to slow processing
   - Draft is ~5-10x faster than Slow preset

2. **Process short clips for testing**
   - Extract 10-30 second samples
   - Test different presets and settings
   ```bash
   ffmpeg -i input.mp4 -ss 60 -t 30 -c copy sample.mp4
   ```

3. **Use hardware encoding**
   - VapourSynth outputs raw YUV, encoding is separate
   - Use NVENC or QSV for faster encoding
   ```bash
   vspipe --y4m script.vpy - | ffmpeg -i pipe: -c:v h264_nvenc -preset p4 output.mp4
   ```

4. **Adjust VapourSynth threads**
   - Auto-detect usually works well
   - Manual control in .vpy script:
   ```python
   core.num_threads = 8  # Set to your CPU core count
   ```

5. **Monitor memory usage**
   - QTGMC is memory-intensive
   - Higher presets need more RAM
   - Close other applications during processing

### FFmpeg Filter Optimization

1. **Use hardware acceleration for encoding**
   ```python
   # In DeinterlaceProcessor, encoding uses libx264 by default
   # Modify to use NVENC for faster encoding:
   cmd.extend(["-c:v", "h264_nvenc", "-preset", "p4"])
   ```

2. **Process in parallel**
   - FFmpeg filters are single-threaded per video
   - Process multiple videos in parallel:
   ```bash
   parallel -j 4 python test_deinterlace.py --engine bwdif -i {} -o output/{/} ::: input/*.mp4
   ```

## Troubleshooting

### VapourSynth Import Errors

**Error:** `ImportError: No module named vapoursynth`

**Solutions:**
1. Install VapourSynth with Python bindings
2. Make sure you're using the correct Python version (same as VapourSynth)
3. Check PYTHONPATH includes VapourSynth

```bash
# Test VapourSynth import
python -c "import vapoursynth as vs; print(vs.core.version())"
```

### havsfunc Not Found

**Error:** `ImportError: No module named havsfunc`

**Solution:**
```bash
pip install havsfunc

# Or install from GitHub for latest version
pip install git+https://github.com/HomeOfVapourSynthEvolution/havsfunc.git
```

### No Source Filter Available

**Error:** `AttributeError: 'Core' object has no attribute 'ffms2'`

**Solution:**
Install a source plugin (ffms2, lsmas, or bestsource)

**Windows:**
1. Download ffms2: https://github.com/FFMS/ffms2/releases
2. Extract ffms2.dll to VapourSynth plugins folder
3. Default location: `C:\Program Files\VapourSynth\plugins\`

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install ffms2

# Arch
sudo pacman -S ffms2
```

### vspipe Not Found

**Error:** `FileNotFoundError: vspipe not found`

**Solution:**
- Windows: vspipe.exe should be in VapourSynth installation (add to PATH)
- Linux: Install vapoursynth-tools package
  ```bash
  sudo apt install vapoursynth-tools
  ```

### Wrong Field Order / Still Seeing Combing

**Problem:** Output still shows combing artifacts

**Solutions:**
1. Verify field order with ffprobe
2. Try opposite field order (TFF vs BFF)
3. Check if source is telecined (3:2 pulldown)
4. Some sources are progressive mislabeled as interlaced

```bash
# Try both field orders
python test_deinterlace.py --engine qtgmc -i input.mp4 -o test_tff.mp4
python test_deinterlace.py --engine qtgmc -i input.mp4 -o test_bff.mp4 --bff

# Compare results
```

### Slow Processing

**Problem:** QTGMC is too slow

**Solutions:**
1. Use lower preset (Draft instead of Slow)
2. Use FFmpeg filter (bwdif) instead
3. Process in sections and concatenate
4. Reduce resolution before deinterlacing (not recommended for quality)

```bash
# Process in sections (faster on multi-core)
vspipe --y4m --start 0 --end 500 script.vpy - | ffmpeg -i pipe: part1.mp4 &
vspipe --y4m --start 500 --end 1000 script.vpy - | ffmpeg -i pipe: part2.mp4 &
wait
ffmpeg -i "concat:part1.mp4|part2.mp4" -c copy output.mp4
```

### Memory Errors

**Problem:** Out of memory during QTGMC processing

**Solutions:**
1. Close other applications
2. Use lower preset (less memory intensive)
3. Process at lower resolution
4. Reduce FPSDivisor to 2 (output half framerate)
5. Add more RAM or use system with more memory

## Advanced Usage

### Custom VapourSynth Scripts

For maximum control, edit the VapourSynth template directly:

```python
# Copy template
cp vhs_upscaler/vapoursynth_scripts/qtgmc_deinterlace.vpy custom.vpy

# Edit custom.vpy to adjust:
# - SourceMatch (0-3)
# - Lossless (0-2)
# - Sharpness (0.0-1.0)
# - NoiseRestore (temporal noise reduction)
# - Plus many other QTGMC parameters
```

See QTGMC documentation: https://github.com/HomeOfVapourSynthEvolution/havsfunc

### Combining with Other Filters

VapourSynth scripts can combine multiple operations:

```python
# In .vpy script
clip = haf.QTGMC(clip, Preset="Medium", TFF=True)
clip = haf.SMDegrain(clip, tr=2)  # Temporal denoise
clip = core.std.Limiter(clip)      # Ensure legal range
clip = haf.FineDehalo(clip)        # Remove halos
```

### Batch Processing

Process multiple files with different settings:

```python
from pathlib import Path
from vhs_upscaler.deinterlace import DeinterlaceProcessor, DeinterlaceEngine

input_dir = Path("interlaced_videos/")
output_dir = Path("progressive_videos/")
output_dir.mkdir(exist_ok=True)

processor = DeinterlaceProcessor(engine=DeinterlaceEngine.QTGMC)

for video in input_dir.glob("*.mp4"):
    output = output_dir / f"{video.stem}_progressive.mp4"
    processor.deinterlace(video, output, preset="medium", tff=True)
    print(f"Completed: {video.name}")
```

## References

- **QTGMC**: https://github.com/HomeOfVapourSynthEvolution/havsfunc
- **VapourSynth**: http://www.vapoursynth.com/doc/
- **Doom9 QTGMC Guide**: https://forum.doom9.org/showthread.php?t=156028
- **FFmpeg Deinterlacing**: https://ffmpeg.org/ffmpeg-filters.html#deinterlace
- **Field Order Explained**: https://en.wikipedia.org/wiki/Interlaced_video
