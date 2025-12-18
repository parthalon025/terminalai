# VHS & Video Enhancement Best Practices

## Table of Contents
- [Capture & Digitization](#capture--digitization)
- [Processing Order](#processing-order-critical)
- [Upscaling Best Practices](#upscaling-best-practices)
- [Sharpening Best Practices](#sharpening-best-practices)
- [Denoising Best Practices](#denoising-best-practices)
- [Face Restoration Best Practices](#face-restoration-best-practices)
- [Color Correction Best Practices](#color-correction-best-practices)
- [Encoding Best Practices](#encoding-best-practices)
- [Performance Best Practices](#performance-best-practices)
- [Quality Control](#quality-control)
- [What NOT to Do](#what-not-to-do)

---

## Capture & Digitization

### Hardware Recommendations
- **Use a TBC (Time Base Corrector)** for damaged tapes with tracking issues, frame jitter, or color drift
- **Capture at highest quality**: Use lossless codec (HuffYUV, FFV1) or ProRes during capture—don't compress until final encode
- **Match source framerate**: NTSC = 29.97fps, PAL = 25fps—don't convert during capture
- **Capture interlaced**: Don't deinterlace during capture; do it in post with QTGMC for best results
- **Clean VCR heads** before important captures—dirty heads = noise and dropouts

### Capture Settings
```bash
# Example lossless capture command (adjust for your hardware)
ffmpeg -f dshow -i video="Capture Device" -c:v ffv1 -level 3 -c:a pcm_s16le output.avi
```

---

## Processing Order (Critical)

⚠️ **This order matters!** Processing in the wrong order will amplify artifacts.

```
1. DEINTERLACE (QTGMC/yadif) ← ALWAYS FIRST FOR VHS
   ↓
2. LIGHT DENOISE (hqdn3d 0.5-1.0) ← Preserve detail
   ↓
3. COLOR CORRECT (optional) ← Fix VHS color issues
   ↓
4. UPSCALE (Real-ESRGAN) ← Do ONCE, not multiple times
   ↓
5. FACE RESTORE (GFPGAN/CodeFormer) ← Optional
   ↓
6. SHARPEN (CAS 0.3-0.5) ← Enhance clarity/detail
   ↓
7. ENCODE (H.264/H.265 CRF 18-20) ← Final compression
```

### Why This Order?

1. **Always deinterlace FIRST** — AI upscalers amplify interlacing artifacts if you skip this
2. **Denoise BEFORE upscaling** — Upscaling amplifies noise; remove it early but lightly
3. **Color correct BEFORE upscaling** — Easier to fix at lower resolution
4. **Upscale ONCE** — Multiple upscale passes degrade quality; do 4x in one pass, not 2x twice
5. **Sharpen AFTER upscaling** — Sharpening before upscale creates harsh artifacts
6. **Face restore AFTER upscaling** — GFPGAN/CodeFormer work best on higher resolution input

---

## Upscaling Best Practices

### Resolution Strategy
- **2x vs 4x**: For VHS (480i), 2x to 1080p often looks better than 4x to 4K—less hallucinated detail
- **Scale once, scale right**: Don't do 2x twice; do 4x in one pass if needed

### Model Selection
```
RealESRGAN_x4plus     → Best detail recovery, slower
realesr-general-x4v3  → Good balance, has denoise option
realesr-animevideov3  → Fastest, best for animation
```

### Implementation
```bash
# Recommended: 2x upscale with denoise disabled
python inference_realesrgan_video.py \
  -i preprocessed.mp4 \
  -n RealESRGAN_x4plus \
  -s 2 \
  --suffix upscaled

# Alternative: General model with built-in denoise
python inference_realesrgan_video.py \
  -i preprocessed.mp4 \
  -n realesr-general-x4v3 \
  -s 2 \
  -dn 1
```

### Key Settings
- **Disable built-in denoise** (`-dn 0`) when you've already denoised—prevents over-smoothing
- **Use PNG for frame extraction** — Lossless; JPEG introduces compression artifacts
- **Tile size**: Use `--tile 512` or `--tile 256` if you get VRAM errors; 0 = auto

---

## Sharpening Best Practices

### General Rules
- **Less is more**: Start at CAS 0.2-0.3, increase only if needed
- **Watch for halos**: White/dark edges around objects = too much sharpening
- **Avoid double-sharpening**: Real-ESRGAN already adds some sharpness
- **Test on motion**: Sharpening artifacts are more visible in motion than still frames
- **Use adaptive sharpening** (CAS) over unsharp mask—CAS is edge-aware

### Filter Reference

| Filter | Strength | Use Case | Risk |
|--------|----------|----------|------|
| `cas=0.2` | Light | Subtle enhancement | Low |
| `cas=0.4` | Medium | General use (recommended) | Low |
| `cas=0.6` | Heavy | Very soft sources | Medium |
| `unsharp=3:3:0.5` | Light | Edge enhancement | Low |
| `unsharp=5:5:1.0` | Heavy | Aggressive sharpening | High |
| `unsharp=5:5:1.5` | Extreme | Caution: creates halos | Very High |

### Implementation
```bash
# Recommended: Contrast Adaptive Sharpening
ffmpeg -i upscaled.mp4 -vf "cas=0.4" -c:a copy sharpened.mp4

# Light unsharp (subtle)
ffmpeg -i upscaled.mp4 -vf "unsharp=3:3:0.5:3:3:0.3" -c:a copy sharpened.mp4

# Combined denoise + sharpen
ffmpeg -i upscaled.mp4 -vf "hqdn3d=1:1:2:2,cas=0.3" -c:a copy final.mp4
```

---

## Denoising Best Practices

### Philosophy
- **Temporal > Spatial**: `hqdn3d` (temporal) preserves more detail than `nlmeans` (spatial)
- **Light touch**: Heavy denoise = plastic/waxy look; VHS grain is part of the aesthetic
- **Scene-dependent**: Some scenes need more/less—consider per-scene processing
- **Test on dark scenes**: Noise is most visible in shadows; check there first

### Filter Guide

| Filter | Type | Strength | Use Case |
|--------|------|----------|----------|
| `hqdn3d=0.5:0.5:1:1` | Temporal | Very light | Preserve grain |
| `hqdn3d=2:2:3:3` | Temporal | Light | General use |
| `hqdn3d=6:4:8:6` | Temporal | Heavy | Very noisy VHS |
| `nlmeans=s=3:p=7:r=15` | Spatial | Medium | GPU-accelerated |

### Implementation
```bash
# Light temporal denoise (recommended for VHS)
ffmpeg -i input.mp4 -vf "hqdn3d=2:2:3:3" denoised.mp4

# Heavy denoise for very degraded footage
ffmpeg -i input.mp4 -vf "hqdn3d=6:4:8:6" denoised.mp4

# GPU-accelerated spatial denoise
ffmpeg -i input.mp4 -vf "nlmeans=s=3:p=7:r=15" denoised.mp4
```

---

## Face Restoration Best Practices

### When to Use
- **CodeFormer > GFPGAN** for very old/degraded footage—better at extreme cases
- **Only on faces**: Don't run face models on entire frame—blend face regions only
- **Watch for uncanny valley**: Over-restored faces look artificial; sometimes less is more

### Settings
```bash
# GFPGAN (good for general use)
python inference_gfpgan.py \
  -i upscaled_frames/ \
  -o face_enhanced/ \
  -v 1.4 \
  -s 2

# CodeFormer (better for old footage)
python inference_codeformer.py \
  -i upscaled_frames/ \
  -o face_enhanced/ \
  --fidelity_weight 0.7
```

### Fidelity Weight (CodeFormer)
- **0.5** = more AI enhancement (creative restoration)
- **0.7** = balanced (recommended)
- **0.9** = closer to original (conservative)

---

## Color Correction Best Practices

### VHS-Specific Issues
- **VHS has color bleed**: Chroma bleeding due to analog limitations
- **Saturation boost**: VHS fades over time; moderate saturation increase often helps
- **Don't over-correct**: Some color fade is authentic; preserve the era's look if desired

### When to Correct
- **Fix before upscale**: Easier and faster at 480p than 4K
- **Test on representative clips**: Color varies across tape

### Common Corrections

```bash
# VHS color bleed fix
ffmpeg -i input.mp4 -vf "colorbalance=rs=0.1:gs=0:bs=-0.1" fixed.mp4

# Saturation boost for faded VHS
ffmpeg -i input.mp4 -vf "eq=saturation=1.2" color.mp4

# Auto levels
ffmpeg -i input.mp4 -vf "eq=saturation=1.2,curves=preset=color_negative" color.mp4

# Manual curves (example: reduce blue cast)
ffmpeg -i input.mp4 -vf "curves=r='0/0 0.5/0.6 1/1':g='0/0 0.5/0.5 1/1':b='0/0 0.5/0.4 1/1'" color.mp4
```

---

## Encoding Best Practices

### Codec Selection
- **H.264 (libx264)**: Universal compatibility, good quality
- **H.265 (libx265)**: Better compression, smaller files, less compatible

### CRF (Constant Rate Factor)
- **Lower CRF = Higher Quality = Bigger File**
- **Higher CRF = Lower Quality = Smaller File**

| Codec | CRF Range | Recommended |
|-------|-----------|-------------|
| H.264 | 18-20 | CRF 18 for archival, 20 for sharing |
| H.265 | 20-22 | CRF 20 for archival, 22 for sharing |

### Commands
```bash
# H.264 high quality (recommended)
ffmpeg -i sharpened.mp4 \
  -c:v libx264 \
  -crf 18 \
  -preset slow \
  -c:a aac -b:a 192k \
  final.mp4

# H.265 (smaller file)
ffmpeg -i sharpened.mp4 \
  -c:v libx265 \
  -crf 20 \
  -preset slow \
  -c:a aac -b:a 192k \
  final.mp4

# 10-bit for gradients (reduces banding)
ffmpeg -i sharpened.mp4 \
  -c:v libx264 \
  -crf 18 \
  -preset slow \
  -pix_fmt yuv420p10le \
  -c:a aac -b:a 192k \
  final.mp4
```

### Audio Handling
- **Keep original** if possible: `-c:a copy` unless enhancing audio
- **If re-encoding**: AAC at 192k is good balance of quality/size

---

## Performance Best Practices

### Hardware Optimization
- **Batch similar content**: Process all episodes of a series together
- **Test on 30-second clip first**: Don't process 2 hours to find settings are wrong
- **Use ncnn-vulkan** for AMD/Intel GPUs—no CUDA required
- **Watch VRAM**: 8GB VRAM handles most tasks; 4GB may need smaller tile sizes
- **SSD for temp files**: Frame extraction = thousands of files; SSD is 10x faster than HDD

### Tile Size for VRAM Constraints
```bash
# Default (auto)
python inference_realesrgan_video.py -i input.mp4 -n RealESRGAN_x4plus

# 4GB VRAM
python inference_realesrgan_video.py -i input.mp4 -n RealESRGAN_x4plus --tile 256

# 6GB VRAM
python inference_realesrgan_video.py -i input.mp4 -n RealESRGAN_x4plus --tile 512
```

---

## Quality Control

### A/B Comparison
- **Always compare**: Side-by-side upscaled vs original
- **Use video players with A/B mode**: VLC, MPV support synchronized playback

### Problem Areas to Check
1. **Fast motion**: Look for ghosting or temporal artifacts
2. **Text/titles**: Should be readable, not smeared
3. **Faces**: Natural, not waxy or over-smoothed
4. **Fine patterns**: No moiré or aliasing
5. **Dark scenes**: Check noise levels in shadows
6. **Edges**: No halos or over-sharpening artifacts

### Workflow
```
1. Export test segments (10 seconds from beginning, middle, end)
2. Process test segments with candidate settings
3. A/B compare against original
4. Adjust settings based on worst problem area
5. Repeat until satisfied
6. Process full video
```

---

## What NOT to Do

❌ **Don't upscale interlaced footage** — deinterlace first

❌ **Don't stack multiple AI upscalers** — use one, done well

❌ **Don't over-denoise** — you'll lose texture and detail

❌ **Don't over-sharpen** — creates halos and unnatural edges

❌ **Don't use JPEG for intermediate frames** — use PNG

❌ **Don't process at max settings without testing** — waste of time

❌ **Don't expect miracles** — 480i VHS has fundamental resolution limits

❌ **Don't skip quality control** — artifacts only visible in motion

❌ **Don't batch process blindly** — content varies, settings should too

❌ **Don't ignore audio** — poor audio ruins good video

---

## Quick Reference Commands

### Full VHS Pipeline (Single Command)
```bash
# Minimal preprocessing
ffmpeg -i input.mp4 \
  -vf "yadif=1,hqdn3d=1:1:2:2,eq=saturation=1.1" \
  -c:v libx264 -crf 20 \
  preprocessed.mp4

# Then upscale
python inference_realesrgan_video.py \
  -i preprocessed.mp4 \
  -n RealESRGAN_x4plus \
  -s 2 \
  --suffix upscaled

# Then sharpen + encode
ffmpeg -i preprocessed_upscaled.mp4 \
  -vf "cas=0.4" \
  -c:v libx264 -crf 18 -preset slow \
  -c:a copy \
  final.mp4
```

### Analyze Source
```bash
# Check for interlacing
ffmpeg -i input.mp4 -vf idet -f null -

# Get video info
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,codec_name \
  -of csv=p=0 input.mp4
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Combing artifacts after upscale | Deinterlace BEFORE upscaling |
| Over-sharpened/halos | Reduce CAS to 0.2-0.3 |
| Mushy/soft faces | Add GFPGAN or CodeFormer |
| Color bleeding | Add colorbalance filter |
| Blocky output | Add deblock step for YouTube sources |
| Grainy output | Increase denoise (but lose detail) |
| Processing too slow | Use ncnn-vulkan, reduce scale to 2x |
| VRAM errors | Add `--tile 256` or `--tile 512` |
| Flickering | Use temporal denoise (hqdn3d) |
| Waxy/plastic skin | Reduce denoise, lower face restoration fidelity |
| Unnatural colors | Skip auto color correction, use manual curves |
| Moiré patterns | Add light blur before upscale |
| Audio/video sync | Extract audio first, recombine with original timing |

---

## Model Reference

| Model | Type | Best For | Detail Level | Speed |
|-------|------|----------|--------------|-------|
| `RealESRGAN_x4plus` | Upscale | Max detail/sharpness | ★★★★★ | Slow |
| `realesr-general-x4v3` | Upscale | VHS balanced | ★★★★☆ | Fast |
| `realesr-general-x4v3 -dn 0` | Upscale | Sharpest (no denoise) | ★★★★★ | Fast |
| `realesr-animevideov3` | Upscale | Animation/cartoons | ★★★★☆ | Fastest |
| `GFPGAN v1.4` | Face | Face detail recovery | ★★★★☆ | Medium |
| `CodeFormer` | Face | Old footage faces | ★★★★★ | Medium |

---

## Further Reading

- [Real-ESRGAN Documentation](https://github.com/xinntao/Real-ESRGAN)
- [FFmpeg Filters Guide](https://ffmpeg.org/ffmpeg-filters.html)
- [QTGMC Deinterlacing Guide](http://avisynth.nl/index.php/QTGMC)
- [Video2X](https://github.com/k4yt3x/video2x)
