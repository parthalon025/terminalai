#!/bin/bash
################################################################################
# YouTube Batch Downloader and Processor
################################################################################
#
# PURPOSE:
#   Download and process multiple YouTube videos in one workflow.
#   Supports individual video URLs, playlists, and channel downloads.
#
# FEATURES:
#   - Batch download from URL list file
#   - Automatic preset selection for YouTube content
#   - Sequential or parallel processing
#   - Resume capability for interrupted batches
#   - Quality selection (best, 1080p, 720p, etc.)
#
# REQUIREMENTS:
#   - Python 3.10+
#   - yt-dlp (pip install yt-dlp)
#   - FFmpeg
#   - Real-ESRGAN or NVIDIA Maxine (for upscaling)
#
# USAGE:
#   # Single video
#   ./youtube_batch.sh "https://youtube.com/watch?v=VIDEO_ID"
#
#   # Multiple videos from file
#   ./youtube_batch.sh urls.txt
#
#   # Playlist
#   ./youtube_batch.sh "https://youtube.com/playlist?list=PLAYLIST_ID"
#
# URL FILE FORMAT (urls.txt):
#   https://youtube.com/watch?v=VIDEO_ID_1
#   https://youtube.com/watch?v=VIDEO_ID_2
#   https://youtube.com/watch?v=VIDEO_ID_3
#
# CUSTOMIZATION:
#   Edit the "CONFIGURATION" section below to adjust download and processing.
#
################################################################################

set -e  # Exit on error

################################################################################
# CONFIGURATION
################################################################################

# Output Settings
OUTPUT_DIR="./youtube_downloads"  # Output directory for all files
UPSCALED_DIR="./youtube_upscaled" # Directory for upscaled videos

# Download Settings
DOWNLOAD_QUALITY="best"            # best, 1080p, 720p, 480p, 360p
DOWNLOAD_FORMAT="mp4"              # mp4, webm, mkv
DOWNLOAD_PLAYLIST="false"          # Allow playlist downloads (true/false)
DOWNLOAD_SUBTITLES="false"         # Download subtitles (true/false)
KEEP_ORIGINALS="true"              # Keep downloaded originals after upscaling

# Processing Settings
ENABLE_UPSCALING="true"            # Enable AI upscaling (set to "false" to just download)
RESOLUTION="1080"                  # Target resolution (1080, 1440, 2160)
PRESET="youtube"                   # Preset: youtube, clean (youtube recommended for compressed content)
ENGINE="auto"                      # Upscale engine: auto, maxine, realesrgan, ffmpeg
ENCODER="h264_nvenc"               # Encoder: h264_nvenc, h265_nvenc, libx264, libx265
CRF="23"                           # Quality (18-28, lower = better)

# Audio Settings
AUDIO_ENHANCE="light"              # none, light, moderate, aggressive, voice, music
AUDIO_FORMAT="aac"                 # aac, ac3, eac3

# Advanced Settings
PARALLEL_DOWNLOADS="1"             # Number of simultaneous downloads (1 = sequential)
PARALLEL_PROCESSING="1"            # Number of simultaneous upscales (1 = sequential)
SKIP_EXISTING="true"               # Skip already downloaded/processed videos
VERBOSE="false"                    # Enable verbose logging

################################################################################
# HELPER FUNCTIONS
################################################################################

# Check if yt-dlp is installed
check_ytdlp() {
    if ! command -v yt-dlp &> /dev/null; then
        echo "ERROR: yt-dlp is not installed"
        echo ""
        echo "Install with: pip install yt-dlp"
        echo ""
        exit 1
    fi
}

# Download a single video
download_video() {
    local url="$1"
    local output_template="${OUTPUT_DIR}/%(title)s.%(ext)s"

    echo "Downloading: $url"

    # Build yt-dlp command
    local cmd="yt-dlp"

    # Quality selection
    if [ "$DOWNLOAD_QUALITY" = "best" ]; then
        cmd="$cmd -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    else
        cmd="$cmd -f bestvideo[height<=${DOWNLOAD_QUALITY%p}][ext=mp4]+bestaudio[ext=m4a]/best"
    fi

    # Output format and template
    cmd="$cmd --merge-output-format $DOWNLOAD_FORMAT"
    cmd="$cmd -o \"$output_template\""

    # Playlist handling
    if [ "$DOWNLOAD_PLAYLIST" = "false" ]; then
        cmd="$cmd --no-playlist"
    fi

    # Subtitles
    if [ "$DOWNLOAD_SUBTITLES" = "true" ]; then
        cmd="$cmd --write-sub --sub-lang en"
    fi

    # Skip existing
    if [ "$SKIP_EXISTING" = "true" ]; then
        cmd="$cmd --no-overwrites"
    fi

    # Progress display
    cmd="$cmd --progress"

    # Execute download
    eval $cmd

    if [ $? -eq 0 ]; then
        echo "Download complete"
        return 0
    else
        echo "Download failed: $url"
        return 1
    fi
}

