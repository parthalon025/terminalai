"""
Shared argument groups for CLI subcommands.

This module provides reusable argparse argument groups that are common across
multiple subcommands. Each function adds a logical group of related arguments
to the provided parser.

Usage:
    parser = argparse.ArgumentParser()
    add_upscale_arguments(parser)
    add_processing_arguments(parser)
    args = parser.parse_args()
"""

import argparse
from pathlib import Path
from typing import Optional


def add_upscale_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add upscaling-related arguments to parser.

    Arguments added:
        -r, --resolution: Target resolution (720, 1080, 1440, 2160)
        -q, --quality: Quality mode (0=best, 1=fast)
        --crf: Output quality CRF value
        --encoder: Output encoder (hevc_nvenc, h264_nvenc, libx265, libx264)
        -p, --preset: Processing preset (vhs, dvd, webcam, clean, youtube, auto)

    Args:
        parser: ArgumentParser instance to add arguments to
    """
    upscale_group = parser.add_argument_group(
        'Upscaling Options',
        'Control output resolution, quality, and processing presets'
    )

    upscale_group.add_argument(
        "-r", "--resolution",
        type=int,
        default=1080,
        choices=[720, 1080, 1440, 2160],
        help="Target resolution (default: 1080)"
    )

    upscale_group.add_argument(
        "-q", "--quality",
        type=int,
        default=0,
        choices=[0, 1],
        help="Quality mode: 0=best quality, 1=fast performance (default: 0)"
    )

    upscale_group.add_argument(
        "--crf",
        type=int,
        default=20,
        help="Output quality CRF (Constant Rate Factor): lower=better quality, "
             "higher=smaller file (default: 20, range: 0-51)"
    )

    upscale_group.add_argument(
        "--encoder",
        default="hevc_nvenc",
        choices=["hevc_nvenc", "h264_nvenc", "libx265", "libx264"],
        help="Output video encoder: hevc_nvenc/h264_nvenc (NVIDIA GPU), "
             "libx265/libx264 (CPU) (default: hevc_nvenc)"
    )

    upscale_group.add_argument(
        "-p", "--preset",
        default="vhs",
        choices=["vhs", "dvd", "webcam", "clean", "youtube", "auto"],
        help="Processing preset optimized for source type (default: vhs)"
    )


def add_processing_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add video processing arguments to parser.

    Arguments added:
        --deinterlace: Deinterlacing filter configuration
        --denoise: Denoise filter configuration
        --sharpen: Sharpening filter configuration
        --color-correct: Color correction filter
        --lut: Apply 3D LUT file for color grading
        --face-restore: Enable face restoration (experimental)

    Args:
        parser: ArgumentParser instance to add arguments to
    """
    processing_group = parser.add_argument_group(
        'Processing Options',
        'Video enhancement filters and corrections'
    )

    processing_group.add_argument(
        "--deinterlace",
        default=None,
        help="Deinterlacing filter (e.g., 'yadif=1', 'bwdif=1', 'none'). "
             "Auto-applied by presets. Use 'none' to disable."
    )

    processing_group.add_argument(
        "--deinterlace-algorithm",
        default="yadif",
        choices=["yadif", "bwdif", "w3fdif", "qtgmc"],
        help="Deinterlacing algorithm: yadif (fast), bwdif (better motion), "
             "w3fdif (better detail), qtgmc (best quality, requires VapourSynth) (default: yadif)"
    )

    processing_group.add_argument(
        "--qtgmc-preset",
        default=None,
        choices=["draft", "medium", "slow", "very_slow"],
        help="QTGMC quality preset (only for --deinterlace-algorithm qtgmc)"
    )

    processing_group.add_argument(
        "--denoise",
        default=None,
        help="Denoise filter (e.g., 'hqdn3d=4:3:6:4.5', 'nlmeans', 'none'). "
             "Auto-applied by presets. Use 'none' to disable."
    )

    processing_group.add_argument(
        "--sharpen",
        default=None,
        help="Sharpening filter (e.g., 'cas=0.4', 'unsharp', 'none'). "
             "Auto-applied by presets. Use 'none' to disable."
    )

    processing_group.add_argument(
        "--color-correct",
        default=None,
        help="Color correction filter (e.g., 'eq=saturation=1.1:brightness=0.02', 'none')"
    )

    processing_group.add_argument(
        "--lut",
        type=Path,
        default=None,
        help="Apply 3D LUT file for color grading (.cube format)"
    )

    processing_group.add_argument(
        "--lut-strength",
        type=float,
        default=1.0,
        help="LUT blend strength: 0.0 (no effect) to 1.0 (full strength) (default: 1.0)"
    )

    processing_group.add_argument(
        "--face-restore",
        action="store_true",
        help="Enable AI face restoration (experimental, requires additional dependencies)"
    )

    processing_group.add_argument(
        "--face-restore-strength",
        type=float,
        default=0.5,
        help="Face restoration strength: 0.0 (original) to 1.0 (full restoration) (default: 0.5)"
    )

    processing_group.add_argument(
        "--face-restore-upscale",
        type=int,
        default=2,
        choices=[1, 2, 4],
        help="Face restoration upscale factor (default: 2)"
    )


