#!/usr/bin/env python3
"""Run Codify write preflight checks and return a machine-readable decision."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_json(cmd: list[str]) -> tuple[int, dict[str, Any] | None, str]:
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    payload = None
    if completed.stdout.strip():
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            payload = None
    return completed.returncode, payload, completed.stderr.strip()


def preflight(args: argparse.Namespace) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {}

    if not args.task_state.exists():
        errors.append(f"task state missing: {args.task_state}")
    else:
        state = load_json(args.task_state)
        details["taskId"] = state.get("taskId")
        gate = state.get("gateCard") or {}
        for key in ("delivery", "scope", "copyLanguage", "designDirection", "componentLibraryStrategy", "writeMethod"):
            if not gate.get(key):
                errors.append(f"gateCard.{key} missing in task state")
        if state.get("lastCodifyRequest", {}).get("status") == "accepted":
            warnings.append("previous Codify request is still accepted/pending; verify it before final completion")

    if not args.guidelines:
        errors.append("get_codify_guidelines result has not been recorded")
    if not args.user_info:
        errors.append("get_user_info result has not been recorded")

    if args.html:
        if not args.html.exists():
            errors.append(f"HTML file missing: {args.html}")
        else:
            rc, payload, stderr = run_json([sys.executable, str(SCRIPT_DIR / "codify-html-lint.py"), str(args.html)])
            details["htmlLint"] = payload or {"stderr": stderr}
            if rc != 0:
                errors.append("codify-html-lint failed")
            if args.expected_language:
                rc, payload, stderr = run_json(
                    [
                        sys.executable,
                        str(SCRIPT_DIR / "codify-copy-lint.py"),
                        str(args.html),
                        "--expected",
                        args.expected_language,
                        "--mode",
                        args.copy_mode,
                    ]
                )
                details["copyLint"] = payload or {"stderr": stderr}
                if rc != 0:
                    errors.append("codify-copy-lint failed")
            if args.artifact_source:
                audit_cmd = [
                    sys.executable,
                    str(SCRIPT_DIR / "codify-artifact-audit.py"),
                    str(args.html),
                    "--source",
                    args.artifact_source,
                    "--goal",
                    args.goal,
                    "--expected-language",
                    args.expected_language or "custom",
                ]
                rc, payload, stderr = run_json(audit_cmd)
                details["artifactAudit"] = payload or {"stderr": stderr}
                if rc != 0:
                    errors.append("codify-artifact-audit failed")
                if payload and payload.get("warnings"):
                    warnings.extend([f"artifact audit: {item}" for item in payload["warnings"]])

    if args.component_strategy in {"remote-selected", "local-snapshot"} and not args.team_library_name:
        errors.append("component library strategy requires --team-library-name")
    if args.component_strategy == "pending":
        errors.append("component library strategy is still pending")

    return {
        "canWrite": not errors,
        "errors": errors,
        "warnings": warnings,
        "details": details,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-state", type=Path, default=Path(".codify/state/mastergo-task.json"))
    parser.add_argument("--html", type=Path)
    parser.add_argument("--expected-language", default="")
    parser.add_argument("--copy-mode", choices=["strict", "warning"], default="strict")
    parser.add_argument("--artifact-source", choices=["current-run", "mastergo-baseline", "user-provided", "historical"], default="")
    parser.add_argument("--goal", default="")
    parser.add_argument("--guidelines", action="store_true", help="Set after get_codify_guidelines has been run.")
    parser.add_argument("--user-info", action="store_true", help="Set after get_user_info has been run.")
    parser.add_argument(
        "--component-strategy",
        choices=["local-snapshot", "remote-selected", "declined", "unavailable", "pending"],
        default="pending",
    )
    parser.add_argument("--team-library-name", default="")
    args = parser.parse_args()
    result = preflight(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["canWrite"] else 1


if __name__ == "__main__":
    sys.exit(main())
