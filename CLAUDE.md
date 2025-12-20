# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🎯 Meta Orchestrator Role

**YOU ARE A META ORCHESTRATOR AGENT WITH 40+ SPECIALIZED AGENTS AT YOUR DISPOSAL.**

Your primary role is **intelligent routing and coordination**, not direct implementation.

### Core Principles

1. **Route, Don't Execute**: Launch specialized agents for non-trivial tasks
2. **Intelligent Matching**: Route to agents with relevant expertise (python-pro, security-auditor, test-automator, etc.)
3. **Parallel Coordination**: Launch multiple agents concurrently when tasks are independent
4. **Strategic Delegation**: Break complex work into specialized subtasks
5. **Quality Orchestration**: Use review agents to validate work before completion
6. **Background Execution Priority**: ALWAYS run agents in background using `run_in_background=true` unless you need immediate results

### Orchestration Example

```
User: "Add user authentication to the app"

1. Launch Explore agent → understand existing patterns
2. Launch Plan agent → design approach
3. Launch security-auditor → review requirements (parallel)
4. Launch python-pro + react-specialist → implement (parallel)
5. Launch test-automator → create tests
6. Launch code-reviewer + security-auditor → final review (parallel)
```

### Background Execution Pattern

```python
# GOOD: Parallel background execution (2 min total)
reviewer = Task(subagent_type="code-reviewer", run_in_background=True, ...)
tester = Task(subagent_type="test-automator", run_in_background=True, ...)
docs = Task(subagent_type="documentation-engineer", run_in_background=True, ...)

# Do other work, then collect results
review = TaskOutput(task_id=reviewer.agent_id, block=True)
tests = TaskOutput(task_id=tester.agent_id, block=True)

# BAD: Sequential blocking (4 min total)
Task(subagent_type="code-reviewer", ...)  # Wait 2 min
Task(subagent_type="test-automator", ...) # Wait 1 min
Task(subagent_type="documentation-engineer", ...) # Wait 1 min
```

---

## Project Overview

**TerminalAI** is an AI-powered video processing suite for upscaling VHS/DVD footage with NVIDIA RTX acceleration, YouTube downloading, audio enhancement, and surround sound upmixing.

**Current Version:** 1.5.1
**Status:** Production ready (98%+ test pass rate, 246+/251 tests passing)

### v1.5.1 Key Features (December 2025)

- **RTX Video SDK Integration**: AI upscaling for RTX 20/30/40/50 series (replaces deprecated Maxine)
- **RTX 50 Series Support**: Full Ada Lovelace Next architecture support (sm_120)
- **AI Audio**: DeepFilterNet denoising, AudioSR upsampling, CodeFormer face restoration
- **Critical Bug Fixes**: Hardware detection hanging, QueueJob parameters, Gradio 6.0 theme, PowerShell encoding
- **Cinema-Grade GUI**: Professional dark theme (see `docs/GUI_DESIGN_SPECIFICATION.md`)
- **Automated Installation**: Windows installer with CUDA detection (`install_windows.py`)

---

## Key Commands

### Development Setup
```bash
# Install with all features
pip install -e ".[full]"

# Windows with CUDA (automated)
python install_windows.py --full

# Verify installation
python scripts/installation/verify_installation.py
```

### Running
```bash
# GUI (primary interface)
python -m vhs_upscaler.gui

# CLI processing
python -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4 --preset vhs

# Testing
pytest tests/ -v
pytest tests/ --cov=vhs_upscaler
```

---

## Architecture Overview

### Core Pipeline

1. **Download** (optional): YouTube/URL via yt-dlp
2. **Preprocessing**: Deinterlacing, denoising, color correction
3. **AI Upscaling**: RTX Video SDK → Real-ESRGAN → FFmpeg (fallback chain)
4. **Encoding**: NVENC hardware encoding or CPU fallback
5. **Audio Processing** (optional): Enhancement, AudioSR, surround upmix

### Key Classes

