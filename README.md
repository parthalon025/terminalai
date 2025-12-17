# TerminalAI

An AI-powered terminal assistant for developers.

[![CI](https://github.com/parthalon025/terminalai/actions/workflows/ci.yml/badge.svg)](https://github.com/parthalon025/terminalai/actions/workflows/ci.yml)
[![Security](https://github.com/parthalon025/terminalai/actions/workflows/security.yml/badge.svg)](https://github.com/parthalon025/terminalai/actions/workflows/security.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- AI-powered command suggestions
- Interactive terminal chat
- Context-aware assistance
- Cross-platform support (Linux, macOS, Windows)

## Installation

```bash
npm install -g terminalai
# or
pnpm add -g terminalai
```

## Quick Start

```bash
# Basic usage
terminalai "How do I find large files?"

# Interactive mode
terminalai --interactive

# Get help
terminalai --help
```

## Development

### Prerequisites

- Node.js 20.x or higher
- pnpm 8.x or higher

### Setup

```bash
# Clone the repository
git clone https://github.com/parthalon025/terminalai.git
cd terminalai

# Install dependencies
pnpm install

# Build
pnpm build

# Run in development mode
pnpm dev
```

### Scripts

| Command                 | Description              |
| ----------------------- | ------------------------ |
| `pnpm dev`              | Start development mode   |
| `pnpm build`            | Build for production     |
| `pnpm test`             | Run all tests            |
| `pnpm test:unit`        | Run unit tests           |
| `pnpm test:integration` | Run integration tests    |
| `pnpm test:e2e`         | Run E2E tests            |
| `pnpm lint`             | Run ESLint               |
| `pnpm format`           | Format with Prettier     |
| `pnpm type-check`       | TypeScript type checking |

## Project Structure

```
terminalai/
├── .github/
│   ├── workflows/         # CI/CD pipelines
│   │   ├── ci.yml        # Main CI pipeline
│   │   ├── security.yml  # Security scanning
│   │   └── release.yml   # Release automation
│   ├── ISSUE_TEMPLATE/   # Issue templates
│   └── dependabot.yml    # Dependency updates
├── src/                  # Source code
├── tests/                # Test suites
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── e2e/             # End-to-end tests
├── docs/                 # Documentation
└── dist/                 # Build output
```

## CI/CD Pipeline

This project includes a comprehensive CI/CD pipeline:

### Continuous Integration

- **Linting & Formatting**: ESLint + Prettier checks
- **Type Checking**: TypeScript strict mode
- **Unit Tests**: Vitest with coverage reporting
- **Integration Tests**: Component interaction testing
- **E2E Tests**: Cross-platform testing (Linux, macOS, Windows)

### Security Scanning

- **CodeQL**: Static application security testing (SAST)
- **Snyk**: Dependency vulnerability scanning
- **Gitleaks**: Secret detection
- **OWASP Dependency Check**: Known vulnerability detection
- **License Compliance**: License compatibility checking

### Release Automation

- Multi-platform binary builds
- Automatic GitHub releases
- npm package publishing
- Changelog generation

## Quality Standards

- **Code Coverage**: 80% minimum
- **Type Safety**: Strict TypeScript
- **Security**: Automated vulnerability scanning
- **Documentation**: Comprehensive docs

See [CI/CD QC Plan](docs/CI_CD_QC_PLAN.md) for full details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for
guidelines.

## Security

For security concerns, please see [SECURITY.md](SECURITY.md).

## License

MIT License - see [LICENSE](LICENSE) for details.
