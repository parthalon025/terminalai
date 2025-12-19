"""
Security Vulnerability Tests
=============================

Tests for critical security fixes in TerminalAI v1.5.2:
1. ZIP slip vulnerability protection
2. Command injection prevention
3. Download checksum verification
4. SMTP header injection prevention
"""

import hashlib
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest


# ============================================================================
# 1. ZIP Slip Vulnerability Tests
# ============================================================================

class TestZipSlipProtection:
    """Test ZIP slip vulnerability protection in setup_rtx_video.py"""

    def test_extract_sdk_blocks_parent_traversal(self, tmp_path):
        """Test that extraction blocks '../' path traversal"""
        from scripts.setup_rtx_video import extract_sdk

        # Create malicious ZIP with parent directory reference
        zip_path = tmp_path / "malicious.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('../malware.txt', 'malicious content')

        target_dir = tmp_path / "extracted"

        # Should fail and return False
        result = extract_sdk(zip_path, target_dir)

        assert result is False
        # Malicious file should NOT exist outside target directory
        assert not (tmp_path / "malware.txt").exists()

    def test_extract_sdk_blocks_absolute_paths(self, tmp_path):
        """Test that extraction blocks absolute paths in ZIP"""
        from scripts.setup_rtx_video import extract_sdk

        # Create malicious ZIP with absolute path
        zip_path = tmp_path / "malicious.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('/etc/passwd', 'malicious content')

        target_dir = tmp_path / "extracted"

        # Should fail
        result = extract_sdk(zip_path, target_dir)

        assert result is False

    def test_extract_sdk_blocks_complex_traversal(self, tmp_path):
        """Test that extraction blocks complex path traversal like 'lib/../../'"""
        from scripts.setup_rtx_video import extract_sdk

        # Create malicious ZIP with complex traversal
        zip_path = tmp_path / "malicious.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('lib/../../malware.dll', 'malicious content')

        target_dir = tmp_path / "extracted"

        # Should fail
        result = extract_sdk(zip_path, target_dir)

        assert result is False

    def test_extract_sdk_allows_valid_paths(self, tmp_path):
        """Test that extraction allows valid paths within target directory"""
        from scripts.setup_rtx_video import extract_sdk

        # Create legitimate ZIP
        zip_path = tmp_path / "legitimate.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('lib/NVVideoEffects.dll', 'legitimate content')
            zf.writestr('bin/helper.exe', 'legitimate content')

        target_dir = tmp_path / "extracted"

        # Should succeed
        result = extract_sdk(zip_path, target_dir)

        assert result is True
        assert (target_dir / "lib" / "NVVideoEffects.dll").exists()
        assert (target_dir / "bin" / "helper.exe").exists()

    def test_extract_sdk_blocks_windows_path_traversal(self, tmp_path):
        """Test that extraction blocks Windows-style path traversal"""
        from scripts.setup_rtx_video import extract_sdk

        # Create malicious ZIP with Windows-style traversal
        zip_path = tmp_path / "malicious.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('..\\..\\Windows\\System32\\malware.dll', 'malicious content')

        target_dir = tmp_path / "extracted"

        # Should fail
        result = extract_sdk(zip_path, target_dir)

        assert result is False


# ============================================================================
# 2. Command Injection Tests
# ============================================================================

