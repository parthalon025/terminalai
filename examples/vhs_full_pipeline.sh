#!/bin/bash
################################################################################
# VHS Full Pipeline - Complete VHS Tape Restoration
################################################################################
#
# PURPOSE:
#   Complete VHS restoration pipeline with the following stages:
#   1. DEINTERLACE → Remove interlaced combing artifacts (QTGMC)
#   2. DENOISE → Remove VHS tape noise
#   3. UPSCALE → AI upscaling with Real-ESRGAN or NVIDIA Maxine
#   4. FACE RESTORE → Optional GFPGAN face enhancement
#   5. SHARPEN → CAS (Contrast Adaptive Sharpening)
#   6. ENCODE → Hardware-accelerated H.265 output
#
# REQUIREMENTS:
#   - Python 3.10+
#   - FFmpeg with NVENC support (or CPU encoding)
#   - Real-ESRGAN or NVIDIA Maxine SDK
#   - Optional: GFPGAN for face restoration
#   - Optional: VapourSynth + QTGMC for advanced deinterlacing
#
# USAGE:
#   ./vhs_full_pipeline.sh input.mp4 output.mp4
#   ./vhs_full_pipeline.sh "home_video_1995.avi" "restored_1995.mp4"
#
# CUSTOMIZATION:
#   Edit the "CONFIGURATION" section below to adjust processing parameters.
#
################################################################################

set -e  # Exit on error

################################################################################
# CONFIGURATION
################################################################################

# Video Processing Settings
RESOLUTION="1080"                 # Target resolution (1080, 1440, 2160)
PRESET="vhs"                      # Preset: vhs, dvd, clean, youtube
ENGINE="auto"                     # Upscale engine: auto, maxine, realesrgan, ffmpeg
ENCODER="h265_nvenc"              # Encoder: h265_nvenc, h264_nvenc, libx265, libx264
CRF="20"                          # Quality (lower = better): 18-28
QUALITY_MODE="high"               # Quality mode: high, balanced, fast

# Deinterlacing Settings
DEINTERLACE_ALGO="yadif"          # yadif (fast), qtgmc (best, requires VapourSynth)
QTGMC_PRESET="Medium"             # QTGMC preset: Fast, Medium, Slow, Slower (if using qtgmc)

# Face Restoration (Optional - set to "true" to enable)
ENABLE_FACE_RESTORE="false"       # Enable GFPGAN face restoration
FACE_RESTORE_STRENGTH="0.7"       # Restoration strength: 0.0-1.0 (higher = more aggressive)
FACE_RESTORE_UPSCALE="2"          # Face upscale factor: 1, 2, 4

# Audio Enhancement
AUDIO_ENHANCE="voice"             # none, light, moderate, aggressive, voice, music
AUDIO_UPMIX="none"                # none, simple, surround, prologic, demucs
AUDIO_LAYOUT="original"           # original, stereo, 5.1, 7.1
AUDIO_FORMAT="aac"                # aac, ac3, eac3, dts, flac
AUDIO_BITRATE="192k"              # Audio bitrate

# Advanced Options
KEEP_TEMP="false"                 # Keep temporary files for debugging
VERBOSE="false"                   # Enable verbose logging

################################################################################
# INPUT VALIDATION
################################################################################

# Check arguments
if [ $# -lt 2 ]; then
    echo "ERROR: Missing required arguments"
    echo ""
    echo "Usage: $0 INPUT_FILE OUTPUT_FILE"
    echo ""
    echo "Examples:"
    echo "  $0 vhs_tape.avi restored.mp4"
    echo "  $0 \"family_1990.mp4\" \"output/family_1990_restored.mp4\""
    echo ""
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="$2"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "ERROR: Input file not found: $INPUT_FILE"
    exit 1
fi

# Create output directory if it doesn't exist
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
fi

################################################################################
# PROCESSING
################################################################################

echo "=============================================================================="
echo "VHS FULL PIPELINE - Complete Restoration"
echo "=============================================================================="
echo ""
echo "Configuration:"
echo "  Input:           $INPUT_FILE"
echo "  Output:          $OUTPUT_FILE"
echo "  Resolution:      ${RESOLUTION}p"
echo "  Preset:          $PRESET"
echo "  Engine:          $ENGINE"
echo "  Encoder:         $ENCODER"
echo "  Deinterlace:     $DEINTERLACE_ALGO"
echo "  Face Restore:    $ENABLE_FACE_RESTORE"
echo "  Audio Enhance:   $AUDIO_ENHANCE"
echo ""
echo "Processing stages:"
echo "  1. DEINTERLACE   → Remove interlaced combing artifacts"
echo "  2. DENOISE       → Remove VHS tape noise"
echo "  3. UPSCALE       → AI upscaling (${ENGINE})"
if [ "$ENABLE_FACE_RESTORE" = "true" ]; then
echo "  4. FACE RESTORE  → GFPGAN face enhancement (strength ${FACE_RESTORE_STRENGTH})"
fi
echo "  5. SHARPEN       → Contrast adaptive sharpening"
echo "  6. ENCODE        → ${ENCODER} @ CRF ${CRF}"
echo ""
echo "=============================================================================="
echo ""

# Build command
CMD="python -m vhs_upscaler.cli.upscale"
CMD="$CMD \"$INPUT_FILE\""
CMD="$CMD -o \"$OUTPUT_FILE\""
CMD="$CMD -r $RESOLUTION"
CMD="$CMD -p $PRESET"
CMD="$CMD --engine $ENGINE"
CMD="$CMD --encoder $ENCODER"
CMD="$CMD --crf $CRF"
CMD="$CMD --quality $QUALITY_MODE"

# Deinterlacing
CMD="$CMD --deinterlace-algorithm $DEINTERLACE_ALGO"
if [ "$DEINTERLACE_ALGO" = "qtgmc" ]; then
    CMD="$CMD --qtgmc-preset $QTGMC_PRESET"
fi

# Face restoration
if [ "$ENABLE_FACE_RESTORE" = "true" ]; then
    CMD="$CMD --face-restore"
    CMD="$CMD --face-restore-strength $FACE_RESTORE_STRENGTH"
    CMD="$CMD --face-restore-upscale $FACE_RESTORE_UPSCALE"
fi

# Audio processing
CMD="$CMD --audio-enhance $AUDIO_ENHANCE"
CMD="$CMD --audio-upmix $AUDIO_UPMIX"
CMD="$CMD --audio-layout $AUDIO_LAYOUT"
CMD="$CMD --audio-format $AUDIO_FORMAT"
CMD="$CMD --audio-bitrate $AUDIO_BITRATE"

# Advanced options
if [ "$KEEP_TEMP" = "true" ]; then
    CMD="$CMD --keep-temp"
fi
if [ "$VERBOSE" = "true" ]; then
    CMD="$CMD -v"
fi

# Execute
echo "Starting processing..."
echo ""
eval $CMD

# Check result
if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================================================="
    echo "SUCCESS! VHS restoration complete."
    echo "=============================================================================="
    echo ""
    echo "Output saved to: $OUTPUT_FILE"
    echo ""

    # Display file size if output exists
    if [ -f "$OUTPUT_FILE" ]; then
        OUTPUT_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
        echo "Output file size: $OUTPUT_SIZE"
    fi

    echo ""
    echo "Next steps:"
    echo "  - Review the output video"
    echo "  - Compare quality with the original"
    echo "  - Adjust settings if needed and re-process"
    echo ""
else
    echo ""
    echo "ERROR: Processing failed. Check the error messages above."
    echo ""
    exit 1
fi

################################################################################
# END OF SCRIPT
################################################################################
