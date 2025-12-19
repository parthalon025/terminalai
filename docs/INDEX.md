# TerminalAI Documentation Index

Complete documentation for TerminalAI video processing suite.

## Getting Started

- [README](../README.md) - Main project documentation
- [Installation Guide](../README.md#installation) - Setup instructions
- [Quick Start](../README.md#quick-start) - Basic usage examples
- [CLAUDE.md](../CLAUDE.md) - Development and architecture guide

## User Guides

### Quick Start Guides
- [YouTube Enhancement Quick Start](QUICKSTART_YOUTUBE.md) - Download and enhance YouTube videos
- [Audio Enhancement Quick Start](QUICKSTART_AUDIO.md) - Audio restoration and surround upmixing
- [Deinterlace Quick Start](DEINTERLACE_QUICKSTART.md) - Fast deinterlacing setup

### Core Features
- [RTX Video SDK Guide](RTX_VIDEO_SDK.md) - NVIDIA RTX Video SDK integration (v1.5.1+)
- [Deinterlacing Guide](DEINTERLACING.md) - Complete deinterlacing documentation
- [Deinterlace Integration](DEINTERLACE_INTEGRATION.md) - Integration details
- [Face Restoration](FACE_RESTORATION.md) - Face enhancement with GFPGAN/CodeFormer
- [LUT Guide](LUT_GUIDE.md) - Color grading with LUTs

### Advanced Features
- [Video Analysis](ANALYSIS.md) - Intelligent video analysis system
- [Comparison Module](COMPARISON_MODULE.md) - A/B testing framework
- [Dry Run Mode](DRY_RUN_MODE.md) - Test settings without processing
- [Batch & Parallel Processing](BATCH_PARALLEL.md) - Batch processing guide

### GUI & Interface
- [GUI New Features](GUI_NEW_FEATURES.md) - Web interface features
- [GUI Bug Fixes Summary](GUI_BUG_FIXES_SUMMARY.md) - Recent fixes

## Development

### CI/CD & DevOps
- [CI/CD Guide](CICD.md) - Complete CI/CD documentation
- [CI/CD Quick Start](CICD_QUICKSTART.md) - Fast CI/CD setup
- [CI/CD Checklist](CICD_CHECKLIST.md) - Implementation checklist
- [CI/CD Implementation Summary](CICD_IMPLEMENTATION_SUMMARY.md) - Implementation details

### Security
- [Security Policy](../SECURITY.md) - Security guidelines
- [Security Audit (2025-12-18)](SECURITY_AUDIT_2025-12-18.md) - Recent audit
- [Security Fix Summary](SECURITY_FIX_SUMMARY.md) - Security improvements
- [Shell Injection Fix](SECURITY_FIX_SHELL_INJECTION.md) - CVE details

### Testing & Quality
- [Test Automation Report](TEST_AUTOMATION_REPORT.md) - Testing overview
- [Testing Status Summary](TESTING_STATUS_SUMMARY.md) - Test coverage
- [Verification Report](VERIFICATION_REPORT.md) - Verification results

### Project Management
- [Sprint 2 Implementation](SPRINT2_IMPLEMENTATION.md) - Sprint 2 details
- [Sprint 3 Implementation](SPRINT3_IMPLEMENTATION.md) - Sprint 3 details
- [Best Practices](BEST_PRACTICES.md) - VHS processing best practices
- [Dependency Audit](DEPENDENCY_AUDIT_REPORT.md) - Dependency analysis
- [Dependency Summary](DEPENDENCY_SUMMARY.md) - Dependency overview
- [Documentation Audit](DOCUMENTATION_AUDIT_REPORT.md) - Documentation review

## Contributing

- [Contributing Guide](../CONTRIBUTING.md) - How to contribute
- [Code of Conduct](../CONTRIBUTING.md#code-of-conduct) - Community guidelines
- [Issue Templates](../.github/ISSUE_TEMPLATE/) - Bug reports & feature requests
- [Pull Request Template](../.github/PULL_REQUEST_TEMPLATE.md) - PR guidelines

## Examples

- [Examples Directory](../examples/) - Code examples and usage patterns
- [Basic VHS Upscale](../examples/basic_vhs_upscale.py) - Simple example
- [Example README](../examples/README.md) - All examples

## API Reference

### Core Modules
- `vhs_upscaler.vhs_upscale` - Main processing pipeline
- `vhs_upscaler.queue_manager` - Batch queue management
- `vhs_upscaler.audio_processor` - Audio enhancement
- `vhs_upscaler.gui` - Web interface

### Analysis System
- `vhs_upscaler.analysis.models` - Analysis data models
- `vhs_upscaler.analysis.analyzer_wrapper` - Unified analyzer interface
- `vhs_upscaler.analysis.video_analyzer` - Python video analyzer

### CLI
- `vhs_upscaler.cli.upscale` - Upscale command
- `vhs_upscaler.cli.analyze` - Analysis command
- `vhs_upscaler.cli.batch` - Batch processing command
- `vhs_upscaler.cli.preview` - Preview command

### Utilities
- `vhs_upscaler.comparison` - Video comparison
- `vhs_upscaler.deinterlace` - Deinterlacing utilities
- `vhs_upscaler.dry_run` - Dry run mode
- `vhs_upscaler.face_restoration` - Face restoration
- `vhs_upscaler.presets` - Preset management

## External Resources

- [GitHub Repository](https://github.com/parthalon025/terminalai)
- [Issue Tracker](https://github.com/parthalon025/terminalai/issues)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [NVIDIA RTX Video SDK](https://developer.nvidia.com/rtx-video-sdk) - Recommended AI upscaling
- [NVIDIA Maxine](https://developer.nvidia.com/maxine) - Legacy (deprecated)
- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)

## Version History

- [Changelog](../CHANGELOG.md) - Version history and release notes

---

**Need Help?**
- Check the [Troubleshooting](../README.md#troubleshooting) section
- Search [existing issues](https://github.com/parthalon025/terminalai/issues)
- Ask in [GitHub Discussions](https://github.com/parthalon025/terminalai/discussions)
