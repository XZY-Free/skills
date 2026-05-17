# 收尾契约

每个 turn 收尾的强制结构。覆盖 `~/.codex/AGENTS.md` 工作约定中关于"最终报告必须包含...剩余风险"的默认形态。

## 目录

- [为什么需要这个契约](#为什么需要这个契约)
- [反模式: 剩余风险三连](#反模式-剩余风险三连)
- [正模式: 五段式收尾](#正模式-五段式收尾)
- [不确定项三分类](#不确定项三分类)
- [显式下一步句式](#显式下一步句式)
- [自治推进 vs. 必须用户拍板](#自治推进-vs-必须用户拍板)
- [跟 opc-task-state.py mark 的联动](#跟-opc-task-statepy-mark-的联动)
- [例子](#例子)
- [反模式清单](#反模式清单)

## 为什么需要这个契约

"剩余风险" 单甩给用户是反模式:

- 用户不知道接下来要不要应对、怎么应对
- AI 看似负责 (列了风险), 实际把 routing 责任推回用户
- 对话停在这里, 没人推下一阶段
- Codex 默认收尾习惯就是这样, 形成"汇报+停"的肌肉记忆

Karpathy 第 1 条"不要藏起困惑, 主动暴露 tradeoff" 实际意思不是"甩一堆开放风险等用户决定", 而是"列出选项让用户选, 或给出默认 + 自动继续"。

所以 OPC 在每个 turn 收尾时, 不允许只回一句"完成, 剩余风险 a/b/c"。

## 反模式: 剩余风险三连

不要这样收尾:

```text
❌ 已实现登录页。
   剩余风险:
   - API mock 没接真实后端
   - CI 还没跑
   - 部署目标没定
```

为什么烂:

- "API mock 没接真实后端" 是 (a) 我下一步会接 (b) 等你说要不要接 (c) 已经标记 mock 就完了 — 这三种状态在 AI 嘴里长得一样, 用户必须再问一遍
- "CI 还没跑" 是 (a) 我马上跑 (b) 跑了但失败 (c) 跑不了因为缺凭证 — 同样需要再问
- "部署目标没定" 是 (a) Stage Card 已经选了我没看 (b) 真的没聊 (c) 卡在等你回话 — 同样

用户每收到一句"剩余风险" 就要回一句"那然后呢", 等于把推进责任完全推回去。

## 正模式: 五段式收尾

每个 turn (定义阶段每轮 ConfirmCard、执行阶段每段汇报) 收尾必须满足下面五段。
不是每段都强制有内容, 但段的边界要清楚, 用户能快速识别"我需不需要回话":

```text
✅ [已完成]
   - 登录页 (src/app/login/page.tsx, 截图 .opc/implementation/screenshots/login.png)
   - /api/auth route (Prisma user schema + JWT)

   [证据]
   - pnpm typecheck: 0 errors
   - pnpm test auth.spec.ts: 8 passed
   - 浏览器: localhost:3000/login 主链路通过

   [不确定项 + 我的处理]
   - 真后端 vs mock: Stage Card 已锁"真后端", 我已接通; 如果你说"演示用" 我才回退 mock。
   - CI: 已加 pnpm test 到 .github/workflows/ci.yml (commit abc123); 下次 push 触发, 这轮无凭证不跑。
   - 部署目标: 这轮未触及, 进入 deployment 阶段我再开 ConfirmCard 问你 Vercel / Cloudflare / 自建。

   [下一步]
   我现在进入实现阶段第 2 步: 接真后端 + e2e 跑通。
   你不反对就开始。
```

每段都有明确边界:

| 段 | 必填? | 内容 |
|---|---|---|
| `[已完成]` | 是 | 本轮做了什么具体事 (产物路径 / commit / 截图) |
| `[证据]` | 执行阶段必填 | 测试通过 / 命令退出 0 / 截图 / URL / `get_design_diff` 输出 |
| `[不确定项 + 我的处理]` | 是 (有不确定项时) | 每条必须归类: 自治处理 / 需要拍板 / 卡住缺 X |
| `[需要你拍板]` | 仅在需要时 | 列具体 A / B / C 选项, 标默认, 保留"自定义 / type something"; 禁止"你看呢" |
| `[下一步]` | 是 | 显式写"我现在做 X" / "等你回 A/B/C" / "卡住, 缺 X" 之一 |

定义阶段 (intake / requirements / solution / ui-design) 的 ConfirmCard 也走这个结构, 只是
`[已完成]` 段可能写"列了 N 个默认假设供你校准", `[证据]` 段对应"讨论日志 .opc/<phase>/discussion.md 第 N 轮"。

## 不确定项三分类

每个不确定项必须能归到下面三类之一:

| 类别 | 标识词 | 行动 |
|---|---|---|
| **自治处理** | "我已默认处理" / "我下一步处理" / "我已 mitigation" | AI 已做或马上做, 用户不必决策。给出已做的证据或下一步动作。|
| **需要用户拍板** | "需要你拍板" + 2-3 个具体选项 | 不允许开放式"你看呢"。必须列具体可选项 (默认 + 备选 + 自定义), 标默认。|
| **硬阻塞** | "卡住, 缺 X" + 解锁路径 | 缺 token / 凭证 / 付费资源时, 写明缺什么、怎么补、补完后会自动继续。|

任何不确定项必须能归到一类。如果归不到, 说明 AI 自己还没想清楚, 不要丢给用户。

判断归到哪类的两条线:

**自治处理 (默认这个挡位)**:

- 小依赖选型, 文件命名, helper 拆法, 内部路由, mock seed 值, 单文件内代码组织
- 已被 Stage Card / ConfirmCard 锁定过的项 (即使本轮没具体执行)
- 测试 / lint / build / dev server 启动这类无副作用的工具调用
- 默认假设暴露规则里属于"低赌注" 类目的事 (见 [clarification-loop.md](clarification-loop.md))

**必须用户拍板**:

- API key / token / secret / 私有 URL / 服务器地址 / 账号权限
- production 部署, 远端 push, 覆盖 MasterGo 画布, 覆盖已有服务器或数据库, 破坏性迁移
- 付费资源, 采购, 外部服务开通
- 修改 Stage Card 或 ConfirmCard 已锁定的项 (反悔大决策)
- 法务 / 合规 / 客户数据范围 / 真实 SLA
- 用户 framing 还有歧义且影响交付范围

**禁止把可自治的事推给用户拍板**: 那是把活推回去, 不是负责任。

## 显式下一步句式

每个 turn 必须以下面之一收尾, **不允许省略**, **不允许模糊**:

- `我现在做 X` — 自治推进, 没有等用户的事
- `我现在做 X, 同时等你回 A/B/C 哪个` — 自治推进 + 一个具体决策
- `等你回 A/B/C 哪个再继续` — 必须拍板才能进行
- `卡住, 缺 X, 你补好后我自动继续` — 硬阻塞 + 解锁路径

省略下一步 = "对话停在用户手里, 用户不知道接什么", 是反模式。
模糊下一步 (如"看你的"、"你定吧"、"看情况") 同样反模式。

## 自治推进 vs. 必须用户拍板

定义阶段 (intake / requirements / solution / ui-design) 的"必须拍板" 默认门槛高 — 大部分决策都要拍板。
执行阶段 (implementation / verification / deployment / calibration) 的"必须拍板" 默认门槛低 — 大部分决策可自治。

判定 ladder (从最低门槛到最高门槛):

```text
自动继续  ──→  default + 自治  ──→  default + 短拍板  ──→  必须拍板  ──→  硬阻塞
   ▲                                                                          │
   │                                                                          ▼
完全自治                                                          只能等用户 / 缺凭证
```

- **自动继续**: 已锁过的事 + 无副作用的工具调用 → 不需要"[不确定项]" 段
- **default + 自治**: 我替用户默认了 X, 反对就说; 默认能跑就跑 → 写进"[不确定项 + 我的处理]" 段
- **default + 短拍板**: 我推 A, 但用户简短确认更稳妥 → 写"等你回 A 还是 B/C" 但默认走 A
- **必须拍板**: 见上面"必须用户拍板" 类目 → 写"[需要你拍板]" 段, 列 A/B/C + 默认 + 自定义入口, 必须等回话
- **硬阻塞**: 缺 token / 凭证 / 付费资源 → 写"[卡住]" 段 + 解锁路径

## 跟 opc-task-state.py mark 的联动

AI 在跑 `python scripts/opc-task-state.py mark <phase> done` 之前, 必须先把本轮 hand-off
文本跑过 `scripts/handoff-lint.py` 校验:

```bash
# 把本轮 hand-off 写到文件 (或通过 stdin)
echo "<本轮回答>" > .opc/<phase>/last-handoff.md
python scripts/handoff-lint.py --file .opc/<phase>/last-handoff.md --phase <phase>

# lint 通过 → mark done
python scripts/opc-task-state.py mark <phase> done --evidence "..." --artifact "..."

# lint 不通过 → 重写 hand-off, 不要绕过 lint
```

`handoff-lint.py` 是阶段标 done 的前置 gate。lint 失败意味着这轮收尾不合格, 必须重写。
**不要用"我下次改" 之类的承诺绕过 lint。**

## 例子

### 例 1: 实现阶段中段汇报 (自治推进)

```text
[已完成]
- /api/projects route (POST / GET / PATCH)
- Prisma project schema 迁移

[证据]
- pnpm test projects.spec.ts: 5 passed
- curl localhost:3000/api/projects 返回 200 + 真实数据

[不确定项 + 我的处理]
- 软删除 vs 硬删除: 我默认走软删除 (deletedAt 字段), 如果你说"我就要硬删" 再改。
- 列表分页: PRD 没说, 我默认 limit=20 offset 分页, ConfirmCard 锁的"无大数据量" 前提下够用。

[下一步]
我现在做 /app/projects 前端列表页 + 跑通增删改主链路。
```

### 例 2: 卡 token (硬阻塞)

```text
[已完成]
- Vercel preview 项目已创建
- .env.example 已生成

[证据]
- vercel link OK
- vercel projects ls 显示项目

[卡住]
- 部署需要 DATABASE_URL (Postgres 连接串), 我没法替你创建 Neon / Supabase 实例。
- 解锁路径:
  (1) 去 neon.tech 创建免费 Postgres → 复制 connection string → 贴这里
  (2) 或者你自己跑 `vercel env add DATABASE_URL preview` 后告诉我已加完

[下一步]
等你补 DATABASE_URL, 我立即跑 prisma migrate + 触发首次 preview deploy。
```

### 例 3: 必须用户拍板 (大决策)

```text
[已完成]
- 三个候选部署方案对比文档 (.opc/deployment/options.md)

[证据]
- 三方案对比 Vercel / Cloudflare Pages / 自建 (CDN + Docker)
- 各有成本、CI 复杂度、回滚便利性评估

[需要你拍板]
- A. Vercel (推荐, 零配置, 5 分钟上线, 免费档够用)
- B. Cloudflare Pages (适合 static 主导, edge 函数 cold start 短)
- C. 自建 (适合需要内网部署或合规要求)
- D. 自定义 / type something
- 默认 = A; 你不反对我 30 分钟内按 A 推进

[下一步]
等你回 A/B/C/D 或不反对自动走 A。
```

### 例 4: 定义阶段 ConfirmCard 收尾

```text
[已完成]
- requirements 阶段第 2 轮 ConfirmCard 已抛出
- discussion log 更新到 .opc/requirements/discussion.md 第 2 轮

[证据]
- 第 1 轮你确认了 "企业级 = 多模型接入 + Key 管理 + 应用编排 + Playground; 不含 RBAC/SSO/审计"
- 第 2 轮我列了 5 个剩余默认假设 + 2 个硬决策

[不确定项 + 我的处理]
- 数据源默认假设你只对 1 个有异议 (DB 用 Postgres 不是 SQLite), 我会更新假设, 不需要再讨论
- 测试策略默认假设你没回应, 我默认沿用 lint + typecheck + build + 浏览器主链路

[需要你拍板]
- A. 模型 Provider = OpenAI + Anthropic, 应用编排 = 简单链式 (推荐)
- B. 模型 Provider 再加 Gemini, 应用编排仍走简单链式
- C. 应用编排升级为 LangGraph 状态机
- D. 自定义 / type something
- 默认 = A

[下一步]
等你回 A/B/C/D (或不反对默认), 我落 PRD 进入方案阶段。
```

## 反模式清单

下面这些做法都违反本契约:

- ❌ 收尾只列"剩余风险: a / b / c" 不给行动方案
- ❌ 不确定项没归类 (不知道是自治、拍板还是阻塞)
- ❌ 该自治的事 (比如选 lucide-react 还是 heroicons) 推给用户拍板
- ❌ `[下一步]` 段缺失, 对话停在用户手里
- ❌ 用"你看呢 / 你定吧 / 看你的" 这种开放式问句替代具体选项
- ❌ 拍板项不给默认值 (强迫用户从零思考)
- ❌ 拍板项不给自定义 / type something 入口 (预设答案空间封闭)
- ❌ 把已被 Stage Card / ConfirmCard 锁定的事再翻一遍 "剩余风险"
- ❌ 卡 token 时不给解锁路径, 只说"缺凭证"
- ❌ 自动推进的 turn 末尾没显式宣告 "我现在做 X" (Codex 容易因此停下)
- ❌ 用"我已经做了 X (具体不展开)" 替代证据段 — 证据必须给路径 / 命令 / 截图 / URL
- ❌ 跑了 `handoff-lint.py` 失败后用"我下次注意" 绕过, 直接 mark done
