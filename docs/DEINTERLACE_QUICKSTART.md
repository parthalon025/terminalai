# Deinterlace Module - Quick Start Guide

## Installation

```bash
# Basic (FFmpeg filters only)
# Already installed if you have FFmpeg

# Advanced (QTGMC support)
pip install havsfunc
# + Install VapourSynth from https://github.com/vapoursynth/vapoursynth/releases
```

## Quick Test

```bash
# Check what's available
python vhs_upscaler/test_deinterlace.py --check-setup

# Test on a video
python vhs_upscaler/test_deinterlace.py --engine bwdif -i input.mp4 -o output.mp4
```

## Basic Usage

```python
from pathlib import Path
from vhs_upscaler.deinterlace import DeinterlaceProcessor, DeinterlaceEngine

# Fast, good quality (recommended for most cases)
processor = DeinterlaceProcessor(engine=DeinterlaceEngine.BWDIF)
processor.deinterlace(
    input_path=Path("interlaced.mp4"),
    output_path=Path("progressive.mp4"),
    tff=True  # Top field first (most NTSC VHS)
)

# Best quality (requires VapourSynth)
processor = DeinterlaceProcessor(engine=DeinterlaceEngine.QTGMC)
processor.deinterlace(
    input_path=Path("interlaced.mp4"),
    output_path=Path("progressive.mp4"),
    preset="medium",  # "draft", "medium", "slow", "very_slow", "placebo"
    tff=True
)
```

## Engine Comparison

| Engine | Speed | Quality | When to Use |
|--------|-------|---------|-------------|
| **yadif** | Fastest | Good | Batch processing, previews |
| **bwdif** | Very Fast | Better | **Recommended default** |
| **w3fdif** | Very Fast | Good | Fine details, static scenes |
| **qtgmc** | Slow | Best | Archival, VHS restoration |

## Field Order Quick Reference

| Format | Field Order | TFF Flag |
|--------|-------------|----------|
| NTSC VHS | TFF | `True` |
| PAL VHS | BFF | `False` |
| US Broadcast | TFF | `True` |
| EU Broadcast | BFF | `False` |

**Detect with ffprobe:**
```bash
ffprobe -v quiet -select_streams v:0 -show_entries stream=field_order -of csv=p=0 input.mp4
```

## Preset Integration

```python
# presets.py already updated with:
PRESETS = {
    "vhs_clean": {
        "deinterlace_algorithm": "qtgmc",  # Best for clean VHS
        "qtgmc_preset": "medium",
        # ...
    },
    "vhs_standard": {
        "deinterlace_algorithm": "bwdif",  # Fast for typical VHS
        "qtgmc_preset": None,
        # ...
    },
}
```

## Common Patterns

### With Progress Callback
```python
def progress(percent):
    print(f"Progress: {percent:.1f}%")

processor.deinterlace(
    input_path=Path("input.mp4"),
    output_path=Path("output.mp4"),
    progress_callback=progress
)
```

### Check Capabilities
```python
caps = processor.get_capabilities()
print(f"Available engines: {caps['available_engines']}")
print(f"Has VapourSynth: {caps['has_vapoursynth']}")
```

### List Available Engines
```python
available = DeinterlaceProcessor.list_available_engines()
print(f"Available: {available}")
# Output: ['yadif', 'bwdif', 'w3fdif', 'qtgmc']
```

## Troubleshooting

**QTGMC not available:**
1. Install VapourSynth
2. `pip install havsfunc`
3. Install ffms2 plugin
4. See `docs/DEINTERLACING.md` for details

**Wrong field order (combing still visible):**
Try opposite: `tff=False` instead of `tff=True`

**Too slow:**
Use faster preset or engine:
- QTGMC: Use "draft" preset
- Or switch to bwdif: `DeinterlaceEngine.BWDIF`

## Documentation

- **Full Guide:** `docs/DEINTERLACING.md`
- **VapourSynth Setup:** `vhs_upscaler/vapoursynth_scripts/README.md`
- **Implementation:** `SPRINT2_IMPLEMENTATION.md`

## Example: Complete Workflow

```python
from pathlib import Path
from vhs_upscaler.deinterlace import DeinterlaceProcessor, DeinterlaceEngine

# 1. Check what's available
available = DeinterlaceProcessor.list_available_engines()
print(f"Available engines: {available}")

# 2. Choose engine based on needs
if "qtgmc" in available and high_quality_mode:
    engine = DeinterlaceEngine.QTGMC
    preset = "slow"
else:
    engine = DeinterlaceEngine.BWDIF
    preset = None

# 3. Create processor
processor = DeinterlaceProcessor(engine=engine)

# 4. Process video
processor.deinterlace(
    input_path=Path("vhs_capture.mp4"),
    output_path=Path("deinterlaced.mp4"),
    preset=preset or "medium",
    tff=True,  # NTSC VHS
    progress_callback=lambda p: print(f"\rProgress: {p:.1f}%", end="")
)

print("\nComplete!")
```
