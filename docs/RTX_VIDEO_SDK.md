# RTX Video SDK Integration Guide

**Version:** 1.5.1
**Date:** 2025-12-19

TerminalAI v1.5.1 introduces NVIDIA RTX Video SDK integration, providing the best-in-class AI-powered video upscaling, artifact reduction, and HDR conversion for VHS/DVD restoration.

---

## Quick Start

### 1. Run Setup Wizard

```bash
# Interactive setup (recommended)
terminalai-setup-rtx

# Or via Python module
python -m vhs_upscaler.setup_rtx
```

The setup wizard will:
- Check system requirements
- Detect existing SDK installation
- Guide you through installation steps
- Install Python dependencies

### 2. Use RTX Video SDK

**GUI:**
1. Launch TerminalAI: `python -m vhs_upscaler.gui`
2. Select "rtxvideo" as the AI Upscaler
3. Enable artifact reduction and/or HDR as needed
4. Process your video

**CLI:**
```bash
# Basic upscaling
vhs-upscale upscale video.mp4 -o output.mp4 --engine rtxvideo

# With artifact reduction (great for VHS)
vhs-upscale upscale vhs_tape.mp4 -o restored.mp4 --engine rtxvideo \
  --rtxvideo-artifact-reduction --rtxvideo-artifact-strength 0.7

# With HDR output
vhs-upscale upscale video.mp4 -o hdr_output.mp4 --engine rtxvideo --rtxvideo-hdr
```

---

## Requirements

### Hardware
- **GPU:** NVIDIA RTX 20 series or newer (Turing, Ampere, Ada, Blackwell)
  - RTX 2060, 2070, 2080, 2060 Super, 2070 Super, 2080 Super, 2080 Ti
  - RTX 3060, 3070, 3080, 3090, 3060 Ti, 3070 Ti, 3080 Ti
  - RTX 4060, 4070, 4080, 4090, 4070 Super, 4080 Super
  - RTX A-series, RTX Quadro series
- **VRAM:** 4GB minimum, 8GB+ recommended for 4K

### Software
- **OS:** Windows 10/11 64-bit
- **Driver:** NVIDIA Driver 535+
- **SDK:** RTX Video SDK (download from NVIDIA)

### Python Dependencies
```bash
pip install terminalai[rtxvideo]

# Or manually:
pip install numpy>=1.24.0 opencv-python>=4.8.0

# Optional: CUDA acceleration for better performance
pip install cupy-cuda12x>=12.0.0
```

---

## Installation

### Step 1: Download RTX Video SDK

1. Visit: https://developer.nvidia.com/rtx-video-sdk
2. Click "Get Started"
3. Create or log in to your NVIDIA Developer account (free)
4. Download the RTX Video SDK

### Step 2: Install SDK

1. Run the downloaded installer
2. Note the installation path (default: `C:\Program Files\NVIDIA Corporation\RTX Video SDK`)
3. Complete the installation

### Step 3: Set Environment Variable

**Option A: Permanent (Recommended)**
```powershell
# In PowerShell as Administrator
setx RTX_VIDEO_SDK_HOME "C:\Program Files\NVIDIA Corporation\RTX Video SDK" /M
```

**Option B: Current Session Only**
```powershell
$env:RTX_VIDEO_SDK_HOME = "C:\Program Files\NVIDIA Corporation\RTX Video SDK"
```

**Option C: Via Windows UI**
1. Press `Win + X` → System → Advanced System Settings
2. Click "Environment Variables"
3. Add new System Variable:
   - Name: `RTX_VIDEO_SDK_HOME`
   - Value: `C:\Program Files\NVIDIA Corporation\RTX Video SDK`

### Step 4: Install Python Dependencies

```bash
pip install terminalai[rtxvideo]
```

### Step 5: Verify Installation

```bash
# Run verification
terminalai-setup-rtx

# Or test in Python
python -c "from vhs_upscaler.rtx_video_sdk import is_rtx_video_available; print(is_rtx_video_available())"
```

---

## Features

