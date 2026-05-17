---
name: opc-delivery
description: OPC 一人公司式产品交付工作流，把粗糙业务需求推进成已验证、可部署、可回放校准的产品增量。Use whenever Codex must drive requirement discovery, PRD, solution/UI design, MasterGo/Codify canvas work, MasterGo Magic D2C/C2D restoration, frontend implementation, API wiring, validation, CI/CD, preview/production deployment, release evidence, rollback planning, or shipped-feature replay. Also use for MasterGo URLs, mastergo://, Codify MCP, Magic MCP, D2C/DSL, layerId/contentId, and MasterGo component libraries. Do not use for unrelated Figma, generic MCP/token setup, casual codify wording, or ordinary frontend-only work not framed as OPC/full-cycle delivery.
---

# OPC 产品交付技能

定位: 把"一个啥也不懂的业务员给一个需求"推进成**用户能登录能用的真实产品**, 并完成验证、部署和复盘。MasterGo/Codify/Magic 是 OPC 全流程里的设计与还原能力模块, 不是这个 skill 的全部。

OPC 流程默认假设用户给的是粗糙业务需求, 真实需求要靠**多轮 ConfirmCard 对话**聊清楚, 不是 AI 替用户脑补完一份 158 行 PRD 就 mark done。

每个新任务先读 [opc-flow.md](references/opc-flow.md) 路由阶段。完整 OPC 任务在 intake 之后立即进入 [clarification-loop.md](references/clarification-loop.md) 定义的对话循环, 直到不确定性收敛才进执行阶段。

## 运行要求

| 类型 | 要求 |
|---|---|
| 必需运行时 | `node>=18`(前后端), `python>=3.11`(skill 脚本) |
| 默认后端栈 | Next.js API routes / Hono / Fastify / Express(Node 系); **不默认 Java/Python/Go 后端,太重** |
| 默认数据持久层 | SQLite(本地开发) / Postgres(部署), 配 Prisma 或 Drizzle ORM |
| 设计 MCP | `mcp__codify__*` 用于 MasterGo 画布设计 |
| 还原 MCP | `mcp__mastergo-magic-mcp__*` 用于 MasterGo D2C/DSL |
| 常用验证 | Browser / Playwright、lint、typecheck、unit/e2e、构建、部署状态 |
| 可选工具 | `git`, `gh`, `vercel`, `jq` |

缺 MCP、token、当前宿主配置或本会话工具时, 先走 [mcp-setup.md](references/mcp-setup.md)。
不要把本地 HTML、Markdown、prompt、截图、DSL 或 D2C 包装成真实完成。
不要把 typed mock 包装成"真实可用产品"——除非用户明确说"我就要 demo/演示"。

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

### 阶段推进契约（即自动轮转契约）

OPC 流程分两种节奏:

- **定义阶段 (intake / requirements / solution / ui-design) = 对话式推进**: 目的是把"用户要什么"聊清楚, 不是写完一份长文档就 mark done。AI 写 ConfirmCard、暴露默认假设、问硬决策、跟用户多轮 Q&A, 直到不确定性收敛才写最终文档并 mark done。每阶段问几轮不预设, 像几次需求会议; 详细机制见 [clarification-loop.md](references/clarification-loop.md)。
- **执行阶段 (implementation / verification / deployment / calibration) = 自动推进**: 定义阶段已经聊清楚的需求, 一旦进入执行阶段就连续推进, 除非遇到 token/凭证/生产部署/远端推送/付费资源/破坏性写入等硬阻塞。

阶段间自动衔接, 不要求用户每步说"继续"。但内部讨论没收敛前不要 mark done。
**只有"用户明确说停 / 暂停 / 不做了"才算阶段间硬停。**

### 定义阶段对话契约

完整 OPC 任务在 intake 之后, 立即按 [clarification-loop.md](references/clarification-loop.md) 进入对话循环:

1. 每个定义阶段开始时先读 `.opc/<phase>/discussion.md`(若存在)接着上轮聊。
2. 写 ConfirmCard 第 N 轮: 列出 framing 解析 + 默认假设 + 硬决策。
3. 用户回应 → AI 更新理解, 必要时开第 N+1 轮。
4. 收敛后才写本阶段最终文档(PRD / 方案 / UI Brief), mark done, 进下一阶段。

ConfirmCard 是讨论媒介, 不是 gate。但每个定义阶段必须至少产出一轮 ConfirmCard, 不允许跳过对话直接写文档。

### 默认假设暴露契约

