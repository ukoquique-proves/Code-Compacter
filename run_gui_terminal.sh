#!/bin/bash
# Launcher that opens a terminal to show errors

cd "$(dirname "$0")"

# Try different terminal emulators common in PuppyLinux
if command -v rxvt &> /dev/null; then
    rxvt -e bash -c 'python3 code_compacter_gui.py; echo "Press Enter..."; read'
elif command -v urxvt &> /dev/null; then
    urxvt -e bash -c 'python3 code_compacter_gui.py; echo "Press Enter..."; read'
elif command -v xterm &> /dev/null; then
    xterm -e bash -c 'python3 code_compacter_gui.py; echo "Press Enter..."; read'
elif command -v roxterm &> /dev/null; then
    roxterm -e bash -c 'python3 code_compacter_gui.py; echo "Press Enter..."; read'
else
    # Fallback - try to detect and use whatever terminal is available
    for term in lxterminal xfce4-terminal gnome-terminal konsole terminal; do
        if command -v $term &> /dev/null; then
            $term -e bash -c 'cd "$(dirname "$0")"; python3 code_compacter_gui.py; echo "Press Enter..."; read' "$0"
            exit 0
        fi
    done
    
    # Last resort - run directly and hope for the best
    python3 code_compacter_gui.py
fi