### Super Resolution

AI-powered upscaling that dramatically improves video quality.

| Input | Output | Use Case |
|-------|--------|----------|
| 480p (VHS) | 1080p FHD | Standard restoration |
| 480p (VHS) | 2160p 4K | Maximum quality |
| 720p (DVD) | 1440p QHD | Moderate upscale |
| 1080p | 2160p 4K | HD enhancement |

```bash
# 4x upscale (480p → 2160p 4K)
vhs-upscale upscale video.mp4 -o output.mp4 --engine rtxvideo -r 2160
```

### Artifact Reduction

Removes VHS-specific artifacts and compression noise:
- VHS tracking errors
- Color bleeding
- Head switching noise
- Compression blockyness
- Temporal noise

```bash
# Light artifact reduction (preserve detail)
vhs-upscale upscale video.mp4 -o output.mp4 --engine rtxvideo \
  --rtxvideo-artifact-strength 0.3

# Moderate (balanced, default)
vhs-upscale upscale video.mp4 -o output.mp4 --engine rtxvideo \
  --rtxvideo-artifact-strength 0.5

# Aggressive (heavy artifacts)
vhs-upscale upscale video.mp4 -o output.mp4 --engine rtxvideo \
  --rtxvideo-artifact-strength 0.8
```

### HDR Conversion

Convert SDR video to HDR10 for modern TVs:

```bash
# Enable HDR10 output
vhs-upscale upscale video.mp4 -o output_hdr10.mp4 --engine rtxvideo --rtxvideo-hdr

# Combine with other options
vhs-upscale upscale vhs_tape.mp4 -o restored_hdr.mp4 --engine rtxvideo \
  --rtxvideo-artifact-reduction \
  --rtxvideo-artifact-strength 0.6 \
  --rtxvideo-hdr \
  -r 2160
```

---

## CLI Reference

### Engine Selection

```bash
--engine rtxvideo    # Use RTX Video SDK (best quality)
--engine auto        # Auto-detect (uses RTX Video SDK if available)
```

### RTX Video SDK Options

| Option | Description | Default |
|--------|-------------|---------|
| `--rtxvideo-artifact-reduction` | Enable artifact reduction | Enabled |
| `--rtxvideo-no-artifact-reduction` | Disable artifact reduction | - |
| `--rtxvideo-artifact-strength` | Artifact strength (0.0-1.0) | 0.5 |
| `--rtxvideo-hdr` | Enable SDR to HDR10 | Disabled |
| `--rtxvideo-sdk-path` | Custom SDK path | Auto-detect |

### Example Commands

```bash
# VHS restoration - standard
vhs-upscale upscale vhs_tape.mp4 -o restored.mp4 \
  --engine rtxvideo \
  --preset vhs \
  -r 1080

# VHS restoration - maximum quality
vhs-upscale upscale vhs_tape.mp4 -o restored_4k.mp4 \
  --engine rtxvideo \
  --preset vhs \
  --rtxvideo-artifact-strength 0.7 \
  -r 2160

# VHS to HDR10
vhs-upscale upscale vhs_tape.mp4 -o restored_hdr.mp4 \
  --engine rtxvideo \
  --preset vhs \
  --rtxvideo-hdr \
  -r 2160

# DVD upscale
vhs-upscale upscale dvd_rip.mkv -o restored.mp4 \
  --engine rtxvideo \
  --preset dvd \
  --rtxvideo-artifact-strength 0.4 \
  -r 2160

# Batch processing
vhs-upscale batch ./vhs_tapes/ ./restored/ \
  --engine rtxvideo \
  --preset vhs \
  -r 1080
```

---

## Performance

### Processing Speed

| Resolution | RTX 3080 | RTX 4080 | RTX 4090 |
|------------|----------|----------|----------|
| 480p → 1080p | 35-45 fps | 50-60 fps | 65-80 fps |
| 480p → 2160p | 15-20 fps | 25-35 fps | 40-50 fps |
| 1080p → 2160p | 25-35 fps | 40-50 fps | 55-70 fps |

