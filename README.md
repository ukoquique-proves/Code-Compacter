# Code Compacter

A Python tool that compacts an entire project into a single, AI-readable text file.

## GUI Version (Recommended)

Launch the graphical interface with silent launch and drag-and-drop support:

```bash
./run_gui.sh
```

**Features:**
- **Drag-and-Drop**: Drag a folder onto the `CodeCompacter.desktop` icon or the app directory itself.
- **Silent Launch**: No messy console windows next to your app.
- **Smart Selection**: Click the drop zone or "Browse" to select a project folder.
- **AI Ready**: Generates a structured `.txt` file optimized for AI context.
- **Open Output**: View the result immediately with the "Open Output" button.

## CLI Version

```bash
# Backup current directory
python3 code_compacter.py .

# Backup specific project
python3 code_compacter.py /path/to/project

# Custom output filename
python3 code_compacter.py . -o my_backup.txt
```

## Output Format

The generated file contains:
- **Header** with source path and timestamp
- **Each file** marked with its relative path and language
- **Summary** with statistics and binary file list

Example output:
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
Files skipped: 8
Total lines: 1,247
================================================================================
```

## Features

- **Smart filtering**: Ignores common non-code files (`.git`, `node_modules`, binaries, etc.)
- **Language detection**: Tags each file with its programming language
- **Binary detection**: Automatically skips binary files
- **Encoding handling**: Tries multiple encodings (UTF-8, Latin-1, etc.)
- **Clean format**: Structured for easy AI parsing

## Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Custom output filename |
| `--ignore` | Additional ignore patterns |
| `--no-binary-info` | Skip listing binary files |
| `--include-defaults` | Use only default ignores |

## Puppy Linux / ROX-Filer Support

This project is optimized for Puppy Linux:

**Option 1: AppDir Drag-and-Drop (Recommended)**
Drag any project folder and drop it directly onto the `Code_Compacter` folder. The `AppRun` script handles the rest.

**Option 2: Desktop Shortcut**
Drag a folder onto `CodeCompacter.desktop` for instant compaction.

**Option 3: Terminal launcher (shows errors)**
```bash
./run_gui_terminal.sh
```

**Option 4: Run directly**
```bash
python3 code_compacter_gui.py
```

**Diagnostic - check if requirements are met:**
```bash
python3 -c "import tkinter; print('Tkinter: OK')"
```

**If tkinter is missing, install it:**
```bash
# PuppyLinux/Debian based
apt-get install python3-tk

# Or use the package manager (PPM) in PuppyLinux
```

**Most likely cause**: PuppyLinux uses `rxvt` or `urxvt` terminal. The `run_gui_terminal.sh` tries these automatically. If still failing, open a terminal manually and run:
```bash
cd /root/COMPACTADOR/Code_Compacter
python3 code_compacter_gui.py 2>&1
```
This will show any error messages.

## Ignored by Default

- Version control: `.git`
- Virtual environments: `.venv`, `venv`, `node_modules`
- IDE files: `.vscode`, `.idea`
- Build artifacts: `build`, `dist`, `target`
- Cache: `__pycache__`, `.pytest_cache`
- Binary files: images, videos, executables, archives
- Lock files: `package-lock.json`, `poetry.lock`, etc.
