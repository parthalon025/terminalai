#!/usr/bin/env python3
"""
Tests for Notification System
==============================

Tests for webhook and email notifications including Discord, Slack, and SMTP.
"""

import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock, call
import tempfile

import pytest


class TestNotificationManagerInitialization(unittest.TestCase):
    """Test NotificationManager initialization."""

    def test_init_with_webhook_config(self):
        """Test initialization with webhook configuration."""
        from vhs_upscaler.notifications import NotificationManager

        config = {
            'webhook_url': 'https://discord.com/api/webhooks/123/abc',
            'webhook_type': 'discord'
        }

        manager = NotificationManager(config)
        self.assertEqual(manager.webhook_url, config['webhook_url'])
        self.assertEqual(manager.webhook_type, 'discord')

    def test_init_with_email_config(self):
        """Test initialization with email configuration."""
        from vhs_upscaler.notifications import NotificationManager

        config = {
            'email_enabled': True,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': 'user@example.com',
            'smtp_password': 'password',
            'email_from': 'user@example.com',
            'email_to': 'admin@example.com'
        }

        manager = NotificationManager(config)
        self.assertTrue(manager.email_enabled)
        self.assertEqual(manager.smtp_server, 'smtp.gmail.com')

    def test_init_with_both_webhook_and_email(self):
        """Test initialization with both notification types."""
        from vhs_upscaler.notifications import NotificationManager

        config = {
            'webhook_url': 'https://slack.com/api/webhook',
            'webhook_type': 'slack',
            'email_enabled': True,
            'smtp_server': 'smtp.gmail.com',
            'email_to': 'admin@example.com'
        }

        manager = NotificationManager(config)
        self.assertIsNotNone(manager.webhook_url)
        self.assertTrue(manager.email_enabled)

    def test_init_with_no_config(self):
        """Test initialization with empty config (notifications disabled)."""
        from vhs_upscaler.notifications import NotificationManager

        manager = NotificationManager({})
        self.assertFalse(hasattr(manager, 'webhook_url') and manager.webhook_url)
        self.assertFalse(hasattr(manager, 'email_enabled') and manager.email_enabled)


