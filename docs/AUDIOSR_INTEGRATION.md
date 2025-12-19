# AudioSR Integration Documentation

## Overview

AudioSR is an AI-based audio super-resolution tool that intelligently upsamples low-quality audio to higher sample rates (typically 48kHz) for professional output quality. This integration adds AudioSR support to the VHS upscaler's audio processing pipeline.

## Features

- **AI-Based Upsampling**: Uses deep learning to recover lost high-frequency content
- **Multiple Models**: Supports basic, speech, and music-optimized models
- **Automatic Fallback**: Falls back to FFmpeg resampling if AudioSR is unavailable
- **GPU Acceleration**: Supports CUDA for faster processing when available
- **Pipeline Integration**: Automatically applies before surround upmixing for best results

## Installation

### Install AudioSR

```bash
# Install AudioSR package
pip install audiosr

# Or install with the full audio features
pip install -e ".[audio]"
```

### Verify Installation

```python
python -c "from vhs_upscaler.audio_processor import get_available_features; print(get_available_features())"
```

Expected output:
```python
{'ffmpeg': True, 'ffprobe': True, 'demucs': False, 'deepfilternet': False, 'audiosr': True}
```

## Usage

### Python API

#### Basic Usage

```python
from pathlib import Path
from vhs_upscaler.audio_processor import AudioProcessor, AudioConfig

# Enable AudioSR
config = AudioConfig(
    use_audiosr=True,
    audiosr_model="basic",  # or "speech", "music"
    sample_rate=48000
)

processor = AudioProcessor(config)
result = processor.process(
    input_path=Path("input_22050hz.wav"),
    output_path=Path("output_48000hz.wav")
)

print(f"Processed audio saved to: {result}")
```

#### With Enhancement and Upmixing

```python
from vhs_upscaler.audio_processor import (
    AudioProcessor, AudioConfig,
    AudioEnhanceMode, UpmixMode, AudioChannelLayout
)

# Full pipeline: AudioSR → Enhancement → Upmix
config = AudioConfig(
    use_audiosr=True,           # AI upsampling first
    audiosr_model="speech",     # Optimized for voice
    enhance_mode=AudioEnhanceMode.VOICE,  # Speech enhancement
    upmix_mode=UpmixMode.SURROUND,        # Surround upmix
    output_layout=AudioChannelLayout.SURROUND_51,
    sample_rate=48000
)

processor = AudioProcessor(config)
result = processor.process(
    input_path=Path("vhs_audio_16khz.wav"),
    output_path=Path("enhanced_5.1_48khz.eac3")
)
```

### Command-Line Interface

#### Basic Upsampling

```bash
# Upsample audio to 48kHz with AudioSR
python vhs_upscaler/audio_processor.py \
  -i input_22050hz.wav \
  -o output_48000hz.wav \
  --audio-sr

# Use speech-optimized model
python vhs_upscaler/audio_processor.py \
  -i vhs_dialogue.wav \
  -o enhanced_dialogue.wav \
  --audio-sr \
  --audiosr-model speech
```

#### Full Processing Pipeline

```bash
# VHS audio restoration: AudioSR + Enhancement + Surround Upmix
python vhs_upscaler/audio_processor.py \
  -i vhs_tape_16khz.wav \
  -o restored_5.1_48khz.eac3 \
  --audio-sr \
  --audiosr-model speech \
  --enhance voice \
  --upmix surround \
  --layout 5.1 \
  --format eac3
```

#### Check Feature Availability

```bash
python vhs_upscaler/audio_processor.py -v
```

Output shows available features:
```
Available features: FFmpeg=True, Demucs=False, DeepFilterNet=False, AudioSR=True
```

## Model Selection

AudioSR provides three optimized models:

### Basic Model (Default)

- **Use Case**: General-purpose audio upsampling
- **Best For**: Mixed content, music and speech
- **Model Size**: Medium
- **Speed**: Fast

