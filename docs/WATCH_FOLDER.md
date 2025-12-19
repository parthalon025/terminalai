# Watch Folder Automation

Automatically process videos as they are added to a monitored directory. Perfect for batch workflows, automated download processing, or hands-free video restoration pipelines.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [File Handling](#file-handling)
- [Error Recovery](#error-recovery)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

## Overview

The watch folder system monitors one or more directories for new video files and automatically processes them using TerminalAI's upscaling pipeline. Key features:

- **Multi-folder monitoring** - Watch multiple directories with different presets
- **Automatic processing** - New videos are detected and processed automatically
- **Smart debouncing** - Waits for files to finish copying before processing
- **Lock file protection** - Prevents duplicate processing
- **Retry logic** - Automatically retries failed processing
- **Comprehensive logging** - Detailed logs for debugging and monitoring
- **Flexible file handling** - Move, delete, or preserve originals
- **YAML configuration** - Easy to configure and version control

## Installation

### 1. Install watchdog library

```bash
pip install watchdog
```

### 2. Verify installation

```bash
python -c "import watchdog; print('watchdog installed successfully')"
```

## Quick Start

### 1. Create configuration file

Copy the example configuration:

```bash
cp scripts/watch_folder_config.yaml my_config.yaml
```

Edit `my_config.yaml` to set your input/output folders:

```yaml
watch_folders:
  - input: "./input/vhs"
    output: "./output/vhs"
    preset: "vhs"
    resolution: 1080
```

### 2. Create folders

```bash
mkdir -p input/vhs output/vhs
```

### 3. Start watching

```bash
python scripts/watch_folder.py --config my_config.yaml --verbose
```

### 4. Add a video

Copy a video file to the input folder:

```bash
cp my_vhs_tape.avi input/vhs/
```

The system will automatically detect and process the video!

## Configuration

### Basic Configuration

Minimal configuration requires only input and output paths:

```yaml
watch_folders:
  - input: "./input/vhs"
    output: "./output/vhs"
```

This uses default settings (VHS preset, 1080p, auto engine).

### Complete Configuration

Full configuration with all options:

```yaml
watch_folders:
  - input: "./input/vhs"
    output: "./output/vhs"

    # Processing settings
    preset: "vhs"                    # vhs, dvd, webcam, youtube, clean
    resolution: 1080                 # 480, 720, 1080, 1440, 2160, 4320
    engine: "auto"                   # auto, maxine, realesrgan, ffmpeg
    encoder: "hevc_nvenc"            # hevc_nvenc, h264_nvenc, hevc, h264
    crf: 20                          # 0-51 (lower = better quality)

    # Audio settings
    audio_enhance: "moderate"        # none, light, moderate, aggressive, voice, music
    audio_upmix: "surround"          # none, simple, surround, prologic, demucs
    audio_layout: "stereo"           # original, mono, stereo, 5.1, 7.1

    # HDR output
    hdr_mode: "sdr"                  # sdr, hdr10, hlg

    # File handling
    move_on_complete: true           # Move to _completed subfolder
    delete_on_complete: false        # Delete original (DANGER!)
    preserve_folder_structure: false # Preserve subfolders in output

    # Error handling
    max_retries: 2                   # Number of retry attempts
    retry_delay: 300                 # Seconds between retries
    move_failed_to_error: true       # Move failed files to _errors

    # File filtering
    file_patterns: ["*"]             # Glob patterns to match
    exclude_patterns: []             # Glob patterns to exclude
    min_file_size_mb: 1.0            # Minimum file size
```

### Multiple Watch Folders

Monitor multiple directories with different settings:

```yaml
watch_folders:
  # VHS restoration
  - input: "./input/vhs"
    output: "./output/vhs_restored"
    preset: "vhs"
    resolution: 1080
    audio_enhance: "moderate"

  # DVD to 4K
  - input: "./input/dvd"
    output: "./output/dvd_4k"
    preset: "dvd"
    resolution: 2160
    audio_upmix: "prologic"

  # YouTube processing
  - input: "./downloads/youtube"
    output: "./output/youtube"
    preset: "youtube"
    resolution: 1080
    delete_on_complete: true
```

## Usage Examples

### Basic Usage

Start with default configuration:

```bash
python scripts/watch_folder.py
```

### Custom Configuration

Use a specific configuration file:

```bash
python scripts/watch_folder.py --config /path/to/config.yaml
```

### Verbose Logging

Enable detailed logging for debugging:

```bash
python scripts/watch_folder.py --verbose
```

### Log to File

Write logs to a file for later analysis:

```bash
python scripts/watch_folder.py --log-file watch_folder.log
```

### Combined Options

```bash
python scripts/watch_folder.py \
  --config my_config.yaml \
  --verbose \
  --log-file logs/watch_$(date +%Y%m%d).log
```

### Daemon Mode

Run in background (Linux/Mac):

```bash
nohup python scripts/watch_folder.py \
  --config my_config.yaml \
  --log-file watch_folder.log \
  > /dev/null 2>&1 &
```

### Windows Service (Advanced)

For Windows service integration, use NSSM:

```powershell
# Download NSSM: https://nssm.cc/download
nssm install TerminalAI-Watcher "C:\Python\python.exe" "C:\TerminalAI\scripts\watch_folder.py"
nssm set TerminalAI-Watcher AppDirectory "C:\TerminalAI"
nssm start TerminalAI-Watcher
```

## File Handling

### File Detection

The system monitors for these video formats:

- Common: `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`
- Streaming: `.flv`, `.webm`, `.m4v`
- Legacy: `.mpg`, `.mpeg`, `.m2v`, `.vob`
- Broadcast: `.ts`, `.mts`, `.m2ts`
- Professional: `.3gp`, `.3g2`, `.mxf`

### Debouncing

To prevent processing incomplete files, the system:

1. Waits 3 seconds after file creation
2. Checks file size stability (2 consecutive checks)
3. Verifies minimum file size
4. Only then begins processing

### Lock Files

During processing, a lock file (`.filename.lock`) is created to prevent duplicate processing by multiple instances.

### Original File Handling

After successful processing, you can:

**Move to completed folder** (default):
```yaml
move_on_complete: true
delete_on_complete: false
```

Files move to `input/_completed/` subfolder.

**Delete original** (save space):
```yaml
move_on_complete: false
delete_on_complete: true
```

**Keep in place** (manual cleanup):
```yaml
move_on_complete: false
delete_on_complete: false
```

**Failed files**:
```yaml
move_failed_to_error: true
```

Failed files move to `input/_errors/` with error log.

### Folder Structure Preservation

Preserve subfolder organization in output:

```yaml
preserve_folder_structure: true
```

Input:
```
input/vhs/
  family_1990/
    tape1.avi
    tape2.avi
  vacation_1995/
    beach.avi
```

Output:
```
output/vhs/
  family_1990/
    tape1_1080p.mp4
    tape2_1080p.mp4
  vacation_1995/
    beach_1080p.mp4
```

## Error Recovery

### Automatic Retries

Failed processing is automatically retried:

```yaml
max_retries: 2          # Retry up to 2 times
retry_delay: 300        # Wait 5 minutes between retries
```

Retry schedule example:
- First attempt: Immediate
- First retry: After 5 minutes
- Second retry: After another 5 minutes
- Give up: Move to error folder

### Error Logs

When a file fails (max retries reached), an error log is created:

```
input/_errors/failed_video.mp4
input/_errors/failed_video.error.txt
```

Error log contents:
```
Processing failed at: 2025-12-18T14:30:00
Error: Processing command failed: FFmpeg error...
Retries: 2
```

### Recovery Strategies

**Temporary network issues:**
```yaml
max_retries: 5
retry_delay: 600  # 10 minutes
```

**Aggressive retry (unreliable source):**
```yaml
max_retries: 10
retry_delay: 300
```

**No retries (manual review):**
```yaml
max_retries: 0
move_failed_to_error: true
```

## Advanced Features

### File Pattern Filtering

Process only specific file types:

```yaml
file_patterns: ["*.avi", "*.mkv"]  # Only AVI and MKV
```

Process files matching name pattern:

```yaml
file_patterns: ["family_*.mp4", "vacation_*.mp4"]
```

### Exclude Patterns

Ignore certain files:

```yaml
exclude_patterns: ["*_temp*", "*_preview*", "*.partial"]
```

### Minimum File Size

Skip small/incomplete files:

```yaml
min_file_size_mb: 10.0  # Ignore files under 10MB
```

Useful for:
- Skipping incomplete downloads
- Filtering out corrupt files
- Ignoring test clips

### Preset-Specific Folders

Organize by source type:

```yaml
watch_folders:
  # VHS tapes - heavy restoration
  - input: "./input/vhs"
    output: "./output/restored"
    preset: "vhs"
    resolution: 1080
    audio_enhance: "aggressive"
    max_retries: 3

  # Clean digital - minimal processing
  - input: "./input/digital"
    output: "./output/enhanced"
    preset: "clean"
    resolution: 2160
    audio_enhance: "none"
    max_retries: 1
```

### Integration with yt-dlp

Automatically process YouTube downloads:

**1. Setup yt-dlp download folder:**
```bash
yt-dlp \
  --output "input/youtube/%(title)s.%(ext)s" \
  --format "bestvideo+bestaudio" \
  "https://youtube.com/playlist?list=..."
```

**2. Configure watch folder:**
```yaml
watch_folders:
  - input: "./input/youtube"
    output: "./output/youtube_enhanced"
    preset: "youtube"
    resolution: 1080
    delete_on_complete: true  # Save space
```

**3. Videos are automatically processed as they download!**

### Network Storage Support

Watch folders on network drives:

```yaml
watch_folders:
  - input: "//nas/videos/input"
    output: "//nas/videos/output"
    preset: "vhs"
    # Use longer delays for network stability
    min_file_size_mb: 5.0
    max_retries: 3
    retry_delay: 600
```

## Troubleshooting

### Files Not Being Detected

**Check file extension:**
```bash
# Verify extension is supported
python -c "from scripts.watch_folder import VIDEO_EXTENSIONS; print(VIDEO_EXTENSIONS)"
```

**Check file patterns:**
```yaml
# Try wildcard first
file_patterns: ["*"]
```

**Check minimum size:**
```yaml
# Lower or disable minimum size
min_file_size_mb: 0.1
```

**Enable verbose logging:**
```bash
python scripts/watch_folder.py --verbose
```

### Files Stuck in Processing

**Check for lock files:**
```bash
find input/ -name ".*.lock"
```

**Remove stale locks** (if process crashed):
```bash
find input/ -name ".*.lock" -delete
```

**Check processing logs:**
Look for errors in console output or log file.

### High Retry Rate

**Insufficient system resources:**
- Reduce concurrent processing (hardcoded to 1 in current implementation)
- Increase `retry_delay` to allow system recovery

**FFmpeg/encoder issues:**
- Check FFmpeg installation: `ffmpeg -version`
- Verify NVIDIA drivers (for NVENC): `nvidia-smi`
- Try software encoder: `encoder: "hevc"` (slower but more compatible)

**Corrupt source files:**
```yaml
# Move failed files for manual review
move_failed_to_error: true
max_retries: 1  # Don't waste time on corrupt files
```

### Permission Errors

**Linux/Mac - Ensure write permissions:**
```bash
chmod 755 input/ output/
```

**Windows - Run as administrator** (if watching system folders)

**Network drives - Mount with write access:**
```bash
# Linux example
sudo mount -t cifs //nas/share /mnt/videos -o username=user,rw
```

### Memory Issues

**Large batch processing:**
- Process one at a time (current default)
- Use `delete_on_complete: true` to free space
- Monitor with `--verbose` to identify memory-heavy files

**Adjust FFmpeg settings:**
```yaml
# Use lower quality for less memory usage
crf: 23  # Higher = lower quality/size
resolution: 1080  # Don't upscale to 4K if not needed
```

### Watchdog Not Starting

**Install/upgrade watchdog:**
```bash
pip install --upgrade watchdog
```

**Platform-specific issues:**
- **macOS:** Requires FSEvents (included in watchdog)
- **Linux:** Requires inotify (kernel support, usually available)
- **Windows:** Requires ReadDirectoryChangesW (Windows API, always available)

**Test watchdog separately:**
```python
from watchdog.observers import Observer
print("Watchdog imported successfully")
```

## Best Practices

### Production Deployment

1. **Use absolute paths:**
   ```yaml
   input: "/home/user/videos/input"
   output: "/home/user/videos/output"
   ```

2. **Enable file logging:**
   ```bash
   python scripts/watch_folder.py --log-file /var/log/terminalai_watch.log
   ```

3. **Run as service** (Linux systemd example):
   ```ini
   [Unit]
   Description=TerminalAI Watch Folder
   After=network.target

   [Service]
   Type=simple
   User=videouser
   WorkingDirectory=/opt/terminalai
   ExecStart=/usr/bin/python3 scripts/watch_folder.py --config /etc/terminalai/watch.yaml
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. **Monitor disk space:**
   ```bash
   # Add to crontab
   0 */6 * * * df -h /path/to/output | mail -s "Disk Space" admin@example.com
   ```

5. **Regular cleanup:**
   ```bash
   # Archive old completed files
   find input/_completed -mtime +30 -exec mv {} /archive/ \;
   ```

### Testing Configuration

Before production, test with a small file:

```bash
# 1. Start watcher in verbose mode
python scripts/watch_folder.py --config test_config.yaml --verbose

# 2. Copy a small test file
cp test_small.mp4 input/vhs/

# 3. Monitor logs for errors
# 4. Verify output file created
# 5. Check original file moved/deleted as expected
```

### Monitoring

**Real-time monitoring:**
```bash
tail -f watch_folder.log | grep "ERROR\|WARNING\|Completed"
```

**Statistics tracking:**
```bash
# Count completed
find output/ -name "*.mp4" | wc -l

# Count failed
find input/_errors/ -name "*.mp4" | wc -l

# Total processing time (from logs)
grep "Completed:" watch_folder.log | awk '{sum+=$NF} END {print sum}'
```

## Performance Tips

1. **SSD for temp files** - TerminalAI uses temp files, SSD speeds up processing
2. **GPU acceleration** - Use NVENC encoder for faster processing
3. **Batch similar content** - Group VHS, DVD, etc. for consistent settings
4. **Network drive considerations** - Local processing is faster than network I/O
5. **Resource monitoring** - Watch CPU/GPU/RAM to optimize concurrent processing

## Future Enhancements

Planned features for future versions:

- [ ] Parallel processing (multiple videos simultaneously)
- [ ] GUI monitoring dashboard
- [ ] Email/webhook notifications
- [ ] Priority queuing
- [ ] Scheduled processing windows
- [ ] Integration with video analysis for auto-preset selection
- [ ] Cloud storage integration (S3, Google Drive, etc.)

## Support

For issues or questions:

1. Check this documentation
2. Review logs with `--verbose`
3. Test with simple configuration
4. File an issue on GitHub with logs and configuration

---

**Version:** 1.0
**Last Updated:** 2025-12-18
**Compatible with:** TerminalAI v1.4.2+
