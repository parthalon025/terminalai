"""
QTGMC Deinterlacing Template for VapourSynth
==============================================

This is a standalone VapourSynth script template for high-quality deinterlacing
using QTGMC (Quality Time-based Motion Compensation).

QTGMC is considered the best deinterlacing filter available, especially for
VHS and analog video sources. It uses motion compensation to reconstruct frames
with minimal artifacts.

Usage:
    1. Replace the placeholders below with your actual values:
       - INPUT_VIDEO_PATH: Path to your interlaced video
       - FIELD_ORDER: 2 for TFF (top field first), 1 for BFF (bottom field first)
       - QTGMC_PRESET: "Draft", "Medium", "Slow", "Very Slow", or "Placebo"

    2. Run with vspipe:
       vspipe --y4m qtgmc_deinterlace.vpy - | ffmpeg -i pipe: output.mp4

    Or preview with VapourSynth Editor/vspreview

Requirements:
    - VapourSynth: https://github.com/vapoursynth/vapoursynth
    - havsfunc: pip install havsfunc
    - ffms2 or lsmas source plugin

QTGMC Preset Guide:
    - Draft: Fast preview, good for testing (fastest)
    - Medium: Balanced quality/speed, recommended for most content
    - Slow: High quality, better motion handling
    - Very Slow: Very high quality, excellent for restoration
    - Placebo: Maximum quality, very slow (diminishing returns)

Field Order Detection:
    - Top Field First (TFF): Most NTSC broadcasts, most VHS
    - Bottom Field First (BFF): PAL broadcasts, some professional cameras
    - Use ffprobe to detect: ffprobe -show_streams video.mp4 | grep field_order

Common VHS Settings:
    - NTSC VHS: TFF (field_order=2), 29.97fps, 720x480
    - PAL VHS: BFF (field_order=1), 25fps, 720x576
"""

import vapoursynth as vs
from vapoursynth import core

# ============================================================================
# Configuration - EDIT THESE VALUES
# ============================================================================

# Input video path (use raw string with r'' to handle Windows paths)
INPUT_VIDEO_PATH = r"C:\path\to\your\interlaced_video.mp4"

# Field order: 2 = TFF (top field first), 1 = BFF (bottom field first)
FIELD_ORDER = 2  # Change to 1 for BFF

# QTGMC preset: "Draft", "Medium", "Slow", "Very Slow", "Placebo"
QTGMC_PRESET = "Medium"

# Top field first flag (True for TFF, False for BFF)
TFF = True  # Change to False for BFF

# ============================================================================
# Advanced QTGMC Parameters (optional tuning)
# ============================================================================

# Source matching (0-3):
#   0 = disabled
#   1 = match to progressive source
#   2 = match to interlaced source
#   3 = auto-detect and match (recommended)
SOURCE_MATCH = 3

# Lossless mode (0-2):
#   0 = standard quality
#   1 = higher quality
#   2 = highest quality (recommended for archival)
LOSSLESS = 2

# Sharpness (0.0-1.0, default 0.2):
#   Higher = sharper output, but may enhance noise
#   Lower = softer, better for noisy sources
SHARPNESS = 0.2

# Noise removal (-1.0 to disable, 0.0-10.0 for strength):
#   Useful for VHS sources with temporal noise
#   Start with 0.0 (disabled) and increase if needed
NOISE_REDUCTION = 0.0

# FPS divisor (1 or 2):
#   1 = output same FPS (bob deinterlacing, 25i -> 50p or 30i -> 60p)
#   2 = output half FPS (25i -> 25p or 30i -> 30p)
FPS_DIVISOR = 1

# ============================================================================
# Processing Pipeline
# ============================================================================

# Import havsfunc for QTGMC
try:
    import havsfunc as haf
except ImportError as e:
    raise ImportError(
        "havsfunc not found. Install with: pip install havsfunc\n"
        "Or download from: https://github.com/HomeOfVapourSynthEvolution/havsfunc"
    ) from e

# Load video using best available source filter
# Priority: ffms2 > lsmas > bestsource
try:
    # Try ffms2 (FFmpegSource2) - excellent compatibility
    clip = core.ffms2.Source(source=INPUT_VIDEO_PATH)
    print(f"Loaded video using ffms2: {INPUT_VIDEO_PATH}")
