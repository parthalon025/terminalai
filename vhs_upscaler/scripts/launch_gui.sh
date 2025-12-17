#!/bin/bash
# Launch VHS Upscaler Web GUI
# Opens a browser with the modern web interface

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "============================================"
echo "  VHS Upscaler - Web GUI"
echo "============================================"
echo ""

# Check if Gradio is installed
if ! python3 -c "import gradio" 2>/dev/null; then
    echo "Installing required packages..."
    pip3 install gradio
    echo ""
fi

# Launch the GUI
echo "Starting web interface..."
echo ""
echo "The browser will open automatically."
echo "Press Ctrl+C to stop the server."
echo ""

python3 "$PARENT_DIR/gui.py" --output-dir "$PARENT_DIR/output" "$@"
