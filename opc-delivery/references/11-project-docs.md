# 11 — 项目长期文档萃取

OPC 默认交付不只是"能跑的代码", 还要让**别的开发者 / 别的 AI 工具**接手时不破坏项目。`.opc/` 下的产物是**过程证据**, 不是长期文档。本节定义 implementation 完成时必须从过程证据里萃取出 `README.md` + `docs/` 长期文档体系。

## 何时读

- 进入 implementation 阶段, 已完成 implementation-plan 和首批 slice
- 准备 `opc-task-state.py mark implementation done` 前
- 跟接手者(人 / AI / 工具)交接前

跳过场景:
- 极小修改 / 单文件 bug 修复 / 仅改 README — 不引入新模块, 标 `skipped` + 原因
- Magic 纯还原 + 用户明确"不要长期文档" — 标 `skipped` + 原因
- 现有项目已有 `README.md` + `docs/` 且本次改动不影响公共接口 — 只补差异, 不全量重写

## 目录

- [为什么需要](#为什么需要)
- [必产出清单](#必产出清单)
- [显式不产出](#显式不产出)
- [萃取规则](#萃取规则)
- [README.md 模板](#readmemd-模板)
- [docs/ARCHITECTURE.md 模板](#docsarchitecturemd-模板)
- [docs/DATA-MODEL.md 模板](#docsdata-modelmd-模板)
- [docs/CONVENTIONS.md 模板](#docsconventionsmd-模板)
- [docs/decisions/ 处理](#docsdecisions-处理)
- [实现完成门槛集成](#实现完成门槛集成)

---

## 为什么需要

`.opc/` 目录里有 PRD、solution、implementation-plan、ADR、verification、release — 这些是**给当前会话和恢复用的过程产物**。它们**不是为接手者优化的入口**:

| 痛点 | 现象 |
|---|---|
| 找不到入口 | 新人 / AI clone 项目, 看到 `.opc/` 下 30 个文件不知道从哪读 |
| 过程词混入 | `.opc/implementation-plan/architecture.md` 里有 slice / checkpoint / context budget 这些过程词, 对接手者无意义 |
| 数据字典散落 | DB 表定义散在 `contracts.md` + 多个 slice + 各 ADR 里, 没有统一视图 |
| 提交规范不沉淀 | skill 里写了 commit 节奏指导, 但项目本身没有 `CONTRIBUTING.md` 或 `docs/CONVENTIONS.md` |
| 决策无主索引 | ADR 在 `.opc/implementation-plan/decisions/`, 接手者不知道这是项目宪法 |

修复方向: 在实现完成时**萃取**(不是复制)过程证据成长期文档。

---

## 必产出清单

完整 OPC 在 `implementation` 完成前必须满足:

| 文件 | 来源 | 用途 |
|---|---|---|
| `README.md` | 综合萃取 | 接手者第一眼看的项目入口 |
| `docs/ARCHITECTURE.md` | `.opc/implementation-plan/architecture.md` | 模块边界 / 系统拓扑 / 横切规则 |
| `docs/DATA-MODEL.md` | `.opc/implementation-plan/contracts.md` 的 DB 段 + Prisma schema | 表 / 字段 / 关系 / 索引 / 数据字典 |
| `docs/CONVENTIONS.md` | 综合萃取 | 提交规范 / 命名 / 目录约定 / 代码风格 |
| `docs/decisions/` | 挪自 `.opc/implementation-plan/decisions/` | ADR 主索引(每个决策一份) |

可选(推荐):
- `docs/runbook.md` — 怎么启动 / 部署 / 回滚(小项目可合并进 README)
- `docs/API.md` — API endpoint 清单(只在 API 暴露给外部消费者时产出)

---

## 显式不产出

**不**自动生成以下工具方言文件 — 这些反映**用户的工具栈选择**, 不是 skill 该替用户决定的:

- `AGENTS.md`(Codex 约定)
- `CLAUDE.md`(Claude Code 约定)
- `.cursorrules`(Cursor 约定)
- `.windsurfrules`(Windsurf 约定)
- `.github/copilot-instructions.md`(GitHub Copilot 约定)
- `GEMINI.md`(Gemini CLI 约定)

为什么:

1. **尊重项目主权**: 项目原本有这些文件 → 那是用户/团队的配置, 不覆盖; 没有 → 不强加
2. **避免方言战争**: 明天 Cline 流行了又得加 `.clinerules`, 永远追不完
3. **通用就够**: 所有主流 AI 编程工具默认都扫 `README.md` + `docs/`, 不需要方言文件做 redirect
4. **符合外科手术原则**: 只产出本任务必需的, 不顺手"美化"项目

例外: 项目原本就有这些文件 + 用户明确说"同步更新到 X" → 按用户授权更新。

---

## 萃取规则

### 不是复制, 是重写

`.opc/implementation-plan/architecture.md` 直接 `cp` 到 `docs/ARCHITECTURE.md` = 错误。过程产物里有 slice / checkpoint / context budget / ADR 引用等只对当前会话有意义的词, 接手者读不懂。

正确做法:

- **去过程词**: 删 `Read Set` / `Context Budget` / `Checkpoint Trigger` / `slice 指针`
- **加入口语**: 加"快速启动 / 必读 / 主要模块"等接手者视角章节
- **稳定路径**: 用项目里的真实路径(如 `src/lib/`), 不用 `.opc/implementation-plan/slices/03-*` 这种过程路径
- **可独立读完**: docs/ 里每个文件独立可读, 不要求读者读完 `.opc/` 才看懂

### 单一真相源原则

一个事实只在一处写定义, 其它地方 anchor 引用:

| 事实 | 真相源 | 引用方 |
|---|---|---|
| 项目简介 / 跑起来 | `README.md` | 其它文档 anchor 回来 |
| 模块边界 / 部署形态 | `docs/ARCHITECTURE.md` | README 摘一句 |
| 表结构 | `docs/DATA-MODEL.md` 或 `prisma/schema.prisma` | 二选一, 不重复 |
| 提交规范 | `docs/CONVENTIONS.md` | README 摘一句 |
| 高影响决策 | `docs/decisions/ADR-XXXX.md` | README 列索引 |

`.opc/` 下的对应文件保留(供 skill 自己 resume 用), **不删除, 也不在 docs/ 里 backlink** — 它是 skill 内部状态, 接手者不该看到。

---

## README.md 模板

接手者第一眼看的, **不要超过 200 行**。结构:

```markdown
# <项目名>

<一句话定位: 谁用的、解决什么问题>

## Tech Stack

- 前端: <e.g. Next.js 15 App Router + TS + Tailwind + shadcn/ui>
- 后端: <e.g. Next.js API routes / Hono / Fastify>
- DB: <e.g. MySQL 8 (Docker 容器本地起, 部署同一种), Prisma>
- 鉴权: <e.g. NextAuth>
- 部署: <e.g. 本地 production server / 远程服务器 SSH>

## Quick Start

\`\`\`bash
# 1. 起 MySQL (本地无 MySQL 时跑这条)
docker run -d --name <app>-mysql -p 3306:3306 \\
  -e MYSQL_ROOT_PASSWORD=devpass \\
  -e MYSQL_DATABASE=<app> mysql:8

# 2. 安装依赖
npm install

# 3. 初始化 DB
cp .env.example .env  # 必要时改 DATABASE_URL
npx prisma migrate dev
npx prisma db seed

# 4. 启动 dev server
npm run dev
# → http://localhost:3000
\`\`\`

默认账号(seed 灌入): `admin@example.com` / `admin123`

## Project Layout

\`\`\`
src/
├── app/          # Next.js App Router pages
├── components/   # 共享 React 组件
├── lib/          # 业务逻辑 + DB 客户端
└── api/          # API routes
prisma/
└── schema.prisma # DB schema (见 docs/DATA-MODEL.md)
docs/             # 接手者必读
\`\`\`

## 接手必读

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 模块边界、系统拓扑、横切规则
- [docs/DATA-MODEL.md](docs/DATA-MODEL.md) — 数据表 / 字段字典
- [docs/CONVENTIONS.md](docs/CONVENTIONS.md) — 提交 / 命名 / 目录约定
- [docs/decisions/](docs/decisions/) — 关键技术决策(ADR)

## Scripts

| 命令 | 用途 |
|---|---|
| `npm run dev` | 启动 dev server |
| `npm run build` | 生产构建 |
| `npm test` | 跑单元 + 集成测试 |
| `npm run lint` | ESLint + typecheck |
| `npx prisma studio` | DB GUI |

## Deployment

- 本地 production server: `npm run build && npm run start`, http://localhost:3000
- 远程服务器(可选): SSH 部署, 见 [08b-ssh-deploy.md](#) 或项目自定义脚本
- Rollback: 远端通过 pm2 切换上一版本, 或重跑 `git checkout <prev-tag> && npm run build`

详见 [docs/runbook.md](docs/runbook.md)(如有)。

## License

<根据项目选, 没有就省略>
```

---

## docs/ARCHITECTURE.md 模板

从 `.opc/implementation-plan/architecture.md` 萃取, 去过程词:

```markdown
# Architecture

## System Context

<一段文字: 这个系统是什么、谁用、跟外部系统怎么交互>

## Containers / Modules

<C4 风格 container 图或表格. 用真实路径>

| 模块 | 路径 | 职责 |
|---|---|---|
| Web | `src/app/` | Next.js App Router 页面 |
| API | `src/app/api/` | REST endpoints |
| Domain | `src/lib/<domain>/` | 业务逻辑 |
| DB | `prisma/` | schema + migrations |

## 横切规则

- **鉴权**: NextAuth session, 见 `src/lib/auth.ts`
- **权限**: <RBAC 模型说明>
- **日志**: <方案说明>
- **错误处理**: <方案说明>
- **可访问性**: <WCAG 等级>
- **性能预算**: <LCP / FID / CLS 目标>
- **国际化**: <i18n 方案 + 默认语言>

## 数据流(关键路径)

<一两个核心 user flow 的数据流图>

## 边界约束

- 禁止改动: <legacy 接口 / 第三方契约>
- 复用点: <共享 lib / hooks / utils>

## 部署形态

- 环境: dev / preview / staging / production
- 部署平台: <Vercel / Netlify / 自有>
- 关键 env vars: <见 `.env.example`>
```

---

## docs/DATA-MODEL.md 模板

```markdown
# Data Model

DB schema 单一真相源是 \`prisma/schema.prisma\`(或 Drizzle schema 对应文件)。本文档是给接手者读的数据字典视图。

## ER 概览

<文字描述或简单图: 表之间的关系, 主键 / 外键链路>

## 表清单

### users

| 字段 | 类型 | 约束 | 含义 |
|---|---|---|---|
| id | String | PK | UUID |
| email | String | UNIQUE, NOT NULL | 登录邮箱 |
| password_hash | String | NOT NULL | bcrypt 哈希 |
| created_at | DateTime | DEFAULT now() | |
| role | enum(admin\|user) | DEFAULT 'user' | RBAC 角色 |

索引: `email`(UNIQUE)

### <下一张表>

...

## 关系

- `users` 1 — N `orders`(`orders.user_id`)
- `orders` N — M `products`(via `order_items`)

## 枚举 / 状态机

\`\`\`
order.status: pending → paid → shipped → delivered
                       ↓
                    refunded
\`\`\`

## 迁移注意

- 加 NOT NULL 列必须给 default 或先 ALTER 加 nullable 再 backfill
- 删列前先发废弃日志一个 release
- 索引变更走 `prisma migrate dev --create-only`, 人工 review SQL
```

---

## docs/CONVENTIONS.md 模板

```markdown
# Conventions

## Commit Style

跟随项目既有风格嗅探 \`git log --oneline -20\`. 当前项目用 <conventional commits / 中文自由格式 / ticket 前缀>。

模板:
\`\`\`
<type>(<scope>): <一句 what>

<可选: 为什么这么做, 哪些副作用>
\`\`\`

- type: feat / fix / refactor / chore / docs / test / build / ci / perf / style
- 一个 commit 一件事, 不要混着提
- message 写 why(diff 已经是 what)
- 实验性大重构前先 commit 安全点

## 分支策略

- `main` — 生产分支, 自动部署 production
- 功能分支: `feat/<short-name>` / `fix/<short-name>`
- PR 前必跑: lint + typecheck + test + build

## 目录约定

- 共享代码: `src/lib/`
- 共享 React 组件: `src/components/`
- 业务模块: `src/lib/<domain>/`
- 测试文件: `*.test.ts` 跟源码同目录, 或 `tests/` 镜像

## 代码风格

- 跟随 ESLint + Prettier 配置, 不手动改格式
- TypeScript strict 模式
- 命名: camelCase 变量 / PascalCase 组件类 / SCREAMING_SNAKE 常量

## 测试约束

- 新业务逻辑 / API 路由 / 状态机 — 先写失败测试再实现(TDD)
- 修 bug — 先写复现测试, 再修
- UI 关键流程 — Playwright e2e 覆盖

## 不允许的退化路径

- in-memory store / typed mock 当生产数据
- HTTP 200 / 构建成功就说"完成"
- 跳过浏览器验证
- 跳过 lint / typecheck 失败
```

---

## docs/decisions/ 处理

`.opc/implementation-plan/decisions/ADR-XXXX-*.md` 直接 `git mv` 到 `docs/decisions/` (而不是复制), 然后:

1. 写 `docs/decisions/README.md` 索引所有 ADR
2. 删 `.opc/implementation-plan/decisions/`(已经挪走)
3. 在 `docs/ARCHITECTURE.md` 里引用相关 ADR

ADR 格式保持不变(见 [06a-implementation-plan.md#adr-规则](06a-implementation-plan.md#adr-规则))。

---

## 实现完成门槛集成

`implementation` 阶段 mark done 前, 跑:

```bash
python3 <skill-dir>/scripts/mandatory/handoff-lint.py \
  --file .opc/implementation/last-handoff.md \
  --phase implementation
```

lint 检查(除原有项外, 新增):

- ✓ `README.md` 存在且 < 300 行(超过说明内容应该挪到 docs/)
- ✓ `docs/ARCHITECTURE.md` 存在
- ✓ `docs/DATA-MODEL.md` 存在(或项目无 DB 时标 `skipped`)
- ✓ `docs/CONVENTIONS.md` 存在
- ✓ `docs/decisions/` 目录存在(或本项目无 ADR 时标 `skipped`)
- ⚠️ `AGENTS.md` / `CLAUDE.md` / `.cursorrules` 新出现且**非用户授权** → fail

跳过场景必须显式标注:

```bash
python3 <skill-dir>/scripts/mandatory/opc-task-state.py mark implementation done \
  --artifact "src/" \
  --evidence "..." \
  --note "project-docs: skipped — 极小修改, 仅改 lib/foo.ts 一处 bug" \
  --next-action "进入 verification"
```

未授权出现工具方言文件 → 在收尾里说明:

```text
[已完成]
- 实现完成, 长期文档已产出

[证据]
- README.md, docs/ARCHITECTURE.md, docs/DATA-MODEL.md, docs/CONVENTIONS.md, docs/decisions/

[继续下一阶段]
- 进入 verification
```

---

## 反模式

- ❌ 把 `.opc/implementation-plan/architecture.md` 直接 `cp` 成 `docs/ARCHITECTURE.md` — 过程词混入
- ❌ 不产出 README.md, 只在 `.opc/` 下交付 — 接手者不知道入口
- ❌ 自动写 `AGENTS.md` / `CLAUDE.md` / `.cursorrules` — 污染项目, 越界
- ❌ 数据字典只写在 ADR 里, 不挪到 `docs/DATA-MODEL.md` — 散落难找
- ❌ ADR 留在 `.opc/implementation-plan/decisions/`, 不挪到 `docs/decisions/` — 接手者看不到
- ❌ 把 docs/ 写成 100 个文件的迷宫 — 应该精简, 看 `必产出清单` 5 项就够
- ❌ 跳过 README / docs/ 但不在台账标 `skipped` — 静默退化
