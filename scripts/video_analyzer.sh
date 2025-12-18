#!/bin/bash
#
# Video Analyzer - Bash Backend
#
# This is a placeholder for the user-provided video_analyzer.sh implementation.
# The full implementation should analyze video characteristics and output JSON
# matching the VideoAnalysis schema.
#
# Usage:
#   bash video_analyzer.sh [--json-only] <video_file>
#
# Output:
#   JSON object with video analysis results
#

set -e

# Parse arguments
JSON_ONLY=false
VIDEO_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --json-only)
            JSON_ONLY=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--json-only] <video_file>"
            echo ""
            echo "Options:"
            echo "  --json-only    Output only JSON (no verbose logging)"
            echo "  --help         Show this help message"
            exit 0
            ;;
        *)
            VIDEO_FILE="$1"
            shift
            ;;
    esac
done

if [ -z "$VIDEO_FILE" ]; then
    echo "Error: No video file specified" >&2
    echo "Usage: $0 [--json-only] <video_file>" >&2
    exit 1
fi

if [ ! -f "$VIDEO_FILE" ]; then
    echo "Error: File not found: $VIDEO_FILE" >&2
    exit 1
fi

# Check for required tools
if ! command -v ffprobe &> /dev/null; then
    echo "Error: ffprobe not found. Please install FFmpeg." >&2
    exit 1
fi

# Extract metadata with ffprobe
METADATA=$(ffprobe -v quiet -print_format json -show_format -show_streams "$VIDEO_FILE" 2>&1)

# Parse video stream
VIDEO_STREAM=$(echo "$METADATA" | grep -A 50 '"codec_type": "video"' | head -60)
WIDTH=$(echo "$VIDEO_STREAM" | grep -o '"width": [0-9]*' | grep -o '[0-9]*' | head -1)
HEIGHT=$(echo "$VIDEO_STREAM" | grep -o '"height": [0-9]*' | grep -o '[0-9]*' | head -1)
CODEC=$(echo "$VIDEO_STREAM" | grep -o '"codec_name": "[^"]*"' | cut -d'"' -f4 | head -1)

# Parse format
FORMAT=$(echo "$METADATA" | grep -A 20 '"format"')
DURATION=$(echo "$FORMAT" | grep -o '"duration": "[^"]*"' | cut -d'"' -f4)
SIZE=$(echo "$FORMAT" | grep -o '"size": "[^"]*"' | cut -d'"' -f4)
BITRATE=$(echo "$FORMAT" | grep -o '"bit_rate": "[^"]*"' | cut -d'"' -f4)

# Calculate derived values
FILESIZE_MB=$(awk "BEGIN {printf \"%.2f\", $SIZE / 1048576}")
BITRATE_KBPS=$(awk "BEGIN {printf \"%d\", $BITRATE / 1000}")

# Basic source format detection
SOURCE_FORMAT="unknown"
if [ "$WIDTH" = "720" ] && ([ "$HEIGHT" = "480" ] || [ "$HEIGHT" = "576" ]); then
    SOURCE_FORMAT="vhs"
elif [ "$WIDTH" -ge "1920" ]; then
    SOURCE_FORMAT="digital"
fi

# Output JSON
cat <<EOF
{
  "filepath": "$VIDEO_FILE",
  "filename": "$(basename "$VIDEO_FILE")",
  "filesize_mb": $FILESIZE_MB,
  "duration_seconds": $DURATION,
  "width": ${WIDTH:-0},
  "height": ${HEIGHT:-0},
  "framerate": 29.97,
  "framerate_fraction": "30000/1001",
  "codec": "${CODEC:-unknown}",
  "pixel_format": "yuv420p",
  "bitrate_kbps": ${BITRATE_KBPS:-0},
  "scan_type": "unknown",
  "content_type": "live_action",
  "source_format": "$SOURCE_FORMAT",
  "noise_level": "medium",
  "estimated_quality_score": 50.0,
  "has_tracking_errors": false,
  "has_color_bleeding": false,
  "has_head_switching_noise": false,
  "has_dropout_lines": false,
  "has_jitter": false,
  "audio_codec": "aac",
  "audio_channels": 2,
  "audio_sample_rate": 44100,
  "audio_bitrate_kbps": 128,
  "recommended_tools": ["ffmpeg"],
  "recommended_settings": {
    "preset": "clean"
  },
  "processing_notes": [
    "Basic bash analyzer - limited detection capabilities",
    "Consider using Python+OpenCV backend for better analysis"
  ],
  "estimated_processing_time": ""
}
EOF
