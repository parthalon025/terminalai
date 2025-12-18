# Dry-Run Mode

## Overview

Dry-run mode provides complete pipeline visualization without executing any processing. It shows exactly what will happen during processing, including all commands, filters, and configuration settings. This is essential for validating settings before committing to full processing.

## Features

- **Complete Pipeline Visualization**: See all processing stages and their configuration
- **FFmpeg Command Preview**: View estimated FFmpeg commands that would be executed
- **Configuration Validation**: Automatic detection of missing dependencies and invalid settings
- **Zero Risk**: No files are modified, no processing occurs
- **Performance Estimation**: Get insight into processing requirements

## Usage

### Modern CLI

```bash
# Basic dry-run
vhs-upscale upscale video.mp4 -o output.mp4 --dry-run

# Dry-run with specific settings
vhs-upscale upscale video.mp4 -o output.mp4 \
    -p vhs \
    -r 2160 \
    --deinterlace-algorithm qtgmc \
    --qtgmc-preset medium \
    --dry-run

# Test LUT and face restoration settings
vhs-upscale upscale video.mp4 -o output.mp4 \
    --lut luts/vhs_restore.cube \
    --face-restore \
    --dry-run
```

### Legacy CLI

```bash
# Basic dry-run
vhs-upscale -i video.mp4 -o output.mp4 --dry-run

# With preset and settings
vhs-upscale -i video.mp4 -o output.mp4 \
    -p vhs_heavy \
    -r 1080 \
    --deinterlace-algorithm bwdif \
    --dry-run
```

## Output Format

### Example Dry-Run Output

```
================================================================================
DRY-RUN MODE: Processing Pipeline Visualization
================================================================================

Input/Output Configuration:
  Input File: old_vhs_tape.mp4
  Output File: old_vhs_tape_1080p.mp4
  Input Resolution: 720x480
  Input Duration: 3600.0 seconds
  Input Codec: mpeg2video
  Input Bitrate: 5.2 Mbps
  Target Resolution: 1080p

Video Analysis:
  Interlaced: Yes
  Frame Rate: 29.97 fps
  Aspect Ratio: 1.50:1

Stage 1: Preprocessing
--------------------------------------------------------------------------------
  [1.1] Deinterlacing: QTGMC
        Engine: VapourSynth QTGMC
        Quality Preset: medium
        Processing: Separate pass (highest quality)
  [1.2] Denoising: ENABLED
        Algorithm: hqdn3d
        Strength: Luma=4.0, Chroma=3.0, Temporal Luma=6.0, Temporal Chroma=4.5
  [1.3] Color Grading (LUT): ENABLED
        LUT File: luts/vhs_restore.cube
        Strength: 70%
  [1.4] Audio Extraction: ENABLED
        Format: AAC

Stage 2: Upscaling
--------------------------------------------------------------------------------
  [2.1] Upscaling Engine: REALESRGAN
        Model: realesrgan-x4plus
        Target Resolution: 1080p
        Processing: GPU accelerated
  [2.2] Face Restoration: ENABLED
        Model: GFPGAN v1.3
        Strength: 50%
        Processing: Separate pass (blended with upscaled video)

Stage 3: Encoding & Finalization
--------------------------------------------------------------------------------
  [3.1] Sharpening: DISABLED
  [3.2] Video Encoding:
        Codec: libx264
        Quality: CRF 18
        Preset: medium
        HDR Mode: SDR (Standard Dynamic Range)
  [3.3] Audio Processing:
        Format: aac
        Bitrate: 192k
        Normalization: ENABLED

================================================================================
FFmpeg Commands (Estimated)
================================================================================

[Preprocessing FFmpeg Command]
  ffmpeg -i old_vhs_tape.mp4 -vf hqdn3d=4.0:3.0:6.0:4.5,lut3d=file='luts/vhs_restore.cube' -an prepped_video.mp4

[Real-ESRGAN Upscaling Command]
  realesrgan-ncnn-vulkan -i prepped_video.mp4 -o upscaled_video.mp4 -n realesrgan-x4plus

[Final Encoding Command]
  ffmpeg -i upscaled_video.mp4 -i audio.aac -c:v libx264 -crf 18 -preset medium -c:a copy -y output.mp4

================================================================================
Configuration Warnings
================================================================================

  [WARNING] Very low CRF (18) will produce very large files

================================================================================
This is a DRY-RUN - no files will be modified
Remove --dry-run flag to execute processing
================================================================================
```

## Use Cases

### 1. Validate Settings Before Processing

Test configuration before committing to hours of processing:

```bash
# Test VHS restoration pipeline
vhs-upscale upscale old_tape.mp4 -o restored.mp4 \
    -p vhs_heavy \
    --deinterlace-algorithm qtgmc \
    --qtgmc-preset slow \
    --dry-run
```

### 2. Compare Different Configurations

Quickly test multiple configurations to find optimal settings:

```bash
# Test with QTGMC
vhs-upscale upscale video.mp4 -o out.mp4 \
    --deinterlace-algorithm qtgmc \
    --dry-run > qtgmc_pipeline.txt

# Test with BWDIF
vhs-upscale upscale video.mp4 -o out.mp4 \
    --deinterlace-algorithm bwdif \
    --dry-run > bwdif_pipeline.txt

# Compare
diff qtgmc_pipeline.txt bwdif_pipeline.txt
```

### 3. Troubleshoot Configuration Issues

Identify missing dependencies or configuration problems:

```bash
# Will show warnings if QTGMC not available
vhs-upscale upscale video.mp4 -o output.mp4 \
    --deinterlace-algorithm qtgmc \
    --dry-run
```

### 4. Generate Documentation

Create processing documentation for archival projects:

