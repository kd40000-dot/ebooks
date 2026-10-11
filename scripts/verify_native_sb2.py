#!/usr/bin/env python3
"""Read-only validation of a genuine Android KursX Smart Book SB2 container.

This cannot decrypt or verify the alignment inside encrypted chapters.
It checks native package shape, encryption flags and ZIP structure only.
"""
import argparse
import hashlib
from pathlib import Path
import sys
import zipfile


def inspect(path: Path, chapters: int) -> int:
    if not path.is_file():
        print(f"Missing SB2: {path}", file=sys.stderr)
        return 2
    raw = path.read_bytes()
    try:
        with zipfile.ZipFile(path) as z:
            entries = z.infolist()
            sb = [x for x in entries if x.filename.lower().endswith(".sb") and not x.is_dir()]
            metadata = [x for x in sb if "/" not in x.filename]
            chapter = [x for x in sb if "/" in x.filename]
            bad = [x.filename for x in sb if not (x.flag_bits & 1)]
            unsafe = [x.filename for x in entries if x.filename.startswith("/") or ".." in x.filename.split("/")]
            print(f"File: {path.name}")
            print(f"Size: {len(raw)} bytes")
            print(f"SHA-256: {hashlib.sha256(raw).hexdigest()}")
            print(f"Metadata entries: {len(metadata)}; chapter entries: {len(chapter)}")
            for entry in sb:
                print(f"  {'encrypted' if entry.flag_bits & 1 else 'NOT encrypted'} {entry.filename} ({entry.file_size} B)")
            if len(metadata) != 1 or len(chapter) != chapters or bad or unsafe:
                print(f"INVALID SHAPE (unencrypted={bad!r}, unsafe={unsafe!r})", file=sys.stderr)
                return 1
            print("PASS: expected native encrypted ZIP entry structure.")
            print("NOTE: encrypted content and translation alignment require in-app import testing.")
            return 0
    except (zipfile.BadZipFile, OSError) as e:
        print(f"Cannot parse ZIP: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file", type=Path)
    p.add_argument("--chapters", required=True, type=int)
    args = p.parse_args()
    raise SystemExit(inspect(args.file, args.chapters))
