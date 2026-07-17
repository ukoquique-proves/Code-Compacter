# Troubleshooting

## Building a standalone binary

### The problem chain (fully resolved via Docker)

Three separate issues were hit in sequence when trying to build on the host system. All are bypassed by using `docker_build.sh` instead.

---

#### Issue 1 — `libpython3.13.so.1.0` not found (host build)

Running `build_linux.sh` directly on the host fails with:

```
ERROR: Python shared library ('libpython3.13.so.1.0') was not found!
```

PyInstaller needs Python built with `--enable-shared`. The host `python3.13` package is statically linked, and `python3.13-dev` (which provides the shared library) is uninstallable due to a version-index mismatch on this system:

```
python3.13-dev requires python3.13 = 3.13.5-2+deb13u2
but                       python3.13 = 3.13.5-2 is installed
```

**Fix:** use `docker_build.sh` — the official `python:3.13-slim-bullseye` image is compiled with `--enable-shared`, so the library is just there.

---

#### Issue 2 — `libtk8.6.so: cannot open shared object file` (inside Docker, first attempt)

The first Dockerfile used `python:3.13-slim-bullseye` without any extra packages. `build_linux.sh` locates the tkdnd data path by importing `tkinterdnd2`, which in turn imports `tkinter`, which needs `libtk8.6.so`. The slim image ships without Tk libraries.

```
ImportError: libtk8.6.so: cannot open shared object file: No such file or directory
```

**Fix:** added `tk-dev` to the Dockerfile's `apt-get install` step:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends tk-dev \
    && rm -rf /var/lib/apt/lists/*
```

---

#### Issue 3 — glibc compatibility (design consideration, not a crash)

The host system runs glibc 2.41 (Debian trixie). A binary built there would require glibc ≥ 2.41 on the target machine. PuppyLinux typically ships glibc 2.31–2.35, so the binary would silently refuse to launch.

**Fix:** `Dockerfile.build` builds against `python:3.13-slim-bullseye` (Debian bullseye, glibc 2.31), so the output binary runs on any system with glibc ≥ 2.31 — covering all mainstream Linux distros from 2021 onward.

Check your target system's glibc version with:

```bash
ldd --version
```

If it's below 2.31, switch to a manylinux base image in `Dockerfile.build`:

```dockerfile
FROM quay.io/pypa/manylinux_2_28_x86_64
```

---

### How to build (current working method)

```bash
bash docker_build.sh
```

This builds inside Docker, extracts the binary, and places it at `dist/CodeCompacter/CodeCompacter`. The tkdnd data files are bundled correctly under `dist/CodeCompacter/_internal/tkinterdnd2/tkdnd/`.

To distribute, zip the entire `dist/CodeCompacter/` directory.

---

### Running from source (no build needed)

If you just need to run the app on the current machine:

```bash
python3 code_compacter_gui.py
```

tkinter, tkinterdnd2, and drag-and-drop all work correctly this way with no build step required.

---

### Current state

| Component | Status |
|---|---|
| `python3 code_compacter_gui.py` | ✅ works |
| `python3 code_compacter.py` (CLI) | ✅ works |
| tkinter | ✅ installed (`python3-tk`) |
| tkinterdnd2 0.6.2 | ✅ installed |
| Drag-and-drop (source run) | ✅ works |
| Docker build (`docker_build.sh`) | ✅ works — produces `dist/CodeCompacter/` |
| tkdnd data bundled in binary | ✅ confirmed at `_internal/tkinterdnd2/tkdnd/` |
| glibc target | ✅ 2.31 (bullseye base — runs on PuppyLinux) |
| Host `build_linux.sh` (no Docker) | ❌ blocked — `python3.13-dev` uninstallable on this host |

---

### Other issues

#### Desktop icon doesn't respond in ROX-Filer

ROX-Filer only picks up `.desktop` files from `/root/Desktop/`, not arbitrary directories.

```bash
cp CodeCompacter.desktop /root/Desktop/
chmod +x /root/Desktop/CodeCompacter.desktop
```

#### AppRun permission denied

```bash
chmod +x AppRun
```

#### GUI opens but nothing happens on click

Check the Processing Log panel for error messages, or run with visible output:

```bash
./run_gui_terminal.sh
```
