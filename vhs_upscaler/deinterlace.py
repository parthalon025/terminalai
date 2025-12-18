"""
Deinterlacing abstraction layer with support for multiple engines.

This module provides a unified interface for deinterlacing video using different
engines: FFmpeg built-in filters (yadif, bwdif, w3fdif) and VapourSynth QTGMC.

QTGMC (via VapourSynth) provides best-in-class deinterlacing quality for VHS
restoration, but requires VapourSynth installation. The module gracefully falls
back to FFmpeg filters when VapourSynth is unavailable.

Usage:
    from deinterlace import DeinterlaceProcessor, DeinterlaceEngine

    processor = DeinterlaceProcessor(engine=DeinterlaceEngine.QTGMC)
    processor.deinterlace(
        input_path=Path("interlaced.mp4"),
        output_path=Path("progressive.mp4"),
        preset="medium",
        tff=True
    )
"""

import logging
import subprocess
import tempfile
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple, List, Callable

logger = logging.getLogger(__name__)


class DeinterlaceEngine(Enum):
    """Available deinterlacing engines."""
    YADIF = "yadif"      # FFmpeg built-in (fast, good quality) - Bob deinterlacing
    BWDIF = "bwdif"      # FFmpeg built-in (better motion compensation than yadif)
    QTGMC = "qtgmc"      # VapourSynth (best quality, slowest) - Motion-compensated
    W3FDIF = "w3fdif"    # FFmpeg built-in (better detail preservation)


