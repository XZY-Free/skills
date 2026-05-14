#!/usr/bin/env python3
"""Publish only runtime OPC delivery skill files to Codex and Claude skill dirs."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RUNTIME_ITEMS = ("SKILL.md", "agents", "references", "scripts", "evals")
NOISE_NAMES = {
    "README.md",
    "README.en.md",
    "BENCHMARK.md",
    "examples",
    "docs-images",
    ".omc",
    "__pycache__",
}
NOISE_FILE_GLOBS = ("*.pyc",)


def copy_item(source: Path, target: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, target, ignore=shutil.ignore_patterns(*NOISE_NAMES, *NOISE_FILE_GLOBS))
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def find_noise(target_dir: Path) -> list[str]:
    found: list[str] = []
    for path in target_dir.rglob("*"):
        if path.name in NOISE_NAMES or any(path.match(pattern) for pattern in NOISE_FILE_GLOBS):
            found.append(str(path.relative_to(target_dir)))
    return sorted(found)


def publish(source_dir: Path, targets: list[Path]) -> None:
    for target_dir in targets:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True)
        for item in RUNTIME_ITEMS:
            source = source_dir / item
            if source.exists():
                copy_item(source, target_dir / item)
        unexpected = find_noise(target_dir)
        if unexpected:
            raise RuntimeError(f"Published skill contains non-runtime files: {unexpected}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(ROOT / "opc-delivery"))
    parser.add_argument(
        "--target",
        action="append",
        default=None,
        help="Target skill directory. Repeat to publish to multiple hosts.",
    )
    args = parser.parse_args()

    source_dir = Path(args.source).expanduser().resolve()
    raw_targets = args.target or [
        str(Path.home() / ".codex/skills/opc-delivery"),
        str(Path.home() / ".claude/skills/opc-delivery"),
    ]
    targets = [Path(target).expanduser().resolve() for target in raw_targets]
    publish(source_dir, targets)
    for target in targets:
        print(f"published {source_dir} -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
