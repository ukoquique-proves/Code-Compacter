#!/bin/bash
# Build script for PuppyLinux — bundles tkinterdnd2 correctly.
#
# tkinterdnd2 is a thin Python wrapper around a Tcl/Tk "tkdnd" package that
# ships as data files inside the tkinterdnd2 install, not as pure Python.
# PyInstaller's default hidden-import discovery misses these data files,
# which is the most common reason drag-and-drop silently stops working in
# the packaged .exe/binary even though it works fine when run with `python3`.

set -e

# Locate the tkdnd data directory inside the installed tkinterdnd2 package
TKDND_PATH=$(python3 -c "import tkinterdnd2, os; print(os.path.join(os.path.dirname(tkinterdnd2.__file__), 'tkdnd'))")

if [ ! -d "$TKDND_PATH" ]; then
    echo "ERROR: tkdnd data not found at $TKDND_PATH"
    echo "Run: pip install tkinterdnd2"
    exit 1
fi

pyinstaller code_compacter_gui.py \
    --noconsole \
    --onedir \
    -y \
    --name CodeCompacter \
    --add-data "$TKDND_PATH:tkinterdnd2/tkdnd" \
    --hidden-import tkinterdnd2

echo ""
echo "Build complete: dist/CodeCompacter"
echo "Verify drag-and-drop on a CLEAN machine (no system-wide tkinterdnd2 install)"
echo "before trusting the demo video matches the shipped product."
