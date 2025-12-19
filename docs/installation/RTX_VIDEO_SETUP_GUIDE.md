# RTX Video SDK Setup Guide

## Automatic Installation (New!)

The RTX Video SDK setup wizard now includes automatic detection and installation of the SDK.

### Quick Start

1. Download the RTX Video SDK ZIP from [NVIDIA Developer Portal](https://developer.nvidia.com/rtx-video-sdk)
   - Requires free NVIDIA Developer account
   - Download to Downloads folder, Desktop, or any location

2. Run the setup wizard:
   ```bash
   python scripts/setup_rtx_video.py
   ```

3. Choose automatic installation when prompted
   - Wizard searches common locations (Downloads, Desktop, current directory)
   - Displays found files with size and location
   - Select from list or provide manual path

4. Installation proceeds automatically:
   - ZIP validation (checks for corruption and SDK files)
   - Extraction to `C:\Program Files\NVIDIA Corporation\RTX Video SDK`
   - Environment variable setup (`RTX_VIDEO_SDK_HOME`)
   - Python dependency installation
   - Verification of DLL files

### Features

#### Auto-Detection
- Searches Downloads folder, Desktop, and current directory
- Matches patterns: `*rtx*video*.zip`, `*RTXVideo*.zip`, etc.
- Displays multiple files with metadata (size, location)
- Sorts by modification time (newest first)

#### Manual Path Input
- Fallback if auto-detection doesn't find files
- Supports both relative and absolute paths
- Handles quoted paths from drag-and-drop
- Validates file exists and is a ZIP

#### Smart Installation
- Validates ZIP integrity before extraction
- Checks for SDK-specific files (NVVideoEffects.dll)
- Shows progress during extraction
- Handles existing installations (asks to overwrite)
- Detects permission issues and suggests running as admin

#### Environment Configuration
- Sets `RTX_VIDEO_SDK_HOME` system variable automatically
- Also sets for current session
- Provides manual instructions if automatic setting fails

#### Error Handling
- Corrupted ZIP detection
- Permission errors with admin suggestion
- Missing files with clear error messages
- Graceful fallback to manual installation

### Installation Flow

```
Step 1: Check System Requirements
  - Windows 64-bit
  - NVIDIA GPU (RTX 20+ recommended)
  - Driver version check

Step 2: Show Benefits
  - RTX Video SDK capabilities
  - Comparison with other engines

Step 3: Install Python Dependencies
  - numpy, opencv-python
  - Optional: CuPy for CUDA acceleration

Step 4: SDK Installation (Automatic)
  [1/5] Search for ZIP files in common locations
  [2/5] Manual path input if needed
  [3/5] Validate ZIP file integrity
  [4/5] Extract to installation directory
  [5/5] Set environment variables

Step 5: Verification
  - Check for NVVideoEffects.dll
  - Verify environment variable
  - Ready to use!
```

### Manual Installation Fallback

If automatic installation doesn't work or you prefer manual setup:

1. Wizard provides detailed instructions
2. Opens browser to download page
3. Step-by-step guide for:
   - Installing SDK
   - Setting environment variables
   - Verifying installation

### Common Issues

**Permission Denied**
```
[x] Permission denied. Try running as Administrator:
  1. Right-click Command Prompt or PowerShell
  2. Select 'Run as administrator'
  3. Run: python setup_rtx_video.py
```

**ZIP Not Found**
```
[!] No SDK files found in common locations
[!] Searched: Downloads, Desktop, current directory

Enter path to SDK ZIP file (or 'q' to quit):
```

**Invalid ZIP**
```
[x] File is not a valid ZIP archive
```

**Corrupt ZIP**
```
[x] Corrupt file in ZIP: path/to/file
```

### Verification

After installation, verify with:

```bash
# Check environment variable
echo %RTX_VIDEO_SDK_HOME%

# Expected output
C:\Program Files\NVIDIA Corporation\RTX Video SDK

# Launch TerminalAI
python -m vhs_upscaler.gui

# In GUI, select:
AI Upscaler: rtxvideo
```

### Advanced Options

**Custom Installation Path**
- When directory exists, wizard asks to overwrite
- Can provide custom path instead
- Environment variable set to custom path

**Skip Dependency Installation**
- Answer 'n' to Python dependencies prompt
- Install manually later:
  ```bash
  pip install numpy opencv-python
  pip install cupy-cuda12x  # Optional CUDA acceleration
  ```

### Requirements

- Windows 64-bit
- NVIDIA RTX 20 series GPU or newer
- NVIDIA Driver 535+
- Python 3.10+
- Downloaded RTX Video SDK ZIP file

### Support

For issues or questions:
- GitHub Issues: https://github.com/parthalon025/terminalai
- RTX Video SDK Docs: https://developer.nvidia.com/rtx-video-sdk
