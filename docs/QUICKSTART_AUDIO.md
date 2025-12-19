# Audio Enhancement & Surround Sound Quick-Start Guide

Complete guide to audio restoration and surround upmixing for VHS tapes, DVDs, and digital video.

---

## Table of Contents

1. [Overview](#overview)
2. [Audio Enhancement Modes](#audio-enhancement-modes)
3. [Surround Upmixing Algorithms](#surround-upmixing-algorithms)
4. [Output Formats](#output-formats)
5. [Complete Workflows](#complete-workflows)
6. [Advanced Options](#advanced-options)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The VHS Upscaler includes powerful audio processing capabilities:

- **6 Enhancement Modes**: From light cleanup to aggressive restoration
- **4 Upmix Algorithms**: Convert stereo to 5.1 or 7.1 surround sound
- **Multiple Output Formats**: AAC, AC3, EAC3, DTS, FLAC
- **AI-Powered Processing**: Demucs stem separation for best results
- **EBU R128 Normalization**: Professional loudness standards

### Audio Processing Pipeline

```
INPUT AUDIO
    |
    v
┌─────────────────┐
│ 1. EXTRACT      │  Extract audio from video (if needed)
└────────┬────────┘
         v
┌─────────────────┐
│ 2. ENHANCE      │  Noise reduction, EQ, compression
└────────┬────────┘
         v
┌─────────────────┐
│ 3. UPMIX        │  Stereo → 5.1/7.1 surround (optional)
└────────┬────────┘
         v
┌─────────────────┐
│ 4. NORMALIZE    │  EBU R128 loudness normalization
└────────┬────────┘
         v
┌─────────────────┐
│ 5. ENCODE       │  Compress to AAC/AC3/EAC3/DTS/FLAC
└────────┬────────┘
         v
OUTPUT AUDIO
```

### Requirements

**Basic Audio Processing:**
- FFmpeg (bundled with application)

**AI Surround Upmixing (Demucs):**
```bash
# Install Demucs for best quality surround
pip install demucs
# Or install with full audio support
pip install -e ".[audio]"
```

---

## Audio Enhancement Modes

Enhancement modes clean up noisy, distorted, or low-quality audio using FFmpeg filters.

### Mode Comparison

| Mode | Use Case | Noise Reduction | Compression | Processing Time |
|------|----------|-----------------|-------------|-----------------|
| `none` | Clean source | None | None | Instant |
| `light` | Minor cleanup | Subtle | Gentle | ~5 sec |
| `moderate` | General restoration | Medium | Moderate | ~10 sec |
| `aggressive` | Heavy noise | Strong | Heavy | ~15 sec |
| `voice` | Dialogue/speech | Optimized | Speech-tuned | ~12 sec |
| `music` | Music preservation | Light | Dynamic | ~8 sec |

### 1. None - Passthrough

No processing applied. Use for high-quality sources.

```bash
# Just copy audio without changes
vhs-upscale upscale video.mp4 -o output.mp4 --audio-enhance none
```

**When to Use:**
- Modern digital recordings
- Already processed audio
- Lossless preservation needed

---

### 2. Light Enhancement

Gentle cleanup for minor issues. Minimal audible changes.

**Filters Applied:**
- High-pass filter @ 80 Hz (remove rumble)
- Low-pass filter @ 15 kHz (remove hiss)
- Light compression (2:1 ratio)

```bash
vhs-upscale upscale video.mp4 -o output.mp4 --audio-enhance light
```

**Best For:**
- Modern VHS recordings (1990s+)
- DVD audio with minor issues
- Clean digital sources needing slight polish

**Example Output:**
- Before: Light background hum, slight hiss
- After: Clear audio, imperceptible processing

---

### 3. Moderate Enhancement

Balanced restoration for typical VHS/DVD audio.

**Filters Applied:**
- High-pass filter @ 100 Hz
- Low-pass filter @ 14 kHz
- FFT noise reduction (-20 dB)
- Moderate compression (3:1 ratio)
- Presence boost @ 3 kHz (+2 dB)

```bash
vhs-upscale upscale video.mp4 -o output.mp4 --audio-enhance moderate
```

**Best For:**
- Standard VHS tapes (1980s-1990s)
- Commercial DVD releases
- Home videos with typical noise

**Example Output:**
- Before: Background hiss, uneven levels
- After: Clear dialogue, reduced hiss, balanced volume

---

### 4. Aggressive Enhancement

Maximum noise reduction for heavily degraded audio.

**Filters Applied:**
- High-pass filter @ 120 Hz
- Low-pass filter @ 12 kHz
- Strong FFT noise reduction (-15 dB)
- Non-local means denoising
- Heavy compression (4:1 ratio)

```bash
vhs-upscale upscale video.mp4 -o output.mp4 --audio-enhance aggressive
```

**Best For:**
- Old/damaged VHS tapes (1970s-1980s)
- Third-generation copies
- Extremely noisy recordings

**Warning:** May introduce artifacts on clean audio. Use only for very noisy sources.

**Example Output:**
- Before: Heavy hiss, tape hum, distortion
- After: Much cleaner, some detail loss possible

---

### 5. Voice Mode

Optimized for speech and dialogue clarity.

**Filters Applied:**
- High-pass filter @ 100 Hz
- Low-pass filter @ 8 kHz (speech range)
- FFT noise reduction (-18 dB)
- EQ: -3 dB @ 200 Hz (reduce muddiness)
- EQ: +4 dB @ 2.5 kHz (presence/clarity)
- EQ: +2 dB @ 5 kHz (air/intelligibility)
- Speech compression (3:1 ratio, fast attack)
- Brick-wall limiter @ -0.5 dB

```bash
vhs-upscale upscale interview.mp4 -o output.mp4 --audio-enhance voice
```

**Best For:**
- Interviews and documentaries
- VHS home videos (conversations)
- Podcasts from old recordings
- Talking-head videos

**Example Output:**
- Before: Muffled voices, background noise
- After: Crystal clear speech, minimal background

---

### 6. Music Mode

Preserves dynamics and frequency range for music.

**Filters Applied:**
- High-pass filter @ 30 Hz (subsonic removal only)
- Light FFT noise reduction (-25 dB)
- Gentle compression (2:1 ratio, slow release)
- Wide frequency preservation

```bash
vhs-upscale upscale concert.mp4 -o output.mp4 --audio-enhance music
```

**Best For:**
- Concert recordings
- Music videos
- VHS music performances
- Bootleg recordings

**Example Output:**
- Before: Tape hiss, uneven levels
- After: Clean sound, preserved dynamics

---

## Surround Upmixing Algorithms

Convert stereo (2.0) audio to multi-channel surround (5.1 or 7.1).

### Algorithm Comparison

| Algorithm | Quality | Speed | AI-Powered | Channel Sep. | GPU Required |
|-----------|---------|-------|------------|--------------|--------------|
| `simple` | ⭐⭐ | Instant | No | Basic | No |
| `surround` | ⭐⭐⭐ | ~5 sec | No | Good | No |
| `prologic` | ⭐⭐⭐⭐ | ~8 sec | No | Better | No |
| `demucs` | ⭐⭐⭐⭐⭐ | ~60 sec | Yes | Excellent | Optional |

### Processing Time Estimates (5-minute video)

- **Simple**: < 1 second
- **Surround**: ~5-10 seconds
- **Pro Logic II**: ~10-15 seconds
- **Demucs (CPU)**: ~3-5 minutes
- **Demucs (CUDA GPU)**: ~30-60 seconds

---

### 1. Simple Upmix

Basic channel mapping with LFE extraction. Fast but limited separation.

**Channel Mapping:**
```
FL = Left input
FR = Right input
FC = 0.5*L + 0.5*R (center mix)
LFE = 0.5*L + 0.5*R (bass extracted)
BL = 0.7*L (rear left)
BR = 0.7*R (rear right)
```

```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix simple \
  --audio-layout 5.1 \
  --audio-format eac3
```

**Best For:**
- Quick conversions
- Background compatibility
- Non-critical playback

**Limitations:**
- No intelligent separation
- Rear channels just duplicate front
- Center is simple stereo collapse

---

### 2. Surround Filter

FFmpeg's built-in surround filter. Good balance of speed and quality.

**Processing:**
- Analyzes stereo field correlation
- Extracts center-panned content
- Creates ambient rear channels
- Low-frequency extraction for LFE

```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix surround \
  --audio-layout 5.1 \
  --audio-format eac3
```

**Best For:**
- Most video content
- Movies from DVD
- General use cases

**Advantages:**
- Decent spatial separation
- No AI dependencies
- Fast processing

---

### 3. Pro Logic II Simulation

Simulates Dolby Pro Logic II matrix decoding. Better separation than simple filters.

**Channel Mapping:**
```
FL = 0.5*L + 0.25*Center
FR = 0.5*R + 0.25*Center
FC = 0.5*L + 0.5*R (mono sum)
LFE = 0.5*L + 0.5*R (low-pass filtered)
BL = 0.5*L - 0.25*R (difference)
BR = 0.5*R - 0.25*L (difference)
```

```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix prologic \
  --audio-layout 5.1 \
  --audio-format ac3
```

**Best For:**
- Movies originally mixed for Pro Logic
- TV shows from 1990s-2000s
- Content with clear center dialogue

**Advantages:**
- Better than simple/surround
- Mimics proven technology
- Good dialogue isolation

---

### 4. Demucs AI Upmix (Highest Quality)

Uses AI stem separation to intelligently map audio sources to surround channels.

**How It Works:**
1. Demucs separates stereo into 4 stems:
   - **Vocals**: Speech, singing
   - **Drums**: Percussion, rhythm
   - **Bass**: Low-frequency instruments
   - **Other**: Everything else (instruments, ambience)

2. Intelligent channel mapping:
   - **Vocals** → Center channel (mostly) + slight L/R
   - **Drums** → Front L/R + slight surrounds
   - **Bass** → LFE (subwoofer) + Front L/R
   - **Other** → Front L/R + Surround L/R

```bash
vhs-upscale upscale movie.mp4 -o output.mp4 \
  --audio-upmix demucs \
  --audio-layout 5.1 \
  --audio-format eac3
```

**Advanced Options:**
```bash
# Use faster Demucs model
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix demucs \
  --demucs-model htdemucs \
  --demucs-device cuda

# High-quality model (slower)
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix demucs \
  --demucs-model htdemucs_ft
```

**Best For:**
- Movies and music videos
- Content with clear dialogue
- When quality matters most
- Final delivery/archival

**Requirements:**
- Python package: `demucs`
- 4-8 GB RAM minimum
- CUDA GPU recommended (optional)

**Processing Time:**
- CPU (Intel i7): ~3-5 minutes per 5-minute video
- GPU (RTX 3060): ~30-60 seconds per 5-minute video

---

### 5.1 vs 7.1 Surround

**5.1 Surround (6 channels):**
- Front Left (FL)
- Front Right (FR)
- Center (FC)
- Low-Frequency Effects / Subwoofer (LFE)
- Surround/Rear Left (BL)
- Surround/Rear Right (BR)

**7.1 Surround (8 channels):**
- All 5.1 channels +
- Side Left (SL)
- Side Right (SR)

```bash
# 5.1 surround (standard)
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-layout 5.1 --audio-upmix surround

# 7.1 surround (more immersive)
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-layout 7.1 --audio-upmix surround
```

**Recommendation:** Use 5.1 for most cases. 7.1 only if playback system supports it.

---

## Output Formats

Choose the right audio codec for your needs.

### Format Comparison

| Format | Max Channels | Bitrate | Lossy/Lossless | Best For |
|--------|--------------|---------|----------------|----------|
| AAC | 2.0 | 128-320k | Lossy | Stereo, streaming |
| AC3 | 5.1 | 640k | Lossy | Standard surround |
| EAC3 | 7.1 | 640k+ | Lossy | Modern surround |
| DTS | 5.1 | 1536k | Lossy | High quality |
| FLAC | 8.0 | Variable | Lossless | Archival |

---

### 1. AAC (Advanced Audio Codec)

Modern, efficient stereo codec. Default for stereo content.

```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-format aac \
  --audio-bitrate 192k
```

**Recommended Bitrates:**
- Stereo: 128k (acceptable) - 192k (good) - 256k (excellent)

**Best For:**
- Stereo content
- Web streaming
- Mobile playback
- YouTube uploads

**Compatibility:** Excellent (plays everywhere)

---

### 2. AC3 (Dolby Digital)

Standard surround sound codec. Widely compatible.

```bash
vhs-upscale upscale movie.mp4 -o output.mp4 \
  --audio-layout 5.1 \
  --audio-format ac3
```

**Automatic Bitrate:**
- 5.1 surround: 640 kbps
- Stereo: 192 kbps

**Best For:**
- DVD-style 5.1 surround
- Home theater playback
- Blu-ray authoring
- Maximum compatibility

**Compatibility:** Excellent (all players support)

---

### 3. EAC3 (Dolby Digital Plus)

Enhanced AC3 with better quality and 7.1 support.

```bash
vhs-upscale upscale movie.mp4 -o output.mp4 \
  --audio-layout 5.1 \
  --audio-format eac3
```

**Automatic Bitrate:**
- 5.1/7.1 surround: 640 kbps
- Stereo: 192 kbps

**Best For:**
- Streaming services
- Modern home theater
- 7.1 surround sound
- Blu-ray

**Compatibility:** Good (2010+ devices)

---

### 4. DTS

High bitrate surround format. Better quality than AC3.

```bash
vhs-upscale upscale movie.mp4 -o output.mp4 \
  --audio-layout 5.1 \
  --audio-format dts
```

**Automatic Bitrate:**
- 5.1 surround: 1536 kbps (3x AC3)
- Stereo: 192 kbps

**Best For:**
- Audiophile listening
- High-quality archival
- Large file sizes acceptable

**Compatibility:** Good (most modern players)

---

### 5. FLAC (Lossless)

Lossless compression. Perfect quality preservation.

```bash
vhs-upscale upscale video.mp4 -o output.mkv \
  --audio-layout 5.1 \
  --audio-format flac
```

**Bitrate:** Variable (typically 800-1200 kbps for 5.1)

**Best For:**
- Archival purposes
- When file size doesn't matter
- Maximum quality preservation
- Intermediate processing

**Note:** Requires MKV container (not MP4)

**Compatibility:** Limited (modern players only)

---

## Complete Workflows

Real-world examples combining enhancement and upmixing.

### Workflow 1: VHS Home Video Restoration

**Scenario:** Old family VHS tape (1990s) with dialogue and background noise.

**Goal:** Clean audio, upscale video, preserve memories.

```bash
vhs-upscale upscale family_vhs_1995.mp4 -o restored.mp4 \
  --preset vhs \
  --audio-enhance voice \
  --audio-format aac \
  --audio-bitrate 192k \
  -r 1080
```

**Processing Steps:**
1. Deinterlace VHS footage
2. AI upscale to 1080p
3. Apply voice enhancement (removes hiss, boosts clarity)
4. Normalize to -14 LUFS
5. Encode to AAC 192k

**Processing Time:** ~5 minutes for 30-minute video (RTX GPU)

**Result:**
- Clear, intelligible dialogue
- Reduced tape hiss and hum
- Crisp 1080p video

---

### Workflow 2: DVD Movie with AI Surround

**Scenario:** DVD rip (stereo audio) for home theater playback.

**Goal:** Create immersive 5.1 surround experience.

```bash
vhs-upscale upscale movie_dvd.mkv -o movie_5.1.mkv \
  --preset dvd \
  --audio-enhance moderate \
  --audio-upmix demucs \
  --audio-layout 5.1 \
  --audio-format eac3 \
  -r 1080
```

**Processing Steps:**
1. Upscale DVD to 1080p
2. Moderate audio enhancement (cleanup)
3. Demucs AI stem separation
4. Intelligent 5.1 channel mapping:
   - Dialogue → Center channel
   - Music/ambience → Surround channels
   - Bass → LFE subwoofer
5. Normalize loudness
6. Encode to EAC3 5.1

**Processing Time:** ~10 minutes for 2-hour movie (RTX GPU)

**Result:**
- Full HD 1080p video
- True 5.1 surround sound
- Clear dialogue in center channel
- Immersive rear channels

---

### Workflow 3: Music Concert Recording

**Scenario:** VHS recording of live concert (1980s).

**Goal:** Preserve musical dynamics, reduce noise, create surround.

```bash
vhs-upscale upscale concert_vhs.mp4 -o concert_restored.mp4 \
  --preset vhs \
  --audio-enhance music \
  --audio-upmix demucs \
  --audio-layout 5.1 \
  --audio-format dts \
  -r 1080
```

**Processing Steps:**
1. Deinterlace VHS footage
2. Upscale to 1080p
3. Music enhancement (light cleanup, preserve dynamics)
4. Demucs separation:
   - Vocals → Center
   - Instruments → L/R + surrounds
   - Bass → LFE
5. High-bitrate DTS encoding (1536 kbps)

**Processing Time:** ~15 minutes for 60-minute concert (GPU)

**Result:**
- Restored video quality
- Preserved musical dynamics
- Immersive surround soundstage
- Professional-grade audio

---

### Workflow 4: Interview/Documentary

**Scenario:** Old interview tape with poor audio quality.

**Goal:** Maximum speech intelligibility.

```bash
vhs-upscale upscale interview.mp4 -o interview_clean.mp4 \
  --preset vhs \
  --audio-enhance voice \
  --audio-layout stereo \
  --audio-format aac \
  --audio-bitrate 192k \
  --audio-target-loudness -16.0 \
  -r 1080
```

**Processing Steps:**
1. Upscale to 1080p
2. Voice-optimized enhancement:
   - Remove rumble and hiss
   - Boost speech frequencies (2-5 kHz)
   - Heavy compression for consistent levels
3. Normalize to broadcast standard (-16 LUFS)
4. Keep stereo (no upmix needed for voice)

**Processing Time:** ~3 minutes for 20-minute interview

**Result:**
- Crystal clear speech
- No background noise
- Consistent volume levels
- Broadcast-ready audio

---

### Workflow 5: Batch Processing VHS Collection

**Scenario:** Process entire VHS collection (50 tapes) with same settings.

**Goal:** Automated restoration with consistent quality.

```bash
vhs-upscale batch ./vhs_collection/ ./restored_collection/ \
  --preset vhs \
  --audio-enhance moderate \
  --audio-upmix surround \
  --audio-layout 5.1 \
  --audio-format ac3 \
  --parallel 2 \
  -r 1080
```

**Processing Steps:**
1. Scan input folder for videos
2. Process 2 videos simultaneously
3. Apply VHS preset to all
4. Moderate audio enhancement
5. Surround filter upmix (fast)
6. AC3 5.1 encoding

**Processing Time:** ~24 hours for 50x 60-minute tapes (2 parallel)

**Best Practices:**
- Test on 1-2 videos first
- Use `surround` upmix (fast) instead of `demucs` for batch
- Monitor disk space (5-10 GB per restored tape)
- Use `--resume` flag if interrupted

---

### Workflow 6: YouTube Upload Preparation

**Scenario:** VHS footage for YouTube channel.

**Goal:** Optimize for streaming, good audio quality, fast upload.

```bash
vhs-upscale upscale vhs_video.mp4 -o youtube_upload.mp4 \
  --preset vhs \
  --encoder h264 \
  --crf 18 \
  --audio-enhance moderate \
  --audio-format aac \
  --audio-bitrate 192k \
  --audio-target-loudness -14.0 \
  -r 1080
```

**Processing Steps:**
1. Upscale to 1080p (YouTube standard)
2. H.264 encoding (best compatibility)
3. CRF 18 (high quality for YouTube re-encode)
4. Moderate audio cleanup
5. AAC 192k (YouTube standard)
6. -14 LUFS loudness (streaming standard)

**File Size:** ~500 MB for 10-minute video

**Result:**
- Optimized for YouTube processing
- Clear audio meeting streaming standards
- Fast upload times

---

## Advanced Options

Fine-tune audio processing for specific needs.

### Loudness Normalization

Control target loudness using EBU R128 standards.

```bash
# Default: -14 LUFS (streaming standard)
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-enhance moderate

# Broadcast standard: -16 LUFS
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-enhance moderate \
  --audio-target-loudness -16.0

# Loud (not recommended): -12 LUFS
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-enhance moderate \
  --audio-target-loudness -12.0

# Disable normalization (preserve original levels)
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-enhance moderate \
  --no-audio-normalize
```

**LUFS Targets:**
- **-14 LUFS**: Spotify, Apple Music, YouTube (default)
- **-16 LUFS**: Broadcast TV (EBU R128)
- **-18 LUFS**: Cinematic content
- **-12 LUFS**: Podcasts (louder)

---

### LFE Crossover Frequency

Control subwoofer frequency cutoff.

```bash
# Default: 120 Hz (THX standard)
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-layout 5.1 \
  --audio-upmix surround

# Lower crossover: 80 Hz (smaller subwoofer)
# Higher crossover: 150 Hz (larger subwoofer)
```

**Note:** Currently fixed at 120 Hz in AudioConfig. Can be modified in code if needed.

---

### Demucs Model Selection

Choose AI model for quality vs speed tradeoff.

```bash
# Default: htdemucs (hybrid transformer, best quality)
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix demucs \
  --demucs-model htdemucs

# Fine-tuned model (higher quality, slower)
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix demucs \
  --demucs-model htdemucs_ft

# Extra quality (very slow)
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix demucs \
  --demucs-model mdx_extra
```

**Model Comparison:**

| Model | Quality | Speed | VRAM Usage |
|-------|---------|-------|------------|
| htdemucs | Excellent | Fast | 2-4 GB |
| htdemucs_ft | Better | Medium | 3-5 GB |
| mdx_extra | Best | Slow | 4-8 GB |

---

### GPU Acceleration for Demucs

Use CUDA GPU for 5-10x faster Demucs processing.

```bash
# Auto-detect (default - uses GPU if available)
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix demucs \
  --demucs-device auto

# Force GPU
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix demucs \
  --demucs-device cuda

# Force CPU (no GPU)
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix demucs \
  --demucs-device cpu
```

**Performance:**
- **CPU (Intel i7)**: ~3-5 min for 5-minute video
- **GPU (RTX 3060)**: ~30-60 sec for 5-minute video

---

### Custom Bitrates

Override default bitrates for specific needs.

```bash
# Stereo AAC
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-format aac \
  --audio-bitrate 256k  # Higher quality

# 5.1 Surround AC3
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-layout 5.1 \
  --audio-format ac3 \
  --audio-bitrate 448k  # Lower bitrate (space-saving)

# Maximum quality DTS
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-layout 5.1 \
  --audio-format dts \
  --audio-bitrate 1536k  # Maximum DTS bitrate
```

**Bitrate Guidelines:**

**Stereo (AAC):**
- 128k: Acceptable (streaming)
- 192k: Good (default)
- 256k: Excellent (archival)

**5.1 Surround:**
- AC3: 448k (minimum) - 640k (standard)
- EAC3: 640k (standard) - 1024k (high)
- DTS: 1536k (maximum quality)

---

### Standalone Audio Processing

Process audio without video upscaling.

```bash
# Extract and enhance audio only
python -m vhs_upscaler.audio_processor \
  -i video.mp4 \
  -o enhanced_audio.aac \
  --enhance voice \
  --normalize

# Create 5.1 surround from stereo audio file
python -m vhs_upscaler.audio_processor \
  -i stereo_audio.wav \
  -o surround_audio.eac3 \
  --upmix demucs \
  --layout 5.1 \
  --format eac3

# Full processing pipeline
python -m vhs_upscaler.audio_processor \
  -i noisy_audio.mp3 \
  -o clean_surround.ac3 \
  --enhance aggressive \
  --upmix surround \
  --layout 5.1 \
  --format ac3 \
  --bitrate 640k
```

---

## Troubleshooting

### Problem: Demucs Not Available

**Error Message:**
```
Warning: Demucs not available, falling back to FFmpeg surround
```

**Solution:**
```bash
# Install Demucs
pip install demucs

# Or install with full audio support
pip install -e ".[audio]"

# Verify installation
python -c "import demucs; print('Demucs installed')"
```

---

### Problem: Audio Sounds "Hollow" or "Phasy"

**Cause:** Over-aggressive upmixing or enhancement.

**Solutions:**

1. Use lighter enhancement mode:
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-enhance light  # Instead of aggressive
```

2. Use better upmix algorithm:
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix demucs  # Instead of simple
```

3. Disable upmix if stereo sounds better:
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-layout stereo  # Keep original stereo
```

---

### Problem: Dialogue Too Quiet in Surround Mix

**Cause:** Center channel mix level too low.

**Solution:** Use `voice` enhancement mode or `demucs` upmix:

```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-enhance voice \
  --audio-upmix demucs \
  --audio-layout 5.1
```

**Demucs advantages:**
- Isolates vocals to center channel
- Better dialogue clarity
- Intelligent stem separation

---

### Problem: Distorted Audio / Clipping

**Cause:** Over-normalization or aggressive compression.

**Solutions:**

1. Lower target loudness:
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-target-loudness -16.0  # Instead of -14.0
```

2. Disable normalization:
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --no-audio-normalize
```

3. Use lighter enhancement:
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-enhance light  # Instead of aggressive
```

---

### Problem: Surround Channels Too Loud

**Cause:** Simple upmix creates excessive rear channel content.

**Solutions:**

1. Use better upmix algorithm:
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix surround  # Or prologic instead of simple
```

2. Use Demucs for intelligent separation:
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix demucs
```

---

### Problem: Processing Takes Too Long

**Cause:** Demucs AI processing on CPU.

**Solutions:**

1. Use GPU acceleration:
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix demucs \
  --demucs-device cuda
```

2. Use faster upmix algorithm:
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix surround  # Much faster than demucs
```

3. Use faster Demucs model:
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-upmix demucs \
  --demucs-model htdemucs  # Instead of htdemucs_ft
```

---

### Problem: No Audio in Output

**Cause:** Audio stream not copied or incompatible format.

**Solutions:**

1. Check input has audio:
```bash
ffprobe -i input.mp4
```

2. Use compatible format:
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-format aac  # Universal compatibility
```

3. Check FFmpeg logs for errors (use `-v` verbose flag).

---

### Problem: Audio Out of Sync

**Cause:** Processing altered timing or sample rate mismatch.

**Solution:** Ensure consistent sample rate:

```bash
# Audio processor defaults to 48 kHz (standard for video)
# This should prevent sync issues
vhs-upscale upscale video.mp4 -o output.mp4 \
  --audio-enhance moderate
```

**If sync issues persist:** Report as a bug with input video details.

---

## Quick Reference

### Common Command Patterns

**Clean VHS dialogue:**
```bash
vhs-upscale upscale input.mp4 -o output.mp4 --audio-enhance voice
```

**Create 5.1 from stereo (fast):**
```bash
vhs-upscale upscale input.mp4 -o output.mp4 --audio-upmix surround --audio-layout 5.1 --audio-format ac3
```

**Create 5.1 from stereo (best quality):**
```bash
vhs-upscale upscale input.mp4 -o output.mp4 --audio-upmix demucs --audio-layout 5.1 --audio-format eac3
```

**Maximum quality restoration:**
```bash
vhs-upscale upscale input.mp4 -o output.mkv --audio-enhance moderate --audio-upmix demucs --audio-layout 5.1 --audio-format flac
```

**YouTube upload:**
```bash
vhs-upscale upscale input.mp4 -o output.mp4 --audio-enhance moderate --audio-format aac --audio-bitrate 192k
```

---

## Processing Time Estimates

**5-minute video:**

| Processing | CPU (i7) | GPU (RTX 3060) |
|------------|----------|----------------|
| Enhancement only | ~10 sec | ~10 sec |
| Simple upmix | ~15 sec | ~15 sec |
| Surround upmix | ~20 sec | ~20 sec |
| Pro Logic upmix | ~25 sec | ~25 sec |
| Demucs upmix | ~3-5 min | ~30-60 sec |

**Add video upscaling time:**
- Maxine (RTX GPU): +2-3 minutes
- Real-ESRGAN (Vulkan): +3-5 minutes
- FFmpeg (CPU): +10-15 minutes

---

## Related Documentation

- **Video Analysis**: `docs/ANALYSIS.md`
- **Deinterlacing Guide**: `vhs_upscaler/DEINTERLACE_QUICKSTART.md`
- **Main README**: `README.md`
- **Troubleshooting**: `README.md#troubleshooting`

---

## Support

For issues or questions:
1. Check this guide and main README
2. Review FFmpeg/Demucs logs with `-v` verbose flag
3. Open GitHub issue with:
   - Command used
   - Error messages
   - Input video characteristics
   - System specifications

---

**Last Updated:** 2025-12-18
**Version:** 1.4.2
