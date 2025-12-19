"""
Notification System for TerminalAI
==================================
Sends notifications via webhooks (Discord/Slack) and email when jobs complete or fail.

Supports:
- Generic webhook notifications (Discord, Slack, custom)
- Email notifications via SMTP
- Job completion and error alerts
- Configuration via YAML or environment variables
- Automatic retry with exponential backoff
"""

import logging
import os
import smtplib
import time
import traceback
from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class NotificationConfig:
    """Configuration for notification system."""

    # Webhook settings
    webhook_enabled: bool = False
    webhook_url: Optional[str] = None

    # Email settings
    email_enabled: bool = False
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None
    to_email: Optional[str] = None
    use_tls: bool = True

    # Notification preferences
    notify_on_complete: bool = True
    notify_on_error: bool = True
    notify_on_batch_complete: bool = True

    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0  # Initial delay in seconds

    @classmethod
    def from_dict(cls, data: dict) -> 'NotificationConfig':
        """Create config from dictionary."""
        return cls(
            webhook_enabled=data.get('webhook', {}).get('enabled', False),
            webhook_url=data.get('webhook', {}).get('url'),
            email_enabled=data.get('email', {}).get('enabled', False),
            smtp_server=data.get('email', {}).get('smtp_server'),
            smtp_port=data.get('email', {}).get('smtp_port', 587),
            smtp_user=data.get('email', {}).get('smtp_user'),
            smtp_password=data.get('email', {}).get('smtp_password'),
            from_email=data.get('email', {}).get('from_email'),
            to_email=data.get('email', {}).get('to_email'),
            use_tls=data.get('email', {}).get('use_tls', True),
            notify_on_complete=data.get('notify_on_complete', True),
            notify_on_error=data.get('notify_on_error', True),
            notify_on_batch_complete=data.get('notify_on_batch_complete', True),
        )

    @classmethod
    def from_yaml(cls, config_path: Path) -> 'NotificationConfig':
        """Load config from YAML file."""
        if not HAS_YAML:
            logger.warning("PyYAML not installed, using default notification config")
            return cls()

        try:
            with open(config_path) as f:
                data = yaml.safe_load(f)

            notifications = data.get('notifications', {})
            if not notifications.get('enabled', False):
                return cls()

            return cls.from_dict(notifications)
        except Exception as e:
            logger.warning(f"Failed to load notification config from YAML: {e}")
            return cls()

    @classmethod
    def from_env(cls) -> 'NotificationConfig':
        """Load config from environment variables."""
        webhook_url = os.getenv('TERMINALAI_WEBHOOK_URL')
        smtp_server = os.getenv('TERMINALAI_SMTP_SERVER')

        return cls(
            webhook_enabled=bool(webhook_url),
            webhook_url=webhook_url,
            email_enabled=bool(smtp_server),
            smtp_server=smtp_server,
            smtp_port=int(os.getenv('TERMINALAI_SMTP_PORT', '587')),
            smtp_user=os.getenv('TERMINALAI_SMTP_USER'),
            smtp_password=os.getenv('TERMINALAI_SMTP_PASSWORD'),
            from_email=os.getenv('TERMINALAI_EMAIL_FROM'),
            to_email=os.getenv('TERMINALAI_EMAIL_TO'),
            use_tls=os.getenv('TERMINALAI_SMTP_TLS', 'true').lower() == 'true',
        )


# ============================================================================
# Notifier Class
# ============================================================================

