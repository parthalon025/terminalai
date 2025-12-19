# Rust Auto-Installation for DeepFilterNet

## Overview

The TerminalAI installer now automatically detects and installs the Rust compiler when needed for DeepFilterNet audio AI features. This eliminates the need for manual Rust installation and provides a seamless setup experience.

## What is DeepFilterNet?

DeepFilterNet is an AI-powered audio denoising tool that provides superior speech clarity for VHS tape restoration. It requires the Rust compiler to build during pip installation.

## How It Works

### Detection Flow

1. When you run `python install.py --audio` or `python install.py --full`
2. The installer checks if Rust is already installed
3. If Rust is not found, it automatically downloads and installs it
4. After Rust installation, DeepFilterNet is installed via pip
5. Installation continues with other audio features

### Platform-Specific Installation

#### Windows
```
1. Downloads rustup-init.exe from https://win.rustup.rs/x86_64
2. Runs silent installation: rustup-init.exe -y --default-toolchain stable
3. Adds %USERPROFILE%\.cargo\bin to PATH
4. Proceeds with DeepFilterNet installation
```

#### Linux/macOS
```
1. Uses curl to download: https://sh.rustup.rs
2. Pipes to shell: sh -s -- -y
3. Adds ~/.cargo/bin to PATH
4. Proceeds with DeepFilterNet installation
```

## Installation Commands

### Recommended: Full Installation with Audio AI

```bash
# Installs everything including Rust (if needed) and DeepFilterNet
python scripts/installation/install.py --full
```

### Audio Features Only

```bash
# Installs audio AI features with automatic Rust installation
python scripts/installation/install.py --audio
```

### Basic Installation (No Rust)

```bash
# Skips audio AI features, no Rust installation
python scripts/installation/install.py
```

## What Gets Installed

When Rust auto-installation is triggered:

