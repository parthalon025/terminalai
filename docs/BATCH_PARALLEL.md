# Parallel Batch Processing

## Overview

Enhanced batch processing with parallel execution support for processing multiple videos simultaneously. This dramatically reduces total processing time for large video collections by utilizing multiple CPU/GPU cores.

## Features

- **Parallel Execution**: Process multiple videos simultaneously using ThreadPoolExecutor
- **Configurable Workers**: Adjust parallelism based on system resources
- **Progress Tracking**: Real-time completion tracking across all workers
- **Error Isolation**: Failed videos don't block other processing jobs
- **Resource Management**: Smart worker allocation to prevent system overload

## Performance Benefits

### Processing Time Comparison

For a batch of 10 videos (10 minutes each, 1080p VHS restoration):

| Workers | Total Time | Speedup | Notes |
|---------|------------|---------|-------|
| 1 (sequential) | 5h 0m | 1.0x | Baseline |
| 2 parallel | 2h 30m | 2.0x | Ideal for dual GPU |
| 3 parallel | 1h 40m | 3.0x | Good for high-end systems |
| 4 parallel | 1h 15m | 4.0x | Requires significant RAM/VRAM |

### Resource Considerations

**Recommended Worker Counts:**
- **1 Worker (Sequential)**: Low memory systems, single GPU
- **2 Workers**: Dual GPU systems, 32GB RAM minimum
- **3 Workers**: High-end workstations, 64GB RAM, multiple GPUs
- **4+ Workers**: Server-grade hardware, 128GB+ RAM, GPU cluster

**Resource Requirements per Worker:**
- **RAM**: 8-16GB per worker (depending on resolution)
- **VRAM**: 4-8GB per worker (for Real-ESRGAN/GFPGAN)
- **Disk I/O**: Ensure fast SSD for temp files
- **CPU**: 4+ cores recommended per worker

## Usage

### Basic Parallel Processing

```bash
# Process with 2 parallel workers
vhs-upscale batch ./videos/ ./output/ -p vhs --parallel 2

# Process with 3 workers for faster batch
vhs-upscale batch ./archive/ ./restored/ -p vhs_heavy --parallel 3
```

### Advanced Examples

```bash
# High-performance batch (4 workers, 4K output)
vhs-upscale batch ./vhs_collection/ ./4k_restored/ \
    -p vhs_archive \
    -r 2160 \
    --parallel 4 \
    --skip-existing

# Memory-efficient parallel (2 workers, lower quality)
vhs-upscale batch ./videos/ ./output/ \
    -p vhs_standard \
    -r 1080 \
    --parallel 2 \
    --crf 23

# Resume interrupted parallel batch
vhs-upscale batch ./videos/ ./output/ \
    -p vhs \
    --parallel 3 \
    --resume
```

### Testing Parallel Performance

```bash
# Test with small subset first
vhs-upscale batch ./videos/ ./test_output/ \
    -p vhs \
    --parallel 3 \
    --max-count 5

# Dry-run to preview batch
vhs-upscale batch ./videos/ ./output/ \
    -p vhs \
    --parallel 3 \
    --dry-run
```

## Architecture

### Sequential Processing (--parallel 1)

```
┌─────────────┐
│   Video 1   │ ──► Process ──► Done
└─────────────┘
       ↓
┌─────────────┐
│   Video 2   │ ──► Process ──► Done
└─────────────┘
       ↓
┌─────────────┐
│   Video 3   │ ──► Process ──► Done
└─────────────┘

Total Time: 3 × Processing Time
```

### Parallel Processing (--parallel 3)

```
┌─────────────┐
│   Video 1   │ ──► [Worker 1] ──► Done
└─────────────┘

┌─────────────┐
│   Video 2   │ ──► [Worker 2] ──► Done
└─────────────┘

┌─────────────┐
│   Video 3   │ ──► [Worker 3] ──► Done
└─────────────┘
       ↓
┌─────────────┐
│   Video 4   │ ──► [Worker 1] ──► Done  (reuses completed worker)
└─────────────┘

Total Time: ⌈Videos / Workers⌉ × Processing Time
```

