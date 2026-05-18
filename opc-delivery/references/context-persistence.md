# 上下文持久化和主动拆分

目标: OPC 交付不能依赖单轮聊天历史。每次使用 skill 都要把当前阶段、产物路径、证据、
阻塞和下一步写进用户项目，确保换新会话后能从文件恢复。

本文件里的命令是给代理自动执行的，不是让用户手动运行。代理自动执行恢复、初始化和记录；
用户只需要说“继续上次那个
OPC 需求”或重新触发 `$opc-delivery`，代理必须自己读取台账并继续。

## 目录

- [恢复优先](#恢复优先)
- [每阶段必须记录](#每阶段必须记录)
- [主动拆分](#主动拆分)
- [台账只存摘要](#台账只存摘要)
- [新会话交接](#新会话交接)

## 恢复优先

每次进入完整 OPC、阶段交付或“继续上次”任务时，代理必须自动执行:

1. 如果 `.opc/state/opc-task.json` 存在，先运行:

   ```bash
   python3 <skill-dir>/scripts/opc-task-state.py resume
   ```

2. 按 `resumePhase`、`nextAction` 和 `recentHistory` 恢复当前阶段，不要求用户重讲上下文。
3. 如果台账不存在，代理先写最小内部 OPC Stage Card，再初始化:

   ```bash
   python3 <skill-dir>/scripts/opc-task-state.py init \
     --goal "<原始用户目标>" \
     --delivery "<真实交付物>" \
     --acceptance "<验收方式>" \
     --artifact "<内部 Stage Card 或入口文档路径>" \
     --evidence "<入口判断依据>" \
     --next-action "<下一阶段第一步>"
   ```

## 每阶段必须记录

阶段完成、阻塞、跳过、暂停或需要用户动作前，都写台账:

```bash
python3 <skill-dir>/scripts/opc-task-state.py mark <phase> <done|blocked|skipped|pending> \
  --artifact "<产物路径，不贴大段内容>" \
  --evidence "<一句话证据摘要>" \
  --next-action "<新会话继续时第一步>"
```

临时进展但阶段未完成时，用 note:

```bash
python3 <skill-dir>/scripts/opc-task-state.py note \
  --phase <phase> \
  --text "<当前进展或用户动作>" \
  --artifact "<相关文件路径>" \
  --next-action "<恢复后的下一步>"
```

自治补齐动作也要记录: 例如 `git init`、创建 `.gitignore`、脚手架、mock 数据、测试命令、
CI/CD 或 preview 配置。记录自动创建了什么、还缺什么凭证/授权、恢复后第一步继续做什么。

## 主动拆分

不要把 PRD、方案、设计说明、实现报告、验证报告、发布证据、校准报告塞进一个大文件。
默认按阶段拆到这些路径:

| 阶段 | 默认文件 |
|---|---|
| 需求 | `.opc/requirements/prd.md` |
| 方案 | `.opc/solution/solution-design.md` |
| 界面 | `.opc/design/design-brief.md` 或 `.codify/state/mastergo-task.json` |
| 实现 | `.opc/implementation/implementation-report.md` |
| 验证 | `.opc/verification/verification.md` |
| 部署 | `.opc/deployment/release.md` |
| 校准 | `.opc/calibration/<feature>-gap-report.md` |

单个文件接近 200 行或 12KB 时主动拆分:

- `prd.md` 拆成 `scope.md`、`flows.md`、`acceptance.md`；
- `solution-design.md` 拆成 `options.md`、`architecture.md`、`test-deploy-plan.md`；
- `verification.md` 拆成 `commands.md`、`screenshots.md`、`issues.md`；
- `release.md` 拆成 `environment.md`、`healthcheck.md`、`rollback.md`。

父文件只保留摘要、目录和子文件路径。

## 台账只存摘要

`.opc/state/opc-task.json` 只保存:

- 当前阶段；
- 每阶段状态；
- 产物路径；
- 一句话证据；
- 最近历史；
- 下一步。

不要把完整 PRD、完整会议纪要、长日志或大段代码写进状态台账。长输入放到
`.opc/source/` 或项目既有 docs，再在台账里记录路径和摘要。

## 新会话交接

向用户汇报“当前阶段”时，代理先自动运行 `opc-task-state.py resume`。回答格式:

```text
当前阶段: <resumePhase>
已完成: <done/skipped 阶段 + 产物路径>
待处理: <pending/blocked 阶段 + next-action>
恢复依据: .opc/state/opc-task.json
```

不要要求用户复制命令、读 JSON 或手动选择阶段。用户要做的只有提供被阻塞的外部信息，
例如 token、权限、服务器地址、截图或生产发布授权。
