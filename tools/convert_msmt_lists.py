#!/usr/bin/env python3
"""
Convert MSMT17 list_* files to v2 folder layout (bounding_box_train, query, bounding_box_test).
Behavior:
 - Reads list_train.txt, list_val.txt, list_query.txt, list_gallery.txt under the dataset root.
 - For each filename in the lists it searches for the file anywhere under the dataset root (recursively).
 - If found, copies it to the destination folder (train -> bounding_box_train, test -> bounding_box_test, query -> query)
 - By default runs in dry-run mode printing what it would copy. Use --execute to actually copy.

Usage:
 python tools/convert_msmt_lists.py /path/to/datasets/MSMT17 --dry-run
 python tools/convert_msmt_lists.py /path/to/datasets/MSMT17 --execute

Notes:
 - This script copies files (does not move). It will create the destination dirs if missing.
 - It tries to be safe: check dry-run output before running with --execute.
"""

import argparse
from pathlib import Path
import shutil
import sys
import re

LIST_MAP = {
    'list_train.txt': 'bounding_box_train',
    'list_val.txt': 'bounding_box_train',
    'list_query.txt': 'query',
    'list_gallery.txt': 'bounding_box_test'
}

FILENAME_RE = re.compile(r"([\-\d]+)_([\-\d]+)_([\-\d]+)")


def find_file(root: Path, fname: str):
    """Search for fname (basename) anywhere under root. Return Path or None."""
    # First try exact path relative to root
    cand = root / fname
    if cand.exists():
        return cand
    # Try basename search
    basename = Path(fname).name
    # Use rglob for recursive search but limit to common extensions
    for p in root.rglob(basename):
        if p.is_file():
            return p
    return None


def process(root: Path, execute: bool = False):
    root = Path(root)
    if not root.exists():
        print(f"Dataset root not found: {root}")
        return 1

    total_missing = 0
    actions = []

    for list_name, dest_sub in LIST_MAP.items():
        list_path = root / list_name
        dest_dir = root / dest_sub
        if not list_path.exists():
            print(f"  Skipping missing list: {list_path}")
            continue
        print(f"Processing {list_name} -> {dest_sub}")
        with list_path.open('r', encoding='utf-8') as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        for ln in lines:
            # lines may contain additional fields like pid or bbox; take first token
            fname = ln.split(' ')[0]
            src = find_file(root, fname)
            if src is None:
                print(f"  MISSING: {fname}")
                total_missing += 1
                continue
            # destination path keeps only basename
            dst = dest_dir / Path(fname).name
            actions.append((src, dst))

    if total_missing:
        print(f"\nTotal missing files referenced in lists: {total_missing}")
        print("Fix missing files before executing. Dry-run shows what would be copied.")

    if not actions:
        print("No files to copy.")
        return 0

    # print summary (first 20)
    print(f"\nPlanned copy operations: {len(actions)}")
    for src, dst in actions[:20]:
        print(f"  {src} -> {dst}")
    if len(actions) > 20:
        print(f"  ... and {len(actions)-20} more")

    if not execute:
        print("\nDry-run complete. Rerun with --execute to perform copies.")
        return 0

    # perform copies
    for src, dst in actions:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(src, dst)
    print("\nCopy complete.")
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert MSMT17 lists to v2 layout')
    parser.add_argument('root', help='Path to MSMT17 dataset root (containing list_*.txt)')
    parser.add_argument('--execute', action='store_true', help='Actually copy files. Without this flag runs a dry-run')
    args = parser.parse_args()
    rc = process(Path(args.root), execute=args.execute)
    sys.exit(rc)
