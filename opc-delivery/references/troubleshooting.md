# troubleshooting — MCP / 渲染 / 配置异常

任何 MCP 报错、行为异常、不熟字段、配置卡住 → **先 `bash + curl` 拉官方文档 / npm registry / DuckDuckGo, 再决定怎么提示用户**。绝不允许凭印象答用户。

## 何时读

- Magic 工具(`getDsl` / `getD2c` / `getMeta`)报错
- Codify 工具(`design` / `agent_*` / `get_*`)报错
- D2C 渲染问题(蒙版/字体/胶囊/SVG → 看 [07b-restore-verify.md](07d-restore-patches.md#渲染补丁))
- MCP 配置卡住、token 占位、本地 bridge / 远端 URL 异常 → 看 [mcp-setup.md](mcp-setup.md)

## 目录

- [遇错先查文档](#遇错先查文档)
- [需要用户行动时的输出契约](#需要用户行动时的输出契约)
- [错误路由表](#错误路由表)
- [Magic 排障](#magic-排障)
- [Magic Request too large](#magic-request-too-large)
- [Codify 排障](#codify-排障)
- [DSL 看不到画布上画的原型连线](#dsl-看不到画布上画的原型连线)

---

## 遇错先查文档

```bash
# 1. MasterGo 官方帮助页
python3 <skill-dir>/scripts/helpers/fetch-doc-snippet.py https://mastergo.com/help/MG/MCP \
  --keyword "个人访问令牌" --keyword "生成令牌" --keyword "发送数据"

# 2. magic-mcp 源码 / README
curl -sL https://registry.npmjs.org/@mastergo/magic-mcp/latest | jq -r '.dist.tarball'
TARBALL=$(curl -sL https://registry.npmjs.org/@mastergo/magic-mcp/latest | jq -r '.dist.tarball')
curl -sL "$TARBALL" -o /tmp/mg.tgz && tar -xzf /tmp/mg.tgz -C /tmp/mg-mcp-src

# 3. Codify MCP 包名 / 文档
curl -sL https://registry.npmjs.org/-/v1/search?text=codify | jq '.objects[].package | {name, description, links}'

# 4. DDG 搜社区案例 / 报错关键词
curl -sL 'https://duckduckgo.com/html/?q=mastergo+mcp+<错误关键词>'
```

---

## 需要用户行动时的输出契约

任何报错让用户动手时, 回复必须同时包含**为什么 / 依据 / 具体步骤 / 完成后继续 / 兜底**五项。

禁止只说: "把 token 发我" / "去 MasterGo 点发送数据" / "订阅一下组件库" / "把接口文档给我" / "截图发我" — 都必须改成带路径和下一步的可执行说明。

---

## 错误路由表

| 报错来源 | 跳哪一节 |
|---|---|
| Magic 工具(`getDsl` / `getD2c` / `getMeta`) | [Magic 排障](#magic-排障) |
| Codify 工具(`design` / `agent_*` / `get_*`) | [Codify 排障](#codify-排障) |
| 渲染问题(蒙版/字体/胶囊/SVG) | [07d-restore-patches.md 渲染补丁](07d-restore-patches.md#渲染补丁) |
| API 文档格式 / 字段映射 / 溯源汇报 | [06c-api-wiring.md](06c-api-wiring.md) |
| MCP 配置 / token 占位 / 本地 bridge | [mcp-setup.md](mcp-setup.md) |

---

## Magic 排障

### A.1 `Could not extract layerId from URL`

**症状**: 给的 URL 调 `getDsl` 报这个。

**根因**: URL 里没 `layer_id=` 参数。常见: 短链 `mastergo.com/goto/xxx?file=...` 没在画布选中状态下生成; 文件根 URL `mastergo.com/file/<fileId>`。

**修法**: 让用户在 MasterGo 画布**单击目标 Frame** 让它高亮选中 → 直接复制地址栏 URL(会自动带 `&layer_id=xxx%3Ayyy`); 或图层面板右键 Frame → "复制链接"。

### A.2 `Request too large (max 20MB)` — Magic 拉根容器

见下文 [Magic Request too large](#magic-request-too-large)。

### A.3 `🔒 禁止访问 / 10003`(权限错误)

**症状**: 调任何 Magic 工具报 `code: "10003"`。

**先判定配置是否真的存在**:

1. 检查当前宿主配置文件:
   - Codex: `~/.codex/config.toml`
   - Claude Code: `~/.claude.json` 或 `claude mcp list`
   - Cursor: `~/.cursor/mcp.json` / 项目 `.cursor/mcp.json`
2. 只确认是否存在 `@mastergo/magic-mcp` 和非占位 token, **不打印 token 明文**
3. 没有配置、token 为空、或仍是 `<USER_MASTERGO_TOKEN>` 这类占位 → **MCP 未正确配置**, 不是文件权限问题

**重要**: `tool_search` 搜到 `mcp__mastergo_magic_mcp__mcp__getDsl` **不能当作已配置证据**。它可能只是运行时暴露了工具 schema; 没有本地 token 配置时直接调用会得到没有诊断价值的 10003。

配置真实存在后, 10003 常见根因:

1. token 错(过期 / 用错账号 / 误粘贴)
2. token 所属账号在该 MasterGo 文件**不是团队版及以上**
3. token 所属账号在该团队**没有编辑席位或研发席位**

**修法**:

- 配置缺失/占位 → 回 [mcp-setup.md](mcp-setup.md) 重新配置, 重启会话
- 按官方帮助页重新生成 MCP token: https://mastergo.com/help/MG/MCP (MasterGo → 个人设置 → 安全设置 → 个人访问令牌 → 生成令牌)
- 让用户确认文件所在团队的席位类型
- 验证: 同账号 `get_user_info`(Codify) 能用 → 账号活的; 只有 Magic 报 10003 = 席位问题

### A.4 D2C 缓存: 设计变了但 HTML 一字不差

**症状**: 用户说改了设计稿, 重拉 D2C 后 HTML md5 跟旧的完全相同。

**根因**: D2C 在 MasterGo 服务端缓存, 缓存键是 contentId。设计师改了设计但还没触发"发送数据"重新生成。

**修法**:

1. 先拉 DSL(DSL 不缓存, 永远最新)
2. 跟旧 DSL diff 字节数和 hash 验证设计是否真的变了
3. 让用户在 MasterGo **重新点"发送数据"** 触发 D2C 重生成
4. 用新 `outDir`(避免本地资源混淆)重拉

### A.5 `getMeta` 返回 `<info></info>` 空

**症状**: 调 `getMeta(fileId, rootLayerId)` 期望拿站点目录, 结果空。

**根因**: 设计师没按 MasterGo 规范在根容器上注入 `meta` 和 `action` 字段。绝大多数文件都没有。

**修法**: 跳过 meta 工作流, 直接 `getDsl(rootLayerId)` 然后遍历 `children` 自己列出页面目录。

### A.6 `未找到该 contentId 对应的数据`

**症状**: `getD2c(contentId=..., ...)` 报这个。

**根因**: 用户还没在 MasterGo Codify 插件里对该 Frame 点过"发送数据"。

**修法**:

- 告诉用户**具体哪个 Frame** 需要发送(用 Frame name + layerId 指认)
- 说明依据: MasterGo 官方 MCP 文档 `mcp_getD2c` 流程要求先点击"发送数据"
- 给步骤: MasterGo 选中该 Frame → 打开 Codify / MCP 相关面板 → 点击"发送数据"
- 用户点完后重新拉 `getD2c(contentId=..., fileId=...)`
- 用户找不到按钮 → 让他发当前 MasterGo 右侧/插件面板截图继续定位入口

---

## Magic Request too large

**症状**: 拉根容器 DSL 报 `Request too large (max 20MB)`。

**根因**: 根容器 DSL 包含所有页面, 整体可能超 20MB。

**修法**:

- **不要**重试整体, 永远会失败
- 改成对每个 1440 子 Frame 单独 `getDsl(fileId, childLayerId)`, 单页通常 < 2MB
- 解析每页 DSL 单独处理 + diff

---

## DSL 看不到画布上画的原型连线

**症状**: 用户在 MasterGo Prototype 模式画了 Frame ↔ Frame 的连接线, 但 DSL 里 `interactive` 字段没新增。

**根因**: MasterGo MCP 的 DSL **不下发跨 Frame 原型连线**, 只下发**组件级 interactive**(比如输入框 hover 状态变体过渡)。检查 DSL 里既有的 `interactive` 节点, 会发现 `targetLayerId` 指向的是 `COMPONENT` 类型节点(变体), 不是 `FRAME` 类型(页面)。

**修法**:

- 向用户说明这是 MasterGo MCP 的**能力边界, 不是同步问题不是 bug**
- 让用户用自然语言告诉你跳转关系: 例 "首页的[请明天的年假]按钮 → /leave-with"
- 在代码里用 `<Link href="/leave-with">` 或 `router.push('/leave-with')` 手写

需要程序化判断:

```python
def find_node(dsl, target_id):
    if isinstance(dsl, dict):
        if dsl.get('id') == target_id: return dsl
        for v in dsl.values():
            r = find_node(v, target_id)
            if r: return r
    elif isinstance(dsl, list):
        for x in dsl:
            r = find_node(x, target_id)
            if r: return r

# find_node(...).get('type') == 'COMPONENT' → 变体过渡, 不是页面跳转
```

---

## Codify 排障

### B.1 `❌ 获取失败: 未找到 API 终结点或活跃连接`

**症状**: 几乎所有 Codify 工具(`get_library_list` / `design` / `agent_*`)报这个。

**根因**: Codify 插件跟 MCP 之间的 WebSocket 连接断了。常见触发: 用户关闭 MasterGo 标签页 / 关掉插件面板 / 浏览器刷新 / 插件面板状态指示灯不再是绿色 `● ONLINE` / 长时间无操作超时挂起。

**修法**: 让用户**确认 MasterGo 标签页还开着、插件面板还显示 `● ONLINE`** → 用户说"好了"之后重试。**不要重复重试, 每次都问用户确认状态**。

### B.2 `10003 禁止访问 / 配额不足`

**症状**: `design` / `get_component_info` 等写操作报权限或配额错。

**根因**: Codify Access Key 错 / 过期; 或账号配额(看 `get_user_info` 输出)用完。

**修法**:

- `get_user_info` 先看配额: "生成设计 / 获取代码"显示用完 → 告诉用户充值或升级
- 让用户回 Codify 后台重新复制 access key → 更新 MCP 配置文件 → **重启会话**

### B.3 `📋 代码列表为空`

**症状**: `get_code_list` 返回空。

**根因**: 用户没在 Codify 插件里对任何图层点过"复制代码 / 发送代码"按钮。**这不是 bug, 是正常状态**。

**修法**:

- 不要把"列表为空"当报错回答用户
- 想看单页 → 在画布选中, 用 `get_selection_code` 拉
- 想看整文件目录 → 走 Magic MCP `getDsl`, 不是 Codify

### B.4 团队组件库相关错误

| 报错 | 修法 |
|---|---|
| `团队库列表为空` | 当前 MasterGo 文件没订阅任何团队库。先查 MasterGo 团队库/资源库官方说明, 引导用户: 左侧面板 → 组件 → 资产 → 添加团队库; 找不到入口让他发侧栏截图 |
| `get_component_info` 报组件不存在 | 用户传的 `teamLibraryName` 拼错; 先 `get_library_list` 拿准确名称 |
| `var(--xxx)` 在生成的 HTML 里渲染不出来 | `variable.json` 没落盘 / 变量名拼错; 重跑 `get_component_info` |
| 自绘比例过高(组件没用上) | 看 `design` 返回里有没有"组件缺失原因"声明; 改 `buildStrategy` 或换更合适的库重跑 |

### B.5 contentId 相关

Codify 的 `get_code` 等工具需要 contentId(用户在插件里点复制按钮才生成)。

**不让用户复制 contentId**: 可通过 `get_code_list` 或 `get_selection_code` 走 layerId 路径。

### B.6 `design` 工具的 buildStrategy 拒绝继续

**症状**: `design(useComponentLibrary=true, ...)` 没传 `buildStrategy` 时报错要求二选一。

**根因**: Codify 规则强制每次调用都要明确策略。

**修法**: 按场景填:

- 后台 / 表单 / 业务页 → `full-components`
- 落地页 / 营销页 / 自定义视觉多 → `hybrid`

不确定时直接问用户。

### B.7 Codify 规范 / Tailwind 同步问题

**症状**: 本地 HTML 看起来正常, 同步到 MasterGo 后样式丢失、布局漂移, 或 Codify 提示需要按当前规范重写。

**根因**: 本地稿用了原生 CSS、`<style>`、外链 CSS 或运行时样式, 但当前 Codify 规范要求 Tailwind utility class / 可解析组件结构。

**修法**:

- 先运行 `get_codify_guidelines`, **不要凭旧经验猜 Codify 规范**
- 再运行 `get_user_info`, 确认账号、权限、配额和当前上下文
- 按 [05a-codify-design.md HTML 与 UI 文案合规](05a-codify-design.md#html-与-ui-文案合规) 把原生 CSS HTML 转成 Tailwind utility HTML
- 重新写入 MasterGo 后用 `get_design_diff` 或画布截图验证

### B.8 远端 TLS / 404 / 本地 bridge 未启动

**症状**: Codify MCP 初始化失败、远端 URL 报 TLS / 404 / connection refused, 或本地 `http://127.0.0.1:9999` 没响应。

**修法**:

- 先运行 `scripts/mandatory/check-mcp-config.py --host <当前宿主>`, 看 `url_type` 是 `remote` / `local` / `missing`
- 远端 URL 失败 → 确认当前包 README 要求的 URL 是否仍是 `https://mcp.codify-api.com`
- 本地 bridge 模式先跑 `curl -i http://127.0.0.1:9999/`; 连不上让用户启动本地 bridge / Go server, 重启宿主会话
- Go server 返回非 MCP 内容 → 记录响应摘要, **不要继续调写入工具**; 让用户发本地 bridge 启动日志或当前配置
