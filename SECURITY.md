# Security Policy

## Supported Versions

We actively support the following versions of TerminalAI with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.4.x   | :white_check_mark: |
| 1.3.x   | :white_check_mark: |
| 1.2.x   | :x:                |
| < 1.2   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### 1. Do Not Open a Public Issue

Please **do not** open a public GitHub issue for security vulnerabilities. This helps prevent malicious actors from exploiting the vulnerability before a fix is available.

### 2. Report Privately

Report security vulnerabilities through one of these channels:

- **Preferred:** Use GitHub's private vulnerability reporting feature
  - Go to the [Security tab](https://github.com/parthalon025/terminalai/security)
  - Click "Report a vulnerability"

- **Alternative:** Email the maintainers directly
  - Subject: "[SECURITY] TerminalAI Vulnerability Report"
  - Include detailed information about the vulnerability

### 3. Include in Your Report

Please provide as much information as possible:

- **Type of vulnerability** (e.g., code injection, path traversal, etc.)
- **Affected version(s)** (e.g., v1.4.2, all versions, etc.)
- **Location of the issue** (file path and line number if possible)
- **Step-by-step instructions** to reproduce the vulnerability
- **Proof of concept** (if applicable)
- **Impact assessment** (what could an attacker achieve?)
- **Suggested fix** (if you have one)

### 4. What to Expect

- **Acknowledgment:** We will acknowledge receipt within 48 hours
- **Assessment:** We will assess the vulnerability within 7 days
- **Updates:** We will keep you informed of our progress
- **Fix timeline:** Critical issues will be patched within 14 days
- **Credit:** We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices for Users

### Safe Installation

```bash
# Always verify you're installing from the official repository
git clone https://github.com/parthalon025/terminalai.git
cd terminalai

# Verify the repository authenticity
git remote -v

# Install in a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

pip install -e .
```

### Input Validation

TerminalAI processes video files and URLs. To minimize security risks:

1. **Only process videos from trusted sources**
   - Malicious video files could potentially exploit codec vulnerabilities
   - Use antivirus scanning on downloaded content

2. **Validate YouTube URLs**
   - Only download from legitimate YouTube URLs
   - The application uses yt-dlp, which includes URL validation

3. **Avoid processing untrusted user-provided paths**
   - Be cautious when processing files from untrusted users
   - Use sandboxed environments for untrusted content

### File Permissions

TerminalAI creates temporary files during processing:

```bash
# Default temporary directory (cleaned automatically)
# Linux/Mac: /tmp/vhs_upscaler_*
# Windows: %TEMP%\vhs_upscaler_*

# Ensure proper permissions on output directories
chmod 750 output_directory  # Owner: rwx, Group: r-x, Others: none
```

### Network Security

When using YouTube download features:

- **HTTPS only:** yt-dlp uses HTTPS by default
- **No credential storage:** TerminalAI does not store authentication credentials
- **Proxy support:** Use `--proxy` flag for yt-dlp if needed

### Dependencies

Keep dependencies updated for security patches:

```bash
# Update to latest compatible versions
pip install --upgrade yt-dlp pyyaml gradio

# Security audit
pip install pip-audit
pip-audit

# Check for outdated packages
pip list --outdated
```

## Known Security Considerations

### 1. FFmpeg Vulnerabilities

**Issue:** TerminalAI relies on FFmpeg for video processing. FFmpeg has had security vulnerabilities in the past.

**Mitigation:**
- Keep FFmpeg updated to the latest version
- Linux: `sudo apt update && sudo apt upgrade ffmpeg`
- macOS: `brew upgrade ffmpeg`
- Windows: `winget upgrade FFmpeg`

**Current requirement:** FFmpeg 4.0+ (latest recommended)

### 2. Subprocess Execution

**Issue:** The application executes external binaries (FFmpeg, Maxine, Real-ESRGAN).

**Mitigation:**
- All subprocess calls use argument lists (not shell=True)
- Input sanitization prevents command injection
- Paths are validated before execution

**Code example:**
```python
# Safe subprocess call (used in TerminalAI)
subprocess.run(["ffmpeg", "-i", input_file, output_file], check=True)

# Unsafe (NOT used in TerminalAI)
# subprocess.run(f"ffmpeg -i {input_file} {output_file}", shell=True)
```

### 3. Temporary File Handling

**Issue:** Temporary files could be intercepted or modified.

**Mitigation:**
- Uses Python's `tempfile` module with secure defaults
- Temporary files use unique, unpredictable names
- Cleanup in `finally` blocks ensures removal
- Windows: Inherits user's permissions
- Linux/Mac: Uses 0600 permissions (owner-only)

### 4. Path Traversal

**Issue:** Malicious input paths could access unintended files.

**Mitigation:**
- Path validation using `pathlib.Path.resolve()`
- Relative path resolution prevents directory traversal
- Output directory sanitization

### 5. YAML Configuration

**Issue:** PyYAML can execute arbitrary Python code if used unsafely.

**Mitigation:**
- Uses `yaml.safe_load()` (not `yaml.load()`)
- Configuration files are not user-editable via web interface
- Schema validation on configuration values

## Security Features

### 1. Input Sanitization

All user inputs are sanitized:

- File paths: Resolved to absolute paths, validated
- URLs: Validated by yt-dlp before downloading
- Configuration values: Type-checked and range-validated
- Preset names: Whitelist-based validation

### 2. Sandboxing Recommendations

For processing untrusted content, consider:

```bash
# Docker isolation (recommended for untrusted content)
docker run --rm -v $(pwd):/data terminalai \
  python -m vhs_upscaler.vhs_upscale -i /data/untrusted.mp4 -o /data/output.mp4

# Firejail (Linux)
firejail --private --net=none python -m vhs_upscaler.vhs_upscale -i video.mp4 -o out.mp4
```

### 3. Network Isolation

The web GUI (Gradio) binds to localhost by default:

```python
# Default: Only accessible from local machine
app.launch(server_name="127.0.0.1", server_port=7860)

# To expose (use with caution, behind firewall/VPN)
# app.launch(server_name="0.0.0.0", server_port=7860)
```

## Dependency Security

### Automated Scanning

We use the following automated security tools:

- **pip-audit:** Weekly scans for known vulnerabilities
- **GitHub Dependabot:** Automated dependency updates
- **GitHub CodeQL:** Static analysis security scanning
- **Dependency Review Action:** PR-based dependency checks

### Current Status

Last security audit: 2025-12-18
Known vulnerabilities: **0 critical, 0 high, 0 medium**

See: [DEPENDENCY_AUDIT_REPORT.md](DEPENDENCY_AUDIT_REPORT.md)

### Manual Review Schedule

- **Weekly:** Dependency security scans (automated)
- **Monthly:** Manual code review of security-critical sections
- **Quarterly:** Full security audit and penetration testing
- **Per-release:** Security checklist verification

## Secure Development Practices

### Code Review Checklist

Before merging security-sensitive code:

- [ ] No `shell=True` in subprocess calls
- [ ] All file paths validated and sanitized
- [ ] YAML uses `safe_load()` not `load()`
- [ ] No hardcoded credentials or secrets
- [ ] Input validation on all user-provided data
- [ ] Proper error handling (no info leakage)
- [ ] Temporary files cleaned up properly
- [ ] Tests include security test cases

### Pre-commit Hooks

Install security-focused pre-commit hooks:

```bash
pip install pre-commit
pre-commit install

# Hooks include:
# - Ruff (linting, including security rules)
# - Black (code formatting)
# - Check for secrets/credentials
# - Check for large files
# - YAML validation
```

## Security Advisories

Security advisories will be published at:
- GitHub Security Advisories: https://github.com/parthalon025/terminalai/security/advisories
- Release notes: https://github.com/parthalon025/terminalai/releases

Subscribe to the repository to receive notifications.

## Responsible Disclosure

We appreciate security researchers who:

- Follow responsible disclosure practices
- Give us reasonable time to fix vulnerabilities
- Do not exploit vulnerabilities for personal gain
- Help us improve the security of TerminalAI

**Thank you for helping keep TerminalAI and its users safe!**

---

Last updated: 2025-12-18
Version: 1.4.2
