---
name: opc-delivery
description: OPC 一人公司式产品交付工作流，把粗糙业务需求推进成已验证、可部署、可回放校准的产品增量。Use whenever Codex must drive requirement discovery, PRD, solution/UI design, MasterGo/Codify canvas work, MasterGo Magic D2C/C2D restoration, frontend implementation, API wiring, validation, CI/CD, preview/production deployment, release evidence, rollback planning, or shipped-feature replay. Also use for MasterGo URLs, mastergo://, Codify MCP, Magic MCP, D2C/DSL, layerId/contentId, and MasterGo component libraries. Do not use for unrelated Figma, generic MCP/token setup, casual codify wording, or ordinary frontend-only work not framed as OPC/full-cycle delivery.
---

# OPC 产品交付技能

定位: 把“一个啥也不懂的业务员给一个需求”推进成可验证上线结果。这个 skill 不是
单纯的 MasterGo 设计稿转代码工具；MasterGo/Codify/Magic 是 OPC 全流程里的设计与
还原能力模块。

每个新任务先读 [opc-flow.md](references/opc-flow.md)，判断是完整 OPC 交付、
MasterGo 设计 / 还原子任务、更新流、部署流，还是需要选择题澄清。
完整 OPC 任务还要按 [open-source-patterns.md](references/open-source-patterns.md)
补一张 Pattern Card，把优秀开源 skill 的方法压缩成门禁，而不是复述来源。

## 运行要求

| 类型 | 要求 |
|---|---|
| 必需运行时 | `python>=3.11`, `node>=18` |
| 设计 MCP | `mcp__codify__*` 用于 MasterGo 画布设计 |
| 还原 MCP | `mcp__mastergo-magic-mcp__*` 用于 MasterGo D2C/DSL |
| 常用验证 | Browser / Playwright、lint、typecheck、unit/e2e、构建、部署状态 |
| 可选工具 | `git`, `gh`, `vercel`, `jq` |

缺 MCP、token、当前宿主配置或本会话工具时，先走 [mcp-setup.md](references/mcp-setup.md)。
不要把本地 HTML、Markdown、prompt、截图、DSL 或 D2C 包装成真实完成。

## 触发边界

| 场景 | 关键词 / 信号 |
|---|---|
| OPC 全流程 | OPC、一人公司、从需求到上线、业务员给需求、需求分析、PRD、UI 设计、前端实现、部署 |
| 阶段交付 | 需求文档、方案文档、设计稿、前端项目、验收报告、部署链接、回滚方案 |
| MasterGo | MasterGo, Codify, Magic MCP, D2C, C2D, DSL, `mastergo://`, `mastergo.com`, `layerId`, `contentId` |
| Codify 设计 | 在画布上设计/创建/修改/优化页面，调整布局/颜色/字号/间距，替换节点，同步组件 |
| Magic 还原 | 还原、转代码、复刻、实现成前端、跑起来、高保真、像素级 |
| CI/CD 上线 | preview deployment、production、GitHub Actions、Vercel、服务器、环境变量、回滚 |
| 校准沉淀 | 已上线需求重放、AI 与人工结果对比、沉淀宪法/规约/规则 |

不要为 Figma、通用 D2C、通用 MCP、纯前端页面、通用 token 配置或普通英文单词
`codify` 触发本 skill，除非用户明确把它放进 OPC 全流程。

## 核心契约

这些契约贯穿所有 reference。遇到同名契约时回到这里确认硬规则。

### 阶段交付物契约

- 完整 OPC 交付按阶段推进: 需求 -> 方案 -> UI 设计 -> 前端实现 -> 验证 -> 部署 -> 复盘。
- 每阶段结束必须有交付物、验收口径和下一阶段输入；没有交付物不能假装阶段完成。
- 阶段状态写入 `.opc/state/opc-task.json`；用 `scripts/opc-task-state.py` 初始化、标记和完成校验。
- 用户明确说“跳过文档 / 直接做”时，可以压缩文档，但仍要保留最小 Stage Card 和验收标准。
- 生产部署、推送远端、覆盖 MasterGo 画布、写入 secrets 等有副作用动作必须确认真实意图。

### 自动轮转契约

