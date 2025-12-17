@echo off
REM Launch VHS Upscaler Web GUI
REM Opens a browser with the modern web interface

setlocal

echo.
echo ============================================
echo   VHS Upscaler - Web GUI
echo ============================================
echo.

REM Check if Gradio is installed
python -c "import gradio" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    pip install gradio
    echo.
)

REM Launch the GUI
echo Starting web interface...
echo.
echo The browser will open automatically.
echo Press Ctrl+C to stop the server.
echo.

python "%~dp0..\gui.py" --output-dir "%~dp0..\output" %*

pause
