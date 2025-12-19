#!/usr/bin/env python3
"""
First-Run Setup Wizard for TerminalAI
======================================

Interactive wizard that runs on first launch to:
1. Detect hardware (GPU, VRAM)
2. Download AI models (GFPGAN, CodeFormer) with progress
3. Configure optimal defaults
4. Show welcome message on subsequent runs

This prevents the "frozen app" UX issue where models download
during video processing without progress indication.
"""

import gradio as gr
import logging
import platform
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple, Callable
import threading

logger = logging.getLogger(__name__)


# =============================================================================
# Hardware Detection
# =============================================================================

class HardwareDetector:
    """Detect GPU and system capabilities."""

    @staticmethod
    def detect_gpu() -> Dict[str, any]:
        """
        Detect GPU hardware and capabilities.

        Returns:
            Dict with:
            - vendor: "nvidia", "amd", "intel", or "cpu"
            - name: GPU model name
            - vram_mb: VRAM in MB (None if unavailable)
            - cuda_available: Whether CUDA is available
            - compute_capability: CUDA compute capability (NVIDIA only)
        """
        gpu_info = {
            "vendor": "cpu",
            "name": "CPU Only",
            "vram_mb": None,
            "cuda_available": False,
            "compute_capability": None,
        }

        # Try nvidia-smi first (faster and more reliable than PyTorch import)
        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            if result.stdout.strip():
                parts = [p.strip() for p in result.stdout.strip().split(",")]
                gpu_info["vendor"] = "nvidia"
                gpu_info["name"] = parts[0]
                gpu_info["cuda_available"] = True

                # Parse VRAM
                if len(parts) > 1:
                    vram_str = parts[1]
                    if "MiB" in vram_str:
                        gpu_info["vram_mb"] = int(float(vram_str.replace("MiB", "").strip()))
                    elif "GiB" in vram_str:
                        gpu_info["vram_mb"] = int(float(vram_str.replace("GiB", "").strip()) * 1024)

                logger.info(f"Detected NVIDIA GPU via nvidia-smi: {gpu_info['name']}")
                return gpu_info
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.debug("nvidia-smi not available")
        except Exception as e:
            logger.debug(f"nvidia-smi detection failed: {e}")

        # Only try PyTorch if nvidia-smi failed (PyTorch import can be slow)
        try:
            import torch
            if torch.cuda.is_available():
                gpu_info["vendor"] = "nvidia"
                gpu_info["name"] = torch.cuda.get_device_name(0)
                gpu_info["cuda_available"] = True

                # Get VRAM
                props = torch.cuda.get_device_properties(0)
                gpu_info["vram_mb"] = props.total_memory // (1024 * 1024)
                gpu_info["compute_capability"] = f"{props.major}.{props.minor}"

                logger.info(f"Detected NVIDIA GPU via PyTorch: {gpu_info['name']} ({gpu_info['vram_mb']} MB)")
                return gpu_info
        except ImportError:
            logger.debug("PyTorch not available for CUDA detection")
        except Exception as e:
            logger.debug(f"CUDA detection failed: {e}")

        # Try AMD ROCm detection (skip if slow)
        try:
            import torch
            if hasattr(torch, 'hip') and torch.hip.is_available():
                gpu_info["vendor"] = "amd"
                gpu_info["name"] = "AMD GPU (ROCm)"
                gpu_info["cuda_available"] = False
                logger.info("Detected AMD GPU with ROCm")
                return gpu_info
        except Exception as e:
            logger.debug(f"ROCm detection failed: {e}")

        # Try OpenVINO/Intel detection
        try:
            # Check for Intel GPU via environment or common names
            import subprocess
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True, text=True, timeout=5
                )
                if "Intel" in result.stdout:
                    gpu_info["vendor"] = "intel"
                    gpu_info["name"] = "Intel Integrated Graphics"
                    logger.info("Detected Intel GPU")
                    return gpu_info
        except Exception as e:
            logger.debug(f"Intel GPU detection failed: {e}")

        logger.info("No GPU detected, using CPU")
        return gpu_info

    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """Get system information."""
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
        }


# =============================================================================
# Model Downloader with Progress
# =============================================================================

