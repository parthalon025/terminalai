"""
Tests for scripts/installation/install.py

Focuses on the basicsr torchvision compatibility patch.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest

# Add scripts/installation to path
scripts_path = Path(__file__).parent.parent / "scripts" / "installation"
sys.path.insert(0, str(scripts_path))

from install import TerminalAIInstaller


class TestBasicsrPatch:
    """Test the basicsr torchvision compatibility patch."""

    @pytest.fixture
    def installer(self):
        """Create installer instance."""
        return TerminalAIInstaller(install_type="full")

    @pytest.fixture
    def mock_basicsr_content_unpatched(self):
        """Mock unpatched basicsr degradations.py content."""
        return """import numpy as np
import torch
from torch.nn import functional as F
from torchvision.transforms.functional_tensor import rgb_to_grayscale

def some_function():
    pass
"""

    @pytest.fixture
    def mock_basicsr_content_patched(self):
        """Mock already patched basicsr degradations.py content."""
        return """import numpy as np
import torch
from torch.nn import functional as F
# Fix for torchvision >= 0.17 where functional_tensor was removed
try:
    from torchvision.transforms.functional import rgb_to_grayscale
except ImportError:
    from torchvision.transforms.functional_tensor import rgb_to_grayscale

def some_function():
    pass
"""

    def test_patch_basicsr_not_installed(self, installer, capsys):
        """Test patch when basicsr is not installed."""
        with patch('subprocess.run') as mock_run:
            # Simulate CalledProcessError (basicsr import fails)
            from subprocess import CalledProcessError
            mock_run.side_effect = CalledProcessError(1, "python")

            installer.patch_basicsr_torchvision()

            captured = capsys.readouterr()
            assert "basicsr not installed" in captured.out.lower()

    def test_patch_basicsr_file_not_found(self, installer, capsys):
        """Test patch when degradations.py doesn't exist."""
        with patch('subprocess.run') as mock_run:
            # Mock basicsr installed but file missing
            mock_result = MagicMock()
            mock_result.stdout = "/fake/path/basicsr/__init__.py\n"
            mock_run.return_value = mock_result

            installer.patch_basicsr_torchvision()

            captured = capsys.readouterr()
            assert "degradations.py not found" in captured.out.lower()

    def test_patch_basicsr_success(self, installer, mock_basicsr_content_unpatched, capsys):
        """Test successful patching of basicsr."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create fake basicsr structure
            basicsr_dir = Path(tmpdir) / "basicsr"
            data_dir = basicsr_dir / "data"
            data_dir.mkdir(parents=True)

            degradations_file = data_dir / "degradations.py"
            degradations_file.write_text(mock_basicsr_content_unpatched, encoding='utf-8')

            with patch('subprocess.run') as mock_run:
                # Mock basicsr location
                mock_result = MagicMock()
                mock_result.stdout = str(basicsr_dir / "__init__.py") + "\n"
                mock_run.return_value = mock_result

                installer.patch_basicsr_torchvision()

                # Verify patch applied
                patched_content = degradations_file.read_text(encoding='utf-8')
                assert "Fix for torchvision >= 0.17" in patched_content
                assert "try:" in patched_content
                assert "from torchvision.transforms.functional import rgb_to_grayscale" in patched_content
                assert "except ImportError:" in patched_content

                # Verify log message
                captured = capsys.readouterr()
                assert "successfully patched" in captured.out.lower()

                # Verify installer tracking
                assert "basicsr torchvision compatibility patch" in installer.installed

    def test_patch_basicsr_idempotent(self, installer, mock_basicsr_content_patched, capsys):
        """Test that patch is idempotent (safe to run multiple times)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create fake basicsr structure with already patched file
            basicsr_dir = Path(tmpdir) / "basicsr"
            data_dir = basicsr_dir / "data"
            data_dir.mkdir(parents=True)

            degradations_file = data_dir / "degradations.py"
            degradations_file.write_text(mock_basicsr_content_patched, encoding='utf-8')

            original_content = degradations_file.read_text(encoding='utf-8')

            with patch('subprocess.run') as mock_run:
                # Mock basicsr location
                mock_result = MagicMock()
                mock_result.stdout = str(basicsr_dir / "__init__.py") + "\n"
                mock_run.return_value = mock_result

                installer.patch_basicsr_torchvision()

                # Verify content unchanged
                current_content = degradations_file.read_text(encoding='utf-8')
                assert current_content == original_content

                # Verify log message
                captured = capsys.readouterr()
                assert "already patched" in captured.out.lower()

                # Should not add to installed list again
                assert "basicsr torchvision compatibility patch" not in installer.installed

    def test_patch_basicsr_import_already_modified(self, installer, capsys):
        """Test when import line is already modified (different from our patch)."""
        modified_content = """import numpy as np
# Some custom import modification
from torchvision.transforms import functional as F
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            basicsr_dir = Path(tmpdir) / "basicsr"
            data_dir = basicsr_dir / "data"
            data_dir.mkdir(parents=True)

            degradations_file = data_dir / "degradations.py"
            degradations_file.write_text(modified_content, encoding='utf-8')

            with patch('subprocess.run') as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(basicsr_dir / "__init__.py") + "\n"
                mock_run.return_value = mock_result

                installer.patch_basicsr_torchvision()

                # Should skip patching
                captured = capsys.readouterr()
                assert "already modified" in captured.out.lower() or "skipping patch" in captured.out.lower()

    def test_patch_basicsr_handles_exceptions(self, installer):
        """Test that patch handles exceptions gracefully."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Unexpected error")

            # Should not raise exception
            installer.patch_basicsr_torchvision()

            # Should add warning
            assert any("basicsr patching failed" in w for w in installer.warnings)

    def test_patch_preserves_file_encoding(self, installer, mock_basicsr_content_unpatched):
        """Test that patch preserves UTF-8 encoding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            basicsr_dir = Path(tmpdir) / "basicsr"
            data_dir = basicsr_dir / "data"
            data_dir.mkdir(parents=True)

            degradations_file = data_dir / "degradations.py"
            degradations_file.write_text(mock_basicsr_content_unpatched, encoding='utf-8')

            with patch('subprocess.run') as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(basicsr_dir / "__init__.py") + "\n"
                mock_run.return_value = mock_result

                installer.patch_basicsr_torchvision()

                # Read with UTF-8 should work
                content = degradations_file.read_text(encoding='utf-8')
                assert "Fix for torchvision >= 0.17" in content


class TestInstallerIntegration:
    """Test installer integration."""

    def test_full_installation_includes_patch(self):
        """Test that full installation includes basicsr patch step."""
        installer = TerminalAIInstaller(install_type="full")

        # Mock all steps to prevent actual installation
        with patch.object(installer, 'check_python_version', return_value=True), \
             patch.object(installer, 'check_pip', return_value=True), \
             patch.object(installer, 'install_package', return_value=True), \
             patch.object(installer, 'check_ffmpeg', return_value=True), \
             patch.object(installer, 'check_nvidia_gpu', return_value=True), \
             patch.object(installer, 'check_maxine_sdk', return_value=True), \
             patch.object(installer, 'check_realesrgan', return_value=True), \
             patch.object(installer, 'install_optional_vapoursynth', return_value=None), \
             patch.object(installer, 'install_optional_realesrgan', return_value=None), \
             patch.object(installer, 'install_optional_gfpgan', return_value=None), \
             patch.object(installer, 'patch_basicsr_torchvision', return_value=None) as mock_patch, \
             patch.object(installer, 'create_config', return_value=True), \
             patch.object(installer, 'verify_installation', return_value=True), \
             patch.object(installer, 'print_summary', return_value=True):

            installer.run()

            # Verify patch method was called
            mock_patch.assert_called_once()

    def test_basic_installation_skips_patch(self):
        """Test that basic installation doesn't include basicsr patch."""
        installer = TerminalAIInstaller(install_type="basic")

        # Mock steps
        with patch.object(installer, 'check_python_version', return_value=True), \
             patch.object(installer, 'check_pip', return_value=True), \
             patch.object(installer, 'install_package', return_value=True), \
             patch.object(installer, 'check_ffmpeg', return_value=True), \
             patch.object(installer, 'check_nvidia_gpu', return_value=True), \
             patch.object(installer, 'check_maxine_sdk', return_value=True), \
             patch.object(installer, 'check_realesrgan', return_value=True), \
             patch.object(installer, 'patch_basicsr_torchvision', return_value=None) as mock_patch, \
             patch.object(installer, 'create_config', return_value=True), \
             patch.object(installer, 'verify_installation', return_value=True), \
             patch.object(installer, 'print_summary', return_value=True):

            installer.run()

            # Verify patch method was NOT called
            mock_patch.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
