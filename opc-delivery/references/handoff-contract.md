# 收尾契约

每个 turn 收尾的强制结构。覆盖 `~/.codex/AGENTS.md` 工作约定中关于“最终报告必须包含...剩余风险”的默认形态。

核心原则: 不把不确定项甩给用户。无需用户决策时继续推进; 需要用户决策时优先打开宿主原生选择/确认交互。

## 目录

- [为什么需要这个契约](#为什么需要这个契约)
- [反模式: 剩余风险三连](#反模式-剩余风险三连)
- [正模式: 结构化收尾](#正模式-结构化收尾)
- [宿主原生交互优先](#宿主原生交互优先)
- [不确定项三分类](#不确定项三分类)
- [显式下一步句式](#显式下一步句式)
- [自治推进 vs. 必须用户拍板](#自治推进-vs-必须用户拍板)
- [跟 opc-task-state.py mark 的联动](#跟-opc-task-statepy-mark-的联动)
- [例子](#例子)
- [反模式清单](#反模式清单)

## 为什么需要这个契约

“剩余风险”单甩给用户是反模式:

- 用户不知道接下来要不要应对、怎么应对;
- AI 看似负责, 实际把 routing 责任推回用户;
- 对话停在这里, 没人推下一阶段;
- Codex 默认收尾习惯容易变成“汇报 + 停”。

Karpathy 第 1 条“不要藏起困惑, 主动暴露 tradeoff”的意思是: 该自治就自治, 该拍板就给选项和推荐, 该卡住就说缺什么和怎么解锁。

## 反模式: 剩余风险三连

不要这样收尾:

```text
已实现登录页。
剩余风险:
- API mock 没接真实后端
- CI 还没跑
- 部署目标没定
```

问题在于每条都缺行动分类: 是 AI 下一步做、等用户拍板、还是卡住缺凭证? 用户必须再问一遍。

## 正模式: 结构化收尾

每个 turn 收尾必须满足下面结构。不是每段都强制有大量内容, 但边界要清楚, 用户能快速识别“我需不需要动作”。普通用户问进度时默认用结果摘要, 不贴内部阶段表。

```text
[已完成]
- 登录页 (src/app/login/page.tsx)
- /api/auth route (Prisma user schema + JWT)

[证据]
- pnpm typecheck: 0 errors
- pnpm test auth.spec.ts: 8 passed
- Browser: localhost:3000/login 主链路通过

[不确定项 + 我的处理]
- 真后端 vs mock: 已按 PRD 锁定的真后端接通; 不需要你决策。
- CI: 已加 pnpm test 到 .github/workflows/ci.yml; 下次 push 触发。
- 部署目标: 还没到 deployment 阶段, 进入时若未明确我会打开选择框。

[下一步]
我现在做 /app/projects 前端列表页 + 跑通增删改主链路。
```

| 段 | 必填? | 内容 |
|---|---|---|
| `[已完成]` | 是 | 本轮做了什么具体事, 含产物路径 / commit / 截图 |
| `[证据]` | 是 | 测试通过 / 命令退出 0 / 截图 / URL / `get_design_diff` 输出; 尚未执行也要写“待验证”原因 |
| `[不确定项 + 我的处理]` | 是 | 每条归类: 自治处理 / 需要拍板 / 卡住缺 X; 没有就写“没有未决项” |
| `[需要你拍板]` | 仅在需要时 | 原生选择/确认交互优先; 不可用时才列 A/B/C + 默认 + 自定义 / type something |
| `[下一步]` | 是 | “我现在做 X” / “等你在原生交互提交” / “等你回 A/B/C” / “卡住, 缺 X”之一 |

内部阶段卡或确认卡也遵守这个收尾结构, 但不要求把完整卡片贴给用户。若本轮没有需要用户决策的事, 就写“没有未决项”并继续推进。

普通用户进度摘要也可用下面段名, 与上面结构等价:

```text
目标: <用户目标>
已交付: <普通话术摘要>
正在推进: <普通话术摘要>
需要你做什么: <无需操作 / 等选择 / 卡住缺 X>
接下来: <下一步动作>
```

禁止默认展示 `阶段进度(OPC 8 阶段)`、box-drawing 表格、raw phase IDs
(`intake`, `requirements`, `solution`, `ui-design`, `implementation-plan`,
`implementation`, `verification`, `deployment`, `calibration`) 或
`artifact/evidence/nextAction`。这些只用于内部恢复和审计, 用户明确要求内部状态时才展示。

## 宿主原生交互优先

需要用户拍板时, 先判断当前 AI 宿主是否有真实结构化决策交互可用且当前模式允许调用。例子包括 Codex App 的 `request_user_input`、Claude Code / 其它 runner 暴露的 confirm/select/prompt 工具、OMX question bridge 或等价 native UI。

可用时:

- 调用宿主原生交互工具, 不要只在聊天里列文本 A/B/C/D;
- 每轮最多 1-3 个问题, 每题 2-3 个选项;
- 推荐项放第一并标 `(Recommended)` 或宿主等价推荐标记;
- hand-off 只写“已打开宿主原生交互”、推荐默认和等待提交的下一步;
- 说明选择框含自定义入口, 或依赖宿主自动提供 Other。

不可用时:

- 明说“当前宿主没有可用结构化交互, 降级为文本选项”;
- 在 `[需要你拍板]` 段列 A/B/C/D, 标默认或推荐, 保留“自定义 / type something”;
- 如果硬决策超过 3 个, 拆成多轮, 不要一次丢长问卷。

## 不确定项三分类

| 类别 | 标识词 | 行动 |
|---|---|---|
| **自治处理** | “我已默认处理” / “我下一步处理” / “没有未决项” | AI 已做或马上做, 用户不必决策。给出证据或下一步。 |
| **需要用户拍板** | “需要你拍板” + 原生选择/确认交互, 或文本降级选项 | 不允许开放式“你看呢”。必须有推荐默认和自定义入口。 |
| **硬阻塞** | “卡住, 缺 X” + 解锁路径 | 缺 token / 凭证 / 付费资源时, 写明缺什么、怎么补、补完后继续。 |

自治处理:

- 小依赖、文件命名、helper 拆法、内部路由、mock seed 值;
- 已被 PRD、方案、用户提交或内部记录锁定过的项;
- 测试 / lint / build / dev server 启动这类无副作用工具调用;
- 默认假设暴露规则里属于低风险类目的事。

必须用户拍板:

- API key / token / secret / 私有 URL / 服务器地址 / 账号权限;
- production 部署、远端 push、覆盖 MasterGo 画布、覆盖已有服务器或数据库、破坏性迁移;
- 付费资源、采购、外部服务开通;
- 修改已锁定的高影响决策;
- 法务 / 合规 / 客户数据范围 / 真实 SLA;
- 用户 framing 仍有歧义且影响交付范围。

禁止把可自治的事推给用户拍板。

## 显式下一步句式

每个 turn 必须以下面之一收尾:

- `我现在做 X` — 自治推进, 没有等用户的事;
- `我现在做 X, 同时等你在原生交互提交` — 自治推进 + 一个具体决策;
- `等你在原生交互提交后继续` — 必须拍板且原生结构化交互可用;
- `等你回 A/B/C 哪个再继续` — 文本降级;
- `卡住, 缺 X, 你补好后我自动继续` — 硬阻塞 + 解锁路径。

省略下一步、写“看你的 / 你定吧 / 看情况”都算反模式。

## 自治推进 vs. 必须用户拍板

默认从低干扰到高干预判断:

```text
自动继续 -> default + 自治 -> default + 短拍板 -> 必须拍板 -> 硬阻塞
```

- **自动继续**: 已锁定的事 + 无副作用工具调用。
- **default + 自治**: 我替用户默认了 X, 反对可改, 但默认能跑就跑。
- **default + 短拍板**: 影响较大但有强推荐; 原生交互可用时开确认。
- **必须拍板**: 高影响事项; 等用户提交。
- **硬阻塞**: 缺凭证、付费资源或真实权限; 写解锁路径。

定义阶段也不是每次都必须拍板; 只有高影响不确定才拍板。执行阶段更应避免把小事推给用户。

## 跟 opc-task-state.py mark 的联动

AI 在跑 `python3 scripts/opc-task-state.py mark <phase> done` 之前, 必须先把本轮 hand-off 文本跑过 `scripts/handoff-lint.py`:

```bash
printf "%s" "<本轮回答>" > .opc/<phase>/last-handoff.md
python3 scripts/handoff-lint.py --file .opc/<phase>/last-handoff.md --phase <phase>

python3 scripts/opc-task-state.py mark <phase> done --evidence "..." --artifact "..."
```

lint 失败意味着这轮收尾不合格, 必须重写。不要用“我下次改”绕过。

## 例子

### 例 1: 实现阶段中段汇报

```text
[已完成]
- /api/projects route (POST / GET / PATCH)
- Prisma project schema 迁移

[证据]
- pnpm test projects.spec.ts: 5 passed
- curl localhost:3000/api/projects 返回 200 + 真实数据

[不确定项 + 我的处理]
- 软删除 vs 硬删除: 我默认走软删除 (deletedAt 字段), 如果你说“我就要硬删”再改。
- 列表分页: PRD 没说, 我默认 limit=20 offset 分页。

[下一步]
我现在做 /app/projects 前端列表页 + 跑通增删改主链路。
```

### 例 2: 卡 token

```text
[已完成]
- Vercel preview 项目已创建
- .env.example 已生成

[证据]
- vercel link OK
- vercel projects ls 显示项目

[卡住]
- 部署需要 DATABASE_URL (Postgres 连接串), 我没法替你创建 Neon / Supabase 实例。
- 解锁路径: 创建 Postgres 后把 connection string 放到安全环境变量, 或告诉我你已在平台配置。

[下一步]
卡住, 缺 DATABASE_URL; 你补好后我继续跑 prisma migrate + preview deploy。
```

### 例 3: 必须用户拍板

```text
[已完成]
- 三个候选部署方案对比文档 (.opc/deployment/options.md)

[证据]
- 三方案对比 Vercel / Cloudflare Pages / 自建, 含成本、CI 复杂度和回滚便利性。

[需要你拍板]
- 已打开宿主原生交互: 部署平台
- 推荐默认 = Vercel, 因为 Next.js 零配置、免费档够用
- 选择框含自定义入口

[下一步]
等你在原生交互提交后, 我按你的选择部署。
```

宿主原生结构化交互不可用时才降级为:

```text
[需要你拍板]
- A. Vercel (推荐)
- B. Cloudflare Pages
- C. 自建服务器
- D. 自定义 / type something
- 默认 = A

[下一步]
等你回 A/B/C/D 后继续部署。
```

## 反模式清单

- 收尾只列“剩余风险”不给行动方案。
- 不确定项没归类。
- 该自治的事推给用户拍板。
- `[下一步]` 段缺失。
- 用“你看呢 / 你定吧 / 看你的”替代具体选项。
- 拍板项不给默认值。
- 拍板项不给自定义 / type something 入口。
- 当前宿主有真实选择/确认交互时, 仍要求用户手打 A/B/C。
- 因为选择框一次只能承载少量问题, 就退回长文本问卷。
- 把已锁定的事反复当成“剩余风险”。
- 卡 token 时不给解锁路径。
- 自动推进的 turn 末尾没显式写“我现在做 X”。
- 用“我已经做了 X (具体不展开)”替代证据段。
- 跑了 `handoff-lint.py` 失败后绕过, 直接 mark done。
