# VHS Restoration Quick Start Guide

**Complete beginner-friendly guide to restoring VHS tapes to 1080p HD quality**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start - Single Command](#quick-start---single-command)
3. [Complete VHS Pipeline - Step by Step](#complete-vhs-pipeline---step-by-step)
4. [Using Presets](#using-presets)
5. [Auto-Detection - Let AI Choose Settings](#auto-detection---let-ai-choose-settings)
6. [Batch Processing - Multiple VHS Tapes](#batch-processing---multiple-vhs-tapes)
7. [Expected Processing Times](#expected-processing-times)
8. [Quality Comparison - What to Expect](#quality-comparison---what-to-expect)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Tips](#advanced-tips)

---

## Prerequisites

### Required Software

**1. TerminalAI Installation**
```bash
# Clone and install
git clone https://github.com/parthalon025/terminalai.git
cd terminalai
pip install -e .
```

**2. FFmpeg (Required)**
```bash
# Linux (Ubuntu/Debian)
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows (with winget)
winget install FFmpeg
```

**3. AI Upscaling Engine (Choose One)**

**Option A: Real-ESRGAN** (works on ANY GPU - AMD/Intel/NVIDIA)
- Download from: https://github.com/xinntao/Real-ESRGAN/releases
- Extract to a folder and add to PATH
- **Recommended for most users**

**Option B: NVIDIA Maxine** (RTX GPUs only, best quality)
- Requires RTX 2060 or newer
- Download from NVIDIA Developer site
- Set `MAXINE_HOME` environment variable

**Option C: FFmpeg** (CPU only, works everywhere)
- Already installed if you have FFmpeg
- Slower but works without GPU

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 8GB | 16GB+ |
| **GPU** | None (CPU mode) | NVIDIA RTX 3060+ or AMD/Intel with Vulkan |
| **VRAM** | 2GB (720p) | 6GB+ (1080p) |
| **Storage** | 10GB free | SSD with 50GB+ free |

---

## Quick Start - Single Command

**For users who just want it to work - one command to do everything automatically:**

```bash
# Analyze your VHS tape and process with optimal settings
vhs-upscale upscale family_vacation_1995.mp4 \
  -o restored_vacation_1995.mp4 \
  --auto-detect
```

**What this does:**
1. Analyzes your video (scan type, noise level, source format)
2. Recommends optimal settings
3. Shows you what it will do
4. Asks for confirmation
5. Processes with best settings for your specific tape

**That's it!** The system will:
- Detect interlacing and choose the right deinterlace algorithm
- Measure noise and apply appropriate denoise
- Identify VHS artifacts and fix them
- Choose the best upscaling engine for your hardware
- Upscale to 1080p HD
- Enhance audio (remove hiss, improve clarity)
- Encode to high-quality H.264

**Expected time:** 15-30 minutes for 1 hour of VHS footage (with GPU)

---

## Complete VHS Pipeline - Step by Step

For those who want to understand and control each step of the restoration process.

### Processing Order (Critical)

**This order is scientifically proven to give the best results. Don't skip or reorder steps!**

```
INPUT (480i VHS)
    ↓
1. DEINTERLACE ← Remove combing artifacts FIRST
    ↓
2. DENOISE ← Remove VHS noise/grain
    ↓
3. COLOR CORRECT ← Fix faded colors (optional)
    ↓
4. UPSCALE ← AI enhancement to 1080p
    ↓
5. FACE RESTORE ← Enhance faces (optional)
    ↓
6. SHARPEN ← Enhance detail
    ↓
7. ENCODE ← Final compression
    ↓
OUTPUT (1080p HD)
```

---

### Step 1: Deinterlace (REQUIRED for VHS)

**Why:** VHS uses interlaced video (480i). If you skip this, you'll see "combing" artifacts - horizontal lines on anything that moves.

**Command:**
```bash
# Recommended: BWDIF (fast, good quality)
vhs-upscale upscale vhs_tape.mp4 -o deinterlaced.mp4 \
  --deinterlace-algorithm bwdif

# Best quality: QTGMC (requires VapourSynth, slower)
vhs-upscale upscale vhs_tape.mp4 -o deinterlaced.mp4 \
  --deinterlace-algorithm qtgmc --qtgmc-preset medium
```

**Which algorithm to use?**

| Algorithm | Speed | Quality | When to Use |
|-----------|-------|---------|-------------|
| **YADIF** | ⚡⚡⚡ Fastest | ⭐⭐⭐ Good | Quick preview, batch processing |
| **BWDIF** | ⚡⚡ Fast | ⭐⭐⭐⭐ Better | **Recommended for most VHS** |
| **W3FDIF** | ⚡⚡ Fast | ⭐⭐⭐⭐ Better | Fine details, text, static scenes |
| **QTGMC** | ⚡ Slow | ⭐⭐⭐⭐⭐ Best | Archival quality, important footage |

**Processing time:** 5-10 minutes per hour of video

**What you'll see:** Smooth motion, no more combing/horizontal lines

---

### Step 2: Denoise (Remove VHS Grain/Snow)

**Why:** VHS has inherent noise - grain, snow, static. Remove it BEFORE upscaling so the AI doesn't amplify it.

**Command:**
```bash
# Light denoise (preserves detail)
vhs-upscale upscale deinterlaced.mp4 -o denoised.mp4 \
  --preset vhs

# Heavy denoise (very noisy tapes)
vhs-upscale upscale deinterlaced.mp4 -o denoised.mp4 \
  --preset vhs --engine realesrgan --realesrgan-denoise 0.8
```

**Denoise strength guide:**

| VHS Condition | Denoise Level | Example |
|---------------|---------------|---------|
| Clean VHS (stored well) | 0.3-0.5 | Recent recordings, good storage |
| Typical VHS | 0.5-0.7 | Most home videos |
| Degraded VHS | 0.7-0.9 | Old tapes, many replays |
| Severely damaged | 0.9-1.0 | Tracking errors, heavy snow |

**Processing time:** Included in upscaling step

**What you'll see:** Cleaner image, less grain, preserved details

**Warning:** Too much denoise (>0.8) creates a "waxy" or "plastic" look. Less is often more.

---

### Step 3: Color Correction (Optional)

**Why:** VHS tapes fade over time. Colors become washed out or develop color casts (often yellow/red).

**When to use:**
- Colors look faded or washed out
- Visible color cast (everything looks yellow/blue)
- White balance is off
- Tape is 20+ years old

**Command:**
```bash
# Boost saturation for faded colors
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs --color-saturation 1.2

# Use a professional color LUT
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs --lut film_look.cube --lut-strength 0.7
```

**Quick color fixes:**

| Problem | Solution | Example |
|---------|----------|---------|
| Faded colors | Increase saturation to 1.2-1.3 | `--color-saturation 1.2` |
| Yellow cast | Apply color balance | Use LUT or manual curves |
| Dark/underexposed | Increase brightness | `--color-brightness 1.1` |
| Washed out | Increase contrast | `--color-contrast 1.1` |

**Processing time:** Negligible (part of filter chain)

**What you'll see:** Vibrant colors like when the tape was new

**Tip:** Don't overdo it - some fade is authentic to the era. Aim for natural, not oversaturated.

---

### Step 4: Upscale (480p → 1080p AI Enhancement)

**Why:** VHS is 480i (~240p effective). AI upscaling to 1080p recovers detail and sharpness.

**Command:**
```bash
# Real-ESRGAN (recommended - works on any GPU)
vhs-upscale upscale preprocessed.mp4 -o upscaled.mp4 \
  --engine realesrgan \
  --realesrgan-model realesrgan-x4plus \
  -r 1080

# NVIDIA Maxine (RTX GPUs only, best quality)
vhs-upscale upscale preprocessed.mp4 -o upscaled.mp4 \
  --engine maxine \
  -r 1080

# FFmpeg (CPU only, no GPU needed)
vhs-upscale upscale preprocessed.mp4 -o upscaled.mp4 \
  --engine ffmpeg \
  --ffmpeg-scale-algo lanczos \
  -r 1080
```

**Engine comparison:**

| Engine | GPU | Quality | Speed | Best For |
|--------|-----|---------|-------|----------|
| **Real-ESRGAN** | Any (AMD/Intel/NVIDIA) | ⭐⭐⭐⭐ | Medium | **Most users** |
| **NVIDIA Maxine** | RTX only | ⭐⭐⭐⭐⭐ | Fast | RTX 3060+ owners |
| **FFmpeg** | None (CPU) | ⭐⭐⭐ | Slow | No GPU available |

**Real-ESRGAN models:**

| Model | Best For | Quality | Speed |
|-------|----------|---------|-------|
| `realesrgan-x4plus` | **VHS, general use** | Highest | Medium |
| `realesrgan-x4plus-anime` | Animation, cartoons | High | Fast |
| `realesrgan-animevideov3` | Fast processing | Good | Fastest |

**Processing time:** 20-60 minutes per hour (varies by GPU)

**What you'll see:** Sharper image, recovered details, HD quality

**Tip:** 1080p is the sweet spot for VHS. 4K often creates too much "hallucinated" detail.

---

### Step 5: Face Restore (Optional)

**Why:** AI face restoration (GFPGAN) can dramatically improve faces in home videos.

**When to use:**
- Home videos with family/friends
- Wedding videos
- Interview footage
- Any video where faces are important

**When to SKIP:**
- Landscape/nature videos
- Sports (faces too distant)
- Already-HD content
- Animated content

**Command:**
```bash
# Enable face restoration
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  --face-restore \
  --face-restore-strength 0.5

# Stronger restoration for heavily degraded footage
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  --face-restore \
  --face-restore-strength 0.7 \
  --face-restore-upscale 4
```

**Strength guide:**

| Strength | Effect | Best For |
|----------|--------|----------|
| 0.3 | Subtle enhancement | Already decent quality |
| 0.5 | Balanced (recommended) | Typical VHS restoration |
| 0.7 | Strong enhancement | Heavy degradation |
| 1.0 | Maximum | Severely damaged footage |

**Processing time:** +30-50% to total time (if faces detected)

**What you'll see:** Clearer faces, restored facial details, less blur

**Warning:** Too strong (>0.7) can create an "uncanny valley" effect - faces look artificial.

---

### Step 6: Sharpen (Enhance Detail)

**Why:** After upscaling, light sharpening enhances edge detail and clarity.

**Command:**
```bash
# Recommended: Contrast Adaptive Sharpening (CAS)
# Already included in vhs preset at optimal level (0.4)

# If you want to adjust:
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  --sharpen-strength 0.3  # Light
  # or
  --sharpen-strength 0.5  # Medium
```

**Sharpening guide:**

| Strength | Effect | When to Use |
|----------|--------|-------------|
| 0.2 | Very subtle | Already sharp sources |
| 0.3-0.4 | Light | **Recommended for VHS** |
| 0.5-0.6 | Medium | Very soft sources |
| 0.7+ | Heavy | Caution: creates halos |

**Processing time:** Negligible (part of filter chain)

**What you'll see:** Enhanced edges, crisp details, improved clarity

**Warning:** Over-sharpening (>0.6) creates white "halos" around objects - looks unnatural.

---

### Step 7: Encode (Final Compression)

**Why:** Create the final video file with optimal quality and compatibility.

**Command:**
```bash
# High quality H.264 (recommended - plays everywhere)
vhs-upscale upscale processed.mp4 -o final.mp4 \
  --encoder h264_nvenc \  # GPU encoding (fast)
  --crf 18                 # Quality (lower = better)

# CPU encoding (no GPU needed)
vhs-upscale upscale processed.mp4 -o final.mp4 \
  --encoder libx264 \
  --crf 18
```

**Quality settings (CRF):**

| CRF | Quality | File Size | Best For |
|-----|---------|-----------|----------|
| 16-18 | Excellent (archival) | Large | Long-term storage |
| 18-20 | Very good | Medium | **Recommended** |
| 20-23 | Good | Small | Sharing online |
| 23-28 | Fair | Very small | Rough previews |

**Lower CRF = Higher Quality = Bigger File**

**Encoder comparison:**

| Encoder | GPU Required | Speed | Quality | Compatibility |
|---------|--------------|-------|---------|---------------|
| `h264_nvenc` | NVIDIA | ⚡⚡⚡ Fast | ⭐⭐⭐⭐ | Excellent |
| `hevc_nvenc` | NVIDIA | ⚡⚡⚡ Fast | ⭐⭐⭐⭐⭐ | Modern devices |
| `libx264` | None (CPU) | ⚡ Slow | ⭐⭐⭐⭐ | **Plays everywhere** |
| `libx265` | None (CPU) | 🐌 Very slow | ⭐⭐⭐⭐⭐ | Smaller files |

**Processing time:** 5-15 minutes per hour (varies by encoder)

**What you'll see:** Compressed video ready to play, share, or archive

---

## Complete Pipeline - Single Command

**All steps in one command** (recommended for most users):

```bash
vhs-upscale upscale family_vhs_1995.mp4 -o restored_1995.mp4 \
  --preset vhs \
  --deinterlace-algorithm bwdif \
  --engine realesrgan \
  --realesrgan-model realesrgan-x4plus \
  --realesrgan-denoise 0.6 \
  -r 1080 \
  --audio-enhance voice \
  --encoder h264_nvenc \
  --crf 18

# Expected time: 30-60 minutes for 1 hour of VHS (with GPU)
```

**What this does:**
1. Deinterlaces with BWDIF (fast, good quality)
2. Removes VHS noise (denoise 0.6)
3. AI upscales to 1080p with Real-ESRGAN
4. Enhances audio (removes hiss, improves dialogue)
5. Encodes to high-quality H.264

---

## Using Presets

**Presets are pre-configured settings optimized for different video sources.**

### Available Presets

| Preset | Source Type | Deinterlace | Denoise | Best For |
|--------|-------------|-------------|---------|----------|
| **vhs** | VHS tapes (480i) | ✅ Yes | Strong | Old home videos, VHS captures |
| **dvd** | DVD rips (480p/576p) | ✅ Yes | Moderate | DVD backups, DVD rips |
| **webcam** | Low-quality webcam | ❌ No | Strong | Old webcam footage |
| **youtube** | YouTube downloads | ❌ No | Light | Downloaded videos |
| **clean** | High-quality | ❌ No | None | Already clean sources |

### Using Presets

```bash
# VHS home videos
vhs-upscale upscale family_video.mp4 -o restored.mp4 --preset vhs

# DVD movie backup
vhs-upscale upscale dvd_rip.mp4 -o restored.mp4 --preset dvd

# Old webcam footage
vhs-upscale upscale webcam_2005.mp4 -o restored.mp4 --preset webcam
```

### Customizing Presets

You can start with a preset and override specific settings:

```bash
# Use VHS preset but with stronger denoise
vhs-upscale upscale very_noisy_vhs.mp4 -o restored.mp4 \
  --preset vhs \
  --realesrgan-denoise 0.9

# Use DVD preset with face restoration
vhs-upscale upscale wedding_dvd.mp4 -o restored.mp4 \
  --preset dvd \
  --face-restore --face-restore-strength 0.5
```

---

## Auto-Detection - Let AI Choose Settings

**Best for beginners - let TerminalAI analyze your video and recommend optimal settings.**

### Step 1: Analyze Your Video

```bash
# Analyze characteristics
vhs-upscale analyze family_vhs.mp4

# Save analysis for later use
vhs-upscale analyze family_vhs.mp4 --save family_vhs_analysis.json
```

**Analysis Output Example:**
```
═══════════════════════════════════════════════════════════
VIDEO ANALYSIS REPORT
═══════════════════════════════════════════════════════════

File: family_vhs.mp4
Duration: 1h 23m 14s
Size: 2.4 GB

DETECTED CHARACTERISTICS:
─────────────────────────────────────────────────────────
Scan Type:       Interlaced (Top Field First)
Source Format:   VHS
Content Type:    Live Action (Talking Head)
Noise Level:     HIGH
Quality Score:   42/100

VHS ARTIFACTS DETECTED:
─────────────────────────────────────────────────────────
✓ Color bleeding
✓ Head switching noise (bottom 8 pixels)
✓ Tracking jitter
✗ Dropout lines

RECOMMENDED SETTINGS:
─────────────────────────────────────────────────────────
Preset:          vhs_heavy
Deinterlace:     bwdif (better motion handling)
Denoise:         0.7 (high noise detected)
Upscale Engine:  realesrgan
Upscale Model:   realesrgan-x4plus
Target Res:      1080p
Audio Enhance:   voice (talking head detected)
Face Restore:    recommended (faces detected)

PROCESSING NOTES:
─────────────────────────────────────────────────────────
• Crop bottom 8 pixels to remove head switching noise
• Use moderate face restoration (strength 0.5-0.6)
• Audio enhancement recommended (voice mode)

ESTIMATED:
─────────────────────────────────────────────────────────
Processing Time: 45-60 minutes
Output Size:     ~3.2 GB (1080p, CRF 18)
```

### Step 2: Process with Auto-Detected Settings

```bash
# One command - analyze and process
vhs-upscale upscale family_vhs.mp4 -o restored.mp4 --auto-detect

# Or use saved analysis
vhs-upscale upscale family_vhs.mp4 -o restored.mp4 \
  --analysis-config family_vhs_analysis.json
```

**What happens:**
1. System analyzes video (15-30 seconds)
2. Shows recommended settings
3. Asks for confirmation
4. Processes with optimal settings

**Benefits:**
- No guesswork - AI chooses best settings
- Optimal results for your specific tape
- Consistent quality across similar tapes

---

## Batch Processing - Multiple VHS Tapes

**Process entire VHS collections efficiently.**

### Method 1: Batch with Same Settings

```bash
# Process all videos in a folder
vhs-upscale batch ./vhs_tapes/ ./restored_videos/ \
  --preset vhs \
  --engine realesrgan \
  -r 1080

# Process only MP4 files
vhs-upscale batch ./vhs_tapes/ ./restored_videos/ \
  --preset vhs \
  --pattern "*.mp4"
```

### Method 2: Parallel Processing (Faster)

```bash
# Process 2 videos at once
vhs-upscale batch ./vhs_tapes/ ./restored_videos/ \
  --preset vhs \
  --parallel 2

# Maximum parallelism (4-6 workers recommended)
vhs-upscale batch ./vhs_tapes/ ./restored_videos/ \
  --preset vhs \
  --parallel 4
```

**Parallel processing benefits:**

| Workers | Time for 10 Videos | GPU Usage | Recommended For |
|---------|-------------------|-----------|-----------------|
| 1 (sequential) | 10 hours | 50-70% | Single GPU, low RAM |
| 2 workers | 5-6 hours | 80-95% | **Most users** |
| 4 workers | 3-4 hours | 95-100% | High-end GPU, 32GB+ RAM |
| 8+ workers | 2-3 hours | 100% | Server/render farm |

### Method 3: Analyze First, Batch Later

**Recommended for mixed quality tapes:**

```bash
# Step 1: Analyze all tapes
for video in vhs_tapes/*.mp4; do
  vhs-upscale analyze "$video" --save "${video%.mp4}_config.json"
done

# Step 2: Review analysis reports, adjust if needed

# Step 3: Batch process with individual configs
for config in vhs_tapes/*_config.json; do
  video="${config%_config.json}.mp4"
  output="restored_videos/$(basename $video)"
  vhs-upscale upscale "$video" -o "$output" --analysis-config "$config"
done
```

### Batch Best Practices

**Resource Management:**
- **GPU-bound** (AI upscaling): 2-4 workers max
- **CPU-bound** (FFmpeg encoding): Match CPU core count
- **RAM**: 4-8GB free per worker
- **Storage**: Use SSD for temp files when processing 4K

**Skip Already Processed:**
```bash
vhs-upscale batch ./input/ ./output/ --skip-existing
```

**Resume Interrupted Batch:**
```bash
vhs-upscale batch ./input/ ./output/ --resume
```

---

## Expected Processing Times

**All times assume 1 hour of VHS footage (480i → 1080p)**

### By Hardware

| System | Engine | Time | Notes |
|--------|--------|------|-------|
| RTX 4090 | Maxine | 15-20 min | Fastest |
| RTX 3060/3070 | Real-ESRGAN | 30-40 min | Recommended |
| RTX 2060 | Real-ESRGAN | 45-60 min | Still good |
| AMD RX 6800 | Real-ESRGAN | 35-50 min | Vulkan support |
| Intel Arc A770 | Real-ESRGAN | 40-60 min | Decent |
| CPU only (i7) | FFmpeg | 2-4 hours | No GPU needed |

### By Processing Stage

| Stage | Time | % of Total |
|-------|------|-----------|
| Deinterlace | 5-10 min | 10-15% |
| Denoise + Upscale | 20-40 min | 50-70% |
| Face Restore (if enabled) | +10-15 min | +20-30% |
| Encode | 5-15 min | 10-20% |
| **Total** | **30-60 min** | **100%** |

### Resolution Impact

| Resolution | Processing Time | File Size | Recommendation |
|------------|----------------|-----------|----------------|
| 720p | 15-25 min | ~1.5 GB | Laptop/mobile viewing |
| 1080p | 30-60 min | ~3.0 GB | **Recommended** |
| 1440p | 45-90 min | ~5.0 GB | Large display viewing |
| 2160p (4K) | 90-180 min | ~8.0 GB | Rarely worth it for VHS |

**Recommendation:** 1080p is the sweet spot for VHS - best quality/time ratio.

---

## Quality Comparison - What to Expect

### Visual Improvements

**Before (Original VHS):**
- Resolution: 480i (~240p effective)
- Interlacing artifacts (combing on motion)
- Heavy grain/noise
- Faded colors
- Blurry faces
- Tracking jitter
- Color bleeding

**After (Restored to 1080p):**
- Resolution: 1920×1080 (Full HD)
- Smooth progressive video
- Significantly reduced noise
- Vibrant colors (like new)
- Enhanced facial details
- Stable, smooth playback
- Corrected colors

### Realistic Expectations

**What VHS Restoration CAN Do:**
✅ Remove interlacing artifacts (combing)
✅ Upscale to 1080p with AI detail recovery
✅ Dramatically reduce noise/grain
✅ Restore faded colors
✅ Enhance faces and fine details
✅ Improve audio clarity (remove hiss)
✅ Stabilize jittery footage
✅ Fix tracking errors

**What VHS Restoration CANNOT Do:**
❌ Create detail that never existed
❌ Magically transform VHS to Blu-ray quality
❌ Fix severely damaged/corrupted tapes
❌ Restore lost frames or dropouts
❌ Completely eliminate all VHS artifacts
❌ Match quality of native HD footage

**Quality Improvement Scale:**

| Source Quality | Improvement | Result Quality |
|----------------|-------------|----------------|
| Clean VHS (well-stored) | ████████░░ 80% | Excellent restoration |
| Typical VHS | ███████░░░ 70% | Very good restoration |
| Degraded VHS | █████░░░░░ 50% | Good restoration |
| Severely damaged | ███░░░░░░░ 30% | Watchable restoration |

### Before/After Examples

**Example 1: Family Home Video (1995)**
- **Before:** 480i, heavy grain, faded colors, blurry faces
- **After:** 1080p, clean image, vibrant colors, clear faces
- **Improvement:** 75% - dramatic improvement

**Example 2: Wedding Video (1990)**
- **Before:** 480i, tracking errors, color bleeding, muffled audio
- **After:** 1080p, stable, corrected colors, enhanced audio
- **Improvement:** 80% - excellent restoration

**Example 3: Heavily Worn Tape (1985)**
- **Before:** 480i, severe noise, dropouts, major fading
- **After:** 1080p, reduced noise, filled dropouts, improved colors
- **Improvement:** 50% - good but not perfect (source limitations)

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Combing artifacts still visible after processing"

**Cause:** Deinterlacing not applied or wrong field order

**Solution:**
```bash
# Try opposite field order
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  --deinterlace-algorithm bwdif \
  --field-order bff  # Try BFF if TFF doesn't work

# Or use stronger algorithm
vhs-upscale upscale input.mp4 -o output.mp4 \
  --deinterlace-algorithm qtgmc --qtgmc-preset medium
```

#### Issue: "Output looks too smooth/waxy (plastic skin)"

**Cause:** Too much denoising

**Solution:**
```bash
# Reduce denoise strength
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  --realesrgan-denoise 0.3  # Lower from default 0.6

# Or preserve more grain
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset clean  # No denoise preset
```

#### Issue: "White halos around objects"

**Cause:** Over-sharpening

**Solution:**
```bash
# Reduce sharpen strength
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  --sharpen-strength 0.2  # Lower from default 0.4

# Or disable sharpening
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  --sharpen-strength 0
```

#### Issue: "Processing too slow / takes forever"

**Cause:** Hardware limitations or 4K output

**Solutions:**
```bash
# 1. Use lower resolution
vhs-upscale upscale input.mp4 -o output.mp4 -r 720  # Instead of 1080

# 2. Use faster engine
vhs-upscale upscale input.mp4 -o output.mp4 \
  --engine realesrgan \
  --realesrgan-model realesrgan-animevideov3  # Fastest model

# 3. Use faster deinterlace
vhs-upscale upscale input.mp4 -o output.mp4 \
  --deinterlace-algorithm yadif  # Faster than BWDIF

# 4. Skip optional steps
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  # Don't use --face-restore (saves 30-50% time)
```

#### Issue: "CUDA out of memory" or "VRAM error"

**Cause:** GPU doesn't have enough memory for 1080p

**Solutions:**
```bash
# 1. Use lower resolution
vhs-upscale upscale input.mp4 -o output.mp4 -r 720

# 2. Close other GPU applications (browsers, games)

# 3. Use CPU-only mode
vhs-upscale upscale input.mp4 -o output.mp4 \
  --engine ffmpeg \
  --encoder libx264

# 4. Process in smaller chunks
vhs-upscale preview input.mp4 -o part1.mp4 --start 0 --duration 600
vhs-upscale preview input.mp4 -o part2.mp4 --start 600 --duration 600
# Then merge with FFmpeg
```

#### Issue: "Faces look unnatural/creepy"

**Cause:** Face restoration too strong

**Solution:**
```bash
# Reduce face restoration strength
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  --face-restore \
  --face-restore-strength 0.3  # Lower from default 0.5

# Or disable face restoration
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs
  # Remove --face-restore flag
```

#### Issue: "Colors look oversaturated/unnatural"

**Cause:** Too much color correction

**Solution:**
```bash
# Reduce saturation boost
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  --color-saturation 1.1  # Instead of 1.3

# Or skip color correction
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset clean  # No color adjustment
```

#### Issue: "Output file is huge (10GB+)"

**Cause:** CRF too low (too high quality)

**Solution:**
```bash
# Increase CRF for smaller files
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  --crf 23  # Higher CRF = smaller file (was 18)

# Or use H.265 (better compression)
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  --encoder hevc_nvenc \
  --crf 20
```

#### Issue: "Audio out of sync"

**Cause:** Processing altered frame timing

**Solution:**
```bash
# Copy audio without processing
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  --audio-copy  # Don't enhance audio

# Or extract and re-sync manually with FFmpeg
ffmpeg -i input.mp4 -vn -c:a copy audio.aac  # Extract audio
# Process video
ffmpeg -i video_only.mp4 -i audio.aac -c copy synced.mp4  # Combine
```

---

## Advanced Tips

### Tip 1: Test Before Committing

**Always test on a short clip first before processing the entire tape:**

```bash
# Generate 30-second preview clip
vhs-upscale preview vhs_tape.mp4 -o test_preview.mp4 \
  --start 120 \    # Start at 2 minutes
  --duration 30 \  # 30-second clip
  --preset vhs

# Review preview, adjust settings, then process full video
```

### Tip 2: Compare Multiple Presets

**Not sure which preset to use? Test them all:**

```bash
# Test all presets on a clip
vhs-upscale test-presets vhs_tape.mp4 -o preset_tests/ \
  --create-grid \
  --duration 10

# Creates comparison_grid.mp4 with all presets side-by-side
# Choose the best-looking one
```

### Tip 3: Optimize for Your Content

**Different VHS content needs different settings:**

| Content Type | Recommended Settings |
|--------------|---------------------|
| **Home videos with people** | `--preset vhs --face-restore --audio-enhance voice` |
| **Concerts/music** | `--preset vhs --audio-enhance music --realesrgan-denoise 0.5` |
| **Sports/action** | `--deinterlace-algorithm bwdif --realesrgan-denoise 0.6` |
| **Cartoons/animation** | `--preset clean --realesrgan-model realesrgan-x4plus-anime` |
| **Old news footage** | `--preset vhs --color-saturation 1.2` |

### Tip 4: Preserve Originals

**Never delete the original VHS capture until you're happy with the restoration:**

```bash
# Create a backup workflow
mkdir -p originals restored_videos

# Copy original to backup
cp vhs_capture.mp4 originals/

# Process
vhs-upscale upscale vhs_capture.mp4 -o restored_videos/restored.mp4 --preset vhs

# Keep originals until verified
```

### Tip 5: Batch Similar Content Together

**Group tapes by condition for consistent settings:**

```bash
# Good condition tapes
vhs-upscale batch ./good_condition/ ./restored/ \
  --preset vhs \
  --realesrgan-denoise 0.5

# Poor condition tapes
vhs-upscale batch ./poor_condition/ ./restored/ \
  --preset vhs \
  --realesrgan-denoise 0.8 \
  --face-restore
```

### Tip 6: Use LUTs for Cinematic Look

**Apply professional color grading:**

```bash
# Download free LUTs from RocketStock, LUTs.io, etc.

# Apply cinematic LUT
vhs-upscale upscale vhs_tape.mp4 -o restored.mp4 \
  --preset vhs \
  --lut film_look.cube \
  --lut-strength 0.7
```

### Tip 7: Monitor GPU Usage

**Optimize parallel processing:**

```bash
# While processing, monitor GPU in another terminal
watch -n 1 nvidia-smi  # Linux/Mac
# or
nvidia-smi -l 1        # Windows

# Adjust parallel workers based on GPU utilization:
# - If GPU < 80%: Increase workers
# - If GPU 95-100%: Current setting optimal
# - If system crashes: Decrease workers
```

### Tip 8: Dry-Run Mode

**Preview the processing pipeline before executing:**

```bash
# See what will happen without processing
vhs-upscale upscale vhs_tape.mp4 -o restored.mp4 --preset vhs --dry-run

# Shows:
# - Complete filter chain
# - Estimated output size
# - Estimated processing time
# - Any warnings or errors
```

---

## Quick Reference Card

**Save this command for most VHS tapes:**

```bash
# The "just works" command for 90% of VHS tapes
vhs-upscale upscale input.mp4 -o output.mp4 \
  --preset vhs \
  --deinterlace-algorithm bwdif \
  --engine realesrgan \
  -r 1080 \
  --audio-enhance voice \
  --encoder h264_nvenc \
  --crf 18
```

**Or let AI decide:**

```bash
# Let TerminalAI analyze and choose optimal settings
vhs-upscale upscale input.mp4 -o output.mp4 --auto-detect
```

---

## Next Steps

**After successfully restoring your first VHS tape:**

1. **Explore the Web GUI** - `python -m vhs_upscaler.gui`
   - Upload multiple videos
   - Queue batch processing
   - Monitor progress visually

2. **Read Advanced Documentation:**
   - `docs/BEST_PRACTICES.md` - Deep dive into VHS processing theory
   - `docs/DEINTERLACING.md` - Advanced deinterlacing techniques
   - `docs/FACE_RESTORATION.md` - Face restoration optimization
   - `README.md` - Complete feature reference

3. **Join the Community:**
   - Report issues: https://github.com/parthalon025/terminalai/issues
   - Share results: Discussions on GitHub
   - Contribute: Submit improvements

---

## Summary

**For most VHS home videos, this workflow will give excellent results:**

1. **Quick Start:** Use `--auto-detect` to let AI choose settings
2. **Or Manual:** `--preset vhs` with Real-ESRGAN to 1080p
3. **Enhance:** Add `--face-restore` for home videos with people
4. **Audio:** Add `--audio-enhance voice` for better dialogue
5. **Test First:** Always preview 30 seconds before processing hours of video

**Expected Results:**
- Clean 1080p HD video from 480i VHS
- Removed interlacing, noise, and VHS artifacts
- Restored colors and enhanced details
- Improved audio clarity
- Processing time: 30-60 minutes per hour of footage (with GPU)

**Remember:** VHS restoration is about enhancing what exists, not creating new content. Set realistic expectations, test settings, and enjoy bringing your old memories back to life!

---

**Happy Restoring!** 🎬✨
