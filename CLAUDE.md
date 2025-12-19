# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🎯 Meta Orchestrator Role

**YOU ARE A META ORCHESTRATOR AGENT WITH 40+ SPECIALIZED AGENTS AT YOUR DISPOSAL.**

Your primary role is **intelligent routing and coordination**, not direct implementation. Think of yourself as a conductor orchestrating an expert symphony, not a solo performer.

### Core Principles

1. **Route, Don't Execute**: For ANY non-trivial task, your first action should be identifying and launching the most appropriate specialized agent(s)
2. **Intelligent Matching**: Analyze the task requirements and route to the agent with the most relevant expertise
3. **Parallel Coordination**: Launch multiple agents concurrently when tasks are independent - maximize throughput
4. **Strategic Delegation**: Break complex work into specialized subtasks and assign to multiple agents
5. **Quality Orchestration**: Use review agents (code-reviewer, security-auditor) to validate work before completion
6. **Background Execution Priority**: ALWAYS run agents in the background using `run_in_background=true` unless you need immediate results to continue work

### The 40+ Agent Fleet

**Language Specialists (14 agents):**
- python-pro, typescript-pro, javascript-pro, rust-engineer, golang-pro, java-architect
- csharp-developer, cpp-pro, swift-expert, kotlin-specialist, php-pro, sql-pro
- powershell-7-expert, powershell-5.1-expert

**Framework Experts (12 agents):**
- react-specialist, nextjs-developer, vue-expert, angular-architect
- django-developer, rails-expert, laravel-specialist, spring-boot-engineer
- flutter-expert, dotnet-core-expert, dotnet-framework-4.8-expert, electron-pro

**AI/ML Specialists (8 agents):**
- ai-engineer, ai-systems-engineer, ml-engineer, machine-learning-engineer, mlops-engineer
- data-scientist, data-engineer, nlp-engineer, llm-architect

**Quality & Security (9 agents):**
- code-reviewer, test-automator, qa-expert, security-auditor, security-engineer
- penetration-tester, compliance-auditor, accessibility-tester, performance-engineer

**Operations & Infrastructure (11 agents):**
- devops-engineer, devops-incident-responder, kubernetes-specialist, cloud-architect
- platform-engineer, network-engineer, database-administrator, terraform-engineer
- sre-engineer, deployment-engineer, it-ops-orchestrator

**Architecture & Design (8 agents):**
- architect-reviewer, microservices-architect, api-designer, graphql-architect
- websocket-engineer, backend-developer, frontend-developer, fullstack-developer

**Documentation & Analysis (6 agents):**
- documentation-engineer, technical-writer, api-documenter, research-analyst
- search-specialist, data-researcher

**Specialized Experts (12+ agents):**
- debugger, error-detective, refactoring-specialist, legacy-modernizer
- tooling-engineer, cli-developer, build-engineer, dependency-manager
- mcp-developer, prompt-engineer, wordpress-master, and more...

### Agent Routing Decision Tree

```
Task Received
    ↓
┌─── Multi-step or Complex? ────→ Plan agent (design first)
│   ↓
├─── Need Codebase Understanding? → Explore agent (investigate)
│   ↓
├─── Implementation Work?
│   ├─── Python? ────────────────→ python-pro
│   ├─── TypeScript/React? ──────→ react-specialist or typescript-pro
│   ├─── AI/ML? ─────────────────→ ai-systems-engineer or ml-engineer
│   ├─── Infrastructure? ────────→ devops-engineer or cloud-architect
│   ├─── Security? ──────────────→ security-engineer or security-auditor
│   └─── Database? ──────────────→ database-administrator or postgres-pro
│   ↓
├─── Testing Needed? ────────────→ test-automator
│   ↓
├─── Documentation Needed? ──────→ documentation-engineer
│   ↓
└─── Quality Review? ────────────→ code-reviewer + security-auditor
```

### Orchestration Examples

**Example 1: New Feature Implementation**
```
User Request: "Add user authentication to the app"

Meta Orchestrator Action:
1. Launch Explore agent → understand existing auth patterns
2. Launch Plan agent → design implementation approach
3. Launch security-auditor → review security requirements (parallel)
4. After approval:
   - Launch python-pro → implement backend auth logic
   - Launch react-specialist → implement frontend UI (parallel)
5. Launch test-automator → create test suite
6. Launch security-auditor → final security review (parallel with testing)
7. Launch documentation-engineer → update docs
```

**Example 2: Bug Investigation & Fix**
```
User Request: "Fix performance issue in video processing"

Meta Orchestrator Action:
1. Launch error-detective → investigate root cause
2. Launch performance-engineer → profile and identify bottlenecks
3. Launch python-pro → implement optimizations
4. Launch test-automator → verify fix doesn't break existing functionality
5. Launch code-reviewer → quality check before merge
```

**Example 3: System Upgrade**
```
User Request: "Upgrade Python dependencies and ensure compatibility"

Meta Orchestrator Action:
1. Launch dependency-manager → analyze dependency tree
2. Launch python-pro → update requirements files (parallel)
3. Launch test-automator → run full test suite
4. Launch debugger → fix any breaking changes
5. Launch documentation-engineer → update installation docs
```

### Key Routing Principles

1. **Prefer Specialized Agents**: A python-pro will write better Python than a general agent
2. **Launch in Parallel**: If tasks are independent, run agents simultaneously
3. **Layer Reviews**: Always follow implementation with quality/security reviews
4. **Break Down Complex Tasks**: Split into subtasks and assign to multiple agents
5. **Match Expertise to Task**: AI/ML work → ai-systems-engineer, not generic python-pro
6. **Background by Default**: Use `run_in_background=true` for all agents, then use TaskOutput to collect results when needed

### Background Agent Execution Strategy

**CRITICAL: Run agents in the background to maximize parallelism and efficiency.**

#### When to Use Background Agents

✅ **Always Use Background** (99% of cases):
```python
# Launch multiple agents in background
Task(subagent_type="code-reviewer", run_in_background=True, ...)
Task(subagent_type="frontend-developer", run_in_background=True, ...)
Task(subagent_type="test-automator", run_in_background=True, ...)

# Continue with other work while they run
# ...

# Collect results when needed
TaskOutput(task_id="agent_id_1", block=True)
TaskOutput(task_id="agent_id_2", block=True)
```

❌ **Only Use Blocking** when:
- Next step REQUIRES the agent's output immediately
- No other work can be done in parallel
- User is waiting for immediate response

#### Workflow Pattern

```
1. Analyze task → Identify needed agents
2. Launch ALL agents in background (run_in_background=true)
3. Continue with independent work OR
4. If nothing to do, use TaskOutput(block=true) to wait
5. Collect results and synthesize
```

#### Example: Multi-Agent Feature Implementation

```python
# BAD: Sequential blocking
Task(subagent_type="code-reviewer", ...)  # Wait 2 min
Task(subagent_type="test-automator", ...) # Wait 1 min
Task(subagent_type="documentation-engineer", ...) # Wait 1 min
# Total: 4 minutes

# GOOD: Parallel background
reviewer = Task(subagent_type="code-reviewer", run_in_background=True, ...)
tester = Task(subagent_type="test-automator", run_in_background=True, ...)
docs = Task(subagent_type="documentation-engineer", run_in_background=True, ...)

# Do other work here...

# Collect when done
review = TaskOutput(task_id=reviewer.agent_id, block=True)
tests = TaskOutput(task_id=tester.agent_id, block=True)
documentation = TaskOutput(task_id=docs.agent_id, block=True)
# Total: 2 minutes (parallel execution)
```