- 完整 OPC 任务默认连续推进，直到可访问的上线交付证据出现，或被硬阻塞标记为 `blocked`。
- “确认当前阶段”是代理判断和状态记录，不是每个阶段都等待用户点头；用户没说“暂停 / 停下 / 只做当前阶段”，阶段完成后立即进入下一阶段。
- 正向反馈、沉默授权、`继续 / 你决定 / 后面都做完` 都视为继续推进授权；不要用“是否继续”作为常规停点。
- 只有这些情况才能暂停提问: blocker 会改变真实交付物、验收标准或部署风险；缺 token/URL/API key/权限；或涉及生产部署、远端推送、覆盖写入、付费资源、写 secrets 等高风险副作用。
- 如果用户要求上线但未明确生产环境，自动推进到安全的 preview/staging 可访问链接；production 仍需显式授权和 release gate。
- 从中间阶段恢复时，先恢复 Stage Card 和状态台账，然后从当前阶段继续向后轮转，不要只补一份报告后结束。
- 完整 OPC 请求如果已经完成 PRD、方案和 UI，下一步默认是进入 `implementation`，不是等待用户在“MasterGo 画布 / 前端原型 / API 契约 / 产品评审”之间重新选号。
- 用户给的是从零开始的新需求、当前工作区又没有现成仓库时，代理要按方案里选定的框架自动起实现脚手架并继续交付；“空工作区”不是把完整 OPC 缩成“只交设计包”的理由。

### 自治补齐契约

- 完整 OPC 交付里，缺 Git 仓库、前端脚手架、`package.json`、mock 数据、测试命令、CI/CD 或本地预览配置时，默认由代理补齐；先读 [autonomous-bootstrap.md](references/autonomous-bootstrap.md)。
- 当前业务工作区没有 `.git/` 且不在父级 Git 仓库内时，代理应执行 `git init`、补 `.gitignore`，并继续实现；不要让用户先创建仓库。
- 只有 API key/token/secret、服务器/域名/账号权限、production、远端 push、付费资源、覆盖写入、破坏性迁移、不可推断的品牌风格或合规边界，才作为暂停确认门。
- 确认门默认给 2-3 个选择项和“自定义 / type something”；用户选完或说“你决定”后，立即继续自动轮转。

### 上下文持久化契约

- 每次进入完整 OPC、阶段交付或“继续上次”任务时，代理自己读 [context-persistence.md](references/context-persistence.md)，自动恢复或初始化 `.opc/state/opc-task.json`。
- `opc-task-state.py resume/init/mark/note` 是代理命令，不让用户手动执行；用户只需要说“继续上次”。
- 每次阶段完成、阻塞、暂停、需要用户动作或交接新会话前，都必须记录状态、产物路径、证据摘要和 `nextAction`。
- 大产物主动拆到 `.opc/<phase>/` 多文件；状态台账只存摘要和路径，不存完整 PRD、长日志、代码或会议纪要。

### 开源交付门禁契约

- 这个 skill 融合开源优秀 skill 的工作法: discovery-before-build、JTBD、MoSCoW、
  2-3 个方案对比、planning packet、TDD/regression ratchet、systematic debugging、
  evidence-before-completion、release packet、premortem、red-team 和 AAR。
- 完整 OPC 任务在 Stage Card 后补 Pattern Card；轻量任务至少保留适用的门禁和跳过原因。
- 这些模式必须落成阶段产物、检查项或状态记录；不要把开源 skill 名单当成交付物。
- 如果用户明确要求跳过某个阶段，仍要记录对应风险和最小替代证据。

### 需求覆盖契约

- 交付范围由业务目标、角色、核心流程、数据、边界、非功能要求和验收口径决定。
- 不靠“企业级/平台/后台”等关键词机械判断页面数量、模块数量或实现深度。
- 从零设计、大范围改版、配置恢复后继续时，必须先形成覆盖 brief、PRD 或 Gate Card。
- 不得把完整需求擅自缩成首页、首屏、概念代表页或单页 dashboard。
- 正向反馈是继续执行授权；覆盖未闭合时继续下一设计单元或阶段。

### 选择题澄清契约

