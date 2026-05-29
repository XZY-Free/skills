#!/usr/bin/env python3
"""Guard OPC delivery skill docs against stale tools, undeclared scripts, and weak evals.

启用的 check (按 references/01-10 + mcp-setup + troubleshooting + scripts/README 新结构):

- check_frontmatter      — SKILL.md frontmatter 格式 + 行数 ≤ 500
- check_evals            — evals/ 下所有 *.json 集合: 必需 name + 结构 + skill_name
- check_banned           — 文本里禁用过时工具(html2text / AskUserQuestion)
- check_script_references — 引用的脚本存在 + python3 调用 + shebang 可执行
- check_skill_hygiene    — skill 根目录干净 + agents/openai.yaml 内容
- check_reference_tocs   — references/*.md 超 100 行需有 ## 目录
- check_runtime_subset   — publish 脚本声明的运行时白名单与噪声排除

已移除的 check:
- check_markdown_links   — 被 dev/check-anchor-links.py 替代(后者覆盖 anchor + 文件存在)
- check_scope_contract   — 200+ 行硬编码旧 reference phrase, references 重组后全废
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_TEXTS = [
    ROOT / "SKILL.md",
    *(ROOT / "references").glob("*.md"),
    *(ROOT / "evals").glob("*"),
]
ALLOWED_ROOT_ITEMS = {"SKILL.md", "agents", "references", "scripts", "evals", "assets"}
# .omc 是 OMC 宿主运行时注入的临时目录, 不属于 skill 自身
ALLOWED_ROOT_TRANSIENT = {".omc"}
NOISE_NAMES = {
    ".DS_Store",
    "README.en.md",
    "BENCHMARK.md",
    "__pycache__",
    "examples",
}
# scripts/README.md 是合法脚本索引; root 级 README.md 才算 noise
ROOT_LEVEL_NOISE = {"README.md"}
NOISE_SUFFIXES = {".pyc"}
BANNED = {
    "html2text": "Use scripts/fetch-doc-snippet.py instead of optional html2text.",
    "AskUserQuestion": "Ask directly or use the host's available user-input mechanism.",
}
REQUIRED_EVAL_NAMES = {
    "opc-intake-records-internal-stage-state",
    "requirements-prd-before-ui",
    "solution-design-before-implementation",
    "ordinary-user-progress-uses-result-brief",
    "internal-stage-table-not-user-visible",
    "implementation-plan-required-before-code",
    "large-implementation-plan-splits-context-safely",
    "implementation-reads-current-slice-not-all-docs",
    "implementation-plan-uses-value-slices-not-layer-splits",
    "adr-records-high-impact-decisions",
    "implementation-plan-records-context-budget",
    "implementation-plan-identifies-parallel-lanes",
    "empty-workspace-full-opc-enters-implementation",
    "missing-prerequisites-auto-bootstrap",
    "verification-phase-state-ledger",
    "handoff-structured-turn-close",
    "karpathy-framing-before-code",
    "implementation-does-not-skip-browser-qa",
    "deployment-preview-before-production",
    "golden-feature-calibration",
    "requirements-uses-jtbd-and-moscow",
    "solution-offers-alternatives-and-self-review",
    "implementation-prefers-tdd-regression",
    "production-deploy-runs-premortem-redteam",
    "calibration-uses-aar-to-update-rules",
    "professional-completion-requires-evidence",
    "full-opc-auto-advances-until-release",
    "skill-creator-structure-hygiene",
    "frontend-design-quality-in-opc-ui",
    "context-persistence-auto-resume",
    "mcp-setup-codex",
    "single-page-restoration",
    "design-update-diff",
    "codify-design-preflight-gates",
    "codify-guidelines-before-push",
    "codify-tailwind-sync-html",
    "design-completion-requires-mastergo-push",
    "delivery-contract-no-substitute-artifacts",
    "missing-magic-mcp-no-local-code-fallback",
    "missing-codify-mcp-no-local-doc-fallback",
    "update-flow-diff-report-not-completion",
    "d2c-raw-output-not-restoration-complete",
    "mcp-config-written-needs-restart-verification",
    "positive-feedback-continues-design-task",
    "requirement-coverage-not-keyword-page-count",
    "clarification-prefers-choice-with-custom",
    "config-restart-resumes-original-requirement",
    "codify-accepted-not-complete",
    "local-html-not-primary-mastergo-deliverable",
    "raw-token-rotate-warning",
    "codify-html-lint-no-text-regex",
    "ui-copy-follows-chat-language",
    "explicit-english-ui-overrides-chat-language",
    "mixed-technical-terms-allowed-in-chinese-ui",
    "screenshot-language-inference",
    "localization-verification-before-completion",
    "magic-mcp-tool-search-is-not-config",
    "current-host-config-only",
    "user-action-guidance-contract",
    "mastergo-goto-url-parse",
    "no-stale-tool-or-optional-html-parser",
    "api-doc-script-availability",
    "gate-card-before-codify-write",
    "enterprise-ai-platform-not-single-dashboard",
    "task-ledger-required-before-completion",
    "local-library-snapshot-priority",
    "unauthorized-get-library-list-avoided",
    "codify-preflight-blocks-stale-html",
    "accepted-pending-written-to-state",
    "codify-bridge-local-url",
    "magic-restoration-state-and-language",
    "update-flow-language-risk-applied",
    "native-decision-interaction-required",
    "clear-requirement-proceeds-without-card-ceremony",
    "low-risk-details-do-not-interrupt-user",
    "deployment-default-is-local-production-server",
    "deployment-parses-ssh-one-line-credentials",
    "db-default-mysql-not-sqlite-or-postgres",
    "mysql-auto-install-via-docker-when-missing",
    "wrap-up-asks-once-about-remote-deploy",
    "credentials-redacted-in-echo-and-release-md",
    "production-remote-deploy-still-runs-premortem",
    "no-paas-platforms-in-default-flow",
}
REQUIRED_NEGATIVE_EVAL_NAMES = {
    "figma-not-mastergo",
    "pure-frontend-no-design-source",
    "mastergo-link-broken-not-task",
    "general-mcp-not-mastergo",
    "design-system-figma-tokens",
    "d2c-but-not-mastergo",
    "codify-name-collision",
    "frontend-framework-pick-no-design",
    "general-token-config",
    "ai-design-prompt-only",
    "no-mention-of-vercel-or-netlify-when-deployment-target-unclear",
}


def frontmatter_keys(text: str) -> list[str]:
    if not text.startswith("---\n"):
        return []
    end = text.find("\n---", 4)
    if end == -1:
        return []
    keys: list[str] = []
    for line in text[4:end].splitlines():
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):", line)
        if match:
            keys.append(match.group(1))
    return keys


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def check_banned() -> list[str]:
    errors: list[str] = []
    for path in RUNTIME_TEXTS:
        text = read(path)
        for token, message in BANNED.items():
            if token in text:
                errors.append(f"{path.relative_to(ROOT)} contains {token!r}: {message}")
    return errors


def check_frontmatter() -> list[str]:
    text = read(ROOT / "SKILL.md")
    keys = frontmatter_keys(text)
    if not keys:
        return ["SKILL.md must start with YAML frontmatter"]
    allowed = {"name", "description"}
    unexpected = sorted(set(keys) - allowed)
    missing = sorted(allowed - set(keys))
    errors: list[str] = []
    end = text.find("\n---", 4)
    if end != -1 and end - 4 > 1024:
        errors.append("SKILL.md frontmatter should stay under 1024 characters")
    if end != -1:
        for line in text[4:end].splitlines():
            if not line.strip() or line.startswith((" ", "\t")):
                continue
            match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
            if not match:
                errors.append(f"SKILL.md frontmatter has unsupported line: {line!r}")
                continue
            raw_value = match.group(2).strip()
            is_quoted = (raw_value.startswith('"') and raw_value.endswith('"')) or (
                raw_value.startswith("'") and raw_value.endswith("'")
            )
            if re.search(r":\s", raw_value) and not is_quoted:
                errors.append(f"SKILL.md frontmatter value containing ': ' must be quoted: {match.group(1)}")
    if len(text.splitlines()) > 500:
        errors.append("SKILL.md should stay under 500 lines; move details into references/")
    if unexpected:
        errors.append(f"SKILL.md frontmatter has unsupported keys: {unexpected}")
    if missing:
        errors.append(f"SKILL.md frontmatter missing required keys: {missing}")
    return errors


def check_script_references() -> list[str]:
    errors: list[str] = []
    for path in [ROOT / "SKILL.md", *(ROOT / "references").glob("*.md")]:
        text = read(path)
        if re.search(r"\bpython\s+(?:scripts/|<skill-dir>/scripts/)", text):
            errors.append(f"{path.relative_to(ROOT)} must use python3 when invoking bundled scripts")
        for match in re.finditer(r"scripts/([A-Za-z0-9_./\-]+)", text):
            rel = match.group(1)
            # 跳过结尾标点和 anchor / glob 之类
            rel = rel.rstrip(".,;:)")
            script = ROOT / "scripts" / rel
            if script.suffix in ("", ".md", ".py", ".sh", ".mjs", ".json") and not script.exists():
                # README 索引 / placeholder 文案不报错
                if rel.endswith("/") or rel == "README.md":
                    continue
                errors.append(f"{path.relative_to(ROOT)} references missing script scripts/{rel}")
    for script in sorted((ROOT / "scripts").rglob("*")):
        if not script.is_file():
            continue
        if script.suffix not in (".py", ".sh", ".mjs"):
            continue
        first_line = script.read_text(encoding="utf-8", errors="ignore").splitlines()[:1]
        if first_line and first_line[0].startswith("#!") and script.stat().st_mode & 0o111 == 0:
            errors.append(f"{script.relative_to(ROOT)} has a shebang but is not executable")
    return errors


def check_skill_hygiene() -> list[str]:
    errors: list[str] = []
    for item in ROOT.iterdir():
        if item.name in ALLOWED_ROOT_ITEMS or item.name in ALLOWED_ROOT_TRANSIENT:
            continue
        errors.append(f"unexpected non-runtime skill root item {item.relative_to(ROOT)}")
    for path in ROOT.rglob("*"):
        # 跳过 OMC 注入的运行时目录(任何深度)
        if any(part in ALLOWED_ROOT_TRANSIENT for part in path.parts):
            continue
        if path.name in NOISE_NAMES or path.suffix in NOISE_SUFFIXES:
            errors.append(f"runtime noise must not be bundled: {path.relative_to(ROOT)}")
        # root 级 README.md 是 noise, 但 scripts/README.md 是合法脚本索引
        if path.name in ROOT_LEVEL_NOISE and path.parent == ROOT:
            errors.append(f"runtime noise must not be bundled: {path.relative_to(ROOT)}")

    openai_yaml = ROOT / "agents/openai.yaml"
    if not openai_yaml.exists():
        errors.append("agents/openai.yaml is required")
        return errors
    text = read(openai_yaml)
    for phrase in ["display_name:", "short_description:", "default_prompt:", "$opc-delivery"]:
        if phrase not in text:
            errors.append(f"agents/openai.yaml missing phrase {phrase!r}")
    for phrase in ["OPC/full-cycle", "MasterGo-backed", "implementation planning"]:
        if phrase not in text:
            errors.append(f"agents/openai.yaml default prompt missing phrase {phrase!r}")
    short_match = re.search(r'short_description:\s*"([^"]+)"', text)
    if short_match and not (25 <= len(short_match.group(1)) <= 64):
        errors.append("agents/openai.yaml short_description should be 25-64 characters")
    prompt_match = re.search(r'default_prompt:\s*"([^"]+)"', text)
    if prompt_match:
        default_prompt = prompt_match.group(1)
        if len(default_prompt) > 128:
            errors.append("agents/openai.yaml default_prompt should stay at or under 128 characters")
        if "continue unless blocked" not in default_prompt:
            errors.append("agents/openai.yaml default_prompt should mention continuing unless blocked")
    return errors


def check_reference_tocs() -> list[str]:
    errors: list[str] = []
    for path in sorted((ROOT / "references").glob("*.md")):
        text = read(path)
        if len(text.splitlines()) <= 100:
            continue
        head = "\n".join(text.splitlines()[:30])
        if "## 目录" not in head and "## Table of Contents" not in head:
            errors.append(f"{path.relative_to(ROOT)} is over 100 lines and needs a top-level table of contents")
    return errors


def check_runtime_subset() -> list[str]:
    errors: list[str] = []
    publish_script = ROOT.parent / "scripts" / "publish-opc-delivery-skill.py"
    if not publish_script.exists():
        return ["scripts/publish-opc-delivery-skill.py is required"]
    text = read(publish_script)
    for token in ["RUNTIME_ITEMS", "SKILL.md", "agents", "references", "scripts", "evals"]:
        if token not in text:
            errors.append(f"publish-opc-delivery-skill.py missing runtime token {token!r}")
    for noise in [
        "README.md",
        "README.en.md",
        "BENCHMARK.md",
        "examples",
        "docs-images",
        ".omc",
        "__pycache__",
        ".DS_Store",
        "*.pyc",
    ]:
        if noise not in text:
            errors.append(f"publish-opc-delivery-skill.py missing noise exclusion {noise!r}")
    if ".claude/skills/opc-delivery" in text:
        errors.append("publish-opc-delivery-skill.py should not reference legacy .claude path")
    return errors


def check_evals() -> list[str]:
    """检查 evals/ 下所有 *.json (core / productization / regression-*).

    旧版只读单一 evals.json; 重构后改为读所有分层 eval 文件并整体验证.
    """
    evals_dir = ROOT / "evals"
    if not evals_dir.is_dir():
        return ["evals/ directory missing"]
    json_files = sorted(evals_dir.glob("*.json"))
    if not json_files:
        return ["evals/ has no *.json files"]

    errors: list[str] = []
    all_evals: list[dict] = []
    all_negative: list[dict] = []

    for jf in json_files:
        rel = jf.relative_to(ROOT)
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{rel} is not valid JSON: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{rel} top-level must be an object")
            continue
        if data.get("skill_name") != ROOT.name:
            errors.append(f"{rel} skill_name must be {ROOT.name!r}")
        if not isinstance(data.get("evals", []), list):
            errors.append(f"{rel} evals must be a list when present")
            continue
        if not isinstance(data.get("negative_evals", []), list):
            errors.append(f"{rel} negative_evals must be a list when present")
            continue
        for item in data.get("evals", []):
            if isinstance(item, dict):
                item["_source"] = str(rel)
                all_evals.append(item)
        for item in data.get("negative_evals", []):
            if isinstance(item, dict):
                item["_source"] = str(rel)
                all_negative.append(item)

    if errors:
        return errors

    seen_ids: set[int] = set()
    seen_names: set[str] = set()
    required_positive = {"id", "name", "prompt", "expected_output", "files"}
    required_negative = {"id", "name", "prompt", "expected_behavior", "should_trigger"}

    for section_name, items, required in (
        ("evals", all_evals, required_positive),
        ("negative_evals", all_negative, required_negative),
    ):
        for index, item in enumerate(items):
            src = item.get("_source", "?")
            missing = required - item.keys() - {"_source"}
            if missing:
                errors.append(f"{src} {section_name}[{index}] missing keys {sorted(missing)}")
            item_id = item.get("id")
            if not isinstance(item_id, int):
                errors.append(f"{src} {section_name}[{index}].id must be int")
            else:
                seen_ids.add(item_id)
            name = item.get("name")
            if not isinstance(name, str) or not name:
                errors.append(f"{src} {section_name}[{index}].name must be non-empty string")
            else:
                seen_names.add(name)
            if section_name == "evals" and "files" in item and not isinstance(item["files"], list):
                errors.append(f"{src} {section_name}[{index}].files must be list")
            if section_name == "negative_evals" and "should_trigger" in item and not isinstance(item.get("should_trigger"), bool):
                errors.append(f"{src} {section_name}[{index}].should_trigger must be bool")

    names = {item.get("name") for item in all_evals if isinstance(item, dict)}
    negative_names = {item.get("name") for item in all_negative if isinstance(item, dict)}
    missing = sorted(REQUIRED_EVAL_NAMES - names)
    if missing:
        errors.append(f"evals/ missing required evals (across all *.json): {missing}")
    missing_negative = sorted(REQUIRED_NEGATIVE_EVAL_NAMES - negative_names)
    if missing_negative:
        errors.append(f"evals/ missing required negative evals (across all *.json): {missing_negative}")

    forward_tests = ROOT / "evals/forward-tests.md"
    if not forward_tests.exists():
        errors.append("evals/forward-tests.md is required for no-leak forward-test protocol")
    else:
        forward_text = read(forward_tests)
        for phrase in [
            "Source validation before publishing",
            "Publish to the Codex installed copy",
            "Installed copy verification after publishing",
        ]:
            if phrase not in forward_text:
                errors.append(f"evals/forward-tests.md release gates missing phrase {phrase!r}")
        if "Before publishing the skill" in forward_text and "--installed-target" in forward_text:
            errors.append("evals/forward-tests.md must not require installed-target checks before publishing")

    combined_text = "\n".join(json.dumps(d, ensure_ascii=False) for d in (all_evals + all_negative))
    for stale_gate in ["quick_validate", "check-links"]:
        if stale_gate in combined_text:
            errors.append(f"evals/ contains stale validation gate {stale_gate!r}")
    return errors


def main() -> int:
    errors = (
        check_frontmatter()
        + check_evals()
        + check_banned()
        + check_script_references()
        + check_skill_hygiene()
        + check_reference_tocs()
        + check_runtime_subset()
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("opc-delivery skill rule check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
