# Scripts Directory

This directory contains utility scripts and automation tools for TerminalAI.

## Available Scripts

### watch_folder.py - Watch Folder Automation

Monitors directories for new video files and automatically processes them with configurable presets.

**Features:**
- Real-time file monitoring using watchdog
- Multiple watch folder support with different settings per folder
- Automatic retry on processing errors
- Move completed/failed files to organized directories
- YAML configuration support
- Graceful shutdown (Ctrl+C)

**Installation:**
```bash
pip install watchdog
```

**Basic Usage:**
```bash
# Watch a single folder
python scripts/watch_folder.py \
  --input ~/Videos/to_process \
  --output ~/Videos/processed \
  --preset vhs

# Watch multiple folders with config file
python scripts/watch_folder.py --config watch_config.yaml

# Process existing files before starting watch
python scripts/watch_folder.py --config watch_config.yaml --process-existing

# Generate example config file
python scripts/watch_folder.py --create-config watch_config.yaml
```

**Configuration File Example:**
```yaml
watch_folders:
  - input_dir: ~/Videos/vhs_to_process
    output_dir: ~/Videos/vhs_processed
    preset: vhs
    resolution: 1080
    move_on_complete: true
    delete_on_complete: false
    retry_on_error: true
    max_retries: 3
    # Optional advanced settings
    face_restore: true
    audio_enhance: voice
    audio_upmix: demucs
    encoder: hevc_nvenc
    crf: 18
    
  - input_dir: ~/Videos/youtube_to_process
    output_dir: ~/Videos/youtube_processed
    preset: youtube
    resolution: 1080
```

**Directory Structure:**
When processing completes, the watch folder automatically organizes files:

```
input_dir/
├── video1.mp4          # Currently processing or pending
├── video2.mp4
├── _completed/         # Successfully processed originals moved here
│   ├── video0.mp4
│   └── old_tape.avi
└── _failed/            # Failed processing originals moved here
    └── corrupted.mp4

output_dir/
├── video0_processed.mp4
└── old_tape_processed.avi
```

**Workflow:**
1. Drop video file into `input_dir`
2. Watch folder detects new file
3. Waits for file to finish copying (3 stable size checks)
4. Adds to processing queue with configured preset
5. Monitors job completion
6. On success: Moves original to `_completed/`, outputs processed video to `output_dir`
7. On failure: Retries up to `max_retries`, then moves to `_failed/`

**Advanced Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `preset` | Processing preset (vhs, dvd, youtube, etc.) | vhs |
| `resolution` | Output resolution (720, 1080, 2160) | 1080 |
| `move_on_complete` | Move original to `_completed/` after success | true |
| `delete_on_complete` | Delete original after success (USE WITH CAUTION) | false |
| `retry_on_error` | Retry failed jobs automatically | true |
| `max_retries` | Maximum retry attempts | 3 |
| `encoder` | Video encoder (h264_nvenc, hevc_nvenc, libx265) | (preset default) |
| `crf` | Quality (lower = better, 15-28) | (preset default) |
| `face_restore` | Enable face restoration with GFPGAN | false |
| `audio_enhance` | Audio enhancement mode (light, voice, music) | (none) |
| `audio_upmix` | Surround upmix (simple, demucs) | (none) |
| `deinterlace` | Deinterlacing algorithm (yadif, qtgmc) | (preset default) |
| `denoise` | Denoise level (light, medium, heavy) | (preset default) |

**Command-Line Arguments:**
```
--config, -c       YAML configuration file path
--input, -i        Input directory to watch (single folder mode)
--output, -o       Output directory (single folder mode)
--preset, -p       Processing preset (default: vhs)
--resolution, -r   Output resolution (default: 1080)
--process-existing Process existing files before watching
--create-config    Generate example config file
--log-level        Logging level (DEBUG, INFO, WARNING, ERROR)
```

**Logging:**
The watch folder system logs all activity:
- File detection
- Processing queue additions
- Job completion/failure
- File moves
- Errors with stack traces

Set log level with `--log-level DEBUG` for detailed output.

**Stopping the Watcher:**
Press `Ctrl+C` to gracefully shut down. The system will:
1. Stop monitoring folders
2. Complete any in-progress file checks
3. Shut down observers cleanly

**Production Deployment:**

Run as a system service (Linux/macOS):
```bash
# Create systemd service: /etc/systemd/system/terminalai-watch.service
[Unit]
Description=TerminalAI Watch Folder Automation
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/terminalai
ExecStart=/usr/bin/python3 scripts/watch_folder.py --config /path/to/watch_config.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable terminalai-watch
sudo systemctl start terminalai-watch
sudo systemctl status terminalai-watch
```

**Windows Service:**
Use NSSM (Non-Sucking Service Manager):
```cmd
nssm install TerminalAIWatch "C:\Python39\python.exe" "scripts\watch_folder.py --config watch_config.yaml"
nssm start TerminalAIWatch
```

**Docker Deployment:**
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -e ".[full]" watchdog
CMD ["python", "scripts/watch_folder.py", "--config", "/config/watch_config.yaml"]
```

Mount volumes for input/output directories:
```bash
docker run -d \
  -v /path/to/input:/input \
  -v /path/to/output:/output \
  -v /path/to/config:/config \
  terminalai-watch
```

**Best Practices:**

1. **Use separate directories** for each content type (VHS, DVD, YouTube) with appropriate presets
2. **Test with small files first** to verify settings before batch processing
3. **Monitor disk space** - processing can temporarily use 2-3x source file size
4. **Enable retry_on_error** for production to handle transient failures
5. **Use `--process-existing`** carefully - it processes ALL files in directory
6. **Backup important files** before using `delete_on_complete`
7. **Set appropriate max_retries** (3 is recommended, 1 for fast fail)

**Troubleshooting:**

**Files not being detected:**
- Check input directory path is correct
- Verify file extensions are supported (.mp4, .avi, .mkv, .mov)
- Ensure files are fully copied (watch folder waits for stable file size)
- Check log output with `--log-level DEBUG`

**Processing failures:**
- Check output directory has write permissions
- Verify FFmpeg is installed and in PATH
- Check GPU/upscale engine availability
- Review failed files in `_failed/` directory

**High CPU/Memory usage:**
- Reduce concurrent processing (use queue's worker limit)
- Use faster presets (youtube vs vhs_heavy)
- Lower resolution output
- Disable face restoration if not needed

**Files stuck in "processing":**
- Check process is still running
- Review logs for errors
- Kill and restart watch folder service
- Files will be re-detected on restart

---

For more information, see:
- [Main README](../README.md)
- [Queue Manager Documentation](../vhs_upscaler/queue_manager.py)
- [Processing Presets](../vhs_upscaler/config.yaml)
