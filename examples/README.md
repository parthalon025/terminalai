# TerminalAI Examples

This directory contains example scripts and usage patterns for TerminalAI video processing.

## Basic Examples

### 1. Simple VHS Upscale
```python
# examples/basic_vhs_upscale.py
from vhs_upscaler.vhs_upscale import VideoUpscaler, UpscaleConfig

config = UpscaleConfig(
    input_file="old_vhs_tape.mp4",
    output_file="restored.mp4",
    preset="vhs",
    target_resolution="1080p",
    engine="auto"
)

upscaler = VideoUpscaler(config)
upscaler.process()
```

### 2. Batch Processing
```python
# examples/batch_processing.py
from pathlib import Path
from vhs_upscaler.queue_manager import VideoQueue, QueueJob

queue = VideoQueue()

# Add multiple videos
for video in Path("old_videos").glob("*.mp4"):
    job = QueueJob(
        input_file=str(video),
        output_file=f"output/{video.stem}_upscaled.mp4",
        preset="vhs"
    )
    queue.add_job(job)

# Process queue
queue.start_processing()
```

### 3. YouTube Download + Upscale
```python
# examples/youtube_upscale.py
from vhs_upscaler.vhs_upscale import VideoUpscaler, UpscaleConfig

config = UpscaleConfig(
    youtube_url="https://youtube.com/watch?v=VIDEO_ID",
    output_file="upscaled_video.mp4",
    preset="youtube",
    target_resolution="1080p"
)

upscaler = VideoUpscaler(config)
upscaler.process()
```

### 4. Advanced Audio Processing
```python
# examples/audio_enhancement.py
from vhs_upscaler.vhs_upscale import VideoUpscaler, UpscaleConfig, AudioConfig

audio_config = AudioConfig(
    enable_audio_processing=True,
    enhance_mode="moderate",
    upmix_to_surround=True,
    upmix_mode="demucs",  # AI-powered best quality
    output_format="eac3"
)

config = UpscaleConfig(
    input_file="old_movie.mp4",
    output_file="enhanced.mp4",
    preset="dvd",
    audio_config=audio_config
)

upscaler = VideoUpscaler(config)
upscaler.process()
```

### 5. HDR Conversion
```python
# examples/hdr_conversion.py
from vhs_upscaler.vhs_upscale import VideoUpscaler, UpscaleConfig

config = UpscaleConfig(
    input_file="video.mp4",
    output_file="video_hdr.mp4",
    preset="clean",
    target_resolution="2160p",
    hdr_mode="hdr10",
    encoder="hevc_nvenc"  # Required for HDR
)

upscaler = VideoUpscaler(config)
upscaler.process()
```

### 6. Custom Filter Chain
```python
# examples/custom_filters.py
from vhs_upscaler.vhs_upscale import VideoUpscaler, UpscaleConfig

config = UpscaleConfig(
    input_file="video.mp4",
    output_file="custom_output.mp4",
    preset="clean",
    deinterlace=True,
    denoise_strength="4:3:6:4.5",  # Custom hqdn3d values
    sharpen_strength=0.5,
    color_correction="eq=contrast=1.15:brightness=0.1:saturation=1.05"
)

upscaler = VideoUpscaler(config)
upscaler.process()
```

### 7. Analysis + Processing
```python
# examples/analyze_and_process.py
from vhs_upscaler.analysis import AnalyzerWrapper
from vhs_upscaler.vhs_upscale import VideoUpscaler
from vhs_upscaler.presets import get_preset_from_analysis

# Analyze video
analyzer = AnalyzerWrapper()
analysis = analyzer.analyze("unknown_video.mp4")

# Get recommended preset
preset = get_preset_from_analysis(analysis)
print(f"Recommended preset: {preset}")
print(f"Detected: {analysis.source_format}, {analysis.scan_type}")

# Process with recommendations
config = analysis.to_upscale_config(output_file="restored.mp4")
upscaler = VideoUpscaler(config)
upscaler.process()
```

## CLI Examples

### Basic CLI Usage
```bash
# Simple upscale
vhs-upscale -i video.mp4 -o output.mp4 --preset vhs

# Auto-detect settings
vhs-upscale -i video.mp4 -o output.mp4 --auto-detect

# Analyze only
vhs-upscale -i video.mp4 --analyze-only --save-analysis config.json

# Use saved analysis
vhs-upscale -i video.mp4 -o output.mp4 --analysis-config config.json
```

### Batch CLI
```bash
# Process directory
for f in old_videos/*.mp4; do
  vhs-upscale -i "$f" -o "output/$(basename $f)" --preset vhs
done
```

### With Audio Enhancement
```bash
vhs-upscale -i video.mp4 -o output.mp4 \
  --preset vhs \
  --enhance-audio moderate \
  --upmix-surround demucs \
  --audio-format eac3
```

## Integration Examples

See the main documentation for:
- GUI integration patterns
- Queue callback handlers
- Custom progress tracking
- Engine detection and fallbacks
- Error handling strategies

## Contributing

Feel free to contribute your own examples via pull request!
