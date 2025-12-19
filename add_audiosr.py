#!/usr/bin/env python3
"""
Script to add AudioSR integration to audio_processor.py
"""

import re

def add_audiosr_integration():
    """Add AudioSR integration to audio_processor.py"""

    file_path = r"D:\SSD\AI_Tools\terminalai\vhs_upscaler\audio_processor.py"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add AudioSR settings to AudioConfig
    audioconfig_pattern = r'(    # Demucs settings\n    demucs_model: str = "htdemucs".*?\n    demucs_device: str = "auto".*?\n)\n(    # Advanced)'
    audioconfig_replacement = r'\1\n    # AudioSR settings (AI-based audio upsampling)\n    use_audiosr: bool = False        # Enable AI-based upsampling to 48kHz\n    audiosr_model: str = "basic"     # basic, speech, music\n    audiosr_device: str = "auto"     # auto, cuda, cpu\n\n\2'

    content = re.sub(audioconfig_pattern, audioconfig_replacement, content, flags=re.DOTALL)

    # 2. Add AudioSR check method after deepfilternet check
    check_method = '''
    def _check_audiosr(self) -> bool:
        """Check if AudioSR is available."""
        try:
            import audiosr
            return True
        except ImportError:
            return False
'''

    # Find position after _check_deepfilternet
    deepfilternet_check_pattern = r'(    def _check_deepfilternet\(self\) -> bool:.*?return False\n)'
    content = re.sub(deepfilternet_check_pattern, r'\1' + check_method, content, flags=re.DOTALL)

    # 3. Add audiosr_available to __init__
    init_pattern = r'(        self\.deepfilternet_available = self\._check_deepfilternet\(\))'
    init_replacement = r'\1\n        self.audiosr_available = self._check_audiosr()'
    content = re.sub(init_pattern, init_replacement, content)

    # 4. Add AudioSR upsampling to process() pipeline before upmixing
    # Find the section after enhancement and before upmix
    process_pattern = r'(            # Step 2: Apply enhancement\n.*?current_audio = enhanced\n)\n(            # Step 3: Apply upmix)'
    process_replacement = r'''\1
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

\2'''
    content = re.sub(process_pattern, process_replacement, content, flags=re.DOTALL)

    # 5. Add _upsample_audiosr method before _upmix_with_ffmpeg
    audiosr_method = '''    def _upsample_audiosr(self, input_path: Path, output_path: Path, target_sr: int = 48000):
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

'''

    # Find position before _upmix_with_ffmpeg
    upmix_pattern = r'(    def _upmix_with_ffmpeg\(self, input_path: Path, output_path: Path\):)'
    content = re.sub(upmix_pattern, audiosr_method + r'\1', content)

    # 6. Add audiosr to get_available_features()
    features_pattern = r'(        "deepfilternet": False,\n    \})'
    features_replacement = r'        "deepfilternet": False,\n        "audiosr": False,\n    }'
    content = re.sub(features_pattern, features_replacement, content)

    # Add audiosr check to get_available_features
    features_check_pattern = r'(    try:\n        import df\n        features\["deepfilternet"\] = True\n    except ImportError:\n        pass)'
    features_check_replacement = r'''\1

    try:
        import audiosr
        features["audiosr"] = True
    except ImportError:
        pass'''
    content = re.sub(features_check_pattern, features_check_replacement, content)

    # 7. Add --audio-sr CLI flag
    cli_pattern = r'(    # Demucs options\n    parser\.add_argument\("--demucs-model",.*?\n.*?help="Demucs model for AI separation"\))'
    cli_replacement = r'''\1

    # AudioSR options
    parser.add_argument("--audio-sr", action="store_true",
                        help="Enable AI-based audio upsampling to 48kHz (requires audiosr package)")
    parser.add_argument("--audiosr-model", default="basic",
                        choices=["basic", "speech", "music"],
                        help="AudioSR model selection")'''
    content = re.sub(cli_pattern, cli_replacement, content)

    # 8. Update CLI features check
    cli_features_pattern = r'(    print\(f"Available features: FFmpeg=\{features\[\'ffmpeg\'\]\}, Demucs=\{features\[\'demucs\'\]\}, "\n          f"DeepFilterNet=\{features\[\'deepfilternet\'\]\}"\))'
    cli_features_replacement = r'''    print(f"Available features: FFmpeg={features['ffmpeg']}, Demucs={features['demucs']}, "
          f"DeepFilterNet={features['deepfilternet']}, AudioSR={features['audiosr']}")'''
    content = re.sub(cli_features_pattern, cli_features_replacement, content)

    # 9. Add AudioSR to config in CLI
    cli_config_pattern = r'(        normalize=args\.normalize,\n        demucs_model=args\.demucs_model,\n    \))'
    cli_config_replacement = r'''        normalize=args.normalize,
        demucs_model=args.demucs_model,
        use_audiosr=args.audio_sr,
        audiosr_model=args.audiosr_model,
    )'''
    content = re.sub(cli_config_pattern, cli_config_replacement, content)

    # 10. Add warning for AudioSR not available
    cli_warning_pattern = r'(    if args\.enhance == "deepfilternet" and not features\["deepfilternet"\]:.*?\n.*?args\.enhance = "aggressive")'
    cli_warning_replacement = r'''\1

    if args.audio_sr and not features["audiosr"]:
        print("Warning: AudioSR not available, will use FFmpeg resampling fallback")'''
    content = re.sub(cli_warning_pattern, cli_warning_replacement, content)

    # Write the modified content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("AudioSR integration added successfully!")
    print("Changes made:")
    print("  1. Added AudioSR settings to AudioConfig")
    print("  2. Added _check_audiosr() method")
    print("  3. Added audiosr_available attribute to AudioProcessor")
    print("  4. Integrated AudioSR into process() pipeline")
    print("  5. Added _upsample_audiosr() method")
    print("  6. Added _resample_ffmpeg() fallback method")
    print("  7. Updated get_available_features()")
    print("  8. Added --audio-sr and --audiosr-model CLI flags")
    print("  9. Updated CLI help text and config")

if __name__ == "__main__":
    add_audiosr_integration()
