# Production Deployment - Quick Reference

## Pre-Deployment (15 min)

```bash
# Run tests
pytest tests/ -v --cov=vhs_upscaler
# Target: >90% coverage, 0 failures

# Code quality
black vhs_upscaler/ tests/ --check --line-length 100
ruff check vhs_upscaler/ tests/
# Target: 0 errors

# Security scan
bandit -r vhs_upscaler/ -ll
pip-audit
# Target: 0 critical issues

# Tag release
git tag -a v1.4.2 -m "Production release v1.4.2"
git push origin v1.4.2
```

**Checklist:**
- [ ] All tests passing
- [ ] Code quality checks pass
- [ ] No security vulnerabilities
- [ ] Documentation updated
- [ ] Version tagged in git

---

## System Setup (30 min)

### Linux Production Server

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev \
    build-essential ffmpeg libsm6 libxext6

# Create app user
sudo useradd -m -s /bin/bash vhsupscaler
sudo usermod -aG video vhsupscaler

# Create directories
sudo mkdir -p /opt/vhs-upscaler/{output,temp,logs,uploads}
sudo chown -R vhsupscaler:vhsupscaler /opt/vhs-upscaler
```

### Application Install

```bash
# Clone repository
cd /opt/vhs-upscaler
git clone https://github.com/parthalon025/terminalai.git .
git checkout v1.4.2

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install application
pip install --upgrade pip
pip install -e .

# Verify installation
python -c "import vhs_upscaler; print(vhs_upscaler.__version__)"
# Expected: 1.4.2
```

**Checklist:**
- [ ] Python 3.10+ installed
- [ ] FFmpeg installed
- [ ] Virtual environment created
- [ ] Application installed
- [ ] Version verified

---

## Configuration (10 min)

### Create Production Config

```bash
# Copy and edit config
cp vhs_upscaler/config.yaml /opt/vhs-upscaler/config.yaml
nano /opt/vhs-upscaler/config.yaml
```

**Key Settings:**
```yaml
ffmpeg_path: "/usr/bin/ffmpeg"
maxine_path: "/opt/NVIDIA/Maxine/bin"  # If using Maxine

defaults:
  encoder: "hevc_nvenc"  # or "libx265" for CPU
  nvenc_preset: "p7"
  crf: 20

advanced:
  max_workers: 2  # Adjust per server
  log_level: "INFO"
  keep_temp: false
```

### Environment Variables

```bash
# Create .env file
cat > /opt/vhs-upscaler/.env << EOF
VHS_OUTPUT_DIR=/opt/vhs-upscaler/output
VHS_TEMP_DIR=/opt/vhs-upscaler/temp
VHS_LOG_DIR=/opt/vhs-upscaler/logs
GRADIO_SERVER_PORT=7860
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_ANALYTICS_ENABLED=false
MAXINE_HOME=/opt/NVIDIA/Maxine
EOF

# Load environment
source /opt/vhs-upscaler/.env
```

**Checklist:**
- [ ] config.yaml configured
- [ ] .env file created
- [ ] Directories exist
- [ ] Permissions correct

---

## GPU Setup (Optional, 15 min)

### NVIDIA Driver (Required for GPU)

```bash
# Install driver (Ubuntu)
sudo apt install -y nvidia-driver-535
sudo reboot

# Verify
nvidia-smi
# Check: Driver Version 535+ shown
```

### NVIDIA Maxine (Optional, Best Quality)

```bash
# Download from: https://developer.nvidia.com/maxine-getting-started

# Install
sudo mkdir -p /opt/NVIDIA/Maxine
sudo unzip Maxine_VideoEffects_SDK.zip -d /opt/NVIDIA/Maxine/

# Verify
ls -la /opt/NVIDIA/Maxine/bin/VideoEffectsApp
```

### Real-ESRGAN (Alternative)

```bash
# Download
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip

# Install
sudo unzip realesrgan-ncnn-vulkan-20220424-ubuntu.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/realesrgan-ncnn-vulkan

