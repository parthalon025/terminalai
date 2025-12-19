# GUI Quick Fix Presets Guide

## Overview

The TerminalAI GUI now includes **Quick Fix Preset** buttons that automatically configure optimal settings for different video sources. This eliminates the guesswork and ensures you're using best-practice settings for your specific content type.

## Quick Fix Buttons

Located below the Preset and Resolution dropdowns, you'll find 8 quick-fix buttons:

### 📼 VHS Home Movies
**Best for:** Family VHS tapes, home videos from the 80s/90s

**Automatically sets:**
- Preset: VHS
- Resolution: 1080p
- CRF: 18 (excellent quality)
- Encoder: HEVC NVENC (GPU accelerated)
- Upscale Engine: Auto (best available)
- Face Restore: **Enabled** (0.5 strength)
- Audio Enhancement: Voice (optimized for dialogue)
- Audio Upmix: Demucs AI
- Audio Layout: 5.1 Surround
- Deinterlace: YADIF (fast, good quality)

**Use when:** Processing home movies with faces/people, want face enhancement and surround sound

---

### 🔊 Noisy VHS
**Best for:** Damaged VHS tapes, heavily degraded footage, noisy sources

**Automatically sets:**
- Preset: VHS
- Resolution: 1080p
- CRF: 18 (excellent quality)
- Encoder: HEVC NVENC
- Upscale Engine: Real-ESRGAN
- Real-ESRGAN Model: x4plus (general purpose)
- Real-ESRGAN Denoise: 0.8 (heavy)
- Face Restore: Disabled (noise may interfere)
- Audio Enhancement: Aggressive
- Deinterlace: QTGMC (best quality, slower)
- QTGMC Preset: Medium

**Use when:** VHS tapes with heavy noise, tracking errors, dropout lines, or severe degradation

---

### 💿 DVD Rip
**Best for:** DVD sources (480p/576p), already progressive or lightly interlaced

**Automatically sets:**
- Preset: DVD
- Resolution: 1080p
- CRF: 20 (very good quality)
- Encoder: HEVC NVENC
- Upscale Engine: Auto
- Face Restore: Disabled
- Audio Enhancement: Light
- Deinterlace: YADIF

**Use when:** Processing DVD rips that are already decent quality with minimal noise

---

### 📺 Old YouTube
**Best for:** Compressed YouTube videos, old uploads with heavy compression artifacts

**Automatically sets:**
- Preset: YouTube
- Resolution: 1080p
- CRF: 20 (very good quality)
- Encoder: HEVC NVENC
- Upscale Engine: Real-ESRGAN
- Face Restore: Disabled
- Audio Enhancement: Moderate

**Use when:** Enhancing downloaded YouTube videos with compression artifacts and blockiness

---

### 🎨 Anime/Animation
**Best for:** Anime, cartoons, animated content

**Automatically sets:**
- Preset: Clean
- Resolution: 1080p
- CRF: 18 (excellent quality)
- Encoder: HEVC NVENC
- Upscale Engine: Real-ESRGAN
- Real-ESRGAN Model: **animevideov3** (anime-optimized)
- Face Restore: Disabled (not needed for animation)
- Audio Enhancement: None

**Use when:** Processing anime or animated content where sharp lines and vibrant colors are important

---

### 🎥 Webcam Footage
**Best for:** Low-quality webcam recordings, video calls, screen recordings

**Automatically sets:**
- Preset: Webcam
- Resolution: 1080p
- CRF: 20 (very good quality)
- Encoder: HEVC NVENC
- Upscale Engine: Auto
- Face Restore: Disabled
- Audio Enhancement: Voice (speech optimized)

**Use when:** Cleaning up webcam footage, Zoom recordings, or other progressive low-quality sources

---

### ✨ Clean Digital
**Best for:** Already high-quality digital sources, minimal processing needed

**Automatically sets:**
- Preset: Clean
- Resolution: 1080p
- CRF: 18 (excellent quality)
- Encoder: HEVC NVENC
- Upscale Engine: Auto
- Face Restore: Disabled
- Audio Enhancement: None

**Use when:** Source is already clean and you just want to upscale resolution without heavy processing

---

### ⭐ Best Quality (Slow)
**Best for:** When quality matters more than speed, archival purposes

**Automatically sets:**
- Preset: VHS
- Resolution: 1080p
- CRF: 15 (visually lossless)
- Quality Priority: 0 (best)
- Encoder: libx265 (CPU, slower but better)
- Upscale Engine: Maxine (requires RTX GPU)
- Face Restore: **Enabled** (0.7 strength - strong)
- Audio Enhancement: Voice
- Audio Upmix: Demucs AI
- Audio Layout: **7.1 Surround**
- Deinterlace: QTGMC (best quality)
- QTGMC Preset: Slow

**Use when:** Processing important footage for archival, willing to wait for maximum quality

⚠️ **Warning:** This preset is very slow (1-5 fps) but produces the best possible results

---

## How to Use

1. **Upload or specify your video** in the "Upload File" or "URL / Path" tab
2. **Click the appropriate Quick Fix button** based on your source type
3. **Review the auto-configured settings** (they'll update in the Advanced Options accordion)
4. **Optionally adjust** any settings if needed
5. **Click "Add to Queue"** to process

The status message at the bottom will confirm which preset was applied and show a brief description.

## Customization

After clicking a Quick Fix button, you can still manually adjust any setting:
- Open the **"Advanced Options"** accordion to see what was configured
- Modify any value (resolution, CRF, encoder, etc.)
- Your changes will override the preset

## Tips

- **Start with Quick Fix** - Always start with the appropriate quick-fix button, then adjust if needed
- **VHS Home Movies** - Most common choice for family videos from VHS tapes
- **Noisy VHS** - Use for tapes with visible noise, static, or tracking errors
- **Best Quality** - Only use if you're willing to wait hours and have an RTX GPU
- **Anime** - Critical to use the anime-specific model for animation content

## Best Practices

### VHS Content:
1. Click **"VHS Home Movies"** for most family tapes
2. Click **"Noisy VHS"** if you see heavy grain, dropout lines, or tracking errors
3. Click **"Best Quality (Slow)"** only for your most precious memories

### Modern Content:
1. Click **"YouTube Old"** for compressed/blocky YouTube videos
2. Click **"Webcam"** for Zoom recordings or webcam footage
3. Click **"Clean Digital"** for already good quality sources

### Animation:
1. **Always** click **"Anime/Animation"** - uses the anime-specific AI model
2. Do not use VHS presets for anime, even if it's from VHS

## Advanced Users

Quick Fix presets are defined in `vhs_upscaler/gui.py` in the `get_quick_fix_presets()` function. You can:
- Add custom presets
- Modify existing preset values
- Create specialized configurations for your workflow

The presets follow the best practices documented in the comprehensive VHS Processing Best Practices guide in the plan file.

---

**Related Documentation:**
- Main README: [README.md](../README.md)
- VHS Quick Start: [QUICKSTART_VHS.md](QUICKSTART_VHS.md)
- YouTube Quick Start: [QUICKSTART_YOUTUBE.md](QUICKSTART_YOUTUBE.md)
- Audio Upmix Guide: [QUICKSTART_AUDIO.md](QUICKSTART_AUDIO.md)