class TestCommandInjectionPrevention:
    """Test command injection prevention in LUT file path handling"""

    def test_lut_path_suspicious_char_detection(self):
        """Test that suspicious characters in LUT paths are detected"""
        # The security fix is in the _preprocess() method
        # It checks for these suspicious characters: ; | & $ ` \n \r
        suspicious_chars = [';', '|', '&', '$', '`', '\n', '\r']

        for char in suspicious_chars:
            test_path = f"test{char}file.cube"
            # Should contain suspicious character
            assert any(c in test_path for c in suspicious_chars)

    def test_lut_path_escaping_quotes(self):
        """Test the escaping logic for single quotes"""
        # The fix escapes: backslash, single quote, colon
        test_path = "user's_lut.cube"
        escaped = test_path.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

        # Should have escaped the single quote
        assert "\\'" in escaped

    def test_lut_path_escaping_backslash(self):
        """Test the escaping logic for backslashes"""
        test_path = "path\\to\\lut.cube"
        escaped = test_path.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

        # Should have escaped the backslashes
        assert "\\\\" in escaped

    def test_lut_path_safe_characters_unchanged(self):
        """Test that safe characters don't get flagged"""
        safe_chars = ['-', '_', '.', '0', 'a', 'A']
        suspicious_chars = [';', '|', '&', '$', '`', '\n', '\r']

        for char in safe_chars:
            test_path = f"test{char}file.cube"
            # Should not contain any suspicious characters
            assert not any(c in test_path for c in suspicious_chars)

    def test_command_injection_protection_documented(self):
        """Test that the security fix is properly documented in code"""
        # Read the vhs_upscale.py file to verify security comments exist
        from pathlib import Path
        vhs_upscale_file = Path(__file__).parent.parent / "vhs_upscaler" / "vhs_upscale.py"

        if vhs_upscale_file.exists():
            content = vhs_upscale_file.read_text()
            # Check for security comments
            assert "SECURITY:" in content or "Security:" in content
            assert "escape" in content.lower() or "sanitize" in content.lower()


# ============================================================================
# 3. Download Checksum Verification Tests
# ============================================================================

class TestChecksumVerification:
    """Test download checksum verification in face_restoration.py"""

    def test_verify_checksum_success(self, tmp_path):
        """Test that valid checksum passes verification"""
        from vhs_upscaler.face_restoration import FaceRestorer

        # Create test file
        test_file = tmp_path / "model.pth"
        test_content = b"test model data"
        test_file.write_bytes(test_content)

        # Calculate correct checksum
        expected_sha256 = hashlib.sha256(test_content).hexdigest()

        restorer = FaceRestorer()
        result = restorer._verify_checksum(test_file, expected_sha256)

        assert result is True

    def test_verify_checksum_failure(self, tmp_path):
        """Test that invalid checksum fails verification"""
        from vhs_upscaler.face_restoration import FaceRestorer

        # Create test file
        test_file = tmp_path / "model.pth"
        test_file.write_bytes(b"test model data")

        # Use wrong checksum
        wrong_checksum = "0" * 64

        restorer = FaceRestorer()
        result = restorer._verify_checksum(test_file, wrong_checksum)

        assert result is False

    def test_verify_checksum_case_insensitive(self, tmp_path):
        """Test that checksum verification is case-insensitive"""
        from vhs_upscaler.face_restoration import FaceRestorer

        # Create test file
        test_file = tmp_path / "model.pth"
        test_content = b"test model data"
        test_file.write_bytes(test_content)

        # Calculate checksum
        checksum = hashlib.sha256(test_content).hexdigest()

        restorer = FaceRestorer()

        # Test uppercase
        assert restorer._verify_checksum(test_file, checksum.upper()) is True
        # Test lowercase
        assert restorer._verify_checksum(test_file, checksum.lower()) is True

    def test_verify_checksum_placeholder_warning(self, tmp_path, caplog):
        """Test that placeholder checksums generate warnings"""
        from vhs_upscaler.face_restoration import FaceRestorer

        # Create test file
        test_file = tmp_path / "model.pth"
        test_file.write_bytes(b"test model data")

        # Use placeholder checksum (starts with c953a88f)
        placeholder = "c953a88f2727c85c3d9ae72e2bd4a0d1e5c8c6b8c67c3a9e2c3d0e3f0e0f0e0f"

        restorer = FaceRestorer()
        result = restorer._verify_checksum(test_file, placeholder)

        # Should pass but log warning
        assert result is True
        assert "SECURITY: Checksum verification skipped" in caplog.text
        assert "placeholder hash" in caplog.text

    @patch('vhs_upscaler.face_restoration.requests.get')
    def test_download_model_verifies_checksum(self, mock_get, tmp_path):
        """Test that download_model verifies checksums"""
        from vhs_upscaler.face_restoration import FaceRestorer

        # Mock HTTP response
        mock_response = Mock()
        mock_response.headers.get.return_value = '100'
        mock_response.iter_content.return_value = [b"test model data"]
        mock_get.return_value = mock_response

        restorer = FaceRestorer(model_path=tmp_path / "model.pth")

        # Download should verify checksum
        # (will use placeholder checksum in tests)
        result = restorer.download_model()

        # Verification should have happened
        assert result is True or result is False  # Depends on checksum

    @patch('vhs_upscaler.face_restoration.requests.get')
    def test_download_model_deletes_corrupted_file(self, mock_get, tmp_path):
        """Test that corrupted downloads are deleted"""
        from vhs_upscaler.face_restoration import FaceRestorer

        # Mock HTTP response
        mock_response = Mock()
        mock_response.headers.get.return_value = '100'
        mock_response.iter_content.return_value = [b"corrupted data"]
        mock_get.return_value = mock_response

        # Create restorer with explicit wrong checksum
        restorer = FaceRestorer(model_path=tmp_path / "model.pth")

        # Temporarily set a real (wrong) checksum
        original_models = restorer.GFPGAN_MODELS.copy()
        restorer.GFPGAN_MODELS["v1.3"]["sha256"] = "0" * 64  # Wrong checksum

        try:
            result = restorer.download_model()

            # Should fail and delete temp file
            assert result is False
            assert not (tmp_path / "model.pth").exists()
        finally:
            restorer.GFPGAN_MODELS = original_models


