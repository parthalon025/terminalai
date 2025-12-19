# VHS Upscaler GUI - User Guide

## Quick Start (3 Steps)

### For Beginners:
1. **Upload** your video file or paste YouTube URL
2. **Click** a Quick Fix preset button (e.g., "📼 VHS Home Movies")
3. **Click** "➕ Add to Queue" → Done!

The interface now automatically shows only the settings you need based on your selections.

---

## Understanding the New Interface

### What's Different?

**Before**: All settings visible at once (overwhelming!)
**Now**: Settings appear automatically based on what you're doing (smart!)

### Dynamic Interface Examples:

#### Example 1: Selecting AI Upscaler
```
When you select:           You see:
─────────────────          ────────────────────
auto                       No extra options
rtxvideo                   🚀 RTX Video SDK Settings
realesrgan                 🎨 Real-ESRGAN Settings
ffmpeg                     🔧 FFmpeg Settings
```

#### Example 2: Enabling Face Restoration
```
When you check:                    You see:
─────────────────────              ───────────────────────
☐ Enable Face Restoration          (nothing)
☑ Enable Face Restoration          • Restoration Strength
                                   • Face Upscale Factor
```

#### Example 3: Audio Surround Sound
```
When you select:                   You see:
─────────────────────              ───────────────────────
Output Layout: original            (nothing)
Output Layout: 5.1                 🔊 Surround Sound Config
                                   • Subwoofer Crossover
                                   • Center Channel Level
                                   • Surround Delay
```

---

## Interface Sections

### 🎯 Quick Fix Presets (Recommended)

One-click configurations for common scenarios. Just click and go!

| Preset | When to Use | What It Does |
|--------|-------------|-------------|
| **📼 VHS Home Movies** | Family VHS tapes | Face restoration + voice enhancement + 5.1 surround |
| **🔊 Noisy VHS** | Damaged/noisy tapes | Heavy denoising + QTGMC deinterlacing |
| **💿 DVD Rip** | DVD sources | Light processing for already decent quality |
| **📺 Old YouTube** | Low-quality downloads | Deblock compression artifacts |
| **🎨 Anime** | Cartoons/animation | Anime-optimized AI model |
| **🎥 Webcam** | Low-quality webcam | Heavy denoise, no deinterlacing |
| **✨ Clean Digital** | Already good quality | Minimal processing, just upscale |
| **⭐ Best Quality** | Archival/premium | Everything maxed (very slow!) |

**Pro Tip**: Start with a preset, then tweak individual settings if needed.

---

### ⚙️ Basic Settings

Always visible. These are your main controls:

- **Preset Profile**: Source type (VHS/DVD/YouTube/etc.) - affects deinterlacing/denoising
- **Target Resolution**: 1080p recommended for VHS/DVD, 2160p for modern displays
- **AI Upscaler**:
  - `auto` - Let the system choose (recommended)
  - `rtxvideo` - RTX 20+ GPUs (best quality)
  - `realesrgan` - AMD/Intel/NVIDIA GPUs
  - `ffmpeg` - CPU fallback (no GPU needed)

---

### Advanced Sections (Click to Expand)

#### ▼ ⚙️ Encoding & Quality Settings

Controls video encoder and compression quality.

**When to open**: If you need specific encoder (CPU vs GPU) or want to control file size.

**Key settings**:
- **Video Encoder**:
  - `hevc_nvenc` - NVIDIA GPU, best compression (default)
  - `libx265` - CPU encoder (slower, no GPU needed)
- **CRF Quality**: Lower = better quality, larger file
  - `18` - Near-lossless (large files)
  - `20` - Excellent (recommended)
  - `23` - Good (smaller files)

#### ▼ 🎨 AI Upscaler Settings

**Shows**: Engine-specific options based on your AI Upscaler selection

**RTX Video SDK** (rtxvideo):
- ✓ Artifact Reduction - Essential for VHS/DVD
- Reduction Strength - Higher for noisier sources
- SDR to HDR - Only for modern TVs

**Real-ESRGAN** (realesrgan):
- AI Model - Choose based on content type
- Noise Reduction - Higher for VHS (0.7-1.0)

**FFmpeg** (ffmpeg):
- Scaling Algorithm - lanczos is best for most cases

#### ▼ 🌈 HDR & Color Settings

**When to open**: If you want HDR output or need color correction.

**Dynamic behavior**:
- Select HDR mode → HDR conversion settings appear
- Stay on SDR → No extra options

**LUT Color Grading**: Optional .cube file for cinematic looks or VHS color correction.

#### ▼ 👤 Face Restoration

**When to use**: Home videos with people's faces visible.
**Skip if**: Landscapes, sports, animation, or no faces.

