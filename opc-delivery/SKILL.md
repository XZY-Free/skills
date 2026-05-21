---
name: opc-delivery
description: "OPC 一人公司式产品交付工作流，把粗糙业务需求推进成已验证、可部署、可回放校准的产品增量。Use when Codex must run OPC/full-cycle delivery: requirements discovery, PRD, solution/UI design, implementation planning, full-stack implementation, validation, CI/CD, preview/production release evidence, rollback planning, or shipped-feature replay. Also use for MasterGo-backed delivery involving MasterGo URLs, mastergo://, Codify MCP, Magic MCP, D2C/DSL, layerId/contentId, or MasterGo component libraries. Do not use for unrelated Figma, generic MCP/token setup, casual codify wording, framework selection, ordinary frontend-only work, or standalone page implementation not framed as OPC/full-cycle or MasterGo-backed delivery."
---

# OPC 产品交付技能

定位: 把一句粗糙业务目标推进成**能登录、能操作、数据能持久化、验证和部署有证据**的产品增量。MasterGo、Codify、Magic、Node、数据库和持续集成只是能力模块, 主线永远是成品交付。

每个新任务先读 [opc-flow.md](references/opc-flow.md) 路由。若进入完整 OPC, 默认连续推进到验证和部署证据; 只有高影响不确定、硬阻塞或用户明确暂停才停。

## 运行要求

| 类型 | 要求 |
|---|---|
| 必需运行时 | `node>=18`, `python>=3.11` |
| 默认后端栈 | Next.js API routes / Hono / Fastify / Express(Node 系) |
| 默认数据层 | SQLite(本地开发) / Postgres(部署), 配 Prisma 或 Drizzle |
| 设计工具 | `mcp__codify__*` 用于 MasterGo 画布设计 |
| 还原工具 | `mcp__mastergo-magic-mcp__*` 用于 MasterGo D2C/DSL |
| 常用验证 | Browser / Playwright、lint、typecheck、unit/e2e、build、部署状态 |
| 可选工具 | `git`, `gh`, `vercel`, `jq` |

缺 MCP、token、当前宿主配置或本会话工具时, 读 [mcp-setup.md](references/mcp-setup.md)。不要把本地 HTML、Markdown、prompt、截图、DSL 或 D2C 包装成真实完成。不要把 typed mock 包装成真实可用产品, 除非用户明确选择演示版。

## 触发边界

| 场景 | 关键词 / 信号 |
|---|---|
| OPC 全流程 | OPC、一人公司、从需求到上线、业务员给需求、需求分析、PRD、UI 设计、前端实现、部署 |
| 阶段交付 | 需求文档、方案文档、设计稿、实现计划、全栈项目、验收报告、部署链接、回滚方案 |
| MasterGo | MasterGo, Codify, Magic MCP, D2C, C2D, DSL, `mastergo://`, `mastergo.com`, `layerId`, `contentId` |
| Codify 设计 | 在画布上设计/创建/修改/优化页面, 调整布局/颜色/字号/间距, 替换节点, 同步组件 |
| Magic 还原 | 还原、转代码、复刻、实现成前端、跑起来、高保真、像素级 |
| CI/CD 上线 | preview deployment、production、GitHub Actions、Vercel、服务器、环境变量、回滚 |
| 校准沉淀 | 已上线需求重放、AI 与人工结果对比、沉淀宪法/规约/规则 |

不要为 Figma、通用 D2C、通用 MCP、纯前端页面、通用 token 配置或普通英文单词 `codify` 触发本 Skill, 除非用户明确把它放进 OPC 全流程。

## 核心契约

这些契约是硬规则。细节放在 `references/`, 确定性校验放在 `scripts/` 和 `evals/`。

### 用户侧交互模型

OPC 是**成品驱动 / 疑点触发确认 / 证据驱动完成**。

