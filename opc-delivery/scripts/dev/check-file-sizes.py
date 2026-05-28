#!/usr/bin/env python3
"""Check opc-delivery skill 自身文件是否超出"单次 Read 可读完"边界.

为什么需要这个:
SKILL.md / references / evals 任一文件超过单次 Read tool 的 token 上限 (~25000 tokens),
模型读自己的 skill 会失败. 这违反 references/09-runtime-budget.md 自己定的资源边界规则.

退出码:
  0  全部通过
  1  有文件超过硬上限 (skill 必修)
  2  有文件接近上限 (warn, 应主动拆分)

用法:
  python3 scripts/dev/check-file-sizes.py
  python3 scripts/dev/check-file-sizes.py --skill-dir /path/to/opc-delivery
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# 经验值: ~25000 tokens ≈ 单次 Read 上限. 中文 ~ 1 token/字, markdown 平均 ~ 8-10 token/行.
# 500 行留足 token 余量, 任何宿主单次 Read 都能读完.
MD_HARD_LIMIT = 500
MD_WARN = 400

# JSON 主要是 evals 这种结构化数据, 拐点更高. 但若是 LLM 要全量读 evals 调试时, 仍受限制.
JSON_HARD_LIMIT = 1000
JSON_WARN = 800


# 已审议的 borderline 文件: warn 区但有意保留, 不再报警.
# 加入条件: 文件确实接近 warn 但**没有独立流程边界**, 硬拆会破坏单一真相源/可读性.
# 加新文件前必须写 Why; 写不出来就说明应该拆.
DELIBERATE_BORDERLINE: dict[str, str] = {
    "references/04-solution.md": (
        "方案阶段单一连续逻辑: 进入条件 → 高影响决策 → 探索门禁 → 文档结构 → 产品姿态 → "
        "UI/设计质量门禁 → 收敛. 拆开会让模型读方案阶段时多读 2-3 个文件, 违反 progressive disclosure."
    ),
    "references/05b-magic-restore.md": (
        "模式 A(企业级)/B(快速复刻) 共享 URL 解析 / 拉 D2C / 资源落盘 / 框架探嗅前置. "
        "拆成两个文件后, 模式 A/B 都要 include 前置, 复制反而比单文件大."
    ),
    "references/10-contracts.md": (
        "核心契约总集 (北极星 / 收尾 / 交付 / 证据 / 持久化 / Karpathy / token). "
        "已按 '规则 + Why + 应用 + 例外' 重写, 是契约查阅入口; 拆开破坏单一真相源."
    ),
    "references/11-project-docs.md": (
        "5 个长期文档模板 (README / ARCHITECTURE / DATA-MODEL / CONVENTIONS / decisions) "
        "+ 萃取规则 + 完成门槛集成. 模板集本就是一站式查询, 拆开后每个 30-80 行的子文件意义不大."
    ),
}


def scan(skill_dir: Path) -> tuple[list[tuple[Path, int, str]], list[tuple[Path, int, str]], list[tuple[Path, int, str]]]:
    fails: list[tuple[Path, int, str]] = []
    warns: list[tuple[Path, int, str]] = []
    deliberate: list[tuple[Path, int, str]] = []

    targets = [
        ("*.md", MD_HARD_LIMIT, MD_WARN),
        ("*.json", JSON_HARD_LIMIT, JSON_WARN),
    ]

    for pattern, hard, warn in targets:
        for f in sorted(skill_dir.rglob(pattern)):
            # 跳过 workspace 副本和 .git
            if "skill-snapshot" in f.parts or ".git" in f.parts:
                continue
            try:
                lines = sum(1 for _ in f.open(encoding="utf-8"))
            except (UnicodeDecodeError, OSError):
                continue
            rel = f.relative_to(skill_dir)
            rel_str = rel.as_posix()
            if lines > hard:
                fails.append((rel, lines, f"超硬上限 {hard}"))
            elif lines > warn:
                if rel_str in DELIBERATE_BORDERLINE:
                    deliberate.append((rel, lines, DELIBERATE_BORDERLINE[rel_str]))
                else:
                    warns.append((rel, lines, "接近上限, 建议拆分"))

    return fails, warns, deliberate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skill-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent,
        help="skill 根目录 (默认: 脚本所在 skill)",
    )
    args = parser.parse_args()

    skill_dir = args.skill_dir.resolve()
    if not skill_dir.is_dir():
        print(f"❌ skill 目录不存在: {skill_dir}", file=sys.stderr)
        return 2

    fails, warns, deliberate = scan(skill_dir)

    if fails:
        print(f"❌ {len(fails)} 个文件超硬上限 (skill 必修):")
        for rel, lines, why in fails:
            print(f"  - {rel}: {lines} 行 ({why})")
    if warns:
        print(f"⚠️  {len(warns)} 个文件接近上限 (建议拆分):")
        for rel, lines, why in warns:
            print(f"  - {rel}: {lines} 行 ({why})")
    if deliberate:
        print(f"ℹ️  {len(deliberate)} 个 borderline 文件已审议 (warn 区, 有意保留):")
        for rel, lines, why in deliberate:
            print(f"  - {rel}: {lines} 行")
            print(f"      Why: {why}")

    if not fails and not warns:
        if deliberate:
            print(f"\n✓ 所有 .md ≤ {MD_HARD_LIMIT} 行, .json ≤ {JSON_HARD_LIMIT} 行 ({len(deliberate)} 个 borderline 已审议)")
        else:
            print(f"✓ 所有 .md ≤ {MD_HARD_LIMIT} 行, .json ≤ {JSON_HARD_LIMIT} 行")
        return 0

    if fails:
        print(
            "\n修复指引:",
            "  - .md 文件按独立流程边界拆 (不机械按行数切)",
            "  - 父文件保留索引 + 一句话定位, 内容挪到子文件",
            "  - 更新 SKILL.md 索引和所有 anchor 链接",
            "  - .json 文件按主题/层级拆 (如 evals 已分 core/regression/productization)",
            sep="\n",
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