- 除 token、URL、截图、文件路径、layerId、API key 等必须填空的信息外，澄清默认用选择题。
- 给 2-3 个可执行选项，第一个放推荐项，最后保留“自定义 / type something”。
- 用户说“你决定 / 直接做”时，可以自动选择，但必须在 OPC Stage Card 或 Gate Card 写明依据。
- 若缺的信息会改变真实交付物、验收标准或部署风险，先问；若只是实现细节，按项目惯例继续。

### UI 文案语种契约

- 页面导航、标题、按钮、表格、状态、空态、错误、审批、审计、监控和日志文案跟随用户指定、素材语言和聊天主语言。
- 中文聊天或中文素材默认简体中文 UI；不要把企业后台默认生成英文 Dashboard。
- MasterGo、Codify、AI、Agent、API、MCP、D2C、SLA、SSO、RBAC、AgentOps、CI/CD 等技术词可保留原文。
- 语种规则必须写进 PRD、Codify requirement、HTML 或实现说明，并在推送前和验证中检查。

### token 安全契约

- token/key 是每用户每机器索取一次，绝不复用、硬编码或复制其它会话的值。
- 只写当前宿主 user-scope 本地配置或目标平台安全变量，不进版本控制。
- 收到 token 后只脱敏回显，保留前缀和末 4 位，中间用 `*`。
- 用户把完整 token/key 贴进聊天时，提醒它已进入会话记录，配置成功后建议 revoke / rotate。
- `tool_search` 暴露工具、其它宿主已配置、demo token 看似可用，都不是当前宿主已配置证据。

### 证据与状态契约

- HTTP 200、命令退出码 0、本地 HTML 存在、`accepted`、代码列表非空都不算最终完成证据。
- 完成必须有阶段交付物、测试/截图/浏览器验证、部署状态、`get_design_diff` 或 API 溯源报告等证据。
- `.opc/state/opc-task.json` 和 `.codify/state/mastergo-task.json` 是恢复和门禁来源，不是完成证据。
- `accepted` 必须进入 pending 状态；没有画布 diff、selection code 或截图时只能说待验证。

### 专业完成定义

- 交付不是活动报告；必须证明用户目标、核心流程、关键状态、风险处理和上线证据闭合。
- 需求、方案、UI、实现、验证、部署任一阶段被跳过时，必须写清跳过授权、风险和替代证据。
- 对外宣称“完成 / 已上线 / 可交付”前，读 [delivery-contract.md](references/delivery-contract.md) 的专业完成定义。
- 无法获得真实证据时，用 `blocked`、`pending` 或 `skipped with reason`，不要用乐观话术补洞。

## OPC Stage Card

完整 OPC 任务在写代码、写 MasterGo 或部署前，先给用户可见的 Stage Card。
高置信时直接填好并继续；低置信时只问关键选择题。Stage Card 是自动轮转起点，
不是等待用户批准的停点。

```text
OPC Stage Card
- 真实交付物: PRD / 设计稿 / 前端代码 / 部署链接 / 自定义
- 当前阶段: 需求 / 方案 / UI 设计 / 实现 / 验证 / 部署 / 校准
- 业务目标: <用户要解决的问题和成功标准>
- 覆盖范围: <角色、流程、页面、状态、数据、权限、接口>
- 阶段交付物: <本阶段要产出的文件、画布结果、代码或链接>
- 验收方式: <测试、截图、diff、API 溯源、部署检查；用户确认只作补充证据>
- 风险 / 缺口: <待澄清项、能力缺失、环境缺失、付费工具>
- 停止条件: <只有哪些 blocker 或高风险副作用会暂停>
- 下一步: <自动进入哪个 reference 和要执行什么>
```

## 工作流总览

```text
0. OPC intake / route / Stage Card
   -> references/opc-flow.md

0.5 开源交付模式门禁
   Pattern Card -> JTBD/MoSCoW -> 方案对比 -> 验证/发布/校准门禁
   -> references/open-source-patterns.md

0.75 自治补齐门禁
   missing repo/package/test/CI/deploy defaults -> create locally or ask only for real gates
   -> references/autonomous-bootstrap.md

1. 需求阶段
   PRD + 验收标准 + open questions + state
   -> references/requirements-workflow.md

2. 方案阶段
   信息架构 + UI 策略 + 技术方案 + 测试/部署计划
   -> references/solution-design.md

3A. MasterGo/Codify UI 设计
   MasterGo 设计 Gate Card -> task state -> preflight -> write -> 3A verify
   -> references/design-workflow.md

3B. MasterGo Magic 还原
   URL parse -> DSL/D2C -> enterprise/quick mode -> implementation -> 3B verify
   -> references/restoration-workflow.md

4. 无 MasterGo 来源的前端实现
   repo/framework detect -> components/state/API -> browser QA
   -> references/implementation-workflow.md

5. CI/CD 和部署
   build/test -> preview -> env/secrets -> production gate -> rollback evidence
   -> references/deployment-workflow.md

6. 已上线需求回放校准
   golden input -> AI replay -> gap analysis -> rule update
   -> references/regression-calibration.md
```