- 阶段卡和确认卡是内部工具, 用来记录推理、默认假设和阶段状态; 不作为用户默认可见流程。
- 用户默认只需要看到结果摘要: 目标、已交付、正在推进、需要用户提供什么、接下来。
- 用户询问进度时, 先用 `opc-task-state.py brief` 或等价摘要回答; `summary` / `resume` 的 raw phase、artifact、evidence、nextAction 只给代理恢复用, 不默认贴给普通用户。
- 不要求每个阶段都至少一轮用户确认。需求已经足够明确时, 直接进入产物、实现、验证和部署。
- 不懂且会改变最终成品时不要假设; 用宿主原生选择/确认交互让用户拍板。

### 自动轮转契约

定义阶段(intake / requirements / solution / ui-design / implementation-plan)的目标是把交付物做对, 不是让用户看流程卡。执行阶段(implementation / verification / deployment / calibration)默认连续推进。

- 阶段产物是下一阶段输入, 不是自然停点。
- 用户说“从需求到上线 / 后面都做完 / 你负责”时, 视为完整链路授权。
- 只有用户明确说停、硬阻塞或高影响副作用确认门禁才暂停。
- 内部讨论没收敛时不要标记阶段完成; 无高影响疑点时不要为了流程感打断用户。
- `ui-design` 后必须先进入 `implementation-plan`, 写出可分片读取的技术实现总方案和开发计划; 没有该阶段产物不得直接进入代码实现。

### 选择交互澄清契约

只有高影响不确定才问用户:

- 真实数据还是演示数据;
- 权限深度、审计、合规、品牌硬约束;
- 部署目标、production 发布、远端 push;
- API key、token、secret、账号权限、私有 URL、服务器地址;
- 付费资源、外部服务开通、破坏性写入或迁移;
- 会改变交付范围的用户 framing, 例如“企业级 / 完整 / 生产级 / 智能 / 后台”。

低风险工程细节直接自治: 文件名、目录、小依赖、helper 拆法、内部路由、mock seed、可逆默认值、本地脚手架。

需要用户拍板时, 优先使用当前宿主真实结构化交互: Codex App 的 `request_user_input`、Claude Code / 其它 runner 暴露的 confirm/select/prompt、OMX question bridge 或等价 native UI。真实选择放工具里, 推荐项放第一并标推荐, 保留自定义入口。工具不可用时才文本降级为 A/B/C/D + 默认 + 自定义 / type something。

### 阶段交付物契约

OPC 默认交付真实全栈产品:

- 前端能访问, 用户能登录和操作;
- 数据默认真实持久化, 本地 SQLite、部署 Postgres, 配 Prisma 或 Drizzle;
- 后端默认 Node 系: Next.js API routes、Hono、Fastify、Express;
- 没有接口文档时, 代理按需求设计真实 API 和数据模型;
- `.env.example` 自动生成, 真实 secret 只进用户级配置或部署平台安全变量;
- 只有用户明确说“演示版 / 不要真后端 / 只做展示”时, 才允许 mock 成为交付目标。

`真实交付物`不写“或”假设。部署目标、数据来源或权限范围不明确且会改变成品时, 走选择交互。

### 实现规划契约

完整 OPC 在实现前必须读 [implementation-planning.md](references/implementation-planning.md)。技术实现总方案和开发计划不得塞进单个巨大文档, 也不得机械拆成 frontend/backend/database/tests。默认写 `.opc/implementation-plan/index.md`、`architecture.md`、`contracts.md`、`work-breakdown.md`、`parallelization.md`、`verification.md`、`slices/*.md` 和必要 ADR。实现任何 slice 前只读 `index + architecture + contracts + verification + 当前 slice + ADR`, 不默认读取整个目录。非平凡项目必须写并行分配: 哪些 slice/lane 可并行、依赖、Write Set、验证责任和是否适合子代理; 不适合并行也要写原因。

### 自治补齐契约

实现期缺 Git 仓库、前端脚手架、Node 后端、API 路由、DB schema、`.env.example`、测试命令、CI/CD 或预览配置时, 默认补齐。详见 [autonomous-bootstrap.md](references/autonomous-bootstrap.md)。

暂停确认门只包含: secret/账号/私有 URL、production、远端 push、覆盖画布或服务器、破坏性迁移、付费资源、真实 SLA、法务合规或客户数据边界。