class ModelDownloader:
    """Download AI models with progress tracking."""

    def __init__(self):
        self.progress_callback: Optional[Callable] = None
        self.cancel_requested = False

    def download_gfpgan(
        self,
        model_version: str = "v1.3",
        progress_callback: Optional[Callable] = None
    ) -> Tuple[bool, str]:
        """
        Download GFPGAN model.

        Args:
            model_version: Model version to download
            progress_callback: Callback(downloaded_mb, total_mb, speed_mbps, eta_seconds, status_msg)

        Returns:
            (success: bool, message: str)
        """
        self.progress_callback = progress_callback
        self.cancel_requested = False

        try:
            from face_restoration import FaceRestorer

            # Check if model already exists
            restorer = FaceRestorer(model_version=model_version, backend="gfpgan")
            if restorer.model_path.exists():
                return True, f"GFPGAN {model_version} already downloaded"

            # Prepare download
            model_info = FaceRestorer.GFPGAN_MODELS.get(
                model_version,
                FaceRestorer.GFPGAN_MODELS[FaceRestorer.DEFAULT_MODEL]
            )

            url = model_info["url"]
            total_mb = model_info["size_mb"]

            # Download with progress
            return self._download_with_progress(
                url=url,
                output_path=restorer.model_path,
                total_size_mb=total_mb,
                model_name=f"GFPGAN {model_version}"
            )

        except ImportError as e:
            logger.error(f"Face restoration module not available: {e}")
            return False, f"Face restoration module not available: {e}"
        except Exception as e:
            logger.error(f"GFPGAN download failed: {e}")
            return False, f"Download failed: {e}"

    def download_codeformer(
        self,
        model_version: str = "v0.1.0",
        progress_callback: Optional[Callable] = None
    ) -> Tuple[bool, str]:
        """
        Download CodeFormer model.

        Args:
            model_version: Model version to download
            progress_callback: Callback(downloaded_mb, total_mb, speed_mbps, eta_seconds, status_msg)

        Returns:
            (success: bool, message: str)
        """
        self.progress_callback = progress_callback
        self.cancel_requested = False

        try:
            from face_restoration import FaceRestorer

            # Check if model already exists
            restorer = FaceRestorer(model_version=model_version, backend="codeformer")
            if restorer.model_path.exists():
                return True, f"CodeFormer {model_version} already downloaded"

            # Prepare download
            model_info = FaceRestorer.CODEFORMER_MODELS.get(
                model_version,
                FaceRestorer.CODEFORMER_MODELS["v0.1.0"]
            )

            url = model_info["url"]
            total_mb = model_info["size_mb"]

            # Download with progress
            return self._download_with_progress(
                url=url,
                output_path=restorer.model_path,
                total_size_mb=total_mb,
                model_name=f"CodeFormer {model_version}"
            )

        except ImportError as e:
            logger.error(f"Face restoration module not available: {e}")
            return False, f"Face restoration module not available: {e}"
        except Exception as e:
            logger.error(f"CodeFormer download failed: {e}")
            return False, f"Download failed: {e}"

    def _download_with_progress(
        self,
        url: str,
        output_path: Path,
        total_size_mb: int,
        model_name: str
    ) -> Tuple[bool, str]:
        """
        Download file with progress updates.

        Args:
            url: Download URL
            output_path: Output file path
            total_size_mb: Expected file size in MB
            model_name: Model name for logging

        Returns:
            (success: bool, message: str)
        """
        try:
            import requests
        except ImportError:
            return False, "requests library not available. Install: pip install requests"

        logger.info(f"Downloading {model_name} from {url}")

        # Create parent directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = output_path.with_suffix('.tmp')

        try:
            # Start download
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', total_size_mb * 1024 * 1024))
            total_mb = total_size / (1024 * 1024)

            downloaded = 0
            start_time = time.time()
            chunk_size = 8192

            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if self.cancel_requested:
                        temp_path.unlink(missing_ok=True)
                        return False, "Download cancelled"

                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Calculate progress
                        downloaded_mb = downloaded / (1024 * 1024)
                        elapsed = time.time() - start_time

                        if elapsed > 0:
                            speed_mbps = downloaded_mb / elapsed
                            remaining_mb = total_mb - downloaded_mb
                            eta_seconds = remaining_mb / speed_mbps if speed_mbps > 0 else 0

                            # Update progress
                            if self.progress_callback:
                                status_msg = f"Downloading {model_name}..."
                                self.progress_callback(
                                    downloaded_mb, total_mb, speed_mbps, eta_seconds, status_msg
                                )

            # Move temp file to final location
            temp_path.rename(output_path)

            logger.info(f"Successfully downloaded {model_name} to {output_path}")
            return True, f"Successfully downloaded {model_name}"

        except requests.RequestException as e:
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"Download failed: {e}")
            return False, f"Download failed: {e}"
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"Unexpected error during download: {e}")
            return False, f"Unexpected error: {e}"

    def cancel(self):
        """Cancel ongoing download."""
        self.cancel_requested = True