class Notifier:
    """
    Unified notification handler for webhooks and email.

    Usage:
        notifier = Notifier()
        notifier.notify_complete({
            'filename': 'video.mp4',
            'status': 'Success',
            'duration': '15m 32s',
        })
    """

    def __init__(self, config: Optional[NotificationConfig] = None, config_path: Optional[Path] = None):
        """
        Initialize notifier.

        Args:
            config: Notification configuration (if None, loads from YAML or env)
            config_path: Path to config.yaml file (default: vhs_upscaler/config.yaml)
        """
        if config:
            self.config = config
        elif config_path and config_path.exists():
            self.config = NotificationConfig.from_yaml(config_path)
        else:
            # Try default config path
            default_path = Path(__file__).parent / 'config.yaml'
            if default_path.exists():
                yaml_config = NotificationConfig.from_yaml(default_path)
                # Merge with environment variables (env takes precedence)
                env_config = NotificationConfig.from_env()
                if env_config.webhook_url or env_config.smtp_server:
                    self.config = env_config
                else:
                    self.config = yaml_config
            else:
                self.config = NotificationConfig.from_env()

        self._validate_config()

    def _validate_config(self):
        """Validate configuration and log warnings."""
        if self.config.webhook_enabled and not self.config.webhook_url:
            logger.warning("Webhook enabled but no URL provided")
            self.config.webhook_enabled = False

        if self.config.webhook_enabled and not HAS_REQUESTS:
            logger.warning("Webhook enabled but 'requests' library not installed. Install with: pip install requests")
            self.config.webhook_enabled = False

        if self.config.webhook_enabled and self.config.webhook_url:
            if not self._validate_webhook_url(self.config.webhook_url):
                logger.warning(f"Invalid webhook URL: {self.config.webhook_url}")
                self.config.webhook_enabled = False

        if self.config.email_enabled and not all([
            self.config.smtp_server,
            self.config.smtp_user,
            self.config.smtp_password,
            self.config.from_email,
            self.config.to_email,
        ]):
            logger.warning("Email enabled but missing required SMTP configuration")
            self.config.email_enabled = False

    def _validate_webhook_url(self, url: str) -> bool:
        """Validate webhook URL format."""
        if not url:
            return False
        return url.startswith('http://') or url.startswith('https://')

    def is_enabled(self) -> bool:
        """Check if any notification method is enabled."""
        return self.config.webhook_enabled or self.config.email_enabled

    # ========================================================================
    # Public Notification Methods
    # ========================================================================

    def notify_complete(self, job_info: Dict[str, Any]) -> bool:
        """
        Send job completion notification.

        Args:
            job_info: Job information dictionary with keys:
                - filename: Input filename
                - status: Job status (e.g., "Success")
                - duration: Processing duration
                - input_size: Input file size (optional)
                - output_size: Output file size (optional)
                - resolution: Target resolution (optional)
                - preset: Processing preset (optional)
                - output_path: Output file path (optional)

        Returns:
            True if at least one notification sent successfully
        """
        if not self.config.notify_on_complete:
            return False

        title = "Video Processing Complete"
        filename = job_info.get('filename', 'Unknown')

        # Build message
        fields = []
        fields.append({"name": "File", "value": filename, "inline": False})
        fields.append({"name": "Status", "value": job_info.get('status', 'Complete'), "inline": True})
        fields.append({"name": "Duration", "value": job_info.get('duration', 'N/A'), "inline": True})

        if 'resolution' in job_info:
            fields.append({"name": "Resolution", "value": f"{job_info['resolution']}p", "inline": True})

        if 'preset' in job_info:
            fields.append({"name": "Preset", "value": job_info['preset'], "inline": True})

        if 'input_size' in job_info:
            fields.append({"name": "Input Size", "value": job_info['input_size'], "inline": True})

        if 'output_size' in job_info:
            fields.append({"name": "Output Size", "value": job_info['output_size'], "inline": True})

        if 'output_path' in job_info:
            fields.append({"name": "Output", "value": job_info['output_path'], "inline": False})

        # Color: Green for success
        webhook_message = {
            "title": title,
            "description": f"Successfully processed: **{filename}**",
            "color": 3066993,  # Green
            "fields": fields,
        }

        # Email body
        email_body = self._format_email_body(title, fields)

        # Send notifications
        webhook_sent = False
        email_sent = False

        if self.config.webhook_enabled:
            webhook_sent = self.send_webhook(webhook_message)

        if self.config.email_enabled:
            email_sent = self.send_email(title, email_body)

        return webhook_sent or email_sent

    def notify_error(self, error_info: Dict[str, Any]) -> bool:
        """
        Send error notification.

        Args:
            error_info: Error information dictionary with keys:
                - filename: Input filename
                - error: Error message
                - traceback: Full traceback (optional)
                - stage: Processing stage where error occurred (optional)

        Returns:
            True if at least one notification sent successfully
        """
        if not self.config.notify_on_error:
            return False

        title = "Video Processing Failed"
        filename = error_info.get('filename', 'Unknown')
        error_msg = error_info.get('error', 'Unknown error')

        # Build message
        fields = []
        fields.append({"name": "File", "value": filename, "inline": False})
        fields.append({"name": "Error", "value": error_msg[:1024], "inline": False})

        if 'stage' in error_info:
            fields.append({"name": "Stage", "value": error_info['stage'], "inline": True})

        # Color: Red for error
        webhook_message = {
            "title": title,
            "description": f"Failed to process: **{filename}**",
            "color": 15158332,  # Red
            "fields": fields,
        }

        # Email body (include full traceback if available)
        email_fields = fields.copy()
        if 'traceback' in error_info:
            email_fields.append({"name": "Traceback", "value": f"```\n{error_info['traceback'][:2000]}\n```", "inline": False})

        email_body = self._format_email_body(title, email_fields)

        # Send notifications
        webhook_sent = False
        email_sent = False

        if self.config.webhook_enabled:
            webhook_sent = self.send_webhook(webhook_message)

        if self.config.email_enabled:
            email_sent = self.send_email(title, email_body)

        return webhook_sent or email_sent

    def notify_batch_complete(self, batch_info: Dict[str, Any]) -> bool:
        """
        Send batch processing completion notification.

        Args:
            batch_info: Batch information dictionary with keys:
                - total: Total jobs
                - completed: Successfully completed jobs
                - failed: Failed jobs
                - duration: Total duration
                - total_size: Total output size (optional)

        Returns:
            True if at least one notification sent successfully
        """
        if not self.config.notify_on_batch_complete:
            return False

        title = "Batch Processing Complete"
        total = batch_info.get('total', 0)
        completed = batch_info.get('completed', 0)
        failed = batch_info.get('failed', 0)

        # Build message
        fields = []
        fields.append({"name": "Total Jobs", "value": str(total), "inline": True})
        fields.append({"name": "Completed", "value": str(completed), "inline": True})
        fields.append({"name": "Failed", "value": str(failed), "inline": True})
        fields.append({"name": "Duration", "value": batch_info.get('duration', 'N/A'), "inline": True})

        if 'total_size' in batch_info:
            fields.append({"name": "Total Output", "value": batch_info['total_size'], "inline": True})

        # Color: Blue for batch complete
        color = 3447003 if failed == 0 else 15105570  # Blue if all success, Orange if some failed

        webhook_message = {
            "title": title,
            "description": f"Processed {completed}/{total} videos successfully",
            "color": color,
            "fields": fields,
        }

        email_body = self._format_email_body(title, fields)

        # Send notifications
        webhook_sent = False
        email_sent = False

        if self.config.webhook_enabled:
            webhook_sent = self.send_webhook(webhook_message)

        if self.config.email_enabled:
            email_sent = self.send_email(title, email_body)

        return webhook_sent or email_sent

    # ========================================================================
    # Webhook Methods
    # ========================================================================

    def send_webhook(self, message: Dict[str, Any]) -> bool:
        """
        Send webhook notification with retry logic.

        Args:
            message: Message dictionary with:
                - title: Message title
                - description: Message description
                - color: Embed color (decimal)
                - fields: List of field dictionaries

        Returns:
            True if sent successfully
        """
        if not self.config.webhook_enabled or not HAS_REQUESTS:
            return False

        # Build Discord-compatible embed
        payload = {
            "embeds": [{
                "title": message.get("title", "TerminalAI Notification"),
                "description": message.get("description", ""),
                "color": message.get("color", 3066993),
                "fields": message.get("fields", []),
                "footer": {"text": "TerminalAI v1.4.2"},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            }]
        }

        # Retry with exponential backoff
        for attempt in range(self.config.max_retries):
            try:
                response = requests.post(
                    self.config.webhook_url,
                    json=payload,
                    timeout=10
                )
                response.raise_for_status()
                logger.debug(f"Webhook notification sent successfully")
                return True

            except requests.exceptions.RequestException as e:
                delay = self.config.retry_delay * (2 ** attempt)
                logger.warning(f"Webhook send failed (attempt {attempt + 1}/{self.config.max_retries}): {e}")

                if attempt < self.config.max_retries - 1:
                    logger.debug(f"Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to send webhook after {self.config.max_retries} attempts")

        return False

    # ========================================================================
    # Email Methods
    # ========================================================================

    def send_email(self, subject: str, body: str) -> bool:
        """
        Send email notification.

        Args:
            subject: Email subject
            body: Email body (plain text or HTML)

        Returns:
            True if sent successfully
        """
        if not self.config.email_enabled:
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config.from_email
            msg['To'] = self.config.to_email
            msg['Subject'] = f"[TerminalAI] {subject}"

            # Attach body
            msg.attach(MIMEText(body, 'plain'))

            # Send via SMTP
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port, timeout=30) as server:
                if self.config.use_tls:
                    server.starttls()

                server.login(self.config.smtp_user, self.config.smtp_password)
                server.send_message(msg)

            logger.debug(f"Email notification sent successfully to {self.config.to_email}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"Failed to send email: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def _format_email_body(self, title: str, fields: list) -> str:
        """Format email body from fields."""
        lines = [title, "=" * len(title), ""]

        for field in fields:
            name = field.get('name', '')
            value = field.get('value', '')
            # Remove markdown formatting for plain text
            value = value.replace('**', '').replace('```', '').strip()
            lines.append(f"{name}: {value}")

        lines.append("")
        lines.append("---")
        lines.append("Sent by TerminalAI v1.4.2")

        return "\n".join(lines)

    def test_webhook(self) -> bool:
        """Test webhook configuration."""
        if not self.config.webhook_enabled:
            logger.error("Webhook not enabled")
            return False

        test_message = {
            "title": "Test Notification",
            "description": "This is a test notification from TerminalAI",
            "color": 3447003,  # Blue
            "fields": [
                {"name": "Status", "value": "Testing webhook configuration", "inline": False},
            ],
        }

        result = self.send_webhook(test_message)
        if result:
            logger.info("Webhook test successful")
        else:
            logger.error("Webhook test failed")

        return result

    def test_email(self) -> bool:
        """Test email configuration."""
        if not self.config.email_enabled:
            logger.error("Email not enabled")
            return False

        subject = "Test Notification"
        body = "This is a test notification from TerminalAI\n\nIf you received this, email notifications are working correctly."

        result = self.send_email(subject, body)
        if result:
            logger.info(f"Email test successful (sent to {self.config.to_email})")
        else:
            logger.error("Email test failed")

        return result


# ============================================================================
# Utility Functions
# ============================================================================

def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.0f}m {seconds % 60:.0f}s"
    else:
        hours = seconds / 3600
        minutes = (seconds % 3600) / 60
        return f"{hours:.0f}h {minutes:.0f}m"
