@echo off
REM VHS to 1080p Upscale
REM Usage: upscale_vhs_1080p.bat input.mp4 [output.mp4]

setlocal

set INPUT=%~1
set OUTPUT=%~2

if "%INPUT%"=="" (
    echo Usage: %~nx0 input.mp4 [output.mp4]
    echo.
    echo Upscales VHS-quality video to 1080p using NVIDIA Maxine
    exit /b 1
)

if "%OUTPUT%"=="" (
    set OUTPUT=%~dpn1_1080p.mp4
)

echo.
echo ========================================
echo   VHS to 1080p Upscaler
echo ========================================
echo   Input:  %INPUT%
echo   Output: %OUTPUT%
echo ========================================
echo.

python "%~dp0..\vhs_upscale.py" ^
    --input "%INPUT%" ^
    --output "%OUTPUT%" ^
    --preset vhs ^
    --resolution 1080 ^
    --quality 0

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Success! Output saved to: %OUTPUT%
) else (
    echo.
    echo Error: Processing failed
    exit /b 1
)
