# TerminalAI Windows Installation Script
# ========================================
# Automated installation with all optional features for Windows 10/11 + NVIDIA RTX
# Supports: PyTorch (CUDA), VapourSynth, GFPGAN, CodeFormer, DeepFilterNet, AudioSR, Demucs

param(
    [switch]$Full,           # Install all optional features
    [switch]$Audio,          # Install audio processing (Demucs, DeepFilterNet, AudioSR)
    [switch]$Faces,          # Install face restoration (GFPGAN, CodeFormer)
    [switch]$Automation,     # Install watch folder automation
    [switch]$VapourSynth,    # Install VapourSynth for QTGMC deinterlacing
    [switch]$Dev,            # Install development dependencies
    [switch]$SkipFFmpeg,     # Skip FFmpeg check/install
    [switch]$CPUOnly,        # Install CPU-only PyTorch (no CUDA)
    [switch]$Verbose         # Enable verbose output
)

# Color output functions
function Write-Success { param($msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "✗ $msg" -ForegroundColor Red }
function Write-Warning { param($msg) Write-Host "⚠ $msg" -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host "ℹ $msg" -ForegroundColor Cyan }
function Write-Section { param($msg) Write-Host "`n═══ $msg ═══" -ForegroundColor Magenta }

# Global variables
$script:InstallLog = @()
$script:ErrorLog = @()
$script:StartTime = Get-Date
$script:LogFile = "install_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$script:RollbackActions = @()

# Add to installation log
function Add-Log {
    param($Message, [switch]$Error)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $entry = "[$timestamp] $Message"

    if ($Error) {
        $script:ErrorLog += $entry
        $entry | Out-File -FilePath $script:LogFile -Append
    } else {
        $script:InstallLog += $entry
        $entry | Out-File -FilePath $script:LogFile -Append
    }
}

# Register rollback action
function Register-Rollback {
    param([scriptblock]$Action, [string]$Description)
    $script:RollbackActions += @{Action = $Action; Description = $Description}
}

# Execute rollback
function Invoke-Rollback {
    Write-Section "Executing Rollback"
    foreach ($item in $script:RollbackActions | Select-Object -Last $script:RollbackActions.Count) {
        try {
            Write-Info "Rolling back: $($item.Description)"
            & $item.Action
            Add-Log "Rollback successful: $($item.Description)"
        } catch {
            Write-Warning "Rollback failed for: $($item.Description) - $($_.Exception.Message)"
            Add-Log "Rollback failed: $($item.Description) - $($_.Exception.Message)" -Error
        }
    }
}

# Check if running as administrator
function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check Python version
function Test-Python {
    Write-Section "Checking Python Installation"

    try {
        $pythonVersion = & python --version 2>&1
        if ($pythonVersion -match "Python (\d+\.\d+)") {
            $version = [version]$matches[1]
            Write-Info "Found: $pythonVersion"
            Add-Log "Python version: $pythonVersion"

            if ($version -lt [version]"3.10") {
                Write-Error "Python 3.10+ required (found $version)"
                Add-Log "Python version check failed: $version < 3.10" -Error
                return $false
            }

            Write-Success "Python version OK"
            return $true
        } else {
            Write-Error "Could not determine Python version"
            Add-Log "Python version detection failed" -Error
            return $false
        }
    } catch {
        Write-Error "Python not found in PATH"
        Add-Log "Python not found: $($_.Exception.Message)" -Error

        Write-Info "`nInstall Python 3.10+ from:"
        Write-Info "  https://www.python.org/downloads/"
        Write-Info "  OR: winget install Python.Python.3.13"
        return $false
    }
}

# Check pip availability
function Test-Pip {
    try {
        $null = & python -m pip --version 2>&1
        Write-Success "pip available"
        Add-Log "pip check: OK"
        return $true
    } catch {
        Write-Error "pip not available"
        Add-Log "pip check failed" -Error

        Write-Info "`nInstalling pip..."
        try {
            & python -m ensurepip --upgrade
            Write-Success "pip installed"
            Add-Log "pip installation: successful"
            return $true
        } catch {
            Write-Error "Failed to install pip: $($_.Exception.Message)"
            Add-Log "pip installation failed: $($_.Exception.Message)" -Error
            return $false
        }
    }
}

# Upgrade pip
function Update-Pip {
    Write-Info "Upgrading pip..."
    try {
        & python -m pip install --upgrade pip setuptools wheel | Out-Null
        Write-Success "pip upgraded"
        Add-Log "pip upgrade: successful"
        return $true
    } catch {
        Write-Warning "pip upgrade failed (continuing anyway)"
        Add-Log "pip upgrade warning: $($_.Exception.Message)" -Error
        return $true  # Non-fatal
    }
}

# Check FFmpeg
function Test-FFmpeg {
    Write-Section "Checking FFmpeg"

    if ($SkipFFmpeg) {
        Write-Warning "FFmpeg check skipped"
        Add-Log "FFmpeg check skipped by user"
        return $true
    }

    try {
        $ffmpegVersion = & ffmpeg -version 2>&1 | Select-Object -First 1
        Write-Info "$ffmpegVersion"
        Write-Success "FFmpeg found"
        Add-Log "FFmpeg: $ffmpegVersion"
        return $true
    } catch {
        Write-Warning "FFmpeg not found"
        Add-Log "FFmpeg not found" -Error

        Write-Info "`nFFmpeg is REQUIRED for video processing."
        Write-Info "Install options:"
        Write-Info "  1. winget install FFmpeg"
        Write-Info "  2. choco install ffmpeg"
        Write-Info "  3. Download from: https://ffmpeg.org/download.html"

        $response = Read-Host "`nContinue without FFmpeg? (y/N)"
        return ($response -eq 'y')
    }
}

# Detect NVIDIA GPU and CUDA support
function Get-NvidiaInfo {
    Write-Section "Detecting NVIDIA GPU"

    $info = @{
        HasNvidia = $false
        GPUName = ""
        DriverVersion = ""
        CUDAVersion = "12.1"  # Default to latest stable
        ComputeCapability = ""
    }

    try {
        $gpuInfo = & nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>&1
        if ($LASTEXITCODE -eq 0) {
            $parts = $gpuInfo -split ','
            $info.HasNvidia = $true
            $info.GPUName = $parts[0].Trim()
            $info.DriverVersion = $parts[1].Trim()

            Write-Success "GPU: $($info.GPUName)"
            Write-Info "Driver: $($info.DriverVersion)"
            Add-Log "GPU detected: $($info.GPUName), Driver: $($info.DriverVersion)"

            # Determine CUDA version based on driver
            $driverNum = [double]$info.DriverVersion.Split('.')[0]
            if ($driverNum -ge 570) {
                $info.CUDAVersion = "12.6"
            } elseif ($driverNum -ge 550) {
                $info.CUDAVersion = "12.4"
            } elseif ($driverNum -ge 530) {
                $info.CUDAVersion = "12.1"
            } elseif ($driverNum -ge 520) {
                $info.CUDAVersion = "11.8"
            }

            Write-Info "Recommended CUDA: $($info.CUDAVersion)"
            Add-Log "Recommended CUDA version: $($info.CUDAVersion)"
        } else {
            Write-Warning "No NVIDIA GPU detected"
            Add-Log "No NVIDIA GPU detected"
        }
    } catch {
        Write-Warning "nvidia-smi not available"
        Add-Log "nvidia-smi check failed: $($_.Exception.Message)"
    }

    return $info
}

# Install PyTorch with CUDA support
function Install-PyTorch {
    param($NvidiaInfo)

    Write-Section "Installing PyTorch"

    if ($CPUOnly -or -not $NvidiaInfo.HasNvidia) {
        Write-Info "Installing CPU-only PyTorch..."
        Add-Log "Installing PyTorch CPU-only"

        try {
            & python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
            if ($LASTEXITCODE -eq 0) {
                Write-Success "PyTorch (CPU) installed"
                Add-Log "PyTorch CPU installation: successful"
                Register-Rollback -Action {
                    & python -m pip uninstall -y torch torchaudio
                } -Description "Uninstall PyTorch CPU"
                return $true
            } else {
                throw "pip install failed"
            }
        } catch {
            Write-Error "PyTorch (CPU) installation failed: $($_.Exception.Message)"
            Add-Log "PyTorch CPU installation failed: $($_.Exception.Message)" -Error
            return $false
        }
    } else {
        # CUDA installation
        $cudaVersion = $NvidiaInfo.CUDAVersion
        $cudaVersionShort = $cudaVersion.Replace('.', '')

        Write-Info "Installing PyTorch with CUDA $cudaVersion support..."
        Add-Log "Installing PyTorch with CUDA $cudaVersion"

        try {
            $indexUrl = "https://download.pytorch.org/whl/cu$cudaVersionShort"
            Write-Info "Using index: $indexUrl"

            & python -m pip install torch torchaudio --index-url $indexUrl

            if ($LASTEXITCODE -eq 0) {
                Write-Success "PyTorch (CUDA $cudaVersion) installed"
                Add-Log "PyTorch CUDA installation: successful"

                # Verify CUDA availability
                $cudaCheck = & python -c "import torch; print(torch.cuda.is_available())" 2>&1
                if ($cudaCheck -eq "True") {
                    Write-Success "CUDA is available in PyTorch"
                    Add-Log "PyTorch CUDA verification: successful"
                } else {
                    Write-Warning "CUDA not available in PyTorch (may still work)"
                    Add-Log "PyTorch CUDA verification: CUDA not available" -Error
                }

                Register-Rollback -Action {
                    & python -m pip uninstall -y torch torchaudio
                } -Description "Uninstall PyTorch CUDA"
                return $true
            } else {
                throw "pip install failed"
            }
        } catch {
            Write-Error "PyTorch (CUDA) installation failed: $($_.Exception.Message)"
            Add-Log "PyTorch CUDA installation failed: $($_.Exception.Message)" -Error

            Write-Warning "Falling back to CPU-only PyTorch..."
            Add-Log "Falling back to PyTorch CPU"

            try {
                & python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
                Write-Success "PyTorch (CPU) installed as fallback"
                Add-Log "PyTorch CPU fallback: successful"
                return $true
            } catch {
                Write-Error "PyTorch fallback also failed"
                Add-Log "PyTorch CPU fallback failed: $($_.Exception.Message)" -Error
                return $false
            }
        }
    }
}

# Install VapourSynth
function Install-VapourSynth {
    Write-Section "Installing VapourSynth"

    # Check if already installed
    try {
        $vsTest = & python -c "import vapoursynth" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "VapourSynth already installed"
            Add-Log "VapourSynth: already installed"
            return $true
        }
    } catch { }

    Write-Info "VapourSynth provides QTGMC deinterlacing (highest quality)"
    Write-Info "Installation requires:"
    Write-Info "  1. VapourSynth runtime (automatic download)"
    Write-Info "  2. Python VapourSynth package"

    # Download VapourSynth installer
    $vsVersion = "R70"
    $vsUrl = "https://github.com/vapoursynth/vapoursynth/releases/download/$vsVersion/VapourSynth64-Portable-$vsVersion.7z"
    $vsInstaller = "$env:TEMP\VapourSynth.7z"
    $vsExtractPath = "$env:LOCALAPPDATA\VapourSynth"

    Write-Info "Downloading VapourSynth $vsVersion..."
    Add-Log "Downloading VapourSynth from: $vsUrl"

    try {
        # Download
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $vsUrl -OutFile $vsInstaller -UseBasicParsing
        $ProgressPreference = 'Continue'
        Write-Success "Download complete"
        Add-Log "VapourSynth download: successful"

        # Extract using built-in Windows extraction or 7-Zip
        Write-Info "Extracting VapourSynth..."

        if (Test-Path $vsExtractPath) {
            Write-Warning "Removing existing VapourSynth installation..."
            Remove-Item -Path $vsExtractPath -Recurse -Force
        }

        New-Item -ItemType Directory -Path $vsExtractPath -Force | Out-Null

        # Try 7-Zip first
        $sevenZipPaths = @(
            "$env:ProgramFiles\7-Zip\7z.exe",
            "$env:ProgramFiles(x86)\7-Zip\7z.exe",
            "C:\Program Files\7-Zip\7z.exe"
        )

        $sevenZip = $sevenZipPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

        if ($sevenZip) {
            & $sevenZip x "-o$vsExtractPath" $vsInstaller -y | Out-Null
            Write-Success "VapourSynth extracted"
            Add-Log "VapourSynth extraction: successful (7-Zip)"
        } else {
            Write-Warning "7-Zip not found - VapourSynth installation may require manual setup"
            Write-Info "Please install VapourSynth manually from:"
            Write-Info "  https://github.com/vapoursynth/vapoursynth/releases"
            Add-Log "VapourSynth extraction: 7-Zip not found" -Error
            return $false
        }

        # Set environment variable
        $vsPath = "$vsExtractPath\VapourSynth64"
        [Environment]::SetEnvironmentVariable("VAPOURSYNTH_PATH", $vsPath, "User")
        $env:VAPOURSYNTH_PATH = $vsPath

        Write-Info "VapourSynth path set: $vsPath"
        Add-Log "VapourSynth environment variable set: $vsPath"

        # Install Python package
        Write-Info "Installing VapourSynth Python package..."
        & python -m pip install vapoursynth

        if ($LASTEXITCODE -eq 0) {
            Write-Success "VapourSynth Python package installed"
            Add-Log "VapourSynth Python package: successful"

            # Install HAVSFunc for QTGMC
            Write-Info "Installing HAVSFunc (QTGMC support)..."
            & python -m pip install havsfunc
            Write-Success "HAVSFunc installed"
            Add-Log "HAVSFunc installation: successful"

            Register-Rollback -Action {
                & python -m pip uninstall -y vapoursynth havsfunc
                Remove-Item -Path $vsExtractPath -Recurse -Force -ErrorAction SilentlyContinue
            } -Description "Uninstall VapourSynth"

            return $true
        } else {
            Write-Error "VapourSynth Python package installation failed"
            Add-Log "VapourSynth Python package failed" -Error
            return $false
        }

    } catch {
        Write-Error "VapourSynth installation failed: $($_.Exception.Message)"
        Add-Log "VapourSynth installation failed: $($_.Exception.Message)" -Error

        Write-Info "`nManual installation:"
        Write-Info "  Download: https://github.com/vapoursynth/vapoursynth/releases"
        Write-Info "  Then run: pip install vapoursynth havsfunc"

        return $false
    } finally {
        # Cleanup
        if (Test-Path $vsInstaller) {
            Remove-Item $vsInstaller -Force
        }
    }
}

