#!/bin/bash
# Launch Code Compacter GUI (suppress console)

cd "$(dirname "$0")"
python3 code_compacter_gui.py "$1" > /dev/null 2>&1 &