AI 单方面替用户做的决定必须列在 ConfirmCard 的`[我替你默认了什么]`段, 一行一条, 末尾标"反对就说"。不允许把单方面决策埋进 PRD/方案文档的`Won't / 风险 / 缺口`段, 等用户回头才发现。

必须列出来的高赌注类目: 数据来源、部署目标、后端栈、DB 选型、用户 framing 的字面解析、测试策略、主要范围裁剪、视觉/品牌(无参考稿时)。

低赌注类目(小依赖、文件命名、helper 拆法、mock seed 具体值)走自治补齐, 不必列入 ConfirmCard。
详见 [clarification-loop.md](references/clarification-loop.md) 的`默认假设暴露规则`。

### 用户 framing 解析契约（即选择题澄清契约）

用户原话用"企业级 / 完整 / 专业级 / 生产级 / production-ready / 智能 / 后台 / 小需求"这类承诺性词时, ConfirmCard 第 1 轮必须把 AI 对这些词的解读翻译成具体清单, 让用户校准。

例: "企业级大模型管理平台" → AI 要列"含 = 多模型接入 + Key 管理 + 应用编排 + 知识库 + Playground + 日志; 不含 = RBAC/SSO/审计/AgentOps/计费(?)", 然后让用户改清单。

不允许 AI 按字面理解写完 PRD 才在 `Won't` 段交代"我没做 RBAC/SSO/审计"。误解 framing 是定义阶段最大的浪费来源。

### 全栈交付默认契约（即阶段交付物契约）

OPC 默认交付的真实交付物 = **用户能访问、能登录、能操作、数据能真实持久化的全栈应用 + 部署链接**, 不是前端 + mock 的演示版。

- 数据来源默认 = 真实接入 + AI 自建后端 + DB; mock 只在用户明确说"我就要 demo / 演示给客户看 / 不要真后端"时才用。
- 后端栈默认走 Node 系: Next.js API routes、Hono、Fastify、Express。**不默认 Java/Spring/Python/Django/FastAPI/Go**, 这些太重、起势慢、跟前端联调成本高。用户明确指定才用。
- DB 默认 SQLite(本地开发零配置) / Postgres(部署可持久化), 配 Prisma 或 Drizzle ORM, schema 写入 `.opc/runtime/` 或项目 `prisma/`。
- `.env` 模板自动生成, 不写真实 secret; 真实 key/凭证走宿主 user-scope 配置, 不进版本控制。

`真实交付物`字段不允许写"或"假设(如"Vercel preview 或本地等价")。要确定其中一个; 不确定就在 ConfirmCard 里先问。

### 自治补齐契约

定义阶段聊清楚之后, 实现期缺 Git 仓库、前端脚手架、Node 后端项目、API 路由、DB schema、`.env` 模板、mock 数据(用户已选 mock 时)、测试命令、CI/CD 或本地预览配置时, 默认由代理补齐。

只有以下情况作为暂停确认门:

- API key/token/secret、私有 URL、服务器地址、账号权限
- production 部署、远端 push、覆盖 MasterGo 画布、覆盖已有服务器/数据库、破坏性迁移
- 付费资源、采购、外部服务开通
- 法务/合规/客户数据范围/真实 SLA

详见 [autonomous-bootstrap.md](references/autonomous-bootstrap.md)。

### 讨论日志契约

每个定义阶段维护 `.opc/<phase>/discussion.md`(追加模式), 记录每一轮 ConfirmCard 和用户回应。会话断了下次 `resume` 时先读 discussion log, 不要求用户重讲上下文。

state 台账(`.opc/state/opc-task.json`)只记关键节点摘要 + discussion.md 路径; 不存原始对话。
最终交付文档(PRD / 方案 / UI Brief)只放收敛后的结论 + discussion log 路径; 不把讨论纪要塞进正文。

详见 [clarification-loop.md](references/clarification-loop.md) 的`讨论日志规约`。

### 上下文持久化契约

每次进入完整 OPC、阶段交付或"继续上次"任务时, 代理自己读 [context-persistence.md](references/context-persistence.md), 自动恢复或初始化 `.opc/state/opc-task.json` 和当前阶段的 `discussion.md`。

`opc-task-state.py resume/init/mark/note` 是代理命令, 不让用户手动执行; 用户只需要说"继续上次"。
大产物主动拆到 `.opc/<phase>/` 多文件; 状态台账只存摘要和路径。

### 开源交付门禁契约

