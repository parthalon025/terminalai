# RTX Video SDK Installation Guide

## Quick Installation

### 1. Download SDK

Visit: https://developer.nvidia.com/rtx-video-sdk/getting-started

- Create free NVIDIA Developer account (if needed)
- Download RTX Video SDK v1.1.0
- Save the ZIP file to Downloads folder

### 2. Extract SDK

```powershell
# Extract to Program Files (recommended)
Expand-Archive -Path "$env:USERPROFILE\Downloads\rtx_video_sdk_v1.1.0.zip" `
  -DestinationPath "C:\Program Files\NVIDIA Corporation\RTX Video SDK"
```

Or extract manually:
- Right-click the ZIP file → Extract All
- Extract to: `C:\Program Files\NVIDIA Corporation\RTX Video SDK`

### 3. Set Environment Variable

**Option A: PowerShell (Administrator)**
```powershell
# Set system-wide environment variable
[System.Environment]::SetEnvironmentVariable(
    'RTX_VIDEO_SDK_HOME',
    'C:\Program Files\NVIDIA Corporation\RTX Video SDK',
    [System.EnvironmentVariableTarget]::Machine
)
```

**Option B: Command Prompt (Administrator)**
```cmd
setx RTX_VIDEO_SDK_HOME "C:\Program Files\NVIDIA Corporation\RTX Video SDK" /M
```

**Option C: Windows GUI**
1. Press `Win + X` → System → Advanced System Settings
2. Click "Environment Variables"
3. Under "System variables", click "New..."
4. Variable name: `RTX_VIDEO_SDK_HOME`
5. Variable value: `C:\Program Files\NVIDIA Corporation\RTX Video SDK`
6. Click OK

### 4. Install Python Dependencies

```bash
# Install RTX Video SDK Python packages
pip install -e ".[rtxvideo]"

# Or manually:
pip install numpy>=1.24.0 opencv-python>=4.8.0

# Optional: CUDA acceleration (better performance)
pip install cupy-cuda12x>=12.0.0
```

### 5. Restart Terminal

Close and reopen your terminal to load the new environment variable.

### 6. Verify Installation

```bash
# Run verification
python -c "from vhs_upscaler.rtx_video_sdk import is_rtx_video_available; available, msg = is_rtx_video_available(); print(f'Available: {available}'); print(f'Message: {msg}')"
```

Expected output:
```
Available: True
Message: RTX Video SDK ready
```

## Usage

### GUI

```bash
python -m vhs_upscaler.gui
```

1. Select **"rtxvideo"** as AI Upscaler
2. Enable **Artifact Reduction** (recommended for VHS)
3. Enable **HDR** if desired
4. Set output resolution (1080p or 4K)
5. Process video

### CLI

```bash
# Basic 4K upscale
vhs-upscale upscale video.mp4 -o output.mp4 --engine rtxvideo -r 2160

# VHS restoration with artifact reduction
vhs-upscale upscale vhs_tape.mp4 -o restored.mp4 --engine rtxvideo \
  --rtxvideo-artifact-reduction --rtxvideo-artifact-strength 0.7

# HDR conversion
vhs-upscale upscale video.mp4 -o hdr.mp4 --engine rtxvideo --rtxvideo-hdr
```

## System Requirements

### Hardware
- **GPU**: NVIDIA RTX 20 series or newer (Turing, Ampere, Ada, Blackwell)
  - RTX 2060, 2070, 2080 (+ Super/Ti variants)
  - RTX 3060, 3070, 3080, 3090 (+ Ti variants)
  - RTX 4060, 4070, 4080, 4090 (+ Super variants)
  - RTX 50 series (Blackwell)
- **VRAM**: 4GB minimum, 8GB+ recommended for 4K

### Software
- **OS**: Windows 10/11 64-bit
- **Driver**: NVIDIA Driver 535+ (latest recommended)
- **Python**: 3.10+

## Troubleshooting

### SDK Not Found

If verification fails:

1. **Check SDK path exists**:
   ```powershell
   Test-Path "C:\Program Files\NVIDIA Corporation\RTX Video SDK"
   ```

2. **Check environment variable**:
   ```powershell
   $env:RTX_VIDEO_SDK_HOME
   ```

3. **Verify DLLs present**:
   ```powershell
   Get-ChildItem "C:\Program Files\NVIDIA Corporation\RTX Video SDK" -Filter *.dll -Recurse
   ```

### GPU Not Supported

Check GPU compute capability:
```bash
nvidia-smi --query-gpu=name,compute_cap --format=csv
```

RTX Video SDK requires:
- Compute Capability 7.5+ (RTX 20 series = Turing)
- Driver 535+

### Performance Issues

1. **Install CUDA acceleration**:
   ```bash
   pip install cupy-cuda12x>=12.0.0
   ```

2. **Close other GPU applications** (games, browsers with hardware acceleration)

3. **Update NVIDIA driver** to latest version

4. **Lower resolution** if GPU has limited VRAM

## Benefits vs Other Upscalers

| Feature | RTX Video SDK | Real-ESRGAN | FFmpeg |
|---------|---------------|-------------|--------|
| Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Speed (RTX GPU) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Artifact Reduction | ✅ | ✅ | ❌ |
| HDR Conversion | ✅ | ❌ | Limited |
| GPU Support | NVIDIA RTX only | Universal (Vulkan) | CPU/Any GPU |
| Hardware Acceleration | Tensor Cores | Shader Cores | Varied |

**Recommendation**: Use RTX Video SDK for RTX GPUs for best quality and speed!

## References

- [RTX Video SDK Homepage](https://developer.nvidia.com/rtx-video-sdk)
- [Getting Started Guide](https://developer.nvidia.com/rtx-video-sdk/getting-started)
- [RTX Video FAQ](https://nvidia.custhelp.com/app/answers/detail/a_id/5448/~/rtx-video-faq)
- [SDK Documentation](https://docs.nvidia.com/video-effects-sdk/)
