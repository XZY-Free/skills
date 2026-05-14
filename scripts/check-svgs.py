#!/usr/bin/env python3
"""Validate every .svg file in the repo is well-formed XML.

Exit codes:
  0 = all SVGs valid
  1 = at least one SVG broken
  2 = unexpected error
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", "node_modules", ".omc", ".idea", "dist", "build"}


def iter_svg_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.svg"):
        if any(part in EXCLUDE_DIRS for part in path.relative_to(ROOT).parts):
            continue
        files.append(path)
    return sorted(files)


def main() -> int:
    files = iter_svg_files()
    if not files:
        print("no SVG files found (skip)")
        return 0

    failed = 0
    for f in files:
        rel = f.relative_to(ROOT)
        try:
            ET.parse(f)
        except ET.ParseError as exc:
            failed += 1
            print(f"✗ {rel}: {exc}")
            continue
        except Exception as exc:
            failed += 1
            print(f"✗ {rel}: unexpected error: {exc}")
            continue
        print(f"✓ {rel}")

    if failed:
        print(f"\n❌ {failed}/{len(files)} SVG(s) invalid")
        return 1
    print(f"\n✅ SVG check OK ({len(files)} files)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # pragma: no cover
        print(f"check-svgs.py crashed: {exc}", file=sys.stderr)
        sys.exit(2)
