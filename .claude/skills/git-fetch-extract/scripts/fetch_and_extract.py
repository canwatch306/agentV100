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

def get_remote_branches(repo_url: str):
    """Get list of remote branches from a Git repository."""
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", repo_url],
            check=True,
            capture_output=True,
            text=True
        )
        branches = []
        for line in result.stdout.strip().split('\n'):
            if line:
                # refs/heads/master -> master
                ref = line.split()[1]
                if ref.startswith('refs/heads/'):
                    branch = ref[len('refs/heads/'):]
                    branches.append(branch)
        return branches
    except subprocess.CalledProcessError as e:
        print(f"Failed to list remote branches: {e.stderr}", file=sys.stderr)
        return []

def run_git_clone(repo_url: str, branch: str, dest_dir: Path):
    """Clone a specific branch of a Git repository into dest_dir."""
    try:
        subprocess.run(
            ["git", "clone", "--branch", branch, "--depth", "1", repo_url, str(dest_dir)],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git clone failed for branch '{branch}': {e.stderr}", file=sys.stderr)
        return False

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
        return False

    print(f"Found {len(archives)} archive(s) in drv/:")
    success = True
    for archive in archives:
        print(f"  - {archive.name} -> extracting to {target_dir}...")
        if not extract_archive(archive, target_dir):
            success = False
    return success

def main():
    parser = argparse.ArgumentParser(description="Fetch a Git repository and extract all archives from its /drv directory.")
    parser.add_argument("repo_url", help="Git repository URL")
    parser.add_argument("--branch", default="main", help="Branch name (default: main)")
    parser.add_argument("--target", default="output", help="Target directory for extraction (default: output, relative to current directory)")
    args = parser.parse_args()

    target_path = Path(args.target)

    # Get all remote branches
    print(f"Fetching remote branches from {args.repo_url}...")
    all_branches = get_remote_branches(args.repo_url)
    if not all_branches:
        print("No remote branches found.", file=sys.stderr)
        sys.exit(1)

    # Determine which branches to try
    branches_to_try = [args.branch] if args.branch in all_branches else []
    # Add other branches, excluding the already tried one
    for branch in all_branches:
        if branch != args.branch:
            branches_to_try.append(branch)

    print(f"Branches available: {', '.join(all_branches)}")
    print(f"Will try branches in order: {', '.join(branches_to_try)}")

    success = False
    for branch in branches_to_try:
        print(f"\nTrying branch: {branch}")
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir) / "repo"
            if not run_git_clone(args.repo_url, branch, repo_dir):
                print(f"Failed to clone branch '{branch}', trying next...")
                continue

            drv_dir = repo_dir / "drv"
            if not drv_dir.exists() or not drv_dir.is_dir():
                print(f"No drv/ directory found in branch '{branch}', trying next...")
                continue

            # Found drv directory, extract archives
            if extract_all_archives(drv_dir, target_path):
                print(f"Successfully extracted archives from branch '{branch}'.")
                success = True
                break
            else:
                print(f"No archives found in drv/ directory of branch '{branch}', trying next...")

    if not success:
        print("Failed to find and extract archives from any branch.", file=sys.stderr)
        sys.exit(1)

    print("Extraction completed.")

if __name__ == "__main__":
    main()