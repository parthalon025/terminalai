# GUI Model Download UX Improvements

## Problem Statement

When users enable Face Restoration in the GUI for the first time, model downloads happen automatically during video processing. This can be confusing because:

1. ❌ No warning that models will be downloaded (332-360 MB)
2. ❌ Processing appears to freeze for 5-10 minutes
3. ❌ No GUI progress bar (only log messages)
4. ❌ Users may think the app crashed

## Current Behavior

```python
# User workflow:
1. Enable "Face Restoration" checkbox
2. Click "Add to Queue"
3. Click "Start Processing"
4. [Video processes normally]
5. [FREEZE - downloading model, 5-10 min]  ← User confused
6. [Processing continues]
```

## Recommended Improvements

### Option 1: Pre-Download Button (Best UX)

Add a "Download Models" button in the Face Restoration accordion:

```python
# In GUI face restoration section:
with gr.Accordion("👤 Face Restoration", open=False):
    gr.Markdown("""
    **First Time Setup**: Face restoration requires AI models (~350MB).
    Models download automatically on first use, or you can pre-download them:
    """)

    with gr.Row():
        check_models_btn = gr.Button("Check Models Status", variant="secondary")
        download_models_btn = gr.Button("Pre-Download Models", variant="primary")

    model_status = gr.Markdown("Status: Not checked")

    face_restore = gr.Checkbox(
        label="Enable Face Restoration",
        value=False,
        info="Restore faces using AI (requires models)"
    )
```

**Implementation:**

```python
def check_model_status():
    """Check if face restoration models are downloaded."""
    try:
        from vhs_upscaler.face_restoration import FaceRestorer
        restorer = FaceRestorer()

        # Check GFPGAN
        gfpgan_path = restorer._get_model_path("v1.3")
        gfpgan_exists = gfpgan_path.exists()

        # Check CodeFormer
        codeformer_path = restorer._get_model_path("v0.1.0", backend="codeformer")
        codeformer_exists = codeformer_path.exists()

        if gfpgan_exists and codeformer_exists:
            return "✅ **All models downloaded** (Ready to use)"
        elif gfpgan_exists:
            return "⚠️ **GFPGAN ready**, CodeFormer not downloaded"
        elif codeformer_exists:
            return "⚠️ **CodeFormer ready**, GFPGAN not downloaded"
        else:
            return "❌ **No models found** (Will download on first use: ~350MB)"

    except Exception as e:
        return f"❌ Error checking models: {e}"

def download_models_preemptively():
    """Download face restoration models before processing."""
    try:
        from vhs_upscaler.face_restoration import FaceRestorer

        yield "📥 Starting model downloads..."

        # Download GFPGAN v1.3 (default)
        yield "📥 Downloading GFPGAN v1.3 (332 MB)..."
        restorer = FaceRestorer(backend="gfpgan", model_version="v1.3")
        if restorer.download_model():
            yield "✅ GFPGAN v1.3 downloaded successfully"
        else:
            yield "❌ GFPGAN v1.3 download failed"
            return

        # Download CodeFormer
        yield "📥 Downloading CodeFormer (360 MB)..."
        restorer = FaceRestorer(backend="codeformer")
        if restorer.download_model():
            yield "✅ CodeFormer downloaded successfully"
        else:
            yield "❌ CodeFormer download failed"
            return

        yield "✅ **All models downloaded!** Face restoration is ready to use."

    except Exception as e:
        yield f"❌ Download error: {e}"

# Wire up the buttons
check_models_btn.click(
    fn=check_model_status,
    outputs=[model_status]
)

download_models_btn.click(
    fn=download_models_preemptively,
    outputs=[model_status],
    show_progress=True
)
```

### Option 2: Auto-Check on Checkbox Enable

Show a warning popup when user enables face restoration:

