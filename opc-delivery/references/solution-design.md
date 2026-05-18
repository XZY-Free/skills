# 方案阶段工作流

目标: 在 PRD 之后、UI/代码之前, 定义“怎么做”。方案要给 UI 设计、前端实现、API wiring、测试和部署提供可执行输入。

方案阶段不固定要求用户看确认卡。先基于 PRD、现有项目和默认栈形成方案; 只有后端栈、DB、部署目标、权限/合规等高影响项不明确时, 才使用原生选择交互。

## 目录

- [进入条件](#进入条件)
- [高影响方案决策](#高影响方案决策)
- [方案探索门禁](#方案探索门禁)
- [全栈技术默认](#全栈技术默认)
- [方案文档结构](#方案文档结构)
- [UI 方案门禁](#ui-方案门禁)
- [实现方案门禁](#实现方案门禁)
- [收敛与完成判断](#收敛与完成判断)

## 进入条件

- 有 PRD 或足够明确的需求 brief;
- 已检查 `.opc/requirements/discussion.md`、现有项目结构、技术栈、组件库、接口文档和部署环境;
- 需求阶段的数据来源、核心流程和验收口径足够驱动方案。

## 高影响方案决策

需要用户拍板的方案项:

- 后端栈会影响组织长期维护, 且用户已有明确偏好或现有系统约束;
- DB 选型会影响部署、成本、迁移或多人协作;
- 部署目标未明确, 或会从本地/preview 进入 production;
- 权限、审计、SSO、多租户、客户数据范围不明确;
- 方案需要采购、外部服务开通、付费 API、远端 push 或破坏性迁移。

不需要用户拍板的方案项:

- 新项目默认 Next.js + Node API + SQLite/Postgres + Prisma/Drizzle;
- 目录布局、组件边界、内部 API 路由命名;
- 测试命令、本地脚手架、`.env.example`、基础 CI;
- 已被 PRD、现有项目或用户原话锁定的技术栈。

需要拍板时, 优先用 `request_user_input` 或等价原生选择/确认交互。文本 A/B/C 只在工具不可用时使用。

## 方案探索门禁

技术选型已有强约束时, 直接给单条推荐路径并写明放弃原因。无强约束时给 2-3 个方案方向, 每个写清:

- 适用场景;
- 交付速度;
- 可维护性;
- UI/体验质量;
- 验证和部署风险;
- 推荐结论。

方案不是想法列表。选定推荐方案后, 把工作切成 Planning Packet: discovery、foundation、delivery、verification、follow-through。

## 全栈技术默认

OPC 默认全栈交付, 推荐 Node 系轻量栈:

| 层 | 默认 | 适用 | 备选 |
|---|---|---|---|
| 前端 | Next.js 15 (App Router) | SSR、SEO、混合渲染、有部署平台 | React + Vite, Astro |
| 后端 | Next.js API routes | 同仓库 monorepo 风、起手最快 | Hono、Fastify、Express |
| DB | SQLite + Prisma -> Postgres + Prisma | 本地开发零配置, 部署可持久化 | MySQL、MongoDB、Supabase/PlanetScale |
| ORM | Prisma | 类型安全、迁移好 | Drizzle、Kysely、手写 SQL |
| 鉴权 | NextAuth(Auth.js) | 主流社交登录、邮箱 | Lucia、自写 JWT、Clerk/Supabase Auth |
| 文件/对象存储 | 本地 `./uploads/` 开发, S3/R2 部署 | 上传/导出场景 | UploadThing、Cloudflare R2、Supabase Storage |
| 队列/异步 | 不默认; 真需要才引 | 长任务、定时任务 | BullMQ + Redis、Inngest、Trigger.dev |
| 验证/表单 | zod + react-hook-form | 类型推导、SSR friendly | Valibot、Yup |

默认不用 Java/Spring、Python/Django/FastAPI、Go、Rust 作为后端, 除非用户明确指定或现有项目就是这些栈。理由: 与前端联调成本、起势速度和部署简单度都不如 Node 系。

## 方案文档结构

写 `.opc/solution/solution-design.md`(除非项目已有规范路径)。多轮讨论或原生选择提交结果留在 `.opc/solution/discussion.md`。

```markdown
# <需求名称> Solution Design

> 状态: solution 阶段产出
> 讨论日志: .opc/solution/discussion.md
> 输入: .opc/requirements/prd.md

## 需求映射
| PRD 条目 | 方案响应 | 风险 |
|---|---|---|

## 候选方案
| 方案 | 适用场景 | 取舍 | 风险 | 推荐度 |
|---|---|---|---|---|

## 推荐方案
- 选择:
- 原因:
- 放弃的方案:
- 用户拍板记录: (如有, 写原生选择结果或文本降级回复)

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
- 后端栈:
- DB + ORM:
- 鉴权方案:
- 路由:
- 状态管理:
- 数据获取:
- 表单/校验:
- 权限:
- 日志/埋点:

## API 和数据
- 接口设计风格: REST / RPC / Server Actions
- DB schema 概要:
- 字段映射:
- 真实数据来源:
- API 溯源报告要求:

## 测试策略
- 单元测试:
- 组件/集成测试:
- 浏览器/截图验证:
- 回归风险:

## 部署计划
- 部署目标: 本地 / Vercel / Netlify / Cloudflare / 自有服务器
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
- 设计方向, 或用户已通过原生选择交互确认的风格;
- 组件库策略;
- 验证方式。

这些字段要映射进 [design-workflow.md](design-workflow.md) 的 MasterGo 设计 Gate Card。

## 实现方案门禁

进入代码实现前, 方案必须给出:

- 使用现有项目栈还是新建项目;
- 如果是新建项目, 实现目录、脚手架、默认框架;
- 是否需要自动初始化 Git、`.gitignore`、测试命令、最小 CI/CD;
- 目标路由和组件边界;
- API endpoint 列表(name + method + 简述);
- DB schema 概要;
- 数据来源(真实接入路径或演示标识);
- 交互状态和错误处理;
- 测试命令、浏览器验证目标和部署目标。

如果这些信息缺失但可由现有项目或默认规则安全推断, 直接补齐并记录。只有高影响不确定才回到选择交互。

## 收敛与完成判断

收敛信号:

- 后端栈、DB、部署目标为具体值, 不存在会影响实现的“或”假设;
- 鉴权/权限范围已明确或有清楚默认;
- 候选方案对比已写或单条路径理由已写;
- Planning Packet 已成形;
- PRD 的 Must 在方案里都有响应;
- 关键风险有处理方式;
- 未决项已归类为自治处理 / 需要拍板 / 卡住缺 X。

完成动作:

1. 写 `.opc/solution/solution-design.md`;
2. 更新 `.opc/solution/discussion.md`;
3. 写 `.opc/solution/last-handoff.md`;
4. 跑 `scripts/handoff-lint.py --phase solution`;
5. `opc-task-state.py mark solution done --artifact .opc/solution/solution-design.md --evidence "方案覆盖 PRD、技术栈、数据、测试和部署计划" --next-action "进入 ui-design 或 implementation"`;
6. 自动进入下一阶段。
