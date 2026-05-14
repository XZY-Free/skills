#!/usr/bin/env python3
"""Inspect current-host MasterGo MCP config without printing secrets."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore


PLACEHOLDER_RE = re.compile(
    r"^\s*$|<[^>]*(TOKEN|KEY)[^>]*>|YOUR[_-]?(TOKEN|KEY)|USER[_-]?(TOKEN|KEY)",
    re.IGNORECASE,
)

SERVER_ALIASES = {
    "magic": ("mastergo-magic-mcp", "mastergo_magic_mcp", "@mastergo/magic-mcp"),
    "codify": ("codify", "codify-mcp", "mastergo-codify"),
}


def expand(path: str) -> Path:
    return Path(path).expanduser()


def redact(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:3]}{'*' * 8}{value[-4:]}"


def is_placeholder(value: str | None) -> bool:
    return value is None or bool(PLACEHOLDER_RE.search(str(value)))


def flatten_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        out: list[str] = []
        for item in value.values():
            out.extend(flatten_values(item))
        return out
    if isinstance(value, list):
        out = []
        for item in value:
            out.extend(flatten_values(item))
        return out
    if value is None:
        return []
    return [str(value)]


def find_tokenish_values(value: Any) -> list[str]:
    texts = flatten_values(value)
    hits: list[str] = []
    for text in texts:
        if "--token=" in text:
            hits.append(text.split("--token=", 1)[1].split()[0].strip("'\""))
        elif re.search(r"(TOKEN|KEY|ACCESS)", text, re.IGNORECASE):
            hits.append(text)
    return hits


def find_url_values(value: Any) -> list[str]:
    hits: list[str] = []
    for text in flatten_values(value):
        if "--url=" in text:
            hits.append(text.split("--url=", 1)[1].split()[0].strip("'\""))
        elif text.startswith(("http://", "https://")):
            hits.append(text)
        elif "CODIFY_MCP_URL" in text and "=" in text:
            hits.append(text.split("=", 1)[1].strip("'\""))
    return hits


def url_type(url: str | None) -> str:
    if not url:
        return "missing"
    if url.startswith(("http://127.0.0.1", "http://localhost", "http://[::1]")):
        return "local"
    if url.startswith("https://"):
        return "remote"
    return "custom"


def network_status(url: str | None) -> dict[str, Any] | None:
    if not url:
        return None
    try:
        request = Request(url, method="GET")
        with urlopen(request, timeout=3) as response:  # noqa: S310 - user-local diagnostic helper
            return {"ok": True, "status": response.status}
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"ok": False, "error": str(exc)}


def key_matches(key: str, aliases: tuple[str, ...]) -> bool:
    key_lower = key.lower()
    return any(alias.lower() in key_lower for alias in aliases)


def collect_server_blocks(config: Any, aliases: tuple[str, ...]) -> list[Any]:
    blocks: list[Any] = []
    if isinstance(config, dict):
        for key, value in config.items():
            if key_matches(str(key), aliases):
                blocks.append(value)
            blocks.extend(collect_server_blocks(value, aliases))
    elif isinstance(config, list):
        for item in config:
            blocks.extend(collect_server_blocks(item, aliases))
    return blocks


def server_status(config: Any, aliases: tuple[str, ...], *, check_network: bool = False) -> dict[str, Any]:
    blocks = collect_server_blocks(config, aliases)
    if not blocks:
        blob = json.dumps(config, ensure_ascii=False) if config is not None else ""
        if any(alias in blob for alias in aliases):
            blocks = [config]
        else:
            return {"present": False, "token": "missing"}

    token_values: list[str] = []
    url_values: list[str] = []
    for block in blocks:
        token_values.extend(find_tokenish_values(block))
        url_values.extend(find_url_values(block))

    url = url_values[0] if url_values else None
    base: dict[str, Any] = {
        "present": True,
        "url": url or "",
        "url_type": url_type(url),
    }
    if check_network:
        base["network"] = network_status(url)

    if not token_values:
        return {**base, "token": "missing"}

    real_values = [value for value in token_values if not is_placeholder(value)]
    if not real_values:
        return {**base, "token": "placeholder"}

    return {
        **base,
        "present": True,
        "token": "configured",
        "redacted_examples": [redact(value) for value in real_values[:2]],
    }


def read_json(path: Path) -> Any:
    return json.loads(path.read_text()) if path.exists() else None


def read_toml(path: Path) -> Any:
    return tomllib.loads(path.read_text()) if path.exists() else None


def inspect_host(host: str, *, check_network: bool = False) -> dict[str, Any]:
    if host == "codex":
        path = expand(os.environ.get("CODEX_CONFIG", "~/.codex/config.toml"))
        data = read_toml(path)
    elif host == "claude":
        path = expand("~/.claude.json")
        data = read_json(path)
    elif host == "cursor":
        candidates = [expand("~/.cursor/mcp.json"), Path.cwd() / ".cursor/mcp.json"]
        path = next((candidate for candidate in candidates if candidate.exists()), candidates[0])
        data = read_json(path)
    else:
        raise ValueError(f"Unsupported host: {host}")

    exists = path.exists()
    servers = {
        name: server_status(data, aliases, check_network=check_network)
        if data is not None
        else {"present": False, "token": "missing", "url": "", "url_type": "missing"}
        for name, aliases in SERVER_ALIASES.items()
    }
    return {
        "host": host,
        "config_path": str(path),
        "config_exists": exists,
        "servers": servers,
    }


def process_chain_text(limit: int = 8) -> str:
    parts: list[str] = []
    pid = os.getpid()
    for _ in range(limit):
        try:
            completed = subprocess.run(
                ["ps", "-o", "ppid=", "-o", "comm=", "-o", "args=", "-p", str(pid)],
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError:
            break
        line = completed.stdout.strip()
        if not line:
            break
        parts.append(line)
        fields = line.split(None, 1)
        if not fields or not fields[0].isdigit():
            break
        parent = int(fields[0])
        if parent <= 1 or parent == pid:
            break
        pid = parent
    return "\n".join(parts).lower()


def detect_host() -> str | None:
    env_text = " ".join(
        f"{key}={value}"
        for key, value in os.environ.items()
        if re.search(r"codex|claude|cursor", key, re.IGNORECASE)
    ).lower()
    process_text = process_chain_text()
    combined = f"{env_text}\n{process_text}"

    if "codex" in combined:
        return "codex"
    if "claude" in combined:
        return "claude"
    if "cursor" in combined:
        return "cursor"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=["auto", "codex", "claude", "cursor"], default="auto")
    parser.add_argument("--all", action="store_true", help="Inspect all known hosts for migration reference.")
    parser.add_argument("--check-network", action="store_true", help="Optionally probe configured MCP URLs.")
    args = parser.parse_args()

    if args.all:
        result = {"inspected": [inspect_host(host, check_network=args.check_network) for host in ("codex", "claude", "cursor")]}
    else:
        host = detect_host() if args.host == "auto" else args.host
        if host is None:
            print(
                json.dumps(
                    {
                        "error": "current_host_unknown",
                        "message": "Ask the user whether the current host is Codex, Claude Code, or Cursor; do not use another host's config as proof.",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 2
        result = inspect_host(host, check_network=args.check_network)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
