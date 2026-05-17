# OPC 全流程入口

本文件负责把一个粗需求路由到正确阶段, 并保证每阶段都有交付物。OPC 流程分两种节奏:

- **定义阶段 (intake / requirements / solution / ui-design) = 对话式推进**: AI 用 ConfirmCard 跟用户多轮 Q&A, 直到不确定性收敛才落最终文档并 mark done。详见 [clarification-loop.md](clarification-loop.md)。
- **执行阶段 (implementation / verification / deployment / calibration) = 自动推进**: 连续推进, 除非遇到 token/凭证/生产/远端 push/付费/破坏性写入等硬阻塞。

阶段间自动衔接, 不要求用户每步说"继续"。但定义阶段内部讨论没收敛前不要 mark done; 部署目标这类高赌注决策没在 ConfirmCard 里聊明确前不允许进 deployment 阶段。

**空工作区不是设计收尾理由**: 如果是从零开始的新需求、当前目录又没有可复用前端仓库, 代理把 `.opc/` 里的 PRD/方案/UI 当成实现输入, 自动进入前端 + Node 后端 + DB 全栈脚手架和实现, 而不是停在"请用户选择下一步"。

**缺项默认补齐**: 完整 OPC 里, 缺 Git、前端脚手架、Node 后端、DB schema、mock、测试、CI/CD 或预览配置时, 先读 [autonomous-bootstrap.md](autonomous-bootstrap.md)。只有凭证、生产环境、远端推送、付费资源、破坏性写入、不可推断的风格/合规边界才暂停确认。

## 目录

