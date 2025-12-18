"""
CLI module for VHS Upscaler.

This module provides a modern subcommand-based CLI architecture for the
VHS upscaler application. Each subcommand is self-contained with its own
argument parsing and execution logic.

Available subcommands:
    upscale       - Upscale a single video file
    analyze       - Analyze video characteristics
    preview       - Generate before/after comparison preview
    batch         - Process multiple videos sequentially
    test-presets  - Test multiple presets on a clip

Usage:
    vhs-upscale <subcommand> [options]
    vhs-upscale upscale input.mp4 -o output.mp4
    vhs-upscale analyze input.mp4
    vhs-upscale preview input.mp4 -o preview.mp4
    vhs-upscale batch input_folder/ output_folder/
    vhs-upscale test-presets input.mp4 -o test_results/
"""

from .upscale import setup_upscale_parser, handle_upscale
from .analyze import setup_analyze_parser, handle_analyze
from .preview import setup_preview_parser, handle_preview
from .batch import setup_batch_parser, handle_batch
from .test_presets import setup_test_presets_parser, handle_test_presets

# Export common argument builders for potential reuse
from .common import (
    add_upscale_arguments,
    add_processing_arguments,
    add_audio_arguments,
    add_advanced_arguments,
    add_analysis_arguments,
    add_common_arguments,
    add_output_argument,
)

__all__ = [
    # Subcommand setup functions
    'setup_upscale_parser',
    'setup_analyze_parser',
    'setup_preview_parser',
    'setup_batch_parser',
    'setup_test_presets_parser',
    # Subcommand handlers
    'handle_upscale',
    'handle_analyze',
    'handle_preview',
    'handle_batch',
    'handle_test_presets',
    # Common argument builders
    'add_upscale_arguments',
    'add_processing_arguments',
    'add_audio_arguments',
    'add_advanced_arguments',
    'add_analysis_arguments',
    'add_common_arguments',
    'add_output_argument',
]

__version__ = '2.0.0'  # CLI refactor version
