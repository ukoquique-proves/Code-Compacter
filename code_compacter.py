#!/usr/bin/env python3
"""
Code Compacter - CLI for compacting projects into AI-readable files.
"""

import os
import sys
import argparse
from pathlib import Path

# Import core logic
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
try:
    from core import compact_directory_logic, DEFAULT_IGNORES
except ImportError:
    from src.core import compact_directory_logic, DEFAULT_IGNORES

def main():
    parser = argparse.ArgumentParser(
        description='Compact a project into a single AI-readable text file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/project                          # Output: project_compact.txt
  %(prog)s /path/to/project -o my_compact.txt         # Custom output name
  %(prog)s . --ignore *.log temp/                     # Extra ignore patterns
        """
    )
    
    parser.add_argument('source', help='Source directory to compact')
    parser.add_argument('-o', '--output', help='Output file name')
    parser.add_argument('--ignore', metavar='PATTERN', nargs='+',
                        help='Extra ignore patterns e.g. --ignore *.log temp/')

    args = parser.parse_args()
    
    source_dir = Path(args.source).resolve()
    if not source_dir.exists() or not source_dir.is_dir():
        print(f"Error: Invalid directory: {source_dir}")
        sys.exit(1)
    
    output_file = Path(args.output) if args.output else Path(f"{source_dir.name}_compact.txt")
    extra_ignores = set(args.ignore) if args.ignore else None

    print(f"Compacting: {source_dir}")
    print(f"Output: {output_file.absolute()}")
    if extra_ignores:
        print(f"Extra ignores: {', '.join(sorted(extra_ignores))}")
    
    stats = compact_directory_logic(
        source_dir,
        output_file,
        log_callback=lambda m: print(f"  {m}"),
        extra_ignores=extra_ignores
    )
    
    print(f"\n✓ Complete!")
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Total lines: {stats['total_lines']}")
    print(f"  Output size: {output_file.stat().st_size:,} bytes")

if __name__ == '__main__':
    main()
