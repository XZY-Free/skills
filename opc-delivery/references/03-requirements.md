# 03 — 需求阶段

把口语化、模糊、不懂业务边界的输入, 变成能驱动设计、实现和验收的 PRD。

需求阶段**不是**"必须先给用户一轮确认卡"。正确节奏: 先抽事实, 内部记录默认假设和缺口; 只有高影响不确定才打开原生选择交互。信息足够时直接写 `.opc/requirements/prd.md`, 自动进 solution 阶段。

## 何时读

- 进入 requirements 阶段
- 写 PRD 前补齐 JTBD / MoSCoW
- UI 文案语种判断 / 复杂平台覆盖单元拆解

## 目录

- [输入检查](#输入检查)
- [高影响疑点判断](#高影响疑点判断)
- [用户 framing 翻译](#用户-framing-翻译)
- [JTBD + MoSCoW 门禁](#jtbd--moscow-门禁)
- [PRD 最小结构](#prd-最小结构)
- [UI 文案语种契约](#ui-文案语种契约)
- [复杂产品覆盖模板](#复杂产品覆盖模板)
- [收敛与完成判断](#收敛与完成判断)

---

## 输入检查

优先从用户原话、会议纪要、已上线需求、接口文档、截图、现有代码和业务规则中**抽事实**。先抽再问。

承诺性词("企业级 / 完整 / 专业 / 生产级 / 智能 / 后台 / 小需求") 必须翻译成具体清单。翻译结果会改变范围或成本 → 原生选择交互; 只是记录默认理解 → 写进 PRD 和 discussion log 后继续。

---

## 高影响疑点判断

**必须确认**:

- 数据来源: 真实接入、演示数据、用户上传或第三方 API
- 权限深度: 账号、角色、RBAC、SSO、审计、多租户
- 范围裁剪: "企业级 / 完整 / 生产级"包含或不包含哪些模块
- 合规/品牌: 客户数据、法务、品牌强约束
- 验收边界: 是否必须上线、是否允许仅预览、是否涉及真实用户
- 用户给出多个互斥目标且无法同时满足

**不用确认**(参考 02-clarification.md 的不问白名单):

- 文档标题、文件名、目录结构
- 小依赖、helper、内部路由
- 可逆默认(分页大小、默认排序)
- 已由用户原话或现有资料明确给出的范围

需要确认 → 按 [02-clarification.md](02-clarification.md#宿主原生交互) 打开宿主原生选择交互。

---

## 用户 framing 翻译

把抽象词翻成可验收范围:

| 用户原话 | 翻译清单 |
|---|---|
| 企业级 | 是否含登录、RBAC、SSO、审计日志、多租户、数据导出、SLA、合规 |
| 完整 / 完整上线 | 是否端到端可用、是否真实数据、是否可部署、是否含回滚 |
| 专业级 / 高级 | 视觉质感、功能完整度、工程质量还是运营后台能力 |
| 生产级 / production-ready | preview/staging 还是 production; 是否有真实用户访问 |
| 智能 / AI | 真接 LLM/Embedding API 还是演示响应; 哪家模型; 成本限制 |
| 数据看板 / 后台 | 真实数据源、角色、实时性、权限、导入导出、审计 |
| 小需求 | 单页单接口, 还是用户口中的"小"但涉及多模块 |

示例:

```text
"企业级用户中心"
默认理解:
- 含: 登录、账号列表、角色、基础 RBAC、审计日志、数据导出
- 暂不含: SSO、多租户、计费、复杂审批
- 需要拍板: 权限深度是"基础 RBAC"还是"SSO + 多租户"
```

当前宿主支持 `request_user_input` → 权限深度用选择框确认; 不要求用户手敲 A/B/C。

---

## JTBD + MoSCoW 门禁

PRD 必须包含:

- **Core Job**: `当 <场景>, <角色> 想要 <能力>, 以便 <业务结果>`
- Functional / Emotional / Social job
- Compensating behavior: 用户现在用什么土办法
- **MoSCoW**: Must / Should / Could / Won't

MoSCoW 由 AI 先草拟, 但**高影响裁剪必须暴露**:

- 裁剪会明显改变交付物 → 选择交互确认
- 只是低风险默认 → PRD 的 Won't 和 discussion log 写"我已默认处理"

---

## PRD 最小结构

写 `.opc/requirements/prd.md`(除非项目已有规范路径)。PRD 是收敛后最终稿, 讨论纪要单独留在 `.opc/requirements/discussion.md`。

```markdown
# <需求名称> PRD

> 状态: requirements 阶段产出
> 讨论日志: .opc/requirements/discussion.md
> 交互说明: 高影响不确定已通过原生选择交互 / 文本降级 / 现有资料解决

## 背景和目标
- 背景 / 目标 / 非目标 / 成功指标

## 用户和场景
- 角色 / 使用场景 / 触发条件

## JTBD
- Core Job
- Functional jobs
- Emotional / social jobs
- Compensating behavior

## 范围
- Must / Should / Could / Won't / 依赖

## 用户故事
- 作为 <角色>, 我想 <能力>, 以便 <价值>

## 核心流程
1. 入口
2. 操作
3. 成功结果
4. 异常 / 空态 / 权限态

## 数据和接口
- 数据来源: (真实接入 / 演示数据 / 用户上传 / 第三方 API)
- 关键字段
- 接口/后端依赖: (Node 后端默认; 接什么外部服务)

## UI/交互要求
- 页面/模块 / 状态 / 文案语种 / 可访问性

## 非功能要求
- 性能 / 安全/权限 / 兼容性 / 日志/审计

## 验收标准
- Given/When/Then
- 必须通过的测试/截图/部署检查

## Open Questions
- [ ] <问题> | 影响: <影响> | 当前处理: 自治默认 / 需要拍板 / 卡住缺 X

## 决策记录
- <日期>: <决策> | 原因: <依据, 可引用 discussion.md>
```

---

## UI 文案语种契约

约束 MasterGo 设计稿、Codify HTML 和 Magic 还原代码里的页面 UI 文案语种。**不约束助手回复语言**; 助手回复仍按宿主和用户语言习惯处理。

### 判断顺序

1. 用户明确指定的语言
2. 用户提供的截图、已有设计稿、素材或品牌规范里的主要语言
3. 当前对话的主要语言
4. 目标用户 / 业务区域能明确推断的语言

信号冲突或低置信 → 选择题澄清。不要因为"企业级、SaaS、Dashboard、AgentOps"等词就默认英文 UI。

### 中文场景默认

用户全程中文、截图为中文、或需求面向中文团队时:

- 默认简体中文 UI 文案
- 导航、标题、按钮、表头、筛选项、状态标签、空态、错误态、审批、审计、监控、日志和提示都应是中文
- 品牌名、产品名、缩写、协议名和常用技术名词可保留原文: MasterGo、Codify、AI、Agent、API、MCP、D2C、SLA、SSO、RBAC、AgentOps
- 中英混排要自然, 不要把整页变成英文后台模板

### 选择题模板

```
我先确认页面 UI 文案语种:
A. 跟随当前聊天语言(推荐): 简体中文, 保留必要英文技术名词
B. 中文 UI + 更多英文技术标签: 适合面向研发 / AgentOps 团队
C. English UI: 全英文
D. 自定义 / type something
```

用户说"你决定 / 直接做", 当前聊天是中文 → 默认 A 继续。

### 写入 Codify requirement

调用 `design()` / `agent_create_page()` / 生成 Tailwind HTML 前, 把语种写入 requirement, **不要只在口头回复说**。

短句模板:

```
UI copy language: Simplified Chinese.
Keep product names, brand names, and technical acronyms as-is:
MasterGo, Codify, AI, Agent, API, MCP, D2C, SLA, SSO, RBAC, AgentOps.
All navigation, titles, buttons, table headers, states, empty states, errors,
approval/audit/monitoring copy, and log snippets should follow this language.
```

### 推送前 copy lint

```bash
python3 <skill-dir>/scripts/helpers/codify-copy-lint.py <html-file> \
  --expected simplified-chinese --mode strict
```

模式: `strict`(默认, 大面积未授权英文 UI 直接阻断) / `warning`(还原已有英文稿或混排, warning 写进验证记录)。误伤用 `--allow Term` 追加白名单, **不要为了让 lint 通过而把整页改成英文**。

### 修改和还原场景

- 局部修改 UI 文案 → 沿用目标画布/页面当前主要语言
- Magic 还原代码 → 保留原设计稿文案语言, 不要自动翻译
- 接 API 或替换假数据 → 字段名、枚举值按接口原文; 界面静态文案按本契约
- 设计稿更新流 → 新旧版本语种不一致 = diff 风险点, 先确认是否有意改变

### 验证抽查

推送前和 3A 验证至少抽查: 左侧/顶部导航 / 页面主标题和区块标题 / 主要按钮和二级按钮 / 表格列名、筛选项、状态标签 / 空态、错误态、审批提示、审计时间线、监控告警、运行日志。

未获授权的英文 UI 大面积出现 → 不要说设计完成; 回 `agent_update_node` / `agent_replace_node` 或重新生成。

```bash
python3 <skill-dir>/scripts/helpers/verification-state.py record \
  --type design --unit-id <unit-id> \
  --copy-language simplified-chinese \
  --note "UI 文案语种抽查通过"
```

---

## 复杂产品覆盖模板

**只提供覆盖 brief 的候选单元, 不是固定页数清单**。最终范围由用户目标、角色、核心流程和验收口径决定。用户明确选概念代表页 → 只取一个单元, 但必须标注它不是完整产品设计交付。

### 使用原则

- 用户说"你决定 / 直接做"且需求明显复杂 → 优先选"完整稿"或"评审方向稿"
- 不要把复杂平台压成一个 dashboard; 至少覆盖核心流程、详情、配置、治理和关键状态
- 每个设计单元写入 `.codify/state/mastergo-task.json`, 逐个生成、推送、验证
- 设计单元可以是页面、状态、弹窗、抽屉或组件变体, 不必都做成独立页面

### AI 多智能体协作平台

| id | 标题 | 类型 | 说明 |
|---|---|---|---|
| overview | 总览工作台 | page | 运行概览、关键指标、异常、成本、队列和最近任务 |
| orchestration-canvas | 多智能体编排画布 | page | Agent 节点、工具节点、知识库、条件分支、人工审批 |
| run-detail | 运行详情 / trace | page | trace timeline、日志、工具调用、token 成本、失败重试 |
| agent-catalog | Agent 目录与能力配置 | page | Agent 列表、能力、模型、权限、版本、评估 |
| tools-knowledge | 工具 / 知识库 / 连接器管理 | page | API、MCP、文档库、权限和健康状态 |
| governance | 治理 / 审批 / 审计 | page | 风险策略、人工审批、审计时间线、合规记录 |
| settings | 团队 / 权限 / 模型 / 预算设置 | page | RBAC、SSO、模型路由、预算、限额、通知 |
| create-run | 新建运行弹窗 | modal | 目标、输入、Agent 编排模板、审批策略 |
| approval-drawer | 人工审批抽屉 | drawer | 风险摘要、上下文、批准/驳回、审计留痕 |
| failure-empty-loading | 异常 / 空态 / 加载态 | state | 失败恢复、无运行、无权限、加载骨架 |

设计方向: 企业运营型(清晰、密集、低装饰) / AgentOps 观测型(trace、日志、拓扑) / 高管演示型(信息少、对比强、路演风)。

### 客服运营平台

| id | 标题 | 类型 | 说明 |
|---|---|---|---|
| queue | 工单 / 会话队列 | page | SLA、优先级、分派、过滤、批量操作 |
| conversation | 会话详情 | page | 用户画像、对话、内部备注、AI 建议、转接 |
| quality | 质检与复盘 | page | 抽检、评分、违规项、改进建议 |
| knowledge | 知识库 | page | 文档、FAQ、命中率、过期提醒 |
| analytics | 运营报表 | page | 趋势、渠道、满意度、人员绩效 |
| settings | SLA / 团队 / 权限设置 | page | 规则、通知、排班、权限 |

### 后台 / AgentOps 通用状态

不要遗漏:

- 空态: 无数据、无权限、未接入、未订阅组件库
- 加载态: 页面骨架、表格骨架、运行中 trace
- 错误态: 接口失败、权限不足、token 过期、运行失败
- 审批态: 待审、通过、驳回、超时、升级
- 风险态: 高风险工具调用、敏感数据访问、预算超限
- 组件变体: 筛选器、表格、详情面板、批量操作、状态标签、时间线

---

## 收敛与完成判断

可以完成 requirements 的信号:

- 用户 framing 已翻译成具体范围
- 真实数据/演示数据、主要角色、核心流程和成功结果明确
- Must / Should / Won't 能写入 PRD
- 高影响不确定已确认或有明确阻塞记录
- PRD 能驱动方案阶段, 不需要再猜

完成动作:

1. 写 `.opc/requirements/prd.md`
2. 更新 `.opc/requirements/discussion.md`
3. 写 `.opc/requirements/last-handoff.md`
4. 跑 `scripts/mandatory/handoff-lint.py --phase requirements`
5. `opc-task-state.py mark requirements done --artifact .opc/requirements/prd.md --evidence "PRD 覆盖目标、范围、数据和验收标准" --next-action "进入 solution 阶段"`
6. **自动进入 solution 阶段**

用户明确要"轻量 PRD / 我自己写 PRD / 跳过这步" → 记录用户授权、风险和替代证据再继续; 不把跳过伪装成完整需求收敛。