# Install core TerminalAI package
function Install-TerminalAI {
    param([string]$Mode = "basic")

    Write-Section "Installing TerminalAI Core Package"

    try {
        $installCmd = switch ($Mode) {
            "dev"   { "pip install -e `".[dev]`"" }
            "full"  { "pip install -e `".[full]`"" }
            default { "pip install -e ." }
        }

        Write-Info "Mode: $Mode"
        Write-Info "Command: python -m $installCmd"
        Add-Log "Installing TerminalAI: $Mode mode"

        Invoke-Expression "python -m $installCmd"

        if ($LASTEXITCODE -eq 0) {
            Write-Success "TerminalAI installed successfully"
            Add-Log "TerminalAI installation: successful ($mode)"

            Register-Rollback -Action {
                & python -m pip uninstall -y terminalai
            } -Description "Uninstall TerminalAI"

            return $true
        } else {
            throw "Installation command failed"
        }
    } catch {
        Write-Error "TerminalAI installation failed: $($_.Exception.Message)"
        Add-Log "TerminalAI installation failed: $($_.Exception.Message)" -Error
        return $false
    }
}

# Install audio processing dependencies
function Install-AudioDependencies {
    Write-Section "Installing Audio Processing Dependencies"

    $packages = @(
        "demucs>=4.0.0",
        "deepfilternet>=0.5.0",
        "audiosr>=0.0.4"
    )

    foreach ($pkg in $packages) {
        Write-Info "Installing $pkg..."
        Add-Log "Installing package: $pkg"

        try {
            & python -m pip install $pkg
            if ($LASTEXITCODE -eq 0) {
                Write-Success "$pkg installed"
                Add-Log "$pkg installation: successful"
            } else {
                Write-Warning "$pkg installation failed (non-fatal)"
                Add-Log "$pkg installation: failed (continuing)" -Error
            }
        } catch {
            Write-Warning "$pkg installation error: $($_.Exception.Message)"
            Add-Log "$pkg installation error: $($_.Exception.Message)" -Error
        }
    }

    Register-Rollback -Action {
        & python -m pip uninstall -y demucs deepfilternet audiosr
    } -Description "Uninstall audio dependencies"

    return $true
}

# Install face restoration dependencies
function Install-FaceDependencies {
    Write-Section "Installing Face Restoration Dependencies"

    $packages = @(
        "gfpgan>=1.3.0",
        "basicsr>=1.4.2",
        "facexlib>=0.2.5",
        "opencv-python"
    )

    foreach ($pkg in $packages) {
        Write-Info "Installing $pkg..."
        Add-Log "Installing package: $pkg"

        try {
            & python -m pip install $pkg
            if ($LASTEXITCODE -eq 0) {
                Write-Success "$pkg installed"
                Add-Log "$pkg installation: successful"
            } else {
                Write-Warning "$pkg installation failed (non-fatal)"
                Add-Log "$pkg installation: failed (continuing)" -Error
            }
        } catch {
            Write-Warning "$pkg installation error: $($_.Exception.Message)"
            Add-Log "$pkg installation error: $($_.Exception.Message)" -Error
        }
    }

    # CodeFormer is optional and may not be on PyPI
    Write-Info "Installing CodeFormer (optional)..."
    try {
        & python -m pip install codeformer 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "CodeFormer installed"
            Add-Log "CodeFormer installation: successful"
        } else {
            Write-Warning "CodeFormer not available via pip (will auto-download on first use)"
            Add-Log "CodeFormer: not available via pip"
        }
    } catch {
        Write-Warning "CodeFormer installation skipped"
        Add-Log "CodeFormer: installation skipped"
    }

    Register-Rollback -Action {
        & python -m pip uninstall -y gfpgan basicsr facexlib opencv-python codeformer
    } -Description "Uninstall face dependencies"

    return $true
}

