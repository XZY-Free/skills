#!/usr/bin/env python3
"""Manage the per-project OPC delivery stage ledger."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_STATE = Path(".opc/state/opc-task.json")
PHASES = ("intake", "requirements", "solution", "ui-design", "implementation", "deployment", "calibration")
STATUSES = ("pending", "done", "skipped", "blocked")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def phase_record(
    status: str = "pending",
    artifact: str = "",
    evidence: str = "",
    note: str = "",
    next_action: str = "",
) -> dict:
    record = {
        "status": status,
        "artifact": artifact,
        "evidence": evidence,
        "nextAction": next_action,
        "notes": [],
        "updatedAt": now(),
    }
    if note:
        record["notes"].append({"at": now(), "text": note})
    return record


def next_phase(phases: dict) -> str:
    for phase in PHASES:
        status = phases.get(phase, {}).get("status", "pending")
        if status in ("pending", "blocked"):
            return phase
    return "complete"


def default_next_action(phase: str, status: str, resume_phase: str) -> str:
    if status == "blocked":
        return f"Resolve blocker in {phase}, then continue the OPC chain."
    if status == "pending":
        return f"Continue {phase}."
    if resume_phase == "complete":
        return "Run completion validation and report final evidence."
    return f"Continue with {resume_phase}."


def load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"state not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updatedAt"] = now()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cmd_init(args: argparse.Namespace) -> int:
    phases = {phase: phase_record() for phase in PHASES}
    phases["intake"] = phase_record(
        status="done",
        artifact=args.artifact or "OPC Stage Card",
        evidence=args.evidence or "Stage Card initialized",
    )
    data = {
        "version": 1,
        "taskId": args.task_id or f"opc-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "goal": args.goal,
        "delivery": args.delivery,
        "acceptance": args.acceptance,
        "currentPhase": next_phase(phases),
        "nextAction": args.next_action or "Continue with requirements.",
        "createdAt": now(),
        "updatedAt": now(),
        "history": [
            {
                "at": now(),
                "phase": "intake",
                "status": "done",
                "artifact": phases["intake"]["artifact"],
                "evidence": phases["intake"]["evidence"],
                "nextAction": args.next_action or "Continue with requirements.",
            }
        ],
        "phases": phases,
    }
    save(args.path, data)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def cmd_mark(args: argparse.Namespace) -> int:
    data = load(args.path)
    phases = data.setdefault("phases", {})
    record = phases.get(args.phase, phase_record())
    record["status"] = args.status
    if args.artifact:
        record["artifact"] = args.artifact
    if args.evidence:
        record["evidence"] = args.evidence
    resume_phase = next_phase({**phases, args.phase: record})
    next_action = args.next_action or default_next_action(args.phase, args.status, resume_phase)
    record["nextAction"] = next_action
    if args.note:
        record.setdefault("notes", []).append({"at": now(), "text": args.note})
    record["updatedAt"] = now()
    phases[args.phase] = record
    data["currentPhase"] = resume_phase
    data["nextAction"] = next_action
    data.setdefault("history", []).append(
        {
            "at": now(),
            "phase": args.phase,
            "status": args.status,
            "artifact": record.get("artifact", ""),
            "evidence": record.get("evidence", ""),
            "note": args.note,
            "nextAction": next_action,
        }
    )
    save(args.path, data)
    print(f"{args.phase}: {args.status}")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    data = load(args.path)
    print(f"taskId: {data.get('taskId', '')}")
    print(f"goal: {data.get('goal', '')}")
    print(f"currentPhase: {data.get('currentPhase') or next_phase(data.get('phases', {}))}")
    print(f"nextAction: {data.get('nextAction') or '-'}")
    for phase, record in data.get("phases", {}).items():
        artifact = record.get("artifact") or "-"
        evidence = record.get("evidence") or "-"
        next_action = record.get("nextAction") or "-"
        print(
            f"- {phase}: {record.get('status', 'pending')} | artifact={artifact} "
            f"| evidence={evidence} | next={next_action}"
        )
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    data = load(args.path)
    phases = data.get("phases", {})
    phase = data.get("currentPhase") or next_phase(phases)
    print(f"taskId: {data.get('taskId', '')}")
    print(f"goal: {data.get('goal', '')}")
    print(f"delivery: {data.get('delivery', '')}")
    print(f"acceptance: {data.get('acceptance', '')}")
    print(f"resumePhase: {phase}")
    print(f"nextAction: {data.get('nextAction') or '-'}")
    if phase in phases:
        record = phases[phase]
        print(f"resumeStatus: {record.get('status', 'pending')}")
        print(f"resumeArtifact: {record.get('artifact') or '-'}")
        print(f"resumeEvidence: {record.get('evidence') or '-'}")
        print(f"resumeNextAction: {record.get('nextAction') or data.get('nextAction') or '-'}")
    print("recentHistory:")
    for item in data.get("history", [])[-5:]:
        note = item.get("note") or ""
        print(
            f"- {item.get('at', '')} | {item.get('phase', '')}: {item.get('status', '')} "
            f"| artifact={item.get('artifact') or '-'} | evidence={item.get('evidence') or '-'}"
            + (f" | next={item.get('nextAction')}" if item.get("nextAction") else "")
            + (f" | note={note}" if note else "")
        )
    return 0


def cmd_note(args: argparse.Namespace) -> int:
    data = load(args.path)
    phases = data.setdefault("phases", {})
    record = phases.get(args.phase, phase_record())
    if args.artifact:
        record["artifact"] = args.artifact
    if args.evidence:
        record["evidence"] = args.evidence
    if args.next_action:
        record["nextAction"] = args.next_action
        data["nextAction"] = args.next_action
    record.setdefault("notes", []).append({"at": now(), "text": args.text})
    record["updatedAt"] = now()
    phases[args.phase] = record
    data["currentPhase"] = data.get("currentPhase") or next_phase(phases)
    data.setdefault("history", []).append(
        {
            "at": now(),
            "phase": args.phase,
            "status": record.get("status", "pending"),
            "artifact": record.get("artifact", ""),
            "evidence": record.get("evidence", ""),
            "note": args.text,
            "nextAction": record.get("nextAction", ""),
        }
    )
    save(args.path, data)
    print(f"{args.phase}: noted")
    return 0


def validate_completion(data: dict) -> list[str]:
    errors: list[str] = []
    phases = data.get("phases", {})
    for phase in PHASES:
        if phase not in phases:
            errors.append(f"missing phase: {phase}")
            continue
        record = phases[phase]
        status = record.get("status", "pending")
        if status not in ("done", "skipped"):
            errors.append(f"{phase} is {status}, expected done or skipped")
        if status == "done" and not (record.get("artifact") or record.get("evidence")):
            errors.append(f"{phase} is done but has no artifact/evidence")
        if status == "skipped" and not (record.get("evidence") or record.get("notes")):
            errors.append(f"{phase} is skipped but has no reason")
    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    data = load(args.path)
    errors = validate_completion(data) if args.for_completion else []
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("opc task state OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=DEFAULT_STATE)
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create an OPC delivery stage ledger.")
    p_init.add_argument("--task-id", default="")
    p_init.add_argument("--goal", required=True)
    p_init.add_argument("--delivery", required=True)
    p_init.add_argument("--acceptance", required=True)
    p_init.add_argument("--artifact", default="")
    p_init.add_argument("--evidence", default="")
    p_init.add_argument("--next-action", default="")
    p_init.set_defaults(func=cmd_init)

    p_mark = sub.add_parser("mark", help="Mark a phase status.")
    p_mark.add_argument("phase")
    p_mark.add_argument("status", choices=STATUSES)
    p_mark.add_argument("--artifact", default="")
    p_mark.add_argument("--evidence", default="")
    p_mark.add_argument("--note", default="")
    p_mark.add_argument("--next-action", default="")
    p_mark.set_defaults(func=cmd_mark)

    p_summary = sub.add_parser("summary", help="Print a compact phase summary.")
    p_summary.set_defaults(func=cmd_summary)

    p_resume = sub.add_parser("resume", help="Print the next resumable phase and recent history.")
    p_resume.set_defaults(func=cmd_resume)

    p_note = sub.add_parser("note", help="Append a progress note without closing a phase.")
    p_note.add_argument("--phase", required=True)
    p_note.add_argument("--text", required=True)
    p_note.add_argument("--artifact", default="")
    p_note.add_argument("--evidence", default="")
    p_note.add_argument("--next-action", default="")
    p_note.set_defaults(func=cmd_note)

    p_validate = sub.add_parser("validate", help="Validate the ledger.")
    p_validate.add_argument("--for-completion", action="store_true")
    p_validate.set_defaults(func=cmd_validate)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
