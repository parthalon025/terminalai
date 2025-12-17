# TerminalAI Quick Install Script for Windows
# ============================================
# Usage: .\install.ps1 [-Dev]
# Run in PowerShell: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

param(
    [switch]$Dev
)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  TerminalAI Video Upscaler Installer" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -ge 3 -and $minor -ge 10) {
            Write-Host "[OK] Python $major.$minor detected" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Python 3.10+ required (found $major.$minor)" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.10+" -ForegroundColor Red
    Write-Host "  Download: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check for FFmpeg
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    if ($ffmpegVersion -match "ffmpeg version") {
        Write-Host "[OK] FFmpeg detected" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARN] FFmpeg not found - please install FFmpeg" -ForegroundColor Yellow
    Write-Host "  Download: https://ffmpeg.org/download.html" -ForegroundColor Yellow
    Write-Host "  Or use: winget install FFmpeg" -ForegroundColor Yellow
}

# Check for NVIDIA GPU
try {
    $gpuInfo = nvidia-smi --query-gpu=name --format=csv,noheader 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] NVIDIA GPU: $gpuInfo" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARN] NVIDIA GPU not detected (AI upscaling requires RTX GPU)" -ForegroundColor Yellow
}

# Check for NVIDIA Maxine SDK
$maxinePath = "$env:LOCALAPPDATA\NVIDIA\Maxine\bin\VideoEffectsApp.exe"
if (Test-Path $maxinePath) {
    Write-Host "[OK] NVIDIA Maxine SDK detected" -ForegroundColor Green
} else {
    Write-Host "[WARN] NVIDIA Maxine SDK not found" -ForegroundColor Yellow
    Write-Host "  Download: https://developer.nvidia.com/maxine" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan

# Install based on argument
if ($Dev) {
    Write-Host "Installing with development dependencies..." -ForegroundColor Cyan
    pip install -e ".[dev]"
} else {
    pip install -e .
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Installation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the GUI:" -ForegroundColor Cyan
Write-Host "  python -m vhs_upscaler.gui" -ForegroundColor White
Write-Host ""
Write-Host "Or use command line:" -ForegroundColor Cyan
Write-Host "  python -m vhs_upscaler.vhs_upscale -i video.mp4 -o output.mp4" -ForegroundColor White
Write-Host ""

# Run tests if dev install
if ($Dev) {
    Write-Host "Running tests..." -ForegroundColor Cyan
    pytest tests/ -v --tb=short
}
