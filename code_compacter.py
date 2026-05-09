#!/usr/bin/env python3
"""
Code Compacter - Backs up an entire project into a single AI-readable text file.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime


# Default ignore patterns (like .gitignore essentials)
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

# Binary file extensions to skip
BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
    '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.webm',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
    '.exe', '.dll', '.so', '.dylib', '.bin',
    '.db', '.sqlite', '.sqlite3',
    '.woff', '.woff2', '.ttf', '.otf', '.eot'
}

# Code file extensions to prioritize
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
    '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go', '.rs',
    '.rb', '.php', '.swift', '.kt', '.scala', '.r', '.m', '.mm',
    '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
    '.html', '.htm', '.css', '.scss', '.sass', '.less', '.xml',
    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    '.sql', '.md', '.rst', '.txt', '.dockerfile', 'makefile',
    '.cmake', '.gradle', '.proto', '.thrift', '.graphql'
}


def should_ignore(path: Path, ignore_patterns: set) -> bool:
    """Check if a path should be ignored based on patterns."""
    name = path.name
    
    for pattern in ignore_patterns:
        if pattern.startswith('*'):
            if name.endswith(pattern[1:]):
                return True
        elif pattern.startswith('.'):
            if name.startswith(pattern):
                return True
        else:
            if name == pattern:
                return True
                
    # Check parent directories
    for parent in path.parents:
        parent_name = parent.name
        for pattern in ignore_patterns:
            if not pattern.startswith('*') and parent_name == pattern:
                return True
                
    return False


def is_binary_file(path: Path) -> bool:
    """Check if file is binary by extension or content."""
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    
    # Try to detect binary by reading first chunk
    try:
        with open(path, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return True
    except:
        return True
        
    return False


def get_file_language(path: Path) -> str:
    """Get programming language name from file extension."""
    ext = path.suffix.lower()
    mapping = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'jsx',
        '.tsx': 'tsx',
        '.vue': 'vue',
        '.svelte': 'svelte',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.m': 'objectivec',
        '.mm': 'objectivec',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'zsh',
        '.fish': 'fish',
        '.ps1': 'powershell',
        '.bat': 'batch',
        '.cmd': 'batch',
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',
        '.xml': 'xml',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini',
        '.sql': 'sql',
        '.md': 'markdown',
        '.rst': 'restructuredtext',
        '.txt': 'text',
        '.dockerfile': 'dockerfile',
        'makefile': 'makefile',
        '.cmake': 'cmake',
        '.gradle': 'gradle',
        '.proto': 'protobuf',
        '.thrift': 'thrift',
        '.graphql': 'graphql'
    }
    return mapping.get(ext, 'text')


def read_file_content(path: Path) -> tuple[str, bool]:
    """Read file content with encoding detection."""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read(), True
        except UnicodeDecodeError:
            continue
    
    return "", False


def compact_directory(
    source_dir: Path,
    output_file: Path,
    ignore_patterns: set = None,
    include_binary_info: bool = True
) -> dict:
    """
    Compact an entire directory into a single text file.
    
    Returns statistics about the operation.
    """
    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORES.copy()
    
    stats = {
        'files_processed': 0,
        'files_skipped': 0,
        'directories_skipped': 0,
        'total_lines': 0,
        'total_chars': 0,
        'binary_files': []
    }
    
    with open(output_file, 'w', encoding='utf-8') as out:
        # Write header
        out.write("=" * 80 + "\n")
        out.write(f"CODE COMPACT BACKUP\n")
        out.write(f"Source: {source_dir.absolute()}\n")
        out.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"=" * 80 + "\n\n")
        
        # Walk through directory
        for root, dirs, files in os.walk(source_dir):
            root_path = Path(root)
            
            # Filter out ignored directories
            dirs[:] = [
                d for d in dirs 
                if not should_ignore(root_path / d, ignore_patterns)
            ]
            
            skipped_dirs = [
                d for d in os.listdir(root) 
                if (root_path / d).is_dir() and should_ignore(root_path / d, ignore_patterns)
            ]
            stats['directories_skipped'] += len(skipped_dirs)
            
            for file in sorted(files):
                file_path = root_path / file
                rel_path = file_path.relative_to(source_dir)
                
                # Skip ignored files
                if should_ignore(file_path, ignore_patterns):
                    stats['files_skipped'] += 1
                    continue
                
                # Handle binary files
                if is_binary_file(file_path):
                    if include_binary_info:
                        stats['binary_files'].append(str(rel_path))
                    stats['files_skipped'] += 1
                    continue
                
                # Read file content
                content, success = read_file_content(file_path)
                if not success:
                    stats['files_skipped'] += 1
                    continue
                
                # Write file section
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
        
        # Write summary
        out.write("=" * 80 + "\n")
        out.write("SUMMARY\n")
        out.write("=" * 80 + "\n")
        out.write(f"Files processed: {stats['files_processed']}\n")
        out.write(f"Files skipped: {stats['files_skipped']}\n")
        out.write(f"Directories skipped: {stats['directories_skipped']}\n")
        out.write(f"Total lines: {stats['total_lines']}\n")
        out.write(f"Total characters: {stats['total_chars']}\n")
        
        if stats['binary_files']:
            out.write(f"\nBinary files detected ({len(stats['binary_files'])}):\n")
            for bf in stats['binary_files']:
                out.write(f"  - {bf}\n")
        
        out.write("=" * 80 + "\n")
        out.write("END OF BACKUP\n")
        out.write("=" * 80 + "\n")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Compact a project into a single AI-readable text file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/project                    # Output: project_backup.txt
  %(prog)s /path/to/project -o my_backup.txt   # Custom output name
  %(prog)s .                                   # Backup current directory
  %(prog)s . --no-binary-info                  # Skip binary file listing
        """
    )
    
    parser.add_argument(
        'source',
        help='Source directory to compact'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file name (default: <source_dir_name>_backup.txt)'
    )
    parser.add_argument(
        '--ignore',
        nargs='*',
        help='Additional patterns to ignore'
    )
    parser.add_argument(
        '--no-binary-info',
        action='store_true',
        help='Do not list binary files in summary'
    )
    parser.add_argument(
        '--include-defaults',
        action='store_true',
        help='Use only default ignores (ignore any custom additions)'
    )
    
    args = parser.parse_args()
    
    source_dir = Path(args.source).resolve()
    if not source_dir.exists():
        print(f"Error: Directory not found: {source_dir}")
        sys.exit(1)
    if not source_dir.is_dir():
        print(f"Error: Not a directory: {source_dir}")
        sys.exit(1)
    
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = Path(f"{source_dir.name}_backup.txt")
    
    ignore_patterns = DEFAULT_IGNORES.copy()
    if args.ignore:
        ignore_patterns.update(args.ignore)
    
    print(f"Compacting: {source_dir}")
    print(f"Output: {output_file.absolute()}")
    print("Processing...")
    
    stats = compact_directory(
        source_dir,
        output_file,
        ignore_patterns=ignore_patterns,
        include_binary_info=not args.no_binary_info
    )
    
    print(f"\n✓ Complete!")
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Files skipped: {stats['files_skipped']}")
    print(f"  Total lines: {stats['total_lines']}")
    print(f"  Output size: {output_file.stat().st_size:,} bytes")


if __name__ == '__main__':
    main()
