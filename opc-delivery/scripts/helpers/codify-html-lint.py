#!/usr/bin/env python3
"""Lint Codify-bound HTML without scanning visible text as CSS/class content."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


VISUAL_TAGS = {
    "a",
    "article",
    "aside",
    "button",
    "canvas",
    "div",
    "fieldset",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "img",
    "input",
    "label",
    "li",
    "main",
    "nav",
    "ol",
    "p",
    "section",
    "select",
    "span",
    "table",
    "tbody",
    "td",
    "textarea",
    "th",
    "thead",
    "tr",
    "ul",
}


class CodifyHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.errors: list[dict[str, str | int]] = []
        self.warnings: list[dict[str, str | int]] = []
        self.counts = {"elements": 0, "visual_elements": 0, "data_name": 0}
        self.root_tag = ""
        self.visible_text_nodes = 0
        self._stack: list[str] = []

    def _issue(self, level: str, tag: str, message: str) -> None:
        bucket = self.errors if level == "error" else self.warnings
        bucket.append({"line": self.getpos()[0], "tag": tag, "message": message})

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self._stack.append(tag)
        if not self.root_tag and tag not in {"!doctype", "html", "head", "meta", "title", "link", "script", "style"}:
            self.root_tag = tag
        attr = {name.lower(): value or "" for name, value in attrs}
        self.counts["elements"] += 1

        if tag == "style":
            self._issue("error", tag, "<style> is not Codify-safe; use Tailwind utility classes.")

        if tag == "link" and attr.get("rel", "").lower() == "stylesheet":
            self._issue("error", tag, "External stylesheets are not Codify-safe.")

        if "style" in attr:
            self._issue("error", tag, "Inline style is not Codify-safe; convert to utility classes.")

        if tag in VISUAL_TAGS:
            self.counts["visual_elements"] += 1
            if attr.get("data-name"):
                self.counts["data_name"] += 1
            else:
                self._issue("warning", tag, "Visible element has no data-name.")

        class_value = attr.get("class", "")
        if class_value:
            for token in class_value.split():
                if re.search(r"[{};]", token):
                    self._issue("error", tag, f"Class token looks like raw CSS: {token}")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self._stack:
            index = len(self._stack) - 1 - self._stack[::-1].index(tag)
            del self._stack[index:]

    def handle_data(self, data: str) -> None:
        if any(tag in {"script", "style", "template", "svg"} for tag in self._stack):
            return
        if data.strip():
            self.visible_text_nodes += 1


def lint(path: Path) -> dict[str, object]:
    parser = CodifyHtmlParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return {
        "file": str(path),
        "counts": parser.counts,
        "root_tag": parser.root_tag,
        "visible_text_nodes": parser.visible_text_nodes,
        "errors": parser.errors,
        "warnings": parser.warnings,
        "ok": not parser.errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_file", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit stable JSON output (default behavior).")
    args = parser.parse_args()

    result = lint(args.html_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
