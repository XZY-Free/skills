#!/usr/bin/env python3
"""DSL diff for MasterGo Magic update flow.

Loads two MCP toolu_*.json captures (or already-parsed DSL JSON files) and reports
added / removed / changed node signatures by id. Used by update-flow.md step 3-4 so
each session does not reinvent the same recursive walk.

Signature fields: type, name, text, fill, strokeColor, interactive.

Usage:
    scripts/dsl-diff.py <old.json> <new.json>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def load_dsl(path: Path) -> Any:
    raw = path.read_text(encoding="utf-8")
    outer = json.loads(raw)
    if isinstance(outer, list) and outer and isinstance(outer[0], dict) and "text" in outer[0]:
        inner = outer[0]["text"]
        return json.loads(inner)
    if isinstance(outer, dict) and "text" in outer and isinstance(outer["text"], str):
        return json.loads(outer["text"])
    return outer


def collect_signatures(dsl: Any) -> dict[str, dict[str, Any]]:
    sigs: dict[str, dict[str, Any]] = {}

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            nid = node.get("id")
            if nid:
                sigs[nid] = {
                    "type": node.get("type"),
                    "name": node.get("name"),
                    "text": str(node.get("text", "")),
                    "fill": node.get("fill"),
                    "strokeColor": node.get("strokeColor"),
                    "width": node.get("width"),
                    "height": node.get("height"),
                    "relativeX": node.get("relativeX"),
                    "relativeY": node.get("relativeY"),
                    "layoutStyle": node.get("layoutStyle"),
                    "interactive": json.dumps(node.get("interactive", []), ensure_ascii=False, sort_keys=True),
                }
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(dsl.get("dsl", dsl) if isinstance(dsl, dict) else dsl)
    return sigs


def diff(old: dict[str, dict[str, Any]], new: dict[str, dict[str, Any]]) -> dict[str, Any]:
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed: list[dict[str, Any]] = []
    for nid in sorted(set(old) & set(new)):
        if old[nid] != new[nid]:
            field_diff = {k: {"old": old[nid].get(k), "new": new[nid].get(k)} for k in set(old[nid]) | set(new[nid]) if old[nid].get(k) != new[nid].get(k)}
            changed.append({"id": nid, "fields": field_diff})
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "categories": categorize_changes(changed),
        "summary": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
        },
    }


def has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def has_ascii_word(text: str) -> bool:
    return bool(re.search(r"[A-Za-z]{3,}", text))


def categorize_changes(changed: list[dict[str, Any]]) -> dict[str, Any]:
    categories: dict[str, list[dict[str, Any]]] = {
        "text": [],
        "fill": [],
        "layout": [],
        "interaction": [],
        "other": [],
    }
    language_risks: list[dict[str, Any]] = []
    for item in changed:
        fields = item.get("fields", {})
        bucketed = False
        for field, diff_value in fields.items():
            target = "other"
            if field == "text":
                target = "text"
                old_text = str(diff_value.get("old", ""))
                new_text = str(diff_value.get("new", ""))
                if (has_cjk(old_text) and has_ascii_word(new_text)) or (has_ascii_word(old_text) and has_cjk(new_text)):
                    language_risks.append({"id": item.get("id"), "old": old_text, "new": new_text})
            elif field in {"fill", "strokeColor"}:
                target = "fill"
            elif field == "interactive":
                target = "interaction"
            elif field in {"width", "height", "relativeX", "relativeY", "layoutStyle"}:
                target = "layout"
            categories[target].append({"id": item.get("id"), "field": field, "diff": diff_value})
            bucketed = True
        if not bucketed:
            categories["other"].append(item)
    return {**categories, "language_risks": language_risks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", help="Path to old DSL JSON file (raw MCP capture or already-parsed)")
    parser.add_argument("new", help="Path to new DSL JSON file")
    parser.add_argument("--output", choices=["json", "summary"], default="json")
    parser.add_argument("--language-risk", action="store_true", help="Exit 1 when text diff suggests a UI language change.")
    args = parser.parse_args()

    old_dsl = load_dsl(Path(args.old))
    new_dsl = load_dsl(Path(args.new))

    result = diff(collect_signatures(old_dsl), collect_signatures(new_dsl))

    if args.output == "summary":
        print(f"+ added:   {result['summary']['added']}")
        print(f"- removed: {result['summary']['removed']}")
        print(f"~ changed: {result['summary']['changed']}")
        print(f"! language risks: {len(result['categories']['language_risks'])}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if args.language_risk and result["categories"]["language_risks"] else 0


if __name__ == "__main__":
    sys.exit(main())