# Install automation dependencies
function Install-AutomationDependencies {
    Write-Section "Installing Automation Dependencies"

    try {
        & python -m pip install "watchdog>=3.0.0" "requests>=2.28.0"
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Automation dependencies installed"
            Add-Log "Automation dependencies: successful"

            Register-Rollback -Action {
                & python -m pip uninstall -y watchdog requests
            } -Description "Uninstall automation dependencies"

            return $true
        } else {
            throw "Installation failed"
        }
    } catch {
        Write-Error "Automation dependencies installation failed: $($_.Exception.Message)"
        Add-Log "Automation dependencies failed: $($_.Exception.Message)" -Error
        return $false
    }
}

# Verify installations
function Test-Installations {
    Write-Section "Verifying Installations"

    $results = @{
        Core = $false
        PyTorch = $false
        PyTorchCUDA = $false
        Gradio = $false
        YTDLP = $false
        Demucs = $false
        DeepFilterNet = $false
        AudioSR = $false
        GFPGAN = $false
        VapourSynth = $false
        Watchdog = $false
    }

    # Core packages
    try {
        & python -c "import vhs_upscaler" 2>&1 | Out-Null
        $results.Core = ($LASTEXITCODE -eq 0)
    } catch { }

    try {
        & python -c "import gradio" 2>&1 | Out-Null
        $results.Gradio = ($LASTEXITCODE -eq 0)
    } catch { }

    try {
        & python -c "import yt_dlp" 2>&1 | Out-Null
        $results.YTDLP = ($LASTEXITCODE -eq 0)
    } catch { }

    # PyTorch
    try {
        & python -c "import torch" 2>&1 | Out-Null
        $results.PyTorch = ($LASTEXITCODE -eq 0)

        if ($results.PyTorch) {
            $cudaAvailable = & python -c "import torch; print(torch.cuda.is_available())" 2>&1
            $results.PyTorchCUDA = ($cudaAvailable -eq "True")
        }
    } catch { }

    # Audio packages
    try {
        & python -c "import demucs" 2>&1 | Out-Null
        $results.Demucs = ($LASTEXITCODE -eq 0)
    } catch { }

    try {
        & python -c "import df" 2>&1 | Out-Null
        $results.DeepFilterNet = ($LASTEXITCODE -eq 0)
    } catch { }

    try {
        & python -c "import audiosr" 2>&1 | Out-Null
        $results.AudioSR = ($LASTEXITCODE -eq 0)
    } catch { }

    # Face restoration
    try {
        & python -c "import gfpgan" 2>&1 | Out-Null
        $results.GFPGAN = ($LASTEXITCODE -eq 0)
    } catch { }

    # VapourSynth
    try {
        & python -c "import vapoursynth" 2>&1 | Out-Null
        $results.VapourSynth = ($LASTEXITCODE -eq 0)
    } catch { }

    # Watchdog
    try {
        & python -c "import watchdog" 2>&1 | Out-Null
        $results.Watchdog = ($LASTEXITCODE -eq 0)
    } catch { }

    # Display results
    Write-Host "`n" -NoNewline
    Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "         INSTALLATION VERIFICATION         " -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""

    function Show-Result { param($name, $status)
        $symbol = if ($status) { "✓" } else { "✗" }
        $color = if ($status) { "Green" } else { "Red" }
        Write-Host "  $symbol " -ForegroundColor $color -NoNewline
        Write-Host $name
        Add-Log "Verification - $name: $status"
    }

    Write-Host "Core Components:" -ForegroundColor Yellow
    Show-Result "TerminalAI Package" $results.Core
    Show-Result "Gradio (Web GUI)" $results.Gradio
    Show-Result "yt-dlp (YouTube)" $results.YTDLP

    Write-Host "`nAI Frameworks:" -ForegroundColor Yellow
    Show-Result "PyTorch" $results.PyTorch
    Show-Result "PyTorch CUDA Support" $results.PyTorchCUDA

    Write-Host "`nOptional Features:" -ForegroundColor Yellow
    Show-Result "Demucs (AI Audio)" $results.Demucs
    Show-Result "DeepFilterNet (AI Denoise)" $results.DeepFilterNet
    Show-Result "AudioSR (AI Upsample)" $results.AudioSR
    Show-Result "GFPGAN (Face Restore)" $results.GFPGAN
    Show-Result "VapourSynth (QTGMC)" $results.VapourSynth
    Show-Result "Watchdog (Automation)" $results.Watchdog

    Write-Host ""

    $totalTests = $results.Values.Count
    $passedTests = ($results.Values | Where-Object { $_ -eq $true }).Count
    $successRate = [math]::Round(($passedTests / $totalTests) * 100, 1)

    Write-Host "Success Rate: $passedTests/$totalTests ($successRate%)" -ForegroundColor $(if ($successRate -ge 80) { "Green" } else { "Yellow" })

    return $results
}

