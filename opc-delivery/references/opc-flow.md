# OPC 全流程入口

本文件负责把一个粗需求路由到正确阶段, 并保证每阶段都有可验证交付物。OPC 的用户侧模型是**成品驱动 / 疑点触发确认 / 证据驱动完成**。

- 定义阶段(intake / requirements / solution / ui-design): 先抽取事实, 内部维护阶段卡/确认卡。只有高影响不确定才用原生选择交互问用户; 没有疑点就直接产出阶段文档。
- 执行阶段(implementation / verification / deployment / calibration): 连续推进, 除非遇到 token、凭证、production、远端 push、付费资源、破坏性写入等硬门禁。

阶段间自动衔接, 不要求用户每步说“继续”。空工作区不是设计收尾理由: 从零开始的新需求会自动进入前端 + Node 后端 + DB 全栈脚手架和实现。

## 目录

- [决策树](#决策树)
- [阶段链路](#阶段链路)
- [疑点触发澄清](#疑点触发澄清)
- [执行阶段自动推进](#执行阶段自动推进)
- [状态台账](#状态台账)
- [澄清策略](#澄清策略)
- [外部资料压缩规则](#外部资料压缩规则)

## 决策树

```text
1. 用户要完整 OPC / 从需求到上线吗?
   ├── 是 -> 初始化内部 OPC Stage Card -> clarification-loop.md(按需澄清) -> autonomous-bootstrap.md -> open-source-patterns.md -> requirements-workflow.md
   └── 否 -> 进 2

2. 用户要 MasterGo 画布设计 / 修改吗?
   ├── 是 -> intent-routing.md -> design-workflow.md
   └── 否 -> 进 3

3. 用户给 MasterGo URL 并要还原/转代码吗?
   ├── 是 -> intent-routing.md -> restoration-workflow.md
   └── 否 -> 进 4

4. 用户已有 PRD/设计并要实现前端或全栈吗?
   ├── 是 -> solution-design.md(补齐缺口; 高影响不确定才确认) -> implementation-workflow.md
   └── 否 -> 进 5

5. 用户要部署/CI/CD/上线吗?
   ├── 是 -> deployment-workflow.md(部署目标不明确才确认)
   └── 否 -> clarification-loop.md 判断真实交付物, 再路由到对应阶段
```

## 阶段链路

| 阶段 | 节奏 | 目标 | 交付物 | 完成证据 |
|---|---|---|---|---|
| intake | 内部路由 | 判断真实交付物和风险 | 内部 OPC Stage Card, `.opc/state/opc-task.json` | 阶段、范围、验收方式、用户 framing 解析、默认假设摘要 |
| requirements | 按需澄清 | 把口语需求变成可验收需求 | `.opc/requirements/discussion.md` + `.opc/requirements/prd.md` | 高影响疑点已处理, PRD 可作为方案输入 |
| solution | 按需澄清 | 定义怎么做 | `.opc/solution/discussion.md` + `.opc/solution/solution-design.md` | 后端栈/DB/部署目标等关键项明确, 方案覆盖 PRD |
| ui-design | 按需澄清 | 形成可实现 UI | `.opc/ui/discussion.md` + 设计说明 / MasterGo 画布 | 视觉风格、语种、关键状态明确; 3A 验证或截图 |
| implementation | 执行 | 写成全栈项目 | 前端代码 + Node 后端 + DB schema + API 路由 | lint/typecheck/test/build/Browser QA |
| verification | 执行 | 验证主链路和证据 | `.opc/verification/verification.md` | 命令、截图、URL、数据刷新或差异证据 |
| deployment | 执行(部署目标不明才确认) | 发布到目标环境 | preview/prod URL、环境变量记录、回滚方式 | 可访问链接、部署状态、健康检查、访问证据 |
| calibration | 执行 | 用真实已上线需求调参 | gap report、规则补丁、eval 更新 | 差距项闭合或 `skipped with reason` |

## 疑点触发澄清

进入定义阶段时:

1. 读 `.opc/<phase>/discussion.md` 和 `.opc/state/opc-task.json`。
2. 抽取已知事实: 用户原话、现有文档、代码、截图、接口、配置。
3. 判断是否有高影响不确定。标准见 [clarification-loop.md](clarification-loop.md)。
4. 没有高影响不确定 -> 写阶段产物并继续。
5. 有高影响不确定 -> 打开宿主原生选择/确认交互; 工具不可用时才文本降级。
6. 用户提交后更新 discussion log, 继续写产物或进入下一阶段。

反模式:

- 把“每个定义阶段至少一轮确认”当硬规则。
- 把内部确认卡完整贴给用户作为固定仪式。
- 高影响不确定没处理就写 PRD 或代码。
- 需求已经明确却仍问“是否继续”。
- 低风险工程细节让用户拍板。

## 执行阶段自动推进

本节也称“自动阶段轮转”契约。implementation -> verification -> deployment -> calibration 默认连续推进。

1. 本阶段交付物、验收口径和下一阶段输入齐了, 立即 mark done 并进下一阶段。
2. 不要在每个阶段末尾问“是否继续”; 只在硬阻塞或高风险副作用前提问。
3. 用户说“继续 / 你决定 / 后面都做完 / 从需求到上线”时, 视为完整链路授权。
4. production 部署、远端 push、覆盖 MasterGo 画布、写 secrets、付费资源、破坏性迁移仍是确认门禁。
5. 用户只说“上线”但没明确 production 时, 默认走 preview/staging 可访问链接; 部署目标平台不明确时用原生选择交互确认。
6. 某阶段被用户明确跳过, 状态写 `skipped` + 原因 + 替代证据, 继续后续阶段。
7. 中间阶段恢复时, 先 resume state + discussion log, 再继续。
8. `ui-design` 收敛后默认下一步是 `implementation`; 只有用户明确说“先别实现”或有 blocker 才停。
9. 当前工作区没有现成代码仓库、`package.json` 或前端项目结构时, 按方案自动新建全栈工作区。
10. 当前业务工作区没有 Git 仓库且不在父级仓库内时, 默认 `git init`、补 `.gitignore`, 继续推进; 没有 remote 不是停点。
11. 缺 mock 数据(用户已选演示)、测试脚本、CI/CD 或 preview 默认配置时, 先创建最小可用版本; 缺 API key、服务器、production 授权或风格/合规关键选择时, 走原生选择交互收集, 用户选完继续。

## 状态台账

状态台账是代理自动读写的恢复机制, 不是用户手动步骤。进入任务时先读 [context-persistence.md](context-persistence.md): 有 `.opc/state/opc-task.json` 就自动 `resume`, 没有就先写最小内部 OPC Stage Card 再初始化。

定义阶段额外读 `.opc/<phase>/discussion.md`。

初始化:

```bash
python3 <skill-dir>/scripts/opc-task-state.py init \
  --goal "<原始用户目标>" \
  --delivery "从需求到上线的 OPC 交付" \
  --acceptance "用户能按验收标准访问并验证部署结果" \
  --next-action "进入 requirements; 若存在高影响不确定则打开原生选择交互"
```

阶段推进:

```bash
python3 <skill-dir>/scripts/opc-task-state.py mark requirements done \
  --artifact ".opc/requirements/prd.md" \
  --evidence "高影响疑点已处理, PRD 可作为方案输入" \
  --next-action "进入 solution 阶段, 补齐技术方案、数据和部署计划"
```

等待用户动作:

```bash
python3 <skill-dir>/scripts/opc-task-state.py note \
  --phase deployment \
  --text "已打开部署平台选择框, 等用户提交" \
  --next-action "用户提交平台后继续 build + deploy"
```

完成前:

```bash
python3 <skill-dir>/scripts/opc-task-state.py validate --for-completion
```

`blocked` 和 `pending` 不是完成。`skipped` 必须有用户授权或明确原因。

错误停点:

- “我先产出可评审的设计包, 后面等你选下一步”
- “这里不是 Git 仓库, 所以本轮先停在方案/设计”
- “MasterGo 画布、前端原型、API 契约或产品评审, 你来选一个我再继续”
- “没有 Git 仓库, 你先创建好我再继续”
- “没有部署服务器, 所以本轮只能结束在设计”
- “Vercel token 缺失, 我退回本地 production server”

## 澄清策略

澄清不等于固定问卷。先判断影响面:

- 高影响: 原生选择交互优先; 文本降级必须有默认和自定义 / type something。
- 低影响: 自治处理, 记录在内部日志或结构化收尾。
- 已锁定: 不重复问。

如果用户说“你决定”, 对低风险项直接决定; 对高影响项给推荐默认和理由, 原生确认可用时打开确认框。用户提交或明确授权默认后继续。

## 外部资料压缩规则

外部最佳实践只用于校准流程, 不要把长文档塞进 Skill。保留成阶段门禁:

- PRD 要含目标、用户、JTBD、MoSCoW、用户故事、验收标准和 Open Questions。
- 方案要有 2-3 个候选路径(或写明为何只有一条)、推荐理由、Planning Packet 和自我审查; 必须明示后端栈、DB、部署目标。
- UI 设计要有信息架构、状态、语种、可访问性、性能预算和视觉验证。
- 全栈实现要遵循现有项目约定、组件 + API routes + DB schema 拆分、TDD/regression ratchet 和浏览器验证。
- CI/CD 要先 preview、保护 secrets、记录 release packet、stop conditions、部署状态和回滚方式。
- 已上线需求回放要用 AAR 把差距沉淀到规则、脚本或 eval。
