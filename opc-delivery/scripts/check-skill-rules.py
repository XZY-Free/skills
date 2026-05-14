#!/usr/bin/env python3
"""Guard OPC delivery skill docs against stale tools, undeclared scripts, and weak evals."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_TEXTS = [
    ROOT / "SKILL.md",
    *(ROOT / "references").glob("*.md"),
    *(ROOT / "evals").glob("*"),
]
ALLOWED_ROOT_ITEMS = {"SKILL.md", "agents", "references", "scripts", "evals", "assets"}
BANNED = {
    "html2text": "Use scripts/fetch-doc-snippet.py instead of optional html2text.",
    "AskUserQuestion": "Ask directly or use the host's available user-input mechanism.",
    "webapp-testing": "Use Browser/Playwright guidance or scripts/screenshot.mjs.",
    "ui-ux-pro-max": "Reference only currently discoverable design skills.",
}
REQUIRED_EVAL_NAMES = {
    "opc-intake-produces-stage-card",
    "requirements-prd-before-ui",
    "solution-design-before-implementation",
    "empty-workspace-full-opc-enters-implementation",
    "missing-prerequisites-auto-bootstrap",
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
        for match in re.finditer(r"scripts/([A-Za-z0-9_.-]+)", read(path)):
            script = ROOT / "scripts" / match.group(1)
            if not script.exists():
                errors.append(f"{path.relative_to(ROOT)} references missing script {match.group(0)}")
    return errors


def check_skill_hygiene() -> list[str]:
    errors: list[str] = []
    for item in ROOT.iterdir():
        if item.name.startswith("."):
            continue
        if item.name not in ALLOWED_ROOT_ITEMS:
            errors.append(f"unexpected non-runtime skill root item {item.relative_to(ROOT)}")

    openai_yaml = ROOT / "agents/openai.yaml"
    if not openai_yaml.exists():
        errors.append("agents/openai.yaml is required")
        return errors
    text = read(openai_yaml)
    for phrase in ["display_name:", "short_description:", "default_prompt:", "$opc-delivery"]:
        if phrase not in text:
            errors.append(f"agents/openai.yaml missing phrase {phrase!r}")
    short_match = re.search(r'short_description:\s*"([^"]+)"', text)
    if short_match and not (25 <= len(short_match.group(1)) <= 64):
        errors.append("agents/openai.yaml short_description should be 25-64 characters")
    prompt_match = re.search(r'default_prompt:\s*"([^"]+)"', text)
    if prompt_match and "without stopping unless blocked" not in prompt_match.group(1):
        errors.append("agents/openai.yaml default_prompt should mention continuous delivery without stopping unless blocked")
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


def check_scope_contract() -> list[str]:
    errors: list[str] = []
    required_files = [
        ROOT / "references/opc-flow.md",
        ROOT / "references/autonomous-bootstrap.md",
        ROOT / "references/context-persistence.md",
        ROOT / "references/open-source-patterns.md",
        ROOT / "references/requirements-workflow.md",
        ROOT / "references/solution-design.md",
        ROOT / "references/implementation-workflow.md",
        ROOT / "references/deployment-workflow.md",
        ROOT / "references/regression-calibration.md",
        ROOT / "references/design-scope.md",
        ROOT / "references/copy-language.md",
        ROOT / "references/design-coverage-patterns.md",
        ROOT / "scripts/codify-html-lint.py",
        ROOT / "scripts/codify-copy-lint.py",
        ROOT / "scripts/codify-preflight.py",
        ROOT / "scripts/codify-artifact-audit.py",
        ROOT / "scripts/mastergo-task-state.py",
        ROOT / "scripts/library-snapshot.py",
        ROOT / "scripts/verification-state.py",
        ROOT / "scripts/check-release-env.py",
        ROOT / "scripts/opc-task-state.py",
    ]
    for path in required_files:
        if not path.exists():
            errors.append(f"missing required runtime file {path.relative_to(ROOT)}")

    scope_text = read(ROOT / "references/design-scope.md")
    required_phrases = [
        "不根据",
        "关键词",
        "自定义 / type something",
        "覆盖 brief",
        "中断后恢复",
    ]
    for phrase in required_phrases:
        if phrase not in scope_text:
            errors.append(f"references/design-scope.md missing phrase {phrase!r}")

    skill_text = read(ROOT / "SKILL.md")
    for phrase in [
        "OPC Stage Card",
        "阶段交付物契约",
        "开源交付门禁契约",
        "Gate Card",
        "需求覆盖契约",
        "选择题澄清契约",
        "自动轮转契约",
        "自治补齐契约",
        "上下文持久化契约",
        "UI 文案语种契约",
        "专业完成定义",
        "revoke / rotate",
    ]:
        if phrase not in skill_text:
            errors.append(f"SKILL.md missing contract phrase {phrase!r}")

    opc_flow = read(ROOT / "references/opc-flow.md")
    for phrase in [
        "requirements-workflow.md",
        "open-source-patterns.md",
        "deployment-workflow.md",
        "autonomous-bootstrap.md",
        "context-persistence.md",
        "opc-task-state.py",
        "自动阶段轮转",
        "自定义 / type something",
        "git init",
    ]:
        if phrase not in opc_flow:
            errors.append(f"references/opc-flow.md missing phrase {phrase!r}")

    bootstrap_text = read(ROOT / "references/autonomous-bootstrap.md")
    for phrase in [
        "git init",
        ".gitignore",
        "package.json",
        "mock",
        "CI/CD",
        "API key",
        "production",
        "远端 push",
        "自定义 / type something",
        "没有 Git 仓库，你先创建好我再继续",
    ]:
        if phrase not in bootstrap_text:
            errors.append(f"references/autonomous-bootstrap.md missing phrase {phrase!r}")

    context_text = read(ROOT / "references/context-persistence.md")
    for phrase in ["代理自动执行", "不是让用户手动运行", "nextAction", "主动拆分", "只存摘要", "自治补齐动作"]:
        if phrase not in context_text:
            errors.append(f"references/context-persistence.md missing phrase {phrase!r}")

    pattern_text = read(ROOT / "references/open-source-patterns.md")
    for phrase in [
        "JTBD",
        "MoSCoW",
        "2-3 个方案",
        "TDD/regression ratchet",
        "systematic debugging",
        "evidence-before-completion",
        "release packet",
        "premortem",
        "red-team",
        "AAR",
    ]:
        if phrase not in pattern_text:
            errors.append(f"references/open-source-patterns.md missing phrase {phrase!r}")

    requirements_text = read(ROOT / "references/requirements-workflow.md")
    for phrase in ["PRD", "验收标准", "Open Questions", ".opc/requirements/prd.md", "JTBD", "MoSCoW", "Core Job"]:
        if phrase not in requirements_text:
            errors.append(f"references/requirements-workflow.md missing phrase {phrase!r}")

    delivery_text = read(ROOT / "references/delivery-contract.md")
    for phrase in ["专业完成定义", "业务目标", "方案合理性", "UI/体验", "工程实现", "发布", "skipped with reason"]:
        if phrase not in delivery_text:
            errors.append(f"references/delivery-contract.md missing phrase {phrase!r}")

    solution_text = read(ROOT / "references/solution-design.md")
    for phrase in ["2-3 个方案", "Planning Packet", "自我审查", "推荐方案", "自动初始化 Git"]:
        if phrase not in solution_text:
            errors.append(f"references/solution-design.md missing phrase {phrase!r}")

    implementation_text = read(ROOT / "references/implementation-workflow.md")
    for phrase in ["TDD", "regression ratchet", "systematic debugging", "gate truth", "空工作区启动规则", "git init", "缺仓库 / 缺脚手架", "不是 Git 仓库，所以本轮先停在设计包"]:
        if phrase not in implementation_text:
            errors.append(f"references/implementation-workflow.md missing phrase {phrase!r}")

    deployment_text = read(ROOT / "references/deployment-workflow.md")
    for phrase in ["preview", "production", "rollback", ".opc/deployment/release.md", "release profile", "premortem", "red-team", "stop conditions", "git init", "无部署凭证/服务器"]:
        if phrase not in deployment_text:
            errors.append(f"references/deployment-workflow.md missing phrase {phrase!r}")

    calibration_text = read(ROOT / "references/regression-calibration.md")
    for phrase in ["AAR", "what expected", "what happened", "why different", "what changes"]:
        if phrase not in calibration_text:
            errors.append(f"references/regression-calibration.md missing phrase {phrase!r}")

    copy_text = read(ROOT / "references/copy-language.md")
    for phrase in ["Simplified Chinese", "codify-copy-lint.py", "自定义 / type something", "AgentOps", "不要因为企业级"]:
        if phrase not in copy_text:
            errors.append(f"references/copy-language.md missing phrase {phrase!r}")

    design_workflow = read(ROOT / "references/design-workflow.md")
    for phrase in ["MasterGo 设计 Gate Card", "mastergo-task-state.py", "library-snapshot.py", "codify-preflight.py"]:
        if phrase not in design_workflow:
            errors.append(f"references/design-workflow.md missing phrase {phrase!r}")

    push_text = read(ROOT / "references/codify-push-protocol.md")
    for phrase in ["codify-preflight.py", "codify-copy-lint.py", "codify-artifact-audit.py", "accepted"]:
        if phrase not in push_text:
            errors.append(f"references/codify-push-protocol.md missing phrase {phrase!r}")
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
    for noise in ["README.md", "README.en.md", "BENCHMARK.md", "examples", "docs-images", "__pycache__", "*.pyc"]:
        if noise not in text:
            errors.append(f"publish-opc-delivery-skill.py missing noise exclusion {noise!r}")
    return errors


def check_evals() -> list[str]:
    data = json.loads((ROOT / "evals/evals.json").read_text(encoding="utf-8"))
    names = {item.get("name") for item in data.get("evals", []) if isinstance(item, dict)}
    negative_names = {item.get("name") for item in data.get("negative_evals", []) if isinstance(item, dict)}
    missing = sorted(REQUIRED_EVAL_NAMES - names)
    if missing:
        return [f"evals/evals.json missing required evals: {missing}"]
    missing_negative = sorted(REQUIRED_NEGATIVE_EVAL_NAMES - negative_names)
    if missing_negative:
        return [f"evals/evals.json missing required negative evals: {missing_negative}"]
    if not (ROOT / "evals/forward-tests.md").exists():
        return ["evals/forward-tests.md is required for no-leak forward-test protocol"]
    return []


def main() -> int:
    errors = (
        check_frontmatter()
        + check_banned()
        + check_script_references()
        + check_skill_hygiene()
        + check_reference_tocs()
        + check_scope_contract()
        + check_runtime_subset()
        + check_evals()
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("opc-delivery skill rule check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
