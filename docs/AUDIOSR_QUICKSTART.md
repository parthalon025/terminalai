# AudioSR Quick Start Guide

## Installation

```bash
pip install audiosr
```

## Basic Usage

### Python API

```python
from pathlib import Path
from vhs_upscaler.audio_processor import AudioProcessor, AudioConfig

# Enable AudioSR with speech model
config = AudioConfig(
    use_audiosr=True,
    audiosr_model="speech",
    sample_rate=48000
)

processor = AudioProcessor(config)
result = processor.process(
    input_path=Path("vhs_16khz.wav"),
    output_path=Path("restored_48khz.wav")
)
```

### Command Line

```bash
# Basic upsampling
python vhs_upscaler/audio_processor.py \
  -i input.wav \
  -o output.wav \
  --audio-sr

# With speech optimization
python vhs_upscaler/audio_processor.py \
  -i vhs_dialogue.wav \
  -o enhanced.wav \
  --audio-sr \
  --audiosr-model speech \
  --enhance voice
```

## Models

| Model | Best For | Use Case |
|-------|----------|----------|
| `basic` | General | Mixed content (default) |
| `speech` | Voice | VHS tapes, podcasts, dialogue |
| `music` | Music | Concerts, music videos |

## Common Workflows

### VHS Restoration

```bash
python vhs_upscaler/audio_processor.py \
  -i vhs_tape_16khz.wav \
  -o restored.aac \
  --audio-sr \
  --audiosr-model speech \
  --enhance voice \
  --normalize
```

### DVD Surround Upmix

```bash
python vhs_upscaler/audio_processor.py \
  -i dvd_stereo.ac3 \
  -o surround_5.1.eac3 \
  --audio-sr \
  --upmix surround \
  --layout 5.1 \
  --format eac3
```

### Music Archive

```bash
python vhs_upscaler/audio_processor.py \
  -i concert_22khz.wav \
  -o restored.flac \
  --audio-sr \
  --audiosr-model music \
  --enhance music \
  --format flac
```

## Features

- **AI Upsampling**: 16kHz → 48kHz with deep learning
- **GPU Acceleration**: CUDA support for 5-10x speedup
- **Auto Fallback**: Uses FFmpeg if AudioSR unavailable
- **Smart Skip**: Automatically skips if already 48kHz
- **3 Models**: Optimized for speech, music, or general use

## Troubleshooting

### AudioSR Not Found
```bash
pip install audiosr
```

### CUDA Out of Memory
```python
config = AudioConfig(use_audiosr=True, audiosr_device="cpu")
```

### Quality Not Improving
- Check input quality is <48kHz
- Try different models (speech vs music)
- Combine with enhancement (`--enhance voice`)

## Verification

```python
from vhs_upscaler.audio_processor import get_available_features
print(get_available_features())
# Expected: {'audiosr': True, ...}
```

## Documentation

Full docs: `docs/AUDIOSR_INTEGRATION.md`
