# Preset Comparison Module

## Overview

Comprehensive preset comparison tool for VHS upscaler that generates side-by-side comparison grids to evaluate different presets on the same source material.

## Features

- **Multi-Clip Extraction**: Extract multiple clips from different positions in the video
- **Preset Processing**: Process each clip with multiple presets automatically
- **Comparison Grids**: Create horizontal stacks (per clip) and full grid (all clips × all presets)
- **Text Labels**: Automatic text overlay for preset identification
- **Flexible Configuration**: Custom timestamps, clip count, duration
- **Report Generation**: Automatic text report with file sizes and usage instructions

## Architecture

### Processing Flow

```
Input Video
    ↓
┌─────────────────────────────────┐
│ 1. Extract N Clips              │
│    (evenly spaced or custom     │
│     timestamps)                 │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ 2. Process Each Clip            │
│    with M Presets               │
│    (N × M total clips)          │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ 3. Create Individual            │
│    Comparisons                  │
│    (horizontal stack per clip)  │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ 4. Create Full Grid             │
│    (all clips × all presets)    │
└─────────────────────────────────┘
```

### Output Structure

```
output_dir/
├── clips/
│   ├── clip_0_original.mp4
│   ├── clip_0_vhs_standard.mp4
│   ├── clip_0_vhs_clean.mp4
│   ├── clip_1_original.mp4
│   ├── clip_1_vhs_standard.mp4
│   └── ...
├── comparisons/
│   ├── comparison_clip0.mp4    # Horizontal stack for clip 0
│   ├── comparison_clip1.mp4    # Horizontal stack for clip 1
│   ├── comparison_clip2.mp4    # Horizontal stack for clip 2
│   └── comparison_full.mp4     # Full grid (all clips × all presets)
└── comparison_report.txt        # Summary report
```

## Usage

### Modern CLI (Multi-Clip Mode)

```bash
# Basic multi-clip comparison (3 clips, all default presets)
vhs-upscale test-presets video.mp4 -o test_output/ --multi-clip

# Compare specific presets
vhs-upscale test-presets video.mp4 -o test_output/ \
    --multi-clip \
    --presets vhs_standard,vhs_clean,vhs_heavy

# Custom number of clips
vhs-upscale test-presets video.mp4 -o test_output/ \
    --multi-clip \
    --clip-count 5 \
    --duration 10

# Custom timestamps (30s, 90s, 150s)
vhs-upscale test-presets video.mp4 -o test_output/ \
    --multi-clip \
    --timestamps "30,90,150"

# Keep individual processed clips
vhs-upscale test-presets video.mp4 -o test_output/ \
    --multi-clip \
    --keep-temp
```

### Legacy Single-Clip Mode

```bash
# Test all default presets on a single clip
vhs-upscale test-presets video.mp4 -o test_output/

# Test specific presets with custom start time
vhs-upscale test-presets video.mp4 -o test_output/ \
    --presets vhs,dvd,clean \
    --start 120 \
    --duration 15

# Create comparison grid (2x2 layout)
vhs-upscale test-presets video.mp4 -o test_output/ \
    --create-grid \
    --grid-layout 2x2
```

### Python API

```python
from pathlib import Path
from vhs_upscaler.comparison import generate_preset_comparison

# Generate comparison suite
comparisons = generate_preset_comparison(
    input_path=Path("old_vhs.mp4"),
    output_dir=Path("./test_output"),
    presets=["vhs_standard", "vhs_clean", "vhs_heavy"],
    clip_count=3,
    clip_duration=10
)

# Returns dict of generated files
# {
#     "clip_0": Path("comparisons/comparison_clip0.mp4"),
#     "clip_1": Path("comparisons/comparison_clip1.mp4"),
#     "clip_2": Path("comparisons/comparison_clip2.mp4"),
#     "full_grid": Path("comparisons/comparison_full.mp4")
# }
```

### Advanced Python Usage

```python
from pathlib import Path
from vhs_upscaler.comparison import PresetComparator, ComparisonConfig

# Create custom configuration
config = ComparisonConfig(
    input_path=Path("video.mp4"),
    output_dir=Path("./comparisons"),
    presets=["vhs_standard", "vhs_clean", "vhs_heavy", "clean"],
    clip_count=3,
    clip_duration=10,
    timestamps=[30, 90, 150],  # Custom timestamps
    include_original=True,
    label_position="top",
    label_font_size=28,
    label_bg_color="black@0.8",
    label_text_color="white",
    ffmpeg_path="ffmpeg",
    keep_individual_clips=True
)

# Generate comparison suite
comparator = PresetComparator(config)
comparisons = comparator.generate_comparison_suite()

# Generate report
report = comparator.generate_comparison_report(comparisons)
print(report)
```

## Configuration Options

### ComparisonConfig Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `input_path` | Path | Required | Source video file |
| `output_dir` | Path | Required | Output directory |
| `presets` | List[str] | Required | List of preset names to test |
| `clip_count` | int | 3 | Number of clips to extract |
| `clip_duration` | int | 10 | Clip duration in seconds |
| `timestamps` | List[int] | None | Custom timestamps (overrides clip_count) |
| `include_original` | bool | True | Include original in comparisons |
| `label_position` | str | "top" | Label position (top, bottom, overlay) |
| `label_font_size` | int | 24 | Font size for labels |
| `label_bg_color` | str | "black@0.7" | Label background color |
| `label_text_color` | str | "white" | Label text color |
| `ffmpeg_path` | str | "ffmpeg" | Path to ffmpeg executable |
| `keep_individual_clips` | bool | True | Keep individual processed clips |