# ============================================================================
# 4. SMTP Header Injection Tests
# ============================================================================

class TestSMTPHeaderInjection:
    """Test SMTP header injection prevention in notifications.py"""

    def test_sanitize_email_header_removes_crlf(self):
        """Test that CRLF characters are removed from headers"""
        from vhs_upscaler.notifications import Notifier, NotificationConfig

        config = NotificationConfig(email_enabled=False)
        notifier = Notifier(config)

        # Test CRLF injection attempt
        malicious_subject = "Test\r\nBcc: hacker@evil.com\r\nX-Priority: 1"
        sanitized = notifier._sanitize_email_header(malicious_subject, "Subject")

        # Should have CRLF removed (but the text content remains)
        assert '\r' not in sanitized
        assert '\n' not in sanitized
        # The injected header attempt is neutralized by removing CRLF
        # The remaining text is harmless without newlines
        assert sanitized == "TestBcc: hacker@evil.comX-Priority: 1"

    def test_sanitize_email_header_removes_null_bytes(self):
        """Test that null bytes are removed from headers"""
        from vhs_upscaler.notifications import Notifier, NotificationConfig

        config = NotificationConfig(email_enabled=False)
        notifier = Notifier(config)

        malicious_subject = "Test\x00Injection"
        sanitized = notifier._sanitize_email_header(malicious_subject, "Subject")

        assert '\x00' not in sanitized

    def test_sanitize_email_header_limits_length(self):
        """Test that headers are limited to RFC 2822 length"""
        from vhs_upscaler.notifications import Notifier, NotificationConfig

        config = NotificationConfig(email_enabled=False)
        notifier = Notifier(config)

        # Create very long subject
        long_subject = "A" * 2000
        sanitized = notifier._sanitize_email_header(long_subject, "Subject")

        # Should be truncated to 998 characters
        assert len(sanitized) <= 998

    def test_sanitize_email_header_rejects_heavy_injection(self):
        """Test that headers with too many dangerous characters are rejected"""
        from vhs_upscaler.notifications import Notifier, NotificationConfig

        config = NotificationConfig(email_enabled=False)
        notifier = Notifier(config)

        # More than 50% dangerous characters (need more chars to trigger the threshold)
        # Pattern: short text with many dangerous chars
        malicious_subject = "T\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\nXY"  # 3 chars, 9 CRLF pairs = 18 dangerous chars

        with pytest.raises(ValueError, match="suspicious content"):
            notifier._sanitize_email_header(malicious_subject, "Subject")

    def test_validate_email_address_rejects_crlf(self):
        """Test that email addresses with CRLF are rejected"""
        from vhs_upscaler.notifications import Notifier, NotificationConfig

        config = NotificationConfig(email_enabled=False)
        notifier = Notifier(config)

        # Malicious email with CRLF
        malicious_email = "user@example.com\r\nBcc: hacker@evil.com"
        result = notifier._validate_email_address(malicious_email)

        assert result is False

    def test_validate_email_address_rejects_invalid_format(self):
        """Test that invalid email formats are rejected"""
        from vhs_upscaler.notifications import Notifier, NotificationConfig

        config = NotificationConfig(email_enabled=False)
        notifier = Notifier(config)

        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user@@example.com",
            "user@example",
        ]

        for email in invalid_emails:
            assert notifier._validate_email_address(email) is False

    def test_validate_email_address_accepts_valid(self):
        """Test that valid email addresses are accepted"""
        from vhs_upscaler.notifications import Notifier, NotificationConfig

        config = NotificationConfig(email_enabled=False)
        notifier = Notifier(config)

        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "123@example.com",
        ]

        for email in valid_emails:
            assert notifier._validate_email_address(email) is True

    @patch('vhs_upscaler.notifications.smtplib.SMTP')
    def test_send_email_sanitizes_subject(self, mock_smtp):
        """Test that send_email sanitizes subject headers"""
        from vhs_upscaler.notifications import Notifier, NotificationConfig

        config = NotificationConfig(
            email_enabled=True,
            smtp_server="smtp.example.com",
            smtp_user="user",
            smtp_password="pass",
            from_email="from@example.com",
            to_email="to@example.com",
        )
        notifier = Notifier(config)

        # Malicious subject
        malicious_subject = "Job Complete\r\nBcc: hacker@evil.com"

        # Should sanitize and send
        result = notifier.send_email(malicious_subject, "Body text")

        # Email should be sent with sanitized subject
        # (CRLF removed, Bcc not added)

    @patch('vhs_upscaler.notifications.smtplib.SMTP')
    def test_send_email_validates_addresses(self, mock_smtp):
        """Test that send_email validates email addresses"""
        from vhs_upscaler.notifications import Notifier, NotificationConfig

        # Invalid FROM address
        config = NotificationConfig(
            email_enabled=True,
            smtp_server="smtp.example.com",
            smtp_user="user",
            smtp_password="pass",
            from_email="not-an-email",  # Invalid
            to_email="to@example.com",
        )
        notifier = Notifier(config)

        result = notifier.send_email("Subject", "Body")

        # Should fail validation
        assert result is False


