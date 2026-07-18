@echo off
:: Launch Code Compacter GUI on Windows.
:: - Double-clicked (no argument): opens the GUI.
:: - Folder dropped onto this file: runs headless, no window.
cd /d "%~dp0"
if "%~1"=="" (
    start "" pythonw code_compacter_gui.py
) else (
    python code_compacter_gui.py --headless "%~1"
)
