# Hardware Detection & Auto-Configuration

**Version:** 1.5.1+
**Status:** Implemented
**Module:** `vhs_upscaler/hardware_detection.py`

## Overview

The hardware detection system automatically identifies your GPU and configures optimal settings for video processing, eliminating manual configuration and preventing common mistakes.

## Features

### Automatic GPU Detection

- **NVIDIA GPUs**: Full support via `nvidia-smi`
  - RTX 50 series (5090, 5080, 5070, etc.)
  - RTX 40 series (4090, 4080, 4070, etc.)
  - RTX 30 series (3090, 3080, 3070, 3060, etc.)
  - RTX 20 series (2080 Ti, 2070, 2060, etc.)
  - GTX 16 series (1660 Ti, 1650, etc.)
  - GTX 10 series (1080 Ti, 1070, 1060, etc.)
  - Legacy GTX (900 series and older)

- **AMD GPUs**: Basic support via system tools
  - RDNA 3 (RX 7000 series)
  - RDNA 2 (RX 6000 series)
  - RDNA (RX 5000 series)
  - Legacy AMD cards

- **Intel GPUs**: Basic support
  - Intel Arc (A770, A750, etc.)
  - Integrated graphics (UHD, Iris, etc.)

- **CPU-Only**: Automatic fallback when no GPU detected

### Capability Detection

The system checks for:
- **VRAM amount** (GPU memory)
- **Driver version**
- **CUDA availability** (for PyTorch-based features)
- **NVENC support** (hardware video encoding)
- **RTX Video SDK installation**
- **Compute capability** (for CUDA features)

### Intelligent Configuration

Based on detected hardware, the system automatically sets:

#### RTX 50/40 Series
```python
{
    "upscale_engine": "rtxvideo",    # RTX Video SDK (if installed)
    "encoder": "hevc_nvenc",          # H.265 hardware encoding
    "quality": "best",                # Maximum quality
    "face_restore": True,             # AI face restoration
    "audio_upmix": "demucs"           # AI surround sound (if CUDA available)
}
```

#### RTX 30 Series
```python
{
    "upscale_engine": "rtxvideo",     # RTX Video SDK (if installed)
    "encoder": "hevc_nvenc",          # H.265 hardware encoding
    "quality": "best",                # Maximum quality
    "face_restore": True,             # If 6GB+ VRAM
    "audio_upmix": "demucs"           # If 8GB+ VRAM and CUDA
}
```

#### RTX 20 Series
```python
{
    "upscale_engine": "rtxvideo",     # RTX Video SDK (if installed)
    "encoder": "hevc_nvenc",          # H.265 hardware encoding
    "quality": "balanced",            # Good quality
    "face_restore": True,             # If 6GB+ VRAM
    "audio_upmix": "surround"         # Standard surround
}
```

#### GTX 16/10 Series
```python
{
    "upscale_engine": "realesrgan",   # AI upscaling via Vulkan
    "encoder": "h264_nvenc",          # H.264 hardware encoding
    "quality": "balanced",            # Good quality
    "face_restore": False,            # Too slow on GTX
    "audio_upmix": "simple"           # Basic upmix
}
```

#### AMD/Intel GPUs
```python
{
    "upscale_engine": "realesrgan",   # Vulkan-based AI upscaling
    "encoder": "libx265",             # CPU encoding
    "quality": "balanced",            # Good quality
    "face_restore": False,            # CUDA-only feature
    "audio_upmix": "simple"           # Basic processing
}
```

#### CPU-Only
```python
{
    "upscale_engine": "ffmpeg",       # Traditional upscaling
    "encoder": "libx265",             # CPU H.265 encoding
    "quality": "good",                # Lower quality (faster)
    "face_restore": False,            # Too slow on CPU
    "audio_upmix": "simple"           # Minimal processing
}
```

## Usage

### In Python Code

```python
from vhs_upscaler.hardware_detection import detect_hardware, get_optimal_config, print_hardware_report

# Detect hardware
hw = detect_hardware()

# Get optimal configuration
config = get_optimal_config(hw)

# Print report
print_hardware_report(hw, config)

# Access hardware info
print(f"GPU: {hw.display_name}")
print(f"VRAM: {hw.vram_gb:.1f} GB")
print(f"Supports AI upscaling: {hw.supports_ai_upscaling}")
print(f"Supports hardware encoding: {hw.supports_hardware_encoding}")
print(f"RTX Video SDK installed: {hw.has_rtx_video_sdk}")

# Access configuration
print(f"Upscale engine: {config['upscale_engine']}")
print(f"Encoder: {config['encoder']}")
print(f"Quality: {config['quality']}")

# Check for warnings
if config['warnings']:
    for warning in config['warnings']:
        print(f"Warning: {warning}")
```

### In GUI

The GUI automatically detects hardware on startup and:
1. Displays hardware info banner at the top
2. Sets optimal defaults for all controls
3. Shows warnings if features are unavailable
4. Updates recommendations based on GPU capabilities

