#!/usr/bin/env python3
"""Fetch an HTML/text document and print searchable plain-text snippets."""

from __future__ import annotations

import argparse
import html
import re
import sys
import urllib.request
from html.parser import HTMLParser


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1
        if tag in {"p", "br", "div", "section", "article", "li", "tr", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1
        if tag in {"p", "div", "section", "article", "li", "tr", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        raw = html.unescape(" ".join(self.parts))
        return re.sub(r"[ \t\r\f\v]+", " ", re.sub(r"\n\s*\n+", "\n", raw)).strip()


def fetch(url: str, timeout: int) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "mastergo-skill/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        content_type = response.headers.get("content-type", "")
        body = response.read().decode("utf-8", errors="ignore")
    if "html" not in content_type and "<html" not in body[:500].lower():
        return body
    parser = TextExtractor()
    parser.feed(body)
    return parser.text()


def snippets(text: str, keywords: list[str], radius: int) -> list[str]:
    if not keywords:
        return [text[: radius * 2]]
    found: list[str] = []
    lower = text.lower()
    for keyword in keywords:
        idx = lower.find(keyword.lower())
        if idx < 0:
            found.append(f"[MISSING] {keyword}")
            continue
        start = max(0, idx - radius)
        end = min(len(text), idx + len(keyword) + radius)
        found.append(f"[FOUND] {keyword}\n{text[start:end].strip()}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--keyword", action="append", default=[])
    parser.add_argument("--radius", type=int, default=360)
    parser.add_argument("--timeout", type=int, default=12)
    args = parser.parse_args()

    try:
        text = fetch(args.url, args.timeout)
    except Exception as exc:
        print(f"fetch failed: {exc}", file=sys.stderr)
        return 2

    print("\n\n---\n\n".join(snippets(text, args.keyword, args.radius)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
