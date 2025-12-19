#!/bin/bash
################################################################################
# Preset Comparison Testing
################################################################################
#
# PURPOSE:
#   Test multiple presets side-by-side to help you choose the best settings
#   for your content. Generates comparison videos and reports.
#
# FEATURES:
#   - Extract representative clips from your video
#   - Process same clips with different presets
#   - Create side-by-side comparison grid
#   - Generate quality comparison report
#   - Save time by testing on short clips first
#
# OUTPUT:
#   - Individual preset videos (preset_vhs.mp4, preset_dvd.mp4, etc.)
#   - Comparison grid video (all presets in one video)
#   - Quality comparison report (text file)
#
# REQUIREMENTS:
#   - Python 3.10+
#   - FFmpeg
#   - Real-ESRGAN or NVIDIA Maxine (for upscaling)
#
# USAGE:
#   ./comparison_testing.sh input.mp4
#   ./comparison_testing.sh input.mp4 --start 60 --duration 15
#   ./comparison_testing.sh input.mp4 --presets vhs,dvd,clean
#
# CUSTOMIZATION:
#   Edit the "CONFIGURATION" section below to test different presets.
#
################################################################################

set -e  # Exit on error

################################################################################
# CONFIGURATION
################################################################################

# Test Clip Settings
AUTO_START="true"                  # Auto-select start time (25% through video)
CLIP_START="60"                    # Manual start time in seconds (if AUTO_START="false")
CLIP_DURATION="10"                 # Test clip duration in seconds
MULTI_CLIP="false"                 # Extract multiple clips for comprehensive testing
CLIP_COUNT="3"                     # Number of clips if MULTI_CLIP="true"

# Presets to Test (comma-separated)
PRESETS="vhs,dvd,clean,youtube"    # Available: vhs, dvd, webcam, clean, youtube

# Processing Settings
RESOLUTION="1080"                  # Target resolution (1080, 1440, 2160)
ENGINE="auto"                      # Upscale engine: auto, maxine, realesrgan, ffmpeg
ENCODER="h264_nvenc"               # Encoder: h264_nvenc, h265_nvenc, libx264, libx265
CRF="20"                           # Quality (18-28, lower = better)

# Comparison Grid Settings
CREATE_GRID="true"                 # Create comparison grid video
GRID_LAYOUT="2x2"                  # Grid layout: 2x2, 2x3, 3x2, 1x4, 4x1

# Output Settings
OUTPUT_DIR="./comparison_tests"    # Output directory for all test files
KEEP_INDIVIDUAL_CLIPS="true"       # Keep individual preset videos

# Advanced Settings
VERBOSE="false"                    # Enable verbose logging

################################################################################
# HELPER FUNCTIONS
################################################################################

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --start)
                CLIP_START="$2"
                AUTO_START="false"
                shift 2
                ;;
            --duration)
                CLIP_DURATION="$2"
                shift 2
                ;;
            --presets)
                PRESETS="$2"
                shift 2
                ;;
            --resolution|-r)
                RESOLUTION="$2"
                shift 2
                ;;
            --multi-clip)
                MULTI_CLIP="true"
                shift
                ;;
            --clip-count)
                CLIP_COUNT="$2"
                shift 2
                ;;
            --no-grid)
                CREATE_GRID="false"
                shift
                ;;
            --grid-layout)
                GRID_LAYOUT="$2"
                shift 2
                ;;
            --output|-o)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            --verbose|-v)
                VERBOSE="true"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                if [ -z "$INPUT_FILE" ]; then
                    INPUT_FILE="$1"
                else
                    echo "ERROR: Unknown argument: $1"
                    exit 1
                fi
                shift
                ;;
        esac
    done
}

