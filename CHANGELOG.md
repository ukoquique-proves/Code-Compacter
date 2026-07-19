# Changelog

## Unreleased

### Added
- `Extra ignores` field in the GUI — add patterns like `*.log, temp/` at runtime without editing code
- Persistent output path label under the progress bar so the full output path stays visible after completion
- `requirements.txt` declaring `tkinterdnd2>=0.4.2`
- `build_linux.sh` — build script that locates the `tkdnd` Tcl/Tk data directory inside the tkinterdnd2 package and passes it to PyInstaller via `--add-data`, fixing the silent drag-and-drop failure in standalone binaries
- `Dockerfile.build` — builds against `python:3.13-slim-bullseye` (glibc 2.31) with `tk-dev` installed, bypassing the host `libpython3.13.so.1.0` and `python3.13-dev` package conflict
- `docker_build.sh` — one-command build: runs Docker build, extracts `dist/CodeCompacter/` to the workspace
- `.dockerignore` — excludes `dist/`, `build/`, `__pycache__/` from Docker build context (reduces context from ~28 MB to ~248 KB)
- `TROUBLESHOOTING.md` documenting all three build blockers encountered and their resolutions
- `ROADMAP.md` — headless mode feature plan, now fully completed
- `README.md` rewritten to reflect current features, correct install commands, and link to TROUBLESHOOTING.md
- Headless mode (`--headless`): dropping a folder onto the app icon compacts it immediately with no window; opening the icon with no argument still opens the GUI
- `_notify_headless()` — platform-aware completion notification: PowerShell toast (Windows), `notify-send`/`xmessage` (Linux); swallows all exceptions so a missing notification tool can never fail the run
- `run_gui.bat` — double-click opens GUI; dropping a folder runs headless (matches `AppRun` behaviour on Linux); uses `python` (not `pythonw`) in headless mode so `✓ Done` output is visible
- `create_windows_shortcut.bat` — automatically generates a Windows `.lnk` Desktop shortcut that supports both double-click execution and drag-and-drop headless compaction.

### Changed
- `AppRun` updated to pass `--headless "$@"` when called with a path argument; opens GUI when called with no argument
- `run_gui.py` — `capture_output` is now `False` in headless mode so progress and `✓ Done` lines are visible; GUI mode still captures stderr for the error dialog
- `build_linux.sh` now uses `--onedir` (directory bundle) instead of `--onefile`, and adds `-y` to allow overwriting existing output without prompting
- `compact_directory_logic` in `src/core.py` now accepts an `extra_ignores` parameter that merges with `DEFAULT_IGNORES` at runtime
- Missing `tkinterdnd2` now surfaces in the status bar instead of only the processing log
- GUI minimum height increased to 540×440 to accommodate the new fields
- Supported platforms narrowed to Linux and Windows only — macOS/darwin references removed from all files

### Fixed
- `CodeCompacter.desktop` had wrong install path (`/root/COMPACTADOR/...`) — corrected to `/root/my-applications/COMPACTADOR/...`; same fix applied to the copy in `COMPACT_SELL`
- Standalone binary drag-and-drop was silently broken when built with `--hidden-import tkinterdnd2` alone; `build_linux.sh` fixes this by bundling the tkdnd data files
- `CodeCompacter.spec` hardcoded the host tkdnd path; replaced with a dynamic lookup using the same logic as `build_linux.sh`
- CLI `--ignore` flag was documented but never implemented; `code_compacter.py` now accepts `--ignore PATTERN [PATTERN ...]`
- Shell injection in `open_output` — replaced `os.system(f'xdg-open "{path}"')` with `subprocess.Popen(["xdg-open", path])` (no shell)
- Shell injection in headless notification — Windows PowerShell message now passed via `COMPACTER_MSG` env var and `-EncodedCommand` Base64; no filename interpolation in any script string
- `docker_build.sh` failed on repeat runs with "container name already in use" — stale container is now removed before `docker create`
- `Dockerfile.build` smoke-tests the packaged binary with `--headless` before extraction, catching silent failures that source-level tests miss
- `docker_build.sh` verify message pointed at `./dist/CodeCompacter` (a directory) instead of the executable `./dist/CodeCompacter/CodeCompacter`
- `run_gui.bat` always opened the GUI regardless of arguments — dropping a folder onto it now correctly triggers headless mode, matching the behaviour of `AppRun` on Linux

## 1.0.0 — Initial release

- GUI (`code_compacter_gui.py`) with drag-and-drop via tkinterdnd2, folder browse, progress bar, and processing log
- CLI (`code_compacter.py`) with source/output arguments
- `src/core.py` with file walking, binary detection, encoding fallback, and language tagging
- `AppRun` and `CodeCompacter.desktop` for ROX-Filer / Puppy Linux integration
- `run_gui.sh` silent launcher and `run_gui_terminal.sh` debug launcher
