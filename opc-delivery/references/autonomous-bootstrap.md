# 自治补齐工作流

目标: 把"缺少前置条件"当成交付工作的一部分处理。完整 OPC 任务里, 代理默认自己补齐本地工程、版本控制、**后端 + DB**、验证和预览交付需要的基础设施; 只有真正需要用户输入、授权或承担风险时才暂停。

**重要边界**: 自治补齐是执行阶段动作, 它不替代高影响疑点确认。后端栈、DB 选型、部署目标、数据来源(真实 / 演示)若仍不明确且会改变成品, 先用宿主原生选择/确认交互处理; 若已有 PRD、方案、现有项目或安全默认可推断, 直接执行并记录。

## 触发场景

- 完整 OPC: 用户说"从需求到上线"/"后面都做完"/"你决定"/"完整交付";
- 当前目录没有 Git 仓库、`package.json`、前端项目、后端项目、DB schema、API 路由、测试命令、CI/CD 或部署配置;
- 中断恢复后发现当前阶段需要的本地前置条件不存在;
- solution 阶段已锁定栈/DB/部署目标, implementation-plan 已给出当前 slice, 进 implementation 时缺脚手架。

## 自治补齐矩阵

| 缺什么 | 默认动作 | 何时问用户 |
|---|---|---|
| Git 仓库 | 在当前业务工作区 `git init`, 补 `.gitignore`, 阶段完成可做本地里程碑 commit | 已有父级仓库、目录所有权不清、需要推送远端 |
| 前端工程 | 按方案或默认栈起脚手架(Next.js / Vite / Astro) | 现有项目强约束冲突, 需拍板 |
| **Node 后端** | 按方案或默认栈起后端(Next.js API routes / Hono / Fastify / Express); 写最简 health endpoint | 后端栈会影响组织长期维护且未明确 |
| **DB + ORM** | `prisma init --datasource-provider sqlite`(开发); 部署切 Postgres; 按 schema 概要写 `schema.prisma` + `migrate dev` | DB 未明确且会影响部署/迁移, 或需要外部托管凭证 |
| **API 路由** | 按 PRD/方案 endpoint 列表创建 route handlers, 每个至少有 happy path + 一个错误路径 | endpoint 数量影响范围且无法推断 |
| **Seed 数据** | 写 `prisma/seed.ts`, 灌入开发数据让首次跑就有可看的内容 | 数据需要真实业务样本(脱敏后由用户提供) |
| 鉴权 | 按方案接入(NextAuth / Lucia / 自写 JWT) | 需要第三方 IdP(Google / GitHub / SAML) 凭证 |
| 设计风格 | 按 UI 方案落地; 无强约束默认 shadcn/Tailwind | 品牌/风格会显著影响验收且无法推断 |
| **演示数据** | 不默认创建 typed mock; 只有用户明确选择演示版时才用 | 用户没明确选演示而数据真实性影响交付 |
| 测试能力 | 新项目补最小 test/build/browser 验证; 现有项目复用已有命令 | 加依赖会冲突、测试环境需要凭证或外部服务 |
| CI/CD | 没有配置时补最小 build/test workflow 或 release checklist | 需要远端仓库、组织权限、付费 runner 或生产审批 |
| 预览上线 | 按已明确部署目标执行; 缺凭证不降级 | 部署目标不明确或缺凭证, 用原生选择/确认交互 |
| `.env` 模板 | 自动生成 `.env.example` 进版本; `.env` 进 `.gitignore` | 真实 secret 走宿主 user-scope 配置 |
| 文档/台账 | 自动写 `.opc/` 阶段产物、`discussion.md`、状态记录 | 不问, 除非用户明确只要口头结论 |

## 用户确认门

下面情况允许暂停, 打开宿主原生选择/确认交互或要用户提供具体值(参考 [clarification-loop.md](clarification-loop.md)):

- API key、token、secret、私有 URL、服务器地址、账号权限;
- production 部署、远端 push、覆盖已有画布/服务器/数据库、破坏性迁移;
- 付费资源、采购、外部服务开通;
- 法务、合规、客户数据范围、真实 SLA 这类代理无法自证的业务约束;
- 品牌/风格/交互取向会显著影响验收, 且无法从上下文可靠推断。

用户选择后立即继续当前阶段; 不要把"已收到选择"当成收尾。

需要用户拍板时优先使用当前 AI 宿主的真实结构化决策交互; 不可用时才降级为文本选择题。降级文本选项末尾必须保留"自定义 / type something", 允许用户输入未覆盖的方案; 不要预设答案空间封闭, 也不要用开放式"你看呢"替代具体选项。

## Git 启动规则

- 当前目录没有 `.git/` 且不在父级 Git 仓库内时, 完整 OPC 默认 `git init`;
- 同时补 `.gitignore`, 覆盖 `node_modules`、构建产物、`.env*`(不含 `.env.example`)、日志、缓存、本地 DB 文件(`*.db`、`*.sqlite*`)、Prisma 客户端生成物(若不进版本);
- 本地 commit 可作为阶段证据; commit message 记录为什么做这个阶段;
- 没有 remote 时不要要求用户先建 GitHub 仓库; 继续本地实现、验证和 preview;
- 远端 push、创建远端 repo、修改受保护分支仍是确认门。

## 后端 + DB 启动规则

按 solution 锁定的方案执行, 不重新选型。常见路径:

**Next.js API routes + Prisma + SQLite(开发) → Postgres(部署)**:

```bash
npm i prisma @prisma/client zod
npm i -D @types/node tsx
npx prisma init --datasource-provider sqlite
# 写 prisma/schema.prisma(按 solution schema 概要)
npx prisma migrate dev --name init
# 写 prisma/seed.ts, 配置 package.json prisma.seed 字段
npx prisma db seed
```

**独立 Hono 后端**:

```bash
npm i hono @hono/node-server
npm i -D tsx
# server/index.ts 注册路由
# 同样 prisma 走起
```

DB 文件路径默认 `prisma/dev.db`(SQLite) 或 `DATABASE_URL` env 指向(Postgres)。**绝不把 DB 文件提交进 Git**。

## 状态记录

自治补齐动作写入 `.opc/state/opc-task.json` 的阶段 note 或 evidence:

- 自动创建了哪些本地资源(脚手架、schema、API endpoint、seed);
- 哪些资源仍 pending, 因为需要用户凭证或授权;
- 下一个自动动作是什么;
- 如果暂停, 用户回来后代理应该从哪里继续。

## 反模式(自治补齐里不允许的)

- ❌ "用户没说要后端, 我先做前端 + mock" — 后端是默认全栈交付的一部分, 除非 solution 明确锁了 mock
- ❌ "起后端太慢, 我用 in-memory store 顶一下" — 等于 mock, 不持久, 不算实现
- ❌ "Server Component 直接 import 一个静态 JSON" — 等于 mock 的另一种写法
- ❌ "没有 Git 仓库，你先创建好我再继续"
- ❌ "没有 package.json, 所以不能实现"
- ❌ "没有部署服务器, 本轮只能结束在设计"
- ❌ "等你决定风格后我再开始做, 当前先到这里"(没强约束就用默认, 有强约束就开原生选择)
- ❌ "Vercel token 缺失, 我退回 next start"(应说明卡住缺凭证或让用户选择部署路径, 不自动降级)
