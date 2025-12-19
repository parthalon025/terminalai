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

### v1.5.1 New Features
- **RTX Video SDK Integration**: NVIDIA's latest AI upscaling with artifact reduction and SDR-to-HDR conversion (RTX 20+ GPUs)
- **Maxine Deprecated**: Legacy Maxine support archived in favor of RTX Video SDK

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
- `docs/WINDOWS_INSTALLATION.md`: Comprehensive Windows installation guide with RTX GPU support
- `docs/DEPENDENCY_ANALYSIS.md`: Technical deep dive into dependency tree and compatibility
- `INSTALLATION_SUMMARY.md`: Quick reference for installation options
- `QUICK_INSTALL.txt`: One-page copy-paste installation commands

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
python verify_installation.py

# Quick check of all components
python verify_installation.py --quick

# Check specific component
python verify_installation.py --check pytorch
python verify_installation.py --check gfpgan

# Generate diagnostic report
python verify_installation.py --report diagnostic.json

# Check feature availability
python -c "from verify_installation import get_available_features; print(get_available_features())"
```

**Verification System Components:**
- **`verify_installation.py`**: Main verification script (1,100+ lines)
  - Checks 10 components: Python, FFmpeg, GPU, PyTorch, VapourSynth, GFPGAN, CodeFormer, DeepFilterNet, AudioSR, Demucs
  - Verifies 9 features: video processing, GPU acceleration, hardware encoding, AI upscaling, deinterlacing, face restoration, audio AI
  - Generates JSON diagnostic reports
  - Provides installation suggestions for missing components
  - Python API for integration: `check_component()`, `get_available_features()`, `verify_all_components()`

- **Documentation**:
  - `docs/VERIFICATION_GUIDE.md`: User guide with examples and API reference
  - `docs/INSTALLATION_TROUBLESHOOTING.md`: 850-line troubleshooting guide for all components
  - `VERIFICATION_QUICK_REFERENCE.md`: One-page quick reference

- **Tests**: `tests/test_installation_verification.py` (23 tests, 100% passing)

**Feature Detection API Example:**
```python
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
1. **NVIDIA Maxine** - Checks `MAXINE_HOME` env var or config path for `VideoEffectsApp.exe`
2. **Real-ESRGAN** - Searches PATH and common locations for `realesrgan-ncnn-vulkan[.exe]`
3. **FFmpeg** - Always available as fallback (CPU-based scaling)

When `--engine auto` is specified, the system selects the best available engine for the hardware.

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

**Test Structure** (160+ tests):
- `test_gui_helpers.py` - GUI utility functions (formatting, status emojis)
- `test_gui_integration.py` - GUI component integration tests
- `test_queue_manager.py` - Queue operations, threading, callbacks
- `test_audio_processor_deepfilternet.py` - DeepFilterNet AI denoising (v1.5.0, 14 tests)
- `test_audio_processor_audiosr.py` - AudioSR upsampling (v1.5.0, 20+ tests)
- `test_watch_folder.py` - Watch folder automation (v1.4.5, 20+ tests)
- `test_rtx_video_sdk.py` - RTX Video SDK integration (v1.5.1, 25+ tests)

Tests use:
- `pytest` fixtures for setup/teardown
- `unittest.mock` for patching subprocess calls and AI backends
- Temporary directories for file operations
- Feature detection mocking for optional dependencies
- Graceful fallback validation

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
- Python 3.10+ (match type hints, dataclasses)

**Optional but Recommended:**
- NVIDIA Driver 535+ (for NVENC hardware encoding)
- NVIDIA Maxine SDK (best AI upscaling on RTX GPUs)
- Real-ESRGAN ncnn-vulkan (AI upscaling for non-NVIDIA GPUs)

**Optional for Audio (v1.5.0):**
- **DeepFilterNet** (AI audio denoising, superior speech clarity)
- **AudioSR** (AI audio upsampling to 48kHz with speech/music models)
- PyTorch, torchaudio, Demucs (AI audio separation for best surround upmix)

**Optional for Face Restoration (v1.5.0):**
- **CodeFormer** (best-in-class face restoration, alternative to GFPGAN)
- GFPGAN (face restoration, good quality)

**Optional for Automation:**
- **watchdog** (watch folder file system monitoring, v1.4.5)
- **requests** (webhook notifications, v1.5.0)

The application gracefully handles missing optional dependencies and provides appropriate fallbacks or disables features.

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