**`VideoUpscaler`** (`vhs_upscale.py`)
- Main pipeline coordinator
- Engine detection and selection (RTX Video SDK, Real-ESRGAN, FFmpeg)
- FFmpeg filter chain management

**`VideoQueue`** (`queue_manager.py`)
- Thread-safe job queue with lifecycle management
- Status tracking: PENDING → PROCESSING → COMPLETED/FAILED

**`AudioProcessor`** (`audio_processor.py`)
- DeepFilterNet AI denoising (v1.5.0)
- AudioSR upsampling to 48kHz (v1.5.0)
- Surround upmix (simple/surround/prologic/demucs AI)
- Graceful fallbacks when AI unavailable

**`FaceRestorer`** (`face_restoration.py`)
- Dual-backend: CodeFormer (best) → GFPGAN (fallback)
- Automatic model download

**`AppState`** (`gui.py`)
- Gradio GUI state management
- Settings persistence, log buffering

### Module Organization

```
vhs_upscaler/
├── vhs_upscale.py         # Main pipeline, VideoUpscaler
├── queue_manager.py        # VideoQueue, QueueJob, JobStatus
├── audio_processor.py      # Audio enhancement, AI backends
├── face_restoration.py     # CodeFormer + GFPGAN
├── notifications.py        # Webhooks, email alerts
├── gui.py                  # Gradio interface
├── logger.py               # Logging config
└── config.yaml             # Presets and defaults

tests/                      # 251 tests, 98%+ pass rate
scripts/installation/       # Verification, installers
docs/                       # Comprehensive documentation
```

### Configuration (`config.yaml`)

**Presets**: vhs, dvd, webcam, youtube, clean
**Defaults**: Resolution, encoder, CRF, quality mode
**Paths**: FFmpeg, model locations

### Upscale Engine Priority

1. **RTX Video SDK** (RTX 20/30/40/50, best quality)
2. **Real-ESRGAN** (AMD/Intel/NVIDIA, good quality)
3. **FFmpeg** (CPU fallback, acceptable quality)

### Audio Processing Order

```
1. Enhancement (DeepFilterNet or FFmpeg)
2. AudioSR Upsampling (if needed)
3. Surround Upmix (optional)
4. Normalization
5. Encoding
```

All AI features include graceful fallbacks.

---

## Important Implementation Details

### Thread Safety
- `VideoQueue`: `threading.Lock()` for all operations
- `UnifiedProgress`: Locked progress updates
- GUI: Main Gradio thread for callbacks

### Temporary Files
- `tempfile.mkdtemp()` with unique prefixes
- Cleanup in `finally` blocks
- `keep_temp` config option for debugging

### FFmpeg Filter Chains
```
scale → deinterlace → denoise → color correction → encode
```

Example (VHS preset):
```
yadif=1:0:0,hqdn3d=3:2:3:2,eq=contrast=1.1:brightness=0.05
```

### Error Handling
- Subprocess calls wrapped in try-except with logging
- Graceful degradation through fallback chain
- Queue jobs marked FAILED with error messages
- User-friendly GUI error messages

---

## Development Guidelines

### Code Style
- Line length: 100 characters (Black/Ruff)
- Python 3.10+ (3.11 recommended, 3.12/3.13 supported)
- Google-style docstrings
- Dataclasses for config objects
- Enums for fixed option sets

### Logging
```python
logger = logging.getLogger(__name__)
# INFO: user-visible operations
# DEBUG: technical details
# WARNING: recoverable issues
# ERROR: failures
```

### FFmpeg Subprocess Pattern
```python
cmd = ["ffmpeg", "-i", input_file, ...]  # List args (security)
result = subprocess.run(cmd, capture_output=True, text=True, check=True)
```

### Gradio 6.0 Theme Migration
```python
# IMPORTANT: Theme moved to launch() in Gradio 6.0
with gr.Blocks(css=custom_css) as app:  # No theme parameter
    pass

app.launch(theme=custom_theme)  # Theme applied here
```

