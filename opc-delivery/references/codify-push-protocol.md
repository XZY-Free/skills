# Codify 推送协议

## 目录

- [适用范围](#适用范围)
- [写入前硬门禁](#写入前硬门禁)
- [HTML 与 UI 文案合规](#html-与-ui-文案合规)
- [旧稿复用审计](#旧稿复用审计)
- [组件库写入策略](#组件库写入策略)
- [写入工具选择](#写入工具选择)
- [accepted pending 闭环](#accepted-pending-闭环)
- [推送后验证](#推送后验证)

本文件定义 Codify 写入 MasterGo 画布前必须遵守的协议。设计任务只有在成功推送到
MasterGo 画布并完成验证后才算完成。本地 HTML、浏览器预览、截图、request id
只能算中间证据或 pending 状态。

## 适用范围

以下任一 Codify 写操作前都必须执行本协议:

- `design(...)`
- `agent_create_page(...)`
- `agent_create_component(...)`
- `agent_update_node(...)`
- `agent_replace_node(...)`
- `agent_remove_node(...)`
- `agent_sync_design(...)`

`agent_sync_design` 是全量覆盖，只能在用户明确说“同步到画布 / 覆盖这个节点”后执行。

## 写入前硬门禁

写入 MasterGo 前必须同时满足:

1. 已输出 MasterGo 设计 Gate Card。
2. 已初始化或恢复 `.codify/state/mastergo-task.json`。
3. 已调用 `get_codify_guidelines`。
4. 已调用 `get_user_info`。
5. 已确认组件库策略。
6. 已确认 UI 文案语种并写入 requirement / HTML。
7. 已运行 `scripts/codify-preflight.py` 且 `canWrite=true`。

示例:

```bash
python3 <skill-dir>/scripts/codify-preflight.py \
  --task-state .codify/state/mastergo-task.json \
  --guidelines \
  --user-info \
  --component-strategy remote-selected \
  --team-library-name "Ant Design For AI"
```

有 HTML 时:

```bash
python3 <skill-dir>/scripts/codify-preflight.py \
  --task-state .codify/state/mastergo-task.json \
  --html .codify/design/overview-tailwind.html \
  --expected-language simplified-chinese \
  --artifact-source current-run \
  --goal "<原始用户目标>" \
  --guidelines \
  --user-info \
  --component-strategy local-snapshot \
  --team-library-name "Ant Design For AI"
```

缺少 `get_codify_guidelines` 或 `get_user_info` 的结果时，不要执行写操作；按
[troubleshooting-codify.md](troubleshooting-codify.md) 排查连接、权限或配额。

## HTML 与 UI 文案合规

以 `get_codify_guidelines` 返回为准。没有明确允许时默认:

- 使用 Tailwind utility class 表达布局、间距、颜色、字号、圆角、阴影和状态。
- 不把 `<style>`、外链 CSS、全局 CSS 文件或 inline style 当作可推送成品。
- 不依赖运行时 JS 计算布局。
- 用组件库时保留 `<ui-component>` / `<ui-icon>` 等 Codify 可识别结构。
- UI 文案语种遵守 [copy-language.md](copy-language.md)。

先跑结构 lint:

```bash
python3 <skill-dir>/scripts/codify-html-lint.py <html-file>
```

再跑 copy lint:

```bash
python3 <skill-dir>/scripts/codify-copy-lint.py <html-file> \
  --expected simplified-chinese \
  --mode strict
```

`codify-html-lint.py` 只检查标签和属性，不把正文里的 `grid` / `items-*` 误判为 class。
`codify-copy-lint.py` 只看可见 UI 文案和白名单技术词。

## 旧稿复用审计

任何已有 HTML 作为本轮 Codify 输入前，都必须记录来源:

- `current-run`: 本轮新生成。
- `mastergo-baseline`: 从 MasterGo 拉取或当前画布基准。
- `user-provided`: 用户提供文件。
- `historical`: 历史中间稿。

历史中间稿必须重新过:

```bash
python3 <skill-dir>/scripts/codify-artifact-audit.py <html-file> \
  --source historical \
  --goal "<本轮原始用户目标>" \
  --expected-language simplified-chinese
python3 <skill-dir>/scripts/codify-html-lint.py <html-file>
python3 <skill-dir>/scripts/codify-copy-lint.py <html-file> \
  --expected simplified-chinese \
  --mode strict
```

旧英文单页稿、历史 demo、本地 mockup 不得直接作为新中文企业级平台的完成物。覆盖单元、
UI 语种、设计方向、组件库策略和 Codify HTML 结构不匹配时，先重做或修正。

## 组件库写入策略

优先使用本地库快照:

```bash
python3 <skill-dir>/scripts/library-snapshot.py list \
  --catalog .codify/library/catalog.json
```

本地无快照时，先让用户选择是否使用团队组件库。用户授权后再调用:

1. `get_library_list`
2. `get_component_info(teamLibraryName="...", projectDir="...")`

用户未明确授权时，不要违反工具描述直接查库；也不要把“用户没说组件库”当作自绘授权。
用户明确拒绝或无可用库时，Gate Card 标记 `declined` / `unavailable`，再允许自绘。

## 写入工具选择

| 场景 | 工具 | 额外要求 |
|---|---|---|
| 从零复杂设计 | `design` | 按 Gate Card 的设计单元分批，不把复杂平台压成单页 |
| 新增明确页面且已有合规 HTML | `agent_create_page` | HTML 必须通过 lint、copy lint、artifact audit |
| 创建组件 | `agent_create_component` | 明确组件用途、变体和复用范围 |
| 局部修改 | `agent_update_node` / `agent_replace_node` | 先 `get_selection_code` 或读取目标节点现状 |
| 删除节点 | `agent_remove_node` | 确认 nodeId 和影响范围 |
| 全量覆盖 | `agent_sync_design` | 用户明确授权覆盖；否则禁止 |

从零复杂设计优先 `design`。`agent_create_page` 适合“已有合规 HTML + 新增一个明确页面”，
不是把旧本地稿直接丢给 Codify 然后宣布完成的捷径。

## accepted pending 闭环

Codify 写工具返回 `accepted`、request id 或“已受理”，只代表请求进入处理队列。

必须写入 task state:

```bash
python3 <skill-dir>/scripts/mastergo-task-state.py request \
  --request-id "<requestId>" \
  --status accepted
```

后续验证顺序:

1. `get_code_list`
2. `get_selection_code`
3. `get_design_diff`
4. 用户 MasterGo 截图

没有图层或截图证据时，状态是 `blocked: waiting-for-canvas-verification` 或待验证。最终回复
只能说“已发送，待画布验证”，不能说“设计已完成”。

## 推送后验证

写入成功后立即进入 [verification.md](verification.md) 3A:

- 用 `get_design_diff` 检查本地基准与画布现状。
- 用整页、根 Frame、关键弹窗/抽屉截图检查视觉。
- 用 `codify-copy-lint.py` 或人工抽查确认 UI 文案语种。
- 用了组件库时跑 `scripts/component-ratio.sh <html> full-components|hybrid`。
- 用 `scripts/verification-state.py record` 归档验证。
- 用 `scripts/mastergo-task-state.py mark <unit> verified` 闭合设计单元。

任一证据缺失时，不要说完成。继续修正、等待用户截图、或标记为待验证。