这个 skill 融合开源优秀 skill 的工作法: discovery-before-build、JTBD、MoSCoW、2-3 个方案对比、planning packet、TDD/regression ratchet、systematic debugging、evidence-before-completion、release packet、premortem、red-team 和 AAR。完整 OPC 任务在 Stage Card 后补 Pattern Card; 这些模式必须落成阶段产物或检查项, 不要把开源 skill 名单当成交付物。

### 需求覆盖契约

交付范围由业务目标、角色、核心流程、数据、边界、非功能要求和验收口径决定; 不靠"企业级/平台/后台"等关键词机械判断。从零设计、大范围改版、配置恢复后继续时, 必须先形成覆盖 brief、PRD 或 Gate Card; 不得把完整需求擅自缩成首页或单页 dashboard。

### UI 文案语种契约

页面导航、标题、按钮、表格、状态、空态、错误、审批、审计、监控和日志文案跟随用户指定、素材语言和聊天主语言。中文聊天或中文素材默认简体中文 UI; 不要把企业后台默认生成英文 Dashboard。MasterGo、Codify、AI、Agent、API、MCP、D2C、SLA、SSO、RBAC、AgentOps、CI/CD 等技术词可保留原文。语种规则必须写进 PRD、Codify requirement、HTML 或实现说明, 并在推送前和验证中检查。

### token 安全契约

token/key 每用户每机器索取一次, 绝不复用、硬编码或复制其它会话的值; 只写当前宿主 user-scope 本地配置或目标平台安全变量, 不进版本控制。收到 token 后只脱敏回显(前缀 + 末 4 位)。用户把完整 token 贴进聊天时, 提醒它已进入会话记录, 配置成功后建议 revoke / rotate。`tool_search` 暴露工具、其它宿主已配置、demo token 看似可用, 都不是当前宿主已配置证据。

### 证据与状态契约

HTTP 200、命令退出码 0、本地 HTML 存在、`accepted`、代码列表非空都不算最终完成证据。完成必须有阶段交付物、测试/截图/浏览器验证、部署状态、`get_design_diff` 或 API 溯源报告等证据。`accepted` 必须进入 pending 状态; 没有画布 diff、selection code 或截图时只能说待验证。

### 专业完成定义

交付不是活动报告; 必须证明用户目标、核心流程、关键状态、风险处理和上线证据闭合。需求、方案、UI、实现、验证、部署任一阶段被跳过时, 必须写清跳过授权、风险和替代证据。对外宣称"完成 / 已上线 / 可交付"前, 读 [delivery-contract.md](references/delivery-contract.md) 的专业完成定义。无法获得真实证据时, 用 `blocked`、`pending` 或 `skipped with reason`, 不要用乐观话术补洞。

### 收尾契约

OPC 任务的每个 turn (定义阶段每轮 ConfirmCard、执行阶段每段汇报) 收尾必须满足五段结构, 不允许只甩"剩余风险: a / b / c" 给用户。详见 [handoff-contract.md](references/handoff-contract.md)。

强制结构:

1. **[已完成]** — 本轮做了什么具体事
2. **[证据]** — 文件路径 / 命令退出 / 测试通过 / 截图 / URL (执行阶段强制)
3. **[不确定项 + 我的处理]** — 每条必须归类: 自治处理 / 需要你拍板 / 卡住缺 X
4. **(可选) [需要你拍板]** — 列具体 A / B / C 选项 + 标默认 + 保留"自定义 / type something"; 禁止"你看呢" 这类开放式提问
5. **[下一步]** — 必须显式写 "我现在做 X" / "等你回 A/B/C" / "卡住, 缺 X" 之一

本契约覆盖 `~/.codex/AGENTS.md` 工作约定中"最终报告必须包含...剩余风险" 的默认形态: "剩余风险" 单甩给用户是反模式 — Karpathy 第 1 条要求的是"列出选项让用户选 + 给默认 + 自动继续", 不是"列风险等用户问"。

AI 在跑 `python scripts/opc-task-state.py mark <phase> done` 之前, 必须先把本轮 hand-off 文本写到 `.opc/<phase>/last-handoff.md` (或通过 stdin), 跑 `python scripts/handoff-lint.py --file .opc/<phase>/last-handoff.md --phase <phase>` 校验通过。校验失败要重写 hand-off, 不要绕过 lint 直接 mark done。

### Karpathy 行为契约

把 Andrej Karpathy 关于 LLM 写代码常见毛病的四原则, 落到 OPC 的具体阶段动作。详见 [karpathy-discipline.md](references/karpathy-discipline.md)。

四条总览:

1. **写代码之前先思考** — 在 ConfirmCard 第 1 轮暴露所有默认假设 + framing 翻译; 不要藏假设
2. **优先简单** — 不做 PRD 范围之外的功能; 一次性代码不抽象; 200 行能 50 就重写
3. **外科手术式修改** — 每行 diff 都能追溯到本次任务; 不顺手"美化" 邻近代码 (跟 `~/.claude/CLAUDE.md` 全局基线一致)
4. **目标驱动执行** — Stage Card / PRD / ConfirmCard 的"验收方式" 必须可执行 (测试 / 命令 / 截图)

全局基线已在 `~/.claude/CLAUDE.md` 和 `~/.codex/AGENTS.md` 的"模型行为四原则" 小节生效; 本契约是 OPC 上下文里的具体翻译, 不重复全局条款。

## OPC Stage Card

完整 OPC 任务在 intake 阶段输出 Stage Card; 这张卡是后续 ConfirmCard 讨论的起点, 不是替代品。Stage Card 锁定真实交付物的形状, ConfirmCard 在每个定义阶段把内部细节聊清楚。

```text
OPC Stage Card

- 真实交付物: 默认 = 用户能登录能用的全栈 Web 应用 + 真实持久化数据 + 可访问 URL
              (用户明确说 demo/演示才退回前端 + mock 形态)
- 当前阶段: 需求 / 方案 / UI 设计 / 实现 / 验证 / 部署 / 校准
- 业务目标: <用户要解决的问题和成功标准>
- 用户 framing 解析: <用户用了"企业级 / 完整 / 智能"等承诺词时, 翻译成具体清单>
- 覆盖范围: <角色、流程、页面、状态、数据、权限、接口 — 收敛后才填具体>
- 默认假设(一句话可改):
  • 数据来源 = ?(默认: 真实接入 + 我自建 Node 后端 + DB)
  • 后端栈 = ?(默认推荐: Next.js API routes / Hono / Fastify 三选一)
  • DB = ?(默认: SQLite 开发, Postgres 部署; 含 Prisma)
  • 部署目标 = ?(必须明确, 不允许"或"假设)
  • 视觉/品牌 = ?(默认: shadcn/Tailwind; 用户给参考则跟参考)
  • 测试策略 = ?(默认: lint + typecheck + build + 浏览器主链路)
  • 主要范围裁剪(如有) = ?
- 阶段交付物: <本阶段要产出的文件、画布结果、代码或链接>
- 验收方式: <测试、截图、diff、API 溯源、部署检查; 用户确认只作补充证据>
- 风险 / 缺口: <待澄清项、能力缺失、环境缺失、付费工具>
- 停止条件: <只有哪些 blocker 或高风险副作用会暂停>
- 下一步: <进入 clarification-loop 的第一轮 ConfirmCard, 还是直接进具体阶段 reference>
```

Stage Card 里`默认假设`字段如果有"?"或"或"假设, 不允许直接进 requirements; 必须先在 ConfirmCard 第 1 轮把它聊明确。

## 工作流总览

```text
0. OPC intake / route / Stage Card
   -> references/opc-flow.md

0.5 定义阶段对话循环(贯穿 intake -> requirements -> solution -> ui-design)
   ConfirmCard -> 多轮 Q&A -> dialogue log -> 收敛 -> 落最终文档
   -> references/clarification-loop.md

0.7 开源交付模式门禁
   Pattern Card -> JTBD/MoSCoW -> 方案对比 -> 验证/发布/校准门禁
   -> references/open-source-patterns.md

0.8 自治补齐门禁(执行阶段缺前置时)
   missing repo/scaffold/backend/DB/test/CI/deploy defaults
   -> references/autonomous-bootstrap.md

1. 需求阶段(对话式)
   ConfirmCard 几轮 -> PRD + 验收标准 + open questions
   -> references/requirements-workflow.md

2. 方案阶段(对话式)
   ConfirmCard 关于栈/DB/部署 -> 信息架构 + 技术方案 + 测试/部署计划
   -> references/solution-design.md

3A. MasterGo/Codify UI 设计
   MasterGo 设计 Gate Card -> task state -> preflight -> write -> 3A verify
   -> references/design-workflow.md

3B. MasterGo Magic 还原
   URL parse -> DSL/D2C -> enterprise/quick mode -> implementation -> 3B verify
   -> references/restoration-workflow.md

4. 前端 + Node 后端实现(执行式)
   repo/framework detect -> 前端组件 + API routes + DB schema + 真实接口 -> browser QA
   -> references/implementation-workflow.md

5. CI/CD 和部署(执行式, 但部署目标必须先在 ConfirmCard 锁定)
   build/test -> 部署目标确认 -> env/secrets -> preview -> production gate -> rollback evidence
   -> references/deployment-workflow.md

6. 已上线需求回放校准
   golden input -> AI replay -> gap analysis -> rule update
   -> references/regression-calibration.md
```

