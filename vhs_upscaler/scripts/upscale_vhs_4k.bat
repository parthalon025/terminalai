@echo off
REM VHS to 4K Upscale
REM Usage: upscale_vhs_4k.bat input.mp4 [output.mp4]

setlocal

set INPUT=%~1
set OUTPUT=%~2

if "%INPUT%"=="" (
    echo Usage: %~nx0 input.mp4 [output.mp4]
    echo.
    echo Upscales VHS-quality video to 4K using NVIDIA Maxine
    echo Note: Requires 16GB+ VRAM for best results
    exit /b 1
)

if "%OUTPUT%"=="" (
    set OUTPUT=%~dpn1_4k.mp4
)

echo.
echo ========================================
echo   VHS to 4K Upscaler
echo ========================================
echo   Input:  %INPUT%
echo   Output: %OUTPUT%
echo   Note:   This may take a while!
echo ========================================
echo.

python "%~dp0..\vhs_upscale.py" ^
    --input "%INPUT%" ^
    --output "%OUTPUT%" ^
    --preset vhs ^
    --resolution 2160 ^
    --quality 0 ^
    --crf 18

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Success! Output saved to: %OUTPUT%
) else (
    echo.
    echo Error: Processing failed
    exit /b 1
)
