@echo off
REM Watch Folder Mode
REM Monitors ./input folder and processes videos automatically

setlocal

set INPUT_DIR=%~dp0..\input
set OUTPUT_DIR=%~dp0..\output

REM Allow custom paths via arguments
if not "%~1"=="" set INPUT_DIR=%~1
if not "%~2"=="" set OUTPUT_DIR=%~2

echo.
echo ========================================
echo   VHS Upscaler - Watch Folder Mode
echo ========================================
echo   Input Folder:  %INPUT_DIR%
echo   Output Folder: %OUTPUT_DIR%
echo.
echo   Drop video files into the input folder
echo   Processed files will appear in output
echo.
echo   Press Ctrl+C to stop
echo ========================================
echo.

REM Create folders if they don't exist
if not exist "%INPUT_DIR%" mkdir "%INPUT_DIR%"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

python "%~dp0..\vhs_upscale.py" ^
    --watch ^
    --input "%INPUT_DIR%" ^
    --output "%OUTPUT_DIR%" ^
    --preset vhs ^
    --resolution 1080

echo.
echo Watch mode ended.
pause
