#!/usr/bin/env python3
"""Validate every <skill>/evals/evals.json conforms to the expected shape.

Expected schema:
  {
    "skill_name": str,                 # must match the parent skill directory
    "evals": [
      {
        "id": int,
        "name": str,
        "prompt": str,
        "expected_output": str,
        "files": list                  # may be empty
      },
      ...
    ],
    "negative_evals": [                # optional but validated when present
      {
        "id": int,
        "name": str,
        "prompt": str,
        "expected_behavior": str,
        "should_trigger": bool
      },
      ...
    ]
  }

Exit codes:
  0 = all evals.json valid
  1 = at least one invalid
  2 = unexpected error
"""

from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", "node_modules", ".omc", ".idea", "dist", "build"}

REQUIRED_TOP = {"skill_name", "evals"}
REQUIRED_PER_EVAL = {"id", "name", "prompt", "expected_output", "files"}
REQUIRED_PER_NEGATIVE = {"id", "name", "prompt", "expected_behavior", "should_trigger"}


def resolve_eval_file(root: Path, value: str) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        direct = root / candidate
        if direct.exists():
            candidate = direct
        else:
            candidate = root / value / "evals" / "evals.json"
    if candidate.is_dir():
        candidate = candidate / "evals" / "evals.json"
    return candidate.resolve()


def iter_eval_files(root: Path, skills: list[str] | None = None) -> tuple[list[Path], list[str]]:
    if skills:
        files = [resolve_eval_file(root, skill) for skill in skills]
        missing = [str(file) for file in files if not file.is_file()]
        return [file for file in files if file.is_file()], [f"evals.json not found: {path}" for path in missing]

    files: list[Path] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name in EXCLUDE_DIRS:
            continue
        candidate = child / "evals" / "evals.json"
        if candidate.is_file():
            files.append(candidate)
    return files, []


def check(file: Path) -> list[str]:
    errs: list[str] = []
    skill_dir = file.parent.parent.name
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]
    except Exception as exc:
        return [f"unreadable: {exc}"]

    if not isinstance(data, dict):
        return ["top-level must be a JSON object"]

    missing_top = REQUIRED_TOP - data.keys()
    if missing_top:
        errs.append(f"missing top-level keys: {sorted(missing_top)}")
        return errs

    if not isinstance(data["skill_name"], str):
        errs.append("`skill_name` must be a string")
    elif data["skill_name"] != skill_dir:
        errs.append(f"`skill_name` is {data['skill_name']!r}, expected {skill_dir!r}")

    evals = data.get("evals")
    if not isinstance(evals, list):
        errs.append("`evals` must be a list")
        return errs

    seen_ids: set[int] = set()
    seen_names: set[str] = set()

    def check_common(ev: object, prefix: str, required: set[str], str_fields: tuple[str, ...]) -> None:
        if not isinstance(ev, dict):
            errs.append(f"{prefix}: must be an object")
            return
        missing = required - ev.keys()
        if missing:
            errs.append(f"{prefix}: missing keys {sorted(missing)}")
        if "id" in ev:
            if not isinstance(ev["id"], int):
                errs.append(f"{prefix}.id: must be int")
            elif ev["id"] in seen_ids:
                errs.append(f"{prefix}.id: duplicate id {ev['id']}")
            else:
                seen_ids.add(ev["id"])
        if "name" in ev and isinstance(ev["name"], str):
            if ev["name"] in seen_names:
                errs.append(f"{prefix}.name: duplicate name {ev['name']!r}")
            else:
                seen_names.add(ev["name"])
        for str_field in str_fields:
            if str_field in ev and not isinstance(ev[str_field], str):
                errs.append(f"{prefix}.{str_field}: must be string")
        if "checks" in ev:
            checks = ev["checks"]
            if not isinstance(checks, dict):
                errs.append(f"{prefix}.checks: must be object when present")
            else:
                for key in ("must_include", "must_not_include"):
                    if key in checks and (
                        not isinstance(checks[key], list)
                        or any(not isinstance(item, str) for item in checks[key])
                    ):
                        errs.append(f"{prefix}.checks.{key}: must be list[str]")

    for idx, ev in enumerate(evals):
        check_common(ev, f"evals[{idx}]", REQUIRED_PER_EVAL, ("name", "prompt", "expected_output"))
        if isinstance(ev, dict):
            if "files" in ev and not isinstance(ev["files"], list):
                errs.append(f"evals[{idx}].files: must be list")

    negative_evals = data.get("negative_evals", [])
    if negative_evals is None:
        negative_evals = []
    if not isinstance(negative_evals, list):
        errs.append("`negative_evals` must be a list when present")
        return errs
    for idx, ev in enumerate(negative_evals):
        check_common(
            ev,
            f"negative_evals[{idx}]",
            REQUIRED_PER_NEGATIVE,
            ("name", "prompt", "expected_behavior"),
        )
        if isinstance(ev, dict) and "should_trigger" in ev and not isinstance(ev["should_trigger"], bool):
            errs.append(f"negative_evals[{idx}].should_trigger: must be bool")

    return errs


def relative_to_root(path: Path, root: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=str(ROOT),
        help="Repository root containing skill directories (default: this repository).",
    )
    parser.add_argument(
        "--skill",
        action="append",
        default=None,
        help="Skill name, skill directory, or evals.json path to validate. Repeatable.",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    files, setup_errors = iter_eval_files(root, args.skill)
    if setup_errors:
        for error in setup_errors:
            print(f"✗ {error}")
        return 1
    if not files:
        print("no evals.json files found (skip)")
        return 0

    failed = 0
    for f in files:
        rel = relative_to_root(f, root)
        errs = check(f)
        if errs:
            failed += 1
            print(f"✗ {rel}")
            for e in errs:
                print(f"    {e}")
        else:
            print(f"✓ {rel}")

    if failed:
        print(f"\n❌ {failed}/{len(files)} evals.json file(s) invalid")
        return 1
    print(f"\n✅ evals.json check OK ({len(files)} files)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # pragma: no cover
        print(f"check-evals.py crashed: {exc}", file=sys.stderr)
        sys.exit(2)
