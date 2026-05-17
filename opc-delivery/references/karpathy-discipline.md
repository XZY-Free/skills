# Karpathy 行为契约

把 Andrej Karpathy 关于 LLM 写代码常见毛病的四原则, 落到 OPC 一人公司式产品交付的每个阶段动作里。

来源: https://x.com/karpathy/status/2015883857489522876
全局基线: `~/.claude/CLAUDE.md` 和 `~/.codex/AGENTS.md` 的"模型行为四原则"小节。
本文件是 OPC skill 内的具体动作翻译, 不是抽象口号。

## 目录

- [为什么 OPC 需要这个契约](#为什么-opc-需要这个契约)
- [原则 1: 写代码之前先思考](#原则-1-写代码之前先思考)
- [原则 2: 优先简单](#原则-2-优先简单)
- [原则 3: 外科手术式修改](#原则-3-外科手术式修改)
- [原则 4: 目标驱动执行](#原则-4-目标驱动执行)
- [跟 OPC 既有契约的映射](#跟-opc-既有契约的映射)
- [反模式清单](#反模式清单)

## 为什么 OPC 需要这个契约

OPC 流程的失败模式跟 Karpathy 观察到的 LLM 毛病高度重合:

| Karpathy 观察到的 LLM 毛病 | 在 OPC 上的具体表现 |
|---|---|
| 乱假设 / 不澄清困惑 | 用户说"企业级", AI 默认含 RBAC + SSO + 审计, 写完 158 行 PRD 才在 Won't 段说"我没做 RBAC" |
| 过度抽象 / 单次抽象 | 三个 API route 抽出一个 BaseRouteHandler 基类 + 五个 DiscountStrategy 子类 |
| 顺手乱改无关代码 | 修 login bug 时顺手把整个 auth/ 目录改成新的 directory pattern |
| 弱目标 → 没法 loop | 用"让登录能用"当成功标准, 没写"哪个测试通过 = 完成" |

这四个毛病在 OPC 默认的"自动推进 + 大范围执行"模式下成本特别高: 一旦走偏, 下游 4-5 个阶段都跟着错。
因此 OPC 把这四条原则**前置到定义阶段**, 不到执行阶段才发现。

## 原则 1: 写代码之前先思考

**核心**: 不藏假设, 不藏困惑, 把 tradeoff 摆出来。

OPC 上的具体动作:

- **每个定义阶段第 1 轮 ConfirmCard 必须列默认假设**, 标"反对就说"。不允许写完 158 行 PRD 才在 Won't 段交代。这条在 [clarification-loop.md](clarification-loop.md) 的"默认假设暴露规则" 已强制。
- **用户用承诺性词时** ("企业级 / 完整 / 智能 / 生产级"), 第 1 轮必须翻译成具体清单让用户校准。见 [clarification-loop.md](clarification-loop.md) 的"用户 framing 解析"。
- **多种合理解释并存时全部列出**: 比如"做一个 dashboard" 可能是 (a) 业务运营后台 (b) 监控可视化 (c) 客户面板。ConfirmCard 把三种都列出来让用户选, 不要默默挑一种就写 PRD。
- **如果有更简单的方案明说**: 用户说"做一个 AI 客服系统", 如果 ChatGPT API 嵌入就够, 不要默默上 Agent 框架 + 向量库 + 多 agent 编排。在 ConfirmCard 写"我推荐 = 直接接 ChatGPT API + 简单工单存 SQLite; 完整 Agent 框架是 overkill, 除非你有多 LLM/工具调用需求"。
- **不清楚就停下问**: ConfirmCard 的"硬决策" 段就是这个机制。问题必须具体到"A / B / C 选一个", 不要开放式问 (跟 [handoff-contract.md](handoff-contract.md) 一致)。

收尾要求: 进入下一阶段前 [clarification-loop.md](clarification-loop.md) 的"推进与收敛判断"四条必须全部满足。

## 原则 2: 优先简单

**核心**: 用最少代码解决问题, 不为想象中的未来写代码。

OPC 上的具体动作:

- **不做 PRD 范围之外的功能**。PRD 没写"管理员后台" 就不要顺手做。Stage Card 的"主要范围裁剪" 字段就是给这个用的。
- **一次性代码不抽象**: 一个 page 只用一次的辅助函数, 直接写在 page 文件里, 不要拉到 `lib/utils`。三个相似 page 再考虑共享。
- **不写"未来可配置"**: 用户说"默认 SQLite", DB 配置就硬编码 SQLite, 不要默默搭一层 `DatabaseAdapter` interface "以后切 Postgres 容易"。要切的时候再切。
- **不为不可能场景写错误处理**: 内部函数被自己调用、输入已经 typed, 不需要 try/catch + zod parse + null check 三层。只在系统边界 (用户输入、外部 API、文件 IO) 做 validation。
- **200 行能 50 行就重写**: 写完一个 component / route handler / lib, 回头看一眼。如果资深工程师会说"这过度设计", 直接 rewrite。

OPC 已有的相关约束:

- [autonomous-bootstrap.md](autonomous-bootstrap.md) 的"自治补齐范围" — 缺前置才补, 不无中生有
- [solution-design.md](solution-design.md) 的"2-3 个方案对比" — 默认推荐最简方案, 复杂方案要给出理由
- [implementation-workflow.md](implementation-workflow.md) 的"复用现有工具和模式" — 引入新抽象前先看现有的能不能用

## 原则 3: 外科手术式修改

**核心**: 只动该动的, 只清理自己造成的烂摊子。

OPC 上的具体动作:

- **每一行 diff 都能追溯到本次任务**: 修登录 bug 时不顺手重命名 `auth/` 下其它文件; 改一个 API route 时不顺手把其它 routes 也换成新的 pattern。
- **不"美化" 邻近代码**: 看到 5 米外有不一致的命名、过时注释、可以简化的逻辑 — **提一句**, 不要顺手改。提的方式: 在 turn 收尾的"[不确定项 + 我的处理]" 段写"副观察: src/lib/auth.ts L42 命名不一致, 建议单独开 task 处理"。
- **不重构没坏的东西**: 这跟全局 CLAUDE.md "默认最优最干净" 的精神不矛盾 — 默认允许"必要重构", 但"必要 = 与本次任务有直接因果关系"。仅仅"路过看着不爽" 不算必要。
- **跟随现有风格**: 即使你更喜欢 `const arrow function` 而项目用 `function declaration`, 跟项目。
- **自己改动造成的孤儿**: 改完后 import 没用了、变量没引用了 — 清掉, 这是你的烂摊子。
- **既存的死代码**: 别动。除非用户要求"顺便清理一下"。

什么时候允许扩散到无关代码:

- 用户明确说"顺便清一下这个目录" / "重构这个模块"
- 不动它就改不了本次任务 (例: 要改 schema 必须同步迁移文件)
- Stage Card 或 PRD 写了"重构 X" 作为目标

**全局基线**: `~/.claude/CLAUDE.md` 和 `~/.codex/AGENTS.md` 的"编辑哲学" 已经覆盖了这条; OPC skill 内部不重复条款, 但要在执行阶段的 turn 收尾里检查"diff 是否扩散到无关代码"。

## 原则 4: 目标驱动执行

**核心**: 定义可验证的成功标准, 循环到通过为止。

OPC 上的具体动作:

- **Stage Card 的"验收方式"字段必须可执行**: 不要写"看起来对就行" / "用户满意", 写"pnpm test auth.spec.ts 通过" / "浏览器登录主链路截图存在" / "vercel preview URL 返回 200"。
- **PRD 的"验收标准"段必须可执行**: 同上。
- **修 bug 先写复现测试**: bug 修复任务的成功标准 = "复现 bug 的测试从红变绿 + 其它测试不变红"。先写测试, 再修。
- **加功能先写期望测试**: 新功能任务的成功标准 = "新写的测试通过 + 既有测试不变红"。
- **重构成功 = 测试不变红**: 重构任务的成功标准 = "覆盖目标代码的测试在重构前后都通过"。

多步任务的计划格式 (Stage Card 和 ConfirmCard 都适用):

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

OPC 已有相关机制:

- [open-source-patterns.md](open-source-patterns.md) 的 evidence-before-completion 模式
- [verification.md](verification.md) 的 3A / 3B 验证矩阵
- 上面所有"verify:" 检查都要落到 [handoff-contract.md](handoff-contract.md) 的"[证据]" 段里给用户看

## 跟 OPC 既有契约的映射

为避免重复条款, 下表列出本契约跟既有 OPC 契约的映射:

| Karpathy 原则 | 在 OPC 既有契约里的体现 |
|---|---|
| 1. 写代码之前先思考 | [clarification-loop.md](clarification-loop.md) 的"默认假设暴露规则" + "用户 framing 解析" + ConfirmCard 多轮讨论 |
| 2. 优先简单 | [solution-design.md](solution-design.md) 的"2-3 方案默认推最简" + [autonomous-bootstrap.md](autonomous-bootstrap.md) 的"只补缺的前置不无中生有" |
| 3. 外科手术式修改 | 主要靠 `~/.claude/CLAUDE.md` 和 `~/.codex/AGENTS.md` 全局基线 + [handoff-contract.md](handoff-contract.md) 的 turn 收尾检查 |
| 4. 目标驱动执行 | [open-source-patterns.md](open-source-patterns.md) 的 evidence-before-completion + [verification.md](verification.md) 的 3A/3B + [handoff-contract.md](handoff-contract.md) 的"[证据]" 段强制 |

## 反模式清单

在 OPC 上看到下面这些做法, 就是违反 Karpathy 行为契约:

- ❌ 用户说"做一个企业级用户中心", AI 不写 ConfirmCard 翻译 framing, 直接默认含 RBAC + SSO + 审计 + 多租户 + 计费
- ❌ 实现单个 API route 时为"以后好扩展" 抽出 `BaseRouteHandler` 基类
- ❌ 修一行 typo 时顺手把整个文件的命名风格改成自己喜欢的
- ❌ Stage Card "验收方式" 字段写"看起来可用" 而不是具体命令 / 测试
- ❌ 给 PRD 范围内没有的"超级管理员后台" 顺手做了一份
- ❌ 看到现有代码"过度抽象" 不在 ConfirmCard 里跟用户聊就默默重写
- ❌ ConfirmCard 抛硬决策时用"你看呢" 而不是"A / B / C 选一个 + 我推 A"
- ❌ 收尾时不给"[证据]" 段, 只说"完成了"
- ❌ 写"未来可配置 / 灵活扩展" 的抽象层, 但当前 PRD 根本不需要
- ❌ 内部函数加 try/catch + zod parse 三层防御, 输入根本不会越界
