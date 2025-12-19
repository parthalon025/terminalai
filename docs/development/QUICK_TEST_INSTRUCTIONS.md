# Quick GUI Test Instructions

## 1. Launch GUI (2 minutes)

```bash
cd D:\SSD\AI_Tools\terminalai
python -m vhs_upscaler.gui
```

**Watch For**:
- Console output for errors
- Browser opening (usually http://127.0.0.1:7860)
- Hardware detection completion message (should finish in ~1-2 seconds)

---

## 2. Check Hardware Detection (30 seconds)

**Console should show**:
```
Detecting hardware capabilities...
```

**Two possible outcomes**:
- ✓ Detection completes: "Hardware: [CPU/GPU info]"
- ✓ Detection times out: "Hardware detection timed out - using CPU fallback"

**Both are OK** - timeout is handled gracefully.

---

## 3. Test Job Queue (1 minute)

**In the GUI**:

1. Enter a video file path or leave blank for test
2. Scroll down to "Face Restoration" section
3. Enable "Face Restore"
4. Select "CodeFormer" from "Face Model" dropdown
5. Scroll to "Audio Enhancement" section
6. Enable "Audio SR Upsampling"
7. Select "speech" from "Audio SR Model" dropdown
8. Click "Add to Queue"

**Expected Result**: ✓ Job added successfully, NO TypeError

---

## 4. Check for Errors (30 seconds)

**Console Output**:
- Look for any lines containing "TypeError" or "Error"
- Acceptable: "WARNING | RTX Video SDK not installed"
- Not OK: "TypeError: got an unexpected keyword argument"

**Latest Log File**:
```bash
# Check the newest log file
dir logs\vhs_upscaler_*.log /O-D /B | select -First 1
```

---

## 5. Quick Automated Test (Alternative)

If GUI won't launch, run this diagnostic:

```bash
python test_gui_launch.py
```

This tests all components without launching the GUI.

---

## Success Indicators

- ✓ GUI opens in browser without crashing
- ✓ Hardware detection finishes (or times out gracefully)
- ✓ Can add job with face_model parameter
- ✓ Can add job with audio_sr parameters
- ✓ No TypeError messages in console

---

## Common Issues

**Issue**: GUI doesn't open
**Solution**: Check if port 7860 is in use, try closing and restarting

**Issue**: Hardware detection takes forever
**Solution**: Wait 10 seconds, it will timeout and use CPU fallback

**Issue**: TypeError about parameters
**Solution**: This means the fix didn't work - report the exact error

---

## Report Results

After testing, provide:

1. **Did GUI launch?** Yes/No
2. **Hardware detection time**: X seconds (or timed out)
3. **Job queue test result**: Success/Failed
4. **Any errors in console?**: Copy exact error message
5. **Latest log file**: Check for errors

---

## Files to Check

- Console output (live)
- `logs\vhs_upscaler_20251219_*.log` (latest)
- Browser console (F12 for developer tools)

---

**Total Test Time**: ~5 minutes
**Created**: 2025-12-19
