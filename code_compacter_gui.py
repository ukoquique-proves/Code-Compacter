#!/usr/bin/env python3
"""
Code Compacter GUI - Drag/drop interface for compacting projects into AI-readable files.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
import threading

# Import core logic
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
try:
    from core import compact_directory_logic
except ImportError:
    from src.core import compact_directory_logic

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False

class CodeCompacterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Compacter")
        self.root.geometry("600x540")
        self.root.minsize(500, 440)
        
        # Style
        self.root.configure(bg='#f5f5f5')
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.source_path = tk.StringVar()
        self.ignore_patterns = tk.StringVar()
        self.status = tk.StringVar(value="Select a project folder to compact")
        self.progress = tk.DoubleVar(value=0)
        self.output_display = tk.StringVar(value="")
        
        self._build_ui()
        self._setup_dnd()
        
    def _setup_dnd(self):
        if HAS_DND:
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self._handle_drop)
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind('<<Drop>>', self._handle_drop)
        else:
            self.log("Note: Drag-and-drop into window requires 'tkinterdnd2'.")
            self.log("However, you can drag folders onto the desktop icon!")
            self.status.set("Drag-and-drop not bundled — use Browse or drop onto the desktop icon")

    def _parse_dropped_path(self, data: str) -> str | None:
        """Parse tkinterdnd2 / ROX drop data (handles spaces and brace-wrapped paths)."""
        try:
            paths = self.root.tk.splitlist(data)
        except tk.TclError:
            paths = [data]
        if not paths:
            return None
        path = paths[0].strip()
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]
        path = path.replace('file://', '')
        return os.path.abspath(os.path.expanduser(path))

    def _handle_drop(self, event):
        path = self._parse_dropped_path(event.data)
        if not path:
            return
        path_obj = Path(path)
        if path_obj.is_dir():
            self.source_path.set(str(path_obj))
            self.status.set("Ready - click 'Create File' button")
            self.log(f"Dropped: {path_obj}")
        else:
            messagebox.showwarning("Warning", "Please drop a folder, not a file.")
            
    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title = ttk.Label(main_frame, text="📦 Code Compacter", font=('Segoe UI', 18, 'bold'))
        title.pack(pady=(0, 5))
        
        subtitle = ttk.Label(main_frame, text="Compact your entire project into a single AI-readable file", font=('Segoe UI', 9), foreground='gray')
        subtitle.pack(pady=(0, 20))
        
        self.drop_frame = tk.Frame(main_frame, bg='#e8f4f8', bd=2, relief='groove', height=150, highlightbackground='#2196F3', highlightthickness=2)
        self.drop_frame.pack(fill=tk.X, pady=10)
        self.drop_frame.pack_propagate(False)
        
        self.drop_label = tk.Label(self.drop_frame, text="📁\nDrop project folder here\nor click to browse", bg='#e8f4f8', font=('Segoe UI', 11), cursor='hand2')
        self.drop_label.pack(expand=True)
        
        for widget in [self.drop_frame, self.drop_label]:
            widget.bind('<Button-1>', lambda e: self.browse_folder())
            widget.bind('<Enter>', lambda e: self._highlight_drop(True))
            widget.bind('<Leave>', lambda e: self._highlight_drop(False))
        
        self.path_frame = ttk.Frame(main_frame)
        self.path_frame.pack(fill=tk.X, pady=10)
        self.path_entry = ttk.Entry(self.path_frame, textvariable=self.source_path, state='readonly')
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.browse_btn = ttk.Button(self.path_frame, text="Browse...", command=self.browse_folder)
        self.browse_btn.pack(side=tk.RIGHT)

        self.ignore_frame = ttk.Frame(main_frame)
        self.ignore_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(self.ignore_frame, text="Extra ignores:", font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.ignore_entry = ttk.Entry(self.ignore_frame, textvariable=self.ignore_patterns)
        self.ignore_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(self.ignore_frame, text="e.g. *.log, temp/", font=('Segoe UI', 8), foreground='gray').pack(side=tk.LEFT, padx=(5, 0))
        
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress, maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=10)
        self.progress_bar.pack_forget()
        
        self.status_label = ttk.Label(main_frame, textvariable=self.status, font=('Segoe UI', 10))
        self.status_label.pack(pady=5)

        self.output_label = ttk.Label(main_frame, textvariable=self.output_display, font=('Segoe UI', 9, 'bold'), foreground='#2196F3')
        self.output_label.pack(pady=(0, 5))
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        self.backup_btn = ttk.Button(btn_frame, text="Create File", command=self.create_compact_file)
        self.backup_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.open_btn = ttk.Button(btn_frame, text="Open Output", command=self.open_output, state='disabled')
        self.open_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT)

        self.log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="5")
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, height=8, font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.output_path = None
        
    def _highlight_drop(self, active):
        color = '#bbdefb' if active else '#e8f4f8'
        self.drop_frame.configure(bg=color)
        self.drop_label.configure(bg=color)
        
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self.source_path.set(folder)
            self.status.set("Ready - click 'Create File' button")
            self.log(f"Selected: {folder}")
            
    def log(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def create_compact_file(self):
        source_str = self.source_path.get()
        if not source_str:
            folder = filedialog.askdirectory(title="Select Project Folder to Compact")
            if not folder: return
            self.source_path.set(folder)
            source_str = folder
            
        source = Path(source_str)
        if not source.exists():
            messagebox.showerror("Error", "Selected folder does not exist!")
            return
            
        output = source.parent / f"{source.name}_compact.txt"
        self.output_path = output
        
        self.backup_btn.configure(state='disabled')
        self.browse_btn.configure(state='disabled')
        self.progress_bar.pack(fill=tk.X, pady=10)
        self.progress.set(0)
        self.output_display.set("")

        raw = self.ignore_patterns.get()
        extra_ignores = {p.strip() for p in raw.split(',') if p.strip()} if raw else None
        
        thread = threading.Thread(target=self._process, args=(source, output, extra_ignores))
        thread.daemon = True
        thread.start()
        
    def _process(self, source: Path, output: Path, extra_ignores=None):
        try:
            stats = compact_directory_logic(
                source, 
                output, 
                progress_callback=lambda p: self.root.after(0, lambda: self.progress.set(p)),
                log_callback=lambda m: self.root.after(0, lambda: self.log(m)),
                extra_ignores=extra_ignores
            )
            self.root.after(0, lambda: self._on_complete(stats, output))
        except Exception as e:
            self.root.after(0, lambda: self._on_error(str(e)))
            
    def _on_complete(self, stats, output):
        self.progress.set(100)
        self.status.set(f"✓ File created: {output.name}")
        self.output_display.set(f"📄 {output}")
        self.log(f"Complete! Processed {stats['files_processed']} files")
        self.open_btn.configure(state='normal')
        self.browse_btn.configure(state='normal')
        messagebox.showinfo("Success", f"File created successfully!\n\nFiles: {stats['files_processed']}\nLines: {stats['total_lines']:,}\nOutput: {output}")
            
    def _on_error(self, error):
        self.progress_bar.pack_forget()
        self.status.set("Error occurred")
        self.log(f"ERROR: {error}")
        self.backup_btn.configure(state='normal')
        self.browse_btn.configure(state='normal')
        messagebox.showerror("Error", f"Failed to create file:\n{error}")
        
    def open_output(self):
        if self.output_path and self.output_path.exists():
            import subprocess
            if sys.platform == 'darwin':
                subprocess.Popen(["open", str(self.output_path)])
            elif sys.platform == 'win32':
                os.startfile(self.output_path)
            else:
                subprocess.Popen(["xdg-open", str(self.output_path)])

def _notify_headless(filename: str):
    """Best-effort desktop notification after a headless run.
    Uses platform-native mechanisms; silently does nothing if unavailable.
    The output file is always the ground truth — notification is informational only.
    Swallows ALL exceptions so it can never fail a successful compact run.
    NO CODE INJECTION: All untrusted input (filename) is passed safely via environment variables,
    never interpolated into interpreter script strings.
    """
    try:
        import subprocess
        import os

        if sys.platform == 'win32':
            # Windows toast via PowerShell — NO CODE INJECTION: message passed via env var
            ps_script = r"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType=WindowsRuntime] | Out-Null;
            $t = [Windows.UI.Notifications.ToastTemplateType]::ToastText01;
            $x = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent($t);
            $msg = [System.Environment]::GetEnvironmentVariable("COMPACTER_MSG");
            $x.GetElementsByTagName("text")[0].AppendChild($x.CreateTextNode($msg)) | Out-Null;
            $n = [Windows.UI.Notifications.ToastNotification]::new($x);
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Code Compacter").Show($n);
            """
            env = os.environ.copy()
            env["COMPACTER_MSG"] = f"✓ {filename} created"
            # Use -EncodedCommand to avoid any interpolation issues
            import base64
            encoded_script = base64.b64encode(ps_script.encode('utf-16-le')).decode('ascii')
            subprocess.Popen(
                ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-EncodedCommand", encoded_script],
                env=env,
                creationflags=0x08000000  # CREATE_NO_WINDOW
            )

        elif sys.platform == 'darwin':
            # macOS notification via osascript — NO CODE INJECTION: use 'quoted form of' in AppleScript
            # to safely handle any characters in the message, including quotes and backslashes
            apple_script = '''
            on run argv
                set msg to item 1 of argv
                display notification msg with title "Code Compacter"
            end run
            '''
            subprocess.Popen([
                "osascript", "-e", apple_script, "-", f"✓ {filename} created"
            ])

        else:
            # Linux / Puppy Linux — NO CODE INJECTION: message passed as separate list arguments
            if subprocess.run(["which", "notify-send"], capture_output=True, check=False).returncode == 0:
                subprocess.Popen(["notify-send", "Code Compacter", f"✓ {filename} created"])
            elif subprocess.run(["which", "xmessage"], capture_output=True, check=False).returncode == 0:
                subprocess.Popen(["xmessage", "-timeout", "4", f"✓ {filename} created"])
            # If neither is available, the file appearing is the signal — no action needed
    except Exception:
        # Swallow ANY exception — notification is purely best-effort
        pass


