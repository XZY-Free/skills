#!/usr/bin/env python3
"""Lint visible Codify HTML copy for the expected UI language."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


DEFAULT_ALLOWED = {
    "MasterGo",
    "Codify",
    "AI",
    "Agent",
    "Agents",
    "AgentOps",
    "API",
    "MCP",
    "D2C",
    "SLA",
    "SSO",
    "RBAC",
    "SSO",
    "OAuth",
    "SDK",
    "UI",
    "UX",
    "HTTP",
    "JSON",
    "GraphQL",
    "WebSocket",
}
SKIP_TAGS = {"script", "style", "svg", "path", "noscript", "template"}
ASCII_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9+/#._-]*")
HAN_RE = re.compile(r"[\u4e00-\u9fff]")


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.texts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack.append(tag.lower())
        for name, value in attrs:
            if name.lower() in {"aria-label", "alt", "title", "placeholder"} and value:
                self.texts.append(value)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.stack:
            index = len(self.stack) - 1 - self.stack[::-1].index(tag)
            del self.stack[index:]

    def handle_data(self, data: str) -> None:
        if any(tag in SKIP_TAGS for tag in self.stack):
            return
        text = " ".join(data.split())
        if text:
            self.texts.append(text)


def visible_text(path: Path) -> list[str]:
    parser = VisibleTextParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return parser.texts


def strip_allowed(text: str, allowed: set[str]) -> str:
    normalized = text
    for term in sorted(allowed, key=len, reverse=True):
        normalized = re.sub(rf"\b{re.escape(term)}\b", " ", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\b\d+[a-zA-Z%]*\b", " ", normalized)
    return normalized


def lint_texts(texts: list[str], expected: str, allowed: set[str], strict: bool) -> dict[str, object]:
    joined = "\n".join(texts)
    checked = strip_allowed(joined, allowed)
    ascii_words = ASCII_WORD_RE.findall(checked)
    han_chars = HAN_RE.findall(checked)
    text_count = len(texts)
    english_word_count = len(ascii_words)
    han_count = len(han_chars)
    samples = []
    for text in texts:
        stripped = strip_allowed(text, allowed)
        if ASCII_WORD_RE.search(stripped):
            samples.append(text)
        if len(samples) >= 8:
            break

    errors: list[str] = []
    warnings: list[str] = []
    expected = expected.lower()
    if expected in {"simplified-chinese", "zh", "zh-cn", "chinese"}:
        if text_count and han_count == 0:
            errors.append("expected Simplified Chinese UI copy, but no CJK text was found")
        ratio = english_word_count / max(1, english_word_count + han_count)
        threshold = 0.34 if strict else 0.5
        if english_word_count >= 12 and ratio > threshold:
            bucket = errors if strict else warnings
            bucket.append(f"English-looking visible copy ratio is too high: {ratio:.2f}")
    elif expected in {"english", "en"}:
        if text_count and han_count > 8:
            errors.append("expected English UI copy, but substantial CJK text was found")
    else:
        warnings.append(f"custom expected language {expected!r}; only summary metrics were produced")

    return {
        "expectedLanguage": expected,
        "textNodes": text_count,
        "hanChars": han_count,
        "englishWordsAfterAllowlist": english_word_count,
        "englishSamples": samples,
        "errors": errors,
        "warnings": warnings,
        "ok": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_file", type=Path)
    parser.add_argument("--expected", required=True, help="simplified-chinese, english, or custom label")
    parser.add_argument("--mode", choices=["strict", "warning"], default="strict")
    parser.add_argument("--allow", action="append", default=[], help="Additional allowed original-language term")
    args = parser.parse_args()

    allowed = set(DEFAULT_ALLOWED) | set(args.allow)
    result = lint_texts(visible_text(args.html_file), args.expected, allowed, args.mode == "strict")
    result["file"] = str(args.html_file)
    result["allowedTerms"] = sorted(allowed)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] or args.mode == "warning" else 1


if __name__ == "__main__":
    sys.exit(main())