### Command-Line Test

```bash
# Test hardware detection
python test_hardware_detection.py

# Output:
# ======================================================================
# Hardware Detection Report
# ======================================================================
#
# GPU: NVIDIA GeForce RTX 5080 (16GB VRAM)
# Vendor: NVIDIA
# Driver: 591.59
# Compute Capability: 12.0
#
# Capabilities:
#   AI Upscaling: Yes
#   Hardware Encoding: Yes
#   RTX Video SDK: Yes
#   CUDA Acceleration: Yes
#   Vulkan Support: Yes
#
# Recommended Configuration:
#   Upscale Engine: rtxvideo
#   Video Encoder: hevc_nvenc
#   Quality Mode: best
#   Face Restoration: Enabled
#   Audio Upmix: demucs
# ...
```

## Hardware Info Class

### HardwareInfo Dataclass

```python
@dataclass
class HardwareInfo:
    vendor: GPUVendor             # nvidia, amd, intel, cpu
    tier: GPUTier                 # Performance tier
    name: str                     # GPU name
    vram_gb: float                # VRAM in GB
    driver_version: Optional[str] # Driver version
    cuda_version: Optional[str]   # CUDA version
    compute_capability: Optional[str]  # Compute capability

    # Capabilities
    has_nvenc: bool               # Hardware encoding
    has_rtx_video_sdk: bool       # RTX Video SDK installed
    has_cuda: bool                # CUDA available
    has_vulkan: bool              # Vulkan support

    # Properties
    @property
    def display_name(self) -> str:
        """Human-readable name for display"""

    @property
    def supports_ai_upscaling(self) -> bool:
        """Check if AI upscaling available"""

    @property
    def supports_hardware_encoding(self) -> bool:
        """Check if hardware encoding available"""

    @property
    def is_rtx_capable(self) -> bool:
        """Check if RTX Video SDK supported"""
```

## Configuration Dictionary

The `get_optimal_config()` function returns:

```python
{
    # Core settings
    "upscale_engine": str,    # 'rtxvideo', 'realesrgan', or 'ffmpeg'
    "encoder": str,           # 'hevc_nvenc', 'h264_nvenc', 'libx265', 'libx264'
    "quality": str,           # 'best', 'balanced', or 'good'

    # Feature flags
    "face_restore": bool,     # Enable face restoration
    "audio_upmix": str,       # 'demucs', 'surround', 'simple', 'none'

    # Model selection
    "realesrgan_model": str,  # Real-ESRGAN model name

    # User feedback
    "explanation": str,       # Human-readable explanation
    "warnings": List[str]     # List of warnings/limitations
}
```

## Warning Messages

The system generates context-specific warnings:

### RTX GPUs without RTX Video SDK
```
"RTX Video SDK not installed. Using Real-ESRGAN instead.
Install RTX Video SDK for best quality: terminalai-setup-rtx"
```

### Low VRAM
```
"Limited VRAM - face restoration disabled to prevent out-of-memory errors"
```

### GTX 16/10 Series
```
"GTX series doesn't support RTX Video SDK. Using Real-ESRGAN for AI upscaling."
```

### AMD/Intel GPUs
```
"AMD GPU detected. Using Vulkan-based Real-ESRGAN. Some CUDA-only features unavailable."
```

### CPU-Only
```
"No GPU detected. Processing will be VERY slow (10-50x slower)."
"Consider using a system with GPU for practical use."
"AI features (upscaling, face restoration) unavailable."
```

## Integration Points

### GUI Integration

The GUI (`gui.py`) integrates hardware detection via:

1. **Hardware Info Display**
   ```python
   hardware_info = gr.HTML(value=get_hardware_info_html())
   ```

2. **Optimal Defaults**
   ```python
   hw_defaults = get_hardware_defaults()
   upscale_engine = gr.Dropdown(value=hw_defaults.get('upscale_engine', 'auto'))
   encoder = gr.Dropdown(value=hw_defaults.get('encoder', 'hevc_nvenc'))
   ```

3. **Startup Detection**
   ```python
   def create_gui():
       # Detect hardware on startup
       AppState.detect_hardware_once()
       ...
   ```

### CLI Integration

Command-line tools can use:

```python
from vhs_upscaler.hardware_detection import detect_hardware, get_optimal_config

# In argparse setup
hw = detect_hardware()
config = get_optimal_config(hw)

parser.add_argument('--engine', default=config['upscale_engine'])
parser.add_argument('--encoder', default=config['encoder'])
```

## Performance Considerations

### Detection Speed

- **NVIDIA detection**: ~50-200ms (nvidia-smi call)
- **AMD/Intel detection**: ~100-300ms (wmic/lspci call)
- **Total overhead**: <500ms on first call

Detection is cached in `AppState.hardware` to avoid repeated calls.

### Graceful Degradation

The system gracefully handles:
- Missing nvidia-smi (CPU-only mode)
- Missing PyTorch (disables CUDA checks)
- Missing RTX Video SDK (falls back to Real-ESRGAN)
- Insufficient VRAM (disables memory-intensive features)

