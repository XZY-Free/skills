# 变更日志 / Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 规范,
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

[English version](CHANGELOG.en.md)

---

## [Unreleased]

> 即将打 `v0.1.0-alpha` tag 时,把本节内容剪切到下方新建的 `[0.1.0-alpha] - YYYY-MM-DD` 标题下,
> 并在顶部重建一个空的 `[Unreleased]` 节。

### 新增

- **首个 skill `opc-delivery`**:面向 OPC 一人公司式交付,
  把"粗业务需求 → PRD → UI 设计 → 前端实现 → 验证 → 部署"封装成端到端 markdown skill
  - 全流程阶段门禁:需求、方案、MasterGo/Codify 设计、Magic 还原、前端实现、CI/CD 部署、已上线需求回放校准
  - 保留 MasterGo 双 MCP(Codify + Magic)作为设计和 D2C 子流程
  - references 覆盖 mcp-setup / intent-routing / requirements / solution / design /
    implementation / deployment / calibration / verification / troubleshooting / update-flow
  - 默认企业级实现 + opt-in 快速复刻模式
  - evals.json 覆盖 OPC 全流程与 MasterGo 子流程
- **仓库元信息**:README.md / README.en.md(双语)、LICENSE(Apache-2.0)、
  SECURITY.md、CLAUDE.md、.gitignore
- **GitHub 模板**:bug_report / mcp_error / feature_request / config + PR 模板
- **opc-delivery skill 的视觉素材**:5 张 SVG(efficiency-comparison / how-it-works /
  quick-start / skill-structure / roadmap)
- **opc-delivery skill 的 README**:中英双语,含 SVG 内嵌
- **examples 脚手架**:`opc-delivery/examples/` 含 `_template/` 完整模板,
  v0.2 会补 5 个真实样例
- **CONTRIBUTING.md / CONTRIBUTING.en.md**:贡献流程、SKILL.md 规范、
  commit / PR 约定
- **scripts/** 仓库校验脚本:
  - `check-links.py` — markdown 内部链接 + 图片路径校验
  - `check-svgs.py` — SVG XML 合法性校验
  - `check-skill-frontmatter.py` — SKILL.md frontmatter 校验
  - `check-evals.py` — evals.json schema 校验
  - `run-evals.py` — 从 evals.json 生成 BENCHMARK.md 骨架
- **CI(`.github/workflows/ci.yml`)**:push / PR 时自动跑四个校验脚本
- **opc-delivery/BENCHMARK.md**:由 `run-evals.py` 生成的骨架,等首次完整复测填数据
- **opc-delivery 方案介绍页**:8 屏滑动官网 + 方案文档双入口部署上线,README 提供链接

### 已知限制

- 暂无 demo GIF / 视频(P0 阶段定位为"看起来不业余",demo 留给 v0.2)
- 暂无真实样例(只有 `_template/`,v0.2 补)
- BENCHMARK 数字未实测(骨架已落地,等维护者跑完填数据)

---

<!--
版本历史从下方开始。tag 时把 [Unreleased] 内容移过来:

## [0.1.0-alpha] - YYYY-MM-DD

### 新增
- ...

### 变更
- ...

### 修复
- ...
-->