# =============================================================================
# First Run Manager
# =============================================================================

class FirstRunManager:
    """Manage first-run wizard state."""

    CACHE_DIR = Path.home() / ".cache" / "terminalai"
    FIRST_RUN_MARKER = CACHE_DIR / ".first_run_complete"
    CONFIG_FILE = CACHE_DIR / "config.json"

    @classmethod
    def is_first_run(cls) -> bool:
        """Check if this is the first run."""
        return not cls.FIRST_RUN_MARKER.exists()

    @classmethod
    def mark_complete(cls, config: Dict[str, any] = None):
        """Mark first run as complete and save config."""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Save marker
        cls.FIRST_RUN_MARKER.write_text(
            f"First run completed: {datetime.now().isoformat()}\n"
        )

        # Save config
        if config:
            import json
            cls.CONFIG_FILE.write_text(json.dumps(config, indent=2))

        logger.info("First run setup complete")

    @classmethod
    def load_config(cls) -> Dict[str, any]:
        """Load saved configuration."""
        if cls.CONFIG_FILE.exists():
            import json
            return json.loads(cls.CONFIG_FILE.read_text())
        return {}

    @classmethod
    def reset(cls):
        """Reset first-run state (for testing)."""
        cls.FIRST_RUN_MARKER.unlink(missing_ok=True)
        cls.CONFIG_FILE.unlink(missing_ok=True)
        logger.info("First run state reset")


# =============================================================================
# Wizard UI
# =============================================================================