```python
def on_face_restore_enable(enabled):
    """Check model status when face restoration is enabled."""
    if not enabled:
        return gr.update(visible=False), ""

    # Check if models are downloaded
    from vhs_upscaler.face_restoration import FaceRestorer
    restorer = FaceRestorer()
    model_path = restorer._get_model_path("v1.3")

    if not model_path.exists():
        warning = """
        ⚠️ **First-time setup required**

        Face restoration models (~350 MB) will be downloaded automatically
        when you start processing. This may take 5-10 minutes.

        **Tip**: Use the "Pre-Download Models" button above to download in advance.
        """
        return gr.update(visible=True), warning
    else:
        return gr.update(visible=True), "✅ Models ready"

# Wire up the event
face_restore.change(
    fn=on_face_restore_enable,
    inputs=[face_restore],
    outputs=[face_restore_options, model_status]
)
```

### Option 3: Progress Bar During Download

Show download progress in the GUI during processing:

```python
# Modify FaceRestorer.download_model() to yield progress
def download_model_with_progress(self, force: bool = False):
    """Download model with GUI progress updates."""
    # ... existing code ...

    with open(temp_path, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)

                # Yield progress for GUI
                percent = (downloaded / total_size) * 100
                yield {
                    "status": "downloading",
                    "percent": percent,
                    "downloaded_mb": downloaded / 1_000_000,
                    "total_mb": total_size / 1_000_000,
                    "message": f"Downloading {self.backend} model: {percent:.1f}%"
                }

    # Verify checksum
    yield {"status": "verifying", "message": "Verifying checksum..."}
    if not self._verify_checksum(temp_path, expected_sha256):
        yield {"status": "error", "message": "Checksum verification failed"}
        return

    yield {"status": "complete", "message": "Model ready"}
```

---

## Implementation Priority

### 🔴 HIGH PRIORITY (Implement First)

**Option 1: Pre-Download Button**
- ✅ Best user experience
- ✅ Users can prepare in advance
- ✅ Clear status indication
- ✅ No surprises during processing

**Estimated Implementation Time:** 1-2 hours

### 🟡 MEDIUM PRIORITY (Nice to Have)

**Option 2: Auto-Check Warning**
- ✅ Warns users about download
- ✅ Minimal UI changes
- ⚠️ Still downloads during processing

**Estimated Implementation Time:** 30 minutes

### 🟢 LOW PRIORITY (Future Enhancement)

**Option 3: Progress Bar**
- ✅ Best visibility during download
- ⚠️ Requires threading/async changes
- ⚠️ More complex implementation

**Estimated Implementation Time:** 3-4 hours

---

## Quick Win: Add Info Text

**Minimal change (5 minutes):**

```python
# Update face restoration checkbox in gui.py
face_restore = gr.Checkbox(
    label="Enable Face Restoration",
    value=False,
    info="⚠️ First use downloads models (~350MB, 5-10 min). Check logs for progress."
)
```

---

## Testing Checklist

After implementing improvements:

- [ ] Test with no models cached (first-time user)
- [ ] Test with models already downloaded
- [ ] Test pre-download button functionality
- [ ] Verify download progress shows in GUI
- [ ] Test error handling (network failure)
- [ ] Test cancellation during download
- [ ] Verify checksum verification works
- [ ] Test with both GFPGAN and CodeFormer

---

## User Documentation Update

Add to README.md:

```markdown
### Face Restoration (First-Time Setup)

Face restoration uses AI models that need to be downloaded once:

**Option 1: Pre-download (Recommended)**
1. Open GUI
2. Go to "Face Restoration" section
3. Click "Pre-Download Models" button
4. Wait 5-10 minutes for ~350MB download

**Option 2: Auto-download**
- Models download automatically on first use
- Watch the logs for download progress
- Processing will pause during download

**Models are cached** in `~/.cache/terminalai/models/` and only download once.
```

---

## Conclusion

**Recommended Action Plan:**

1. **This week:** Add info text to checkbox (5 minutes)
   ```python
   info="⚠️ First use downloads models (~350MB). See logs for progress."
   ```

2. **Next sprint:** Implement pre-download button (1-2 hours)
   - Best UX improvement
   - Users can prepare in advance
   - Clear status indication

3. **Future:** Add progress bar in GUI (optional enhancement)

This will significantly improve the first-time user experience with face restoration!
