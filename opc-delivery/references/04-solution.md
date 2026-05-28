# 04 — 方案阶段

在 PRD 之后、UI/实现规划之前, 定义"怎么做"。方案要锁定产品路径、架构方向、技术路线、数据和部署约束; 完整开发切片和上下文拆分交给 [06a-implementation-plan.md](06a-implementation-plan.md)。

方案阶段**不固定**要求用户看确认卡。先基于 PRD、现有项目和默认栈形成方案; 只有后端栈、DB、部署目标、权限/合规等高影响项不明确时, 才用原生选择交互。

## 何时读

- 进入 solution 阶段
- 需要锁定后端栈 / DB / 部署目标
- 涉及新 UI / 重设计 / Codify requirement / 非像素级还原实现

跳过场景: 现有项目栈已固定且 PRD 没引出新决策, 直接进 implementation-plan。

## 目录

- [进入条件](#进入条件)
- [高影响方案决策](#高影响方案决策)
- [方案探索门禁](#方案探索门禁)
- [全栈技术默认](#全栈技术默认)
- [方案文档结构](#方案文档结构)
- [产品姿态门禁](#产品姿态门禁)
- [UI 方案门禁](#ui-方案门禁)
- [体验设计质量门禁](#体验设计质量门禁)
- [实现规划门禁](#实现规划门禁)
- [收敛与完成判断](#收敛与完成判断)

---

## 进入条件

- 有 PRD 或足够明确的需求 brief
- 已检查 `.opc/requirements/discussion.md`、现有项目结构、技术栈、组件库、接口文档和部署环境
- 需求阶段的数据来源、核心流程和验收口径足够驱动方案

---

## 高影响方案决策

**需要用户拍板**:

- 后端栈会影响组织长期维护, 且用户已有明确偏好或现有系统约束
- DB 选型会影响部署、成本、迁移或多人协作
- 部署目标未明确, 或会从本地/preview 进入 production
- 权限、审计、SSO、多租户、客户数据范围不明确
- 方案需要采购、外部服务开通、付费 API、远端 push 或破坏性迁移

**不需要用户拍板**:

- 新项目默认 Next.js + Node API + SQLite/Postgres + Prisma/Drizzle
- 目录布局、组件边界、内部 API 路由命名
- 测试命令、本地脚手架、`.env.example`、基础 CI
- 已被 PRD、现有项目或用户原话锁定的技术栈

需要拍板时, 优先 `request_user_input` 或等价原生选择/确认。文本 A/B/C 只在工具不可用时使用。

---

## 方案探索门禁

技术选型已有强约束 → 直接给单条推荐路径并写明放弃原因。无强约束 → 给 2-3 个方案方向, 每个写清:

- 适用场景
- 交付速度
- 可维护性
- UI/体验质量
- 验证和部署风险
- 推荐结论

方案不是想法列表。选定推荐方案后, 把工作切成 **Planning Packet**: discovery、foundation、delivery、verification、follow-through。

---

## 全栈技术默认

OPC 默认全栈交付, 推荐 Node 系轻量栈:

| 层 | 默认 | 适用 | 备选 |
|---|---|---|---|
| 前端 | Next.js 15 (App Router) | SSR、SEO、混合渲染 | React + Vite, Astro |
| 后端 | Next.js API routes | 同仓库 monorepo, 起手最快 | Hono、Fastify、Express |
| DB | SQLite + Prisma → Postgres + Prisma | 本地零配置, 部署可持久化 | MySQL、MongoDB、Supabase/PlanetScale |
| ORM | Prisma | 类型安全、迁移好 | Drizzle、Kysely、手写 SQL |
| 鉴权 | NextAuth(Auth.js) | 主流社交登录、邮箱 | Lucia、自写 JWT、Clerk/Supabase Auth |
| 文件/对象存储 | 本地 `./uploads/` 开发, S3/R2 部署 | 上传/导出场景 | UploadThing、Cloudflare R2、Supabase Storage |
| 队列/异步 | 不默认; 真需要才引 | 长任务、定时任务 | BullMQ + Redis、Inngest、Trigger.dev |
| 验证/表单 | zod + react-hook-form | 类型推导、SSR friendly | Valibot、Yup |

**不默认用** Java/Spring、Python/Django/FastAPI、Go、Rust 作为后端, 除非用户明确指定或现有项目就是。理由: 与前端联调成本、起势速度和部署简单度都不如 Node 系。

---

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
- 选择 / 原因 / 放弃的方案 / 用户拍板记录

## Planning Packet
- Discovery / Foundation / Delivery / Verification / Follow-through

## 信息架构和流程
- 导航/入口 / 页面/模块
- 状态: loading / empty / error / success / permission / audit
- 关键流程

## 产品姿态门禁
- 主姿态 / 子类型 / 反例排除 / 同品类参照
- 首屏主信号(具体可截图描述)
- 能力升降级表(4 层级, 高曝光 ≤5)
- 竞品调研引用: .opc/solution/competitor-survey.md

## UI 策略
- 文案语种 / 设计方向 / 目的 / 受众 / 记忆点
- 反 generic AI aesthetics guardrails
- 组件库策略 / 可访问性 / 动效 / 性能约束
- MasterGo/Codify 是否需要

## 技术方案
- 前端框架 / 后端栈 / DB + ORM / 鉴权方案 / 路由
- 状态管理 / 数据获取 / 表单校验 / 权限 / 日志埋点

## API 和数据
- 接口设计风格: REST / RPC / Server Actions
- DB schema 概要 / 字段映射 / 真实数据来源 / API 溯源报告要求

## 测试策略
- 单元 / 组件集成 / 浏览器截图 / 回归风险

## 部署计划
- 部署目标: 本地 / Vercel / Netlify / Cloudflare / 自有服务器
- 环境变量/secrets / production gate / 回滚方式

## 自我审查
- Must 覆盖 / 占位符/未知项 / 假设冲突 / 可交给 UI/实现/部署的输入
```

---

## 产品姿态门禁

涉及新 UI、新产品或重设计时**必读**, 在 [UI 方案门禁](#ui-方案门禁) 和 [体验设计质量门禁](#体验设计质量门禁) **之前**先做。

解决"功能齐了但像后台 / 内部工具 / engineering demo"的问题。

通用原则和品类骨架:
- [03b-productization.md](03b-productization.md) — 跨场景产品化原则
- [03c-content-products.md](03c-content-products.md) — 内容消费类骨架
- [03d-saas-workspace.md](03d-saas-workspace.md) — SaaS / 工作台类骨架

### 强制 4 张产物

方案阶段必须输出以下 4 张产物。`handoff-lint.py --phase solution` 硬卡: 缺任一张不通过。

| 产物 | 写在哪 | 内容 |
|---|---|---|
| **竞品调研** | `.opc/solution/competitor-survey.md` | 2-3 个同品类成熟产品的姿态 / 一级 nav / 首屏 / 学不学 |
| **产品姿态判断** | solution-design.md 的产品姿态门禁 section | 主姿态 + 子类型 + 反例排除 + 同品类参照 |
| **首屏主信号** | 同上 | 具体可截图画面描述 + 反 dashboard 化承诺 + 同品类对比 |
| **能力升降级表** | 同上 | 4 层级分配 + 高曝光 ≤5 硬卡 + 低/上下文 ≥30% 软 |

### Step 0: 竞品调研

详见 [03b-productization.md#竞品调研](03b-productization.md#竞品调研)。

执行:

1. 基于 PRD 列 2-3 个同品类成熟产品
2. 拿到啥用啥: `curl` / `WebFetch` 拿 marketing 页 → `webapp-testing` 拿未登录态截图(可选) → 知识库 IA 描述兜底
3. 写入 `.opc/solution/competitor-survey.md`, 含表格 + 总结
4. VIP 内部页面不需要; marketing landing + 未登录态足够推断姿态

模板:

```markdown
# 竞品调研 vs <需求>

| 产品 | 姿态推断 | 一级导航 | 首屏主信号 | 学什么 | 不学什么 |
|---|---|---|---|---|---|
| <产品 A> | <姿态> | <一级 nav> | <一句描述> | <一句> | <一句> |

## 总结
- 共性: ...
- 我的选择: 学 <X> 的 <Y>; 不学 <Z>
```

### Step 1: 产品姿态判断

7 类姿态选 1 主 + 可选 1 次; 详见 [03b-productization.md#产品姿态判断](03b-productization.md#产品姿态判断)。

**不允许"什么都是"。** 写反例排除:

```markdown
## 产品姿态
- 主姿态: <内容消费 / SaaS-工作台 / 专业工具 / 学习产品 / 社区 / AI 助手 / 其它>
- 子类型: <reading / dashboard / IDE / chat / ...>
- 次要姿态(可选): <...>
- 理由: 用户主任务是 <...>, 不是 <...>
- 反例排除:
  - 不是 <其它姿态 X>: 因为 <一句>
  - 不是 <其它姿态 Y>: 因为 <一句>
- 同品类参照: <一个具体产品名>
```

### Step 2: 首屏主信号

详见 [03b-productization.md#首屏主信号](03b-productization.md#首屏主信号)。

**写法约束**:

- 必须能描述成"可截图的具体画面", 不能写口号
- 不接受: "突出核心价值 / 展示产品能力 / 让用户感受智能"
- 必须有反 dashboard 化承诺(除非本身是 dashboard 类)
- 必须给同品类对比一句

模板:

```markdown
## 首屏主信号
- 用户首屏第一眼看到:
  - 主区(<X>% 视觉权重): <具体可截图画面>
  - 次区(<Y>%): <具体>
  - 边缘: 导航 / 账号 / 搜索
- 反 dashboard 化承诺: 这个首屏不是 "<N 个 KPI 卡 + M 个能力入口>" 的工程后台样
  (如果就是 dashboard 类, 说明主次指标排序而不是空话)
- 同品类对比: <竞品名> 的首屏是 <一句描述>; 我在 <X> 像, 在 <Y> 故意不同, 原因是 <Z>
```

### Step 3: 能力升降级表

详见 [03b-productization.md#能力升降级](03b-productization.md#能力升降级)。

```markdown
## 能力升降级
| 能力 | 曝光层级 | 出现位置 | 理由 |
|---|---|---|---|
| <A> | 高曝光 | 一级导航 / 首页主区 | <为啥必须高曝光> |
| <B> | 中曝光 | 二级 tab / 详情侧栏 | <...> |
| <C> | 低曝光 | 设置 / 用户菜单 | <...> |
| <D> | 仅上下文 | 行内按钮 / 悬浮 | <...> |

约束:
- 高曝光数 ≤ 5 (硬卡)
- 低曝光 + 仅上下文 比例 ≥ 30% (软约束, 不到必给理由)
```

多角色产品(如客服系统): 分角色给表(详见 [03d-saas-workspace.md#子类型-客服--工单系统](03d-saas-workspace.md#子类型-客服--工单系统))。

### handoff-lint 硬卡

`handoff-lint.py --phase solution` 检查:

1. ✓ `.opc/solution/competitor-survey.md` 存在且非空
2. ✓ `solution-design.md` 含"## 产品姿态门禁" section
3. ✓ section 内含产品姿态、首屏主信号、升降级表 3 部分
4. ✓ 升降级表里"高曝光"行数 ≤ 5
5. ⚠️ 升降级表里"低曝光" + "仅上下文"占比 < 30% 时, 必须有"低占比理由"说明

任一不通过 → 不可 mark solution done。

### 跳过场景

- Magic 纯还原视觉(不引入新产品姿态): 标 `skipped` + 原因 = "纯还原, 沿用原产品姿态"
- 极小修改(改 1-2 个组件): 标 `skipped` + 原因
- 用户明确说"先不要产品化收口": 写明用户授权 + 注明 3C 将相应跳过
- 现有项目沿用既有 IA 仅扩功能: 升降级表必填(评估新能力的层级), 其它可简化

跳过时 3C 也跳过。

---

## UI 方案门禁

进入 MasterGo/Codify 前, 方案必须给出:

- 覆盖范围: 页面、状态、弹窗、抽屉、错误/空态、权限态
- UI 文案语种
- 设计方向, 或用户已通过原生选择交互确认的风格
- 目的、受众、记忆点和反 generic AI aesthetics guardrails
- 组件库策略
- 验证方式

这些字段要映射进 [05a-codify-design.md](05a-codify-design.md#mastergo-设计-gate-card) 的 MasterGo 设计 Gate Card。

---

## 体验设计质量门禁

涉及新 UI、重设计、Codify requirement 或非像素级还原实现时, 必读本节, 并在 `.opc/solution/solution-design.md` 写**设计质量 brief**。

### Design Quality Brief

生成设计或代码前, 在阶段产物里写一段简明但有决断力的 brief:

- **Purpose**: 这个界面支持什么用户任务
- **Audience**: 谁在反复使用 / 在什么压力下使用
- **Tone**: 一个清晰方向 — utilitarian / editorial / playful / luxury / brutalist / industrial / calm analytical / 或其他领域贴合方向
- **Differentiation**: 应该让人记住的一个视觉或交互点
- **Constraints**: 框架、组件库、可访问性、性能、内容密度、品牌、设备目标
- **UI language**: 跟随 [03-requirements.md](03-requirements.md#ui-文案语种契约)

运营工具 → 偏密集、可扫读、克制的界面, 不要 marketing-style hero。游戏/创意工具/活动页/海报/编辑型产物 → 允许更强的视觉表达, 只要匹配 PRD。

### Direction Rules

- **承诺一个连贯的美学视角**; 避免胆怯地混合不相关风格
- **复杂度匹配方向**: maximal 概念需要更丰富的布局和动效; refined 概念需要精确的间距、层级和克制
- **善用 typography**: 项目允许时用差异化字体; 现有设计系统锁字体, 就通过比例、节奏、内容结构和组件组合创造差异
- 使用 CSS variables 或现有 design tokens 表达 color、spacing、radius、shadow、motion
- **避免 generic AI aesthetics**: default SaaS card grids、紫色渐变在白底、随机 glow blobs、重复 rounded cards、平庸 dashboard、stock-style decoration
- 不要在需要速度和清晰度的领域强行创新。高频管理后台应组织有序且快, 不应戏剧化

### Required UI Coverage

设计或实现必须覆盖真实产品状态, 不只是 happy-path 截图:

- default, loading, empty, error, success, disabled, permission, destructive-action 状态
- web 产品要 desktop 和 mobile 响应式
- keyboard focus、点击区域、对比度、reduced motion、可读文本换行
- 真实数据密度、长 label、空数据集、permission-limited 视图
- 所选 UI 语言的核心 microcopy

### MasterGo / Codify Use

准备 MasterGo Gate Card 或 Codify requirement 时, 包含:

- design quality brief: purpose、tone、differentiation、constraints
- visual direction: 具体的 layout、typography、color、density、motion notes
- anti-generic guardrails: 这个领域必须避免什么
- state coverage: 页面、对话框、抽屉、表格、表单、空态/错误/加载
- verification: screenshot review、`get_design_diff`、copy-language check、组件映射

不用本地 HTML、截图或文本 prompt 替代 MasterGo 画布交付。它们只能作为 Codify 写入和验证前的中间产物。

### Implementation Use

实现前端 slice 时:

- 把 design quality brief 翻译成全局样式、tokens、layout primitives、组件 variants
- 保留现有项目约定和组件库, 不要发明无关抽象
- 重复的 UI pattern 保持一致, 但给产品一个有意的难忘细节
- 文本要在 desktop 和 mobile 容器里 fit; 不要依赖 viewport-scaled font sizes
- 动效要有目的、性能好、尊重 reduced motion
- 用真实数据和真实边界判断视觉密度和状态质量

现有项目已有强 design system → 不要用无关美学覆盖。通过 hierarchy、spacing、状态覆盖和一个 domain-specific 的交互/组合选择来增强它。

### Verification Checklist

声明 UI 设计或实现完成前, 收集证据:

- design quality brief 出现在 PRD / solution / implementation-plan / Codify requirement / slice notes
- desktop 和至少一个 mobile viewport 无 overlap / clipping / 空状态 / framework overlay
- typography / color / spacing / density / motion 匹配所选方向
- 所有必需 UI 状态都有表达或显式延后(写明原因)
- UI 文案语种符合契约
- OPC 非 prototype 范围时主流程用真实 API/DB 数据
- screenshots 或 Browser/Playwright 证据支持视觉主张

普通前端页面、独立组件或不属于 OPC/MasterGo 交付 → 不要因为设计质量门禁就触发 `opc-delivery`; 让更合适的前端设计技能处理。

---

## 实现规划门禁

进入 `implementation-plan` 前, 方案必须给出:

- 使用现有项目栈还是新建项目
- 新建项目的目录、脚手架、默认框架
- 是否需要自动初始化 Git、`.gitignore`、测试命令、最小 CI/CD
- 目标路由和主要组件边界
- API endpoint 概要(name + method + 简述)
- DB schema 概要和关键关系
- 数据来源(真实接入路径或演示标识)
- 交互状态和错误处理
- 设计质量 brief 如何进入当前 slice 和浏览器验证
- 测试命令、浏览器验证目标和部署目标
- 哪些高影响技术决策需要 ADR

信息缺失但可由现有项目或默认规则安全推断 → 直接补齐并记录。只有高影响不确定才回到选择交互。

**不要**在 `solution-design.md` 里写完整开发计划或把所有实现细节堆成一个大文档。方案完成后必须进入 `implementation-plan`, 由 `index.md`、全局契约文件、用户价值 slices 和 ADR 承接实现上下文。

---

## 收敛与完成判断

收敛信号:

- 后端栈、DB、部署目标为具体值, 不存在会影响实现的"或"假设
- 鉴权/权限范围已明确或有清楚默认
- 候选方案对比已写或单条路径理由已写
- Planning Packet 已成形
- PRD 的 Must 在方案里都有响应
- 关键风险有处理方式
- 涉及新 UI 时, 产品姿态门禁 4 张产物已就绪(或显式 skipped)
- 未决项已归类为自治处理 / 需要拍板 / 卡住缺 X

完成动作:

1. 写 `.opc/solution/solution-design.md`
2. 更新 `.opc/solution/discussion.md`
3. 写 `.opc/solution/last-handoff.md`
4. 跑 `scripts/mandatory/handoff-lint.py --phase solution`
5. `opc-task-state.py mark solution done --artifact .opc/solution/solution-design.md --evidence "方案覆盖 PRD、技术栈、数据、测试和部署计划" --next-action "进入 ui-design; UI 已收敛后进入 implementation-plan"`
6. **自动进入下一阶段**