class DeinterlaceProcessor:
    """
    Unified deinterlacing processor supporting multiple engines.

    Automatically detects VapourSynth availability and provides graceful
    fallback to FFmpeg filters when QTGMC is requested but unavailable.

    Attributes:
        engine: Selected deinterlace engine
        has_vapoursynth: Whether VapourSynth is available
        ffmpeg_path: Path to ffmpeg executable
    """

    # QTGMC preset to quality mapping
    QTGMC_PRESETS = {
        "draft": "Fast preview quality (fastest)",
        "medium": "Balanced quality/speed (default)",
        "slow": "High quality (slower)",
        "very_slow": "Highest quality (very slow)",
        "placebo": "Ultra quality (extremely slow)",
    }

    # FFmpeg filter quality comparison
    FILTER_QUALITY_RANKING = [
        "qtgmc",    # Best quality (requires VapourSynth)
        "bwdif",    # Good motion compensation
        "w3fdif",   # Good detail preservation
        "yadif",    # Fast and reliable baseline
    ]

    def __init__(self, engine: DeinterlaceEngine, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize deinterlace processor.

        Args:
            engine: Deinterlacing engine to use
            ffmpeg_path: Path to ffmpeg executable (default: "ffmpeg")
        """
        self.engine = engine
        self.ffmpeg_path = ffmpeg_path
        self.has_vapoursynth = self._check_vapoursynth()
        self.has_vspipe = self._check_vspipe()

        # Validate engine availability
        if self.engine == DeinterlaceEngine.QTGMC:
            if not self.has_vapoursynth:
                logger.warning(
                    "QTGMC requested but VapourSynth not available. "
                    "Falling back to bwdif filter."
                )
                self.engine = DeinterlaceEngine.BWDIF
            elif not self.has_vspipe:
                logger.warning(
                    "QTGMC requested but vspipe not found. "
                    "Falling back to bwdif filter."
                )
                self.engine = DeinterlaceEngine.BWDIF

        logger.info(f"Deinterlace processor initialized with engine: {self.engine.value}")

    def _check_vapoursynth(self) -> bool:
        """
        Check if VapourSynth Python module is available.

        Returns:
            True if VapourSynth is importable, False otherwise
        """
        try:
            import vapoursynth as vs
            version = vs.core.version()
            logger.debug(f"VapourSynth found: {version}")
            return True
        except ImportError:
            logger.debug("VapourSynth not available (ImportError)")
            return False
        except Exception as e:
            logger.debug(f"VapourSynth check failed: {e}")
            return False

    def _check_vspipe(self) -> bool:
        """
        Check if vspipe executable is available.

        Returns:
            True if vspipe is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["vspipe", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.debug(f"vspipe found: {result.stdout.strip()}")
                return True
            return False
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.debug("vspipe not found in PATH")
            return False

    @classmethod
    def list_available_engines(cls, ffmpeg_path: str = "ffmpeg") -> List[str]:
        """
        Get list of available deinterlacing engines on this system.

        Args:
            ffmpeg_path: Path to ffmpeg executable

        Returns:
            List of available engine names (e.g., ["yadif", "bwdif", "qtgmc"])
        """
        available = []

        # Check FFmpeg filters (all should be available if FFmpeg is installed)
        try:
            subprocess.run(
                [ffmpeg_path, "-version"],
                capture_output=True,
                check=True,
                timeout=5
            )
            # Standard FFmpeg filters - always available
            available.extend(["yadif", "bwdif", "w3fdif"])
        except Exception:
            logger.warning("FFmpeg not available - no deinterlacing will be possible")

        # Check VapourSynth
        processor = cls(DeinterlaceEngine.YADIF, ffmpeg_path)
        if processor.has_vapoursynth and processor.has_vspipe:
            available.append("qtgmc")

        return available

    def deinterlace(
        self,
        input_path: Path,
        output_path: Path,
        preset: str = "medium",
        tff: bool = True,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """
        Deinterlace video using selected engine.

        Args:
            input_path: Input video file (interlaced)
            output_path: Output video file (progressive)
            preset: QTGMC preset for quality/speed tradeoff
                   ("draft", "medium", "slow", "very_slow", "placebo")
                   Ignored for FFmpeg filters.
            tff: Top field first (True) or bottom field first (False)
            progress_callback: Optional callback function(percent: float)
                             Called with progress updates (0-100)

        Returns:
            True if deinterlacing succeeded, False otherwise

        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If deinterlacing process fails
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Deinterlacing {input_path.name} using {self.engine.value} "
            f"(TFF={tff}, preset={preset})"
        )

        try:
            if self.engine == DeinterlaceEngine.QTGMC:
                return self._deinterlace_qtgmc(
                    input_path, output_path, preset, tff, progress_callback
                )
            else:
                return self._deinterlace_ffmpeg(
                    input_path, output_path, tff, progress_callback
                )
        except subprocess.CalledProcessError as e:
            logger.error(f"Deinterlacing failed: {e}")
            raise RuntimeError(f"Deinterlacing process failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during deinterlacing: {e}")
            raise

    def _deinterlace_qtgmc(
        self,
        input_path: Path,
        output_path: Path,
        preset: str,
        tff: bool,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """
        Execute QTGMC deinterlacing via VapourSynth.

        This method:
        1. Generates a VapourSynth script with QTGMC settings
        2. Pipes the script output through vspipe to FFmpeg
        3. Encodes the result with high-quality settings

        Args:
            input_path: Input video file
            output_path: Output video file
            preset: QTGMC quality preset
            tff: Top field first flag
            progress_callback: Progress callback function

        Returns:
            True if successful
        """
        # Validate preset
        if preset not in self.QTGMC_PRESETS:
            logger.warning(
                f"Invalid QTGMC preset '{preset}', using 'medium'. "
                f"Valid: {list(self.QTGMC_PRESETS.keys())}"
            )
            preset = "medium"

        # Generate VapourSynth script
        vpy_script_path = self._generate_qtgmc_script(input_path, preset, tff)

        try:
            # Build vspipe + ffmpeg command pipeline
            # vspipe outputs raw YUV4MPEG2 format which FFmpeg can read

            # Start vspipe process
            vspipe_cmd = [
                "vspipe",
                "--y4m",
                str(vpy_script_path),
                "-"
            ]

            # Start ffmpeg process that reads from vspipe stdout
            ffmpeg_cmd = [
                self.ffmpeg_path,
                "-i", "pipe:",
                "-c:v", "libx264",
                "-crf", "18",
                "-preset", "medium",
                "-progress", "pipe:1",
                str(output_path)
            ]

            logger.debug(f"QTGMC vspipe command: {' '.join(vspipe_cmd)}")
            logger.debug(f"QTGMC ffmpeg command: {' '.join(ffmpeg_cmd)}")

            # Execute pipeline without shell - manually pipe between processes
            vspipe_process = subprocess.Popen(
                vspipe_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False  # Binary data for video
            )

            process = subprocess.Popen(
                ffmpeg_cmd,
                stdin=vspipe_process.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Close vspipe stdout in parent to allow SIGPIPE to vspipe if ffmpeg exits
            vspipe_process.stdout.close()

            # Monitor progress if callback provided
            if progress_callback:
                # Get video duration for progress calculation
                duration = self._get_video_duration(input_path)

                for line in process.stdout:
                    if line.startswith("out_time_ms=") and duration > 0:
                        try:
                            ms = int(line.split("=")[1])
                            progress = min(100, (ms / 1000000) / duration * 100)
                            progress_callback(progress)
                        except (ValueError, IndexError):
                            pass

            # Wait for completion of both processes
            stdout, stderr = process.communicate()

            # Also wait for vspipe to complete
            vspipe_process.wait()

            # Check for errors in either process
            if process.returncode != 0:
                logger.error(f"FFmpeg process failed: {stderr}")
                return False

            if vspipe_process.returncode != 0:
                vspipe_stderr = vspipe_process.stderr.read() if vspipe_process.stderr else ""
                logger.error(f"vspipe process failed: {vspipe_stderr}")
                return False

            logger.info(f"QTGMC deinterlacing complete: {output_path}")
            return True

        finally:
            # Clean up temporary script
            if vpy_script_path.exists():
                vpy_script_path.unlink()

    def _deinterlace_ffmpeg(
        self,
        input_path: Path,
        output_path: Path,
        tff: bool,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """
        Execute FFmpeg-based deinterlacing.

        Uses one of the built-in FFmpeg deinterlacing filters:
        - yadif: Yet Another DeInterlacing Filter (fast, good quality)
        - bwdif: Bob Weaver Deinterlacing Filter (better motion handling)
        - w3fdif: Weston 3 Field Deinterlacing Filter (better detail)

        Args:
            input_path: Input video file
            output_path: Output video file
            tff: Top field first flag
            progress_callback: Progress callback function

        Returns:
            True if successful
        """
        filter_str = self._get_ffmpeg_filter(tff)

        cmd = [
            self.ffmpeg_path,
            "-i", str(input_path),
            "-vf", filter_str,
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "medium",
            "-c:a", "copy",  # Copy audio without re-encoding
            "-progress", "pipe:1",
            str(output_path)
        ]

        logger.debug(f"FFmpeg deinterlace command: {' '.join(cmd)}")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Monitor progress if callback provided
        if progress_callback:
            duration = self._get_video_duration(input_path)

            for line in process.stdout:
                if line.startswith("out_time_ms=") and duration > 0:
                    try:
                        ms = int(line.split("=")[1])
                        progress = min(100, (ms / 1000000) / duration * 100)
                        progress_callback(progress)
                    except (ValueError, IndexError):
                        pass

        # Wait for completion
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            logger.error(f"FFmpeg deinterlacing failed: {stderr}")
            return False

        logger.info(f"FFmpeg deinterlacing complete ({self.engine.value}): {output_path}")
        return True

    def _generate_qtgmc_script(
        self,
        input_path: Path,
        preset: str,
        tff: bool
    ) -> Path:
        """
        Generate QTGMC VapourSynth script from template.

        Creates a .vpy script that:
        1. Loads the video using ffms2 source filter
        2. Sets field order metadata
        3. Applies QTGMC deinterlacing with specified preset
        4. Outputs the processed clip

        Args:
            input_path: Input video file
            preset: QTGMC preset name
            tff: Top field first flag

        Returns:
            Path to generated .vpy script file
        """
        # Convert preset name to title case for QTGMC
        qtgmc_preset = preset.replace("_", " ").title()

        # Field order: 2 = TFF (top field first), 1 = BFF (bottom field first)
        field_based = 2 if tff else 1

        # Generate script content
        script_content = f'''import vapoursynth as vs
from vapoursynth import core

# Try to import havsfunc for QTGMC
try:
    import havsfunc as haf
except ImportError:
    raise ImportError(
        "havsfunc not found. Install with: pip install havsfunc"
    )

# Load video using ffms2 (best compatibility)
# Fallback to other source filters if ffms2 not available
try:
    clip = core.ffms2.Source(source=r'{input_path.as_posix()}')
except AttributeError:
    try:
        clip = core.lsmas.LWLibavSource(source=r'{input_path.as_posix()}')
    except AttributeError:
        clip = core.bs.VideoSource(source=r'{input_path.as_posix()}')

# Set field order metadata
# _FieldBased: 0 = progressive, 1 = BFF, 2 = TFF
clip = core.std.SetFrameProp(clip, prop="_FieldBased", intval={field_based})

# Apply QTGMC deinterlacing
# Preset: {qtgmc_preset}
# TFF: {tff}
clip = haf.QTGMC(
    clip,
    Preset="{qtgmc_preset}",
    TFF={str(tff)},
    SourceMatch=3,         # Match to source type
    Lossless=2,           # Highest quality mode
    FPSDivisor=1          # Output same FPS (bob deinterlacing)
)

# Set output
clip.set_output()
'''

        # Write to temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.vpy',
            prefix='qtgmc_deinterlace_',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(script_content)
            script_path = Path(f.name)

        logger.debug(f"Generated VapourSynth script: {script_path}")
        return script_path

    def _get_ffmpeg_filter(self, tff: bool) -> str:
        """
        Get FFmpeg deinterlace filter string for selected engine.

        Args:
            tff: Top field first flag

        Returns:
            FFmpeg filter string (e.g., "yadif=1:-1")
        """
        # Field order: 0 = auto, 1 = BFF, 2 = TFF, -1 = auto detect
        field_order = "tff" if tff else "bff"

        if self.engine == DeinterlaceEngine.YADIF:
            # yadif=mode:parity:deint
            # mode: 0=frame (25fps->25fps), 1=field (25fps->50fps, bob)
            # parity: -1=auto, 0=BFF, 1=TFF
            # We use mode=1 (bob) for best quality
            return "yadif=1:-1"  # Bob deinterlace, auto field order

        elif self.engine == DeinterlaceEngine.BWDIF:
            # bwdif=mode:parity:deint
            # Same syntax as yadif but with better motion compensation
            return "bwdif=1:-1"  # Bob deinterlace, auto field order

        elif self.engine == DeinterlaceEngine.W3FDIF:
            # w3fdif=filter:deint
            # filter: 0=simple, 1=complex (better)
            # deint: 0=all frames, 1=interlaced only
            return f"w3fdif=1:{field_order}"

        else:
            # Fallback to yadif
            logger.warning(f"Unknown engine {self.engine}, using yadif")
            return "yadif=1:-1"

    def _get_video_duration(self, input_path: Path) -> float:
        """
        Get video duration in seconds using ffprobe.

        Args:
            input_path: Input video file

        Returns:
            Duration in seconds, or 0 if detection fails
        """
        try:
            import json
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "json",
                str(input_path)
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            data = json.loads(result.stdout)
            return float(data.get("format", {}).get("duration", 0))
        except Exception as e:
            logger.debug(f"Could not get video duration: {e}")
            return 0.0

    def get_capabilities(self) -> dict:
        """
        Get processor capabilities and configuration info.

        Returns:
            Dictionary with capability information:
            {
                "engine": "qtgmc",
                "has_vapoursynth": True,
                "has_vspipe": True,
                "available_engines": ["yadif", "bwdif", "qtgmc"],
                "qtgmc_presets": ["draft", "medium", "slow", ...],
            }
        """
        return {
            "engine": self.engine.value,
            "has_vapoursynth": self.has_vapoursynth,
            "has_vspipe": self.has_vspipe,
            "available_engines": self.list_available_engines(self.ffmpeg_path),
            "qtgmc_presets": list(self.QTGMC_PRESETS.keys()),
            "filter_quality_ranking": self.FILTER_QUALITY_RANKING,
        }


def test_deinterlace_setup(ffmpeg_path: str = "ffmpeg") -> dict:
    """
    Test deinterlacing setup and return availability status.

    This is a convenience function for testing/debugging the deinterlace
    module configuration.

    Args:
        ffmpeg_path: Path to ffmpeg executable

    Returns:
        Dictionary with test results:
        {
            "ffmpeg_available": bool,
            "vapoursynth_available": bool,
            "vspipe_available": bool,
            "available_engines": List[str],
            "recommended_engine": str,
        }
    """
    results = {
        "ffmpeg_available": False,
        "vapoursynth_available": False,
        "vspipe_available": False,
        "available_engines": [],
        "recommended_engine": None,
    }

    # Test FFmpeg
    try:
        subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            check=True,
            timeout=5
        )
        results["ffmpeg_available"] = True
    except Exception:
        pass

    # Test VapourSynth
    try:
        import vapoursynth as vs
        results["vapoursynth_available"] = True
    except ImportError:
        pass

    # Test vspipe
    try:
        subprocess.run(
            ["vspipe", "--version"],
            capture_output=True,
            check=True,
            timeout=5
        )
        results["vspipe_available"] = True
    except Exception:
        pass

    # Get available engines
    if results["ffmpeg_available"]:
        results["available_engines"] = DeinterlaceProcessor.list_available_engines(ffmpeg_path)

    # Recommend best engine
    if "qtgmc" in results["available_engines"]:
        results["recommended_engine"] = "qtgmc"
    elif "bwdif" in results["available_engines"]:
        results["recommended_engine"] = "bwdif"
    elif "yadif" in results["available_engines"]:
        results["recommended_engine"] = "yadif"

    return results