### Hardware Detection with Timeout
```python
def detect_hardware_once():
    detection_result = {"hardware": None, "error": None}

    def run_detection():
        try:
            detection_result["hardware"] = detect_hardware()
        except Exception as e:
            detection_result["error"] = e

    thread = threading.Thread(target=run_detection, daemon=True)
    thread.start()
    thread.join(timeout=10.0)  # Prevent infinite hang

    if thread.is_alive():
        logger.error("Hardware detection timed out")
        # Use CPU fallback
```

### GPU Detection Optimization
```python
# ALWAYS try nvidia-smi first (0.06s), PyTorch import is slow (2-3s)
def detect_gpu():
    # Fast path: nvidia-smi
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, check=True, timeout=5
        )
        if result.stdout.strip():
            return parse_nvidia_smi_output(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Slow path: Only import PyTorch if nvidia-smi failed
    try:
        import torch  # 2-3s delay
        if torch.cuda.is_available():
            return get_pytorch_gpu_info()
    except ImportError:
        pass

    return {"has_gpu": False}
```

---

## Testing

**Test Suite**: 251 tests, 98%+ pass rate
**Coverage**: 85%+ estimated
**Execution**: ~15-20 seconds

### Test Categories
- GUI & Interface: 45 tests (100%)
- Queue Management: 25 tests (100%)
- Audio Processing: 37 tests (95%)
- Video Processing: 120 tests (99%+)
- Hardware Detection: 35 tests (100%)
- Security: 15 tests (100%)
- Face Restoration: 23 tests (100%)

### Running Tests
```bash
# Full suite
pytest tests/ -v

# Critical tests only
pytest tests/test_gui_launch.py \
       tests/test_hardware_detection_fix.py \
       tests/test_security_shell_injection.py -v

# With coverage
pytest tests/ --cov=vhs_upscaler --cov-report=html
```

### Verification System
```bash
# Comprehensive check
python scripts/installation/verify_installation.py

# Quick check
python scripts/installation/verify_installation.py --quick

# Component-specific
python scripts/installation/verify_installation.py --check pytorch
```

---

## Presets

| Preset  | Source         | Deinterlace | Denoise           | Use Case          |
|---------|----------------|-------------|-------------------|-------------------|
| vhs     | 480i VHS       | Yes         | Strong (3,2,3,2)  | Old home videos   |
| dvd     | 480p/576p DVD  | Yes         | Moderate (2,1,2,1)| DVD rips          |
| webcam  | Low-quality    | No          | Strong (4,3,4,3)  | Webcam footage    |
| youtube | Downloaded     | No          | Light             | YouTube videos    |
| clean   | High-quality   | No          | None              | Clean sources     |

---

## Dependencies

**Required:**
- Python 3.10+ (3.11 recommended)
- FFmpeg

**GPU Acceleration (Recommended):**
- NVIDIA Driver 535+
- RTX Video SDK (RTX 20/30/40/50)
- PyTorch with CUDA 12.1+ (cu128 for RTX 50)

**Optional AI Features:**
- DeepFilterNet (audio denoising)
- AudioSR (audio upsampling)
- CodeFormer (face restoration)
- GFPGAN (face restoration fallback)
- Demucs (AI surround upmix)

**Python Compatibility:**
- 3.10: Fully compatible
- 3.11: Recommended (most stable)
- 3.12: Fully compatible
- 3.13: Compatible with patches

All optional dependencies gracefully degrade with fallbacks.

---

## Critical Bug Fixes (v1.5.1)

### 1. Hardware Detection Hanging
**Problem:** GUI stuck on "Detecting hardware..." indefinitely
**Solution:** 10-second timeout wrapper, nvidia-smi prioritization (0.06s vs 2-3s PyTorch import)
**Result:** Infinite hang → 0.06s (150× improvement)
**Files:** `gui.py`, `hardware_detection.py`, `first_run_wizard.py`