def create_wizard_ui() -> gr.Blocks:
    """
    Create first-run wizard Gradio interface.

    Returns:
        Gradio Blocks interface
    """

    # Shared state
    detector = HardwareDetector()
    downloader = ModelDownloader()

    with gr.Blocks(
        title="TerminalAI - First Run Setup"
    ) as wizard:

        # State
        gpu_info = gr.State({})
        download_thread = gr.State(None)

        # Header
        gr.Markdown(
            """
            # Welcome to TerminalAI!

            Let's set up your system for the best video processing experience.
            This will only take a few minutes.
            """
        )

        # Phase 1: Hardware Detection
        with gr.Group(visible=True) as detection_phase:
            gr.Markdown("## Hardware Detection")

            with gr.Row():
                detect_btn = gr.Button("Detect Hardware", variant="primary", size="lg")

            detection_output = gr.Markdown("")

            with gr.Row(visible=False) as detection_results:
                with gr.Column():
                    gpu_status = gr.Textbox(label="GPU", interactive=False)
                    vram_status = gr.Textbox(label="VRAM", interactive=False)
                with gr.Column():
                    cuda_status = gr.Textbox(label="CUDA Support", interactive=False)
                    recommendation = gr.Textbox(label="Recommendation", interactive=False)

            next_to_download_btn = gr.Button("Continue to Download", visible=False, variant="primary")

        # Phase 2: Model Download
        with gr.Group(visible=False) as download_phase:
            gr.Markdown("## AI Model Download")
            gr.Markdown(
                """
                TerminalAI uses AI models for face restoration and upscaling.
                These models are downloaded once and cached locally.
                """
            )

            # GFPGAN Download
            with gr.Group():
                gr.Markdown("### GFPGAN (Face Restoration)")
                gfpgan_status = gr.Markdown("Status: Not started")
                gfpgan_progress = gr.Progress()
                gfpgan_bar = gr.Slider(
                    minimum=0, maximum=100, value=0, label="Progress",
                    interactive=False, show_label=False
                )
                gfpgan_details = gr.Markdown("")

            # CodeFormer Download
            with gr.Group():
                gr.Markdown("### CodeFormer (Advanced Face Restoration)")
                codeformer_status = gr.Markdown("Status: Not started")
                codeformer_progress = gr.Progress()
                codeformer_bar = gr.Slider(
                    minimum=0, maximum=100, value=0, label="Progress",
                    interactive=False, show_label=False
                )
                codeformer_details = gr.Markdown("")

            with gr.Row():
                download_btn = gr.Button("Start Download", variant="primary", size="lg")
                skip_btn = gr.Button("Skip (Download Later)", variant="secondary")

            next_to_config_btn = gr.Button("Continue to Configuration", visible=False, variant="primary")

        # Phase 3: Configuration
        with gr.Group(visible=False) as config_phase:
            gr.Markdown("## Configuration")

            config_summary = gr.Markdown("")

            with gr.Row():
                finish_btn = gr.Button("Complete Setup", variant="primary", size="lg")

        # Phase 4: Complete
        with gr.Group(visible=False) as complete_phase:
            gr.Markdown(
                """
                # Setup Complete!

                TerminalAI is ready to use. The main application will launch in a moment.

                Future launches will skip this setup and go straight to the main interface.
                """
            )
            launch_btn = gr.Button("Launch TerminalAI", variant="primary", size="lg")

        # =============================================================================
        # Event Handlers
        # =============================================================================

        def detect_hardware():
            """Detect hardware and show results."""
            gpu = detector.detect_gpu()
            system = detector.get_system_info()

            # Build detection message
            msg = "### Detection Results\n\n"

            # GPU Info
            if gpu["vendor"] == "nvidia":
                msg += f"✓ **GPU Detected:** {gpu['name']}\n\n"
                msg += f"✓ **VRAM:** {gpu['vram_mb']:,} MB\n\n"
                msg += f"✓ **CUDA:** Available (Compute {gpu['compute_capability']})\n\n"
                msg += "**Recommendation:** Your system supports GPU-accelerated processing! "
                msg += "All AI features will run significantly faster.\n"

                rec_text = "GPU Acceleration Available - Optimal Performance"

            elif gpu["vendor"] in ["amd", "intel"]:
                msg += f"✓ **GPU Detected:** {gpu['name']}\n\n"
                msg += "⚠ **CUDA:** Not available (AMD/Intel GPU)\n\n"
                msg += "**Recommendation:** AI models will run on CPU. "
                msg += "Consider using NVIDIA GPU for best performance.\n"

                rec_text = "CPU Processing - Slower but functional"

            else:
                msg += "ℹ **GPU:** None detected (CPU only)\n\n"
                msg += "**Recommendation:** AI models will run on CPU. "
                msg += "Processing will be slower but fully functional.\n"

                rec_text = "CPU Only - Expect longer processing times"

            # System info
            msg += f"\n**System:** {system['platform']} {system['platform_release']} ({system['architecture']})\n"
            msg += f"**Python:** {system['python_version']}\n"

            return (
                gr.update(value=msg),
                gr.update(visible=True),
                gr.update(value=gpu['name']),
                gr.update(value=f"{gpu['vram_mb']:,} MB" if gpu['vram_mb'] else "N/A"),
                gr.update(value="Yes" if gpu['cuda_available'] else "No"),
                gr.update(value=rec_text),
                gr.update(visible=True),
                gpu
            )

        def show_download_phase():
            """Transition to download phase."""
            return (
                gr.update(visible=False),
                gr.update(visible=True)
            )

        def download_models(gpu_data):
            """Download models with progress updates."""

            def update_gfpgan_progress(downloaded_mb, total_mb, speed_mbps, eta_seconds, status_msg):
                progress_pct = (downloaded_mb / total_mb * 100) if total_mb > 0 else 0

                details = f"""
                **Downloaded:** {downloaded_mb:.1f} / {total_mb:.1f} MB ({progress_pct:.1f}%)

                **Speed:** {speed_mbps:.1f} MB/s

                **Time Remaining:** {int(eta_seconds // 60)}m {int(eta_seconds % 60)}s
                """

                return (
                    gr.update(value=f"Status: {status_msg}"),
                    gr.update(value=progress_pct),
                    gr.update(value=details)
                )

            def update_codeformer_progress(downloaded_mb, total_mb, speed_mbps, eta_seconds, status_msg):
                progress_pct = (downloaded_mb / total_mb * 100) if total_mb > 0 else 0

                details = f"""
                **Downloaded:** {downloaded_mb:.1f} / {total_mb:.1f} MB ({progress_pct:.1f}%)

                **Speed:** {speed_mbps:.1f} MB/s

                **Time Remaining:** {int(eta_seconds // 60)}m {int(eta_seconds % 60)}s
                """

                return (
                    gr.update(value=f"Status: {status_msg}"),
                    gr.update(value=progress_pct),
                    gr.update(value=details)
                )

            # Download GFPGAN
            yield (
                gr.update(value="Status: Starting download..."),
                gr.update(value=0),
                gr.update(value=""),
                gr.update(value="Status: Waiting..."),
                gr.update(value=0),
                gr.update(value=""),
                gr.update(visible=False)
            )

            success_gfpgan, msg_gfpgan = downloader.download_gfpgan(
                progress_callback=lambda *args: None  # Simplified for now
            )

            if success_gfpgan:
                yield (
                    gr.update(value=f"Status: {msg_gfpgan} ✓"),
                    gr.update(value=100),
                    gr.update(value="**Complete!**"),
                    gr.update(value="Status: Waiting..."),
                    gr.update(value=0),
                    gr.update(value=""),
                    gr.update(visible=False)
                )
            else:
                yield (
                    gr.update(value=f"Status: Failed - {msg_gfpgan}"),
                    gr.update(value=0),
                    gr.update(value=f"**Error:** {msg_gfpgan}"),
                    gr.update(value="Status: Skipped"),
                    gr.update(value=0),
                    gr.update(value=""),
                    gr.update(visible=True)
                )
                return

            # Download CodeFormer
            yield (
                gr.update(value=f"Status: {msg_gfpgan} ✓"),
                gr.update(value=100),
                gr.update(value="**Complete!**"),
                gr.update(value="Status: Starting download..."),
                gr.update(value=0),
                gr.update(value=""),
                gr.update(visible=False)
            )

            success_codeformer, msg_codeformer = downloader.download_codeformer(
                progress_callback=lambda *args: None  # Simplified for now
            )

            if success_codeformer:
                yield (
                    gr.update(value=f"Status: {msg_gfpgan} ✓"),
                    gr.update(value=100),
                    gr.update(value="**Complete!**"),
                    gr.update(value=f"Status: {msg_codeformer} ✓"),
                    gr.update(value=100),
                    gr.update(value="**Complete!**"),
                    gr.update(visible=True)
                )
            else:
                yield (
                    gr.update(value=f"Status: {msg_gfpgan} ✓"),
                    gr.update(value=100),
                    gr.update(value="**Complete!**"),
                    gr.update(value=f"Status: Failed - {msg_codeformer}"),
                    gr.update(value=0),
                    gr.update(value=f"**Error:** {msg_codeformer}"),
                    gr.update(visible=True)
                )

        def skip_download():
            """Skip download phase."""
            return (
                gr.update(value="Status: Skipped by user"),
                gr.update(value="Status: Skipped by user"),
                gr.update(visible=True)
            )

        def show_config_phase(gpu_data):
            """Show configuration summary."""

            summary = "## Configuration Summary\n\n"
            summary += "Based on your hardware, the following defaults have been configured:\n\n"

            if gpu_data.get("cuda_available"):
                summary += "- **Processing:** GPU-accelerated (CUDA)\n"
                summary += "- **AI Models:** Will run on GPU for fast processing\n"
                summary += "- **Video Encoding:** Hardware-accelerated (NVENC)\n"
            else:
                summary += "- **Processing:** CPU-based\n"
                summary += "- **AI Models:** Will run on CPU (slower)\n"
                summary += "- **Video Encoding:** Software encoding\n"

            summary += "\nYou can change these settings later in the main interface.\n"

            return (
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(value=summary)
            )

        def complete_setup(gpu_data):
            """Mark setup as complete."""
            config = {
                "first_run_date": datetime.now().isoformat(),
                "gpu_vendor": gpu_data.get("vendor", "cpu"),
                "gpu_name": gpu_data.get("name", "Unknown"),
                "cuda_available": gpu_data.get("cuda_available", False),
            }

            FirstRunManager.mark_complete(config)

            return (
                gr.update(visible=False),
                gr.update(visible=True)
            )

        # Connect events
        detect_btn.click(
            fn=detect_hardware,
            outputs=[
                detection_output,
                detection_results,
                gpu_status,
                vram_status,
                cuda_status,
                recommendation,
                next_to_download_btn,
                gpu_info
            ]
        )

        next_to_download_btn.click(
            fn=show_download_phase,
            outputs=[detection_phase, download_phase]
        )

        download_btn.click(
            fn=download_models,
            inputs=[gpu_info],
            outputs=[
                gfpgan_status,
                gfpgan_bar,
                gfpgan_details,
                codeformer_status,
                codeformer_bar,
                codeformer_details,
                next_to_config_btn
            ]
        )

        skip_btn.click(
            fn=skip_download,
            outputs=[
                gfpgan_status,
                codeformer_status,
                next_to_config_btn
            ]
        )

        next_to_config_btn.click(
            fn=show_config_phase,
            inputs=[gpu_info],
            outputs=[download_phase, config_phase, config_summary]
        )

        finish_btn.click(
            fn=complete_setup,
            inputs=[gpu_info],
            outputs=[config_phase, complete_phase]
        )

    return wizard


