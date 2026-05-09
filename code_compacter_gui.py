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

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False


# Default ignore patterns
DEFAULT_IGNORES = {
    '.git', '__pycache__', '.venv', 'venv', 'node_modules',
    '.idea', '.vscode', '.vs', '*.pyc', '*.pyo', '*.pyd',
    '.DS_Store', 'Thumbs.db', '*.so', '*.dylib', '*.dll',
    '*.exe', '*.bin', '*.obj', '*.o', 'a.out', '*.class',
    '*.jar', '*.war', '*.ear', 'target', 'build', 'dist',
    '*.egg-info', '.pytest_cache', '.mypy_cache', '.coverage',
    'htmlcov', '.tox', '*.log', '*.tmp', '*.temp', '*.swp',
    '*.swo', '*~', '.env', '.env.local', 'package-lock.json',
    'yarn.lock', 'pnpm-lock.yaml', 'Cargo.lock', 'poetry.lock',
    'Gemfile.lock', 'composer.lock'
}

BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
    '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.webm',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
    '.exe', '.dll', '.so', '.dylib', '.bin',
    '.db', '.sqlite', '.sqlite3',
    '.woff', '.woff2', '.ttf', '.otf', '.eot'
}


def should_ignore(path: Path, ignore_patterns: set) -> bool:
    """Check if a path should be ignored based on patterns."""
    name = path.name
    for pattern in ignore_patterns:
        if pattern.startswith('*'):
            if name.endswith(pattern[1:]): return True
        elif pattern.startswith('.'):
            if name.startswith(pattern): return True
        else:
            if name == pattern: return True
    for parent in path.parents:
        for pattern in ignore_patterns:
            if not pattern.startswith('*') and parent.name == pattern:
                return True
    return False


