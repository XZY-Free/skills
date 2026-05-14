# 安全策略 / Security Policy

## 报告漏洞 / Reporting a Vulnerability

如果你发现安全问题（特别是涉及 token 泄漏 / 提权 / RCE / 数据外发等），请**不要**直接开 issue。

- 邮件: `security@<your-domain>`（仓库 owner 部署后请替换）
- 或在 GitHub 通过 [Private Security Advisory](https://github.com/sunshine/skills/security/advisories/new) 私下报告

我们承诺：
- **72 小时内**初步回复
- 确认漏洞后协调修复时间表
- 修复后在 advisory 中致谢报告者（除非你要求匿名）

## Token 处理承诺

本 skill 涉及两类敏感凭据：

- **MasterGo MCP token**（给 Magic MCP）
- **Codify Access Key**（给 Codify MCP）

我们对这两类凭据的处理原则与 [`opc-delivery/references/mcp-setup.md`](opc-delivery/references/mcp-setup.md) 严格一致：

1. **每用户每机器各自索取**，绝不复用历史 token，绝不写硬编码默认值
2. token 只写入**用户机器本地**的 user-scope 配置文件：
   - Claude Code: `~/.claude.json`
   - Codex CLI: `~/.codex/config.toml`
   - Cursor: `~/.cursor/mcp.json`
3. **绝不**把 token 提交到任何版本控制（仓库根 `.gitignore` 已排除 `.claude/` / `.codex/`）
4. skill 收到 token 后**脱敏回显**（如 `mg_********xxxx`），原文不出现在对话日志中
5. token 只发往对应 MCP server（`@mastergo/magic-mcp` 和 Codify 官方 server），不会发到任何第三方

## 已知风险点 / Known Considerations

- **MCP server 自身的网络行为**不在本 skill 控制范围内。MasterGo Magic MCP 和 Codify MCP 是上游软件，请自行评估它们的隐私和数据处理策略
- **D2C 还原过程会本地写入 `.codify/` 目录**（设计 token、API 文档缓存等），请确保该目录在你的 `.gitignore` 里
- **企业级实现模式会扫描 `.codify/api-docs/`**，里面如果有真实接口文档，避免在公开仓库提交

## 支持的版本

| 版本 | 安全更新 |
|---|---|
| v0.1.x (alpha) | ✅ 当前活跃 |

未来发布 v1.0 后，将明确长期支持版本策略。