except AttributeError:
    try:
        # Try lsmas (L-SMASH) - good for MP4/MKV
        clip = core.lsmas.LWLibavSource(source=INPUT_VIDEO_PATH)
        print(f"Loaded video using lsmas: {INPUT_VIDEO_PATH}")
    except AttributeError:
        try:
            # Try bestsource - newest and most accurate
            clip = core.bs.VideoSource(source=INPUT_VIDEO_PATH)
            print(f"Loaded video using bestsource: {INPUT_VIDEO_PATH}")
        except AttributeError:
            raise RuntimeError(
                "No source filter found. Install one of:\n"
                "  - ffms2: https://github.com/FFMS/ffms2\n"
                "  - lsmas: https://github.com/AkarinVS/L-SMASH-Works\n"
                "  - bestsource: https://github.com/vapoursynth/bestsource"
            )

# Set field order metadata
# _FieldBased property: 0 = progressive, 1 = BFF, 2 = TFF
clip = core.std.SetFrameProp(clip, prop="_FieldBased", intval=FIELD_ORDER)

# Print input video info
print(f"Input format: {clip.format.name}")
print(f"Resolution: {clip.width}x{clip.height}")
print(f"FPS: {clip.fps_num}/{clip.fps_den} ({clip.fps_num/clip.fps_den:.3f})")
print(f"Frames: {clip.num_frames}")
print(f"Field order: {'TFF' if FIELD_ORDER == 2 else 'BFF'}")

# ============================================================================
# Apply QTGMC Deinterlacing
# ============================================================================

clip = haf.QTGMC(
    clip,
    Preset=QTGMC_PRESET,
    TFF=TFF,
    SourceMatch=SOURCE_MATCH,
    Lossless=LOSSLESS,
    Sharpness=SHARPNESS,
    NoiseRestore=NOISE_REDUCTION if NOISE_REDUCTION > 0 else None,
    FPSDivisor=FPS_DIVISOR
)

# Print output info
print(f"\nQTGMC settings:")
print(f"  Preset: {QTGMC_PRESET}")
print(f"  TFF: {TFF}")
print(f"  SourceMatch: {SOURCE_MATCH}")
print(f"  Lossless: {LOSSLESS}")
print(f"  FPSDivisor: {FPS_DIVISOR}")
print(f"\nOutput format: {clip.format.name}")
print(f"Output FPS: {clip.fps_num}/{clip.fps_den} ({clip.fps_num/clip.fps_den:.3f})")
print(f"Output frames: {clip.num_frames}")

# ============================================================================
# Optional Post-Processing
# ============================================================================

# Uncomment to resize output (useful if source has incorrect aspect ratio)
# clip = core.resize.Spline36(clip, width=720, height=480)

# Uncomment to convert to 8-bit for compatibility (QTGMC outputs 8-bit by default)
# clip = core.resize.Point(clip, format=vs.YUV420P8)

# Uncomment to add temporal stabilization (reduces jitter)
# clip = haf.Stab(clip, dxmax=2, dymax=2)

# Uncomment for additional noise reduction (use conservatively)
# clip = haf.SMDegrain(clip, tr=2, thSAD=200)

# ============================================================================
# Set Output
# ============================================================================

clip.set_output()

# ============================================================================
# Usage Examples
# ============================================================================

"""
1. Process and encode to MP4:
   vspipe --y4m qtgmc_deinterlace.vpy - | ffmpeg -i pipe: -c:v libx264 -crf 18 -preset slow output.mp4

2. Process and encode to high-quality archival format:
   vspipe --y4m qtgmc_deinterlace.vpy - | ffmpeg -i pipe: -c:v libx265 -crf 18 -preset slow -pix_fmt yuv420p10le output.mkv

3. Preview in VapourSynth Editor:
   - Open this .vpy file in VapourSynth Editor (vspreview)
   - Use left/right arrows to navigate frames
   - Compare with source by toggling between clips

4. Benchmark processing speed:
   vspipe --info qtgmc_deinterlace.vpy -

5. Process specific frame range (frames 100-200):
   vspipe --y4m --start 100 --end 200 qtgmc_deinterlace.vpy - | ffmpeg -i pipe: output.mp4

6. Multi-pass encoding with FFmpeg:
   vspipe --y4m qtgmc_deinterlace.vpy - | ffmpeg -i pipe: -c:v libx264 -preset slow -b:v 5000k -pass 1 -f null -
   vspipe --y4m qtgmc_deinterlace.vpy - | ffmpeg -i pipe: -c:v libx264 -preset slow -b:v 5000k -pass 2 output.mp4
"""
