# 开源交付模式融合参考

目标: 把优秀开源 skill 的做事方式压缩成 OPC 阶段门禁。不要在交付时复述这些
来源，也不要把其它 skill 原文搬进上下文；把它们转成 PRD、方案、测试、部署和校准的
可检查行为。

## 来源模式

| 来源 | 借鉴模式 | OPC 落点 |
|---|---|---|
| Superpowers | brainstorming, writing plans, TDD/regression ratchet, systematic debugging, evidence-before-completion | 先澄清/设计再实现；方案给 2-3 个可选路径；行为可测时先写失败测试或回归用例；失败先定位根因；完成前必须有新鲜证据 |
| Anthropic skills | skill progressive disclosure, frontend design, browser validation | `SKILL.md` 只放硬规则，细节放 references；UI 要有明确审美方向；前端完成要用真实浏览器/截图/console 证据 |
| jakenuts agent-skills | design-led development, git workflow safety | 每个功能先写用户结果句；错误、恢复、可访问性和性能预算前置；有副作用的 git/发布动作保留确认和可回滚路径 |
| neurofoo agent-skills | JTBD, MoSCoW, premortem, red-team, AAR | 需求阶段写核心 Job 和优先级；生产前做失败预演和对抗审查；上线回放用 after-action review 沉淀规则 |
| oh-my-skills | task-planning, testing strategies, deployment automation, accessibility, code-review | 把混乱上下文整理成 packet；按风险选择最小可信验证层；部署产 release packet；扫描结果不能替代手工可访问性验证；评审聚焦风险和缺失证据 |

## OPC Pattern Card

完整 OPC 任务在 Stage Card 后补一张轻量 Pattern Card，写入 `.opc/state/opc-task.json`
或阶段文档的“决策记录”:

```text
OPC Pattern Card
- Discovery model: JTBD / MoSCoW / existing PRD / golden replay
- Design model: 2-3 approaches / single constrained path / existing design
- Planning packet: discovery / foundation / delivery / verification / follow-through
- Validation gate: local / PR / release / scheduled
- Risk checks: premortem / red-team / systematic debugging / none with reason
- Evidence to claim done: tests / browser screenshot / diff / deployment health / AAR
```

## 阶段门禁

### 需求阶段

- 写一个 Core Job: `当 <场景>，<角色> 想要 <能力>，以便 <业务结果>`。
- 用 MoSCoW 拆范围；`Must` 不能吞掉全部工作，`Won't` 要明确防止范围蔓延。
- 记录替代方案和补偿行为: 用户现在怎么解决、为什么不够好、上线后要替代什么。
- 只问 blocker，且一次只问一个关键选择题；能自动决定的写入决策记录。

### 方案阶段

- 至少给出 2-3 个方案方向，除非 PRD 或现有系统已经强约束只剩一条路。
- 对每个方向写清取舍: 交付速度、可维护性、设计质量、验证成本、部署风险。
- 方案结尾做自我审查: 是否覆盖 Must、是否有占位符、是否存在互相矛盾的假设、是否能直接交给实现。
- 把工作拆成 planning packet: discovery、foundation、delivery、verification、follow-through。

### UI 和实现阶段

- 每个核心功能先写用户结果句: `这帮助 <用户> 通过 <机制> 达成 <结果>`。
- 交互组件覆盖 default、hover/focus、loading、empty、error、success、disabled/permission 状态。
- 行为可测时先补失败测试或回归用例，再写实现；没有测试基础设施时，写明原因并用浏览器场景补证据。
- 遇到 bug 或验证失败时走 systematic debugging: 复现 -> 读错误 -> 查最近变化 -> 单一假设 -> 最小验证 -> 修根因。

### 验证阶段

- 先命名 gate truth: local、PR、release 或 scheduled，不把一个测试命令冒充全部质量策略。
- 按风险选择最小可信层: unit/component、integration、contract、smoke/E2E、manual exploratory。
- 自动化扫描是输入，不是完成；可访问性、响应式、动效、焦点和屏幕阅读器相关问题要保留手工验证项。
- evidence-before-completion: 先说什么能证明完成，再运行验证、读输出、记录证据。

### 部署阶段

- 生产前必须有 release packet: artifact、环境、promotion model、rollout strategy、verification、rollback。
- production gate 前做 premortem: 假设发布失败，列 top risks、early warning、prevention、mitigation、owner。
- 高风险发布做 red-team: 权限、数据、secrets、回滚不可逆、依赖供应商、监控盲区。
- 写 stop conditions；一旦命中，停止 promotion 或触发 rollback，而不是继续乐观推进。

### 校准阶段

- 用 AAR 闭环: what expected、what happened、why different、what changes。
- 把差距分成 skill 通用规则、项目规则、脚本检查、eval；能自动化的优先进入 scripts 或 evals。
- 只有当高影响差距有规则更新或明确后续时，才说校准完成。
