# 05a — MasterGo Codify 设计

用户要在 MasterGo 画布上生产、修改、维护设计。**真实交付物是 MasterGo 画布成果**, 不是本地 HTML、截图、Markdown 或可粘贴 prompt。

## 何时读

- 进入 MasterGo Codify 路径(在画布上做设计 / 修改 / 维护)
- 不确定是否走 Codify → 先看 [01-routing.md#mastergo-子任务路由](01-routing.md#mastergo-子任务路由)
- 配套还原流程在 [05b-magic-restore.md](05b-magic-restore.md)

跳过场景: 已经在某条 unit 内推进, Codify 流程已锁定。

## 目录

- [Codify MCP 可用性门禁](#codify-mcp-可用性门禁)
- [MasterGo 设计 Gate Card](#mastergo-设计-gate-card)
- [任务台账](#任务台账)
- [设计方向选择](#设计方向选择)
- [体验质量门禁](#体验质量门禁)
- [组件库三段式策略](#组件库三段式策略)
- [写入前 preflight 硬门禁](#写入前-preflight-硬门禁)
- [HTML 与 UI 文案合规](#html-与-ui-文案合规)
- [旧稿复用审计](#旧稿复用审计)
- [写入工具选择](#写入工具选择)
- [accepted pending 闭环](#accepted-pending-闭环)
- [推送后跳 3A 验证](#推送后跳-3a-验证)
- [反馈与恢复](#反馈与恢复)

---

## Codify MCP 可用性门禁

开始任何设计产物前确认:

- 当前宿主配置里有 Codify MCP, token/key 不是占位
- 当前会话能看到 `mcp__codify__*` 写入工具
- 需要后续还原代码时, 再确认 Magic MCP

缺任一项: 回 [mcp-setup.md](mcp-setup.md) 检查配置 → 按用户行动契约说明缺什么、为什么、怎么配 → 标记任务待配置/待推送, **不创建本地替代设计交付**。

只有用户明确改口"先不要推 MasterGo, 只要本地方案/文档"时, 才允许离开本路径。

## MasterGo 设计 Gate Card

从零设计、大范围改版、旧稿复用、配置恢复后继续时, 必须先给用户可见 Gate Card。**没有 Gate Card 不得写入 MasterGo**。

固定格式:

```text
MasterGo 设计 Gate Card
- 真实交付物: MasterGo 画布设计稿
- 覆盖范围: 完整稿 / 评审方向稿 / 概念代表页 / 自定义
- 设计单元: <页面、状态、弹窗、抽屉、组件变体清单>
- UI 文案语种: Simplified Chinese / English / 自定义
- 设计方向: <用户选择或"用户授权我决定"的依据>
- 体验质量门禁: <purpose / tone / differentiation / constraints / anti-generic guardrails>
- 用户结果句: 这帮助 <用户> 通过 <机制> 达成 <结果>
- 组件库策略: 本地库快照 / 远端查库 / 用户拒绝 / 无库自绘
- 写入方式: design / agent_create_page / agent_update_node / agent_sync_design
- 验证方式: get_design_diff + 截图 + 语种检查 + 组件映射率
```

高置信直接填好继续。低置信只问关键选择题, 保留"自定义 / type something"。

### 覆盖范围原则

**不根据"企业级 / 平台 / 工作台 / 后台 / 协作"等关键词机械决定页面数量**。设计单元由用户目标、角色、核心流程和验收标准决定。

不要把完整需求擅自缩成一个首页 / 首屏 / 概念页。本轮只做代表性页面 → 必须是用户明确选择, Gate Card 标注"不代表完整覆盖"。

复杂平台覆盖单元模板见 [03-requirements.md](03-requirements.md#复杂产品覆盖模板)。中文"企业级 AI 多智能体协作平台设计稿"的默认推荐不是单页 dashboard, 至少覆盖: 总览工作台 / 编排画布 / 运行详情 / Agent 目录 / 工具知识库管理 / 治理审批 / 设置 / 关键弹窗抽屉 / 异常空态加载态。

### UI 文案语种

跟随 [03-requirements.md](03-requirements.md#ui-文案语种契约)。中文聊天/中文素材 → 默认简体中文 UI, 这段必须进入 Codify requirement 或 HTML, **不只写在回复里**。

```
UI copy language: Simplified Chinese.
Keep product names and technical acronyms as-is:
MasterGo, Codify, AI, Agent, API, MCP, D2C, SLA, SSO, RBAC, AgentOps.
```

## 任务台账

Gate Card 确定后, 在用户项目工作区写 `.codify/state/mastergo-task.json`。这是**恢复和门禁来源, 不是完成证据**。

```json
{
  "originalUserGoal": "<原始用户目标>",
  "gateCard": {
    "delivery": "MasterGo 画布设计稿",
    "scope": "完整稿 / 评审方向稿 / 概念代表页 / 自定义",
    "copyLanguage": "simplified-chinese",
    "designDirection": "企业运营型 / AgentOps 观测型 / 高管演示型 / 自定义",
    "componentLibraryStrategy": "local-snapshot|remote-selected|declined|unavailable|pending",
    "writeMethod": "design|agent_create_page|agent_update_node|agent_sync_design"
  },
  "units": [
    {"id": "overview", "title": "总览工作台", "type": "page", "status": "planned"}
  ]
}
```

```bash
python3 <skill-dir>/scripts/helpers/mastergo-task-state.py init \
  --goal "<原始用户目标>" \
  --scope "完整稿:覆盖核心流程、主要界面、关键状态和治理细节" \
  --copy-language simplified-chinese \
  --design-direction "企业运营型:清晰、密集、低装饰" \
  --component-library pending \
  --write-method design \
  --unit overview:总览工作台:page \
  --unit orchestration-canvas:多智能体编排画布:page

python3 <skill-dir>/scripts/helpers/mastergo-task-state.py resume
python3 <skill-dir>/scripts/helpers/mastergo-task-state.py list
```

未 `verified` 或未明确 `blocked` 的单元仍在 → 不得结束任务。

## 设计方向选择

默认提供 2-3 个方向, 或用户授权"你决定"时自动选择并写入 Gate Card:

```text
设计方向建议:
A. 企业运营型(推荐): 清晰、密集、低装饰, 适合高频工作和团队协作
B. AgentOps 观测型: trace、日志、拓扑、状态表达更强
C. 高管演示型: 信息更少、对比更强, 适合路演和评审
D. 自定义 / type something
```

读 [04-solution.md](04-solution.md#体验设计质量门禁) 产出视觉决策, 但**不要把本地页面、截图或 prompt 当最终交付**。设计质量 brief、覆盖 brief 和 UI 语种合并成 Codify requirement。

设计方向不只写视觉形容词, 还要写设计 led check: 用户结果句清楚 / default-loading-empty-error-success-disabled-permission 状态齐全 / 键盘焦点、对比度、目标尺寸、reduced motion / 核心操作反馈和可恢复 / 性能预算不被破坏。

## 体验质量门禁

Codify requirement 或 HTML 写入前必须包含:

- **purpose**: 当前设计服务的用户任务
- **tone**: 一个明确调性, 符合产品领域
- **differentiation**: 一个可记住的视觉/交互点
- **constraints**: 组件库、品牌、可访问性、性能、设备约束
- **anti-generic guardrails**: 避免模板化 dashboard、随意紫色渐变、重复卡片堆叠、无意义装饰
- **state coverage**: default / loading / empty / error / success / permission

已有团队组件库或品牌系统 → 体验质量门禁应**强化**现有系统, 不要用无关美术风格覆盖。

## 组件库三段式策略

**不再绝对要求**每次普通 design 先调 `get_library_list`。Codify 工具描述限制普通设计场景查库时, 按三段执行。

### ① 本地库快照优先

```bash
python3 <skill-dir>/scripts/helpers/library-snapshot.py list \
  --catalog .codify/library/catalog.json
python3 <skill-dir>/scripts/helpers/library-snapshot.py recommend \
  --catalog .codify/library/catalog.json --scenario enterprise
```

本地有可用库 → Gate Card 标 `组件库策略: 本地库快照` + 使用快照中的 `teamLibraryName` / `buildStrategy`。**不需要立刻远端查库**。

### ② 本地无快照时给选择题

```text
组件库策略:
A. 使用团队组件库(推荐): 我会按 Codify 工具要求调用 get_library_list, 再让你选库
B. 暂不使用组件库: 记录用户拒绝, 允许自绘, 但后续组件化成本更高
C. 不确定: 我先说明差异, 你再选
D. 自定义 / type something
```

用户选 A 后: `get_library_list` → 展示候选 → 用户选定 → `get_component_info(teamLibraryName="...", projectDir="...")` → 落盘后继续 preflight。

**用户未明确授权时不要违反工具描述直接调用 `get_library_list`; 也不要静默自绘**。

### ③ 无库或用户拒绝

Gate Card 写明 `组件库策略: 用户拒绝` 或 `无库自绘`。调用 Codify 允许 `useComponentLibrary=false`, 但必须先告知**自绘后续组件化成本更高**。

## 写入前 preflight 硬门禁

任何 `design` / `agent_*` / `agent_sync_design` 写操作前必须**同时**满足:

1. 已输出 MasterGo 设计 Gate Card
2. 已初始化或恢复 `.codify/state/mastergo-task.json`
3. 已调用 `get_codify_guidelines`
4. 已调用 `get_user_info`
5. 已确认组件库策略
6. 已确认 UI 文案语种并写入 requirement / HTML
7. 已运行 preflight 且 `canWrite=true`

```bash
python3 <skill-dir>/scripts/mandatory/codify-preflight.py \
  --task-state .codify/state/mastergo-task.json \
  --guidelines --user-info \
  --component-strategy remote-selected \
  --team-library-name "Ant Design For AI"
```

有 HTML 时追加:

```bash
python3 <skill-dir>/scripts/mandatory/codify-preflight.py \
  --task-state .codify/state/mastergo-task.json \
  --html .codify/design/overview-tailwind.html \
  --expected-language simplified-chinese \
  --artifact-source current-run \
  --goal "<原始用户目标>" \
  --guidelines --user-info \
  --component-strategy local-snapshot \
  --team-library-name "Ant Design For AI"
```

`canWrite=false` → 不得调用写入工具, 按 errors 修复后重跑。

缺 `get_codify_guidelines` 或 `get_user_info` 结果 → 不要执行写操作, 按 [troubleshooting.md](troubleshooting.md#codify-排障) 排查。

`agent_sync_design` 是全量覆盖, **只能在用户明确说"同步到画布 / 覆盖这个节点"后执行**。

## HTML 与 UI 文案合规

以 `get_codify_guidelines` 返回为准。无明确允许时默认:

- 用 Tailwind utility class 表达布局、间距、颜色、字号、圆角、阴影和状态
- **不**把 `<style>`、外链 CSS、全局 CSS 文件或 inline style 当作可推送成品
- 不依赖运行时 JS 计算布局
- 用组件库时保留 `<ui-component>` / `<ui-icon>` 等 Codify 可识别结构
- UI 文案语种遵守契约

```bash
python3 <skill-dir>/scripts/helpers/codify-html-lint.py <html-file>
python3 <skill-dir>/scripts/helpers/codify-copy-lint.py <html-file> \
  --expected simplified-chinese --mode strict
```

## 旧稿复用审计

任何已有 HTML 作为 Codify 输入前, 必须记录来源:

- `current-run`: 本轮新生成
- `mastergo-baseline`: 从 MasterGo 拉取或当前画布基准
- `user-provided`: 用户提供文件
- `historical`: 历史中间稿

历史中间稿必须重新过:

```bash
python3 <skill-dir>/scripts/helpers/codify-artifact-audit.py <html-file> \
  --source historical \
  --goal "<本轮原始用户目标>" \
  --expected-language simplified-chinese
python3 <skill-dir>/scripts/helpers/codify-html-lint.py <html-file>
python3 <skill-dir>/scripts/helpers/codify-copy-lint.py <html-file> \
  --expected simplified-chinese --mode strict
```

**旧英文单页稿、历史 demo、本地 mockup 不得直接作为新中文企业级平台的完成物**。覆盖单元、UI 语种、设计方向、组件库策略和 Codify HTML 结构不匹配 → 先重做或修正。

## 写入工具选择

| 任务 | 写入方式 | 额外要求 |
|---|---|---|
| 从零复杂设计 | `design` | 按 task state 设计单元分批, 不把复杂平台压成单页 |
| 新增明确页面且已有合规 HTML | `agent_create_page` | HTML 必须通过 lint + copy lint + artifact audit |
| 创建组件 | `agent_create_component` | 明确组件用途、变体和复用范围 |
| 局部修改 | `agent_update_node` / `agent_replace_node` | 先 `get_selection_code` 或读取目标节点现状 |
| 删除节点 | `agent_remove_node` | 确认 nodeId 和影响范围 |
| 全量覆盖 | `agent_sync_design` | 用户明确授权; 否则禁止 |

`agent_create_page` **不是**把旧本地稿直接丢给 Codify 然后宣布完成的捷径。

## accepted pending 闭环

Codify 写工具返回 `accepted` / request id / "已受理" 只代表请求进入处理队列。

```bash
python3 <skill-dir>/scripts/helpers/mastergo-task-state.py request \
  --request-id "<requestId>" --status accepted
```

后续验证: `get_code_list` → `get_selection_code` → `get_design_diff` → 用户 MasterGo 截图。

**没有图层或截图证据 → 状态是 `blocked: waiting-for-canvas-verification` 或待验证**。最终回复只能说"已发送, 待画布验证", 不能说"设计已完成"。

## 推送后跳 3A 验证

写入后立即进入 [07a-design-verify.md](07a-design-verify.md) 3A:

- `get_design_diff` 检查本地基准与画布现状
- 整页、根 Frame、关键弹窗/抽屉截图
- `codify-copy-lint.py` 或人工抽查确认 UI 文案语种
- 用了组件库时跑 `scripts/helpers/component-ratio.sh <html> full-components|hybrid`
- `scripts/helpers/verification-state.py record` 归档
- `scripts/helpers/mastergo-task-state.py mark <unit> verified` 闭合设计单元

任一证据缺失 → 不要说完成。继续修正、等用户截图、或标记待验证。

## 反馈与恢复

用户说"不错 / 可以 / 没问题 / 继续":

1. `mastergo-task-state.py list` 查剩余单元
2. **继续下一个 `planned/generated` 单元**(不要回头问"接下来做什么")
3. 每个单元重复 preflight → write → 3A verify

配置重启、reconnect 或工具恢复后:

```bash
python3 <skill-dir>/scripts/helpers/mastergo-task-state.py resume
```

先复述原始目标、Gate Card 和剩余单元再继续, **不要把任务缩成 demo 页**。

---
