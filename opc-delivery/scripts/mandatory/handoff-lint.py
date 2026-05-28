#!/usr/bin/env python3
"""Lint a turn's hand-off message against OPC 收尾契约.

读 hand-off 文本 (stdin 或 --file), 检查它符合 references/handoff-contract.md
要求的结构化收尾: [已完成] + [证据] + [不确定项归类] + 显式下一步.
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
        r"\[已完成\]|^已完成[:：]|^✅\s*已完成|^已交付[:：]|^这轮交付[:：]|^目标[:：]",
        "缺少 [已完成] 段 — 列出本轮做了哪些具体事 (产物路径 / commit / 截图)",
    ),
    "evidence": (
        r"\[证据\]|^证据[:：]|^怎么检查[:：]|^检查方式[:：]|^正在推进[:：]",
        "缺少 [证据] 段 — 给文件路径 / 命令退出码 / 测试通过 / 截图 / URL",
    ),
    "status_marker": (
        r"\[继续下一\s*slice\]|\[继续下一阶段\]|\[需要你拍板\]|\[需要你提供\]|\[结构化输入\]|\[选择框\]|\[卡住\]|\[硬阻塞\]|\[不确定项|\[等你|没有未决项|任务完成|^接下来[:：]|^下一步[:：]|\[下一步\]",
        "缺少四态收尾标记 — 必须出现 [继续下一 slice] / [下一步] / [需要你提供] / [需要你拍板] / [卡住] 之一; 实现期 slice 间默认用 [继续下一 slice], 不要硬挤 [需要你拍板]",
    ),
    "next_step": (
        r"我现在做|我现在进入|我下一步|继续下一\s*slice|继续下一阶段|任务完成|\[需要你提供\]|\[需要你拍板\]|等你在选择框|等你提交选择框|等你在原生交互|等你提交原生交互|等你通过结构化输入|等你回|等你选|等你补|等你提供|你补好|卡住[,，]\s*缺|下一步[:：]|^接下来[:：]",
        "缺少显式下一步 — 必须写 '我现在做 X' / '继续下一 slice: X' / '任务完成' / '等你在原生交互提交' / '等你回 A/B/C' / '等你提供 X' / '卡住, 缺 X' 之一",
    ),
}

# 反模式: 末尾段附近出现 '剩余风险' 但没有跟随行动短语
ACTION_TOKENS = (
    "我现在",
    "我下一步",
    "我已默认",
    "我已 mitigation",
    "我会立即",
    "继续下一",
    "任务完成",
    "等你在选择框",
    "等你提交选择框",
    "等你在原生交互",
    "等你提交原生交互",
    "等你通过结构化输入",
    "等你回",
    "等你选",
    "等你补",
    "等你提供",
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

PHASE_IDS = (
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

INTERNAL_FIELD_TOKENS = ("artifact", "evidence", "nextAction", "currentPhase", "resumePhase")


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


def check_internal_progress_table(text: str) -> list[str]:
    errors: list[str] = []
    if re.search(r"OPC\s*[89]\s*阶段|阶段进度", text):
        errors.append("[progress] 普通用户输出禁止默认展示 OPC 阶段进度表; 改用 目标/已交付/正在推进/需要你做什么/接下来")
    if any(ch in text for ch in ("┌", "┬", "┐", "├", "┼", "┤", "└", "┴", "┘")) and sum(phase in text for phase in PHASE_IDS) >= 2:
        errors.append("[progress] 普通用户输出禁止展示包含内部 phase id 的 box-drawing 阶段表")
    if sum(phase in text for phase in PHASE_IDS) >= 3 and any(token in text for token in INTERNAL_FIELD_TOKENS):
        errors.append("[progress] 普通用户输出禁止混合 raw phase ids 和 artifact/evidence/nextAction; summary/resume 只用于内部恢复")
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


# === Productization Gate Checks (filesystem-level) ===


def is_productization_skipped(section_text: str) -> bool:
    """方案阶段产品姿态门禁是否标记为跳过。"""
    if not section_text:
        return False
    lowered = section_text.lower()
    for marker in ("本阶段跳过", "已 skipped", "skipped:", "status: skipped"):
        if marker.lower() in lowered:
            return True
    return False


def check_capability_table(section_text: str) -> list[str]:
    """从产品姿态门禁 section 抽升降级表, 验证 ≤5 硬卡和 ≥30% 软约束。"""
    errors: list[str] = []
    rows: list[tuple[str, str]] = []
    in_table = False
    for line in section_text.splitlines():
        if "曝光层级" in line and "|" in line:
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                in_table = False
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            if "---" in cells[0]:
                continue
            capability = cells[0]
            level = cells[1]
            if capability and level and "能力" not in capability:
                rows.append((capability, level))

    if not rows:
        errors.append(
            "[productization] 升降级表为空或解析不到 (需要含'能力'列和'曝光层级'列的 markdown 表)"
        )
        return errors

    high = sum(1 for _, lvl in rows if "高曝光" in lvl)
    low_or_ctx = sum(1 for _, lvl in rows if "低曝光" in lvl or "上下文" in lvl)
    total = len(rows)

    if high > 5:
        errors.append(f"[productization] 升降级表高曝光数 = {high}, 超过硬卡 ≤5")

    low_ratio = low_or_ctx / total if total else 0
    if low_ratio < 0.3 and "低占比理由" not in section_text:
        errors.append(
            f"[productization] 升降级表低曝光+仅上下文比例 = {low_ratio:.0%} (< 30%), "
            "必须写'低占比理由'说明 (软约束)"
        )

    return errors


def check_solution_productization_gate(source_dir: Path) -> list[str]:
    """方案阶段产品姿态门禁检查 (filesystem-level)。"""
    errors: list[str] = []

    design = source_dir / ".opc" / "solution" / "solution-design.md"
    if not design.is_file():
        return []  # 方案文档都没有就不是 productization 的问题

    design_text = design.read_text(encoding="utf-8", errors="ignore")

    if "## 产品姿态门禁" not in design_text:
        errors.append(
            "[productization] solution-design.md 缺 '## 产品姿态门禁' section "
            "(方案阶段强制; 不适用时显式写 'Status: skipped' + 原因)"
        )
        return errors

    section_match = re.search(
        r"##\s*产品姿态门禁(.*?)(?=\n## |\Z)",
        design_text,
        re.DOTALL,
    )
    section = section_match.group(1) if section_match else ""

    if is_productization_skipped(section):
        return []

    competitor = source_dir / ".opc" / "solution" / "competitor-survey.md"
    if not competitor.is_file() or not competitor.read_text(encoding="utf-8").strip():
        errors.append("[productization] 缺 .opc/solution/competitor-survey.md (或为空)")

    for required_sub in ("产品姿态", "首屏主信号", "升降级"):
        if required_sub not in section:
            errors.append(f"[productization] 产品姿态门禁 section 缺 '{required_sub}' 子部分")

    errors.extend(check_capability_table(section))

    return errors


def check_implementation_product_surface(source_dir: Path) -> list[str]:
    """实现阶段每个 UI slice 必填 Product Surface section (filesystem-level)。"""
    errors: list[str] = []

    # 方案阶段已 skip productization → 实现阶段也 skip
    design = source_dir / ".opc" / "solution" / "solution-design.md"
    if design.is_file():
        design_text = design.read_text(encoding="utf-8", errors="ignore")
        match = re.search(
            r"##\s*产品姿态门禁(.*?)(?=\n## |\Z)",
            design_text,
            re.DOTALL,
        )
        if match and is_productization_skipped(match.group(1)):
            return []

    slices_dir = source_dir / ".opc" / "implementation-plan" / "slices"
    if not slices_dir.is_dir():
        return []  # implementation-plan 不存在不在本检查范围

    for slice_file in sorted(slices_dir.glob("*.md")):
        content = slice_file.read_text(encoding="utf-8", errors="ignore")
        has_ui = "## UI" in content
        has_surface = "## Product Surface" in content
        if has_ui and not has_surface:
            errors.append(
                f"[productization] {slice_file.name} 有 ## UI 但缺 ## Product Surface section"
            )

    return errors


def is_project_docs_skipped(handoff_text: str) -> bool:
    """handoff 文本里显式标记 project-docs 跳过 → 不强卡。"""
    if not handoff_text:
        return False
    skip_markers = (
        "project-docs: skipped",
        "project-docs skipped",
        "11-project-docs: skipped",
        "项目文档跳过",
        "docs/ 跳过",
        "long-term docs skipped",
    )
    lowered = handoff_text.lower()
    return any(m.lower() in lowered for m in skip_markers)


def check_implementation_project_docs(source_dir: Path, handoff_text: str) -> list[str]:
    """实现完成前必须萃取项目长期文档. 见 references/11-project-docs.md.

    需求来源: 让别的开发者 / AI 工具接手时, 不破坏项目. .opc/ 下是过程证据,
    不是给接手者读的入口. 必须在 implementation 完成前萃取出 README + docs/.
    """
    if is_project_docs_skipped(handoff_text):
        return []

    errors: list[str] = []

    if not (source_dir / "README.md").is_file():
        errors.append(
            "[project-docs] 缺 README.md (项目入口) — implementation 完成前必产; "
            "需含 tech stack / quick start / project layout / 接手必读 / scripts. "
            "见 references/11-project-docs.md. 跳过须在 handoff 写 'project-docs: skipped' + 原因"
        )

    docs_dir = source_dir / "docs"
    if not docs_dir.is_dir():
        errors.append(
            "[project-docs] 缺 docs/ 目录 — implementation 完成前必产; "
            "至少含 ARCHITECTURE.md / DATA-MODEL.md / CONVENTIONS.md / decisions/. "
            "见 references/11-project-docs.md"
        )
    else:
        for required in ("ARCHITECTURE.md", "CONVENTIONS.md"):
            if not (docs_dir / required).is_file():
                errors.append(
                    f"[project-docs] 缺 docs/{required} — 从 .opc/implementation-plan/ 萃取(不复制, 去过程词)"
                )
        # DATA-MODEL.md 在无 DB 项目里可缺, 但项目有 prisma/schema.prisma 或 drizzle schema 时必产
        has_db_schema = (
            (source_dir / "prisma" / "schema.prisma").is_file()
            or any(source_dir.rglob("drizzle.config.*"))
        )
        if has_db_schema and not (docs_dir / "DATA-MODEL.md").is_file():
            errors.append(
                "[project-docs] 项目有 DB schema 但缺 docs/DATA-MODEL.md — "
                "把 .opc/implementation-plan/contracts.md 的 DB 段萃取成数据字典视图"
            )
        # decisions/ 只在有 ADR 时必产
        adr_source = source_dir / ".opc" / "implementation-plan" / "decisions"
        if adr_source.is_dir() and any(adr_source.glob("ADR-*.md")):
            if not (docs_dir / "decisions").is_dir():
                errors.append(
                    "[project-docs] .opc/implementation-plan/decisions/ 有 ADR 但 docs/decisions/ 不存在 — "
                    "把 ADR 挪到 docs/decisions/ (git mv), 让接手者看得到"
                )

    # 工具方言文件: 仅警告, 不 fail (项目可能本来就有, 脚本无法区分)
    vendor_files = ("AGENTS.md", "CLAUDE.md", ".cursorrules", ".windsurfrules", "GEMINI.md")
    new_vendor = [v for v in vendor_files if (source_dir / v).exists()]
    if new_vendor and not any(
        token in handoff_text for token in ("用户授权", "用户要求", "原本存在", "preserved")
    ):
        errors.append(
            f"[project-docs] 检测到工具方言文件 {new_vendor} — 若是 skill 自动生成请删除并改用 README + docs/; "
            "若是用户原本就有或明确授权, 在 handoff 写 '用户授权 X.md' 跳过本警告. "
            "见 references/11-project-docs.md#显式不产出"
        )

    return errors


# === End Productization Gate Checks ===


def lint(text: str, phase: str = "", source_dir: Path | None = None) -> list[str]:
    errors: list[str] = []
    errors.extend(check_required(text))
    errors.extend(check_internal_progress_table(text))
    errors.extend(check_residual_risk_anti_pattern(text))
    errors.extend(check_open_ended(text))
    errors.extend(check_decision_block(text))
    if phase:
        errors.extend(check_phase_specific(text, phase))
    if phase and source_dir:
        if phase == "solution":
            errors.extend(check_solution_productization_gate(source_dir))
        elif phase == "implementation":
            errors.extend(check_implementation_product_surface(source_dir))
            errors.extend(check_implementation_project_docs(source_dir, text))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, help="读 hand-off 文本的路径; 不给则读 stdin")
    parser.add_argument(
        "--phase",
        default="",
        choices=("", "intake", "requirements", "solution", "ui-design", "implementation-plan", "implementation", "verification", "deployment", "calibration"),
        help="可选: 当前阶段名, 用于阶段特定检查",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path.cwd(),
        help="项目根目录, 默认当前目录。用于 phase=solution/implementation 的产品化门禁文件级检查",
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

    errors = lint(text, phase=args.phase, source_dir=args.source_dir)

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
