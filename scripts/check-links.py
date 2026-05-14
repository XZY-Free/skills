#!/usr/bin/env python3
"""Check that all internal markdown links resolve to real files.

Scans every .md file in the repo (excluding .git, node_modules, .omc),
extracts relative links and image paths, and verifies each target exists.

Exit codes:
  0 = all links OK
  1 = broken links found
  2 = unexpected error
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", "node_modules", ".omc", ".idea", "dist", "build"}

# Files in any `_template/` directory have placeholder links by design
# (they are templates for contributors to fill in). Skip link-checking them.
TEMPLATE_MARKERS = {"_template"}

# match  [text](path)  and  ![alt](path)  and  <img src="path">
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+?)(?:\s+\"[^\"]*\")?\)|<img[^>]+src=\"([^\"]+)\"")

# Template / placeholder syntaxes that should not be treated as real links.
PLACEHOLDER_TOKENS = ("{{", "}}", "${", "<%", "%>", "<your-", "<skill-")


def iter_md_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.md"):
        parts = path.relative_to(ROOT).parts
        if any(part in EXCLUDE_DIRS for part in parts):
            continue
        if any(part in TEMPLATE_MARKERS for part in parts):
            continue
        files.append(path)
    return sorted(files)


def is_external(link: str) -> bool:
    return link.startswith(("http://", "https://", "mailto:", "tel:"))


def is_placeholder(link: str) -> bool:
    """Return True if the link contains a template / placeholder token
    (e.g. `{{keyword}}`, `${var}`, `<skill-name>`). These appear inside
    skill documentation that describes conventions; they aren't real paths."""
    return any(token in link for token in PLACEHOLDER_TOKENS)


def resolve(file: Path, link: str) -> Path:
    link = link.split("#", 1)[0].strip()
    if not link:
        return file  # anchor-only link, trivially valid
    return (file.parent / link).resolve()


def check(file: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = file.read_text(encoding="utf-8")
    except Exception as exc:
        return [f"unreadable: {exc}"]
    for m in LINK_RE.finditer(text):
        link = m.group(1) or m.group(2)
        if not link or is_external(link) or is_placeholder(link):
            continue
        target = resolve(file, link)
        if not target.exists():
            errors.append(f"{link}  (resolved to {target.relative_to(ROOT) if target.is_absolute() else target})")
    return errors


def main() -> int:
    files = iter_md_files()
    if not files:
        print("no markdown files found", file=sys.stderr)
        return 2

    failed = 0
    for f in files:
        errs = check(f)
        rel = f.relative_to(ROOT)
        if errs:
            failed += 1
            print(f"✗ {rel}")
            for e in errs:
                print(f"    {e}")
        else:
            print(f"✓ {rel}")

    if failed:
        print(f"\n❌ {failed} file(s) with broken links")
        return 1
    print(f"\n✅ link check OK ({len(files)} files)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # pragma: no cover
        print(f"check-links.py crashed: {exc}", file=sys.stderr)
        sys.exit(2)
