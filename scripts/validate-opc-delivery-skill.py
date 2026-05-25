#!/usr/bin/env python3
"""Validate the OPC delivery skill without third-party dependencies."""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parent.parent
NOISE_NAMES = {
    ".DS_Store",
    ".omc",
    "README.md",
    "README.en.md",
    "BENCHMARK.md",
    "__pycache__",
    "examples",
}
NOISE_SUFFIXES = {".pyc"}
REFERENCE_LINE_WARN = 200
REFERENCE_BYTES_WARN = 12 * 1024


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def run_command(cmd: list[str], errors: list[str]) -> None:
    result = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True)
    if result.returncode == 0:
        return
    rendered = " ".join(cmd)
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    errors.append(f"{rendered} exited {result.returncode}\n{output}")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str | None]:
    if not text.startswith("---\n"):
        return {}, "SKILL.md must start with YAML frontmatter"
    end = text.find("\n---", 4)
    if end == -1:
        return {}, "SKILL.md frontmatter is not closed"
    metadata: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            return metadata, f"unsupported frontmatter line: {line!r}"
        raw_value = match.group(2).strip()
        is_quoted = (raw_value.startswith('"') and raw_value.endswith('"')) or (
            raw_value.startswith("'") and raw_value.endswith("'")
        )
        if re.search(r":\s", raw_value) and not is_quoted:
            return metadata, f"frontmatter value containing ': ' must be quoted: {match.group(1)}"
        metadata[match.group(1)] = raw_value.strip('"').strip("'")
    return metadata, None


def check_frontmatter(source: Path, errors: list[str]) -> None:
    skill_md = source / "SKILL.md"
    if not skill_md.is_file():
        errors.append(f"{rel(skill_md)} is required")
        return
    metadata, parse_error = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if parse_error:
        errors.append(parse_error)
        return
    keys = set(metadata)
    if keys != {"name", "description"}:
        errors.append(f"SKILL.md frontmatter keys must be exactly name/description, got {sorted(keys)}")
    if metadata.get("name") != source.name:
        errors.append(f"SKILL.md name must be {source.name!r}")
    if not metadata.get("description"):
        errors.append("SKILL.md description must be non-empty")


def normalize_markdown_target(raw_target: str) -> str:
    target = raw_target.strip()
    if not target:
        return ""
    if target.startswith("<") and ">" in target:
        target = target[1 : target.find(">")]
    else:
        target = target.split()[0]
    return unquote(target.strip("<>\"'"))


def markdown_files(source: Path) -> list[Path]:
    return [source / "SKILL.md", *sorted((source / "references").glob("*.md"))]


def check_markdown_links(source: Path, errors: list[str]) -> None:
    for path in markdown_files(source):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r"!?\[[^\]]*]\(([^)]+)\)", text):
            target = normalize_markdown_target(match.group(1))
            if not target or target.startswith(("#", "http://", "https://", "mailto:", "mastergo://")):
                continue
            local_target = target.split("#", 1)[0]
            if not local_target:
                continue
            resolved = (path.parent / local_target).resolve()
            try:
                resolved.relative_to(source)
            except ValueError:
                errors.append(f"{rel(path)} links outside skill root: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{rel(path)} links to missing file: {target}")


def check_script_references(source: Path, errors: list[str]) -> None:
    for path in markdown_files(source):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"\bpython\s+(?:scripts/|<skill-dir>/scripts/)", text):
            errors.append(f"{rel(path)} must use python3 when invoking bundled scripts")
        for match in re.finditer(r"(?:<skill-dir>/)?scripts/([A-Za-z0-9_./-]+\.(?:py|mjs|sh))", text):
            script = source / "scripts" / match.group(1)
            if not script.exists():
                errors.append(f"{rel(path)} references missing script {match.group(0)}")


def check_executable_scripts(source: Path, errors: list[str]) -> None:
    paths = [*sorted((source / "scripts").rglob("*")), *sorted((REPO_ROOT / "scripts").glob("*.py"))]
    for path in paths:
        if not path.is_file():
            continue
        first_line = path.read_text(encoding="utf-8", errors="ignore").splitlines()[:1]
        if first_line and first_line[0].startswith("#!") and path.stat().st_mode & 0o111 == 0:
            errors.append(f"{rel(path)} has a shebang but is not executable")


