#!/usr/bin/env python3
"""Extract common design tokens from MasterGo D2C HTML/CSS files."""

from __future__ import annotations

import argparse
import collections
import glob
import json
import re
from pathlib import Path


TOKEN_PATTERNS = {
    "colors": re.compile(r"(?:background(?:-color)?|color|fill|stroke)\s*:\s*(#[0-9A-Fa-f]{3,8}|rgba?\([^)]+\))"),
    "fonts": re.compile(r"font-family\s*:\s*([^;\"']+|\"[^\"]+\"|'[^']+')"),
    "fontSizes": re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?px)"),
    "radii": re.compile(r"border-radius\s*:\s*(\d+(?:\.\d+)?px|9999px|50%)"),
    "spacing": re.compile(r"(?:padding|margin|gap|top|left|right|bottom|width|height)\s*:\s*(-?\d+(?:\.\d+)?px)"),
}


def clean_font(value: str) -> str:
    return value.strip().strip("\\\"'").split(",")[0].strip().strip("\\\"'")


def extract(files: list[str]) -> dict[str, dict[str, int]]:
    counters = {name: collections.Counter() for name in TOKEN_PATTERNS}
    for file in files:
        text = Path(file).read_text(encoding="utf-8", errors="ignore")
        for name, pattern in TOKEN_PATTERNS.items():
            values = pattern.findall(text)
            if name == "fonts":
                values = [clean_font(value) for value in values]
            counters[name].update(value for value in values if value)
    return {name: dict(counter.most_common(80)) for name, counter in counters.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--glob", default=".mg/**/*.html", help="Input glob, default: .mg/**/*.html")
    parser.add_argument("--out", default=".codify/design-tokens.json")
    args = parser.parse_args()

    files = sorted(glob.glob(args.glob, recursive=True))
    tokens = extract(files)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"files": files, "tokens": tokens}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {output} from {len(files)} file(s)")
    for group, values in tokens.items():
        preview = ", ".join(list(values)[:8]) or "(none)"
        print(f"{group}: {preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