class TestWebhookNotifications(unittest.TestCase):
    """Test webhook notification functionality."""

    @patch('requests.post')
    def test_send_discord_webhook(self, mock_post):
        """Test sending Discord webhook notification."""
        from vhs_upscaler.notifications import NotificationManager

        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        config = {
            'webhook_url': 'https://discord.com/api/webhooks/123/abc',
            'webhook_type': 'discord'
        }

        manager = NotificationManager(config)
        manager.send_webhook("Test message")

        # Verify webhook was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Verify Discord-specific format
        payload = call_args[1]['json']
        self.assertIn('content', payload)
        self.assertEqual(payload['content'], "Test message")

    @patch('requests.post')
    def test_send_slack_webhook(self, mock_post):
        """Test sending Slack webhook notification."""
        from vhs_upscaler.notifications import NotificationManager

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        config = {
            'webhook_url': 'https://hooks.slack.com/services/T00/B00/XXX',
            'webhook_type': 'slack'
        }

        manager = NotificationManager(config)
        manager.send_webhook("Test message")

        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Verify Slack-specific format
        payload = call_args[1]['json']
        self.assertIn('text', payload)
        self.assertEqual(payload['text'], "Test message")

    @patch('requests.post')
    def test_send_custom_webhook(self, mock_post):
        """Test sending custom webhook notification."""
        from vhs_upscaler.notifications import NotificationManager

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        config = {
            'webhook_url': 'https://example.com/webhook',
            'webhook_type': 'custom'
        }

        manager = NotificationManager(config)
        manager.send_webhook("Test message", extra_data={'key': 'value'})

        mock_post.assert_called_once()

    @patch('requests.post')
    def test_webhook_retry_on_failure(self, mock_post):
        """Test webhook retry logic on temporary failure."""
        from vhs_upscaler.notifications import NotificationManager

        # Simulate failure then success
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_success = Mock()
        mock_response_success.status_code = 200

        mock_post.side_effect = [mock_response_fail, mock_response_success]

        config = {
            'webhook_url': 'https://discord.com/api/webhooks/123/abc',
            'webhook_type': 'discord',
            'retry_count': 3,
            'retry_delay': 0.1
        }

        manager = NotificationManager(config)
        result = manager.send_webhook("Test message")

        # Should retry and eventually succeed
        self.assertEqual(mock_post.call_count, 2)
        self.assertTrue(result)

    @patch('requests.post')
    def test_webhook_timeout_handling(self, mock_post):
        """Test webhook timeout handling."""
        from vhs_upscaler.notifications import NotificationManager
        import requests

        mock_post.side_effect = requests.Timeout("Request timed out")

        config = {
            'webhook_url': 'https://discord.com/api/webhooks/123/abc',
            'webhook_type': 'discord',
            'timeout': 5
        }

        manager = NotificationManager(config)
        result = manager.send_webhook("Test message")

        # Should handle timeout gracefully
        self.assertFalse(result)

    @patch('requests.post')
    def test_webhook_rate_limiting(self, mock_post):
        """Test handling of rate limit responses."""
        from vhs_upscaler.notifications import NotificationManager

        # Simulate rate limit (429) then success
        mock_response_ratelimit = Mock()
        mock_response_ratelimit.status_code = 429
        mock_response_ratelimit.headers = {'Retry-After': '1'}

        mock_response_success = Mock()
        mock_response_success.status_code = 200

        mock_post.side_effect = [mock_response_ratelimit, mock_response_success]

        config = {
            'webhook_url': 'https://discord.com/api/webhooks/123/abc',
            'webhook_type': 'discord',
            'respect_rate_limits': True
        }

        manager = NotificationManager(config)
        result = manager.send_webhook("Test message")

        # Should respect rate limit and retry
        self.assertTrue(result)


class TestEmailNotifications(unittest.TestCase):
    """Test email notification functionality."""

    @patch('smtplib.SMTP')
    def test_send_email_basic(self, mock_smtp):
        """Test sending basic email notification."""
        from vhs_upscaler.notifications import NotificationManager

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        config = {
            'email_enabled': True,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': 'user@example.com',
            'smtp_password': 'password',
            'email_from': 'user@example.com',
            'email_to': 'admin@example.com'
        }

        manager = NotificationManager(config)
        manager.send_email("Test Subject", "Test Body")

        # Verify SMTP connection
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('user@example.com', 'password')
        mock_server.send_message.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_email_with_html(self, mock_smtp):
        """Test sending email with HTML content."""
        from vhs_upscaler.notifications import NotificationManager

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        config = {
            'email_enabled': True,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email_from': 'user@example.com',
            'email_to': 'admin@example.com'
        }

        manager = NotificationManager(config)
        html_body = "<h1>Test</h1><p>HTML content</p>"
        manager.send_email("Test Subject", "Plain text", html_body=html_body)

        mock_server.send_message.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_email_retry_on_failure(self, mock_smtp):
        """Test email retry logic on temporary failure."""
        from vhs_upscaler.notifications import NotificationManager
        import smtplib

        mock_server = MagicMock()
        mock_server.send_message.side_effect = [
            smtplib.SMTPException("Temporary error"),
            None  # Success on retry
        ]
        mock_smtp.return_value.__enter__.return_value = mock_server

        config = {
            'email_enabled': True,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email_from': 'user@example.com',
            'email_to': 'admin@example.com',
            'retry_count': 3
        }

        manager = NotificationManager(config)
        result = manager.send_email("Test", "Body")

        # Should retry and succeed
        self.assertTrue(result)

    @patch('smtplib.SMTP')
    def test_send_email_authentication_error(self, mock_smtp):
        """Test handling of authentication errors."""
        from vhs_upscaler.notifications import NotificationManager
        import smtplib

        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")
        mock_smtp.return_value.__enter__.return_value = mock_server

        config = {
            'email_enabled': True,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': 'user@example.com',
            'smtp_password': 'wrong_password',
            'email_from': 'user@example.com',
            'email_to': 'admin@example.com'
        }

        manager = NotificationManager(config)
        result = manager.send_email("Test", "Body")

        # Should fail gracefully
        self.assertFalse(result)


