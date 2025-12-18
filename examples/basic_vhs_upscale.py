#!/usr/bin/env python3
"""
Basic VHS Upscaling Example

This example demonstrates the simplest way to upscale a VHS video
using TerminalAI with automatic settings detection.
"""

from pathlib import Path
from vhs_upscaler.vhs_upscale import VideoUpscaler, UpscaleConfig


def main():
    """Upscale a VHS video with automatic engine detection."""

    # Define input and output
    input_video = "old_vhs_tape.mp4"
    output_video = "restored_1080p.mp4"

    # Check if input exists
    if not Path(input_video).exists():
        print(f"Error: Input file '{input_video}' not found")
        print("Please update the input_video path to point to your video file")
        return

    # Create configuration
    config = UpscaleConfig(
        input_file=input_video,
        output_file=output_video,
        preset="vhs",                    # Optimized for VHS content
        target_resolution="1080p",       # Upscale to Full HD
        engine="auto",                   # Auto-detect best engine (Maxine/Real-ESRGAN/FFmpeg)
        encoder="auto",                  # Auto-detect best encoder (NVENC if available)
        quality_mode="balanced",         # Balance speed vs quality
    )

    # Create upscaler and process
    print(f"Processing: {input_video}")
    print(f"Output: {output_video}")
    print(f"Preset: {config.preset}")
    print(f"Target: {config.target_resolution}")
    print("-" * 60)

    upscaler = VideoUpscaler(config)
    success = upscaler.process()

    if success:
        print(f"\nSuccess! Output saved to: {output_video}")
    else:
        print("\nProcessing failed. Check logs for details.")


if __name__ == "__main__":
    main()
