# First-Run Setup Wizard

## Overview

The first-run wizard is an interactive setup system that runs automatically on TerminalAI's first launch. It solves the "frozen app" UX problem where large AI models (350MB+) download during video processing without user awareness.

## Features

### 1. Hardware Detection
- Automatically detects GPU (NVIDIA, AMD, Intel, or CPU-only)
- Reports VRAM capacity for NVIDIA GPUs
- Identifies CUDA support and compute capability
- Provides hardware-specific recommendations

### 2. Model Downloads
- **GFPGAN v1.3** (332 MB) - Face restoration
- **CodeFormer v0.1.0** (360 MB) - Advanced face restoration
- Real-time progress tracking:
  - Download speed (MB/s)
  - Progress percentage
  - Estimated time remaining
  - Current file being downloaded

### 3. Configuration
- Sets optimal defaults based on detected hardware
- Configures GPU acceleration if available
- Enables hardware-accelerated encoding (NVENC)
- Saves preferences for future use

### 4. Skip Logic
- If models already exist, skips download phase
- Shows "Welcome back!" message for returning users
- Goes straight to main GUI after initial setup

## User Flow

```
┌─────────────────────────────────────────┐
│  First Launch                           │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Phase 1: Hardware Detection            │
│  ✓ Detect GPU                           │
│  ✓ Check VRAM                           │
│  ✓ Verify CUDA support                  │
│  ✓ Show recommendations                 │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Phase 2: Model Download                │
│  📥 GFPGAN (332 MB)                     │
│     [████████████░░░] 65%               │
│     Speed: 15.2 MB/s                    │
│     ETA: 2 minutes                      │
│                                         │
│  📥 CodeFormer (360 MB)                 │
│     [░░░░░░░░░░░░░] Waiting...         │
│                                         │
│  [Skip Download] (optional)             │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Phase 3: Configuration Summary         │
│  - GPU acceleration: Enabled            │
│  - Hardware encoding: NVENC             │
│  - AI models: GPU-accelerated           │
│                                         │
│  [Complete Setup]                       │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Setup Complete!                        │
│  Launching main application...          │
└─────────────────────────────────────────┘
```

## Technical Architecture

### Components

#### 1. `HardwareDetector`
Detects system hardware and capabilities.

```python
from first_run_wizard import HardwareDetector

detector = HardwareDetector()
gpu_info = detector.detect_gpu()

# Returns:
{
    "vendor": "nvidia",  # or "amd", "intel", "cpu"
    "name": "NVIDIA GeForce RTX 3060",
    "vram_mb": 12288,  # MB
    "cuda_available": True,
    "compute_capability": "8.6"
}
```

**Detection Methods:**
- **NVIDIA**: PyTorch CUDA detection (most reliable)
- **AMD**: ROCm detection via `torch.hip`
- **Intel**: WMI queries on Windows
- **Fallback**: CPU-only mode

#### 2. `ModelDownloader`
Downloads AI models with progress tracking.

```python
from first_run_wizard import ModelDownloader

downloader = ModelDownloader()

# Download with progress callback
def on_progress(downloaded_mb, total_mb, speed_mbps, eta_seconds, status_msg):
    print(f"{downloaded_mb:.1f}/{total_mb:.1f} MB - {speed_mbps:.1f} MB/s - ETA: {eta_seconds:.0f}s")

success, message = downloader.download_gfpgan(
    model_version="v1.3",
    progress_callback=on_progress
)
```

**Features:**
- Streams downloads to avoid memory issues
- Calculates real-time speed and ETA
- Supports cancellation
- Verifies checksums (SHA256)
- Graceful error handling

#### 3. `FirstRunManager`
Manages first-run state and configuration.

```python
from first_run_wizard import FirstRunManager

# Check if first run
if FirstRunManager.is_first_run():
    print("Running wizard...")

# Mark setup complete
config = {
    "gpu_vendor": "nvidia",
    "cuda_available": True
}
FirstRunManager.mark_complete(config)

# Load saved config
config = FirstRunManager.load_config()
```

**Storage:**
- Cache directory: `~/.cache/terminalai/`
- Marker file: `.first_run_complete`
- Config file: `config.json`

### Integration with GUI

The wizard integrates seamlessly with `vhs_upscaler/gui.py`:

```python
# gui.py main() function

# Check if first run
if FirstRunManager.is_first_run():
    # Launch wizard
    wizard = create_wizard_ui()
    wizard.launch(inbrowser=True)

    # Wait for completion
    if not FirstRunManager.is_first_run():
        print("Setup complete! Launching main app...")
    else:
        print("Setup incomplete. Please run again.")
        return

# Launch main application
app = create_gui()
app.launch(inbrowser=True)
```

## Command-Line Options

### Launch Main GUI

```bash
# Normal launch (shows wizard if first run)
python -m vhs_upscaler.gui

# Skip wizard (for debugging)
python -m vhs_upscaler.gui --skip-wizard

# Reset wizard state (force re-run)
python -m vhs_upscaler.gui --reset-wizard
```

### Test Wizard Standalone

```bash
# Run wizard directly
python -m vhs_upscaler.first_run_wizard

# Check wizard status
python -m vhs_upscaler.first_run_wizard --check

# Reset wizard state
python -m vhs_upscaler.first_run_wizard --reset
```

## Customization

### Adding New Models

Edit `first_run_wizard.py` to add new models to download:

