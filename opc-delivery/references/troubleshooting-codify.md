# Codify MCP 报错处理

## 目录

- [B. Codify MCP 报错](#b-codify-mcp-报错)
- [B.1 获取失败](#b1--获取失败-未找到-api-终结点或活跃连接)
- [B.2 10003 禁止访问 / 配额不足](#b2-10003-禁止访问--配额不足)
- [B.3 代码列表为空](#b3--代码列表为空)
- [B.4 团队组件库相关错误](#b4-团队组件库相关错误)
- [B.5 contentId 相关](#b5-contentid-相关)
- [B.6 buildStrategy 拒绝继续](#b6-design-工具的-buildstrategy-拒绝继续)
- [B.7 Codify 规范 / Tailwind 同步问题](#b7-codify-规范--tailwind-同步问题)
- [B.8 远端 TLS / 404 / 本地 bridge 未启动](#b8-远端-tls--404--本地-bridge-未启动)

## B. Codify MCP 报错

### B.1 `❌ 获取失败: 未找到 API 终结点或活跃连接`

**症状**:几乎所有 Codify 工具(`get_library_list` / `design` / `agent_*` 等)报这个。

**根因**:Codify 插件跟 MCP 之间的 WebSocket 连接断了。常见触发:
- 用户关闭了 MasterGo 标签页 / 关掉插件面板;
- 浏览器刷新 MasterGo 页面;
- 插件面板顶部的状态指示灯不再是绿色 `● ONLINE`;
- 长时间无操作被超时挂起。

**修法**:
- 让用户**确认 MasterGo 标签页还开着、插件面板还显示 `● ONLINE`**;
- 用户说"好了"之后重试;
- 不要重复重试,每次都问用户确认状态。

### B.2 `10003 禁止访问 / 配额不足`

**症状**:`design` / `get_component_info` 等写操作报权限或配额错。

**根因**:
- Codify Access Key 错 / 过期;
- 账号配额(看 `get_user_info` 输出)用完。

**修法**:
- `get_user_info` 先看配额:如果"生成设计 / 获取代码"显示用完,告诉用户充值或升级;
- 让用户回 Codify 后台重新复制 access key,更新 MCP 配置文件后**重启会话**。

### B.3 `📋 代码列表为空`

**症状**:`get_code_list` 返回空。

**根因**:用户没在 Codify 插件里对任何图层点过"复制代码 / 发送代码"按钮。
**这不是 bug,是正常状态**。

**修法**:不要把"列表为空"当报错回答用户。引导用户:
- 想看单页 → 在画布选中,你用 `get_selection_code` 拉;
- 想看整文件目录 → 走 Magic MCP `getDsl`,而不是 Codify。

详见 [design-workflow.md](design-workflow.md) "看页面"小节。

### B.4 团队组件库相关错误

| 报错 | 修法 |
|---|---|
| `团队库列表为空` | 当前 MasterGo 文件没订阅任何团队库。先查 MasterGo 团队库/资源库官方说明,再引导用户:左侧面板 → 组件 → 资产 → 添加团队库;用户找不到入口就让他发侧栏截图继续定位 |
| `get_component_info` 报组件不存在 | 用户传的 `teamLibraryName` 拼错;先 `get_library_list` 拿准确名称 |
| `var(--xxx)` 在生成的 HTML 里渲染不出来 | `variable.json` 没落盘 / 变量名拼错;重跑 `get_component_info` |
| 自绘比例过高(组件没用上) | 看 `design` 返回里有没有"组件缺失原因"声明;改 `buildStrategy` 或换更合适的库重跑 |

### B.5 contentId 相关

Codify 的 `get_code` 等工具需要 contentId(用户在插件里点复制按钮才生成)。
**不让用户复制 contentId**:可以通过 `get_code_list` 或 `get_selection_code` 走 layerId 路径。

### B.6 `design` 工具的 buildStrategy 拒绝继续

**症状**:`design(useComponentLibrary=true, ...)` 没传 `buildStrategy` 时报错要求二选一。

**根因**:Codify 规则强制每次调用都要明确策略。

**修法**:按场景填:
- 后台 / 表单 / 业务页 → `full-components`
- 落地页 / 营销页 / 自定义视觉多 → `hybrid`

不确定时直接问用户。

### B.7 Codify 规范 / Tailwind 同步问题

**症状**:本地 HTML 看起来正常,同步到 MasterGo 后样式丢失、布局漂移,或 Codify
提示需要按当前规范重写。

**根因**:本地稿用了原生 CSS、`<style>`、外链 CSS 或运行时样式,但当前 Codify 规范
要求 Tailwind utility class / 可解析组件结构。

**修法**:
- 先运行 `get_codify_guidelines`,不要凭旧经验猜 Codify 规范;
- 再运行 `get_user_info`,确认账号、权限、配额和当前上下文;
- 按 [codify-push-protocol.md](codify-push-protocol.md) 把原生 CSS HTML 转成
  Tailwind utility HTML;
- 重新写入 MasterGo 后,用 `get_design_diff` 或画布截图验证。

### B.8 远端 TLS / 404 / 本地 bridge 未启动

**症状**:Codify MCP 初始化失败、远端 URL 报 TLS / 404 / connection refused，或本地
`http://127.0.0.1:9999` 没响应。

**修法**:

- 先运行 `scripts/check-mcp-config.py --host <当前宿主>`，看 `url_type` 是
  `remote`、`local` 还是 `missing`。
- 远端 URL 失败时，确认当前包 README 要求的 URL 是否仍是 `https://mcp.codify-api.com`。
- 本地 bridge 模式先跑 `curl -i http://127.0.0.1:9999/`；连不上就让用户启动本地
  bridge / Go server，再重启宿主会话。
- 如果 Go server 返回非 MCP 内容，记录响应摘要，不要继续调写入工具；让用户发本地
  bridge 启动日志或当前配置。

---
