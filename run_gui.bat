@echo off
:: Launch Code Compacter GUI on Windows (no console)
cd /d "%~dp0"
start "" pythonw code_compacter_gui.py "%~1"
