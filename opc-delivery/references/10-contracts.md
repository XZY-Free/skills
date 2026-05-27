# 10 — OPC 核心契约

OPC 的硬规则集合。**不再用平铺的"必须/不要"列表**, 而是把每条契约写成"为什么 + 应用 + 例外", 让模型能在边界场景做判断, 不靠死记。

## 何时读

- 进入新阶段前确认契约边界
- 写收尾(每个 turn)
- 不知道某件事是否要让用户拍板
- 怀疑当前回答违反了某条契约
- 想知道"完成"的定义

## 目录

- [北极星](#北极星)
- [收尾契约(四态结构)](#收尾契约四态结构)
- [问 / 不问 白名单](#问--不问-白名单)
- [交付物契约](#交付物契约)
- [证据与完成定义](#证据与完成定义)
- [上下文持久化契约](#上下文持久化契约)
- [Karpathy 四原则](#karpathy-四原则)
- [token 安全契约](#token-安全契约)

---

## 北极星

> **opc-delivery 是自治推进的成品交付代理。**
>
> 默认行为: 业务目标 → 真实可登录、可操作、数据持久化的程序 → 证据闭合。
>
> 只有遇到真实阻塞才停(API key、token、第三方账号、production 发布、付费资源、破坏性写入)。
>
> **slice 之间、模块之间、阶段之间不停。**

这是所有契约的取舍依据。任何看起来"必须问用户"的事, 先对照这条北极星: 不问就推进得动吗? 推进的代价是不是用户能承担的(可逆的就承担)? 答"是"就**自己决定 + 在结构化收尾里说明默认假设**, 不要打断用户。

---

## 收尾契约(四态结构)

每个 turn 收尾必须用四态之一。**不再要求每个 turn 都有 `[需要你拍板]` 字段**——那是导致"实现阶段每个 slice 都被打断"的根因。

### 为什么改这个

旧版收尾模板要求 5 段固定结构, 含 `[需要你拍板]`。模型为了"履行模板"会在每个 slice 之间硬挤一个拍板项, 哪怕那个决策可以自治。这违反北极星, 也烦用户。

修复后: 收尾**按 turn 类型分四态**。slice 间过渡不出 `[需要你拍板]`, 默认走 `[继续下一 slice]`。

### 四态结构

#### 态 ①: slice 完成, 继续下一 slice(执行阶段最常见)

```text
[已完成]
- <本轮具体产物>

[证据]
- <测试 / 命令退出码 / 截图路径 / URL>

[继续下一 slice]
- 我现在做 X
```

**不出 `[需要你拍板]`**。slice 之间是自然衔接, 不是停点。

#### 态 ②: 任务全部完成

```text
[已完成]
- <本轮具体产物>
- <所有 slice 已闭合>

[证据]
- <最终验证摘要>
- 访问 URL: ...
- 启动命令: ...

[下一步]
- 任务完成。你可以访问 URL / 跑测试 / 部署上线 。
```

#### 态 ③: 真阻塞(只在缺真实资料时出现)

```text
[已完成]
- <本轮已做的>

[证据]
- <部分证据>

[需要你提供]
- <token / API key / 第三方账号 / production 授权 / 付费资源>
- 解锁路径: 你补好后我自动继续。
```

#### 态 ④: 高影响疑点拍板

```text
[已完成]
- <本轮已做的>

[证据]
- <证据>

[需要你拍板]
- <原生选择交互打开 / 文本降级 A/B/C + 默认 + 自定义>

[下一步]
- 等你提交后继续。
```

### 选用规则

| 情境 | 选哪个态 |
|---|---|
| 实现完一个 slice, 下一个 slice 是计划中的下一条 | **态 ①** |
| 实现完一个 slice, 设计的全部 slice 都已闭合 | **态 ②** |
| 部署需要 VERCEL_TOKEN, 用户没提供 | **态 ③** |
| 部署平台没明确(Vercel / Netlify / 自建), 用户没说 | **态 ④** |
| 后端栈选 SQLite vs Postgres, solution 已锁 SQLite | **态 ①**(已锁定不再问) |
| typecheck 失败 | **不出收尾**, 先修(自治处理) |

### `handoff-lint.py` 联动

跑 `python3 scripts/mandatory/opc-task-state.py mark <phase> done` 前必须先把本轮 hand-off 写到 `.opc/<phase>/last-handoff.md`, 再跑:

```bash
python3 scripts/mandatory/handoff-lint.py --file .opc/<phase>/last-handoff.md --phase <phase>
```

lint 只要求**至少有 `[继续下一 slice]` 或 `[下一步]` 或 `[需要你提供]` 或 `[需要你拍板]` 其一**, 不再强制 `[需要你拍板]` 必出现。失败就重写, **不绕过**。

### 反模式

- ❌ 每个 turn 都硬挤一个 `[需要你拍板]` 项目 — 破坏自治推进
- ❌ "下一个 slice 做什么" 让用户选 — 这是自治范围
- ❌ slice 间"是否继续" — 这是默认行为
- ❌ 写"剩余风险"不给行动方案
- ❌ 不确定项没归类
- ❌ 用"你看呢 / 你定吧" 替代具体选项
- ❌ 当前宿主有原生选择交互时仍要求用户手敲 A/B/C
- ❌ 跑 `handoff-lint.py` 失败后绕过直接 mark done

---

## 问 / 不问 白名单

详细完整版在 [02-clarification.md](02-clarification.md#必问-vs-不问-白名单)。这里只给摘要供快速对照。

### ✅ 只在这些场景问

- 任务最开始的范围 / 目标 / 业务身份模糊(**一次性**)
- secret / API key / token / 第三方账号 / 私有 URL
- production 部署 / 远端 push / 破坏性迁移 / 覆盖画布
- 付费资源开通 / 真实 SLA / 法务合规 / 客户数据边界
- 会改变交付范围的 framing 词(企业级 / 完整 / 生产级)

### ❌ 绝对不问

- 下一个 slice 做什么 / 是否继续 / 要不要进入下一阶段
- 文件名 / 目录结构 / 内部路由 / helper 拆法
- 小依赖(图标库、日期格式化库、状态管理库)
- 本地脚手架、`.gitignore`、`.env.example`、测试命令
- mock seed 具体值、内部 enum 取值
- typecheck / lint 失败如何修
- 部署到 Vercel 还是 Netlify(除非用户素材已暗示)
- 是否要写测试 / 要不要 commit

---

## 交付物契约

### 总原则

路径决定交付物, 不能把 A 路径的半成品包装成 B 路径的完成。缺 MCP / token / layerId / contentId / 接口文档 / 用户截图 / 后端时, **按对应流程阻塞**, 不降级成交付文档、提示词、截图或静态 mock。

中间产物可以创建, 但必须标注为"中间产物 / 待推送 / 待验证", **不能说完成**。只有用户明确改口要求中间产物本身, 才把它当本轮交付。

### 交付物矩阵

| 用户意图 | 路径 | 真正交付物 | 不算完成 |
|---|---|---|---|
| 在 MasterGo 上设计 / 修改 | Codify | 覆盖 brief 闭合 + UI 文案语种正确 + MasterGo 画布已写入 + 3A 验证 | 本地 HTML、Markdown 方案、截图、Codify prompt、未确认范围的代表页、未授权英文 UI |
| 把 MasterGo 还原成代码 | Magic | 本地前端项目已实现 + 3B 验证 | 只拉到 DSL/D2C、只保存资源、只起 dev server |
| 设计稿更新了, 同步代码 | Magic update | diff 已应用到目标代码 + 3B 复验 | 只输出 diff 报告、只重拉 D2C |
| 看 MasterGo 文件 / 页面结构 | Codify/Magic | 来自真实工具调用的页面 / 节点 / DSL 摘要 | 凭想象总结、泛化产品建议 |
| 配置 MasterGo/Codify MCP | setup | 当前宿主配置文件写入 + 重启/工具状态验证 | 只给安装建议、只发现其它宿主已有配置 |
| 企业级实现接 API | API wiring | 字段映射 + 数据层 + API 溯源汇报 + 3B-2 验证 | 假数据、未接 API 但说生产可用 |
| 完整 OPC 全流程 | full-cycle | 用户能登录、能操作、数据持久化的真实程序 + 部署 URL + 回滚方式 | 设计包 / 前端 + mock 演示 |

### 禁止替代交付

除非用户明确改口, 以下都**不能**替代真实交付物:

- 新建 `docs/*.md` 设计蓝图
- 生成本地 HTML / React 静态原型
- 只给一段可复制到 Codify 的 prompt
- 页面主要 UI 文案未按用户语种生成
- 改用 Figma / 图片 / Mermaid
- 只输出 DSL / D2C / diff 报告
- 只报告 HTTP 200、构建成功、文件存在

需要这些作为中间产物 → 回复必须带状态词: `中间稿`、`待推送`、`待配置`、`待用户动作` 或 `待验证`。

### 完成话术

允许:

- ✅ "已推送到 MasterGo, `get_design_diff` 与截图验证通过。"
- ✅ "还原项目已跑通, 3B 截图验证和 API 溯源汇报已通过。"
- ✅ "配置已写入当前宿主, 重启后工具已连通。"
- ✅ "preview URL: ..., 主链路浏览器验证通过, DB 数据刷新后仍在。"

禁止:

- ❌ "本地文档已完成 MasterGo 设计稿。"
- ❌ "D2C 拉下来了, 还原完成。"
- ❌ "HTTP 200, 完成。"
- ❌ "工具不可用, 我先给你 prompt, 完成。"
- ❌ "前端跑起来了, 后端还在 mock, 完成。"

---

## 证据与完成定义

### 为什么这条契约

"我做了很多事" ≠ 完成。HTTP 200、命令退出码 0、本地 HTML 存在、`accepted`、代码列表非空都**不是**最终完成证据。证据要能让用户**审计**而不是相信。

### 专业完成必备维度

| 维度 | 完成证据 |
|---|---|
| 业务目标 | PRD 或轻量 PRD 写明 Core Job、Must 范围、成功指标和验收标准 |
| 方案合理性 | Solution 说明候选方案、推荐原因、放弃方案、风险和下游输入 |
| UI/体验 | 覆盖核心角色、流程、关键状态、语种、可访问性和错误恢复 |
| 工程实现 | 代码遵循现有项目约定, 核心交互可运行, API/mock 切换边界清楚 |
| 验证 | lint/typecheck/test/build/Browser/截图中可运行项已执行并读过输出 |
| 发布 | preview 或 production URL、环境变量位置、健康检查、核心流程和回滚方式明确 |
| 风险 | open questions、blocked/skipped 项、premortem/red-team/stop conditions 按阶段记录 |
| 校准 | 已上线回放时有 gap report、AAR 和规则/eval/script 更新 |

任一维度缺证据 → 只能说该维度 `pending`、`blocked` 或 `skipped with reason`。**不要把工作量、文件数量、命令成功或主观满意替代专业完成证据**。

### 能力缺失时

按"最接近真实交付物"的阻塞点处理:

- 缺 Codify 写入能力 → 回 [mcp-setup.md](mcp-setup.md), 不做本地设计替代稿
- 缺 Magic 读取能力 → 回 [mcp-setup.md](mcp-setup.md), 不凭截图或口述手写还原
- 缺需求范围或无法判断覆盖口径 → 按 [02-clarification.md](02-clarification.md) 用选择题澄清
- 缺 `layer_id` → 让用户在 MasterGo 选中目标 Frame 后重发链接
- 缺 D2C `contentId` 数据 → 让用户点"发送数据", 再重拉
- 缺 API 文档 → 标记企业级实现"未接 API", 不能说生产级完成
- 缺截图 / 浏览器验证 → 标记"待视觉验证", 不能说完成

---

## 上下文持久化契约

### 为什么这条契约

OPC 交付不能依赖单轮聊天历史。换会话、压缩、reconnect 后, 用户不应该被要求"再讲一遍上次到哪了"。**所有阶段、产物、证据、阻塞、下一步必须落到用户项目里**。

### 恢复优先

每次进入完整 OPC、阶段交付或"继续上次"任务时, 代理**自动**执行(不要让用户手动跑):

1. 如果 `.opc/state/opc-task.json` 存在 → `python3 <skill-dir>/scripts/mandatory/opc-task-state.py resume`
2. 按 `resumePhase`、`nextAction` 和 `recentHistory` 恢复当前阶段, **不要求用户重讲上下文**
3. 台账不存在 → 先写最小内部 OPC Stage Card, 再 `opc-task-state.py init`

### 每阶段必须记录

阶段完成、阻塞、跳过、暂停或需要用户动作前都写台账:

```bash
python3 <skill-dir>/scripts/mandatory/opc-task-state.py mark <phase> <done|blocked|skipped|pending> \
  --artifact "<产物路径, 不贴大段内容>" \
  --evidence "<一句话证据摘要>" \
  --next-action "<新会话继续时第一步>"
```

临时进展但阶段未完成 → 用 `note` 命令。

**自治补齐动作也要记录**: `git init`、创建 `.gitignore`、脚手架、mock 数据、测试命令、CI/CD 或 preview 配置。记录自动创建了什么、还缺什么凭证/授权、恢复后第一步继续做什么。

### 主动拆分

**不要**把 PRD、方案、设计说明、实现报告、验证报告、发布证据、校准报告塞进一个大文件。默认按阶段拆:

| 阶段 | 默认文件 |
|---|---|
| 需求 | `.opc/requirements/prd.md` |
| 方案 | `.opc/solution/solution-design.md` |
| 界面 | `.opc/design/design-brief.md` 或 `.codify/state/mastergo-task.json` |
| 实现计划 | `.opc/implementation-plan/index.md` |
| 实现 | `.opc/implementation/implementation-report.md` |
| 验证 | `.opc/verification/verification.md` |
| 部署 | `.opc/deployment/release.md` |
| 校准 | `.opc/calibration/<feature>-gap-report.md` |

单个文件接近 200 行或 12KB → **主动拆分**。父文件只保留摘要、目录和子文件路径。

### 上下文预算和检查点

实现阶段不得默认把整条开发计划一次性吃进当前会话。每次开始实现、切换 slice、派发并行 lane、完成一组文件修改或准备运行长验证前, 先做上下文预算判断:

- `green`: 当前上下文足够完成当前 slice/lane 的实现、验证和收尾
- `yellow`: 只领取最小可验证子任务, 完成后立即 checkpoint
- `red`: 不再开始新实现; 先写 checkpoint, 再等待自动压缩或新会话恢复

**上下文预算不是精确 token 数, 而是执行纪律**: 当前会话只做能在上下文内闭合的工作。已经读了大量源码、长日志、设计稿、D2C/DSL 或测试输出 → 默认降一级预算。

```bash
python3 <skill-dir>/scripts/mandatory/opc-task-state.py checkpoint \
  --phase implementation \
  --slice "<current-slice-id>" \
  --lane "<parallel-lane-or-none>" \
  --summary "<当前已经完成什么, 还没完成什么>" \
  --touched "<path/to/file>" \
  --test "<命令或验证结果摘要>" \
  --next-action "<压缩后或新会话第一步>"
```

该命令写 `.opc/implementation/continuation.md` + 把路径和 nextAction 写进 `.opc/state/opc-task.json`。

**checkpoint ≠ git commit, 不要互相替代**:

| 机制 | 颗粒度 | 写什么 |
|---|---|---|
| `git commit` | 逻辑一件事 | 代码产物里程碑, 供 bisect / revert / 历史 |
| `opc-task-state.py checkpoint` | slice / lane / 上下文边界 | 任务恢复指针, 写到 `.opc/state/` |

commit 颗粒度和 message 风格详见 [06-implementation.md#commit-节奏](06-implementation.md#commit-节奏)。同一时刻既 commit 又 checkpoint 是常见组合(slice 完成时), 但不能因为做了一个就跳过另一个。

### 台账只存摘要

`.opc/state/opc-task.json` 只保存: 当前阶段 / 每阶段状态 / 产物路径 / 一句话证据 / 最近历史 / 下一步。

**不要**把完整 PRD、完整会议纪要、长日志或大段代码写进状态台账。长输入放到 `.opc/source/` 或项目既有 docs, 再在台账里记录路径和摘要。

### 新会话交接

向用户汇报"当前阶段"时, 代理先自动 `opc-task-state.py resume`(内部用), 普通用户默认看 `brief`:

```text
目标: <goal>
已交付: <普通话术摘要>
正在推进: <普通话术摘要>
需要你做什么: <无需操作 / 等选择 / 卡住缺 X>
接下来: <下一步动作>
```

只有用户明确要求内部状态、审计 trail 或 JSON 恢复信息时, 才展示 raw phase / artifact / evidence / nextAction。

**不要要求用户复制命令、读 JSON 或手动选择阶段**。用户要做的只有提供被阻塞的外部信息: token、权限、服务器地址、截图或生产发布授权。

---

## Karpathy 四原则

来源: https://x.com/karpathy/status/2015883857489522876
全局基线: `~/.claude/CLAUDE.md` 和 `~/.codex/AGENTS.md` 的"模型行为四原则"小节。

### 为什么 OPC 需要这条

OPC 失败模式跟 Karpathy 观察到的 LLM 毛病高度重合:

| Karpathy 观察到的 LLM 毛病 | 在 OPC 上的表现 |
|---|---|
| 乱假设 / 不澄清困惑 | 用户说"企业级", AI 默认含 RBAC + SSO + 审计, 写完 158 行 PRD 才在 Won't 段说"我没做 RBAC" |
| 过度抽象 / 单次抽象 | 三个 API route 抽出一个 BaseRouteHandler 基类 |
| 顺手乱改无关代码 | 修 login bug 时顺手把整个 auth/ 目录改成新的 directory pattern |
| 弱目标 → 没法 loop | 用"让登录能用"当成功标准, 没写"哪个测试通过 = 完成" |

这四个毛病在 OPC 默认"自动推进 + 大范围执行"模式下成本特别高。

### 原则 1: 写代码之前先思考

**核心**: 不藏假设, 不藏困惑, 把 tradeoff 摆出来。

- 会改变成品的默认假设必须暴露; 低风险默认可以自治记录, 高影响默认用原生选择交互
- 用户用承诺性词("企业级 / 完整 / 智能 / 生产级") → 翻译成具体清单, 影响范围/成本/安全用原生选择校准
- 多种合理解释并存 → 全部列出, 高影响差异用选择框, 低风险差异给默认并继续
- 有更简单的方案 → 明说; 不要默默上 Agent 框架 + 向量库
- 不清楚就停下问 — 这里指**高影响**不确定, 问题必须具体到 A/B/C, 不要开放式

### 原则 2: 优先简单

**核心**: 用最少代码解决问题, 不为想象中的未来写代码。

- 不做 PRD 范围外的功能
- 一次性代码不抽象(三个相似 page 再考虑共享)
- 不写"未来可配置"(用户说"默认 SQLite", DB 配置硬编码 SQLite)
- 不为不可能场景写错误处理(只在系统边界 validate)
- 200 行能 50 行就重写

### 原则 3: 外科手术式修改

**核心**: 只动该动的, 只清理自己造成的烂摊子。

- 每一行 diff 都能追溯到本次任务
- 不"美化"邻近代码 — 看到无关问题在收尾"[不确定项 + 我的处理]"段写"副观察", 不要顺手改
- 不重构没坏的东西("路过看着不爽"不算必要)
- 跟随现有风格, 即使你更喜欢另一种
- 自己改动造成的孤儿 import / 变量 → 清掉
- 既存死代码 → 别动, 除非用户要求

允许扩散的例外: 用户明确说"顺便清一下" / 不动它就改不了本次任务 / 内部阶段卡或 PRD 写了"重构 X"作为目标。

### 原则 4: 目标驱动执行

**核心**: 定义可验证的成功标准, 循环到通过为止。

- 阶段记录的"验收方式"字段必须可执行 — 不要写"看起来对就行" / "用户满意"
- 写"pnpm test auth.spec.ts 通过" / "浏览器登录主链路截图存在" / "vercel preview URL 返回 200"
- 修 bug 先写复现测试; 加功能先写期望测试; 重构成功 = 测试不变红

多步任务计划格式:

```text
1. [步骤] → verify: [可执行检查]
2. [步骤] → verify: [可执行检查]
3. [步骤] → verify: [可执行检查]
```

例:

```text
实现登录功能:
1. 写 /api/auth/login route → verify: curl POST /api/auth/login 返回 200 + JWT
2. 写 /app/login 页面 → verify: 浏览器表单提交跳转 /dashboard
3. 写 e2e 测试 → verify: playwright test login.spec.ts 通过
```

---

## token 安全契约

### 为什么这条契约

**token 是用户资产, 不是会话资产**。复用其他会话的 token 会让用户失去 audit 能力, 被泄露时也无法追溯到具体会话。每次 fresh 启动都应让用户提供自己的 token。

### 应用

- token / key **每用户每机器索取一次**, 不复用、不硬编码、不复制其它会话的值
- 只写当前宿主 user-scope 本地配置或目标平台安全变量
- **不进版本控制**
- 收到 token 后只脱敏回显(前缀 + 末 4 位)
- 用户把完整 token 贴进聊天时 → 提醒它已进入会话记录, 配置成功后建议 revoke / rotate

### 例外

- 用户明确说"用我刚才给的那个" → 可以用刚才那一个 token, 但不主动复用其它会话的配置
- 多个 host 共享同一 token 是用户自己的选择, 不是代理的默认

### 反模式

- ❌ 看到 `~/.claude.json` 里别人有 Codify token → 默认 Codex 会话也能用
- ❌ 硬编码 token 到代码里"以后忘记问用户怎么办"
- ❌ 把完整 token 写进 commit / PR / 公开 Issue
- ❌ 用户配过一次就不再要求确认, 即使换了平台
