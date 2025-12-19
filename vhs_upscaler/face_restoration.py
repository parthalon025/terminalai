#!/usr/bin/env python3
"""
Face Restoration Module
=======================

AI-powered face restoration using GFPGAN or CodeFormer for VHS and low-quality video footage.

Supports two face restoration backends:
1. **GFPGAN** - Generative Facial Prior GAN (default)
   - Fast processing
   - Good general-purpose restoration
   - Weight control (0.0-1.0)

2. **CodeFormer** - Code-based restoration with fidelity control
   - Superior quality
   - Fidelity weight (0.5-0.9) for balance between quality and likeness
   - Slower but better results

Both are particularly effective for:
- VHS talking head videos
- Old home video portraits
- Low-resolution webcam footage
- Digitized analog video interviews

This module provides a high-level wrapper around both backends for video processing.
"""

import hashlib
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


def check_gfpgan_available() -> bool:
    """
    Check if GFPGAN is available for use.

    Returns:
        True if GFPGAN can be imported and used
    """
    try:
        import gfpgan
        from basicsr.archs.rrdbnet_arch import RRDBNet
        return True
    except ImportError:
        return False


def check_codeformer_available() -> bool:
    """
    Check if CodeFormer is available for use.

    Returns:
        True if CodeFormer dependencies can be imported
    """
    try:
        import torch
        import cv2
        # CodeFormer may not be a package, just need torch + cv2
        return True
    except ImportError:
        return False


def get_available_backends() -> list:
    """
    Get list of available face restoration backends.

    Returns:
        List of backend names ('gfpgan', 'codeformer')
    """
    backends = []
    if check_gfpgan_available():
        backends.append('gfpgan')
    if check_codeformer_available():
        backends.append('codeformer')
    return backends


def restore_faces_in_video(
    input_path: str,
    output_path: str,
    backend: str = "gfpgan",
    upscale: int = 2,
    weight: float = 0.5,
    fidelity: float = 0.5
) -> str:
    """
    Convenience function for restoring faces in a video.

    Args:
        input_path: Input video file path
        output_path: Output video file path
        backend: Backend to use ('gfpgan' or 'codeformer')
        upscale: Upscale factor (1, 2, or 4)
        weight: GFPGAN restoration strength (0.0-1.0)
        fidelity: CodeFormer fidelity weight (0.5-0.9)

    Returns:
        Path to output video
    """
    from pathlib import Path

    restorer = FaceRestorer(backend=backend)
    if not restorer.has_backend:
        logger.warning(f"{backend} not available, returning original video")
        return input_path

    result = restorer.restore_faces(
        input_path=Path(input_path),
        output_path=Path(output_path),
        upscale=upscale,
        weight=weight,
        fidelity=fidelity
    )
    return str(result)


def get_available_features() -> dict:
    """
    Get dict of available face restoration features.

    Returns:
        Dict with feature availability
    """
    return {
        'face_restoration': check_gfpgan_available() or check_codeformer_available(),
        'gfpgan': check_gfpgan_available(),
        'codeformer': check_codeformer_available(),
        'backends': get_available_backends()
    }


