# Dependency Management Summary - TerminalAI v1.4.2

**Quick Reference for Developers**

---

## Installation Options

### 1. Minimal Install (Core Features)
```bash
pip install -e .
# Includes: yt-dlp, pyyaml, gradio
```

### 2. Development Install (with Testing & Code Quality)
```bash
pip install -r requirements-dev.txt
# Includes: pytest, black, ruff, mypy, and more
```

### 3. Audio Processing Install (Optional AI Features)
```bash
pip install -r requirements-audio.txt
# Includes: demucs, torch, torchaudio
```

### 4. Full Install (Everything)
```bash
pip install -e ".[full]"
# Or manually:
pip install -r requirements.txt
pip install -r requirements-audio.txt
```

---

## Core Dependencies (3 packages)

| Package | Version | Purpose |
|---------|---------|---------|
| yt-dlp | >=2023.0.0 | YouTube/video downloading |
| pyyaml | >=6.0 | Configuration files |
| gradio | >=4.0.0 | Web interface |

---

## External Tools Required

### Required
- **FFmpeg** (any recent version 4.0+)
  ```bash
  # Linux: sudo apt install ffmpeg
  # macOS: brew install ffmpeg
  # Windows: winget install FFmpeg
  ```

### Optional (Better Quality)
- **NVIDIA Maxine SDK** - Best AI upscaling (RTX GPUs)
- **Real-ESRGAN** - AI upscaling (AMD/Intel/NVIDIA)
- **VapourSynth** - QTGMC deinterlacing (archival quality)

---

## Security Status

Last Audit: 2025-12-18

- Vulnerabilities: **0 critical, 0 high, 0 medium**
- Security Score: **A+ (100/100)**
- License Compliance: **100% MIT compatible**

See: [DEPENDENCY_AUDIT_REPORT.md](DEPENDENCY_AUDIT_REPORT.md) for full details.

---

## Dependency Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Core runtime dependencies |
| `requirements-dev.txt` | Development tools (testing, linting) |
| `requirements-audio.txt` | Optional audio features (Demucs AI) |
| `pyproject.toml` | Package metadata and build config |
| `.github/dependabot.yml` | Automated dependency updates |

---

## Update Strategy

**Automated:** Dependabot creates weekly PRs for dependency updates
**Manual Check:** `pip list --outdated`
**Security Scan:** `pip-audit` (run weekly in CI/CD)

---

## Python Version Support

- Minimum: **Python 3.10**
- Tested: **Python 3.10, 3.11, 3.12, 3.13**
- Recommended: **Python 3.11+**

---

## Quick Commands

```bash
# Check for security vulnerabilities
pip install pip-audit && pip-audit

# Check for outdated packages
pip list --outdated

# Update all dependencies
pip install --upgrade yt-dlp pyyaml gradio

# Run tests
pytest tests/ -v

# Code quality check
black --check vhs_upscaler/ tests/
ruff check vhs_upscaler/ tests/

# Format code
black vhs_upscaler/ tests/
ruff check vhs_upscaler/ tests/ --fix
```

---

## Troubleshooting

### "No module named 'yt_dlp'"
```bash
pip install yt-dlp
```

### "No module named 'gradio'"
```bash
pip install gradio
```

### "ModuleNotFoundError: No module named 'demucs'"
```bash
# Only needed for AI audio upmixing
pip install -r requirements-audio.txt
```

### FFmpeg not found
See external tool installation above.

---

## For CI/CD

```yaml
# GitHub Actions example
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -e .
    pip install -r requirements-dev.txt

- name: Security scan
  run: |
    pip install pip-audit
    pip-audit
```

---

## License Information

- **TerminalAI:** MIT License
- **yt-dlp:** Unlicense (public domain)
- **PyYAML:** MIT License
- **Gradio:** Apache-2.0 License

All dependencies are compatible with MIT licensing.

---

For detailed dependency analysis, see: [DEPENDENCY_AUDIT_REPORT.md](DEPENDENCY_AUDIT_REPORT.md)