class TestNotificationContent(unittest.TestCase):
    """Test notification content formatting."""

    @patch('requests.post')
    def test_format_job_complete_notification(self, mock_post):
        """Test job completion notification formatting."""
        from vhs_upscaler.notifications import NotificationManager

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        config = {
            'webhook_url': 'https://discord.com/api/webhooks/123/abc',
            'webhook_type': 'discord'
        }

        manager = NotificationManager(config)

        job_info = {
            'filename': 'video.mp4',
            'status': 'completed',
            'duration': '5m 30s',
            'output_file': 'output.mp4'
        }

        manager.notify_job_complete(job_info)

        mock_post.assert_called_once()
        # Verify message contains job info
        payload = mock_post.call_args[1]['json']
        message = payload['content']
        self.assertIn('video.mp4', message)
        self.assertIn('completed', message.lower())

    @patch('requests.post')
    def test_format_job_failed_notification(self, mock_post):
        """Test job failure notification formatting."""
        from vhs_upscaler.notifications import NotificationManager

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        config = {
            'webhook_url': 'https://discord.com/api/webhooks/123/abc',
            'webhook_type': 'discord'
        }

        manager = NotificationManager(config)

        job_info = {
            'filename': 'video.mp4',
            'status': 'failed',
            'error': 'FFmpeg encoding error'
        }

        manager.notify_job_failed(job_info)

        mock_post.assert_called_once()
        payload = mock_post.call_args[1]['json']
        message = payload['content']
        self.assertIn('failed', message.lower())
        self.assertIn('error', message.lower())

    @patch('requests.post')
    def test_format_batch_summary_notification(self, mock_post):
        """Test batch processing summary notification."""
        from vhs_upscaler.notifications import NotificationManager

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        config = {
            'webhook_url': 'https://discord.com/api/webhooks/123/abc',
            'webhook_type': 'discord'
        }

        manager = NotificationManager(config)

        batch_info = {
            'total_jobs': 10,
            'completed': 8,
            'failed': 2,
            'total_duration': '1h 23m'
        }

        manager.notify_batch_complete(batch_info)

        mock_post.assert_called_once()
        payload = mock_post.call_args[1]['json']
        message = payload['content']
        self.assertIn('10', message)  # Total jobs
        self.assertIn('8', message)   # Completed
        self.assertIn('2', message)   # Failed

    @patch('requests.post')
    def test_format_with_statistics(self, mock_post):
        """Test notification with processing statistics."""
        from vhs_upscaler.notifications import NotificationManager

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        config = {
            'webhook_url': 'https://discord.com/api/webhooks/123/abc',
            'webhook_type': 'discord'
        }

        manager = NotificationManager(config)

        stats = {
            'filename': 'video.mp4',
            'input_size': '1.2 GB',
            'output_size': '850 MB',
            'compression_ratio': '29%',
            'processing_time': '5m 30s',
            'fps': '30'
        }

        manager.notify_with_stats(stats)

        mock_post.assert_called_once()


