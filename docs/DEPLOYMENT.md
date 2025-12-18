# Production Deployment Guide - VHS Upscaler v1.4.2

## Table of Contents

1. [Pre-Deployment Verification](#1-pre-deployment-verification)
2. [Environment Setup](#2-environment-setup)
3. [Configuration Requirements](#3-configuration-requirements)
4. [GPU/Hardware Requirements](#4-gpuhardware-requirements)
5. [Port and Firewall Configuration](#5-port-and-firewall-configuration)
6. [Logging and Monitoring Setup](#6-logging-and-monitoring-setup)
7. [Backup and Disaster Recovery](#7-backup-and-disaster-recovery)
8. [Performance Optimization](#8-performance-optimization)
9. [Security Hardening](#9-security-hardening)
10. [Post-Deployment Validation](#10-post-deployment-validation)
11. [Rollback Procedures](#11-rollback-procedures)
12. [User Acceptance Testing](#12-user-acceptance-testing)

---

## 1. Pre-Deployment Verification

### 1.1 Code Quality Checks

**Test Suite Execution:**
```bash
# Run full test suite with coverage
pytest tests/ -v --cov=vhs_upscaler --cov-report=html

# Target: >90% code coverage
# Expected: All tests passing, 0 failures
```

**Coverage Requirements:**
- [ ] Core modules (vhs_upscale.py): >95% coverage
- [ ] Queue management: >90% coverage
- [ ] GUI components: >85% coverage
- [ ] Audio processing: >85% coverage
- [ ] Overall coverage: >90%

**Linting and Code Standards:**
```bash
# Check code formatting
black vhs_upscaler/ tests/ --check --line-length 100

# Run linter
ruff check vhs_upscaler/ tests/

# Expected: 0 errors, 0 warnings
```

**Static Analysis:**
```bash
# Type checking (if using mypy)
mypy vhs_upscaler/ --ignore-missing-imports

# Security scanning
bandit -r vhs_upscaler/ -ll

# Dependency vulnerability check
pip-audit
```

### 1.2 Security Audit

**Critical Security Checks:**
- [ ] No hardcoded credentials in codebase
- [ ] Environment variables used for sensitive data
- [ ] Input validation on all user-supplied data
- [ ] Path traversal protection (file uploads)
- [ ] Shell injection protection (subprocess calls)
- [ ] Rate limiting configured for web GUI
- [ ] CORS policies defined
- [ ] Session management implemented

**Dependency Security:**
```bash
# Check for known vulnerabilities
pip-audit

# Update vulnerable packages
pip install --upgrade <package-name>

# Verify requirements.txt is up to date
pip freeze > requirements-frozen.txt
diff requirements.txt requirements-frozen.txt
```

**File Permission Audit:**
```bash
# Ensure proper file permissions (Linux/Mac)
find . -type f -name "*.py" -exec chmod 644 {} \;
find . -type f -name "*.sh" -exec chmod 755 {} \;
chmod 600 config.yaml  # Restrict config file access
```

### 1.3 Documentation Review

**Required Documentation:**
- [ ] README.md up to date with current version
- [ ] CLAUDE.md reflects current architecture
- [ ] API documentation complete
- [ ] Configuration examples provided
- [ ] Troubleshooting guide available
- [ ] Change log updated (CHANGELOG.md)
- [ ] License file present

### 1.4 Version Control

**Pre-Deployment Git Checks:**
```bash
# Ensure working directory is clean
git status

# Tag release version
git tag -a v1.4.2 -m "Production release v1.4.2"
git push origin v1.4.2

# Create release branch
git checkout -b release/v1.4.2
git push -u origin release/v1.4.2
```

**Checklist:**
- [ ] All changes committed
- [ ] Version number updated in all files
- [ ] Release tagged in git
- [ ] Release notes prepared
- [ ] Previous version backed up

---

## 2. Environment Setup

### 2.1 Python Environment

**Python Version Requirements:**
```bash
# Required: Python 3.10+
python --version  # Should output: Python 3.10.x or higher

# Create isolated virtual environment
python -m venv venv

# Activate environment
# Linux/Mac:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
```

**Environment Verification:**
- [ ] Python 3.10+ installed
- [ ] pip updated to latest version
- [ ] Virtual environment created
- [ ] Virtual environment activated

### 2.2 Core Dependencies

**Install Application:**
```bash
# Method 1: Editable install (recommended for production)
pip install -e .

# Method 2: Requirements file
pip install -r requirements.txt

# Verify installation
python -c "import vhs_upscaler; print(vhs_upscaler.__version__)"
# Expected output: 1.4.2
```

**Required Python Packages:**
```
yt-dlp>=2023.0.0      # YouTube downloading
pyyaml>=6.0           # Configuration
gradio>=4.0.0         # Web interface
```

**Optional Production Packages:**
```bash
# Audio processing (recommended)
pip install -e ".[audio]"  # Includes demucs, torch, torchaudio

# Development tools (only for staging/dev environments)
pip install -e ".[dev]"    # Includes pytest, black, ruff

# Full installation (all features)
pip install -e ".[full]"
```

### 2.3 External Binary Dependencies

**FFmpeg Installation:**

**Linux (Ubuntu/Debian):**
```bash
# Install FFmpeg with all codecs
sudo apt update
sudo apt install -y ffmpeg

# Verify installation
ffmpeg -version
ffprobe -version

# Check for hardware encoding support
ffmpeg -codecs | grep -i nvenc  # NVIDIA encoding
ffmpeg -codecs | grep -i vaapi  # Intel/AMD encoding
```

**macOS:**
```bash
# Install via Homebrew
brew install ffmpeg

# Verify installation
ffmpeg -version
```

**Windows:**
```powershell
# Install via winget (Windows 10+)
winget install FFmpeg

# Or download from: https://www.gyan.dev/ffmpeg/builds/
# Add to PATH: C:\ffmpeg\bin
```

**FFmpeg Build Requirements:**
- [ ] FFmpeg version 4.4+
- [ ] libx264 codec available
- [ ] libx265 codec available
- [ ] AAC encoder available
- [ ] Hardware encoder support (nvenc/vaapi) if GPU present

### 2.4 System-Specific Requirements

**Linux Production Server:**
```bash
# Install system libraries
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev

# Create application user (security best practice)
sudo useradd -m -s /bin/bash vhsupscaler
sudo usermod -aG video vhsupscaler  # GPU access

# Set up application directory
sudo mkdir -p /opt/vhs-upscaler
sudo chown vhsupscaler:vhsupscaler /opt/vhs-upscaler
```

**Windows Production Server:**
```powershell
# Install Visual C++ Redistributable (required for some dependencies)
# Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

# Install Python 3.10+ from python.org
# Ensure "Add Python to PATH" is checked during installation

# Create application directory
New-Item -ItemType Directory -Path "C:\Program Files\VHS-Upscaler"
```

**Docker Deployment (Optional):**
```dockerfile
# See docker/Dockerfile for full configuration
# Build image:
docker build -t vhs-upscaler:1.4.2 .

# Run container:
docker run -d \
  --name vhs-upscaler \
  -p 7860:7860 \
  -v /data/videos:/app/videos \
  --gpus all \
  vhs-upscaler:1.4.2
```

---

## 3. Configuration Requirements

### 3.1 Configuration File Setup

**Create Production Config:**
```bash
# Copy example configuration
cp vhs_upscaler/config.yaml /opt/vhs-upscaler/config.yaml

# Edit configuration for production
nano /opt/vhs-upscaler/config.yaml
```

**Critical Configuration Settings:**

```yaml
# vhs_upscaler/config.yaml

# NVIDIA Maxine SDK paths (if using Maxine)
maxine_path: "/opt/NVIDIA/Maxine/bin"
model_dir: "/opt/NVIDIA/Maxine/bin/models"

# FFmpeg path
ffmpeg_path: "/usr/bin/ffmpeg"  # Use absolute path in production

# Production defaults
defaults:
  resolution: 1080
  quality_mode: 0  # Best quality for production
  encoder: "hevc_nvenc"  # Use hardware encoder if available
  nvenc_preset: "p7"     # Best quality preset
  crf: 20                # Balanced quality/size
  preset: "vhs"

# Advanced production settings
advanced:
  keep_temp: false        # Don't keep temporary files
  intermediate_crf: 15    # High quality intermediate files
  max_workers: 2          # Limit concurrent jobs (adjust per server)
  log_level: "INFO"       # Production log level
```

**Configuration Validation:**
```bash
# Test configuration loading
python -c "
import yaml
with open('vhs_upscaler/config.yaml') as f:
    config = yaml.safe_load(f)
    print('Config loaded successfully')
    print(f'Max workers: {config[\"advanced\"][\"max_workers\"]}')
"
```

### 3.2 Environment Variables

**Required Environment Variables:**
```bash
# Create .env file (DO NOT commit to git)
cat > .env << EOF
# Application settings
VHS_OUTPUT_DIR=/opt/vhs-upscaler/output
VHS_TEMP_DIR=/opt/vhs-upscaler/temp
VHS_LOG_DIR=/opt/vhs-upscaler/logs

# NVIDIA Maxine (if installed)
MAXINE_HOME=/opt/NVIDIA/Maxine
MAXINE_MODEL_DIR=/opt/NVIDIA/Maxine/bin/models

# GPU settings
CUDA_VISIBLE_DEVICES=0  # Limit to specific GPU

# Production settings
VHS_ENV=production
VHS_LOG_LEVEL=INFO

# Web GUI settings
GRADIO_SERVER_PORT=7860
GRADIO_SERVER_NAME=0.0.0.0  # Listen on all interfaces
GRADIO_ANALYTICS_ENABLED=false

# Security settings (if implementing authentication)
VHS_SECRET_KEY=$(openssl rand -hex 32)
VHS_MAX_UPLOAD_SIZE=10737418240  # 10GB max upload

# Rate limiting
VHS_RATE_LIMIT_PER_MINUTE=10
EOF

# Load environment variables
source .env
```

**Systemd Environment File (Linux):**
```bash
# /etc/systemd/system/vhs-upscaler.service.d/environment.conf
[Service]
Environment="VHS_OUTPUT_DIR=/opt/vhs-upscaler/output"
Environment="VHS_TEMP_DIR=/opt/vhs-upscaler/temp"
Environment="VHS_LOG_DIR=/opt/vhs-upscaler/logs"
Environment="MAXINE_HOME=/opt/NVIDIA/Maxine"
Environment="GRADIO_SERVER_PORT=7860"
```

### 3.3 Directory Structure Setup

**Create Required Directories:**
```bash
# Linux/Mac
sudo mkdir -p /opt/vhs-upscaler/{output,temp,logs,uploads,models}
sudo chown -R vhsupscaler:vhsupscaler /opt/vhs-upscaler
sudo chmod 755 /opt/vhs-upscaler
sudo chmod 700 /opt/vhs-upscaler/temp  # Restrict temp directory

# Windows
New-Item -ItemType Directory -Path "C:\Program Files\VHS-Upscaler\output"
New-Item -ItemType Directory -Path "C:\Program Files\VHS-Upscaler\temp"
New-Item -ItemType Directory -Path "C:\Program Files\VHS-Upscaler\logs"
```

**Directory Checklist:**
- [ ] Output directory exists (read/write access)
- [ ] Temp directory exists (read/write access, auto-cleanup)
- [ ] Log directory exists (write access, log rotation)
- [ ] Upload directory exists (if using file uploads)
- [ ] Model directory exists (if using AI models)

### 3.4 Storage Requirements

**Disk Space Planning:**

| Component | Typical Size | Recommendation |
|-----------|-------------|----------------|
| Application | 100 MB | 500 MB |
| Python venv | 500 MB | 1 GB |
| FFmpeg | 200 MB | 500 MB |
| NVIDIA Maxine | 2 GB | 5 GB |
| Real-ESRGAN models | 500 MB | 1 GB |
| Demucs models | 1 GB | 2 GB |
| Temp files (per job) | 5-20 GB | 50 GB minimum |
| Output storage | Variable | 1 TB+ recommended |
| Log files | 10 MB/day | 10 GB (with rotation) |

**Storage Monitoring:**
```bash
# Check available disk space
df -h /opt/vhs-upscaler

# Set up disk space alerts (cron job)
cat > /opt/vhs-upscaler/check_disk.sh << 'EOF'
#!/bin/bash
THRESHOLD=90
USAGE=$(df /opt/vhs-upscaler | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $USAGE -gt $THRESHOLD ]; then
    echo "WARNING: Disk usage at ${USAGE}%" | mail -s "VHS Upscaler Disk Alert" admin@example.com
fi
EOF
chmod +x /opt/vhs-upscaler/check_disk.sh

# Add to crontab (run every hour)
echo "0 * * * * /opt/vhs-upscaler/check_disk.sh" | crontab -
```

---

## 4. GPU/Hardware Requirements

### 4.1 NVIDIA GPU Setup

**Driver Installation:**

**Linux:**
```bash
# Check current driver
nvidia-smi

# Install NVIDIA driver 535+ (Ubuntu)
sudo apt install -y nvidia-driver-535
sudo reboot

# Verify installation
nvidia-smi
# Should show: Driver Version: 535.x or higher
```

**Windows:**
```
Download from: https://www.nvidia.com/drivers
Select: GeForce/Quadro > Your GPU model
Minimum version: 535.x
Recommended: Latest Game Ready or Studio driver
```

**GPU Requirements:**
- [ ] NVIDIA GPU with compute capability 6.1+ (Pascal or newer)
- [ ] Driver version 535+
- [ ] NVENC hardware encoder support
- [ ] Minimum 4GB VRAM (8GB+ recommended)
- [ ] CUDA 11.8+ compatible

### 4.2 NVIDIA Maxine SDK (Optional)

**Installation:**
```bash
# Download Maxine SDK from:
# https://developer.nvidia.com/maxine-getting-started

# Linux installation
sudo mkdir -p /opt/NVIDIA/Maxine
sudo unzip Maxine_VideoEffects_SDK.zip -d /opt/NVIDIA/Maxine/

# Verify installation
ls -la /opt/NVIDIA/Maxine/bin/VideoEffectsApp
ls -la /opt/NVIDIA/Maxine/bin/models/

# Set environment variable
export MAXINE_HOME=/opt/NVIDIA/Maxine
echo 'export MAXINE_HOME=/opt/NVIDIA/Maxine' >> ~/.bashrc
```

**Maxine Checklist:**
- [ ] VideoEffectsApp binary present
- [ ] Model files downloaded (upscale models)
- [ ] MAXINE_HOME environment variable set
- [ ] GPU meets Maxine requirements (RTX series)

### 4.3 Real-ESRGAN Installation (Alternative)

**Linux/Mac:**
```bash
# Download latest release
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip

# Extract to /usr/local/bin
sudo unzip realesrgan-ncnn-vulkan-20220424-ubuntu.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/realesrgan-ncnn-vulkan

# Verify installation
realesrgan-ncnn-vulkan --help
```

**Windows:**
```powershell
# Download from GitHub releases
# https://github.com/xinntao/Real-ESRGAN/releases

# Extract to C:\Program Files\RealESRGAN\
# Add to PATH environment variable
```

**Real-ESRGAN Checklist:**
- [ ] Binary executable installed
- [ ] Vulkan runtime available
- [ ] Models downloaded (realesrgan-x4plus)
- [ ] Binary in system PATH

### 4.4 Hardware Acceleration Testing

**Test NVENC Encoding:**
```bash
# Test NVIDIA hardware encoding
ffmpeg -f lavfi -i testsrc=duration=10:size=1920x1080:rate=30 \
  -c:v hevc_nvenc -preset p7 -cq 20 test_nvenc.mp4

# Verify encoding used GPU
nvidia-smi dmon -s u -c 1
```

**Test Maxine Upscaling:**
```bash
# Run verification script
python scripts/verify_setup.py

# Expected output:
# ✓ FFmpeg found
# ✓ NVIDIA GPU detected
# ✓ NVENC available
# ✓ Maxine SDK found
```

**Performance Baseline:**
```bash
# Benchmark upscaling performance
time python -m vhs_upscaler.vhs_upscale \
  -i test_video.mp4 \
  -o test_output.mp4 \
  --engine maxine \
  --resolution 1080

# Record baseline performance metrics
# Expected: ~30-60 fps upscaling speed on RTX 3060+
```

### 4.5 CPU-Only Deployment

**For servers without GPU:**
```yaml
# config.yaml - CPU-only configuration
defaults:
  encoder: "libx265"  # CPU encoder
  preset: "medium"    # FFmpeg CPU preset

advanced:
  max_workers: 1      # Single worker to avoid CPU overload
```

**CPU Requirements:**
- [ ] Modern CPU (Intel i5/AMD Ryzen 5 or better)
- [ ] 16GB+ RAM recommended
- [ ] 8+ cores for parallel processing

---

## 5. Port and Firewall Configuration

### 5.1 Network Ports

**Default Port Configuration:**
- **7860** - Gradio web interface (HTTP)
- **7861** - Gradio internal communication (if using multiple workers)

**Port Checklist:**
- [ ] Port 7860 available (not in use)
- [ ] Firewall rules configured
- [ ] Reverse proxy configured (if applicable)
- [ ] SSL/TLS certificate installed (if HTTPS)

### 5.2 Firewall Rules

**Linux (UFW):**
```bash
# Allow Gradio web interface
sudo ufw allow 7860/tcp comment 'VHS Upscaler Web GUI'

# If using SSH for management
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable

# Verify rules
sudo ufw status
```

**Linux (iptables):**
```bash
# Allow incoming connections on port 7860
sudo iptables -A INPUT -p tcp --dport 7860 -j ACCEPT

# Save rules
sudo netfilter-persistent save
```

**Windows Firewall:**
```powershell
# Allow inbound traffic on port 7860
New-NetFirewallRule -DisplayName "VHS Upscaler Web GUI" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 7860 `
  -Action Allow
```

### 5.3 Reverse Proxy Configuration

**Nginx Configuration:**
```nginx
# /etc/nginx/sites-available/vhs-upscaler

upstream vhs_upscaler {
    server 127.0.0.1:7860;
}

server {
    listen 80;
    server_name vhs-upscaler.example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name vhs-upscaler.example.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/vhs-upscaler.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vhs-upscaler.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Large file upload support
    client_max_body_size 10G;
    client_body_timeout 3600s;
    proxy_read_timeout 3600s;

    location / {
        proxy_pass http://vhs_upscaler;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (for Gradio)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Enable Nginx Configuration:**
```bash
# Link configuration
sudo ln -s /etc/nginx/sites-available/vhs-upscaler /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

**Apache Configuration:**
```apache
# /etc/apache2/sites-available/vhs-upscaler.conf

<VirtualHost *:80>
    ServerName vhs-upscaler.example.com
    Redirect permanent / https://vhs-upscaler.example.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName vhs-upscaler.example.com

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/vhs-upscaler.example.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/vhs-upscaler.example.com/privkey.pem

    # Large file uploads
    LimitRequestBody 10737418240

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:7860/
    ProxyPassReverse / http://127.0.0.1:7860/

    # WebSocket support
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} =websocket [NC]
    RewriteRule /(.*)           ws://127.0.0.1:7860/$1 [P,L]
</VirtualHost>
```

### 5.4 SSL/TLS Certificate

**Let's Encrypt (Certbot):**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d vhs-upscaler.example.com

# Auto-renewal (added automatically)
sudo systemctl status certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

---

## 6. Logging and Monitoring Setup

### 6.1 Application Logging

**Configure Logging:**
```python
# vhs_upscaler/logger.py configuration

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os

def setup_production_logging():
    """Configure production-grade logging."""
    log_dir = os.getenv('VHS_LOG_DIR', '/opt/vhs-upscaler/logs')
    os.makedirs(log_dir, exist_ok=True)

    # Main application log (rotates daily, keeps 30 days)
    app_handler = TimedRotatingFileHandler(
        f'{log_dir}/vhs-upscaler.log',
        when='midnight',
        interval=1,
        backupCount=30
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # Error log (rotates at 100MB, keeps 10 files)
    error_handler = RotatingFileHandler(
        f'{log_dir}/vhs-upscaler-error.log',
        maxBytes=100*1024*1024,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
    ))

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[app_handler, error_handler]
    )
```

**Log Files:**
- `/opt/vhs-upscaler/logs/vhs-upscaler.log` - Application log
- `/opt/vhs-upscaler/logs/vhs-upscaler-error.log` - Error log
- `/opt/vhs-upscaler/logs/access.log` - Web access log
- `/opt/vhs-upscaler/logs/performance.log` - Performance metrics

### 6.2 Log Rotation

**Logrotate Configuration:**
```bash
# /etc/logrotate.d/vhs-upscaler

/opt/vhs-upscaler/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 vhsupscaler vhsupscaler
    sharedscripts
    postrotate
        systemctl reload vhs-upscaler > /dev/null 2>&1 || true
    endscript
}
```

### 6.3 System Monitoring

**Prometheus Metrics (Optional):**
```python
# Add to gui.py for Prometheus integration

from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metrics
jobs_total = Counter('vhs_jobs_total', 'Total jobs processed')
jobs_failed = Counter('vhs_jobs_failed', 'Total jobs failed')
processing_time = Histogram('vhs_processing_seconds', 'Time to process video')
queue_size = Gauge('vhs_queue_size', 'Current queue size')

# Start metrics server
start_http_server(9090)  # Metrics on port 9090
```

**Health Check Endpoint:**
```python
# Add to gui.py

def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "1.4.2",
        "queue_size": queue.size(),
        "uptime": get_uptime(),
        "disk_space": get_disk_space()
    }

# Add to Gradio interface
health_check_endpoint = gr.JSON(value=health_check, every=30)
```

### 6.4 Performance Monitoring

**System Metrics Script:**
```bash
#!/bin/bash
# /opt/vhs-upscaler/monitor.sh

LOG_FILE="/opt/vhs-upscaler/logs/performance.log"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    # CPU usage
    CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

    # Memory usage
    MEM=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')

    # Disk usage
    DISK=$(df /opt/vhs-upscaler | tail -1 | awk '{print $5}' | sed 's/%//')

    # GPU usage (if NVIDIA)
    if command -v nvidia-smi &> /dev/null; then
        GPU=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
        VRAM=$(nvidia-smi --query-gpu=utilization.memory --format=csv,noheader,nounits)
    else
        GPU=0
        VRAM=0
    fi

    # Queue size
    QUEUE=$(curl -s http://localhost:7860/api/queue_size || echo 0)

    echo "$TIMESTAMP,CPU:$CPU,MEM:$MEM,DISK:$DISK,GPU:$GPU,VRAM:$VRAM,QUEUE:$QUEUE" >> $LOG_FILE

    sleep 60  # Log every minute
done
```

**Enable Monitoring:**
```bash
chmod +x /opt/vhs-upscaler/monitor.sh
nohup /opt/vhs-upscaler/monitor.sh &
```

### 6.5 Alert Configuration

**Email Alerts (Simple):**
```bash
# Install mailutils
sudo apt install mailutils

# Configure alert script
cat > /opt/vhs-upscaler/alert.sh << 'EOF'
#!/bin/bash
ADMIN_EMAIL="admin@example.com"

# Check for errors in last hour
ERRORS=$(grep -c "ERROR" /opt/vhs-upscaler/logs/vhs-upscaler-error.log)

if [ $ERRORS -gt 10 ]; then
    echo "VHS Upscaler: $ERRORS errors in the last hour" | \
        mail -s "VHS Upscaler Alert" $ADMIN_EMAIL
fi
EOF

# Add to crontab (check every hour)
echo "0 * * * * /opt/vhs-upscaler/alert.sh" | crontab -
```

---

## 7. Backup and Disaster Recovery

### 7.1 Backup Strategy

**Components to Backup:**
- Configuration files (`config.yaml`, `.env`)
- Custom presets
- User data (if any)
- Database (if implemented)
- Application logs (last 7 days)

**Backup Script:**
```bash
#!/bin/bash
# /opt/vhs-upscaler/backup.sh

BACKUP_DIR="/opt/backups/vhs-upscaler"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/vhs-upscaler-$TIMESTAMP.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
tar -czf $BACKUP_FILE \
    /opt/vhs-upscaler/config.yaml \
    /opt/vhs-upscaler/.env \
    /opt/vhs-upscaler/vhs_upscaler/ \
    /opt/vhs-upscaler/logs/ \
    --exclude='*.pyc' \
    --exclude='__pycache__'

# Keep only last 7 backups
ls -t $BACKUP_DIR/*.tar.gz | tail -n +8 | xargs rm -f

echo "Backup completed: $BACKUP_FILE"
```

**Automated Backup Schedule:**
```bash
# Add to crontab (daily backup at 2 AM)
0 2 * * * /opt/vhs-upscaler/backup.sh >> /opt/vhs-upscaler/logs/backup.log 2>&1
```

### 7.2 Database Backup (If Applicable)

**SQLite Backup:**
```bash
# If using SQLite for job queue
sqlite3 /opt/vhs-upscaler/data/queue.db ".backup '/opt/backups/queue-$TIMESTAMP.db'"
```

**PostgreSQL Backup:**
```bash
# If using PostgreSQL
pg_dump -U vhsupscaler -d vhs_upscaler > /opt/backups/vhs-upscaler-$TIMESTAMP.sql
```

### 7.3 Disaster Recovery Procedures

**Recovery Steps:**

1. **Restore from Backup:**
```bash
# Extract backup
tar -xzf /opt/backups/vhs-upscaler-TIMESTAMP.tar.gz -C /opt/vhs-upscaler/

# Restore permissions
sudo chown -R vhsupscaler:vhsupscaler /opt/vhs-upscaler
```

2. **Reinstall Dependencies:**
```bash
cd /opt/vhs-upscaler
source venv/bin/activate
pip install -r requirements.txt
```

3. **Verify Configuration:**
```bash
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

4. **Restart Service:**
```bash
sudo systemctl start vhs-upscaler
sudo systemctl status vhs-upscaler
```

5. **Validate Functionality:**
```bash
# Run health check
curl http://localhost:7860/health

# Test processing
python -m vhs_upscaler.vhs_upscale -i test.mp4 -o test_out.mp4 --dry-run
```

### 7.4 Data Retention Policy

**Retention Guidelines:**
- **Application logs**: 30 days
- **Error logs**: 90 days
- **Performance metrics**: 6 months
- **Backups**: 7 daily, 4 weekly, 12 monthly
- **Temporary files**: Delete after job completion
- **Output files**: User-defined (not auto-deleted)

**Cleanup Script:**
```bash
#!/bin/bash
# /opt/vhs-upscaler/cleanup.sh

# Remove old logs (>30 days)
find /opt/vhs-upscaler/logs -name "*.log.*" -mtime +30 -delete

# Remove old temp files (>1 day)
find /opt/vhs-upscaler/temp -type f -mtime +1 -delete

# Remove empty directories
find /opt/vhs-upscaler/temp -type d -empty -delete

echo "Cleanup completed at $(date)"
```

---

## 8. Performance Optimization

### 8.1 System Tuning

**Linux Kernel Parameters:**
```bash
# /etc/sysctl.d/99-vhs-upscaler.conf

# Increase file descriptors
fs.file-max = 100000

# Network tuning for large file uploads
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864

# Virtual memory tuning
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# Apply settings
sudo sysctl -p /etc/sysctl.d/99-vhs-upscaler.conf
```

**Ulimit Configuration:**
```bash
# /etc/security/limits.conf

vhsupscaler soft nofile 65536
vhsupscaler hard nofile 65536
vhsupscaler soft nproc 32768
vhsupscaler hard nproc 32768
```

### 8.2 Application Tuning

**Optimize Worker Configuration:**
```yaml
# config.yaml

advanced:
  # Rule of thumb: (CPU cores / 2) - 1
  max_workers: 3  # For 8-core system

  # Keep temp files on fast SSD
  temp_dir: "/mnt/nvme/vhs-temp"

  # Use hardware encoding
  encoder: "hevc_nvenc"
```

**Python Performance:**
```bash
# Use faster Python interpreter (if available)
pip install uvloop  # Faster event loop

# Enable bytecode caching
export PYTHONOPTIMIZE=2

# Use faster JSON library
pip install orjson  # Replace json with orjson
```

### 8.3 FFmpeg Optimization

**Hardware-Accelerated Encoding:**
```yaml
# Optimal NVENC settings for quality/speed balance
defaults:
  encoder: "hevc_nvenc"
  nvenc_preset: "p5"  # Good balance (p1=fast, p7=slow)
  crf: 20

  # Enable B-frames for better compression
  nvenc_bframes: 4

  # Use hardware decoder
  hwaccel: "cuda"
```

**Multi-GPU Setup:**
```bash
# If multiple GPUs available
export CUDA_VISIBLE_DEVICES=0,1

# Load balance jobs across GPUs
# Modify queue_manager.py to assign GPU per job
```

### 8.4 Storage Optimization

**Use Fast Storage for Temp Files:**
```bash
# Mount NVMe SSD for temp directory
sudo mkdir /mnt/nvme
sudo mount /dev/nvme0n1 /mnt/nvme
sudo chown vhsupscaler:vhsupscaler /mnt/nvme

# Update config
sed -i 's|temp_dir:.*|temp_dir: "/mnt/nvme/vhs-temp"|' config.yaml
```

**Enable File System Optimizations:**
```bash
# Mount with noatime for temp filesystem
sudo mount -o remount,noatime /mnt/nvme

# Add to /etc/fstab
echo "/dev/nvme0n1 /mnt/nvme ext4 defaults,noatime 0 2" | sudo tee -a /etc/fstab
```

### 8.5 Network Optimization

**Gradio Server Tuning:**
```python
# Modify gui.py launch configuration

demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    max_threads=40,  # Increase concurrent connections
    ssl_verify=False,

    # Enable compression
    compress=True,

    # Optimize for large file uploads
    max_file_size=10 * 1024 * 1024 * 1024,  # 10GB
)
```

---

## 9. Security Hardening

### 9.1 Application Security

**Input Validation:**
```python
# Add to vhs_upscale.py

import re
from pathlib import Path

def validate_file_path(file_path: str) -> Path:
    """Validate and sanitize file paths to prevent path traversal."""
    path = Path(file_path).resolve()

    # Ensure path doesn't escape allowed directories
    allowed_dirs = [Path('/opt/vhs-upscaler/uploads'), Path('/opt/vhs-upscaler/output')]
    if not any(str(path).startswith(str(d)) for d in allowed_dirs):
        raise ValueError(f"Invalid file path: {file_path}")

    # Check for suspicious patterns
    if '..' in str(path) or path.name.startswith('.'):
        raise ValueError(f"Suspicious file path: {file_path}")

    return path

def sanitize_filename(filename: str) -> str:
    """Remove potentially dangerous characters from filename."""
    # Remove all non-alphanumeric except .-_
    safe_name = re.sub(r'[^\w\s.-]', '', filename)
    safe_name = safe_name.replace(' ', '_')
    return safe_name
```

**Command Injection Prevention:**
```python
# Always use list format for subprocess calls
# GOOD:
subprocess.run(["ffmpeg", "-i", user_input, "output.mp4"])

# BAD - DO NOT USE:
# subprocess.run(f"ffmpeg -i {user_input} output.mp4", shell=True)
```

### 9.2 Authentication and Authorization

**Basic Authentication (Gradio):**
```python
# Modify gui.py

def authenticate(username, password):
    """Simple authentication check."""
    valid_users = {
        "admin": os.getenv("ADMIN_PASSWORD"),
        "user": os.getenv("USER_PASSWORD")
    }
    return valid_users.get(username) == password

# Add to launch
demo.launch(
    auth=authenticate,
    auth_message="VHS Upscaler - Please log in"
)
```

**OAuth2 Integration (Advanced):**
```python
# Use Gradio OAuth support
demo.launch(
    oauth_client_id=os.getenv("OAUTH_CLIENT_ID"),
    oauth_client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
    oauth_scopes="openid profile email"
)
```

### 9.3 File Upload Security

**Restrict File Types:**
```python
# Modify gui.py upload handler

ALLOWED_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'}
MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10GB

def validate_upload(file):
    """Validate uploaded file."""
    path = Path(file.name)

    # Check extension
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type not allowed: {path.suffix}")

    # Check file size
    file_size = os.path.getsize(file.name)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {file_size / 1024**3:.2f}GB")

    # Verify file is actually a video (using ffprobe)
    result = subprocess.run(
        ["ffprobe", "-v", "error", file.name],
        capture_output=True
    )
    if result.returncode != 0:
        raise ValueError("Invalid video file")

    return True
```

**Scan for Malware:**
```bash
# Install ClamAV
sudo apt install clamav clamav-daemon

# Update virus definitions
sudo freshclam

# Create scan script
cat > /opt/vhs-upscaler/scan_upload.sh << 'EOF'
#!/bin/bash
FILE=$1
clamscan --no-summary "$FILE"
if [ $? -ne 0 ]; then
    echo "Malware detected in $FILE"
    rm "$FILE"
    exit 1
fi
EOF
chmod +x /opt/vhs-upscaler/scan_upload.sh
```

### 9.4 Rate Limiting

**Implement Rate Limiting:**
```python
# Add to gui.py

from functools import wraps
from time import time
from collections import defaultdict

class RateLimiter:
    """Simple rate limiter."""
    def __init__(self, max_calls=10, period=60):
        self.max_calls = max_calls
        self.period = period
        self.calls = defaultdict(list)

    def is_allowed(self, key):
        """Check if request is allowed."""
        now = time()
        # Remove old calls
        self.calls[key] = [t for t in self.calls[key] if now - t < self.period]

        if len(self.calls[key]) >= self.max_calls:
            return False

        self.calls[key].append(now)
        return True

rate_limiter = RateLimiter(max_calls=10, period=60)  # 10 calls per minute

def rate_limit(func):
    """Rate limiting decorator."""
    @wraps(func)
    def wrapper(request: gr.Request, *args, **kwargs):
        client_ip = request.client.host
        if not rate_limiter.is_allowed(client_ip):
            raise gr.Error("Rate limit exceeded. Please try again later.")
        return func(*args, **kwargs)
    return wrapper

# Apply to upload function
@rate_limit
def upload_video(request: gr.Request, video_file):
    # ... upload logic
    pass
```

### 9.5 Security Headers

**Configure Security Headers (Nginx):**
```nginx
# Add to nginx configuration

add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 9.6 Secrets Management

**Use Environment Variables:**
```bash
# Never hardcode secrets
# BAD:
# API_KEY = "sk-1234567890abcdef"

# GOOD:
API_KEY = os.getenv("VHS_API_KEY")

# Use .env file (add to .gitignore)
cat > .env << EOF
VHS_SECRET_KEY=$(openssl rand -hex 32)
VHS_DATABASE_PASSWORD=$(openssl rand -base64 32)
EOF

# Load in application
from dotenv import load_dotenv
load_dotenv()
```

**Encrypt Sensitive Configuration:**
```bash
# Encrypt config.yaml
openssl enc -aes-256-cbc -salt -in config.yaml -out config.yaml.enc

# Decrypt at runtime
openssl enc -d -aes-256-cbc -in config.yaml.enc -out config.yaml
```

---

## 10. Post-Deployment Validation

### 10.1 Smoke Tests

**Basic Functionality Tests:**
```bash
#!/bin/bash
# /opt/vhs-upscaler/smoke_test.sh

echo "=== VHS Upscaler Smoke Tests ==="

# Test 1: Check service is running
echo "Test 1: Service status"
systemctl is-active vhs-upscaler || exit 1
echo "✓ Service running"

# Test 2: Check web interface responds
echo "Test 2: Web interface"
curl -f http://localhost:7860/ > /dev/null || exit 1
echo "✓ Web interface accessible"

# Test 3: Check FFmpeg
echo "Test 3: FFmpeg availability"
ffmpeg -version > /dev/null || exit 1
echo "✓ FFmpeg working"

# Test 4: Check GPU (if applicable)
echo "Test 4: GPU detection"
if nvidia-smi > /dev/null 2>&1; then
    echo "✓ NVIDIA GPU detected"
else
    echo "ℹ No NVIDIA GPU (CPU mode)"
fi

# Test 5: Configuration valid
echo "Test 5: Configuration"
python -c "import yaml; yaml.safe_load(open('/opt/vhs-upscaler/config.yaml'))" || exit 1
echo "✓ Configuration valid"

# Test 6: Dry run test
echo "Test 6: Dry run processing"
python -m vhs_upscaler.vhs_upscale -i /opt/vhs-upscaler/tests/sample.mp4 -o /tmp/test.mp4 --dry-run || exit 1
echo "✓ Dry run successful"

echo ""
echo "=== All smoke tests passed ==="
```

### 10.2 Integration Tests

**End-to-End Processing Test:**
```bash
#!/bin/bash
# Test full processing pipeline

TEST_VIDEO="/opt/vhs-upscaler/tests/sample_vhs.mp4"
OUTPUT_DIR="/opt/vhs-upscaler/output/validation"

mkdir -p $OUTPUT_DIR

# Test 1: Basic upscale
echo "Testing basic upscale..."
python -m vhs_upscaler.vhs_upscale \
    -i $TEST_VIDEO \
    -o $OUTPUT_DIR/test_basic.mp4 \
    --preset vhs \
    --resolution 1080

# Verify output exists and is valid
if ffprobe $OUTPUT_DIR/test_basic.mp4 2>&1 | grep -q "1920x1080"; then
    echo "✓ Basic upscale successful"
else
    echo "✗ Basic upscale failed"
    exit 1
fi

# Test 2: Batch processing
echo "Testing batch mode..."
python -m vhs_upscaler.cli.batch \
    -i /opt/vhs-upscaler/tests/ \
    -o $OUTPUT_DIR/batch/ \
    --preset vhs

# Test 3: Audio enhancement
echo "Testing audio enhancement..."
python -m vhs_upscaler.vhs_upscale \
    -i $TEST_VIDEO \
    -o $OUTPUT_DIR/test_audio.mp4 \
    --audio-enhance moderate \
    --audio-upmix surround

echo "All integration tests passed"
```

### 10.3 Performance Validation

**Benchmark Performance:**
```bash
#!/bin/bash
# Benchmark processing performance

TEST_VIDEO="/opt/vhs-upscaler/tests/benchmark_vhs.mp4"  # 1 minute 480p video

echo "=== Performance Benchmark ==="

# Benchmark 1: Maxine upscaling
echo "Benchmark 1: NVIDIA Maxine"
time python -m vhs_upscaler.vhs_upscale \
    -i $TEST_VIDEO \
    -o /tmp/bench_maxine.mp4 \
    --engine maxine \
    --resolution 1080 \
    2>&1 | grep "real"

# Benchmark 2: Real-ESRGAN upscaling
echo "Benchmark 2: Real-ESRGAN"
time python -m vhs_upscaler.vhs_upscale \
    -i $TEST_VIDEO \
    -o /tmp/bench_realesrgan.mp4 \
    --engine realesrgan \
    --resolution 1080 \
    2>&1 | grep "real"

# Benchmark 3: FFmpeg upscaling
echo "Benchmark 3: FFmpeg"
time python -m vhs_upscaler.vhs_upscale \
    -i $TEST_VIDEO \
    -o /tmp/bench_ffmpeg.mp4 \
    --engine ffmpeg \
    --resolution 1080 \
    2>&1 | grep "real"

# Compare file sizes
echo ""
echo "Output file sizes:"
ls -lh /tmp/bench_*.mp4 | awk '{print $9, $5}'

# Cleanup
rm /tmp/bench_*.mp4
```

**Expected Performance:**
- Maxine: 30-60 fps processing speed (1 min video in 1-2 mins)
- Real-ESRGAN: 10-30 fps (1 min video in 2-6 mins)
- FFmpeg: Variable (depends on CPU)

### 10.4 Resource Usage Validation

**Monitor Resource Usage:**
```bash
#!/bin/bash
# Monitor resources during processing

echo "Starting resource monitoring..."

# Start monitoring in background
(
    while true; do
        echo "$(date +%H:%M:%S) CPU:$(top -bn1 | grep Cpu | awk '{print $2}')% MEM:$(free | grep Mem | awk '{print ($3/$2)*100}')% GPU:$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader)%"
        sleep 5
    done
) > /tmp/resource_monitor.log &

MONITOR_PID=$!

# Run test job
python -m vhs_upscaler.vhs_upscale -i test.mp4 -o output.mp4

# Stop monitoring
kill $MONITOR_PID

# Analyze results
echo "Resource usage during processing:"
cat /tmp/resource_monitor.log
```

### 10.5 Security Validation

**Security Checklist:**
```bash
#!/bin/bash
# Security validation checks

echo "=== Security Validation ==="

# Check 1: No exposed secrets
echo "Checking for exposed secrets..."
if grep -r "password\|secret\|key" vhs_upscaler/*.py --exclude="*.pyc" | grep -v "os.getenv"; then
    echo "✗ WARNING: Potential exposed secrets found"
else
    echo "✓ No hardcoded secrets found"
fi

# Check 2: File permissions
echo "Checking file permissions..."
if find /opt/vhs-upscaler -type f -perm /o+w | grep -q .; then
    echo "✗ WARNING: World-writable files found"
else
    echo "✓ File permissions correct"
fi

# Check 3: Firewall rules
echo "Checking firewall..."
if ufw status | grep -q "7860.*ALLOW"; then
    echo "✓ Firewall configured"
else
    echo "ℹ Firewall not configured or disabled"
fi

# Check 4: SSL certificate (if using HTTPS)
echo "Checking SSL certificate..."
if [ -f "/etc/letsencrypt/live/vhs-upscaler.example.com/fullchain.pem" ]; then
    EXPIRY=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/vhs-upscaler.example.com/fullchain.pem | cut -d= -f2)
    echo "✓ SSL certificate valid until $EXPIRY"
else
    echo "ℹ No SSL certificate found"
fi

echo ""
echo "=== Security validation complete ==="
```

---

## 11. Rollback Procedures

### 11.1 Prepare for Rollback

**Pre-Deployment Snapshot:**
```bash
# Create snapshot before deployment
rsync -av /opt/vhs-upscaler/ /opt/vhs-upscaler-backup-$(date +%Y%m%d)/

# Or use git tags
cd /opt/vhs-upscaler
git tag -a rollback-$(date +%Y%m%d) -m "Pre-deployment snapshot"
git push origin --tags
```

### 11.2 Rollback Steps

**Full Rollback Procedure:**
```bash
#!/bin/bash
# /opt/vhs-upscaler/rollback.sh

set -e

BACKUP_DIR="/opt/vhs-upscaler-backup-20231218"  # Update with actual backup date

echo "=== Starting Rollback ==="

# Step 1: Stop service
echo "Stopping service..."
sudo systemctl stop vhs-upscaler

# Step 2: Backup current version (in case rollback fails)
echo "Backing up current version..."
mv /opt/vhs-upscaler /opt/vhs-upscaler-failed-$(date +%Y%m%d_%H%M%S)

# Step 3: Restore from backup
echo "Restoring from backup..."
cp -r $BACKUP_DIR /opt/vhs-upscaler

# Step 4: Restore virtual environment
echo "Reinstalling dependencies..."
cd /opt/vhs-upscaler
source venv/bin/activate
pip install -r requirements.txt

# Step 5: Restore configuration
echo "Restoring configuration..."
# Config already restored in step 3

# Step 6: Verify installation
echo "Verifying installation..."
python -c "import vhs_upscaler; print(vhs_upscaler.__version__)"

# Step 7: Restart service
echo "Restarting service..."
sudo systemctl start vhs-upscaler

# Step 8: Health check
echo "Running health check..."
sleep 5
curl -f http://localhost:7860/ || {
    echo "✗ Rollback failed - service not responding"
    exit 1
}

echo "✓ Rollback completed successfully"
```

### 11.3 Git-Based Rollback

**Rollback to Previous Version:**
```bash
# List recent tags
git tag -l --sort=-v:refname | head

# Rollback to specific version
cd /opt/vhs-upscaler
git checkout v1.4.1  # Previous stable version

# Reinstall dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart vhs-upscaler
```

### 11.4 Database Rollback (If Applicable)

**Restore Database:**
```bash
# SQLite
cp /opt/backups/queue-20231218.db /opt/vhs-upscaler/data/queue.db

# PostgreSQL
psql -U vhsupscaler -d vhs_upscaler < /opt/backups/vhs-upscaler-20231218.sql
```

### 11.5 Verify Rollback

**Post-Rollback Validation:**
```bash
# Run smoke tests
/opt/vhs-upscaler/smoke_test.sh

# Check version
python -c "import vhs_upscaler; print(vhs_upscaler.__version__)"

# Verify functionality
python -m vhs_upscaler.vhs_upscale -i test.mp4 -o output.mp4 --dry-run
```

---

## 12. User Acceptance Testing

### 12.1 UAT Test Plan

**Test Scenarios:**

**Scenario 1: Basic Video Upload and Processing**
1. Navigate to web interface
2. Upload VHS video file (drag and drop)
3. Select preset: VHS
4. Select resolution: 1080p
5. Click "Add to Queue"
6. Verify job appears in queue
7. Monitor progress
8. Download completed video
9. Verify output quality

**Expected Results:**
- Upload completes without errors
- Progress bar updates in real-time
- Processing completes successfully
- Output file is valid and playable
- Resolution matches selection (1920x1080)

**Scenario 2: Batch Processing**
1. Select multiple video files
2. Configure same settings for all
3. Add all to queue
4. Verify all jobs queued
5. Monitor parallel processing
6. Verify all outputs

**Expected Results:**
- All files queue successfully
- Jobs process in order
- No jobs fail
- All outputs valid

**Scenario 3: Advanced Features**
1. Upload video
2. Enable audio enhancement
3. Enable surround upmix
4. Select HDR output
5. Process video
6. Verify audio enhancement applied
7. Verify surround sound channels
8. Verify HDR metadata

**Expected Results:**
- Audio quality improved
- 5.1 surround audio track present
- HDR metadata in output file

### 12.2 UAT Checklist

**Functional Tests:**
- [ ] Video upload works (drag & drop and file picker)
- [ ] All presets selectable
- [ ] Resolution selection works
- [ ] Engine auto-detection works
- [ ] Queue management (add/pause/resume/cancel)
- [ ] Progress tracking accurate
- [ ] Download completed files
- [ ] Error messages clear and helpful
- [ ] Dark mode toggle works

**Performance Tests:**
- [ ] Processing speed meets expectations
- [ ] Multiple concurrent jobs work
- [ ] Large file uploads (>5GB) work
- [ ] No memory leaks during long processing
- [ ] GPU utilization optimal

**Quality Tests:**
- [ ] Output video quality acceptable
- [ ] No visual artifacts introduced
- [ ] Audio sync maintained
- [ ] Correct resolution output
- [ ] File size reasonable

**Usability Tests:**
- [ ] Interface intuitive
- [ ] Error messages helpful
- [ ] Progress information clear
- [ ] Settings easy to understand
- [ ] Help documentation accessible

### 12.3 UAT Test Data

**Sample Test Videos:**
```
/opt/vhs-upscaler/tests/uat/
├── vhs_sample_1min.mp4      # 1 minute VHS footage
├── dvd_sample_5min.mp4      # 5 minute DVD footage
├── large_file_10gb.mp4      # Large file test
├── audio_test.mp4           # Audio quality test
└── batch_test/              # 10 small files for batch testing
    ├── file1.mp4
    ├── file2.mp4
    └── ...
```

### 12.4 UAT Acceptance Criteria

**Must Have (Blocker if not met):**
- [ ] All core processing functions work
- [ ] No data loss during processing
- [ ] No security vulnerabilities
- [ ] Performance within acceptable range (not slower than 50% vs previous version)
- [ ] Critical bugs: 0

**Should Have (Important but not blocking):**
- [ ] All optional features work
- [ ] UI responsive and fast
- [ ] Minor bugs: <3
- [ ] Documentation complete

**Nice to Have:**
- [ ] Advanced features (HDR, AI audio)
- [ ] Performance optimizations
- [ ] UI polish

### 12.5 UAT Sign-Off

**Sign-Off Checklist:**
- [ ] All test scenarios executed
- [ ] All acceptance criteria met
- [ ] Performance benchmarks achieved
- [ ] Security review passed
- [ ] Documentation reviewed and approved
- [ ] Training completed (if applicable)
- [ ] Stakeholder approval obtained

**Sign-Off Document:**
```
UAT Sign-Off - VHS Upscaler v1.4.2

Project: VHS Upscaler Production Deployment
Version: 1.4.2
Date: 2023-12-18

Test Summary:
- Total test scenarios: 25
- Passed: 24
- Failed: 0
- Blocked: 1 (known issue, documented)

Critical Issues: None
Known Issues: [List any known issues with workarounds]

Performance:
- Processing speed: Meets requirements
- Resource usage: Within limits
- Scalability: Tested up to 10 concurrent jobs

Security:
- Security audit: Passed
- Penetration testing: Not applicable
- Vulnerability scan: No critical issues

Recommendation: APPROVED FOR PRODUCTION

Signatures:
- Product Owner: _________________ Date: _______
- Technical Lead: ________________ Date: _______
- QA Lead: ______________________ Date: _______
```

---

## Appendix A: Systemd Service Configuration

**Create Service File:**
```ini
# /etc/systemd/system/vhs-upscaler.service

[Unit]
Description=VHS Upscaler Web Interface
After=network.target

[Service]
Type=simple
User=vhsupscaler
Group=vhsupscaler
WorkingDirectory=/opt/vhs-upscaler
Environment="PATH=/opt/vhs-upscaler/venv/bin"
Environment="VHS_OUTPUT_DIR=/opt/vhs-upscaler/output"
Environment="VHS_LOG_DIR=/opt/vhs-upscaler/logs"
ExecStart=/opt/vhs-upscaler/venv/bin/python -m vhs_upscaler.gui
Restart=always
RestartSec=10
StandardOutput=append:/opt/vhs-upscaler/logs/service.log
StandardError=append:/opt/vhs-upscaler/logs/service-error.log

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/vhs-upscaler

[Install]
WantedBy=multi-user.target
```

**Enable and Start Service:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable vhs-upscaler

# Start service
sudo systemctl start vhs-upscaler

# Check status
sudo systemctl status vhs-upscaler

# View logs
sudo journalctl -u vhs-upscaler -f
```

---

## Appendix B: Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `VHS_OUTPUT_DIR` | Output directory for processed videos | `./output` | No |
| `VHS_TEMP_DIR` | Temporary files directory | System temp | No |
| `VHS_LOG_DIR` | Log files directory | `./logs` | No |
| `VHS_LOG_LEVEL` | Logging level | `INFO` | No |
| `MAXINE_HOME` | NVIDIA Maxine SDK path | Auto-detect | No |
| `MAXINE_MODEL_DIR` | Maxine models directory | `$MAXINE_HOME/bin/models` | No |
| `CUDA_VISIBLE_DEVICES` | GPU selection | All GPUs | No |
| `GRADIO_SERVER_PORT` | Web interface port | `7860` | No |
| `GRADIO_SERVER_NAME` | Bind address | `127.0.0.1` | No |
| `GRADIO_ANALYTICS_ENABLED` | Gradio analytics | `false` | No |
| `VHS_SECRET_KEY` | Session secret key | Auto-generated | No |
| `VHS_MAX_UPLOAD_SIZE` | Max upload file size (bytes) | `10737418240` | No |

---

## Appendix C: Troubleshooting

**Common Issues:**

**Issue 1: Service won't start**
```bash
# Check logs
sudo journalctl -u vhs-upscaler -n 50

# Check permissions
ls -la /opt/vhs-upscaler
sudo chown -R vhsupscaler:vhsupscaler /opt/vhs-upscaler

# Test manual start
sudo -u vhsupscaler /opt/vhs-upscaler/venv/bin/python -m vhs_upscaler.gui
```

**Issue 2: GPU not detected**
```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA
nvcc --version

# Test FFmpeg NVENC
ffmpeg -codecs | grep nvenc
```

**Issue 3: Out of disk space**
```bash
# Check disk usage
df -h /opt/vhs-upscaler

# Clean temp files
rm -rf /opt/vhs-upscaler/temp/*

# Clean old logs
find /opt/vhs-upscaler/logs -name "*.log.*" -mtime +7 -delete
```

---

**Document Version:** 1.0
**Last Updated:** 2023-12-18
**Author:** DevOps Engineering Team
**Status:** Production Ready
