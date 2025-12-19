#!/usr/bin/env python3
"""
Audio Processing Module for VHS Upscaler
=========================================
Provides audio enhancement and surround upmixing capabilities.

Features:
- FFmpeg-based audio enhancement (noise reduction, normalization, EQ)
- DeepFilterNet AI-based denoising for superior speech clarity
- Surround upmixing (stereo → 5.1, 7.1)
- Demucs AI stem separation for intelligent upmixing
- Multiple output formats (AAC, AC3/EAC3, DTS)

All options are FREE and open source.
"""

import json
import logging
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Configuration
# =============================================================================

class AudioFormat(Enum):
    """Output audio formats."""
    AAC = "aac"           # Standard stereo/5.1
    AC3 = "ac3"           # Dolby Digital 5.1
    EAC3 = "eac3"         # Dolby Digital Plus 5.1/7.1
    DTS = "dts"           # DTS 5.1
    FLAC = "flac"         # Lossless
    PCM = "pcm_s16le"     # Uncompressed


class AudioChannelLayout(Enum):
    """Audio channel layouts."""
    STEREO = "stereo"           # 2.0
    SURROUND_51 = "5.1"         # 5.1 surround
    SURROUND_71 = "7.1"         # 7.1 surround
    MONO = "mono"               # 1.0
    ORIGINAL = "original"       # Keep original


class AudioEnhanceMode(Enum):
    """Audio enhancement presets."""
    NONE = "none"               # No enhancement
    LIGHT = "light"             # Light cleanup
    MODERATE = "moderate"       # Moderate enhancement
    AGGRESSIVE = "aggressive"   # Heavy noise reduction
    VOICE = "voice"             # Optimized for speech/dialogue
    MUSIC = "music"             # Optimized for music
    DEEPFILTERNET = "deepfilternet"  # AI-based denoising (DeepFilterNet)


class UpmixMode(Enum):
    """Surround upmix algorithms."""
    NONE = "none"               # No upmix (keep original)
    SIMPLE = "simple"           # FFmpeg pan filter
    SURROUND = "surround"       # FFmpeg surround filter
    PROLOGIC = "prologic"       # Dolby Pro Logic II decode
    DEMUCS = "demucs"           # AI stem separation upmix


@dataclass
class AudioConfig:
    """Audio processing configuration."""
    # Enhancement settings
    enhance_mode: AudioEnhanceMode = AudioEnhanceMode.NONE
    normalize: bool = True
    target_loudness: float = -14.0  # LUFS (streaming standard)

    # Upmix settings
    upmix_mode: UpmixMode = UpmixMode.NONE
    output_layout: AudioChannelLayout = AudioChannelLayout.ORIGINAL

    # Output settings
    output_format: AudioFormat = AudioFormat.AAC
    output_bitrate: str = "192k"  # Per channel for surround
    sample_rate: int = 48000

    # Demucs settings
    demucs_model: str = "htdemucs"  # htdemucs, htdemucs_ft, mdx_extra
    demucs_device: str = "auto"     # auto, cuda, cpu

    # AudioSR settings (AI-based audio upsampling)
    use_audiosr: bool = False        # Enable AI-based upsampling to 48kHz
    audiosr_model: str = "basic"     # basic, speech, music
    audiosr_device: str = "auto"     # auto, cuda, cpu

    # Advanced
    lfe_crossover: int = 120        # LFE crossover frequency (Hz)
    center_mix_level: float = 0.707 # -3dB for center channel


# =============================================================================
# Audio Processor
# =============================================================================

