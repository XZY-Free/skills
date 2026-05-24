# 05 — MasterGo: Codify 设计 + Magic 还原

MasterGo 子流程双轨入口: **Codify**(在画布上生产/修改设计) 和 **Magic**(把画布导出成代码)。路由判断在 [01-routing.md](01-routing.md#mastergo-子任务路由) 已经做完, 这里只走具体执行。

## 何时读

- 进入 MasterGo 设计任务(Codify 路径)
- 收到 `https://mastergo.com/file/...?layer_id=...` 还原需求(Magic 路径)
- 在还原中需要切换框架或回画布微调

跳过场景: 已经在某条 unit/slice 内推进, 流程已锁定。

## 目录

**Codify 设计**:
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

**Magic 还原**:
- [Magic MCP 可用性门禁](#magic-mcp-可用性门禁)
- [URL 解析](#url-解析)
- [整站目录拉取](#整站目录拉取)
- [拉每页 D2C](#拉每页-d2c)
- [状态记录 + 资源落盘 + token 抽取](#状态记录--资源落盘--token-抽取)
- [前端框架探嗅](#前端框架探嗅)
- [模式选择(默认企业级)](#模式选择默认企业级)
- [模式 A 企业级实现](#模式-a-企业级实现)
- [模式 B 快速复刻 opt-in](#模式-b-快速复刻-opt-in)
- [原型连线限制](#原型连线限制)

---

# Codify 设计

用户要在 MasterGo 画布上生产、修改、维护设计。**真实交付物是 MasterGo 画布成果**, 不是本地 HTML、截图、Markdown 或可粘贴 prompt。

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

写入后立即进入 [07-verification.md](07-verification.md) 3A:

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

# Magic 还原

用户要把 MasterGo 设计稿一次性转成前端代码。真实交付物是可运行且验证过的前端实现, 不是 DSL、D2C HTML、资源目录或截图报告。

还原代码应**保留原设计稿页面文案语言**, 不要在组件化、接 API 或快速复刻时自动翻译 UI 文案。

**两种模式**:

| 模式 | 用途 | 默认 | 代码形态 |
|---|---|---|---|
| **企业级实现** | 真正交付到生产、要接 API、要写业务逻辑 | ✅ | 正常 React/Vue 组件, Tailwind/CSS, 正常 fetch, **D2C 当视觉参考稿** |
| **快速复刻** | 给客户/PM 看效果、临时演示、内部 demo | opt-in | `dangerouslySetInnerHTML` 整段塞 D2C HTML, 数据写死, 像素 100% 一致 |

**模式不混用, 一个项目选一种**。需要切换就重新建工程。

## Magic MCP 可用性门禁

开始还原前确认:

- 当前宿主配置里有 MasterGo Magic MCP, token 不是占位
- 当前会话能看到 `mcp__mastergo-magic-mcp__*` 或等价 Magic 工具
- URL 里有可解析的 `layer_id`
- 用户要整站 → 有根容器 Frame 或每页 Frame 的链接

缺任一项 → 回 [mcp-setup.md](mcp-setup.md) / [troubleshooting.md](troubleshooting.md#magic-排障) 定位阻塞, 按用户行动契约告诉用户缺什么、怎么补、补完后继续什么。**不创建本地前端项目、不手写假页面、不说还原完成**。

只有用户明确改口"没有 MCP, 先根据截图/描述写一个独立前端原型"时, 才离开 MasterGo 还原范围, 转普通前端任务。**不要仍称为 MasterGo 还原完成**。

**不要只因为 `tool_search` 暴露出 Magic MCP 工具就直接调用 `getDsl`**。还原前必须确认当前宿主配置文件里有 `@mastergo/magic-mcp` 和非占位 token。配置缺失/占位时调用工具只会得到误导性的权限错误。

## URL 解析

合法 URL 形态:

```
https://mastergo.com/file/<fileId>?file=<fileId>&layer_id=<a>%3A<b>&pageid=<x>%3A<y>
https://mastergo.com/goto/<short>?file=<fileId>&layer_id=<a>%3A<b>
```

**只取 `layer_id=`**。`%3A` URL-decode 是 `:`, MCP 会自己处理。忽略 `pageid` / `page_id`(那是画布页 Tab, 不是图层 ID)。

优先用脚本解析:

```bash
python3 <skill-dir>/scripts/mandatory/parse-mastergo-url.py \
  'https://mastergo.com/file/193097526299871?layer_id=2%3A77196'
```

脚本输出 `fileId`、`layerId` 和 `contentId`。

短链 `/goto/xxx` 用户没在画布选中状态下复制 → 往往不带 `layer_id=`, 报 `Could not extract layerId from URL`。让用户**画布选中目标 Frame 后重新复制 URL**。

## 整站目录拉取

```
mcp__getDsl(fileId, rootLayerId)  # 一次拿到所有子页面
```

让用户在 MasterGo 里**画一个根容器 Frame 包住所有页面 Frame**, 右键复制根容器链接(必须带 `layer_id=`), 再走这一步。

解析返回 JSON, 遍历根容器 `children`, 每个 type=FRAME、宽度 ≥ 1280 的子节点 = 独立页面。映射成路由, 让用户**确认路由命名**再开干。

整站根容器 DSL 偶尔超过 20MB → 报 `Request too large`。改成对每个子 Frame 单独 `getDsl`, 详见 [troubleshooting.md](troubleshooting.md#magic-request-too-large)。

## 拉每页 D2C

```python
contentId = f"{fileId}-{layerId.replace(':','-')}"
mcp__getD2c(contentId, fileId, outDir=f".mg/{routeKey}")
```

每个页面单独一个 outDir。返回:

```
.mg/<routeKey>/
├── <contentId>.html      # 主 HTML
└── asset/
    ├── icons/*.svg
    └── images/*.png|jpg
```

遇到 `❌ 未找到该 contentId 对应的数据` → 让用户在 MasterGo 里点对应 Frame 的"发送数据"按钮, 等他点完再继续。**不让用户复制 contentId, 你能自己拼**。

## 状态记录 + 资源落盘 + token 抽取

### 状态记录

```json
{
  "restoration": {
    "source": {
      "fileId": "<fileId>",
      "layerId": "<layerId>",
      "contentId": "<contentId>"
    },
    "mode": "enterprise|quick-mirror|pending",
    "pages": [
      {"route": "/dashboard", "language": "simplified-chinese", "dslHash": "...", "d2cHash": "..."}
    ],
    "verification": {"status": "pending"}
  }
}
```

页面主语言从 D2C/DSL 可见文本推断, 后续 JSX、mock、空态、错误态**不要擅自翻译**。

### 资源落盘(两种模式都做)

```bash
bash <skill-dir>/scripts/helpers/sync-d2c-assets.sh .mg src/<project>/public/assets
# 输出: 每个 route 一行 "synced: <route>", 末尾汇总数量
```

跑 update 流时(见 [07-verification.md](07-verification.md#设计稿更新流)): `bash <skill-dir>/scripts/helpers/sync-d2c-assets.sh .mg_v2 src/<project>/public/assets`。

### 设计 token 抽取(仅企业级模式)

```bash
python3 <skill-dir>/scripts/helpers/extract-tokens.py \
  --glob "<projectDir>/.mg/**/*.html" \
  --out "<projectDir>/.codify/design-tokens.json"
```

输出摘要给用户(高频色 top 10 / 字体 / 字号梯度), 建议写进 Tailwind config。

## 前端框架探嗅

走 Magic 还原前必须确认目标框架。流程: **自动探嗅 → 用户选择 → 推荐档查询 → 兜底默认**。

### 探嗅脚本

```bash
ROOT="<projectDir 绝对路径>"
test -f "$ROOT/package.json" && jq '{name, dependencies, devDependencies}' "$ROOT/package.json"
ls "$ROOT" 2>/dev/null | grep -E '(next|vite|nuxt|svelte|astro|remix|gatsby|vue|angular|tailwind|postcss|tsconfig)\.config\.(js|mjs|cjs|ts|json)$'
ls "$ROOT"/*lock* 2>/dev/null
test -d "$ROOT/src" && ls -d "$ROOT/src"/* 2>/dev/null | head -20
test -d "$ROOT/app" && echo "(发现 app/ → 可能是 Next.js App Router)"
test -d "$ROOT/pages" && echo "(发现 pages/ → 可能是 Next.js Pages Router / Nuxt)"
```

### 指纹解读

| 指纹 | 推断 |
|---|---|
| `next.config.*` + `dependencies.next` + `app/` | Next.js App Router 13.4+ |
| `next.config.*` + `pages/` | Next.js Pages Router(老项目) |
| `vite.config.*` + `react` | Vite + React |
| `vite.config.*` + `vue` | Vite + Vue |
| `nuxt.config.*` | Nuxt |
| `svelte.config.*` + `@sveltejs/kit` | SvelteKit |
| `astro.config.*` | Astro |
| `tailwind.config.*` + `@tailwindcss/postcss` | Tailwind v4 |
| `tailwind.config.*` + `postcss.config.js` 旧格式 | Tailwind v3 |
| 只有 `index.html` 无 config | 纯 HTML/CSS |

嗅出后对一句话: "我看到你项目用的是 X, 我按这个栈来还原, 可以吗?"

### 项目空白时

选项: 推荐档(我查最稳最流行) / Next.js 15 + React 19 + Tailwind v4 / Vite + React + TS / 纯 HTML + CSS。

用户选"推荐档"时用 bash + curl 查 npm 趋势 / 最新 stable / 社区调查(**不要 WebSearch / WebFetch**):

```bash
# npm 月下载量
for pkg in next react vue svelte @sveltejs/kit astro nuxt; do
  count=$(curl -sL "https://api.npmjs.org/downloads/point/last-month/$pkg" | jq -r '.downloads // "N/A"')
  echo "$pkg : $count"
done

# 最新 stable 版本
for pkg in next react vue svelte; do
  latest=$(curl -sL "https://registry.npmjs.org/$pkg/latest" | jq -r '.version')
  echo "$pkg latest: $latest"
done
```

简短总结给用户(3-5 句), 给出 1 个推荐 + 1 个候补。**所有数字基于实际查询, 不允许编造**。

### 兜底默认

所有分支失败 → **Next.js 15 + React 19 + TypeScript + Tailwind v4**。理由: 还原脚手架基于此栈模板齐全, SSR/静态/API 都覆盖, D2C HTML 用 `dangerouslySetInnerHTML` 在 React 系最自然。默认时也告诉用户"我先按此栈走, 不喜欢可以换"。

### 探嗅结果存放

```json
{
  "framework": {
    "name": "next.js",
    "version": "15.1.0",
    "router": "app",
    "ui": ["tailwindcss@4", "react@19"],
    "language": "typescript",
    "detectedAt": "<ISO 时间>",
    "source": "package.json"
  }
}
```

写入 `.codify/state.json`, 后续会话直接读。

### 切换框架

| 切换 | 改动量 |
|---|---|
| Next.js App ↔ Pages Router | 改路由层, page 文件不动 |
| Next.js ↔ Vite + React | 重建工程, React 组件代码可复用 |
| React ↔ Vue/Svelte | 几乎重写, 但 D2C HTML 可继续用 `v-html` / `{@html}` |

切换前一定让用户口头确认, **不要默默切**。

## 模式选择(默认企业级)

**默认走企业级实现**。**只有以下情况切快速复刻**:

- 用户明确说"快速复刻 / 高保真原型 / 给客户看一眼 / 像素 100% 一致"
- 用户明确说"不用接 API / 数据先写死"
- 用户明确说"我不想要 React 组件, 我要 dangerouslySetInnerHTML"

走快速复刻前**显式跟用户确认一次**:

> 你确认要走快速复刻模式吗? 这种模式产物**不适合接 API、不适合生产**, 只适合临时演示。后续要接 API 必须重做一遍企业级模式。还是要走?(yes / no)

## 模式 A 企业级实现

**D2C HTML 是视觉参考稿, 不是代码来源**。参照 D2C 写正常 React 组件, Tailwind 抄设计 token, SVG/PNG 直接用, 字体/蒙版/渐变用正常 CSS。**像素精度对齐 95-98%(允许小差异), 换来可维护/可测试/可演进**。

### A.1 Tailwind 配置(吃设计 token)

```typescript
import type { Config } from 'tailwindcss'

export default {
  content: ['./src/**/*.{ts,tsx,html}'],
  theme: {
    extend: {
      colors: {
        bg:       { canvas: '#0A0E1A', card: '#111729' },
        brand:    { 500: '#4FB8FF', 600: '#3BA8F0' },
        text:     { primary: '#FFFFFF', muted: '#9CA3AF' },
      },
      fontFamily: {
        display: ['DingTalk JinBuTi', 'PingFang SC', 'system-ui', 'sans-serif'],
        body:    ['PingFang SC', 'system-ui', 'sans-serif'],
      },
      // fontSize / spacing 按 design-tokens.json 抽到的梯度填
    },
  },
} satisfies Config
```

字体加载用 `next/font/local` 或 CDN `@font-face`(详见 [07-verification.md](07-verification.md#渲染补丁))。

### A.2 组件分解策略

D2C HTML 里的 `data-name="..."` 就是天然组件边界:

| D2C 节点 | 处理 |
|---|---|
| 一级 `data-name`(`topbar` / `hero` / `grid`) | → 一个 React 组件 `<TopBar />` |
| 二级带语义的 `data-name`(`brand` / `breadcrumb`) | → 子组件 |
| 重复结构(`act-1` / `act-2` / `act-3`) | → 一个组件 + `.map()` |
| 无 `data-name` 或语义模糊 | → 不单独拆, 留在父组件 |

先输出简短组件树清单。高置信、用户已说"直接做"时**自动执行**; 低置信或会影响公共组件边界时再选择。

### A.3 写 JSX(数据先写死)

D2C 给的:

```html
<div data-name="hero" style="background: #111729; padding: 32px; border-radius: 16px">
  <h1 style="font-family: 'DingTalk JinBuTi'; font-size: 48px; color: #FFFFFF">AURA Agent</h1>
  <p style="font-size: 16px; color: #9CA3AF; margin-top: 8px">智能客服系统</p>
</div>
```

改写成 JSX:

```tsx
export function Hero({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="bg-bg-card p-8 rounded-2xl">
      <h1 className="font-display text-5xl text-text-primary">{title}</h1>
      <p className="text-base text-text-muted mt-2">{subtitle}</p>
    </div>
  )
}
```

视觉参考做法: MasterGo 截图 + 你写的 JSX 渲染截图并排, 用 [07-verification.md](07-verification.md#3b-2-企业级实现验证) 3B-2 检查。差 1-3px 是可接受代价。

### A.4 接 API

写完 JSX 后**自动扫 `.codify/api-docs/`**:

- 找到接口文档 → 跑 `scripts/helpers/parse-api-docs.py` 生成 `.codify/api-endpoints.json`, 走 [06-implementation.md](06-implementation.md#api-接入) 完整流程
- 没找到 → 友好提示用户怎么放, 等用户回应

**接 API 是企业级实现的标配步骤, 不接 API = 没做完**。即使用户暂时没接口文档, 也明确告诉他"现在数据是写死的, 接到 API 才算完整生产代码"。

用户明确说"暂时没有接口文档" → 状态标 `api-pending`, **不假装真数据已接入**。

### A.5 路由 / 入口

每页一个路由(Next.js App Router):

```tsx
// src/app/agent-detail/page.tsx
import { AgentDetailPage } from '@/components/agent-detail/AgentDetailPage'

export default async function Page() {
  const data = await getAgentDetail()
  return <AgentDetailPage data={data} />
}
```

`NavBar` 这种跨页导航抽到 `src/components/NavBar.tsx`, `app/layout.tsx` 全局挂载。

### A.6 验证

走 [07-verification.md](07-verification.md#3b-2-企业级实现验证) 3B-2:

- 视觉相似度 ≥ 95%(允许小差异)
- 接 API 后真数据正确渲染
- **强制打印 API 溯源汇报**
- 业务逻辑测试覆盖(可选)

## 模式 B 快速复刻 opt-in

**只有用户明确选这条路才进**。产物**不适合接 API、不适合生产**。后续如果用户要接 API、权限、表单提交或真实业务逻辑, **必须切回企业级实现重做**, 不要在 `dangerouslySetInnerHTML` 原型上硬接生产逻辑。

本模式**不抽设计 token**(`extract-tokens.py` 不跑), 整段 HTML 直接装载。

### B.1 脚手架(Next.js 15 + React 19 + Tailwind v4)

`package.json`:

```json
{
  "dependencies": { "next": "^15.1.0", "react": "^19.0.0", "react-dom": "^19.0.0" },
  "devDependencies": {
    "@tailwindcss/postcss": "^4.0.0",
    "@types/node": "^22", "@types/react": "^19", "@types/react-dom": "^19",
    "tailwindcss": "^4.0.0", "typescript": "^5"
  }
}
```

`postcss.config.mjs`: `{ plugins: { "@tailwindcss/postcss": {} } }`

`src/app/globals.css` 顶部:

```css
@import "tailwindcss";
@font-face {
  font-family: "DingTalk JinBuTi";
  src: url("https://cdn.jsdelivr.net/gh/cn-fontsource/cn-fontsource-ding-talk-jin-bu-ti/dist/font.woff2") format("woff2");
  font-display: swap;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
```

末尾追加 [07-verification.md](07-verification.md#渲染补丁) 的全局补丁 CSS。

### B.2 装载 D2C HTML

`src/lib/load-design.ts`:

```typescript
import fs from "node:fs"
import path from "node:path"

export function loadDesignHtml(page: string): string {
  const abs = path.join(process.cwd(), "src", "design", `${page}.html`)
  const raw = fs.readFileSync(abs, "utf-8")
  const rewritten = raw.replace(/\.\/asset\//g, `/assets/${page}/`)
  const cleaned   = rewritten.replace(/,\s*NaN\)/g, ", 1)")  // SVG 渐变 alpha 修
  const m = cleaned.match(/<body[^>]*>([\s\S]*)<\/body>/i)
  return m ? m[1] : cleaned
}
```

每个路由 `page.tsx`:

```tsx
import { loadDesignHtml } from "@/lib/load-design"

export default function Page() {
  const html = loadDesignHtml("agent-detail")
  return (
    <div className="design-page grid min-h-screen place-items-center bg-[#f0f3fa] p-4">
      <div
        className="relative shadow-2xl ring-1 ring-black/5"
        style={{ width: 1440, height: 900, overflow: "hidden" }}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  )
}
```

### B.3 NavBar(多页跳转条)

`src/components/NavBar.tsx`:

```tsx
import Link from "next/link"

const ROUTES = [
  { href: "/", label: "首页" },
  { href: "/agent-detail", label: "Agent 详情" },
]

export default function NavBar({ active }: { active: string }) {
  return (
    <nav className="fixed left-1/2 top-3 z-50 flex -translate-x-1/2 gap-1 rounded-full bg-white/80 p-1 shadow-md ring-1 ring-black/5 backdrop-blur">
      {ROUTES.map(r => (
        <Link key={r.href} href={r.href}
          className={
            "rounded-full px-3 py-1.5 text-xs " +
            (active === r.href ? "bg-[#2C68FF] text-white" : "text-[#1A1C27] hover:bg-black/5")
          }
        >
          {r.label}
        </Link>
      ))}
    </nav>
  )
}
```

### B.4 验证

走 [07-verification.md](07-verification.md#3b-1-快速复刻验证) 3B-1 像素全等比对。

## 原型连线限制

**MasterGo Magic MCP 不下发画布上画的 Frame ↔ Frame 原型连线** — 这是 MCP 协议的能力边界, 不是 bug、不是缓存、不是同步问题。

跨 Frame 跳转用自然语言确认后, 代码里手写 `<Link>` / `router.push`。完整诊断方法见 [troubleshooting.md](troubleshooting.md#dsl-看不到画布上画的原型连线)。
