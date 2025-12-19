# TerminalAI Documentation

Comprehensive documentation for the TerminalAI video upscaling suite.

## Documentation Structure

### `installation/` - Installation and Setup
- Complete installation guides for all platforms (Windows, Linux, macOS)
- Verification and troubleshooting documentation
- RTX Video SDK setup guides
- Windows installation with CUDA support
- Dependency analysis and compatibility guides
- Python version notices and Rust installation references

**Key Files:**
- `WINDOWS_INSTALLATION.md` - Comprehensive Windows setup
- `INSTALLATION_TROUBLESHOOTING.md` - Detailed troubleshooting (850+ lines)
- `VERIFICATION_GUIDE.md` - Installation verification
- `DEPENDENCY_ANALYSIS.md` - Technical dependency deep dive
- `PYTHON_VERSION_NOTICE.md` - Python compatibility information
- `RUST_*.md` - Rust toolchain installation guides

### `guides/` - User Guides
- GUI usage guides and optimization documentation
- Feature-specific tutorials
- Best practices for video processing
- Quick start guides for common scenarios

**Key Files:**
- `QUICK_START.md` - Getting started quickly
- `BASIC_MODE_QUICK_START.md` - Simplified beginner mode
- `VERIFY_BASIC_MODE.md` - Basic mode verification
- `GUI_*.md` - GUI usage and optimization guides

### `features/` - Feature Documentation
- Detailed documentation for specific features
- API references and integration guides
- Feature-specific implementation details

**Key Files:**
- `BASIC_ADVANCED_MODE.md` - Beginner vs advanced interface
- `GUI_MODEL_DOWNLOAD_UX_IMPROVEMENTS.md` - Model download improvements

### `development/` - Development Documentation
- Contributing guidelines
- Performance optimization guides and reports
- Test automation reports and coverage analysis
- Code review and quality standards
- Implementation details and bug fixes

**Key Files:**
- `CONTRIBUTING.md` - How to contribute
- `PERFORMANCE_ANALYSIS_REPORT.md` - Performance profiling
- `PERFORMANCE_OPTIMIZATIONS_APPLIED.md` - Applied optimizations
- `TEST_COVERAGE_REPORT.md` - Test coverage metrics
- `TEST_VALIDATION_SUMMARY.md` - Test validation results
- `HARDWARE_DETECTION_*.md` - Hardware detection implementation
- `QUICK_IMPROVEMENTS.md` - Quick wins and improvements
- `BASICSR_PATCH_IMPLEMENTATION.md` - BasicSR patches

### `releases/` - Release Information
- Changelogs and release notes
- Implementation summaries for each release
- Version history and migration guides
- Feature completion reports

**Key Files:**
- `CHANGELOG.md` - Version history
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `PERFORMANCE_SUMMARY.md` - Performance improvements
- `DEPENDENCY_UPDATE_SUMMARY.md` - Dependency changes
- `FIRST_RUN_WIZARD_SUMMARY.md` - Wizard feature summary
- `HARDWARE_DETECTION_SUMMARY.md` - Hardware detection feature
- `GUI_INTEGRATION_REPORT.md` - GUI integration status
- `GUI_OPTIMIZATION_STATUS.md` - GUI optimization tracking

### `deployment/` - Deployment Guides
- Production deployment checklists
- Docker and containerization guides
- Service configuration examples
- CI/CD pipeline documentation

**Key Files:**
- `DEPLOYMENT_CHECKLIST.md` - Pre-deployment checklist

### `security/` - Security Documentation
- Security policies and best practices
- Vulnerability reporting and patches
- Security audit guidelines and reports

**Key Files:**
- `SECURITY.md` - Security policy
- `SECURITY_FIXES.md` - Applied security fixes
- `SECURITY_PATCH_SUMMARY.md` - Patch summaries

### `architecture/` - Architecture Documentation
- System design and architecture
- Component interactions
- Data flow diagrams
- UX design specifications

**Key Files:**
- `GUI_COMPREHENSIVE_UX_PLAN.md` - GUI architecture and UX design

## Quick Start

### Getting Started

- **[Main README](../README.md)** - Project overview, features, quick installation
- **[Installation Guide](installation/WINDOWS_INSTALLATION.md)** - Comprehensive Windows installation
- **[Verification Guide](installation/VERIFICATION_GUIDE.md)** - Installation verification and testing
- **[Quick Install](installation/QUICK_INSTALL.txt)** - One-page copy-paste commands

