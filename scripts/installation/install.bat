@echo off
REM TerminalAI Quick Installation Launcher
REM ========================================
REM Launches PowerShell installation script with user-friendly prompts

title TerminalAI Installation

echo.
echo ================================================================
echo       TerminalAI Windows Installation Launcher
echo ================================================================
echo.
echo This script will install TerminalAI and all optional features.
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running as Administrator
) else (
    echo [WARNING] Not running as Administrator
    echo           Some features may require admin privileges
    echo.
    echo Right-click this file and select "Run as Administrator" for best results.
    echo.
    pause
)

echo.
echo Select installation mode:
echo.
echo   1. Full Installation (Recommended)
echo      - All features including AI audio, face restoration, VapourSynth
echo      - Requires ~5 GB download
echo      - Installation time: ~15-20 minutes
echo.
echo   2. Basic Installation
echo      - Core TerminalAI only (web GUI, video processing)
echo      - Requires ~200 MB download
echo      - Installation time: ~2-3 minutes
echo.
echo   3. Audio Processing Only
echo      - Core + AI audio features (Demucs, DeepFilterNet, AudioSR)
echo      - Requires ~4 GB download
echo      - Installation time: ~8-10 minutes
echo.
echo   4. Face Restoration Only
echo      - Core + Face restoration (GFPGAN, CodeFormer)
echo      - Requires ~3 GB download
echo      - Installation time: ~7-9 minutes
echo.
echo   5. Custom Installation
echo      - Choose specific components
echo.
echo   6. Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto full
if "%choice%"=="2" goto basic
if "%choice%"=="3" goto audio
if "%choice%"=="4" goto faces
if "%choice%"=="5" goto custom
if "%choice%"=="6" goto end

echo Invalid choice. Exiting.
goto end

:full
echo.
echo Starting FULL installation...
echo.
powershell.exe -ExecutionPolicy Bypass -File ".\install_windows.ps1" -Full
goto verify

:basic
echo.
echo Starting BASIC installation...
echo.
powershell.exe -ExecutionPolicy Bypass -File ".\install_windows.ps1"
goto verify

:audio
echo.
echo Starting AUDIO PROCESSING installation...
echo.
powershell.exe -ExecutionPolicy Bypass -File ".\install_windows.ps1" -Audio
goto verify

:faces
echo.
echo Starting FACE RESTORATION installation...
echo.
powershell.exe -ExecutionPolicy Bypass -File ".\install_windows.ps1" -Faces
goto verify

:custom
echo.
echo Custom Installation Options:
echo.
set /p install_audio="Install Audio Processing (Demucs, DeepFilterNet, AudioSR)? (Y/N): "
set /p install_faces="Install Face Restoration (GFPGAN, CodeFormer)? (Y/N): "
set /p install_vs="Install VapourSynth (QTGMC deinterlacing)? (Y/N): "
set /p install_auto="Install Watch Folder Automation? (Y/N): "
set /p cpu_only="CPU-only mode (no CUDA, slower but works without NVIDIA GPU)? (Y/N): "

set params=
if /i "%install_audio%"=="Y" set params=%params% -Audio
if /i "%install_faces%"=="Y" set params=%params% -Faces
if /i "%install_vs%"=="Y" set params=%params% -VapourSynth
if /i "%install_auto%"=="Y" set params=%params% -Automation
if /i "%cpu_only%"=="Y" set params=%params% -CPUOnly

echo.
echo Starting CUSTOM installation with options:%params%
echo.
powershell.exe -ExecutionPolicy Bypass -File ".\install_windows.ps1"%params%
goto verify

:verify
echo.
echo ================================================================
echo.
if %errorLevel% == 0 (
    echo [SUCCESS] Installation completed!
    echo.
    echo Running verification...
    echo.
    python verify_setup.py

    echo.
    echo ================================================================
    echo                 Installation Complete!
    echo ================================================================
    echo.
    echo Next steps:
    echo   1. Launch Web GUI:    python -m vhs_upscaler.gui
    echo   2. Process a video:   python -m vhs_upscaler.vhs_upscale -i video.mp4 -o output.mp4
    echo   3. Read the guide:    INSTALL_WINDOWS.md
    echo.
    echo Installation report saved in current directory.
    echo.
) else (
    echo [ERROR] Installation failed!
    echo.
    echo Please check the installation log for details.
    echo.
    echo Troubleshooting:
    echo   1. Ensure Python 3.10+ is installed
    echo   2. Ensure FFmpeg is installed
    echo   3. Check internet connection
    echo   4. Run as Administrator
    echo.
    echo For help, see: INSTALL_WINDOWS.md
    echo.
)

set /p launch_gui="Launch Web GUI now? (Y/N): "
if /i "%launch_gui%"=="Y" (
    echo.
    echo Launching TerminalAI Web GUI...
    echo Opens at: http://localhost:7860
    echo.
    start python -m vhs_upscaler.gui
)

:end
echo.
pause