class FaceRestorer:
    """
    Multi-backend face restoration for video processing.

    Supports GFPGAN and CodeFormer backends with automatic model downloading,
    frame extraction, face restoration, and video reassembly with audio preservation.
    """

    # GFPGAN model URLs (official releases)
    # SHA256 checksums verify file integrity and authenticity
    GFPGAN_MODELS = {
        "v1.3": {
            "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth",
            "filename": "GFPGANv1.3.pth",
            "size_mb": 332,
            "sha256": "c953a88f2727c85c3d9ae72e2bd4a0d1e5c8c6b8c67c3a9e2c3d0e3f0e0f0e0f",  # Placeholder - replace with actual
            "description": "GFPGAN v1.3 - Best quality, recommended"
        },
        "v1.4": {
            "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth",
            "filename": "GFPGANv1.4.pth",
            "size_mb": 348,
            "sha256": "d953a88f2727c85c3d9ae72e2bd4a0d1e5c8c6b8c67c3a9e2c3d0e3f0e0f0e0f",  # Placeholder - replace with actual
            "description": "GFPGAN v1.4 - Latest version, experimental"
        },
    }

    # CodeFormer model URLs (official releases)
    # SHA256 checksums verify file integrity and authenticity
    CODEFORMER_MODELS = {
        "v0.1.0": {
            "url": "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth",
            "filename": "codeformer.pth",
            "size_mb": 360,
            "sha256": "e953a88f2727c85c3d9ae72e2bd4a0d1e5c8c6b8c67c3a9e2c3d0e3f0e0f0e0f",  # Placeholder - replace with actual
            "description": "CodeFormer v0.1.0 - Superior quality with fidelity control"
        }
    }

    DEFAULT_MODEL = "v1.3"
    DEFAULT_BACKEND = "gfpgan"

    def __init__(
        self,
        model_path: Optional[Path] = None,
        model_version: str = "v1.3",
        ffmpeg_path: str = "ffmpeg",
        backend: str = "gfpgan"
    ):
        """
        Initialize Face Restorer.

        Args:
            model_path: Custom path to model file (.pth)
                       If None, uses default model directory
            model_version: Model version to use ("v1.3", "v1.4" for GFPGAN, "v0.1.0" for CodeFormer)
            ffmpeg_path: Path to ffmpeg executable
            backend: Face restoration backend ("gfpgan" or "codeformer")
        """
        self.ffmpeg_path = ffmpeg_path
        self.model_version = model_version
        self.backend = backend.lower()
        self.model_path = model_path or self._get_default_model_path()

        # Check backend availability
        if self.backend == "gfpgan":
            self.has_backend = self._check_gfpgan()
            backend_name = "GFPGAN"
        elif self.backend == "codeformer":
            self.has_backend = self._check_codeformer()
            backend_name = "CodeFormer"
        else:
            logger.error(f"Unknown backend: {self.backend}, falling back to GFPGAN")
            self.backend = "gfpgan"
            self.has_backend = self._check_gfpgan()
            backend_name = "GFPGAN"

        if self.has_backend:
            logger.info(f"{backend_name} available: {self.model_path}")
        else:
            logger.warning(f"{backend_name} not available - face restoration disabled")

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

    def _check_codeformer(self) -> bool:
        """
        Check if CodeFormer is available and functional.

        Returns:
            True if CodeFormer can be imported and used
        """
        try:
            # Try importing CodeFormer dependencies
            import torch
            import cv2

            # Try to import CodeFormer if package is installed
            try:
                from codeformer import CodeFormer
            except ImportError:
                # CodeFormer may not be a package, just check torch availability
                pass

            # Check if model exists
            if not self.model_path.exists():
                logger.warning(
                    f"CodeFormer model not found at {self.model_path}. "
                    f"Run with --download-models to download."
                )
                return False

            return True

        except ImportError as e:
            logger.debug(f"CodeFormer dependencies import failed: {e}")
            return False

    def _get_default_model_path(self) -> Path:
        """
        Get default model path based on backend and version.

        Returns:
            Path to model file (may not exist yet)
        """
        if self.backend == "codeformer":
            model_dir = Path("models") / "codeformer"
            model_dir.mkdir(parents=True, exist_ok=True)
            model_info = self.CODEFORMER_MODELS.get(self.model_version, self.CODEFORMER_MODELS["v0.1.0"])
        else:  # gfpgan
            model_dir = Path("models") / "gfpgan"
            model_dir.mkdir(parents=True, exist_ok=True)
            model_info = self.GFPGAN_MODELS.get(self.model_version, self.GFPGAN_MODELS[self.DEFAULT_MODEL])

        return model_dir / model_info["filename"]

    def _verify_checksum(self, file_path: Path, expected_sha256: str) -> bool:
        """
        Verify file integrity using SHA256 checksum.

        Security: Prevents use of corrupted or tampered model files.

        Args:
            file_path: Path to file to verify
            expected_sha256: Expected SHA256 hash (hex string)

        Returns:
            True if checksum matches, False otherwise
        """
        # Skip verification if placeholder checksum (starts with c/d/e953a88f...)
        # This allows development until actual checksums are obtained
        if expected_sha256.startswith(('c953a88f', 'd953a88f', 'e953a88f')):
            logger.warning(f"SECURITY: Checksum verification skipped - using placeholder hash")
            logger.warning(f"  File: {file_path.name}")
            logger.warning(f"  Update model checksums in face_restoration.py for production use")
            return True

        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256_hash.update(chunk)

            calculated_hash = sha256_hash.hexdigest()

            if calculated_hash.lower() == expected_sha256.lower():
                logger.info(f"Checksum verified: {file_path.name}")
                return True
            else:
                logger.error(f"SECURITY: Checksum mismatch for {file_path.name}")
                logger.error(f"  Expected: {expected_sha256}")
                logger.error(f"  Got:      {calculated_hash}")
                logger.error(f"  File may be corrupted or tampered with!")
                return False

        except Exception as e:
            logger.error(f"Checksum verification failed: {e}")
            return False

    def download_model(self, force: bool = False, progress_callback=None) -> bool:
        """
        Download model from official GitHub releases (GFPGAN or CodeFormer).

        Security: Verifies file integrity using SHA256 checksum after download.

        Args:
            force: Force re-download even if model exists
            progress_callback: Optional callback(downloaded_mb, total_mb, speed_mbps, eta_seconds, status_msg)
                              for progress updates (used by first-run wizard)

        Returns:
            True if download successful or model already exists
        """
        if self.model_path.exists() and not force:
            logger.info(f"Model already exists: {self.model_path}")
            return True

        if not HAS_REQUESTS:
            logger.error("requests library not available. Install: pip install requests")
            return False

        # Select model info based on backend
        if self.backend == "codeformer":
            model_info = self.CODEFORMER_MODELS.get(self.model_version, self.CODEFORMER_MODELS["v0.1.0"])
        else:
            model_info = self.GFPGAN_MODELS.get(self.model_version, self.GFPGAN_MODELS[self.DEFAULT_MODEL])

        url = model_info["url"]
        size_mb = model_info["size_mb"]
        expected_sha256 = model_info.get("sha256", "")

        backend_name = "CodeFormer" if self.backend == "codeformer" else "GFPGAN"
        logger.info(f"Downloading {backend_name} {self.model_version} ({size_mb}MB)...")
        logger.info(f"URL: {url}")
        logger.info(f"Destination: {self.model_path}")

        temp_path = self.model_path.with_suffix('.tmp')

        try:
            import time

            # Download with progress bar
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            total_mb = total_size / (1024 * 1024)

            downloaded = 0
            start_time = time.time()

            # Create temporary file
            with open(temp_path, 'wb') as f:
                if HAS_TQDM and total_size > 0 and not progress_callback:
                    # Progress bar for CLI
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
                    # Download with optional progress callback
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                            # Update progress callback
                            if progress_callback:
                                downloaded_mb = downloaded / (1024 * 1024)
                                elapsed = time.time() - start_time

                                if elapsed > 0:
                                    speed_mbps = downloaded_mb / elapsed
                                    remaining_mb = total_mb - downloaded_mb
                                    eta_seconds = remaining_mb / speed_mbps if speed_mbps > 0 else 0

                                    progress_callback(
                                        downloaded_mb,
                                        total_mb,
                                        speed_mbps,
                                        eta_seconds,
                                        f"Downloading {backend_name}..."
                                    )

            # SECURITY: Verify checksum before using the downloaded file
            if expected_sha256:
                logger.info("Verifying file integrity...")
                if progress_callback:
                    progress_callback(total_mb, total_mb, 0, 0, "Verifying integrity...")

                if not self._verify_checksum(temp_path, expected_sha256):
                    logger.error("Downloaded file failed checksum verification!")
                    logger.error("This may indicate a corrupted download or security issue.")
                    temp_path.unlink()
                    return False
            else:
                logger.warning("No checksum available for verification - skipping")

            # Move temp file to final location
            temp_path.rename(self.model_path)

            logger.info(f"Model downloaded successfully: {self.model_path}")
            if progress_callback:
                progress_callback(total_mb, total_mb, 0, 0, f"{backend_name} downloaded successfully!")

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
        fidelity: float = 0.5,
        only_center_face: bool = False,
        aligned: bool = False,
        tile_size: int = 512
    ) -> Path:
        """
        Process video frames through face restoration (GFPGAN or CodeFormer).

        Pipeline:
        1. Extract frames from video
        2. Run face restoration on each frame
        3. Reassemble video with restored faces
        4. Remux audio from original

        Args:
            input_path: Input video file path
            output_path: Output video file path
            upscale: Upscale factor (1, 2, or 4)
                    Note: AI models do their own upscaling
            weight: Face restoration strength for GFPGAN (0.0 = original, 1.0 = full restoration)
            fidelity: Fidelity weight for CodeFormer (0.5-0.9, higher = more faithful to original)
            only_center_face: Only restore the largest/center face
            aligned: Whether faces are pre-aligned (False for video)
            tile_size: Tile size for processing (512 or 400, affects VRAM usage)

        Returns:
            Path to output video with restored faces

        Raises:
            RuntimeError: If backend not available or processing fails
        """
        if not self.has_backend:
            backend_name = "CodeFormer" if self.backend == "codeformer" else "GFPGAN"
            logger.warning(f"{backend_name} not available, returning original video")
            return input_path

        backend_name = "CodeFormer" if self.backend == "codeformer" else "GFPGAN"
        logger.info(f"Starting {backend_name} face restoration...")
        logger.info(f"  Input: {input_path}")
        logger.info(f"  Upscale: {upscale}x")
        if self.backend == "codeformer":
            logger.info(f"  Fidelity: {fidelity}")
        else:
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

            # Run face restoration with selected backend
            restored_dir = temp_path / "restored"
            if self.backend == "codeformer":
                logger.info("Running CodeFormer face restoration...")
                self._process_frames_codeformer(
                    frames_dir=frames_dir,
                    output_dir=restored_dir,
                    upscale=upscale,
                    fidelity=fidelity,
                    only_center_face=only_center_face
                )
            else:
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
            backend_name = "CodeFormer" if self.backend == "codeformer" else "GFPGAN"
            if len(restored_files) == 0:
                raise RuntimeError(f"{backend_name} produced no output frames")

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

    def _process_frames_codeformer(
        self,
        frames_dir: Path,
        output_dir: Path,
        upscale: int,
        fidelity: float,
        only_center_face: bool
    ):
        """
        Process frames with CodeFormer.

        Args:
            frames_dir: Directory containing input frames
            output_dir: Directory for restored frames
            upscale: Upscale factor (1, 2, or 4)
            fidelity: Fidelity weight (0.5-0.9, higher = more faithful to original)
            only_center_face: Only process center face
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            import torch
            import cv2
            import numpy as np
            from torchvision.transforms.functional import normalize

            # Check for CodeFormer package or load directly
            try:
                from codeformer.basicsr.utils import img2tensor, tensor2img
                from codeformer.facelib.utils.face_restoration_helper import FaceRestoreHelper
                from codeformer.basicsr.archs.codeformer_arch import CodeFormer as CodeFormerArch
            except ImportError:
                # Fallback: Try BasicSR utilities
                try:
                    from basicsr.utils import img2tensor, tensor2img
                    logger.warning("CodeFormer package not found, using BasicSR utilities")
                    # Need to load CodeFormer model manually
                    logger.error("CodeFormer architecture not available")
                    raise RuntimeError("CodeFormer not properly installed")
                except ImportError:
                    logger.error("Neither CodeFormer nor BasicSR utilities available")
                    raise RuntimeError("CodeFormer dependencies not installed")

            # Device setup
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"Using device: {device}")

            # Initialize CodeFormer model
            logger.info("Initializing CodeFormer...")
            net = CodeFormerArch(
                dim_embd=512,
                codebook_size=1024,
                n_head=8,
                n_layers=9,
                connect_list=['32', '64', '128', '256']
            ).to(device)

            # Load checkpoint
            checkpoint = torch.load(str(self.model_path), map_location=device)
            if 'params_ema' in checkpoint:
                net.load_state_dict(checkpoint['params_ema'])
            elif 'params' in checkpoint:
                net.load_state_dict(checkpoint['params'])
            else:
                net.load_state_dict(checkpoint)
            net.eval()

            # Initialize face restoration helper
            face_helper = FaceRestoreHelper(
                upscale_factor=upscale,
                face_size=512,
                crop_ratio=(1, 1),
                det_model='retinaface_resnet50',
                save_ext='png',
                use_parse=True,
                device=device
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

                # Process with CodeFormer
                try:
                    # Detect and align faces
                    face_helper.clean_all()
                    face_helper.read_image(img)
                    face_helper.get_face_landmarks_5(
                        only_center_face=only_center_face,
                        resize=640,
                        eye_dist_threshold=5
                    )
                    face_helper.align_warp_face()

                    # Restore each face
                    for idx, cropped_face in enumerate(face_helper.cropped_faces):
                        # Prepare input
                        cropped_face_t = img2tensor(
                            cropped_face / 255.0,
                            bgr2rgb=True,
                            float32=True
                        )
                        normalize(
                            cropped_face_t,
                            (0.5, 0.5, 0.5),
                            (0.5, 0.5, 0.5),
                            inplace=True
                        )
                        cropped_face_t = cropped_face_t.unsqueeze(0).to(device)

                        # Inference with fidelity weight
                        with torch.no_grad():
                            output = net(cropped_face_t, w=fidelity, adain=True)[0]
                            restored_face = tensor2img(output, rgb2bgr=True, min_max=(-1, 1))

                        del output
                        torch.cuda.empty_cache()

                        # Store restored face
                        face_helper.add_restored_face(restored_face)

                    # Paste faces back to original image
                    face_helper.get_inverse_affine(None)
                    restored_img = face_helper.paste_faces_to_input_image()

                    # Save restored frame
                    output_path = output_dir / frame_path.name
                    cv2.imwrite(str(output_path), restored_img)

                except Exception as e:
                    logger.warning(f"Failed to restore frame {frame_path.name}: {e}")
                    # Copy original frame as fallback
                    shutil.copy(frame_path, output_dir / frame_path.name)

            logger.info("CodeFormer processing complete")

        except ImportError as e:
            logger.error(f"CodeFormer dependencies not available: {e}")
            logger.error("Install: pip install torch opencv-python")
            logger.error("CodeFormer package: https://github.com/sczhou/CodeFormer")
            raise RuntimeError("CodeFormer not properly installed")

        except Exception as e:
            logger.error(f"CodeFormer processing error: {e}")
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
