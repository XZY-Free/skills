# 方案阶段工作流

目标: 在 PRD 之后、UI/代码之前, 定义"怎么做"。方案阶段不是大而空的架构文档; 它要给 UI 设计、前端实现、API wiring、测试和部署提供可执行输入。

**节奏 = 对话式**。方案阶段也走多轮 ConfirmCard, 重点对后端栈、DB、部署目标、技术取舍这几项做集中确认。详见 [clarification-loop.md](clarification-loop.md)。

收敛后才写 `.opc/solution/solution-design.md` 最终稿, mark done, 自动进 ui-design 阶段。

## 目录

- [进入条件](#进入条件)
- [第 1 轮 ConfirmCard 模板](#第-1-轮-confirmcard-模板)
- [多轮迭代规则](#多轮迭代规则)
- [方案探索门禁](#方案探索门禁)
- [全栈技术默认](#全栈技术默认)
- [方案文档结构](#方案文档结构)
- [UI 方案门禁](#ui-方案门禁)
- [实现方案门禁](#实现方案门禁)
- [收敛与完成判断](#收敛与完成判断)

## 进入条件

- 有 PRD 或足够明确的需求 brief; `.opc/requirements/discussion.md` 收敛;
- PRD 里"数据来源"已锁定(真实接入 / mock — 由 requirements ConfirmCard 决定);
- 已检查现有项目结构、技术栈、组件库、接口文档和部署环境。

## 第 1 轮 ConfirmCard 模板

进方案阶段时先读 `.opc/solution/discussion.md`(若存在)。否则开第 1 轮:

```text
OPC ConfirmCard · solution · 第 1 轮

[基于 requirements 的事实]
- 业务目标 + framing 翻译: <复述 requirements 收敛的事实>
- 数据来源: 真实接入 + 自建 Node 后端 + DB
- 必做模块(Must): ...

[我替你默认的技术栈(一句话可改)]
- 前端框架 = Next.js 15 + TS + Tailwind + shadcn/ui (反对就说"用 Vite + React")
- 后端栈 = Next.js API routes(同仓库, 起手最快)
  • 备选: Hono(轻、edge ready)、Fastify(独立服务)、Express(传统)
- DB = SQLite(本地) + Postgres(部署), 配 Prisma 或 Drizzle ORM
  • 备选: MySQL, MongoDB, Supabase(BaaS, 含 Auth)
- 鉴权 = NextAuth / Lucia / 自写 JWT(看复杂度)
- 表单/校验 = react-hook-form + zod
- 状态管理 = React 内置(Server/Client Component) + 必要时 Zustand
- 部署目标 = ?(必须明确, 不允许"或"假设)
  • A. 本地 production server (零成本, 不对外)
  • B. Vercel / Netlify / Cloudflare Pages (云平台, 需要账号)
  • C. 自有服务器(VPS / Docker, 需要 SSH + 域名)
- 测试策略 = lint + typecheck + build + 浏览器主链路; 关键业务逻辑补 unit
- CI/CD = 简易 GitHub Actions(若有 remote) / 纯本地脚本(若无)

[这轮必须先问你才能继续的硬决策]
- 宿主原生结构化交互可用: 打开真实选择框/确认框/选择工具, 先问后端栈 / DB / 部署目标这 1-3 个高影响决策
- 宿主原生结构化交互不可用: 降级为 A/B/C/D 文本选项, 每题标默认并保留"自定义 / type something"
- 鉴权范围、现有脚手架等次级问题放下一轮或用文件探索先自治判断, 不要把 5 个问题一次塞给用户

[我还不确定但不急的, 下一轮再聊]
- 具体 API endpoint 设计
- DB schema 细节
- 部署环境变量
- 性能预算

[这轮答完后]
- 收敛后写 .opc/solution/solution-design.md
- 部署目标这条必须明确; 不明确不能进 implementation
```

## 多轮迭代规则

方案阶段常见的"答完引出新问题":

- 用户答"用 Postgres" → AI 追问"用本地 Docker Postgres 起服务, 还是 Supabase / Neon / 自建实例?"
- 用户答"部署到 Vercel" → AI 追问"你有账号 + token 吗? 是否需要自定义域名? 数据库选 Vercel Postgres 还是 Supabase?"
- 用户答"加 SSO" → AI 追问"哪家 IdP? Google / GitHub / 企业 SAML?"
- 用户答"多租户" → AI 追问"按行隔离(row-level)、按 schema、还是按 DB 实例?"

这些都是合理的第 2、3 轮 ConfirmCard 内容。**不要一次性把所有细节抛在第 1 轮**, 用户会被淹没。

## 方案探索门禁

技术选型已有强约束(用户 / 现有项目 / 行业标准)时, 直接给单条推荐路径 + 写明放弃的方案。无强约束时给 2-3 个方案方向, 每个写清:

- 适用场景;
- 交付速度;
- 可维护性;
- UI/体验质量;
- 验证和部署风险;
- 推荐结论。

方案不是"想法列表"。选定推荐方案后, 把工作切成 planning packet: discovery、foundation、delivery、verification、follow-through。

## 全栈技术默认

OPC 默认全栈交付, 推荐 Node 系轻量栈:

| 层 | 默认 | 适用 | 备选 |
|---|---|---|---|
| 前端 | Next.js 15 (App Router) | SSR、SEO、混合渲染、有部署平台 | React + Vite (纯 SPA), Astro (内容站) |
| 后端 | Next.js API routes | 同仓库 monorepo 风、起手最快 | Hono(轻、edge), Fastify(独立服务高吞吐), Express(经典) |
| DB | SQLite + Prisma → Postgres + Prisma | 本地开发零配置, 部署可持久化 | MySQL, MongoDB(NoSQL 场景), Supabase/PlanetScale(BaaS) |
| ORM | Prisma | 类型安全、迁移好 | Drizzle(轻、边缘友好), Kysely(query builder), 手写 SQL(简单场景) |
| 鉴权 | NextAuth(Auth.js) | 主流社交登录、邮箱 | Lucia(灵活), 自写 JWT + bcrypt(完全控制), Clerk/Supabase Auth(BaaS) |
| 文件/对象存储 | 本地 `./uploads/` 开发, S3/R2 部署 | 上传/导出场景 | UploadThing, Cloudflare R2, Supabase Storage |
| 队列/异步 | 不默认; 真需要才引 | 长任务、定时任务 | BullMQ + Redis, Inngest, Trigger.dev |
| 验证/表单 | zod + react-hook-form | 类型推导、SSR friendly | Valibot(更轻), Yup |

**默认不用 Java/Spring、Python/Django/FastAPI、Go、Rust** 作为后端, 除非用户明确指定或现有项目已经是这些栈。理由: 与前端联调成本、起势速度、部署简单度都不如 Node 系。

如果用户说"用 Python" / "用 Java", 切到对应栈, 但在 ConfirmCard 里复述决策依据(用户明确指定 + AI 不抗辩)。

## 方案文档结构

收敛后写 `.opc/solution/solution-design.md`(除非项目已有规范路径)。文档是最终稿, 多轮 Q&A 留在 `.opc/solution/discussion.md`。

```markdown
# <需求名称> Solution Design

> 状态: solution 阶段产出
> 讨论日志: .opc/solution/discussion.md(N 轮已收敛)
> 输入: .opc/requirements/prd.md

## 需求映射
| PRD 条目 | 方案响应 | 风险 |
|---|---|---|

## 候选方案(对比)
| 方案 | 适用场景 | 取舍 | 风险 | 推荐度 |
|---|---|---|---|---|

## 推荐方案
- 选择:
- 原因:
- 放弃的方案:

## Planning Packet
- Discovery:
- Foundation:
- Delivery:
- Verification:
- Follow-through:

## 信息架构和流程
- 导航/入口:
- 页面/模块:
- 状态: loading / empty / error / success / permission / audit
- 关键流程:

## UI 策略
- 文案语种:
- 设计方向:
- 组件库策略:
- 可访问性约束:
- MasterGo/Codify 是否需要:

## 技术方案
- 前端框架:
- 后端栈: (Next.js API routes / Hono / Fastify / ...)
- DB + ORM: (SQLite/Postgres + Prisma / ...)
- 鉴权方案:
- 路由:
- 状态管理:
- 数据获取:
- 表单/校验:
- 权限:
- 日志/埋点:

## API 和数据
- 接口设计风格: (REST / RPC / Server Actions)
- DB schema 概要:
- 字段映射:
- 真实数据来源: (内部、外部 API、用户上传)
- API 溯源报告要求:

## 测试策略
- 单元测试:
- 组件/集成测试:
- 浏览器/截图验证:
- 回归风险:

## 部署计划
- 部署目标: (本地 / Vercel / Netlify / 自有服务器 — 必须明确)
- 环境变量/secrets:
- production gate:
- 回滚方式:

## 自我审查
- Must 覆盖:
- 占位符/未知项:
- 假设冲突:
- 可交给 UI/实现/部署的输入:
```

## UI 方案门禁

进入 MasterGo/Codify 前, 方案必须给出:

- 覆盖范围: 页面、状态、弹窗、抽屉、错误/空态、权限态;
- UI 文案语种;
- 设计方向, 或在 ConfirmCard 里聊出来的选择;
- 组件库策略;
- 验证方式。

这些字段要映射进 [design-workflow.md](design-workflow.md) 的 MasterGo 设计 Gate Card。

## 实现方案门禁

进入代码实现前, 方案必须给出:

- 使用现有项目栈还是新建项目;
- 如果是新建项目, 实现目录放哪里、脚手架怎么起、默认框架是什么(全栈: 前端 + Node 后端 + DB);
- 是否需要自动初始化 Git、`.gitignore`、测试命令、最小 CI/CD;
- 目标路由和组件边界;
- API endpoint 列表(name + method + 简述);
- DB schema 概要;
- 数据来源(真实接入路径或 mock 标识);
- 交互状态和错误处理;
- 测试命令、浏览器验证目标和部署目标。

如果这些信息不完整, 先补方案 ConfirmCard; 不要直接写一个无法验收的静态页面。

## 收敛与完成判断

收敛信号:

- [ ] 后端栈、DB、部署目标三项已锁定为具体值, 不存在"或"假设
- [ ] 鉴权/权限范围已聊清
- [ ] 候选方案对比已写或单条路径理由已写
- [ ] Planning packet 已成形
- [ ] 上一轮答案没引出新硬决策
- [ ] PRD 的 Must 在方案里都有响应
- [ ] 关键风险有处理方式

满足后:

1. 写 `.opc/solution/solution-design.md`。
2. 在 `.opc/solution/discussion.md` 末尾写"Round N 已收敛, 进 ui-design"。
3. `opc-task-state.py mark solution done --artifact .opc/solution/solution-design.md --evidence "ConfirmCard 第 N 轮收敛, 后端栈=Hono, DB=Postgres+Prisma, 部署=Vercel" --next-action "进 ui-design 阶段, 第 1 轮 ConfirmCard 聊视觉/品牌/密度"`。
4. 自动进入 ui-design 阶段。