**Dynamic behavior**:
- Check "Enable Face Restoration" → Strength/Upscale sliders appear
- Uncheck → Options hide

**Settings** (when enabled):
- **Model**: gfpgan (balanced) vs codeformer (higher quality)
- **Strength**: 0.5 default, 0.8+ for heavily damaged faces
- **Upscale Factor**: 2x for most cases

#### ▼ 📼 Deinterlacing

**When to use**: VHS tapes, DVDs, broadcast recordings (interlaced sources).
**Skip if**: Already progressive (most modern videos).

**Dynamic behavior**:
- Select "qtgmc" algorithm → QTGMC Preset dropdown appears
- Other algorithms → No extra options

**Algorithms**:
- `yadif` - Fast, good quality (default)
- `qtgmc` - Best quality, requires VapourSynth

#### ▼ 🔊 Audio Processing

Complex section with multiple conditional groups.

**Basic Settings** (always visible):
- **Noise Reduction**: none/light/aggressive/voice/deepfilternet
- **Audio Codec**: aac (streaming) vs eac3 (5.1 theater) vs flac (archival)
- **Surround Upmix**: Create 5.1/7.1 from stereo
- **Output Layout**: Stereo vs 5.1 vs 7.1

**Dynamic Groups**:

1. **Advanced Audio Cleanup** - Appears when Noise Reduction ≠ "none"
   - Target Loudness: -14 for YouTube/Spotify
   - Noise Gate: -25 to -30 for VHS

2. **Demucs AI Stem Separation** - Appears when Surround Upmix = "demucs"
   - AI Model: htdemucs (fast) vs htdemucs_ft (best)
   - Device: auto (GPU if available)
   - Quality Passes: 1 is usually enough

3. **Surround Sound Configuration** - Appears when Output Layout = "5.1" or "7.1"
   - Subwoofer Crossover: 120Hz for typical setups
   - Center Channel Level: 0.707 default
   - Surround Delay: 15-20ms for movies

---

## Understanding Conditional Visibility

### Why Settings Appear/Disappear:

**Old Way**: Show all options all the time
- Pro: You see everything
- Con: Overwhelming, confusing, easy to misconfigure

**New Way**: Show only relevant options
- Pro: Clean interface, fewer mistakes
- Con: You might not see advanced options unless you trigger them

### How to Find "Hidden" Options:

1. **Enable the feature** - Check the main checkbox or select the option
2. **Look below** - Related settings appear automatically
3. **Check accordions** - Advanced options live in collapsible sections

### Example Workflow:

```
Goal: Use QTGMC deinterlacing

Step 1: Expand "📼 Deinterlacing" accordion
Step 2: Select "qtgmc" from Algorithm dropdown
Step 3: QTGMC Preset dropdown appears automatically!
Step 4: Choose preset (medium/slow/very_slow)
```

No hunting through menus - the option appears exactly when you need it!

---

## Tips & Tricks

### Tip 1: Use Quick Fix Presets First
Start with a preset, then expand accordions to fine-tune. Much faster than manual configuration!

### Tip 2: Hover Over Info Icons
Every setting has a tooltip explaining when to use it and what values to choose.

### Tip 3: Don't Overthink It
The defaults are good! Only change settings if you know why.

### Tip 4: Accordion Organization
Settings are grouped by purpose:
- **Encoding** - Technical video settings
- **AI Upscaler** - Upscaling engine options
- **HDR & Color** - Display/color correction
- **Face Restoration** - AI face enhancement
- **Deinterlacing** - Remove interlacing artifacts
- **Audio** - Sound processing

### Tip 5: Check the Help Sidebar
The right sidebar has quick reference guides for each setting type.

---

## Common Scenarios

### Scenario 1: "I just want to upscale my VHS tape"
1. Upload video
2. Click "📼 VHS Home Movies" preset
3. Click "Add to Queue"
**Done!** Everything is configured optimally.

### Scenario 2: "My VHS tape is REALLY noisy"
1. Upload video
2. Click "🔊 Noisy VHS" preset
3. (Optional) Open "🔊 Audio Processing" accordion
4. Change Noise Reduction to "deepfilternet" if still too noisy
**Done!**

### Scenario 3: "I want maximum quality, I don't care about time"
1. Upload video
2. Click "⭐ Best Quality" preset
3. Review settings:
   - Encoder: libx265 (CPU, slow)
   - CRF: 15 (huge files)
   - AI Upscaler: maxine or realesrgan
   - Face Restore: CodeFormer (slow)
   - Deinterlace: QTGMC very_slow
   - Audio: DeepFilterNet + Demucs 7.1
4. Click "Add to Queue"
**Warning**: This will take a LONG time!

