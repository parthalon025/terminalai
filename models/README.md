# Models Directory

This directory contains AI models used by TerminalAI for upscaling and enhancement.

## Overview

Models are downloaded automatically when first needed. This directory is intentionally kept minimal in the repository to avoid large file sizes.

## Model Types

### 1. Real-ESRGAN Models (External)

Real-ESRGAN models are bundled with the `realesrgan-ncnn-vulkan` executable and don't need to be downloaded separately.

**Models included:**
- `realesrgan-x4plus` - General purpose 4x upscaling
- `realesrgan-x4plus-anime` - Optimized for animation
- `realesr-animevideov3` - Video-specific anime model

**Installation:**
Download Real-ESRGAN from: https://github.com/xinntao/Real-ESRGAN/releases

### 2. GFPGAN Models (Auto-download)

GFPGAN models for face restoration are downloaded automatically on first use.

**Default model:** `GFPGANv1.3.pth` (~332 MB)

**Download location:** `models/gfpgan/`

**Manual download:**
```bash
# If auto-download fails, download manually
mkdir -p models/gfpgan
cd models/gfpgan
wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth
```

### 3. NVIDIA Maxine Models (Bundled with SDK)

NVIDIA Maxine Video Super Resolution models are included with the Maxine SDK installation.

**Maxine SDK location:**
- Windows: `C:\Program Files\NVIDIA Corporation\NVIDIA Video Effects`
- Linux: `/opt/nvidia/maxine` or custom `$MAXINE_HOME`

**Installation:**
Download Maxine SDK from: https://developer.nvidia.com/maxine

### 4. Demucs Models (Auto-download)

Demucs models for AI audio separation are downloaded automatically when using the audio upmix feature.

**Default model:** `htdemucs` (~2 GB)

**Download location:** `~/.cache/torch/hub/checkpoints/`

## Disk Space Requirements

| Model | Size | Feature | Auto-Download |
|-------|------|---------|---------------|
| Real-ESRGAN (bundled) | ~50 MB | AI upscaling | With executable |
| GFPGAN v1.3 | ~332 MB | Face restoration | Yes |
| NVIDIA Maxine | ~500 MB | Best upscaling (RTX) | With SDK installer |
| Demucs htdemucs | ~2 GB | Audio AI separation | Yes |

**Total (all features):** ~3 GB

## Configuration

### Setting Model Paths

You can configure custom model paths in `vhs_upscaler/config.yaml`:

```yaml
models:
  gfpgan_path: "models/gfpgan/GFPGANv1.3.pth"
  realesrgan_path: "/path/to/realesrgan-ncnn-vulkan"
  maxine_path: "C:\\Program Files\\NVIDIA Corporation\\NVIDIA Video Effects"
```

### Environment Variables

- `MAXINE_HOME` - NVIDIA Maxine SDK installation directory
- `TORCH_HOME` - PyTorch cache directory (for Demucs models)

## Troubleshooting

### Model Download Fails

**GFPGAN:**
```bash
# Check internet connection
ping github.com

# Try manual download
wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth \
  -O models/gfpgan/GFPGANv1.3.pth
```

**Demucs:**
```bash
# Pre-download Demucs model
python -c "import torch; torch.hub.load('facebookresearch/demucs', 'htdemucs')"
```

### Model Not Found

If TerminalAI reports "model not found":

1. **Check model exists:**
   ```bash
   ls -lh models/gfpgan/
   ```

2. **Verify permissions:**
   ```bash
   chmod -R 755 models/
   ```

3. **Check config.yaml paths:**
   ```bash
   cat vhs_upscaler/config.yaml
   ```

### Disk Space Issues

To clean up cached models:

```bash
# Remove GFPGAN models
rm -rf models/gfpgan/*.pth

# Remove Demucs models
rm -rf ~/.cache/torch/hub/checkpoints/
```

Models will be re-downloaded automatically when needed.

## Model Licenses

- **Real-ESRGAN:** BSD-3-Clause License
- **GFPGAN:** Apache License 2.0
- **NVIDIA Maxine:** NVIDIA SDK License Agreement
- **Demucs:** MIT License

Please review individual model licenses before commercial use.

## Adding Custom Models

To use custom trained models:

1. Place model file in appropriate directory
2. Update `config.yaml` with model path
3. Ensure model is compatible with TerminalAI's architecture

Example for custom GFPGAN model:

```yaml
face_restore_model: "models/gfpgan/custom_model.pth"
```

## Performance Notes

- **Model loading time:** 2-10 seconds per model (first time only)
- **Memory usage:**
  - GFPGAN: ~2 GB VRAM
  - Real-ESRGAN: ~4 GB VRAM
  - Maxine: ~6 GB VRAM
  - Demucs: ~4 GB RAM

For best performance, ensure adequate VRAM/RAM is available.

---

For more information, see:
- [Main README](../README.md)
- [Deployment Guide](../docs/DEPLOYMENT.md)
- [Face Restoration Guide](../docs/FACE_RESTORATION.md)
