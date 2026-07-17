# Roadmap

## Silent/headless mode on icon drop ✅ Completed

Goal: dropping a folder onto the app icon (or AppDir) immediately generates the compact file with no dialog, no button click. The GUI remains available for interactive use as today.

---

### Step 1 — Add `--headless` flag to `code_compacter_gui.py` ✅

`_run_headless()` calls `compact_directory_logic` directly with no Tk window. Works without a display (`DISPLAY` unset). Exits 0 on success, 1 on error.

---

### Step 2 — Update `AppRun` ✅

`AppRun` passes `--headless "$@"` when called with a path argument, opens GUI when called with none.

---

### Step 3 — `CodeCompacter.desktop` ✅

No change needed — `Exec=AppRun "%f"` already passes the dropped path. Verified with ROX-Filer.

---

### Step 4 — User feedback on headless completion ✅

`_notify_headless()` dispatches by platform:
- Windows: PowerShell toast (`Windows.UI.Notifications`) — no extra dependencies
- macOS: `osascript` display notification
- Linux: `notify-send`, fallback to `xmessage`, fallback to silent

All paths use `subprocess.Popen` with list args — no shell string interpolation.

---

### Step 5 — `Dockerfile.build` smoke test ✅

```dockerfile
RUN mkdir -p /tmp/test_project && \
    echo 'print("hello")' > /tmp/test_project/main.py && \
    ./dist/CodeCompacter/CodeCompacter --headless /tmp/test_project && \
    test -f /tmp/test_project_compact.txt && \
    echo "headless smoke test OK" && \
    rm -rf /tmp/test_project /tmp/test_project_compact.txt
```

Confirmed passing: `headless smoke test OK` in build log.

---

### Step 6 — Docs ✅

README, CHANGELOG, TROUBLESHOOTING all updated.

---

### Acceptance criteria

- ✅ Dropping a folder onto the desktop icon produces `<folder>_compact.txt` next to the folder with no window appearing
- ✅ Opening the icon with no argument still opens the full GUI
- ✅ Running `python3 code_compacter_gui.py --headless /path/to/project` works from a terminal with no display (`DISPLAY` unset)
- ✅ The built binary (`dist/CodeCompacter/CodeCompacter`) supports both modes (smoke-tested in Docker)

---

## Next

- Windows `.exe` build — headless notification uses PowerShell toast (implemented), but the build pipeline (`Dockerfile.build`) is Linux-only; a separate Windows build workflow is needed
- `%F` multi-folder support in `CodeCompacter.desktop` — currently only the first dropped folder is processed
- Configurable output directory — today the compact file always lands next to the source folder
