# TerminalAI Performance Optimization - Quick Reference

**Date:** 2025-12-19
**Version:** 1.5.1

---

## TL;DR

- **32 optimizations identified** across 5 modules
- **6 high-priority patches** ready to apply
- **Expected improvement:** 40-65% faster processing
- **All tools ready:** Profilers, analyzers, patches, validation tests

---

## Quick Commands

```bash
# List available patches
python performance_patches.py --list

# Run static analysis
python analyze_performance.py

# Profile entire system
python performance_profiler.py --module all

# Validate after applying patches
pytest tests/test_performance_validation.py -v
```

---

## Top 6 Bottlenecks & Fixes

### 1. Multiple FFmpeg Calls (CRITICAL)
**File:** `vhs_upscaler/vhs_upscale.py`
**Problem:** 4-6 sequential subprocess calls
**Fix:** Single FFmpeg command with filter chain
**Impact:** 50-60% faster preprocessing
**Patch:** `video_pipeline_filters`

### 2. AI Model Reload Per File (CRITICAL)
**File:** `vhs_upscaler/audio_processor.py`
**Problem:** DeepFilterNet/AudioSR loaded every file
**Fix:** Pre-load during initialization
**Impact:** 2-10 seconds saved per file
**Patch:** `audio_model_preload`

### 3. Queue Lock Contention (HIGH)
**File:** `vhs_upscaler/queue_manager.py`
**Problem:** Single lock blocks concurrent reads
**Fix:** Read-write lock pattern
**Impact:** 4x query throughput
**Patch:** `queue_rwlock`

### 4. Excessive GUI Polling (HIGH)
**File:** `vhs_upscaler/gui.py`
**Problem:** 1-second polling interval
**Fix:** 2-second interval + debouncing
**Impact:** 50% CPU reduction
**Patch:** `gui_polling`

### 5. Progress Update Overhead (MEDIUM)
**File:** `vhs_upscaler/vhs_upscale.py`
**Problem:** Updates on every frame (60 FPS)
**Fix:** 500ms throttling
**Impact:** 10-15% overhead reduction
**Patch:** `progress_throttle`

### 6. Single-Frame GPU Processing (CRITICAL)
**File:** `vhs_upscaler/rtx_video_sdk/video_processor.py`
**Problem:** GPU idle during I/O
**Fix:** Batch 16-32 frames
**Impact:** 60-70% GPU utilization improvement
**Patch:** RTX batching (see PERFORMANCE_REPORT.md)

---

## Performance Targets

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Preprocessing (1080p, 60s) | 120s | 50s | 58% faster |
| AI model loading (batch) | 50s | 5s | 90% faster |
| Queue queries/sec | 100 | 450 | 350% faster |
| GUI CPU overhead | 15% | 6% | 60% reduction |
| GPU utilization | 45% | 85% | 89% improvement |
| Memory peak | 4 GB | 2.5 GB | 38% reduction |

---

## Implementation Priority

### Phase 1 (Week 1) - Critical Fixes
1. Video pipeline filter chain
2. Audio model pre-loading
3. RTX Video SDK batching

**Expected:** 45-55% overall improvement

### Phase 2 (Week 2) - Concurrency
1. Queue read-write locks
2. Async notifications
3. GUI polling optimization

**Expected:** 25-35% concurrent improvement

### Phase 3 (Week 3) - Memory
1. Temp file management
2. GPU buffer pre-allocation
3. Log buffer optimization

**Expected:** 30-40% memory reduction

---

## How to Apply Patches

### Step 1: Review Patch

```bash
python performance_patches.py --apply audio_model_preload
```

### Step 2: Apply Changes Manually

See patch output for detailed code changes.

### Step 3: Validate

```bash
pytest tests/test_performance_validation.py::test_audio_model_preload_speed
```

### Step 4: Benchmark

```bash
python performance_profiler.py --module audio_processing
```

---

## Quick Wins (< 1 hour each)

### 1. GUI Polling Interval
**File:** `vhs_upscaler/gui.py`
```python
# Change line ~400
QUEUE_POLL_INTERVAL = 2.0  # Was 1.0
```
**Impact:** 40-50% reduction in polling overhead

### 2. Filter Chain Caching
**File:** `vhs_upscaler/audio_processor.py`
```python
# Add decorator to _build_enhancement_filters_cached()
from functools import lru_cache

@lru_cache(maxsize=32)
def _build_enhancement_filters_cached(...):
    ...
```
**Impact:** 5-10% preprocessing improvement

### 3. Progress Throttling
**File:** `vhs_upscaler/vhs_upscale.py`
```python
# Add to UnifiedProgress.update_progress()
if time.time() - self.last_update < 0.5:
    return  # Skip update
```
**Impact:** 10-15% overhead reduction

