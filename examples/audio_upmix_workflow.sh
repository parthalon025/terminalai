#!/bin/bash
################################################################################
# Audio Enhancement and Surround Upmix Workflow
################################################################################
#
# PURPOSE:
#   Extract audio from video, enhance it, and upmix to 5.1/7.1 surround.
#   Perfect for restoring VHS dialogue or creating immersive audio from stereo.
#
# WORKFLOW:
#   1. Extract audio from video → Stereo WAV
#   2. Audio enhancement → Noise reduction, EQ, normalization
#   3. Surround upmix → Convert stereo to 5.1 or 7.1
#   4. Encode to target format → AC3, EAC3, DTS, or AAC
#   5. Mux back with video → Final video with enhanced surround audio
#
# UPMIX ALGORITHMS:
#   - simple:   Fast FFmpeg pan filter (★★☆☆☆)
#   - surround: FFmpeg surround filter (★★★☆☆)
#   - prologic: Dolby Pro Logic II decoder (★★★☆☆)
#   - demucs:   AI stem separation - BEST quality (★★★★★, requires PyTorch)
#
# REQUIREMENTS:
#   - Python 3.10+
#   - FFmpeg
#   - For Demucs AI: pip install torch torchaudio demucs
#
# USAGE:
#   ./audio_upmix_workflow.sh input.mp4 output.mp4
#   ./audio_upmix_workflow.sh "vhs_tape.avi" "enhanced_5.1.mp4"
#
# CUSTOMIZATION:
#   Edit the "CONFIGURATION" section below for different enhancement modes.
#
################################################################################

set -e  # Exit on error

################################################################################
# CONFIGURATION
################################################################################

# Audio Enhancement Settings
ENHANCE_MODE="voice"               # none, light, moderate, aggressive, voice, music
NORMALIZE="true"                   # Enable loudness normalization (EBU R128)
TARGET_LOUDNESS="-14"              # Target loudness in LUFS (-14 = streaming standard)

# Surround Upmix Settings
UPMIX_MODE="prologic"              # none, simple, surround, prologic, demucs
OUTPUT_LAYOUT="5.1"                # stereo, 5.1, 7.1
LFE_CROSSOVER="120"                # LFE crossover frequency in Hz (80-150)
CENTER_MIX_LEVEL="0.707"           # Center channel mix level (-3dB default)

# Audio Output Format
AUDIO_FORMAT="ac3"                 # aac, ac3, eac3, dts, flac
AUDIO_BITRATE="640k"               # Total bitrate (192k per channel for 5.1 ≈ 1152k)

# Demucs AI Settings (only used if UPMIX_MODE="demucs")
DEMUCS_MODEL="htdemucs"            # htdemucs, htdemucs_ft, mdx_extra
DEMUCS_DEVICE="auto"               # auto (uses GPU if available), cuda, cpu

# Video Processing (Optional)
COPY_VIDEO="true"                  # Copy video stream (true) or re-encode (false)
VIDEO_ENCODER="h264_nvenc"         # Only used if COPY_VIDEO="false"
VIDEO_CRF="20"                     # Only used if COPY_VIDEO="false"

# Advanced Settings
KEEP_TEMP="false"                  # Keep temporary audio files for debugging
VERBOSE="false"                    # Enable verbose logging

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
    echo "  $0 input.mp4 output_5.1.mp4"
    echo "  $0 vhs_tape.avi enhanced_surround.mp4"
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

# Create output directory if needed
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
fi

################################################################################
# DISPLAY CONFIGURATION
################################################################################

echo "=============================================================================="
echo "Audio Enhancement and Surround Upmix Workflow"
echo "=============================================================================="
echo ""
echo "Configuration:"
echo "  Input:            $INPUT_FILE"
echo "  Output:           $OUTPUT_FILE"
echo ""
echo "Enhancement:"
echo "  Mode:             $ENHANCE_MODE"
echo "  Normalize:        $NORMALIZE"
if [ "$NORMALIZE" = "true" ]; then
echo "  Target Loudness:  ${TARGET_LOUDNESS} LUFS"
fi
echo ""
echo "Surround Upmix:"
echo "  Algorithm:        $UPMIX_MODE"
echo "  Output Layout:    $OUTPUT_LAYOUT"
echo "  Format:           $AUDIO_FORMAT @ $AUDIO_BITRATE"
if [ "$UPMIX_MODE" != "none" ]; then
echo "  LFE Crossover:    ${LFE_CROSSOVER} Hz"
echo "  Center Mix:       $CENTER_MIX_LEVEL"
fi
if [ "$UPMIX_MODE" = "demucs" ]; then
echo ""
echo "Demucs AI:"
echo "  Model:            $DEMUCS_MODEL"
echo "  Device:           $DEMUCS_DEVICE"
fi
echo ""
echo "Processing stages:"
echo "  1. EXTRACT       → Extract audio from video"
echo "  2. ENHANCE       → $ENHANCE_MODE enhancement"
if [ "$NORMALIZE" = "true" ]; then
echo "  3. NORMALIZE     → EBU R128 loudness normalization"
fi
if [ "$UPMIX_MODE" != "none" ]; then
echo "  4. UPMIX         → $UPMIX_MODE algorithm (${OUTPUT_LAYOUT})"
fi
echo "  5. ENCODE        → $AUDIO_FORMAT @ $AUDIO_BITRATE"
echo "  6. MUX           → Combine with video"
echo ""
echo "=============================================================================="
echo ""

