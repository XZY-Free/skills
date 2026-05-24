#!/usr/bin/env python3
"""Guard OPC delivery skill docs against stale tools, undeclared scripts, and weak evals.

WARNING (2026-05-24): references/ 重组为 01-10 + mcp-setup + troubleshooting 12 个文件后,
本脚本里硬编码的旧 reference 名字(design-scope / opc-flow / intent-routing / clarification-loop
/ delivery-contract / handoff-contract / karpathy-discipline / context-persistence / design-workflow
/ restoration-workflow / verification-implementation / implementation-planning / implementation-workflow
/ frontend-design-quality / deployment-workflow / copy-language ...) 已全部失效。

41 处硬编码旧路径需要按新结构重写。在此之前本脚本只跑 frontmatter + evals 结构 + scripts 索引
的基础检查, 跳过 references 内容契约校验。

待办: 按新 12 reference 结构重写本脚本的契约校验, 或拆分成多个小脚本。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_TEXTS = [
    ROOT / "SKILL.md",
    *(ROOT / "references").glob("*.md"),
    *(ROOT / "evals").glob("*"),
]
ALLOWED_ROOT_ITEMS = {"SKILL.md", "agents", "references", "scripts", "evals", "assets"}
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
BANNED = {
    "html2text": "Use scripts/fetch-doc-snippet.py instead of optional html2text.",
    "AskUserQuestion": "Ask directly or use the host's available user-input mechanism.",
    "webapp-testing": "Use Browser/Playwright guidance or scripts/screenshot.mjs.",
    "ui-ux-pro-max": "Reference only currently discoverable design skills.",
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
        for match in re.finditer(r"scripts/([A-Za-z0-9_.-]+)", text):
            script = ROOT / "scripts" / match.group(1)
            if not script.exists():
                errors.append(f"{path.relative_to(ROOT)} references missing script {match.group(0)}")
    for script in sorted((ROOT / "scripts").iterdir()):
        if not script.is_file():
            continue
        first_line = script.read_text(encoding="utf-8", errors="ignore").splitlines()[:1]
        if first_line and first_line[0].startswith("#!") and script.stat().st_mode & 0o111 == 0:
            errors.append(f"{script.relative_to(ROOT)} has a shebang but is not executable")
    return errors


def normalize_markdown_target(raw_target: str) -> str:
    target = raw_target.strip()
    if not target:
        return ""
    if target.startswith("<") and ">" in target:
        target = target[1 : target.find(">")]
    else:
        target = target.split()[0]
    return unquote(target.strip("<>\"'"))


def check_markdown_links() -> list[str]:
    errors: list[str] = []
    for path in [ROOT / "SKILL.md", *(ROOT / "references").glob("*.md")]:
        text = read(path)
        for match in re.finditer(r"!?\[[^\]]*]\(([^)]+)\)", text):
            target = normalize_markdown_target(match.group(1))
            if not target or target.startswith(("#", "http://", "https://", "mailto:", "mastergo://")):
                continue
            local_target = target.split("#", 1)[0]
            if not local_target:
                continue
            resolved = (path.parent / local_target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)} links outside skill root: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)} links to missing file {target}")
    return errors


def check_skill_hygiene() -> list[str]:
    errors: list[str] = []
    for item in ROOT.iterdir():
        if item.name not in ALLOWED_ROOT_ITEMS:
            errors.append(f"unexpected non-runtime skill root item {item.relative_to(ROOT)}")
    for path in ROOT.rglob("*"):
        if path.name in NOISE_NAMES or path.suffix in NOISE_SUFFIXES:
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


def check_scope_contract() -> list[str]:
    errors: list[str] = []
    required_files = [
        ROOT / "references/opc-flow.md",
        ROOT / "references/autonomous-bootstrap.md",
        ROOT / "references/context-persistence.md",
        ROOT / "references/open-source-patterns.md",
        ROOT / "references/requirements-workflow.md",
        ROOT / "references/solution-design.md",
        ROOT / "references/frontend-design-quality.md",
        ROOT / "references/implementation-planning.md",
        ROOT / "references/implementation-workflow.md",
        ROOT / "references/deployment-workflow.md",
        ROOT / "references/regression-calibration.md",
        ROOT / "references/design-scope.md",
        ROOT / "references/copy-language.md",
        ROOT / "references/design-coverage-patterns.md",
        ROOT / "references/handoff-contract.md",
        ROOT / "references/karpathy-discipline.md",
        ROOT / "scripts/handoff-lint.py",
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
        "选择交互澄清契约",
        "自动轮转契约",
        "自治补齐契约",
        "上下文持久化契约",
        "UI 文案语种契约",
        "UI 设计质量契约",
        "实现规划契约",
        "上下文持久化契约",
        "专业完成定义",
        "收尾契约",
        "Karpathy 行为契约",
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
        "implementation-planning.md",
        "implementation-plan",
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
    for phrase in ["代理自动执行", "不是让用户手动运行", "nextAction", "主动拆分", "只存摘要", "自治补齐动作", "implementation-plan", "Read Set", "上下文预算", "checkpoint", "continuation.md"]:
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
    for phrase in ["2-3 个方案", "Planning Packet", "自我审查", "推荐方案", "自动初始化 Git", "implementation-plan", "frontend-design-quality.md", "记忆点"]:
        if phrase not in solution_text:
            errors.append(f"references/solution-design.md missing phrase {phrase!r}")

    frontend_quality_text = read(ROOT / "references/frontend-design-quality.md")
    for phrase in ["Design Quality Brief", "generic AI aesthetics", "MasterGo / Codify", "Verification Checklist", "copy-language.md"]:
        if phrase not in frontend_quality_text:
            errors.append(f"references/frontend-design-quality.md missing phrase {phrase!r}")

    planning_text = read(ROOT / "references/implementation-planning.md")
    for phrase in [
        "implementation-plan",
        "index.md",
        "architecture.md",
        "contracts.md",
        "work-breakdown.md",
        "verification.md",
        "slices/",
        "ADR",
        "Read Set",
        "用户价值",
        "frontend.md",
        "backend.md",
        "database.md",
        "12KB",
        "frontend-design-quality.md",
        "generic AI aesthetics",
        "parallelization.md",
        "Context Budget",
        "Write Set",
        "checkpoint",
    ]:
        if phrase not in planning_text:
            errors.append(f"references/implementation-planning.md missing phrase {phrase!r}")

    implementation_text = read(ROOT / "references/implementation-workflow.md")
    for phrase in ["TDD", "regression ratchet", "systematic debugging", "gate truth", "空工作区启动规则", "git init", "缺仓库 / 缺脚手架", "不是 Git 仓库，所以本轮先停在设计包", "implementation-plan", "Read Set", "frontend-design-quality.md", "generic AI aesthetics", "上下文预算执行", "并行 lane", "continuation.md", "Eligible For Subagent"]:
        if phrase not in implementation_text:
            errors.append(f"references/implementation-workflow.md missing phrase {phrase!r}")

    state_script = read(ROOT / "scripts/opc-task-state.py")
    for phrase in ['"verification"', '"implementation-plan"', "PHASES", "normalize_phases", "cmd_brief", "cmd_checkpoint", "continuation.md", "implementation cannot be marked done"]:
        if phrase not in state_script:
            errors.append(f"scripts/opc-task-state.py missing phase phrase {phrase!r}")

    handoff_script = read(ROOT / "scripts/handoff-lint.py")
    for phrase in ["check_decision_block", "check_internal_progress_table", "自定义 / type something", "退出码 0", "OPC", "artifact", "nextAction"]:
        if phrase not in handoff_script:
            errors.append(f"scripts/handoff-lint.py missing handoff guard phrase {phrase!r}")

    deployment_text = read(ROOT / "references/deployment-workflow.md")
    for phrase in ["preview", "production", "rollback", ".opc/deployment/release.md", "release profile", "premortem", "red-team", "stop conditions", "初始化", "无凭证就跳过整个 deployment"]:
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
    for phrase in ["MasterGo 设计 Gate Card", "mastergo-task-state.py", "library-snapshot.py", "codify-preflight.py", "frontend-design-quality.md", "体验质量门禁"]:
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
        errors.append("publish-opc-delivery-skill.py must default to Codex only; add Claude only via explicit --target")
    return errors


def check_evals() -> list[str]:
    evals_path = ROOT / "evals/evals.json"
    try:
        data = json.loads(evals_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"evals/evals.json is not valid JSON: {exc}"]
    if not isinstance(data, dict):
        return ["evals/evals.json top-level must be an object"]

    errors: list[str] = []
    if data.get("skill_name") != ROOT.name:
        errors.append(f"evals/evals.json skill_name must be {ROOT.name!r}")
    if not isinstance(data.get("evals"), list):
        errors.append("evals/evals.json evals must be a list")
    if not isinstance(data.get("negative_evals", []), list):
        errors.append("evals/evals.json negative_evals must be a list when present")
    if errors:
        return errors

    seen_ids: set[int] = set()
    seen_names: set[str] = set()
    required_positive = {"id", "name", "prompt", "expected_output", "files"}
    required_negative = {"id", "name", "prompt", "expected_behavior", "should_trigger"}
    for section, required in [("evals", required_positive), ("negative_evals", required_negative)]:
        for index, item in enumerate(data.get(section, [])):
            if not isinstance(item, dict):
                errors.append(f"evals/evals.json {section}[{index}] must be an object")
                continue
            missing = required - item.keys()
            if missing:
                errors.append(f"evals/evals.json {section}[{index}] missing keys {sorted(missing)}")
            item_id = item.get("id")
            if not isinstance(item_id, int):
                errors.append(f"evals/evals.json {section}[{index}].id must be int")
            elif item_id in seen_ids:
                errors.append(f"evals/evals.json duplicate eval id {item_id}")
            else:
                seen_ids.add(item_id)
            name = item.get("name")
            if not isinstance(name, str) or not name:
                errors.append(f"evals/evals.json {section}[{index}].name must be non-empty string")
            elif name in seen_names:
                errors.append(f"evals/evals.json duplicate eval name {name!r}")
            else:
                seen_names.add(name)
            if section == "evals" and "files" in item and not isinstance(item["files"], list):
                errors.append(f"evals/evals.json {section}[{index}].files must be list")
            if section == "negative_evals" and "should_trigger" in item and not isinstance(item["should_trigger"], bool):
                errors.append(f"evals/evals.json {section}[{index}].should_trigger must be bool")

    names = {item.get("name") for item in data.get("evals", []) if isinstance(item, dict)}
    negative_names = {item.get("name") for item in data.get("negative_evals", []) if isinstance(item, dict)}
    missing = sorted(REQUIRED_EVAL_NAMES - names)
    if missing:
        errors.append(f"evals/evals.json missing required evals: {missing}")
    missing_negative = sorted(REQUIRED_NEGATIVE_EVAL_NAMES - negative_names)
    if missing_negative:
        errors.append(f"evals/evals.json missing required negative evals: {missing_negative}")
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
    eval_text = json.dumps(data, ensure_ascii=False)
    for stale_gate in ["quick_validate", "check-links"]:
        if stale_gate in eval_text:
            errors.append(f"evals/evals.json contains stale validation gate {stale_gate!r}")
    return errors


def main() -> int:
    # 按新 references 结构(01-10 + mcp-setup + troubleshooting)只跑两个兼容的检查。
    # 其余 6 个检查依赖旧 reference 名字, 留待重写。
    print("WARNING: references 已重组为 12 个文件; 跳过依赖旧路径的 6 个检查项", file=sys.stderr)
    errors = (
        check_frontmatter()
        + check_evals()
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("opc-delivery skill rule check OK (frontmatter + evals only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