- [决策树](#决策树)
- [阶段链路](#阶段链路)
- [定义阶段对话式推进](#定义阶段对话式推进)
- [执行阶段自动推进](#执行阶段自动推进)
- [状态台账](#状态台账)
- [澄清策略](#澄清策略)
- [外部资料压缩规则](#外部资料压缩规则)

## 决策树

```text
1. 用户要完整 OPC / 从需求到上线吗?
   ├── 是 -> Stage Card -> clarification-loop.md(第 1 轮 ConfirmCard) -> autonomous-bootstrap.md -> open-source-patterns.md -> requirements-workflow.md
   └── 否 -> 进 2

2. 用户要 MasterGo 画布设计 / 修改吗?
   ├── 是 -> intent-routing.md -> design-workflow.md
   └── 否 -> 进 3

3. 用户给 MasterGo URL 并要还原/转代码吗?
   ├── 是 -> intent-routing.md -> restoration-workflow.md
   └── 否 -> 进 4

4. 用户已有 PRD/设计并要实现前端吗?
   ├── 是 -> solution-design.md 轻量 ConfirmCard 确认栈/DB/部署 -> implementation-workflow.md
   └── 否 -> 进 5

5. 用户要部署/CI/CD/上线吗?
   ├── 是 -> deployment-workflow.md 的部署目标 ConfirmCard 必跑
   └── 否 -> ConfirmCard 第 1 轮澄清真实交付物
```

## 阶段链路

| 阶段 | 节奏 | 目标 | 交付物 | 完成证据 |
|---|---|---|---|---|
| intake | 对话 | 判断真实交付物和风险 | OPC Stage Card, `.opc/state/opc-task.json` | 阶段、范围、验收方式、用户 framing 解析、默认假设清单已写明 |
| requirements | 对话 | 把口语需求变成可验收需求 | `.opc/requirements/discussion.md` + `.opc/requirements/prd.md` | ConfirmCard 已收敛(用户 framing、默认假设、硬决策全部回答完), PRD 可作为方案输入 |
| solution | 对话 | 定义怎么做 | `.opc/solution/discussion.md` + `.opc/solution/solution-design.md` | 后端栈/DB/部署目标已锁定, 方案覆盖 PRD 且关键风险闭合 |
| ui-design | 对话 | 形成可实现 UI | `.opc/ui/discussion.md` + 设计说明 / MasterGo 画布 | 视觉风格、密度、品牌已聊清; 3A 验证或本地概念+截图 |
| implementation | 执行 | 写成全栈项目 | 前端代码 + Node 后端 + DB schema + API 路由 | lint/typecheck/test/build/Browser QA |
| deployment | 执行(但部署目标必须先聊定) | 发布到目标环境 | preview/prod URL、环境变量记录、回滚方式 | 可访问链接、部署状态、健康检查、访问证据 |
| calibration | 执行 | 用真实已上线需求调参 | gap report、规则补丁、eval 更新 | 差距项闭合或记录; 无真实流量时 `skipped with reason` |

## 定义阶段对话式推进

每个定义阶段(intake → requirements → solution → ui-design)的循环:

1. 进阶段时先读 `.opc/<phase>/discussion.md`(若存在), 接着上轮聊。
2. 写 ConfirmCard 第 N 轮: framing 解析 + 默认假设 + 硬决策。详见 [clarification-loop.md](clarification-loop.md) 的`ConfirmCard 模板`。
3. 用户回应, AI 更新理解。
4. 引出新问题 → 第 N+1 轮 ConfirmCard, 只问新问题。
5. 用户答复模糊("你看着办") → AI 摆推荐项 + 选不上的理由, 让用户至少不反对; 这本身也是一轮。
6. 不确定性收敛(四条满足: 默认假设全认可或一一改、硬决策全答、上轮没引新硬决策、文档可写) → 写最终文档 → mark done → 自动进下一阶段。

**收敛判断不要求用户说"继续"**, 但每个定义阶段的 discussion log 最后一行必须明确写"已收敛, 进 <next>"。

下面这些做法是定义阶段反模式, 不允许出现:

- ❌ "用户在 intake 选了 4 题, requirements 阶段直接写 158 行 PRD, mark done 进 solution"
- ❌ ConfirmCard 打完直接 mark done, 没等用户回应
- ❌ ConfirmCard 打完等用户说"继续"才进下一阶段(把讨论媒介当 gate)
- ❌ 第 N+1 轮 ConfirmCard 重问 N 轮已确定的事(没读 dialogue log)
- ❌ 把单方面决策埋进 PRD `Won't` 假装"已声明"
- ❌ 用户用了承诺词("企业级"), AI 没在第 1 轮翻译就开写

## 执行阶段自动推进

本节也称"自动阶段轮转"契约。实施 → 验证 → 部署 → 校准阶段, 默认连续推进。规则:

1. 本阶段交付物、验收口径和下一阶段输入齐了, 立即 mark done 并进下一阶段。
2. 不要在每个阶段末尾问"是否继续"; 只在硬阻塞或高风险副作用前提问。
3. 用户说"继续 / 你决定 / 后面都做完 / 从需求到上线"时, 视为完整链路授权。
4. 生产部署、远端推送、覆盖 MasterGo 画布、写 secrets、付费资源、破坏性迁移仍是确认门禁。
5. 用户只说"上线"但没明确 production 时, 自动走 preview/staging 可访问链接; 但**部署目标平台**(本地/Vercel/Netlify/Cloudflare/自有服务器)必须在 ConfirmCard 里聊明确, 不允许默默退回本地。
6. 某阶段被用户明确跳过, 状态写 `skipped` + 原因 + 替代证据, 继续后续阶段。
7. 中间阶段恢复时, 先 resume Stage Card + dialogue log, 再从当前阶段继续向后轮转。
8. `ui-design` 收敛后默认下一步是 `implementation`; 只有用户明确说"先别实现"或有 blocker 才允许停。
9. 当前工作区没有现成代码仓库、`package.json` 或前端项目结构时, 按方案里的目标框架自动新建全栈(前端 + Node 后端 + DB)工作区; 不要把"没有 repo"解释成"本轮只做产品设计"。
10. 当前业务工作区没有 Git 仓库且不在父级仓库内时, 默认 `git init`、补 `.gitignore`, 继续推进; 没有 remote 不是停点。
11. 缺 mock 数据(用户已选 mock 时)、测试脚本、CI/CD 或 preview 默认配置时, 先创建最小可用版本; 缺 API key、服务器、production 授权或风格/合规关键选择时, 走 ConfirmCard 收集, 用户选完继续。

## 状态台账

状态台账是代理自动读写的恢复机制, 不是用户手动操作步骤。进入任务时先读 [context-persistence.md](context-persistence.md): 有 `.opc/state/opc-task.json` 就自动 `resume`, 没有就先写最小 Stage Card 再初始化。

定义阶段额外读 `.opc/<phase>/discussion.md`(若存在), 续接上轮 ConfirmCard。

在用户项目工作区初始化:

```bash
python3 <skill-dir>/scripts/opc-task-state.py init \
  --goal "<原始用户目标>" \
  --delivery "从需求到上线的 OPC 交付" \
  --acceptance "用户能按验收标准访问并验证部署结果" \
  --next-action "进入 clarification-loop 第 1 轮 ConfirmCard, 解析 framing + 列默认假设"
```

阶段推进时(只在定义阶段收敛、或执行阶段完成时调用):

```bash
python3 <skill-dir>/scripts/opc-task-state.py mark requirements done \
  --artifact ".opc/requirements/prd.md" \
  --evidence "ConfirmCard 第 N 轮已收敛, 用户 framing 已翻译并认可, 默认假设全部确认" \
  --next-action "进入 solution 阶段, 第 1 轮 ConfirmCard 聊后端栈/DB/部署目标"
```

阶段未完成但要中断或等待用户动作时:

```bash
python3 <skill-dir>/scripts/opc-task-state.py note \
  --phase deployment \
  --text "ConfirmCard 已抛部署平台 A/B/C, 等用户选" \
  --next-action "用户选完平台后继续 build + deploy"
```

完成前:

```bash
python3 <skill-dir>/scripts/opc-task-state.py validate --for-completion
```

`blocked` 和 `pending` 不是完成。`skipped` 必须有用户授权或明确原因。

以下说法都属于错误停点, 不应出现在完整 OPC 任务里:

- "我先产出可评审的设计包, 后面等你选下一步"
- "这里不是 Git 仓库, 所以本轮先停在方案/设计"
- "MasterGo 画布、前端原型、API 契约或产品评审, 你来选一个我再继续"
- "没有 Git 仓库, 你先创建好我再继续"
- "没有部署服务器, 所以本轮只能结束在设计"
- "Vercel token 缺失, 我退回本地 production server"(应该回到 ConfirmCard 让用户选平台, 而不是默默降级)

## 澄清策略

完整 OPC 的澄清都走 [clarification-loop.md](clarification-loop.md) 的多轮 ConfirmCard 机制, 不再单独用一两题选择题包装。轻量任务(只补一个阶段、用户给得很具体)允许简化, 但仍要在动手前用一张 ConfirmCard 列出默认假设。

如果用户说"你决定", AI 仍要写 ConfirmCard 把推荐项明示, 在用户没主动反对前不要把"你决定"理解为"我可以全程不抛卡"。

硬决策选择题写法: 列 2-4 个具体选项, 末尾保留"自定义 / type something" 允许用户输入未覆盖的方案; 不要用开放式"你看呢"替代具体选项。

## 外部资料压缩规则

外部最佳实践只用于校准流程, 不要把长文档塞进 skill。保留成阶段门禁:

- PRD 要含目标、用户、JTBD、MoSCoW、用户故事、验收标准和 open questions。
- 方案要有 2-3 个候选路径(或写明为何只有一条)、推荐理由、planning packet 和自我审查; 必须明示后端栈、DB、部署目标。
- UI 设计要有信息架构、状态、语种、可访问性、性能预算和视觉验证。
- 全栈实现要遵循现有项目约定、组件 + API routes + DB schema 拆分、TDD/regression ratchet 和浏览器验证。
- CI/CD 要先 preview、保护 secrets、记录 release packet、stop conditions、部署状态和回滚方式。
- 已上线需求回放要用 AAR 把差距沉淀到规则、脚本或 eval。
