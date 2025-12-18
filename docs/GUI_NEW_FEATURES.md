# GUI New Features Guide

## Video Enhancement Options

The VHS Upscaler GUI now includes advanced video enhancement options that were previously only available via command-line. These features are located in the **"Video Enhancement Options"** accordion in the Single Video tab.

## Features Overview

### 1. LUT Color Grading

Apply professional color grading to your videos using .cube LUT files.

**When to Use**:
- Fix VHS color issues (faded colors, color bleeding)
- Add cinematic color grades
- Restore vintage film looks
- Match colors across multiple tapes

**Settings**:

#### LUT File Path
Enter the path to your .cube LUT file.

**Examples**:
```
luts/vhs_restore.cube          # VHS color restoration
luts/cinematic_teal_orange.cube  # Cinematic look
C:\Users\You\LUTs\film_emulation.cube  # Absolute path
```

**Where to Find LUTs**:
- [Free LUTs Collection](https://luts.iwltbap.com/)
- [RocketStock Free LUTs](https://www.rocketstock.com/free-after-effects-templates/35-free-luts-for-color-grading-videos/)
- Create your own in DaVinci Resolve or Adobe Premiere

#### LUT Strength
Control how strongly the LUT is applied (0.0 = off, 1.0 = full strength).

**Recommended Values**:
- **0.5-0.7**: Subtle color correction, maintains natural look
- **0.8-0.9**: Noticeable correction, balanced
- **1.0**: Full LUT effect, most dramatic

**Tips**:
- Start at 0.7 and adjust based on preview
- Lower values preserve more of the original colors
- Higher values create more dramatic transformations

### 2. Face Restoration (GFPGAN)

Use AI to enhance and restore faces in your videos.

**When to Use**:
- Home videos with family/friends
- Wedding videos
- Vintage family footage
- Any video where faces are important

**When to Skip**:
- Landscapes without people
- Animation or cartoons
- Videos where no faces are visible
- Already high-quality modern footage

**Requirements**:
This feature requires GFPGAN to be installed:
```bash
pip install gfpgan basicsr opencv-python torch
```

**Settings**:

#### Enable Face Restoration
Check this box to activate face enhancement.

**What It Does**:
- Detects faces in each frame
- Applies AI enhancement to improve clarity
- Reduces blur and artifacts
- Enhances facial features

#### Restoration Strength
Control how aggressively faces are enhanced (0.0 = minimal, 1.0 = maximum).

**Recommended Values**:
- **0.3-0.5**: Subtle enhancement, natural look
- **0.5-0.7**: Balanced restoration (recommended)
- **0.8-1.0**: Maximum restoration for heavily damaged footage

**Tips**:
- Start at 0.5 for most videos
- Use 0.8+ only for very degraded VHS tapes
- Too high may look artificial or "plastic"
- Different faces may respond differently

#### Face Upscale Factor
Choose how much to upscale detected faces.

**Options**:
- **1x**: No upscaling (just enhancement)
- **2x**: Double resolution (recommended for most cases)
- **4x**: Quadruple resolution (for very small/distant faces)

**Recommendations**:
- Use **2x** for most home videos
- Use **4x** only if faces are tiny in the frame
- Higher upscale = longer processing time
- 4x works best on already upscaled video

### 3. Deinterlacing Method

Choose the algorithm for removing interlacing artifacts from VHS/DVD sources.

**What is Interlacing?**
VHS tapes and DVDs often use interlaced video (480i, 576i), which creates "combing" artifacts when viewed on modern displays. Deinterlacing removes these artifacts.

**When to Use**:
- VHS tapes (always interlaced)
- DVD sources marked as 480i or 576i
- Broadcast TV recordings
- Old camcorder footage

**Settings**:

#### Algorithm
Choose the deinterlacing method.

**yadif** (Yet Another DeInterlacing Filter)
- **Speed**: Fast ⚡⚡⚡
- **Quality**: Good ⭐⭐⭐
- **Best For**: Most VHS/DVD content
- **Processing Time**: Real-time
- **Recommendation**: Default choice for most users

**bwdif** (Bob Weaver DeInterlacing Filter)
- **Speed**: Fast ⚡⚡⚡
- **Quality**: Better ⭐⭐⭐⭐
- **Best For**: Sports, fast motion content
- **Processing Time**: Real-time
- **Recommendation**: Better motion handling than yadif

**w3fdif** (Weston 3-Field DeInterlacing Filter)
- **Speed**: Medium ⚡⚡
- **Quality**: Better ⭐⭐⭐⭐
- **Best For**: Fine detail preservation
- **Processing Time**: 1.5x slower than yadif
- **Recommendation**: When detail is critical

**qtgmc** (Quality Time Gradient Motion Compensation)
- **Speed**: Slow ⚡
- **Quality**: Best ⭐⭐⭐⭐⭐
- **Best For**: Archival, maximum quality
- **Processing Time**: 5-10x slower than yadif
- **Requirements**: Requires VapourSynth installation
- **Recommendation**: Only for archival/preservation projects

#### QTGMC Preset
Only active when QTGMC algorithm is selected.

**Options**:

**draft**
- Fastest QTGMC mode
- Still better than yadif
- Good for testing

**medium** (recommended)
- Balanced quality/speed
- Excellent results
- 2-3x slower than draft

**slow**
- Higher quality
- 4-6x slower than draft
- Recommended for important content

**very_slow**
- Maximum quality
- 8-10x slower than draft
- Only for archival purposes

**Requirements**:
QTGMC requires VapourSynth:
```bash
# Windows
Download from: http://www.vapoursynth.com/

# Install QTGMC plugin
pip install vsutil
# Download QTGMC.py to VapourSynth plugins folder
```

## Example Workflows

### Restoring VHS Family Videos

1. **Upload video** in Single Video tab
2. **Select preset**: "vhs"
3. **Set resolution**: 1080p or 2160p
4. **Video Enhancement Options**:
   - LUT File: `luts/vhs_restore.cube`
   - LUT Strength: 0.7
   - Enable Face Restoration: ✓
   - Face Restore Strength: 0.6
   - Face Upscale: 2x
   - Deinterlace Algorithm: bwdif
5. **Audio Options**:
   - Audio Cleanup: "voice"
   - Surround Upmix: "demucs" (if 5.1 system)
6. **Click "Add to Queue"**

### Professional VHS Archival

1. **Upload video**
2. **Select preset**: "vhs"
3. **Set resolution**: 2160p (4K)
4. **Set CRF**: 15 (higher quality)
5. **Video Enhancement Options**:
   - LUT File: `luts/vhs_color_correct.cube`
   - LUT Strength: 0.8
   - Enable Face Restoration: ✓
   - Face Restore Strength: 0.5
   - Face Upscale: 2x
   - Deinterlace Algorithm: qtgmc
   - QTGMC Preset: slow
6. **Advanced Options**:
   - AI Upscaler: Real-ESRGAN
   - Real-ESRGAN Model: realesrgan-x4plus
   - Noise Reduction: 0.7
7. **Audio Options**:
   - Audio Cleanup: "moderate"
   - Audio Format: "flac" (lossless)

### Quick DVD Upscale

1. **Upload video**
2. **Select preset**: "dvd"
3. **Set resolution**: 1080p
4. **Video Enhancement Options**:
   - Deinterlace Algorithm: bwdif
   - (skip LUT and face restoration for speed)
5. **Click "Add to Queue"**

## Troubleshooting

### "Face restoration requested but module not available"

**Solution**:
```bash
pip install gfpgan basicsr opencv-python torch
```

If using CUDA GPU:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install gfpgan basicsr opencv-python
```

### "QTGMC not available - falling back to yadif"

**Solution**:
1. Install VapourSynth: http://www.vapoursynth.com/
2. Install QTGMC plugin
3. Restart application

**Alternative**: Use bwdif or w3fdif instead (good quality, no dependencies)

### LUT File Not Found

**Checklist**:
- File path is correct
- File exists at specified location
- File has .cube extension
- Path uses forward slashes: `luts/file.cube` not `luts\file.cube`

**Solution**:
Use absolute path if relative path doesn't work:
```
C:/Users/YourName/Documents/LUTs/vhs_restore.cube
```

### Processing Very Slow with QTGMC

**This is normal**. QTGMC is extremely high-quality but slow.

**Options**:
1. Use "draft" or "medium" preset instead of "slow"
2. Switch to bwdif algorithm (much faster, still good)
3. Process overnight for long videos
4. Only use QTGMC for important archival content

## Performance Tips

### Fast Processing
- Use yadif or bwdif deinterlacing
- Skip face restoration if not needed
- Use lower LUT strength (less processing)
- Use 1080p instead of 4K

### Best Quality
- Use QTGMC "slow" preset
- Enable face restoration at 0.6 strength
- Use LUT at 0.7-0.8 strength
- Process at 4K resolution
- Use Real-ESRGAN AI upscaler

### Balanced (Recommended)
- Use bwdif deinterlacing
- Enable face restoration at 0.5 strength
- Use LUT at 0.7 strength
- Process at 1080p
- Use Maxine or Real-ESRGAN upscaler

## Credits

- **GFPGAN**: Face restoration AI by Tencent
- **QTGMC**: Deinterlacing by Didée
- **LUT Support**: FFmpeg lut3d filter
- **VapourSynth**: Video processing framework

## Further Reading

- [LUT Color Grading Tutorial](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
- [Understanding Deinterlacing](https://en.wikipedia.org/wiki/Deinterlacing)
- [GFPGAN Paper](https://arxiv.org/abs/2101.04061)
- [VHS Restoration Best Practices](../BEST_PRACTICES.md)