def check_noise(source: Path, errors: list[str]) -> None:
    for path in source.rglob("*"):
        if path.name in NOISE_NAMES or path.suffix in NOISE_SUFFIXES:
            errors.append(f"runtime/cache noise must be removed: {rel(path)}")
    scripts_root = REPO_ROOT / "scripts"
    if not scripts_root.exists():
        return
    for path in scripts_root.rglob("*"):
        if path.name in {"__pycache__", ".DS_Store"} or path.suffix in NOISE_SUFFIXES:
            errors.append(f"runtime/cache noise must be removed: {rel(path)}")


def check_python_syntax(source: Path, errors: list[str]) -> None:
    files = [
        *sorted((source / "scripts").rglob("*.py")),
        REPO_ROOT / "scripts" / "publish-opc-delivery-skill.py",
        REPO_ROOT / "scripts" / "check-evals.py",
        Path(__file__).resolve(),
    ]
    for path in files:
        if not path.is_file():
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{rel(path)} has invalid Python syntax: {exc}")


def check_node_syntax(source: Path, errors: list[str]) -> None:
    files = sorted((source / "scripts").rglob("*.mjs"))
    if not files:
        return
    node = shutil.which("node")
    if not node:
        errors.append("node is required to syntax-check .mjs files")
        return
    for path in files:
        run_command([node, "--check", str(path)], errors)


def check_shell_syntax(source: Path, errors: list[str]) -> None:
    for path in sorted((source / "scripts").rglob("*.sh")):
        run_command(["bash", "-n", str(path)], errors)


def check_publish(source: Path, installed_targets: list[Path], errors: list[str]) -> None:
    publish_script = REPO_ROOT / "scripts" / "publish-opc-delivery-skill.py"
    with tempfile.TemporaryDirectory(prefix="opc-delivery-publish-") as tmp:
        dry_target = Path(tmp) / source.name
        run_command(
            ["python3", str(publish_script), "--source", str(source), "--target", str(dry_target)],
            errors,
        )
    for target in installed_targets:
        run_command(
            [
                "python3",
                str(publish_script),
                "--source",
                str(source),
                "--target",
                str(target),
                "--check",
            ],
            errors,
        )


def check_eval_schema(source: Path, errors: list[str]) -> None:
    evals_path = source / "evals" / "evals.json"
    if not evals_path.is_file():
        errors.append(f"{rel(evals_path)} is required")
        return
    try:
        data = json.loads(evals_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{rel(evals_path)} invalid JSON: {exc}")
        return
    if not isinstance(data, dict):
        errors.append(f"{rel(evals_path)} top-level must be object")
        return
    if data.get("skill_name") != source.name:
        errors.append(f"{rel(evals_path)} skill_name must be {source.name!r}")


def collect_size_warnings(source: Path) -> list[str]:
    warnings: list[str] = []
    for path in sorted((source / "references").glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        line_count = len(text.splitlines())
        byte_count = len(text.encode("utf-8"))
        if line_count <= REFERENCE_LINE_WARN and byte_count <= REFERENCE_BYTES_WARN:
            continue
        has_toc = "## 目录" in "\n".join(text.splitlines()[:30]) or "## Table of Contents" in "\n".join(
            text.splitlines()[:30]
        )
        status = "has TOC" if has_toc else "no TOC"
        warnings.append(f"{rel(path)} is {line_count} lines/{byte_count} bytes ({status})")
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(REPO_ROOT / "opc-delivery"))
    parser.add_argument(
        "--installed-target",
        action="append",
        default=[],
        help="Installed skill directory to compare with the generated runtime snapshot. Repeatable.",
    )
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    installed_targets = [Path(target).expanduser().resolve() for target in args.installed_target]
    errors: list[str] = []

    if not source.is_dir():
        errors.append(f"source skill directory does not exist: {source}")
    else:
        check_frontmatter(source, errors)
        check_noise(source, errors)
        check_markdown_links(source, errors)
        check_script_references(source, errors)
        check_executable_scripts(source, errors)
        check_eval_schema(source, errors)
        check_python_syntax(source, errors)
        check_node_syntax(source, errors)
        check_shell_syntax(source, errors)
        run_command(["python3", str(source / "scripts" / "dev" / "check-skill-rules.py")], errors)
        run_command(["python3", str(REPO_ROOT / "scripts" / "check-evals.py"), "--root", str(REPO_ROOT), "--skill", source.name], errors)
        check_publish(source, installed_targets, errors)

    warnings = collect_size_warnings(source) if source.is_dir() else []
    for warning in warnings:
        print(f"WARN: {warning}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"{source.name} validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