### 2. QueueJob Missing Parameters
**Problem:** Crashes with face restoration/AudioSR enabled
**Solution:** Added `face_model`, `audio_sr_enabled`, `audio_sr_model` parameters
**Files:** `queue_manager.py`, `gui.py`

### 3. PowerShell Unicode Encoding
**Problem:** Installation script fails on Unicode symbols
**Solution:** Replaced Unicode (✓✗⚠) with ASCII ([OK][FAIL][WARN])
**Files:** `scripts/installation/install_windows.ps1`

### 4. Gradio 6.0 Theme Migration
**Problem:** Custom theme not applied
**Solution:** Moved theme parameter from `gr.Blocks()` to `app.launch()`
**Files:** `gui.py`

---

## Known Issues

### RTX 50 Series PyTorch
**Issue:** Requires PyTorch nightly with cu128
**Workaround:**
```bash
pip install torch torchvision torchaudio --pre --index-url https://download.pytorch.org/whl/nightly/cu128
```

### basicsr torchvision Compatibility
**Issue:** basicsr incompatible with torchvision 0.17+
**Workaround:** Automated patch applied (`scripts/installation/patch_basicsr.py`)

---

## Common Development Patterns

### Adding New Upscale Engine
1. Add detection in `VideoUpscaler._check_dependencies()`
2. Implement `_upscale_with_newengine()` method
3. Add to `available_engines` list
4. Update `_upscale()` routing logic
5. Update GUI dropdowns

### Adding New Audio Effect
1. Define enum in `AudioEnhanceMode` or `UpmixMode`
2. Add filter chain in `AudioProcessor._build_enhancement_filters()`
3. Add to `AudioConfig` dataclass
4. Update GUI options
5. Add tests

### Adding New Preset
1. Define in `config.yaml` under `presets:`
2. Add to GUI dropdown
3. Document in README.md

---

## GUI Design System

**Full specification:** `docs/GUI_DESIGN_SPECIFICATION.md` (1,935 lines)

**Design Philosophy:**
- Dark-mode first (cinema-grade palette)
- Professional aesthetics (DaVinci Resolve inspired)
- WCAG 2.1 AA compliant
- GPU-accelerated feel

**Color Palette:**
- Background: #0a0e1a (deep space black)
- Accent: #5865f2 (Discord Blue)
- GPU: #76b900 (NVIDIA Green)
- Status: Green (completed), Purple (processing), Red (failed)

---

## Intelligent Video Analysis System

**Status:** Planned (not implemented)
**Plan:** `C:\Users\justi\.claude\plans\zippy-frolicking-chipmunk.md`

**Overview:** Auto-detect video characteristics (interlacing, noise, artifacts) and recommend optimal processing settings.

**Planned Features:**
- Multi-backend analysis (Python+OpenCV → Bash → FFprobe)
- VHS artifact detection (head switching noise, color bleeding, dropouts)
- Preset recommendations based on analysis
- JSON import/export for batch processing

**Implementation:** ~1,300 lines of new code across 7 files

---

## Documentation

**Installation:**
- `docs/installation/WINDOWS_INSTALLATION.md` - Comprehensive guide
- `docs/installation/VERIFICATION_GUIDE.md` - Verification system
- `docs/installation/INSTALLATION_TROUBLESHOOTING.md` - 850-line troubleshooting

**Technical Fixes:**
- `HARDWARE_DETECTION_FIX.md` - Hardware detection fix (280 lines)
- `POWERSHELL_UNICODE_FIX.md` - Encoding fix (128 lines)
- `docs/GUI_DESIGN_SPECIFICATION.md` - GUI design (1,935 lines)

**Testing:**
- `scripts/installation/verify_installation.py` - Comprehensive verification (1,100+ lines)
- `tests/` - 31 test files, 251 tests

**Development:**
- `CLAUDE.md` - This file (maintainer guide)
- `README.md` - User-facing documentation
