# Changelog

## Unreleased

### Added
- `Extra ignores` field in the GUI — add patterns like `*.log, temp/` at runtime without editing code
- Persistent output path label under the progress bar so the full output path stays visible after completion
- `requirements.txt` declaring `tkinterdnd2>=0.4.2`
- `build_linux.sh` — build script that locates the `tkdnd` Tcl/Tk data directory inside the tkinterdnd2 package and passes it to PyInstaller via `--add-data`, fixing the silent drag-and-drop failure in standalone binaries
- `Dockerfile.build` — builds against `python:3.13-slim-bullseye` (glibc 2.31) with `tk-dev` installed, bypassing the host `libpython3.13.so.1.0` and `python3.13-dev` package conflict
- `docker_build.sh` — one-command build: runs Docker build, extracts `dist/CodeCompacter/` to the workspace
- `TROUBLESHOOTING.md` documenting all three build blockers encountered and their resolutions
- `ROADMAP.md` outlining the headless/silent drop mode feature plan
- `README.md` rewritten to reflect current features, correct install commands, and link to TROUBLESHOOTING.md
- Headless mode (`--headless`): dropping a folder onto the app icon now compacts it immediately with no window; opening the icon with no argument still opens the GUI; best-effort desktop notification via `notify-send` / `xmessage` on completion
- `build_windows.bat` — Windows build script for PyInstaller, bundling tkinterdnd2 data files for drag-and-drop support

### Changed
- `build_linux.sh` now uses `--onedir` instead of `--onefile` as default build mode
- `compact_directory_logic` in `src/core.py` now accepts an `extra_ignores` parameter that merges with `DEFAULT_IGNORES` at runtime
- Missing `tkinterdnd2` now surfaces in the status bar ("Drag-and-drop not bundled — use Browse or drop onto the desktop icon") instead of only appearing in the processing log
- GUI minimum height increased to 540×440 to accommodate the new fields

### Fixed
- Standalone binary drag-and-drop was silently broken when built with `--hidden-import tkinterdnd2` alone; `build_linux.sh` fixes this by bundling the tkdnd data files
- CLI `--ignore` flag was documented in the README options table but never implemented; `code_compacter.py` now accepts `--ignore PATTERN [PATTERN ...]` and passes it through to `compact_directory_logic` as `extra_ignores`
- Shell injection risk in headless completion notification and `open_output`:
  - Replaced `os.system(f'...')` with `subprocess.Popen([...])` list args (no OS shell)
  - COMPLETELY fixed interpreter-level injection for Windows PowerShell: no string interpolation of untrusted filename in PowerShell script; message passed via `COMPACTER_MSG` environment variable, script encoded as Base64 with `-EncodedCommand`
- Headless notification was Linux-only; replaced with a platform-aware `_notify_headless()` function (PowerShell toast on Windows, `notify-send`/`xmessage` on Linux, silent fallback if none available)
- `docker_build.sh` would fail on repeat runs with "container name already in use"; stale container is now removed before `docker create`
- `docker_build.sh` sent the entire `dist/` directory (up to 28 MB) as Docker build context; `.dockerignore` now excludes `dist/`, `build/`, `__pycache__/` — context reduced to ~248 KB
- PyInstaller failed on repeat builds inside Docker with "output directory is not empty"; added `-y` flag to `build_linux.sh`
- `Dockerfile.build` smoke-tests the packaged binary with `--headless` before extraction, catching silent failures in the built binary that source-level tests miss
- Headless run could fail with exit code 1 even after successfully writing the compact file; notification failure is now completely guarded, `_notify_headless()` swallows all exceptions, and the call is wrapped in an additional try/except as a double safeguard

## 1.0.0 — Initial release

- GUI (`code_compacter_gui.py`) with drag-and-drop via tkinterdnd2, folder browse, progress bar, and processing log
- CLI (`code_compacter.py`) with source/output arguments
- `src/core.py` with file walking, binary detection, encoding fallback, and language tagging
- `AppRun` and `CodeCompacter.desktop` for ROX-Filer / Puppy Linux integration
- `run_gui.sh` silent launcher and `run_gui_terminal.sh` debug launcher
