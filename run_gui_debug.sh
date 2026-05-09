#!/bin/bash
# Debug launcher for PuppyLinux

cd "$(dirname "$0")"

# Check for display
if [ -z "$DISPLAY" ]; then
    echo "ERROR: No DISPLAY variable set"
    exit 1
fi

# Check Python
echo "Python version:"
python3 --version 2>&1 || echo "Python3 not found"

# Check tkinter
echo ""
echo "Checking tkinter:"
python3 -c "import tkinter; print('Tkinter OK')" 2>&1

# Run with error output visible
echo ""
echo "Launching GUI..."
python3 code_compacter_gui.py 2>&1

echo ""
echo "Press Enter to close..."
read