### Troubleshooting

- **[Installation Troubleshooting](installation/INSTALLATION_TROUBLESHOOTING.md)** - Detailed troubleshooting for all components (850+ lines)
- **[Dependency Analysis](installation/DEPENDENCY_ANALYSIS.md)** - Technical deep dive into dependencies

## Quick Links

### Installation & Verification

#### Basic Installation
```bash
# Install package
pip install -e .

# Verify installation
python scripts/installation/verify_installation.py
```

#### Install Optional Features

**PyTorch (for AI features):**
```bash
# CPU version
pip install torch torchaudio

# CUDA 11.8 (for NVIDIA GPU)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**VapourSynth (advanced deinterlacing):**
```bash
# Install runtime: https://github.com/vapoursynth/vapoursynth/releases
pip install vapoursynth havsfunc
```

**Face Restoration:**
```bash
# GFPGAN (faster, good quality)
pip install gfpgan basicsr opencv-python

# CodeFormer (slower, best quality)
# Requires PyTorch installed first
# Models download automatically
```

**Audio Enhancement:**
```bash
# DeepFilterNet (AI denoising)
pip install deepfilternet

# AudioSR (AI upsampling)
pip install audiosr

# Demucs (AI stem separation for surround)
pip install demucs
```

### Verification

```bash
# Quick check
python scripts/installation/verify_installation.py --quick

# Full verification
python scripts/installation/verify_installation.py

# Check specific component
python scripts/installation/verify_installation.py --check pytorch

# Generate diagnostic report
python scripts/installation/verify_installation.py --report diagnostic.json

# Show feature matrix
python scripts/installation/verify_installation.py --matrix
```

## Feature Availability Reference

| Feature | Requirements | GPU Required | Documentation |
|---------|--------------|--------------|---------------|
| Basic Video Processing | FFmpeg | No | [README](../README.md) |
| Hardware Encoding | FFmpeg + NVIDIA GPU | Yes | [Troubleshooting](INSTALLATION_TROUBLESHOOTING.md#nvenc-not-available) |
| QTGMC Deinterlacing | VapourSynth + havsfunc | No | [Deinterlace Guide](../vhs_upscaler/DEINTERLACE_QUICKSTART.md) |
| Face Restoration (GFPGAN) | GFPGAN + PyTorch | Recommended | [Troubleshooting](INSTALLATION_TROUBLESHOOTING.md#gfpgan-issues) |
| Face Restoration (CodeFormer) | CodeFormer + PyTorch | Highly Recommended | [Troubleshooting](INSTALLATION_TROUBLESHOOTING.md#codeformer-issues) |
| AI Audio Denoising | DeepFilterNet + PyTorch | Recommended | [Troubleshooting](INSTALLATION_TROUBLESHOOTING.md#deepfilternet-issues) |
| AI Audio Upsampling | AudioSR + PyTorch | Recommended | [Troubleshooting](INSTALLATION_TROUBLESHOOTING.md#audiosr-issues) |
| AI Surround Upmix | Demucs + PyTorch | Essential | [Troubleshooting](INSTALLATION_TROUBLESHOOTING.md#demucs-issues) |

## Common Tasks

### Verify Installation Status

```bash
# Get feature availability
python -c "import sys; sys.path.insert(0, 'scripts/installation'); from verify_installation import get_available_features; print(get_available_features())"

# Check if GPU acceleration available
python -c "import sys; sys.path.insert(0, 'scripts/installation'); from verify_installation import check_component; print(check_component('gpu').is_available)"

# Check PyTorch CUDA status
python -c "import sys; sys.path.insert(0, 'scripts/installation'); from verify_installation import check_component; import json; print(json.dumps(check_component('pytorch').details, indent=2))"
```

### Troubleshoot Installation Issues

1. **Run verification:**
   ```bash
   python scripts/installation/verify_installation.py --report issue.json
   ```

2. **Check specific failing component:**
   ```bash
   python scripts/installation/verify_installation.py --check component_name
   ```

3. **Review suggestions in output**

4. **Consult troubleshooting guide:**
   - [Installation Troubleshooting](INSTALLATION_TROUBLESHOOTING.md)

### Performance Optimization

**Check GPU status:**
```bash
# Verify GPU detected
python scripts/installation/verify_installation.py --check gpu

# Monitor GPU usage (NVIDIA)
nvidia-smi -l 1
```

**Check encoder availability:**
```bash
# List available encoders
ffmpeg -hide_banner -encoders | grep nvenc

