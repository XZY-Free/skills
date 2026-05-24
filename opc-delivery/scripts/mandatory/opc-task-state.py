#!/usr/bin/env python3
"""Manage the per-project OPC delivery stage ledger."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_STATE = Path(".opc/state/opc-task.json")
DEFAULT_CONTINUATION = Path(".opc/implementation/continuation.md")
PHASES = (
    "intake",
    "requirements",
    "solution",
    "ui-design",
    "implementation-plan",
    "implementation",
    "verification",
    "deployment",
    "calibration",
)
STATUSES = ("pending", "done", "skipped", "blocked")
PHASE_LABELS = {
    "intake": "理解目标",
    "requirements": "整理需求",
    "solution": "确定做法",
    "ui-design": "设计界面",
    "implementation-plan": "拆开发计划",
    "implementation": "做出可用版本",
    "verification": "检查能不能用",
    "deployment": "提供访问方式",
    "calibration": "复盘校准",
    "complete": "交付完成",
}


def phase_label(phase: str) -> str:
    return PHASE_LABELS.get(phase, phase.replace("-", " "))


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
        return f"先处理{phase_label(phase)}里的阻塞，再继续交付链路。"
    if status == "pending":
        return f"继续推进{phase_label(phase)}。"
    if resume_phase == "complete":
        return "运行完成校验并汇报最终证据。"
    return f"继续推进{phase_label(resume_phase)}。"


def load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"state not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if normalize_phases(data):
        save(path, data)
    return data


def normalize_phases(data: dict) -> bool:
    """Normalize older ledgers that predate the implementation-plan phase."""
    phases = data.setdefault("phases", {})
    had_implementation_plan = "implementation-plan" in phases
    changed = False
    ordered: dict[str, dict] = {}
    for phase in PHASES:
        if phase in phases:
            ordered[phase] = phases[phase]
        elif phase == "implementation-plan" and "implementation" in phases and not had_implementation_plan:
            changed = True
            ordered[phase] = phase_record(
                status="skipped",
                evidence="legacy state before implementation-plan phase",
                note="Inserted for compatibility with ledgers created before implementation-plan existed.",
                next_action="继续按旧台账状态推进。",
            )
        else:
            changed = True
            ordered[phase] = phase_record()
    for phase, record in phases.items():
        if phase not in ordered:
            ordered[phase] = record
    if list(phases) != list(ordered):
        changed = True
    if phases is not ordered:
        data["phases"] = ordered
    if not data.get("currentPhase") or data.get("currentPhase") not in ordered:
        data["currentPhase"] = next_phase(ordered)
        changed = True
    return changed


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
        "nextAction": args.next_action or "继续整理需求。",
        "createdAt": now(),
        "updatedAt": now(),
        "history": [
            {
                "at": now(),
                "phase": "intake",
                "status": "done",
                "artifact": phases["intake"]["artifact"],
                "evidence": phases["intake"]["evidence"],
                "nextAction": args.next_action or "继续整理需求。",
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
    if args.phase == "implementation" and args.status == "done":
        planning = phases.get("implementation-plan", {})
        planning_status = planning.get("status", "pending")
        has_skip_reason = bool(planning.get("evidence") or planning.get("notes"))
        if planning_status != "done" and not (planning_status == "skipped" and has_skip_reason):
            print(
                "ERROR: implementation cannot be marked done before implementation-plan is done or explicitly skipped with a reason",
                file=sys.stderr,
            )
            return 1
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


def collect_done_labels(phases: dict) -> list[str]:
    labels: list[str] = []
    for phase, record in phases.items():
        status = record.get("status", "pending")
        if status == "done":
            labels.append(phase_label(phase))
        elif status == "skipped":
            labels.append(f"{phase_label(phase)}(已跳过)")
    return labels


def user_action_for(data: dict, phase: str) -> str:
    phases = data.get("phases", {})
    record = phases.get(phase, {})
    status = record.get("status", "pending")
    notes = "；".join(note.get("text", "") for note in record.get("notes", [])[-2:] if note.get("text"))
    next_action = record.get("nextAction") or data.get("nextAction") or ""
    combined = f"{notes} {next_action}".strip()
    blocker_tokens = (
        "token",
        "secret",
        "API key",
        "账号",
        "凭证",
        "权限",
        "服务器",
        "DATABASE_URL",
        "付费",
        "production",
        "选择框",
        "拍板",
    )
    if status == "blocked":
        return combined or "卡住了，需要补齐外部信息或权限后才能继续。"
    if any(token in combined for token in blocker_tokens):
        return combined
    return "暂时不需要你操作；我会按已确认的信息继续推进。"


def cmd_brief(args: argparse.Namespace) -> int:
    data = load(args.path)
    phases = data.get("phases", {})
    current = data.get("currentPhase") or next_phase(phases)
    done = collect_done_labels(phases)
    doing = "全部阶段已完成。" if current == "complete" else f"{phase_label(current)}。"
    print(f"目标: {data.get('goal', '') or '-'}")
    print(f"已交付: {'、'.join(done) if done else '还没有完成的可交付项。'}")
    print(f"正在推进: {doing}")
    print(f"需要你做什么: {user_action_for(data, current)}")
    print(f"接下来: {data.get('nextAction') or '继续推进当前交付链路。'}")
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


def render_bullets(items: list[str]) -> list[str]:
    if not items:
        return ["- none"]
    return [f"- {item}" for item in items]


def cmd_checkpoint(args: argparse.Namespace) -> int:
    data = load(args.path)
    checkpoint_path = args.file
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = now()
    lines = [
        "# OPC Continuation Checkpoint",
        "",
        f"- updatedAt: {timestamp}",
        f"- taskId: {data.get('taskId', '')}",
        f"- goal: {data.get('goal', '')}",
        f"- phase: {args.phase}",
        f"- slice: {args.slice or 'none'}",
        f"- parallelLane: {args.lane or 'none'}",
        "",
        "## Summary",
        args.summary,
        "",
        "## Files Touched",
        *render_bullets(args.touched or []),
        "",
        "## Verification Run",
        *render_bullets(args.test or []),
        "",
        "## Blockers",
        *render_bullets(args.blocker or []),
        "",
        "## Next Action",
        args.next_action,
        "",
    ]
    checkpoint_path.write_text("\n".join(lines), encoding="utf-8")

    phases = data.setdefault("phases", {})
    record = phases.get(args.phase, phase_record())
    record["artifact"] = str(checkpoint_path)
    record["evidence"] = args.summary
    record["nextAction"] = args.next_action
    record.setdefault("notes", []).append({"at": timestamp, "text": f"context checkpoint: {args.summary}"})
    record["updatedAt"] = timestamp
    phases[args.phase] = record
    if args.phase in PHASES:
        data["currentPhase"] = args.phase
    data["nextAction"] = args.next_action
    data.setdefault("history", []).append(
        {
            "at": timestamp,
            "phase": args.phase,
            "status": record.get("status", "pending"),
            "artifact": str(checkpoint_path),
            "evidence": args.summary,
            "note": "context checkpoint",
            "nextAction": args.next_action,
        }
    )
    save(args.path, data)
    print(f"checkpoint: {checkpoint_path}")
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

    p_brief = sub.add_parser("brief", help="Print a user-facing result brief.")
    p_brief.set_defaults(func=cmd_brief)

    p_resume = sub.add_parser("resume", help="Print the next resumable phase and recent history.")
    p_resume.set_defaults(func=cmd_resume)

    p_note = sub.add_parser("note", help="Append a progress note without closing a phase.")
    p_note.add_argument("--phase", required=True)
    p_note.add_argument("--text", required=True)
    p_note.add_argument("--artifact", default="")
    p_note.add_argument("--evidence", default="")
    p_note.add_argument("--next-action", default="")
    p_note.set_defaults(func=cmd_note)

    p_checkpoint = sub.add_parser("checkpoint", help="Write a resumable implementation checkpoint.")
    p_checkpoint.add_argument("--phase", default="implementation")
    p_checkpoint.add_argument("--slice", default="")
    p_checkpoint.add_argument("--lane", default="")
    p_checkpoint.add_argument("--summary", required=True)
    p_checkpoint.add_argument("--touched", action="append", default=[])
    p_checkpoint.add_argument("--test", action="append", default=[])
    p_checkpoint.add_argument("--blocker", action="append", default=[])
    p_checkpoint.add_argument("--next-action", required=True)
    p_checkpoint.add_argument("--file", type=Path, default=DEFAULT_CONTINUATION)
    p_checkpoint.set_defaults(func=cmd_checkpoint)

    p_validate = sub.add_parser("validate", help="Validate the ledger.")
    p_validate.add_argument("--for-completion", action="store_true")
    p_validate.set_defaults(func=cmd_validate)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