def _run_headless(path: str):
    """Run compaction directly with no GUI. Used when --headless flag is passed."""
    source = Path(path).resolve()
    if not source.is_dir():
        print(f"Error: not a directory: {source}")
        sys.exit(1)

    output = source.parent / f"{source.name}_compact.txt"
    print(f"Compacting: {source}")
    print(f"Output:     {output}")

    try:
        stats = compact_directory_logic(
            source,
            output,
            log_callback=lambda m: print(f"  {m}"),
            progress_callback=lambda p: None,
        )
        print(f"✓ Done — {stats['files_processed']} files, {stats['total_lines']:,} lines")
        # Best-effort desktop notification, platform-aware.
        # In headless mode there is no window, so this is the only completion signal.
        # Each branch fails silently if the notification tool is unavailable —
        # the output file is always the ground truth.
        try:
            _notify_headless(output.name)
        except Exception:
            # Swallow ANY exception — notification failure can't make the whole run fail
            pass
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    args = sys.argv[1:]

    # Strip --headless flag and collect the remaining path tokens
    headless = '--headless' in args
    args = [a for a in args if a != '--headless']

    # Reconstruct path (handles filenames with spaces passed as multiple tokens)
    raw_path = (' '.join(args) if len(args) > 1 and not os.path.exists(args[0]) else args[0]) if args else ''
    raw_path = raw_path.replace('file://', '').strip()
    if raw_path.startswith('{') and raw_path.endswith('}'):
        raw_path = raw_path[1:-1]
    path = os.path.abspath(os.path.expanduser(raw_path)) if raw_path else ''

    if headless and path:
        _run_headless(path)
        return  # sys.exit called inside, but keeps linters happy

    if HAS_DND: root = TkinterDnD.Tk()
    else: root = tk.Tk()
    app = CodeCompacterGUI(root)

    if path:
        if os.path.isdir(path):
            app.source_path.set(path)
            app.status.set("Ready - click 'Create File' button")
            app.log(f"Selected via argument: {path}")
        elif os.path.isfile(path):
            app.source_path.set(os.path.dirname(path))
            app.status.set("Ready - click 'Create File' button")
            app.log(f"Selected parent of: {path}")

    root.mainloop()

if __name__ == '__main__':
    main()
