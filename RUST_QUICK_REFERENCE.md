# Rust Auto-Installation - Quick Reference

## TL;DR

The installer now automatically installs Rust when needed for DeepFilterNet. Just run:

```bash
python scripts/installation/install.py --audio
```

No manual Rust installation required!

## What Was Added

**Two new methods in `TerminalAIInstaller`**:

1. `check_rust()` - Detects if Rust is installed
2. `install_rust()` - Automatically installs Rust compiler

## When Does It Run?

Automatically when you use:
- `--audio` flag
- `--full` flag

Does NOT run with:
- `--basic` (default)
- `--dev` (unless combined with --audio)

## Installation Flow

```
python install.py --audio
  ↓
Install PyTorch + Demucs
  ↓
Check for Rust
  ├─ Found? → Install DeepFilterNet
  └─ Missing? → Install Rust → Install DeepFilterNet
  ↓
Done!
```

## Platform Details

### Windows
- Downloads: https://win.rustup.rs/x86_64
- Installs to: `%USERPROFILE%\.cargo\`
- Time: 2-5 minutes

### Linux/macOS
- Uses: `curl https://sh.rustup.rs | sh`
- Installs to: `~/.cargo/`
- Time: 2-5 minutes

## Verify Installation

```bash
# Check Rust
rustc --version
cargo --version

# Check DeepFilterNet
python -c "import deepfilternet; print('OK')"
```

## Troubleshooting

### Installation Failed?

1. **Check error message in installer output**
2. **Try manual Rust install**: https://rustup.rs/
3. **Then rerun**: `python install.py --audio`

### Timeout?

Rust installation can take 5-10 minutes on slow connections. Just rerun the installer.

### Still Not Working?

See full guide: `docs/installation/RUST_AUTO_INSTALLATION.md`

## Files Modified

- `scripts/installation/install.py` (+186 lines)

## Files Created

- `docs/installation/RUST_AUTO_INSTALLATION.md` (detailed guide)
- `test_rust_installer.py` (test script)
- `RUST_AUTO_INSTALL_SUMMARY.md` (technical details)
- `RUST_INSTALLATION_COMPLETE.md` (implementation summary)
- `RUST_QUICK_REFERENCE.md` (this file)

## Code Locations

**Absolute Paths**:
- Installer: `D:\SSD\AI_Tools\terminalai\scripts\installation\install.py`
- Documentation: `D:\SSD\AI_Tools\terminalai\docs\installation\RUST_AUTO_INSTALLATION.md`

**Line Numbers in install.py**:
- `check_rust()`: Lines 71-96
- `install_rust()`: Lines 98-212
- Integration: Lines 258-281

## Quick Test

```bash
cd D:\SSD\AI_Tools\terminalai
python test_rust_installer.py
```

This will show you the installation flow without actually installing anything.
