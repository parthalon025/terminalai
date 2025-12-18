# Makefile for TerminalAI VHS Upscaler
# =====================================
# Provides common development tasks for cross-platform development

.PHONY: help install install-dev install-full clean lint format test test-cov test-fast \
        docker-build docker-run docker-dev pre-commit setup-hooks benchmark release

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python
PIP := pip
PYTEST := pytest
BLACK := black
RUFF := ruff
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)TerminalAI VHS Upscaler - Development Makefile$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# Installation targets
install: ## Install package with core dependencies
	$(PIP) install -e .

install-dev: ## Install package with development dependencies
	$(PIP) install -e ".[dev]"

install-full: ## Install package with all optional dependencies
	$(PIP) install -e ".[full,dev]"

install-audio: ## Install package with audio processing dependencies
	$(PIP) install -e ".[audio]"

# Cleaning targets
clean: ## Clean build artifacts and cache files
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.orig" -delete
	@echo "$(GREEN)Clean complete!$(NC)"

clean-docker: ## Clean Docker images and containers
	$(DOCKER) system prune -f
	$(DOCKER) image prune -f

# Code quality targets
lint: ## Run linting checks (ruff)
	@echo "$(BLUE)Running Ruff linter...$(NC)"
	$(RUFF) check vhs_upscaler/ tests/ download_youtube.py

lint-fix: ## Run linting checks and auto-fix issues
	@echo "$(BLUE)Running Ruff with auto-fix...$(NC)"
	$(RUFF) check vhs_upscaler/ tests/ download_youtube.py --fix

format: ## Format code with Black
	@echo "$(BLUE)Formatting code with Black...$(NC)"
	$(BLACK) vhs_upscaler/ tests/ download_youtube.py --line-length 100

format-check: ## Check code formatting without changes
	@echo "$(BLUE)Checking code formatting...$(NC)"
	$(BLACK) --check vhs_upscaler/ tests/ download_youtube.py --line-length 100

# Testing targets
test: ## Run all tests
	@echo "$(BLUE)Running test suite...$(NC)"
	$(PYTEST) tests/ -v

test-fast: ## Run fast unit tests only
	@echo "$(BLUE)Running fast unit tests...$(NC)"
	$(PYTEST) tests/ -v -m "unit" --tb=short

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(PYTEST) tests/ -v -m "integration"

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTEST) tests/ --cov=vhs_upscaler --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	$(PYTEST) tests/ -v -f

benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running benchmarks...$(NC)"
	$(PYTEST) tests/ -v --benchmark-only

# Pre-commit targets
setup-hooks: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	$(PIP) install pre-commit
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "$(GREEN)Pre-commit hooks installed!$(NC)"

pre-commit: ## Run pre-commit on all files
	@echo "$(BLUE)Running pre-commit checks...$(NC)"
	pre-commit run --all-files

# Docker targets
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	$(DOCKER) build -t terminalai:latest .

docker-build-dev: ## Build development Docker image
	@echo "$(BLUE)Building development Docker image...$(NC)"
	$(DOCKER) build -t terminalai:dev --target development .

docker-run: ## Run Docker container
	$(DOCKER_COMPOSE) up terminalai-gpu

docker-run-cpu: ## Run Docker container (CPU only)
	$(DOCKER_COMPOSE) --profile cpu up terminalai-cpu

docker-dev: ## Run development Docker container
	$(DOCKER_COMPOSE) --profile dev run --rm terminalai-dev

docker-stop: ## Stop Docker containers
	$(DOCKER_COMPOSE) down

# Release targets
version-bump-patch: ## Bump patch version (e.g., 1.4.2 -> 1.4.3)
	@echo "$(BLUE)Bumping patch version...$(NC)"
	@$(PYTHON) -c "import re; \
		content = open('pyproject.toml').read(); \
		match = re.search(r'version = \"(\d+)\.(\d+)\.(\d+)\"', content); \
		new_version = f'{match.group(1)}.{match.group(2)}.{int(match.group(3))+1}'; \
		print(f'New version: {new_version}'); \
		new_content = re.sub(r'version = \"\d+\.\d+\.\d+\"', f'version = \"{new_version}\"', content); \
		open('pyproject.toml', 'w').write(new_content)"

version-bump-minor: ## Bump minor version (e.g., 1.4.2 -> 1.5.0)
	@echo "$(BLUE)Bumping minor version...$(NC)"
	@$(PYTHON) -c "import re; \
		content = open('pyproject.toml').read(); \
		match = re.search(r'version = \"(\d+)\.(\d+)\.(\d+)\"', content); \
		new_version = f'{match.group(1)}.{int(match.group(2))+1}.0'; \
		print(f'New version: {new_version}'); \
		new_content = re.sub(r'version = \"\d+\.\d+\.\d+\"', f'version = \"{new_version}\"', content); \
		open('pyproject.toml', 'w').write(new_content)"

build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)Build complete! Packages in dist/$(NC)"

release-test: build ## Upload to Test PyPI
	@echo "$(BLUE)Uploading to Test PyPI...$(NC)"
	twine upload --repository testpypi dist/*

release: build ## Upload to PyPI (production)
	@echo "$(YELLOW)WARNING: This will upload to production PyPI!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		twine upload dist/*; \
	fi

# Development helpers
run-gui: ## Launch Gradio GUI
	$(PYTHON) -m vhs_upscaler.gui

run-cli-help: ## Show CLI help
	$(PYTHON) -m vhs_upscaler.vhs_upscale --help

check-deps: ## Check for outdated dependencies
	$(PIP) list --outdated

update-deps: ## Update all dependencies
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --upgrade -r requirements.txt

verify-install: ## Verify installation is working
	@echo "$(BLUE)Verifying installation...$(NC)"
	@$(PYTHON) -c "from vhs_upscaler.logger import get_logger; print('✓ Logger OK')"
	@$(PYTHON) -c "from vhs_upscaler.queue_manager import VideoQueue; print('✓ Queue OK')"
	@$(PYTHON) -c "from vhs_upscaler import __version__; print(f'✓ Version: {__version__}')"
	@$(PYTHON) -m vhs_upscaler.vhs_upscale --help > /dev/null && echo "✓ CLI OK"
	@echo "$(GREEN)All checks passed!$(NC)"

# CI/CD simulation
ci-local: clean lint format-check test-cov ## Simulate CI pipeline locally
	@echo "$(GREEN)Local CI checks complete!$(NC)"

# Documentation
docs: ## Generate documentation (placeholder)
	@echo "$(YELLOW)Documentation generation not yet implemented$(NC)"
	@echo "See README.md and CLAUDE.md for current documentation"
