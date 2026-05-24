#!/usr/bin/env python3
"""Archive MasterGo verification evidence and summarize completion state."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE = Path(".codify/state.json")
DEFAULT_TASK = Path(".codify/state/mastergo-task.json")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record(args: argparse.Namespace) -> int:
    state = load(args.state)
    evidence = {
        "type": args.type,
        "mode": args.mode,
        "at": now_iso(),
        "unitId": args.unit_id,
        "passed": args.passed,
        "getDesignDiff": args.diff,
        "screenshot": args.screenshot,
        "copyLanguage": args.copy_language,
        "componentRatio": args.component_ratio,
        "apiTraceReportShown": args.api_trace_report_shown,
        "notes": args.note,
    }
    state["lastVerification"] = evidence
    state.setdefault("verifications", []).append(evidence)
    save(args.state, state)

    if args.task.exists() and args.unit_id:
        task = load(args.task)
        for unit in task.get("units", []):
            if unit.get("id") == args.unit_id:
                unit.setdefault("verification", {}).update(evidence)
                if args.passed:
                    unit["status"] = "verified"
        task["updatedAt"] = now_iso()
        save(args.task, task)

    print(json.dumps({"ok": True, "verification": evidence}, ensure_ascii=False, indent=2))
    return 0


def summary(args: argparse.Namespace) -> int:
    state = load(args.state)
    task = load(args.task) if args.task.exists() else {}
    units = task.get("units", [])
    open_units = [unit for unit in units if unit.get("status") not in {"verified", "blocked"}]
    pending_request = task.get("lastCodifyRequest", {}).get("status") == "accepted"
    result = {
        "taskId": task.get("taskId"),
        "lastVerification": state.get("lastVerification"),
        "openUnits": open_units,
        "pendingAcceptedRequest": pending_request,
        "canClaimComplete": bool(units) and not open_units and not pending_request,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["canClaimComplete"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--task", type=Path, default=DEFAULT_TASK)
    sub = parser.add_subparsers(dest="command", required=True)

    p_record = sub.add_parser("record")
    p_record.add_argument("--type", choices=["design", "implementation", "update"], required=True)
    p_record.add_argument("--mode", default="")
    p_record.add_argument("--unit-id", default="")
    p_record.add_argument("--passed", action="store_true")
    p_record.add_argument("--diff", default="")
    p_record.add_argument("--screenshot", default="")
    p_record.add_argument("--copy-language", default="")
    p_record.add_argument("--component-ratio", default="")
    p_record.add_argument("--api-trace-report-shown", action="store_true")
    p_record.add_argument("--note", default="")
    p_record.set_defaults(func=record)

    p_summary = sub.add_parser("summary")
    p_summary.set_defaults(func=summary)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