def is_binary_file(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXTENSIONS: return True
    try:
        with open(path, 'rb') as f:
            return b'\x00' in f.read(1024)
    except: return True
    return False


def get_file_language(path: Path) -> str:
    ext = path.suffix.lower()
    mapping = {
        '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
        '.jsx': 'jsx', '.tsx': 'tsx', '.vue': 'vue', '.svelte': 'svelte',
        '.java': 'java', '.c': 'c', '.cpp': 'cpp', '.h': 'c', '.hpp': 'cpp',
        '.cs': 'csharp', '.go': 'go', '.rs': 'rust', '.rb': 'ruby',
        '.php': 'php', '.swift': 'swift', '.kt': 'kotlin', '.scala': 'scala',
        '.r': 'r', '.sh': 'bash', '.html': 'html', '.css': 'css',
        '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml', '.md': 'markdown',
        '.sql': 'sql', '.xml': 'xml', '.dockerfile': 'dockerfile'
    }
    return mapping.get(ext, 'text')


def read_file_content(path: Path) -> tuple[str, bool]:
    for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']:
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read(), True
        except UnicodeDecodeError: continue
    return "", False


class CodeCompacterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Compacter")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)
        
        # Style
        self.root.configure(bg='#f5f5f5')
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.source_path = tk.StringVar()
        self.status = tk.StringVar(value="Select a project folder to compact")
        self.progress = tk.DoubleVar(value=0)
        
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

    def _handle_drop(self, event):
        path = event.data
        # Clean path (handle curly braces/quotes from some OSs)
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]
        
        path_obj = Path(path)
        if path_obj.is_dir():
            self.source_path.set(str(path_obj))
            self.status.set("Ready - click 'Create File' button")
            self.log(f"Dropped: {path_obj}")
        else:
            messagebox.showwarning("Warning", "Please drop a folder, not a file.")
            
    def _build_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="📦 Code Compacter", 
                         font=('Segoe UI', 18, 'bold'))
        title.pack(pady=(0, 5))
        
        subtitle = ttk.Label(main_frame, 
                           text="Compact your entire project into a single AI-readable file",
                           font=('Segoe UI', 9), foreground='gray')
        subtitle.pack(pady=(0, 20))
        
        # Drop zone / Selection area
        self.drop_frame = tk.Frame(main_frame, bg='#e8f4f8', bd=2, relief='groove',
                                   height=150, highlightbackground='#2196F3',
                                   highlightthickness=2)
        self.drop_frame.pack(fill=tk.X, pady=10)
        self.drop_frame.pack_propagate(False)
        
        self.drop_label = tk.Label(self.drop_frame, text="📁\nDrop project folder here\nor click to browse",
                                  bg='#e8f4f8', font=('Segoe UI', 11), cursor='hand2')
        self.drop_label.pack(expand=True)
        
        # Bind click and drag events
        for widget in [self.drop_frame, self.drop_label]:
            widget.bind('<Button-1>', lambda e: self.browse_folder())
            widget.bind('<Enter>', lambda e: self._highlight_drop(True))
            widget.bind('<Leave>', lambda e: self._highlight_drop(False))
        
        # Path display
        self.path_frame = ttk.Frame(main_frame)
        self.path_frame.pack(fill=tk.X, pady=10)
        
        self.path_entry = ttk.Entry(self.path_frame, textvariable=self.source_path,
                                   state='readonly')
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.browse_btn = ttk.Button(self.path_frame, text="Browse...", 
                                    command=self.browse_folder)
        self.browse_btn.pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress,
                                           maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=10)
        self.progress_bar.pack_forget()  # Hidden initially
        
        # Status text
        self.status_label = ttk.Label(main_frame, textvariable=self.status,
                                     font=('Segoe UI', 10))
        self.status_label.pack(pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        self.backup_btn = ttk.Button(btn_frame, text="Create File", 
                                    command=self.create_compact_file)
        self.backup_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.open_btn = ttk.Button(btn_frame, text="Open Output", 
                                  command=self.open_output, state='disabled')
        self.open_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT)

        # Log area
        self.log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="5")
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD,
                                                 height=8, font=('Consolas', 9))
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
            # No folder selected, prompt user
            folder = filedialog.askdirectory(title="Select Project Folder to Compact")
            if not folder:
                return
            self.source_path.set(folder)
            self.log(f"Selected: {folder}")
            source_str = folder
            
        source = Path(source_str)
        if not source.exists():
            messagebox.showerror("Error", "Selected folder does not exist!")
            return
            
        # Output next to source
        output = source.parent / f"{source.name}_compact.txt"
        self.output_path = output
        
        # Start processing in thread
        self.backup_btn.configure(state='disabled')
        self.browse_btn.configure(state='disabled')
        self.progress_bar.pack(fill=tk.X, pady=10)
        self.progress.set(0)
        
        thread = threading.Thread(target=self._process, args=(source, output))
        thread.daemon = True
        thread.start()
        
    def _process(self, source: Path, output: Path):
        try:
            stats = self._compact_directory(source, output)
            
            self.root.after(0, lambda: self._on_complete(stats, output))
        except Exception as e:
            self.root.after(0, lambda: self._on_error(str(e)))
            
    def _compact_directory(self, source: Path, output: Path) -> dict:
        stats = {'files_processed': 0, 'files_skipped': 0, 'total_lines': 0, 'total_chars': 0}
        all_files = []
        
        # Collect files first for progress
        for root, dirs, files in os.walk(source):
            root_path = Path(root)
            dirs[:] = [d for d in dirs if not should_ignore(root_path / d, DEFAULT_IGNORES)]
            for file in files:
                file_path = root_path / file
                if not should_ignore(file_path, DEFAULT_IGNORES) and not is_binary_file(file_path):
                    all_files.append(file_path)
        
        total = len(all_files)
        
        with open(output, 'w', encoding='utf-8') as out:
            # Header
            out.write("=" * 80 + "\n")
            out.write(f"CODE COMPACT FILE\n")
            out.write(f"Source: {source.absolute()}\n")
            out.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            out.write(f"=" * 80 + "\n\n")
            
            for i, file_path in enumerate(all_files):
                rel_path = file_path.relative_to(source)
                content, success = read_file_content(file_path)
                
                if success:
                    lang = get_file_language(file_path)
                    out.write("-" * 80 + "\n")
                    out.write(f"FILE: {rel_path}\n")
                    out.write(f"LANGUAGE: {lang}\n")
                    out.write("-" * 80 + "\n")
                    out.write(content)
                    if content and not content.endswith('\n'):
                        out.write('\n')
                    out.write("\n")
                    
                    stats['files_processed'] += 1
                    stats['total_lines'] += content.count('\n') + (1 if content and not content.endswith('\n') else 0)
                    stats['total_chars'] += len(content)
                    
                    # Update progress
                    progress = ((i + 1) / total) * 100
                    self.root.after(0, lambda p=progress: self.progress.set(p))
                    self.root.after(0, lambda f=rel_path: self.log(f"Processing: {f}"))
                else:
                    stats['files_skipped'] += 1
            
            # Summary
            out.write("=" * 80 + "\n")
            out.write("SUMMARY\n")
            out.write("=" * 80 + "\n")
            out.write(f"Files processed: {stats['files_processed']}\n")
            out.write(f"Total lines: {stats['total_lines']}\n")
            out.write(f"Total characters: {stats['total_chars']}\n")
            out.write("=" * 80 + "\n")
            
        return stats
        
    def _on_complete(self, stats, output):
        self.progress.set(100)
        self.status.set(f"✓ File created: {output.name}")
        self.log(f"Complete! Processed {stats['files_processed']} files")
        self.log(f"Output: {output}")
        self.open_btn.configure(state='normal')
        self.browse_btn.configure(state='normal')
        
        messagebox.showinfo("Success", 
            f"File created successfully!\n\n"
            f"Files: {stats['files_processed']}\n"
            f"Lines: {stats['total_lines']:,}\n"
            f"Output: {output}")
            
    def _on_error(self, error):
        self.progress_bar.pack_forget()
        self.status.set("Error occurred")
        self.log(f"ERROR: {error}")
        self.backup_btn.configure(state='normal')
        self.browse_btn.configure(state='normal')
        messagebox.showerror("Error", f"Failed to create file:\n{error}")
        
    def open_output(self):
        if self.output_path and self.output_path.exists():
            if sys.platform == 'darwin':
                os.system(f'open "{self.output_path}"')
            elif sys.platform == 'win32':
                os.startfile(self.output_path)
            else:
                os.system(f'xdg-open "{self.output_path}"')


def main():
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = CodeCompacterGUI(root)
    
    # Handle command line argument for drag and drop onto shortcut/script
    if len(sys.argv) > 1:
        # Join arguments in case of spaces if not properly quoted by OS
        path = " ".join(sys.argv[1:]) if len(sys.argv) > 2 and not os.path.exists(sys.argv[1]) else sys.argv[1]
        
        # Clean path (handle ROX-Filer or URI artifacts)
        path = path.replace('file://', '')
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]
            
        path = os.path.abspath(os.path.expanduser(path))
        
        if os.path.isdir(path):
            app.source_path.set(path)
            app.status.set("Ready - click 'Create File' button")
            app.log(f"Selected via argument: {path}")
        elif os.path.isfile(path):
            # If a file was dropped, use its parent folder
            parent = os.path.dirname(path)
            app.source_path.set(parent)
            app.status.set("Ready - click 'Create File' button")
            app.log(f"Selected parent of: {path}")
            
    root.mainloop()


if __name__ == '__main__':
    main()
