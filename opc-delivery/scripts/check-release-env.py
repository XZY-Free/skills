#!/usr/bin/env python3
"""Check local release-gate dependencies for the OPC delivery skill."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys


def command_version(cmd: list[str]) -> str | None:
    if not shutil.which(cmd[0]):
        return None
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    return (completed.stdout or completed.stderr).strip().splitlines()[0] if completed.returncode == 0 else None


def main() -> int:
    checks = {
        "python": sys.version.split()[0],
        "yaml": bool(importlib.util.find_spec("yaml")),
        "uv": command_version(["uv", "--version"]),
        "node": command_version(["node", "--version"]),
        "playwright_optional": bool(importlib.util.find_spec("playwright")),
    }
    errors = []
    if not checks["yaml"] and not checks["uv"]:
        errors.append("PyYAML is missing and uv is unavailable; skill-creator quick_validate.py cannot run")
    if not checks["node"]:
        errors.append("node is missing; screenshot.mjs syntax check cannot run")
    result = {"ok": not errors, "checks": checks, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