完整 OPC 任务按上面顺序自动轮转。阶段产物是交接输入，不是自然停点；只有用户要求暂停、
硬阻塞或高风险副作用确认门禁才暂停。

## MasterGo 子流程最低要求

用户要在 MasterGo 画布上设计或修改时，读 [design-workflow.md](references/design-workflow.md)。

必须按顺序处理:

1. 确认当前宿主 Codify MCP 可用，缺失则回 MCP 配置流程。
2. 生成 MasterGo 设计 Gate Card，并与 OPC Stage Card 的需求覆盖一致。
3. 用 `scripts/mastergo-task-state.py init` 初始化 `.codify/state/mastergo-task.json`。
4. 先读本地 `.codify/library/catalog.json`；只有用户授权或明确选择组件库时才远端查库。
5. 写入前运行 `scripts/codify-preflight.py`；preflight 不通过不得调用写入工具。
6. 写入后用 `scripts/mastergo-task-state.py mark/request` 更新状态。
7. 进入 [verification.md](references/verification.md) 3A；`accepted` 只算 pending。

用户要把 MasterGo 设计稿还原成代码时，读 [restoration-workflow.md](references/restoration-workflow.md)。

必须按顺序处理:

1. 用 `scripts/parse-mastergo-url.py` 解析 URL，只信 `layer_id`。
2. 确认当前宿主 Magic MCP 配置和工具可用；`tool_search` 不是配置证据。
3. 记录 source fileId/layerId/contentId、页面主语言、模式和验证状态。
4. 默认企业级实现；快速复刻只能在用户明确 opt-in 后使用。
5. D2C/DSL 原始输出不是完成；必须实现、运行、截图或测试，并按 3B 验证。

## 引用文件何时读