### ThreadPoolExecutor Implementation

```python
# Prepare jobs
jobs = [(video, output_path, config) for video, output_path in video_pairs]

# Process with thread pool
with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
    futures = {executor.submit(process_job, job): job for job in jobs}

    # Track completions
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        # Handle success/failure
```

## Output Format

### Sequential Mode Output

```
Starting batch processing (10 videos)
============================================================

[1/10] Processing: video1.mp4
  Output: video1_1080p.mp4
  Success
------------------------------------------------------------
[2/10] Processing: video2.mp4
  Output: video2_1080p.mp4
  Success
------------------------------------------------------------
...
```

### Parallel Mode Output

```
Starting batch processing (10 videos)
Parallel mode: 3 workers
============================================================

[1/10] SUCCESS: video1.mp4
------------------------------------------------------------
[3/10] SUCCESS: video3.mp4
------------------------------------------------------------
[2/10] SUCCESS: video2.mp4
------------------------------------------------------------
[4/10] SUCCESS: video4.mp4
------------------------------------------------------------
...

============================================================
BATCH PROCESSING COMPLETE
============================================================
Total videos: 10
Successful:   9
Failed:       1
Output:       ./restored/
```

## Error Handling

### Isolated Failures

Failed videos don't block other processing:

```bash
# Even if video 3 fails, others continue
[1/10] SUCCESS: video1.mp4
[2/10] SUCCESS: video2.mp4
[3/10] FAILED: video3.mp4
  Error: Corrupted video file
[4/10] SUCCESS: video4.mp4
...
```

### Comprehensive Error Logging

```bash
# View detailed errors
vhs-upscale batch ./videos/ ./output/ \
    -p vhs \
    --parallel 3 \
    --verbose

# Errors logged to console with stack traces
# Failed videos can be reprocessed individually
```

## Best Practices

### 1. Start with Low Parallelism

Test with 2 workers before scaling up:

```bash
# Test performance
vhs-upscale batch ./videos/ ./test/ \
    -p vhs \
    --parallel 2 \
    --max-count 3
```

### 2. Monitor System Resources

Watch for:
- **RAM usage**: Should stay below 80% total
- **VRAM usage**: Each worker needs dedicated VRAM
- **Disk I/O**: Ensure SSD isn't bottlenecked
- **CPU**: Should see high utilization across cores

### 3. Use --skip-existing for Reliability

Resume failed batches without reprocessing:

```bash
vhs-upscale batch ./videos/ ./output/ \
    -p vhs \
    --parallel 3 \
    --skip-existing
```

### 4. Optimize Worker Count

**Formula**: `workers = min(GPUs, RAM_GB / 16, Videos / 2)`

Examples:
- **Single RTX 3080 (24GB RAM)**: 1-2 workers
- **Dual RTX 4090 (64GB RAM)**: 2-4 workers
- **4x A100 (256GB RAM)**: 4-8 workers

### 5. Consider Temporary Disk Space

Each worker needs temp space:
- **1080p processing**: ~5-10GB per worker
- **4K processing**: ~20-40GB per worker

Ensure adequate free space: `workers × temp_space_per_worker`

## Troubleshooting

### Issue: Out of Memory Errors

**Symptoms**: Crashes mid-processing, system freezing

**Solutions**:
```bash
# Reduce worker count
vhs-upscale batch ./videos/ ./output/ --parallel 1

# Lower target resolution
vhs-upscale batch ./videos/ ./output/ -r 720 --parallel 2

# Increase CRF (lower quality, less memory)
vhs-upscale batch ./videos/ ./output/ --crf 25 --parallel 2
```

### Issue: Slower Than Sequential

**Causes**: Disk I/O bottleneck, insufficient RAM, thermal throttling

