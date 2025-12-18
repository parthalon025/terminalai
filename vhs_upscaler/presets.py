"""
Preset library for intelligent video processing settings.

Maps VideoAnalysis results to optimal processing configurations based on
detected video characteristics (scan type, noise level, source format, content type).

Presets follow VHS restoration best practices:
  1. Deinterlace FIRST (if needed)
  2. Denoise BEFORE upscaling (light touch)
  3. Color correct (optional)
  4. Upscale ONCE
  5. Sharpen AFTER upscaling
  6. Encode
"""

from typing import Any, Dict

from .analysis.models import ContentType, NoiseLevel, SourceFormat, VideoAnalysis

# Preset definitions based on source characteristics
PRESETS = {
    "vhs_standard": {
        "description": "Standard VHS (medium noise, typical artifacts)",
        "deinterlace": "yadif=1",
        "deinterlace_algorithm": "bwdif",  # FFmpeg filter with good motion compensation
        "qtgmc_preset": None,  # Not using QTGMC for standard quality
        "denoise": "hqdn3d=4:3:6:4.5",
        "sharpen": "cas=0.4",
        "color_correct": "eq=saturation=1.1",
        "lut_file": "luts/vhs_restore.cube",  # VHS color restoration LUT
        "lut_strength": 0.7,  # Balanced restoration
        "upscale_model": "realesrgan-x4plus",
        "upscale_factor": 2,
        "target_resolution": 1080,
        "encoder": "libx264",
        "crf": 18,
    },
    "vhs_clean": {
        "description": "Clean VHS (low noise, good quality)",
        "deinterlace": "yadif=1",
        "deinterlace_algorithm": "qtgmc",  # Best quality for clean VHS
        "qtgmc_preset": "medium",  # Balanced quality/speed
        "denoise": "hqdn3d=2:1:2:3",
        "sharpen": "cas=0.3",
        "color_correct": "eq=saturation=1.05",
        "lut_file": "luts/vhs_restore.cube",  # VHS color restoration LUT
        "lut_strength": 0.5,  # Lighter touch for clean sources
        "upscale_model": "realesrgan-x4plus",
        "upscale_factor": 2,
        "target_resolution": 1080,
        "encoder": "libx264",
        "crf": 18,
    },
    "vhs_heavy": {
        "description": "Degraded VHS (severe noise, heavy artifacts)",
        "deinterlace": "yadif=1",
        "deinterlace_algorithm": "qtgmc",  # Best quality for restoration
        "qtgmc_preset": "slow",  # Higher quality for degraded sources
        "denoise": "hqdn3d=8:6:12:9",
        "sharpen": "cas=0.5",
        "color_correct": "eq=saturation=1.15:brightness=0.02",
        "crop_bottom": 8,  # Remove head switching noise
        "lut_file": "luts/vhs_restore.cube",  # VHS color restoration LUT
        "lut_strength": 0.9,  # Stronger correction for degraded tapes
        "upscale_model": "realesrgan-x4plus",
        "upscale_factor": 2,
        "target_resolution": 1080,
        "encoder": "libx264",
        "crf": 18,
    },
    "dvd_interlaced": {
        "description": "Interlaced DVD (clean source, needs deinterlacing)",
        "deinterlace": "yadif=1",
        "deinterlace_algorithm": "bwdif",  # Good balance for DVD sources
        "qtgmc_preset": None,  # QTGMC overkill for DVD
        "denoise": "hqdn3d=2:1:2:3",
        "sharpen": "cas=0.3",
        "color_correct": None,
        "upscale_model": "realesrgan-x4plus",
        "upscale_factor": 2,
        "target_resolution": 1080,
        "encoder": "libx264",
        "crf": 18,
    },
    "dvd_progressive": {
        "description": "Progressive DVD (clean, no deinterlacing needed)",
        "deinterlace": None,
        "deinterlace_algorithm": None,  # No deinterlacing needed
        "qtgmc_preset": None,
        "denoise": "hqdn3d=1:1:2:2",
        "sharpen": "cas=0.25",
        "color_correct": None,
        "upscale_model": "realesrgan-x4plus",
        "upscale_factor": 2,
        "target_resolution": 1080,
        "encoder": "libx264",
        "crf": 18,
    },
    "youtube_old": {
        "description": "Old YouTube rips (compression artifacts, blocking)",
        "deinterlace": None,
        "deinterlace_algorithm": None,  # Usually progressive
        "qtgmc_preset": None,
        "deblock": "deblock=filter=weak",
        "denoise": "hqdn3d=3:2:4:3",
        "sharpen": "cas=0.4",
        "color_correct": None,
        "upscale_model": "realesrgan-x4plus",
        "upscale_factor": 2,
        "target_resolution": 1080,
        "encoder": "libx264",
        "crf": 18,
    },
    "animation": {
        "description": "Animation/cartoon content",
        "deinterlace": None,
        "deinterlace_algorithm": None,  # Usually progressive
        "qtgmc_preset": None,
        "denoise": "hqdn3d=1:1:2:2",
        "sharpen": "cas=0.2",
        "color_correct": None,
        "upscale_model": "realesrgan-x4plus-anime",
        "upscale_factor": 2,
        "target_resolution": 1080,
        "encoder": "libx264",
        "crf": 18,
    },
    "clean": {
        "description": "Clean digital source (minimal processing)",
        "deinterlace": None,
        "deinterlace_algorithm": None,  # No deinterlacing needed
        "qtgmc_preset": None,
        "denoise": None,
        "sharpen": "cas=0.15",
        "color_correct": None,
        "upscale_model": "realesrgan-x4plus",
        "upscale_factor": 2,
        "target_resolution": 1080,
        "encoder": "libx264",
        "crf": 18,
    },
    "broadcast_1080i": {
        "description": "HD broadcast (1080i interlaced)",
        "deinterlace": "yadif=1",
        "deinterlace_algorithm": "bwdif",  # Good for broadcast content
        "qtgmc_preset": None,  # QTGMC not needed for HD broadcast
        "denoise": "hqdn3d=1:1:2:2",
        "sharpen": "cas=0.2",
        "color_correct": None,
        "upscale_model": None,  # Already HD, no upscaling
        "upscale_factor": 1,
        "target_resolution": 1080,
        "encoder": "libx264",
        "crf": 18,
    },
}


