#!/usr/bin/env python3
"""Validate every <skill>/SKILL.md has a usable frontmatter block.

Required:
  - starts with a `---` line
  - has a closing `---` line within first 200 lines
  - frontmatter contains `name:` and `description:` keys
  - `name` matches the directory name (e.g. opc-delivery/SKILL.md → name: opc-delivery)

This does NOT do strict YAML parsing (avoids adding pyyaml dependency).
It's a smoke check, not a schema validator.

Exit codes:
  0 = all SKILL.md files valid
  1 = at least one invalid
  2 = unexpected error
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", "node_modules", ".omc", ".idea", "dist", "build", "examples", "_template"}


def iter_skill_md() -> list[Path]:
    files: list[Path] = []
    # Look in top-level subdirs only: <skill-name>/SKILL.md
    for child in sorted(ROOT.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith(".") or child.name in EXCLUDE_DIRS:
            continue
        candidate = child / "SKILL.md"
        if candidate.is_file():
            files.append(candidate)
    return files


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    """Naive line-based frontmatter parser. Returns (fields, errors)."""
    lines = text.splitlines()
    errors: list[str] = []
    if not lines or lines[0].strip() != "---":
        errors.append("missing opening `---` on line 1")
        return {}, errors
    end = None
    for i, line in enumerate(lines[1:200], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        errors.append("missing closing `---` within first 200 lines")
        return {}, errors

    fields: dict[str, str] = {}
    current_key: str | None = None
    for raw in lines[1:end]:
        # Multi-line value support (basic): "key: |" or "key: >"
        if current_key is not None and (raw.startswith(" ") or raw.startswith("\t") or raw == ""):
            fields[current_key] += "\n" + raw.strip()
            continue
        if ":" in raw and not raw.lstrip().startswith("#"):
            key, _, value = raw.partition(":")
            key = key.strip()
            value = value.strip()
            fields[key] = value
            current_key = key if value in ("|", ">") else None
        else:
            current_key = None
    return fields, errors


def check(file: Path) -> list[str]:
    errs: list[str] = []
    try:
        text = file.read_text(encoding="utf-8")
    except Exception as exc:
        return [f"unreadable: {exc}"]

    fields, parse_errs = parse_frontmatter(text)
    errs.extend(parse_errs)
    if parse_errs:
        return errs

    if "name" not in fields:
        errs.append("missing `name:` in frontmatter")
    if "description" not in fields:
        errs.append("missing `description:` in frontmatter")

    if "name" in fields:
        skill_dir = file.parent.name
        # `name` can be "value" or "|" (then real value is in following block)
        name_value = fields["name"].strip().strip('"').strip("'")
        # For multi-line strings the value starts with '|' or '>' followed by indented lines.
        # We stored those lines into the same key, so split off the marker.
        if name_value.startswith(("|", ">")):
            name_value = name_value.split("\n", 1)[-1].strip()
        if name_value and name_value != skill_dir:
            errs.append(
                f"frontmatter `name: {name_value!r}` does not match directory name {skill_dir!r}"
            )

    return errs


def main() -> int:
    files = iter_skill_md()
    if not files:
        print("no SKILL.md files found (skip)")
        return 0

    failed = 0
    for f in files:
        rel = f.relative_to(ROOT)
        errs = check(f)
        if errs:
            failed += 1
            print(f"✗ {rel}")
            for e in errs:
                print(f"    {e}")
        else:
            print(f"✓ {rel}")

    if failed:
        print(f"\n❌ {failed}/{len(files)} SKILL.md file(s) invalid")
        return 1
    print(f"\n✅ SKILL.md frontmatter check OK ({len(files)} files)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # pragma: no cover
        print(f"check-skill-frontmatter.py crashed: {exc}", file=sys.stderr)
        sys.exit(2)
