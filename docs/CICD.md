# CI/CD Pipeline Documentation

Complete guide to the TerminalAI CI/CD infrastructure for continuous integration, deployment, and release automation.

## Table of Contents

- [Overview](#overview)
- [Workflows](#workflows)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Docker Deployment](#docker-deployment)
- [Release Process](#release-process)
- [Development Workflow](#development-workflow)
- [Monitoring & Metrics](#monitoring--metrics)

---

## Overview

The TerminalAI CI/CD pipeline ensures code quality, automated testing, and streamlined releases through:

- **GitHub Actions** - Automated testing, linting, security scanning
- **Pre-commit Hooks** - Local code quality checks before commits
- **Docker** - Containerized deployment with GPU support
- **Automated Releases** - Version management and PyPI publishing
- **Performance Monitoring** - Benchmark tracking and memory profiling

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────┐
│              Developer Workflow                      │
├─────────────────────────────────────────────────────┤
│  1. Write Code                                      │
│  2. Pre-commit Hooks (local validation)             │
│  3. Push to GitHub                                  │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│              CI Pipeline (GitHub Actions)            │
├─────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  Lint    │  │  Test    │  │ Security │          │
│  │  Check   │  │  Suite   │  │  Scan    │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│       │             │             │                 │
│       └─────────────┴─────────────┘                 │
│                     │                               │
│            ┌────────▼────────┐                      │
│            │  Build Package  │                      │
│            └────────┬────────┘                      │
└─────────────────────┼─────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────┐
│          Release Pipeline (on tag)                 │
├───────────────────────────────────────────────────┤
│  1. Validate version                              │
│  2. Build distributions (wheel + sdist)           │
│  3. Test installations (multi-platform)           │
│  4. Create GitHub release                         │
│  5. Publish to PyPI                               │
│  6. Build & push Docker images                    │
└───────────────────────────────────────────────────┘
```

---

## Workflows

### 1. CI Pipeline (`ci.yml`)

**Triggers:** Push to main/develop, Pull Requests

**Jobs:**

#### Lint Job
- Runs Black (code formatting check)
- Runs Ruff (linting)
- Fast fail for code quality issues

#### Test Job
- Matrix testing: Python 3.10, 3.11, 3.12
- Cross-platform: Ubuntu, Windows, macOS
- Installs FFmpeg on each platform
- Runs full test suite
- Uploads test results as artifacts

#### Coverage Job
- Runs tests with coverage measurement
- Uploads to Codecov
- Enforces 70% coverage minimum
- Generates HTML coverage report

#### Security Job
- Bandit security scanning
- Safety dependency vulnerability checks
- Uploads security reports

#### Build Job
- Builds source distribution (sdist)
- Builds wheel distribution
- Validates with Twine
- Uploads build artifacts

#### Integration Test Job
- Runs integration tests separately
- Requires test job to pass first

**Usage:**

```bash
# Triggered automatically on push/PR
# View results in GitHub Actions tab
# Download artifacts from workflow run page
```

**Configuration:**

```yaml
# .github/workflows/ci.yml
env:
  PYTHON_VERSION: "3.10"  # Default Python version
```

---

### 2. Release Automation (`release.yml`)

**Triggers:**
- Git tags matching `v*.*.*` pattern
- Manual workflow dispatch with version input

**Jobs:**

#### Validate Version
- Extracts version from tag or input
- Validates version format (x.y.z)
- Checks consistency with pyproject.toml

#### Build Release
- Builds source and wheel distributions
- Verifies packages with Twine

#### Test Installation
- Tests installation on all platforms
- Verifies imports and CLI entry points
- Ensures package works before release

#### Create GitHub Release
- Generates changelog from git commits
- Creates GitHub release with artifacts
- Attaches wheel and sdist files

#### Publish to PyPI
- Publishes to PyPI (on tag push)
- Publishes to Test PyPI (on manual trigger)
- Requires PyPI API tokens in secrets

**Usage:**

```bash
# Create release by pushing a tag
git tag v1.4.3
git push origin v1.4.3

# Or trigger manually from GitHub Actions UI
# Actions → Release Automation → Run workflow
# Input: version (e.g., 1.4.3)
```

**Required Secrets:**

- `PYPI_API_TOKEN` - Production PyPI token
- `TEST_PYPI_API_TOKEN` - Test PyPI token

---

### 3. Docker Pipeline (`docker.yml`)

**Triggers:** Push to main, tags, PRs, manual dispatch

**Jobs:**

#### Build Docker
- Multi-architecture builds (amd64, arm64)
- Pushes to GitHub Container Registry
- Tags images with version and SHA
- Caches layers for faster builds

#### Security Scan
- Scans images with Trivy
- Uploads results to GitHub Security
- Detects vulnerabilities in dependencies

**Usage:**

```bash
# Pull latest image
docker pull ghcr.io/parthalon025/terminalai:latest

# Run container
docker-compose up terminalai-gpu

# Or manually
docker run -p 7860:7860 ghcr.io/parthalon025/terminalai:latest
```

**Image Tags:**

- `latest` - Latest main branch build
- `v1.4.2` - Specific version
- `sha-abc123` - Git commit SHA
- `main` - Main branch builds

---

### 4. CodeQL Security Analysis (`codeql.yml`)

**Triggers:**
- Push to main/develop
- Pull requests
- Weekly schedule (Monday midnight)

**Features:**

- Static code analysis for security vulnerabilities
- Detects common security issues
- Extended query suite
- Results viewable in GitHub Security tab

**Usage:**

Results automatically appear in:
- Pull request checks
- Repository Security tab
- Security advisories (if issues found)

---

### 5. Performance Benchmarks (`performance.yml`)

**Triggers:**
- Push to main
- Pull requests
- Weekly schedule (Sunday 2am)
- Manual dispatch

**Jobs:**

#### Benchmark
- Runs pytest benchmarks
- Tracks performance over time
- Stores results for comparison

#### Memory Profile
- Profiles memory usage
- Generates memory plots
- Uploads artifacts

**Usage:**

```bash
# View benchmark trends in Actions
# Download memory profiles from artifacts

# Run locally
make benchmark
```

---

### 6. Dependency Review (`dependency-review.yml`)

**Triggers:** Pull Requests

**Jobs:**

#### Dependency Review
- Analyzes dependency changes
- Detects security vulnerabilities
- Comments on PRs with findings
- Fails on moderate+ severity issues

#### Pip Audit
- Audits Python dependencies
- Checks for known vulnerabilities
- Uploads audit reports

**Usage:**

- Automatic on every PR
- View results in PR checks
- Review comments for details

---

## Pre-commit Hooks

Automated local code quality checks before commits.

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks (run once)
make setup-hooks

# Or manually
pre-commit install
pre-commit install --hook-type commit-msg
```

### Hooks Configured

#### General File Checks
- Trailing whitespace removal
- End-of-file fixer
- YAML/TOML/JSON validation
- Large file detection
- Merge conflict detection
- Private key detection

#### Python Code Quality
- **Black** - Code formatting (100 char lines)
- **Ruff** - Fast linting with auto-fix
- **isort** - Import sorting
- **mypy** - Type checking
- **Bandit** - Security scanning
- **pydocstyle** - Docstring validation

#### Documentation
- **markdownlint** - Markdown formatting
- **shellcheck** - Shell script validation

#### Custom Hooks
- **pytest-check** - Run fast unit tests
- **check-version-sync** - Verify version consistency
- **check-forbidden-patterns** - Detect anti-patterns

### Usage

```bash
# Hooks run automatically on commit
git commit -m "feat: add new feature"

# Run manually on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Skip hooks (not recommended)
git commit --no-verify -m "emergency fix"
```

### Configuration

Edit `.pre-commit-config.yaml` to customize:

```yaml
# Disable specific hooks
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        # Add files to exclude
        exclude: ^migrations/
```

---

## Docker Deployment

### Images

Three Docker targets available:

1. **Runtime (Production)**
   ```bash
   docker build --target runtime -t terminalai:latest .
   docker-compose up terminalai-gpu
   ```

2. **CPU-Only**
   ```bash
   docker-compose --profile cpu up terminalai-cpu
   ```

3. **Development**
   ```bash
   docker build --target development -t terminalai:dev .
   docker-compose --profile dev run terminalai-dev
   ```

### Features

- NVIDIA GPU support (CUDA 12.1)
- Non-root user for security
- Multi-stage builds for smaller images
- Health checks
- Volume mounts for I/O
- Environment variable configuration

### Docker Compose

```yaml
# docker-compose.yml
services:
  terminalai-gpu:      # GPU-accelerated (default)
  terminalai-cpu:      # CPU-only (--profile cpu)
  terminalai-dev:      # Development (--profile dev)
```

**Usage:**

```bash
# Start GPU version
docker-compose up -d terminalai-gpu

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Clean up
make clean-docker
```

### Environment Variables

```bash
# docker-compose.yml or .env file
NVIDIA_VISIBLE_DEVICES=all
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
```

### Volume Mounts

```yaml
volumes:
  - ./input:/app/input:ro       # Read-only input
  - ./output:/app/output:rw     # Read-write output
  - ./models:/app/models:rw     # Model storage
  - ./config.yaml:/app/config.yaml:ro
```

---

## Release Process

### Version Bumping

```bash
# Bump patch version (1.4.2 → 1.4.3)
make version-bump-patch

# Bump minor version (1.4.2 → 1.5.0)
make version-bump-minor

# Manual version update
# Edit pyproject.toml: version = "1.4.3"
```

### Creating a Release

#### 1. Prepare Release

```bash
# Ensure clean working directory
git status

# Run full CI locally
make ci-local

# Update CHANGELOG (if exists)
# Update version in pyproject.toml
make version-bump-patch

# Commit version bump
git add pyproject.toml
git commit -m "chore: bump version to 1.4.3"
git push
```

#### 2. Create and Push Tag

```bash
# Create annotated tag
git tag -a v1.4.3 -m "Release version 1.4.3"

# Push tag (triggers release workflow)
git push origin v1.4.3
```

#### 3. Monitor Release

1. Go to GitHub Actions
2. Watch "Release Automation" workflow
3. Verify all jobs pass
4. Check GitHub Releases page

#### 4. Verify Release

```bash
# Check PyPI
# https://pypi.org/project/terminalai/

# Test installation
pip install terminalai==1.4.3

# Verify
python -c "from vhs_upscaler import __version__; print(__version__)"
```

### Hotfix Releases

```bash
# Create hotfix branch from tag
git checkout -b hotfix/1.4.3 v1.4.2

# Make fixes
git commit -m "fix: critical bug"

# Bump patch version
make version-bump-patch

# Merge to main
git checkout main
git merge hotfix/1.4.3

# Tag and release
git tag v1.4.3
git push origin v1.4.3
```

---

## Development Workflow

### Daily Development

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and test locally
make lint format test

# 3. Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: add new feature"

# 4. Push and create PR
git push origin feature/new-feature
# Create PR on GitHub
```

### Code Quality Checks

```bash
# Linting
make lint              # Check for issues
make lint-fix          # Auto-fix issues

# Formatting
make format-check      # Check formatting
make format            # Apply formatting

# Testing
make test              # All tests
make test-fast         # Unit tests only
make test-cov          # With coverage

# Full CI simulation
make ci-local
```

### Makefile Commands

```bash
# Installation
make install           # Core dependencies
make install-dev       # Dev dependencies
make install-full      # All dependencies

# Code Quality
make lint              # Run linting
make format            # Format code
make test              # Run tests
make test-cov          # Tests with coverage

# Pre-commit
make setup-hooks       # Install hooks
make pre-commit        # Run all hooks

# Docker
make docker-build      # Build image
make docker-run        # Run container
make docker-dev        # Dev environment

# Release
make version-bump-patch    # Bump patch
make version-bump-minor    # Bump minor
make build                 # Build packages
make release-test          # Test PyPI
make release               # Production PyPI

# Utilities
make clean             # Clean artifacts
make verify-install    # Verify setup
make check-deps        # Check outdated deps
```

---

## Monitoring & Metrics

### Code Coverage

**Target:** Minimum 70% coverage

```bash
# Generate coverage report
make test-cov

# View HTML report
open htmlcov/index.html

# Check coverage in CI
# Codecov dashboard: https://codecov.io/gh/parthalon025/terminalai
```

### Performance Benchmarks

```bash
# Run benchmarks locally
make benchmark

# View trends in GitHub Actions
# Actions → Performance Benchmarks → View results
```

### Security Scanning

**Tools:**
- Bandit - Python security linting
- Safety - Dependency vulnerability scanning
- Trivy - Docker image scanning
- CodeQL - Advanced static analysis

**View Results:**
- Repository → Security tab
- Pull request checks
- Actions artifacts

### Build Metrics

**Tracked Metrics:**
- Build time (target: < 30 seconds)
- Test execution time
- Docker image size
- Package size
- Coverage percentage

### CI/CD Health Dashboard

Monitor in GitHub:
- Actions → Workflows (success rate)
- Security → Code scanning alerts
- Insights → Community Standards
- Pulse → Activity overview

---

## Troubleshooting

### Pre-commit Hooks Failing

```bash
# Skip specific hook temporarily
SKIP=black git commit -m "temp commit"

# Update hooks
pre-commit autoupdate

# Clear cache
pre-commit clean
```

### CI Tests Failing

```bash
# Run same tests locally
make ci-local

# Check specific job
pytest tests/ -v -k test_name

# View detailed logs in GitHub Actions
```

### Docker Build Issues

```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t terminalai:latest .

# Check Docker logs
docker logs terminalai-app
```

### Release Workflow Issues

```bash
# Verify secrets are set
# Settings → Secrets and variables → Actions

# Test release to Test PyPI first
# Workflow dispatch with version input

# Check PyPI token validity
```

---

## Best Practices

### Commit Messages

Follow Conventional Commits:

```
feat: add new feature
fix: resolve bug
docs: update documentation
test: add tests
chore: update dependencies
refactor: restructure code
perf: improve performance
ci: update workflows
```

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch (optional)
- `feature/*` - New features
- `fix/*` - Bug fixes
- `hotfix/*` - Critical fixes
- `release/*` - Release preparation

### Pull Request Workflow

1. Create feature branch
2. Make changes with tests
3. Run `make ci-local`
4. Push and create PR
5. Address review comments
6. Squash merge to main

### Testing Strategy

- **Unit tests** - Fast, isolated, 80%+ coverage
- **Integration tests** - Component interactions
- **Performance tests** - Benchmark critical paths
- **Security tests** - Automated scanning

---

## Configuration Files

### `.pre-commit-config.yaml`
Pre-commit hooks configuration

### `pyproject.toml`
- Package metadata
- Tool configuration (Black, Ruff, pytest)
- Build system settings

### `pytest.ini`
Pytest configuration and markers

### `Dockerfile`
Multi-stage Docker build

### `docker-compose.yml`
Container orchestration

### `Makefile`
Development task automation

### `.github/workflows/*.yml`
GitHub Actions workflows

---

## Resources

### Documentation
- [GitHub Actions Docs](https://docs.github.com/actions)
- [Pre-commit Docs](https://pre-commit.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Project Files
- `README.md` - Project overview
- `CLAUDE.md` - Development guide
- `BEST_PRACTICES.md` - VHS processing guidelines

### External Tools
- Codecov: https://codecov.io
- PyPI: https://pypi.org
- Test PyPI: https://test.pypi.org
- GitHub Container Registry: https://ghcr.io

---

## Maintenance

### Regular Tasks

**Weekly:**
- Review security alerts
- Check dependency updates
- Monitor CI success rates

**Monthly:**
- Update dependencies
- Review and clean workflows
- Update documentation

**Per Release:**
- Update CHANGELOG
- Test all platforms
- Verify documentation
- Create GitHub release

### Dependency Updates

```bash
# Check outdated packages
make check-deps

# Update dependencies
pip install --upgrade -r requirements.txt

# Test after updates
make test

# Update pre-commit hooks
pre-commit autoupdate
```

---

**Last Updated:** 2024-12-18
**Maintained By:** TerminalAI Contributors
**Questions?** Open an issue on GitHub