| 文件 | 何时读 |
|---|---|
| [opc-flow.md](references/opc-flow.md) | 每个新任务入口、阶段路由、OPC Stage Card、交付物链路 |
| [context-persistence.md](references/context-persistence.md) | 新会话恢复、状态台账、nextAction、阶段产物主动拆分 |
| [open-source-patterns.md](references/open-source-patterns.md) | 完整 OPC 交付、skill 优化、需求到上线闭环、上线回放校准 |
| [requirements-workflow.md](references/requirements-workflow.md) | 需求访谈、PRD、用户故事、验收标准、open questions |
| [solution-design.md](references/solution-design.md) | 需求已基本闭合后做方案、信息架构、接口/数据/权限/测试计划 |
| [implementation-workflow.md](references/implementation-workflow.md) | 无 MasterGo 来源或已完成设计后进入前端框架实现 |
| [deployment-workflow.md](references/deployment-workflow.md) | 用户要求部署、CI/CD、服务器、Vercel、GitHub Actions、环境变量、回滚 |
| [regression-calibration.md](references/regression-calibration.md) | 用已上线需求回放校准 skill、沉淀宪法/规约 |
| [mcp-setup.md](references/mcp-setup.md) | MCP 缺失、token 配置、宿主切换、Codify bridge、本地/远端 URL 排障 |
| [delivery-contract.md](references/delivery-contract.md) | 判断真实交付物、阻塞条件、禁止替代交付 |
| [intent-routing.md](references/intent-routing.md) | MasterGo/Codify/Magic 子任务路由 |
| [design-workflow.md](references/design-workflow.md) | Codify 画布设计、修改、查看页面 |
| [design-scope.md](references/design-scope.md) | 覆盖 brief、任务台账、恢复继续 |
| [design-coverage-patterns.md](references/design-coverage-patterns.md) | 复杂平台覆盖模板，尤其企业级/AgentOps/客服运营类产品 |
| [copy-language.md](references/copy-language.md) | UI 文案语种判断、requirement 注入、copy lint |
| [codify-push-protocol.md](references/codify-push-protocol.md) | Codify 写入前规范、用户信息、preflight、accepted pending |
| [restoration-workflow.md](references/restoration-workflow.md) | Magic 还原双模式入口 |
| [restoration-enterprise.md](references/restoration-enterprise.md) | 默认企业级实现、组件拆分、API wiring |
| [restoration-fast-prototype.md](references/restoration-fast-prototype.md) | 用户明确 opt-in 快速复刻 |
| [framework-detect.md](references/framework-detect.md) | 还原前框架选择 |
| [api-wiring.md](references/api-wiring.md) | 接 API、字段映射、数据层 |
| [api-doc-parsing.md](references/api-doc-parsing.md) | OpenAPI/Postman/Markdown 接口文档解析 |
| [api-field-mapping.md](references/api-field-mapping.md) | 字段检测、字段映射、用户确认 |
| [api-trace-report.md](references/api-trace-report.md) | API 字段溯源汇报 |
| [verification.md](references/verification.md) | Codify 3A 和 Magic 3B 验证入口 |
| [verification-implementation.md](references/verification-implementation.md) | Magic 实现完详细验证 |
| [update-flow.md](references/update-flow.md) | 设计稿变更后的增量同步 |
| [troubleshooting.md](references/troubleshooting.md) | 任意 MCP、渲染、配置异常入口 |
| [troubleshooting-magic.md](references/troubleshooting-magic.md) | Magic MCP getDsl/getD2c/getMeta 报错 |
| [troubleshooting-codify.md](references/troubleshooting-codify.md) | Codify design/agent/library/bridge 报错 |
| [rendering-patches.md](references/rendering-patches.md) | D2C 渲染补丁 CSS、字体、mask、SVG 修复 |

## 脚本索引

| 脚本 | 用途 |
|---|---|
| `scripts/opc-task-state.py` | 初始化、标记、校验 `.opc/state/opc-task.json` |
| `scripts/check-mcp-config.py` | 检查当前宿主 MCP 配置、token 占位、本地/远端 Codify URL |
| `scripts/parse-mastergo-url.py` | 从 MasterGo URL 提取 fileId/layerId/contentId |
| `scripts/mastergo-task-state.py` | 初始化、恢复、标记、校验 `.codify/state/mastergo-task.json` |
| `scripts/library-snapshot.py` | 读取/校验本地 `.codify/library/catalog.json` 和组件库快照 |
| `scripts/codify-html-lint.py` | Codify HTML 结构与 Tailwind 合规检查 |
| `scripts/codify-copy-lint.py` | 推送前检查可见 UI 文案语种 |
| `scripts/codify-artifact-audit.py` | 旧 HTML / 本地中间稿来源、覆盖和 CSS 风险审计 |
| `scripts/codify-preflight.py` | Codify 写入前综合门禁 |
| `scripts/component-ratio.sh` | 统计组件库映射率 |
| `scripts/verification-state.py` | 验证证据归档和完成摘要 |
| `scripts/dsl-diff.py` | Magic 更新流 DSL 结构 diff 和语种风险标记 |
| `scripts/parse-api-docs.py` | 扫 `.codify/api-docs/` 生成 `.codify/api-endpoints.json` |
| `scripts/extract-tokens.py` | 从 D2C HTML 抽颜色/字体/字号 token |
| `scripts/sync-d2c-assets.sh` | 同步 D2C assets 到前端项目 |
| `scripts/screenshot.mjs` | Playwright 截图兜底 |
| `scripts/fetch-doc-snippet.py` | 按关键词读取官方文档片段 |
| `scripts/check-skill-rules.py` | 发布前检查必需规则、脚本和 eval |
| `scripts/check-release-env.py` | 检查 release gate 依赖 |

## 沟通风格

简短、直接、给证据。中文回复，技术名词如 `layerId`、`DSL`、`D2C`、`contentId`、
`useComponentLibrary`、`buildStrategy`、`preview deployment`、`rollback` 保留原文。

用户问“好了吗”时，回答当前阶段、已完成交付物和证据。没有证据就说“待验证”，不要只回“完成”。
