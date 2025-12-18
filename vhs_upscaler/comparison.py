"""
Preset comparison tool for VHS upscaler.

Generates side-by-side comparison grids to evaluate different presets
on the same source material. Useful for:
- Testing preset quality
- Choosing optimal settings
- Demonstrating processing improvements
- Quality assurance

Architecture:
    1. Extract N clips from source video at evenly spaced intervals
    2. Process each clip with M different presets
    3. Create comparison grids:
       - Individual: Each clip × all presets (horizontal stack)
       - Full: All clips × all presets (grid layout)
    4. Add text labels for identification
"""

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ComparisonConfig:
    """Configuration for preset comparison generation."""
    input_path: Path
    output_dir: Path
    presets: List[str]
    clip_count: int = 3
    clip_duration: int = 10
    timestamps: Optional[List[int]] = None  # Custom timestamps (overrides clip_count)
    include_original: bool = True
    label_position: str = "top"  # top, bottom, overlay
    label_font_size: int = 24
    label_bg_color: str = "black@0.7"
    label_text_color: str = "white"
    ffmpeg_path: str = "ffmpeg"
    keep_individual_clips: bool = True


class PresetComparator:
    """
    Generate side-by-side preset comparison grids.

    Example usage:
        config = ComparisonConfig(
            input_path=Path("video.mp4"),
            output_dir=Path("./comparisons"),
            presets=["vhs_standard", "vhs_clean", "vhs_heavy"],
            clip_count=3
        )

        comparator = PresetComparator(config)
        comparator.generate_comparison_suite()
    """

    def __init__(self, config: ComparisonConfig):
        """
        Initialize preset comparator.

        Args:
            config: Comparison configuration
        """
        self.config = config
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # Subdirectories for organization
        self.clips_dir = self.config.output_dir / "clips"
        self.comparisons_dir = self.config.output_dir / "comparisons"
        self.clips_dir.mkdir(exist_ok=True)
        self.comparisons_dir.mkdir(exist_ok=True)

    def generate_comparison_suite(self) -> Dict[str, Path]:
        """
        Generate complete comparison suite.

        Returns:
            Dict mapping comparison type to output path:
            {
                "clip_0": Path("comparisons/comparison_clip0.mp4"),
                "clip_1": Path("comparisons/comparison_clip1.mp4"),
                "full_grid": Path("comparisons/comparison_full.mp4")
            }
        """
        logger.info("Starting preset comparison suite generation")
        logger.info(f"Input: {self.config.input_path}")
        logger.info(f"Output: {self.config.output_dir}")
        logger.info(f"Presets: {', '.join(self.config.presets)}")

        # Step 1: Extract test clips
        logger.info("Step 1: Extracting test clips...")
        clips = self._extract_test_clips()
        logger.info(f"  Extracted {len(clips)} clips")

        # Step 2: Process clips with each preset
        logger.info("Step 2: Processing clips with each preset...")
        processed_clips = self._process_clips_with_presets(clips)

        # Step 3: Create individual comparisons (per clip)
        logger.info("Step 3: Creating individual comparisons...")
        individual_comparisons = {}
        for clip_idx in range(len(clips)):
            comparison_path = self._create_clip_comparison(
                clip_idx,
                processed_clips[clip_idx]
            )
            individual_comparisons[f"clip_{clip_idx}"] = comparison_path
            logger.info(f"  Created comparison for clip {clip_idx}")

        # Step 4: Create full grid comparison
        logger.info("Step 4: Creating full grid comparison...")
        full_grid_path = self._create_full_grid(processed_clips)
        individual_comparisons["full_grid"] = full_grid_path

        logger.info("Comparison suite generation complete!")
        logger.info(f"  Output directory: {self.config.output_dir}")

        return individual_comparisons

    def _extract_test_clips(self) -> List[Path]:
        """
        Extract test clips from source video.

        Returns:
            List of paths to extracted clips
        """
        # Get video duration
        duration = self._get_video_duration(self.config.input_path)

        # Calculate timestamps
        if self.config.timestamps:
            timestamps = self.config.timestamps
        else:
            # Evenly spaced throughout video
            interval = duration / (self.config.clip_count + 1)
            timestamps = [interval * (i + 1) for i in range(self.config.clip_count)]

        clips = []
        for i, timestamp in enumerate(timestamps):
            clip_path = self.clips_dir / f"clip_{i}_original.mp4"

            # Extract clip with FFmpeg
            cmd = [
                self.config.ffmpeg_path,
                "-ss", str(timestamp),
                "-i", str(self.config.input_path),
                "-t", str(self.config.clip_duration),
                "-c", "copy",  # Stream copy for speed
                "-y",
                str(clip_path)
            ]

            subprocess.run(cmd, capture_output=True, check=True)
            clips.append(clip_path)

        return clips

    def _process_clips_with_presets(self, clips: List[Path]) -> Dict[int, Dict[str, Path]]:
        """
        Process each clip with each preset.

        Args:
            clips: List of extracted clip paths

        Returns:
            Dict mapping clip index to dict of preset→processed_path:
            {
                0: {"original": Path(...), "vhs": Path(...), "clean": Path(...)},
                1: {"original": Path(...), "vhs": Path(...), "clean": Path(...)},
            }
        """
        from .vhs_upscale import VHSUpscaler, ProcessingConfig

        results = {}

        for clip_idx, clip in enumerate(clips):
            results[clip_idx] = {}

            # Include original if requested
            if self.config.include_original:
                results[clip_idx]["original"] = clip

            # Process with each preset
            for preset in self.config.presets:
                logger.info(f"  Processing clip {clip_idx} with preset '{preset}'...")

                output_path = self.clips_dir / f"clip_{clip_idx}_{preset}.mp4"

                # Create config for this preset
                config = ProcessingConfig(
                    preset=preset,
                    keep_temp=False
                )

                # Process clip
                try:
                    upscaler = VHSUpscaler(config)
                    upscaler.process(str(clip), output_path)
                    results[clip_idx][preset] = output_path
                except Exception as e:
                    logger.error(f"Failed to process clip {clip_idx} with preset '{preset}': {e}")
                    # Use original as fallback
                    results[clip_idx][preset] = clip

        return results

    def _create_clip_comparison(self, clip_idx: int, preset_results: Dict[str, Path]) -> Path:
        """
        Create horizontal comparison for a single clip across all presets.

        Args:
            clip_idx: Clip index
            preset_results: Dict mapping preset name to processed clip path

        Returns:
            Path to comparison video
        """
        output_path = self.comparisons_dir / f"comparison_clip{clip_idx}.mp4"

        # Build FFmpeg filter complex for horizontal stack with labels
        inputs = []
        input_labels = []
        filter_parts = []

        for idx, (preset, path) in enumerate(preset_results.items()):
            inputs.extend(["-i", str(path)])
            input_label = f"[{idx}:v]"
            input_labels.append(input_label)

            # Add text label
            label_text = preset.replace("_", " ").title()
            labeled = f"[v{idx}]"

            filter_parts.append(
                f"{input_label}drawtext="
                f"text='{label_text}':"
                f"fontsize={self.config.label_font_size}:"
                f"fontcolor={self.config.label_text_color}:"
                f"box=1:boxcolor={self.config.label_bg_color}:"
                f"boxborderw=5:"
                f"x=(w-text_w)/2:y=10"
                f"{labeled}"
            )

        # Horizontal stack
        stack_inputs = "".join(input_labels)
        stack_filter = f"{stack_inputs}hstack=inputs={len(preset_results)}[v]"
        filter_parts.append(stack_filter)

        filter_complex = ";".join(filter_parts)

        # Build command
        cmd = [
            self.config.ffmpeg_path,
            *inputs,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "fast",
            "-y",
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True, check=True)
        return output_path

    def _create_full_grid(self, all_results: Dict[int, Dict[str, Path]]) -> Path:
        """
        Create full grid comparison (all clips × all presets).

        Layout:
                    Original    Preset1     Preset2     Preset3
        Clip0       [frame]     [frame]     [frame]     [frame]
        Clip1       [frame]     [frame]     [frame]     [frame]
        Clip2       [frame]     [frame]     [frame]     [frame]

        Args:
            all_results: Dict of all processed clips

        Returns:
            Path to full grid comparison video
        """
        output_path = self.comparisons_dir / "comparison_full.mp4"

        # First, create horizontal stacks for each clip (rows)
        rows = []
        for clip_idx in sorted(all_results.keys()):
            row_path = tempfile.mktemp(suffix=".mp4")
            self._create_horizontal_stack(all_results[clip_idx], Path(row_path))
            rows.append(row_path)

        # Then, stack rows vertically
        inputs = []
        for row in rows:
            inputs.extend(["-i", row])

        # Vertical stack filter
        input_labels = "".join([f"[{i}:v]" for i in range(len(rows))])
        vstack_filter = f"{input_labels}vstack=inputs={len(rows)}[v]"

        cmd = [
            self.config.ffmpeg_path,
            *inputs,
            "-filter_complex", vstack_filter,
            "-map", "[v]",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "fast",
            "-y",
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True, check=True)

        # Clean up temp row files
        for row in rows:
            Path(row).unlink(missing_ok=True)

        return output_path

    def _create_horizontal_stack(self, preset_results: Dict[str, Path], output_path: Path):
        """
        Create horizontal stack of videos without labels (for grid rows).

        Args:
            preset_results: Dict mapping preset name to video path
            output_path: Where to save the stacked video
        """
        inputs = []
        for path in preset_results.values():
            inputs.extend(["-i", str(path)])

        # Horizontal stack filter
        input_labels = "".join([f"[{i}:v]" for i in range(len(preset_results))])
        hstack_filter = f"{input_labels}hstack=inputs={len(preset_results)}[v]"

        cmd = [
            self.config.ffmpeg_path,
            *inputs,
            "-filter_complex", hstack_filter,
            "-map", "[v]",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "fast",
            "-y",
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True, check=True)

    def _get_video_duration(self, video_path: Path) -> float:
        """
        Get video duration in seconds using ffprobe.

        Args:
            video_path: Path to video file

        Returns:
            Duration in seconds
        """
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            str(video_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])

    def generate_comparison_report(self, comparisons: Dict[str, Path]) -> str:
        """
        Generate text report summarizing comparison results.

        Args:
            comparisons: Dict of generated comparison paths

        Returns:
            Report text
        """
        report_lines = [
            "=" * 70,
            "Preset Comparison Report",
            "=" * 70,
            "",
            f"Input Video: {self.config.input_path.name}",
            f"Output Directory: {self.config.output_dir}",
            "",
            "Presets Tested:",
        ]

        for preset in self.config.presets:
            report_lines.append(f"  - {preset}")

        report_lines.extend([
            "",
            f"Clips Extracted: {self.config.clip_count}",
            f"Clip Duration: {self.config.clip_duration} seconds",
            "",
            "Generated Files:",
        ])

        for name, path in comparisons.items():
            if path.exists():
                size_mb = path.stat().st_size / (1024 * 1024)
                report_lines.append(f"  - {name}: {path.name} ({size_mb:.1f} MB)")

        report_lines.extend([
            "",
            "=" * 70,
            "How to Use:",
            "  1. Open individual clip comparisons to see detailed preset differences",
            "  2. Open full grid to see all clips and presets at once",
            "  3. Choose the preset that best matches your quality requirements",
            "=" * 70,
        ])

        return "\n".join(report_lines)


