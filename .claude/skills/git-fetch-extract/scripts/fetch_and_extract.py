
---

## scripts/fetch_and_extract.py

```python
#!/usr/bin/env python3
"""Fetch a Git repository and extract a specific tarball from it.

Usage:
    python fetch_and_extract.py <repo_url> [--branch <branch>] [--target <target_dir>]

Example:
    python fetch_and_extract.py https://github.com/example/project.git --branch main --target d/save
"""

import sys
import os
import argparse
import subprocess
import tarfile
import shutil
import tempfile
from pathlib import Path

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

def extract_tar_gz(repo_path: Path, target_dir: Path):
    """Find drv/a.tar.gz inside repo_path and extract it to target_dir."""
    tarball_path = repo_path / "drv" / "a.tar.gz"
    if not tarball_path.exists():
        print(f"Error: File 'drv/a.tar.gz' not found in the repository.", file=sys.stderr)
        sys.exit(1)

    try:
        # Ensure target directory exists
        target_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(tarball_path, "r:gz") as tar:
            tar.extractall(target_dir)
    except tarfile.TarError as e:
        print(f"Error extracting tarball: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Fetch a Git repository and extract drv/a.tar.gz.")
    parser.add_argument("repo_url", help="Git repository URL")
    parser.add_argument("--branch", default="main", help="Branch name (default: main)")
    parser.add_argument("--target", default="d/save", help="Target directory for extraction (default: d/save)")
    args = parser.parse_args()

    # Use a temporary directory for cloning, then clean up after extraction
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir) / "repo"
        print(f"Cloning repository {args.repo_url} (branch: {args.branch})...")
        run_git_clone(args.repo_url, args.branch, repo_dir)

        print(f"Extracting drv/a.tar.gz to {args.target}...")
        target_path = Path(args.target)
        extract_tar_gz(repo_dir, target_path)

        print("Extraction completed.")
        # Temporary directory is automatically deleted after this block

if __name__ == "__main__":
    main()