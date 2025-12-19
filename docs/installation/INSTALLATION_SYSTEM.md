# TerminalAI Installation System Documentation

## Overview

The TerminalAI installation system provides automated, robust installation of the entire software stack on Windows systems with full rollback support, dependency verification, and comprehensive logging.

## Components

### 1. PowerShell Installation Script (`install_windows.ps1`)

**Purpose**: Main automated installation engine for Windows systems.

**Features**:
- Automatic CUDA version detection based on NVIDIA driver
- PyTorch installation with correct CUDA support
- Optional feature installation (audio, faces, VapourSynth, automation)
- Rollback mechanism for failed installations
- Comprehensive logging and error handling
- Installation verification at each step
- Colored terminal output for better UX
- Automatic dependency resolution

**Key Functions**:

| Function | Purpose |
|----------|---------|
| `Test-Python` | Verify Python 3.10+ installed |
| `Test-FFmpeg` | Check FFmpeg availability |
| `Get-NvidiaInfo` | Detect GPU and determine CUDA version |
| `Install-PyTorch` | Install PyTorch with CUDA/CPU support |
| `Install-VapourSynth` | Download and install VapourSynth |
| `Install-AudioDependencies` | Install Demucs, DeepFilterNet, AudioSR |
| `Install-FaceDependencies` | Install GFPGAN, CodeFormer, OpenCV |
| `Test-Installations` | Verify all components |
| `Invoke-Rollback` | Undo installations on failure |

**Usage**:
```powershell
# Full installation
.\install_windows.ps1 -Full

# Selective features
.\install_windows.ps1 -Audio -Faces

# CPU-only mode
.\install_windows.ps1 -Full -CPUOnly

# With verbose output
.\install_windows.ps1 -Full -Verbose
```

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `-Full` | Switch | Install all optional features |
| `-Audio` | Switch | Install audio processing (Demucs, etc.) |
| `-Faces` | Switch | Install face restoration (GFPGAN, etc.) |
| `-Automation` | Switch | Install watch folder automation |
| `-VapourSynth` | Switch | Install VapourSynth for QTGMC |
| `-Dev` | Switch | Install development dependencies |
| `-CPUOnly` | Switch | Install CPU-only PyTorch |
| `-SkipFFmpeg` | Switch | Skip FFmpeg verification |
| `-Verbose` | Switch | Enable detailed output |

### 2. Verification Script (`verify_setup.py`)

**Purpose**: Comprehensive post-installation verification and diagnostics.

**Features**:
- Checks all core and optional dependencies
- GPU and CUDA detection
- PyTorch CUDA availability testing
- VapourSynth installation verification
- Maxine SDK detection
- Real-ESRGAN availability check
- JSON report export
- Colored terminal output
- Actionable recommendations

**Verification Categories**:

1. **System Requirements**
   - Python version (3.10+)
   - FFmpeg availability

2. **GPU Support**
   - NVIDIA GPU detection
   - Driver version
   - PyTorch CUDA availability

3. **Core Components**
   - TerminalAI package
   - Gradio
   - yt-dlp
   - PyYAML

4. **AI Frameworks**
   - PyTorch
   - TorchAudio

5. **Upscaling Engines**
   - NVIDIA Maxine SDK
   - Real-ESRGAN

6. **Advanced Features**
   - VapourSynth (QTGMC)
   - Demucs (AI audio)
   - DeepFilterNet (AI denoise)
   - AudioSR (AI upsample)
   - GFPGAN (face restoration)
   - CodeFormer (face restoration)
   - Watchdog (automation)

**Usage**:
```bash
# Run verification
python verify_setup.py

# Verbose output with detailed errors
python verify_setup.py --verbose

# Export JSON report
python verify_setup.py --export

# Custom report filename
python verify_setup.py --export --report-file my_report.json
```

**Exit Codes**:
- `0`: All critical components verified
- `1`: One or more critical components missing

### 3. Batch File Launcher (`install.bat`)

**Purpose**: User-friendly menu-driven installation launcher for non-technical users.

**Features**:
- Interactive menu system
- Pre-defined installation profiles
- Custom component selection
- Administrator privilege checking
- Automatic verification after installation
- GUI launch option

