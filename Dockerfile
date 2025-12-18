# Multi-stage Dockerfile for TerminalAI VHS Upscaler
# Optimized for production deployment with GPU support

# Stage 1: Base image with system dependencies
FROM nvidia/cuda:12.1.0-base-ubuntu22.04 AS base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash terminalai

# Stage 2: Python dependencies builder
FROM base AS builder

WORKDIR /build

# Copy dependency files
COPY requirements.txt pyproject.toml ./
COPY vhs_upscaler/__init__.py vhs_upscaler/__init__.py

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --user --no-warn-script-location -r requirements.txt

# Install the package
COPY . .
RUN pip install --user --no-warn-script-location -e .

# Stage 3: Runtime image
FROM base AS runtime

# Copy Python packages from builder
COPY --from=builder /root/.local /home/terminalai/.local

# Set up working directory
WORKDIR /app

# Copy application code
COPY --chown=terminalai:terminalai . .

# Switch to non-root user
USER terminalai

# Add local bin to PATH
ENV PATH="/home/terminalai/.local/bin:${PATH}"

# Create directories for input/output
RUN mkdir -p /app/input /app/output /app/models

# Expose Gradio port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# Default command: Launch Gradio GUI
CMD ["python3", "-m", "vhs_upscaler.gui", "--server-name", "0.0.0.0", "--server-port", "7860"]

# Stage 4: Development image with additional tools
FROM runtime AS development

USER root

# Install development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    ruff \
    ipython \
    jupyter

USER terminalai

# Override CMD for development
CMD ["/bin/bash"]