### 上下文持久化契约

每次进入完整 OPC、阶段交付或“继续上次”时, 自动读 [context-persistence.md](references/context-persistence.md)。有 `.opc/state/opc-task.json` 就恢复, 没有就初始化。

内部记录:

- `.opc/state/opc-task.json`: 当前阶段、产物路径、证据摘要、nextAction;
- `.opc/<phase>/discussion.md`: 仅记录必要决策、默认假设、用户提交和内部阶段卡/确认卡摘要;
- `.opc/<phase>/last-handoff.md`: 阶段完成前的结构化收尾文本。

实现阶段必须评估当前会话上下文预算, 只领取能在当前上下文内完成并验证的 slice/lane。开始长实现、切换 slice、完成一组文件修改、运行长验证前, 或感觉接近上下文压缩前, 写 `.opc/implementation/continuation.md` 并用 `opc-task-state.py checkpoint` 更新台账, 让自动压缩或新会话能直接恢复。

不要让用户手动执行状态脚本; 这些是代理命令。

### 需求覆盖契约

交付范围由业务目标、角色、核心流程、数据、边界、非功能要求和验收口径决定, 不靠“企业级/平台/后台”等关键词机械判断。从零设计、大范围改版、配置恢复后继续时, 必须先形成覆盖 brief、PRD 或 Gate Card; 不得把完整需求擅自缩成首页或单页 dashboard。

### 开源交付门禁契约

完整 OPC 使用这些工作法, 但不把方法名当交付物: discovery-before-build、JTBD、MoSCoW、2-3 个方案对比、Planning Packet、TDD/regression ratchet、systematic debugging、evidence-before-completion、release packet、premortem、red-team 和 AAR。需要时写内部 Pattern Card, 并把它落成阶段产物或检查项。

### UI 文案语种契约

页面导航、标题、按钮、表格、状态、空态、错误、审批、审计、监控和日志文案跟随用户指定、素材语言和聊天主语言。中文聊天或中文素材默认简体中文 UI; 不要把企业后台默认生成英文 Dashboard。MasterGo、Codify、AI、Agent、API、MCP、D2C、SLA、SSO、RBAC、AgentOps、CI/CD 等技术词可保留原文。语种规则必须写进 PRD、Codify requirement、HTML 或实现说明, 并在推送前和验证中检查。

### UI 设计质量契约

完整 OPC 涉及新 UI、重设计、Codify 画布设计或非像素级还原实现时, 必须读 [frontend-design-quality.md](references/frontend-design-quality.md)。把目的、受众、设计调性、记忆点、约束和反 generic AI aesthetics guardrails 写进 PRD、solution、Codify requirement 或当前 slice。设计质量不改变触发边界: 普通前端页面或独立组件仍不触发本 Skill, 除非它属于 OPC 全流程或 MasterGo-backed delivery。

### token 安全契约

token/key 每用户每机器索取一次, 绝不复用、硬编码或复制其它会话的值; 只写当前宿主 user-scope 本地配置或目标平台安全变量, 不进版本控制。收到 token 后只脱敏回显(前缀 + 末 4 位)。用户把完整 token 贴进聊天时, 提醒它已进入会话记录, 配置成功后建议 revoke / rotate。

### 证据与状态契约

HTTP 200、命令退出码 0、本地 HTML 存在、`accepted`、代码列表非空都不算最终完成证据。完成必须有阶段交付物、测试/截图/浏览器验证、部署状态、`get_design_diff` 或 API 溯源报告等证据。`accepted` 必须进入 pending 状态; 没有画布 diff、selection code 或截图时只能说待验证。

### 专业完成定义

交付不是活动报告; 必须证明用户目标、核心流程、关键状态、风险处理和上线证据闭合。需求、方案、UI、实现、验证、部署任一阶段被跳过时, 必须写清跳过授权、风险和替代证据。对外宣称“完成 / 已上线 / 可交付”前, 读 [delivery-contract.md](references/delivery-contract.md)。

### 收尾契约

