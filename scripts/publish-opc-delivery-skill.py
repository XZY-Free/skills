#!/usr/bin/env python3
"""Publish only runtime OPC delivery skill files to the Codex skill dir by default."""

from __future__ import annotations

import argparse
import shutil
import tempfile
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
    ".DS_Store",
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


def compare_trees(expected: Path, actual: Path) -> list[str]:
    errors: list[str] = []
    if not actual.exists():
        return [f"target does not exist: {actual}"]

    for expected_path in sorted(expected.rglob("*")):
        rel = expected_path.relative_to(expected)
        actual_path = actual / rel
        if expected_path.is_dir():
            if not actual_path.is_dir():
                errors.append(f"missing directory: {rel}")
        elif expected_path.is_file():
            if not actual_path.is_file():
                errors.append(f"missing file: {rel}")
            elif expected_path.read_bytes() != actual_path.read_bytes():
                errors.append(f"content differs: {rel}")

    for actual_path in sorted(actual.rglob("*")):
        rel = actual_path.relative_to(actual)
        if not (expected / rel).exists():
            errors.append(f"unexpected extra path: {rel}")

    return errors


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


def check_published(source_dir: Path, targets: list[Path]) -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="opc-delivery-runtime-") as tmp:
        expected = Path(tmp) / "expected"
        publish(source_dir, [expected])
        for target in targets:
            target_errors = compare_trees(expected, target)
            noise = find_noise(target) if target.exists() else []
            if noise:
                target_errors.extend(f"non-runtime noise in target: {item}" for item in noise)
            errors.extend(f"{target}: {error}" for error in target_errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(ROOT / "opc-delivery"))
    parser.add_argument(
        "--target",
        action="append",
        default=None,
        help="Target skill directory. Repeat to publish to additional hosts; default is Codex only.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare target runtime files against a temporary source snapshot without writing targets.",
    )
    args = parser.parse_args()

    source_dir = Path(args.source).expanduser().resolve()
    raw_targets = args.target or [
        str(Path.home() / ".codex/skills/opc-delivery"),
    ]
    targets = [Path(target).expanduser().resolve() for target in raw_targets]
    if args.check:
        errors = check_published(source_dir, targets)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        for target in targets:
            print(f"checked {source_dir} == {target}")
        return 0

    publish(source_dir, targets)
    for target in targets:
        print(f"published {source_dir} -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