#### Benefits of Background Execution

- **2-5× faster** overall completion through parallelism
- **Better resource utilization** - all agents work simultaneously
- **Unblocked workflow** - continue other tasks while agents run
- **Scalable** - easily add more agents without time penalty

## Project Overview

TerminalAI is an AI-powered video processing suite for upscaling VHS/DVD footage with NVIDIA RTX acceleration, YouTube downloading, audio enhancement, and surround sound upmixing. Built with Python, FFmpeg, and Gradio for a modern web interface.

**Current Version:** 1.5.1

**Production Status:** Major release with RTX Video SDK integration (Super Resolution, Artifact Reduction, HDR conversion), AI audio enhancement (DeepFilterNet, AudioSR), enhanced face restoration (CodeFormer), notification system, and comprehensive documentation. All features tested and production-ready.

### v1.5.1 New Features (December 2025)
- **RTX Video SDK Integration**: NVIDIA's latest AI upscaling with artifact reduction and SDR-to-HDR conversion (RTX 20/30/40/50 series GPUs)
- **Maxine Deprecated**: Legacy Maxine support archived in favor of RTX Video SDK
- **RTX 50 Series Support**: Full compatibility with Ada Lovelace Next architecture (sm_120 compute capability)
- **Critical Bug Fixes**: QueueJob parameters, hardware detection hanging, PowerShell Unicode encoding, Gradio 6.0 theme migration
- **Cinema-Grade GUI Redesign**: Professional dark theme with Discord Blue accents, NVIDIA Green branding, WCAG 2.1 AA accessibility
- **Dependency Modernization**: pynvml → nvidia-ml-py, Python 3.13 compatibility, PyTorch nightly cu128 for RTX 50
- **Enhanced Installation**: Automated Windows installer with CUDA detection, comprehensive verification system

### Recent Major Updates

#### v1.5.1 - RTX Video SDK & Critical Fixes (December 19, 2025)
**Breaking Changes:**
- NVIDIA Maxine deprecated in favor of RTX Video SDK
- pynvml replaced with nvidia-ml-py (official NVIDIA package)

**New Features:**
- RTX Video SDK integration for superior AI upscaling (RTX 20+)
- RTX 50 series full support with PyTorch nightly builds
- Cinema-grade GUI redesign (see `docs/GUI_DESIGN_SPECIFICATION.md`)
- Automated Windows installer with CUDA detection

**Bug Fixes:**
- Fixed QueueJob missing parameters (face_model, audio_sr_enabled, audio_sr_model)
- Fixed hardware detection hanging indefinitely (added 10s timeout, prioritized nvidia-smi)
- Fixed PowerShell Unicode encoding errors in installer (Unicode → ASCII)
- Fixed Gradio 6.0 theme migration (theme moved to launch())
- Fixed first-run wizard slow GPU detection (prioritize nvidia-smi over PyTorch import)

**Documentation:**
- `docs/GUI_DESIGN_SPECIFICATION.md` - Complete design system (1,935 lines)
- `docs/installation/WINDOWS_INSTALLATION.md` - Comprehensive Windows setup guide
- `HARDWARE_DETECTION_FIX.md` - Technical fix documentation (280 lines)
- `POWERSHELL_UNICODE_FIX.md` - Encoding fix reference (128 lines)

**Performance:**
- Hardware detection: Infinite hang → 0.06s (nvidia-smi optimization)
- GPU verification: 2-3s → 0.1s (removed blocking imports)
- Installation time: ~15 minutes (automated, no manual steps)

#### v1.5.0 - AI Audio & Face Restoration (November 2025)
**New Features:**
- DeepFilterNet AI audio denoising for superior speech clarity
- AudioSR upsampling (AI-based audio super-resolution to 48kHz)
- CodeFormer face restoration (best-in-class quality with fidelity control)
- Webhook notifications (Discord, Slack, custom endpoints)
- Email notifications (SMTP-based alerts)
- Watch folder automation system

**Improvements:**
- Optimized audio processing order (Enhancement → AudioSR → Upmix → Normalize → Encode)
- Graceful fallbacks for all AI features when dependencies unavailable
- Dual-backend face restoration (GFPGAN + CodeFormer)

#### v1.4.5 - File System Monitoring (October 2025)
- Watch folder automation with multi-folder support
- Smart debouncing and lock file protection
- Per-folder preset configurations
- Automatic retry with configurable delays

## Key Commands

### Development Setup
```bash
# Install package in editable mode (recommended)
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install with audio processing capabilities (Demucs AI)
pip install -e ".[audio]"

# Install with all features
pip install -e ".[full]"

# Or just dependencies without package installation
pip install -r requirements.txt
```

**Windows-Specific Installation (RTX GPUs):**
```bash
# Automated full installation with PyTorch CUDA support
python install_windows.py --full

# Manual installation with CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -e ".[dev]"
pip install demucs deepfilternet
pip install opencv-python basicsr facexlib gfpgan

# Verify CUDA is working
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

**Installation Documentation:**
- `docs/installation/WINDOWS_INSTALLATION.md`: Comprehensive Windows installation guide with RTX GPU support
- `docs/installation/DEPENDENCY_ANALYSIS.md`: Technical deep dive into dependency tree and compatibility
- `docs/installation/INSTALLATION_SUMMARY.md`: Quick reference for installation options
- `docs/installation/QUICK_INSTALL.txt`: One-page copy-paste installation commands

### Running the Application
```bash
# Launch web GUI (primary interface)
python -m vhs_upscaler.gui
# OR
python vhs_upscaler/gui.py

# Command-line video processing
python -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4 --preset vhs

# Standalone YouTube downloader
python download_youtube.py "https://youtube.com/watch?v=VIDEO_ID"
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=vhs_upscaler

# Run specific test file
pytest tests/test_gui_helpers.py -v

# Run tests matching pattern
pytest tests/ -k "test_format" -v
```

### Code Quality
```bash
# Format code with Black
black vhs_upscaler/ tests/ --line-length 100

# Lint with Ruff
ruff check vhs_upscaler/ tests/

# Auto-fix linting issues
ruff check vhs_upscaler/ tests/ --fix
```

### Installation Verification
```bash
# Comprehensive installation verification
python scripts/installation/verify_installation.py

# Quick check of all components
python scripts/installation/verify_installation.py --quick

# Check specific component
python scripts/installation/verify_installation.py --check pytorch
python scripts/installation/verify_installation.py --check gfpgan

# Generate diagnostic report
python scripts/installation/verify_installation.py --report diagnostic.json

