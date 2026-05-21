# 实现前技术规划

目标: 在写代码之前, 把 PRD、方案、UI 设计、现有代码和部署约束整理成可执行、
可恢复、可分片读取的技术实现总方案和开发计划。`implementation-plan` 是完整
OPC 的硬门禁: 没有实现计划, 不进入 `implementation`。

本文件吸收 C4 分层视图、arc42 架构模板、ADR 单决策记录、Gerrit design docs、
GitLab planning breakdown 和 Skill progressive disclosure 的做法。不要把这些
方法名展示给普通用户; 把它们落成索引、契约、切片、ADR 和验证门禁。

## 目录

- [进入条件](#进入条件)
- [核心原则](#核心原则)
- [目录结构](#目录结构)
- [文件职责](#文件职责)
- [上下文预算计划](#上下文预算计划)
- [并行分配计划](#并行分配计划)
- [上下文读取规则](#上下文读取规则)
- [拆分规则](#拆分规则)
- [Slice 模板](#slice-模板)
- [ADR 规则](#adr-规则)
- [普通用户汇报](#普通用户汇报)
- [完成门禁](#完成门禁)

## 进入条件

- `.opc/requirements/prd.md` 或等价需求 brief 已收敛;
- `.opc/solution/solution-design.md` 已确定方案方向、技术路线、数据和部署约束;
- `.opc/ui/design-brief.md`、MasterGo 画布或等价 UI 说明已可作为实现输入;
- 涉及新 UI、重设计或非像素级还原时, solution 已按 [frontend-design-quality.md](frontend-design-quality.md)
  写出设计质量 brief;
- 已检查现有项目结构、测试命令、接口文档、数据层和部署环境;
- 高影响不确定已处理或进入 `blocked` / `需要用户拍板`。

如果是极小改动且用户明确要求跳过规划, 可以把 `implementation-plan` 标记为
`skipped`, 但必须写明风险和跳过授权。完整 OPC 默认不得跳过。

## 核心原则

- **一个入口**: `.opc/implementation-plan/index.md` 是唯一入口, 后续实现先读它。
- **全局契约集中**: 架构边界、API/DB/权限/环境变量和验证规则只放在全局契约文件,
  不在每个 slice 里重复长段内容。
- **按用户价值切片**: 开发计划按可验证用户链路拆, 不按 `frontend.md` /
  `backend.md` / `database.md` / `tests.md` 机械拆。
- **每片可执行**: 每个 slice 同时包含 UI、API、DB、文件范围、步骤和验收, 读取
  `index + architecture + contracts + verification + 当前 slice + ADR` 后即可实现。
- **设计质量入片**: 新 UI 或非像素级还原的 purpose、tone、differentiation、
  constraints 和 anti-generic guardrails 必须进入 `architecture.md`、`verification.md`
  或当前 slice, 不能只留在 solution。
- **上下文预算优先**: 每个 slice 都要估计当前会话是否能完成实现、验证和 checkpoint;
  超出预算就继续拆 slice, 不靠聊天历史硬撑。
- **并行先识别后派发**: 非平凡项目必须识别可并行 lane。只有依赖清楚、Write Set 不重叠、
  验证责任明确且宿主/上层指令允许时, 才把 lane 分给子代理。
- **决策单独记录**: 高影响技术选择写 ADR, 每份 ADR 只记录一个决策。
- **边实现边校准**: 实现中发现计划不匹配, 先更新 slice 或 ADR, 再继续编码。

## 目录结构

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

小项目也要有轻量计划, 但可以只有 `index.md`、`work-breakdown.md`、
`verification.md` 和 1 个 slice。大项目必须拆出 `architecture.md`、`contracts.md`
和 `decisions/`。

## 文件职责

`index.md` 控制在约 150 行以内:

- 目标和当前实现计划状态;
- 必读顺序;
- 当前上下文预算: green / yellow / red;
- checkpoint 路径: `.opc/implementation/continuation.md`;
- 全局约束摘要;
- slice 列表、依赖关系和推荐实现顺序;
- parallel lanes 摘要;
- 当前 slice 指针;
- 影响全局实现的 ADR 列表;
- 文件拆分和恢复提示。

`architecture.md`:

- C4 风格 context / container / component 摘要;
- 系统边界、模块关系、部署形态;
- 横切规则: 鉴权、权限、日志、错误处理、可访问性、性能预算、国际化、设计质量 brief;
- 现有代码复用点和禁止改动的边界。

`contracts.md`:

- API endpoint、输入/输出 schema、错误码;
- DB schema、关系、索引、迁移约束;
- 权限模型、角色、审计;
- 环境变量、secret、安全存放位置;
- 外部接口、文件、队列、定时任务和数据来源;
- 不可破坏的兼容约束。

`work-breakdown.md`:

- 按用户价值链组织开发计划;
- 每个 slice 的依赖、预计文件范围、验证方式和完成定义;
- 不把一条用户链路拆散到前端、后端、数据库三个互不相干的计划里。

`parallelization.md`:

- dependency graph: 哪些 slice/lane 可并行, 哪些必须串行;
- lane owner: main / subagent-eligible / manual-only;
- Write Set: 每条 lane 可写文件/目录, 必须互不重叠或明确协调点;
- Read Set: 每条 lane 所需最小上下文;
- handoff contract: 子代理返回必须包含 changed paths、tests、risks、next action;
- merge order: 主代理整合顺序和冲突处理;
- context budget: 每条 lane 预估 green/yellow/red 和 checkpoint 时机。

`verification.md`:

- lint、typecheck、unit/integration/e2e/build 命令;
- Browser / Playwright 主链路;
- 设计质量 brief 检查: 桌面/移动截图、状态覆盖、文案语种、无 generic AI aesthetics blocker;
- 数据持久化、刷新后状态、权限和错误态检查;
- 部署前检查和回归风险。

## 上下文预算计划

编写 implementation-plan 时, 先评估本会话能做多少:

- `green`: 可完成当前 slice 的代码、测试、浏览器验证和 checkpoint;
- `yellow`: 只做一个小 lane 或一个文件组, 完成后立刻 checkpoint;
- `red`: 不开始新实现, 先写 `.opc/implementation/continuation.md`。

每个 slice 必须写:

- Context Budget: green / yellow / red;
- Checkpoint Trigger: 何时调用 `opc-task-state.py checkpoint`;
- Resume Command: 恢复时先读哪些文件;
- Stop Before: 哪些动作之前必须先 checkpoint, 例如大规模重构、长测试、部署或切换 slice。

如果发现当前 slice 无法在上下文内完成并验证, 先拆成更小的 value slice 或 lane, 再实现。

## 并行分配计划

非平凡项目必须写 `.opc/implementation-plan/parallelization.md`。识别并行时同时考虑上下文预算:

- 可并行: 独立页面/流程、独立 API resource、独立测试补强、文档/验证工件、互不重叠的组件族;
- 不可并行: 同一文件/同一 schema 的竞争修改、跨模块接口未定、迁移顺序未定、需要同一浏览器会话连续操作;
- 子代理适用: lane 目标明确、输入 Read Set 小、Write Set 独立、可用命令验证、失败可局部回滚;
- 主代理保留: 架构决策、共享 schema/API 契约、最终整合、冲突解决、发布和最终证据。

写给子代理的 lane 必须包含: 目标、Read Set、Write Set、禁止改动范围、验证命令、返回格式。
如果当前宿主或上层指令不允许子代理, 仍保留 parallelization plan, 但由主代理按 lane 顺序执行。

## 上下文读取规则

实现任何 slice 前, 固定读取:

```text
1. .opc/implementation-plan/index.md
2. .opc/implementation-plan/architecture.md
3. .opc/implementation-plan/contracts.md
4. .opc/implementation-plan/verification.md
5. .opc/implementation-plan/slices/<current-slice>.md
6. 当前 slice 引用的 ADR
```

禁止默认一次性读取整个 `.opc/implementation-plan/`。只有当当前 slice 的 `Read Set`
明确引用其它文件, 或发现全局契约冲突时, 才继续读取额外文件。

## 拆分规则

- 不允许只写一个巨大 `technical-implementation-plan.md` 或 `development-plan.md`。
- 不允许只按技术层拆成 `frontend.md`、`backend.md`、`database.md`、`tests.md`。
- 单个文件接近 200 行或 12KB 时继续拆, 并更新 `index.md`。
- 每个 slice 覆盖一个可独立验证的用户价值链; 太大时按子流程拆成 `03a-*`、
  `03b-*` 这类连续切片。
- 每个 slice 必须有 `Read Set`; 没有 Read Set 的 slice 不可进入实现。
- 拆分后不得出现孤儿文件; 所有文件都要从 `index.md` 或某个 slice 可达。

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
- Input:
- Output:
- Error:

## Data
- 表/字段/关系:
- seed 或真实数据来源:

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
- Command: python3 <skill-dir>/scripts/opc-task-state.py checkpoint ...
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

适合写 ADR 的事项: ORM、鉴权、部署平台、权限深度、队列/异步、第三方服务、
破坏性迁移、跨模块 API 契约。不为文件命名、普通组件拆分、小 helper 写 ADR。

## 普通用户汇报

这个阶段对普通用户显示为结果摘要, 不贴内部目录树和阶段表:

```text
目标: <用户目标>
已交付: 已整理需求、已确定做法、已完成界面方向
正在推进: 正在把方案拆成可执行开发步骤
需要你做什么: 暂时不需要你操作 / 等你选择 X / 卡住缺 X
接下来: 我会按第一条开发切片开始实现并验证
```

只有用户明确要求技术审计、计划详情或内部状态时, 才展示 `index.md` 和 slice 路径。

## 完成门禁

完成 `implementation-plan` 前必须满足:

- `index.md` 存在且包含读取顺序、slice 索引、依赖顺序和当前推荐实现顺序;
- 全局契约文件覆盖架构、API/DB/权限/环境变量和验证;
- `work-breakdown.md` 按用户价值切片, 不是按技术层机械拆;
- `parallelization.md` 存在, 或轻量任务写明无需并行的原因;
- 每个 slice 有 `Read Set`、Context Budget、Parallelization、UI/API/Data/Files/Steps/Verify/Checkpoint;
- UI 相关 slice 已带入设计质量 brief 或明确说明严格跟随 MasterGo 原稿;
- 高影响决策已写入 `decisions/ADR-xxxx.md`;
- 单文件未超过主动拆分阈值, 或已拆分并更新索引;
- `opc-task-state.py mark implementation-plan done` 的 evidence 指向 `index.md`
  和当前第一条 slice。