# Generate installation report
function New-InstallationReport {
    param($VerificationResults, $NvidiaInfo)

    Write-Section "Generating Installation Report"

    $reportFile = "installation_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
    $duration = (Get-Date) - $script:StartTime

    $report = @"
═══════════════════════════════════════════════════════════════
    TerminalAI Installation Report
═══════════════════════════════════════════════════════════════

Installation Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Duration: $($duration.ToString("hh\:mm\:ss"))
Installation Mode: $(if ($Full) { "Full" } elseif ($Audio) { "Audio" } elseif ($Faces) { "Faces" } else { "Basic" })

═══════════════════════════════════════════════════════════════
SYSTEM INFORMATION
═══════════════════════════════════════════════════════════════

OS Version: $([System.Environment]::OSVersion.VersionString)
Python Version: $(& python --version 2>&1)
GPU: $(if ($NvidiaInfo.HasNvidia) { $NvidiaInfo.GPUName } else { "No NVIDIA GPU detected" })
Driver Version: $(if ($NvidiaInfo.DriverVersion) { $NvidiaInfo.DriverVersion } else { "N/A" })
CUDA Version: $(if ($NvidiaInfo.HasNvidia) { $NvidiaInfo.CUDAVersion } else { "N/A" })

═══════════════════════════════════════════════════════════════
INSTALLATION RESULTS
═══════════════════════════════════════════════════════════════

Core Components:
  [$(if ($VerificationResults.Core) { "✓" } else { "✗" })] TerminalAI Package
  [$(if ($VerificationResults.Gradio) { "✓" } else { "✗" })] Gradio Web Interface
  [$(if ($VerificationResults.YTDLP) { "✓" } else { "✗" })] yt-dlp YouTube Downloader

AI Frameworks:
  [$(if ($VerificationResults.PyTorch) { "✓" } else { "✗" })] PyTorch
  [$(if ($VerificationResults.PyTorchCUDA) { "✓" } else { "✗" })] PyTorch CUDA Support

Optional Features:
  [$(if ($VerificationResults.Demucs) { "✓" } else { "✗" })] Demucs (AI Audio Separation)
  [$(if ($VerificationResults.DeepFilterNet) { "✓" } else { "✗" })] DeepFilterNet (AI Audio Denoise)
  [$(if ($VerificationResults.AudioSR) { "✓" } else { "✗" })] AudioSR (AI Audio Upsample)
  [$(if ($VerificationResults.GFPGAN) { "✓" } else { "✗" })] GFPGAN (Face Restoration)
  [$(if ($VerificationResults.VapourSynth) { "✓" } else { "✗" })] VapourSynth (QTGMC Deinterlacing)
  [$(if ($VerificationResults.Watchdog) { "✓" } else { "✗" })] Watchdog (Watch Folder Automation)

═══════════════════════════════════════════════════════════════
NEXT STEPS
═══════════════════════════════════════════════════════════════

1. Launch Web GUI:
   python -m vhs_upscaler.gui

   Opens at: http://localhost:7860

2. Process a video (CLI):
   python -m vhs_upscaler.vhs_upscale -i input.mp4 -o output.mp4 -p vhs

3. Analyze a video:
   python -m vhs_upscaler.vhs_upscale analyze input.mp4

4. Check available features:
   python verify_setup.py

═══════════════════════════════════════════════════════════════
TROUBLESHOOTING
═══════════════════════════════════════════════════════════════

$(if (-not $VerificationResults.PyTorchCUDA) { @"
⚠ PyTorch CUDA not available
  - GPU acceleration will not work for AI audio features
  - Face restoration may be slower
  - Video upscaling via Maxine/Real-ESRGAN should still work

  To fix:
  1. Ensure NVIDIA driver is up to date (535+)
  2. Reinstall PyTorch: pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu$($NvidiaInfo.CUDAVersion.Replace('.', ''))

"@ } else { "" })

$(if (-not $VerificationResults.VapourSynth) { @"
ℹ VapourSynth not installed
  - QTGMC deinterlacing unavailable
  - YADIF, BWDIF, W3FDIF deinterlacing still available

  To install manually:
  1. Download: https://github.com/vapoursynth/vapoursynth/releases
  2. Install VapourSynth runtime
  3. Run: pip install vapoursynth havsfunc

"@ } else { "" })

Full installation log: $($script:LogFile)

═══════════════════════════════════════════════════════════════
"@

    $report | Out-File -FilePath $reportFile -Encoding UTF8

    Write-Info "Report saved: $reportFile"
    Add-Log "Installation report generated: $reportFile"

    return $reportFile
}

# Main installation flow
function Start-Installation {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "       TerminalAI Windows Installation Script v1.0            " -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""

    Add-Log "Installation started"
    Add-Log "Parameters: Full=$Full, Audio=$Audio, Faces=$Faces, Automation=$Automation, VapourSynth=$VapourSynth, Dev=$Dev, CPUOnly=$CPUOnly"

    # Determine installation mode
    $installMode = if ($Full) { "full" } elseif ($Dev) { "dev" } else { "basic" }

    Write-Info "Installation Mode: $installMode"
    Write-Info "Target: Windows 10/11 with NVIDIA RTX support"
    Write-Info ""

    # Pre-flight checks
    if (-not (Test-Python)) {
        Write-Error "Python check failed. Aborting installation."
        return $false
    }

    if (-not (Test-Pip)) {
        Write-Error "pip check failed. Aborting installation."
        return $false
    }

    Update-Pip

    if (-not (Test-FFmpeg)) {
        $continue = Read-Host "Continue without FFmpeg? (y/N)"
        if ($continue -ne 'y') {
            Write-Warning "Installation aborted by user"
            Add-Log "Installation aborted: FFmpeg not available"
            return $false
        }
    }

    # Detect NVIDIA GPU
    $nvidiaInfo = Get-NvidiaInfo

    # Main installation sequence
    try {
        # 1. Install TerminalAI core
        if (-not (Install-TerminalAI -Mode $installMode)) {
            throw "TerminalAI installation failed"
        }

        # 2. Install PyTorch (if audio or faces enabled, or full install)
        if ($Full -or $Audio -or $Faces) {
            if (-not (Install-PyTorch -NvidiaInfo $nvidiaInfo)) {
                Write-Warning "PyTorch installation failed - some features may not work"
                Add-Log "PyTorch installation failed - continuing with limited features" -Error
            }
        }

        # 3. Install audio dependencies
        if ($Full -or $Audio) {
            if (-not (Install-AudioDependencies)) {
                Write-Warning "Audio dependencies installation had issues - check log"
                Add-Log "Audio dependencies installation: partial success" -Error
            }
        }

        # 4. Install face restoration dependencies
        if ($Full -or $Faces) {
            if (-not (Install-FaceDependencies)) {
                Write-Warning "Face restoration dependencies installation had issues - check log"
                Add-Log "Face dependencies installation: partial success" -Error
            }
        }

        # 5. Install VapourSynth
        if ($Full -or $VapourSynth) {
            if (-not (Install-VapourSynth)) {
                Write-Warning "VapourSynth installation failed - QTGMC will not be available"
                Add-Log "VapourSynth installation: failed (optional)" -Error
            }
        }

        # 6. Install automation dependencies
        if ($Full -or $Automation) {
            if (-not (Install-AutomationDependencies)) {
                Write-Warning "Automation dependencies installation had issues - check log"
                Add-Log "Automation dependencies installation: partial success" -Error
            }
        }

        # 7. Verify installations
        $verificationResults = Test-Installations

        # 8. Generate report
        $reportFile = New-InstallationReport -VerificationResults $verificationResults -NvidiaInfo $nvidiaInfo

        # Success!
        Write-Section "Installation Complete!"

        $successCount = ($verificationResults.Values | Where-Object { $_ -eq $true }).Count
        $totalCount = $verificationResults.Values.Count
        $successRate = [math]::Round(($successCount / $totalCount) * 100, 1)

        if ($successRate -ge 90) {
            Write-Success "Excellent! $successRate% of components installed successfully"
        } elseif ($successRate -ge 70) {
            Write-Warning "Good! $successRate% of components installed (some optional features missing)"
        } else {
            Write-Warning "Partial installation: $successRate% of components installed"
        }

        Write-Host ""
        Write-Info "Next Steps:"
        Write-Info "  1. Launch Web GUI: python -m vhs_upscaler.gui"
        Write-Info "  2. Process video: python -m vhs_upscaler.vhs_upscale -i video.mp4 -o output.mp4"
        Write-Info "  3. View report: $reportFile"
        Write-Info "  4. Check log: $($script:LogFile)"
        Write-Host ""

        Add-Log "Installation completed successfully"

        return $true

    } catch {
        Write-Error "Installation failed: $($_.Exception.Message)"
        Add-Log "Installation failed: $($_.Exception.Message)" -Error

        Write-Host ""
        Write-Warning "Installation encountered errors. Initiating rollback..."

        $rollback = Read-Host "Rollback installations? (y/N)"
        if ($rollback -eq 'y') {
            Invoke-Rollback
        }

        Write-Host ""
        Write-Info "Check installation log for details: $($script:LogFile)"

        return $false
    }
}

# Entry point
if ($args -contains "--help" -or $args -contains "-h" -or $args -contains "/?") {
    Write-Host @"

TerminalAI Windows Installation Script
=======================================

USAGE:
  .\install_windows.ps1 [OPTIONS]

OPTIONS:
  -Full           Install all optional features (recommended)
  -Audio          Install audio processing (Demucs, DeepFilterNet, AudioSR)
  -Faces          Install face restoration (GFPGAN, CodeFormer)
  -Automation     Install watch folder automation
  -VapourSynth    Install VapourSynth for QTGMC deinterlacing
  -Dev            Install development dependencies
  -CPUOnly        Install CPU-only PyTorch (no CUDA)
  -SkipFFmpeg     Skip FFmpeg check
  -Verbose        Enable verbose output

EXAMPLES:
  # Full installation with all features
  .\install_windows.ps1 -Full

  # Audio processing only
  .\install_windows.ps1 -Audio

  # Face restoration only
  .\install_windows.ps1 -Faces

  # Basic install without optional features
  .\install_windows.ps1

  # CPU-only installation (no GPU)
  .\install_windows.ps1 -CPUOnly

REQUIREMENTS:
  - Windows 10/11
  - Python 3.10 or higher
  - NVIDIA RTX GPU (recommended, not required)
  - FFmpeg (required for video processing)

For more information: https://github.com/parthalon025/terminalai

"@
    exit 0
}

# Execute installation
$result = Start-Installation

if ($result) {
    exit 0
} else {
    exit 1
}
