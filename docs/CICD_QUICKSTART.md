# CI/CD Quick Start Guide

Get up and running with the TerminalAI CI/CD pipeline in minutes.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [First Commit](#first-commit)
- [Creating a Pull Request](#creating-a-pull-request)
- [Making a Release](#making-a-release)
- [Docker Deployment](#docker-deployment)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- **Git** - Version control
- **Python 3.10+** - Programming language
- **pip** - Package manager

### Optional (for full functionality)

- **Docker** - Container deployment
- **Make** - Task automation (Linux/macOS/WSL)
- **FFmpeg** - Video processing

### GitHub Setup

1. Fork or clone the repository
2. Ensure you have write access
3. For releases, configure PyPI tokens in repository secrets

---

## Local Setup

### 1. Install Development Dependencies

```bash
# Clone repository
git clone https://github.com/parthalon025/terminalai.git
cd terminalai

# Install with dev dependencies
pip install -e ".[dev]"

# Or using Make
make install-dev
```

### 2. Setup Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks (one-time setup)
pre-commit install
pre-commit install --hook-type commit-msg

# Or using Make
make setup-hooks
```

### 3. Verify Installation

```bash
# Run verification
make verify-install

# Or manually
python -c "from vhs_upscaler import __version__; print(__version__)"
pytest tests/ -v --tb=short -k test_quick
```

---

## First Commit

### 1. Create Feature Branch

```bash
# Create and switch to new branch
git checkout -b feature/my-new-feature
```

### 2. Make Changes

```bash
# Edit files
vim vhs_upscaler/some_file.py

# Add new tests
vim tests/test_my_feature.py
```

### 3. Test Locally

```bash
# Run linting
make lint

# Auto-fix linting issues
make lint-fix

# Format code
make format

# Run tests
make test

# Run full CI pipeline locally
make ci-local
```

### 4. Commit Changes

```bash
# Stage changes
git add vhs_upscaler/some_file.py tests/test_my_feature.py

# Commit (pre-commit hooks run automatically)
git commit -m "feat: add new feature"

# Pre-commit hooks will:
# - Check code formatting
# - Run linting
# - Validate commit message
# - Run fast tests
# - Fix common issues
```

**Commit Message Format:**

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvement
- `chore:` - Maintenance

**Examples:**

```bash
git commit -m "feat: add GPU memory optimization"
git commit -m "fix: resolve queue deadlock issue"
git commit -m "docs: update installation guide"
git commit -m "test: add integration tests for audio processing"
```

### 5. Push Changes

```bash
# Push to remote
git push origin feature/my-new-feature
```

---

## Creating a Pull Request

### 1. Push Feature Branch

```bash
git push origin feature/my-new-feature
```

### 2. Create PR on GitHub

1. Go to repository on GitHub
2. Click "Pull requests" → "New pull request"
3. Select your branch
4. Fill in PR template:
   - Description of changes
   - Type of change
   - Testing performed
   - Checklist items

### 3. Wait for CI Checks

CI pipeline will automatically:

- Run linting checks
- Execute tests on Python 3.10, 3.11, 3.12
- Test on Ubuntu, Windows, macOS
- Check code coverage
- Scan for security issues
- Build packages
- Label PR automatically

**Typical CI run time:** 5-10 minutes

### 4. Address Review Comments

```bash
# Make requested changes
git add .
git commit -m "fix: address review comments"
git push origin feature/my-new-feature

# CI runs again automatically
```

### 5. Merge PR

Once approved and CI passes:
- Use "Squash and merge" (recommended)
- Or "Merge commit" for important features
- PR is automatically labeled and closed

---

## Making a Release

### 1. Prepare Release Branch (Optional)

```bash
# For major releases, create release branch
git checkout -b release/1.5.0
```

### 2. Update Version

```bash
# Bump version automatically
make version-bump-patch   # 1.4.2 → 1.4.3
make version-bump-minor   # 1.4.2 → 1.5.0

# Or edit manually
vim pyproject.toml
# Change: version = "1.4.3"
```

### 3. Update Documentation

```bash
# Update CHANGELOG (if exists)
vim CHANGELOG.md

# Commit version bump
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 1.4.3"
git push
```

### 4. Create Git Tag

```bash
# Create annotated tag
git tag -a v1.4.3 -m "Release version 1.4.3

- Feature: New GPU optimization
- Fix: Resolve memory leak
- Improvement: 30% faster processing"

# Push tag (triggers release workflow)
git push origin v1.4.3
```

### 5. Monitor Release Pipeline

1. Go to GitHub Actions
2. Watch "Release Automation" workflow
3. Pipeline will:
   - Validate version
   - Build distributions
   - Test installations
   - Create GitHub release
   - Publish to PyPI
   - Build Docker images

**Typical release time:** 10-15 minutes

### 6. Verify Release

```bash
# Check PyPI
# https://pypi.org/project/terminalai/1.4.3/

# Test installation
pip install terminalai==1.4.3

# Verify version
python -c "from vhs_upscaler import __version__; print(__version__)"
```

---

## Docker Deployment

### 1. Build Docker Image

```bash
# Build production image
make docker-build

# Or manually
docker build -t terminalai:latest .
```

### 2. Run Container

```bash
# Using docker-compose (recommended)
docker-compose up -d terminalai-gpu

# Or manually with GPU
docker run -d \
  --gpus all \
  -p 7860:7860 \
  -v ./input:/app/input:ro \
  -v ./output:/app/output:rw \
  terminalai:latest
```

### 3. Access Application

```
Open browser: http://localhost:7860
```

### 4. View Logs

```bash
# Docker compose
docker-compose logs -f terminalai-gpu

# Docker
docker logs -f terminalai-app
```

### 5. Stop Container

```bash
# Docker compose
docker-compose down

# Docker
docker stop terminalai-app
```

---

## Troubleshooting

### Pre-commit Hooks Failing

**Issue:** Hooks fail on commit

```bash
# View detailed error
git commit -m "feat: test"

# Run hooks manually to debug
pre-commit run --all-files

# Skip specific hook temporarily
SKIP=black git commit -m "temp commit"

# Update hooks
pre-commit autoupdate
```

**Common Fixes:**

```bash
# Fix formatting
make format

# Fix linting
make lint-fix

# Clear pre-commit cache
pre-commit clean
```

### CI Tests Failing

**Issue:** Tests pass locally but fail in CI

```bash
# Run tests exactly like CI
pytest tests/ -v --tb=short

# Check Python version
python --version  # Should be 3.10+

# Ensure FFmpeg installed
ffmpeg -version

# Run full CI locally
make ci-local
```

**Common Issues:**

- Missing FFmpeg in CI (check workflow)
- Platform-specific path issues
- Timing-dependent tests
- Network-dependent tests

### Docker Build Issues

**Issue:** Docker build fails

```bash
# Clear Docker cache
docker system prune -a

# Build without cache
docker build --no-cache -t terminalai:latest .

# Check Dockerfile syntax
docker build --dry-run .
```

**Common Issues:**

- Insufficient disk space
- Network issues downloading base image
- Invalid Dockerfile syntax

### Release Workflow Failing

**Issue:** Release fails to publish

**Check:**

1. **Secrets configured?**
   - Go to Settings → Secrets and variables → Actions
   - Add `PYPI_API_TOKEN`
   - Add `TEST_PYPI_API_TOKEN`

2. **Tag format correct?**
   ```bash
   # Correct
   git tag v1.4.3

   # Incorrect
   git tag 1.4.3
   git tag version-1.4.3
   ```

3. **Version in pyproject.toml matches tag?**
   ```bash
   # Tag: v1.4.3
   # pyproject.toml: version = "1.4.3"
   ```

4. **Test release first:**
   ```bash
   # Trigger manual workflow with Test PyPI
   # GitHub Actions → Release Automation → Run workflow
   ```

### Permission Denied Errors

**Issue:** Pre-commit or Git hook permission errors

```bash
# Linux/macOS - Fix hook permissions
chmod +x .git/hooks/*

# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### Coverage Below Threshold

**Issue:** Coverage check fails

```bash
# View coverage report
make test-cov
open htmlcov/index.html

# Add tests for uncovered code
# Coverage threshold: 70% (configurable in workflows/ci.yml)
```

---

## Quick Reference

### Common Commands

```bash
# Development
make install-dev          # Install dev dependencies
make setup-hooks          # Setup pre-commit hooks
make verify-install       # Verify installation

# Code Quality
make lint                 # Check linting
make lint-fix             # Auto-fix linting
make format               # Format code
make format-check         # Check formatting

# Testing
make test                 # Run all tests
make test-fast            # Unit tests only
make test-cov             # With coverage
make ci-local             # Full CI locally

# Docker
make docker-build         # Build image
make docker-run           # Run container
make docker-dev           # Dev container

# Release
make version-bump-patch   # Bump patch
make version-bump-minor   # Bump minor
make build                # Build packages
make release-test         # Test PyPI
make release              # Production PyPI

# Utilities
make clean                # Clean artifacts
make help                 # Show all commands
```

### File Locations

```
terminalai/
├── .github/
│   ├── workflows/          # CI/CD workflows
│   │   ├── ci.yml          # Main CI pipeline
│   │   ├── release.yml     # Release automation
│   │   ├── docker.yml      # Docker builds
│   │   └── ...
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── dependabot.yml      # Dependency updates
├── .pre-commit-config.yaml # Pre-commit hooks
├── pyproject.toml          # Package config
├── Dockerfile              # Docker build
├── docker-compose.yml      # Container orchestration
├── Makefile                # Task automation
└── docs/
    ├── CICD.md             # Full CI/CD docs
    └── CICD_QUICKSTART.md  # This file
```

### CI/CD Status Badges

Add to README.md:

```markdown
![CI](https://github.com/parthalon025/terminalai/workflows/CI%20Pipeline/badge.svg)
![Release](https://github.com/parthalon025/terminalai/workflows/Release%20Automation/badge.svg)
[![codecov](https://codecov.io/gh/parthalon025/terminalai/branch/main/graph/badge.svg)](https://codecov.io/gh/parthalon025/terminalai)
[![PyPI](https://img.shields.io/pypi/v/terminalai)](https://pypi.org/project/terminalai/)
```

---

## Next Steps

### For New Contributors

1. Read [CLAUDE.md](../CLAUDE.md) - Development guide
2. Review [BEST_PRACTICES.md](../BEST_PRACTICES.md) - VHS processing guidelines
3. Check [Issues](https://github.com/parthalon025/terminalai/issues) - Find tasks
4. Look for `good-first-issue` labels

### For Maintainers

1. Review [CICD.md](CICD.md) - Full documentation
2. Configure secrets for PyPI
3. Setup Codecov integration
4. Configure branch protection rules
5. Setup automated dependency updates

### Resources

- [GitHub Actions Docs](https://docs.github.com/actions)
- [Pre-commit Docs](https://pre-commit.com/)
- [Docker Docs](https://docs.docker.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

**Need Help?**

- Open an issue: https://github.com/parthalon025/terminalai/issues
- Check existing issues and PRs
- Review workflow logs in GitHub Actions
- Read full docs: [CICD.md](CICD.md)

**Last Updated:** 2024-12-18
