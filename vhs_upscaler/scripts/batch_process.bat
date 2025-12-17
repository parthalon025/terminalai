@echo off
REM Batch Process Multiple Files
REM Usage: batch_process.bat folder_path [resolution]

setlocal enabledelayedexpansion

set INPUT_FOLDER=%~1
set RESOLUTION=%~2
set PRESET=vhs

if "%INPUT_FOLDER%"=="" (
    echo Usage: %~nx0 folder_path [resolution]
    echo.
    echo Processes all video files in a folder
    echo.
    echo Arguments:
    echo   folder_path  - Folder containing videos
    echo   resolution   - Target resolution: 1080 (default), 1440, 2160
    echo.
    echo Example:
    echo   %~nx0 "C:\Videos\VHS Tapes" 1080
    exit /b 1
)

if "%RESOLUTION%"=="" set RESOLUTION=1080

echo.
echo ========================================
echo   VHS Upscaler - Batch Processing
echo ========================================
echo   Input Folder: %INPUT_FOLDER%
echo   Resolution:   %RESOLUTION%p
echo ========================================
echo.

set COUNT=0
set SUCCESS=0
set FAILED=0

for %%f in ("%INPUT_FOLDER%\*.mp4" "%INPUT_FOLDER%\*.avi" "%INPUT_FOLDER%\*.mkv" "%INPUT_FOLDER%\*.mov") do (
    set /a COUNT+=1
    set "FILENAME=%%~nf"
    set "OUTPUT=%%~dpf!FILENAME!_%RESOLUTION%p.mp4"

    echo.
    echo [!COUNT!] Processing: %%~nxf
    echo     Output: !OUTPUT!
    echo.

    python "%~dp0..\vhs_upscale.py" ^
        --input "%%f" ^
        --output "!OUTPUT!" ^
        --preset %PRESET% ^
        --resolution %RESOLUTION% ^
        --quality 0

    if !ERRORLEVEL! EQU 0 (
        set /a SUCCESS+=1
        echo     Status: SUCCESS
    ) else (
        set /a FAILED+=1
        echo     Status: FAILED
    )
)

echo.
echo ========================================
echo   Batch Processing Complete
echo ========================================
echo   Total:     %COUNT%
echo   Success:   %SUCCESS%
echo   Failed:    %FAILED%
echo ========================================
echo.

pause