每个 turn 必须使用结构化收尾。无需用户决策时, 收尾要写清“没有未决项”并继续推进; 需要决策时, 优先打开原生选择交互。详见 [handoff-contract.md](references/handoff-contract.md)。

强制结构:

1. **[已完成]** — 本轮具体产物;
2. **[证据]** — 路径、命令、测试、截图、URL 或验证输出;
3. **[不确定项 + 我的处理]** — 每条归类为自治处理 / 需要拍板 / 卡住缺 X; 没有就写“没有未决项”;
4. **[需要你拍板]** — 仅需要时出现; 原生交互优先, 文本 A/B/C 只作降级;
5. **[下一步]** — “我现在做 X” / “等你在原生交互提交” / “等你回 A/B/C” / “卡住, 缺 X”之一。

跑 `python3 scripts/opc-task-state.py mark <phase> done` 前, 必须把本轮 hand-off 写到 `.opc/<phase>/last-handoff.md`, 再跑 `python3 scripts/handoff-lint.py --file .opc/<phase>/last-handoff.md --phase <phase>`。失败就重写, 不绕过。

### Karpathy 行为契约

详见 [karpathy-discipline.md](references/karpathy-discipline.md)。

1. **写代码之前先思考** — 暴露会改变成品的默认假设; 不藏困惑。
2. **优先简单** — 不做 PRD 范围之外的功能; 一次性代码不抽象。
3. **外科手术式修改** — 每行 diff 都能追溯到本次任务。
4. **目标驱动执行** — PRD、方案、内部阶段卡/确认卡的验收方式必须可执行。

## 工作流总览

```text
0. OPC intake / route
   -> references/opc-flow.md

0.5 高影响疑点澄清(按需, 不是每阶段固定仪式)
   internal Stage Card / internal ConfirmCard -> native choice if needed -> discussion log
   -> references/clarification-loop.md

0.7 开源交付模式门禁
   Pattern Card -> JTBD/MoSCoW -> 方案对比 -> 验证/发布/校准门禁
   -> references/open-source-patterns.md

0.8 自治补齐门禁
   missing repo/scaffold/backend/DB/test/CI/deploy defaults
   -> references/autonomous-bootstrap.md

1. 需求阶段
   enough facts -> PRD; high-impact ambiguity -> native choice; then PRD
   -> references/requirements-workflow.md

2. 方案阶段
   architecture/data/deploy decisions -> solution design + UI quality brief
   -> references/solution-design.md

3A. MasterGo/Codify UI 设计
   MasterGo 设计 Gate Card + design quality brief -> task state -> preflight -> write -> 3A verify
   -> references/design-workflow.md

3B. MasterGo Magic 还原
   URL parse -> DSL/D2C -> enterprise/quick mode -> implementation-plan -> implementation -> 3B verify
   -> references/restoration-workflow.md

4. 实现前技术规划
   implementation-plan index -> architecture/contracts/work-breakdown/parallelization/verification -> context-budgeted value slices + ADR
   -> references/implementation-planning.md

5. 前端 + Node 后端实现
   context checkpoint -> repo/framework detect -> design quality brief -> components + API routes + DB schema + real data -> browser QA
   -> references/implementation-workflow.md

6. 验证
   lint/typecheck/test/build/browser/data persistence -> evidence
   -> references/verification-implementation.md

7. CI/CD 和部署
   deploy target decision if needed -> preview -> production gate -> rollback evidence
   -> references/deployment-workflow.md

8. 已上线需求回放校准
   golden input -> AI replay -> gap analysis -> rule update
   -> references/regression-calibration.md
```

完整 OPC 任务按上面顺序推进。内部阶段卡和确认卡服务状态恢复与推理纪律, 不把它们变成用户必须消费的流程。

## MasterGo 子流程最低要求

用户要在 MasterGo 画布上设计或修改时, 读 [design-workflow.md](references/design-workflow.md)。必须按顺序: 确认 Codify MCP 可用 → 生成 MasterGo 设计 Gate Card → `mastergo-task-state.py init` → 读本地 `.codify/library/catalog.json` → `codify-preflight.py` → 写入 → `mastergo-task-state.py mark/request` → [verification.md](references/verification.md) 3A。

