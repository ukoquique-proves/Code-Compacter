# Roadmap

## Silent/headless mode on icon drop ✅ Completed

Goal: dropping a folder onto the app icon (or AppDir) immediately generates the compact file with no dialog, no button click. The GUI remains available for interactive use as today.

---

### Step 1 — Add `--headless` flag to `code_compacter_gui.py` ✅
`_run_headless()` calls `compact_directory_logic` directly with no Tk window. Works without a display (`DISPLAY` unset). Exits 0 on success, 1 on error.

### Step 2 — Update `AppRun` ✅
`AppRun` passes `--headless "$@"` when called with a path argument, opens GUI when called with none.

### Step 3 — `CodeCompacter.desktop` ✅
No change needed — `Exec=AppRun "%f"` already passes the dropped path. Verified with ROX-Filer.

### Step 4 — User feedback on headless completion ✅
`_notify_headless()` dispatches by platform:
- Windows: PowerShell toast, message passed via `COMPACTER_MSG` env var, script Base64-encoded — no shell injection
- Linux: `notify-send`, fallback `xmessage`, fallback silent — list-args only, no shell injection

### Step 5 — `Dockerfile.build` smoke test ✅
Confirmed passing: `headless smoke test OK` in build log.

### Step 6 — Docs ✅
README, CHANGELOG, TROUBLESHOOTING all updated.

### Acceptance criteria
- ✅ Dropping a folder onto the desktop icon produces `<folder>_compact.txt` next to the folder with no window appearing
- ✅ Opening the icon with no argument still opens the full GUI
- ✅ `--headless` works from a terminal with no display
- ✅ Built binary supports both modes (smoke-tested in Docker)

---

## Platform build status

| Platform | Packaging | Status |
|---|---|---|
| Linux | `docker_build.sh` (bypasses host `python3.13-dev` issue) | ✅ Working, confirmed |
| Windows | `build_windows.bat` | ✅ Added, bundles tkdnd data correctly |

Only Linux and Windows are supported build targets. No other platform is planned.

---

## Next

- `%F` multi-folder support in `CodeCompacter.desktop` — currently only the first dropped folder is processed
- Configurable output directory — today the compact file always lands next to the source folder
- `run_gui.py` headless output — fixed: `capture_output=False` in headless mode so progress/completion lines are visible; `capture_output=True` kept for interactive GUI launches where stderr feeds the error dialog
