# Changelog

All notable changes to TerminalAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repository structure reorganization for GitHub best practices

## [1.5.1] - 2025-12-19

### Added
- **RTX Video SDK Integration** - NVIDIA's latest AI upscaling technology
  - Super Resolution with up to 4x upscaling and edge/texture refinement
  - Artifact Reduction for VHS tracking errors, compression blockyness, color bleeding
  - SDR to HDR10 conversion for modern TVs
  - Python ctypes wrapper for SDK DLLs (`vhs_upscaler/rtx_video_sdk/`)
  - Automatic SDK detection and GPU validation
  - Requires RTX 20+ (Turing/Ampere/Ada/Blackwell)
- **RTX Video SDK Setup Wizard** - Interactive installation guide
  - Run with `terminalai-setup-rtx` or `python -m vhs_upscaler.setup_rtx`
  - System requirements check (GPU, driver, platform)
  - Benefits explanation with comparison table
  - Browser launch to NVIDIA download page
  - Python dependencies installation
- **GUI RTX Video Options** - New options panel for RTX Video SDK
  - Artifact Reduction toggle and strength slider
  - SDR to HDR conversion toggle
  - Auto-visibility based on engine selection
- **Startup Status Messages** - Shows RTX Video SDK availability at launch
- 25+ new unit tests for RTX Video SDK integration

### Changed
- RTX Video SDK is now the preferred upscaling engine (highest priority)
- Updated engine priority: `rtxvideo > realesrgan > ffmpeg > maxine`
- Updated GUI engine dropdown with RTX Video SDK option

### Deprecated
- NVIDIA Maxine integration - archived in favor of RTX Video SDK
  - Maxine still works but shows deprecation warning
  - New installations should use RTX Video SDK

### Dependencies
- Added optional `rtxvideo` dependency group: `numpy>=1.24.0`, `opencv-python>=4.8.0`
- Added optional `rtxvideo-cuda` group: includes `cupy-cuda12x>=12.0.0`

## [1.5.0] - 2025-12-18

### Added
- **AI Audio Enhancement** - DeepFilterNet and AudioSR Integration
  - DeepFilterNet AI denoising for superior speech clarity
  - AudioSR upsampling to 48kHz with speech/music models
  - Automatic fallbacks to FFmpeg when AI unavailable
  - GPU acceleration with CUDA support
- **CodeFormer Face Restoration** - Alternative to GFPGAN
  - Best-in-class face restoration quality
  - Adjustable fidelity weight (0.5-0.9)
  - Automatic model download and graceful fallback
- **Notification System**
  - Webhook notifications (Discord, Slack, custom)
  - Email notifications via SMTP
  - Job completion and error alerts
- **Watch Folder Automation** (v1.4.5)
  - Monitor directories for new videos
  - Multi-folder support with individual presets
  - Smart debouncing and lock file protection
- Complete documentation overhaul
  - 7 new quick-start guides
  - 600+ lines AudioSR integration guide
  - 300+ lines CodeFormer integration guide
- 50+ new unit tests

### Changed
- Updated audio processing pipeline order
- Improved GUI with conditional options
- Enhanced error handling and fallbacks

## [1.4.2] - 2025-12-18

### Fixed
- Polish codebase: update versions, requirements, and fix lint issues
- Comprehensive troubleshooting section with verbose error explanations

## [1.4.1] - Previous Release

### Added
- Video comparison module for A/B testing
- Dry run mode for testing settings
- Batch parallel processing
- Face restoration integration
- Deinterlacing improvements
- Security fixes for shell injection vulnerabilities

### Changed
- Updated GUI with new features
- Improved test coverage
- Enhanced documentation

## [1.4.0] - Previous Release

### Added
- Intelligent video analysis system
- CLI analyze command
- Preset recommendation engine
- VapourSynth QTGMC deinterlacing support

### Changed
- Refactored CLI into modular subcommands
- Improved audio processing pipeline
- Enhanced queue management

## [1.3.0] - Previous Release

### Added
- Audio enhancement with multiple modes
- Surround sound upmixing (Demucs AI support)
- HDR conversion (HDR10, HLG)
- LUT-based color grading
- Real-ESRGAN fallback engine

### Changed
- Improved FFmpeg filter chain building
- Enhanced progress tracking
- Better error handling

## [1.2.0] - Previous Release

### Added
- Gradio web GUI
- YouTube download integration (yt-dlp)
- Queue-based batch processing
- NVIDIA NVENC hardware encoding

### Changed
- Major refactoring of processing pipeline
- Improved preset system
- Enhanced logging

## [1.1.0] - Previous Release

### Added
- Multiple upscale presets (VHS, DVD, webcam, etc.)
- Deinterlacing support
- Noise reduction filters
- Color correction

## [1.0.0] - Initial Release

### Added
- Basic video upscaling with NVIDIA Maxine
- FFmpeg integration
- Command-line interface
- Configuration system

---

## Version Numbering

- **Major (X.0.0)**: Breaking changes, major new features
- **Minor (1.X.0)**: New features, backwards compatible
- **Patch (1.0.X)**: Bug fixes, minor improvements

[Unreleased]: https://github.com/parthalon025/terminalai/compare/v1.4.2...HEAD
[1.4.2]: https://github.com/parthalon025/terminalai/releases/tag/v1.4.2
