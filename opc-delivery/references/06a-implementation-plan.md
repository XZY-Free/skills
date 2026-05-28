# 06a — 实现前技术规划 (implementation-plan)

在 implementation 之前写 `.opc/implementation-plan/` 全集合, 把怎么做切成可执行的用户价值 slice。实现期默认**自治推进**: 数据来源、后端栈、DB、部署目标应来自方案、现有项目或安全默认值。仍有高影响不确定时先用原生选择交互处理; 低风险细节直接自治。除非遇到 token/凭证/付费/破坏性写入等硬阻塞, **不打断**。

## 何时读

- 进入 implementation-plan 阶段(写 `.opc/implementation-plan/index.md`)
- 准备开始第一个 slice
- 中途发现 slice 边界 / 上下文预算 / ADR 需要调整

跳过场景: 极小改动且用户明确要求跳过规划 — 标 `implementation-plan: skipped` 并写明风险和跳过授权; **完整 OPC 默认不得跳过**。

实现期产物(代码 / 后端 / DB / 验证)见 [06b-implementation.md](06b-implementation.md)。
API 接入和强制溯源汇报见 [06c-api-wiring.md](06c-api-wiring.md)。

---


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

---

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
- IA Map: 自动聚合所有 slice 的 Product Surface, 出 markdown 表(脚本 ia-map-aggregator.py 生成, 不手维护)

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

## Product Surface
- 仅 UI slice 必填; 后端/基建/数据迁移 slice 写 "N/A (backend / infra)" 跳过
- 入口位置: 一级导航 / 首页主区 / 二级 tab / 详情页 / 设置子项 / 上下文操作
- 对应升降级表能力: <能力名> (查 solution-design.md 的能力升降级表)
- 升降级表标的层级: <高曝光 / 中曝光 / 低曝光 / 仅上下文>
- 实际实现层级: <一级 / 首页 / 二级 / ...>
- 一致性: ✓ 一致 / ⚠️ 偏离(原因: <一句>) / ❌ 新能力(升降级表没覆盖, 现场补判断并追加到 solution-design.md)
- 多个能力时, 每个能力一行
- 详见 [03b-productization.md#能力升降级](03b-productization.md#能力升降级)

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
- 每个 slice 有 Read Set、Context Budget、Parallelization、UI/Product Surface/API/Data/Files/Steps/Verify/Checkpoint
- UI 相关 slice 已带入设计质量 brief 或明确说明严格跟随 MasterGo 原稿
- UI slice 的 Product Surface 一致性 = ✓ 或 ⚠️(有理由); ❌ 矛盾态必须先处理(回方案更新升降级表或现场补判断追加到 solution-design.md)
- 高影响决策已写入 `decisions/ADR-xxxx.md`
- 单文件未超过拆分阈值, 或已拆分并更新索引
- `opc-task-state.py mark implementation-plan done` 的 evidence 指向 `index.md` 和当前第一条 slice

---

