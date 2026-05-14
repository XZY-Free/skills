#!/usr/bin/env python3
"""Generate a BENCHMARK.md scaffold from a skill's evals.json.

Usage:
  python3 scripts/run-evals.py <skill-name>            # prints BENCHMARK.md to stdout
  python3 scripts/run-evals.py <skill-name> --write     # writes <skill>/BENCHMARK.md

Workflow:
  1. Run this script once to scaffold BENCHMARK.md
  2. Open <skill-name>/BENCHMARK.md
  3. For each eval case, copy the prompt, paste into your AI coding agent
     (Claude Code / Codex / Cursor), run it, and fill in:
       - Pass? (✅ / ⚠️ / ❌)
       - Duration
       - Notes / observed deviations from expected_output
  4. Commit the filled BENCHMARK.md so the public sees real numbers

Why not fully automate?
  Some eval cases require real product tokens, MCP responses, deployment
  accounts, or project-specific artifacts, which can't be exercised in CI.
  This script lowers the friction enough that a maintainer can run the suite
  in a single sitting.

Exit codes:
  0 = scaffold generated successfully
  1 = skill or evals.json not found / invalid
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_evals(skill: str) -> tuple[Path, dict]:
    skill_dir = ROOT / skill
    if not skill_dir.is_dir():
        print(f"error: skill directory not found: {skill_dir}", file=sys.stderr)
        sys.exit(1)
    evals_path = skill_dir / "evals" / "evals.json"
    if not evals_path.is_file():
        print(f"error: evals.json not found: {evals_path}", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(evals_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {evals_path}: {exc}", file=sys.stderr)
        sys.exit(1)
    return skill_dir, data


def render(skill: str, data: dict) -> str:
    evals = data.get("evals", [])
    today = datetime.now().strftime("%Y-%m-%d")

    lines: list[str] = []
    lines.append(f"# `{skill}` Benchmark\n")
    lines.append(
        f"本表为 `{skill}` skill 在 [`evals/evals.json`](evals/evals.json) 上的实测结果。\n"
    )
    lines.append("> 生成时间: " + today + "  \n")
    lines.append("> 上次完整复测: _待填_  \n")
    lines.append(
        "> 用 `python3 ../scripts/run-evals.py " + skill + " --write` 可重新生成此文件骨架。\n"
    )
    lines.append("\n---\n")

    # Summary
    lines.append("## 汇总\n")
    lines.append(
        "| 指标 | 数值 |\n"
        "|---|---|\n"
        f"| 测试用例数 | {len(evals)} |\n"
        "| 通过率 (✅) | _待填_ |\n"
        "| 平均耗时 | _待填_ |\n"
        "| 复测人 | _待填_ |\n"
        "| 复测客户端 | Claude Code / Codex / Cursor (选一) |\n"
        "| 复测日期 | _待填_ |\n"
    )
    lines.append("\n图例: ✅ 完全通过 · ⚠️ 部分通过(关键步骤对但有偏差) · ❌ 不通过\n")
    lines.append("\n---\n")

    # Per-case
    lines.append("## 用例详情\n")
    for ev in evals:
        eid = ev.get("id", "?")
        name = ev.get("name", "(no name)")
        prompt = ev.get("prompt", "").rstrip()
        expected = ev.get("expected_output", "").rstrip()

        lines.append(f"### #{eid} · `{name}`\n")
        lines.append("**Prompt** (复制到 agent):\n")
        lines.append("```\n" + prompt + "\n```\n")
        lines.append("**期望行为**:\n")
        lines.append("> " + expected.replace("\n", "\n> ") + "\n")
        lines.append("**实测**:\n")
        lines.append(
            "- 结果: _✅ / ⚠️ / ❌ 待填_\n"
            "- 耗时: _待填_(从 prompt 提交到 skill 报『完成』为止)\n"
            "- 客户端: _Claude Code / Codex / Cursor_\n"
            "- 偏差点(如果有): _待填_\n"
            "- 链接到对话片段 / 截图(可选): _待填_\n"
        )
        lines.append("\n---\n")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate BENCHMARK.md scaffold")
    parser.add_argument("skill", help="Skill name (top-level directory)")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write to <skill>/BENCHMARK.md instead of printing to stdout",
    )
    args = parser.parse_args()

    skill_dir, data = load_evals(args.skill)
    content = render(args.skill, data)

    if args.write:
        target = skill_dir / "BENCHMARK.md"
        target.write_text(content, encoding="utf-8")
        print(f"✅ wrote {target.relative_to(ROOT)}")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