# Check feature availability
python -c "import sys; sys.path.insert(0, 'scripts/installation'); from verify_installation import get_available_features; print(get_available_features())"
```

**Verification System Components:**
- **`scripts/installation/verify_installation.py`**: Main verification script (1,100+ lines)
  - Checks 10 components: Python, FFmpeg, GPU, PyTorch, VapourSynth, GFPGAN, CodeFormer, DeepFilterNet, AudioSR, Demucs
  - Verifies 9 features: video processing, GPU acceleration, hardware encoding, AI upscaling, deinterlacing, face restoration, audio AI
  - Generates JSON diagnostic reports
  - Provides installation suggestions for missing components
  - Python API for integration: `check_component()`, `get_available_features()`, `verify_all_components()`

- **Documentation**:
  - `docs/installation/VERIFICATION_GUIDE.md`: User guide with examples and API reference
  - `docs/installation/INSTALLATION_TROUBLESHOOTING.md`: 850-line troubleshooting guide for all components
  - `docs/installation/VERIFICATION_QUICK_REFERENCE.md`: One-page quick reference

- **Tests**: `tests/test_installation_verification.py` (23 tests, 100% passing)

**Feature Detection API Example:**
```python
import sys
sys.path.insert(0, 'scripts/installation')
from verify_installation import get_available_features, check_component

# Get all features
features = get_available_features()
if features['gpu_acceleration']:
    print("GPU acceleration available")
if features['ai_audio_processing']:
    print("DeepFilterNet/AudioSR available")

# Check PyTorch with CUDA
pytorch = check_component('pytorch')
if pytorch.is_available and pytorch.details.get('cuda_available'):
    device = "cuda"
    print(f"PyTorch CUDA: {pytorch.details['cuda_version']}")
else:
    device = "cpu"
```

## Architecture Overview

### Core Processing Pipeline

The application follows a multi-stage pipeline architecture defined in `vhs_upscaler/vhs_upscale.py`:

1. **Download Stage** (optional): YouTube/URL video downloading via yt-dlp
2. **Preprocessing**: Deinterlacing, denoising, color correction
3. **AI Upscaling**: Using RTX Video SDK, Real-ESRGAN, or FFmpeg
4. **Encoding**: Hardware-accelerated (NVENC) or CPU encoding
5. **Audio Processing** (optional): Enhancement and surround upmixing

### Key Classes and Their Responsibilities

**`VideoUpscaler` (vhs_upscale.py)**
- Main processing pipeline coordinator
- Handles engine detection (RTX Video SDK, Real-ESRGAN, FFmpeg)
- Manages temporary files and FFmpeg filter chains
- Implements upscaling paths:
  - **RTX Video SDK**: NVIDIA RTX 20+ AI upscaling with artifact reduction and HDR (v1.5.1+, best quality)
  - Real-ESRGAN: Vulkan-based AI upscaling (AMD/Intel/NVIDIA)
  - FFmpeg: CPU-based traditional upscaling (universal fallback)
  - NVIDIA Maxine: Legacy support (deprecated in v1.5.1)

**`VideoQueue` (queue_manager.py)**
- Thread-safe job queue for batch processing
- Job lifecycle management (pending → processing → completed/failed)
- Status tracking with `JobStatus` enum
- Progress callback system for GUI updates

**`AudioProcessor` (audio_processor.py)**
- Audio enhancement pipeline (noise reduction, EQ, normalization)
- **DeepFilterNet AI denoising** - Superior speech clarity (v1.5.0)
- **AudioSR upsampling** - AI-based audio super-resolution to 48kHz (v1.5.0)
- Surround upmix algorithms (simple, surround, Pro Logic II, Demucs AI)
- Multiple output formats (AAC, AC3, EAC3, DTS, FLAC)
- Handles both FFmpeg-based and AI-based processing
- Graceful fallbacks when AI backends unavailable

**`UnifiedProgress` (vhs_upscale.py)**
- Real-time progress tracking across all pipeline stages
- Thread-safe progress updates with locking
- Visual progress bar rendering for CLI
- Stage timing and ETA calculation

**`AppState` (gui.py)**
- Global application state management for Gradio GUI
- Settings persistence (dark mode, output directory)
- Log buffer management (last 100 entries)
- Thumbnail caching for uploaded videos

**`FaceRestorer` (face_restoration.py)**
- Dual-backend face restoration (GFPGAN + CodeFormer)
- **CodeFormer integration** - Best-in-class quality with fidelity control (v1.5.0)
- Automatic model download and caching
- Graceful fallback between backends

**`NotificationManager` (notifications.py)**
- **Webhook notifications** - Discord, Slack, custom endpoints (v1.5.0)
- **Email notifications** - SMTP-based alerts (v1.5.0)
- Job completion and error notifications
- Retry logic with exponential backoff

**`WatchFolderMonitor` (scripts/watch_folder.py)**
- **File system monitoring** - Automatic video processing (v1.4.5)
- Multi-folder support with per-folder presets
- Smart debouncing and lock file protection
- Automatic retry with configurable delays

### Module Organization

```
vhs_upscaler/
├── vhs_upscale.py         # Main processing pipeline, VideoUpscaler class
├── queue_manager.py        # VideoQueue, QueueJob, JobStatus enum
├── audio_processor.py      # AudioProcessor, audio enhancement, DeepFilterNet, AudioSR
├── face_restoration.py     # FaceRestorer, GFPGAN + CodeFormer backends
├── notifications.py        # NotificationManager, webhooks, email alerts (v1.5.0)
├── gui.py                 # Gradio web interface, AppState
├── logger.py              # Centralized logging configuration
├── config.yaml            # Default configuration (presets, paths)
└── __init__.py            # Package initialization

scripts/
└── watch_folder.py        # Watch folder automation system (v1.4.5)