## Troubleshooting

### No GPU Detected

**Symptom**: "No GPU detected - using CPU-only mode"

**Solutions**:
1. Verify GPU driver installed: `nvidia-smi` (NVIDIA) or Device Manager (Windows)
2. Update GPU drivers to latest version
3. Check GPU is properly seated in PCIe slot
4. Verify power cables connected (high-end GPUs)

### Wrong GPU Tier

**Symptom**: RTX 3080 detected as "Legacy GPU"

**Solutions**:
1. Update NVIDIA drivers (requires 535+ for RTX features)
2. Check GPU name in nvidia-smi output
3. Report issue if GPU model not recognized

### RTX Video SDK Not Detected

**Symptom**: RTX GPU but RTX Video SDK shows as unavailable

**Solutions**:
1. Install RTX Video SDK: `terminalai-setup-rtx`
2. Set environment variable: `RTX_VIDEO_SDK_HOME=C:\Program Files\NVIDIA Corporation\NVIDIA RTX Video SDK`
3. Verify installation directory exists

### CUDA Not Available

**Symptom**: PyTorch installed but CUDA shows as unavailable

**Solutions**:
1. Install CUDA-enabled PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cu121`
2. Check CUDA version compatibility: `nvidia-smi` shows CUDA version
3. Verify torch.cuda.is_available() returns True

## Best Practices

### For Users

1. **Let auto-detection work**: Don't override settings unless you have specific needs
2. **Check warnings**: Review any warnings in the hardware info display
3. **Upgrade drivers**: Keep GPU drivers up-to-date for best compatibility
4. **Install RTX Video SDK**: For RTX 20+ GPUs, install SDK for best quality

### For Developers

1. **Cache detection results**: Use `AppState.detect_hardware_once()` to avoid repeated calls
2. **Handle missing hardware gracefully**: Always provide CPU-only fallback
3. **Test on multiple GPUs**: Verify detection works on NVIDIA, AMD, Intel, and CPU-only
4. **Update tier classification**: Add new GPU models to `_classify_nvidia_tier()` as released

## Future Enhancements

Planned improvements:

1. **VRAM usage estimation**: Predict memory requirements before processing
2. **Multi-GPU support**: Detect and utilize multiple GPUs
3. **AMD ROCm detection**: Better AMD GPU detection via ROCm
4. **Intel oneAPI detection**: Enhanced Intel GPU detection
5. **Performance benchmarking**: Measure actual processing speed
6. **Auto-scaling**: Adjust settings based on available VRAM
7. **Cloud GPU detection**: Detect AWS/Azure/GCP GPU instances

## Related Documentation

- [Installation Guide](WINDOWS_INSTALLATION.md) - GPU driver installation
- [RTX Video SDK Setup](../vhs_upscaler/setup_rtx.py) - RTX SDK installation
- [Verification Guide](VERIFICATION_GUIDE.md) - System verification
- [Troubleshooting](INSTALLATION_TROUBLESHOOTING.md) - Common issues

## API Reference

### Functions

#### `detect_hardware() -> HardwareInfo`
Detect available hardware and return capabilities.

#### `get_optimal_config(hw: HardwareInfo) -> Dict[str, Any]`
Get optimal configuration for detected hardware.

#### `print_hardware_report(hw: HardwareInfo, config: Dict[str, Any])`
Print formatted hardware detection report.

#### `detect_nvidia_gpu() -> Optional[HardwareInfo]`
Detect NVIDIA GPU specifically.

#### `detect_amd_gpu() -> Optional[HardwareInfo]`
Detect AMD GPU specifically.

#### `detect_intel_gpu() -> Optional[HardwareInfo]`
Detect Intel GPU specifically.

### Enums

#### `GPUVendor`
- `NVIDIA`: NVIDIA GPUs
- `AMD`: AMD GPUs
- `INTEL`: Intel GPUs
- `CPU_ONLY`: No GPU

#### `GPUTier`
- `RTX_50_SERIES`: RTX 5090, 5080, etc.
- `RTX_40_SERIES`: RTX 4090, 4080, etc.
- `RTX_30_SERIES`: RTX 3090, 3080, etc.
- `RTX_20_SERIES`: RTX 2080, 2070, etc.
- `GTX_16_SERIES`: GTX 1660, 1650, etc.
- `GTX_10_SERIES`: GTX 1080, 1070, etc.
- `GTX_LEGACY`: Older GTX cards
- `AMD_RDNA3`: RX 7000 series
- `AMD_RDNA2`: RX 6000 series
- `AMD_RDNA`: RX 5000 series
- `AMD_LEGACY`: Older AMD cards
- `INTEL_ARC`: Intel Arc GPUs
- `INTEL_INTEGRATED`: Intel iGPUs
- `CPU_ONLY`: No GPU detected

## License

Part of TerminalAI v1.5.1+
See main project LICENSE for details.
