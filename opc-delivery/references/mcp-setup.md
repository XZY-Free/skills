# 双 MCP 安装与配置(Codify + MasterGo Magic)

## 目录

- [核心策略](#核心策略)
- [总流程](#总流程)
- [索取 token 的标准话术](#索取-token-的标准话术原话照搬不许只要-token)
- [Claude Code](#claude-code)
- [Codex CLI](#codex-cli)
- [Cursor](#cursor)
- [VSCode / 其它 IDE](#vscode--其它-ide)
- [单装分支](#单装分支)
- [Codify bridge URL](#codify-bridge-url)
- [权限提示](#权限提示)

## 核心策略

本文件假设你已熟悉 SKILL.md 的 [🔐 token 安全契约](../SKILL.md#-token-安全契约)、
[🙋 用户行动契约](../SKILL.md#-用户行动契约) 与
[交付物契约](../SKILL.md#交付物契约)。在此基础上,MCP 配置阶段有三条具体行为:

- **默认双装**:两个 MCP 一起配,因为设计 ↔ 还原工作流经常来回切换;
- **当前宿主配置才是事实源**:`tool_search` / 会话里暴露出的 `mcp__*` 工具只能说明
  当前运行时看见了某个工具入口,**不能证明当前宿主已经配置了用户自己的 token**。
  同一台机器上其它宿主(例如 Claude Code)的配置不能证明当前宿主(例如 Codex)可用——
  这是 token 安全契约里"当前宿主隔离"的具体落实;
- **用户主动说"只装一个" → 听用户的**,把另一个标记为暂不可用,真用上再回来配;
- 写入位置只能是当前宿主的 user-scope 本地配置文件
  (`~/.claude.json` / `~/.codex/config.toml` / `~/.cursor/mcp.json`),不进版本控制。
- **不做本地替代交付**:用户要的是 MasterGo 画布成果时,缺 MCP / token / 当前会话工具
  未加载就是阻塞;不要改成本地 Markdown、HTML、Figma、截图或 Codify prompt 交付。

## 总流程

1. **先确认当前正在运行的宿主 CLI**:能从当前会话判断 Codex / Claude Code / Cursor 时,
   直接运行 `scripts/mandatory/check-mcp-config.py --host codex|claude|cursor`;只有当前会话上下文
   不明确时才运行 `--host auto`,脚本仍无法判断时再问用户,不要靠其它宿主的配置猜;
2. 只检查当前宿主的 MCP 配置文件,只汇报 token 是否存在/是否像占位符,不要打印明文 token;
3. 再检测工具列表里是否存在 `mcp__codify__*` 和 `mcp__mastergo-magic-mcp__*`;
4. 按"配置文件状态 + 工具暴露状态"分类处理(见下表);
5. 缺配置就用下面的标准话术告诉用户 token 用途、获取路径、保存位置和重启要求,
   再跑对应宿主的配置脚本;
6. 提醒用户 `/exit` 重启会话后再继续。

如果用户已经把完整 token / key 贴到聊天里,不要回显明文。只做脱敏确认,并提醒:
该 key 已进入会话记录,建议配置成功后在对应平台 revoke / rotate 一次。

| 配置文件 | 工具入口 | 判定 | 动作 |
|---|---|---|---|
| 无对应 server / token 缺失 / token 是 `<USER_...>` 占位符 | 有或无 | **未正确配置** | 不要调用工具;先配置 token |
| 有真实 token | 无工具入口 | 已配置但本会话未加载 | 提醒重启宿主会话 |
| 有真实 token | 有工具入口 | 可以调用 | 报错再按 troubleshooting 分类 |

**禁止误判**:`tool_search` 搜到 `mcp__mastergo_magic_mcp__mcp__getDsl`
不等于用户已配置 MasterGo MCP。没有本地配置证据时,先查配置文件,不要直接调工具。
更具体地说:如果当前会话在 Codex,即使 `~/.claude.json` 已经配置了 MasterGo,
也不能据此调用 Codex 里的 MCP;必须检查 `~/.codex/config.toml`。

**禁止降级交付**:发现未正确配置时,不要说"我先给你一份本地设计蓝图 /
可粘贴到 Codify 的提示词"并结束。正确输出是:说明当前缺哪个 MCP / token / 重启,
给配置步骤,并明确"配置完成后我会继续推送到 MasterGo"。

配置任务本身的完成标准:
- 配置文件已写入当前宿主 user-scope;
- token 已脱敏确认不是占位;
- 用户已重启或当前会话工具已连通;
- 仍需重启时只能说"配置已写入,待重启加载",不能说 MCP 已可用。
- 重启 / reconnect 后继续原任务时,先复述原始目标;若是设计任务,恢复
  [05-mastergo.md](05-mastergo.md#mastergo-设计-gate-card) 的覆盖 brief,再继续写入或验证。

### 配置文件快速检查

只检查结构和 token 是否缺失/占位,不要把 token 明文输出给用户。

优先用脚本并显式传当前宿主:

```bash
python3 <skill-dir>/scripts/mandatory/check-mcp-config.py --host codex
python3 <skill-dir>/scripts/mandatory/check-mcp-config.py --host claude
python3 <skill-dir>/scripts/mandatory/check-mcp-config.py --host cursor
python3 <skill-dir>/scripts/mandatory/check-mcp-config.py --host codex --check-network
```

如果当前宿主实在无法判断,再用 auto 兜底:

```bash
python3 <skill-dir>/scripts/mandatory/check-mcp-config.py --host auto
```

| 宿主 | 检查位置 |
|---|---|
| Codex | `~/.codex/config.toml` 里的 `[mcp_servers.mastergo-magic-mcp]` / `[mcp_servers.codify]` |
| Claude Code | `~/.claude.json` 里的 MCP server 配置,或 `claude mcp list` |
| Cursor | `~/.cursor/mcp.json` 或项目 `.cursor/mcp.json` |

如果多个宿主配置都存在,先用当前运行环境判断宿主:
- Codex App / Codex CLI / 当前上下文含 `.codex` 运行面 → 只查 Codex 配置;
- Claude Code 会话 / `claude mcp list` 对当前会话有效 → 只查 Claude 配置;
- Cursor 会话 → 只查 Cursor 配置。

无法唯一判断当前宿主时,问用户一句:"你现在是在 Codex、Claude Code 还是 Cursor 里用 MasterGo?"
不要用其它宿主的已有配置代替当前宿主配置。

占位符包括:`<USER_MASTERGO_TOKEN>`、`<USER_CODIFY_KEY>`、空字符串、`YOUR_TOKEN`,
以及明显不是用户 token 的示例值。发现占位符时按"未正确配置"处理。

---

## 索取 token 的标准话术(原话照搬,**不许只要 token**)

```
为了帮你接通 MasterGo,我需要你两个 token。请分别复制给我:

(1) MasterGo MCP token —— 给 Magic MCP 用(D2C 还原):
    官方帮助页: https://mastergo.com/help/MG/MCP
    当前官方路径:
    1. 打开 https://mastergo.com 并登录
    2. 进入个人设置
    3. 打开"安全设置"选项卡
    4. 找到"个人访问令牌"
    5. 点击"生成令牌",复制生成的 token
    
(2) Codify Access Key —— 给 Codify MCP 用(在画布上设计):
    具体获取入口以最新官方文档为准。我先 curl 一下官方说明再告诉你确切步骤,
    或者你已知就直接发我。

注意:
- 这两个 token 是机器本地保存,不会写进版本控制
- 我不会复用任何人的 token
- 如果你直接把完整 key 粘在聊天里,我会脱敏写入;配置成功后建议你轮换一次
- 我会写入当前宿主的本机配置文件,然后需要你重启会话加载 MCP
- 如果你只想装其中一个,告诉我跳过哪一个
```

如果 MasterGo token 路径和用户界面不一致,先重新查官方帮助页,再把最新步骤告诉用户:

```bash
curl -sL https://mastergo.com/help/MG/MCP -o /tmp/mg-mcp.html
python3 - <<'PY'
from pathlib import Path
html = Path('/tmp/mg-mcp.html').read_text(errors='ignore')
for key in ['获取MG_MCP_TOKEN', '个人设置', '安全设置', '个人访问令牌', '生成令牌']:
    print(key, 'FOUND' if key in html else 'MISSING')
PY
```

**Codify 的 access key 获取路径会变**,先 `bash + curl` 查:

```bash
# 1. Codify 官方 / 帮助页(若有)
curl -sL 'https://duckduckgo.com/html/?q=codify+mcp+access+key+获取' | head -100

# 2. npm registry 找 codify mcp 包,看 README
curl -sL https://registry.npmjs.org/-/v1/search?text=codify+mcp | jq '.objects[].package | {name, description, links}'
```

查到之后用查到的路径告诉用户,**不要凭印象给路径**。

---

## Claude Code

`user scope` = 全局,对所有项目生效。

### Magic MCP

```bash
claude mcp add --scope user --transport stdio mastergo-magic-mcp \
  -- npx -y @mastergo/magic-mcp \
     --token=<USER_MASTERGO_TOKEN> \
     --url=https://mastergo.com
```

### Codify MCP

```bash
# 注意:具体 npm 包名 / 启动参数以官方最新文档为准
# 先 curl 查包名,再填入下面
PKG=$(curl -sL https://registry.npmjs.org/-/v1/search?text=codify+mastergo | \
      jq -r '.objects[0].package.name')
echo "查到的 Codify MCP 包名:$PKG"

claude mcp add --scope user --transport stdio codify \
  -- npx -y "$PKG" \
     -e CODIFY_ACCESS_KEY=<USER_CODIFY_KEY>
```

如果 Codify 的启动方式不是 stdio + npx,改成 SSE / http transport 即可,
**先看官方文档,不要硬试 transport 类型**。

### 验证

```bash
claude mcp list | grep -E 'mastergo|codify'
# 期望两条都是 ✓ Connected
```

写入位置:`~/.claude.json`(user scope)或当前项目 `.mcp.json`(project scope)。

### Claude Code 参数顺序坑

- `--scope` / `--transport` 必须在服务器名**之前**,`--` 之后才是要执行的命令;
- 环境变量:统一 `-e KEY=VAL`,不是 `--env KEY=VAL`;
- token 走 `--token=` 参数还是环境变量,**看每个 MCP 包自己的 README**,别混。

---

## Codex CLI

编辑 `~/.codex/config.toml`,TOML 格式:

```toml
[mcp_servers.mastergo-magic-mcp]
command = "npx"
args = ["-y", "@mastergo/magic-mcp", "--token=<USER_MASTERGO_TOKEN>", "--url=https://mastergo.com"]
env = {}
# 可选:startup_timeout_ms = 10000

[mcp_servers.codify]
command = "npx"
# 包名以 curl npm registry 查到的为准
args = ["-y", "<codify-mcp-pkg>"]
env = { CODIFY_ACCESS_KEY = "<USER_CODIFY_KEY>", CODIFY_MCP_URL = "https://mcp.codify-api.com" }
```

Codex 没有 `mcp add` 子命令,只能直接编辑文件。重启 Codex 后 `/mcp` 查状态。

---

## Cursor

编辑 `~/.cursor/mcp.json`(全局)或项目根 `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mastergo-magic-mcp": {
      "command": "npx",
      "args": ["-y", "@mastergo/magic-mcp", "--token=<USER_MASTERGO_TOKEN>", "--url=https://mastergo.com"],
      "env": {}
    },
    "codify": {
      "command": "npx",
      "args": ["-y", "<codify-mcp-pkg>"],
      "env": {
        "CODIFY_ACCESS_KEY": "<USER_CODIFY_KEY>",
        "CODIFY_MCP_URL": "https://mcp.codify-api.com"
      }
    }
  }
}
```

Cursor 重启后在设置里检查 MCP 服务器状态。

---

## VSCode / 其它 IDE

绝大多数都是 JSON 格式 + 重启 IDE。**没有固定路径**:

1. 先让用户告诉你 IDE 名字;
2. `curl -sL 'https://duckduckgo.com/html/?q=<IDE名>+MCP+config+path'` 查;
3. 拿到路径再让用户编辑。

---

## 单装分支

如果用户明确只装一个:

| 装 | 缺另一个的后果 |
|---|---|
| 只装 **Magic** | 走还原流没问题。**不能在画布上设计**(没有 Codify 工具),用户后续说"帮我加一个按钮到画布"这类要求时,先告诉他需要装 Codify,然后回阶段 0 |
| 只装 **Codify** | 走设计流没问题。**不能批量 D2C 还原**(单图层可用 `get_selection_code`,但效率低),用户后续说"把整站还原"时,先告诉他装 Magic 更顺,然后回阶段 0 |

不要因为用户一开始说"只装一个"就永久放弃另一个 —— 遇到真需要的时候再回来,
不要硬用错的工具。

## Codify bridge URL

Codify MCP 支持两类 URL，具体参数名以当前包 README / 官方文档为准:

| 类型 | URL | 何时使用 |
|---|---|---|
| 官方远端 | `https://mcp.codify-api.com` | 默认路径 |
| 本地 bridge | `http://127.0.0.1:9999` | 远端 TLS/网络不可达、本地 Go server 已启动、团队要求走本地转发 |

本地 bridge 健康检查:

```bash
curl -i http://127.0.0.1:9999/
python3 <skill-dir>/scripts/mandatory/check-mcp-config.py --host codex --check-network
```

Codex TOML 示例(按实际包参数调整):

```toml
[mcp_servers.codify]
command = "npx"
args = ["-y", "<codify-mcp-pkg>", "--url=http://127.0.0.1:9999"]
env = { CODIFY_ACCESS_KEY = "<USER_CODIFY_KEY>" }
```

`scripts/mandatory/check-mcp-config.py` 会识别 `--url=...`、`CODIFY_MCP_URL`，并标记
`url_type` 为 `remote` / `local` / `missing` / `custom`。本地 URL 不默认联网探测；
只有加 `--check-network` 时才会尝试访问。

---

## 权限提示

- **Magic MCP `getDsl` 等读操作**:需要 token 所属账号在该 MasterGo 文件的团队里
  是**团队版及以上**且持有**编辑席位或研发席位**;免费版 / 查看席位会报 `10003`;
- **Codify MCP `design` 等写操作**:看 Codify 后台的配额(`get_user_info` 能查),
  团队库相关操作需要文件已订阅团队库;
- 报权限错先确认这两个层面,再确认 token 本身是否过期。

详见 [troubleshooting.md](troubleshooting.md#magic-排障) 与
[troubleshooting.md](troubleshooting.md#codify-排障) 的权限错误小节。
