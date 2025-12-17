# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of TerminalAI seriously. If you believe you have found a
security vulnerability, please report it to us as described below.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via GitHub's private vulnerability reporting:

1. Go to the
   [Security Advisories page](https://github.com/parthalon025/terminalai/security/advisories)
2. Click "Report a vulnerability"
3. Fill out the form with details about the vulnerability

Alternatively, you can email security concerns to: [security@example.com]

### What to Include

Please include the following information in your report:

- **Type of issue** (e.g., buffer overflow, SQL injection, cross-site scripting,
  etc.)
- **Full paths of source file(s)** related to the manifestation of the issue
- **Location of the affected source code** (tag/branch/commit or direct URL)
- **Step-by-step instructions** to reproduce the issue
- **Proof-of-concept or exploit code** (if possible)
- **Impact of the issue**, including how an attacker might exploit the issue

### Response Timeline

- **Initial Response**: Within 48 hours
- **Progress Update**: Within 7 days
- **Resolution Target**: Within 90 days (for non-critical issues)
- **Critical Issues**: Addressed as soon as possible

### Disclosure Policy

- We will confirm the vulnerability and determine its impact
- We will release a fix as soon as possible, depending on complexity
- We will publicly disclose the vulnerability after a fix is available
- We will credit the reporter (unless they prefer to remain anonymous)

## Security Best Practices

When using TerminalAI:

### API Keys and Secrets

- Never commit API keys to version control
- Use environment variables for sensitive configuration
- Rotate API keys regularly
- Use the minimum required permissions

### Environment Configuration

- Keep your Node.js version up to date
- Regularly update dependencies (`pnpm update`)
- Review security advisories for dependencies

### Network Security

- Use HTTPS for all external communications
- Be cautious with custom API endpoints
- Review network requests in sensitive environments

## Security Features

TerminalAI includes the following security measures:

- **No credential storage**: API keys are not stored persistently
- **Environment variable support**: Sensitive data via environment variables
- **Input sanitization**: All user input is validated
- **Dependency scanning**: Automated vulnerability scanning in CI/CD
- **Code analysis**: Static analysis with CodeQL and Semgrep

## Known Security Considerations

### AI Integration

- AI responses may contain inaccurate information
- Do not execute AI-generated code without review
- Be cautious with sensitive data in AI prompts

### Local Execution

- CLI commands run with your user permissions
- Review any file operations before confirming

## Security Updates

Security updates are published through:

- GitHub Security Advisories
- Release notes on GitHub Releases
- npm package updates

Subscribe to repository notifications to stay informed about security updates.

## Recognition

We appreciate the security research community and will acknowledge contributors
who help improve TerminalAI's security (with their permission).

Thank you for helping keep TerminalAI and its users safe!
