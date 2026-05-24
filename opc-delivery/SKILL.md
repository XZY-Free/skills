---
name: opc-delivery
description: "OPC 一人公司式产品交付工作流。把粗糙业务目标推进到能登录、能操作、数据持久化的真实程序, 并产出验证 / 部署证据。覆盖需求 → PRD → 方案 → UI 设计 → 实现 → 验证 → 部署 → 校准全链路, 含 MasterGo 设计 / 还原子流程。只在阻塞(API key、token、付费资源、production 发布)时停, slice 间不停。不用于纯前端组件、纯 Figma 任务、单独 MCP 配置。"
---

# OPC 产品交付技能

## 北极星

**opc-delivery 是自治推进的成品交付代理。**

默认行为: 业务目标 → 真实可登录、可操作、数据持久化的程序 → 证据闭合。

只有遇到真实阻塞才停(API key、token、第三方账号、production 发布、付费资源、破坏性写入)。

**slice 之间、模块之间、阶段之间不停。**

这是所有契约的取舍依据。任何看起来"必须问用户"的事先对照北极星: 不问能推进吗? 推进的代价用户能承担吗(可逆的就承担)? 答"是"就**自己决定 + 在结构化收尾里说明默认假设**, 不要打断用户。

## 运行要求

| 类型 | 要求 |
|---|---|
| 必需运行时 | `node>=18`, `python>=3.11` |
| 默认后端栈 | Next.js API routes / Hono / Fastify / Express (Node 系) |
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

## 核心契约索引

详情看 [10-contracts.md](references/10-contracts.md)。这里只给一句话索引:

| 契约 | 一句话 | 详情 |
|---|---|---|
| 收尾(四态) | slice 完成→[继续下一 slice]; 任务完成→[下一步]; 真阻塞→[需要你提供]; 高影响疑点→[需要你拍板] | [10-contracts.md#收尾契约四态结构](references/10-contracts.md#收尾契约四态结构) |
| 问/不问白名单 | 只问 token/付费/production/范围 framing; 不问下一 slice/文件名/typecheck 修法 | [02-clarification.md](references/02-clarification.md#必问-vs-不问-白名单) |
| 交付物 | 真实交付物不是中间产物; 缺能力就阻塞, 不降级 | [10-contracts.md#交付物契约](references/10-contracts.md#交付物契约) |
| 证据 | HTTP 200 不是完成证据; 需要 PRD/方案/UI/验证/部署/风险/校准七维 | [10-contracts.md#证据与完成定义](references/10-contracts.md#证据与完成定义) |
| 上下文持久化 | 进任务自动 resume; 阶段写 `.opc/state/opc-task.json`; 单文件 ≥200 行主动拆 | [10-contracts.md#上下文持久化契约](references/10-contracts.md#上下文持久化契约) |
| 执行期资源边界 | 单次 tool_result ≤5MB; 截图用 thumb; 长日志 tail/grep; 单 turn Read ≤1 reference | [09-runtime-budget.md](references/09-runtime-budget.md) |
| Karpathy 四原则 | 先思考 / 优先简单 / 外科手术 / 目标驱动 | [10-contracts.md#karpathy-四原则](references/10-contracts.md#karpathy-四原则) |
| token 安全 | token 是用户资产, 不复用其它会话, 配置成功后建议 revoke | [10-contracts.md#token-安全契约](references/10-contracts.md#token-安全契约) |
| UI 文案语种 | 跟随用户指定/素材/聊天主语言; 中文场景默认简体中文 UI | [03-requirements.md#ui-文案语种契约](references/03-requirements.md#ui-文案语种契约) |
| UI 设计质量 | 写 purpose/tone/differentiation/constraints/anti-generic guardrails | [04-solution.md#体验设计质量门禁](references/04-solution.md#体验设计质量门禁) |
| 自治补齐 | 缺 Git/脚手架/后端/DB/CI 自动补齐; 缺凭证才停 | [02-clarification.md#自治补齐矩阵](references/02-clarification.md#自治补齐矩阵) |
| 实现规划 | 完整 OPC 必写 implementation-plan/index.md + slices + ADR + parallelization | [06-implementation.md#part-1-implementation-plan实现前技术规划](references/06-implementation.md#part-1-implementation-plan实现前技术规划) |

## 工作流总览

```text
0. OPC intake / route                             → 01-routing.md
0.5 高影响疑点澄清(按需)                          → 02-clarification.md
1. 需求阶段(PRD + JTBD + MoSCoW)                  → 03-requirements.md
2. 方案阶段(架构/数据/部署 + 设计质量 brief)      → 04-solution.md
3A. MasterGo/Codify UI 设计                       → 05-mastergo.md
3B. MasterGo Magic 还原                           → 05-mastergo.md
4. 实现前技术规划(index + slices + parallel)     → 06-implementation.md
5. 前端 + Node 后端实现 + API 接入                → 06-implementation.md
6. 验证(3A 设计完 / 3B 还原实现完 + update flow) → 07-verification.md
7. CI/CD 和部署                                   → 08-deployment.md
8. 已上线需求回放校准                             → 08-deployment.md
```

完整 OPC 任务按上面顺序推进。**执行阶段(implementation / verification / deployment / calibration)默认连续推进, 不在 slice / 模块 / 阶段之间问"是否继续"**。

## 引用文件索引

| 文件 | 何时读 |
|---|---|
| [01-routing.md](references/01-routing.md) | 每个新任务入口、阶段路由、MasterGo 子任务路由(Codify vs Magic) |
| [02-clarification.md](references/02-clarification.md) | 高影响疑点澄清、问/不问白名单、自治补齐矩阵、Git/后端启动规则 |
| [03-requirements.md](references/03-requirements.md) | 需求阶段、PRD、JTBD/MoSCoW、UI 文案语种契约、复杂产品覆盖模板 |
| [04-solution.md](references/04-solution.md) | 方案阶段、全栈技术默认、UI 方案门禁、体验设计质量门禁 |
| [05-mastergo.md](references/05-mastergo.md) | Codify 画布设计 + Magic D2C 还原(企业级/快速复刻双模式) |
| [06-implementation.md](references/06-implementation.md) | 实现规划(implementation-plan)+ 全栈实现 + API 接入 |
| [07-verification.md](references/07-verification.md) | 3A 设计验证 + 3B 还原实现验证 + 渲染补丁 + 设计稿更新流 |
| [08-deployment.md](references/08-deployment.md) | CI/CD、部署目标、Vercel/Netlify/服务器路径、回放校准 |
| [09-runtime-budget.md](references/09-runtime-budget.md) | 执行期资源边界(32MB / 长日志 / 多 Read / 截图回流) |
| [10-contracts.md](references/10-contracts.md) | 核心契约总集: 收尾、交付、证据、持久化、Karpathy、token |
| [mcp-setup.md](references/mcp-setup.md) | MCP 缺失、token 配置、宿主切换、本地/远端 URL 排障 |
| [troubleshooting.md](references/troubleshooting.md) | Magic / Codify MCP 报错、原型连线限制、Request too large |

## 脚本索引

只列 mandatory 层(实现期必跑); helpers 在对应 reference 内按需引用; dev 是开发期自检, 不在此暴露。

| 脚本 | 用途 |
|---|---|
| `scripts/mandatory/opc-task-state.py` | 初始化 / 标记 / checkpoint / 校验 `.opc/state/opc-task.json`, `brief` 输出普通用户结果摘要 |
| `scripts/mandatory/handoff-lint.py` | 校验 turn 结构化收尾, `mark <phase> done` 前的硬门禁 |
| `scripts/mandatory/check-mcp-config.py` | 检查当前宿主 MCP 配置、token 占位、本地/远端 Codify URL |
| `scripts/mandatory/codify-preflight.py` | Codify 写入前综合门禁 |
| `scripts/mandatory/parse-mastergo-url.py` | 从 MasterGo URL 提取 fileId/layerId/contentId |

## 沟通风格

简短、直接、给证据。中文回复, 技术名词如 `layerId`、`DSL`、`D2C`、`contentId`、`useComponentLibrary`、`buildStrategy`、`preview deployment`、`rollback`、`Hono`、`Prisma`、`API routes` 保留原文。

第一反应不是把流程卡抛给用户, 而是判断是否有真实阻塞。没有就继续做成品; 有就打开原生选择交互, 用结构化收尾。

用户问"好了吗"时, 回答当前交付物、证据和下一步。没有证据就说"待验证", 不要只回"完成"。