################################################################################
# AUDIO-ONLY WORKFLOW (using Python module)
################################################################################

# Build command for the upscaler (it handles audio processing)
CMD="python -m vhs_upscaler.cli.upscale"
CMD="$CMD \"$INPUT_FILE\""
CMD="$CMD -o \"$OUTPUT_FILE\""

# Audio enhancement
CMD="$CMD --audio-enhance $ENHANCE_MODE"

# Surround upmix
CMD="$CMD --audio-upmix $UPMIX_MODE"
CMD="$CMD --audio-layout $OUTPUT_LAYOUT"
CMD="$CMD --audio-format $AUDIO_FORMAT"
CMD="$CMD --audio-bitrate $AUDIO_BITRATE"

# Normalization
if [ "$NORMALIZE" = "false" ]; then
    CMD="$CMD --no-audio-normalize"
fi

# Video handling
if [ "$COPY_VIDEO" = "true" ]; then
    # Use copy preset to skip video processing
    CMD="$CMD -p clean --skip-maxine"
    # Override to use fastest settings (just copy video)
    CMD="$CMD --engine ffmpeg"
else
    # Re-encode video
    CMD="$CMD --encoder $VIDEO_ENCODER"
    CMD="$CMD --crf $VIDEO_CRF"
fi

# Advanced options
if [ "$KEEP_TEMP" = "true" ]; then
    CMD="$CMD --keep-temp"
fi
if [ "$VERBOSE" = "true" ]; then
    CMD="$CMD -v"
fi

################################################################################
# EXECUTE PROCESSING
################################################################################

echo "Starting audio processing..."
echo ""

# Execute command
eval $CMD

# Check result
if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================================================="
    echo "SUCCESS! Audio enhancement complete."
    echo "=============================================================================="
    echo ""
    echo "Output saved to: $OUTPUT_FILE"
    echo ""

    # Display file info
    if [ -f "$OUTPUT_FILE" ]; then
        OUTPUT_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
        echo "Output file size: $OUTPUT_SIZE"

        # Display audio stream info using ffprobe
        if command -v ffprobe &> /dev/null; then
            echo ""
            echo "Audio stream information:"
            ffprobe -v error -select_streams a:0 \
                    -show_entries stream=codec_name,channels,channel_layout,bit_rate \
                    -of default=noprint_wrappers=1 \
                    "$OUTPUT_FILE" 2>/dev/null || true
        fi
    fi

    echo ""
    echo "Next steps:"
    echo "  - Play the output file to hear the enhanced audio"
    echo "  - Compare with original using headphones or surround system"
    echo "  - Adjust settings if needed:"
    if [ "$ENHANCE_MODE" = "voice" ]; then
        echo "    * Try 'music' mode for music-heavy content"
    fi
    if [ "$UPMIX_MODE" != "demucs" ]; then
        echo "    * Try 'demucs' upmix for best quality (requires PyTorch)"
    fi
    echo ""
else
    echo ""
    echo "=============================================================================="
    echo "ERROR: Audio processing failed."
    echo "=============================================================================="
    echo ""
    echo "Common issues:"
    echo ""

    if [ "$UPMIX_MODE" = "demucs" ]; then
        echo "  Demucs AI requirements:"
        echo "    - Install PyTorch: pip install torch torchaudio"
        echo "    - Install Demucs: pip install demucs"
        echo "    - GPU recommended for faster processing"
        echo ""
    fi

    echo "  General troubleshooting:"
    echo "    - Check FFmpeg installation: ffmpeg -version"
    echo "    - Verify input file has audio: ffprobe \"$INPUT_FILE\""
    echo "    - Try with --verbose flag for detailed logs"
    echo "    - Use simpler upmix mode (surround or prologic)"
    echo ""
    exit 1
fi

################################################################################
# QUALITY TIPS
################################################################################

echo "Audio Quality Tips:"
echo "=============================================================================="
echo ""
echo "Enhancement Modes:"
echo "  voice      - Best for VHS dialogue (reduces tape hiss, boosts clarity)"
echo "  music      - Preserves dynamics for music content"
echo "  aggressive - Heavy noise reduction for very noisy sources"
echo ""
echo "Upmix Algorithms (Quality Rating):"
echo "  simple     - ★★☆☆☆ Fast but basic channel duplication"
echo "  surround   - ★★★☆☆ Good balance of speed and quality"
echo "  prologic   - ★★★☆☆ Dolby Pro Logic II decoder"
echo "  demucs     - ★★★★★ AI stem separation (best, slower, needs GPU)"
echo ""
echo "Format Recommendations:"
echo "  AC3    - Standard 5.1 (compatible with all devices)"
echo "  EAC3   - Enhanced AC3 (better quality, modern devices)"
echo "  DTS    - High quality (larger file size)"
echo "  AAC    - Best for stereo or web streaming"
echo "  FLAC   - Lossless (huge file size)"
echo ""
echo "Bitrate Guidelines:"
echo "  Stereo:  192k - 320k"
echo "  5.1:     640k - 1536k (192k per channel × 6 ÷ efficiency)"
echo "  7.1:     768k - 2048k"
echo ""
echo "=============================================================================="
echo ""

################################################################################
# END OF SCRIPT
################################################################################
