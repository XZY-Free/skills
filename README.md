<div align="center">

# 🧰 Skills

**AI Coding Agent 可复用的 markdown skill 集合**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Maintainer](https://img.shields.io/badge/维护-华润雪花啤酒智数AI团队-DC2626.svg)](#致谢)
[![Skills](https://img.shields.io/badge/Skills-1-7C3AED.svg)](#已收录的-skills)

**简体中文** · [English](README.en.md)

</div>

---

## 这是什么

一个把日常工作流、领域知识、外部平台对接沉淀成可复用 [markdown skill](https://docs.claude.com/en/docs/claude-code/skills) 的仓库。每个 skill 都是一个独立子目录，可以装进任何兼容的 AI Coding Agent —— [Claude Code](https://docs.claude.com/en/docs/claude-code/quickstart) · [Codex CLI](https://github.com/openai/codex) · [Cursor](https://cursor.com) · 其它支持 markdown skill loader 的客户端。

skill 是 markdown + 配套素材（references / evals / assets），不依赖云服务、不绑 IDE、不需要订阅，**复制粘贴就走**。

> 🌱 **好用的都可以放进来**。看下方"贡献新 skill"。

## 已收录的 Skills

| Skill | 一句话简介 | 入口 |
|---|---|---|
| 🚀 **opc-delivery** | 把一句话业务想法做成能登录、能操作的真实页面，带方案、验证和部署证据 | [SKILL.md](opc-delivery/SKILL.md) |

> 仓库目前只有 1 个 skill。后续会按业务场景持续增加，命名约定见下方"贡献新 skill"。

### 了解 opc-delivery

想看它把"一句话需求"推进成可上线产品的全貌，有两个入口：

- 🌐 **方案官网** — <http://119.45.222.120/plans/>，8 屏滑动叙事：是什么、谁用、做出来什么、怎么开口、怎么推进、边界、产品化、总结
- 📖 **方案文档** — <http://119.45.222.120/plans/doc>，四个核心设计 + 七阶段流程 + 停下来的边界 + 怎么用怎么判断

skill 源码看 [`opc-delivery/SKILL.md`](opc-delivery/SKILL.md) 和 [`opc-delivery/references/`](opc-delivery/references/)。

## 通用安装方式

每个 skill 的具体安装步骤看自己的 `SKILL.md` 和 `references/`，通用模式都是：

```bash
# 1. clone 本仓库
git clone <repo-url> skills && cd skills

# 2. 把想用的 skill 复制到 agent 的 skills 目录
#    Claude Code:
cp -r <skill-name> ~/.claude/skills/
#    Codex CLI:
cp -r <skill-name> ~/.codex/skills/
#    Cursor / 其它:见各 agent 文档

# 3. 重启 agent 会话，让它发现新 skill
```

如果 skill 需要额外的 MCP / token / 配置，看 skill 自己的 `SKILL.md` 或配置 reference。

## 贡献新 Skill

欢迎贡献新 skill。每个 skill 都是 `<skill-name>/` 子目录，至少包含：

```
<skill-name>/
├── SKILL.md            # 入口，frontmatter 含 name + description + 触发关键词
├── agents/
│   └── openai.yaml     # 可选但推荐，UI metadata
├── references/         # 按需触发的详细指引（避免上下文爆炸）
│   └── *.md
├── scripts/            # 可选，确定性检查 / 转换脚本
├── evals/
│   └── evals.json      # 评测用例
└── assets/             # 可选，运行时真正需要的模板 / 资源
```

参考 `opc-delivery/` 作为完整范本。详细贡献流程、SKILL.md 规范、commit / PR 流程见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

快速入口:

- **MCP / skill 报错** → 用 [MCP 错误模板](.github/ISSUE_TEMPLATE/mcp_error.yml) 开 issue
- **新 skill 提案** → 用 [feature 模板](.github/ISSUE_TEMPLATE/feature_request.yml) 先讨论用例
- **PR** → 看 [PR 模板](.github/PULL_REQUEST_TEMPLATE.md),描述测试方式

## 仓库结构

```
.
├── README.md / README.en.md     # 本文件:skills 集合索引
├── LICENSE                       # Apache-2.0
├── SECURITY.md                   # 通用安全策略(token 处理等)
├── CLAUDE.md                     # 给 Claude Code 的仓库级提示
├── .github/                      # issue / PR 模板
└── opc-delivery/                 # ← 第一个 skill
    ├── SKILL.md
    ├── agents/
    ├── references/
    ├── evals/
    └── scripts/
```

## 安全

涉及 token / 凭据的 skill 共用一份 [`SECURITY.md`](SECURITY.md) 准则：本地保存、绝不复用、绝不进版本控制、脱敏回显。

## License

[Apache License 2.0](LICENSE)


## 致谢

- 华润雪花啤酒智数 AI 团队 资源支持
- [Anthropic](https://www.anthropic.com) —— [Skills 规范](https://docs.claude.com/en/docs/claude-code/skills) 的提出者
- 所有提 issue、提 PR、分享用例的早期用户 —— 让仓库长出 v0.2 及以后的方向