**Installation Profiles**:

| Profile | Components | Size | Time |
|---------|------------|------|------|
| **Full** | Everything | ~5 GB | 15-20 min |
| **Basic** | Core only | ~200 MB | 2-3 min |
| **Audio** | Core + Audio AI | ~4 GB | 8-10 min |
| **Faces** | Core + Face restoration | ~3 GB | 7-9 min |
| **Custom** | User-selected | Varies | Varies |

**Usage**:
1. Double-click `install.bat`
2. Select installation mode from menu
3. Follow prompts
4. Optionally launch GUI after installation

### 4. Installation Guide (`INSTALL_WINDOWS.md`)

**Purpose**: Comprehensive installation documentation for Windows users.

**Sections**:
- Prerequisites and system requirements
- Quick installation instructions
- Manual installation steps
- Installation options explained
- Verification procedures
- Troubleshooting common issues
- Next steps and getting started

## Installation Flow

### Automated Installation Process

```
┌─────────────────────────────────────────┐
│  User launches install_windows.ps1      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Pre-flight Checks                      │
│  • Python 3.10+ installed?              │
│  • pip available?                       │
│  • FFmpeg installed?                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  GPU Detection                          │
│  • Detect NVIDIA GPU                    │
│  • Get driver version                   │
│  • Determine CUDA version               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Install TerminalAI Core                │
│  • pip install -e .                     │
│  • Register rollback action             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Install PyTorch (if needed)            │
│  • Determine CUDA vs CPU                │
│  • Install from correct index           │
│  • Verify CUDA availability             │
│  • Fallback to CPU if CUDA fails        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Install Optional Features              │
│  • Audio: Demucs, DeepFilterNet, etc.   │
│  • Faces: GFPGAN, CodeFormer, etc.      │
│  • VapourSynth: Download, extract, pip  │
│  • Automation: Watchdog, requests       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Verification                           │
│  • Test import of all packages          │
│  • Check PyTorch CUDA                   │
│  • Verify VapourSynth                   │
│  • Test command-line tools              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Generate Report                        │
│  • Installation summary                 │
│  • Success rate                         │
│  • Troubleshooting info                 │
│  • Next steps                           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Installation Complete                  │
│  • Log file saved                       │
│  • Report file saved                    │
│  • User prompted for next action        │
└─────────────────────────────────────────┘
```

### Error Handling Flow

```
┌─────────────────────────────────────────┐
│  Installation Step Fails                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Log Error                              │
│  • Add to error log                     │
│  • Display error message                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Is this a critical failure?            │
└──────┬───────────────────┬──────────────┘
       │ YES               │ NO
       ▼                   ▼
┌─────────────┐   ┌──────────────────────┐
│  Abort      │   │  Continue with       │
│  Prompt     │   │  Warning             │
│  Rollback?  │   └──────────────────────┘
└──────┬──────┘
       │ YES
       ▼
┌─────────────────────────────────────────┐
│  Execute Rollback                       │
│  • Uninstall packages in reverse order  │
│  • Remove extracted files               │
│  • Clean environment variables          │
└─────────────────────────────────────────┘
```

## CUDA Version Detection

The installation script automatically detects the correct CUDA version based on the installed NVIDIA driver:

| Driver Version | CUDA Version | PyTorch Index URL |
|----------------|--------------|-------------------|
| 570+ | 12.6 | `cu126` |
| 550-569 | 12.4 | `cu124` |
| 530-549 | 12.1 | `cu121` |
| 520-529 | 11.8 | `cu118` |
| < 520 | CPU-only | `cpu` |

**Logic**:
```powershell
$driverNum = [double]$driverVersion.Split('.')[0]
if ($driverNum -ge 570) {
    $cudaVersion = "12.6"
} elseif ($driverNum -ge 550) {
    $cudaVersion = "12.4"
} elseif ($driverNum -ge 530) {
    $cudaVersion = "12.1"
} else {
    # Fall back to CPU-only
}
```

## VapourSynth Installation

