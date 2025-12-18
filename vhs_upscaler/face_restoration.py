#!/usr/bin/env python3
"""
GFPGAN Face Restoration Module
===============================

AI-powered face restoration using GFPGAN for VHS and low-quality video footage.

GFPGAN (Generative Facial Prior GAN) is designed to restore severely degraded faces
in images and videos. It's particularly effective for:
- VHS talking head videos
- Old home video portraits
- Low-resolution webcam footage
- Digitized analog video interviews

This module provides a high-level wrapper around GFPGAN for video processing.
"""

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import shutil

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


logger = logging.getLogger(__name__)


class FaceRestorer:
    """
    GFPGAN-based face restoration for video processing.

    Handles model downloading, frame extraction, face restoration,
    and video reassembly with audio preservation.
    """

    # GFPGAN model URLs (official releases)
    GFPGAN_MODELS = {
        "v1.3": {
            "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth",
            "filename": "GFPGANv1.3.pth",
            "size_mb": 332,
            "description": "GFPGAN v1.3 - Best quality, recommended"
        },
        "v1.4": {
            "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth",
            "filename": "GFPGANv1.4.pth",
            "size_mb": 348,
            "description": "GFPGAN v1.4 - Latest version, experimental"
        },
    }

    DEFAULT_MODEL = "v1.3"

    def __init__(
        self,
        model_path: Optional[Path] = None,
        model_version: str = "v1.3",
        ffmpeg_path: str = "ffmpeg"
    ):
        """
        Initialize Face Restorer.

        Args:
            model_path: Custom path to GFPGAN model file (.pth)
                       If None, uses default model directory
            model_version: GFPGAN version to use ("v1.3" or "v1.4")
            ffmpeg_path: Path to ffmpeg executable
        """
        self.ffmpeg_path = ffmpeg_path
        self.model_version = model_version
        self.model_path = model_path or self._get_default_model_path()
        self.has_gfpgan = self._check_gfpgan()

        if self.has_gfpgan:
            logger.info(f"GFPGAN available: {self.model_path}")
        else:
            logger.warning("GFPGAN not available - face restoration disabled")

    def _check_gfpgan(self) -> bool:
        """
        Check if GFPGAN is available and functional.

        Returns:
            True if GFPGAN can be imported and used
        """
        try:
            # Try importing GFPGAN
            import gfpgan
            from basicsr.archs.rrdbnet_arch import RRDBNet

            # Check if model exists
            if not self.model_path.exists():
                logger.warning(
                    f"GFPGAN model not found at {self.model_path}. "
                    f"Run with --download-models to download."
                )
                return False

            return True

        except ImportError as e:
            logger.debug(f"GFPGAN import failed: {e}")
            return False

    def _get_default_model_path(self) -> Path:
        """
        Get default model path based on version.

        Returns:
            Path to model file (may not exist yet)
        """
        model_dir = Path("models") / "gfpgan"
        model_dir.mkdir(parents=True, exist_ok=True)

        model_info = self.GFPGAN_MODELS.get(self.model_version, self.GFPGAN_MODELS[self.DEFAULT_MODEL])
        return model_dir / model_info["filename"]

    def download_model(self, force: bool = False) -> bool:
        """
        Download GFPGAN model from official GitHub releases.

        Args:
            force: Force re-download even if model exists

        Returns:
            True if download successful or model already exists
        """
        if self.model_path.exists() and not force:
            logger.info(f"Model already exists: {self.model_path}")
            return True

        if not HAS_REQUESTS:
            logger.error("requests library not available. Install: pip install requests")
            return False

        model_info = self.GFPGAN_MODELS.get(
            self.model_version,
            self.GFPGAN_MODELS[self.DEFAULT_MODEL]
        )

        url = model_info["url"]
        size_mb = model_info["size_mb"]

        logger.info(f"Downloading GFPGAN {self.model_version} ({size_mb}MB)...")
        logger.info(f"URL: {url}")
        logger.info(f"Destination: {self.model_path}")

        try:
            # Download with progress bar
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            # Create temporary file
            temp_path = self.model_path.with_suffix('.tmp')

            with open(temp_path, 'wb') as f:
                if HAS_TQDM and total_size > 0:
                    # Progress bar
                    with tqdm(
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        desc="Downloading"
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    # Simple download without progress
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            # Move temp file to final location
            temp_path.rename(self.model_path)

            logger.info(f"Model downloaded successfully: {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Model download failed: {e}")
            if temp_path.exists():
                temp_path.unlink()
            return False

    def restore_faces(
        self,
        input_path: Path,
        output_path: Path,
        upscale: int = 2,
        weight: float = 0.5,
        only_center_face: bool = False,
        aligned: bool = False,
        tile_size: int = 512
    ) -> Path:
        """
        Process video frames through GFPGAN face restoration.

        Pipeline:
        1. Extract frames from video
        2. Run GFPGAN on each frame
        3. Reassemble video with restored faces
        4. Remux audio from original

        Args:
            input_path: Input video file path
            output_path: Output video file path
            upscale: Upscale factor (1, 2, or 4)
                    Note: GFPGAN does its own upscaling
            weight: Face restoration strength (0.0 = original, 1.0 = full restoration)
            only_center_face: Only restore the largest/center face
            aligned: Whether faces are pre-aligned (False for video)
            tile_size: Tile size for processing (512 or 400, affects VRAM usage)

        Returns:
            Path to output video with restored faces

        Raises:
            RuntimeError: If GFPGAN not available or processing fails
        """
        if not self.has_gfpgan:
            logger.warning("GFPGAN not available, returning original video")
            return input_path

        logger.info("Starting GFPGAN face restoration...")
        logger.info(f"  Input: {input_path}")
        logger.info(f"  Upscale: {upscale}x")
        logger.info(f"  Weight: {weight}")
        logger.info(f"  Only center face: {only_center_face}")

        # Create temp directory for frame processing
        with tempfile.TemporaryDirectory(prefix="gfpgan_") as temp_dir:
            temp_path = Path(temp_dir)

            # Extract frames
            frames_dir = temp_path / "frames"
            logger.info("Extracting frames...")
            self._extract_frames(input_path, frames_dir)

            # Count frames
            frame_files = sorted(frames_dir.glob("frame_*.png"))
            total_frames = len(frame_files)
            logger.info(f"Extracted {total_frames} frames")

            if total_frames == 0:
                raise RuntimeError("No frames extracted from video")

            # Run GFPGAN
            restored_dir = temp_path / "restored"
            logger.info("Running GFPGAN face restoration...")
            self._process_frames_gfpgan(
                frames_dir=frames_dir,
                output_dir=restored_dir,
                upscale=upscale,
                weight=weight,
                only_center_face=only_center_face,
                aligned=aligned,
                tile_size=tile_size
            )

            # Verify restoration output
            restored_files = sorted(restored_dir.glob("*.png"))
            if len(restored_files) == 0:
                raise RuntimeError("GFPGAN produced no output frames")

            logger.info(f"Restored {len(restored_files)} frames")

            # Reassemble video
            logger.info("Reassembling video...")
            self._reassemble_video(restored_dir, output_path, input_path)

        logger.info(f"Face restoration complete: {output_path}")
        return output_path

    def _extract_frames(self, input_path: Path, frames_dir: Path):
        """
        Extract video frames to directory.

        Args:
            input_path: Input video file
            frames_dir: Output directory for frames
        """
        frames_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.ffmpeg_path,
            "-i", str(input_path),
            "-qscale:v", "1",  # High quality PNG frames
            "-qmin", "1",
            "-qmax", "1",
            "-vsync", "0",  # Preserve all frames
            str(frames_dir / "frame_%08d.png")
        ]

        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Frame extraction failed: {e.stderr}")
            raise RuntimeError("Failed to extract frames")

    def _process_frames_gfpgan(
        self,
        frames_dir: Path,
        output_dir: Path,
        upscale: int,
        weight: float,
        only_center_face: bool,
        aligned: bool,
        tile_size: int
    ):
        """
        Process frames with GFPGAN.

        Args:
            frames_dir: Directory containing input frames
            output_dir: Directory for restored frames
            upscale: Upscale factor
            weight: Restoration weight
            only_center_face: Only process center face
            aligned: Face alignment flag
            tile_size: Processing tile size
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            import cv2
            from gfpgan import GFPGANer
            from basicsr.archs.rrdbnet_arch import RRDBNet

            # Initialize background upsampler (Real-ESRGAN)
            bg_upsampler = None
            if upscale > 1:
                try:
                    bg_upsampler = RRDBNet(
                        num_in_ch=3,
                        num_out_ch=3,
                        num_feat=64,
                        num_block=23,
                        num_grow_ch=32,
                        scale=upscale
                    )
                    logger.debug("Background upsampler initialized")
                except Exception as e:
                    logger.warning(f"Could not initialize background upsampler: {e}")

            # Initialize GFPGAN
            logger.info("Initializing GFPGAN...")
            restorer = GFPGANer(
                model_path=str(self.model_path),
                upscale=upscale,
                arch='clean',
                channel_multiplier=2,
                bg_upsampler=bg_upsampler
            )

            # Process each frame
            frame_files = sorted(frames_dir.glob("frame_*.png"))

            for i, frame_path in enumerate(frame_files):
                if i % 10 == 0:
                    logger.info(f"Processing frame {i+1}/{len(frame_files)}...")

                # Read frame
                img = cv2.imread(str(frame_path), cv2.IMREAD_COLOR)
                if img is None:
                    logger.warning(f"Could not read frame: {frame_path}")
                    continue

                # Enhance with GFPGAN
                try:
                    _, _, restored_img = restorer.enhance(
                        img,
                        has_aligned=aligned,
                        only_center_face=only_center_face,
                        paste_back=True,
                        weight=weight
                    )

                    # Save restored frame
                    output_path = output_dir / frame_path.name
                    cv2.imwrite(str(output_path), restored_img)

                except Exception as e:
                    logger.warning(f"Failed to restore frame {frame_path.name}: {e}")
                    # Copy original frame as fallback
                    shutil.copy(frame_path, output_dir / frame_path.name)

            logger.info("GFPGAN processing complete")

        except ImportError as e:
            logger.error(f"GFPGAN dependencies not available: {e}")
            logger.error("Install: pip install gfpgan basicsr opencv-python")
            raise RuntimeError("GFPGAN not properly installed")

        except Exception as e:
            logger.error(f"GFPGAN processing error: {e}")
            raise RuntimeError(f"Face restoration failed: {e}")

    def _reassemble_video(
        self,
        frames_dir: Path,
        output_path: Path,
        original_video: Path
    ):
        """
        Reassemble frames back into video with audio.

        Args:
            frames_dir: Directory containing restored frames
            output_path: Output video path
            original_video: Original video (for audio and metadata)
        """
        # Get framerate from original video
        fps = self._get_framerate(original_video)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Reassemble video with audio
        cmd = [
            self.ffmpeg_path,
            "-y",  # Overwrite output
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%08d.png"),
            "-i", str(original_video),  # Get audio from original
            "-map", "0:v",  # Video from frames
            "-map", "1:a?",  # Audio from original (optional)
            "-c:v", "libx264",
            "-crf", "18",  # High quality
            "-preset", "medium",
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",  # Copy audio without re-encoding
            str(output_path)
        ]

        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Video reassembly failed: {e.stderr}")
            raise RuntimeError("Failed to reassemble video")

    def _get_framerate(self, video_path: Path) -> float:
        """
        Get video framerate using ffprobe.

        Args:
            video_path: Video file path

        Returns:
            Framerate as float (e.g., 29.97, 30.0)
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )

            # Parse fraction (e.g., "30000/1001" or "30/1")
            fps_str = result.stdout.strip()
            if '/' in fps_str:
                num, den = map(int, fps_str.split('/'))
                return num / den if den != 0 else 30.0
            else:
                return float(fps_str)

        except Exception as e:
            logger.warning(f"Could not get framerate: {e}")
            return 30.0  # Default fallback

    def check_installation(self) -> dict:
        """
        Check GFPGAN installation status and requirements.

        Returns:
            Dict with installation status information
        """
        status = {
            "gfpgan_installed": False,
            "model_exists": False,
            "model_path": str(self.model_path),
            "dependencies": {
                "gfpgan": False,
                "basicsr": False,
                "opencv": False,
                "torch": False,
            },
            "ready": False
        }

        # Check dependencies
        try:
            import gfpgan
            status["dependencies"]["gfpgan"] = True
        except ImportError:
            pass

        try:
            import basicsr
            status["dependencies"]["basicsr"] = True
        except ImportError:
            pass

        try:
            import cv2
            status["dependencies"]["opencv"] = True
        except ImportError:
            pass

        try:
            import torch
            status["dependencies"]["torch"] = True
        except ImportError:
            pass

        # Check model file
        status["model_exists"] = self.model_path.exists()
        if status["model_exists"]:
            size_mb = self.model_path.stat().st_size / (1024 * 1024)
            status["model_size_mb"] = round(size_mb, 2)

        # Overall status
        status["gfpgan_installed"] = all(status["dependencies"].values())
        status["ready"] = status["gfpgan_installed"] and status["model_exists"]

        return status

    def print_installation_guide(self):
        """Print installation instructions for GFPGAN."""
        print("\n" + "=" * 60)
        print("  GFPGAN Face Restoration Installation")
        print("=" * 60)

        status = self.check_installation()

        print("\nDependencies:")
        for dep, installed in status["dependencies"].items():
            status_str = "[OK]" if installed else "[MISSING]"
            print(f"  {status_str} {dep}")

        print(f"\nModel:")
        if status["model_exists"]:
            print(f"  [OK] {self.model_path}")
            print(f"       Size: {status.get('model_size_mb', 0):.2f} MB")
        else:
            print(f"  [MISSING] {self.model_path}")

        if not status["ready"]:
            print("\n" + "-" * 60)
            print("Installation Instructions:")
            print("-" * 60)

            if not status["gfpgan_installed"]:
                print("\n1. Install GFPGAN and dependencies:")
                print("   pip install gfpgan basicsr opencv-python torch")

            if not status["model_exists"]:
                print("\n2. Download GFPGAN model:")
                print(f"   vhs-upscale --download-gfpgan-model")
                print("   OR")
                print(f"   Manual download from:")
                model_info = self.GFPGAN_MODELS[self.model_version]
                print(f"   {model_info['url']}")

        else:
            print("\n[OK] GFPGAN is ready to use!")

        print("\n" + "=" * 60)


def main():
    """CLI entry point for testing face restoration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="GFPGAN Face Restoration Module"
    )
    parser.add_argument("input", nargs="?", help="Input video file")
    parser.add_argument("-o", "--output", help="Output video file")
    parser.add_argument("--check", action="store_true",
                       help="Check installation status")
    parser.add_argument("--download-model", action="store_true",
                       help="Download GFPGAN model")
    parser.add_argument("--weight", type=float, default=0.5,
                       help="Restoration weight (0.0-1.0)")
    parser.add_argument("--upscale", type=int, default=2, choices=[1, 2, 4],
                       help="Upscale factor")

    args = parser.parse_args()

    # Initialize restorer
    restorer = FaceRestorer()

    # Check installation
    if args.check:
        restorer.print_installation_guide()
        return

    # Download model
    if args.download_model:
        success = restorer.download_model()
        if success:
            print("Model downloaded successfully!")
        else:
            print("Model download failed")
        return

    # Process video
    if args.input and args.output:
        restorer.restore_faces(
            Path(args.input),
            Path(args.output),
            upscale=args.upscale,
            weight=args.weight
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
