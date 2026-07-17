import os
from pathlib import Path
from datetime import datetime

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

# Binary file extensions
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

def compact_directory_logic(source: Path, output: Path, progress_callback=None, log_callback=None, extra_ignores: set | None = None) -> dict:
    stats = {'files_processed': 0, 'files_skipped': 0, 'total_lines': 0, 'total_chars': 0}
    all_files = []
    ignore_patterns = DEFAULT_IGNORES | (extra_ignores or set())

    for root, dirs, files in os.walk(source):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if not should_ignore(root_path / d, ignore_patterns)]
        for file in files:
            file_path = root_path / file
            if not should_ignore(file_path, ignore_patterns) and not is_binary_file(file_path):
                all_files.append(file_path)
    
    total = len(all_files)
    if total == 0 and log_callback:
        log_callback("No text files found to compact (folder may be empty or all ignored).")

    with open(output, 'w', encoding='utf-8') as out:
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
                
                if progress_callback and total > 0:
                    progress_callback(((i + 1) / total) * 100)
                if log_callback:
                    log_callback(f"Processing: {rel_path}")
            else:
                stats['files_skipped'] += 1
        
        out.write("=" * 80 + "\n")
        out.write("SUMMARY\n")
        out.write("=" * 80 + "\n")
        out.write(f"Files processed: {stats['files_processed']}\n")
        out.write(f"Total lines: {stats['total_lines']}\n")
        out.write(f"Total characters: {stats['total_chars']}\n")
        out.write("=" * 80 + "\n")
        
    return stats