def get_preset_from_analysis(analysis: VideoAnalysis) -> str:
    """
    Select optimal preset based on video analysis results.

    This function implements intelligent preset selection logic based on
    detected video characteristics. Priority order:
      1. Content type (animation gets special treatment)
      2. Source format (VHS, DVD, digital, broadcast)
      3. Noise level (affects VHS preset variant)
      4. Scan type (interlaced vs progressive)
      5. Quality score (affects VHS clean vs standard)

    Args:
        analysis: VideoAnalysis results from analyzer

    Returns:
        Preset name (key from PRESETS dict)
    """
    # Animation content gets anime preset regardless of source
    if analysis.content_type == ContentType.ANIMATION:
        return "animation"

    # VHS source detection
    if analysis.source_format == SourceFormat.VHS:
        # Severe noise = heavy processing
        if analysis.noise_level == NoiseLevel.SEVERE:
            return "vhs_heavy"
        # High quality VHS (rare but exists) = light processing
        elif analysis.estimated_quality_score > 60:
            return "vhs_clean"
        # Standard VHS = balanced processing
        else:
            return "vhs_standard"

    # DVD source
    elif analysis.source_format == SourceFormat.DVD:
        # Check if interlaced
        if analysis.scan_type.value.startswith("interlaced"):
            return "dvd_interlaced"
        else:
            return "dvd_progressive"

    # Broadcast HD (1080i)
    elif analysis.source_format == SourceFormat.BROADCAST:
        if analysis.width == 1920 and analysis.height == 1080:
            return "broadcast_1080i"
        # Fallback for other broadcast formats
        elif analysis.scan_type.value.startswith("interlaced"):
            return "dvd_interlaced"
        else:
            return "clean"

    # Low bitrate (likely old YouTube/web rips)
    # Use getattr() with default to handle backends that don't populate bitrate_kbps
    elif getattr(analysis, 'bitrate_kbps', None) and analysis.bitrate_kbps < 2000:
        return "youtube_old"

    # High resolution digital (already good quality)
    elif analysis.width >= 1920:
        return "clean"

    # Default fallback
    else:
        return "clean"


def get_preset_details(preset_name: str) -> Dict[str, Any]:
    """
    Get preset configuration by name.

    Args:
        preset_name: Name of preset from PRESETS dict

    Returns:
        Preset configuration dict

    Raises:
        KeyError: If preset_name doesn't exist
    """
    if preset_name not in PRESETS:
        raise KeyError(f"Unknown preset: {preset_name}. Available: {list(PRESETS.keys())}")

    return PRESETS[preset_name].copy()


def apply_preset_to_args(args, preset_name: str):
    """
    Apply preset settings to argument namespace.

    This modifies args in-place with preset values, while preserving
    any user-specified overrides.

    Args:
        args: argparse.Namespace with CLI arguments
        preset_name: Name of preset to apply

    Returns:
        Modified args namespace
    """
    preset = get_preset_details(preset_name)

    # Map preset to existing CLI args
    # Only set if not already specified by user

    if not hasattr(args, 'preset_applied') or args.preset_applied is None:
        args.preset = preset_name

    # These are typically not directly exposed as CLI args,
    # but stored for the processing pipeline
    if not hasattr(args, 'processing_settings'):
        args.processing_settings = {}

    # Apply all preset settings
    for key, value in preset.items():
        if key != 'description' and value is not None:
            args.processing_settings[key] = value

    return args