**Solutions**:
```bash
# Ensure using SSD for temp files
vhs-upscale batch ./videos/ ./output/ \
    --parallel 2 \
    --keep-temp=false  # Clean up temp files immediately

# Check thermal throttling (monitor GPU temps)
# Reduce workers if GPUs exceed 80°C
```

### Issue: Videos Processing Out of Order

**Expected Behavior**: Parallel processing completes jobs out of order

**Solution**: Use sequential if order matters:
```bash
vhs-upscale batch ./videos/ ./output/ --parallel 1
```

### Issue: Some Workers Idle

**Cause**: Uneven video lengths or processing complexity

**Solution**: Normal behavior - workers complete at different rates. Overall speedup still achieved.

## Performance Tuning

### GPU-Bound Workloads

For Real-ESRGAN/GFPGAN intensive processing:

```bash
# Match workers to GPUs
vhs-upscale batch ./videos/ ./output/ \
    --parallel 2 \  # For dual GPU
    --engine realesrgan
```

### CPU-Bound Workloads

For FFmpeg-heavy preprocessing:

```bash
# Higher parallelism for CPU work
vhs-upscale batch ./videos/ ./output/ \
    --parallel 4 \  # More workers for CPU tasks
    --skip-maxine \
    --engine ffmpeg
```

### Balanced Workloads

Mix of GPU upscaling and CPU preprocessing:

```bash
# Moderate parallelism
vhs-upscale batch ./videos/ ./output/ \
    --parallel 3 \
    -p vhs_standard
```

## Comparison with Sequential

### When to Use Sequential (--parallel 1)

- Limited RAM (<16GB)
- Single GPU systems
- Debugging individual videos
- Order-sensitive workflows
- Low-power systems

### When to Use Parallel (--parallel 2+)

- Large video collections (10+ videos)
- Multi-GPU systems
- High RAM (32GB+)
- Time-critical projects
- Server/workstation environments

## Advanced Patterns

### Batch with Custom Settings per Video

For advanced users needing different settings per video, use sequential with scripting:

```bash
# Process each with custom preset
for video in ./videos/*.mp4; do
    preset=$(determine_preset "$video")  # Custom logic
    vhs-upscale upscale "$video" -o "./output/$(basename "$video")" -p "$preset"
done
```

### Distributed Processing

For massive collections, split across multiple machines:

```bash
# Machine 1: Videos 1-100
vhs-upscale batch ./videos/ ./output/ --parallel 4 --max-count 100

# Machine 2: Videos 101-200
vhs-upscale batch ./videos/ ./output/ --parallel 4 --skip-existing --max-count 200
```

## Integration with Other Features

### Parallel + Auto-Detect

Analyze each video before processing (sequential analysis, parallel processing):

```bash
# Auto-detect analyzes sequentially, then processes in parallel
vhs-upscale batch ./videos/ ./output/ \
    --auto-detect \
    --parallel 3
```

### Parallel + Preset Comparison

Not recommended - use sequential for comparison:

```bash
# Use sequential for preset testing
vhs-upscale test-presets video.mp4 -o ./comparisons/ \
    --multi-clip \
    --presets vhs_standard,vhs_clean,vhs_heavy
```

## Future Enhancements

Potential improvements for future versions:

1. **Dynamic Worker Scaling**: Adjust workers based on system load
2. **Priority Queuing**: Process important videos first
3. **Distributed Processing**: Network-based job distribution
4. **GPU Affinity**: Pin workers to specific GPUs
5. **Progress Persistence**: Save/resume complex batch jobs
6. **Resource Prediction**: Estimate completion time and resource needs

## References

- [Python ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html)
- [FFmpeg Parallel Processing](https://trac.ffmpeg.org/wiki/EncodingForStreamingSites#Parallelprocessing)
- [Real-ESRGAN GPU Memory](https://github.com/xinntao/Real-ESRGAN#-memory-efficient-inference)
