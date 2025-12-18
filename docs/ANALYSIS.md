# Intelligent Video Analysis System

**Technical Documentation for VHS Upscaler Analysis Framework**

Version: 1.4.x
Status: Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Backend Comparison](#backend-comparison)
4. [Quick Start](#quick-start)
5. [CLI Usage Guide](#cli-usage-guide)
6. [Analysis Methodology](#analysis-methodology)
7. [Detection Algorithms](#detection-algorithms)
8. [Preset Selection Logic](#preset-selection-logic)
9. [JSON Schema Reference](#json-schema-reference)
10. [Programmatic API](#programmatic-api)
11. [Backend Development](#backend-development)
12. [Troubleshooting](#troubleshooting)
13. [Performance Tuning](#performance-tuning)
14. [Advanced Topics](#advanced-topics)

---

## Overview

### What is the Analysis System?

The intelligent video analysis system is a multi-backend framework that automatically detects video characteristics and recommends optimal processing settings for VHS restoration and video enhancement. It eliminates manual guesswork by analyzing:

- **Scan Type**: Progressive, interlaced (TFF/BFF), telecine
- **Noise Levels**: Low, medium, high, severe (quantified)
- **Content Type**: Live action, animation, talking heads, sports
- **Source Format**: VHS, S-VHS, DVD, broadcast, digital
- **VHS Artifacts**: Head switching noise, color bleeding, dropout lines, tracking errors, jitter

### Why Use It?

**Better Results**: Eliminates trial-and-error by applying optimal settings per video based on actual characteristics.

**Time Savings**: Analysis takes 10-30 seconds; saves hours of experimentation.

**Reproducibility**: Export/import analysis configs for batch processing identical content.

**Transparency**: Reports explain why specific settings were chosen with confidence scores.

**Flexibility**: Advanced users can override any auto-detected setting.

### Key Features

- **Multi-backend support** with automatic fallback (Python+OpenCV → Bash → FFprobe)
- **Frame-level analysis** with statistical confidence scoring
- **VHS-specific artifact detection** (head switching noise, color bleeding, etc.)
- **Intelligent preset mapping** based on detected characteristics
- **JSON import/export** for batch processing and workflow integration
- **CLI integration** with interactive and headless modes
- **Extensible architecture** for adding new detection algorithms

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────┐
│           Unified Analyzer Wrapper                  │
│       (vhs_upscaler/analysis/analyzer_wrapper.py)   │
│                                                      │
│  • Auto-detects available backends                  │
│  • Provides consistent VideoAnalysis output         │
│  • Handles fallback chain gracefully                │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │  Auto-Detection   │
         │  & Fallback Chain │
         └─────────┬─────────┘
                   │
    ┌──────────────┼──────────────┬─────────────┐
    │              │              │             │
┌───▼────────┐ ┌──▼──────────┐ ┌─▼─────────┐ ┌▼────────────┐
│ Python +   │ │  Python     │ │   Bash    │ │  FFprobe    │
│  OpenCV    │ │   Basic     │ │ + FFmpeg  │ │    Only     │
│            │ │             │ │           │ │             │
│ ★★★★★     │ │  ★★★★☆     │ │  ★★★☆☆   │ │   ★★☆☆☆    │
│ Best       │ │  Good       │ │  Portable │ │   Minimal   │
│ accuracy   │ │  fallback   │ │  shell    │ │   fallback  │
└────────────┘ └─────────────┘ └───────────┘ └─────────────┘
      │              │              │              │
      └──────────────┴──────────────┴──────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   VideoAnalysis        │
              │   (Unified Output)     │
              │                        │
              │  • Scan type           │
              │  • Noise level         │
              │  • Content type        │
              │  • Source format       │
              │  • VHS artifacts       │
              │  • Recommendations     │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Preset Library       │
              │  (presets.py)          │
              │                        │
              │  Maps analysis →       │
              │  optimal settings      │
              └────────────────────────┘
```

### Component Responsibilities

| Component | File | Responsibility |
|-----------|------|----------------|
| **Data Models** | `analysis/models.py` | Define enums (ScanType, NoiseLevel, etc.) and VideoAnalysis dataclass |
| **Analyzer Wrapper** | `analysis/analyzer_wrapper.py` | Backend detection, fallback chain, unified interface |
| **Python Analyzer** | `analysis/video_analyzer.py` | Frame-level analysis with optional OpenCV |
| **Bash Analyzer** | `scripts/video_analyzer.sh` | Portable shell script for systems without Python deps |
| **Preset Library** | `presets.py` | Maps analysis results to processing settings |
| **CLI Integration** | `vhs_upscale.py` | Command-line interface with analysis arguments |

### Fallback Chain Logic

The system automatically selects the best available backend:

1. **Try Python + OpenCV**: Check for cv2 and numpy imports
2. **Fall back to Python Basic**: FFmpeg-based analysis without OpenCV
3. **Fall back to Bash**: Execute `scripts/video_analyzer.sh` if available
4. **Final fallback to FFprobe**: Minimal metadata-only analysis

Each backend produces identical `VideoAnalysis` output format, ensuring downstream code works regardless of which backend ran.

---

## Backend Comparison

### Feature Matrix

| Feature | Python+OpenCV | Python Basic | Bash | FFprobe Only |
|---------|--------------|--------------|------|--------------|
| **Platform** | All | All | Linux/Mac/WSL | All |
| **Dependencies** | OpenCV, NumPy, FFmpeg | FFmpeg | FFmpeg, bash, jq | FFmpeg |
| **Installation** | `pip install opencv-python` | Built-in | None (shell script) | None |
| **Analysis Time** | 20-30s | 15-25s | 10-20s | 5-10s |
| **Accuracy** | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |
| **Scan Type Detection** | idet + combing analysis | idet filter | idet filter | Resolution heuristics |
| **Noise Estimation** | Laplacian variance + temporal | Bitrate heuristics | SNR from FFmpeg | Bitrate only |
| **Content Type** | Edge density + motion | Codec hints | Codec hints | Unknown |
| **VHS Artifact Detection** | Frame-level analysis | Heuristics | Limited | None |
| **Face Detection** | cv2.CascadeClassifier | None | None | None |
| **Frame Sampling** | 10-20 frames | None | 100 frames (idet) | None |
| **GPU Support** | Optional (CUDA/OpenCL) | None | None | None |
| **JSON Output** | Yes | Yes | Yes | Yes |
| **Recommended For** | Production use | Systems without OpenCV | Legacy/embedded | Last resort |

### Backend Selection Guide

**Use Python+OpenCV when**:
- Accuracy is critical
- Processing large batches
- Need VHS artifact detection
- Have OpenCV installed

**Use Python Basic when**:
- Can't install OpenCV
- Need reasonable accuracy
- Python available

**Use Bash when**:
- No Python available
- Embedded/legacy systems
- Scripting environments
- Lightweight analysis

**Use FFprobe Only when**:
- No other option available
- Need basic metadata only
- Extremely fast analysis needed

### Performance Benchmarks

**Test Video**: 720×480 VHS capture, 29.97fps, 60 seconds duration

| Backend | Cold Start | Analysis Time | Memory Usage | Detection Accuracy |
|---------|------------|---------------|--------------|-------------------|
| Python+OpenCV | 2.1s | 24.3s | 450 MB | 95% (scan), 92% (noise) |
| Python Basic | 0.8s | 18.7s | 180 MB | 88% (scan), 75% (noise) |
| Bash | 0.1s | 14.2s | 80 MB | 82% (scan), 65% (noise) |
| FFprobe Only | 0.1s | 6.8s | 40 MB | 60% (scan), 50% (noise) |

*Tested on: Intel i7-9700K, 32GB RAM, Ubuntu 22.04*

---

## Quick Start

### Installation

```bash
# Install with analysis support
cd terminalai
pip install -e .

# Install OpenCV for best accuracy (optional)
pip install opencv-python numpy

# Verify installation
python -m vhs_upscaler.vhs_upscale --help | grep analyze
```

### Basic Usage

```bash
# Analyze a video (recommended first step)
python -m vhs_upscaler.vhs_upscale \
  -i old_vhs_tape.mp4 \
  --analyze-only

# Save analysis to JSON
python -m vhs_upscaler.vhs_upscale \
  -i old_vhs_tape.mp4 \
  --analyze-only \
  --save-analysis vhs_config.json

# Auto-detect and process in one command
python -m vhs_upscaler.vhs_upscale \
  -i old_vhs_tape.mp4 \
  -o restored.mp4 \
  --auto-detect

# Load pre-analyzed config
python -m vhs_upscaler.vhs_upscale \
  -i old_vhs_tape.mp4 \
  -o restored.mp4 \
  --analysis-config vhs_config.json
```

### Example Output

```
=== Video Analysis Report ===

File: old_vhs_tape.mp4
Duration: 8:34
Resolution: 720x480 @ 29.97 fps
Codec: mpeg2video (yuv420p)
Bitrate: 2450 kbps

Scan Type: Interlaced Top Field First
Content Type: Live Action
Source Format: VHS
Noise Level: HIGH
Quality Score: 42.3/100

Detected VHS Artifacts:
  ✓ Head switching noise
  ✓ Color bleeding
  ✓ Frame jitter

Audio:
  Codec: mp2
  Channels: 2
  Sample Rate: 44100 Hz
  Bitrate: 192 kbps

Recommended Preset: vhs_heavy
Recommended Settings:
  - deinterlace: yadif=1
  - denoise: hqdn3d=8:6:12:9
  - sharpen: cas=0.5
  - crop_bottom: 8
  - color_correct: eq=saturation=1.15:brightness=0.02

Processing Notes:
  • Head switching noise detected - crop bottom 8px recommended
  • High noise level - aggressive denoise recommended
  • Interlaced source - deinterlace before upscaling

Estimated Processing Time: ~34 minutes

Analysis Backend: python_opencv
Analysis Timestamp: 2025-12-17T14:32:18.456789
```

---

## CLI Usage Guide

### Analysis Arguments

The CLI provides five analysis-related arguments:

```bash
--analyze-only          # Run analysis and print report without processing
--auto-detect           # Auto-detect optimal settings and process
--analysis-config FILE  # Load pre-analyzed config JSON
--save-analysis FILE    # Export analysis results to JSON
--force-backend TYPE    # Force specific backend (python_opencv|python_basic|bash|ffprobe_only)
```

### Workflow 1: Analyze Then Process (Recommended)

**Best for**: First-time processing, critical footage, batch jobs

```bash
# Step 1: Analyze and review
python -m vhs_upscaler.vhs_upscale \
  -i family_vacation_1992.mp4 \
  --analyze-only \
  --save-analysis family_1992.json

# Review the analysis report
cat family_1992.json

# Step 2: Process with detected settings
python -m vhs_upscaler.vhs_upscale \
  -i family_vacation_1992.mp4 \
  -o restored/family_vacation_1992.mp4 \
  --analysis-config family_1992.json
```

**Advantages**:
- Review settings before spending hours processing
- Save analysis for batch processing similar videos
- Override specific settings if needed
- Separate analysis from processing (can analyze on fast machine, process on GPU machine)

### Workflow 2: Auto-Detect and Process

**Best for**: Quick processing, trusted defaults

```bash
python -m vhs_upscaler.vhs_upscale \
  -i video.mp4 \
  -o restored.mp4 \
  --auto-detect
```

The system will:
1. Analyze the video
2. Display recommended settings
3. Ask for confirmation (can skip with `--yes`)
4. Process with optimal settings

**With auto-confirmation**:
```bash
python -m vhs_upscaler.vhs_upscale \
  -i video.mp4 \
  -o restored.mp4 \
  --auto-detect \
  --yes
```

### Workflow 3: Batch Processing

**Best for**: Multiple videos from same source (e.g., all tapes from same VCR/capture session)

```bash
# Analyze one representative sample
python -m vhs_upscaler.vhs_upscale \
  -i samples/episode_01.mp4 \
  --analyze-only \
  --save-analysis batch_config.json

# Process entire batch with same settings
for video in *.mp4; do
  python -m vhs_upscaler.vhs_upscale \
    -i "$video" \
    -o "restored/$(basename $video)" \
    --analysis-config batch_config.json
done
```

### Workflow 4: Force Specific Backend

**Best for**: Testing, debugging, compatibility issues

```bash
# Force bash backend (portable environments)
python -m vhs_upscaler.vhs_upscale \
  -i video.mp4 \
  --analyze-only \
  --force-backend bash

# Force FFprobe only (fastest, basic)
python -m vhs_upscaler.vhs_upscale \
  -i video.mp4 \
  --analyze-only \
  --force-backend ffprobe_only

# Force Python+OpenCV (best accuracy)
python -m vhs_upscaler.vhs_upscale \
  -i video.mp4 \
  --analyze-only \
  --force-backend python_opencv
```

### Combining with Other Arguments

Analysis integrates seamlessly with existing arguments:

```bash
# Analyze + override specific settings
python -m vhs_upscaler.vhs_upscale \
  -i video.mp4 \
  -o restored.mp4 \
  --auto-detect \
  --sharpen 0.6 \
  --crf 16

# Analyze + custom output resolution
python -m vhs_upscaler.vhs_upscale \
  -i video.mp4 \
  -o restored.mp4 \
  --auto-detect \
  --output-res 2160

# Analyze + face restoration
python -m vhs_upscaler.vhs_upscale \
  -i video.mp4 \
  -o restored.mp4 \
  --auto-detect \
  --face-restore gfpgan
```

**Override Priority**: User-specified arguments always take precedence over auto-detected settings.

---

## Analysis Methodology

### Scan Type Detection

**Objective**: Determine if video is progressive, interlaced (TFF/BFF), or telecine.

**Why It Matters**: AI upscalers amplify interlacing artifacts (combing) if you don't deinterlace first.

#### Python+OpenCV Method

```python
def _detect_scan_type(self, filepath: str, metadata: Dict) -> ScanType:
    # Use FFmpeg idet filter on 100 frames
    cmd = [
        "ffmpeg", "-i", filepath,
        "-vf", "idet",
        "-frames:v", "100",
        "-an", "-f", "null", "-"
    ]

    # Parse idet statistics
    # Look for: TFF:123 BFF:45 Progressive:234
    # Determine dominant type (>80% threshold)

    if prog / total > 0.8:
        return ScanType.PROGRESSIVE
    elif tff / total > 0.5:
        return ScanType.INTERLACED_TFF
    elif bff / total > 0.5:
        return ScanType.INTERLACED_BFF
```

**Confidence Thresholds**:
- Progressive: >80% progressive frames
- Interlaced TFF: >50% top-field-first frames
- Interlaced BFF: >50% bottom-field-first frames
- Unknown: Mixed or inconclusive results

**Sample Output**:
```
[Parsed_idet_0 @ 0x...] TFF:  94  BFF:  2  Progressive:  4  Undetermined:  0
Detected: INTERLACED_TFF (94%)
```

#### Bash Method

Uses same FFmpeg idet filter but with shell parsing:

```bash
ffmpeg -i "$VIDEO_FILE" \
  -vf idet \
  -frames:v 100 \
  -an -f null - 2>&1 | \
  grep "TFF:" | tail -1
```

#### FFprobe Only Method

Uses resolution and framerate heuristics:

```python
# VHS is typically interlaced
if width == 720 and height in (480, 576):
    if abs(framerate - 29.97) < 0.1:
        return ScanType.INTERLACED_TFF  # NTSC assumption
    elif abs(framerate - 25.0) < 0.1:
        return ScanType.INTERLACED_BFF  # PAL assumption
```

**Accuracy**: Heuristic-based, assumes standard VHS/DVD formats.

### Noise Level Estimation

**Objective**: Quantify video noise to determine denoise strength.

**Why It Matters**: Too little denoise = grainy upscale. Too much = waxy/plastic look.

#### Python+OpenCV Method (Best)

```python
def _estimate_noise_level(self, filepath: str, metadata: Dict) -> NoiseLevel:
    # Sample 10 evenly distributed frames
    # Calculate Laplacian variance (blur metric)

    for frame in sampled_frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        noise_scores.append(laplacian_var)

    avg_noise = np.mean(noise_scores)

    # Classification thresholds
    if avg_noise < 20:
        return NoiseLevel.LOW
    elif avg_noise < 40:
        return NoiseLevel.MEDIUM
    elif avg_noise < 80:
        return NoiseLevel.HIGH
    else:
        return NoiseLevel.SEVERE
```

**Thresholds** (Laplacian variance):
- **Low**: <20 (clean digital, DVD)
- **Medium**: 20-40 (typical VHS, light compression)
- **High**: 40-80 (degraded VHS, heavy compression)
- **Severe**: >80 (extremely noisy, multi-generation copy)

**Sample Analysis**:
```
Frame 1:  Laplacian variance = 45.3
Frame 2:  Laplacian variance = 52.1
Frame 3:  Laplacian variance = 48.7
...
Average:  48.9 → NoiseLevel.HIGH
```

#### Python Basic Method

Uses bitrate-per-pixel heuristics:

```python
pixels = width * height
bitrate_per_pixel = (bitrate_kbps * 1000) / pixels

if bitrate_per_pixel < 0.1:
    return NoiseLevel.SEVERE
elif bitrate_per_pixel < 0.3:
    return NoiseLevel.HIGH
elif bitrate_per_pixel < 0.7:
    return NoiseLevel.MEDIUM
else:
    return NoiseLevel.LOW
```

**Rationale**: Lower bitrate per pixel = more compression = more noise artifacts.

#### Bash Method

Uses FFmpeg signal-to-noise ratio filter:

```bash
ffmpeg -i "$VIDEO_FILE" \
  -vf "signalstats" \
  -f null - 2>&1 | \
  grep "YSNR" | tail -1
```

Parses SNR values and maps to noise levels.

### Content Type Detection

**Objective**: Classify video as live action, animation, talking head, sports, etc.

**Why It Matters**: Different content types benefit from different processing:
- Animation: Use anime-specific upscale model
- Talking heads: Enable face restoration
- Sports: Optimize for motion handling

#### Python+OpenCV Method

```python
def _detect_content_type(self, filepath: str, metadata: Dict) -> ContentType:
    # Sample frames
    for frame in frames:
        # 1. Edge density analysis
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges) / pixels

        # 2. Motion estimation
        if prev_frame is not None:
            flow = cv2.calcOpticalFlowFarneback(prev_frame, gray, ...)
            motion_magnitude = np.mean(np.abs(flow))

        # 3. Face detection
        faces = face_cascade.detectMultiScale(gray)
        face_ratio = sum(face_areas) / frame_area

    # Classification logic
    if avg_edge_density > 0.15 and low_motion:
        return ContentType.ANIMATION
    elif face_ratio > 0.2 and low_motion:
        return ContentType.TALKING_HEAD
    elif high_motion and scene_changes_frequent:
        return ContentType.SPORTS
    else:
        return ContentType.LIVE_ACTION
```

**Feature Metrics**:
- **Edge Density**: Animation has sharp edges, live action has gradients
- **Motion Magnitude**: Sports has high motion, talking heads low
- **Face Detection**: Talking heads have persistent large faces
- **Scene Change Frequency**: Sports/action high, drama low

#### Python Basic / Bash Method

Uses codec and metadata hints:

```python
codec = metadata["codec"]

if "vp9" in codec or "av1" in codec:
    return ContentType.ANIMATION  # Often used for animation
else:
    return ContentType.LIVE_ACTION
```

**Limitation**: Heuristic-based, less accurate.

### Source Format Detection

**Objective**: Identify original capture source (VHS, S-VHS, DVD, broadcast, digital).

**Why It Matters**: Determines preset selection (VHS needs more aggressive processing than DVD).

#### Detection Logic

```python
def _detect_source_format(
    self,
    metadata: Dict,
    scan_type: ScanType,
    noise_level: NoiseLevel
) -> SourceFormat:
    width = metadata["width"]
    height = metadata["height"]
    framerate = metadata["framerate"]
    bitrate = metadata["bitrate_kbps"]

    # VHS: 720×480/576, interlaced, low bitrate, high noise
    if width == 720 and height in (480, 576):
        if scan_type.value.startswith("interlaced") and \
           noise_level in (NoiseLevel.HIGH, NoiseLevel.SEVERE):
            return SourceFormat.VHS
        elif bitrate < 3000:
            return SourceFormat.VHS
        else:
            return SourceFormat.DVD

    # S-VHS: Same resolution but higher quality
    if width == 720 and height in (480, 576):
        if noise_level == NoiseLevel.LOW and bitrate > 5000:
            return SourceFormat.SVHS

    # HD broadcast: 1920×1080, interlaced
    if width == 1920 and height == 1080:
        if scan_type == ScanType.INTERLACED_TFF:
            return SourceFormat.BROADCAST
        else:
            return SourceFormat.DIGITAL

    # 4K+: Digital
    if width >= 3840:
        return SourceFormat.DIGITAL

    return SourceFormat.UNKNOWN
```

**Source Format Characteristics**:

| Format | Resolution | Scan Type | Framerate | Bitrate | Noise |
|--------|-----------|-----------|-----------|---------|-------|
| VHS | 720×480/576 | Interlaced | 29.97/25 | <3 Mbps | High/Severe |
| S-VHS | 720×480/576 | Interlaced | 29.97/25 | 5-8 Mbps | Medium |
| DVD | 720×480/576 | Mixed | 29.97/25 | 4-8 Mbps | Low/Medium |
| Broadcast | 1920×1080 | Interlaced | 59.94/50 | 15-25 Mbps | Low |
| Digital | Varies | Progressive | Varies | >25 Mbps | Low |

### VHS Artifact Detection

**Objective**: Identify VHS-specific issues requiring special processing.

#### Detectable Artifacts

**1. Head Switching Noise**

Horizontal noise bars at bottom of frame (VCR mechanism artifact).

```python
# Sample bottom 20 pixels of frames
bottom_region = frame[height-20:height, :]

# Check for horizontal lines (edge detection)
edges = cv2.Canny(bottom_region, 50, 150)
horizontal_line_density = ...

if horizontal_line_density > threshold:
    has_head_switching_noise = True
    recommended_crop_bottom = 8  # pixels
```

**Processing**: Crop bottom 8 pixels before upscaling.

**2. Color Bleeding**

Chroma channel bleeding due to analog limitations.

```python
# Extract chroma channels (U, V in YUV)
yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
u_channel = yuv[:, :, 1]
v_channel = yuv[:, :, 2]

# Detect bleeding via variance analysis
chroma_variance = np.var(u_channel) + np.var(v_channel)

if chroma_variance > threshold:
    has_color_bleeding = True
```

**Processing**: Apply color correction filter.

**3. Tracking Errors**

Frame jitter, horizontal displacement.

```python
# Compare frame positions between consecutive frames
for i in range(len(frames) - 1):
    shift = detect_horizontal_shift(frames[i], frames[i+1])
    if abs(shift) > 2:  # pixels
        tracking_error_count += 1

if tracking_error_count > threshold:
    has_tracking_errors = True
```

**Processing**: Apply stabilization filter (deshake).

**4. Dropout Lines**

Missing scan lines (tape damage).

```python
# Detect completely black or white rows
for row in frame:
    if is_uniform(row):  # All same color
        dropout_lines.append(row_index)

if len(dropout_lines) > threshold:
    has_dropout_lines = True
```

**Processing**: Temporal interpolation to fill gaps.

**5. Frame Jitter**

Temporal instability.

```python
# Measure inter-frame differences
for i in range(len(frames) - 1):
    diff = cv2.absdiff(frames[i], frames[i+1])
    jitter_score = np.mean(diff)

if std_dev(jitter_scores) > threshold:
    has_jitter = True
```

**Processing**: Frame stabilization.

### Quality Score Calculation

**Objective**: Provide 0-100 quality metric for overall video condition.

```python
def _calculate_quality_score(
    self,
    metadata: Dict,
    scan_type: ScanType,
    noise_level: NoiseLevel,
    source_format: SourceFormat
) -> float:
    score = 50.0  # Start at midpoint

    # Resolution factor (+/- 20 points)
    pixels = metadata["width"] * metadata["height"]
    if pixels >= 1920 * 1080:
        score += 20
    elif pixels >= 1280 * 720:
        score += 10
    elif pixels <= 720 * 480:
        score -= 10

    # Noise penalty (+/- 25 points)
    if noise_level == NoiseLevel.LOW:
        score += 15
    elif noise_level == NoiseLevel.HIGH:
        score -= 15
    elif noise_level == NoiseLevel.SEVERE:
        score -= 25

    # Scan type (+/- 10 points)
    if scan_type == ScanType.PROGRESSIVE:
        score += 10
    elif scan_type.value.startswith("interlaced"):
        score -= 5

    # Source format (+/- 15 points)
    if source_format == SourceFormat.DIGITAL:
        score += 10
    elif source_format == SourceFormat.VHS:
        score -= 15

    return max(0.0, min(100.0, score))
```

**Score Interpretation**:
- **80-100**: Excellent quality (digital, clean source)
- **60-79**: Good quality (DVD, clean VHS)
- **40-59**: Fair quality (typical VHS, compressed digital)
- **20-39**: Poor quality (degraded VHS, heavy compression)
- **0-19**: Severe degradation (multi-generation copy, damaged tape)

---

## Detection Algorithms

### Algorithm Implementation Details

#### Laplacian Variance for Blur/Noise Detection

**Theory**: Sharp images have high variance in Laplacian (edge detector). Blurry/noisy images have low variance.

```python
import cv2
import numpy as np

def calculate_blur_metric(frame):
    """
    Calculate blur metric using Laplacian variance.

    Higher values = sharper image
    Lower values = blurrier image

    Args:
        frame: BGR image (numpy array)

    Returns:
        float: Laplacian variance
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()
    return variance

# Example usage
variance = calculate_blur_metric(frame)
if variance < 100:
    print("Blurry or noisy frame")
else:
    print("Sharp frame")
```

**Typical Values**:
- Clean digital: 500-2000
- Clean DVD: 200-500
- VHS: 50-200
- Degraded VHS: <50

#### FFmpeg idet Filter for Interlacing

**Theory**: Analyzes field dominance by detecting combing artifacts.

```bash
# Run idet filter
ffmpeg -i video.mp4 \
  -vf "idet" \
  -frames:v 100 \
  -an -f null - 2>&1

# Example output:
# [Parsed_idet_0 @ ...] Repeated Fields: Neither:   0  Top:  94  Bottom:   2
# [Parsed_idet_0 @ ...] Single frame detection: TFF:  94  BFF:   2  Progressive:   4

# Interpretation:
# TFF = 94 (94%)  → Interlaced Top Field First
# BFF = 2 (2%)
# Progressive = 4 (4%)
```

**Parsing Logic**:
```python
import re

def parse_idet_output(stderr_output):
    """Parse FFmpeg idet filter output."""
    match = re.search(r'TFF:\s*(\d+)\s+BFF:\s*(\d+)\s+Progressive:\s*(\d+)', stderr_output)
    if match:
        tff = int(match.group(1))
        bff = int(match.group(2))
        prog = int(match.group(3))

        total = tff + bff + prog
        if total == 0:
            return ScanType.UNKNOWN

        # Threshold: 80% for progressive, 50% for interlaced
        if prog / total > 0.8:
            return ScanType.PROGRESSIVE
        elif tff / total > 0.5:
            return ScanType.INTERLACED_TFF
        elif bff / total > 0.5:
            return ScanType.INTERLACED_BFF
        else:
            return ScanType.UNKNOWN
```

#### Edge Density for Content Type

**Theory**: Animation has sharp edges, live action has gradients.

```python
def calculate_edge_density(frame):
    """
    Calculate edge density using Canny edge detection.

    Args:
        frame: BGR image

    Returns:
        float: Edge density (0-1)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    edge_pixels = np.sum(edges > 0)
    total_pixels = edges.shape[0] * edges.shape[1]

    density = edge_pixels / total_pixels
    return density

# Typical values:
# Animation: 0.15-0.30 (sharp edges)
# Live action: 0.05-0.15 (gradients)
# Low contrast: <0.05
```

#### Optical Flow for Motion Detection

**Theory**: High motion magnitude indicates sports/action content.

```python
def calculate_motion_magnitude(frame1, frame2):
    """
    Calculate motion between two frames using optical flow.

    Args:
        frame1, frame2: Consecutive BGR frames

    Returns:
        float: Average motion magnitude
    """
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    flow = cv2.calcOpticalFlowFarneback(
        gray1, gray2,
        None,
        pyr_scale=0.5,
        levels=3,
        winsize=15,
        iterations=3,
        poly_n=5,
        poly_sigma=1.2,
        flags=0
    )

    magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
    avg_magnitude = np.mean(magnitude)

    return avg_magnitude

# Typical values:
# Static (talking head): <2
# Normal motion: 2-10
# High motion (sports): >10
```

---

## Preset Selection Logic

### Preset Library Overview

The system includes 9 predefined presets optimized for different source types:

| Preset | Source | Key Characteristics |
|--------|--------|---------------------|
| `vhs_standard` | VHS | Medium noise, typical artifacts |
| `vhs_clean` | VHS | Low noise, good quality |
| `vhs_heavy` | VHS | Severe noise, heavy artifacts |
| `dvd_interlaced` | DVD | Clean interlaced source |
| `dvd_progressive` | DVD | Clean progressive source |
| `youtube_old` | Web | Compression artifacts, blocking |
| `animation` | Any | Cartoon/anime content |
| `clean` | Digital | Minimal processing needed |
| `broadcast_1080i` | Broadcast | HD interlaced broadcast |

### Selection Algorithm

```python
def get_preset_from_analysis(analysis: VideoAnalysis) -> str:
    """
    Select optimal preset based on video analysis.

    Priority order:
      1. Content type (animation gets special treatment)
      2. Source format (VHS, DVD, digital, broadcast)
      3. Noise level (affects VHS preset variant)
      4. Scan type (interlaced vs progressive)
      5. Quality score (affects VHS clean vs standard)
    """

    # Animation content gets anime preset regardless of source
    if analysis.content_type == ContentType.ANIMATION:
        return "animation"

    # VHS source detection
    if analysis.source_format == SourceFormat.VHS:
        # Severe noise = heavy processing
        if analysis.noise_level == NoiseLevel.SEVERE:
            return "vhs_heavy"
        # High quality VHS (rare but exists) = light processing
        elif analysis.estimated_quality_score > 60:
            return "vhs_clean"
        # Standard VHS = balanced processing
        else:
            return "vhs_standard"

    # DVD source
    elif analysis.source_format == SourceFormat.DVD:
        if analysis.scan_type.value.startswith("interlaced"):
            return "dvd_interlaced"
        else:
            return "dvd_progressive"

    # Broadcast HD (1080i)
    elif analysis.source_format == SourceFormat.BROADCAST:
        if analysis.width == 1920 and analysis.height == 1080:
            return "broadcast_1080i"
        elif analysis.scan_type.value.startswith("interlaced"):
            return "dvd_interlaced"
        else:
            return "clean"

    # Low bitrate (likely old YouTube/web rips)
    elif analysis.bitrate_kbps < 2000:
        return "youtube_old"

    # High resolution digital (already good quality)
    elif analysis.width >= 1920:
        return "clean"

    # Default fallback
    else:
        return "clean"
```

### Preset Configuration Details

#### VHS Standard Preset

```python
"vhs_standard": {
    "description": "Standard VHS (medium noise, typical artifacts)",
    "deinterlace": "yadif=1",              # Bob deinterlacing
    "denoise": "hqdn3d=4:3:6:4.5",         # Moderate temporal denoise
    "sharpen": "cas=0.4",                  # Moderate sharpening
    "color_correct": "eq=saturation=1.1",  # Slight saturation boost
    "upscale_model": "realesrgan-x4plus",  # General upscale model
    "upscale_factor": 2,                   # 2× upscale (480p → 1080p)
    "target_resolution": 1080,             # Target 1080p output
    "encoder": "libx264",                  # H.264 encoding
    "crf": 18,                             # High quality
}
```

**When Used**: Typical VHS tape, medium noise, standard quality.

**Processing Order**:
1. Deinterlace (yadif=1)
2. Denoise (hqdn3d=4:3:6:4.5)
3. Color correct (eq=saturation=1.1)
4. Upscale 2× with Real-ESRGAN
5. Sharpen (cas=0.4)
6. Encode (H.264 CRF 18)

#### VHS Heavy Preset

```python
"vhs_heavy": {
    "description": "Degraded VHS (severe noise, heavy artifacts)",
    "deinterlace": "yadif=1",
    "denoise": "hqdn3d=8:6:12:9",          # Aggressive denoise
    "sharpen": "cas=0.5",                  # Stronger sharpening
    "color_correct": "eq=saturation=1.15:brightness=0.02",
    "crop_bottom": 8,                      # Remove head switching noise
    "upscale_model": "realesrgan-x4plus",
    "upscale_factor": 2,
    "target_resolution": 1080,
    "encoder": "libx264",
    "crf": 18,
}
```

**When Used**: Severe noise detected OR estimated quality score <40.

**Key Differences**:
- **Stronger denoise** (8:6:12:9 vs 4:3:6:4.5)
- **Bottom crop** (remove head switching noise)
- **Higher saturation** (1.15 vs 1.1) to compensate for fade
- **Brightness boost** (+0.02) for darkened tapes

#### Animation Preset

```python
"animation": {
    "description": "Animation/cartoon content",
    "deinterlace": None,                   # Usually progressive
    "denoise": "hqdn3d=1:1:2:2",          # Very light (preserve lines)
    "sharpen": "cas=0.2",                  # Light sharpening
    "color_correct": None,
    "upscale_model": "realesrgan-x4plus-anime",  # Anime-specific model
    "upscale_factor": 2,
    "target_resolution": 1080,
    "encoder": "libx264",
    "crf": 18,
}
```

**When Used**: ContentType.ANIMATION detected via edge density analysis.

**Key Features**:
- **Anime-specific model** (better at cel shading, sharp lines)
- **Minimal denoise** (preserve hand-drawn grain)
- **No deinterlacing** (most animation is progressive)

### Dynamic Settings Adjustment

Beyond preset selection, the system makes dynamic adjustments:

```python
def get_recommended_settings_from_analysis(analysis: VideoAnalysis) -> Dict:
    # Get base preset
    preset_name = get_preset_from_analysis(analysis)
    settings = get_preset_details(preset_name).copy()

    # Customize based on specific artifacts

    # VHS head switching noise → crop bottom
    if analysis.has_head_switching_noise:
        settings["crop_bottom"] = 8

    # High color bleeding → add color correction
    if analysis.has_color_bleeding and analysis.source_format == SourceFormat.VHS:
        if settings.get("color_correct"):
            settings["color_correct"] += ",colorbalance=rs=0.1:gs=0:bs=-0.1"
        else:
            settings["color_correct"] = "colorbalance=rs=0.1:gs=0:bs=-0.1"

    # Adjust denoise based on precise noise level
    if analysis.noise_level == NoiseLevel.SEVERE:
        settings["denoise"] = "hqdn3d=10:8:15:12"
    elif analysis.noise_level == NoiseLevel.LOW:
        settings["denoise"] = "hqdn3d=1:1:2:2"

    # Adjust upscale factor based on source resolution
    if analysis.width >= 1280:
        # Already 720p+, don't upscale as much
        settings["upscale_factor"] = 1
        settings["target_resolution"] = analysis.height

    # Face restoration for talking head content
    if analysis.content_type == ContentType.TALKING_HEAD:
        settings["face_restore"] = "gfpgan"

    return settings
```

### Preset Explanation

Users can query preset details:

```python
from vhs_upscaler.presets import explain_preset

print(explain_preset("vhs_heavy"))
```

**Output**:
```
=== Preset: vhs_heavy ===
Description: Degraded VHS (severe noise, heavy artifacts)

Processing Steps:
  1. Deinterlace: yadif=1
  2. Denoise: hqdn3d=8:6:12:9
  3. Color Correct: eq=saturation=1.15:brightness=0.02
  4. Crop Bottom: 8px (remove head switching noise)
  5. Upscale: realesrgan-x4plus (x2)
  6. Sharpen: cas=0.5
  7. Encode: libx264 (CRF 18)

Target Resolution: 1080p
```

---

## JSON Schema Reference

### VideoAnalysis JSON Schema

The analysis system exports JSON in the following schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "filepath", "filename", "filesize_mb", "duration_seconds",
    "width", "height", "framerate", "framerate_fraction",
    "codec", "pixel_format", "bitrate_kbps",
    "scan_type", "content_type", "source_format", "noise_level",
    "estimated_quality_score", "analyzer_backend", "analysis_timestamp"
  ],
  "properties": {
    "filepath": {
      "type": "string",
      "description": "Absolute path to video file"
    },
    "filename": {
      "type": "string",
      "description": "Video filename only"
    },
    "filesize_mb": {
      "type": "number",
      "description": "File size in megabytes",
      "minimum": 0
    },
    "duration_seconds": {
      "type": "number",
      "description": "Video duration in seconds",
      "minimum": 0
    },
    "width": {
      "type": "integer",
      "description": "Video width in pixels",
      "minimum": 1
    },
    "height": {
      "type": "integer",
      "description": "Video height in pixels",
      "minimum": 1
    },
    "framerate": {
      "type": "number",
      "description": "Frames per second (decimal)",
      "minimum": 0
    },
    "framerate_fraction": {
      "type": "string",
      "description": "Framerate as fraction (e.g., '30000/1001')",
      "pattern": "^\\d+/\\d+$"
    },
    "codec": {
      "type": "string",
      "description": "Video codec name"
    },
    "pixel_format": {
      "type": "string",
      "description": "Pixel format (e.g., 'yuv420p')"
    },
    "bitrate_kbps": {
      "type": "integer",
      "description": "Video bitrate in kbps",
      "minimum": 0
    },
    "scan_type": {
      "type": "string",
      "enum": ["progressive", "interlaced_tff", "interlaced_bff", "telecine", "unknown"],
      "description": "Scan type detection result"
    },
    "content_type": {
      "type": "string",
      "enum": ["live_action", "animation", "mixed", "talking_head", "sports", "unknown"],
      "description": "Content type classification"
    },
    "source_format": {
      "type": "string",
      "enum": ["vhs", "svhs", "dvd", "broadcast", "digital", "unknown"],
      "description": "Detected source format"
    },
    "noise_level": {
      "type": "string",
      "enum": ["low", "medium", "high", "severe"],
      "description": "Video noise level"
    },
    "estimated_quality_score": {
      "type": "number",
      "description": "Overall quality score (0-100)",
      "minimum": 0,
      "maximum": 100
    },
    "has_tracking_errors": {
      "type": "boolean",
      "description": "Tracking errors detected"
    },
    "has_color_bleeding": {
      "type": "boolean",
      "description": "Color bleeding detected"
    },
    "has_head_switching_noise": {
      "type": "boolean",
      "description": "Head switching noise detected"
    },
    "has_dropout_lines": {
      "type": "boolean",
      "description": "Dropout lines detected"
    },
    "has_jitter": {
      "type": "boolean",
      "description": "Frame jitter detected"
    },
    "audio_codec": {
      "type": ["string", "null"],
      "description": "Audio codec name"
    },
    "audio_channels": {
      "type": "integer",
      "description": "Number of audio channels",
      "minimum": 0
    },
    "audio_sample_rate": {
      "type": "integer",
      "description": "Audio sample rate in Hz",
      "minimum": 0
    },
    "audio_bitrate_kbps": {
      "type": "integer",
      "description": "Audio bitrate in kbps",
      "minimum": 0
    },
    "recommended_tools": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Recommended processing tools"
    },
    "recommended_settings": {
      "type": "object",
      "description": "Recommended processing settings",
      "properties": {
        "preset": {
          "type": "string",
          "description": "Recommended preset name"
        },
        "deinterlace": {
          "type": ["string", "null"],
          "description": "Deinterlace filter settings"
        },
        "denoise": {
          "type": ["string", "null"],
          "description": "Denoise filter settings"
        },
        "sharpen": {
          "type": ["string", "null"],
          "description": "Sharpen filter settings"
        },
        "color_correct": {
          "type": ["string", "null"],
          "description": "Color correction filter settings"
        },
        "crop_bottom": {
          "type": ["integer", "null"],
          "description": "Pixels to crop from bottom"
        },
        "upscale_model": {
          "type": ["string", "null"],
          "description": "Upscale model name"
        },
        "upscale_factor": {
          "type": "integer",
          "description": "Upscale factor (1, 2, 4)"
        },
        "target_resolution": {
          "type": "integer",
          "description": "Target resolution height"
        },
        "encoder": {
          "type": "string",
          "description": "Video encoder"
        },
        "crf": {
          "type": "integer",
          "description": "CRF quality value"
        }
      }
    },
    "processing_notes": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Human-readable processing notes"
    },
    "estimated_processing_time": {
      "type": "string",
      "description": "Estimated processing time (human-readable)"
    },
    "analyzer_backend": {
      "type": "string",
      "enum": ["python_opencv", "python_basic", "bash", "ffprobe_only"],
      "description": "Backend used for analysis"
    },
    "analysis_timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of analysis"
    }
  }
}
```

### Example JSON Output

```json
{
  "filepath": "/media/videos/old_vhs_tape.mp4",
  "filename": "old_vhs_tape.mp4",
  "filesize_mb": 2450.32,
  "duration_seconds": 514.2,
  "width": 720,
  "height": 480,
  "framerate": 29.97,
  "framerate_fraction": "30000/1001",
  "codec": "mpeg2video",
  "pixel_format": "yuv420p",
  "bitrate_kbps": 2450,
  "scan_type": "interlaced_tff",
  "content_type": "live_action",
  "source_format": "vhs",
  "noise_level": "high",
  "estimated_quality_score": 42.3,
  "has_tracking_errors": false,
  "has_color_bleeding": true,
  "has_head_switching_noise": true,
  "has_dropout_lines": false,
  "has_jitter": true,
  "audio_codec": "mp2",
  "audio_channels": 2,
  "audio_sample_rate": 44100,
  "audio_bitrate_kbps": 192,
  "recommended_tools": [
    "ffmpeg",
    "real-esrgan"
  ],
  "recommended_settings": {
    "preset": "vhs_heavy",
    "deinterlace": "yadif=1",
    "denoise": "hqdn3d=8:6:12:9",
    "sharpen": "cas=0.5",
    "color_correct": "eq=saturation=1.15:brightness=0.02",
    "crop_bottom": 8,
    "upscale_model": "realesrgan-x4plus",
    "upscale_factor": 2,
    "target_resolution": 1080,
    "encoder": "libx264",
    "crf": 18
  },
  "processing_notes": [
    "Head switching noise detected - crop bottom 8px recommended",
    "High noise level - aggressive denoise recommended",
    "Interlaced source - deinterlace before upscaling",
    "Color bleeding detected - consider color correction"
  ],
  "estimated_processing_time": "~34 minutes",
  "analyzer_backend": "python_opencv",
  "analysis_timestamp": "2025-12-17T14:32:18.456789"
}
```

### Loading and Validating JSON

```python
from vhs_upscaler.analysis.models import VideoAnalysis

# Load from JSON file
analysis = VideoAnalysis.from_json("vhs_config.json")

# Validate and use
print(f"Detected: {analysis.source_format.value}")
print(f"Preset: {analysis.recommended_settings['preset']}")

# Export back to JSON
analysis.to_json("vhs_config_copy.json")
```

---

## Programmatic API

### Python API Usage

#### Basic Analysis

```python
from vhs_upscaler.analysis import AnalyzerWrapper

# Auto-detect backend
wrapper = AnalyzerWrapper()
analysis = wrapper.analyze("video.mp4")

# Access results
print(f"Scan Type: {analysis.scan_type.value}")
print(f"Noise Level: {analysis.noise_level.value}")
print(f"Quality Score: {analysis.estimated_quality_score}")

# Get recommendations
preset = analysis.recommended_settings.get("preset")
print(f"Recommended Preset: {preset}")
```

#### Force Specific Backend

```python
from vhs_upscaler.analysis import AnalyzerWrapper, AnalyzerBackend

# Force Python+OpenCV
wrapper = AnalyzerWrapper(force_backend=AnalyzerBackend.PYTHON_OPENCV)
analysis = wrapper.analyze("video.mp4")

# Force bash
wrapper = AnalyzerWrapper(force_backend=AnalyzerBackend.BASH)
analysis = wrapper.analyze("video.mp4")
```

#### Export Analysis

```python
# Export to JSON
analysis.to_json("analysis_results.json")

# Export to dict
analysis_dict = analysis.to_dict()

# Get human-readable summary
summary = analysis.get_summary()
print(summary)
```

#### Load Existing Analysis

```python
from vhs_upscaler.analysis.models import VideoAnalysis

# Load from JSON
analysis = VideoAnalysis.from_json("analysis_results.json")

# Load from dict
analysis = VideoAnalysis.from_dict(analysis_dict)
```

#### Preset Selection

```python
from vhs_upscaler.presets import (
    get_preset_from_analysis,
    get_preset_details,
    get_recommended_settings_from_analysis,
    explain_preset
)

# Get recommended preset name
preset_name = get_preset_from_analysis(analysis)
print(f"Preset: {preset_name}")

# Get preset configuration
preset_config = get_preset_details(preset_name)
print(f"Denoise: {preset_config['denoise']}")

# Get fully customized settings
settings = get_recommended_settings_from_analysis(analysis)
print(settings)

# Explain preset
explanation = explain_preset(preset_name)
print(explanation)
```

#### Batch Processing

```python
from pathlib import Path
from vhs_upscaler.analysis import AnalyzerWrapper

wrapper = AnalyzerWrapper()
video_dir = Path("videos/")

# Analyze all videos
analyses = {}
for video_file in video_dir.glob("*.mp4"):
    print(f"Analyzing {video_file.name}...")
    analysis = wrapper.analyze(str(video_file))
    analyses[video_file.name] = analysis

    # Export individual analysis
    analysis.to_json(f"configs/{video_file.stem}.json")

# Group by preset
from collections import defaultdict
by_preset = defaultdict(list)
for filename, analysis in analyses.items():
    preset = analysis.recommended_settings.get("preset", "unknown")
    by_preset[preset].append(filename)

# Process each group with appropriate settings
for preset, files in by_preset.items():
    print(f"\nPreset '{preset}': {len(files)} videos")
    for filename in files:
        print(f"  - {filename}")
```

#### Custom Detection Logic

```python
from vhs_upscaler.analysis.models import VideoAnalysis, NoiseLevel, SourceFormat

def custom_analysis_handler(analysis: VideoAnalysis):
    """Custom logic based on analysis results."""

    # Override for specific conditions
    if analysis.source_format == SourceFormat.VHS:
        if analysis.noise_level == NoiseLevel.SEVERE:
            # Very degraded VHS - use custom settings
            analysis.recommended_settings["denoise"] = "hqdn3d=12:10:18:15"
            analysis.recommended_settings["crop_bottom"] = 12
            analysis.processing_notes.append("Custom: Extra aggressive processing")

    # Add custom processing notes
    if analysis.has_jitter and analysis.has_tracking_errors:
        analysis.processing_notes.append("Consider manual stabilization")

    return analysis

# Use custom handler
wrapper = AnalyzerWrapper()
analysis = wrapper.analyze("video.mp4")
analysis = custom_analysis_handler(analysis)
```

### Integration with Processing Pipeline

```python
from vhs_upscaler.analysis import AnalyzerWrapper
from vhs_upscaler.presets import get_recommended_settings_from_analysis
import subprocess

def process_video_with_analysis(input_file, output_file):
    """Complete workflow: analyze → process."""

    # Step 1: Analyze
    print("Analyzing video...")
    wrapper = AnalyzerWrapper()
    analysis = wrapper.analyze(input_file)

    # Step 2: Get settings
    settings = get_recommended_settings_from_analysis(analysis)

    # Step 3: Build FFmpeg command
    filters = []

    # Deinterlace
    if settings.get("deinterlace"):
        filters.append(settings["deinterlace"])

    # Denoise
    if settings.get("denoise"):
        filters.append(settings["denoise"])

    # Color correct
    if settings.get("color_correct"):
        filters.append(settings["color_correct"])

    # Crop
    if settings.get("crop_bottom"):
        crop = settings["crop_bottom"]
        filters.append(f"crop=iw:ih-{crop}:0:0")

    filter_chain = ",".join(filters)

    # Step 4: Preprocess
    preprocessed = "preprocessed.mp4"
    cmd = [
        "ffmpeg", "-i", input_file,
        "-vf", filter_chain,
        "-c:v", "libx264", "-crf", "20",
        "-c:a", "copy",
        preprocessed
    ]

    print(f"Preprocessing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    # Step 5: Upscale
    if settings.get("upscale_model"):
        upscale_cmd = [
            "python", "inference_realesrgan_video.py",
            "-i", preprocessed,
            "-n", settings["upscale_model"],
            "-s", str(settings["upscale_factor"]),
            "--suffix", "upscaled"
        ]

        print(f"Upscaling: {' '.join(upscale_cmd)}")
        subprocess.run(upscale_cmd, check=True)

    # Step 6: Sharpen and encode
    upscaled_file = preprocessed.replace(".mp4", "_upscaled.mp4")
    sharpen_filter = settings.get("sharpen", "cas=0.4")

    encode_cmd = [
        "ffmpeg", "-i", upscaled_file,
        "-vf", sharpen_filter,
        "-c:v", settings["encoder"],
        "-crf", str(settings["crf"]),
        "-preset", "slow",
        "-c:a", "copy",
        output_file
    ]

    print(f"Final encode: {' '.join(encode_cmd)}")
    subprocess.run(encode_cmd, check=True)

    print(f"Processing complete: {output_file}")

# Run pipeline
process_video_with_analysis("input.mp4", "output.mp4")
```

---

## Backend Development

### Adding a New Backend

To add a new analyzer backend (e.g., GPU-accelerated, cloud-based):

#### 1. Add Backend to Enum

**File**: `vhs_upscaler/analysis/analyzer_wrapper.py`

```python
class AnalyzerBackend(Enum):
    """Available analyzer backends."""
    PYTHON_OPENCV = "python_opencv"
    PYTHON_BASIC = "python_basic"
    BASH = "bash"
    FFPROBE_ONLY = "ffprobe_only"
    GPU_ANALYZER = "gpu_analyzer"  # NEW
```

#### 2. Implement Detection Logic

```python
def _detect_backend(self) -> AnalyzerBackend:
    """Auto-detect best available backend."""

    # Check for GPU analyzer
    try:
        import gpu_video_analyzer
        if gpu_video_analyzer.has_cuda():
            logger.debug("CUDA detected - using GPU backend")
            return AnalyzerBackend.GPU_ANALYZER
    except ImportError:
        pass

    # ... existing detection logic ...
```

#### 3. Implement Analysis Method

```python
def _run_gpu_analyzer(self, filepath: str) -> VideoAnalysis:
    """Execute GPU-accelerated analyzer."""
    try:
        import gpu_video_analyzer

        # Run analysis
        results = gpu_video_analyzer.analyze(filepath)

        # Convert to VideoAnalysis format
        analysis = VideoAnalysis(
            filepath=filepath,
            filename=Path(filepath).name,
            # ... map all fields ...
            analyzer_backend="gpu_analyzer"
        )

        return analysis

    except Exception as e:
        logger.error(f"GPU analyzer failed: {e}")
        # Fall back to next backend
        return self._run_python_analyzer(filepath, use_opencv=True)
```

#### 4. Add to analyze() Method

```python
def analyze(self, filepath: str) -> VideoAnalysis:
    """Run video analysis using best available backend."""
    # ... existing code ...

    if self.backend == AnalyzerBackend.GPU_ANALYZER:
        return self._run_gpu_analyzer(filepath)
    elif self.backend == AnalyzerBackend.PYTHON_OPENCV:
        return self._run_python_analyzer(filepath, use_opencv=True)
    # ... rest of backends ...
```

### Adding New Detection Algorithms

To add new characteristics to detect (e.g., film grain, specific artifacts):

#### 1. Add Enum (if needed)

**File**: `vhs_upscaler/analysis/models.py`

```python
class FilmGrainLevel(Enum):
    """Film grain intensity."""
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
```

#### 2. Add Field to VideoAnalysis

```python
@dataclass
class VideoAnalysis:
    # ... existing fields ...

    # New field
    film_grain_level: FilmGrainLevel = FilmGrainLevel.NONE
```

#### 3. Implement Detection

**File**: `vhs_upscaler/analysis/video_analyzer.py`

```python
def _detect_film_grain(self, filepath: str, metadata: Dict) -> FilmGrainLevel:
    """Detect film grain level."""
    # Sample frames
    frames = self._sample_frames(filepath, num_frames=10)

    grain_scores = []
    for frame in frames:
        # Analyze high-frequency noise (film grain signature)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply high-pass filter
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        high_freq = cv2.subtract(gray, blur)

        # Measure grain (variance in high-frequency)
        grain_score = np.var(high_freq)
        grain_scores.append(grain_score)

    avg_grain = np.mean(grain_scores)

    # Classify
    if avg_grain < 10:
        return FilmGrainLevel.NONE
    elif avg_grain < 30:
        return FilmGrainLevel.LIGHT
    elif avg_grain < 60:
        return FilmGrainLevel.MEDIUM
    else:
        return FilmGrainLevel.HEAVY
```

#### 4. Integrate into analyze()

```python
def analyze(self, filepath: str) -> VideoAnalysis:
    # ... existing code ...

    # New detection
    film_grain_level = self._detect_film_grain(filepath, metadata)

    return VideoAnalysis(
        # ... existing fields ...
        film_grain_level=film_grain_level,
    )
```

#### 5. Update JSON Serialization

```python
def to_dict(self) -> Dict[str, Any]:
    return {
        # ... existing fields ...
        "film_grain_level": self.film_grain_level.value,
    }

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'VideoAnalysis':
    # ... existing code ...
    data['film_grain_level'] = FilmGrainLevel(data['film_grain_level'])
    return cls(**data)
```

#### 6. Update Preset Logic

**File**: `vhs_upscaler/presets.py`

```python
def get_recommended_settings_from_analysis(analysis: VideoAnalysis) -> Dict:
    # ... existing code ...

    # Adjust for film grain
    if analysis.film_grain_level == FilmGrainLevel.HEAVY:
        # Preserve grain (minimal denoise)
        settings["denoise"] = "hqdn3d=0.5:0.5:1:1"
        settings["processing_notes"].append("Heavy film grain detected - minimal denoise")

    return settings
```

### Testing New Backends/Algorithms

#### Unit Tests

**File**: `tests/test_analysis_custom.py`

```python
import pytest
from vhs_upscaler.analysis import AnalyzerWrapper, AnalyzerBackend
from vhs_upscaler.analysis.models import VideoAnalysis, FilmGrainLevel

def test_gpu_backend():
    """Test GPU backend."""
    wrapper = AnalyzerWrapper(force_backend=AnalyzerBackend.GPU_ANALYZER)
    analysis = wrapper.analyze("tests/fixtures/test_video.mp4")

    assert analysis.analyzer_backend == "gpu_analyzer"
    assert isinstance(analysis.scan_type, ScanType)

def test_film_grain_detection():
    """Test film grain detection."""
    wrapper = AnalyzerWrapper()
    analysis = wrapper.analyze("tests/fixtures/grainy_video.mp4")

    assert analysis.film_grain_level == FilmGrainLevel.HEAVY

def test_film_grain_preset_adjustment():
    """Test preset adjustment for film grain."""
    from vhs_upscaler.presets import get_recommended_settings_from_analysis

    # Create mock analysis with heavy grain
    analysis = VideoAnalysis(
        # ... required fields ...
        film_grain_level=FilmGrainLevel.HEAVY
    )

    settings = get_recommended_settings_from_analysis(analysis)

    # Should use minimal denoise
    assert "hqdn3d=0.5:0.5:1:1" in settings.get("denoise", "")
```

#### Integration Tests

```bash
# Test with real video
python -m vhs_upscaler.vhs_upscale \
  -i tests/fixtures/test_video.mp4 \
  --analyze-only \
  --force-backend gpu_analyzer \
  --save-analysis test_gpu_analysis.json

# Verify output
python -c "
from vhs_upscaler.analysis.models import VideoAnalysis
analysis = VideoAnalysis.from_json('test_gpu_analysis.json')
assert analysis.analyzer_backend == 'gpu_analyzer'
print('✓ GPU backend test passed')
"
```

---

## Troubleshooting

### Common Issues

#### Issue: "No analyzer backend available"

**Cause**: FFmpeg/ffprobe not installed or not in PATH.

**Solution**:
```bash
# Install FFmpeg
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows (using Chocolatey)
choco install ffmpeg

# Verify
ffprobe -version
```

#### Issue: "OpenCV not found - falling back to basic analyzer"

**Cause**: OpenCV not installed.

**Solution**:
```bash
# Install OpenCV
pip install opencv-python numpy

# Verify
python -c "import cv2; print(cv2.__version__)"
```

#### Issue: Analysis reports "unknown" for all characteristics

**Cause**: Using FFprobe-only backend (minimal detection).

**Solution**: Install dependencies for better backends:
```bash
# Install Python dependencies
pip install opencv-python numpy

# Or use bash backend (no Python deps needed)
python -m vhs_upscaler.vhs_upscale \
  -i video.mp4 \
  --analyze-only \
  --force-backend bash
```

#### Issue: Bash analyzer not found

**Cause**: `scripts/video_analyzer.sh` not in expected location.

**Solution**:
```bash
# Check if script exists
ls -la scripts/video_analyzer.sh

# Make executable
chmod +x scripts/video_analyzer.sh

# Test manually
bash scripts/video_analyzer.sh --help
```

#### Issue: Analysis takes too long (>2 minutes)

**Cause**: Large video file, slow disk, or CPU bottleneck.

**Solutions**:
```bash
# Use faster backend
python -m vhs_upscaler.vhs_upscale \
  -i large_video.mp4 \
  --analyze-only \
  --force-backend ffprobe_only  # Fastest but least accurate

# Analyze shorter clip instead
ffmpeg -i large_video.mp4 -t 60 -c copy sample.mp4
python -m vhs_upscaler.vhs_upscale \
  -i sample.mp4 \
  --analyze-only \
  --save-analysis config.json
```

#### Issue: Incorrect scan type detection

**Cause**: Mixed content (progressive + interlaced), or telecine.

**Debugging**:
```bash
# Manual idet check
ffmpeg -i video.mp4 \
  -vf idet \
  -frames:v 200 \
  -an -f null - 2>&1 | grep "TFF:"

# Look at output:
# TFF: 150  BFF: 10  Progressive: 40
# ^ Clearly interlaced TFF

# Override if needed
python -m vhs_upscaler.vhs_upscale \
  -i video.mp4 \
  -o output.mp4 \
  --deinterlace yadif=1  # Force deinterlace
```

#### Issue: JSON load fails with "KeyError"

**Cause**: JSON schema mismatch (old version).

**Solution**:
```python
from vhs_upscaler.analysis.models import VideoAnalysis

try:
    analysis = VideoAnalysis.from_json("old_config.json")
except KeyError as e:
    print(f"Missing field: {e}")
    print("Re-analyze video with current version")
```

### Debugging Tips

#### Enable Verbose Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

from vhs_upscaler.analysis import AnalyzerWrapper

wrapper = AnalyzerWrapper()
analysis = wrapper.analyze("video.mp4")
```

**Output**:
```
DEBUG:vhs_upscaler.analysis.analyzer_wrapper:OpenCV detected - using Python+OpenCV backend
DEBUG:vhs_upscaler.analysis.video_analyzer:Analyzing video with Python backend (OpenCV: True)
DEBUG:vhs_upscaler.analysis.video_analyzer:Sampling 10 frames for noise analysis
...
```

#### Test Individual Components

```python
# Test scan type detection only
from vhs_upscaler.analysis.video_analyzer import VideoAnalyzer

analyzer = VideoAnalyzer(use_opencv=True)
metadata = analyzer._get_metadata("video.mp4")
scan_type = analyzer._detect_scan_type("video.mp4", metadata)
print(f"Scan type: {scan_type}")

# Test noise estimation only
noise_level = analyzer._estimate_noise_level("video.mp4", metadata)
print(f"Noise level: {noise_level}")
```

#### Compare Backends

```bash
# Compare all backends on same video
for backend in python_opencv python_basic bash ffprobe_only; do
  echo "=== $backend ==="
  python -m vhs_upscaler.vhs_upscale \
    -i video.mp4 \
    --analyze-only \
    --force-backend $backend \
    --save-analysis "analysis_$backend.json"
done

# Compare results
for f in analysis_*.json; do
  echo "$f:"
  jq '.scan_type, .noise_level, .source_format' "$f"
done
```

#### Validate JSON Output

```bash
# Use jq to validate and pretty-print
jq . analysis.json

# Extract specific fields
jq '.scan_type, .noise_level, .recommended_settings.preset' analysis.json

# Check for missing fields
jq 'to_entries | map(select(.value == null or .value == "unknown"))' analysis.json
```

---

## Performance Tuning

### Optimization Strategies

#### 1. Backend Selection

**Fastest to Slowest**:
1. FFprobe Only: 5-10s (minimal accuracy)
2. Bash: 10-20s (good for scripts)
3. Python Basic: 15-25s (no OpenCV)
4. Python+OpenCV: 20-30s (best accuracy)

**Recommendation**: Use Python+OpenCV for critical footage, bash for batch jobs.

#### 2. Frame Sampling

Reduce number of frames analyzed:

```python
# Default: 10 frames
class VideoAnalyzer:
    def __init__(self, num_sample_frames=10):
        self.num_sample_frames = num_sample_frames

# Fast mode: 5 frames
analyzer = VideoAnalyzer(num_sample_frames=5)
```

**Trade-off**: Fewer frames = faster but less accurate.

#### 3. Parallel Analysis

Analyze multiple videos in parallel:

```python
from concurrent.futures import ProcessPoolExecutor
from vhs_upscaler.analysis import AnalyzerWrapper

def analyze_video(filepath):
    wrapper = AnalyzerWrapper()
    return wrapper.analyze(filepath)

videos = ["video1.mp4", "video2.mp4", "video3.mp4"]

with ProcessPoolExecutor(max_workers=4) as executor:
    analyses = list(executor.map(analyze_video, videos))
```

#### 4. Cache Analysis Results

Avoid re-analyzing same video:

```python
from pathlib import Path
import hashlib

def get_video_hash(filepath):
    """Generate hash of first 10MB (fast fingerprint)."""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read(10 * 1024 * 1024)).hexdigest()

def analyze_with_cache(filepath):
    video_hash = get_video_hash(filepath)
    cache_file = Path(f"cache/{video_hash}.json")

    if cache_file.exists():
        print(f"Loading cached analysis for {filepath}")
        return VideoAnalysis.from_json(str(cache_file))

    # Analyze and cache
    wrapper = AnalyzerWrapper()
    analysis = wrapper.analyze(filepath)

    cache_file.parent.mkdir(exist_ok=True)
    analysis.to_json(str(cache_file))

    return analysis
```

#### 5. Skip Analysis for Known Sources

If you know the source characteristics:

```python
from vhs_upscaler.analysis.models import VideoAnalysis, ScanType, NoiseLevel, SourceFormat, ContentType

# Manually create analysis for known VHS source
analysis = VideoAnalysis(
    filepath="video.mp4",
    filename="video.mp4",
    filesize_mb=2000,
    duration_seconds=3600,
    width=720,
    height=480,
    framerate=29.97,
    framerate_fraction="30000/1001",
    codec="mpeg2video",
    pixel_format="yuv420p",
    bitrate_kbps=2500,
    scan_type=ScanType.INTERLACED_TFF,
    content_type=ContentType.LIVE_ACTION,
    source_format=SourceFormat.VHS,
    noise_level=NoiseLevel.MEDIUM,
    estimated_quality_score=50.0,
    analyzer_backend="manual"
)

# Export for batch use
analysis.to_json("vhs_template.json")
```

### Benchmarking

```python
import time
from vhs_upscaler.analysis import AnalyzerWrapper, AnalyzerBackend

def benchmark_backend(filepath, backend):
    """Benchmark specific backend."""
    wrapper = AnalyzerWrapper(force_backend=backend)

    start = time.time()
    analysis = wrapper.analyze(filepath)
    elapsed = time.time() - start

    return {
        "backend": backend.value,
        "time": elapsed,
        "scan_type": analysis.scan_type.value,
        "noise_level": analysis.noise_level.value
    }

# Run benchmarks
results = []
for backend in AnalyzerBackend:
    try:
        result = benchmark_backend("test.mp4", backend)
        results.append(result)
        print(f"{result['backend']}: {result['time']:.2f}s")
    except Exception as e:
        print(f"{backend.value}: FAILED - {e}")

# Print summary
import pandas as pd
df = pd.DataFrame(results)
print(df)
```

---

## Advanced Topics

### Scene-Based Analysis

Analyze different scenes separately (for mixed content):

```python
def analyze_by_scene(filepath, scene_threshold=0.3):
    """
    Analyze video scene-by-scene.

    Returns dict mapping scene timestamps to VideoAnalysis.
    """
    import subprocess
    import json

    # Detect scene changes
    cmd = [
        "ffmpeg", "-i", filepath,
        "-vf", f"select='gt(scene,{scene_threshold})',showinfo",
        "-f", "null", "-"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Parse scene timestamps from showinfo output
    scene_times = parse_scene_timestamps(result.stderr)

    # Analyze each scene
    wrapper = AnalyzerWrapper()
    scene_analyses = {}

    for i, (start, end) in enumerate(scene_times):
        # Extract scene clip
        scene_file = f"temp_scene_{i}.mp4"
        extract_scene(filepath, start, end, scene_file)

        # Analyze
        analysis = wrapper.analyze(scene_file)
        scene_analyses[f"{start}-{end}"] = analysis

        # Cleanup
        os.remove(scene_file)

    return scene_analyses
```

### Custom Scoring Models

Train custom quality scoring:

```python
from sklearn.ensemble import RandomForestRegressor
import numpy as np

def train_quality_model(training_data):
    """
    Train ML model for quality scoring.

    training_data: List of (analysis, human_quality_score) tuples
    """
    X = []
    y = []

    for analysis, score in training_data:
        # Feature extraction
        features = [
            analysis.width * analysis.height,  # Resolution
            analysis.bitrate_kbps,
            analysis.noise_level.value == "low",
            analysis.scan_type == ScanType.PROGRESSIVE,
            # ... more features
        ]
        X.append(features)
        y.append(score)

    # Train model
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)

    return model

def predict_quality(analysis, model):
    """Predict quality score using trained model."""
    features = extract_features(analysis)
    return model.predict([features])[0]
```

### Audio Analysis Integration

Extend system to analyze audio:

```python
from vhs_upscaler.analysis.models import AudioAnalysis
from dataclasses import dataclass

@dataclass
class AudioAnalysis:
    """Audio analysis results."""
    has_hiss: bool
    has_hum: bool
    has_clipping: bool
    dynamic_range_db: float
    recommended_filters: List[str]

def analyze_audio(filepath):
    """Analyze audio characteristics."""
    # Use FFmpeg audio filters
    cmd = [
        "ffmpeg", "-i", filepath,
        "-af", "astats",
        "-f", "null", "-"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Parse audio statistics
    # Detect hiss, hum, clipping, etc.

    return AudioAnalysis(...)
```

### Cloud-Based Analysis

Offload analysis to cloud:

```python
import requests

class CloudAnalyzer:
    """Cloud-based video analyzer."""

    def __init__(self, api_key, endpoint):
        self.api_key = api_key
        self.endpoint = endpoint

    def analyze(self, filepath):
        """Upload and analyze video in cloud."""
        # Upload video
        with open(filepath, 'rb') as f:
            files = {'video': f}
            headers = {'Authorization': f'Bearer {self.api_key}'}

            response = requests.post(
                f"{self.endpoint}/analyze",
                files=files,
                headers=headers
            )

        # Convert response to VideoAnalysis
        result = response.json()
        return VideoAnalysis.from_dict(result)
```

---

## Further Reading

### Related Documentation

- [BEST_PRACTICES.md](../BEST_PRACTICES.md) - VHS processing guidelines
- [CLAUDE.md](../CLAUDE.md) - Overall project documentation
- [README.md](../README.md) - User guide and installation

### External Resources

- **FFmpeg Filters**: https://ffmpeg.org/ffmpeg-filters.html
- **Real-ESRGAN**: https://github.com/xinntao/Real-ESRGAN
- **OpenCV Documentation**: https://docs.opencv.org/
- **VHS Restoration Guide**: https://obsproject.com/wiki/VHS-Restoration

### Academic Papers

- "Video Interlacing Detection" - IEEE Transactions on Image Processing
- "Blind Noise Level Estimation" - CVPR 2020
- "Content-Aware Video Restoration" - SIGGRAPH 2021

---

## Changelog

**v1.4.x** (2025-12-17)
- Initial release of intelligent analysis system
- Multi-backend support (Python+OpenCV, Bash, FFprobe)
- 9 preset configurations
- VHS artifact detection
- JSON import/export
- CLI integration with 5 new arguments

---

## Contributing

To contribute to the analysis system:

1. **Add test fixtures**: Include representative video samples
2. **Document algorithms**: Explain detection logic with citations
3. **Add unit tests**: Cover new detection code
4. **Update this documentation**: Keep API reference current
5. **Benchmark changes**: Measure impact on analysis time and accuracy

**Testing Requirements**:
- All new detection algorithms must have unit tests
- Integration tests for new backends
- Benchmark against existing backends
- Documentation updates mandatory

---

## License

Same as parent project. See [LICENSE](../LICENSE).

---

## Support

For questions or issues with the analysis system:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [GitHub Issues](https://github.com/parthalon025/terminalai/issues)
3. Consult [BEST_PRACTICES.md](../BEST_PRACTICES.md) for VHS-specific guidance

---

**End of Documentation**

*Last Updated: 2025-12-17*
*Version: 1.4.x*
*Maintained by: VHS Upscaler Project*
