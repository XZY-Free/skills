#!/usr/bin/env python3
"""Inspect local Codify component library snapshots."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_CATALOG = Path(".codify/library/catalog.json")
REQUIRED_FILES = ("index.json", "icons.json", "variable.json")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_catalog(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = read_json(path)
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("libraries", "items", "data"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [data]
    return []


def library_name(item: dict[str, Any]) -> str:
    return str(item.get("name") or item.get("teamLibraryName") or item.get("title") or item.get("id") or "")


def command_list(args: argparse.Namespace) -> int:
    items = load_catalog(args.catalog)
    print(json.dumps({"catalog": str(args.catalog), "libraries": items, "count": len(items)}, ensure_ascii=False, indent=2))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    root = args.library_dir
    errors = []
    for name in REQUIRED_FILES:
        if not (root / name).exists():
            errors.append(f"missing {name}")
    result = {"libraryDir": str(root), "ok": not errors, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def score_library(name: str, scenario: str) -> int:
    lower = f"{name} {scenario}".lower()
    score = 0
    for keyword in ("admin", "dashboard", "enterprise", "antd", "table", "form", "agent", "ops"):
        if keyword in lower:
            score += 1
    if any(keyword in lower for keyword in ("marketing", "landing", "brand")):
        score -= 1
    return score


def command_recommend(args: argparse.Namespace) -> int:
    items = load_catalog(args.catalog)
    ranked = sorted(
        (
            {
                "name": library_name(item),
                "score": score_library(library_name(item), args.scenario),
                "raw": item,
            }
            for item in items
        ),
        key=lambda item: item["score"],
        reverse=True,
    )
    best = ranked[0] if ranked else None
    strategy = "full-components" if args.scenario in {"admin", "dashboard", "enterprise", "form"} else "hybrid"
    print(json.dumps({"recommendation": best, "buildStrategy": strategy, "ranked": ranked}, ensure_ascii=False, indent=2))
    return 0 if best else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_list = sub.add_parser("list")
    p_list.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    p_list.set_defaults(func=command_list)

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("library_dir", type=Path)
    p_validate.set_defaults(func=command_validate)

    p_recommend = sub.add_parser("recommend")
    p_recommend.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    p_recommend.add_argument("--scenario", default="enterprise")
    p_recommend.set_defaults(func=command_recommend)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
