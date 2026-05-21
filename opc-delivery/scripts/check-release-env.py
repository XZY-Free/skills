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
        "python_ok": sys.version_info >= (3, 11),
        "node": command_version(["node", "--version"]),
        "playwright_optional": bool(importlib.util.find_spec("playwright")),
    }
    errors = []
    if not checks["python_ok"]:
        errors.append("python>=3.11 is required for OPC release validation")
    if not checks["node"]:
        errors.append("node is missing; screenshot.mjs syntax check cannot run")
    result = {"ok": not errors, "checks": checks, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
