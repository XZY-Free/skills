#!/usr/bin/env python3
"""Manage the per-project MasterGo task ledger used by the skill."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE = Path(".codify/state/mastergo-task.json")
VALID_UNIT_STATUS = {"planned", "generated", "pushed", "verified", "blocked"}
VALID_REQUEST_STATUS = {"accepted", "verified", "failed", "unknown"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"state file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updatedAt"] = now_iso()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def unit_from_arg(raw: str) -> dict[str, Any]:
    parts = [part.strip() for part in raw.split(":", 2)]
    if len(parts) == 1:
        unit_id = parts[0]
        title = parts[0]
        unit_type = "page"
    elif len(parts) == 2:
        unit_id, title = parts
        unit_type = "page"
    else:
        unit_id, title, unit_type = parts
    if not unit_id:
        raise SystemExit(f"invalid unit value: {raw!r}")
    return {
        "id": unit_id,
        "title": title or unit_id,
        "type": unit_type or "page",
        "status": "planned",
        "localHtml": "",
        "mastergoNodeId": "",
        "verification": {},
    }


def init(args: argparse.Namespace) -> int:
    units = [unit_from_arg(raw) for raw in args.unit]
    data: dict[str, Any] = {
        "taskId": args.task_id or f"mastergo-design-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
        "originalUserGoal": args.goal,
        "deliveryType": args.delivery_type,
        "gateCard": {
            "delivery": args.delivery,
            "scope": args.scope,
            "copyLanguage": args.copy_language,
            "designDirection": args.design_direction,
            "componentLibraryStrategy": args.component_library,
            "writeMethod": args.write_method,
            "verification": args.verification,
        },
        "copyLanguage": {
            "mode": args.copy_language,
            "allowedTerms": [
                "MasterGo",
                "Codify",
                "AI",
                "Agent",
                "API",
                "MCP",
                "D2C",
                "SLA",
                "SSO",
                "RBAC",
                "AgentOps",
            ],
        },
        "designDirection": {
            "status": args.design_status,
            "summary": args.design_direction,
        },
        "componentLibrary": {
            "status": args.component_library,
            "teamLibraryName": args.team_library_name,
            "buildStrategy": args.build_strategy,
        },
        "units": units,
        "lastCodifyRequest": {
            "requestId": "",
            "status": "unknown",
        },
        "updates": [],
    }
    save(args.state, data)
    print(json.dumps({"ok": True, "state": str(args.state), "units": len(units)}, ensure_ascii=False, indent=2))
    return 0


def list_units(args: argparse.Namespace) -> int:
    data = load(args.state)
    rows = [
        {
            "id": unit.get("id"),
            "title": unit.get("title"),
            "type": unit.get("type"),
            "status": unit.get("status"),
            "mastergoNodeId": unit.get("mastergoNodeId", ""),
        }
        for unit in data.get("units", [])
    ]
    print(json.dumps({"taskId": data.get("taskId"), "units": rows}, ensure_ascii=False, indent=2))
    return 0


def find_unit(data: dict[str, Any], unit_id: str) -> dict[str, Any]:
    for unit in data.get("units", []):
        if unit.get("id") == unit_id:
            return unit
    raise SystemExit(f"unknown unit id: {unit_id}")


def mark(args: argparse.Namespace) -> int:
    if args.status not in VALID_UNIT_STATUS:
        raise SystemExit(f"invalid status {args.status!r}; expected one of {sorted(VALID_UNIT_STATUS)}")
    data = load(args.state)
    unit = find_unit(data, args.unit_id)
    unit["status"] = args.status
    if args.local_html:
        unit["localHtml"] = args.local_html
    if args.mastergo_node_id:
        unit["mastergoNodeId"] = args.mastergo_node_id
    if args.note:
        unit.setdefault("notes", []).append({"at": now_iso(), "text": args.note})
    save(args.state, data)
    print(json.dumps({"ok": True, "unit": unit}, ensure_ascii=False, indent=2))
    return 0


def request(args: argparse.Namespace) -> int:
    if args.status not in VALID_REQUEST_STATUS:
        raise SystemExit(f"invalid request status {args.status!r}; expected one of {sorted(VALID_REQUEST_STATUS)}")
    data = load(args.state)
    data["lastCodifyRequest"] = {
        "requestId": args.request_id,
        "status": args.status,
        "at": now_iso(),
    }
    save(args.state, data)
    print(json.dumps({"ok": True, "lastCodifyRequest": data["lastCodifyRequest"]}, ensure_ascii=False, indent=2))
    return 0


def resume(args: argparse.Namespace) -> int:
    data = load(args.state)
    remaining = [
        unit
        for unit in data.get("units", [])
        if unit.get("status") not in {"verified", "blocked"}
    ]
    accepted = data.get("lastCodifyRequest", {}).get("status") == "accepted"
    print(
        json.dumps(
            {
                "taskId": data.get("taskId"),
                "originalUserGoal": data.get("originalUserGoal"),
                "gateCard": data.get("gateCard", {}),
                "remainingUnits": remaining,
                "lastCodifyRequest": data.get("lastCodifyRequest", {}),
                "resumeRequired": bool(remaining or accepted),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def validate(args: argparse.Namespace) -> int:
    data = load(args.state)
    errors: list[str] = []
    warnings: list[str] = []
    gate = data.get("gateCard") or {}
    required_gate = ["delivery", "scope", "copyLanguage", "designDirection", "componentLibraryStrategy", "writeMethod"]
    for key in required_gate:
        if not gate.get(key):
            errors.append(f"gateCard.{key} is required")
    units = data.get("units")
    if not isinstance(units, list) or not units:
        errors.append("at least one design unit is required")
    else:
        open_units = [unit for unit in units if unit.get("status") not in {"verified", "blocked"}]
        if args.for_completion and open_units:
            errors.append(f"unclosed design units: {[unit.get('id') for unit in open_units]}")
        if args.for_write and not any(unit.get("status") in {"planned", "generated"} for unit in units):
            warnings.append("no planned/generated unit remains for write")
    if data.get("lastCodifyRequest", {}).get("status") == "accepted" and args.for_completion:
        errors.append("last Codify request is accepted/pending, not verified")
    result = {"ok": not errors, "errors": errors, "warnings": warnings}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a MasterGo task ledger from a Gate Card.")
    p_init.add_argument("--goal", required=True)
    p_init.add_argument("--task-id")
    p_init.add_argument("--delivery-type", default="mastergo-design")
    p_init.add_argument("--delivery", default="MasterGo canvas design")
    p_init.add_argument("--scope", required=True)
    p_init.add_argument("--copy-language", required=True)
    p_init.add_argument("--design-direction", required=True)
    p_init.add_argument("--design-status", choices=["confirmed", "auto-decided", "pending"], default="pending")
    p_init.add_argument("--component-library", required=True)
    p_init.add_argument("--team-library-name", default="")
    p_init.add_argument("--build-strategy", choices=["full-components", "hybrid", "none", "pending"], default="pending")
    p_init.add_argument("--write-method", required=True)
    p_init.add_argument("--verification", default="get_design_diff + screenshot + copy lint + component ratio")
    p_init.add_argument("--unit", action="append", default=[], help="id[:title[:type]], repeatable")
    p_init.set_defaults(func=init)

    p_list = sub.add_parser("list", help="List design units.")
    p_list.set_defaults(func=list_units)

    p_mark = sub.add_parser("mark", help="Update one design unit.")
    p_mark.add_argument("unit_id")
    p_mark.add_argument("status")
    p_mark.add_argument("--local-html", default="")
    p_mark.add_argument("--mastergo-node-id", default="")
    p_mark.add_argument("--note", default="")
    p_mark.set_defaults(func=mark)

    p_request = sub.add_parser("request", help="Record the latest Codify write request.")
    p_request.add_argument("--request-id", required=True)
    p_request.add_argument("--status", required=True)
    p_request.set_defaults(func=request)

    p_resume = sub.add_parser("resume", help="Print a restart/reconnect resume summary.")
    p_resume.set_defaults(func=resume)

    p_validate = sub.add_parser("validate", help="Validate the ledger for write or completion.")
    p_validate.add_argument("--for-write", action="store_true")
    p_validate.add_argument("--for-completion", action="store_true")
    p_validate.set_defaults(func=validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