# Test NVENC
ffmpeg -i test.mp4 -c:v h264_nvenc -preset p7 -tune hq test_nvenc.mp4
```

## Component Status Quick Reference

### Core Components

- **Python 3.10+**: Required
- **FFmpeg**: Required for all video operations
- **NVIDIA GPU**: Optional, for hardware acceleration

### AI Components

- **PyTorch**: Required for all AI features (CUDA version recommended)
- **VapourSynth**: Optional, for QTGMC deinterlacing
- **GFPGAN**: Optional, face restoration (fast)
- **CodeFormer**: Optional, face restoration (best quality)
- **DeepFilterNet**: Optional, AI audio denoising
- **AudioSR**: Optional, AI audio upsampling
- **Demucs**: Optional, AI surround upmix (GPU essential)

## Testing

### Run Verification Tests

```bash
# Run all verification tests
pytest tests/test_installation_verification.py -v

# Run specific test class
pytest tests/test_installation_verification.py::TestPyTorchVerifier -v

# Run with coverage
pytest tests/test_installation_verification.py --cov=verify_installation
```

### Test Specific Features

```bash
# Test PyTorch CUDA
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Test VapourSynth
python -c "import vapoursynth; print(vapoursynth.core.version())"

# Test GFPGAN
python -c "import gfpgan; print('GFPGAN available')"

# Test Demucs
python -c "import demucs; print('Demucs available')"
```

## Integration Examples

### In Application Code

```python
import sys
sys.path.insert(0, 'scripts/installation')
from verify_installation import get_available_features, check_component

# Get all features
features = get_available_features()

# Conditional feature usage
if features['face_restoration']:
    # Enable face restoration UI
    pass

if features['gpu_acceleration']:
    # Use hardware encoding
    encoder = "hevc_nvenc"
else:
    # Fallback to software
    encoder = "libx265"

# Check specific component details
pytorch = check_component('pytorch')
if pytorch.is_available and pytorch.details.get('cuda_available'):
    # Use GPU-accelerated processing
    device = "cuda"
else:
    # CPU fallback
    device = "cpu"
```

### In Scripts

```bash
#!/bin/bash

# Verify installation before processing
python scripts/installation/verify_installation.py --quiet
if [ $? -ne 0 ]; then
    echo "ERROR: Missing required dependencies"
    echo "Run: python scripts/installation/verify_installation.py"
    exit 1
fi

# Process videos
python -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4
```

## Getting Help

### Bug Reports

When reporting issues, include:

1. **Verification report:**
   ```bash
   python scripts/installation/verify_installation.py --report diagnostic.json
   ```

2. **System information** (from report)

3. **Full error message and traceback**

4. **Steps to reproduce**

### Resources

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: This folder
- **FFmpeg Docs**: https://ffmpeg.org/documentation.html
- **PyTorch Forums**: https://discuss.pytorch.org/
- **VapourSynth Forum**: https://forum.doom9.org/forumdisplay.php?f=82

## Contributing

### Adding New Verifiers

To add verification for new components:

1. **Create verifier class** in `scripts/installation/verify_installation.py`:
   ```python
   class NewComponentVerifier(ComponentVerifier):
       def verify(self) -> ComponentResult:
           try:
               import new_component
               # Verification logic
               return ComponentResult(
                   name="NewComponent",
                   status=ComponentStatus.AVAILABLE,
                   version=new_component.__version__
               )
           except ImportError:
               return ComponentResult(
                   name="NewComponent",
                   status=ComponentStatus.UNAVAILABLE,
                   suggestions=["pip install new_component"]
               )
   ```

2. **Add to verifiers list** in `InstallationVerifier.verify_all()`

3. **Add tests** in `tests/test_installation_verification.py`

4. **Update documentation** in `VERIFICATION_GUIDE.md` and `INSTALLATION_TROUBLESHOOTING.md`

### Testing Verifiers

```bash
# Test new verifier
python scripts/installation/verify_installation.py --check newcomponent

# Run unit tests
pytest tests/test_installation_verification.py::TestNewComponentVerifier -v
```

## Version History

### v1.5.0 (Current)
- Added comprehensive installation verification system
- Added troubleshooting guide for all components
- Added feature detection API
- Added verification test suite

### v1.4.x
- Previous features and updates
- See [main README](../README.md) for full history

## License

Same license as TerminalAI main project.
