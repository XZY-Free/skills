# Codify 设计工作流(在 MasterGo 画布上做设计)

## 目录

- [总流程](#总流程)
- [步骤 -1: Codify MCP 可用性门禁](#步骤--1-codify-mcp-可用性门禁)
- [步骤 0: MasterGo 设计 Gate Card](#步骤-0-mastergo-设计-gate-card)
- [步骤 1: 初始化任务台账](#步骤-1-初始化任务台账)
- [步骤 2: 设计方向选择卡](#步骤-2-设计方向选择卡)
- [步骤 2.5: 体验质量门禁](#步骤-25-体验质量门禁)
- [步骤 3: 组件库策略](#步骤-3-组件库策略)
- [步骤 4: 写入前 preflight](#步骤-4-写入前-preflight)
- [步骤 5: 选择写入工具并推送](#步骤-5-选择写入工具并推送)
- [步骤 6: 设计完跳验证](#步骤-6-设计完跳验证)
- [步骤 7: 反馈和恢复后续作](#步骤-7-反馈和恢复后续作)

定位: 用户要在 MasterGo 画布上生成、修改、维护设计。真实交付物是 MasterGo
画布成果，不是本地 HTML、截图、Markdown 或可粘贴 prompt。

## 总流程

```text
-1. 确认当前宿主 Codify MCP 可用；缺失则回 mcp-setup.md
 0. 输出 MasterGo 设计 Gate Card
 1. 写入 .codify/state/mastergo-task.json
 2. 确定设计方向和 UI 文案语种
 3. 组件库策略: 本地库快照 -> 用户授权远端查库 -> 拒绝/无库自绘
 4. get_codify_guidelines + get_user_info + codify-preflight.py
 5. design / agent_create_page / agent_update_node / agent_sync_design
 6. verification.md 3A
 7. 按 task state 继续剩余设计单元
```

## 步骤 -1: Codify MCP 可用性门禁

开始任何设计产物前先确认:

- 当前宿主配置里有 Codify MCP，且 token/key 不是占位符；
- 当前会话能看到 `mcp__codify__*` 写入工具；
- 需要后续还原代码时，再确认 Magic MCP。

缺任一项时:

1. 回 [mcp-setup.md](mcp-setup.md) 检查当前宿主配置。
2. 按用户行动契约说明缺什么、为什么、怎么配、重启后继续什么。
3. 标记任务为待配置/待推送，不要创建本地替代设计交付。

只有用户明确改口“先不要推 MasterGo，只要本地方案/文档”时，才允许离开本路径。

## 步骤 0: MasterGo 设计 Gate Card

从零设计、大范围改版、旧稿复用、配置恢复后继续时，必须先给用户可见的 Gate Card。
没有 Gate Card 不得写入 MasterGo。

固定格式:

```text
MasterGo 设计 Gate Card
- 真实交付物: MasterGo 画布设计稿
- 覆盖范围: 完整稿 / 评审方向稿 / 概念代表页 / 自定义
- 设计单元: <页面、状态、弹窗、抽屉、组件变体清单>
- UI 文案语种: Simplified Chinese / English / 自定义
- 设计方向: <用户选择或“用户授权我决定”的依据>
- 体验质量门禁: <purpose / tone / differentiation / constraints / anti-generic guardrails>
- 用户结果句: 这帮助 <用户> 通过 <机制> 达成 <结果>
- 组件库策略: 本地库快照 / 远端查库 / 用户拒绝 / 无库自绘
- 写入方式: design / agent_create_page / agent_update_node / agent_sync_design
- 验证方式: get_design_diff + 截图 + 语种检查 + 组件映射率
```

高置信时直接填好并继续。低置信时只问关键选择题，最后保留“自定义 / type something”。

### 覆盖范围

遵守 [design-scope.md](design-scope.md)。复杂平台参考
[design-coverage-patterns.md](design-coverage-patterns.md)，但不要把模板当固定页数。

中文“企业级 AI 多智能体协作平台设计稿”的默认推荐不是单页 dashboard，而是:

- 总览工作台
- 多智能体编排画布
- 运行详情 / trace / 日志
- Agent 目录与能力配置
- 工具、知识库与连接器管理
- 治理、审批、审计与风险策略
- 权限、团队、模型与预算设置
- 新建运行弹窗、人工审批抽屉、异常/空态/加载态

若用户只要概念代表页，必须是用户明确选择，并在 Gate Card 标注“不代表完整覆盖”。

### UI 文案语种

遵守 [copy-language.md](copy-language.md)。中文聊天或中文素材默认:

```text
UI copy language: Simplified Chinese.
Keep product names and technical acronyms as-is:
MasterGo, Codify, AI, Agent, API, MCP, D2C, SLA, SSO, RBAC, AgentOps.
```

这段必须进入 Codify requirement 或 HTML，不只写在回复里。

## 步骤 1: 初始化任务台账

Gate Card 确定后，在用户项目工作区写 `.codify/state/mastergo-task.json`。这是恢复和
门禁来源，不是完成证据。

推荐命令:

```bash
python3 <skill-dir>/scripts/mastergo-task-state.py init \
  --goal "<原始用户目标>" \
  --scope "完整稿:覆盖核心流程、主要界面、关键状态和治理细节" \
  --copy-language simplified-chinese \
  --design-direction "企业运营型:清晰、密集、低装饰" \
  --design-status auto-decided \
  --component-library pending \
  --build-strategy pending \
  --write-method design \
  --unit overview:总览工作台:page \
  --unit orchestration-canvas:多智能体编排画布:page
```

继续任务前:

```bash
python3 <skill-dir>/scripts/mastergo-task-state.py resume
python3 <skill-dir>/scripts/mastergo-task-state.py list
```

若有未 `verified` 或未明确 `blocked` 的单元，不得结束任务。

## 步骤 2: 设计方向选择卡

默认提供 2-3 个方向，或在用户授权“你决定”时自动选择并写入 Gate Card。

```text
设计方向建议:
A. 企业运营型(推荐): 清晰、密集、低装饰，适合高频工作和团队协作。
B. AgentOps 观测型: trace、日志、拓扑、状态表达更强。
C. 高管演示型: 信息更少、对比更强，适合路演和评审。
D. 自定义 / type something: 你直接写风格偏好。
```

读 [frontend-design-quality.md](frontend-design-quality.md), 用它产出视觉决策描述，但不要把本地页面、
截图或 prompt 当最终交付。将设计质量 brief、覆盖 brief 和 UI 文案语种合并成 Codify requirement。

设计方向不只写视觉形容词，还要写设计 led check:

- 用户结果句清楚；
- default、loading、empty、error、success、disabled/permission 状态齐全；
- 键盘焦点、对比度、目标尺寸和 reduced motion 有约束；
- 核心操作有反馈和可恢复路径；
- 性能预算不被动效、图片或复杂效果破坏。

## 步骤 2.5: 体验质量门禁

Codify requirement 或 HTML 写入前, 必须包含:

- purpose: 当前设计服务的用户任务;
- tone: 一个明确调性, 且符合产品领域;
- differentiation: 一个可记住的视觉或交互点;
- constraints: 组件库、品牌、可访问性、性能和设备约束;
- anti-generic guardrails: 避免模板化 dashboard、随意紫色渐变、重复卡片堆叠、无意义装饰;
- state coverage: default / loading / empty / error / success / permission。

如果已有团队组件库或品牌系统, 体验质量门禁应强化现有系统, 不要用无关美术风格覆盖它。

## 步骤 3: 组件库策略

不要再绝对要求每次普通 design 先调用 `get_library_list`。如果 Codify 工具描述限制
普通设计场景查库，按下面三段式执行。

### 3.1 本地库快照优先

先读用户项目的本地库快照:

```bash
python3 <skill-dir>/scripts/library-snapshot.py list \
  --catalog .codify/library/catalog.json
python3 <skill-dir>/scripts/library-snapshot.py recommend \
  --catalog .codify/library/catalog.json \
  --scenario enterprise
```

本地有可用库时，在 Gate Card 标记 `组件库策略: 本地库快照`，并使用快照中的
`teamLibraryName` / `buildStrategy`。不需要立刻远端查库。

### 3.2 本地无快照时给选择题

```text
组件库策略:
A. 使用团队组件库(推荐): 我会按 Codify 工具要求调用 get_library_list，再让你选库。
B. 暂不使用组件库: 记录为用户拒绝，允许自绘，但后续组件化成本更高。
C. 不确定: 我先说明差异，你再选。
D. 自定义 / type something。
```

用户选择 A 后:

1. `get_library_list`
2. 展示候选和推荐项
3. 用户选定库
4. `get_component_info(teamLibraryName="...", projectDir="...")`
5. 落盘后继续 preflight

用户未明确授权时，不要违反工具描述直接调用 `get_library_list`；也不要静默自绘。

### 3.3 无库或用户拒绝

Gate Card 写明 `组件库策略: 用户拒绝` 或 `无库自绘`。调用 Codify 时允许
`useComponentLibrary=false`，但必须先告知自绘后续组件化成本更高。

## 步骤 4: 写入前 preflight

任何 `design` / `agent_*` / `agent_sync_design` 写操作前必须先:

1. 调用 `get_codify_guidelines`
2. 调用 `get_user_info`
3. 准备符合 Codify 规范的 requirement 或 HTML
4. 运行 preflight

示例:

```bash
python3 <skill-dir>/scripts/codify-preflight.py \
  --task-state .codify/state/mastergo-task.json \
  --guidelines \
  --user-info \
  --component-strategy local-snapshot \
  --team-library-name "Ant Design For AI"
```

有本地 HTML 时追加:

```bash
python3 <skill-dir>/scripts/codify-preflight.py \
  --task-state .codify/state/mastergo-task.json \
  --html .codify/design/overview-tailwind.html \
  --expected-language simplified-chinese \
  --artifact-source current-run \
  --goal "<原始用户目标>" \
  --guidelines \
  --user-info \
  --component-strategy remote-selected \
  --team-library-name "Ant Design For AI"
```

`canWrite=false` 时不得调用写入工具。按 errors 修复后重跑。

## 步骤 5: 选择写入工具并推送

| 任务 | 写入方式 |
|---|---|
| 从零复杂设计 | 优先 `design`，按 task state 的设计单元分批 |
| 新增一个明确页面且已有合规 HTML | `agent_create_page` |
| 局部修改 | 先 `get_selection_code`，再 `agent_update_node` / `agent_replace_node` |
| 删除节点 | 先确认选择或 nodeId，再 `agent_remove_node` |
| 全量覆盖 | 仅用户明确授权时 `agent_sync_design` |

旧本地稿、历史中间稿、英文单页稿不能直接推。先运行:

```bash
python3 <skill-dir>/scripts/codify-artifact-audit.py <html> \
  --source historical \
  --goal "<原始用户目标>" \
  --expected-language simplified-chinese
python3 <skill-dir>/scripts/codify-copy-lint.py <html> \
  --expected simplified-chinese \
  --mode strict
python3 <skill-dir>/scripts/codify-html-lint.py <html>
```

写入工具返回 `accepted` 时:

```bash
python3 <skill-dir>/scripts/mastergo-task-state.py request \
  --request-id "<requestId>" \
  --status accepted
```

最终回复只能说“已发送，待画布验证”，不能说设计完成。

## 步骤 6: 设计完跳验证

写入后立即进入 [verification.md](verification.md) 3A:

- `get_design_diff`
- 截图或用户截图
- `codify-copy-lint.py` 或人工语种抽查
- `component-ratio.sh`(用了组件库时)
- `verification-state.py record`
- `mastergo-task-state.py mark <unit> verified`

没有截图或 diff 时，完成状态是 `blocked: waiting-for-canvas-verification` 或待验证。

## 步骤 7: 反馈和恢复后续作

用户说“不错 / 可以 / 没问题 / 继续”时:

1. `mastergo-task-state.py list` 查剩余单元。
2. 继续下一个 `planned/generated` 单元。
3. 每个单元重复 preflight -> write -> 3A verify。

配置重启、reconnect 或工具恢复后:

```bash
python3 <skill-dir>/scripts/mastergo-task-state.py resume
```

先复述原始目标、Gate Card 和剩余单元，再继续，不要把任务缩成 demo 页。
