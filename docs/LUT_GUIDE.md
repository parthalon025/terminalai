# LUT (Look-Up Table) Support Guide

## Table of Contents

1. [What are LUTs?](#what-are-luts)
2. [How LUTs Work](#how-luts-work)
3. [Using LUTs in VHS Upscaler](#using-luts-in-vhs-upscaler)
4. [Included LUTs](#included-luts)
5. [CLI Examples](#cli-examples)
6. [Creating Custom LUTs](#creating-custom-luts)
7. [Free LUT Resources](#free-lut-resources)
8. [Technical Details](#technical-details)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## What are LUTs?

**LUT** (Look-Up Table) is a mathematical color transformation used in professional video production and color grading. Think of it as a color "filter" that maps input colors to output colors in a precise, reproducible way.

### Why Use LUTs?

- **Professional color grading**: Apply Hollywood-style color grades
- **Consistency**: Same look across multiple videos
- **VHS restoration**: Correct typical VHS color degradation
- **Creative looks**: Vintage film, modern cinematic, or custom aesthetics
- **Time-saving**: One-click professional color correction

### LUT vs. Filters

| Feature | LUT | Instagram-style Filter |
|---------|-----|------------------------|
| Precision | Mathematical, exact | Approximate |
| Professional use | Industry standard | Consumer apps |
| Repeatability | 100% consistent | May vary |
| Customization | Fully customizable | Limited |
| File format | .cube, .3dl | Proprietary |

---

## How LUTs Work

### 3D LUTs Explained

A **3D LUT** is a cube of color transformations:

```
Input Color (R, G, B) → LUT → Output Color (R', G', B')
```

**Example transformation:**
- Input: `RGB(255, 128, 64)` → Orange color
- LUT transforms: Warm vintage look
- Output: `RGB(270, 135, 55)` → Warmer orange with lifted values

### LUT Size

VHS Upscaler uses **33x33x33** 3D LUTs:
- **33 points** per color channel (R, G, B)
- **35,937 total color mappings** (33³)
- Industry-standard size (Rec. 709)
- Excellent quality vs. file size balance

### Color Space

LUTs operate in **normalized RGB space** (0.0 to 1.0):
- `0.0` = Black (RGB 0)
- `0.5` = Middle gray (RGB 128)
- `1.0` = White (RGB 255)

---

## Using LUTs in VHS Upscaler

### Basic Usage

Apply a LUT during upscaling:

```bash
vhs-upscale upscale input.mp4 -o output.mp4 --lut luts/vhs_restore.cube
```

### LUT Strength Control

Blend between original and LUT-transformed colors (0.0 to 1.0):

```bash
# 70% LUT intensity (subtle)
vhs-upscale upscale input.mp4 -o output.mp4 \
  --lut luts/warm_vintage.cube \
  --lut-strength 0.7

# 100% LUT intensity (full effect)
vhs-upscale upscale input.mp4 -o output.mp4 \
  --lut luts/cool_modern.cube \
  --lut-strength 1.0
```

**LUT Strength values:**
- `0.0` = No LUT effect (original colors)
- `0.5` = 50% blend (balanced)
- `0.7` = 70% blend (recommended default)
- `1.0` = 100% LUT (full transformation)

### Pipeline Position

LUTs are applied in the **preprocessing stage**, after denoising but before upscaling:

```
1. Deinterlace (if needed)
2. Denoise
3. → LUT COLOR GRADING ←
4. AI Upscale
5. Encode
```

This ensures:
- Clean color correction (after noise removal)
- Upscaler works with corrected colors
- Consistent results

---

## Included LUTs

VHS Upscaler ships with three professionally-crafted LUTs:

### 1. vhs_restore.cube

**Purpose**: VHS color restoration

**What it does:**
- Corrects typical VHS blue channel loss
- Boosts saturation (VHS desaturates over time)
- Warms the image (counteracts VHS coolness)
- Lifts shadows slightly
- Reduces blue cast

**Best for:**
- Home video restoration
- VHS tape transfers
- Betamax/Video8 footage
- Analog camcorder recordings

**Recommended strength**: `0.7` to `1.0`

**Example:**
```bash
vhs-upscale upscale old_vhs_tape.mp4 -o restored.mp4 \
  -p vhs_heavy \
  --lut luts/vhs_restore.cube \
  --lut-strength 0.8
```

---

### 2. warm_vintage.cube

**Purpose**: Warm nostalgic film look

**What it does:**
- Golden/amber color shift
- Lifted blacks (faded vintage aesthetic)
- Reduced contrast (film-like)
- Desaturated highlights
- Creates nostalgic warmth

**Best for:**
- Home movies
- Vintage aesthetic videos
- Wedding/family videos
- Music videos (retro style)
- Documentary footage

**Recommended strength**: `0.6` to `0.9`

**Example:**
```bash
vhs-upscale upscale family_video.mp4 -o nostalgic.mp4 \
  -p dvd_progressive \
  --lut luts/warm_vintage.cube \
  --lut-strength 0.7
```

---

### 3. cool_modern.cube

**Purpose**: Modern cinematic look

**What it does:**
- Teal/cyan color shift (Hollywood style)
- Crushed blacks (deep shadows)
- Increased contrast
- Boosted midtone saturation
- Cool/clean aesthetic

**Best for:**
- Modern talking head videos
- Vlogs and YouTube content
- Corporate videos
- Interviews
- Contemporary documentaries

**Recommended strength**: `0.5` to `0.8`

**Example:**
```bash
vhs-upscale upscale interview.mp4 -o modern.mp4 \
  -p clean \
  --lut luts/cool_modern.cube \
  --lut-strength 0.6 \
  --face-restore
```

---

## CLI Examples

### Example 1: VHS Tape Restoration

Complete VHS restoration with color correction:

```bash
vhs-upscale upscale vhs_wedding_1985.mp4 -o wedding_restored.mp4 \
  -r 1080 \
  -p vhs_heavy \
  --lut luts/vhs_restore.cube \
  --lut-strength 0.9 \
  --encoder hevc_nvenc \
  --crf 18
```

### Example 2: Vintage Home Movie Look

Create a warm, nostalgic aesthetic:

```bash
vhs-upscale upscale family_vacation.mp4 -o vacation_vintage.mp4 \
  -r 1080 \
  -p dvd_interlaced \
  --lut luts/warm_vintage.cube \
  --lut-strength 0.75 \
  --audio-enhance light
```

### Example 3: Modern YouTube Video

Clean, contemporary look for talking head content:

```bash
vhs-upscale upscale interview_raw.mp4 -o interview_final.mp4 \
  -r 2160 \
  -p clean \
  --lut luts/cool_modern.cube \
  --lut-strength 0.6 \
  --face-restore \
  --face-restore-strength 0.5
```

### Example 4: Subtle Color Correction

Very light LUT application:

```bash
vhs-upscale upscale concert.mp4 -o concert_graded.mp4 \
  --lut luts/warm_vintage.cube \
  --lut-strength 0.3  # Very subtle
```

### Example 5: Batch Processing with LUT

Process entire folder with consistent color grading:

```bash
vhs-upscale batch ./input_videos/ ./output_videos/ \
  -p vhs_standard \
  --lut luts/vhs_restore.cube \
  --lut-strength 0.8
```

### Example 6: No LUT (Disable)

Process without LUT (default behavior):

```bash
vhs-upscale upscale video.mp4 -o output.mp4 -p vhs
# LUT is optional, no --lut flag = no LUT applied
```

---

## Creating Custom LUTs

### Using DaVinci Resolve (Professional)

**DaVinci Resolve** is the industry-standard color grading tool (free version available):

#### Step 1: Import Your Video
1. Open DaVinci Resolve
2. Import your source video
3. Drag to timeline in the **Color** page

#### Step 2: Grade Your Video
1. Use **Color Wheels** for primary correction
2. Apply **Curves** for precise adjustments
3. Add **Saturation/Hue** shifts
4. Adjust **Contrast** and **Brightness**

#### Step 3: Export LUT
1. Right-click on the node
2. Select **Generate LUT**
3. Choose format: **Cube (.cube)**
4. Set size: **33**
5. Save to `luts/my_custom.cube`

#### Step 4: Test in VHS Upscaler
```bash
vhs-upscale upscale test.mp4 -o result.mp4 \
  --lut luts/my_custom.cube \
  --lut-strength 1.0
```

**DaVinci Resolve Download**: https://www.blackmagicdesign.com/products/davinciresolve

---

### Using Adobe After Effects

#### Step 1: Create Composition
1. Import source video
2. Create new composition

#### Step 2: Apply Color Corrections
1. Add **Lumetri Color** effect
2. Adjust **Basic Correction**
3. Add **Creative** looks
4. Fine-tune with **Curves**

#### Step 3: Export LUT
1. Right-click on Lumetri Color effect
2. Select **Export LUT**
3. Choose **CUBE (.cube)** format
4. Set resolution: **33**
5. Save LUT file

#### Step 4: Use in VHS Upscaler
```bash
vhs-upscale upscale video.mp4 -o output.mp4 \
  --lut luts/ae_custom.cube
```

---

### Using Online LUT Generators

**Free web tools** for creating LUTs:

#### LUT Creator (Web-based)
- URL: https://lut-creator.com
- Upload reference image
- Adjust color sliders
- Export .cube LUT

#### Photoshop to LUT
1. Open image in Photoshop
2. Apply **Color Adjustments** (Curves, Levels, etc.)
3. Use **LUT Export** plugin
4. Export as .cube file

---

### LUT Creation Best Practices

**Do:**
- Test with representative footage
- Make gradual adjustments
- Export at 33x33x33 size (standard)
- Use .cube format (widely compatible)
- Document your LUT's purpose

**Don't:**
- Apply extreme transformations (can cause banding)
- Clip colors to pure black/white
- Stack multiple strong LUTs
- Use incompatible formats (.3dl is different)
- Forget to test at different LUT strengths

---

## Free LUT Resources

### High-Quality Free LUT Packs

#### 1. **RocketStock Free LUTs**
- URL: https://www.rocketstock.com/free-after-effects-templates/35-free-luts/
- **35 professional LUTs**
- Cinematic looks
- Compatible with VHS Upscaler

#### 2. **Ground Control Free Cinematic LUTs**
- URL: https://groundcontrolcolor.com/products/free-cinematic-luts
- Film-inspired LUTs
- High quality
- Popular for YouTube creators

#### 3. **Lutify.me Free LUTs**
- URL: https://lutify.me/free-luts/
- Professional color grading
- Various film stocks
- Regular updates

#### 4. **FreshLUTs Free Pack**
- URL: https://freshluts.com/free-luts/
- Modern cinematic looks
- Easy to use
- .cube format

#### 5. **SmallHD Free LUTs**
- URL: https://www.smallhd.com/pages/luts
- Broadcast-quality LUTs
- Monitor calibration LUTs
- Technical and creative

### Installing Downloaded LUTs

1. Download LUT pack (.zip file)
2. Extract .cube files
3. Copy to VHS Upscaler `luts/` folder:
   ```bash
   cp ~/Downloads/cinematic.cube ./luts/
   ```
4. Use in command:
   ```bash
   vhs-upscale upscale video.mp4 -o output.mp4 \
     --lut luts/cinematic.cube
   ```

---

## Technical Details

### .cube Format Specification

**Header:**
```
# LUT name
# Description
LUT_3D_SIZE 33
```

**Data:**
```
R G B  (normalized 0.0 to 1.0, 6 decimal places)
0.000000 0.000000 0.000000  # Black
0.031250 0.000000 0.000000
...
1.000000 1.000000 1.000000  # White
```

**Total lines**: 35,937 data lines (33³) + header

### FFmpeg LUT Filter

VHS Upscaler uses FFmpeg's `lut3d` filter internally:

```bash
ffmpeg -i input.mp4 -vf "lut3d=file=luts/my_lut.cube:interp=tetrahedral" output.mp4
```

**Interpolation methods:**
- `tetrahedral` (default, best quality)
- `trilinear` (faster, good quality)
- `cubic` (slowest, highest quality)

VHS Upscaler uses **tetrahedral** for optimal speed/quality.

### LUT Strength Implementation

Blending is done via FFmpeg's mix filter:

```bash
# Pseudo-code for 0.7 strength
original_video → split → [stream1, stream2]
stream1 → lut3d(lut_file) → lut_output
stream2 → original
lut_output + original → mix(weights=0.7:0.3) → final_output
```

This ensures smooth blending at any strength value.

---

## Troubleshooting

### Issue: "LUT file not found"

**Symptom:**
```
Error: LUT file not found: luts/my_lut.cube
```

**Solution:**
1. Check file exists:
   ```bash
   ls luts/my_lut.cube
   ```
2. Use absolute path:
   ```bash
   --lut /full/path/to/luts/my_lut.cube
   ```
3. Verify file permissions:
   ```bash
   chmod 644 luts/my_lut.cube
   ```

---

### Issue: "Invalid LUT format"

**Symptom:**
```
Error: Could not load LUT: invalid format
```

**Solution:**
1. Check LUT header:
   ```bash
   head -n 5 luts/my_lut.cube
   ```
   Should start with `LUT_3D_SIZE 33`

2. Verify .cube format (not .3dl or other)

3. Re-download or re-export LUT

---

### Issue: Colors look wrong/extreme

**Symptom:**
- Over-saturated colors
- Banding artifacts
- Clipped highlights/shadows

**Solution:**
1. Reduce LUT strength:
   ```bash
   --lut-strength 0.5  # Lower intensity
   ```

2. Check LUT is intended for Rec. 709 (not Log or RAW)

3. Use different LUT designed for video (not photography)

---

### Issue: No visible effect

**Symptom:**
LUT applied but no color change visible

**Solution:**
1. Increase LUT strength:
   ```bash
   --lut-strength 1.0  # Full intensity
   ```

2. Check LUT isn't an identity LUT (no transformation)

3. Try a different LUT to verify functionality:
   ```bash
   --lut luts/warm_vintage.cube  # Very visible effect
   ```

---

### Issue: Performance degradation

**Symptom:**
Processing much slower with LUT enabled

**Solution:**
- **Normal**: LUT adds minimal overhead (~5-10%)
- If significantly slower, check:
  1. LUT file size (should be ~2-3 MB for 33³)
  2. Hardware acceleration enabled
  3. Disk I/O speed (slow drive?)

**Optimization:**
```bash
# Use GPU encoding to compensate
--encoder hevc_nvenc
```

---

### Issue: LUT strength has no effect

**Symptom:**
Changing `--lut-strength` doesn't change output

**Solution:**
1. Verify syntax:
   ```bash
   --lut luts/my_lut.cube --lut-strength 0.5
   ```
   (both flags required)

2. Check logs for LUT strength value

3. Ensure LUT strength is between 0.0 and 1.0

---

## Best Practices

### When to Use LUTs

**Good use cases:**
- VHS restoration (color correction)
- Consistent look across multiple videos
- Recreating film looks
- Professional color grading
- YouTube/social media content

**Not recommended:**
- Already professionally color-graded footage
- Log/RAW footage (needs dedicated workflow)
- HDR content (requires HDR LUTs)

---

### Choosing the Right LUT

**VHS/Analog sources:**
→ `vhs_restore.cube`

**Home movies/nostalgia:**
→ `warm_vintage.cube`

**Modern talking heads:**
→ `cool_modern.cube`

**Creative projects:**
→ Download cinematic LUT packs

**Already color-graded:**
→ No LUT (leave as-is)

---

### LUT Strength Guidelines

| Strength | Use Case | Effect |
|----------|----------|--------|
| 0.3-0.5 | Subtle correction | Barely noticeable |
| 0.5-0.7 | Balanced grading | Visible but natural |
| 0.7-0.9 | Strong look | Obvious transformation |
| 0.9-1.0 | Maximum effect | Full LUT application |

**Recommendation**: Start at `0.7` and adjust based on preview.

---

### Combining with Other Features

**LUT + Face Restoration:**
```bash
vhs-upscale upscale interview.mp4 -o output.mp4 \
  --lut luts/cool_modern.cube \
  --lut-strength 0.6 \
  --face-restore \
  --face-restore-strength 0.5
```

**LUT + HDR:**
```bash
# Note: Use HDR-specific LUTs for HDR output
vhs-upscale upscale video.mp4 -o output.mp4 \
  --lut luts/hdr_rec2020.cube \
  --hdr hdr10
```

**LUT + Audio Enhancement:**
```bash
vhs-upscale upscale concert.mp4 -o output.mp4 \
  --lut luts/warm_vintage.cube \
  --audio-enhance music \
  --audio-upmix surround
```

---

### Testing Your LUT

**Create a test sequence:**

1. Use a known reference (e.g., color bars):
   ```bash
   ffmpeg -f lavfi -i smptebars=size=1920x1080:rate=30 \
     -t 10 test_bars.mp4
   ```

2. Apply LUT:
   ```bash
   vhs-upscale upscale test_bars.mp4 -o bars_graded.mp4 \
     --lut luts/my_lut.cube --lut-strength 1.0
   ```

3. Compare side-by-side in video player

4. Check for:
   - Color clipping (loss of detail)
   - Banding (smooth gradients)
   - Proper contrast
   - Accurate skin tones

---

### Quality Control Checklist

Before using a LUT in production:

- [ ] Test on sample footage
- [ ] Check multiple scenes (bright, dark, colorful)
- [ ] Verify skin tones look natural
- [ ] No banding or posterization
- [ ] Shadows aren't crushed
- [ ] Highlights aren't blown out
- [ ] LUT strength is appropriate
- [ ] Consistent results across clips

---

## Advanced Topics

### Creating VHS-Specific LUTs

**VHS color science:**
- Chroma phase shift (colors bleed)
- Blue channel degradation
- Luma separation issues
- Desaturation over time

**Corrective LUT approach:**
1. Analyze VHS color cast (often blue/cool)
2. Warm the image (red/yellow boost)
3. Lift saturation (especially reds)
4. Correct chroma phase
5. Subtle shadow lift

**Example Python LUT generator** (see `scripts/generate_luts.py`).

---

### LUT Stacking

**Not recommended**, but possible:

Apply LUT externally, then upscale with second LUT:
```bash
# Step 1: Apply first LUT
ffmpeg -i input.mp4 -vf "lut3d=lut1.cube" temp.mp4

# Step 2: Upscale with second LUT
vhs-upscale upscale temp.mp4 -o final.mp4 --lut lut2.cube
```

**Better approach**: Combine LUTs in DaVinci Resolve, export single LUT.

---

### Custom LUT Strength Per Clip

For batch processing with varying strength:

```bash
# Script example
for video in *.mp4; do
  # Adjust strength based on filename or analysis
  if [[ $video == *"bright"* ]]; then
    strength=0.5
  else
    strength=0.8
  fi

  vhs-upscale upscale "$video" -o "graded_$video" \
    --lut luts/vhs_restore.cube \
    --lut-strength $strength
done
```

---

## Summary

LUTs provide professional color grading with:
- **Precision**: Mathematical color transformation
- **Consistency**: Reproducible results
- **Flexibility**: Adjustable strength
- **Compatibility**: Industry-standard .cube format

**Quick start:**
```bash
vhs-upscale upscale input.mp4 -o output.mp4 \
  --lut luts/vhs_restore.cube \
  --lut-strength 0.7
```

For more help, see:
- **VHS Upscaler README**: [README.md](../README.md)
- **Face Restoration Guide**: [FACE_RESTORATION.md](FACE_RESTORATION.md)
- **Audio Enhancement**: [AUDIO_GUIDE.md](AUDIO_GUIDE.md)

---

**Generated by VHS Upscaler Documentation**
Version: 1.5.0 | Last Updated: 2025-12-18