def generate_preset_comparison(
    input_path: Path,
    output_dir: Path,
    presets: List[str],
    clip_count: int = 3,
    clip_duration: int = 10,
    timestamps: Optional[List[int]] = None
) -> Dict[str, Path]:
    """
    Convenience function to generate preset comparison suite.

    Args:
        input_path: Source video file
        output_dir: Output directory for comparisons
        presets: List of preset names to compare
        clip_count: Number of clips to extract (default: 3)
        clip_duration: Duration of each clip in seconds (default: 10)
        timestamps: Optional custom timestamps (overrides clip_count)

    Returns:
        Dict mapping comparison type to output path

    Example:
        comparisons = generate_preset_comparison(
            input_path=Path("old_vhs.mp4"),
            output_dir=Path("./test_output"),
            presets=["vhs_standard", "vhs_clean", "vhs_heavy"],
            clip_count=3,
            clip_duration=10
        )
    """
    config = ComparisonConfig(
        input_path=input_path,
        output_dir=output_dir,
        presets=presets,
        clip_count=clip_count,
        clip_duration=clip_duration,
        timestamps=timestamps
    )

    comparator = PresetComparator(config)
    comparisons = comparator.generate_comparison_suite()

    # Generate and save report
    report = comparator.generate_comparison_report(comparisons)
    report_path = output_dir / "comparison_report.txt"
    report_path.write_text(report)

    print(report)

    return comparisons