VapourSynth installation is complex because it requires:
1. Downloading portable .7z archive
2. Extracting with 7-Zip
3. Setting environment variable
4. Installing Python package
5. Installing HAVSFunc for QTGMC

**Process**:

1. **Download**: Fetch VapourSynth R70 portable from GitHub releases
2. **Extract**: Use 7-Zip to extract to `%LOCALAPPDATA%\VapourSynth`
3. **Environment**: Set `VAPOURSYNTH_PATH` user environment variable
4. **Python Package**: `pip install vapoursynth havsfunc`
5. **Verification**: Test import in Python

**Fallback**: If 7-Zip not found, provide manual installation instructions.

## Rollback Mechanism

The installation script maintains a stack of rollback actions that are executed in reverse order if installation fails.

**Rollback Actions**:

| Installation Step | Rollback Action |
|-------------------|-----------------|
| TerminalAI package | `pip uninstall -y terminalai` |
| PyTorch | `pip uninstall -y torch torchaudio` |
| Audio dependencies | `pip uninstall -y demucs deepfilternet audiosr` |
| Face dependencies | `pip uninstall -y gfpgan basicsr facexlib opencv-python` |
| VapourSynth | `pip uninstall -y vapoursynth havsfunc` + delete extracted files |
| Automation | `pip uninstall -y watchdog requests` |

**Example**:
```powershell
Register-Rollback -Action {
    & python -m pip uninstall -y torch torchaudio
} -Description "Uninstall PyTorch"
```

On failure:
```powershell
Invoke-Rollback
# Executes all registered rollback actions in reverse order
```

## Logging

Two types of logs are maintained:

### 1. Installation Log
- **Filename**: `install_YYYYMMDD_HHMMSS.log`
- **Content**: All installation steps, commands, and results
- **Format**: Timestamped entries

**Example**:
```
[2025-12-18 14:30:15] Installation started
[2025-12-18 14:30:16] Python version: 3.13.5
[2025-12-18 14:30:17] GPU detected: RTX 5080, Driver: 591.59
[2025-12-18 14:30:18] Recommended CUDA version: 12.6
[2025-12-18 14:30:45] PyTorch CUDA installation: successful
...
```

### 2. Installation Report
- **Filename**: `installation_report_YYYYMMDD_HHMMSS.txt`
- **Content**: Summary, system info, results, next steps
- **Format**: Human-readable structured text

**Sections**:
1. System Information (OS, Python, GPU, CUDA)
2. Installation Results (checkmarks for each component)
3. Next Steps (how to launch and use)
4. Troubleshooting (specific issues and solutions)

## Verification Report

The verification script can export a JSON report:

**Structure**:
```json
{
  "timestamp": "2025-12-18T14:45:30",
  "system": {
    "python_version": "3.13.5",
    "platform": "win32"
  },
  "results": [
    {
      "name": "Python Version",
      "status": true,
      "version": "3.13.5",
      "error": null,
      "details": "Python 3.13.5 meets minimum requirement (3.10+)",
      "severity": "error"
    },
    ...
  ],
  "summary": {
    "total": 25,
    "passed": 23,
    "errors": 0,
    "warnings": 2
  }
}
```

## Best Practices for Users

### Before Installation

1. **Update NVIDIA driver** to latest version (570+)
2. **Install FFmpeg** via winget or download
3. **Close GPU applications** (browsers, games)
4. **Free up disk space** (~10 GB for full installation)
5. **Run PowerShell as Administrator** for best results

### During Installation

1. **Don't interrupt** the installation process
2. **Monitor output** for any errors
3. **Check internet connection** (stable connection needed)
4. **Wait for verification** to complete

### After Installation

1. **Run verification**: `python verify_setup.py`
2. **Check logs** if any issues
3. **Test core functionality** with a small video
4. **Read documentation** (INSTALL_WINDOWS.md, README.md)

## Troubleshooting

### Common Issues

#### 1. PowerShell Execution Policy Error

**Error**: "cannot be loaded because running scripts is disabled"

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. PyTorch CUDA Not Available

**Symptoms**: `torch.cuda.is_available()` returns `False`

**Causes**:
- Installed CPU-only PyTorch by mistake
- NVIDIA driver too old
- Wrong CUDA version for driver

