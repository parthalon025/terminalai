# CodeFormer Integration - Implementation Summary

## Overview

Successfully integrated CodeFormer as a second face restoration backend alongside GFPGAN in the `vhs_upscaler/face_restoration.py` module.

## Changes Made

### 1. Added `_process_frames_codeformer()` Method (Lines 516-658)

**Location:** After `_process_frames_gfpgan()` method

**Key Features:**
- Full CodeFormer model initialization with fidelity weight control
- Face detection and alignment using FaceRestoreHelper
- Per-frame processing with progress logging (every 10 frames)
- GPU acceleration with automatic device selection (CUDA/CPU)
- Graceful error handling with fallback to original frames
- Memory management (garbage collection after each frame)

**Processing Pipeline:**
1. Import dependencies (torch, cv2, numpy, torchvision)
2. Load CodeFormer architecture and model weights
3. Initialize FaceRestoreHelper for face detection
4. For each frame:
   - Detect and align faces
   - Convert to tensor and normalize
   - Run CodeFormer inference with fidelity weight
   - Paste restored faces back to original image
   - Save restored frame

**Parameters:**
- `frames_dir`: Input frames directory
- `output_dir`: Output restored frames directory
- `upscale`: Upscale factor (1, 2, or 4)
- `fidelity`: Fidelity weight (0.5-0.9, higher = more faithful to original)
- `only_center_face`: Process only the largest/center face

### 2. Updated `restore_faces()` Method (Lines 349-376)

**Backend Dispatch Logic:**
```python
if self.backend == "codeformer":
    logger.info("Running CodeFormer face restoration...")
    self._process_frames_codeformer(
        frames_dir=frames_dir,
        output_dir=restored_dir,
        upscale=upscale,
        fidelity=fidelity,
        only_center_face=only_center_face
    )
else:
    logger.info("Running GFPGAN face restoration...")
    self._process_frames_gfpgan(
        frames_dir=frames_dir,
        output_dir=restored_dir,
        upscale=upscale,
        weight=weight,
        only_center_face=only_center_face,
        aligned=aligned,
        tile_size=tile_size
    )
```

**Improvements:**
- Dynamic backend selection based on `self.backend`
- Separate parameter passing for each backend
- Updated error messages to reflect active backend
- Maintained backward compatibility with GFPGAN

### 3. Existing Backend Selection Infrastructure (Already Present)

The following were already implemented in previous work:
- `_check_codeformer()` method for dependency validation
- `CODEFORMER_MODELS` dictionary with v0.1.0 model definition
- Backend parameter in `__init__()` constructor
- Model path management for both backends
- Download support for CodeFormer models

## Integration Architecture

### Backend Selection Flow

```
FaceRestorer.__init__(backend="codeformer")
    ├─> self.backend = "codeformer"
    ├─> self._check_codeformer()  # Validate dependencies
    ├─> self.model_path = models/codeformer/codeformer.pth
    └─> self.has_backend = True/False

restore_faces(input_video, output_video, fidelity=0.7)
    ├─> Extract frames to temp directory
    ├─> Dispatch based on self.backend:
    │   ├─> CodeFormer: _process_frames_codeformer(fidelity=0.7)
    │   └─> GFPGAN: _process_frames_gfpgan(weight=0.5)
    └─> Reassemble video with audio
```

### Parameter Mapping

| Backend | Primary Control | Range | Purpose |
|---------|----------------|-------|---------|
| GFPGAN | `weight` | 0.0-1.0 | Restoration strength |
| CodeFormer | `fidelity` | 0.5-0.9 | Balance quality/likeness |

Both backends share:
- `upscale`: Upscale factor (1, 2, 4)
- `only_center_face`: Process only center face

GFPGAN-specific:
- `aligned`: Pre-aligned faces flag
- `tile_size`: VRAM usage control

## Usage Examples

### GFPGAN Backend (Default)
```python
from pathlib import Path
from vhs_upscaler.face_restoration import FaceRestorer

restorer = FaceRestorer(backend="gfpgan")
restorer.restore_faces(
    input_path=Path("old_vhs.mp4"),
    output_path=Path("restored_gfpgan.mp4"),
    upscale=2,
    weight=0.5  # GFPGAN weight parameter
)
```

### CodeFormer Backend
```python
from pathlib import Path
from vhs_upscaler.face_restoration import FaceRestorer

restorer = FaceRestorer(backend="codeformer")
restorer.restore_faces(
    input_path=Path("old_vhs.mp4"),
    output_path=Path("restored_codeformer.mp4"),
    upscale=2,
    fidelity=0.7  # CodeFormer fidelity parameter
)
```

## Dependencies

### GFPGAN
```bash
pip install gfpgan basicsr opencv-python torch
```

### CodeFormer
```bash
pip install torch opencv-python torchvision
# Plus CodeFormer package or manual integration
```

## Model Downloads

Both models can be downloaded via the `download_model()` method:

```python
restorer = FaceRestorer(backend="codeformer")
restorer.download_model()  # Downloads codeformer.pth (360MB)
```

Models are stored in:
- GFPGAN: `models/gfpgan/GFPGANv1.3.pth` (332MB)
- CodeFormer: `models/codeformer/codeformer.pth` (360MB)

## Testing

### Validation Script
Run `validate_codeformer.py` to verify integration:

```bash
python validate_codeformer.py
```

**Expected Output:**
```
SUCCESS: CodeFormer integration complete!

Features:
  - Dual backend support (GFPGAN + CodeFormer)
  - Automatic backend selection
  - Fidelity control for CodeFormer (0.5-0.9)
  - Weight control for GFPGAN (0.0-1.0)
  - Frame-by-frame processing with progress logging
  - Graceful fallback on processing errors
```

### Syntax Validation
```bash
python -m py_compile vhs_upscaler/face_restoration.py
```

## Error Handling

Both backends implement identical error handling:

1. **Import Errors**: Log missing dependencies and raise RuntimeError
2. **Model Loading Errors**: Log checkpoint loading issues
3. **Frame Processing Errors**:
   - Log warning for individual frame failures
   - Copy original frame as fallback
   - Continue processing remaining frames
4. **Complete Failure**: Raise RuntimeError with descriptive message

## Performance Characteristics

| Backend | Speed | Quality | VRAM Usage | Best For |
|---------|-------|---------|------------|----------|
| GFPGAN | Fast | Good | Low-Medium | General restoration |
| CodeFormer | Slower | Superior | Medium-High | High-quality restoration |

## Implementation Statistics

- **Lines Added:** ~160 lines (new method + dispatch logic)
- **Files Modified:** 1 (`vhs_upscaler/face_restoration.py`)
- **New Methods:** 1 (`_process_frames_codeformer`)
- **Modified Methods:** 1 (`restore_faces`)
- **Backward Compatibility:** 100% maintained
- **Syntax Check:** Passed ✓
- **Integration Test:** Passed ✓

## Future Enhancements

Potential improvements:
1. GUI integration for backend selection
2. Automatic backend recommendation based on video quality
3. Batch processing with mixed backends
4. Real-time preview during processing
5. Fine-tuned fidelity presets for common scenarios

## References

- **CodeFormer GitHub:** https://github.com/sczhou/CodeFormer
- **GFPGAN GitHub:** https://github.com/TencentARC/GFPGAN
- **Face Restoration Module:** `vhs_upscaler/face_restoration.py`
- **Validation Script:** `validate_codeformer.py`
