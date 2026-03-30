
---

## scripts/fetch_and_extract.py

```python
#!/usr/bin/env python3
"""Fetch a Git repository and extract all archives from its /drv directory.

Usage:
    python fetch_and_extract.py <repo_url> [--branch <branch>] [--target <target_dir>]

Example:
    python fetch_and_extract.py https://github.com/example/project.git --branch main
"""

import sys
import os
import argparse
import subprocess
import tarfile
import zipfile
import shutil
import tempfile
from pathlib import Path

# Supported archive extensions and corresponding handlers
ARCHIVE_HANDLERS = {
    ('.tar.gz', '.tgz'): lambda p, d: tarfile.open(p, 'r:gz').extractall(d),
    ('.tar.bz2', '.tbz2'): lambda p, d: tarfile.open(p, 'r:bz2').extractall(d),
    ('.tar.xz', '.txz'): lambda p, d: tarfile.open(p, 'r:xz').extractall(d),
    ('.zip',): lambda p, d: zipfile.ZipFile(p).extractall(d),
}

def run_git_clone(repo_url: str, branch: str, dest_dir: Path):
    """Clone a specific branch of a Git repository into dest_dir."""
    try:
        subprocess.run(
            ["git", "clone", "--branch", branch, "--depth", "1", repo_url, str(dest_dir)],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Git clone failed: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def extract_archive(archive_path: Path, target_dir: Path):
    """Extract a single archive based on its suffix."""
    suffix = archive_path.suffix
    # Handle double suffixes like .tar.gz
    if archive_path.suffixes[-2:] == ['.tar', '.gz']:
        suffix = '.tar.gz'
    elif archive_path.suffixes[-2:] == ['.tar', '.bz2']:
        suffix = '.tar.bz2'
    elif archive_path.suffixes[-2:] == ['.tar', '.xz']:
        suffix = '.tar.xz'

    for patterns, handler in ARCHIVE_HANDLERS.items():
        if suffix in patterns:
            try:
                handler(archive_path, target_dir)
                return True
            except Exception as e:
                print(f"  Error extracting {archive_path.name}: {e}", file=sys.stderr)
                return False
    print(f"  Skipping {archive_path.name}: unsupported format", file=sys.stderr)
    return False

def extract_all_archives(drv_dir: Path, target_dir: Path):
    """Find all archives in drv_dir and extract them to target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)
    archives = []
    for ext_patterns in ARCHIVE_HANDLERS.keys():
        for ext in ext_patterns:
            archives.extend(drv_dir.glob(f"*{ext}"))

    if not archives:
        print("No archive files found in drv/.")
        return

    print(f"Found {len(archives)} archive(s) in drv/:")
    for archive in archives:
        print(f"  - {archive.name} -> extracting to {target_dir}...")
        extract_archive(archive, target_dir)

def main():
    parser = argparse.ArgumentParser(description="Fetch a Git repository and extract all archives from its /drv directory.")
    parser.add_argument("repo_url", help="Git repository URL")
    parser.add_argument("--branch", default="main", help="Branch name (default: main)")
    parser.add_argument("--target", default="output", help="Target directory for extraction (default: output, relative to current directory)")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir) / "repo"
        print(f"Cloning repository {args.repo_url} (branch: {args.branch})...")
        run_git_clone(args.repo_url, args.branch, repo_dir)

        drv_dir = repo_dir / "drv"
        if not drv_dir.exists() or not drv_dir.is_dir():
            print(f"Warning: drv/ directory not found in repository.", file=sys.stderr)
            sys.exit(0)

        target_path = Path(args.target)
        extract_all_archives(drv_dir, target_path)
        print("Extraction completed.")

if __name__ == "__main__":
    main()