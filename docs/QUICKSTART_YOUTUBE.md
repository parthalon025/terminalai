# YouTube Video Enhancement - Quick Start Guide

## Table of Contents

1. [What is YouTube Enhancement?](#what-is-youtube-enhancement)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Download + Process Workflow](#download--process-workflow)
5. [Enhancement Pipeline](#enhancement-pipeline)
6. [Presets for YouTube Content](#presets-for-youtube-content)
7. [Batch YouTube Processing](#batch-youtube-processing)
8. [Quality Settings by Source](#quality-settings-by-source)
9. [Common Use Cases](#common-use-cases)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

---

## What is YouTube Enhancement?

YouTube video enhancement restores compressed, low-quality, or degraded YouTube videos by:

- **Upscaling resolution**: 240p/360p/480p → 1080p or 4K
- **Removing compression artifacts**: MPEG blocking, mosquito noise
- **Deblocking**: Smooth out macro-blocking from heavy compression
- **Sharpening**: Restore detail lost to compression
- **Audio enhancement**: Clean up lossy audio compression artifacts

### Why Enhance YouTube Videos?

**Use cases:**
- Preserve old/deleted YouTube videos before removal
- Restore archived content (pre-2010 videos often 240p-480p only)
- Improve old music videos, concerts, documentaries
- Upscale educational/historical content
- Create high-quality archives of rare content
- Prepare YouTube downloads for TV/projector playback

**Quality improvements:**
```
Old YouTube (240p-480p)    → Enhanced 1080p+        Improvement
────────────────────────────────────────────────────────────────
Blocky compression    ──▶  Smooth, clean           ████████░░ 80%
Low resolution        ──▶  HD/4K upscale           ███████░░░ 70%
Lossy audio          ──▶  Enhanced clarity         ██████░░░░ 60%
Color degradation    ──▶  Restored colors          █████░░░░░ 50%

Modern YouTube (720p+)     → Enhanced 1080p/4K     Improvement
────────────────────────────────────────────────────────────────
Already good quality  ──▶  Slightly sharper        ███░░░░░░░ 30%
Minimal artifacts    ──▶  Polished look           ███░░░░░░░ 30%
```

*Older/lower quality videos benefit most from enhancement*

---

## Prerequisites

### Required Software

1. **yt-dlp** (YouTube downloader)
   ```bash
   # Install via pip
   pip install yt-dlp

   # Or use package manager
   # macOS:
   brew install yt-dlp

   # Windows:
   winget install yt-dlp
   ```

2. **FFmpeg** (video processing)
   ```bash
   # Ubuntu/Debian:
   sudo apt install ffmpeg

   # macOS:
   brew install ffmpeg

   # Windows:
   winget install FFmpeg
   ```

3. **TerminalAI** (VHS Upscaler)
   ```bash
   pip install -e .
   ```

### Verify Installation

```bash
# Check yt-dlp
yt-dlp --version

# Check FFmpeg
ffmpeg -version

# Check VHS Upscaler
python -m vhs_upscaler.vhs_upscale --help
```

### Optional (Recommended)

- **NVIDIA GPU** with RTX for best AI upscaling
- **Real-ESRGAN** for non-NVIDIA GPU upscaling
- **Demucs** for AI audio separation (surround upmix)

---

## Quick Start

### Single Command Enhancement

TerminalAI integrates yt-dlp for seamless download + processing:

```bash
# Basic: Download and upscale YouTube video to 1080p
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=VIDEO_ID" \
  -o enhanced.mp4 \
  --preset youtube

# Advanced: 4K with audio enhancement
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=VIDEO_ID" \
  -o enhanced_4k.mp4 \
  --preset youtube \
  -r 2160 \
  --audio-enhance moderate
```

**What happens:**
1. Downloads best quality available from YouTube
2. Auto-detects YouTube URL and selects appropriate settings
3. Upscales to target resolution
4. Enhances audio (if specified)
5. Outputs final video ready to watch

---

## Download + Process Workflow

### Integrated Workflow (Recommended)

TerminalAI automatically handles download when given a YouTube URL:

```bash
# TerminalAI detects YouTube URL and downloads automatically
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=dQw4w9WgXcQ" \
  -o rickroll_hd.mp4 \
  --preset youtube_old \
  -r 1080
```

**Supported URL formats:**
- `https://youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/shorts/VIDEO_ID`
- `https://m.youtube.com/watch?v=VIDEO_ID`

### Manual Download + Process Workflow

If you prefer separate steps or need more control:

```bash
# Step 1: Download best quality (manual)
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --merge-output-format mp4 \
  -o "downloaded.mp4" \
  "https://youtube.com/watch?v=VIDEO_ID"

# Step 2: Process downloaded file
python -m vhs_upscaler.vhs_upscale \
  -i downloaded.mp4 \
  -o enhanced.mp4 \
  --preset youtube_old \
  -r 1080
```

### Standalone YouTube Downloader

Use the included downloader script for just downloading:

```bash
# Download only (no processing)
python download_youtube.py "https://youtube.com/watch?v=VIDEO_ID"

# Downloads to current directory as: {video_title}.mp4
```

### GUI Mode

The web interface supports direct YouTube URLs:

```bash
# Launch GUI
python -m vhs_upscaler.gui

# Then:
# 1. Paste YouTube URL in "URL / Path" field
# 2. Select preset (youtube or youtube_old)
# 3. Choose resolution and settings
# 4. Click "Add to Queue"
```

---

## Enhancement Pipeline

YouTube videos flow through this processing pipeline:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   DOWNLOAD   │     │  DEBLOCK     │     │  AI UPSCALE  │     │   SHARPEN    │
│              │────▶│              │────▶│              │────▶│              │
│ yt-dlp       │     │ Remove       │     │ Maxine/      │     │ CAS filter   │
│ Best quality │     │ artifacts    │     │ Real-ESRGAN  │     │ Detail boost │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                      │
┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│   OUTPUT     │     │ AUDIO ENCODE │     │ AUDIO PROC   │◀───────────┘
│              │◀────│              │◀────│              │
│ Final Video  │     │ AAC/AC3      │     │ Enhance/     │
│ HD/4K        │     │ Quality      │     │ Normalize    │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Processing Order (Critical)

For optimal quality, the pipeline follows this proven order:

```
1. DEBLOCK (optional, for heavily compressed sources)
   ↓
2. DENOISE (light, remove compression noise)
   ↓
3. UPSCALE (AI or traditional scaling)
   ↓
4. SHARPEN (optional, restore detail)
   ↓
5. ENCODE (H.264/H.265 with target quality)
   ↓
6. AUDIO (enhance, normalize, optional upmix)
```

**Why this order?**
- Deblock first prevents AI from amplifying compression artifacts
- Denoise before upscale prevents noise amplification
- Sharpen after upscale enhances upscaled detail
- Encode last avoids multiple compression passes

---

## Presets for YouTube Content

TerminalAI provides two YouTube-optimized presets:

### Preset: `youtube` (Modern Videos)

**Best for:** 720p+ YouTube videos uploaded after ~2012

**Settings:**
- **Deinterlace**: Off (YouTube is progressive)
- **Denoise**: Very light (1,1,1,1) - minimal processing
- **Quality mode**: Best (0)

**When to use:**
- Recent uploads (2012+)
- Already 720p or better
- Minimal compression artifacts
- Clean, modern codecs

**Example:**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=NEW_VIDEO" \
  -o output.mp4 \
  --preset youtube \
  -r 1080
```

---

### Preset: `youtube_old` (Legacy/Compressed)

**Best for:** Pre-2010 YouTube (240p-480p), heavily compressed videos

**Settings:**
- **Deinterlace**: Off
- **Denoise**: Moderate (2,1,2,1) - removes compression artifacts
- **Deblock**: Optional (add manually for severe blocking)
- **Quality mode**: Best (0)

**When to use:**
- Old YouTube videos (pre-2010)
- 240p/360p/480p sources
- Visible compression artifacts
- Blocky/pixelated footage
- Archived/rare content

**Example:**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=OLD_VIDEO" \
  -o output.mp4 \
  --preset youtube_old \
  -r 1080 \
  --audio-enhance moderate
```

---

### Adding Deblocking for Heavily Compressed Videos

For severe compression (old YouTube, low bitrate uploads):

```bash
# youtube_old preset + deblocking filter
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=VIDEO_ID" \
  -o output.mp4 \
  --preset youtube_old \
  -r 1080
  # Manual deblock filter addition via custom config
```

**Note:** Deblocking is achieved through the denoise settings in `youtube_old` preset. For extreme cases, consider preprocessing with ffmpeg:

```bash
# Preprocess with deblock filter
ffmpeg -i input.mp4 -vf "deblock=filter=strong" deblocked.mp4

# Then upscale
python -m vhs_upscaler.vhs_upscale \
  -i deblocked.mp4 \
  -o final.mp4 \
  --preset youtube
```

---

### Preset Selection Guide

| Source Quality | Era | Preset | Reason |
|----------------|-----|--------|--------|
| 240p-480p | Pre-2010 | `youtube_old` | Heavy compression, artifacts |
| 720p | 2010-2015 | `youtube` or `youtube_old` | Moderate compression |
| 1080p+ | 2015+ | `youtube` or `clean` | Good quality, minimal issues |
| Music videos (old) | Pre-2010 | `youtube_old` | Often low bitrate |
| Webcam/amateur | Any | `youtube_old` | Usually compressed |
| Professional uploads | 2015+ | `clean` | Already high quality |

---

## Batch YouTube Processing

Process multiple YouTube videos in one command:

### Multiple URLs

```bash
# Create a text file with URLs
cat > urls.txt << EOF
https://youtube.com/watch?v=VIDEO1
https://youtube.com/watch?v=VIDEO2
https://youtube.com/watch?v=VIDEO3
EOF

# Process each URL
while IFS= read -r url; do
  # Extract video ID for filename
  video_id=$(echo "$url" | grep -oP '(?<=v=)[^&]+')

  python -m vhs_upscaler.vhs_upscale \
    -i "$url" \
    -o "enhanced_${video_id}.mp4" \
    --preset youtube_old \
    -r 1080 \
    --audio-enhance moderate
done < urls.txt
```

### Batch Script (Linux/Mac)

```bash
#!/bin/bash
# youtube_batch.sh - Process multiple YouTube videos

PRESET="youtube_old"
RESOLUTION=1080
AUDIO="moderate"

for url in "$@"; do
  echo "Processing: $url"

  # Extract video ID
  video_id=$(echo "$url" | sed -n 's/.*v=\([^&]*\).*/\1/p')
  output="youtube_${video_id}_${RESOLUTION}p.mp4"

  python -m vhs_upscaler.vhs_upscale \
    -i "$url" \
    -o "$output" \
    --preset "$PRESET" \
    -r "$RESOLUTION" \
    --audio-enhance "$AUDIO"

  echo "Saved: $output"
done

echo "Batch processing complete!"
```

**Usage:**
```bash
chmod +x youtube_batch.sh
./youtube_batch.sh \
  "https://youtube.com/watch?v=VIDEO1" \
  "https://youtube.com/watch?v=VIDEO2" \
  "https://youtube.com/watch?v=VIDEO3"
```

### PowerShell Script (Windows)

```powershell
# youtube_batch.ps1 - Process multiple YouTube videos

$urls = @(
    "https://youtube.com/watch?v=VIDEO1",
    "https://youtube.com/watch?v=VIDEO2",
    "https://youtube.com/watch?v=VIDEO3"
)

$preset = "youtube_old"
$resolution = 1080
$audio = "moderate"

foreach ($url in $urls) {
    Write-Host "Processing: $url"

    # Extract video ID
    $videoId = ($url -replace '.*v=([^&]*).*', '$1')
    $output = "youtube_${videoId}_${resolution}p.mp4"

    python -m vhs_upscaler.vhs_upscale `
      -i "$url" `
      -o "$output" `
      --preset "$preset" `
      -r $resolution `
      --audio-enhance "$audio"

    Write-Host "Saved: $output"
}

Write-Host "Batch processing complete!"
```

**Usage:**
```powershell
powershell -ExecutionPolicy Bypass -File youtube_batch.ps1
```

### Playlist Processing

Download entire YouTube playlist, then process:

```bash
# Step 1: Download playlist
yt-dlp -o "%(playlist_index)s_%(title)s.%(ext)s" \
  "https://youtube.com/playlist?list=PLAYLIST_ID"

# Step 2: Batch process all downloaded videos
for video in *.mp4; do
  python -m vhs_upscaler.vhs_upscale \
    -i "$video" \
    -o "enhanced_${video}" \
    --preset youtube_old \
    -r 1080
done
```

---

## Quality Settings by Source

Choose settings based on original YouTube quality:

### 240p Sources (Very Old YouTube)

**Characteristics:**
- 320×240 or 426×240 resolution
- Heavy compression artifacts
- Blocky, pixelated
- Often pre-2008 content

**Recommended settings:**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=VIDEO_ID" \
  -o output.mp4 \
  --preset youtube_old \
  -r 1080 \
  --engine realesrgan \
  --realesrgan-denoise 0.8 \
  --audio-enhance aggressive \
  --crf 18
```

**Explanation:**
- `youtube_old`: Denoise + artifact removal
- `realesrgan`: Better than FFmpeg for extreme upscaling
- `denoise 0.8`: Strong noise reduction for compression artifacts
- `audio-enhance aggressive`: Clean up lossy audio
- `crf 18`: Higher quality output to preserve upscale detail

---

### 360p/480p Sources (Old YouTube)

**Characteristics:**
- 640×360 or 854×480 resolution
- Moderate compression
- Some blocking in high-motion scenes
- 2008-2012 era content

**Recommended settings:**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=VIDEO_ID" \
  -o output.mp4 \
  --preset youtube_old \
  -r 1080 \
  --engine auto \
  --audio-enhance moderate \
  --crf 20
```

**Explanation:**
- `youtube_old`: Moderate denoise
- `auto`: Use best available engine (Maxine/Real-ESRGAN/FFmpeg)
- `audio-enhance moderate`: Balanced audio cleanup
- `crf 20`: Good quality-to-size ratio

---

### 720p Sources (Modern YouTube Standard)

**Characteristics:**
- 1280×720 resolution
- Good quality, minimal artifacts
- 2012+ content
- Already watchable

**Recommended settings:**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=VIDEO_ID" \
  -o output.mp4 \
  --preset youtube \
  -r 1080 \
  --engine maxine \
  --crf 22
```

**Explanation:**
- `youtube`: Light processing (preserve original quality)
- `maxine`: Best AI upscaling for clean sources
- `crf 22`: Efficient encoding (source already good quality)

---

### 1080p Sources (Modern High Quality)

**Characteristics:**
- 1920×1080 resolution
- High bitrate, minimal compression
- Recent uploads (2015+)
- Often professional content

**Recommended settings:**

**Option 1: Upscale to 4K**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=VIDEO_ID" \
  -o output_4k.mp4 \
  --preset clean \
  -r 2160 \
  --engine maxine \
  --crf 20
```

**Option 2: Keep 1080p, polish only**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=VIDEO_ID" \
  -o output_polished.mp4 \
  --preset clean \
  -r 1080 \
  --engine ffmpeg \
  --crf 18
```

**Explanation:**
- `clean`: No denoise, preserve quality
- `maxine` (4K) or `ffmpeg` (1080p): Appropriate scaling
- `crf 18-20`: High quality for archival

---

## Common Use Cases

### Use Case 1: Old Music Video Archive

**Scenario:** Pre-2010 music video, 360p, compressed

```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=MUSIC_VIDEO" \
  -o music_video_hd.mp4 \
  --preset youtube_old \
  -r 1080 \
  --engine realesrgan \
  --realesrgan-denoise 0.7 \
  --audio-enhance music \
  --audio-format flac \
  --crf 18
```

**Result:** Upscaled to 1080p, enhanced audio in lossless FLAC, artifacts removed

---

### Use Case 2: Educational Documentary (720p)

**Scenario:** Educational content, 720p, good quality

```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=DOCUMENTARY" \
  -o documentary_1080p.mp4 \
  --preset youtube \
  -r 1080 \
  --engine maxine \
  --audio-enhance voice \
  --crf 20
```

**Result:** Clean 1080p upscale, voice-optimized audio, archival quality

---

### Use Case 3: Rare Historical Footage (240p)

**Scenario:** Deleted/rare footage, 240p, heavily compressed

```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=RARE_VIDEO" \
  -o rare_restored.mp4 \
  --preset youtube_old \
  -r 1080 \
  --engine realesrgan \
  --realesrgan-model realesrgan-x4plus \
  --realesrgan-denoise 0.9 \
  --audio-enhance aggressive \
  --audio-normalize \
  --crf 16
```

**Result:** Maximum quality restoration, archival-grade output

---

### Use Case 4: Concert Recording for TV Playback

**Scenario:** Concert video, 720p, needs surround sound for home theater

```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=CONCERT" \
  -o concert_4k_surround.mp4 \
  --preset youtube \
  -r 2160 \
  --engine maxine \
  --audio-enhance music \
  --audio-upmix demucs \
  --audio-layout 5.1 \
  --audio-format eac3 \
  --audio-bitrate 640k \
  --crf 18
```

**Result:** 4K video with AI-powered 5.1 surround sound, ready for home theater

---

### Use Case 5: Batch Playlist Archive

**Scenario:** Archive entire music playlist (mixed quality)

```bash
# Download playlist first
yt-dlp -o "%(playlist_index)s_%(title)s.%(ext)s" \
  "https://youtube.com/playlist?list=PLAYLIST_ID"

# Process with consistent settings
for video in *.mp4; do
  python -m vhs_upscaler.vhs_upscale \
    -i "$video" \
    -o "enhanced_${video}" \
    --preset youtube_old \
    -r 1080 \
    --engine realesrgan \
    --audio-enhance music \
    --crf 20
done
```

**Result:** Entire playlist upscaled to 1080p with consistent quality

---

## Troubleshooting

### Issue: "yt-dlp not found" or "yt-dlp: command not found"

**Symptom:**
```
Error: yt-dlp not found. Install with: pip install yt-dlp
```

**Solution:**
```bash
# Install yt-dlp
pip install yt-dlp

# Update to latest version
pip install --upgrade yt-dlp

# Verify installation
yt-dlp --version
```

---

### Issue: "YouTube download failed" or "HTTP Error 429"

**Symptom:**
- Download fails with HTTP 429 (rate limit)
- "Video unavailable" error
- "Sign in to confirm age" error

**Solution:**

**Rate limiting (429):**
```bash
# Wait 10-15 minutes, then retry
# YouTube temporarily blocks rapid downloads
```

**Age-restricted videos:**
```bash
# Export cookies from your browser (logged in to YouTube)
# Use browser extension "Get cookies.txt"
# Save as cookies.txt

# Use cookies with yt-dlp
yt-dlp --cookies cookies.txt "https://youtube.com/watch?v=VIDEO_ID"
```

**Region-locked videos:**
```bash
# Use VPN or proxy
# Or try downloading from different location
```

---

### Issue: Output quality not much better than source

**Symptom:**
Enhanced video looks similar to original YouTube download

**Solution:**

**Check source quality:**
```bash
# See what quality yt-dlp downloaded
ffprobe -v quiet -show_entries stream=width,height,bit_rate downloaded.mp4
```

**If source is already 1080p:**
- YouTube provides good quality at 1080p
- Enhancement gives diminishing returns
- Consider upscaling to 4K instead:
  ```bash
  -r 2160  # 4K upscale
  ```

**If source is low quality:**
- Use stronger upscale engine:
  ```bash
  --engine realesrgan --realesrgan-model realesrgan-x4plus
  ```
- Add denoising:
  ```bash
  --preset youtube_old
  ```

---

### Issue: Download very slow

**Symptom:**
Download takes a long time, especially for long videos

**Solution:**

**Use faster download options:**
```bash
# Download lower quality for faster processing
yt-dlp -f "worst" "URL"  # Fastest download

# Or select specific quality
yt-dlp -f "bestvideo[height<=720]+bestaudio" "URL"
```

**Parallel downloads:**
```bash
# Download multiple videos simultaneously
yt-dlp --external-downloader aria2c --external-downloader-args "-x 16 -s 16" "URL"

# Requires aria2c: sudo apt install aria2
```

---

### Issue: Audio quality poor after enhancement

**Symptom:**
Enhanced audio has artifacts, distortion, or sounds worse

**Solution:**

**Choose appropriate enhancement level:**
```bash
# For already decent audio:
--audio-enhance light

# For noisy/compressed audio:
--audio-enhance moderate

# For very poor audio (use sparingly):
--audio-enhance aggressive
```

**Use lossless audio codec:**
```bash
--audio-format flac  # Lossless, larger files
--audio-format ac3   # Good quality, compatible
```

**Disable enhancement if source is good:**
```bash
# No audio processing
--audio-enhance none
```

---

### Issue: Video and audio out of sync

**Symptom:**
Audio doesn't match video after processing

**Solution:**

**This is usually from source download issues:**
```bash
# Re-download with sync fix
yt-dlp --fixup detect_or_warn "URL"

# Or force specific format merge
yt-dlp -f "bestvideo+bestaudio" --merge-output-format mp4 "URL"
```

**If still out of sync after processing:**
```bash
# Check original download first
ffplay downloaded.mp4

# If original is OK but output is not, report as bug
```

---

## Best Practices

### Analyze Before Processing

Use the analysis feature to get optimal settings:

```bash
# Download first
yt-dlp -o "youtube.mp4" "https://youtube.com/watch?v=VIDEO_ID"

# Analyze
python -m vhs_upscaler.vhs_upscale \
  -i youtube.mp4 \
  --analyze-only

# Process with recommended settings
python -m vhs_upscaler.vhs_upscale \
  -i youtube.mp4 \
  -o enhanced.mp4 \
  --auto-detect
```

---

### Preview Before Full Processing

Generate a preview to test settings:

```bash
# Download
yt-dlp -o "youtube.mp4" "https://youtube.com/watch?v=VIDEO_ID"

# Create 10-second preview from middle
vhs-upscale preview youtube.mp4 -o preview.mp4 \
  --preset youtube_old \
  --duration 10

# Review preview, then process full video if satisfied
```

---

### Choose Appropriate Resolution

Don't over-upscale unnecessarily:

| Source | Target | Recommendation |
|--------|--------|----------------|
| 240p | 720p-1080p | Good improvement |
| 360p | 1080p | Recommended |
| 480p | 1080p | Good balance |
| 720p | 1080p or 4K | 1080p for most cases |
| 1080p | 4K | Only if displaying on 4K screen |

**Reasoning:** Upscaling too much (240p → 4K) can amplify artifacts without real quality gain.

---

### Audio Enhancement Guidelines

| Source Audio | Enhancement | Reason |
|--------------|-------------|--------|
| 64kbps or lower | aggressive | Heavy compression, needs cleanup |
| 96-128kbps | moderate | Typical old YouTube audio |
| 192kbps+ | light or none | Already good quality |
| Music content | music | Preserves dynamics |
| Voice/dialogue | voice | Optimized for speech clarity |

---

### CRF Quality Guidelines

Choose CRF based on intended use:

| CRF | Quality | File Size | Use Case |
|-----|---------|-----------|----------|
| 16-18 | Excellent | Large | Archival, rare content |
| 18-20 | Very Good | Medium | General enhancement |
| 20-22 | Good | Smaller | Already decent sources |
| 22-24 | Acceptable | Small | Previews, tests |

**Recommendation:** Use CRF 18-20 for most YouTube enhancement.

---

### Comparison Testing

Test multiple presets to find best settings:

```bash
# Download once
yt-dlp -o "source.mp4" "https://youtube.com/watch?v=VIDEO_ID"

# Test different presets
vhs-upscale test-presets source.mp4 -o tests/ \
  --presets youtube,youtube_old,clean \
  --create-grid

# Review comparison_grid.mp4 to choose best preset
```

---

### Efficient Batch Processing

For multiple videos, optimize workflow:

**Serial processing (one at a time):**
```bash
# Reliable, lower memory usage
for url in $(cat urls.txt); do
  python -m vhs_upscaler.vhs_upscale -i "$url" -o "output_${n}.mp4" --preset youtube_old
done
```

**Parallel processing (advanced):**
```bash
# Faster but requires more resources
# Only use if you have powerful hardware (RTX GPU, 32GB+ RAM)
cat urls.txt | xargs -P 2 -I {} bash -c \
  'python -m vhs_upscaler.vhs_upscale -i "{}" -o "enhanced_$(basename {}).mp4" --preset youtube_old'
```

**Recommendation:** Use serial for most cases, parallel only on high-end systems.

---

### Storage Management

YouTube enhancement creates large files:

**Estimated output sizes:**
- 240p → 1080p: ~500MB per 10 minutes
- 480p → 1080p: ~800MB per 10 minutes
- 720p → 1080p: ~1GB per 10 minutes
- 1080p → 4K: ~3GB per 10 minutes

**Tips:**
- Use external drive for large batches
- Enable `--keep-temp` only for debugging
- Delete original downloads after successful processing
- Compress archives with 7zip for long-term storage

---

## Summary

YouTube video enhancement workflow:

**Basic enhancement:**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=VIDEO_ID" \
  -o enhanced.mp4 \
  --preset youtube_old \
  -r 1080
```

**Advanced enhancement with audio:**
```bash
python -m vhs_upscaler.vhs_upscale \
  -i "https://youtube.com/watch?v=VIDEO_ID" \
  -o enhanced.mp4 \
  --preset youtube_old \
  -r 1080 \
  --engine realesrgan \
  --realesrgan-denoise 0.7 \
  --audio-enhance moderate \
  --crf 18
```

**Key points:**
- Use `youtube` preset for modern videos (720p+, 2012+)
- Use `youtube_old` preset for old/compressed videos (240p-480p, pre-2010)
- Add `--audio-enhance` for better audio quality
- Choose appropriate resolution (don't over-upscale)
- Test with preview before processing full videos
- Analyze first for optimal settings

For more information:
- **VHS Upscaler README**: [README.md](../README.md)
- **Audio Enhancement**: [AUDIO_GUIDE.md](AUDIO_GUIDE.md)
- **Preset Testing**: [COMPARISON_MODULE.md](COMPARISON_MODULE.md)
- **Best Practices**: [BEST_PRACTICES.md](BEST_PRACTICES.md)

---

**Generated by VHS Upscaler Documentation**
Version: 1.4.2 | Last Updated: 2025-12-18