```bash
# Save pipeline for documentation
vhs-upscale upscale source.mp4 -o output.mp4 \
    -p vhs_archive \
    --dry-run > processing_pipeline.txt
```

### 5. Estimate Processing Requirements

Understand what processing will occur without execution:

```bash
# Check if face restoration will be used
vhs-upscale upscale talking_head.mp4 -o output.mp4 \
    --auto-detect \
    --dry-run
```

## Pipeline Stages Explained

### Stage 1: Preprocessing

**Deinterlacing**: Converts interlaced video to progressive
- **yadif**: Fast, good quality (FFmpeg)
- **bwdif**: Better motion compensation (FFmpeg)
- **w3fdif**: Better detail preservation (FFmpeg)
- **qtgmc**: Best quality, slowest (VapourSynth)

**Denoising**: Reduces video noise/grain
- **hqdn3d**: High-quality 3D denoising
- Strength: Separate for luma, chroma, and temporal

**Color Grading**: Applies LUT color correction
- Supports .cube and .3dl LUT files
- Adjustable strength (0.0-1.0)

**Audio Extraction**: Separates audio for parallel processing

### Stage 2: Upscaling

**Upscaling Engine**:
- **Real-ESRGAN**: AI upscaling (GPU required)
- **Maxine**: NVIDIA Video Super Resolution (RTX required)
- **FFmpeg**: Fallback scaling (CPU)

**Face Restoration** (optional):
- **GFPGAN**: AI face enhancement
- Blended with upscaled background
- Adjustable strength

### Stage 3: Encoding & Finalization

**Sharpening**: Optional unsharp mask filter

**Video Encoding**:
- Codec: libx264, libx265, h264_nvenc, hevc_nvenc
- Quality: CRF value (lower = higher quality)
- Preset: Speed vs compression trade-off
- HDR: SDR, HDR10, HDR10+, Dolby Vision

**Audio Processing**:
- Enhancement: noise reduction, clarity improvement
- Upmixing: stereo to surround
- Format: AAC, AC3, EAC3, DTS, FLAC
- Normalization: loudness equalization

## Validation Warnings

Dry-run mode automatically detects potential issues:

### Dependency Warnings

```
[WARNING] QTGMC requested but VapourSynth not installed - will fall back to yadif
[WARNING] Face restoration requested but GFPGAN not installed
[WARNING] Maxine engine selected but maxine_path not configured or invalid
[WARNING] LUT file not found: luts/custom.cube
```

### Configuration Warnings

```
[WARNING] Very low CRF (10) will produce very large files
[WARNING] High CRF (32) may produce noticeable quality loss
[WARNING] Very high resolution (4320p) requires significant processing time and disk space
```

## Integration with Other Features

### With Auto-Detect

Preview recommended settings before processing:

```bash
# Analyze, then show recommended pipeline
vhs-upscale upscale video.mp4 -o output.mp4 \
    --auto-detect \
    --dry-run
```

### With Preview Mode

Combine with preview for complete validation:

```bash
# 1. Check pipeline
vhs-upscale upscale video.mp4 -o output.mp4 \
    -p vhs \
    --dry-run

# 2. Generate preview with same settings
vhs-upscale preview video.mp4 -o preview.mp4 \
    -p vhs \
    --duration 10

# 3. If satisfied, run full processing
vhs-upscale upscale video.mp4 -o output.mp4 -p vhs
```

### With Batch Processing

Preview batch pipeline before processing hundreds of files:

```bash
# Check pipeline for first file
vhs-upscale upscale ./videos/first.mp4 -o test.mp4 \
    -p vhs_standard \
    --dry-run

# If satisfied, process all
vhs-upscale batch ./videos/ -o ./output/ -p vhs_standard
```

## Performance Considerations

Dry-run mode is extremely fast (< 1 second) because it:
- Does not process any video
- Only reads video metadata with ffprobe
- Performs basic configuration validation

This makes it ideal for:
- Quick configuration testing
- CI/CD pipeline validation
- Batch job preparation
- Training and documentation

## Troubleshooting

### Issue: Dry-run shows different settings than expected

**Cause**: Preset overrides command-line arguments

**Solution**: Check preset definition or use `--preset none` for manual control

```bash
# See what preset does
vhs-upscale upscale video.mp4 -o out.mp4 -p vhs --dry-run

# Override with manual settings
vhs-upscale upscale video.mp4 -o out.mp4 \
    --preset none \
    --deinterlace-algorithm bwdif \
    --dry-run
```

### Issue: Validation warnings appear

**Cause**: Missing dependencies or configuration issues

**Solution**: Install missing dependencies or adjust configuration

```bash
# If QTGMC warning appears
pip install vapoursynth vapoursynth-havsfunc

# If GFPGAN warning appears
pip install gfpgan basicsr facexlib
```

### Issue: Can't see FFmpeg commands

**Cause**: Commands may be wrapped for readability

**Solution**: Redirect output to file for full commands

```bash
vhs-upscale upscale video.mp4 -o out.mp4 --dry-run > pipeline.txt
cat pipeline.txt
```

## Best Practices

1. **Always Dry-Run First**: Test configuration before long processing jobs
2. **Save Pipeline Output**: Document processing for archival projects
3. **Check Warnings**: Resolve dependency issues before processing
4. **Compare Configurations**: Use diff to evaluate different settings
5. **Combine with Preview**: Use both dry-run (validate) and preview (test quality)

## References

- [FFmpeg Filters Documentation](https://ffmpeg.org/ffmpeg-filters.html)
- [Real-ESRGAN GitHub](https://github.com/xinntao/Real-ESRGAN)
- [GFPGAN GitHub](https://github.com/TencentARC/GFPGAN)
- [VapourSynth QTGMC](https://github.com/HomeOfVapourSynthEvolution/havsfunc)