class AudioProcessor:
    """
    Handles all audio processing operations.

    Uses FFmpeg for basic operations, DeepFilterNet for AI-powered denoising,
    and Demucs for AI-powered stem separation.
    """

    def __init__(self, config: AudioConfig = None, ffmpeg_path: str = "ffmpeg"):
        self.config = config or AudioConfig()
        self.ffmpeg_path = ffmpeg_path
        self.demucs_available = self._check_demucs()
        self.deepfilternet_available = self._check_deepfilternet()
        self.audiosr_available = self._check_audiosr()

    def _check_demucs(self) -> bool:
        """
        Check if Demucs is available for AI stem separation.

        Returns:
            True if Demucs is installed and importable, False otherwise
        """
        try:
            result = subprocess.run(
                ["python3", "-c", "import demucs; print('ok')"],
                capture_output=True, text=True, timeout=10
            )
            is_available = "ok" in result.stdout
            if is_available:
                logger.debug("Demucs is available")
            return is_available
        except subprocess.TimeoutExpired:
            logger.debug("Demucs check timed out")
            return False
        except Exception as e:
            logger.debug(f"Demucs check failed: {e}")
            return False

    def _check_deepfilternet(self) -> bool:
        """
        Check if DeepFilterNet is available for AI denoising.

        Returns:
            True if DeepFilterNet is installed and importable, False otherwise
        """
        try:
            import df  # DeepFilterNet package  # noqa: F401
            logger.debug("DeepFilterNet is available")
            return True
        except ImportError:
            logger.debug("DeepFilterNet not available")
            return False

    def _check_audiosr(self) -> bool:
        """
        Check if AudioSR is available for AI upsampling.

        Returns:
            True if AudioSR is installed and importable, False otherwise
        """
        try:
            import audiosr  # noqa: F401
            logger.debug("AudioSR is available")
            return True
        except ImportError:
            logger.debug("AudioSR not available")
            return False

    def get_audio_info(self, input_path: Path) -> Dict[str, Any]:
        """
        Get audio stream information using ffprobe.

        Args:
            input_path: Path to audio/video file

        Returns:
            Dictionary containing audio stream metadata (codec, channels, sample rate, etc.)
            Returns default values if probe fails
        """
        cmd = [
            "ffprobe", "-v", "quiet",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_name,channels,channel_layout,sample_rate,bit_rate",
            "-of", "json",
            str(input_path)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
            data = json.loads(result.stdout)
            stream = data.get("streams", [{}])[0]
            return {
                "codec": stream.get("codec_name", "unknown"),
                "channels": int(stream.get("channels", 2)),
                "channel_layout": stream.get("channel_layout", "stereo"),
                "sample_rate": int(stream.get("sample_rate", 48000)),
                "bitrate": stream.get("bit_rate", "unknown"),
            }
        except subprocess.TimeoutExpired:
            logger.warning(f"Audio info probe timed out for: {input_path}")
            return {"channels": 2, "codec": "unknown", "sample_rate": 48000}
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse ffprobe JSON: {e}")
            return {"channels": 2, "codec": "unknown", "sample_rate": 48000}
        except subprocess.CalledProcessError as e:
            logger.warning(f"ffprobe failed: {e}")
            return {"channels": 2, "codec": "unknown", "sample_rate": 48000}
        except Exception as e:
            logger.warning(f"Unexpected error getting audio info: {e}", exc_info=True)
            return {"channels": 2, "codec": "unknown", "sample_rate": 48000}

    def process(self, input_path: Path, output_path: Path,
                video_path: Optional[Path] = None) -> Path:
        """
        Process audio with enhancement and/or upmixing.

        Args:
            input_path: Input audio/video file
            output_path: Output audio file
            video_path: Optional video to mux audio into

        Returns:
            Path to processed audio (or muxed video if video_path provided)
        """
        temp_dir = Path(tempfile.mkdtemp(prefix="audio_proc_"))

        try:
            # Get input info
            audio_info = self.get_audio_info(input_path)
            logger.info(f"Input audio: {audio_info['channels']}ch {audio_info['codec']}")

            current_audio = input_path

            # Step 1: Extract audio if from video
            if input_path.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov']:
                extracted = temp_dir / "extracted.wav"
                self._extract_audio(input_path, extracted)
                current_audio = extracted

            # Step 2: Apply enhancement
            if self.config.enhance_mode != AudioEnhanceMode.NONE:
                enhanced = temp_dir / "enhanced.wav"
                self._enhance_audio(current_audio, enhanced)
                current_audio = enhanced

            # Step 2.5: Apply AudioSR upsampling if enabled (before upmixing)
            if self.config.use_audiosr and self.audiosr_available:
                # Check if current sample rate is below 48kHz
                current_info = self.get_audio_info(current_audio)
                if current_info['sample_rate'] < 48000:
                    upsampled = temp_dir / "audiosr_upsampled.wav"
                    self._upsample_audiosr(current_audio, upsampled)
                    current_audio = upsampled
                else:
                    logger.info(f"Audio already at {current_info['sample_rate']}Hz, skipping AudioSR")

            # Step 3: Apply upmix
            if (self.config.upmix_mode != UpmixMode.NONE and
                self.config.output_layout != AudioChannelLayout.ORIGINAL):

                if self.config.upmix_mode == UpmixMode.DEMUCS and self.demucs_available:
                    upmixed = temp_dir / "upmixed.wav"
                    self._upmix_with_demucs(current_audio, upmixed, temp_dir)
                    current_audio = upmixed
                else:
                    upmixed = temp_dir / "upmixed.wav"
                    self._upmix_with_ffmpeg(current_audio, upmixed)
                    current_audio = upmixed

            # Step 4: Normalize if enabled
            if self.config.normalize:
                normalized = temp_dir / "normalized.wav"
                self._normalize_audio(current_audio, normalized)
                current_audio = normalized

            # Step 5: Encode to output format
            self._encode_audio(current_audio, output_path)

            # Step 6: Mux with video if provided
            if video_path:
                muxed = output_path.parent / f"{output_path.stem}_muxed{video_path.suffix}"
                self._mux_audio_video(video_path, output_path, muxed)
                return muxed

            return output_path

        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _extract_audio(self, input_path: Path, output_path: Path) -> None:
        """
        Extract audio from video file.

        Args:
            input_path: Input video file
            output_path: Output audio file (WAV)

        Raises:
            subprocess.CalledProcessError: If ffmpeg extraction fails
        """
        cmd = [
            self.ffmpeg_path, "-y",
            "-i", str(input_path),
            "-vn",  # No video
            "-acodec", "pcm_s16le",
            "-ar", str(self.config.sample_rate),
            str(output_path)
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=300)
            logger.debug(f"Extracted audio to {output_path}")
        except subprocess.TimeoutExpired:
            logger.error(f"Audio extraction timed out after 5 minutes: {input_path}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio extraction failed: {e.stderr}")
            raise

    def _enhance_audio(self, input_path: Path, output_path: Path) -> None:
        """
        Apply audio enhancement filters.

        Args:
            input_path: Input audio file
            output_path: Output enhanced audio file

        Uses DeepFilterNet for AI denoising if available, otherwise falls back
        to FFmpeg-based enhancement based on the selected mode.
        """
        # Handle DeepFilterNet separately (not FFmpeg-based)
        if self.config.enhance_mode == AudioEnhanceMode.DEEPFILTERNET:
            if self.deepfilternet_available:
                self._denoise_deepfilternet(input_path, output_path)
                return
            else:
                logger.warning(
                    "DeepFilterNet not available, falling back to aggressive FFmpeg denoise"
                )
                # Fallback to aggressive mode
                self.config.enhance_mode = AudioEnhanceMode.AGGRESSIVE

        filters = []

        if self.config.enhance_mode == AudioEnhanceMode.LIGHT:
            # Light cleanup - gentle highpass and slight compression
            filters = [
                "highpass=f=80",
                "lowpass=f=15000",
                "acompressor=threshold=-20dB:ratio=2:attack=20:release=250",
            ]

        elif self.config.enhance_mode == AudioEnhanceMode.MODERATE:
            # Moderate - noise reduction + compression
            filters = [
                "highpass=f=100",
                "lowpass=f=14000",
                "afftdn=nf=-20",  # FFT-based noise reduction
                "acompressor=threshold=-18dB:ratio=3:attack=10:release=200",
                "equalizer=f=3000:t=q:w=1:g=2",  # Slight presence boost
            ]

        elif self.config.enhance_mode == AudioEnhanceMode.AGGRESSIVE:
            # Aggressive noise reduction
            filters = [
                "highpass=f=120",
                "lowpass=f=12000",
                "afftdn=nf=-15:nt=w",  # Stronger noise reduction
                "anlmdn=s=7:p=0.002:r=0.002",  # Non-local means denoising
                "acompressor=threshold=-15dB:ratio=4:attack=5:release=150",
            ]

        elif self.config.enhance_mode == AudioEnhanceMode.VOICE:
            # Optimized for speech/dialogue
            filters = [
                "highpass=f=100",
                "lowpass=f=8000",
                "afftdn=nf=-18",
                "equalizer=f=200:t=q:w=1:g=-3",   # Reduce muddiness
                "equalizer=f=2500:t=q:w=1:g=4",   # Presence/clarity
                "equalizer=f=5000:t=q:w=1:g=2",   # Air
                "acompressor=threshold=-20dB:ratio=3:attack=5:release=100",
                "alimiter=limit=0.95",
            ]

        elif self.config.enhance_mode == AudioEnhanceMode.MUSIC:
            # Optimized for music - preserve dynamics
            filters = [
                "highpass=f=30",
                "afftdn=nf=-25",  # Light noise reduction
                "acompressor=threshold=-24dB:ratio=2:attack=50:release=500",
            ]

        if not filters:
            # Just copy if no enhancement
            shutil.copy(input_path, output_path)
            return

        filter_str = ",".join(filters)
        cmd = [
            self.ffmpeg_path, "-y",
            "-i", str(input_path),
            "-af", filter_str,
            "-acodec", "pcm_s16le",
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        logger.info(f"Applied {self.config.enhance_mode.value} enhancement")

    def _denoise_deepfilternet(self, input_path: Path, output_path: Path):
        """
        Deep learning-based audio denoising using DeepFilterNet.

        DeepFilterNet provides superior noise reduction compared to traditional
        FFmpeg filters, especially for speech clarity in noisy environments.

        Args:
            input_path: Input audio file (WAV format expected)
            output_path: Output denoised audio file
        """
        try:
            import torch
            import torchaudio
            from df.enhance import enhance, init_df
            from df.io import resample

            logger.info("Running DeepFilterNet AI denoising...")

            # Initialize DeepFilterNet model
            model, df_state, _ = init_df()

            # Load audio
            audio, sr = torchaudio.load(str(input_path))

            # DeepFilterNet expects 48kHz sample rate
            if sr != df_state.sr():
                logger.debug(f"Resampling from {sr}Hz to {df_state.sr()}Hz")
                audio = resample(audio, sr, df_state.sr())
                sr = df_state.sr()

            # Process audio - DeepFilterNet works on mono or stereo
            # If stereo, process each channel
            if audio.shape[0] == 1:
                # Mono processing
                enhanced = enhance(model, df_state, audio)
            elif audio.shape[0] == 2:
                # Stereo - process each channel separately then recombine
                left_enhanced = enhance(model, df_state, audio[0:1, :])
                right_enhanced = enhance(model, df_state, audio[1:2, :])
                enhanced = torch.cat([left_enhanced, right_enhanced], dim=0)
            else:
                # Multi-channel - process first 2 channels
                logger.warning(f"Multi-channel audio detected ({audio.shape[0]} channels), "
                             "processing only first 2 channels")
                left_enhanced = enhance(model, df_state, audio[0:1, :])
                right_enhanced = enhance(model, df_state, audio[1:2, :])
                enhanced = torch.cat([left_enhanced, right_enhanced], dim=0)

            # Resample back to target sample rate if needed
            if sr != self.config.sample_rate:
                enhanced = resample(enhanced, sr, self.config.sample_rate)

            # Save enhanced audio
            torchaudio.save(
                str(output_path),
                enhanced,
                self.config.sample_rate,
                encoding="PCM_S",
                bits_per_sample=16
            )

            logger.info("DeepFilterNet denoising completed successfully")

        except ImportError as e:
            logger.error(f"DeepFilterNet dependencies not available: {e}")
            logger.info("Install with: pip install deepfilternet")
            raise
        except Exception as e:
            logger.error(f"DeepFilterNet processing failed: {e}")
            logger.warning("Falling back to FFmpeg aggressive denoise")
            # Fallback to FFmpeg-based denoising
            self.config.enhance_mode = AudioEnhanceMode.AGGRESSIVE
            self._enhance_audio(input_path, output_path)

    def _upsample_audiosr(self, input_path: Path, output_path: Path, target_sr: int = 48000):
        """
        AI-based audio upsampling using AudioSR.

        AudioSR uses deep learning to intelligently upsample low-quality audio
        to higher sample rates, recovering lost high-frequency content and
        improving overall audio fidelity.

        Args:
            input_path: Input audio file (WAV format)
            output_path: Output upsampled audio file
            target_sr: Target sampling rate (default: 48000 Hz)

        Returns:
            Path to upsampled audio file
        """
        try:
            import torch
            import torchaudio
            from audiosr import AudioSR, build_audiosuperresolution

            logger.info(f"Running AudioSR AI upsampling to {target_sr}Hz...")

            # Determine device
            device = self.config.audiosr_device
            if device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"

            logger.debug(f"Using AudioSR device: {device}")

            # Initialize AudioSR model
            # Models: basic (general), speech (optimized for voice), music (optimized for music)
            model_name = self.config.audiosr_model
            if model_name not in ["basic", "speech", "music"]:
                logger.warning(f"Unknown AudioSR model '{model_name}', using 'basic'")
                model_name = "basic"

            # Build the model
            audiosr_model = build_audiosuperresolution(
                model_name=model_name,
                device=device
            )

            # Load input audio
            audio, sr = torchaudio.load(str(input_path))
            logger.debug(f"Loaded audio: {audio.shape}, sample rate: {sr}Hz")

            # AudioSR expects mono or stereo
            # If more channels, convert to stereo
            if audio.shape[0] > 2:
                logger.warning(f"Audio has {audio.shape[0]} channels, converting to stereo")
                audio = audio[:2, :]  # Take first 2 channels

            # Move to device
            audio = audio.to(device)

            # Upsample with AudioSR
            with torch.no_grad():
                # AudioSR processes in chunks for memory efficiency
                upsampled_audio = audiosr_model(audio, sr, target_sr)

            # Move back to CPU for saving
            upsampled_audio = upsampled_audio.cpu()

            # Save upsampled audio
            torchaudio.save(
                str(output_path),
                upsampled_audio,
                target_sr,
                encoding="PCM_S",
                bits_per_sample=16
            )

            logger.info(f"AudioSR upsampling completed: {sr}Hz → {target_sr}Hz")
            return str(output_path)

        except ImportError as e:
            logger.warning(f"AudioSR not available: {e}")
            logger.info("Install with: pip install audiosr")
            logger.info("Falling back to FFmpeg resampling")
            return self._resample_ffmpeg(input_path, output_path, target_sr)

        except Exception as e:
            logger.error(f"AudioSR processing failed: {e}")
            logger.warning("Falling back to FFmpeg resampling")
            return self._resample_ffmpeg(input_path, output_path, target_sr)

    def _resample_ffmpeg(self, input_path: Path, output_path: Path, target_sr: int = 48000) -> str:
        """
        Fallback resampling using FFmpeg.

        Args:
            input_path: Input audio file
            output_path: Output resampled audio file
            target_sr: Target sampling rate

        Returns:
            Path to resampled audio file
        """
        logger.info(f"Resampling to {target_sr}Hz using FFmpeg")

        cmd = [
            self.ffmpeg_path, "-y",
            "-i", str(input_path),
            "-ar", str(target_sr),
            "-acodec", "pcm_s16le",
            str(output_path)
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            logger.debug(f"FFmpeg resampling completed")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg resampling failed: {e}")
            # If resampling fails, just copy the file
            import shutil
            shutil.copy(input_path, output_path)
            return str(output_path)

    def _upmix_with_ffmpeg(self, input_path: Path, output_path: Path):
        """Upmix stereo to surround using FFmpeg filters."""
        layout = self.config.output_layout
        mode = self.config.upmix_mode

        if layout == AudioChannelLayout.SURROUND_51:
            if mode == UpmixMode.SURROUND:
                # Use FFmpeg surround filter
                filter_str = "surround=chl_out=5.1:fc_in=0.6:lfe_in=0.5"
            elif mode == UpmixMode.PROLOGIC:
                # Dolby Pro Logic II decode simulation
                filter_str = (
                    "pan=5.1|"
                    "FL=0.5*FL+0.25*FC|"
                    "FR=0.5*FR+0.25*FC|"
                    "FC=0.5*FL+0.5*FR|"
                    "LFE=0.5*FL+0.5*FR|"
                    "BL=0.5*FL-0.25*FR|"
                    "BR=0.5*FR-0.25*FL"
                )
            else:  # SIMPLE
                # Simple channel mapping with LFE extraction
                filter_str = (
                    "pan=5.1|"
                    "FL=FL|"
                    "FR=FR|"
                    "FC=0.5*FL+0.5*FR|"
                    "LFE=0.5*FL+0.5*FR|"
                    "BL=0.7*FL|"
                    "BR=0.7*FR,"
                    f"lowpass=f={self.config.lfe_crossover}:c=LFE"
                )
            channels = 6
            ch_layout = "5.1"

        elif layout == AudioChannelLayout.SURROUND_71:
            # 7.1 upmix
            filter_str = (
                "pan=7.1|"
                "FL=FL|"
                "FR=FR|"
                "FC=0.5*FL+0.5*FR|"
                "LFE=0.5*FL+0.5*FR|"
                "BL=0.6*FL|"
                "BR=0.6*FR|"
                "SL=0.5*FL+0.2*FR|"
                "SR=0.5*FR+0.2*FL,"
                f"lowpass=f={self.config.lfe_crossover}:c=LFE"
            )
            channels = 8
            ch_layout = "7.1"
        else:
            # Keep stereo
            shutil.copy(input_path, output_path)
            return

        cmd = [
            self.ffmpeg_path, "-y",
            "-i", str(input_path),
            "-af", filter_str,
            "-ac", str(channels),
            "-channel_layout", ch_layout,
            "-acodec", "pcm_s16le",
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        logger.info(f"Upmixed to {ch_layout} using {mode.value}")

    def _upmix_with_demucs(self, input_path: Path, output_path: Path, temp_dir: Path):
        """
        Upmix using Demucs AI stem separation.

        Separates audio into stems (vocals, drums, bass, other) then
        maps them intelligently to surround channels.
        """
        stems_dir = temp_dir / "stems"
        stems_dir.mkdir(exist_ok=True)

        # Run Demucs separation
        logger.info("Running Demucs stem separation...")
        device = self.config.demucs_device
        if device == "auto":
            device = "cuda" if shutil.which("nvidia-smi") else "cpu"

        cmd = [
            "python3", "-m", "demucs",
            "-n", self.config.demucs_model,
            "-d", device,
            "-o", str(stems_dir),
            str(input_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning(f"Demucs failed: {result.stderr}")
            # Fallback to FFmpeg upmix
            self._upmix_with_ffmpeg(input_path, output_path)
            return

        # Find separated stems
        stem_name = input_path.stem
        model_dir = stems_dir / self.config.demucs_model / stem_name

        vocals = model_dir / "vocals.wav"
        drums = model_dir / "drums.wav"
        bass = model_dir / "bass.wav"
        other = model_dir / "other.wav"

        if not all(p.exists() for p in [vocals, drums, bass, other]):
            logger.warning("Demucs stems not found, falling back to FFmpeg")
            self._upmix_with_ffmpeg(input_path, output_path)
            return

        # Create surround mix from stems
        layout = self.config.output_layout

        if layout == AudioChannelLayout.SURROUND_51:
            # Intelligent 5.1 mapping:
            # - Vocals → Center (mostly) + slight L/R
            # - Drums → L/R + slight surrounds
            # - Bass → LFE + Front L/R
            # - Other → L/R + Surrounds

            filter_complex = (
                f"[0:a]pan=stereo|FL=FL|FR=FR[voc];"
                f"[1:a]aformat=channel_layouts=stereo[drm];"
                f"[2:a]aformat=channel_layouts=stereo[bas];"
                f"[3:a]aformat=channel_layouts=stereo[oth];"
                # Create LFE from bass
                f"[bas]lowpass=f={self.config.lfe_crossover}[lfe];"
                # Create center from vocals
                f"[voc]pan=mono|c0=0.5*FL+0.5*FR[ctr];"
                # Mix to 5.1
                f"[drm][oth]amix=inputs=2[lr];"
                f"[lr][voc]amix=inputs=2:weights=0.7 0.3[front];"
                f"[oth]pan=stereo|FL=0.5*FL|FR=0.5*FR[rear];"
                # Final 5.1 assembly
                f"[front][ctr][lfe][rear]amerge=inputs=4,"
                f"pan=5.1|FL=c0|FR=c1|FC=c2|LFE=c3|BL=c4|BR=c5[out]"
            )

            cmd = [
                self.ffmpeg_path, "-y",
                "-i", str(vocals),
                "-i", str(drums),
                "-i", str(bass),
                "-i", str(other),
                "-filter_complex", filter_complex,
                "-map", "[out]",
                "-ac", "6",
                "-acodec", "pcm_s16le",
                str(output_path)
            ]
        else:
            # For other layouts, use simpler approach
            self._upmix_with_ffmpeg(input_path, output_path)
            return

        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=300)
            logger.info("Created 5.1 upmix from Demucs stems")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Demucs mixing failed: {e}, falling back to FFmpeg")
            self._upmix_with_ffmpeg(input_path, output_path)
        except subprocess.TimeoutExpired:
            logger.warning("Demucs mixing timed out, falling back to FFmpeg")
            self._upmix_with_ffmpeg(input_path, output_path)

    def _normalize_audio(self, input_path: Path, output_path: Path):
        """Normalize audio to target loudness (EBU R128)."""
        # Two-pass loudnorm for accurate normalization
        # Pass 1: Measure
        measure_cmd = [
            self.ffmpeg_path, "-y",
            "-i", str(input_path),
            "-af", f"loudnorm=I={self.config.target_loudness}:TP=-1.5:LRA=11:print_format=json",
            "-f", "null", "-"
        ]
        result = subprocess.run(measure_cmd, capture_output=True, text=True)

        # Parse measured values (simplified - use defaults if parsing fails)
        try:
            # Find JSON in stderr
            stderr = result.stderr
            json_start = stderr.rfind('{')
            json_end = stderr.rfind('}') + 1
            if json_start >= 0:
                measured = json.loads(stderr[json_start:json_end])
                input_i = measured.get("input_i", "-24")
                input_tp = measured.get("input_tp", "-2")
                input_lra = measured.get("input_lra", "7")
                input_thresh = measured.get("input_thresh", "-34")
            else:
                raise ValueError("No JSON found")
        except (json.JSONDecodeError, ValueError, KeyError):
            input_i, input_tp, input_lra, input_thresh = "-24", "-2", "7", "-34"

        # Pass 2: Normalize
        norm_filter = (
            f"loudnorm=I={self.config.target_loudness}:TP=-1.5:LRA=11:"
            f"measured_I={input_i}:measured_TP={input_tp}:"
            f"measured_LRA={input_lra}:measured_thresh={input_thresh}:"
            f"linear=true"
        )

        cmd = [
            self.ffmpeg_path, "-y",
            "-i", str(input_path),
            "-af", norm_filter,
            "-acodec", "pcm_s16le",
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        logger.info(f"Normalized to {self.config.target_loudness} LUFS")

    def _encode_audio(self, input_path: Path, output_path: Path):
        """Encode audio to output format."""
        fmt = self.config.output_format
        layout = self.config.output_layout

        # Determine channel count
        if layout == AudioChannelLayout.SURROUND_71:
            channels = 8
        elif layout == AudioChannelLayout.SURROUND_51:
            channels = 6
        elif layout == AudioChannelLayout.MONO:
            channels = 1
        else:
            channels = 2

        # Build encoder command
        if fmt == AudioFormat.AAC:
            codec_args = ["-c:a", "aac", "-b:a", self.config.output_bitrate]
        elif fmt == AudioFormat.AC3:
            codec_args = ["-c:a", "ac3", "-b:a", "640k" if channels > 2 else "192k"]
        elif fmt == AudioFormat.EAC3:
            codec_args = ["-c:a", "eac3", "-b:a", "640k" if channels > 2 else "192k"]
        elif fmt == AudioFormat.DTS:
            codec_args = ["-c:a", "dca", "-b:a", "1536k" if channels > 2 else "192k"]
        elif fmt == AudioFormat.FLAC:
            codec_args = ["-c:a", "flac"]
        else:  # PCM
            codec_args = ["-c:a", "pcm_s16le"]

        cmd = [
            self.ffmpeg_path, "-y",
            "-i", str(input_path),
            *codec_args,
            "-ar", str(self.config.sample_rate),
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        logger.info(f"Encoded to {fmt.value}")

    def _mux_audio_video(self, video_path: Path, audio_path: Path, output_path: Path):
        """Mux audio and video together."""
        cmd = [
            self.ffmpeg_path, "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", "copy",
            "-c:a", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        logger.info(f"Muxed audio and video to {output_path}")


# =============================================================================
# Convenience Functions
# =============================================================================

def enhance_audio(input_path: str, output_path: str,
                  mode: str = "moderate") -> str:
    """
    Quick audio enhancement.

    Args:
        input_path: Input audio/video file
        output_path: Output audio file
        mode: Enhancement mode (none, light, moderate, aggressive, voice, music)

    Returns:
        Path to enhanced audio
    """
    config = AudioConfig(
        enhance_mode=AudioEnhanceMode(mode),
        normalize=True
    )
    processor = AudioProcessor(config)
    return str(processor.process(Path(input_path), Path(output_path)))


def upmix_to_surround(input_path: str, output_path: str,
                      layout: str = "5.1", mode: str = "surround",
                      use_demucs: bool = False) -> str:
    """
    Upmix stereo to surround sound.

    Args:
        input_path: Input stereo audio/video
        output_path: Output surround audio
        layout: Target layout (5.1 or 7.1)
        mode: Upmix algorithm (simple, surround, prologic, demucs)
        use_demucs: Use AI stem separation (requires demucs package)

    Returns:
        Path to surround audio
    """
    config = AudioConfig(
        upmix_mode=UpmixMode.DEMUCS if use_demucs else UpmixMode(mode),
        output_layout=AudioChannelLayout(layout),
        output_format=AudioFormat.EAC3 if layout != "stereo" else AudioFormat.AAC
    )
    processor = AudioProcessor(config)
    return str(processor.process(Path(input_path), Path(output_path)))


def get_available_features() -> Dict[str, bool]:
    """Check which audio features are available."""
    features = {
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "ffprobe": shutil.which("ffprobe") is not None,
        "demucs": False,
        "deepfilternet": False,
        "audiosr": False,
    }

    try:
        result = subprocess.run(
            ["python3", "-c", "import demucs; print('ok')"],
            capture_output=True, text=True, timeout=10
        )
        features["demucs"] = "ok" in result.stdout
    except (subprocess.SubprocessError, OSError):
        pass

    try:
        import df  # noqa: F401
        features["deepfilternet"] = True
    except ImportError:
        pass

    try:
        import audiosr  # noqa: F401
        features["audiosr"] = True
    except ImportError:
        pass

    return features


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """Command-line interface for audio processing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Audio Enhancement and Surround Upmixing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enhance noisy audio
  python audio_processor.py -i input.mp4 -o enhanced.aac --enhance moderate

  # Upmix to 5.1 surround
  python audio_processor.py -i stereo.mp4 -o surround.eac3 --upmix surround --layout 5.1

  # AI-powered upmix with Demucs
  python audio_processor.py -i music.mp3 -o surround.eac3 --upmix demucs --layout 5.1

  # Full processing: enhance + upmix + normalize
  python audio_processor.py -i vhs_video.mp4 -o output.eac3 --enhance voice --upmix surround --layout 5.1
        """
    )

    parser.add_argument("-i", "--input", required=True, help="Input audio/video file")
    parser.add_argument("-o", "--output", required=True, help="Output audio file")

    # Enhancement options
    parser.add_argument("--enhance", default="none",
                        choices=["none", "light", "moderate", "aggressive", "voice", "music", "deepfilternet"],
                        help="Audio enhancement mode")

    # Upmix options
    parser.add_argument("--upmix", default="none",
                        choices=["none", "simple", "surround", "prologic", "demucs"],
                        help="Surround upmix algorithm")
    parser.add_argument("--layout", default="original",
                        choices=["original", "stereo", "5.1", "7.1", "mono"],
                        help="Output channel layout")

    # Output options
    parser.add_argument("--format", default="aac",
                        choices=["aac", "ac3", "eac3", "dts", "flac", "pcm_s16le"],
                        help="Output audio format")
    parser.add_argument("--bitrate", default="192k", help="Output bitrate")
    parser.add_argument("--normalize", action="store_true", default=True,
                        help="Normalize loudness (EBU R128)")
    parser.add_argument("--no-normalize", action="store_false", dest="normalize",
                        help="Disable loudness normalization")

    # Demucs options
    parser.add_argument("--demucs-model", default="htdemucs",
                        choices=["htdemucs", "htdemucs_ft", "mdx_extra"],
                        help="Demucs model for AI separation")

    # AudioSR options
    parser.add_argument("--audio-sr", action="store_true",
                        help="Enable AudioSR AI upsampling to 48kHz")
    parser.add_argument("--audiosr-model", default="basic",
                        choices=["basic", "speech", "music"],
                        help="AudioSR model (basic, speech, music)")

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Check features
    features = get_available_features()
    print(f"Available features: FFmpeg={features['ffmpeg']}, Demucs={features['demucs']}, "
          f"DeepFilterNet={features['deepfilternet']}, AudioSR={features['audiosr']}")

    if args.upmix == "demucs" and not features["demucs"]:
        print("Warning: Demucs not available, falling back to FFmpeg surround")
        args.upmix = "surround"

    if args.enhance == "deepfilternet" and not features["deepfilternet"]:
        print("Warning: DeepFilterNet not available, falling back to aggressive denoise")
        args.enhance = "aggressive"

    if args.audio_sr and not features["audiosr"]:
        print("Warning: AudioSR not available, disabling AI upsampling")
        args.audio_sr = False

    # Build config
    config = AudioConfig(
        enhance_mode=AudioEnhanceMode(args.enhance),
        upmix_mode=UpmixMode(args.upmix),
        output_layout=AudioChannelLayout(args.layout),
        output_format=AudioFormat(args.format),
        output_bitrate=args.bitrate,
        normalize=args.normalize,
        demucs_model=args.demucs_model,
        use_audiosr=args.audio_sr,
        audiosr_model=args.audiosr_model,
    )

    # Process
    processor = AudioProcessor(config)
    output = processor.process(Path(args.input), Path(args.output))
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
