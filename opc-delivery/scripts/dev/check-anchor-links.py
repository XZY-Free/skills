#!/usr/bin/env python3
"""检查 opc-delivery skill 内所有 markdown anchor 链接是否有效.

为什么需要:
拆分 references 时, 把 [05-mastergo.md#xxx] 改成 [05a-codify-design.md#xxx]. 如果 anchor
slug 不对(比如目标文件不存在或标题已重命名), 链接就断了, 模型跳过去会找不到内容.

规则:
1. 提取所有 [...](path) markdown 链接
2. 解析 path = file#anchor 或 file 或 #anchor
3. 验证文件存在 + (如有 anchor) anchor 对应到目标文件的某个 ## 标题
4. 跨文件 anchor 用 GitHub-style slug (中文标题保留 + 小写 ASCII + 替换空格 / 特殊符号)

退出码:
  0  全部通过
  1  有断链
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


def slugify(heading: str) -> str:
    """GitHub-style heading slug. 关键: 删除不在白名单的字符(包括 emoji / +/:/()), 但**不**合并相邻空格, 且**不** strip 开头/结尾 -.

    例:
        "⚠️ 强制溯源汇报"      → "-强制溯源汇报"  (emoji 删除后留空格→-)
        "JTBD + MoSCoW 门禁"   → "jtbd--moscow-门禁" (+ 删除产生双空格→--)
        "校准: 已上线需求回放" → "校准-已上线需求回放"
    """
    s = heading.strip().lower()
    s = re.sub(r"[`*_]", "", s)  # 删 markdown 装饰
    # 白名单: ASCII letters/digits/_, 空白, -, CJK
    # 其它字符(标点 / emoji / 全角符号)全部删除, 不替换为 -
    s = re.sub(r"[^\w\s\-一-鿿]", "", s)
    s = re.sub(r"\s", "-", s)  # 每个空白→-, 不合并(GitHub 行为)
    return s  # 不 strip 开头/结尾, 与 GitHub 行为对齐


def extract_headings(md_path: Path) -> set[str]:
    """提取一个 md 文件的所有 ## 标题, 返回 slug 集合."""
    slugs: set[str] = set()
    if not md_path.is_file():
        return slugs
    for line in md_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"^#{1,6}\s+(.+)$", line)
        if m:
            slugs.add(slugify(m.group(1)))
    return slugs


def extract_links(md_path: Path) -> list[tuple[int, str, str]]:
    """提取 (line_no, link_text, target) 元组. 跳过 fenced code block 内的链接(模板示例)."""
    out: list[tuple[int, str, str]] = []
    if not md_path.is_file():
        return out
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    in_fence = False
    for i, line in enumerate(md_path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue  # 模板 / 代码示例里的链接不算 skill 自身导航
        for m in pattern.finditer(line):
            target = m.group(2).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            out.append((i, m.group(1), target))
    return out


def main() -> int:
    skill_dir = Path(__file__).resolve().parent.parent.parent
    md_files = sorted(skill_dir.rglob("*.md"))
    md_files = [p for p in md_files if "skill-snapshot" not in p.parts and ".git" not in p.parts]

    # 先把所有目标文件的 slugs 缓存
    file_slugs: dict[Path, set[str]] = {}
    for f in md_files:
        file_slugs[f.resolve()] = extract_headings(f)

    broken: list[str] = []

    for f in md_files:
        rel_self = f.relative_to(skill_dir)
        for ln, text, target in extract_links(f):
            # 分离 path 和 anchor
            if "#" in target:
                path_part, anchor = target.split("#", 1)
                anchor = unquote(anchor)
            else:
                path_part, anchor = target, ""

            # 相对路径解析
            if path_part == "":
                # 同文件 anchor 跳转
                target_file = f.resolve()
            else:
                target_file = (f.parent / path_part).resolve()
                if not target_file.exists():
                    broken.append(f"{rel_self}:{ln} → {target}  (文件不存在)")
                    continue
                if target_file.is_dir():
                    # 链接到目录(如 docs/decisions/) 没 anchor 检查
                    continue

            if anchor:
                target_slug = slugify(anchor)
                slugs = file_slugs.get(target_file, set())
                if target_slug not in slugs:
                    broken.append(
                        f"{rel_self}:{ln} → {target}  (anchor '#{anchor}' 在目标文件不存在)"
                    )

    if broken:
        print(f"❌ {len(broken)} 个 anchor 断链:")
        for b in broken[:30]:
            print(f"  - {b}")
        if len(broken) > 30:
            print(f"  ... 还有 {len(broken) - 30} 个未显示")
        return 1

    print(f"✓ 所有 markdown anchor 链接有效 (扫描 {len(md_files)} 个文件)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