tests/
├── test_audio_processor_deepfilternet.py  # DeepFilterNet tests (v1.5.0)
├── test_audio_processor_audiosr.py        # AudioSR tests (v1.5.0)
└── test_watch_folder.py                   # Watch folder tests (v1.4.5)
```

### Configuration System

`config.yaml` defines:
- **Presets**: vhs, dvd, webcam, youtube, clean (different deinterlace/denoise settings)
- **Defaults**: Resolution, encoder, CRF quality, quality mode
- **Paths**: Maxine SDK, FFmpeg executable locations
- **Advanced**: Temp file handling, worker count, log level

Configuration is loaded via YAML and can be overridden by CLI arguments or GUI selections.

### Upscale Engine Selection Logic

The system auto-detects available engines in this priority order:
1. **RTX Video SDK** - NVIDIA RTX 20/30/40/50 series AI upscaling (v1.5.1+, best quality)
   - Checks for RTX Video SDK installation
   - Verifies GPU compute capability (sm_86+ for RTX 30+, sm_120 for RTX 50)
   - Features: Super Resolution, Artifact Reduction, SDR-to-HDR conversion
2. **Real-ESRGAN** - Vulkan-based AI upscaling (AMD/Intel/NVIDIA)
   - Searches PATH and common locations for `realesrgan-ncnn-vulkan[.exe]`
   - Universal AI upscaling with good quality
3. **FFmpeg** - Always available as fallback (CPU-based scaling)
   - Traditional bicubic/lanczos scaling
   - No AI enhancement but very fast
4. **NVIDIA Maxine (Deprecated)** - Legacy RTX support (v1.5.0 and earlier)
   - Checks `MAXINE_HOME` env var or config path for `VideoEffectsApp.exe`
   - Archived in favor of RTX Video SDK

When `--engine auto` is specified, the system selects the best available engine for the hardware.

**Engine Recommendation by GPU:**
- RTX 20/30/40/50: RTX Video SDK (best quality, fastest)
- AMD/Intel: Real-ESRGAN (good quality, GPU accelerated)
- CPU-only: FFmpeg (acceptable quality, slow)

### Audio Processing Architecture

Audio processing is modular and optional, controlled by `AudioConfig`:

**Enhancement Modes**: light, moderate, aggressive, voice, music, **deepfilternet** (v1.5.0)
- Built with FFmpeg audio filters (highpass, lowpass, compand, dynaudnorm)
- Voice mode optimized for VHS dialogue clarity
- Music mode preserves dynamics
- **DeepFilterNet**: AI-based denoising for superior speech clarity (v1.5.0)
  - Real-time processing on CPU, 5-10× faster on GPU
  - Automatic fallback to FFmpeg aggressive mode if unavailable

**AudioSR Upsampling** (v1.5.0):
- AI-based audio super-resolution to 48kHz
- Models: basic, speech (VHS/dialogue), music (concerts)
- GPU acceleration via CUDA
- Automatic skip if audio already ≥48kHz
- Graceful fallback to FFmpeg resampling

**Upmix Algorithms**:
- **simple**: Basic channel mapping (fast, ⭐⭐ quality)
- **surround**: FFmpeg surround filter (good, ⭐⭐⭐ quality)
- **prologic**: Dolby Pro Logic II decode (better, ⭐⭐⭐ quality)
- **demucs**: AI stem separation (best, ⭐⭐⭐⭐⭐ quality, requires PyTorch)

**Processing Order** (v1.5.0 optimized):
```
1. Audio Extraction
2. Enhancement (DeepFilterNet or FFmpeg)
3. AudioSR Upsampling (if needed)
4. Surround Upmix (optional)
5. Normalization
6. Encoding
```

All AI processing includes graceful fallbacks when dependencies are unavailable.

## Important Implementation Details

### Thread Safety
- `VideoQueue` uses `threading.Lock()` for all queue operations
- `UnifiedProgress` uses locks for progress updates
- GUI callbacks run on main Gradio thread

### Temporary File Management
- All intermediate files use `tempfile.mkdtemp()` with unique prefixes
- Cleanup in `finally` blocks ensures temp files are removed
- Config option `keep_temp` can preserve files for debugging

### FFmpeg Filter Chains
Filters are built dynamically based on preset and options:
```
scale → deinterlace → denoise → color correction → encode
```

Example filter chain for VHS preset:
```
yadif=1:0:0,hqdn3d=3:2:3:2,eq=contrast=1.1:brightness=0.05
```

### HDR Conversion
HDR output (hdr10, hlg) is handled via FFmpeg filters:
- Color space conversion (bt709 → bt2020)
- Transfer characteristics (sRGB → PQ or HLG)
- Metadata injection for HDR10
- Configurable brightness, saturation, contrast

### Error Handling
- All subprocess calls wrapped in try-except with logging
- Graceful degradation (e.g., RTX Video SDK unavailable → use Real-ESRGAN → use FFmpeg)
- Queue jobs marked FAILED with error messages stored
- GUI displays user-friendly error messages

## Testing Architecture

**Test Structure** (200+ tests):
- `test_gui_helpers.py` - GUI utility functions (formatting, status emojis)
- `test_gui_integration.py` - GUI component integration tests
- `test_queue_manager.py` - Queue operations, threading, callbacks (includes QueueJob parameter fixes)
- `test_audio_processor_deepfilternet.py` - DeepFilterNet AI denoising (v1.5.0, 14 tests)
- `test_audio_processor_audiosr.py` - AudioSR upsampling (v1.5.0, 20+ tests)
- `test_watch_folder.py` - Watch folder automation (v1.4.5, 20+ tests)
- `test_rtx_video_sdk.py` - RTX Video SDK integration (v1.5.1, 25+ tests)
- `test_hardware_detection.py` - GPU detection and capabilities (v1.5.1, 15+ tests)
- `test_first_run_wizard.py` - First-run setup wizard (v1.5.1, 10+ tests)
- `test_gpu_scenarios.py` - Multi-GPU vendor testing (NVIDIA, AMD, Intel, CPU-only)

**Testing Infrastructure:**
- `verify_installation.py` - Comprehensive installation verification (1,100+ lines)
  - Tests 10 components (Python, FFmpeg, GPU, PyTorch, etc.)
  - Validates 9 features (video processing, GPU acceleration, AI features)
  - Generates JSON diagnostic reports
  - Provides installation suggestions

Tests use:
- `pytest` fixtures for setup/teardown
- `unittest.mock` for patching subprocess calls and AI backends
- Temporary directories for file operations
- Feature detection mocking for optional dependencies
- Graceful fallback validation
- Timeout testing for hanging prevention (hardware detection, GPU queries)

## Preset System

Presets in `config.yaml` define processing parameters:

| Preset | Source | Deinterlace | Denoise | Use Case |
|--------|--------|-------------|---------|----------|
| vhs | 480i VHS | Yes | Strong (3,2,3,2) | Old home videos |
| dvd | 480p/576p | Yes | Moderate (2,1,2,1) | DVD rips |
| webcam | Low-quality | No | Strong (4,3,4,3) | Webcam footage |
| youtube | Downloaded | No | Light | YouTube videos |
| clean | High-quality | No | None | Already clean sources |

The preset system allows consistent processing profiles while still supporting per-job customization.

## Common Development Patterns

### Adding a New Upscale Engine
1. Add detection logic in `VideoUpscaler._check_dependencies()`
2. Implement upscaling method (e.g., `_upscale_with_newengine()`)
3. Add engine name to `available_engines` list
4. Update `_upscale()` method to route to new engine
5. Add configuration options in `UpsacaleConfig` dataclass
6. Update GUI dropdowns in `gui.py`

### Adding a New Audio Effect
1. Define new enum value in `AudioEnhanceMode` or `UpmixMode`
2. Add filter chain in `AudioProcessor._build_enhancement_filters()`
3. Add configuration in `AudioConfig` dataclass
4. Update GUI options in `gui.py` (conditional display logic)
5. Add tests in `tests/test_audio_processor.py` (if file exists)

### Adding a New Preset
1. Add preset definition in `config.yaml` under `presets:`
2. Define deinterlace/denoise/quality_mode settings
3. Add to GUI dropdown in `gui.py`
4. Document in README.md preset table

## External Dependencies

**Required:**
- FFmpeg (all video/audio processing)
- Python 3.10+ (3.11 recommended, 3.12/3.13 supported with compatibility patches)

**GPU Acceleration (Recommended):**
- **NVIDIA Driver 535+** (for NVENC hardware encoding and RTX features)
- **NVIDIA RTX Video SDK** (v1.5.1+, best AI upscaling for RTX 20/30/40/50 GPUs)
  - Supports sm_86+ compute capability (RTX 30+)
  - RTX 50 series with sm_120 compute capability
  - Features: Super Resolution, Artifact Reduction, SDR-to-HDR
- **Real-ESRGAN ncnn-vulkan** (AI upscaling for AMD/Intel/NVIDIA GPUs)
- **PyTorch with CUDA 12.1+** (GPU-accelerated AI processing)
  - RTX 50 series: PyTorch nightly with cu128

**Legacy (Deprecated):**
- **NVIDIA Maxine SDK** (v1.5.0 and earlier, replaced by RTX Video SDK)

**Optional AI Features (v1.5.0+):**
- **DeepFilterNet** (AI audio denoising, superior speech clarity)
- **AudioSR** (AI audio upsampling to 48kHz with speech/music models)
- **CodeFormer** (best-in-class face restoration with fidelity control)
- **GFPGAN** (face restoration, good quality, fallback for CodeFormer)
- **Demucs** (AI audio stem separation for best surround upmix)

**Optional Automation & Notifications (v1.4.5+):**
- **watchdog** (watch folder file system monitoring)
- **requests** (webhook notifications for Discord, Slack, custom endpoints)
- **smtplib** (email notifications, included with Python)

**Development & Testing:**
- **pytest, pytest-cov** (testing framework and coverage)
- **black** (code formatting)
- **ruff** (linting)
- **nvidia-ml-py** (GPU monitoring, replaces deprecated pynvml)

**Dependency Management:**
The application gracefully handles missing optional dependencies with:
- Feature detection at startup
- Automatic fallbacks (e.g., CodeFormer → GFPGAN → disabled)
- Clear error messages about missing features
- Installation verification system (`verify_installation.py`)

**Python Version Compatibility:**
- **Python 3.10**: Fully compatible
- **Python 3.11**: Recommended (most stable, best performance)
- **Python 3.12**: Fully compatible
- **Python 3.13**: Compatible with patches (basicsr torchvision compatibility, async warnings)

**Windows-Specific:**
- **Visual C++ Redistributable** (for PyTorch DLL dependencies)
- **PowerShell 5.1+** (for automated installer)
- **winget** (optional, for automated FFmpeg/Python installation)

## Development Guidelines

### Code Style
- Line length: 100 characters (Black/Ruff config)
- Target: Python 3.10+ (use modern type hints)
- Docstrings: Google style for classes/functions
- Use dataclasses for configuration objects
- Use Enums for fixed option sets

### Logging
- Use module-level logger: `logger = logging.getLogger(__name__)`
- INFO for user-visible operations
- DEBUG for technical details (filter chains, subprocess commands)
- WARNING for recoverable issues
- ERROR for failures

### FFmpeg Subprocess Calls
Always use this pattern:
```python
cmd = ["ffmpeg", "-i", input_file, ...]
result = subprocess.run(cmd, capture_output=True, text=True, check=True)
```

For progress parsing, use `subprocess.Popen` with stdout streaming.

### GUI Updates
Gradio GUI uses reactive state updates:
- Return updated components from callback functions
- Use `gr.update()` for conditional visibility
- Thread-safe queue polling with `queue.get_status()`

**Gradio 6.0 Theme Migration Pattern:**
```python
# Create custom theme
custom_theme = gr.themes.Soft(...).set(...)