def list_all_presets() -> Dict[str, str]:
    """
    Get all available presets with descriptions.

    Returns:
        Dict mapping preset name to description
    """
    return {
        name: config.get("description", "No description")
        for name, config in PRESETS.items()
    }


def get_recommended_settings_from_analysis(analysis: VideoAnalysis) -> Dict[str, Any]:
    """
    Generate recommended processing settings from analysis.

    This is a more detailed version of get_preset_from_analysis that
    returns specific settings rather than just a preset name.

    Args:
        analysis: VideoAnalysis results

    Returns:
        Dict with recommended processing settings
    """
    # Get base preset
    preset_name = get_preset_from_analysis(analysis)
    settings = get_preset_details(preset_name).copy()

    # Add preset name
    settings["preset"] = preset_name

    # Customize based on specific artifacts detected

    # VHS head switching noise → crop bottom
    if analysis.has_head_switching_noise:
        settings["crop_bottom"] = 8

    # High color bleeding → add color correction
    if analysis.has_color_bleeding and analysis.source_format == SourceFormat.VHS:
        if settings.get("color_correct"):
            # Enhance existing color correction
            settings["color_correct"] += ",colorbalance=rs=0.1:gs=0:bs=-0.1"
        else:
            settings["color_correct"] = "colorbalance=rs=0.1:gs=0:bs=-0.1"

    # Adjust denoise based on precise noise level
    if analysis.noise_level == NoiseLevel.SEVERE and "denoise" in settings:
        # Increase denoise strength for severe cases
        settings["denoise"] = "hqdn3d=10:8:15:12"
    elif analysis.noise_level == NoiseLevel.LOW and "denoise" in settings:
        # Reduce denoise for clean sources
        settings["denoise"] = "hqdn3d=1:1:2:2"

    # Adjust upscale factor based on source resolution
    if analysis.width >= 1280:
        # Already 720p+, don't upscale as much
        settings["upscale_factor"] = 1
        settings["target_resolution"] = analysis.height

    # Face restoration for talking head content
    if analysis.content_type == ContentType.TALKING_HEAD:
        settings["face_restore"] = True
        settings["face_restore_strength"] = 0.6
        settings["face_restore_upscale"] = 2

    return settings


def explain_preset(preset_name: str) -> str:
    """
    Get human-readable explanation of what a preset does.

    Args:
        preset_name: Name of preset

    Returns:
        Multi-line explanation string
    """
    if preset_name not in PRESETS:
        return f"Unknown preset: {preset_name}"

    preset = PRESETS[preset_name]
    lines = [
        f"=== Preset: {preset_name} ===",
        f"Description: {preset.get('description', 'No description')}",
        "",
        "Processing Steps:",
    ]

    step_num = 1

    # Deinterlacing
    if preset.get("deinterlace"):
        lines.append(f"  {step_num}. Deinterlace: {preset['deinterlace']}")
        step_num += 1

    # Deblocking (YouTube)
    if preset.get("deblock"):
        lines.append(f"  {step_num}. Deblock: {preset['deblock']}")
        step_num += 1

    # Denoising
    if preset.get("denoise"):
        lines.append(f"  {step_num}. Denoise: {preset['denoise']}")
        step_num += 1

    # Color correction
    if preset.get("color_correct"):
        lines.append(f"  {step_num}. Color Correct: {preset['color_correct']}")
        step_num += 1

    # Cropping
    if preset.get("crop_bottom"):
        lines.append(f"  {step_num}. Crop Bottom: {preset['crop_bottom']}px (remove head switching noise)")
        step_num += 1

    # Upscaling
    if preset.get("upscale_model"):
        lines.append(f"  {step_num}. Upscale: {preset['upscale_model']} (x{preset.get('upscale_factor', 2)})")
        step_num += 1

    # Sharpening
    if preset.get("sharpen"):
        lines.append(f"  {step_num}. Sharpen: {preset['sharpen']}")
        step_num += 1

    # Encoding
    encoder = preset.get("encoder", "libx264")
    crf = preset.get("crf", 18)
    lines.append(f"  {step_num}. Encode: {encoder} (CRF {crf})")

    lines.append("")
    lines.append(f"Target Resolution: {preset.get('target_resolution', 1080)}p")

    return "\n".join(lines)
