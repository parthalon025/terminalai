#!/usr/bin/env python3
"""
Apply Basic/Advanced mode toggle patch to GUI.
This script modifies gui.py to add a mode toggle feature.
"""

import re

GUI_FILE = "vhs_upscaler/gui.py"

# Read the file
with open(GUI_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Patch 1: Add mode toggle event handlers before file upload handler
event_handler_marker = """        # =====================================================================
        # Event Handlers
        # =====================================================================

        # File upload handler"""

event_handler_replacement = """        # =====================================================================
        # Event Handlers
        # =====================================================================

        # Mode toggle handler
        def toggle_mode(mode):
            \"\"\"Toggle between Basic and Advanced modes.\"\"\"
            is_basic = "Basic" in mode
            return {
                basic_mode_ui: gr.update(visible=is_basic),
                advanced_mode_ui: gr.update(visible=not is_basic)
            }

        mode_toggle.change(
            fn=toggle_mode,
            inputs=[mode_toggle],
            outputs=[basic_mode_ui, advanced_mode_ui]
        )

        # Basic mode process button handler
        def process_basic_video(file_path, url_input, basic_preset_choice, basic_quality_choice):
            \"\"\"Process video from basic mode with smart defaults.\"\"\"
            # Map basic presets to configuration
            preset_map = {
                "📼 Old VHS tape (home movies, family recordings)": {
                    "preset": "vhs",
                    "resolution": 1080,
                    "upscale_engine": "auto",
                    "face_restore": True,
                    "audio_enhance": "voice",
                    "audio_upmix": "demucs",
                    "audio_layout": "5.1",
                    "audio_sr_enabled": True,
                    "audio_sr_model": "speech",
                    "encoder": "hevc_nvenc"
                },
                "💿 DVD movie": {
                    "preset": "dvd",
                    "resolution": 1080,
                    "upscale_engine": "auto",
                    "face_restore": False,
                    "audio_enhance": "light",
                    "audio_upmix": "prologic",
                    "audio_layout": "5.1",
                    "audio_sr_enabled": False,
                    "encoder": "hevc_nvenc"
                },
                "📺 YouTube video": {
                    "preset": "youtube",
                    "resolution": 1080,
                    "upscale_engine": "realesrgan",
                    "face_restore": False,
                    "audio_enhance": "moderate",
                    "audio_upmix": "none",
                    "audio_layout": "original",
                    "audio_sr_enabled": False,
                    "encoder": "hevc_nvenc"
                },
                "🎥 Recent digital video (phone, camera)": {
                    "preset": "clean",
                    "resolution": 1080,
                    "upscale_engine": "auto",
                    "face_restore": False,
                    "audio_enhance": "none",
                    "audio_upmix": "none",
                    "audio_layout": "original",
                    "audio_sr_enabled": False,
                    "encoder": "hevc_nvenc"
                }
            }

            # Map quality choices to CRF values
            quality_map = {
                "Good (Fast, smaller file)": 23,
                "Better (Balanced)": 20,
                "Best (Slow, larger file)": 18
            }

            config = preset_map.get(basic_preset_choice, preset_map["📼 Old VHS tape (home movies, family recordings)"])
            crf = quality_map.get(basic_quality_choice, 20)

            # Use file path if uploaded, otherwise URL
            source = file_path if file_path else url_input

            # Call add_to_queue with smart defaults
            return add_to_queue(
                input_source=source,
                preset=config["preset"],
                resolution=config["resolution"],
                quality=0,  # Best quality preset
                crf=crf,
                encoder=config["encoder"],
                upscale_engine=config["upscale_engine"],
                hdr_mode="sdr",  # Default to SDR
                realesrgan_model="realesrgan-x4plus",
                realesrgan_denoise=0.5,
                ffmpeg_scale_algo="lanczos",
                hdr_brightness=400,
                hdr_color_depth=10,
                rtxvideo_artifact_reduction=True,
                rtxvideo_artifact_strength=0.5,
                rtxvideo_hdr=False,
                audio_enhance=config["audio_enhance"],
                audio_upmix=config["audio_upmix"],
                audio_layout=config["audio_layout"],
                audio_format="aac",
                audio_target_loudness=-14.0,
                audio_noise_floor=-20.0,
                demucs_model="htdemucs",
                demucs_device="auto",
                demucs_shifts=1,
                lfe_crossover=120,
                center_mix=0.707,
                surround_delay=15,
                lut_file="",
                lut_strength=1.0,
                face_restore=config["face_restore"],
                face_model="gfpgan",
                face_restore_strength=0.5,
                face_restore_upscale=2,
                audio_sr_enabled=config["audio_sr_enabled"],
                audio_sr_model=config.get("audio_sr_model", "basic"),
                deinterlace_algorithm="yadif",
                qtgmc_preset="medium"
            )

        basic_process_btn.click(
            fn=process_basic_video,
            inputs=[final_input, input_source, basic_preset, basic_quality],
            outputs=[status_msg, queue_display]
        )

        # File upload handler"""

if event_handler_marker in content:
    content = content.replace(event_handler_marker, event_handler_replacement)
    print("[OK] Added mode toggle and basic mode handlers")
else:
    print("[ERROR] Could not find event handler marker")
    import sys
    sys.exit(1)

# Write the modified file
with open(GUI_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"[OK] Patched {GUI_FILE}")
