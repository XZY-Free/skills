# 06b — 全栈实现

把 [06a-implementation-plan.md](06a-implementation-plan.md) 写好的 slice 落成**真实可登录、可操作、数据持久化**的程序。**前端 + 后端 + DB 三层都要落地**, 不是前端 + mock 演示。

## 何时读

- 已完成 implementation-plan, 开始第一个 slice
- 后端 / DB 初始化、Git / 工程初始化
- 选定 commit 节奏 / 上下文预算 / 并行 lane 执行
- 前端设计质量执行

API 接入(企业级 / 替换占位数据为真实接口)见 [06c-api-wiring.md](06c-api-wiring.md)。

---


## 目录

- [全栈实现默认](#全栈实现默认)
- [框架选择 + 空工作区](#框架选择--空工作区)
- [Git / 工程初始化](#git--工程初始化)
- [Commit 节奏](#commit-节奏)
- [后端 + DB 初始化](#后端--db-初始化)
- [TDD / regression ratchet](#tdd--regression-ratchet)
- [上下文预算执行](#上下文预算执行)
- [并行 lane 执行](#并行-lane-执行)
- [实现步骤](#实现步骤)
- [前端设计质量执行](#前端设计质量执行)
- [MasterGo 来源实现衔接](#mastergo-来源实现衔接)
- [实现完成门槛](#实现完成门槛)

---

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

commit 颗粒度和 message 风格见下文 [Commit 节奏](#commit-节奏); 不要在阶段 / slice 之间机械切 commit。

实现阶段 gate truth = 真实运行的产物(测试通过 + 浏览器主链路截图 + API 返回真实数据), 不是"代码写完了"。lint 通过、build 通过只是必要条件, 不是充分证据。

## Commit 节奏

OPC 默认 commit 节奏 = **工程师的常态 commit 习惯**, 不是机械化的"每个 slice 一个 commit"。"是否要 commit"在 [不问白名单](02-clarification.md#必问-vs-不问-白名单) 里 — 代理自己判断, 不让用户停下来定。

### 为什么不按 slice / 阶段切

把 commit 颗粒度跟 slice / 阶段绑死会出两种坏味:

- slice 内做了 3 件不相关的事(scaffold + 写 schema + 改样式)凑成一个大 commit → 后续 bisect / revert 没法用
- slice 是个跨 4 文件的小修复, 又被切成 1 commit / 文件 → commit 历史噪音化

commit 颗粒度由**逻辑内聚性**决定: 一个 commit 描述一件事。这件事可以横跨多个 slice 步骤, 也可以只是 slice 里的一个子动作。

### Commit 触发信号(自治判断)

看到这些信号就 commit, 不用问用户:

- **一件事闭合**: 一个用户价值 / 一个功能点 / 一个修复, 代码行为可验证 → commit
- **重构稳定**: 行为不变, 测试还绿, 跟前面 feat 是两件事 → 单独 commit
- **实验性 / 破坏性改动前**: 准备做大重命名、删大段代码、跑会改 schema 的迁移 → 先把"现在能跑"的状态 commit 当安全点
- **切换上下文前**: 一组逻辑相关改动结束, 要切到不相关的另一块前 → commit 划界, 避免下一段混进来
- **长测试 / 浏览器验证 / 部署前**: 先 commit 锁定要被验证的版本
- **阶段闭合**: 需求 / 方案 / UI / 实现 / 部署任一阶段产物落盘 → commit 当里程碑(可叠加在常规 commit 之上)

### 一个 commit 一件事

混着不算 commit:

- ❌ "feat: 加登录 + 顺手 format + 删了几个 TODO"
- ❌ "fix bug + refactor user.ts + 升级 dependency"
- ✅ 拆成 3 个 commit, 一件事一个

一次写完发现已经混了 → 用 `git add -p` 分块 stage, 或先 stash 一部分, 分批 commit; 不要强行打包。

### Commit message: 跟随项目风格, 写 why

**先嗅探项目既有风格再决定 message 格式**:

```bash
git log --oneline -20
```

按观察到的实际风格写:

- 项目用 conventional commits(`feat:` / `fix:` / `refactor:` 开头) → 跟用
- 项目用中文自由格式("让 X 做 Y" / "修 X bug") → 跟用
- 项目用 ticket 前缀(`PROJ-123:`) → 跟用
- 项目混用 / 无既有 commit / 仓库刚 `git init` → 默认 conventional commits

默认 conventional commits 模板(仅在无既有风格时):

```
<type>(<scope>): <一句 what>

<可选: 为什么这么做, 哪些副作用, 跟哪个 slice / PRD 段对齐>
```

- type: feat / fix / refactor / chore / docs / test / build / ci / perf / style
- 中文 OK; 技术名词保留英文(`Prisma`、`API routes`、`schema`)

为什么 message 要写 why(无论哪种风格):

- diff 已经是 what; message 再重复 what 信息密度为零
- 几个月后回头读 git log 决定 revert / cherry-pick → 看的是 why
- bisect 命中某个 commit 时, message 要能一句话讲清"这个 commit 在做什么 + 为什么这样选"

### 跟 checkpoint 的分工

OPC 有两套持久化, 不要互相替代:

| 机制 | 颗粒度 | 写什么 |
|---|---|---|
| `git commit` | 逻辑一件事 | 代码产物里程碑, 供 bisect / revert / 历史 |
| `opc-task-state.py checkpoint` | slice / lane / 上下文边界 | 任务恢复指针, 写到 `.opc/state/` |

可以同一时刻既 commit 又 checkpoint(常见: slice 完成时), 但不要因为 checkpoint 就跳过 commit, 也不要因为 commit 就跳过 checkpoint。两者用途不同。

### 远端 push 仍是确认门

commit 是本地的, 用户随时丢弃。push 不是: 协作者会拉, CI 会跑, 公开仓库可能被索引。

- push 到 remote → 按 [02-clarification.md#git-与后端启动规则](02-clarification.md#git-与后端启动规则) 走确认门
- force push / 改受保护分支 / 跨用户改 PR → 确认门
- 含 secret 的 commit 哪怕只在本地, 不要 push; 授权 push 前先扫一遍

### 反模式

- ❌ 每个 slice 自动 commit, 不论改动是否内聚
- ❌ 一天攒一个超大 commit "Day 1 progress"
- ❌ message 只写 "update" / "fix" / "WIP" / "."
- ❌ 项目明明用中文自由格式, 强行套 conventional commits
- ❌ 无关 format / lint 改动混进 feat commit
- ❌ commit 含 `.env`、secret、build 产物、本地 DB(`.gitignore` 失效时)
- ❌ 实验性大重构前不 commit, 改炸了只能靠 IDE 撤销
- ❌ 因为做了 checkpoint 就跳过 commit, 或反过来
- ❌ 让用户决定"现在要不要 commit"

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

4. **接 API**(如果 PRD 写了第三方接口): 见 [06c-api-wiring.md](06c-api-wiring.md)

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

实现新 UI 或非像素级还原时:

**Product Surface 一致性**(先做): 实际放置位置和 solution-design.md 的升降级表对账; 不一致写理由到 slice 的 Product Surface 字段, 矛盾态先回方案补。详见 [03b-productization.md#能力升降级](03b-productization.md#能力升降级)。

**设计质量 brief 兑现**: 把 [04-solution.md](04-solution.md#体验设计质量门禁) 落到代码里:

- 全局样式或 design tokens 表达当前 tone: 字体、色彩、空间、radius、shadow、motion
- 组件变体覆盖 default / loading / empty / error / success / disabled / permission
- 页面信息密度匹配业务场景, 企业后台优先可扫描、可比较、可重复操作
- 保留一个有意图的记忆点, 但不破坏可用性、性能和可访问性
- 避免模板化 SaaS 卡片堆、随意紫色渐变、无意义 glow、文案溢出和卡片套卡片
- 桌面和移动视口都要确认无重叠、无裁切、无空白假完成

项目已有设计系统 → 先复用现有 tokens、组件和图标库。只有在 PRD 或方案明确需要新视觉方向时, 才新增样式层或设计 primitives。

---


---

## MasterGo 来源实现衔接

- 企业级实现默认读 [05b-magic-restore.md](05b-magic-restore.md#模式-a-企业级实现)
- 快速复刻只在用户明确 opt-in 后读 [05b-magic-restore.md](05b-magic-restore.md#模式-b-快速复刻-opt-in)
- 视觉差异、字体、mask、SVG、渐变等问题读 [07b-restore-verify.md](07d-restore-patches.md#渲染补丁)
- 实现完必须进 [07b-restore-verify.md](07b-restore-verify.md#3b-magic-还原验证)
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
- **项目长期文档已产出**: `README.md` + `docs/ARCHITECTURE.md` + `docs/DATA-MODEL.md` + `docs/CONVENTIONS.md` + `docs/decisions/`, 详见 [11-project-docs.md](11-project-docs.md)
- **未授权产出工具方言文件**(`AGENTS.md` / `CLAUDE.md` / `.cursorrules` / 同类): 不应自动新建, 见 [11-project-docs.md#显式不产出](11-project-docs.md#显式不产出)
- `.opc/state/opc-task.json` 中 `implementation` 标记为 `done`, 记录代码路径、API 路径、DB schema 路径和验证证据

某项无法验证 → 标记为 `blocked` 或 `skipped` 并写明原因; **不要说"已完成"**。
