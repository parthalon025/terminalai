# Basic Mode - Quick Start Guide

## For Non-Technical Users

### What You See in Basic Mode

```
┌─────────────────────────────────────────────────────┐
│ 🎬 VHS Video Upscaler                              │
│ Interface Mode: 🎯 Basic Mode / ⚙️ Advanced Mode   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 📥 Input Source                                     │
│                                                     │
│ [Drag & Drop Video File Here]                      │
│   or                                                │
│ [Enter YouTube URL or File Path]                   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 🎯 Simple Preset Selection                         │
│                                                     │
│ What type of video are you restoring?              │
│                                                     │
│ ◉ 📼 Old VHS tape (home movies, family recordings) │
│ ○ 💿 DVD movie                                      │
│ ○ 📺 YouTube video                                  │
│ ○ 🎥 Recent digital video (phone, camera)          │
│                                                     │
│ Output Quality:                                     │
│ ○ Good (Fast, smaller file)                        │
│ ◉ Better (Balanced) ⭐ Recommended                  │
│ ○ Best (Slow, larger file)                         │
│                                                     │
│         [🚀 Process Video]                          │
└─────────────────────────────────────────────────────┘

💡 What will happen:
• VHS: AI upscaling, face restoration, audio cleanup, surround sound
• DVD: Smart upscaling with light cleanup
• YouTube: Remove compression artifacts
• Digital: Minimal processing, just upscale
```

## 3-Click Workflow

### Step 1: Upload Video
- **Drag & drop** your video file into the upload area
- **OR** enter a YouTube URL
- **OR** type the path to your video file

### Step 2: Choose Your Video Type
Pick the option that best describes your video:
- **📼 VHS tape** - Old home movies, family recordings (most common)
- **💿 DVD movie** - DVD rips or disc backups
- **📺 YouTube** - Downloaded YouTube videos
- **🎥 Digital** - Recent phone or camera footage

### Step 3: Select Quality
Choose based on your needs:
- **Good** - Faster processing, smaller files (great for sharing online)
- **Better** - Balanced quality and speed (recommended for most users)
- **Best** - Slowest processing, largest files (for archival quality)

### Step 4: Click "Process Video"
That's it! The system will:
1. Analyze your video
2. Apply optimal settings automatically
3. Process the video
4. Save the enhanced version to the output folder

## What Gets Applied Automatically?

### For VHS Tapes
The system automatically:
- Removes interlacing (those horizontal lines)
- Upscales to 1080p HD
- Restores faces (makes people look clearer)
- Cleans up audio (removes hiss and noise)
- Creates 5.1 surround sound
- Enhances speech clarity
- Uses the best available AI upscaler

**Result:** Your old VHS tapes look and sound like modern HD videos!

### For DVD Movies
The system automatically:
- Upscales to 1080p HD
- Light cleanup (preserves original quality)
- Creates 5.1 surround sound with Pro Logic II
- Compresses efficiently with HEVC

**Result:** DVD quality videos enhanced to HD!

### For YouTube Videos
The system automatically:
- Removes compression blocky artifacts
- Upscales to 1080p HD
- Moderate audio enhancement
- Preserves original aspect ratio

**Result:** Cleaner, sharper YouTube videos!

### For Digital Videos
The system automatically:
- Upscales to 1080p HD (if lower)
- Preserves original quality
- Minimal processing
- Maintains original audio

**Result:** Your videos upscaled without over-processing!

## Where Do I Find My Processed Videos?

By default, processed videos are saved to:
- **Windows:** `output/` folder in the application directory
- **Linux/Mac:** `output/` folder in the application directory

Look for files named like:
- `your_video_1080p.mp4`
- `youtube_YYYYMMDD_HHMMSS_1080p.mp4`

## How Long Does It Take?

Processing time depends on:
- Video length
- Your computer's GPU
- Quality setting chosen

**Typical times:**
- 10-minute VHS tape: 30-60 minutes (Better quality)
- 2-hour DVD movie: 4-8 hours (Better quality)
- 5-minute YouTube clip: 15-30 minutes (Better quality)

**With modern GPU (RTX 2060+):** 2-3x faster
**Without GPU:** 2-3x slower (but still works!)

## What If I Want More Control?

Switch to **⚙️ Advanced Mode** at the top!

In Advanced Mode, you can:
- Adjust all 78 settings manually
- Use quick-fix presets for specific scenarios
- Fine-tune AI models
- Customize audio processing
- Control HDR conversion
- Apply color grading LUTs

**Tip:** Start in Basic Mode, then switch to Advanced if you need to tweak something specific. Your settings will be preserved!

## Common Questions

**Q: Do I need a powerful computer?**
A: No! The system works on CPU without GPU. It's just slower.

**Q: Can I process multiple videos?**
A: Yes! Use the "Batch Processing" tab to add multiple videos to the queue.

**Q: Will it work on my old laptop?**
A: Yes, but processing will be slower. Consider the "Good" quality setting for faster results.

**Q: Can I stop processing and resume later?**
A: Yes, use the "Queue" tab to pause/resume processing.

**Q: Where can I see what's happening?**
A: Check the "Queue" tab for real-time progress and the "Logs" tab for detailed information.

**Q: Can I use this on YouTube URLs directly?**
A: Yes! Just paste the YouTube URL instead of uploading a file.

## Troubleshooting

**Problem:** "No file uploaded" error
**Solution:** Make sure you dragged a file into the upload area or entered a valid path/URL

**Problem:** Processing is very slow
**Solution:** Select "Good" quality for faster processing, or close other programs

**Problem:** "GPU not detected" message
**Solution:** The system will use CPU - it's slower but works fine

**Problem:** Output file is huge
**Solution:** Select "Good" quality for smaller files

**Problem:** Video looks over-processed
**Solution:** Try the "Digital" preset for minimal processing

## Need Help?

1. Check the "Logs" tab for error messages
2. Review the "Settings" tab to verify your output directory
3. Switch to Advanced Mode to see what settings were applied
4. Consult the full documentation in `BASIC_ADVANCED_MODE.md`

## Tips for Best Results

1. **VHS Tapes:** Always use the VHS preset - it's specifically designed for old analog video
2. **Quality:** "Better" is perfect for 95% of videos
3. **Patience:** Good results take time - don't cancel early!
4. **Originals:** Keep your original files - you can always re-process with different settings
5. **Preview:** Process a short clip first to verify settings before doing a 2-hour movie

---

**That's it!** Basic Mode makes professional video upscaling accessible to everyone. No technical knowledge required - just upload, pick a preset, and process!