### Scenario 4: "I have an RTX GPU and want to use it"
1. Upload video
2. Basic Settings → AI Upscaler: `rtxvideo`
3. **RTX Video SDK Settings** section appears automatically
4. Configure:
   - ✓ Artifact Reduction (ON for VHS/DVD)
   - Reduction Strength: 0.7-1.0 for heavy artifacts
   - SDR to HDR: OFF (unless you have HDR display)
5. Click "Add to Queue"

### Scenario 5: "I want 5.1 surround from my stereo VHS audio"
1. Upload video
2. Click "📼 VHS Home Movies" preset (already has 5.1!)
3. (Optional) Open "🔊 Audio Processing" accordion
4. Surround Upmix: `demucs` (AI, best) or `prologic` (faster)
5. Output Layout: `5.1`
6. **Surround Sound Configuration** appears automatically
7. Adjust if needed (defaults are good)
8. Click "Add to Queue"

---

## Troubleshooting

### "I can't find the setting I need!"

**Check if it's conditional**:
1. Is it in a collapsed accordion? Click to expand.
2. Does it depend on another setting? Enable the trigger.
3. Is it engine-specific? Select the right AI Upscaler.

**Examples**:
- QTGMC Preset → Select "qtgmc" algorithm first
- RTX Settings → Select "rtxvideo" AI Upscaler first
- Surround Config → Select "5.1" or "7.1" layout first

### "The interface looks different from the screenshots!"

**Possible causes**:
1. Accordions collapsed - Click to expand sections
2. Conditional groups hidden - Enable the trigger setting
3. Different selections - Engine-specific options change based on AI Upscaler

### "I enabled a feature but don't see the options!"

**Solution**:
1. Look directly below the checkbox/dropdown
2. Scroll down - options may be below viewport
3. Check if in a `gr.Group` that needs another trigger

### "Too many options! I'm overwhelmed!"

**Solution**:
1. **Use Quick Fix Presets** - They handle everything for you
2. **Ignore accordions** - Collapsed by default, only open if you need
3. **Start simple** - Basic Settings are all you need for most videos
4. **Expand gradually** - Only open accordions when you want to tweak

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Tab | Navigate between controls |
| Space | Toggle checkboxes, expand dropdowns |
| Enter | Submit form (Add to Queue) |
| Arrow Up/Down | Navigate dropdown options |
| Esc | Close open dropdown |

---

## Accessibility Features

- **Keyboard Navigation**: Full interface accessible without mouse
- **Screen Reader Support**: ARIA labels on all conditional groups
- **High Contrast**: Color-coded sections with WCAG AA compliance
- **Focus Indicators**: Clear focus states for keyboard navigation
- **Logical Tab Order**: Settings flow top-to-bottom, left-to-right

---

## Mobile/Tablet Usage

**Optimizations**:
- Touch-friendly accordion toggles
- Larger tap targets for buttons
- Stacked layout on small screens
- Quick Presets in 2x4 grid
- Collapsible help sidebar

**Best Practices**:
- Use Quick Fix Presets on mobile (fewer taps)
- Expand one accordion at a time (less scrolling)
- Upload via URL instead of file picker (easier)

---

## FAQ

**Q: Do I need to configure everything?**
A: No! Quick Fix Presets handle it. Advanced options are for tweaking.

**Q: What if I don't have a GPU?**
A: Select `ffmpeg` AI Upscaler and `libx265` encoder. Slower but works!

**Q: Which preset should I use?**
A: Match your source type:
- VHS tape → "VHS Home Movies" or "Noisy VHS"
- DVD → "DVD Rip"
- YouTube → "Old YouTube"
- Anime → "Anime"

**Q: Why do some settings disappear?**
A: They're conditional - only shown when relevant. Enable the trigger to see them.

**Q: Can I save my custom configuration?**
A: Not yet - coming in a future update. For now, use Quick Fix presets or note your settings.

**Q: What's the fastest preset?**
A: "Clean Digital" - minimal processing.

**Q: What's the slowest preset?**
A: "Best Quality" - everything maxed.

**Q: How do I know if a feature is available?**
A: Options appear if available. Missing options = feature not installed.

**Q: Can I process multiple videos?**
A: Yes! Use the "📚 Batch Processing" tab.

---

## Summary

The optimized GUI uses **progressive disclosure** - showing options exactly when you need them:

✅ **Cleaner**: Less clutter, easier to navigate
✅ **Smarter**: Options appear based on your selections
✅ **Faster**: Quick Fix Presets for one-click configuration
✅ **Flexible**: Advanced users can still access all options

**Golden Rule**: Start with Basic Settings + Quick Fix Preset. Only expand accordions if you want to customize!