```python
def download_new_model(self, progress_callback=None):
    """Download a new AI model."""
    from some_module import ModelClass

    model = ModelClass()
    if model.model_path.exists():
        return True, "Model already downloaded"

    return self._download_with_progress(
        url="https://example.com/model.pth",
        output_path=model.model_path,
        total_size_mb=500,
        model_name="New Model"
    )
```

Then update the wizard UI in `create_wizard_ui()`:

```python
# Add new model download group
with gr.Group():
    gr.Markdown("### New Model (AI Enhancement)")
    new_model_status = gr.Markdown("Status: Not started")
    new_model_bar = gr.Slider(...)
    new_model_details = gr.Markdown("")
```

### Customizing Hardware Detection

Add custom GPU detection logic:

```python
@staticmethod
def detect_custom_gpu():
    """Detect custom GPU vendor."""
    try:
        # Your detection logic
        import custom_gpu_lib
        if custom_gpu_lib.is_available():
            return {
                "vendor": "custom",
                "name": "Custom GPU",
                "vram_mb": 8192,
                "cuda_available": False,
            }
    except:
        pass

    return None
```

## Troubleshooting

### Wizard Doesn't Launch

**Symptom:** Main GUI launches directly on first run.

**Solutions:**
1. Check if marker file exists: `~/.cache/terminalai/.first_run_complete`
2. Reset wizard state: `python -m vhs_upscaler.gui --reset-wizard`
3. Check logs for import errors

### Download Fails

**Symptom:** Model download shows error or hangs.

**Solutions:**
1. Check internet connection
2. Verify firewall/antivirus not blocking downloads
3. Try downloading manually from GitHub releases
4. Check disk space (need ~1 GB free)

### GPU Not Detected

**Symptom:** Shows "CPU Only" despite having GPU.

**Solutions:**
1. Verify PyTorch installed: `pip install torch`
2. Check CUDA drivers: `nvidia-smi` (NVIDIA)
3. Verify GPU compatibility (CUDA 11.8+ for RTX)
4. See `docs/WINDOWS_INSTALLATION.md` for detailed setup

### Progress Bar Stuck

**Symptom:** Download progress freezes at certain percentage.

**Solutions:**
1. Wait 2-3 minutes (large chunks may take time)
2. Check network stability
3. Cancel and restart wizard
4. Skip download and install models manually

## Manual Model Installation

If wizard download fails, install models manually:

### GFPGAN v1.3

```bash
# Download
wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth

# Place in models directory
mkdir -p models/gfpgan
mv GFPGANv1.3.pth models/gfpgan/
```

### CodeFormer v0.1.0

```bash
# Download
wget https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth

# Place in models directory
mkdir -p models/codeformer
mv codeformer.pth models/codeformer/
```

After manual installation, mark wizard as complete:

```bash
python -m vhs_upscaler.first_run_wizard --check
# If still shows first run:
mkdir -p ~/.cache/terminalai
echo "Manual setup completed" > ~/.cache/terminalai/.first_run_complete
```

## Testing

Run automated tests:

```bash
# Full test suite
pytest tests/test_first_run_wizard.py -v

# Specific test
pytest tests/test_first_run_wizard.py::TestHardwareDetector::test_detect_gpu_nvidia -v

# Integration test
pytest tests/test_first_run_wizard.py::TestWizardIntegration -v
```

## Future Enhancements

Planned improvements:

1. **Multiple Model Versions**: Let users choose GFPGAN v1.3 vs v1.4
2. **Parallel Downloads**: Download multiple models simultaneously
3. **Resume Downloads**: Continue interrupted downloads
4. **Bandwidth Limiting**: Throttle download speed if needed
5. **Model Verification**: Enhanced checksum verification
6. **Cloud Storage**: Mirror downloads from CDN for reliability
7. **Offline Mode**: Bundle models with installer (optional)

## FAQ

### Q: Can I skip the wizard?
**A:** Yes, use `--skip-wizard` flag. Models will download during first video processing instead.

### Q: How long does setup take?
**A:** 5-15 minutes depending on internet speed (downloading ~700 MB total).

### Q: Is an internet connection required?
**A:** Yes, for initial model downloads. After that, TerminalAI works offline.

### Q: Can I run the wizard again?
**A:** Yes, use `--reset-wizard` to clear state and re-run setup.

### Q: What if I have slow internet?
**A:** Use "Skip Download" button in wizard and download models manually later.

### Q: Does the wizard require admin privileges?
**A:** No, all files stored in user's home directory (`~/.cache/terminalai/`).

## References

- **Main Documentation**: `README.md`
- **Installation Guide**: `docs/WINDOWS_INSTALLATION.md`
- **GPU Setup**: `docs/GPU_SETUP.md`
- **Troubleshooting**: `docs/INSTALLATION_TROUBLESHOOTING.md`
- **Face Restoration**: `vhs_upscaler/face_restoration.py`

## Contributing

To contribute wizard improvements:

1. **Add Features**: Edit `vhs_upscaler/first_run_wizard.py`
2. **Add Tests**: Update `tests/test_first_run_wizard.py`
3. **Update Docs**: Edit this file
4. **Test Thoroughly**: Run test suite and manual testing
5. **Submit PR**: Include before/after screenshots

### Development Guidelines

- Use Gradio's built-in themes for consistency
- Add progress tracking for all long-running operations
- Provide clear error messages with actionable solutions
- Test on Windows, Linux, and macOS
- Test with and without GPU
- Test with slow/interrupted internet connections

---

**Last Updated:** 2025-12-19
**Version:** 1.5.1
**Status:** Production Ready
