# 全栈实现工作流

目标: 把已确认的 PRD/方案/UI 变成可运行、可测试、可部署的**全栈应用**——前端 + Node 后端 + DB + 真实 API。不要把 D2C、截图、静态 mock、纯前端 + typed mock 当成实现完成。

**节奏 = 执行式自动推进**。进入实现阶段时, 数据来源、后端栈、DB、部署目标应来自方案、现有项目或安全默认值。若仍存在高影响不确定, 先用宿主原生选择/确认交互处理; 低风险细节直接自治。除非遇到 token/凭证/付费/破坏性写入等硬阻塞, 不打断。

## 目录

- [进入条件](#进入条件)
- [全栈实现默认](#全栈实现默认)
- [框架选择](#框架选择)
- [空工作区启动规则](#空工作区启动规则)
- [Git / 工程初始化](#git--工程初始化)
- [后端 + DB 初始化](#后端--db-初始化)
- [TDD / regression ratchet](#tdd--regression-ratchet)
- [实现步骤](#实现步骤)
- [新项目脚手架补充](#新项目脚手架补充)
- [MasterGo 来源实现](#mastergo-来源实现)
- [完成门槛](#完成门槛)

## 进入条件

- 有 PRD + 方案 + 设计 brief(或对应 discussion.md 收敛证据);
- 方案或现有项目已明确后端栈、DB、部署目标、数据来源; 若未明确, 已按 [clarification-loop.md](clarification-loop.md) 处理高影响疑点;
- 若来自 MasterGo, 还原路径已经完成 DSL/D2C 拉取和模式选择;
- 若无 MasterGo 来源, 已明确 UI 策略、页面、状态和验收标准。

## 全栈实现默认

OPC 默认交付**用户能登录能用的全栈应用**, 不是前端 + mock 的演示版。

实现阶段必须落地:

1. **前端** — 路由、组件、状态、表单、表格、弹窗、空态/错误态、权限态。
2. **后端** — Node 系 API routes(默认 Next.js API routes / Hono / Fastify / Express, 按 solution 锁定的栈)。
3. **DB schema + 迁移** — 默认 Prisma schema(`schema.prisma`)+ `prisma migrate dev`; 或 Drizzle schema + `drizzle-kit push`。
4. **真实 API 接口** — CRUD、查询、鉴权、文件上传等; **不是 typed mock 包装层**。
5. **种子数据** — 用 `prisma db seed` 或独立 seed 脚本灌入开发数据, 让首次启动就有可看的内容。
6. **`.env` + `.env.example`** — `.env.example` 进版本控制; `.env` 进 `.gitignore`。真实 secret 走宿主 user-scope 配置。

**只有当用户明确选择“演示版 / 不要真后端 / 只做展示”时, 才允许跳过后端 + DB, 用前端 + typed mock 替代。**

不允许的退化路径:

- ❌ "项目复杂, 我先用 mock, 等后端就绪再接" — 默认就要起后端
- ❌ "我没看到 API 文档, 所以全 mock" — 没文档就自己设计 API
- ❌ "我自己起后端来不及, 用 in-memory store 就行" — in-memory 不算持久化, 退化成 mock 一样
- ❌ "用 Server Component 直接读硬编码 JSON" — 这就是 mock 的另一种写法

## 框架选择

先遵循现有仓库:

1. 读 `package.json`、路由结构、组件目录、样式体系和测试命令。
2. 复用现有框架、组件库、图标库、数据层和 lint/typecheck/test 配置。
3. 未经明确需要, 不新增依赖。

无现有仓库时, 按方案或默认栈起脚手架。默认推荐(若 solution 没另写):

- 前端: Next.js 15 (App Router) + TS + Tailwind + shadcn/ui;
- 后端: Next.js API routes(同仓库); 单独服务时用 Hono / Fastify;
- DB: SQLite(开发) + Prisma; 部署时切 Postgres;
- 鉴权: NextAuth(Auth.js) 或自写 JWT, 看 solution 决定。

## 空工作区启动规则

如果当前工作区没有现成仓库, 不要把完整 OPC 收缩成"先交设计包"。应直接继续:

1. 读取 `.opc/requirements/prd.md`、`.opc/solution/solution-design.md`、`.opc/ui/design-brief.md` 或同目录 `discussion.md`;
2. 确认方案里写的是"新建项目"还是"复用现有项目";
3. 没有现成项目时, 按方案里的目标栈自动起**全栈**脚手架(前端 + 后端 + DB + ORM);
4. 脚手架完成后立即继续组件、API、DB、验证和部署链路。

默认目录策略:

- 当前目录为空或只有 `.opc/`、`.codify/`、`.omx/` 这类过程目录时, 直接在当前目录起项目;
- 当前目录已是业务工作区但没有实现目录时, 新建 `app/`、`web/` 或方案里明确的实现目录;
- 只有当目录选择会影响真实交付物、已有代码所有权或部署方式时, 才向用户确认。

以下说法不允许作为完整 OPC 的收尾:

- "这里不是 Git 仓库，所以本轮先停在设计包"
- "我先把 PRD、方案、UI 做完, 等你决定要不要实现"
- "下一步请在前端原型、API 契约、产品评审里选一个"

## Git / 工程初始化

完整 OPC 实现阶段默认补齐本地工程基础设施:

- 当前目录没有 `.git/` 且不在父级 Git 仓库内时, 执行 `git init`;
- 缺 `.gitignore` 时创建, 覆盖 `node_modules`、构建产物、`.env*`(不含 `.env.example`)、日志、缓存、Prisma 本地 DB(`*.db`、`*.sqlite*`);
- 缺 `package.json` 时按方案栈创建脚手架, 不要求用户先准备项目;
- 缺测试命令时, 新项目补最小 test/build/browser 验证;
- 没有 git remote 时继续本地实现和验证; 远端 push、创建远端 repo 或改受保护分支才需要确认。

这些动作写入 `.opc/state/opc-task.json` 的 note/evidence。不要把"缺仓库 / 缺脚手架 / 缺测试"作为实现阶段停点。

实现阶段的 gate truth = 真实运行的产物 (测试通过 + 浏览器主链路截图 + API 返回真实数据), 不是"代码写完了"。lint 通过、build 通过都只是必要条件, 不是充分证据。

## 后端 + DB 初始化

按 solution 阶段锁定的后端栈和 DB 起服务。最常见路径(Next.js API routes + Prisma + SQLite):

```bash
# 安装依赖(按 solution 栈调整)
npm i prisma @prisma/client zod
npm i -D @types/node tsx

# 初始化 Prisma
npx prisma init --datasource-provider sqlite

# 编辑 prisma/schema.prisma, 按 solution 的 DB schema 概要建模
# 然后 migrate
npx prisma migrate dev --name init

# 写 seed 脚本(prisma/seed.ts), 灌入开发数据
npx prisma db seed
```

独立后端(Hono / Fastify / Express)走对应栈的初始化:

```bash
# Hono 例
npm i hono @hono/node-server
# Fastify 例
npm i fastify @fastify/cors
```

API 路由组织建议:

- Next.js: `app/api/<resource>/route.ts` 用 Route Handlers; 同步 `lib/db.ts` 出 Prisma client。
- Hono / Fastify: `server/index.ts` 注册路由; `server/routes/<resource>.ts` 拆模块。
- 共享类型: 在 `lib/schema.ts` 用 zod 写 input/output schema, 前后端都用。

`.env.example` 必填字段示例:

```
DATABASE_URL="file:./dev.db"
# 部署时切: DATABASE_URL="postgresql://user:pass@host:5432/db"
NEXTAUTH_SECRET="<generate-with: openssl rand -base64 32>"
NEXTAUTH_URL="http://localhost:3000"
```

## TDD / regression ratchet

可测试行为默认先补失败测试或回归用例, 再写实现:

- 新业务逻辑、字段映射、权限、表单校验、状态机、API contract: 先写 unit/component/integration/contract 测试。
- API 路由: 用 `vitest` + `supertest`(或框架原生测试)覆盖 happy path + 至少一个错误路径。
- 修 bug: 先复现失败, 再补能证明该 bug 的最小回归用例。
- UI 交互或响应式风险: 先写 Playwright/Browser 场景或明确截图检查点。
- 项目没有测试基础设施时, 记录原因, 并用浏览器验证脚本、截图、console 和核心流程操作作为替代证据。

遇到红测、构建失败、运行时报错或视觉异常时, 先走 systematic debugging: 复现 → 读错误 → 查最近变化 → 提一个单一假设 → 最小验证 → 修根因。不要靠猜测连打补丁。

## 实现步骤

1. **建立实现 inventory**:
   - 路由(前端 page + 后端 endpoint)、组件、状态、表单、表格、弹窗、权限、空态/错误态;
   - DB schema 表、字段、关系、索引;
   - API endpoint 列表(method + path + input/output schema);
   - UI 文案语种和技术词保留;
   - 测试和部署命令;
   - TDD/regression ratchet 选择: 要先补哪些测试、哪些只能人工/浏览器验证;
   - 如果没有现成项目: 脚手架目录、栈、路由和初始依赖怎么落地。

2. **后端 + DB 先于前端动手**(同仓库 monorepo 风):
   - 写 `schema.prisma`, 跑 `migrate`;
   - 写 zod schema(input/output), 出共享类型;
   - 写 API routes / endpoints, 每个 endpoint 至少有 happy path test;
   - seed 脚本灌开发数据;
   - 验证后端能跑: `curl` 几个 endpoint 拿到非空真实 JSON。

3. **前端按模式拆组件**:
   - app shell / route page / feature modules / reusable primitives / data helpers;
   - 不把复杂页面写成一个巨大组件;
   - 相同 UI 用同一组件或明确 variant;
   - 数据获取走真实 API: 用 `fetch` / `tRPC` / `react-query` / Server Component 直连。

4. **接 API**(如果 PRD 写了第三方接口):
   - 有 `.codify/api-docs/` 时读 [api-doc-parsing.md](api-doc-parsing.md);
   - 字段不确定时读 [api-field-mapping.md](api-field-mapping.md);
   - 完成后产出 [api-trace-report.md](api-trace-report.md) 口径的溯源报告。

5. **实现交互**:
   - 控件更新真实 DB 数据(经 API);
   - 表单有校验、提交中、成功和失败状态;
   - 数据视图有 loading、empty、error、permission 状态;
   - 重要副作用(删除、覆盖、付款)有二次确认;
   - 鉴权页面有未登录态。

6. **验证**:
   - 运行 lint、typecheck、unit/integration/e2e、build;
   - 启动 dev server + 后端 + DB, 用 Browser 优先验证, 不可用时用 Playwright;
   - 浏览器主链路: 注册 / 登录 / 主流程 CRUD / 关键交互;
   - 检查桌面和一个移动尺寸;
   - 截图或 DOM/console 证据要能证明非空、无框架 overlay、无相关 console error、DB 数据真实持久(刷新后还在)。

## 新项目脚手架补充

从零起项目时, 先把"能继续交付的最小工程"搭起来:

- 生成 `package.json`、启动命令、构建命令和必要的目录结构;
- 初始化本地 Git 和 `.gitignore`;
- 建立 app shell、基础路由、全局样式和页面骨架;
- **同步起后端 + DB**(Prisma init + schema + 一两个最简 endpoint), 不要"前端先, 后端等以后";
- 把 PRD 的核心流程先落成可点击 + 数据真实持久化的主链路, 而不是只生成静态首页;
- 让 UI 文案跟随 PRD 语种规则, 不默认变成英文 dashboard;
- 先记录 preview 部署路径和后续环境变量需求, 避免实现完再回头补部署计划。

## MasterGo 来源实现

- 企业级实现默认读 [restoration-enterprise.md](restoration-enterprise.md);
- 快速复刻只在用户明确 opt-in 后读 [restoration-fast-prototype.md](restoration-fast-prototype.md);
- 视觉差异、字体、mask、SVG、渐变等问题读 [rendering-patches.md](rendering-patches.md);
- 实现完必须进 [verification-implementation.md](verification-implementation.md);
- MasterGo 还原的项目同样默认 + 后端 + DB, 除非 solution 阶段明确锁定为"仅前端静态原型"。

## 完成门槛

实现阶段完成必须满足:

- 代码覆盖方案里的 must-have;
- **前端 + 后端 + DB 三层都已落地, 不是前端 + mock 假装完整**(除非 solution 明确锁定 mock);
- 关键 UI 状态和核心流程可交互, 数据经 API 真实读写, 刷新后状态还在;
- 可测试行为已有失败测试/回归用例, 或记录了替代验证理由;
- lint/typecheck/test/build 中能运行的都已运行并读过输出;
- 浏览器验证已完成, 含截图或等价证据;
- `.opc/state/opc-task.json` 中 `implementation` 标记为 `done`, 记录代码路径、API 路径、DB schema 路径和验证证据。

如果某项无法验证, 标记为 `blocked` 或 `skipped` 并写明原因; 不要说"已完成"。