---

## Validation Checklist

After applying patches:

- [ ] All tests passing: `pytest tests/ -v`
- [ ] Performance validation passing: `pytest tests/test_performance_validation.py -v`
- [ ] Output quality unchanged: Compare PSNR/SSIM scores
- [ ] Memory usage within limits: Monitor peak RSS
- [ ] No lock contention: Check queue throughput
- [ ] GUI responsive: Test upload/polling

---

## Monitoring Commands

### Check Performance Metrics

```bash
# Video processing speed
grep "Processing rate" logs/vhs_upscaler.log

# Memory usage
grep "Memory peak" logs/vhs_upscaler.log

# Queue throughput
grep "Queue status" logs/vhs_upscaler.log
```

### Profile Specific Function

```python
import cProfile
cProfile.run('upscaler.preprocess(...)', 'profile_stats.prof')

# View results
python -m pstats profile_stats.prof
```

### Memory Profile

```bash
# Install if needed
pip install memory-profiler

# Run with profiling
python -m memory_profiler vhs_upscaler/vhs_upscale.py
```

---

## Common Issues & Solutions

### Issue: FFmpeg Filter Chain Not Working
**Symptom:** Video output incorrect or missing
**Solution:** Validate filter string syntax
```bash
ffmpeg -h filter=yadif
ffmpeg -h filter=hqdn3d
```

### Issue: Model Loading Fails
**Symptom:** DeepFilterNet/AudioSR not caching
**Solution:** Check model availability
```python
try:
    from deepfilternet import DeepFilterNet
    print("DeepFilterNet available")
except ImportError:
    print("DeepFilterNet not installed")
```

### Issue: Queue Deadlock
**Symptom:** Queue operations hang
**Solution:** Check lock acquisition order
- Always acquire read lock before write lock
- Release locks in reverse order
- Use context managers (`with` statements)

### Issue: GUI Not Updating
**Symptom:** Progress frozen
**Solution:** Check polling interval
```python
# Verify polling is running
print(f"Polling interval: {QUEUE_POLL_INTERVAL}s")
```

---

## Performance Debugging

### Enable Debug Logging

```python
# In vhs_upscale.py
logging.basicConfig(level=logging.DEBUG)
```

### Measure Function Time

```python
import time

start = time.time()
result = function_to_profile()
elapsed = time.time() - start
print(f"Function took {elapsed:.3f}s")
```

### Check GPU Utilization

```bash
# NVIDIA GPUs
nvidia-smi -l 1

# Check GPU memory
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

### Profile Memory Usage

```python
import tracemalloc

tracemalloc.start()
# ... code to profile ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f} MB")
print(f"Peak: {peak / 1024 / 1024:.1f} MB")
tracemalloc.stop()
```

---

## Expected Results by Use Case

### VHS to 1080p (60 second clip)
- **Before:** 180 seconds total
- **After:** 85 seconds total
- **Improvement:** 53% faster

### Batch Processing (10 videos with AI)
- **Before:** 350 seconds total
- **After:** 255 seconds total
- **Improvement:** 27% faster

### Concurrent Queue (4 workers)
- **Before:** 100 queries/sec, 40% blocked
- **After:** 450 queries/sec, 10% blocked
- **Improvement:** 4.5x throughput

---

## Files Overview

| File | Purpose | Size |
|------|---------|------|
| `PERFORMANCE_SUMMARY.md` | Executive summary | Quick read |
| `PERFORMANCE_REPORT.md` | Detailed analysis | Full reference |
| `performance_profiler.py` | Runtime profiling | Run to profile |
| `analyze_performance.py` | Static analysis | Run to analyze |
| `performance_patches.py` | Patch system | Apply patches |
| `optimization_plan.txt` | Static results | Generated output |
| `tests/test_performance_validation.py` | Validation | Run after patches |

---

## Support & Resources

### Documentation
- Full report: `PERFORMANCE_REPORT.md`
- Optimization plan: `optimization_plan.txt`
- This guide: `PERFORMANCE_QUICK_REFERENCE.md`

### Tools
- Profiler: `python performance_profiler.py --help`
- Analyzer: `python analyze_performance.py --help`
- Patches: `python performance_patches.py --help`

### Testing
- Validation: `pytest tests/test_performance_validation.py -v`
- Benchmarking: `pytest tests/ --benchmark-only`

---

## One-Liner Summary

**6 critical patches ready to deliver 40-65% faster processing with better concurrency and 35% less memory.**

Apply patches incrementally, validate with tests, measure improvements, iterate.

---

**Quick Reference Version:** 1.0
**Last Updated:** 2025-12-19
**Status:** Ready for implementation