# Process a downloaded video
process_video() {
    local input_file="$1"
    local filename=$(basename "$input_file")
    local name_no_ext="${filename%.*}"
    local output_file="${UPSCALED_DIR}/${name_no_ext}_${RESOLUTION}p.mp4"

    # Skip if already processed
    if [ "$SKIP_EXISTING" = "true" ] && [ -f "$output_file" ]; then
        echo "Skipping (already processed): $filename"
        return 0
    fi

    echo "Processing: $filename"

    # Build upscale command
    local cmd="python -m vhs_upscaler.cli.upscale"
    cmd="$cmd \"$input_file\""
    cmd="$cmd -o \"$output_file\""
    cmd="$cmd -r $RESOLUTION"
    cmd="$cmd -p $PRESET"
    cmd="$cmd --engine $ENGINE"
    cmd="$cmd --encoder $ENCODER"
    cmd="$cmd --crf $CRF"
    cmd="$cmd --audio-enhance $AUDIO_ENHANCE"
    cmd="$cmd --audio-format $AUDIO_FORMAT"

    if [ "$VERBOSE" = "true" ]; then
        cmd="$cmd -v"
    fi

    # Execute processing
    eval $cmd

    if [ $? -eq 0 ]; then
        echo "Processing complete: $filename"

        # Delete original if requested
        if [ "$KEEP_ORIGINALS" = "false" ]; then
            echo "Removing original: $filename"
            rm "$input_file"
        fi

        return 0
    else
        echo "Processing failed: $filename"
        return 1
    fi
}

################################################################################
# MAIN SCRIPT
################################################################################

# Check requirements
check_ytdlp

# Create output directories
mkdir -p "$OUTPUT_DIR"
if [ "$ENABLE_UPSCALING" = "true" ]; then
    mkdir -p "$UPSCALED_DIR"
fi

echo "=============================================================================="
echo "YouTube Batch Downloader and Processor"
echo "=============================================================================="
echo ""
echo "Configuration:"
echo "  Download Quality:  $DOWNLOAD_QUALITY"
echo "  Output Directory:  $OUTPUT_DIR"

if [ "$ENABLE_UPSCALING" = "true" ]; then
    echo "  Upscale Enabled:   Yes"
    echo "  Target Resolution: ${RESOLUTION}p"
    echo "  Upscale Preset:    $PRESET"
    echo "  Upscale Engine:    $ENGINE"
    echo "  Upscaled Output:   $UPSCALED_DIR"
else
    echo "  Upscale Enabled:   No (download only)"
fi

echo ""
echo "=============================================================================="
echo ""

# Check arguments
if [ $# -lt 1 ]; then
    echo "ERROR: Missing URL or URL file"
    echo ""
    echo "Usage:"
    echo "  $0 URL                    # Download single video"
    echo "  $0 urls.txt              # Download from URL list file"
    echo ""
    echo "Examples:"
    echo "  $0 'https://youtube.com/watch?v=VIDEO_ID'"
    echo "  $0 youtube_urls.txt"
    echo ""
    exit 1
fi

INPUT="$1"

################################################################################
# DOWNLOAD PHASE
################################################################################

DOWNLOAD_SUCCESS=0
DOWNLOAD_FAILED=0

echo "Starting download phase..."
echo ""

# Check if input is a file or URL
if [ -f "$INPUT" ]; then
    # Read URLs from file
    echo "Reading URLs from file: $INPUT"
    echo ""

    while IFS= read -r url || [ -n "$url" ]; do
        # Skip empty lines and comments
        [[ -z "$url" || "$url" =~ ^[[:space:]]*# ]] && continue

        if download_video "$url"; then
            ((DOWNLOAD_SUCCESS++))
        else
            ((DOWNLOAD_FAILED++))
        fi
        echo ""
    done < "$INPUT"
else
    # Single URL
    if download_video "$INPUT"; then
        ((DOWNLOAD_SUCCESS++))
    else
        ((DOWNLOAD_FAILED++))
    fi
fi

echo ""
echo "Download phase complete"
echo "  Success: $DOWNLOAD_SUCCESS"
echo "  Failed:  $DOWNLOAD_FAILED"
echo ""

################################################################################
# PROCESSING PHASE
################################################################################

if [ "$ENABLE_UPSCALING" = "true" ]; then
    echo "Starting processing phase..."
    echo ""

    PROCESS_SUCCESS=0
    PROCESS_FAILED=0

    # Process all downloaded videos
    for video_file in "$OUTPUT_DIR"/*.{mp4,webm,mkv}; do
        # Skip if glob didn't match any files
        [ -e "$video_file" ] || continue

        if process_video "$video_file"; then
            ((PROCESS_SUCCESS++))
        else
            ((PROCESS_FAILED++))
        fi
        echo ""
    done

    echo ""
    echo "Processing phase complete"
    echo "  Success: $PROCESS_SUCCESS"
    echo "  Failed:  $PROCESS_FAILED"
    echo ""
fi

################################################################################
# SUMMARY
################################################################################

echo "=============================================================================="
echo "BATCH PROCESSING COMPLETE"
echo "=============================================================================="
echo ""
echo "Download Results:"
echo "  Success:        $DOWNLOAD_SUCCESS"
echo "  Failed:         $DOWNLOAD_FAILED"
echo "  Download Dir:   $OUTPUT_DIR"

if [ "$ENABLE_UPSCALING" = "true" ]; then
    echo ""
    echo "Processing Results:"
    echo "  Success:        $PROCESS_SUCCESS"
    echo "  Failed:         $PROCESS_FAILED"
    echo "  Upscaled Dir:   $UPSCALED_DIR"
fi

echo ""
echo "Next steps:"
echo "  - Review processed videos in: $UPSCALED_DIR"
echo "  - Check originals in: $OUTPUT_DIR"
if [ "$DOWNLOAD_FAILED" -gt 0 ] || [ "$PROCESS_FAILED" -gt 0 ]; then
    echo "  - Review errors for failed videos above"
fi
echo ""

################################################################################
# END OF SCRIPT
################################################################################