```python
config = AudioConfig(use_audiosr=True, audiosr_model="basic")
```

### Speech Model

- **Use Case**: Voice/dialogue optimization
- **Best For**: VHS tapes, podcasts, interviews
- **Optimizations**: Preserves vocal clarity, reduces artifacts in speech frequencies
- **Recommended For**: Home videos, documentaries

```python
config = AudioConfig(use_audiosr=True, audiosr_model="speech")
```

### Music Model

- **Use Case**: Music and complex audio
- **Best For**: Concert recordings, music videos
- **Optimizations**: Preserves stereo imaging, harmonic content
- **Recommended For**: Live performances, studio recordings

```python
config = AudioConfig(use_audiosr=True, audiosr_model="music")
```

## Processing Pipeline Order

AudioSR is automatically inserted at the optimal point in the processing pipeline:

```
1. Extract Audio (if from video)
2. Enhancement (optional)
   ↓
3. AudioSR Upsampling ← NEW: AI upsampling to 48kHz
   ↓
4. Surround Upmix (optional)
   ↓
5. Normalization (optional)
   ↓
6. Encoding (final format)
```

**Why This Order?**

- **After Enhancement**: Denoising works better on original sample rate
- **Before Upmixing**: Provides higher quality source for surround generation
- **Before Encoding**: Ensures consistent 48kHz output for all formats

## Configuration Options

### AudioConfig Fields

```python
@dataclass
class AudioConfig:
    # AudioSR settings
    use_audiosr: bool = False        # Enable AI upsampling
    audiosr_model: str = "basic"     # Model: basic, speech, music
    audiosr_device: str = "auto"     # Device: auto, cuda, cpu
    sample_rate: int = 48000         # Target sample rate
```

### Device Selection

```python
# Automatic (uses CUDA if available)
config = AudioConfig(use_audiosr=True, audiosr_device="auto")

# Force CPU (for compatibility)
config = AudioConfig(use_audiosr=True, audiosr_device="cpu")

# Force CUDA (requires GPU)
config = AudioConfig(use_audiosr=True, audiosr_device="cuda")
```

## Behavior and Fallbacks

### Automatic Skip Conditions

AudioSR will be skipped (no processing) if:

1. **Already High Sample Rate**: Input is already ≥48kHz
   ```
   INFO: Audio already at 48000Hz, skipping AudioSR
   ```

2. **AudioSR Not Installed**: Package not available
   ```
   WARNING: AudioSR not available, using FFmpeg resampling
   ```

3. **Processing Error**: AI processing fails
   ```
   ERROR: AudioSR processing failed, falling back to FFmpeg resampling
   ```

### Graceful Fallback

When AudioSR is unavailable or fails, the system automatically falls back to high-quality FFmpeg resampling:

```python
def _resample_ffmpeg(self, input_path: Path, output_path: Path, target_sr: int = 48000):
    """Fallback resampling using FFmpeg (high-quality)."""
    # Uses FFmpeg's high-quality resampler
```

## Performance Considerations

### Processing Speed

| Input Sample Rate | Duration | Device | Processing Time |
|-------------------|----------|--------|-----------------|
| 16kHz → 48kHz     | 1 minute | CPU    | ~15-30 seconds  |
| 16kHz → 48kHz     | 1 minute | CUDA   | ~3-5 seconds    |
| 22kHz → 48kHz     | 1 minute | CPU    | ~10-20 seconds  |
| 22kHz → 48kHz     | 1 minute | CUDA   | ~2-4 seconds    |

### Memory Usage

- **CPU Mode**: ~500MB-1GB for typical audio files
- **GPU Mode**: ~1-2GB VRAM + ~500MB RAM
- **Chunked Processing**: AudioSR processes in chunks for memory efficiency

### Quality vs. Speed Trade-off