# Apply custom CSS
custom_css = """..."""

# IMPORTANT: Theme goes to launch(), NOT Blocks()
with gr.Blocks(css=custom_css) as app:  # No theme parameter here
    # ... build UI ...
    pass

# Theme applied at launch
app.launch(
    theme=custom_theme,  # Theme parameter moved here in Gradio 6.0
    server_name="0.0.0.0",
    server_port=7860
)
```

**Hardware Detection with Timeout:**
```python
# Prevent hanging with timeout wrapper
def detect_hardware_once(cls):
    detection_result = {"hardware": None, "config": None, "error": None}

    def run_detection():
        try:
            detection_result["hardware"] = detect_hardware()
            detection_result["config"] = get_optimal_config(detection_result["hardware"])
        except Exception as e:
            detection_result["error"] = e

    detection_thread = threading.Thread(target=run_detection, daemon=True)
    detection_thread.start()
    detection_thread.join(timeout=10.0)  # 10-second timeout prevents infinite hang

    if detection_thread.is_alive():
        logger.error("Hardware detection timed out")
        # Use CPU fallback
```

**GPU Detection Optimization:**
```python
# ALWAYS try nvidia-smi first (0.06s), PyTorch import is slow (2-3s)
def detect_gpu() -> Dict[str, any]:
    # Fast path: nvidia-smi (most reliable and fastest)
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
        import torch  # Can take 2-3 seconds
        if torch.cuda.is_available():
            return get_pytorch_gpu_info()
    except ImportError:
        pass

    return {"has_gpu": False}
