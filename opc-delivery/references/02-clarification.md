# 02 — 澄清与自治补齐

不懂时不要假设, 也不要把内部阶段卡变成用户必须消费的流程。OPC 的澄清模型: **成品驱动 + 疑点触发确认**。

## 何时读

- 进入定义阶段(requirements / solution / ui-design / implementation-plan)
- 进入执行阶段发现缺前置(脚手架 / 后端 / DB / API / 测试)
- 不确定要不要打断用户拍板时

跳过场景: 已经在 slice 内推进, 没有新出现的高影响疑点。

## 目录

- [核心心智](#核心心智)
- [必问 vs 不问 白名单](#必问-vs-不问-白名单)
- [自治补齐矩阵](#自治补齐矩阵)
- [Git 与后端启动规则](#git-与后端启动规则)
- [宿主原生交互](#宿主原生交互)
- [内部记录(确认卡 + discussion log)](#内部记录确认卡--discussion-log)
- [用户可见输出](#用户可见输出)
- [OPC Pattern Card 与阶段门禁](#opc-pattern-card-与阶段门禁)
- [反模式](#反模式)

---

## 核心心智

**错误模型**:

```text
每阶段给用户一张卡 → 等用户回 → 再给下一张卡 → 用户被流程拖住
```

**正确模型**:

```text
用户给目标
  → AI 内部拆范围、默认值、风险
  → 没有高影响疑点: 直接推进成品
  → 有高影响疑点: 打开原生选择交互
  → 用户提交后继续推进
  → 产出 PRD / 方案 / 代码 / 验证 / 部署证据
```

内部阶段卡和确认卡作用: 保存当前理解、默认假设、用户提交结果和下一步; 支持断线恢复; 让 `handoff-lint.py`、`opc-task-state.py` 和 eval 能验证行为。**不把"每阶段至少一轮"强加给用户**。

执行阶段(implementation / verification / deployment / calibration)默认**自治推进**, 不在 slice/模块/阶段之间问"是否继续"。只在硬阻塞或高风险副作用前提问。

---

## 必问 vs 不问 白名单

### ✅ 必须问(只有这些场景)

| 类目 | 示例 | 为什么高影响 |
|---|---|---|
| 任务最开始 | 范围 / 目标 / 业务身份模糊 | 决定整轮交付方向 |
| 数据真实性 | 真实接入 / 演示数据 / 用户上传 CSV | 决定是否需要后端、数据库和验收口径 |
| 范围承诺 | "企业级"/"完整"/"生产级"/"智能"/"后台"具体含义 | 直接改变模块数量和验收标准 |
| 权限与合规 | RBAC、SSO、审计、客户数据、SLA、品牌硬约束 | 涉及安全、法务和信任 |
| 部署路径 | 本地预览 / Vercel / Cloudflare / 自有服务器 / production | 决定凭证、成本和回滚 |
| 账号与密钥 | API key、token、secret、私有 URL、服务器地址 | 代理不能代造或写入仓库 |
| 副作用 | 远端 push、覆盖画布、覆盖服务器/数据库、破坏性迁移 | 不可逆或影响协作者 |
| 付费资源 | 采购、开通云服务、升配 | 涉及真实成本 |

用户说"你决定", 高影响项仍要给推荐默认和理由; 宿主支持原生交互时打开确认框。用户明确授权默认项后继续。

### ❌ 绝对不问(自治处理)

- **下一个 slice 做什么 / 是否继续 / 要不要进入下一阶段** — 这是 P0 反模式, 破坏自治推进
- 文件名 / 目录结构 / 内部路由 / helper 拆法
- 小依赖(图标库、日期格式化库、状态管理库)
- 本地脚手架、`.gitignore`、`.env.example`、测试命令
- mock seed 具体值、内部 enum 取值、单文件代码组织
- 可逆默认值(分页大小、默认排序、按钮文案微调)
- typecheck / lint 失败如何修
- 部署到 Vercel 还是 Netlify(除非用户素材已暗示某一个)
- 是否要写测试 / 要不要 commit
- 已被用户、PRD、方案或现有代码明确锁定的事项

不要为了显得严谨把这些推回给用户。

---

## 自治补齐矩阵

把"缺少前置条件"当成交付工作的一部分处理。完整 OPC 里, 代理默认自己补齐本地工程、版本控制、**后端 + DB**、验证和预览基础设施; 只有真正需要用户输入、授权或承担风险时才暂停。

| 缺什么 | 默认动作 | 何时问用户 |
|---|---|---|
| Git 仓库 | 当前业务工作区 `git init` + `.gitignore`, 按工程师直觉自治 commit(信号驱动, 一个 commit 一件事) | 已有父级仓库 / 目录所有权不清 / 需推远端 |
| 前端工程 | 按方案或默认栈起脚手架(Next.js / Vite / Astro) | 现有项目强约束冲突 |
| **Node 后端** | 起后端(Next.js API routes / Hono / Fastify / Express) + health endpoint | 后端栈影响长期维护且未明确 |
| **DB + ORM** | `prisma init --datasource-provider sqlite`(开发) → Postgres(部署); 写 `schema.prisma` + `migrate dev` | DB 未明确且影响部署/迁移 |
| **API 路由** | 按 PRD/方案 endpoint 列表创建 handlers, 每个至少 happy path + 一个错误路径 | endpoint 数量影响范围且无法推断 |
| **Seed 数据** | `prisma/seed.ts`, 灌入开发数据让首次跑就有内容 | 数据需要真实业务样本 |
| 鉴权 | 按方案接入(NextAuth / Lucia / 自写 JWT) | 需第三方 IdP 凭证 |
| 设计风格 | 按 UI 方案; 无强约束默认 shadcn/Tailwind | 品牌/风格显著影响验收且无法推断 |
| **演示数据** | 不默认创建 typed mock; 只有用户明确选演示版才用 | 用户没明确选演示而数据真实性影响交付 |
| 测试能力 | 新项目补最小 test/build/browser; 现有项目复用已有命令 | 加依赖会冲突 / 测试环境需凭证 |
| CI/CD | 没有配置时补最小 build/test workflow | 需远端仓库 / 组织权限 / 付费 runner |
| 预览上线 | 按已明确部署目标执行; 缺凭证不降级 | 部署目标不明确或缺凭证 |
| `.env` 模板 | 自动生成 `.env.example` 进版本; `.env` 进 `.gitignore` | 真实 secret 走宿主 user-scope 配置 |
| 文档/台账 | 自动写 `.opc/` 阶段产物、`discussion.md`、状态记录 | 不问 |

**自治补齐 ≠ 跳过高影响疑点确认**。后端栈、DB 选型、部署目标、数据来源若仍不明确且会改变成品, 先用原生交互处理; 已有 PRD / 方案 / 现有项目 / 安全默认可推断, 直接执行并记录。

---

## Git 与后端启动规则

### Git

- 当前目录没 `.git/` 且不在父级仓库内 → 完整 OPC 默认 `git init`
- 同时补 `.gitignore`: `node_modules`、构建产物、`.env*`(不含 `.env.example`)、日志、缓存、本地 DB(`*.db`、`*.sqlite*`)、Prisma 生成物
- 本地 commit 可作为阶段证据; commit 颗粒度和 message 风格见 [06b-implementation.md#commit-节奏](06b-implementation.md#commit-节奏)(信号驱动, 一个 commit 一件事, 跟随项目既有风格)
- 没有 remote 时**不要**要求用户先建 GitHub 仓库; 继续本地实现、验证和 preview
- 远端 push、创建远端 repo、修改受保护分支 = 确认门

### 后端 + DB

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

**独立 Hono 后端**: `npm i hono @hono/node-server` + tsx, server/index.ts 注册路由, prisma 同上。

DB 文件路径默认 `prisma/dev.db`(SQLite) 或 `DATABASE_URL` env(Postgres)。**绝不把 DB 文件提交进 Git**。

---

## 宿主原生交互

需要用户拍板时, 优先用宿主真实结构化交互:

1. Codex App 的 `request_user_input`
2. Claude Code / 其它 runner 暴露的 confirm/select/prompt
3. OMX question bridge 或等价 native UI
4. 上述都不可用 → 文本降级为 A/B/C/D

使用原生交互时:

- 每轮 1-3 个问题, 每题 2-3 个互斥选项
- 推荐项放第一并标 `(Recommended)` 或宿主等价标记
- 保留 Other / 自定义入口
- 普通聊天文本只写"已打开原生交互、默认推荐、等你提交后继续", 不复制长问卷

文本降级格式:

```text
[需要你拍板]
- A. <推荐默认> — <一句理由>
- B. <备选> — <一句影响>
- C. <备选> — <一句影响>
- D. 自定义 / type something
- 默认 = A

[下一步]
等你回 A/B/C/D 后继续。
```

降级时必须说明原因: 当前宿主没有可用结构化交互、当前模式不允许调用, 或运行面没有 question bridge。

---

## 内部记录(确认卡 + discussion log)

需要澄清时内部记录:

```text
OPC Internal ConfirmCard · <phase> · <yyyy-MM-dd HH:mm>

[当前理解]
- 业务目标:
- 用户 framing 翻译:
- 已锁定事实:

[我默认处理]
- 低风险默认:
- 理由:

[需要用户拍板]
- 问题:
- 推荐:
- 备选:
- 交互面: request_user_input / confirm-select / 文本降级
- 用户提交:

[收敛判断]
- 可继续:
- 下一步:
```

写入 `.opc/<phase>/discussion.md`, **不必完整贴给用户**。

每个定义阶段维护 `.opc/<phase>/discussion.md`, 追加模式:

```markdown
# <phase> Discussion Log

## Entry <N> — <yyyy-MM-dd HH:mm UTC>

### 来源
- 用户输入 / 现有 PRD / 代码 / 接口文档 / 截图

### 内部理解
- 业务目标 / 用户 framing 翻译 / 已锁定事实 / 低风险默认及理由

### 高影响不确定
- 是否存在 / 需要拍板的问题 / 交互面 / 推荐默认 / 用户提交结果

### 决策结果
- 确定 / 自治处理 / 仍卡住

### 下一步
- 写 PRD / 写方案 / 进入实现 / 等用户提交 / 卡住缺 X
```

PRD、方案、UI Brief 只写收敛结论, 不塞长讨论纪要。

---

## 用户可见输出

进度类问题默认结果摘要, 不展示内部阶段表:

```text
目标: <用户目标>
已交付: <普通话术摘要>
正在推进: <普通话术摘要>
需要你做什么: <无需操作 / 等选择 / 卡住缺 X>
接下来: <下一步动作>
```

无高影响疑点时, 用户可见输出**直接推进**:

```text
[已完成]
- 我已从你的需求里抽出目标、角色、核心流程和验收口径。

[证据]
- PRD: .opc/requirements/prd.md
- 状态台账: .opc/state/opc-task.json

[继续下一阶段]
- 我现在进入方案设计并补齐接口、数据和部署计划。
```

有高影响疑点时, 保持短:

```text
[已完成]
- 我已把"企业级用户中心"拆成账号、登录、角色、权限、审计和导出几类范围。

[证据]
- 内部澄清记录: .opc/requirements/discussion.md

[需要你拍板]
- 已打开原生选择框: 权限深度
- 推荐默认 = 基础 RBAC + 审计日志, 因为它覆盖企业后台最常见验收。

[下一步]
等你在原生交互提交后, 我把结果写入 PRD 并继续方案设计。
```

---

## OPC Pattern Card 与阶段门禁

完整 OPC 任务在内部阶段卡之后补一张轻量 Pattern Card, 写入 `.opc/state/opc-task.json` 或阶段文档"决策记录"。这是**内部执行纪律**, 不是用户侧固定流程:

```text
OPC Pattern Card
- Discovery model: JTBD / MoSCoW / existing PRD / golden replay
- Design model: 2-3 approaches / single constrained path / existing design
- Planning packet: discovery / foundation / delivery / verification / follow-through
- Validation gate: local / PR / release / scheduled
- Risk checks: premortem / red-team / systematic debugging / none with reason
- Evidence to claim done: tests / browser screenshot / diff / deployment health / AAR
```

### 各阶段门禁要点

**需求**: 写 Core Job `当 <场景>，<角色> 想要 <能力>，以便 <业务结果>`; MoSCoW 拆范围, `Must` 不吞全部, `Won't` 明确防蔓延; 记录替代方案; 只问 blocker, 一次一个关键选择题。

**方案**: ≥2-3 个方案方向(除非已强约束); 每个方向写取舍(交付速度、可维护性、设计质量、验证成本、部署风险); 自我审查覆盖 Must、占位符、矛盾假设; 拆 planning packet(discovery / foundation / delivery / verification / follow-through)。

**UI / 实现规划 / 实现**: 每个核心功能写用户结果句 `这帮助 <用户> 通过 <机制> 达成 <结果>`; 实现前写 `.opc/implementation-plan/index.md` + 当前用户价值 slice; 交互组件覆盖 default / hover / focus / loading / empty / error / success / disabled 状态; 行为可测先补失败测试; bug 走 systematic debugging(复现 → 读错误 → 查最近变化 → 单一假设 → 最小验证 → 修根因)。

**验证**: 命名 gate truth(local / PR / release / scheduled); 按风险选最小可信层(unit/component / integration / contract / smoke/E2E / manual); 自动化扫描是输入不是完成; evidence-before-completion。

**部署**: production 前必须有 release packet(artifact / 环境 / promotion / rollout / verification / rollback); premortem 列 top risks / early warning / prevention / mitigation / owner; 高风险发布做 red-team(权限、数据、secrets、回滚不可逆、依赖供应商、监控盲区); 写 stop conditions。

**校准**: AAR 闭环(what expected / what happened / why different / what changes); 差距分类: skill 通用规则、项目规则、脚本检查、eval; 能自动化的优先进 scripts 或 evals。

---

## 反模式

**澄清类**:
- 把阶段卡或确认卡当成用户侧固定流程
- 默认展示"阶段进度(OPC 8 阶段)"表、box-drawing 表格、raw phase IDs
- 每个定义阶段都强制至少一轮用户确认
- 需求清楚时仍停下问"是否继续"
- 低风险工程细节让用户拍板
- 高影响不确定不问, 私自猜完再写进 PRD
- 当前宿主能打开选择框, 仍要求用户手敲 A/B/C
- 文本降级不给默认项或自定义入口
- 一轮塞 5 个以上问题
- 收尾只列"剩余风险", 没有行动、默认、阻塞分类或下一步

**自治补齐类**:
- ❌ "用户没说要后端, 我先做前端 + mock" — 后端是默认全栈交付的一部分
- ❌ "起后端太慢, 我用 in-memory store 顶一下" — 等于 mock, 不持久, 不算实现
- ❌ "Server Component 直接 import 一个静态 JSON" — mock 的另一种写法
- ❌ "没有 Git 仓库, 你先创建好我再继续"
- ❌ "没有 package.json, 所以不能实现"
- ❌ "没有部署服务器, 本轮只能结束在设计"
- ❌ "等你决定风格后我再开始, 当前先到这里"(没强约束就用默认; 有强约束就开原生选择)
- ❌ "Vercel token 缺失, 我退回 next start"(应说明卡住缺凭证或让用户选部署路径)