**Solution**:
```bash
# Check driver version
nvidia-smi

# Reinstall PyTorch with correct CUDA
pip uninstall torch torchaudio
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu126
```

#### 3. VapourSynth Installation Fails

**Symptoms**: "7-Zip not found"

**Solution**:
1. Install 7-Zip: `winget install 7zip.7zip`
2. OR download VapourSynth installer manually
3. Run installer, then `pip install vapoursynth havsfunc`

#### 4. Out of Disk Space

**Symptoms**: Installation fails during PyTorch download

**Solution**:
- Free up at least 10 GB
- Change temp directory to different drive
- Install selective features instead of full

## Development and Maintenance

### Adding New Optional Features

To add a new optional feature to the installation system:

1. **Add to pyproject.toml**:
   ```toml
   [project.optional-dependencies]
   newfeature = [
       "package1>=1.0.0",
       "package2>=2.0.0",
   ]
   ```

2. **Add installation function in install_windows.ps1**:
   ```powershell
   function Install-NewFeature {
       Write-Section "Installing New Feature"
       # Installation logic
       Register-Rollback -Action { ... }
   }
   ```

3. **Add parameter**:
   ```powershell
   param(
       [switch]$NewFeature
   )
   ```

4. **Add to installation flow**:
   ```powershell
   if ($Full -or $NewFeature) {
       Install-NewFeature
   }
   ```

5. **Add verification in verify_setup.py**:
   ```python
   def check_new_feature(self):
       self.check_package("package1", optional=True)
   ```

6. **Update documentation**:
   - INSTALL_WINDOWS.md
   - Installation system docs

### Testing

Test the installation system on:
- **Clean VM**: Fresh Windows 10/11 installation
- **With NVIDIA GPU**: RTX 2060 or higher
- **Without GPU**: Verify CPU-only fallback
- **Different Python versions**: 3.10, 3.11, 3.12, 3.13
- **With/without admin privileges**
- **Poor network conditions**: Test timeout handling

### Updating CUDA Versions

When new CUDA versions are released:

1. Update driver version table in `Get-NvidiaInfo`
2. Update INSTALL_WINDOWS.md compatibility table
3. Test with new PyTorch index URLs
4. Update default CUDA version if needed

## Performance Metrics

Typical installation times (on high-speed internet):

| Component | Download Size | Install Time |
|-----------|---------------|--------------|
| Core TerminalAI | 50 MB | 30 sec |
| PyTorch (CUDA 12.6) | 2.5 GB | 5 min |
| Demucs | 500 MB | 2 min |
| DeepFilterNet | 200 MB | 1 min |
| AudioSR | 100 MB | 1 min |
| GFPGAN + deps | 1 GB | 3 min |
| VapourSynth | 50 MB | 2 min |
| **Total (Full)** | **~5 GB** | **15-20 min** |

**Factors affecting installation time**:
- Internet speed
- Disk I/O speed (SSD vs HDD)
- CPU speed (for package compilation if needed)
- Available RAM

## Security Considerations

The installation script:
- **Downloads from official sources**: PyTorch, PyPI, GitHub releases
- **Uses HTTPS**: All downloads over encrypted connections
- **No sudo/admin required**: (except for VapourSynth extraction on some systems)
- **No system modifications**: Installs to user-level Python environment
- **Transparent**: All commands logged and visible

**User can review**:
- PowerShell script source code (install_windows.ps1)
- Verification script source (verify_setup.py)
- Installation log file
- All pip commands before execution

## Future Enhancements

Planned improvements:

1. **Progress bars**: Visual progress for large downloads
2. **Parallel downloads**: Download multiple packages simultaneously
3. **Cached downloads**: Store downloads for reinstallation
4. **Delta updates**: Only update changed components
5. **Uninstaller**: Automated removal of all components
6. **Docker image**: Pre-built Windows container image
7. **MSI installer**: Traditional Windows installer package
8. **Auto-updater**: Check for and install updates

---

**Version**: 1.0
**Author**: TerminalAI DevOps Team
**Last Updated**: 2025-12-18