### VRAM Usage

| Operation | Estimated VRAM |
|-----------|----------------|
| Super Resolution only | 2-3 GB |
| + Artifact Reduction | 3-4 GB |
| + HDR Conversion | 4-5 GB |
| 4K output | +2 GB |

---

## Comparison with Other Engines

| Feature | RTX Video SDK | Real-ESRGAN | FFmpeg |
|---------|---------------|-------------|--------|
| Quality | ⭐⭐⭐⭐⭐ Best | ⭐⭐⭐⭐ Great | ⭐⭐⭐ Good |
| Speed | ⭐⭐⭐⭐⭐ Fastest | ⭐⭐⭐ Medium | ⭐⭐ Slow |
| Artifact Removal | ✅ AI-powered | ❌ | ❌ |
| HDR Conversion | ✅ Built-in | ❌ | Manual |
| GPU Support | RTX 20+ only | Any Vulkan | CPU/Any |
| Platform | Windows only | Cross-platform | Cross-platform |

**When to use RTX Video SDK:**
- VHS/DVD restoration with heavy artifacts
- HDR output for modern TVs
- Maximum quality with fast processing
- Windows system with RTX GPU

**When to use alternatives:**
- Linux/macOS → Use Real-ESRGAN
- AMD/Intel GPU → Use Real-ESRGAN
- No GPU → Use FFmpeg
- Anime content → Use Real-ESRGAN with anime model

---

## Troubleshooting

### SDK Not Detected

**Symptom:** "RTX Video SDK not found" message

**Solutions:**
1. Run setup wizard: `terminalai-setup-rtx`
2. Verify SDK installation path
3. Check environment variable:
   ```powershell
   echo $env:RTX_VIDEO_SDK_HOME
   ```
4. Restart your terminal/IDE after setting the variable

### GPU Not Supported

**Symptom:** "GPU does not support RTX Video SDK"

**Solutions:**
1. Verify you have an RTX 20+ GPU:
   ```bash
   nvidia-smi
   ```
2. Update NVIDIA drivers to 535+
3. Use Real-ESRGAN as fallback

### Processing Errors

**Symptom:** Processing fails or produces artifacts

**Solutions:**
1. Update NVIDIA drivers
2. Reduce artifact strength: `--rtxvideo-artifact-strength 0.3`
3. Check GPU temperature (throttling can cause issues)
4. Try processing a shorter clip first

### Import Errors

**Symptom:** Python import errors

**Solutions:**
```bash
# Reinstall dependencies
pip install --upgrade numpy opencv-python

# For CUDA acceleration
pip install cupy-cuda12x
```

---

## FAQ

**Q: Is RTX Video SDK free?**
A: Yes, RTX Video SDK is free to download and use. You only need a free NVIDIA Developer account.

**Q: Can I use RTX Video SDK on Linux?**
A: No, RTX Video SDK is Windows-only. Use Real-ESRGAN or Maxine (deprecated) on Linux.

**Q: Do I need the SDK for every machine?**
A: Yes, RTX Video SDK must be installed on each machine. The SDK is not redistributable.

**Q: What's the difference between RTX Video SDK and Maxine?**
A: RTX Video SDK is newer and includes artifact reduction + HDR conversion. Maxine is now deprecated but still supported for legacy installations.

**Q: Can I combine RTX Video SDK with face restoration?**
A: Yes! Use RTX Video SDK for upscaling and artifact removal, then apply face restoration:
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --engine rtxvideo \
  --face-restore \
  --face-restore-strength 0.6
```

---

## Resources

- [RTX Video SDK Download](https://developer.nvidia.com/rtx-video-sdk)
- [NVIDIA Developer Documentation](https://docs.nvidia.com/video-technologies/)
- [TerminalAI GitHub](https://github.com/parthalon025/terminalai)
- [Feature Comparison](./FEATURE_COMPARISON.md)

---

**Document Version:** 1.0
**Last Updated:** 2025-12-19
**Author:** TerminalAI Development Team
