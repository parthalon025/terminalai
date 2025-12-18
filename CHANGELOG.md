# Changelog

All notable changes to TerminalAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repository structure reorganization for GitHub best practices
- Comprehensive `.gitignore` with video/audio file patterns
- `MANIFEST.in` for proper Python packaging
- `CONTRIBUTING.md` with detailed contribution guidelines
- `examples/` directory with usage examples
- `.github/FUNDING.yml` template for sponsor links

### Changed
- Moved documentation files to `docs/` directory
- Moved test files to `tests/` directory
- Moved utility scripts to `scripts/` directory
- Organized project structure following industry standards

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
