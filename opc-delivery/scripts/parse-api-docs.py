#!/usr/bin/env python3
"""Summarize API docs from OpenAPI JSON, Postman JSON, Markdown, and text."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}
ENDPOINT_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)\s+([/\w:.-][^\s`)]*)", re.IGNORECASE)
YAML_PATH_RE = re.compile(r"^\s{0,8}(/[^\s:][^:]*):\s*(?:#.*)?$")
YAML_METHOD_RE = re.compile(r"^\s{2,12}(get|post|put|patch|delete|options|head):\s*(?:#.*)?$", re.IGNORECASE)


def endpoint(method: str, url: str, source: str, **extra: Any) -> dict[str, Any]:
    return {"method": method.upper(), "url": url, "source": source, **{k: v for k, v in extra.items() if v}}


def parse_openapi_json(path: Path, data: dict[str, Any]) -> list[dict[str, Any]]:
    endpoints: list[dict[str, Any]] = []
    for url, methods in (data.get("paths") or {}).items():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            if method.lower() not in METHODS or not isinstance(operation, dict):
                continue
            responses = operation.get("responses") or {}
            ok_response = responses.get("200") or responses.get("201") or responses.get("default") or {}
            content = ok_response.get("content") if isinstance(ok_response, dict) else {}
            schema = (content or {}).get("application/json", {}).get("schema") if isinstance(content, dict) else None
            endpoints.append(
                endpoint(
                    method,
                    url,
                    f"{path}#paths.{url}.{method}",
                    operationId=operation.get("operationId"),
                    summary=operation.get("summary"),
                    response_schema=schema,
                )
            )
    return endpoints


def parse_postman(path: Path, data: dict[str, Any]) -> list[dict[str, Any]]:
    endpoints: list[dict[str, Any]] = []

    def walk(items: list[dict[str, Any]]) -> None:
        for item in items:
            if "item" in item and isinstance(item["item"], list):
                walk(item["item"])
                continue
            request = item.get("request")
            if not isinstance(request, dict):
                continue
            raw_url = request.get("url")
            url = raw_url.get("raw") if isinstance(raw_url, dict) else raw_url
            if not url:
                continue
            responses = item.get("response") or []
            sample = responses[0].get("body") if responses and isinstance(responses[0], dict) else None
            endpoints.append(
                endpoint(
                    request.get("method", "GET"),
                    str(url),
                    f"{path}#item.{item.get('name', len(endpoints))}",
                    operationId=item.get("name"),
                    summary=item.get("description"),
                    sample_response=sample,
                )
            )

    walk(data.get("item", []) if isinstance(data.get("item"), list) else [])
    return endpoints


def parse_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and ("openapi" in data or "swagger" in data):
        return parse_openapi_json(path, data)
    if isinstance(data, dict) and data.get("info"):
        return parse_postman(path, data)
    return []


def parse_text(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    endpoints = []
    for index, match in enumerate(ENDPOINT_RE.finditer(text), start=1):
        endpoints.append(endpoint(match.group(1), match.group(2), f"{path}#match.{index}"))
    return endpoints


def parse_openapi_yaml(path: Path) -> list[dict[str, Any]]:
    """Best-effort OpenAPI YAML path/method parser without third-party deps."""
    endpoints: list[dict[str, Any]] = []
    current_path: str | None = None
    in_paths = False
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

    for line_number, line in enumerate(lines, start=1):
        if re.match(r"^\s*paths:\s*(?:#.*)?$", line):
            in_paths = True
            continue
        if not in_paths:
            continue
        path_match = YAML_PATH_RE.match(line)
        if path_match:
            current_path = path_match.group(1).strip("'\"")
            continue
        method_match = YAML_METHOD_RE.match(line)
        if current_path and method_match:
            endpoints.append(
                endpoint(
                    method_match.group(1),
                    current_path,
                    f"{path}#L{line_number}",
                )
            )

    return endpoints


def parse_file(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        try:
            parsed = parse_json(path)
            if parsed:
                return parsed
        except json.JSONDecodeError:
            pass
    if path.suffix.lower() in {".yaml", ".yml"}:
        parsed = parse_openapi_yaml(path)
        if parsed:
            return parsed
    return parse_text(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default=".codify/api-docs")
    parser.add_argument("--out", default=".codify/api-endpoints.json")
    args = parser.parse_args()

    docs_dir = Path(args.dir)
    endpoints: list[dict[str, Any]] = []
    if docs_dir.exists():
        for path in sorted(p for p in docs_dir.rglob("*") if p.is_file()):
            endpoints.extend(parse_file(path))

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(endpoints, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {output} with {len(endpoints)} endpoint(s)")
    print(json.dumps(endpoints[:20], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