def add_audio_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add audio processing arguments to parser.

    Arguments added:
        --audio-enhance: Audio enhancement mode
        --audio-upmix: Surround upmixing mode
        --audio-layout: Output channel layout
        --audio-format: Output audio codec
        --audio-bitrate: Audio bitrate
        --no-audio-normalize: Disable loudness normalization
        --audio-target-loudness: Target LUFS for normalization
        --audio-noise-floor: Noise floor threshold for enhancement

    Args:
        parser: ArgumentParser instance to add arguments to
    """
    audio_group = parser.add_argument_group(
        'Audio Options',
        'Audio enhancement, upmixing, and output configuration'
    )

    audio_group.add_argument(
        "--audio-enhance",
        default="none",
        choices=["none", "light", "moderate", "aggressive", "voice", "music"],
        help="Audio enhancement mode: none (passthrough), light (subtle cleanup), "
             "moderate (balanced), aggressive (heavy processing), voice (speech optimize), "
             "music (music optimize) (default: none)"
    )

    audio_group.add_argument(
        "--audio-upmix",
        default="none",
        choices=["none", "simple", "surround", "prologic", "demucs"],
        help="Surround upmixing: none, simple (basic stereo spread), "
             "surround (FFmpeg surround), prologic (Dolby Pro Logic), "
             "demucs (AI stem separation) (default: none)"
    )

    audio_group.add_argument(
        "--audio-layout",
        default="original",
        choices=["original", "stereo", "5.1", "7.1", "mono"],
        help="Output channel layout (default: original)"
    )

    audio_group.add_argument(
        "--audio-format",
        default="aac",
        choices=["aac", "ac3", "eac3", "dts", "flac"],
        help="Output audio codec: aac (best compatibility), ac3/eac3 (surround), "
             "dts (high quality), flac (lossless) (default: aac)"
    )

    audio_group.add_argument(
        "--audio-bitrate",
        default="192k",
        help="Audio bitrate (default: 192k, use 640k for 5.1/7.1)"
    )

    audio_group.add_argument(
        "--no-audio-normalize",
        action="store_true",
        help="Disable audio loudness normalization (keeps original levels)"
    )

    audio_group.add_argument(
        "--audio-target-loudness",
        type=float,
        default=-14.0,
        help="Target loudness in LUFS for normalization (default: -14.0, range: -24 to -9)"
    )

    audio_group.add_argument(
        "--audio-noise-floor",
        type=float,
        default=-20.0,
        help="Noise floor threshold in dB for enhancement (default: -20.0, range: -30 to -10)"
    )


def add_advanced_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add advanced/expert arguments to parser.

    Arguments added:
        --engine: Upscaling engine selection
        --realesrgan-model: Real-ESRGAN model selection
        --realesrgan-denoise: Denoise strength for Real-ESRGAN
        --ffmpeg-scale-algo: FFmpeg scaling algorithm
        --hdr: HDR output mode
        --hdr-brightness: Peak brightness for HDR
        --color-depth: Color bit depth (8 or 10)
        --gpu-id: GPU device ID for multi-GPU systems
        --demucs-model: Demucs model for AI upmixing
        --demucs-shifts: Demucs processing shifts
        --lfe-crossover: LFE crossover frequency
        --center-mix: Center channel mix level
        --surround-delay: Surround channel delay

    Args:
        parser: ArgumentParser instance to add arguments to
    """
    advanced_group = parser.add_argument_group(
        'Advanced Options',
        'Expert settings for fine-tuning (use with caution)'
    )

    # Engine selection
    advanced_group.add_argument(
        "--engine",
        default="auto",
        choices=["auto", "rtxvideo", "realesrgan", "ffmpeg", "maxine"],
        help="Upscaling engine: auto (detect best available), "
             "rtxvideo (NVIDIA RTX Video SDK, best quality), "
             "realesrgan (AMD/Intel/NVIDIA), ffmpeg (CPU fallback), "
             "maxine (deprecated) (default: auto)"
    )

    advanced_group.add_argument(
        "--skip-maxine",
        action="store_true",
        help="Force skip NVIDIA Maxine even if available (deprecated, use --engine)"
    )

    # RTX Video SDK options
    advanced_group.add_argument(
        "--rtxvideo-artifact-reduction",
        action="store_true",
        default=True,
        help="Enable RTX Video SDK artifact reduction (removes VHS noise, compression artifacts)"
    )

    advanced_group.add_argument(
        "--rtxvideo-no-artifact-reduction",
        dest="rtxvideo_artifact_reduction",
        action="store_false",
        help="Disable RTX Video SDK artifact reduction"
    )

    advanced_group.add_argument(
        "--rtxvideo-artifact-strength",
        type=float,
        default=0.5,
        help="RTX Video SDK artifact reduction strength (default: 0.5, range: 0.0-1.0)"
    )

    advanced_group.add_argument(
        "--rtxvideo-hdr",
        action="store_true",
        help="Enable SDR to HDR10 conversion via RTX Video SDK"
    )

    advanced_group.add_argument(
        "--rtxvideo-sdk-path",
        type=str,
        default="",
        help="Custom path to RTX Video SDK installation (auto-detected if not specified)"
    )

    # Real-ESRGAN options
    advanced_group.add_argument(
        "--realesrgan-model",
        default="realesrgan-x4plus",
        choices=["realesrgan-x4plus", "realesrgan-x4plus-anime",
                 "realesr-animevideov3", "realesrnet-x4plus"],
        help="Real-ESRGAN model: x4plus (general), x4plus-anime (animation), "
             "animevideov3 (anime video), realesrnet-x4plus (sharp) (default: realesrgan-x4plus)"
    )

    advanced_group.add_argument(
        "--realesrgan-denoise",
        type=float,
        default=0.5,
        help="Real-ESRGAN denoise strength (default: 0.5, range: 0.0-1.0)"
    )

    # FFmpeg scaling
    advanced_group.add_argument(
        "--ffmpeg-scale-algo",
        default="lanczos",
        choices=["lanczos", "bicubic", "bilinear", "spline", "neighbor"],
        help="FFmpeg scaling algorithm (default: lanczos)"
    )

    # HDR options
    advanced_group.add_argument(
        "--hdr",
        default="sdr",
        choices=["sdr", "hdr10", "hlg"],
        help="HDR output mode: sdr (standard), hdr10 (HDR10), hlg (HLG broadcast) (default: sdr)"
    )

    advanced_group.add_argument(
        "--hdr-brightness",
        type=int,
        default=400,
        help="Peak brightness in nits for HDR output (default: 400, range: 100-10000)"
    )

    advanced_group.add_argument(
        "--color-depth",
        type=int,
        default=10,
        choices=[8, 10],
        help="Output color bit depth (default: 10)"
    )

    # GPU options
    advanced_group.add_argument(
        "--gpu-id",
        type=int,
        default=0,
        help="GPU device ID for multi-GPU systems (default: 0)"
    )

    # Demucs advanced options
    advanced_group.add_argument(
        "--demucs-model",
        default="htdemucs",
        choices=["htdemucs", "htdemucs_ft", "mdx_extra", "mdx_extra_q"],
        help="Demucs model for AI audio separation (default: htdemucs)"
    )

    advanced_group.add_argument(
        "--demucs-device",
        default="auto",
        choices=["auto", "cuda", "cpu"],
        help="Demucs processing device (default: auto)"
    )

    advanced_group.add_argument(
        "--demucs-shifts",
        type=int,
        default=1,
        help="Demucs processing shifts: higher=better quality, slower (default: 1, range: 0-5)"
    )

    # Surround advanced options
    advanced_group.add_argument(
        "--lfe-crossover",
        type=int,
        default=120,
        help="LFE (subwoofer) crossover frequency in Hz (default: 120, range: 60-200)"
    )

    advanced_group.add_argument(
        "--center-mix",
        type=float,
        default=0.707,
        help="Center channel mix level (default: 0.707 = -3dB, range: 0.0-1.0)"
    )

    advanced_group.add_argument(
        "--surround-delay",
        type=int,
        default=15,
        help="Surround channel delay in ms (default: 15, range: 0-50)"
    )