class TestNotificationConfiguration(unittest.TestCase):
    """Test notification configuration management."""

    def test_load_config_from_file(self):
        """Test loading notification config from file."""
        from vhs_upscaler.notifications import NotificationManager

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                'webhook_url': 'https://discord.com/api/webhooks/123/abc',
                'webhook_type': 'discord',
                'email_enabled': True,
                'smtp_server': 'smtp.gmail.com'
            }
            json.dump(config, f)
            config_file = f.name

        try:
            manager = NotificationManager.from_config_file(config_file)
            self.assertEqual(manager.webhook_type, 'discord')
            self.assertTrue(manager.email_enabled)
        finally:
            Path(config_file).unlink()

    def test_validate_webhook_url(self):
        """Test webhook URL validation."""
        from vhs_upscaler.notifications import NotificationManager

        # Valid URLs
        valid_urls = [
            'https://discord.com/api/webhooks/123/abc',
            'https://hooks.slack.com/services/T00/B00/XXX',
            'https://example.com/webhook'
        ]

        for url in valid_urls:
            config = {'webhook_url': url, 'webhook_type': 'discord'}
            manager = NotificationManager(config)
            self.assertTrue(manager.validate_webhook_url())

        # Invalid URLs
        invalid_urls = [
            'http://unsecure.com/webhook',  # Not HTTPS
            'not-a-url',
            ''
        ]

        for url in invalid_urls:
            config = {'webhook_url': url, 'webhook_type': 'discord'}
            manager = NotificationManager(config)
            self.assertFalse(manager.validate_webhook_url())

    def test_validate_email_config(self):
        """Test email configuration validation."""
        from vhs_upscaler.notifications import NotificationManager

        # Valid config
        valid_config = {
            'email_enabled': True,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email_from': 'user@example.com',
            'email_to': 'admin@example.com'
        }

        manager = NotificationManager(valid_config)
        self.assertTrue(manager.validate_email_config())

        # Invalid config (missing SMTP server)
        invalid_config = {
            'email_enabled': True,
            'email_from': 'user@example.com',
            'email_to': 'admin@example.com'
        }

        manager = NotificationManager(invalid_config)
        self.assertFalse(manager.validate_email_config())


class TestNotificationEdgeCases(unittest.TestCase):
    """Test edge cases and error scenarios."""

    @patch('requests.post')
    def test_webhook_with_very_long_message(self, mock_post):
        """Test webhook with message exceeding limits."""
        from vhs_upscaler.notifications import NotificationManager

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        config = {
            'webhook_url': 'https://discord.com/api/webhooks/123/abc',
            'webhook_type': 'discord'
        }

        manager = NotificationManager(config)

        # Discord limit is 2000 characters
        very_long_message = "x" * 3000

        manager.send_webhook(very_long_message)

        # Should truncate message
        payload = mock_post.call_args[1]['json']
        self.assertLessEqual(len(payload['content']), 2000)

    @patch('requests.post')
    def test_webhook_with_special_characters(self, mock_post):
        """Test webhook with special characters and emojis."""
        from vhs_upscaler.notifications import NotificationManager

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        config = {
            'webhook_url': 'https://discord.com/api/webhooks/123/abc',
            'webhook_type': 'discord'
        }

        manager = NotificationManager(config)

        special_message = "Test with emojis: 🎬 🎥 ✅ and chars: <>&\""

        manager.send_webhook(special_message)

        # Should handle special characters
        mock_post.assert_called_once()

    @patch('smtplib.SMTP')
    def test_email_with_multiple_recipients(self, mock_smtp):
        """Test sending email to multiple recipients."""
        from vhs_upscaler.notifications import NotificationManager

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        config = {
            'email_enabled': True,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email_from': 'user@example.com',
            'email_to': ['admin1@example.com', 'admin2@example.com']
        }

        manager = NotificationManager(config)
        manager.send_email("Test", "Body")

        # Verify email sent to all recipients
        mock_server.send_message.assert_called_once()

    def test_disabled_notifications(self):
        """Test that no notifications sent when disabled."""
        from vhs_upscaler.notifications import NotificationManager

        config = {
            'notifications_enabled': False,
            'webhook_url': 'https://discord.com/api/webhooks/123/abc'
        }

        manager = NotificationManager(config)

        with patch('requests.post') as mock_post:
            manager.send_webhook("Test")
            # Should not call webhook when disabled
            mock_post.assert_not_called()


if __name__ == '__main__':
    unittest.main()