```

---

## GUI Design System (v1.5.1)

**Complete redesign specification:** `docs/GUI_DESIGN_SPECIFICATION.md` (1,935 lines)

### Design Philosophy
1. **Dark-Mode First**: Cinema-grade color palette for long processing sessions
2. **Professional Aesthetics**: Inspired by DaVinci Resolve, Premiere Pro
3. **GPU-Accelerated Feel**: Visual elements that convey speed and performance
4. **WCAG 2.1 AA Compliant**: All contrast ratios meet accessibility standards

### Color Palette
```css
/* Primary Colors */
--bg-primary: #0a0e1a;          /* Deep space black */
--bg-secondary: #141b2d;        /* Elevated panels */
--accent-primary: #5865f2;      /* Discord Blue (primary CTA) */
--gpu-nvidia: #76b900;          /* NVIDIA Green (GPU badges) */
--status-success: #3ba55c;      /* Completed jobs */
--status-processing: #9b59b6;   /* Currently processing */
--status-error: #ed4245;        /* Failed jobs */
--video-upscale: #8b5cf6;       /* Upscaling operations (purple) */
--audio-process: #06b6d4;       /* Audio operations (cyan) */
```

### Typography
- **Primary Font**: Inter (body text, UI elements)
- **Monospace**: JetBrains Mono (logs, technical info)
- **Display**: Poppins (headings only)

### Key Components
- **Gradient Header**: `background: linear-gradient(135deg, #5865f2 0%, #7289da 100%)`
- **Job Cards**: Left border indicates status (green=completed, purple=processing, red=failed)
- **Progress Bars**: Animated gradient with shimmer effect during active processing
- **GPU Badges**: Color-coded by vendor (NVIDIA green, AMD red, Intel blue)
- **Hardware Info Cards**: Left border glow effect when GPU detected

### Accessibility
- Primary text contrast: 13.2:1 (AAA)
- Button primary contrast: 8.1:1 (AAA)
- All status colors: 4.7:1+ (AA minimum)
- Focus indicators: 3px ring with 10% opacity background

### Performance Optimizations
- CSS variables for instant theme switching
- Hardware-accelerated transforms (`translateY`, `scale`)
- Minimal reflows (use `transform` over `top/left`)
- Efficient transitions with `cubic-bezier(0.4, 0, 0.2, 1)`

### Implementation Priority
1. **Phase 1**: Core colors & typography (immediate impact)
2. **Phase 2**: Component styling (job cards, progress bars, stats)
3. **Phase 3**: Advanced features (GPU badges, toast notifications)
4. **Phase 4**: Accessibility verification & refinement

---

## 🎬 Intelligent Video Analysis System

**Status**: Planned integration (see plan at `C:\Users\justi\.claude\plans\zippy-frolicking-chipmunk.md`)

### Overview

The intelligent video analysis system automatically detects video characteristics and recommends optimal processing settings, eliminating manual guesswork and improving restoration quality.

### Architecture: Unified Multi-Backend Wrapper

```
┌─────────────────────────────────────────┐
│      Unified Analyzer Wrapper          │
│   (vhs_upscaler/analysis/analyzer_     │
│            wrapper.py)                  │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴─────────┐
       │ Auto-Detection  │
       └───────┬─────────┘
               │
    ┌──────────┴──────────┬────────────┐
    │                     │            │
┌───▼────┐      ┌────────▼────┐   ┌───▼─────┐
│Python+ │      │    Bash     │   │FFprobe  │
│OpenCV  │  →   │  + FFmpeg   │ → │  Only   │
│(best)  │      │  (portable) │   │(basic)  │
└────────┘      └─────────────┘   └─────────┘
```

**Fallback Chain**: Python+OpenCV → Bash → FFprobe-only

### Core Components

#### 1. Data Models (`vhs_upscaler/analysis/models.py`)

**Key Enums**:
- `ScanType`: PROGRESSIVE, INTERLACED_TFF, INTERLACED_BFF, TELECINE
- `ContentType`: LIVE_ACTION, ANIMATION, MIXED, TALKING_HEAD, SPORTS
- `NoiseLevel`: LOW, MEDIUM, HIGH, SEVERE
- `SourceFormat`: VHS, SVHS, DVD, BROADCAST, DIGITAL

**VideoAnalysis Dataclass**:
```python
@dataclass
class VideoAnalysis:
    # File metadata
    filepath: str
    duration_seconds: float
    filesize_mb: float

    # Technical properties
    width: int
    height: int
    framerate: float
    codec: str
    scan_type: ScanType

    # Detected characteristics
    content_type: ContentType
    source_format: SourceFormat
    noise_level: NoiseLevel
    estimated_quality_score: float

    # VHS-specific artifacts
    has_tracking_errors: bool
    has_color_bleeding: bool
    has_head_switching_noise: bool
    has_dropout_lines: bool

    # Recommendations
    recommended_tools: List[str]
    recommended_settings: Dict[str, Any]
    processing_notes: List[str]
```

#### 2. Analyzer Wrapper (`vhs_upscaler/analysis/analyzer_wrapper.py`)

**Responsibilities**:
- Auto-detect available analysis backends
- Provide unified interface regardless of backend
- Graceful fallback when dependencies unavailable
- JSON import/export for batch processing

**Usage**:
```python
from vhs_upscaler.analysis import AnalyzerWrapper

wrapper = AnalyzerWrapper()  # Auto-detects backend
analysis = wrapper.analyze("old_vhs_tape.mp4")

# Analysis provides:
print(analysis.scan_type)       # INTERLACED_TFF
print(analysis.noise_level)     # HIGH
print(analysis.source_format)   # VHS
print(analysis.recommended_settings)  # {'preset': 'vhs_heavy', ...}
```

#### 3. Python Analyzer (`vhs_upscaler/analysis/video_analyzer.py`)

**Analysis Methods**:
- **Interlace Detection**: FFmpeg idet filter + combing artifact detection
- **Noise Estimation**: Laplacian variance on sample frames
- **Content Type**: Edge density, motion analysis, face detection
- **Source Format**: Resolution patterns, bitrate heuristics
- **VHS Artifacts**: Head switching noise, dropout detection

**OpenCV Optional**: Gracefully degrades if OpenCV unavailable

#### 4. Bash Analyzer (`scripts/video_analyzer.sh`)

Portable shell script for systems without Python dependencies:
- Uses ffprobe JSON output for metadata
- FFmpeg idet for interlace detection
- Signal-to-noise ratio for noise estimation
- Outputs JSON matching VideoAnalysis schema

#### 5. Preset Library (`vhs_upscaler/presets.py`)

Maps analysis results to optimal processing settings:

```python
PRESETS = {
    "vhs_standard": {
        "deinterlace": "yadif=1",
        "denoise": "hqdn3d=4:3:6:4.5",
        "sharpen": "cas=0.4",
    },
    "vhs_clean": {
        "deinterlace": "yadif=1",
        "denoise": "hqdn3d=2:1:2:3",
        "sharpen": "cas=0.3",
    },
    "vhs_heavy": {
        "deinterlace": "yadif=1",
        "denoise": "hqdn3d=8:6:12:9",
        "sharpen": "cas=0.5",
        "crop_bottom": 8,  # Remove head switching noise
    },
    "animation": {
        "deinterlace": None,
        "denoise": "hqdn3d=1:1:2:2",
        "sharpen": "cas=0.2",
        "upscale_model": "realesrgan-x4plus-anime",
    },
}

def get_preset_from_analysis(analysis: VideoAnalysis) -> str:
    if analysis.source_format == SourceFormat.VHS:
        if analysis.noise_level == NoiseLevel.SEVERE:
            return "vhs_heavy"
        elif analysis.estimated_quality_score > 60:
            return "vhs_clean"
        else:
            return "vhs_standard"
    elif analysis.content_type == ContentType.ANIMATION:
        return "animation"
    # ... additional logic
```

### CLI Integration

**New Arguments**:
```bash
--analyze-only          # Run analysis and print report without processing
--auto-detect           # Auto-detect optimal settings and process
--analysis-config FILE  # Load pre-analyzed config JSON
--save-analysis FILE    # Export analysis results to JSON
--force-backend TYPE    # Force specific backend (python|bash|basic)
```

**Example Workflows**:

1. **Analyze First** (recommended):
```bash
# Step 1: Analyze and review settings
python -m vhs_upscaler.vhs_upscale \
  -i old_vhs_tape.mp4 \
  --analyze-only \
  --save-analysis vhs_config.json

# Step 2: Review analysis report, then process
python -m vhs_upscaler.vhs_upscale \
  -i old_vhs_tape.mp4 \
  -o restored.mp4 \
  --analysis-config vhs_config.json
```

2. **Auto-Detect and Process** (one command):
```bash
python -m vhs_upscaler.vhs_upscale \
  -i old_vhs_tape.mp4 \
  -o restored.mp4 \
  --auto-detect

# System will:
# 1. Analyze video
# 2. Display recommended settings
# 3. Ask for confirmation
# 4. Process with optimal settings
```

3. **Batch Processing** (same analysis for multiple videos):
```bash
# Analyze one representative video
python -m vhs_upscaler.vhs_upscale \
  -i family_1990/tape1.mp4 \
  --analyze-only \
  --save-analysis family_1990_config.json

# Apply to all similar tapes
for tape in family_1990/*.mp4; do
  python -m vhs_upscaler.vhs_upscale \
    -i "$tape" \
    -o "restored/$(basename $tape)" \
    --analysis-config family_1990_config.json
done
```

### Analysis Methodology

#### Scan Type Detection
**Python+OpenCV**:
- FFmpeg idet filter on sample frames
- Combing artifact detection via edge analysis
- Confidence scoring
- Field order determination (TFF/BFF)

**Bash**:
- FFmpeg idet filter execution
- Frame count analysis (progressive vs interlaced)
- Dominant scan type threshold (>80%)

#### Noise Level Estimation
**Python+OpenCV**:
- Sample 10 evenly distributed frames
- Laplacian variance (blur metric)
- Temporal noise (frame-to-frame differences)
- Classification: Low (<20), Medium (20-40), High (40-80), Severe (>80)

**Bash**:
- Signal-to-noise ratio from FFmpeg stats
- Bitrate heuristics (low bitrate → noisy)
- File size vs resolution analysis

#### Content Type Classification
**Python+OpenCV**:
- Edge density (animation = sharp edges, live action = gradients)
- Motion estimation between frames
- Face detection (talking head identification)
- Scene change frequency

**Bash**:
- Codec hints (animation codec patterns)
- Bitrate patterns (animation compresses better)
- Filename/metadata parsing

#### Source Format Detection
**Heuristics**:
- **VHS**: 720×480/576, interlaced, 29.97/25fps, low bitrate, high noise
- **DVD**: 720×480/576, can be interlaced, medium bitrate
- **Digital**: 1080p+, progressive, high bitrate, low noise
- **Broadcast**: 1080i, interlaced, specific framerates

#### VHS Artifact Detection
- **Head Switching Noise**: Horizontal lines at bottom (edge analysis)
- **Color Bleeding**: Chroma channel bleeding (color variance)
- **Tracking Errors**: Frame jitter, horizontal displacement
- **Dropout Lines**: Missing scan lines (row analysis)

### Processing Order (Critical)

Analysis recommends settings following this proven order:

```
1. DEINTERLACE (yadif/qtgmc)     ← ALWAYS FIRST for VHS
   ↓
2. DENOISE (hqdn3d)               ← Remove noise before upscaling
   ↓
3. COLOR CORRECT (optional)       ← Fix VHS color issues
   ↓
4. UPSCALE (Maxine/Real-ESRGAN)   ← Do ONCE at appropriate scale
   ↓
5. FACE RESTORE (optional)        ← GFPGAN/CodeFormer enhancement
   ↓
6. SHARPEN (CAS)                  ← Enhance detail post-upscale
   ↓
7. ENCODE (H.264/H.265)           ← Final compression
```

**Why This Order?**
- Deinterlace first prevents AI from amplifying combing artifacts
- Denoise before upscale prevents noise amplification
- Sharpen after upscale prevents harsh artifacts
- Encode last avoids multiple compression passes

### Backend Compatibility

| Backend | Platform | Requirements | Speed | Accuracy |
|---------|----------|--------------|-------|----------|
| Python+OpenCV | All | OpenCV, NumPy | 20-30s | ★★★★★ |
| Python Basic | All | Python 3.8+ | 15-25s | ★★★★☆ |
| Bash | Linux/Mac | FFmpeg, jq | 10-20s | ★★★☆☆ |
| FFprobe Only | All | FFmpeg | 5-10s | ★★☆☆☆ |

### JSON Analysis Schema

Exported configs use this structure:

```json
{
  "filepath": "old_vhs_tape.mp4",
  "scan_type": "interlaced_tff",
  "content_type": "live_action",
  "source_format": "vhs",
  "noise_level": "high",
  "estimated_quality_score": 42.3,
  "has_head_switching_noise": true,
  "has_color_bleeding": true,
  "recommended_settings": {
    "preset": "vhs_heavy",
    "deinterlace": "yadif=1",
    "denoise": "hqdn3d=8:6:12:9",
    "sharpen": "cas=0.5",
    "crop_bottom": 8,
    "upscale_model": "realesrgan-x4plus"
  },
  "processing_notes": [
    "Head switching noise detected - crop bottom 8px recommended",
    "High noise level - aggressive denoise recommended"
  ],
  "analyzer_backend": "python_opencv"
}
```

### Implementation Status

**Planned Components** (See full plan: `C:\Users\justi\.claude\plans\zippy-frolicking-chipmunk.md`):

- [ ] `vhs_upscaler/analysis/models.py` (~150 lines)
- [ ] `vhs_upscaler/analysis/analyzer_wrapper.py` (~300 lines)
- [ ] `vhs_upscaler/analysis/video_analyzer.py` (user-provided, ~400 lines)
- [ ] `scripts/video_analyzer.sh` (user-provided, bash)
- [ ] `vhs_upscaler/presets.py` (~250 lines)
- [ ] CLI integration in `vhs_upscale.py` (+150 lines)
- [ ] Documentation: `docs/ANALYSIS.md`, README updates

**Total**: ~1,300 lines of new code

### Benefits

1. **Better Results**: Eliminates guesswork, applies optimal settings per video
2. **Time Savings**: No trial-and-error needed
3. **User-Friendly**: Beginners get expert-level results automatically
4. **Transparency**: Reports explain why settings were chosen
5. **Flexibility**: Advanced users can override any setting
6. **Reproducibility**: Export/import configs for batch processing

### Development Guidelines for Analysis Features

#### Adding New Detection Algorithms
1. Update `VideoAnalysis` dataclass with new fields
2. Implement detection in `video_analyzer.py` (Python backend)
3. Add equivalent bash detection in `video_analyzer.sh`
4. Update `_parse_bash_output()` in wrapper for JSON mapping
5. Add tests for new detection logic

#### Adding New Presets
1. Define preset in `presets.py` PRESETS dictionary
2. Update `get_preset_from_analysis()` selection logic
3. Add to GUI dropdown if applicable
4. Document in `docs/ANALYSIS.md`

#### Testing Analysis Features
```bash
# Unit tests for analysis components
pytest tests/test_analysis_models.py -v
pytest tests/test_analyzer_wrapper.py -v

# Integration tests
pytest tests/test_analysis_integration.py -v

# Test with real videos
python -m vhs_upscaler.vhs_upscale \
  -i test_videos/*.mp4 \
  --analyze-only \
  --save-analysis test_results/
```

### Future Enhancements

1. **Scene-Aware Processing**: Different settings per scene type within same video
2. **ML Quality Prediction**: Predict upscale quality before processing
3. **Audio Analysis**: Detect audio issues (hiss, hum, distortion)
4. **GUI Integration**: Visual analysis report with preview images
5. **Learning System**: Improve recommendations based on user feedback

### References

- **Plan Document**: `C:\Users\justi\.claude\plans\zippy-frolicking-chipmunk.md`
- **Best Practices**: `BEST_PRACTICES.md` (VHS processing guidelines)
- **Real-ESRGAN**: https://github.com/xinntao/Real-ESRGAN
- **FFmpeg Filters**: https://ffmpeg.org/ffmpeg-filters.html

---

## Critical Bug Fixes & Known Issues

### Recently Fixed (v1.5.1, December 2025)

#### 1. Hardware Detection Hanging Indefinitely
**Problem:** GUI stuck on "Detecting hardware capabilities..." forever, application unusable.

**Root Causes:**
- Attempted to import RTX SDK module during detection (blocking)
- No timeout mechanism in GUI detection wrapper
- First-run wizard imported PyTorch before trying nvidia-smi (2-3s delay)

**Solution:**
- Added 10-second timeout wrapper in `gui.py` with graceful fallback
- Removed blocking RTX SDK import from `hardware_detection.py`
- Prioritized nvidia-smi (0.06s) over PyTorch import (2-3s) in `first_run_wizard.py`
- Enhanced error handling with comprehensive logging

**Performance:** Detection time reduced from infinite hang to 0.06 seconds (150× improvement).

**Files:** `vhs_upscaler/gui.py`, `vhs_upscaler/hardware_detection.py`, `vhs_upscaler/first_run_wizard.py`

**Documentation:** `HARDWARE_DETECTION_FIX.md` (280 lines)

#### 2. QueueJob Missing Parameters
**Problem:** Queue manager crashes when creating jobs with face restoration or AudioSR enabled.

**Root Cause:** `QueueJob` dataclass missing `face_model`, `audio_sr_enabled`, `audio_sr_model` parameters added in v1.5.0.

**Solution:**
- Added missing parameters to `QueueJob` dataclass in `queue_manager.py`
- Updated job creation in `gui.py` to pass new parameters
- Added default values for backward compatibility

**Files:** `vhs_upscaler/queue_manager.py`, `vhs_upscaler/gui.py`

#### 3. PowerShell Unicode Encoding Errors
**Problem:** Installation script fails to parse with "Unexpected token" errors on Unicode symbols (✓, ✗, ⚠, ℹ, ═).

**Root Cause:** PowerShell 5.1+ doesn't reliably handle Unicode symbols in all terminal environments.

**Solution:**
- Replaced all Unicode symbols with ASCII equivalents:
  - ✓ → `[OK]`
  - ✗ → `[FAIL]`
  - ⚠ → `[WARN]`
  - ℹ → `[INFO]`
  - ═ → `=`
- Fixed variable interpolation (added braces for proper parsing)

**Files:** `scripts/installation/install_windows.ps1`

**Documentation:** `POWERSHELL_UNICODE_FIX.md` (128 lines)

#### 4. Gradio 6.0 Theme Migration
**Problem:** Custom theme not applied, GUI reverts to default Gradio theme.

**Root Cause:** Gradio 6.0 changed where theme parameter is passed (from `gr.Blocks()` to `app.launch()`).

**Solution:**
```python
# OLD (Gradio < 6.0)
with gr.Blocks(theme=custom_theme, css=custom_css) as app:
    pass

# NEW (Gradio 6.0+)
with gr.Blocks(css=custom_css) as app:  # No theme here
    pass
app.launch(theme=custom_theme)  # Theme moved to launch()
```

**Files:** `vhs_upscaler/gui.py`

#### 5. pynvml Deprecated Package
**Problem:** Warnings about deprecated `pynvml` package, potential compatibility issues with future NVIDIA drivers.

**Root Cause:** `pynvml` is community-maintained fork, NVIDIA now provides official `nvidia-ml-py` package.

**Solution:**
- Replaced all `pynvml` imports with `nvidia-ml-py`
- Updated dependency in `pyproject.toml` and `requirements.txt`
- Updated code to use official NVIDIA package

**Files:** `vhs_upscaler/hardware_detection.py`, `vhs_upscaler/first_run_wizard.py`, `pyproject.toml`, `requirements.txt`

### Known Issues

#### 1. RTX 50 Series PyTorch Compatibility
**Issue:** RTX 50 series requires PyTorch nightly builds with cu128 (CUDA 12.8).

**Workaround:**
```bash
pip install torch torchvision torchaudio --pre --index-url https://download.pytorch.org/whl/nightly/cu128
```

**Status:** Stable PyTorch release with cu128 expected Q1 2025.

#### 2. basicsr torchvision >= 0.17 Compatibility
**Issue:** `basicsr` (used by GFPGAN) has compatibility issues with torchvision 0.17+.

**Workaround:** Automated patch applied during installation:
- `scripts/installation/patch_basicsr.py` (replaces deprecated `torchvision.transforms.functional_tensor` with `torchvision.transforms.functional`)

**Status:** Patch applied automatically by `pip install -e .`

#### 3. AudioSR Windows Installation Issues
**Issue:** AudioSR may fail to install on some Windows systems due to C++ compilation requirements.

**Workaround:**
- AudioSR is optional and can be skipped
- Other audio features (DeepFilterNet, Demucs, FFmpeg enhancement) still work
- Uninstall if problematic: `pip uninstall audiosr`

**Status:** Non-critical, graceful fallback implemented.

#### 4. DeepFilterNet Rust Compiler Requirement
**Issue:** DeepFilterNet may require Rust compiler on some systems.

**Workaround:**
1. Install Rust from https://www.rust-lang.org/tools/install
2. Restart terminal
3. Reinstall: `pip install deepfilternet`

**Status:** Rare issue, most Windows systems have compatible binary wheels.

### Debugging Tips

#### Enable Debug Logging
```python
# In gui.py or vhs_upscale.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Hardware Detection Diagnosis
```bash
# Run standalone hardware detection
python -c "from vhs_upscaler.hardware_detection import detect_hardware; print(detect_hardware())"

# Check with timeout
python -c "import threading; from vhs_upscaler.hardware_detection import detect_hardware; r={'hw':None}; t=threading.Thread(target=lambda: r.update(hw=detect_hardware())); t.start(); t.join(timeout=10); print('Timeout' if t.is_alive() else r['hw'])"
```

#### GPU Detection Verification
```bash
# Fast path (nvidia-smi)
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

# PyTorch CUDA check
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

#### Installation Verification
```bash
# Comprehensive verification
python scripts/installation/verify_installation.py

# Quick check
python scripts/installation/verify_installation.py --quick

# Component-specific
python scripts/installation/verify_installation.py --check pytorch
python scripts/installation/verify_installation.py --check gpu
```

#### Generate Diagnostic Report
```bash
# Create JSON diagnostic report
python scripts/installation/verify_installation.py --report diagnostic.json

# View available features
python -c "import sys; sys.path.insert(0, 'scripts/installation'); from verify_installation import get_available_features; import json; print(json.dumps(get_available_features(), indent=2))"
```

### Testing Infrastructure

#### Hardware Detection Tests
```bash
# Test direct hardware detection (0.06s expected)
python test_hardware_detection_fix.py

# Test GUI wrapper with timeout (should complete in < 10s)
python test_gui_hardware_detection.py

# Test multi-GPU scenarios
pytest tests/test_gpu_scenarios.py -v
```

#### Integration Tests
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=vhs_upscaler --cov-report=html

# Specific test file
pytest tests/test_queue_manager.py -v
pytest tests/test_rtx_video_sdk.py -v
pytest tests/test_hardware_detection.py -v
```

### Performance Benchmarks

| Component | Before Fix | After Fix | Improvement |
|-----------|-----------|-----------|-------------|
| Hardware detection | Infinite hang | 0.06s | 100% reliability |
| nvidia-smi check | N/A | 0.06s | New fast path |
| PyTorch import | 2-3s (blocking) | Skipped | Only when needed |
| GUI startup | Hung indefinitely | < 1s | 10s timeout max |
| Installation time | ~30 min (manual) | ~15 min (automated) | 50% reduction |

### Documentation References

**Installation & Setup:**
- `docs/installation/WINDOWS_INSTALLATION.md` - Comprehensive Windows guide (485 lines)
- `docs/installation/VERIFICATION_GUIDE.md` - Verification system guide
- `docs/installation/INSTALLATION_TROUBLESHOOTING.md` - Troubleshooting guide (850 lines)

**Technical Fixes:**
- `HARDWARE_DETECTION_FIX.md` - Hardware detection hanging fix (280 lines)
- `POWERSHELL_UNICODE_FIX.md` - PowerShell encoding fix (128 lines)
- `docs/GUI_DESIGN_SPECIFICATION.md` - GUI redesign specification (1,935 lines)

**Testing & Verification:**
- `scripts/installation/verify_installation.py` - Comprehensive verification (1,100+ lines)
- `tests/test_hardware_detection.py` - Hardware detection tests
- `tests/test_gpu_scenarios.py` - Multi-GPU vendor tests

**Development:**
- `CLAUDE.md` - This file (maintainer guide)
- `README.md` - User-facing documentation
- `INSTALLATION.md` - Detailed installation instructions