## Example Output

### Comparison Report

```
======================================================================
Preset Comparison Report
======================================================================

Input Video: old_vhs_tape.mp4
Output Directory: D:\test_output

Presets Tested:
  - vhs_standard
  - vhs_clean
  - vhs_heavy

Clips Extracted: 3
Clip Duration: 10 seconds

Generated Files:
  - clip_0: comparison_clip0.mp4 (45.2 MB)
  - clip_1: comparison_clip1.mp4 (43.8 MB)
  - clip_2: comparison_clip2.mp4 (46.1 MB)
  - full_grid: comparison_full.mp4 (135.7 MB)

======================================================================
How to Use:
  1. Open individual clip comparisons to see detailed preset differences
  2. Open full grid to see all clips and presets at once
  3. Choose the preset that best matches your quality requirements
======================================================================
```

## Performance Considerations

### Processing Time Estimates

For a 60-minute source video with 3 clips @ 10 seconds each:

| Presets | Clips | Total Processing Time | Output Size |
|---------|-------|-----------------------|-------------|
| 3 | 3 | ~15 minutes | ~150 MB |
| 5 | 3 | ~25 minutes | ~250 MB |
| 3 | 5 | ~25 minutes | ~300 MB |
| 5 | 5 | ~45 minutes | ~500 MB |

*Times assume Real-ESRGAN upscaling on GPU*

### Optimization Tips

1. **Use Shorter Clips**: 5-10 seconds is usually sufficient for quality evaluation
2. **Limit Presets**: Test 2-4 presets most relevant to your content
3. **Strategic Timestamps**: Choose clips from different scenes (dark, bright, motion, static)
4. **GPU Acceleration**: Use NVIDIA GPU for faster Real-ESRGAN processing
5. **Clean Temp Files**: Use `--keep-temp=false` to save disk space

## Use Cases

### 1. Quality Evaluation

Compare different presets to find the best quality/processing-time trade-off:

```bash
vhs-upscale test-presets tape.mp4 -o quality_test/ \
    --multi-clip \
    --presets vhs_standard,vhs_clean,vhs_heavy \
    --clip-count 3
```

### 2. Before/After Demonstration

Show clients the improvement from various presets:

```bash
vhs-upscale test-presets client_video.mp4 -o demo/ \
    --multi-clip \
    --timestamps "30,120,240" \
    --duration 5
```

### 3. Parameter Tuning

Test subtle variations in preset settings:

```bash
# Create custom presets in vhs_upscale.py, then:
vhs-upscale test-presets video.mp4 -o tuning_test/ \
    --multi-clip \
    --presets vhs_denoise_low,vhs_denoise_med,vhs_denoise_high
```

### 4. Content-Specific Testing

Test different content types (action, dialogue, animation):

```bash
# Action scene
vhs-upscale test-presets action.mp4 -o action_test/ \
    --timestamps "45" --duration 10 --multi-clip

# Dialogue scene
vhs-upscale test-presets dialogue.mp4 -o dialogue_test/ \
    --timestamps "120" --duration 10 --multi-clip
```

## Troubleshooting

### Issue: "Failed to extract clip"

**Cause**: Invalid timestamp or ffmpeg error

**Solution**:
```bash
# Check video duration first
ffprobe -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 video.mp4

# Use valid timestamps within video duration
vhs-upscale test-presets video.mp4 -o test/ \
    --timestamps "30,60,90"  # Must be < duration
```

### Issue: "Processing failed for preset X"

**Cause**: Missing dependencies or invalid preset configuration

**Solution**:
```bash
# Check preset exists
python -c "from vhs_upscaler.presets import PRESETS; print(list(PRESETS.keys()))"

# Verify dependencies
vhs-upscale upscale test_clip.mp4 -o test.mp4 -p vhs_standard
```

### Issue: Grid creation fails

**Cause**: Videos have different resolutions or frame rates

**Solution**: The comparison module automatically handles this by processing all clips with the same settings. If issues persist:

```bash
# Process clips individually and check outputs
ls -lh test_output/clips/

# Verify all clips have same resolution
for f in test_output/clips/*.mp4; do
    ffprobe -v error -select_streams v:0 \
        -show_entries stream=width,height "$f"
done
```

### Issue: Out of disk space

**Cause**: Multiple clips × multiple presets = large storage requirement

**Solution**:
```bash
# Reduce clip count
vhs-upscale test-presets video.mp4 -o test/ \
    --multi-clip --clip-count 2

# Use shorter clips
vhs-upscale test-presets video.mp4 -o test/ \
    --multi-clip --duration 5

# Don't keep individual clips
vhs-upscale test-presets video.mp4 -o test/ \
    --multi-clip --no-keep-temp
```

## Future Enhancements

Potential improvements for future versions:

1. **Quality Metrics**: Automatic PSNR/SSIM/VMAF calculation
2. **Statistical Summary**: Mean/median quality scores per preset
3. **Interactive Viewer**: Web-based comparison viewer
4. **Preset Recommendations**: AI-based preset selection
5. **A/B Testing**: Blind comparison mode for subjective evaluation
6. **Export Formats**: HTML reports, CSV metrics, PDF summaries

## References

- [FFmpeg Grid Filter](https://trac.ffmpeg.org/wiki/FilteringGuide#StackingVideos)
- [FFmpeg Drawtext](https://ffmpeg.org/ffmpeg-filters.html#drawtext-1)
- [Video Comparison Best Practices](https://www.streamingmedia.com/Articles/ReadArticle.aspx?ArticleID=132067)