用户要把 MasterGo 设计稿还原成代码时, 读 [restoration-workflow.md](references/restoration-workflow.md)。必须: `parse-mastergo-url.py` 解析 → 确认 Magic MCP 可用 → 记录 source fileId/layerId/contentId → 默认企业级实现 → D2C/DSL 原始输出不是完成, 必须实现+运行+截图+按 3B 验证。

## 引用文件何时读

| 文件 | 何时读 |
|---|---|
| [opc-flow.md](references/opc-flow.md) | 每个新任务入口、阶段路由、OPC Stage Card 内部记录、交付物链路 |
| [clarification-loop.md](references/clarification-loop.md) | 需要澄清高影响不确定、写内部确认卡、维护 discussion log |
| [context-persistence.md](references/context-persistence.md) | 新会话恢复、状态台账、nextAction、阶段产物主动拆分 |
| [open-source-patterns.md](references/open-source-patterns.md) | 完整 OPC 交付、skill 优化、需求到上线闭环、上线回放校准 |
| [requirements-workflow.md](references/requirements-workflow.md) | 需求阶段、PRD、用户故事、验收标准、Open Questions |
| [solution-design.md](references/solution-design.md) | 需求收敛后做方案, 包含信息架构、技术栈、接口/数据/权限/测试计划 |
| [frontend-design-quality.md](references/frontend-design-quality.md) | OPC 内部涉及新 UI、重设计、Codify requirement、非像素级还原实现或视觉验收时 |
| [implementation-planning.md](references/implementation-planning.md) | 实现前技术总方案、开发计划、上下文拆分、slice 读取、ADR |
| [implementation-workflow.md](references/implementation-workflow.md) | 全栈实现(Node 后端 + DB + 前端 + 真实接口) |
| [deployment-workflow.md](references/deployment-workflow.md) | 部署目标确认、CI/CD、环境变量、回滚 |
| [regression-calibration.md](references/regression-calibration.md) | 用已上线需求回放校准 Skill、沉淀规则 |
| [autonomous-bootstrap.md](references/autonomous-bootstrap.md) | 执行阶段缺前置时的自治补齐范围 |
| [mcp-setup.md](references/mcp-setup.md) | MCP 缺失、token 配置、宿主切换、Codify bridge、本地/远端 URL 排障 |
| [delivery-contract.md](references/delivery-contract.md) | 判断真实交付物、阻塞条件、禁止替代交付 |
| [handoff-contract.md](references/handoff-contract.md) | turn 收尾结构、不确定项分类、显式下一步、handoff-lint.py 联动 |
| [karpathy-discipline.md](references/karpathy-discipline.md) | Karpathy 四原则在 OPC 阶段动作上的具体落地 |
| [intent-routing.md](references/intent-routing.md) | MasterGo/Codify/Magic 子任务路由 |
| [design-workflow.md](references/design-workflow.md) | Codify 画布设计、修改、查看页面 |
| [design-scope.md](references/design-scope.md) | 覆盖 brief、任务台账、恢复继续 |
| [design-coverage-patterns.md](references/design-coverage-patterns.md) | 复杂平台覆盖模板 |
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
| `scripts/opc-task-state.py` | 初始化、标记、checkpoint、校验 `.opc/state/opc-task.json`, `brief` 输出普通用户结果摘要 |
| `scripts/handoff-lint.py` | 校验 turn 结构化收尾, `mark <phase> done` 前的硬门禁 |
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

简短、直接、给证据。中文回复, 技术名词如 `layerId`、`DSL`、`D2C`、`contentId`、`useComponentLibrary`、`buildStrategy`、`preview deployment`、`rollback`、`Hono`、`Prisma`、`API routes` 保留原文。

第一反应不是把流程卡抛给用户, 而是判断是否有高影响疑点。没有就继续做成品; 有就打开原生选择交互。

用户问“好了吗”时, 回答当前交付物、证据和下一步。没有证据就说“待验证”, 不要只回“完成”。
