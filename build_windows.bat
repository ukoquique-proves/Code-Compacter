@echo off
REM Build script for Windows — bundles tkinterdnd2 correctly.
REM
REM tkinterdnd2 is a thin Python wrapper around a Tcl/Tk "tkdnd" package that
REM ships as data files inside the tkinterdnd2 install, not as pure Python.
REM PyInstaller's default hidden-import discovery misses these data files,
REM which is the most common reason drag-and-drop silently stops working in
REM the packaged .exe even though it works fine when run with `python`.

setlocal enabledelayedexpansion

REM Locate the tkdnd data directory inside the installed tkinterdnd2 package
for /f "delims=" %%i in ('python -c "import tkinterdnd2, os; print(os.path.join(os.path.dirname(tkinterdnd2.__file__), 'tkdnd'))"') do set TKDND_PATH=%%i

if not exist "%TKDND_PATH%" (
    echo ERROR: tkdnd data not found at %TKDND_PATH%
    echo Run: pip install tkinterdnd2
    pause
    exit /b 1
)

pyinstaller code_compacter_gui.py ^
    --noconsole ^
    --onedir ^
    -y ^
    --name CodeCompacter ^
    --add-data "%TKDND_PATH%;tkinterdnd2/tkdnd" ^
    --hidden-import tkinterdnd2

echo.
echo Build complete: dist\CodeCompacter
echo Verify drag-and-drop on a CLEAN machine (no system-wide tkinterdnd2 install)
pause
