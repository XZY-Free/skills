#!/usr/bin/env python3
"""Audit whether a local HTML artifact is safe to reuse for a Codify write."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


OLD_MARKERS = [
    "dashboard",
    "governance",
    "agents",
    "observability",
    "audit",
    "english",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[\w\u4e00-\u9fff]+", text)}


def audit(args: argparse.Namespace) -> dict[str, object]:
    text = args.html.read_text(encoding="utf-8", errors="ignore")
    goal = args.goal or ""
    goal_tokens = tokenize(goal)
    artifact_tokens = tokenize(text)
    overlap = sorted(goal_tokens & artifact_tokens)
    errors: list[str] = []
    warnings: list[str] = []

    if args.source == "historical":
        warnings.append("artifact source is historical; require fresh coverage, language, and direction checks")
    if not goal_tokens:
        warnings.append("original goal is empty; cannot verify coverage overlap")
    elif len(overlap) < min(3, len(goal_tokens)):
        warnings.append("artifact has low textual overlap with the current goal")
    if args.expected_language.startswith("simplified") and any(marker in text.lower() for marker in OLD_MARKERS):
        errors.append("artifact contains English product UI markers for a Simplified Chinese target")
    if "<style" in text.lower() or "stylesheet" in text.lower() or " style=" in text.lower():
        errors.append("artifact contains native CSS/style dependencies; convert to Codify-safe Tailwind HTML")
    if args.require_unit and args.require_unit.lower() not in text.lower():
        errors.append(f"required design unit marker {args.require_unit!r} was not found in artifact")

    return {
        "file": str(args.html),
        "source": args.source,
        "sha256": sha256(args.html),
        "expectedLanguage": args.expected_language,
        "goalOverlapTokens": overlap[:30],
        "errors": errors,
        "warnings": warnings,
        "ok": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--source", choices=["current-run", "mastergo-baseline", "user-provided", "historical"], required=True)
    parser.add_argument("--goal", default="")
    parser.add_argument("--expected-language", default="simplified-chinese")
    parser.add_argument("--require-unit", default="")
    args = parser.parse_args()
    result = audit(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