```python
# Fastest (FFmpeg resampling)
config = AudioConfig(use_audiosr=False, sample_rate=48000)

# Balanced (AudioSR with CPU)
config = AudioConfig(use_audiosr=True, audiosr_device="cpu")

# Best Quality (AudioSR with GPU)
config = AudioConfig(use_audiosr=True, audiosr_device="cuda")
```

## Use Cases

### 1. VHS Tape Restoration

VHS tapes typically have:
- **Sample Rate**: 16-22kHz (limited bandwidth)
- **Artifacts**: Tape hiss, dropouts, flutter
- **Content**: Usually speech/dialogue

**Recommended Settings**:
```bash
python vhs_upscaler/audio_processor.py \
  -i vhs_tape.wav \
  -o restored.eac3 \
  --audio-sr \
  --audiosr-model speech \
  --enhance voice \
  --layout stereo \
  --format eac3
```

### 2. Old DVD Upscaling

DVDs often have:
- **Sample Rate**: 44.1kHz or 48kHz (usually OK)
- **Artifacts**: Compression artifacts
- **Content**: Mixed (dialogue + music)

**Recommended Settings** (only if <48kHz):
```bash
python vhs_upscaler/audio_processor.py \
  -i dvd_audio.ac3 \
  -o upscaled.eac3 \
  --audio-sr \
  --audiosr-model basic \
  --enhance moderate \
  --upmix surround \
  --layout 5.1
```

### 3. Low-Quality Web Videos

Web videos may have:
- **Sample Rate**: 16-32kHz (varies widely)
- **Artifacts**: Heavy compression
- **Content**: Usually speech

**Recommended Settings**:
```bash
python vhs_upscaler/audio_processor.py \
  -i youtube_audio.m4a \
  -o enhanced.aac \
  --audio-sr \
  --audiosr-model speech \
  --enhance aggressive \
  --normalize
```

### 4. Music Archive Restoration

Old recordings may have:
- **Sample Rate**: 22-44kHz
- **Artifacts**: Tape hiss, analog noise
- **Content**: Music

**Recommended Settings**:
```bash
python vhs_upscaler/audio_processor.py \
  -i concert_recording.wav \
  -o restored.flac \
  --audio-sr \
  --audiosr-model music \
  --enhance music \
  --format flac \
  --normalize
```

## Integration with Video Processing

AudioSR integrates seamlessly with the main VHS upscaler:

```python
from vhs_upscaler.vhs_upscale import VideoUpscaler
from vhs_upscaler.audio_processor import AudioConfig, AudioEnhanceMode

# Configure audio processing with AudioSR
audio_config = AudioConfig(
    use_audiosr=True,
    audiosr_model="speech",
    enhance_mode=AudioEnhanceMode.VOICE,
    sample_rate=48000
)

# Configure video upscaling
upscaler = VideoUpscaler(
    input_file="vhs_tape.mp4",
    output_file="restored.mp4",
    audio_config=audio_config  # Pass audio config
)

upscaler.process()
```

## Troubleshooting

### AudioSR Not Found

```
ImportError: No module named 'audiosr'
```

**Solution**:
```bash
pip install audiosr
```

### CUDA Out of Memory

```
RuntimeError: CUDA out of memory
```

**Solution**:
```python
# Use CPU mode
config = AudioConfig(use_audiosr=True, audiosr_device="cpu")
```

### Processing Takes Too Long

```
INFO: AudioSR upsampling completed: 16000Hz → 48000Hz
```

**Solutions**:
1. Use CUDA if available
2. Process shorter segments
3. Fall back to FFmpeg: `use_audiosr=False`

### Quality Not Improving

If AudioSR isn't improving quality:

1. **Check Input Quality**: Severely degraded audio may not benefit
2. **Try Different Models**: Speech vs. music models perform differently
3. **Adjust Enhancement**: Combine with appropriate denoise settings
4. **Verify Sample Rate**: Check actual input sample rate

```python
from vhs_upscaler.audio_processor import AudioProcessor

processor = AudioProcessor()
info = processor.get_audio_info(Path("input.wav"))
print(f"Sample rate: {info['sample_rate']}Hz")
```