# Show help message
show_help() {
    echo "Usage: $0 INPUT_FILE [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --start SECONDS         Start time for test clip (default: auto 25%)"
    echo "  --duration SECONDS      Clip duration (default: 10)"
    echo "  --presets LIST          Comma-separated presets (default: vhs,dvd,clean,youtube)"
    echo "  -r, --resolution RES    Target resolution (default: 1080)"
    echo "  --multi-clip            Extract multiple clips for testing"
    echo "  --clip-count N          Number of clips for multi-clip mode (default: 3)"
    echo "  --no-grid               Skip comparison grid creation"
    echo "  --grid-layout LAYOUT    Grid layout: 2x2, 2x3, 3x2, 1x4, 4x1 (default: 2x2)"
    echo "  -o, --output DIR        Output directory (default: ./comparison_tests)"
    echo "  -v, --verbose           Enable verbose logging"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 video.mp4"
    echo "  $0 video.mp4 --start 60 --duration 15"
    echo "  $0 video.mp4 --presets vhs,dvd --resolution 2160"
    echo "  $0 video.mp4 --multi-clip --clip-count 5"
    echo ""
}

################################################################################
# INPUT VALIDATION
################################################################################

# Parse arguments
INPUT_FILE=""
parse_args "$@"

# Check if input file provided
if [ -z "$INPUT_FILE" ]; then
    echo "ERROR: No input file specified"
    echo ""
    show_help
    exit 1
fi

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "ERROR: Input file not found: $INPUT_FILE"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

################################################################################
# DISPLAY CONFIGURATION
################################################################################

echo "=============================================================================="
echo "Preset Comparison Testing"
echo "=============================================================================="
echo ""
echo "Input:             $INPUT_FILE"
echo "Output Directory:  $OUTPUT_DIR"
echo ""
echo "Test Clip Settings:"
if [ "$AUTO_START" = "true" ]; then
echo "  Start Time:      Auto-detect (25% through video)"
else
echo "  Start Time:      ${CLIP_START}s"
fi
echo "  Duration:        ${CLIP_DURATION}s"
if [ "$MULTI_CLIP" = "true" ]; then
echo "  Multi-Clip:      Yes ($CLIP_COUNT clips)"
else
echo "  Multi-Clip:      No (single clip)"
fi
echo ""
echo "Presets to Test:   $PRESETS"
echo "Target Resolution: ${RESOLUTION}p"
echo "Upscale Engine:    $ENGINE"
echo ""
if [ "$CREATE_GRID" = "true" ]; then
echo "Comparison Grid:   Enabled (${GRID_LAYOUT} layout)"
else
echo "Comparison Grid:   Disabled"
fi
echo ""
echo "=============================================================================="
echo ""

################################################################################
# BUILD AND EXECUTE COMMAND
################################################################################

echo "Starting preset comparison..."
echo ""

# Build base command
CMD="python -m vhs_upscaler.cli.test-presets"
CMD="$CMD \"$INPUT_FILE\""
CMD="$CMD -o \"$OUTPUT_DIR\""

# Preset selection
CMD="$CMD --presets $PRESETS"

# Clip settings
if [ "$AUTO_START" = "false" ]; then
    CMD="$CMD --start $CLIP_START"
fi
CMD="$CMD --duration $CLIP_DURATION"

# Multi-clip mode
if [ "$MULTI_CLIP" = "true" ]; then
    CMD="$CMD --multi-clip"
    CMD="$CMD --clip-count $CLIP_COUNT"
fi

# Processing settings
CMD="$CMD -r $RESOLUTION"
CMD="$CMD --engine $ENGINE"
CMD="$CMD --encoder $ENCODER"
CMD="$CMD --crf $CRF"

# Grid settings
if [ "$CREATE_GRID" = "true" ]; then
    CMD="$CMD --create-grid"
    CMD="$CMD --grid-layout $GRID_LAYOUT"
fi

# Advanced options
if [ "$KEEP_INDIVIDUAL_CLIPS" = "true" ]; then
    CMD="$CMD --keep-temp"
fi
if [ "$VERBOSE" = "true" ]; then
    CMD="$CMD -v"
fi

# Execute
eval $CMD

