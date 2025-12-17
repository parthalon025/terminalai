#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Automated NVIDIA Maxine Video Effects SDK setup for VHS Upscaling Pipeline

.DESCRIPTION
    Downloads and configures NVIDIA Maxine SDK, sets up environment paths,
    and validates the installation for RTX GPU acceleration.

.NOTES
    Requires: Windows 11, RTX GPU (30/40/50 series), NVIDIA Driver 535+
#>

param(
    [string]$InstallPath = "$env:LOCALAPPDATA\NVIDIA\Maxine",
    [switch]$SkipDownload,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$MaxineVersion = "0.8.2"
$MaxineUrl = "https://catalog.ngc.nvidia.com/orgs/nvidia/teams/maxine/resources/maxine_video_effects"

# Colors for output
function Write-Status { param($msg) Write-Host "[*] $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "[+] $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "[-] $msg" -ForegroundColor Red }

Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║           VHS Upscaler - Maxine SDK Installer                ║
║              NVIDIA RTX Video Enhancement                     ║
╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Magenta

# Check prerequisites
Write-Status "Checking prerequisites..."

# Check for NVIDIA GPU
$gpu = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -match "NVIDIA" }
if (-not $gpu) {
    Write-Error "No NVIDIA GPU detected. Maxine requires RTX hardware."
    exit 1
}
Write-Success "Found GPU: $($gpu.Name)"

# Check NVIDIA driver version
try {
    $nvidiaSmi = & "nvidia-smi" --query-gpu=driver_version --format=csv,noheader 2>$null
    $driverVersion = [version]($nvidiaSmi.Trim())
    if ($driverVersion.Major -lt 535) {
        Write-Warning "Driver version $nvidiaSmi detected. Recommend 535+ for best performance."
    } else {
        Write-Success "NVIDIA Driver: $nvidiaSmi"
    }
} catch {
    Write-Warning "Could not detect NVIDIA driver version. Ensure drivers are up to date."
}

# Check for FFmpeg
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) {
    Write-Warning "FFmpeg not found in PATH. Installing via winget..."
    try {
        winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    } catch {
        Write-Error "Failed to install FFmpeg. Please install manually from https://ffmpeg.org"
        Write-Host "Add FFmpeg to PATH and re-run this script."
    }
} else {
    Write-Success "FFmpeg found: $($ffmpeg.Source)"
}

# Create installation directory
Write-Status "Setting up installation directory..."
if (Test-Path $InstallPath) {
    if ($Force) {
        Remove-Item -Recurse -Force $InstallPath
    } else {
        Write-Warning "Installation path exists: $InstallPath"
        Write-Warning "Use -Force to overwrite or specify different -InstallPath"
    }
}
New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
New-Item -ItemType Directory -Force -Path "$InstallPath\bin" | Out-Null
New-Item -ItemType Directory -Force -Path "$InstallPath\bin\models" | Out-Null

# Download instructions (manual step due to NGC authentication)
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "  MANUAL DOWNLOAD REQUIRED - NVIDIA NGC Authentication" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Visit: $MaxineUrl" -ForegroundColor White
Write-Host "2. Sign in with NVIDIA account (free)" -ForegroundColor White
Write-Host "3. Download 'Video Effects SDK $MaxineVersion'" -ForegroundColor White
Write-Host "4. Extract to: $InstallPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Expected structure after extraction:" -ForegroundColor Gray
Write-Host "  $InstallPath\bin\VideoEffectsApp.exe" -ForegroundColor Gray
Write-Host "  $InstallPath\bin\models\*.trtpkg" -ForegroundColor Gray
Write-Host ""

if (-not $SkipDownload) {
    Start-Process $MaxineUrl
    Write-Host "Press Enter after downloading and extracting..." -ForegroundColor Yellow
    Read-Host
}

# Validate installation
Write-Status "Validating installation..."
$videoEffectsApp = Join-Path $InstallPath "bin\VideoEffectsApp.exe"
if (-not (Test-Path $videoEffectsApp)) {
    Write-Error "VideoEffectsApp.exe not found at expected location."
    Write-Host "Expected: $videoEffectsApp"
    exit 1
}
Write-Success "VideoEffectsApp.exe found"

# Check for models
$models = Get-ChildItem "$InstallPath\bin\models\*.trtpkg" -ErrorAction SilentlyContinue
if ($models.Count -eq 0) {
    Write-Warning "No model files found. SuperRes may not work correctly."
    Write-Host "Models should be in: $InstallPath\bin\models\"
} else {
    Write-Success "Found $($models.Count) model file(s)"
}

# Set environment variables
Write-Status "Configuring environment variables..."
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
$binPath = "$InstallPath\bin"
if ($currentPath -notlike "*$binPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$binPath", "User")
    Write-Success "Added Maxine bin to user PATH"
}

[Environment]::SetEnvironmentVariable("MAXINE_HOME", $InstallPath, "User")
Write-Success "Set MAXINE_HOME=$InstallPath"

# Create config file with paths
$configPath = Join-Path $PSScriptRoot "config.yaml"
if (Test-Path $configPath) {
    $config = Get-Content $configPath -Raw
    $config = $config -replace 'maxine_path:.*', "maxine_path: `"$InstallPath\bin`""
    $config = $config -replace 'model_dir:.*', "model_dir: `"$InstallPath\bin\models`""
    Set-Content $configPath $config
    Write-Success "Updated config.yaml with installation paths"
}

# Test execution
Write-Status "Testing Maxine SDK..."
try {
    $testOutput = & $videoEffectsApp --help 2>&1
    if ($testOutput -match "VideoEffectsApp") {
        Write-Success "Maxine SDK responds correctly"
    }
} catch {
    Write-Warning "Could not execute VideoEffectsApp. Check NVIDIA drivers and CUDA installation."
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Open a new terminal (to refresh PATH)" -ForegroundColor Gray
Write-Host "  2. Test: python vhs_upscale.py --help" -ForegroundColor Gray
Write-Host "  3. Run: python vhs_upscale.py --input video.mp4 --output upscaled.mp4" -ForegroundColor Gray
Write-Host ""
Write-Host "For watch folder mode:" -ForegroundColor White
Write-Host "  python vhs_upscale.py --watch --input ./input --output ./output" -ForegroundColor Cyan
Write-Host ""