def add_analysis_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add video analysis arguments to parser.

    Arguments added:
        --auto-detect: Auto-detect optimal settings from video analysis
        --analysis-config: Load pre-analyzed configuration JSON
        --save-analysis: Export analysis results to JSON
        --force-backend: Force specific analyzer backend

    Args:
        parser: ArgumentParser instance to add arguments to
    """
    analysis_group = parser.add_argument_group(
        'Analysis Options',
        'Intelligent video analysis and auto-configuration'
    )

    analysis_group.add_argument(
        "--auto-detect",
        action="store_true",
        help="Auto-detect optimal settings based on video analysis (analyzes source, "
             "then applies recommended preset and resolution)"
    )

    analysis_group.add_argument(
        "--analysis-config",
        type=Path,
        help="Load pre-analyzed configuration from JSON file (skip analysis step)"
    )

    analysis_group.add_argument(
        "--save-analysis",
        type=Path,
        help="Export analysis results to JSON file for reuse"
    )

    analysis_group.add_argument(
        "--force-backend",
        choices=["python", "bash", "basic"],
        help="Force specific analyzer backend: python (OpenCV), bash (ffmpeg+awk), "
             "basic (ffprobe only)"
    )


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add common arguments used by most subcommands.

    Arguments added:
        --config: Configuration file path
        --keep-temp: Keep temporary files
        -v, --verbose: Enable verbose output

    Args:
        parser: ArgumentParser instance to add arguments to
    """
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Configuration file path (YAML format) (default: config.yaml)"
    )

    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary files after processing (for debugging)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output with detailed logging"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show processing pipeline without executing (validation and preview mode)"
    )


def add_output_argument(parser: argparse.ArgumentParser, required: bool = True) -> None:
    """
    Add output file/folder argument to parser.

    Args:
        parser: ArgumentParser instance to add arguments to
        required: Whether output argument is required (default: True)
    """
    parser.add_argument(
        "-o", "--output",
        required=required,
        type=Path,
        help="Output video file or folder path"
    )
