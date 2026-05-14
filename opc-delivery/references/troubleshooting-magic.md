# Magic MCP 报错处理

# Magic MCP 报错处理

## 目录

- [A.1 `Could not extract layerId from URL`](#a1-could-not-extract-layerid-from-url)
- [A.2 `Request too large (max 20MB)`](#a2-request-too-large-max-20mb)
- [A.3 `🔒 禁止访问 / 10003`(权限错误)](#a3--禁止访问--10003-权限错误)
- [A.4 D2C 缓存:设计变了但 HTML 一字不差](#a4-d2c-缓存设计变了但-html-一字不差)
- [A.5 `getMeta` 返回 `<info></info>` 空](#a5-getmeta-返回-info-空)
- [A.6 DSL 看不到画布上画的原型连线](#a6-dsl-看不到画布上画的原型连线)
- [A.7 `未找到该 contentId 对应的数据`](#a7-未找到该-contentid-对应的数据)

定位:Magic MCP(`getDsl` / `getD2c` / `getMeta`)报错时按本表查;
不熟的报错先按 [troubleshooting.md](troubleshooting.md) 的 `bash + curl` 查官方文档。

## A. Magic MCP 报错

### A.1 `Could not extract layerId from URL`

**症状**:用户给的 URL 调 `getDsl` 报这个。

**根因**:URL 里没 `layer_id=` 参数。常见于:
- 短链 `https://mastergo.com/goto/xxx?file=...`,没在画布选中状态下生成;
- 文件根 URL `https://mastergo.com/file/<fileId>`。

**修法**:让用户:
1. 在 MasterGo 画布里**单击目标 Frame**让它高亮选中;
2. 直接复制地址栏 URL(这时会自动带 `&layer_id=xxx%3Ayyy`);
   或者图层面板右键 Frame → "复制链接"。

### A.2 `Request too large (max 20MB)`

**症状**:拉根容器 DSL 报这个。

**根因**:根容器 DSL 包含所有页面,整体可能超 20MB。

**修法**:
- **不要**重试整体,永远会失败;
- 改成对每个 1440 子 Frame 单独 `getDsl(fileId, childLayerId)`,单页通常 < 2MB;
- 解析每页 DSL 单独处理 + diff。

### A.3 `🔒 禁止访问 / 10003` (权限错误)

**症状**:调任何 Magic 工具报 `code: "10003"`。

**先判定配置是否真的存在**:

1. 检查当前宿主配置文件:
   - Codex:`~/.codex/config.toml`
   - Claude Code:`~/.claude.json` 或 `claude mcp list`
   - Cursor:`~/.cursor/mcp.json` / 项目 `.cursor/mcp.json`
2. 只确认是否存在 `@mastergo/magic-mcp` 和非占位 token,不要打印 token 明文;
3. 如果没有配置、token 为空、或仍是 `<USER_MASTERGO_TOKEN>` 这类占位符,
   结论是**MCP 未正确配置**,不是 MasterGo 文件权限问题。

**重要**:`tool_search` 搜到 `mcp__mastergo_magic_mcp__mcp__getDsl`
不能当作已配置证据。它可能只是当前运行时暴露了工具 schema;没有本地 token
配置时,直接调用会得到没有诊断价值的 10003。

配置真实存在后,10003 的常见根因才是:
1. token 错(过期 / 用错账号 / 误粘贴);
2. token 所属账号在该 MasterGo 文件**不是团队版及以上**;
3. token 所属账号在该团队**没有编辑席位或研发席位**(查看席位也不行)。

**修法**:
- 配置缺失/占位 → 回 [mcp-setup.md](mcp-setup.md) 重新配置,并重启会话;
- 让用户按官方帮助页重新生成 MCP token:
  https://mastergo.com/help/MG/MCP
  MasterGo → 个人设置 → 安全设置 → 个人访问令牌 → 生成令牌;
- 让用户确认该文件所在团队的席位类型;
- 验证:`get_user_info` 一类 Codify 工具如果同账号能用,说明账号活的;
  只有 Magic 报 10003 就是席位问题。

### A.4 D2C 缓存:设计变了但 HTML 一字不差

**症状**:用户说改了设计稿,重拉 D2C 后 HTML md5 跟旧的完全相同。

**根因**:D2C 在 MasterGo 服务端缓存,缓存键是 contentId。设计师改了设计但还没
触发"发送数据"重新生成。

**修法**:
1. 先拉 DSL(DSL 不缓存,永远是最新);
2. 跟旧 DSL diff 字节数和 hash 验证设计是否真的变了;
3. 让用户在 MasterGo 里**重新点"发送数据"**触发 D2C 重生成;
4. 用新 `outDir`(避免本地资源混淆)重拉。

### A.5 `getMeta` 返回 `<info></info>` 空

**症状**:调 `getMeta(fileId, rootLayerId)` 期望拿站点目录,结果空。

**根因**:设计师没按 MasterGo 规范在根容器上注入 `meta` 和 `action` 字段。绝大
多数文件都没有。

**修法**:跳过 meta 工作流,直接 `getDsl(rootLayerId)` 然后遍历 `children` 自己
列出页面目录。

### A.6 DSL 看不到画布上画的原型连线

**症状**:用户在 MasterGo Prototype 模式画了 Frame ↔ Frame 的连接线,但 DSL 里
`interactive` 字段没新增。

**根因**:MasterGo MCP 的 DSL **不下发跨 Frame 原型连线**,只下发**组件级
interactive**(比如输入框 hover 状态变体过渡)。检查 DSL 里既有的 `interactive`
节点,会发现 `targetLayerId` 指向的是 `COMPONENT` 类型节点(变体),不是 `FRAME`
类型(页面)。

**修法**:
- 向用户说明这是 MasterGo MCP 的能力边界,**不是同步问题不是 bug**;
- 让用户用自然语言告诉你跳转关系,例如:"首页的[请明天的年假]按钮 → /leave-with";
- 在代码里用 `<Link href="/leave-with">` 或 `router.push('/leave-with')` 手写。

如果需要程序化判断,可以在 `getDsl` 返回里递归查找 `interactive` 字段,再判断
`targetLayerId` 对应的节点 type:

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

# 如果 find_node(...).get('type') == 'COMPONENT',那是变体过渡,不是页面跳转
```

### A.7 `未找到该 contentId 对应的数据`

**症状**:`getD2c(contentId=..., ...)` 报这个。

**根因**:用户还没在 MasterGo Codify 插件里对该 Frame 点过"发送数据"。

**修法**:
- 告诉用户**具体哪个 Frame** 需要发送(用 Frame name + layerId 指认);
- 说明依据:MasterGo 官方 MCP 文档的 `mcp_getD2c` 流程要求先点击"发送数据";
- 给步骤:在 MasterGo 选中该 Frame → 打开 Codify / MCP 相关面板 → 点击"发送数据";
- 用户点完后,你重新拉 `getD2c(contentId=..., fileId=...)`;
- 如果用户找不到按钮,让他发当前 MasterGo 右侧/插件面板截图,继续定位入口。

---