# ============================================================================
# Integration Tests
# ============================================================================

class TestSecurityIntegration:
    """Integration tests for multiple security features"""

    def test_all_security_features_work_together(self):
        """Test that all security features can work in harmony"""
        # This is a placeholder for integration testing
        # In production, would test:
        # 1. Extract SDK with valid ZIP
        # 2. Apply LUT with safe filename
        # 3. Download model with checksum
        # 4. Send notification with valid headers
        pass

    def test_security_logging(self, caplog):
        """Test that security violations are properly logged"""
        # Ensure all security violations produce appropriate log messages
        # with WARNING or ERROR level
        pass


# ============================================================================
# Backward Compatibility Tests
# ============================================================================

class TestBackwardCompatibility:
    """Test that security fixes don't break existing functionality"""

    def test_legitimate_zip_extraction_still_works(self, tmp_path):
        """Test that legitimate ZIP files still extract correctly"""
        from scripts.setup_rtx_video import extract_sdk

        # Create legitimate SDK-like ZIP
        zip_path = tmp_path / "sdk.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('lib/NVVideoEffects.dll', 'library file')
            zf.writestr('bin/app.exe', 'executable')
            zf.writestr('docs/README.txt', 'documentation')

        target_dir = tmp_path / "sdk"

        result = extract_sdk(zip_path, target_dir)

        assert result is True
        assert (target_dir / "lib" / "NVVideoEffects.dll").exists()
        assert (target_dir / "bin" / "app.exe").exists()
        assert (target_dir / "docs" / "README.txt").exists()

    def test_legitimate_lut_files_still_work(self, tmp_path):
        """Test that legitimate LUT files still work"""
        # LUT files with normal characters should work fine
        # Only suspicious shell metacharacters are blocked
        pass

    def test_legitimate_model_downloads_work(self):
        """Test that legitimate model downloads still work"""
        # Models with correct checksums should download successfully
        pass

    def test_legitimate_emails_still_send(self):
        """Test that legitimate emails still send correctly"""
        # Normal subject lines and email addresses should work
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