# Verify
realesrgan-ncnn-vulkan --help
```

**Checklist:**
- [ ] NVIDIA driver installed (GPU systems)
- [ ] GPU detected with nvidia-smi
- [ ] Maxine or Real-ESRGAN installed (optional)

---

## Network Configuration (10 min)

### Firewall

```bash
# Allow web interface port
sudo ufw allow 7860/tcp
sudo ufw enable
sudo ufw status
```

### Nginx Reverse Proxy (Optional)

```nginx
# /etc/nginx/sites-available/vhs-upscaler
upstream vhs_upscaler {
    server 127.0.0.1:7860;
}

server {
    listen 80;
    server_name vhs-upscaler.example.com;

    client_max_body_size 10G;
    client_body_timeout 3600s;
    proxy_read_timeout 3600s;

    location / {
        proxy_pass http://vhs_upscaler;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable
sudo ln -s /etc/nginx/sites-available/vhs-upscaler /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Checklist:**
- [ ] Port 7860 accessible
- [ ] Firewall configured
- [ ] Reverse proxy configured (if needed)

---

## Systemd Service (5 min)

### Create Service

```bash
sudo nano /etc/systemd/system/vhs-upscaler.service
```

```ini
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

[Install]
WantedBy=multi-user.target
```

### Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable vhs-upscaler
sudo systemctl start vhs-upscaler
sudo systemctl status vhs-upscaler
```

**Checklist:**
- [ ] Service file created
- [ ] Service enabled
- [ ] Service running
- [ ] Status shows "active (running)"

---

## Post-Deployment Validation (10 min)

### Smoke Tests

```bash
# Service running
systemctl is-active vhs-upscaler

# Web interface accessible
curl -f http://localhost:7860/

# FFmpeg working
ffmpeg -version

# GPU detected (if applicable)
nvidia-smi

# Configuration valid
python -c "import yaml; yaml.safe_load(open('/opt/vhs-upscaler/config.yaml'))"

# Dry run test
python -m vhs_upscaler.vhs_upscale -i test.mp4 -o /tmp/test.mp4 --dry-run
```

### Functional Test

```bash
# Process test video
python -m vhs_upscaler.vhs_upscale \
    -i /opt/vhs-upscaler/tests/sample.mp4 \
    -o /opt/vhs-upscaler/output/test_output.mp4 \
    --preset vhs \
    --resolution 1080

# Verify output
ffprobe /opt/vhs-upscaler/output/test_output.mp4 | grep "1920x1080"
```

**Checklist:**
- [ ] All smoke tests pass
- [ ] Test video processes successfully
- [ ] Output video valid
- [ ] Logs show no errors

---

## Monitoring Setup (15 min)

### Log Rotation

```bash
sudo nano /etc/logrotate.d/vhs-upscaler
```

```
/opt/vhs-upscaler/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 vhsupscaler vhsupscaler
}
```

### Performance Monitoring

```bash
# Create monitoring script
cat > /opt/vhs-upscaler/monitor.sh << 'EOF'
#!/bin/bash
while true; do
    echo "$(date '+%Y-%m-%d %H:%M:%S'),CPU:$(top -bn1 | grep Cpu | awk '{print $2}'),MEM:$(free | grep Mem | awk '{print ($3/$2)*100}'),GPU:$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null || echo 0)" >> /opt/vhs-upscaler/logs/performance.log
    sleep 60
done
EOF
chmod +x /opt/vhs-upscaler/monitor.sh

# Start monitoring
nohup /opt/vhs-upscaler/monitor.sh &
```

### Disk Space Alert

```bash
cat > /opt/vhs-upscaler/disk_alert.sh << 'EOF'
#!/bin/bash
THRESHOLD=90
USAGE=$(df /opt/vhs-upscaler | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $USAGE -gt $THRESHOLD ]; then
    echo "WARNING: Disk usage at ${USAGE}%" | mail -s "VHS Upscaler Disk Alert" admin@example.com
fi
EOF
chmod +x /opt/vhs-upscaler/disk_alert.sh

# Add to crontab
echo "0 * * * * /opt/vhs-upscaler/disk_alert.sh" | crontab -
```

**Checklist:**
- [ ] Log rotation configured
- [ ] Performance monitoring running
- [ ] Disk space alerts configured

---

## Backup Setup (10 min)

### Automated Backup

```bash
cat > /opt/vhs-upscaler/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/vhs-upscaler"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

tar -czf $BACKUP_DIR/vhs-upscaler-$TIMESTAMP.tar.gz \
    /opt/vhs-upscaler/config.yaml \
    /opt/vhs-upscaler/.env \
    /opt/vhs-upscaler/vhs_upscaler/ \
    --exclude='*.pyc' --exclude='__pycache__'

ls -t $BACKUP_DIR/*.tar.gz | tail -n +8 | xargs rm -f
EOF
chmod +x /opt/vhs-upscaler/backup.sh

# Schedule daily backup
echo "0 2 * * * /opt/vhs-upscaler/backup.sh" | crontab -
```

**Checklist:**
- [ ] Backup script created
- [ ] Backup scheduled in crontab
- [ ] Backup directory exists

---

## Security Hardening (20 min)

### File Permissions

```bash
# Restrict config file
chmod 600 /opt/vhs-upscaler/config.yaml
chmod 600 /opt/vhs-upscaler/.env

# Restrict temp directory
chmod 700 /opt/vhs-upscaler/temp
```

### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 7860/tcp  # VHS Upscaler
sudo ufw enable
```

### Rate Limiting (Application Level)

Add to `gui.py`:
```python
from functools import wraps
from time import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_calls=10, period=60):
        self.max_calls = max_calls
        self.period = period
        self.calls = defaultdict(list)

    def is_allowed(self, key):
        now = time()
        self.calls[key] = [t for t in self.calls[key] if now - t < self.period]
        if len(self.calls[key]) >= self.max_calls:
            return False
        self.calls[key].append(now)
        return True

rate_limiter = RateLimiter(max_calls=10, period=60)
```

### Input Validation

Ensure all file paths validated:
```python
def validate_file_path(file_path: str) -> Path:
    path = Path(file_path).resolve()
    if '..' in str(path):
        raise ValueError("Path traversal not allowed")
    return path
```

**Checklist:**
- [ ] File permissions restricted
- [ ] Firewall configured
- [ ] Rate limiting implemented
- [ ] Input validation added
- [ ] No exposed secrets

---

## Rollback Plan (5 min)

### Quick Rollback

```bash
# Stop service
sudo systemctl stop vhs-upscaler

# Restore from backup
BACKUP_DATE="20231218"  # Update with actual date
tar -xzf /opt/backups/vhs-upscaler/vhs-upscaler-$BACKUP_DATE*.tar.gz -C /

# Reinstall dependencies
cd /opt/vhs-upscaler
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl start vhs-upscaler
```

### Git-Based Rollback

```bash
cd /opt/vhs-upscaler
git checkout v1.4.1  # Previous version
pip install -r requirements.txt
sudo systemctl restart vhs-upscaler
```

**Checklist:**
- [ ] Backup exists
- [ ] Rollback procedure tested
- [ ] Previous version tagged

---

## Performance Optimization (15 min)

### System Tuning

```bash
# Increase file descriptors
echo "fs.file-max = 100000" | sudo tee -a /etc/sysctl.conf

# Virtual memory tuning
echo "vm.swappiness = 10" | sudo tee -a /etc/sysctl.conf
echo "vm.dirty_ratio = 15" | sudo tee -a /etc/sysctl.conf

# Apply
sudo sysctl -p
```

### Application Tuning

```yaml
# config.yaml
advanced:
  max_workers: 2  # (CPU cores / 2) - 1
  keep_temp: false
  intermediate_crf: 15

defaults:
  encoder: "hevc_nvenc"  # Hardware encoding
  nvenc_preset: "p5"     # Balance quality/speed
```

### Storage Optimization

```bash
# Use fast storage for temp
sudo mkdir /mnt/nvme/vhs-temp
sudo chown vhsupscaler:vhsupscaler /mnt/nvme/vhs-temp
sudo mount -o noatime /mnt/nvme

# Update config
sed -i 's|VHS_TEMP_DIR=.*|VHS_TEMP_DIR=/mnt/nvme/vhs-temp|' /opt/vhs-upscaler/.env
```

**Checklist:**
- [ ] System parameters tuned
- [ ] Worker count optimized
- [ ] Hardware encoding enabled
- [ ] Fast storage configured

---

## Common Commands

### Service Management

```bash
# Status
sudo systemctl status vhs-upscaler

# Logs
sudo journalctl -u vhs-upscaler -f

# Restart
sudo systemctl restart vhs-upscaler

# Stop
sudo systemctl stop vhs-upscaler
```

### Monitoring

```bash
# Check service
curl http://localhost:7860/

# GPU status
nvidia-smi

# Resource usage
htop

# Disk space
df -h /opt/vhs-upscaler

# Recent errors
tail -f /opt/vhs-upscaler/logs/vhs-upscaler-error.log
```

### Maintenance

```bash
# Clean temp files
rm -rf /opt/vhs-upscaler/temp/*

# Clean old logs
find /opt/vhs-upscaler/logs -name "*.log.*" -mtime +30 -delete

# Rotate logs
sudo logrotate -f /etc/logrotate.d/vhs-upscaler

# Update application
cd /opt/vhs-upscaler
git pull
pip install -r requirements.txt
sudo systemctl restart vhs-upscaler
```

---

## Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u vhs-upscaler -n 50

# Check permissions
ls -la /opt/vhs-upscaler
sudo chown -R vhsupscaler:vhsupscaler /opt/vhs-upscaler

# Test manual start
sudo -u vhsupscaler /opt/vhs-upscaler/venv/bin/python -m vhs_upscaler.gui
```

### GPU not detected

```bash
# Check driver
nvidia-smi

# Check NVENC
ffmpeg -codecs | grep nvenc

# Reload driver
sudo modprobe -r nvidia_uvm nvidia_drm nvidia_modeset nvidia
sudo modprobe nvidia nvidia_modeset nvidia_drm nvidia_uvm
```

### Out of disk space

```bash
# Check usage
df -h /opt/vhs-upscaler

# Clean temp
rm -rf /opt/vhs-upscaler/temp/*

# Clean logs
find /opt/vhs-upscaler/logs -name "*.log.*" -mtime +7 -delete
```

### Port already in use

```bash
# Find process using port
sudo lsof -i :7860

# Kill process
sudo kill -9 <PID>

# Or change port in .env
echo "GRADIO_SERVER_PORT=7861" >> /opt/vhs-upscaler/.env
```

---

## Deployment Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Pre-Deployment** | 15 min | Tests, security scan, version tag |
| **System Setup** | 30 min | Install dependencies, create user |
| **Application Install** | 15 min | Clone, install, verify |
| **Configuration** | 10 min | Config files, environment vars |
| **GPU Setup** | 15 min | Driver, Maxine/Real-ESRGAN |
| **Network Config** | 10 min | Firewall, reverse proxy |
| **Service Setup** | 5 min | Systemd service |
| **Validation** | 10 min | Smoke tests, functional tests |
| **Monitoring** | 15 min | Logs, performance, alerts |
| **Backup** | 10 min | Backup scripts, schedule |
| **Security** | 20 min | Permissions, hardening |
| **Documentation** | 10 min | Update runbooks, handoff |
| **TOTAL** | **2h 45min** | |

---

## Critical Paths

**Minimum Viable Deployment (45 min):**
1. Install dependencies (10 min)
2. Install application (10 min)
3. Configure (5 min)
4. Create service (5 min)
5. Validate (10 min)
6. Security basics (5 min)

**Production-Ready Deployment (2h 45min):**
- Complete all phases above

**Enterprise Deployment (4h+):**
- Add: Load balancing, HA setup, advanced monitoring

---

## Emergency Contacts

| Role | Contact | Responsibility |
|------|---------|---------------|
| **DevOps Lead** | devops@example.com | Deployment, infrastructure |
| **Security Team** | security@example.com | Security issues |
| **Application Owner** | product@example.com | Business decisions |
| **On-Call Engineer** | oncall@example.com | After-hours support |

---

## Useful Links

- **Full Documentation:** `/opt/vhs-upscaler/docs/DEPLOYMENT.md`
- **GitHub Repository:** https://github.com/parthalon025/terminalai
- **NVIDIA Maxine:** https://developer.nvidia.com/maxine
- **Real-ESRGAN:** https://github.com/xinntao/Real-ESRGAN
- **Gradio Docs:** https://gradio.app/docs
- **FFmpeg Docs:** https://ffmpeg.org/documentation.html

---

**Document Version:** 1.0
**Last Updated:** 2023-12-18
**For:** VHS Upscaler v1.4.2
