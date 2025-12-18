# Contributing to TerminalAI

Thank you for your interest in contributing to TerminalAI! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, constructive, and collaborative. We're all here to improve video processing tools.

## How to Contribute

### Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:
- Operating system and version
- Python version
- FFmpeg version
- GPU type (if using hardware acceleration)
- Complete error messages and logs
- Steps to reproduce

### Suggesting Features

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:
- Clear description of the feature
- Use case and benefits
- Potential implementation approach
- Any relevant examples from other tools

### Pull Requests

1. **Fork the repository** and create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our code style guidelines

3. **Write tests** for new functionality
   ```bash
   pytest tests/ -v
   ```

4. **Update documentation** if adding/changing features
   - Update README.md if needed
   - Add/update docstrings
   - Create examples in `examples/` if appropriate

5. **Ensure code quality**
   ```bash
   # Format code
   black vhs_upscaler/ tests/ --line-length 100

   # Lint code
   ruff check vhs_upscaler/ tests/

   # Run tests
   pytest tests/ --cov=vhs_upscaler
   ```

6. **Submit pull request** using our [PR template](.github/PULL_REQUEST_TEMPLATE.md)

## Development Setup

### Prerequisites

- Python 3.10+
- FFmpeg (latest version recommended)
- Git

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/terminalai.git
cd terminalai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev,audio,full]"

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=vhs_upscaler --cov-report=html

# Run specific test file
pytest tests/test_gui_helpers.py -v

# Run tests matching pattern
pytest tests/ -k "test_format" -v
```

### Code Style Guidelines

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (not 79)
- **Docstrings**: Google style
- **Type hints**: Use for function signatures (Python 3.10+ syntax)
- **Imports**: Organized with isort (black profile)

Example:

```python
from typing import Optional
from pathlib import Path

def process_video(
    input_file: str | Path,
    output_file: str | Path,
    preset: str = "vhs",
    quality: Optional[int] = None
) -> bool:
    """Process a video with the specified settings.

    Args:
        input_file: Path to input video file
        output_file: Path to output video file
        preset: Processing preset name (vhs, dvd, etc.)
        quality: Optional quality override (0-51)

    Returns:
        True if processing succeeded, False otherwise

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If preset is invalid
    """
    pass
```

### Commit Message Format

Use conventional commits format:

```
type(scope): brief description

Detailed explanation if needed.

Fixes #123
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding/updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Examples**:
```
feat(audio): add Demucs AI surround upmix support
fix(gui): resolve queue status display race condition
docs(readme): update installation instructions for Windows
test(queue): add concurrent job processing tests
```

## Project Structure

```
terminalai/
├── .github/              # GitHub templates and workflows
├── docs/                 # Documentation files
├── examples/             # Example scripts and usage patterns
├── scripts/              # Utility scripts (setup, analysis, etc.)
├── tests/                # Test suite
├── vhs_upscaler/         # Main package
│   ├── analysis/        # Video analysis module
│   ├── cli/             # CLI subcommands
│   ├── vapoursynth_scripts/  # VapourSynth deinterlacing
│   ├── audio_processor.py
│   ├── gui.py
│   ├── queue_manager.py
│   ├── vhs_upscale.py
│   └── ...
├── luts/                 # LUT files for color grading
├── CLAUDE.md             # Claude Code instructions
├── README.md             # Main documentation
├── pyproject.toml        # Package configuration
└── requirements.txt      # Dependencies
```

## Adding New Features

### Adding a New Upscale Engine

1. Add detection logic in `VideoUpscaler._check_dependencies()`
2. Implement upscaling method (e.g., `_upscale_with_newengine()`)
3. Add engine name to `available_engines` list
4. Update `_upscale()` method routing
5. Add configuration in `UpscaleConfig` dataclass
6. Update GUI dropdowns in `gui.py`
7. Add tests
8. Update documentation

### Adding a New Preset

1. Add preset definition in `config.yaml` or `vhs_upscaler/presets.py`
2. Define deinterlace/denoise/quality settings
3. Add to GUI dropdown
4. Update README.md preset table
5. Add example usage

### Adding a New Audio Effect

1. Define enum value in `AudioEnhanceMode` or `UpmixMode`
2. Add filter chain in `AudioProcessor._build_enhancement_filters()`
3. Update `AudioConfig` dataclass
4. Add GUI controls
5. Add tests
6. Document in README.md

## Testing Guidelines

### What to Test

- All new features
- Bug fixes (regression tests)
- Edge cases and error handling
- Different engine/encoder combinations
- Cross-platform compatibility (if possible)

### Test Organization

```
tests/
├── conftest.py                      # Shared fixtures
├── test_gui_helpers.py             # GUI utility tests
├── test_gui_integration.py         # GUI component tests
├── test_queue_manager.py           # Queue operations
├── test_comparison.py              # Video comparison
├── test_deinterlace_integration.py # Deinterlacing tests
└── ...
```

### Writing Tests

Use pytest fixtures and mocks for subprocess calls:

```python
from unittest.mock import patch, MagicMock

def test_upscale_with_maxine(tmp_path):
    """Test Maxine upscaling engine."""
    input_file = tmp_path / "input.mp4"
    output_file = tmp_path / "output.mp4"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        config = UpscaleConfig(
            input_file=str(input_file),
            output_file=str(output_file),
            engine="maxine"
        )

        upscaler = VideoUpscaler(config)
        result = upscaler._upscale_with_maxine()

        assert result is True
        mock_run.assert_called_once()
```

## Documentation

### Updating Documentation

When adding features, update:

1. **README.md** - User-facing documentation
2. **CLAUDE.md** - Internal architecture documentation
3. **Docstrings** - In-code documentation
4. **examples/** - Usage examples
5. **docs/** - Detailed guides

### Documentation Style

- Use clear, concise language
- Provide code examples
- Include command-line examples
- Explain "why" not just "how"
- Link to related documentation

## Release Process

(For maintainers)

1. Update version in `pyproject.toml`
2. Update CHANGELOG (if exists)
3. Create git tag: `git tag v1.x.x`
4. Push tag: `git push origin v1.x.x`
5. GitHub Actions will build and release

## Getting Help

- Check existing issues and discussions
- Read the [README](README.md) and [documentation](docs/)
- Ask questions in GitHub Discussions
- Join our community (if applicable)

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes (for significant contributions)
- README acknowledgments section (for major features)

---

Thank you for contributing to TerminalAI! Your efforts help improve video restoration for everyone.