1. **Rust Compiler** (rustc)
   - Latest stable version
   - Installed to `~/.cargo/` (or `%USERPROFILE%\.cargo\` on Windows)

2. **Cargo Package Manager**
   - Rust's package manager and build tool
   - Automatically included with Rust

3. **PATH Updates**
   - Cargo bin directory added to PATH
   - Available for current session and future sessions

4. **DeepFilterNet**
   - Installed via pip after Rust is available
   - Includes all required dependencies

## Timeouts and Error Handling

### Installation Timeouts

- **Rust Installation**: 10 minutes (600 seconds)
  - Sufficient for download and compilation on most systems
  - If timeout occurs, installation continues but DeepFilterNet is skipped

- **DeepFilterNet Installation**: 5 minutes (300 seconds)
  - Building from source can be slow on some systems
  - Timeout results in warning, not fatal error

### Error Recovery

The installer handles errors gracefully:

```python
# If Rust installation fails
→ Warning added: "Failed to install Rust - skipping deepfilternet"
→ Installation continues with other features

# If DeepFilterNet installation fails
→ Warning added: "Failed to install deepfilternet (optional)"
→ Other audio features (Demucs, AudioSR) still attempted
```

## Verification

### Check if Rust is Installed

```bash
# Check Rust version
rustc --version

# Check Cargo version
cargo --version

# Expected output:
# rustc 1.x.x (xxxxx 20xx-xx-xx)
# cargo 1.x.x (xxxxx 20xx-xx-xx)
```

### Check if DeepFilterNet is Installed

```bash
# Test import
python -c "import deepfilternet; print('DeepFilterNet available')"

# Expected output:
# DeepFilterNet available
```

### Run Installation Verification

```bash
# Comprehensive verification including DeepFilterNet
python scripts/installation/verify_installation.py

# Check audio features specifically
python scripts/installation/verify_installation.py --check deepfilternet
```

## Troubleshooting

### Windows: "rustup-init.exe download failed"

**Cause**: Network connectivity or firewall blocking download

**Solutions**:
```bash
# Option 1: Manual Rust installation
# Download from https://rustup.rs/
# Then rerun: python install.py --audio

# Option 2: Check firewall settings
# Allow Python to download files

# Option 3: Install with pre-installed Rust
# Install Rust manually first: https://rustup.rs/
# Then run: python install.py --audio
```

### Linux/macOS: "curl not found"

**Cause**: curl is not installed on the system

**Solutions**:
```bash
# Debian/Ubuntu
sudo apt install curl
python install.py --audio

# Fedora/RHEL
sudo dnf install curl
python install.py --audio

# macOS (usually pre-installed, but if needed)
brew install curl
python install.py --audio

# Alternative: Manual Rust installation
# Visit https://rustup.rs/ for manual instructions
```

### "Rust installation timed out"

**Cause**: Slow network or system performance

**Solutions**:
```bash
# Check if Rust installed despite timeout
rustc --version

# If Rust is available, just rerun installer
python install.py --audio

# If Rust is not available, install manually
# Windows: Download from https://rustup.rs/
# Linux/macOS: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### "DeepFilterNet installation failed even with Rust installed"

**Cause**: Build dependencies missing or PyTorch not installed

**Solutions**:
```bash
# Check PyTorch installation
python -c "import torch; print(torch.__version__)"

# If PyTorch missing, install it first
pip install torch torchaudio

# Then retry DeepFilterNet
pip install deepfilternet>=0.5.0

# Windows: May need Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### PATH Not Updated After Installation

**Cause**: Environment variables not refreshed

**Solutions**:
```bash
# Windows: Restart terminal or manually add to PATH
# Add: %USERPROFILE%\.cargo\bin

# Linux/macOS: Source cargo env
source ~/.cargo/env

# Or restart terminal to pick up PATH changes
```

## Manual Rust Installation (Alternative)

If automatic installation fails, you can install Rust manually:

### Windows

1. Download rustup-init.exe from https://rustup.rs/
2. Run the installer
3. Follow on-screen instructions
4. Restart terminal
5. Run `python install.py --audio`

### Linux/macOS

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Source the environment
source ~/.cargo/env

# Verify installation
rustc --version

# Run TerminalAI installer
python install.py --audio
```

## Advanced Configuration

### Custom Rust Installation Location

By default, Rust installs to `~/.cargo/`. To use a custom location:

```bash
# Set CARGO_HOME before installation
export CARGO_HOME=/custom/path/.cargo
export RUSTUP_HOME=/custom/path/.rustup

# Then run installer
python install.py --audio
```

### Offline Installation

For systems without internet access:

1. On a system with internet, download:
   - Rust installer (rustup-init)
   - DeepFilterNet wheel file

2. Transfer files to offline system

3. Install Rust manually:
   ```bash
   # Windows
   rustup-init.exe -y

   # Linux/macOS
   sh rustup-init.sh -y
   ```

4. Install DeepFilterNet from wheel:
   ```bash
   pip install deepfilternet-0.5.x-py3-none-any.whl
   ```

## Performance Considerations

### Installation Time

- **Rust Installation**: 2-5 minutes
  - Download: 30-60 seconds
  - Installation: 1-4 minutes

- **DeepFilterNet Build**: 3-8 minutes
  - Compiling Rust components
  - Building Python bindings

**Total**: Expect 5-15 minutes for first-time installation

### Disk Space Requirements

- **Rust Toolchain**: ~1.5 GB
  - Compiler, standard library, docs

- **DeepFilterNet**: ~200 MB
  - Compiled binaries and models

**Total**: ~1.7 GB additional disk space

## Benefits of Automatic Installation

1. **User-Friendly**: No manual Rust installation needed
2. **Error-Free**: Correct Rust version automatically selected
3. **PATH Handling**: Environment variables updated automatically
4. **Cross-Platform**: Works on Windows, Linux, and macOS
5. **Fallback Strategy**: Continues installation even if Rust fails
6. **Logging**: Clear progress messages and error diagnostics

## Security Considerations

The installer downloads Rust from official sources:

- **Windows**: https://win.rustup.rs/x86_64 (official Rust distribution)
- **Linux/macOS**: https://sh.rustup.rs (official Rust distribution)

Both are HTTPS-secured and verified by the Rust project.

## Related Documentation

- [Installation Guide](WINDOWS_INSTALLATION.md) - Complete installation instructions
- [Dependency Analysis](DEPENDENCY_ANALYSIS.md) - Technical dependency details
- [Troubleshooting](INSTALLATION_TROUBLESHOOTING.md) - General troubleshooting guide
- [Verification Guide](VERIFICATION_GUIDE.md) - Installation verification

## Support

If you encounter issues with Rust auto-installation:

1. Check this troubleshooting guide
2. Review the [main troubleshooting doc](INSTALLATION_TROUBLESHOOTING.md)
3. Run verification: `python scripts/installation/verify_installation.py`
4. Report issues with full error output and system information
