# GFPGAN Face Restoration Guide

## Table of Contents

1. [Overview](#overview)
2. [What is GFPGAN?](#what-is-gfpgan)
3. [Installation](#installation)
4. [Usage Examples](#usage-examples)
5. [Strength Parameter Tuning](#strength-parameter-tuning)
6. [When to Use Face Restoration](#when-to-use-face-restoration)
7. [Model Management](#model-management)
8. [Technical Details](#technical-details)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Overview

**GFPGAN** (Generative Facial Prior GAN) is an AI model that restores severely degraded faces in images and videos. VHS Upscaler integrates GFPGAN to dramatically improve face quality in:

- **VHS talking head videos** (interviews, home videos)
- **Old webcam footage** (early YouTube, video calls)
- **Degraded analog video** (Betamax, Video8)
- **Low-resolution portraits** (digitized photos)

### Before/After Example

```
Original VHS Face → GFPGAN → Restored Face
  [Blurry, pixelated]       [Clear, detailed]
  Low resolution            Enhanced features
  Artifacts                 Smooth skin
  Poor definition           Sharp details
```

---

## What is GFPGAN?

### How It Works

GFPGAN uses **deep learning** to:

1. **Detect faces** in each video frame
2. **Analyze facial structure** (eyes, nose, mouth)
3. **Generate realistic details** using trained priors
4. **Blend restoration** with original background
5. **Preserve identity** while enhancing quality

### Key Features

- **Real face details**: Not just upscaling, but generating realistic features
- **Identity preservation**: Maintains the person's appearance
- **Background preservation**: Only faces are modified
- **Batch processing**: Handles entire videos frame-by-frame

### Limitations

- **Processing time**: Slower than standard upscaling
- **VRAM requirements**: Needs GPU (4GB+ recommended)
- **Face detection**: Only works when faces are visible
- **Not perfect**: May introduce artifacts on extremely degraded sources

---

## Installation

### Step 1: Install Dependencies

GFPGAN requires Python packages and PyTorch:

```bash
# Install GFPGAN and dependencies
pip install gfpgan basicsr opencv-python

# Install PyTorch (choose your platform)
# CPU-only:
pip install torch torchvision

# CUDA 11.8 (NVIDIA GPU):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1 (NVIDIA GPU):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Step 2: Download GFPGAN Model

The GFPGAN model file (~332 MB) is required:

**Option A: Automatic download via VHS Upscaler:**
```bash
vhs-upscale --download-gfpgan-model
```

**Option B: Manual download:**
1. Download from: https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth
2. Save to: `models/gfpgan/GFPGANv1.3.pth`

### Step 3: Verify Installation

Check if GFPGAN is ready:

```bash
python -m vhs_upscaler.face_restoration --check
```

**Expected output:**
```
==========================================================
  GFPGAN Face Restoration Installation
==========================================================

Dependencies:
  [OK] gfpgan
  [OK] basicsr
  [OK] opencv
  [OK] torch

Model:
  [OK] models/gfpgan/GFPGANv1.3.pth
       Size: 332.04 MB

[OK] GFPGAN is ready to use!
==========================================================
```

---

## Usage Examples

### Example 1: Basic Face Restoration

Restore faces in VHS talking head video:

```bash
vhs-upscale upscale interview_1990.mp4 -o restored.mp4 \
  -p vhs_standard \
  --face-restore \
  --face-restore-strength 0.5
```

**Result**: Faces enhanced while preserving original background.

---

### Example 2: Strong Restoration

Maximum face enhancement for heavily degraded VHS:

```bash
vhs-upscale upscale old_vhs_interview.mp4 -o enhanced.mp4 \
  -p vhs_heavy \
  --face-restore \
  --face-restore-strength 0.8 \
  --face-restore-upscale 2
```

**Use case**: Very blurry or pixelated faces.

---

### Example 3: Subtle Enhancement

Light touch for already decent quality:

```bash
vhs-upscale upscale dvd_interview.mp4 -o output.mp4 \
  -p dvd_progressive \
  --face-restore \
  --face-restore-strength 0.3
```

**Use case**: DVD-quality video that just needs slight face improvement.

---

### Example 4: Combined with LUT

Face restoration + color grading:

```bash
vhs-upscale upscale family_video.mp4 -o restored.mp4 \
  -p vhs_standard \
  --lut luts/warm_vintage.cube \
  --lut-strength 0.7 \
  --face-restore \
  --face-restore-strength 0.6
```

**Result**: Professional color grade + enhanced faces.

---

### Example 5: 4K Output with Face Restoration

Upscale to 4K with face enhancement:

```bash
vhs-upscale upscale interview.mp4 -o 4k_restored.mp4 \
  -r 2160 \
  --face-restore \
  --face-restore-strength 0.5 \
  --face-restore-upscale 4 \
  --encoder hevc_nvenc
```

**Use case**: Maximum quality for archival or presentation.

---

### Example 6: Auto-Detection

Let VHS Upscaler detect talking heads and auto-enable face restoration:

```bash
vhs-upscale upscale video.mp4 -o output.mp4 --auto-detect
```

If the video analyzer detects `ContentType.TALKING_HEAD`, face restoration will be automatically enabled with optimal settings.

---

### Example 7: Batch Processing

Restore faces in entire folder:

```bash
vhs-upscale batch ./old_interviews/ ./restored_interviews/ \
  -p vhs_standard \
  --face-restore \
  --face-restore-strength 0.6
```

**Result**: All videos processed with consistent face restoration.

---

## Strength Parameter Tuning

The `--face-restore-strength` parameter controls restoration intensity.

### Strength Scale

| Value | Effect | Recommended For |
|-------|--------|-----------------|
| 0.0 | No restoration (original) | Testing |
| 0.2-0.3 | Very subtle enhancement | HD/DVD sources |
| 0.4-0.6 | Balanced restoration | Standard VHS |
| 0.7-0.8 | Strong enhancement | Degraded VHS |
| 0.9-1.0 | Maximum restoration | Extremely poor quality |

### Visual Guide

**Strength 0.3 (Subtle):**
- Slightly sharper features
- Minimal change to original
- Natural appearance
- Good for already decent quality

**Strength 0.5 (Balanced) - RECOMMENDED:**
- Noticeable improvement
- Enhanced facial details
- Preserved identity
- Best general-purpose setting

**Strength 0.8 (Strong):**
- Dramatic enhancement
- Very clear features
- May look slightly artificial
- Good for very poor sources

**Strength 1.0 (Maximum):**
- Complete AI reconstruction
- Maximum detail
- Risk of over-processing
- Use only for extremely degraded sources

### Finding the Right Strength

**Quick test workflow:**

1. Process 10-second clip at different strengths:
   ```bash
   # Subtle
   vhs-upscale preview video.mp4 -o test_03.mp4 --start 60 --duration 10 \
     --face-restore --face-restore-strength 0.3

   # Balanced
   vhs-upscale preview video.mp4 -o test_05.mp4 --start 60 --duration 10 \
     --face-restore --face-restore-strength 0.5

   # Strong
   vhs-upscale preview video.mp4 -o test_08.mp4 --start 60 --duration 10 \
     --face-restore --face-restore-strength 0.8
   ```

2. Compare results side-by-side

3. Choose strength that looks most natural

4. Apply to full video

---

## When to Use Face Restoration

### Recommended Use Cases

**GOOD candidates for face restoration:**

1. **VHS interviews/talking heads**
   - Person speaking directly to camera
   - Face is primary subject
   - Degraded analog quality

2. **Home video portraits**
   - Family members on camera
   - Birthday parties, celebrations
   - Close-ups of people

3. **Old webcam footage**
   - Early YouTube videos (2005-2010)
   - Video calls/conferences
   - Low-resolution captures

4. **Digitized photos in video**
   - Slideshows of old photos
   - Scanned portraits
   - Photo montages

### When NOT to Use

**AVOID face restoration for:**

1. **Action/sports videos**
   - Faces too small/far away
   - Motion blur dominates
   - Not worth processing time

2. **Landscapes/scenery**
   - No faces present
   - Wastes processing time
   - Use standard upscaling

3. **Already HD content**
   - Modern digital video
   - Professional production
   - May introduce artifacts

4. **Extreme close-ups**
   - Faces already detailed
   - May over-process
   - Use lower strength if needed

5. **Heavy motion blur**
   - Faces too blurry to restore
   - GFPGAN can't fix motion blur
   - Better to stabilize first

### Detection Tips

**How to tell if face restoration will help:**

- [ ] Faces are primary subjects (not background)
- [ ] Face size > 64x64 pixels in frame
- [ ] Faces are visible (not obscured)
- [ ] Video has analog artifacts (VHS noise, etc.)
- [ ] Processing time acceptable (slower than standard upscale)

If all checkboxes: **YES, use face restoration**

If only 1-2 checkboxes: **MAYBE, test on preview first**

If 0 checkboxes: **NO, skip face restoration**

---

## Model Management

### Available Models

VHS Upscaler supports two GFPGAN versions:

#### GFPGANv1.3 (Default, Recommended)

- **File**: `GFPGANv1.3.pth`
- **Size**: 332 MB
- **Quality**: Excellent
- **Speed**: Good
- **Best for**: General VHS restoration

#### GFPGANv1.4 (Experimental)

- **File**: `GFPGANv1.4.pth`
- **Size**: 348 MB
- **Quality**: Slightly better
- **Speed**: Slightly slower
- **Best for**: Testing, comparison

### Switching Models

Use v1.4 instead of default v1.3:

```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --face-restore \
  --gfpgan-version v1.4
```

### Model Location

Models are stored in:
```
models/
└── gfpgan/
    ├── GFPGANv1.3.pth  (default)
    └── GFPGANv1.4.pth  (optional)
```

### Custom Model Path

Use a custom model file:

```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --face-restore \
  --gfpgan-model /path/to/custom_model.pth
```

---

## Technical Details

### Processing Pipeline

Face restoration is integrated into the VHS Upscaler pipeline:

```
1. Deinterlace (if needed)
2. Denoise
3. LUT color grading (if enabled)
4. AI Upscale (Real-ESRGAN/Maxine)
5. → GFPGAN Face Restoration ←
6. Encode
```

**Why after upscaling?**
- GFPGAN works best on higher-resolution faces
- Upscaling provides cleaner input for face detection
- Better final quality

### Frame-by-Frame Processing

GFPGAN processes each frame:

1. **Extract** all frames from video
2. **Detect** faces in each frame
3. **Restore** detected faces
4. **Blend** restored faces with background
5. **Reassemble** frames to video
6. **Remux** audio from original

### Performance

**Processing time** (relative to real-time):

| Resolution | No Face Restore | With Face Restore |
|------------|-----------------|-------------------|
| 480p VHS | 2-3x slower | 10-15x slower |
| 720p DVD | 3-5x slower | 15-25x slower |
| 1080p HD | 5-10x slower | 25-40x slower |

**VRAM usage**:
- Minimum: 4 GB GPU
- Recommended: 6-8 GB GPU
- Optimal: 12+ GB GPU

### GPU Acceleration

GFPGAN automatically uses GPU if available:

```python
# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"
```

**If False**: CPU fallback (much slower)

**If True**: GPU acceleration enabled

---

## Troubleshooting

### Issue: "GFPGAN not installed"

**Symptom:**
```
GFPGAN not available, skipping face restoration
```

**Solution:**
```bash
pip install gfpgan basicsr opencv-python torch
```

---

### Issue: "Model not found"

**Symptom:**
```
GFPGAN model not found at models/gfpgan/GFPGANv1.3.pth
```

**Solution:**
```bash
vhs-upscale --download-gfpgan-model
```

Or manually download from:
https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth

---

### Issue: Out of Memory (CUDA)

**Symptom:**
```
RuntimeError: CUDA out of memory
```

**Solution:**

1. **Reduce upscale factor:**
   ```bash
   --face-restore-upscale 1  # Instead of 2 or 4
   ```

2. **Process smaller segments:**
   ```bash
   # Split video, process separately
   ffmpeg -i video.mp4 -t 300 part1.mp4
   vhs-upscale upscale part1.mp4 -o restored1.mp4 --face-restore
   ```

3. **Use CPU (slower):**
   ```bash
   export CUDA_VISIBLE_DEVICES=""  # Force CPU
   vhs-upscale upscale video.mp4 -o output.mp4 --face-restore
   ```

---

### Issue: Faces look unnatural

**Symptom:**
Restored faces look fake or over-processed

**Solution:**

1. **Reduce strength:**
   ```bash
   --face-restore-strength 0.3  # Instead of 0.8
   ```

2. **Try different model:**
   ```bash
   --gfpgan-version v1.3  # Or v1.4
   ```

3. **Check source quality:**
   - If source is already HD, face restoration may not help
   - Use on VHS/degraded sources only

---

### Issue: No faces detected

**Symptom:**
Face restoration runs but no improvement visible

**Solution:**

1. **Check face size:**
   - Faces must be > 64x64 pixels
   - Zoom in or use higher resolution source

2. **Check visibility:**
   - Faces must be visible (not obscured)
   - Frontal or side views work best

3. **Test with known good clip:**
   ```bash
   vhs-upscale preview video.mp4 -o test.mp4 --start 60 --duration 10 \
     --face-restore --face-restore-strength 1.0
   ```

---

### Issue: Very slow processing

**Symptom:**
Processing takes hours for short video

**Solution:**

1. **Expected behavior:**
   - Face restoration is 10-20x slower than standard upscaling
   - GPU significantly faster than CPU

2. **Use GPU:**
   - Install CUDA-enabled PyTorch
   - Verify GPU: `nvidia-smi`

3. **Process preview first:**
   ```bash
   # Test on 30-second segment
   vhs-upscale preview video.mp4 -o test.mp4 --duration 30 --face-restore
   ```

4. **Consider batch overnight:**
   - Run long videos overnight
   - Use batch mode for multiple files

---

## Best Practices

### Pre-Processing Recommendations

**Before applying face restoration:**

1. **Analyze video first:**
   ```bash
   vhs-upscale analyze video.mp4 --recommend
   ```

2. **Test on preview:**
   ```bash
   vhs-upscale preview video.mp4 -o test.mp4 --start 60 --duration 30 \
     --face-restore --face-restore-strength 0.5
   ```

3. **Compare results:**
   - Watch preview
   - Adjust strength if needed
   - Process full video with optimal settings

### Optimal Settings by Source

**VHS talking head (degraded):**
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  -p vhs_heavy \
  --lut luts/vhs_restore.cube --lut-strength 0.7 \
  --face-restore --face-restore-strength 0.7 \
  --encoder hevc_nvenc
```

**DVD interview (good quality):**
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  -p dvd_progressive \
  --face-restore --face-restore-strength 0.4 \
  --encoder hevc_nvenc
```

**YouTube old webcam (2005-2010):**
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  -p youtube_old \
  --face-restore --face-restore-strength 0.6
```

### Quality Control

**Before final render:**

- [ ] Preview looks natural (not over-processed)
- [ ] Faces are sharper than original
- [ ] Background is preserved
- [ ] No artifacts introduced
- [ ] Processing time acceptable
- [ ] Audio syncs properly

### Archival Recommendations

For long-term archival of restored videos:

```bash
vhs-upscale upscale original.mp4 -o archived.mp4 \
  -r 1080 \
  --face-restore --face-restore-strength 0.5 \
  --encoder libx265 \
  --crf 18 \
  --audio-format flac  # Lossless audio
```

---

## Advanced Topics

### Face Restoration with Demucs Audio

Professional restoration with AI audio upmix:

```bash
vhs-upscale upscale interview_vhs.mp4 -o professional.mp4 \
  -p vhs_standard \
  --face-restore --face-restore-strength 0.6 \
  --audio-enhance voice \
  --audio-upmix demucs \
  --audio-layout 5.1
```

---

### Custom GFPGAN Training

For advanced users who want to train custom GFPGAN models:

**See**: https://github.com/TencentARC/GFPGAN#train

**Workflow:**
1. Collect degraded/restored face pairs
2. Train GFPGAN model
3. Export .pth model file
4. Use with VHS Upscaler:
   ```bash
   --gfpgan-model /path/to/custom_model.pth
   ```

---

### Combining with Real-ESRGAN

Face restoration works seamlessly with Real-ESRGAN upscaling:

```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --engine realesrgan \
  --realesrgan-model realesrgan-x4plus \
  --face-restore --face-restore-strength 0.5
```

**Result**: Real-ESRGAN upscales entire frame, GFPGAN enhances faces specifically.

---

## Comparison: With vs. Without

### Visual Quality

| Feature | Without GFPGAN | With GFPGAN |
|---------|----------------|-------------|
| Face sharpness | Blurry | Sharp |
| Eye detail | Pixelated | Clear |
| Skin texture | Blocky | Smooth |
| Identity | Preserved | Preserved |
| Background | Upscaled | Upscaled (unchanged) |

### Processing Time

- **Without**: ~2-5 minutes for 10-minute video
- **With**: ~20-40 minutes for 10-minute video

**Worth it?** YES for talking head content where faces are important.

---

## Summary

GFPGAN face restoration provides:

- **Dramatic improvement** for degraded faces
- **Identity preservation** (looks like the original person)
- **Easy integration** with VHS Upscaler
- **Flexible strength control** (0.0 to 1.0)

**Quick start:**
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --face-restore \
  --face-restore-strength 0.5
```

For more help, see:
- **VHS Upscaler README**: [README.md](../README.md)
- **LUT Guide**: [LUT_GUIDE.md](LUT_GUIDE.md)
- **Audio Enhancement**: [AUDIO_GUIDE.md](AUDIO_GUIDE.md)

---

**Generated by VHS Upscaler Documentation**
Version: 1.5.0 | Last Updated: 2025-12-18
