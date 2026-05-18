#!/usr/bin/env python3
"""Lint a turn's hand-off message against OPC 收尾契约.

读 hand-off 文本 (stdin 或 --file), 检查它符合 references/handoff-contract.md
要求的五段结构: [已完成] + [证据] + [不确定项归类] + 显式下一步.
需要用户拍板时, 允许当前 AI 宿主的原生结构化选择/确认交互说明; 文本 A/B/C 只是降级格式.

退出码:
  0  通过
  1  收尾契约违规
  2  调用错误 (文件不存在 / 输入为空)

用法:
  echo "<handoff text>" | python scripts/handoff-lint.py
  python scripts/handoff-lint.py --file .opc/<phase>/last-handoff.md
  python scripts/handoff-lint.py --file .opc/<phase>/last-handoff.md --phase implementation

预期触发点: AI 在跑 `opc-task-state.py mark <phase> done` 之前必须先跑这个 lint.
lint 不通过则禁止 mark done, 必须重写 hand-off.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS: dict[str, tuple[str, str]] = {
    "completed": (
        r"\[已完成\]|^已完成[:：]|^✅\s*已完成",
        "缺少 [已完成] 段 — 列出本轮做了哪些具体事 (产物路径 / commit / 截图)",
    ),
    "evidence": (
        r"\[证据\]|^证据[:：]",
        "缺少 [证据] 段 — 给文件路径 / 命令退出码 / 测试通过 / 截图 / URL",
    ),
    "uncertainty_or_done": (
        r"\[不确定项|\[需要你拍板|\[结构化输入|\[选择框|\[卡住|\[硬阻塞|\[等你|不确定项 \+ 我的处理|没有未决项",
        "缺少不确定项归类段 ([不确定项 + 我的处理] / [需要你拍板] / [结构化输入] / [卡住]); 若本轮真的全部收敛, 显式写 '没有未决项'",
    ),
    "next_step": (
        r"我现在做|我现在进入|我下一步|等你在选择框|等你提交选择框|等你在原生交互|等你提交原生交互|等你通过结构化输入|等你回|等你选|等你补|卡住[,，]\s*缺|下一步[:：]",
        "缺少显式下一步 — 必须写 '我现在做 X' / '我现在进入 X' / '等你在原生交互提交' / '等你回 A/B/C' / '卡住, 缺 X' 之一",
    ),
}

# 反模式: 末尾段附近出现 '剩余风险' 但没有跟随行动短语
ACTION_TOKENS = (
    "我现在",
    "我下一步",
    "我已默认",
    "我已 mitigation",
    "我会立即",
    "等你在选择框",
    "等你提交选择框",
    "等你在原生交互",
    "等你提交原生交互",
    "等你通过结构化输入",
    "等你回",
    "等你选",
    "等你补",
    "卡住",
)

OPEN_ENDED_TOKENS = (
    r"你看呢[?？]?\s*$",
    r"你定吧[?？]?\s*$",
    r"看你的\s*$",
    r"看情况\s*$",
    r"自己决定\s*$",
)

STRUCTURED_DECISION_TOKENS = (
    "结构化输入",
    "选择框",
    "request_user_input",
    "Claude Code",
    "confirm/select",
    "confirm-select",
    "prompt 工具",
    "宿主原生",
    "原生结构化",
    "原生选择",
    "原生确认",
    "OMX question",
    "question bridge",
    "真实选择框",
    "native structured input",
    "native decision UI",
)


def check_required(text: str) -> list[str]:
    errors: list[str] = []
    for key, (pattern, message) in REQUIRED_SECTIONS.items():
        if not re.search(pattern, text, re.MULTILINE):
            errors.append(f"[{key}] {message}")
    return errors


def check_residual_risk_anti_pattern(text: str) -> list[str]:
    """检测末尾 ~400 字符内出现'剩余风险' 但未跟随行动短语."""
    tail = text[-500:]
    if "剩余风险" not in tail:
        return []
    if any(token in tail for token in ACTION_TOKENS):
        return []
    return [
        "[anti] 末尾段出现 '剩余风险' 但没有跟随 '我现在做 X' / '等你回' / '卡住, 缺 X' "
        "等行动短语 — 这是 handoff-contract.md 禁止的反模式"
    ]


def check_open_ended(text: str) -> list[str]:
    errors: list[str] = []
    for pattern in OPEN_ENDED_TOKENS:
        if re.search(pattern, text, re.MULTILINE):
            errors.append(
                f"[anti] 出现开放式问句 (匹配 /{pattern}/) — 必须替换成宿主原生结构化选择/确认交互, 或文本降级的 'A/B/C 选一个 + 默认'"
            )
    return errors


def check_phase_specific(text: str, phase: str) -> list[str]:
    """执行阶段必须有可执行证据."""
    errors: list[str] = []
    if phase in ("implementation", "verification", "deployment"):
        evidence_tokens = (
            "pass",
            "passed",
            "通过",
            "退出码 0",
            "0 errors",
            "0 failures",
            "exit 0",
            "HTTP 200",
            "screenshot",
            "截图",
            "URL",
            "健康检查",
            "preview URL",
            "build success",
            "构建成功",
        )
        if not any(token in text for token in evidence_tokens):
            errors.append(
                f"[{phase}] 执行阶段必须有可执行证据 (测试通过 / 退出码 0 / HTTP 200 / 截图 / preview URL)"
            )
    return errors


def check_decision_block(text: str) -> list[str]:
    if not any(marker in text for marker in ("[需要你拍板]", "[结构化输入]", "[选择框]")):
        return []

    match = re.search(r"\[(?:需要你拍板|结构化输入|选择框)\](.*?)(?:\n\[|$)", text, re.DOTALL)
    section = match.group(1) if match else text
    errors: list[str] = []

    if any(token in section for token in STRUCTURED_DECISION_TOKENS) or any(marker in text for marker in ("[结构化输入]", "[选择框]")):
        if not re.search(r"默认|推荐", section):
            errors.append("[decision] 宿主原生结构化交互仍必须说明默认或推荐选项")
        if not re.search(r"自定义|Other|type something", section):
            errors.append("[decision] 宿主原生结构化交互必须说明含自定义 / Other 入口, 或降级文本里保留 type something")
        return errors

    if not re.search(r"(^|\n)\s*[-*]?\s*A[.．、:：]", section):
        errors.append("[decision] [需要你拍板] 段必须使用宿主原生结构化选择/确认交互, 或在降级文本里给 A/B/C 这类具体选项")
    if not re.search(r"默认|推荐", section):
        errors.append("[decision] [需要你拍板] 段必须标明默认或推荐选项")
    if "自定义" not in section and "type something" not in section:
        errors.append("[decision] [需要你拍板] 段必须保留自定义 / type something 入口")
    return errors


def lint(text: str, phase: str = "") -> list[str]:
    errors: list[str] = []
    errors.extend(check_required(text))
    errors.extend(check_residual_risk_anti_pattern(text))
    errors.extend(check_open_ended(text))
    errors.extend(check_decision_block(text))
    if phase:
        errors.extend(check_phase_specific(text, phase))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, help="读 hand-off 文本的路径; 不给则读 stdin")
    parser.add_argument(
        "--phase",
        default="",
        choices=("", "intake", "requirements", "solution", "ui-design", "implementation", "verification", "deployment", "calibration"),
        help="可选: 当前阶段名, 用于阶段特定检查",
    )
    args = parser.parse_args()

    if args.file:
        if not args.file.exists():
            print(f"ERROR: file not found: {args.file}", file=sys.stderr)
            return 2
        text = args.file.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("ERROR: empty handoff text", file=sys.stderr)
        return 2

    errors = lint(text, phase=args.phase)

    if errors:
        print("❌ 收尾契约校验未通过:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print("回 references/handoff-contract.md 修正后重跑。", file=sys.stderr)
        print("不要绕过 lint 直接 mark done。", file=sys.stderr)
        return 1

    print("✅ 收尾契约 OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
