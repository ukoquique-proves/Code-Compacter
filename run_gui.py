#!/usr/bin/env python3
"""
Python-based GUI launcher for PuppyLinux (works with ROX file manager)
"""

import subprocess
import sys
import os

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Try to launch with error capture
try:
    cmd = [sys.executable, 'code_compacter_gui.py']
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])

    headless = '--headless' in sys.argv[1:]
    result = subprocess.run(
        cmd,
        capture_output=not headless,
        text=True,
        check=False
    )
    
    if result.returncode != 0:
        # Error occurred - show in terminal
        error_msg = f"Error launching GUI:\n\n{result.stderr}\n\nPress Enter to close..."
        
        # Try to show in terminal
        try:
            subprocess.run(['xterm', '-e', f'echo "{error_msg}"; read'], check=False)
        except:
            try:
                subprocess.run(['rxvt', '-e', 'bash', '-c', f'echo "{error_msg}"; read'], check=False)
            except:
                # Fallback: print to stdout (visible if run from terminal)
                print(error_msg)
                input()
    
except Exception as e:
    print(f"Failed to launch: {e}")
    input("Press Enter to close...")
