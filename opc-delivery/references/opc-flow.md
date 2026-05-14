# OPC 全流程入口

本文件负责把一个粗需求路由到正确阶段，并保证每阶段都有交付物。不要在入口阶段写长问卷；
先建立最小 Stage Card，再边做边补充。

默认连续推进: 完整 OPC 任务一旦进入阶段链路，就从 Stage Card 往后自动轮转到可访问的
上线交付证据。阶段产物是下一阶段输入，不是等待用户确认的自然停点；除非用户明确说
“暂停 / 停下 / 只做当前阶段”，或遇到硬阻塞 / 高风险副作用确认门禁。

## 目录

- [决策树](#决策树)
- [阶段链路](#阶段链路)
- [自动阶段轮转](#自动阶段轮转)
- [状态台账](#状态台账)
- [澄清策略](#澄清策略)
- [外部资料压缩规则](#外部资料压缩规则)

## 决策树

```text
1. 用户要完整 OPC / 从需求到上线吗?
   ├── 是 -> Stage Card + Pattern Card -> open-source-patterns.md -> requirements-workflow.md
   └── 否 -> 进 2

2. 用户要 MasterGo 画布设计 / 修改吗?
   ├── 是 -> intent-routing.md -> design-workflow.md
   └── 否 -> 进 3

3. 用户给 MasterGo URL 并要还原/转代码吗?
   ├── 是 -> intent-routing.md -> restoration-workflow.md
   └── 否 -> 进 4

4. 用户已有 PRD/设计并要实现前端吗?
   ├── 是 -> solution-design.md(轻量确认) -> implementation-workflow.md
   └── 否 -> 进 5

5. 用户要部署/CI/CD/上线吗?
   ├── 是 -> deployment-workflow.md
   └── 否 -> 选择题澄清真实交付物
```

## 阶段链路

| 阶段 | 目标 | 交付物 | 完成证据 |
|---|---|---|---|
| intake | 判断真实交付物和风险 | OPC Stage Card, OPC Pattern Card, `.opc/state/opc-task.json` | 阶段、范围、验收方式和开源交付门禁已写明 |
| requirements | 把口语需求变成可验收需求 | PRD、用户故事、验收标准、open questions | blocker 已闭合或有默认处理，PRD 可作为方案输入 |
| solution | 定义怎么做 | 方案文档、IA/流程、数据/API、测试计划 | 方案覆盖 PRD 且关键风险闭合 |
| ui-design | 形成可实现 UI | MasterGo 画布、设计说明、组件/语种策略 | 3A 验证或本地概念+截图证据 |
| implementation | 写成前端项目 | 代码、状态/API wiring、测试 | lint/typecheck/test/build/Browser QA |
| deployment | 发布到目标环境 | preview/prod URL、环境变量记录、回滚方式 | 可访问链接、部署状态、健康检查、访问证据 |
| calibration | 用真实已上线需求调参 | gap report、规则补丁、eval 更新 | 差距项闭合或记录为后续规则 |

## 自动阶段轮转

阶段推进规则:

1. 本阶段交付物、验收口径和下一阶段输入齐了，就标记 `done` 并立即进入下一阶段。
2. 不要在每个阶段末尾问“是否继续”；只在硬阻塞或高风险副作用前提问。
3. 用户说“继续 / 你决定 / 后面都做完 / 从需求到上线”时，视为完整链路授权。
4. 生产部署、远端推送、覆盖 MasterGo 画布、写 secrets、付费资源、破坏性迁移仍是确认门禁。
5. 用户只说“上线”但没有明确 production 时，自动走 preview/staging 可访问链接作为上线交付证据。
6. 如果某阶段被用户明确跳过，状态写 `skipped`、记录原因和替代证据，然后继续后续阶段。
7. 如果当前输入来自中间阶段，先恢复或补齐 Stage Card，再从当前阶段继续向后轮转。

## 状态台账

状态台账是代理自动读写的恢复机制，不是用户手动操作步骤。进入任务时先读
[context-persistence.md](context-persistence.md): 有 `.opc/state/opc-task.json` 就自动
`resume`，没有就先写最小 Stage Card 再初始化。

在用户项目工作区初始化:

```bash
python3 <skill-dir>/scripts/opc-task-state.py init \
  --goal "<原始用户目标>" \
  --delivery "从需求到上线的 OPC 交付" \
  --acceptance "用户能按验收标准访问并验证部署结果" \
  --next-action "进入需求阶段，写 .opc/requirements/prd.md"
```

阶段推进时:

```bash
python3 <skill-dir>/scripts/opc-task-state.py mark requirements done \
  --artifact ".opc/requirements/prd.md" \
  --evidence "PRD 覆盖 blocker，可作为方案输入；用户未要求暂停" \
  --next-action "进入方案阶段，写 .opc/solution/solution-design.md"
```

阶段未完成但要中断或等待用户动作时:

```bash
python3 <skill-dir>/scripts/opc-task-state.py note \
  --phase requirements \
  --text "等待用户提供生产服务器地址" \
  --next-action "拿到服务器地址后继续部署预检"
```

完成前:

```bash
python3 <skill-dir>/scripts/opc-task-state.py validate --for-completion
```

`blocked` 和 `pending` 不是完成。`skipped` 必须有用户授权或明确原因。

## 澄清策略

只问会改变真实交付物的问题。优先选择题:

```text
我先确认真实交付物:
A. 完整 OPC 闭环(推荐): PRD -> UI -> 前端实现 -> 部署。
B. 只补当前阶段: 我先完成你指定的一步，并标注上下游缺口。
C. 自定义 / type something: 你直接写想要的范围。
```

如果用户说“你决定”，选 A，但在 Stage Card 写明“按完整 OPC 闭环推进，后续遇到生产部署、
付费工具、覆盖写入、secret 配置时再单独确认”。

## 外部资料压缩规则

外部最佳实践只用于校准流程，不要把长文档塞进 skill。保留成阶段门禁:

- PRD 要含目标、用户、JTBD、MoSCoW、用户故事、验收标准和 open questions。
- 方案要有 2-3 个候选路径、推荐理由、planning packet 和自我审查。
- UI 设计要有信息架构、状态、语种、可访问性、性能预算和视觉验证。
- 前端实现要遵循现有项目约定、组件拆分、API wiring、TDD/regression ratchet 和浏览器验证。
- CI/CD 要先 preview、保护 secrets、记录 release packet、stop conditions、部署状态和回滚方式。
- 已上线需求回放要用 AAR 把差距沉淀到规则、脚本或 eval。
