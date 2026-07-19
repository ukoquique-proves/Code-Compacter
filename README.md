# Code Compacter

A Python tool that compacts an entire project into a single, AI-readable text file.

## Architecture

- `src/core.py` — central processing logic (file filtering, language detection, compacting)
- `code_compacter_gui.py` — GUI wrapper using Tkinter
- `code_compacter.py` — CLI wrapper for terminal use

## Requirements

- Python 3.13+
- `python3-tk` (tkinter)
- `tkinterdnd2` (optional — enables drag-and-drop into the window)

Install tkinter on Debian/Puppy Linux:

```bash
apt-get install python3-tk
```

Install tkinterdnd2 (Linux):

```bash
pip install -r requirements.txt --break-system-packages
```

On Windows, standard pip installation is sufficient:

```bash
pip install -r requirements.txt
```

## Running the GUI

```bash
python3 code_compacter_gui.py
```

Or use the silent launcher (no console window):

```bash
./run_gui.sh
```

**Features:**
- Drop a folder onto the app icon — compacts immediately, no window (headless mode)
- Drag a folder onto the drop zone inside the window (requires tkinterdnd2) or use Browse
- Extra ignores field — add patterns like `*.log, temp/` on top of the defaults
- Progress bar and persistent output path label after completion
- Open Output button to view the result immediately
- If tkinterdnd2 is not installed, status bar says so and Browse still works

## Headless / silent mode

Dropping a folder onto the desktop icon or AppDir runs compaction silently with no window:

```bash
# Same as dropping onto the icon
python3 code_compacter_gui.py --headless /path/to/project
```

On completion a desktop notification appears — PowerShell toast on Windows, `notify-send`/`xmessage` on Linux. If none are available the notification is skipped silently; the output file is always the ground truth. Opening the icon with no argument still opens the full GUI.

## CLI

```bash
# Compact current directory
python3 code_compacter.py .

# Compact a specific project
python3 code_compacter.py /path/to/project

# Custom output filename
python3 code_compacter.py . -o my_compact.txt
```

## Output Format

```
--------------------------------------------------------------------------------
FILE: src/main.py
LANGUAGE: python
--------------------------------------------------------------------------------
def main():
    print("Hello")

================================================================================
SUMMARY
================================================================================
Files processed: 42
Total lines: 1,247
================================================================================
```

## Ignored by Default

- Version control: `.git`
- Virtual environments: `.venv`, `venv`, `node_modules`
- IDE files: `.vscode`, `.idea`
- Build artifacts: `build`, `dist`, `target`
- Cache: `__pycache__`, `.pytest_cache`
- Binary files: images, videos, executables, archives
- Lock files: `package-lock.json`, `poetry.lock`, etc.

Extra patterns can be added at runtime via the GUI's "Extra ignores" field or the CLI's `--ignore` flag.

## Windows

**Running the Application:**
- **GUI:** Double-click the `run_gui.bat` script to launch the application.
- **Headless Mode:** Drag and drop any project folder onto `run_gui.bat` to compact it silently in the background.
- **Desktop Shortcut:** To easily run the app from your desktop (just like on Linux), double-click the `create_windows_shortcut.bat` file. This will automatically generate a "Code Compacter" shortcut on your Desktop. You can double-click this shortcut to open the GUI, or drag and drop a folder onto it for silent compaction!

**Building a Standalone Binary:**
To create a standalone `.exe` that correctly bundles the `tkinterdnd2` dependency (ensuring drag-and-drop works), use the provided build script:
```cmd
build_windows.bat
```

## Puppy Linux / ROX-Filer

**Run directly (most reliable):**

```bash
python3 code_compacter_gui.py
```

**AppDir drag-and-drop:**
Drop any project folder onto the `Code_Compacter` folder itself. `AppRun` handles the rest.

**Desktop shortcut:**
Copy the `.desktop` file to `/root/Desktop/` — ROX-Filer only picks it up from there:

```bash
cp CodeCompacter.desktop /root/Desktop/
chmod +x /root/Desktop/CodeCompacter.desktop
```

**Debug launcher (shows errors in terminal):**

```bash
./run_gui_terminal.sh
```

## Building a Standalone Binary

The recommended way is via Docker, which sidesteps the host Python shared library and glibc issues entirely:

```bash
bash docker_build.sh
```

This produces `dist/CodeCompacter/` — zip it and distribute. Built against glibc 2.31 (Debian bullseye), so it runs on PuppyLinux and any system with glibc ≥ 2.31.

If you want to build directly on the host (requires `python3.13-dev` to be installable):

```bash
pip install pyinstaller --break-system-packages
bash build_linux.sh
```

`build_linux.sh` passes the tkdnd data directory to PyInstaller via `--add-data`. This is the critical step — `--hidden-import tkinterdnd2` alone produces a binary where drag-and-drop silently doesn't work.

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for the full breakdown of issues encountered, including why the host build is blocked on this system and the glibc compatibility considerations.

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for known issues, including:

- `libpython3.13.so.1.0` not found on host build
- `libtk8.6.so` missing in slim Docker image (fixed in `Dockerfile.build`)
- glibc compatibility and how to target older systems
- Desktop icon not responding in ROX-Filer
- AppRun permission denied
