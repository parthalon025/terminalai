# VapourSynth Scripts for VHS Upscaler

This directory contains VapourSynth (.vpy) script templates for advanced video processing operations that go beyond what FFmpeg can offer.

## Scripts

### qtgmc_deinterlace.vpy

High-quality deinterlacing template using QTGMC (Quality Time-based Motion Compensation).

**Use case**: Best-in-class deinterlacing for VHS, analog video, and other interlaced sources.

**Requirements**:
- VapourSynth: https://github.com/vapoursynth/vapoursynth
- havsfunc: `pip install havsfunc`
- Source plugin: ffms2 (recommended), lsmas, or bestsource

**Usage**:
1. Edit the configuration section in the script
2. Set input path, field order, and quality preset
3. Run with vspipe:
   ```bash
   vspipe --y4m qtgmc_deinterlace.vpy - | ffmpeg -i pipe: output.mp4
   ```

**Presets**:
- `Draft`: Fast preview quality (~5-10x realtime)
- `Medium`: Balanced quality/speed (~1-2x realtime) - **Recommended**
- `Slow`: High quality (~0.5-1x realtime)
- `Very Slow`: Very high quality (~0.2-0.5x realtime)
- `Placebo`: Maximum quality (~0.1-0.2x realtime)

## VapourSynth Installation

### Windows

1. Download installer: https://github.com/vapoursynth/vapoursynth/releases
2. Install VapourSynth (includes Python bindings)
3. Install havsfunc: `pip install havsfunc`
4. Install source plugin:
   - Download ffms2 plugin from https://github.com/FFMS/ffms2/releases
   - Extract to VapourSynth plugins directory

### Linux

```bash
# Ubuntu/Debian
sudo apt install vapoursynth python3-vapoursynth ffms2

# Arch Linux
sudo pacman -S vapoursynth python-vapoursynth ffms2

# Install havsfunc
pip install havsfunc
```

### macOS

```bash
# Using Homebrew
brew install vapoursynth ffms2

# Install havsfunc
pip install havsfunc
```

## Testing VapourSynth Setup

Run the deinterlace test script to check your setup:

```bash
python vhs_upscaler/test_deinterlace.py --check-setup
```

This will verify:
- VapourSynth availability
- vspipe executable
- Required plugins (ffms2, lsmas, bs)
- havsfunc library

## QTGMC Background

QTGMC (Quality Time-based Motion Compensation) is widely considered the best deinterlacing filter available. It uses sophisticated motion analysis and temporal processing to reconstruct progressive frames from interlaced video.

**Advantages over FFmpeg filters**:
- Better motion compensation
- Cleaner edge reconstruction
- Less combing artifacts
- Superior handling of fast motion
- Temporal noise reduction

**When to use QTGMC**:
- VHS restoration projects (especially high-value content)
- Archival quality deinterlacing
- When processing time is not critical
- Clean VHS or professional analog sources

**When to use FFmpeg filters** (yadif/bwdif):
- Quick previews
- Real-time processing needed
- VapourSynth not available
- Batch processing of large libraries
- Broadcast HD content (already good quality)

## Field Order Detection

To determine if your video is Top Field First (TFF) or Bottom Field First (BFF):

```bash
ffprobe -v quiet -select_streams v:0 -show_entries stream=field_order -of csv=p=0 input.mp4
```

**Common field orders**:
- NTSC (USA): Usually TFF
- PAL (Europe): Usually BFF
- VHS NTSC: TFF
- VHS PAL: BFF
- HD 1080i: Usually TFF

## Performance Tips

1. **Use Draft preset for testing** - Verify settings before committing to slow processing
2. **Process short clips first** - Test on 10-30 second samples
3. **Use hardware encoding** - VapourSynth outputs raw YUV, use NVENC/QSV for encoding
4. **Adjust threads** - VapourSynth will auto-detect, but you can set `core.num_threads`
5. **Monitor memory** - QTGMC is memory-intensive, especially at higher presets

## Integration with VHS Upscaler

The `DeinterlaceProcessor` class in `deinterlace.py` automatically generates and executes QTGMC scripts when the QTGMC engine is selected. You don't need to manually edit these templates unless you want fine-grained control.

**Automatic usage**:
```python
from vhs_upscaler.deinterlace import DeinterlaceProcessor, DeinterlaceEngine

processor = DeinterlaceProcessor(engine=DeinterlaceEngine.QTGMC)
processor.deinterlace(
    input_path=Path("interlaced.mp4"),
    output_path=Path("progressive.mp4"),
    preset="medium",
    tff=True
)
```

**Manual script editing for advanced control**:
1. Copy `qtgmc_deinterlace.vpy` to a working directory
2. Edit configuration parameters
3. Run with vspipe
4. Integrate output into your workflow

## References

- QTGMC Documentation: https://github.com/HomeOfVapourSynthEvolution/havsfunc
- VapourSynth Documentation: http://www.vapoursynth.com/doc/
- Doom9 QTGMC Thread: https://forum.doom9.org/showthread.php?t=156028
- VapourSynth Database: http://vsdb.top/
