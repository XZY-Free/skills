# 06 — 实现规划与全栈实现

实现期默认**自治推进**: 进入这里时数据来源、后端栈、DB、部署目标应来自方案、现有项目或安全默认值。仍有高影响不确定时先用原生选择交互处理; 低风险细节直接自治。除非遇到 token/凭证/付费/破坏性写入等硬阻塞, **不打断**。

## 何时读

- 进入 implementation-plan 阶段(写 `.opc/implementation-plan/index.md`)
- 开始 implementation slice(实现代码)
- 接 API(Magic 还原企业级模式 / 全栈实现)

跳过场景: 极小改动且用户明确要求跳过规划 — 标 `implementation-plan: skipped` 并写明风险和跳过授权; **完整 OPC 默认不得跳过**。

## 目录

- [核心原则](#核心原则)
- [implementation-plan 目录结构](#implementation-plan-目录结构)
- [文件职责](#文件职责)
- [上下文预算计划](#上下文预算计划)
- [并行分配计划](#并行分配计划)
- [上下文读取规则](#上下文读取规则)
- [拆分规则](#拆分规则)
- [Slice 模板](#slice-模板)
- [ADR 规则](#adr-规则)
- [implementation-plan 完成门禁](#implementation-plan-完成门禁)
- [全栈实现默认](#全栈实现默认)
- [框架选择 + 空工作区](#框架选择--空工作区)
- [Git / 工程初始化](#git--工程初始化)
- [后端 + DB 初始化](#后端--db-初始化)
- [TDD / regression ratchet](#tdd--regression-ratchet)
- [上下文预算执行](#上下文预算执行)
- [并行 lane 执行](#并行-lane-执行)
- [实现步骤](#实现步骤)
- [前端设计质量执行](#前端设计质量执行)
- [API 接入](#api-接入)
- [实现完成门槛](#实现完成门槛)

---

# Part 1: implementation-plan(实现前技术规划)

## 核心原则

- **一个入口**: `.opc/implementation-plan/index.md` 是唯一入口, 后续实现先读它
- **全局契约集中**: 架构边界、API/DB/权限/环境变量和验证规则只放全局契约文件, 不在每个 slice 重复
- **按用户价值切片**: 开发计划按可验证用户链路拆, **不**按 `frontend.md` / `backend.md` / `database.md` / `tests.md` 机械拆
- **每片可执行**: 每个 slice 同时含 UI、API、DB、文件范围、步骤和验收, 读 `index + architecture + contracts + verification + 当前 slice + ADR` 后即可实现
- **设计质量入片**: 新 UI 或非像素级还原的 purpose / tone / differentiation / constraints / anti-generic guardrails 必须进入 `architecture.md` / `verification.md` / 当前 slice
- **上下文预算优先**: 每个 slice 估计当前会话能否完成实现、验证和 checkpoint; 超出预算继续拆 slice, **不靠聊天历史硬撑**
- **并行先识别后派发**: 非平凡项目必须识别可并行 lane, 依赖清楚、Write Set 不重叠、验证责任明确、宿主允许时才派发子代理
- **决策单独记录**: 高影响技术选择写 ADR, 每份 ADR 只记录一个决策
- **边实现边校准**: 实现中发现计划不匹配, 先更新 slice 或 ADR, 再继续编码

## implementation-plan 目录结构

```text
.opc/implementation-plan/
├── index.md
├── architecture.md
├── contracts.md
├── work-breakdown.md
├── parallelization.md
├── verification.md
├── decisions/
│   └── ADR-0001-*.md
└── slices/
    └── 01-*.md
```

小项目轻量版: 只有 `index.md` + `work-breakdown.md` + `verification.md` + 1 个 slice。大项目必须拆出 `architecture.md` + `contracts.md` + `decisions/`。

## 文件职责

**`index.md`** (~150 行):
- 目标和当前实现计划状态
- 必读顺序
- 当前上下文预算: green / yellow / red
- checkpoint 路径: `.opc/implementation/continuation.md`
- 全局约束摘要
- slice 列表、依赖关系和推荐实现顺序
- parallel lanes 摘要
- 当前 slice 指针
- 影响全局实现的 ADR 列表
- 文件拆分和恢复提示

**`architecture.md`**:
- C4 风格 context / container / component 摘要
- 系统边界、模块关系、部署形态
- 横切规则: 鉴权、权限、日志、错误处理、可访问性、性能预算、国际化、设计质量 brief
- 现有代码复用点和禁止改动的边界

**`contracts.md`**:
- API endpoint、输入/输出 schema、错误码
- DB schema、关系、索引、迁移约束
- 权限模型、角色、审计
- 环境变量、secret、安全存放位置
- 外部接口、文件、队列、定时任务和数据来源
- 不可破坏的兼容约束

**`work-breakdown.md`**:
- 按用户价值链组织开发计划
- 每个 slice 的依赖、预计文件范围、验证方式和完成定义
- **不**把一条用户链路拆散到前端、后端、数据库三个互不相干的计划里

**`parallelization.md`**:
- dependency graph: 哪些 slice/lane 可并行, 哪些必须串行
- lane owner: main / subagent-eligible / manual-only
- Write Set: 每条 lane 可写文件/目录, 互不重叠或明确协调点
- Read Set: 每条 lane 所需最小上下文
- handoff contract: 子代理返回必须含 changed paths、tests、risks、next action
- merge order: 主代理整合顺序和冲突处理
- context budget: 每条 lane 预估 green/yellow/red 和 checkpoint 时机

**`verification.md`**:
- lint、typecheck、unit/integration/e2e/build 命令
- Browser / Playwright 主链路
- 设计质量 brief 检查: 桌面/移动截图、状态覆盖、文案语种、无 generic AI aesthetics blocker
- 数据持久化、刷新后状态、权限和错误态检查
- 部署前检查和回归风险

## 上下文预算计划

编写 implementation-plan 时先评估本会话能做多少:

- `green`: 可完成当前 slice 的代码、测试、浏览器验证和 checkpoint
- `yellow`: 只做一个小 lane 或一个文件组, 完成后立刻 checkpoint
- `red`: 不开始新实现, 先写 `.opc/implementation/continuation.md`

每个 slice 必须写:

- Context Budget: green / yellow / red
- Checkpoint Trigger: 何时调用 `opc-task-state.py checkpoint`
- Resume Command: 恢复时先读哪些文件
- Stop Before: 哪些动作前必须先 checkpoint(大规模重构、长测试、部署、切换 slice)

发现当前 slice 无法在上下文内完成 → **先拆成更小的 value slice 或 lane, 再实现**。

## 并行分配计划

非平凡项目必须写 `parallelization.md`。识别并行同时考虑上下文预算:

- **可并行**: 独立页面/流程、独立 API resource、独立测试补强、文档/验证工件、互不重叠的组件族
- **不可并行**: 同一文件/同一 schema 的竞争修改、跨模块接口未定、迁移顺序未定、需要同一浏览器会话连续操作
- **子代理适用**: lane 目标明确、输入 Read Set 小、Write Set 独立、可用命令验证、失败可局部回滚
- **主代理保留**: 架构决策、共享 schema/API 契约、最终整合、冲突解决、发布和最终证据

写给子代理的 lane 必须含: 目标、Read Set、Write Set、禁止改动范围、验证命令、返回格式。

当前宿主或上层指令不允许子代理 → 仍保留 parallelization plan, 由主代理按 lane 顺序执行。

## 上下文读取规则

实现任何 slice 前, **固定**读取:

```text
1. .opc/implementation-plan/index.md
2. .opc/implementation-plan/architecture.md
3. .opc/implementation-plan/contracts.md
4. .opc/implementation-plan/verification.md
5. .opc/implementation-plan/slices/<current-slice>.md
6. 当前 slice 引用的 ADR
```

**禁止默认一次性读取整个 `.opc/implementation-plan/`**。只有当当前 slice 的 `Read Set` 明确引用其它文件, 或发现全局契约冲突时, 才继续读取。

## 拆分规则

- **不允许**只写一个巨大 `technical-implementation-plan.md` 或 `development-plan.md`
- **不允许**只按技术层拆成 `frontend.md` / `backend.md` / `database.md` / `tests.md`
- 单个文件接近 200 行或 12KB 时继续拆, 更新 `index.md`
- 每个 slice 覆盖一个可独立验证的用户价值链; 太大时按子流程拆成 `03a-*` / `03b-*` 连续切片
- 每个 slice 必须有 `Read Set`; 没有 Read Set 的 slice 不可进入实现
- 拆分后不得出现孤儿文件; 所有文件都要从 `index.md` 或某个 slice 可达

## Slice 模板

```markdown
# <slice-id> <用户价值>

## Read Set
- ../index.md
- ../architecture.md
- ../contracts.md
- ../verification.md
- ../decisions/ADR-0001-*.md

## Goal
本切片让 <用户> 能通过 <机制> 达成 <结果>。

## Depends On
- <前置 slice 或 none>

## Context Budget
- Budget: green / yellow / red
- Checkpoint Trigger:
- Resume:
- Stop Before:

## Parallelization
- Lane:
- Eligible For Subagent: yes / no / only-if-host-allows
- Write Set:
- Coordination:

## UI
- 路由/入口:
- 状态: loading / empty / error / success / permission
- 文案语种:
- 设计质量 brief: purpose / tone / differentiation / constraints / anti-generic guardrails

## API
- METHOD /api/<resource>
- Input / Output / Error

## Data
- 表/字段/关系
- seed 或真实数据来源

## Files To Touch
- <前端文件>
- <API 文件>
- <schema/test 文件>

## Steps
1. <先写或更新测试/契约>
2. <实现后端/DB>
3. <实现前端>
4. <接 API 和状态>

## Verify
- <命令>
- Browser: <路径和主链路>
- 数据持久化: <刷新/重启后检查>

## Checkpoint
- Command: python3 <skill-dir>/scripts/mandatory/opc-task-state.py checkpoint ...
- Next Action:
```

## ADR 规则

ADR 只记录高影响技术决策。每份 ADR 一件事:

```markdown
# ADR-0001 <决策标题>

## Status
Accepted / Proposed / Superseded

## Context
为什么现在必须决定。

## Decision
选择什么。

## Consequences
收益、代价、迁移/回滚影响。

## Rejected
- <备选> | <拒绝原因>
```

适合写 ADR: ORM、鉴权、部署平台、权限深度、队列/异步、第三方服务、破坏性迁移、跨模块 API 契约。**不为文件命名、普通组件拆分、小 helper 写 ADR**。

## implementation-plan 完成门禁

满足:

- `index.md` 存在且含读取顺序、slice 索引、依赖顺序和当前推荐实现顺序
- 全局契约文件覆盖架构、API/DB/权限/环境变量和验证
- `work-breakdown.md` 按用户价值切片
- `parallelization.md` 存在, 或轻量任务写明无需并行的原因
- 每个 slice 有 Read Set、Context Budget、Parallelization、UI/API/Data/Files/Steps/Verify/Checkpoint
- UI 相关 slice 已带入设计质量 brief 或明确说明严格跟随 MasterGo 原稿
- 高影响决策已写入 `decisions/ADR-xxxx.md`
- 单文件未超过拆分阈值, 或已拆分并更新索引
- `opc-task-state.py mark implementation-plan done` 的 evidence 指向 `index.md` 和当前第一条 slice

---

# Part 2: implementation(全栈实现)

## 全栈实现默认

OPC 默认交付**用户能登录能用的全栈应用**, 不是前端 + mock 的演示版。

实现阶段必须落地:

1. **前端** — 路由、组件、状态、表单、表格、弹窗、空态/错误态、权限态
2. **后端** — Node 系 API routes(默认 Next.js API routes / Hono / Fastify / Express, 按 solution 锁定的栈)
3. **DB schema + 迁移** — 默认 Prisma schema(`schema.prisma`)+ `prisma migrate dev`; 或 Drizzle schema + `drizzle-kit push`
4. **真实 API 接口** — CRUD、查询、鉴权、文件上传等; **不是 typed mock 包装层**
5. **种子数据** — `prisma db seed` 或独立 seed 脚本灌入开发数据, 让首次启动就有可看的内容
6. **`.env` + `.env.example`** — `.env.example` 进版本控制; `.env` 进 `.gitignore`。真实 secret 走宿主 user-scope 配置

**只有用户明确选择"演示版 / 不要真后端 / 只做展示"时**, 才允许跳过后端 + DB 用前端 + typed mock 替代。

❌ 不允许的退化路径:

- "项目复杂, 我先用 mock, 等后端就绪再接" — 默认就要起后端
- "我没看到 API 文档, 所以全 mock" — 没文档就自己设计 API
- "我自己起后端来不及, 用 in-memory store 就行" — in-memory 不算持久化, 退化成 mock
- "用 Server Component 直接读硬编码 JSON" — mock 的另一种写法

## 框架选择 + 空工作区

先遵循现有仓库:

1. 读 `package.json`、路由结构、组件目录、样式体系和测试命令
2. 复用现有框架、组件库、图标库、数据层和 lint/typecheck/test 配置
3. 未经明确需要, 不新增依赖

无现有仓库时按方案或默认栈起脚手架(默认: Next.js 15 App Router + TS + Tailwind + shadcn/ui; Next.js API routes; SQLite + Prisma → Postgres; NextAuth)。

### 空工作区启动规则

当前工作区没有现成仓库 → **不要**把完整 OPC 收缩成"先交设计包"。继续:

1. 读取 PRD / solution / UI design brief 或对应 discussion.md
2. 读取 `.opc/implementation-plan/index.md` 和当前 slice 的 Read Set
3. 确认方案里是"新建项目"还是"复用现有项目"
4. 没有现成项目 → 按 implementation-plan 锁定的目标栈自动起**全栈**脚手架(前端 + 后端 + DB + ORM)
5. 脚手架完成后立即继续当前 slice 的组件、API、DB、验证和部署链路

默认目录策略:

- 当前目录为空或只有 `.opc/`、`.codify/`、`.omx/` 这类过程目录 → 直接在当前目录起项目
- 当前目录已是业务工作区但没有实现目录 → 新建 `app/`、`web/` 或方案里明确的实现目录
- 只有当目录选择会影响真实交付物、已有代码所有权或部署方式时, 才确认

❌ 不允许作为完整 OPC 收尾:

- "这里不是 Git 仓库, 所以本轮先停在设计包"
- "我先把 PRD、方案、UI 做完, 等你决定要不要实现"
- "下一步请在前端原型、API 契约、产品评审里选一个"

## Git / 工程初始化

完整 OPC 实现阶段默认补齐本地工程基础设施:

- 当前目录没 `.git/` 且不在父级 Git 仓库内 → `git init`
- 缺 `.gitignore` → 创建, 覆盖 `node_modules`、构建产物、`.env*`(不含 `.env.example`)、日志、缓存、Prisma 本地 DB(`*.db`、`*.sqlite*`)
- 缺 `package.json` → 按方案栈创建脚手架, 不要求用户先准备项目
- 缺测试命令 → 新项目补最小 test/build/browser 验证
- 没有 git remote → 继续本地实现和验证; 远端 push、创建远端 repo 或改受保护分支才需确认

这些动作写入 `.opc/state/opc-task.json` 的 note/evidence。**不要把"缺仓库 / 缺脚手架 / 缺测试"作为实现阶段停点**。

实现阶段 gate truth = 真实运行的产物(测试通过 + 浏览器主链路截图 + API 返回真实数据), 不是"代码写完了"。lint 通过、build 通过只是必要条件, 不是充分证据。

## 后端 + DB 初始化

按 solution 锁定的栈起服务。最常见路径(Next.js API routes + Prisma + SQLite):

```bash
npm i prisma @prisma/client zod
npm i -D @types/node tsx
npx prisma init --datasource-provider sqlite
# 编辑 prisma/schema.prisma, 按 solution 的 DB schema 概要建模
npx prisma migrate dev --name init
# 写 seed 脚本(prisma/seed.ts), 灌入开发数据
npx prisma db seed
```

独立后端: `npm i hono @hono/node-server` 或 `npm i fastify @fastify/cors`。

API 路由组织:

- Next.js: `app/api/<resource>/route.ts` 用 Route Handlers; `lib/db.ts` 出 Prisma client
- Hono / Fastify: `server/index.ts` 注册路由; `server/routes/<resource>.ts` 拆模块
- 共享类型: `lib/schema.ts` 用 zod 写 input/output schema, 前后端都用

`.env.example` 必填字段示例:

```
DATABASE_URL="file:./dev.db"
# 部署时切: DATABASE_URL="postgresql://user:pass@host:5432/db"
NEXTAUTH_SECRET="<generate-with: openssl rand -base64 32>"
NEXTAUTH_URL="http://localhost:3000"
```

## TDD / regression ratchet

可测试行为默认**先补失败测试或回归用例**, 再写实现:

- 新业务逻辑、字段映射、权限、表单校验、状态机、API contract → 先写 unit/component/integration/contract 测试
- API 路由 → `vitest` + `supertest`(或框架原生测试)覆盖 happy path + 至少一个错误路径
- 修 bug → 先复现失败, 再补能证明该 bug 的最小回归用例
- UI 交互或响应式风险 → 先写 Playwright/Browser 场景或明确截图检查点
- 项目没有测试基础设施 → 记录原因, 用浏览器验证脚本、截图、console 和核心流程操作作为替代证据

遇到红测、构建失败、运行时报错或视觉异常 → 走 **systematic debugging**: 复现 → 读错误 → 查最近变化 → 提一个单一假设 → 最小验证 → 修根因。**不要靠猜测连打补丁**。

## 上下文预算执行

实现前判断当前会话上下文能否闭合当前 slice/lane:

- `green`: 继续实现当前 slice, 完成后 checkpoint
- `yellow`: 只做当前 lane 的最小闭环, 不开始新 lane
- `red`: 不再开始新代码修改, 立即写 checkpoint

```bash
python3 <skill-dir>/scripts/mandatory/opc-task-state.py checkpoint \
  --phase implementation \
  --slice "<current-slice-id>" \
  --lane "<lane-or-none>" \
  --summary "<已完成/未完成摘要>" \
  --touched "<path>" \
  --test "<command/result>" \
  --next-action "<恢复后第一步>"
```

触发 checkpoint 的时机:

- 已修改一组相关文件, 还没进入下一组
- 准备运行长测试、build、浏览器验证或部署
- 准备切换 slice/lane
- 读入长日志、长 DSL/D2C、长设计文档后
- 感觉上下文接近压缩或回答开始依赖大量聊天历史时

压缩或重开后: `opc-task-state.py resume` → 读 `.opc/implementation/continuation.md` 和当前 slice 的 Read Set, **不要求用户复述**。

## 并行 lane 执行

先读 `.opc/implementation-plan/parallelization.md`。宿主和上层指令允许子代理时, 对 `Eligible For Subagent: yes` 的 lane 可并行派发; 否则主代理按 lane 顺序执行。

派发前检查:

- 该 lane 的 Read Set 足够小
- Write Set 与其它 lane 不重叠, 或已有明确协调点
- shared contracts/schema/API 已稳定
- lane 有独立验证命令
- 子代理返回要求含 changed paths、tests、risks、next action

主代理保留: 共享契约、数据库迁移顺序、跨 lane 冲突、最终验证、部署和用户汇报。

## 实现步骤

1. **建立实现 inventory**:
   - 以当前 slice 为边界, 不把其它 slice 的功能顺手实现
   - 路由(前端 page + 后端 endpoint)、组件、状态、表单、表格、弹窗、权限、空态/错误态
   - DB schema 表、字段、关系、索引
   - API endpoint 列表(method + path + input/output schema)
   - UI 文案语种和技术词保留
   - 设计质量 brief: purpose / audience / tone / differentiation / constraints
   - Context Budget 和 checkpoint 触发点
   - 并行 lane、Write Set、是否适合子代理
   - 测试和部署命令
   - TDD/regression ratchet 选择
   - 没有现成项目: 脚手架目录、栈、路由和初始依赖怎么落地

2. **后端 + DB 先于前端动手**(同仓库 monorepo 风):
   - 写 `schema.prisma`, 跑 `migrate`
   - 写 zod schema(input/output), 出共享类型
   - 写 API routes / endpoints, 每个 endpoint 至少有 happy path test
   - seed 脚本灌开发数据
   - 验证后端能跑: `curl` 几个 endpoint 拿到非空真实 JSON

3. **前端按模式拆组件**:
   - app shell / route page / feature modules / reusable primitives / data helpers
   - 不把复杂页面写成一个巨大组件
   - 相同 UI 用同一组件或明确 variant
   - 数据获取走真实 API: `fetch` / `tRPC` / `react-query` / Server Component 直连

4. **接 API**(如果 PRD 写了第三方接口): 见下文 [API 接入](#api-接入)

5. **实现交互**:
   - 控件更新真实 DB 数据(经 API)
   - 表单有校验、提交中、成功和失败状态
   - 数据视图有 loading、empty、error、permission 状态
   - 重要副作用(删除、覆盖、付款)有二次确认
   - 鉴权页面有未登录态

6. **验证**:
   - 运行 lint、typecheck、unit/integration/e2e、build
   - 启动 dev server + 后端 + DB, 用 Browser 优先验证, 不可用时用 Playwright
   - 浏览器主链路: 注册 / 登录 / 主流程 CRUD / 关键交互
   - 检查桌面和一个移动尺寸
   - 截图或 DOM/console 证据要能证明非空、无框架 overlay、无相关 console error、DB 数据真实持久(刷新后还在)

## 前端设计质量执行

实现新 UI 或非像素级还原时, 把 [04-solution.md](04-solution.md#体验设计质量门禁) 落到代码里:

- 全局样式或 design tokens 表达当前 tone: 字体、色彩、空间、radius、shadow、motion
- 组件变体覆盖 default / loading / empty / error / success / disabled / permission
- 页面信息密度匹配业务场景, 企业后台优先可扫描、可比较、可重复操作
- 保留一个有意图的记忆点, 但不破坏可用性、性能和可访问性
- 避免模板化 SaaS 卡片堆、随意紫色渐变、无意义 glow、文案溢出和卡片套卡片
- 桌面和移动视口都要确认无重叠、无裁切、无空白假完成

项目已有设计系统 → 先复用现有 tokens、组件和图标库。只有在 PRD 或方案明确需要新视觉方向时, 才新增样式层或设计 primitives。

---

# Part 3: API 接入

**定位**: Magic 还原"企业级实现"模式或全栈实现把页面写死的占位数据换成真实接口数据。**快速复刻模式不走本流程**。

**不接 API ≠ 完成**。哪怕用户跳过, 企业级实现也要明确告知"未接 API"状态, 让用户知道这一步欠着。

## 触发条件

进入企业级模式 + 写完 JSX 后**自动触发**:

```
1. 检查 <projectDir>/.codify/api-docs/ 目录
   ├── 存在且非空 → 列出文件 → 自动识别格式 → 进入文档解析
   └── 不存在 / 空 → 走"没文档时的引导"
2. 用户引导后给到文档 → 进入字段检测
3. 用户明确说"暂时没文档" → 跳过本流程, 但明确告诉用户:
     "数据现在是写死的, 后续接口文档到位后, 把它放进 .codify/api-docs/
      告诉我'重新接 API', 我自动接上。"
```

## 文档解析

约定标准目录:

```
<projectDir>/.codify/api-docs/
  ├── auth.openapi.yaml          # 用户认证(OpenAPI)
  ├── agents.openapi.yaml        # Agent 业务(OpenAPI)
  ├── billing.postman.json       # 计费(Postman Collection)
  ├── activities.md              # 活动接口(自由文本)
  └── README.md                  # 可选: 用户自己写的索引
```

目录不存在 → 自动 `mkdir -p .codify/api-docs/`。多文件支持, 所有文件都会被扫。**用户随手往里扔即可, 不要求统一格式**。

支持格式:

| 格式 | 识别 | 解析 |
|---|---|---|
| OpenAPI / Swagger | `.yaml/.yml/.json`, 顶层有 `openapi: 3.x` 或 `swagger: 2.0` | `paths` + `components.schemas` |
| Postman Collection | `.json`, 顶层有 `info.schema` 含 `postman.com` | `jq '.item[] \| {name, request}'` |
| 自由文本 markdown | `.md` | `## GET /xxx` 当 endpoint, 代码块当 sample |
| URL + sample(对话里贴) | 用户口述 `GET https://...` 返回 `{...}` | 当场拼最小 OpenAPI 写到 `_inline.openapi.yaml` |

```bash
python3 <skill-dir>/scripts/helpers/parse-api-docs.py \
  --dir <projectDir>/.codify/api-docs \
  --out <projectDir>/.codify/api-endpoints.json
```

## 字段检测(扫 D2C HTML / JSX)

启发式识别"看着像写死数据"的节点:

| 节点特征 | 大概率动态 |
|---|---|
| `data-name` 含 `name/title/desc/text/value/count/time/date` | ✅ |
| 纯数字(`2.4K` / `87%` / `¥1,234`) | ✅ |
| 时间(`2025-01-15` / `15:30` / `2 小时前`) | ✅ |
| 重复结构 `act-1` / `act-2` / `act-3` 列表 | ✅ |
| 用户名 / 邮箱 / 手机号样式 | ✅ |
| 头像 / 图片 src | ⚠️ 可能 |
| 按钮文案("提交" / "登录") | ❌ 静态 |
| 标签("Beta" / "New") / 品牌名 / logo | ❌ 静态 |

输出候选清单让用户确认(高置信、用户已说"直接做" → 自动接受)。

## 字段映射

每个动态字段 → 跟接口文档对一遍:

1. **字段名直接匹配**: `data-name="user-name"` → `data.user.name` 或 `data.name`
2. **语义匹配**: "2.4K"(number) → API 哪个字段是 number + 含 `count` / `total`
3. **重复结构 → 数组**: `act-1/act-2/act-3` → API 返回的 `activities[]`
4. **匹配不上 → 问用户**

存到 `.codify/api-mapping.json`:

```json
{
  "agent-detail": {
    "endpoint": "GET /api/agents/{id}",
    "source": ".codify/api-docs/agents.openapi.yaml#paths./agents/{id}.get",
    "fields": {
      "hero.title":       "data.name",
      "hero.subtitle":    "data.description",
      "stats.userCount":  "data.stats.userCount"
    },
    "lists": {
      "activities": {
        "endpoint": "GET /api/agents/{id}/activities",
        "itemFields": {
          "title": "title",
          "desc":  "description",
          "time":  "createdAt"
        }
      }
    }
  }
}
```

## 数据层生成

按映射在 `src/lib/api/` 下生成 fetch 模块:

```typescript
// src/lib/api/agents.ts
import { fetcher } from './_base'

export interface Agent {
  id: string
  name: string
  description: string
  stats: { userCount: number; uptime: number; satisfaction: number }
}

export async function getAgent(id: string): Promise<Agent> {
  return fetcher(`/api/agents/${id}`)
}

export async function getAgentActivities(id: string): Promise<Activity[]> {
  return fetcher(`/api/agents/${id}/activities`)
}
```

`src/lib/api/_base.ts` 轻量 fetch 封装(根据项目栈选):

```typescript
export async function fetcher<T>(path: string, init?: RequestInit): Promise<T> {
  const base = process.env.NEXT_PUBLIC_API_BASE ?? ''
  const res = await fetch(`${base}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}
```

项目用 SWR / React Query / Axios → 跟着项目惯例(嗅探 `package.json`)。

## JSX 消费(替换写死数据)

写死的字符串 → prop 传入 + fetch 注入。

```tsx
// 改前
export function Hero() {
  return <h1>AURA Agent</h1>
}

// 改后
export function Hero({ agent }: { agent: Agent }) {
  return <h1>{agent.name}</h1>
}

// 入口
export default async function Page({ params }: { params: { id: string } }) {
  const [agent, activities] = await Promise.all([
    getAgent(params.id),
    getAgentActivities(params.id),
  ])
  return <AgentDetailPage agent={agent} activities={activities} />
}
```

## ⚠️ 强制溯源汇报

**接 API 这一步做完, 必须打印这份汇报给用户**。不打印就不算完成。

```
═══════════════════════════════════════════════════════════════════════
本次 API 接入汇报(模式: 企业级实现)
═══════════════════════════════════════════════════════════════════════

路由: /agent-detail/[id]

  视图字段 ⟵ 接口 (字段路径)
  ───────────────────────────────────────────────────────────────────
  Hero.title             ⟵ GET /api/agents/{id}            (data.name)
  Hero.subtitle          ⟵ GET /api/agents/{id}            (data.description)
  Stats.userCount        ⟵ GET /api/agents/{id}            (data.stats.userCount)
  ActivityItem.title     ⟵ GET /api/agents/{id}/activities ([].title)
  ActivityItem.time      ⟵ GET /api/agents/{id}/activities ([].createdAt)

  源文档: .codify/api-docs/agents.openapi.yaml
  生成的数据层: src/lib/api/agents.ts
  Page 入口:   src/app/agent-detail/[id]/page.tsx

═══════════════════════════════════════════════════════════════════════
未接 API 的字段(静态):
  - Hero.tag           "Beta"        (装饰文案)
  - CTA.button         "试用"        (按钮文案)

接口文档里没用到的接口(本次还原范围外):
  - GET  /api/agents/list           (本次没列表页, 跳过)
═══════════════════════════════════════════════════════════════════════

下一步:
  1. 用真后端跑一遍 dev, 看每页数据是否正确渲染
  2. 走 [07-verification.md](07-verification.md#3b-2-企业级实现验证) 做最终验证
```

汇报里**每一项都必须能溯源到具体文件 + 字段路径**, 不允许只写"接了某接口"。用户拿到这份汇报应该能立刻审计: 哪些没接、接对没、漏了哪个文档里的接口。

## 没文档时的引导

`.codify/api-docs/` 不存在或为空 → 跟用户说:

```
我没找到接口文档。我设了一个默认目录, 你按以下任一方式给我:

a) 把文档放进 <projectDir>/.codify/api-docs/(我会自动识别格式):
     - OpenAPI / Swagger: *.yaml / *.yml / *.json
     - Postman Collection: *.json
     - 自由文本:           *.md

b) 直接告诉我文档的绝对路径, 我去读

c) 你只有 URL + sample 响应也行:
     原话告诉我 "接口 GET https://api.x.com/users/me 返回 {...}",
     我帮你拼成最小 OpenAPI 写进 .codify/api-docs/_inline.openapi.yaml

d) 暂时没有 → 我跳过接 API, 数据先写死。
   告知: 这意味着企业级实现欠了这一步, 后续文档到位告诉我"重新接 API", 我会自动接上。
```

---

## MasterGo 来源实现衔接

- 企业级实现默认读 [05-mastergo.md](05-mastergo.md#模式-a-企业级实现)
- 快速复刻只在用户明确 opt-in 后读 [05-mastergo.md](05-mastergo.md#模式-b-快速复刻-opt-in)
- 视觉差异、字体、mask、SVG、渐变等问题读 [07-verification.md](07-verification.md#渲染补丁)
- 实现完必须进 [07-verification.md](07-verification.md#3b-magic-还原验证)
- MasterGo 还原的项目同样默认 + 后端 + DB, 除非 solution 阶段明确锁定为"仅前端静态原型"

---

## 实现完成门槛

实现阶段完成必须满足:

- 代码覆盖方案里的 must-have
- 已按 `implementation-plan` 当前 slice 实现, 计划和现实冲突已先更新 slice 或 ADR
- 当前 slice/lane 已按 Context Budget 写 checkpoint, 或实现报告说明无需 checkpoint
- **前端 + 后端 + DB 三层都已落地**, 不是前端 + mock 假装完整(除非 solution 明确锁定 mock)
- 关键 UI 状态和核心流程可交互, 数据经 API 真实读写, 刷新后状态还在
- 设计质量 brief 已落到可见 UI, 并通过桌面/移动截图或 Browser/Playwright 检查
- 可测试行为已有失败测试/回归用例, 或记录了替代验证理由
- lint/typecheck/test/build 中能运行的都已运行并读过输出
- 浏览器验证已完成, 含截图或等价证据
- `.opc/state/opc-task.json` 中 `implementation` 标记为 `done`, 记录代码路径、API 路径、DB schema 路径和验证证据

某项无法验证 → 标记为 `blocked` 或 `skipped` 并写明原因; **不要说"已完成"**。