## API Reference

### Methods

#### `AudioProcessor._upsample_audiosr()`

```python
def _upsample_audiosr(
    self,
    input_path: Path,
    output_path: Path,
    target_sr: int = 48000
) -> str:
    """
    AI-based audio upsampling using AudioSR.

    Args:
        input_path: Input audio file (WAV format)
        output_path: Output upsampled audio file
        target_sr: Target sampling rate (default: 48000 Hz)

    Returns:
        Path to upsampled audio file

    Raises:
        ImportError: If AudioSR is not installed
        RuntimeError: If processing fails (falls back to FFmpeg)
    """
```

#### `AudioProcessor._resample_ffmpeg()`

```python
def _resample_ffmpeg(
    self,
    input_path: Path,
    output_path: Path,
    target_sr: int = 48000
) -> str:
    """
    Fallback resampling using FFmpeg.

    Args:
        input_path: Input audio file
        output_path: Output resampled audio file
        target_sr: Target sampling rate

    Returns:
        Path to resampled audio file
    """
```

#### `AudioProcessor._check_audiosr()`

```python
def _check_audiosr(self) -> bool:
    """
    Check if AudioSR is available.

    Returns:
        True if AudioSR is installed and importable, False otherwise
    """
```

## Examples

### Example 1: Basic Upsampling

```python
from pathlib import Path
from vhs_upscaler.audio_processor import AudioProcessor, AudioConfig

config = AudioConfig(use_audiosr=True)
processor = AudioProcessor(config)

result = processor.process(
    Path("low_quality_16khz.wav"),
    Path("high_quality_48khz.wav")
)
```

### Example 2: VHS Restoration

```python
from vhs_upscaler.audio_processor import (
    AudioProcessor, AudioConfig,
    AudioEnhanceMode, AudioChannelLayout
)

config = AudioConfig(
    use_audiosr=True,
    audiosr_model="speech",
    enhance_mode=AudioEnhanceMode.VOICE,
    normalize=True,
    output_layout=AudioChannelLayout.STEREO,
    sample_rate=48000
)

processor = AudioProcessor(config)
result = processor.process(
    Path("vhs_tape_audio.wav"),
    Path("restored_audio.aac")
)
```

### Example 3: Music Upmix

```python
from vhs_upscaler.audio_processor import (
    AudioProcessor, AudioConfig,
    AudioEnhanceMode, UpmixMode, AudioChannelLayout, AudioFormat
)

config = AudioConfig(
    use_audiosr=True,
    audiosr_model="music",
    enhance_mode=AudioEnhanceMode.MUSIC,
    upmix_mode=UpmixMode.DEMUCS,  # AI stem-based upmix
    output_layout=AudioChannelLayout.SURROUND_51,
    output_format=AudioFormat.FLAC,
    sample_rate=48000
)

processor = AudioProcessor(config)
result = processor.process(
    Path("concert_stereo_22khz.wav"),
    Path("concert_5.1_48khz.flac")
)
```

## Best Practices

1. **Use Appropriate Model**: Match the model to your content type
2. **Order Matters**: Let AudioSR run before surround upmixing
3. **Check Input Quality**: Very degraded audio may need enhancement first
4. **GPU When Available**: CUDA significantly speeds up processing
5. **Monitor Memory**: Large files may need chunked processing
6. **Validate Output**: Compare before/after with spectral analysis
7. **Combine With Enhancement**: AudioSR works best with appropriate denoising

## References

- [AudioSR GitHub Repository](https://github.com/haoheliu/versatile_audio_super_resolution)
- [AudioSR Paper](https://arxiv.org/abs/2309.07314)
- [FFmpeg Audio Resampling Documentation](https://ffmpeg.org/ffmpeg-resampler.html)

## License

AudioSR integration follows the same license as the main VHS upscaler project. AudioSR itself is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
