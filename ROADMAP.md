# Roadmap

## Silent/headless mode on icon drop

Goal: dropping a folder onto the app icon (or AppDir) immediately generates the compact file with no dialog, no button click. The GUI remains available for interactive use as today.

---

### How the current flow works

1. User drops a folder onto the `CodeCompacter.desktop` icon or the `Code_Compacter` AppDir in ROX-Filer
2. ROX passes the path as `$1` to `AppRun`, which calls `python3 code_compacter_gui.py "$1"`
3. `main()` in `code_compacter_gui.py` receives the path, pre-fills `source_path`, and sets the status to "Ready — click Create File"
4. The window opens and waits for the user to click the button

The dropped path is already being received correctly. The only missing piece is a code path that skips the window and runs `compact_directory_logic` directly when a flag is set.

---

### Step 1 — Add `--headless` flag to `code_compacter_gui.py`

In `main()`, detect a `--headless` argument (or `-H` short form). When present and a valid directory path is also provided:

- call `compact_directory_logic` directly, no `tk.Tk()` created
- print progress to stdout
- exit with code 0 on success, 1 on error

```python
if '--headless' in sys.argv and path and os.path.isdir(path):
    from src.core import compact_directory_logic
    source = Path(path)
    output = source.parent / f"{source.name}_compact.txt"
    stats = compact_directory_logic(source, output, log_callback=print)
    print(f"✓ {output}  ({stats['files_processed']} files)")
    sys.exit(0)
```

No GUI toolkit is initialised in this path, so it works even without a display.

---

### Step 2 — Update `AppRun` to pass `--headless` when a path argument is present

```sh
HERE="$(dirname "$(readlink -f "$0")")"
if [ -n "$1" ]; then
    exec python3 "$HERE/code_compacter_gui.py" --headless "$@"
else
    exec python3 "$HERE/code_compacter_gui.py"
fi
```

No path → opens the GUI as today. Path provided → runs silently and exits.

---

### Step 3 — Update `CodeCompacter.desktop`

The `Exec` line already passes `"%f"`, so no change needed there. Verify that `MimeType` or `%F` (multiple files) isn't needed — ROX typically passes a single directory as `%f`.

Optionally add a second `.desktop` entry for explicit interactive use:

```ini
Actions=Interactive;

[Desktop Action Interactive]
Name=Open GUI
Exec=/root/COMPACTADOR/Code_Compacter/AppRun
```

---

### Step 4 — User feedback on headless completion

Without a window there is no visible success indicator beyond the output file appearing. Options ranked by effort:

- **Notify-send** (easiest): `notify-send "Code Compacter" "✓ project_compact.txt created"` — works on most Puppy Linux setups that have `libnotify`
- **ROX-style dialog**: `rox --RPC` or `xmessage` as a fallback for systems without notify-send
- **Tray icon / progress window**: a minimal borderless Tk window that auto-closes after 3 seconds — heavier but more visible

Recommended starting point: try `notify-send`, fall back to `xmessage`, fall back silently.

---

### Step 5 — Update `docker_build.sh` / `Dockerfile.build`

The headless path doesn't use tkinter, but the binary still needs to bundle it for the interactive mode. No Dockerfile change needed — the existing build already includes everything.

Smoke-test the headless path inside the container before extracting:

```dockerfile
RUN ./dist/CodeCompacter/CodeCompacter --headless /tmp/test_project && echo "headless OK"
```

---

### Step 6 — Docs

- Update `README.md`: note that dropping a folder onto the icon runs silently; opening the icon with no argument opens the GUI
- Update `CHANGELOG.md` under Unreleased
- Update `TROUBLESHOOTING.md`: add a note that headless mode requires no display and works from cron/scripts too

---

### Acceptance criteria

- Dropping a folder onto the desktop icon produces `<folder>_compact.txt` next to the folder with no window appearing
- Opening the icon with no argument still opens the full GUI
- Running `python3 code_compacter_gui.py --headless /path/to/project` works from a terminal with no display (`DISPLAY` unset)
- The built binary (`dist/CodeCompacter/CodeCompacter`) supports both modes