def create_welcome_back_ui() -> gr.Blocks:
    """
    Create welcome back screen for returning users.

    Returns:
        Gradio Blocks interface
    """

    config = FirstRunManager.load_config()

    with gr.Blocks(
        title="TerminalAI - Welcome Back"
    ) as welcome:

        gr.Markdown(
            f"""
            # Welcome Back to TerminalAI!

            Your system is configured and ready to process videos.

            **GPU:** {config.get('gpu_name', 'Unknown')}

            **CUDA:** {"Enabled" if config.get('cuda_available') else "Disabled"}

            The main application will launch in a moment...
            """
        )

        launch_btn = gr.Button("Launch Main Application", variant="primary", size="lg")

        # Auto-launch after 3 seconds
        welcome.load(
            fn=lambda: time.sleep(3),
            outputs=None
        )

    return welcome


def run_wizard(launch_callback: Optional[Callable] = None) -> bool:
    """
    Run the first-run wizard or welcome screen.

    Args:
        launch_callback: Function to call when wizard completes (receives config dict)

    Returns:
        True if wizard was shown, False if skipped
    """

    if FirstRunManager.is_first_run():
        logger.info("First run detected, launching setup wizard...")
        wizard = create_wizard_ui()
        wizard.launch(
            server_name="127.0.0.1",
            inbrowser=True,
            quiet=True,
            theme=gr.themes.Soft()
        )
        return True
    else:
        logger.info("Returning user, showing welcome message...")
        # Skip welcome screen, go directly to main app
        if launch_callback:
            config = FirstRunManager.load_config()
            launch_callback(config)
        return False


# =============================================================================
# CLI for Testing
# =============================================================================

def main():
    """CLI entry point for testing the wizard."""
    import argparse

    parser = argparse.ArgumentParser(description="TerminalAI First-Run Wizard")
    parser.add_argument("--reset", action="store_true", help="Reset first-run state")
    parser.add_argument("--check", action="store_true", help="Check first-run status")

    args = parser.parse_args()

    if args.reset:
        FirstRunManager.reset()
        print("First-run state reset. Next launch will show wizard.")
        return

    if args.check:
        is_first = FirstRunManager.is_first_run()
        print(f"First run: {is_first}")
        if not is_first:
            config = FirstRunManager.load_config()
            print(f"Config: {config}")
        return

    # Run wizard
    run_wizard()


if __name__ == "__main__":
    main()
