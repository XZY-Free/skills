# 需求阶段工作流

目标: 把口语化、模糊、甚至不懂业务边界的输入, 变成能驱动设计、实现和验收的 PRD。

**节奏 = 对话式**。需求阶段不是 AI 一次性写 158 行 PRD; 是几次需求会议。AI 用 ConfirmCard 暴露默认假设、问硬决策, 用户答, AI 更新理解; 引出新问题就再开一轮。详细机制见 [clarification-loop.md](clarification-loop.md)。

完成标志 = 不确定性收敛, 不是文档行数够。收敛后才写 `.opc/requirements/prd.md` 最终稿, mark done, 自动进 solution 阶段。

## 目录

- [输入检查](#输入检查)
- [第 1 轮 ConfirmCard 模板](#第-1-轮-confirmcard-模板)
- [多轮迭代规则](#多轮迭代规则)
- [JTBD + MoSCoW 门禁](#jtbd--moscow-门禁)
- [PRD 最小结构](#prd-最小结构)
- [收敛与完成判断](#收敛与完成判断)

## 输入检查

优先从用户原话、会议纪要、已上线需求、接口文档、截图、现有代码和业务规则中抽取信息。先抽再问。

输入里包含承诺性词("企业级 / 完整 / 专业 / 生产级 / 智能 / 后台 / 小需求") 时, AI 必须在第 1 轮 ConfirmCard 把这些词翻译成具体清单, 不能按字面写 PRD。详见 [clarification-loop.md](clarification-loop.md) 的`用户 framing 解析`。

## 第 1 轮 ConfirmCard 模板

需求阶段的第 1 轮 ConfirmCard 写到聊天里(同时追加到 `.opc/requirements/discussion.md`):

```text
OPC ConfirmCard · requirements · 第 1 轮

[我对需求的初步理解]
- 业务目标 = <从用户原话提炼>
- 核心 framing 翻译 = "<用户原话里的承诺词>" 我理解为:
  • 含: <模块 1>, <模块 2>, ...
  • 不含: <模块 X>, <模块 Y>, ...
  • 拿不准: <模块 Z(?)>

[我替你默认了什么(一句话可改)]
- 数据来源 = 真实接入 + 我自建 Node 后端 + DB (反对就说"用 mock")
- 主角色 = <X 角色, 因为...>
- 核心场景边界 = <从 <入口> 到 <成功结果>>
- 测试策略 = lint + typecheck + build + 浏览器主链路
- 部署形态 = 等 solution 阶段聊(本阶段不必现在定)

[这轮必须先问你才能继续的硬决策]
- 宿主原生结构化交互可用: 打开真实选择框/确认框/选择工具, 优先问 1-3 个最影响范围的问题
- 宿主原生结构化交互不可用: 降级为 A/B/C/D 文本选项, 每题标默认并保留"自定义 / type something"
- 超过 3 个硬决策: 拆到下一轮, 不要一次发长问卷

[我还不确定但不急的, 下一轮再聊]
- 接口/数据细节
- 边界状态/异常态/权限态
- 验收标准的可测量度

[这轮答完后, 我打算这样推进]
- 收敛后写 .opc/requirements/prd.md
- 引出新问题就开第 2 轮; 没新问题就 mark done 进 solution
```

第 1 轮重点: framing 翻译 + 主角色 + 核心成功结果 + 主要默认假设。不要在第 1 轮塞接口/字段/状态机这类细节, 它们应该在 framing 锁定后再聊。

## 多轮迭代规则

第 2、3、N 轮 ConfirmCard 只问"上轮答完后剩下 + 新引出"的问题, 不要重问已确定的事。

什么时候要再开一轮(不要急着收敛):

- 用户答时提了新角色、新模块、新约束、新依赖
- 用户答时质疑了某条默认假设但没给替换值
- AI 写 PRD 草稿前发现某关键流程的成功条件还在猜
- 用户答完"覆盖范围" 但没说清"什么是 Won't"

什么时候可以收敛(走向 PRD):

- framing 翻译用户认可或一一改过
- 主角色、核心流程、关键成功结果都有用户原话或明确认可
- 大模块 Must / Should / Won't 用户都答过
- 没有遗留的"AI 在猜"的字段

## JTBD + MoSCoW 门禁

ConfirmCard 收敛过程中, JTBD 和 MoSCoW 是组织讨论的脚手架:

- Core Job: `当 <场景>, <角色> 想要 <能力>, 以便 <业务结果>` — 第 1 轮 ConfirmCard 必给, 让用户改。
- Functional / Emotional / Social job — 第 1 或第 2 轮 ConfirmCard 列出来让用户认可。
- Compensating behavior — 用户现在用什么土办法; 在 framing 翻译时一起聊。
- MoSCoW: Must / Should / Could / Won't — Must 在第 1 轮就要让用户对范围有反应; Won't **必须明示**(AI 单方面裁掉的大模块必须列在 Won't 段, 不允许埋进 PRD 文档里)。

不允许"AI 替用户写 MoSCoW 然后写进 PRD" 这条路径。MoSCoW 必须在 ConfirmCard 里跟用户对完才写进 PRD 正文。

## PRD 最小结构

收敛后写 `.opc/requirements/prd.md`(除非项目已有规范路径)。PRD 是收敛后的最终稿, 讨论纪要单独留在 `.opc/requirements/discussion.md`, **不要把多轮 Q&A 塞进 PRD 正文**。

```markdown
# <需求名称> PRD

> 状态: requirements 阶段产出
> 讨论日志: .opc/requirements/discussion.md(N 轮已收敛)
> 用户 framing 翻译: 收敛于 第 <N> 轮 ConfirmCard

## 背景和目标
- 背景:
- 目标:
- 非目标:
- 成功指标:

## 用户和场景
- 角色:
- 使用场景:
- 触发条件:

## JTBD
- Core Job:
- Functional jobs:
- Emotional / social jobs:
- Compensating behavior:

## 范围
- Must:
- Should:
- Could:
- Won't: (必须列, 含 AI 在 ConfirmCard 里跟用户对过的所有裁剪)
- 依赖:

## 用户故事
- 作为 <角色>, 我想 <能力>, 以便 <价值>。

## 核心流程
1. 入口:
2. 操作:
3. 成功结果:
4. 异常/空态/权限态:

## 数据和接口
- 数据来源: (真实接入 / mock — 由 ConfirmCard 锁定)
- 关键字段:
- 接口/后端依赖: (Node 后端默认; 接什么外部服务)

## UI/交互要求
- 页面/模块:
- 状态:
- 文案语种:
- 可访问性:

## 非功能要求
- 性能:
- 安全/权限:
- 兼容性:
- 日志/审计:

## 验收标准
- Given/When/Then:
- 必须通过的测试/截图/部署检查:

## Open Questions
- [ ] <问题> | 影响: <影响> | 默认处理: <默认值, 已与用户对过>

## 决策记录
- <日期>: <决策> | 原因: <依据(可引用 discussion.md 第 N 轮)>
```

## 收敛与完成判断

收敛信号:

- [ ] 用户 framing 已翻译且用户认可
- [ ] ConfirmCard 默认假设全部确认或一一改过
- [ ] Must / Should / Won't 用户都过了一遍
- [ ] 主角色、核心流程、成功结果有用户原话或明确认可
- [ ] 上一轮答案没引出新硬决策
- [ ] PRD 能根据已确定的事实写出来, 不需要再猜

四条满足后:

1. 写 `.opc/requirements/prd.md`。
2. 在 `.opc/requirements/discussion.md` 末尾写"Round N 已收敛, 进 solution"。
3. `opc-task-state.py mark requirements done --artifact .opc/requirements/prd.md --evidence "ConfirmCard 第 N 轮收敛, ..." --next-action "进 solution 阶段, 第 1 轮 ConfirmCard 聊后端栈/DB/部署目标"`。
4. **自动进入 solution 阶段, 不要求用户说"继续"**。

如果用户明确要"只要轻量 PRD / 我自己写 PRD / 跳过这步", 仍要至少跑一轮 ConfirmCard 把 framing 翻译聊清楚, 然后写 `.opc/requirements/discussion.md` 一份简化记录 + 用户授权摘要, 不写 PRD 正文。
