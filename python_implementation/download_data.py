#!/usr/bin/env python3
"""
Data download utility for PyMOCAT-MC

Downloads large TLE CSV data files from remote repository.
This avoids including large files in the pip package.
"""

import os
import urllib.request
import hashlib
from typing import Dict, List, Optional
import json

# Data files to download (with their expected sizes and checksums)
DATA_FILES = {
    '2008.csv': {
        'size_mb': 13,
        'url': 'https://github.com/rushilkukreja/PyMOCAT-MC/raw/main/python_implementation/supporting_data/TLEhistoric/2008.csv'
    },
    '2009.csv': {
        'size_mb': 13,
        'url': 'https://github.com/rushilkukreja/PyMOCAT-MC/raw/main/python_implementation/supporting_data/TLEhistoric/2009.csv'
    },
    '2020.csv': {
        'size_mb': 23,
        'url': 'https://github.com/rushilkukreja/PyMOCAT-MC/raw/main/python_implementation/supporting_data/TLEhistoric/2020.csv'
    },
    '2021.csv': {
        'size_mb': 36,
        'url': 'https://github.com/rushilkukreja/PyMOCAT-MC/raw/main/python_implementation/supporting_data/TLEhistoric/2021.csv'
    },
    '2022.csv': {
        'size_mb': 33,
        'url': 'https://github.com/rushilkukreja/PyMOCAT-MC/raw/main/python_implementation/supporting_data/TLEhistoric/2022.csv'
    },
    '2023.csv': {
        'size_mb': 53,
        'url': 'https://github.com/rushilkukreja/PyMOCAT-MC/raw/main/python_implementation/supporting_data/TLEhistoric/2023.csv'
    },
}

def get_data_dir() -> str:
    """Get the directory where data files should be stored."""
    # Try to find the package installation directory
    try:
        import pymocat_mc
        package_dir = os.path.dirname(pymocat_mc.__file__)
        data_dir = os.path.join(package_dir, 'supporting_data', 'TLEhistoric')
    except ImportError:
        # Fall back to local directory
        data_dir = os.path.join(
            os.path.dirname(__file__),
            'python_implementation',
            'supporting_data',
            'TLEhistoric'
        )

    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def download_file(url: str, dest_path: str, file_size_mb: float) -> bool:
    """
    Download a file with progress indication.

    Args:
        url: URL to download from
        dest_path: Destination file path
        file_size_mb: Expected file size in MB (for progress display)

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Downloading {os.path.basename(dest_path)} (~{file_size_mb:.0f} MB)...")

        def download_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100.0 / total_size, 100)
            print(f"  Progress: {percent:.1f}%", end='\r')

        urllib.request.urlretrieve(url, dest_path, reporthook=download_progress)
        print(f"\n  ✓ Downloaded {os.path.basename(dest_path)}")
        return True

    except Exception as e:
        print(f"\n  ✗ Error downloading {os.path.basename(dest_path)}: {e}")
        return False

def check_data_files() -> Dict[str, bool]:
    """
    Check which data files are present.

    Returns:
        Dictionary mapping filenames to presence status
    """
    data_dir = get_data_dir()
    status = {}

    for filename in DATA_FILES:
        file_path = os.path.join(data_dir, filename)
        status[filename] = os.path.exists(file_path)

    return status

def download_missing_data(files: Optional[List[str]] = None, force: bool = False) -> bool:
    """
    Download missing TLE data files.

    Args:
        files: List of specific files to download (None = all missing)
        force: If True, download even if files exist

    Returns:
        True if all downloads successful, False otherwise
    """
    data_dir = get_data_dir()

    if files is None:
        # Check which files are missing
        status = check_data_files()
        files_to_download = [f for f, exists in status.items() if not exists]
    else:
        files_to_download = files

    if not files_to_download and not force:
        print("All data files are present.")
        return True

    if force:
        files_to_download = files if files else list(DATA_FILES.keys())

    print(f"Downloading {len(files_to_download)} data files...")
    print(f"Target directory: {data_dir}")

    success = True
    for filename in files_to_download:
        if filename not in DATA_FILES:
            print(f"  ✗ Unknown file: {filename}")
            success = False
            continue

        file_info = DATA_FILES[filename]
        dest_path = os.path.join(data_dir, filename)

        if os.path.exists(dest_path) and not force:
            print(f"  ✓ {filename} already exists")
            continue

        if not download_file(file_info['url'], dest_path, file_info['size_mb']):
            success = False

    return success

def main():
    """Command-line interface for data download."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Download TLE data files for PyMOCAT-MC'
    )
    parser.add_argument(
        'files', nargs='*',
        help='Specific files to download (default: all missing)'
    )
    parser.add_argument(
        '--force', '-f', action='store_true',
        help='Force download even if files exist'
    )
    parser.add_argument(
        '--check', '-c', action='store_true',
        help='Check which files are present'
    )

    args = parser.parse_args()

    if args.check:
        status = check_data_files()
        print("Data file status:")
        for filename, exists in status.items():
            status_str = "✓ Present" if exists else "✗ Missing"
            size_str = f"({DATA_FILES[filename]['size_mb']} MB)"
            print(f"  {filename}: {status_str} {size_str}")
    else:
        success = download_missing_data(args.files, args.force)
        if success:
            print("\nAll downloads completed successfully!")
        else:
            print("\nSome downloads failed. Please try again.")
            exit(1)

if __name__ == '__main__':
    main()