完整 OPC 任务按上面顺序推进: 0-3 阶段以对话为主, 4-6 阶段自动推进。
阶段产物是交接输入, 不是自然停点; 只有用户要求暂停、硬阻塞或高风险副作用确认门禁才暂停。

## MasterGo 子流程最低要求

用户要在 MasterGo 画布上设计或修改时, 读 [design-workflow.md](references/design-workflow.md)。必须按顺序: 确认 Codify MCP 可用 → 生成 MasterGo 设计 Gate Card → `mastergo-task-state.py init` → 读本地 `.codify/library/catalog.json` → `codify-preflight.py` → 写入 → `mastergo-task-state.py mark/request` → [verification.md](references/verification.md) 3A。

用户要把 MasterGo 设计稿还原成代码时, 读 [restoration-workflow.md](references/restoration-workflow.md)。必须: `parse-mastergo-url.py` 解析 → 确认 Magic MCP 可用 → 记录 source fileId/layerId/contentId → 默认企业级实现 → D2C/DSL 原始输出不是完成, 必须实现+运行+截图+按 3B 验证。

## 引用文件何时读

| 文件 | 何时读 |
|---|---|
| [opc-flow.md](references/opc-flow.md) | 每个新任务入口、阶段路由、OPC Stage Card、交付物链路 |
| [clarification-loop.md](references/clarification-loop.md) | 进入定义阶段(intake/requirements/solution/ui-design)的对话循环, 写 ConfirmCard, 维护 dialogue log |
| [context-persistence.md](references/context-persistence.md) | 新会话恢复、状态台账、nextAction、阶段产物主动拆分 |
| [open-source-patterns.md](references/open-source-patterns.md) | 完整 OPC 交付、skill 优化、需求到上线闭环、上线回放校准 |
| [requirements-workflow.md](references/requirements-workflow.md) | 需求阶段对话(PRD、用户故事、验收标准、open questions) |
| [solution-design.md](references/solution-design.md) | 需求收敛后做方案(信息架构、技术栈、接口/数据/权限/测试计划) |
| [implementation-workflow.md](references/implementation-workflow.md) | 全栈实现(Node 后端 + DB + 前端 + 真实接口) |
| [deployment-workflow.md](references/deployment-workflow.md) | 部署目标 ConfirmCard、CI/CD、环境变量、回滚 |
| [regression-calibration.md](references/regression-calibration.md) | 用已上线需求回放校准 skill、沉淀宪法/规约 |
| [autonomous-bootstrap.md](references/autonomous-bootstrap.md) | 执行阶段缺前置时的自治补齐范围 |
| [mcp-setup.md](references/mcp-setup.md) | MCP 缺失、token 配置、宿主切换、Codify bridge、本地/远端 URL 排障 |
| [delivery-contract.md](references/delivery-contract.md) | 判断真实交付物、阻塞条件、禁止替代交付 |
| [handoff-contract.md](references/handoff-contract.md) | turn 收尾五段结构、不确定项分类、显式下一步、handoff-lint.py 联动 |
| [karpathy-discipline.md](references/karpathy-discipline.md) | Karpathy 四原则在 OPC 阶段动作上的具体落地 |
| [intent-routing.md](references/intent-routing.md) | MasterGo/Codify/Magic 子任务路由 |
| [design-workflow.md](references/design-workflow.md) | Codify 画布设计、修改、查看页面 |
| [design-scope.md](references/design-scope.md) | 覆盖 brief、任务台账、恢复继续 |
| [design-coverage-patterns.md](references/design-coverage-patterns.md) | 复杂平台覆盖模板, 尤其企业级/AgentOps/客服运营类产品 |
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
| `scripts/handoff-lint.py` | 校验 turn 收尾五段结构, `mark <phase> done` 前的硬门禁 |
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

**定义阶段以对话为主, 不要先输出 158 行 PRD 再让用户回头改。** 第一反应是写 ConfirmCard, 不是写文档。

用户问"好了吗"时, 回答当前阶段、已完成交付物和证据。没有证据就说"待验证", 不要只回"完成"。