# Check result
if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================================================="
    echo "SUCCESS! Preset comparison complete."
    echo "=============================================================================="
    echo ""
    echo "Output files:"
    echo "  Directory: $OUTPUT_DIR"
    echo ""

    # List generated files
    echo "Generated files:"
    if [ -f "$OUTPUT_DIR/original.mp4" ]; then
        echo "  ✓ original.mp4 (source clip)"
    fi

    # List preset videos
    IFS=',' read -ra PRESET_ARRAY <<< "$PRESETS"
    for preset in "${PRESET_ARRAY[@]}"; do
        preset=$(echo "$preset" | xargs)  # Trim whitespace
        if [ -f "$OUTPUT_DIR/preset_${preset}.mp4" ]; then
            echo "  ✓ preset_${preset}.mp4"
        fi
    done

    if [ -f "$OUTPUT_DIR/comparison_grid.mp4" ]; then
        echo "  ✓ comparison_grid.mp4 (side-by-side comparison)"
    fi

    if [ -f "$OUTPUT_DIR/comparison_report.txt" ]; then
        echo "  ✓ comparison_report.txt (quality report)"
    fi

    echo ""
    echo "Next steps:"
    echo "  1. Watch the comparison grid: $OUTPUT_DIR/comparison_grid.mp4"
    echo "  2. Compare individual preset videos side-by-side"
    echo "  3. Read the quality report: $OUTPUT_DIR/comparison_report.txt"
    echo "  4. Choose the best preset for your content"
    echo "  5. Process full video with selected preset"
    echo ""
    echo "Preset selection guide:"
    echo "  vhs      - Best for interlaced VHS tapes (deinterlace + heavy denoise)"
    echo "  dvd      - Best for DVD rips (moderate deinterlace + denoise)"
    echo "  webcam   - Best for low-quality webcam footage (heavy denoise)"
    echo "  youtube  - Best for downloaded YouTube videos (light processing)"
    echo "  clean    - Best for already high-quality sources (minimal processing)"
    echo ""

else
    echo ""
    echo "=============================================================================="
    echo "ERROR: Preset comparison failed."
    echo "=============================================================================="
    echo ""
    echo "Troubleshooting:"
    echo "  - Check input file is valid: ffprobe \"$INPUT_FILE\""
    echo "  - Verify FFmpeg is installed: ffmpeg -version"
    echo "  - Try with --verbose flag for detailed logs"
    echo "  - Reduce clip duration if processing is too slow"
    echo "  - Check available disk space in output directory"
    echo ""
    exit 1
fi

################################################################################
# COMPARISON ANALYSIS
################################################################################

echo "Comparison Analysis Tips:"
echo "=============================================================================="
echo ""
echo "What to look for when comparing presets:"
echo ""
echo "1. DEINTERLACING QUALITY"
echo "   - Look for combing artifacts (horizontal lines in motion)"
echo "   - VHS/DVD presets should remove interlacing"
echo "   - Clean preset skips deinterlacing (bad for interlaced content)"
echo ""
echo "2. NOISE REDUCTION"
echo "   - VHS preset has strongest denoise (good for noisy tapes)"
echo "   - DVD preset has moderate denoise"
echo "   - Clean/YouTube have minimal denoise (preserves detail)"
echo "   - Too much denoise = waxy, smooth faces (unnatural)"
echo ""
echo "3. DETAIL PRESERVATION"
echo "   - Check fine details like text, hair, textures"
echo "   - Aggressive denoise can remove fine detail"
echo "   - Clean preset preserves most detail"
echo ""
echo "4. COLOR ACCURACY"
echo "   - Compare colors between presets"
echo "   - VHS preset may boost contrast slightly"
echo "   - Look for natural skin tones"
echo ""
echo "5. SHARPNESS"
echo "   - AI upscaling should add sharpness"
echo "   - Avoid over-sharpening (halos around edges)"
echo "   - Natural sharpness > artificial sharpness"
echo ""
echo "6. MOTION SMOOTHNESS"
echo "   - Check fast motion scenes"
echo "   - Deinterlacing should create smooth motion"
echo "   - Look for judder or frame drops"
echo ""
echo "Use the comparison grid to play all presets simultaneously and spot"
echo "differences easily. Pause on complex scenes to compare detail."
echo ""
echo "=============================================================================="
echo ""

################################################################################
# END OF SCRIPT
################################################################################
