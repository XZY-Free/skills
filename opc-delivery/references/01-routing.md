# 01 — OPC 路由与阶段链路

把粗需求路由到正确阶段, 并保证每阶段都有可验证交付物。OPC 的用户侧模型是**成品驱动 / 疑点触发确认 / 证据驱动完成**。

## 何时读

- 每个新任务入口
- 中途切换路径(设计 → 还原 / 阶段恢复)
- 不确定是 Codify(画布生产)还是 Magic(画布导出)时

跳过场景: 已经在某条 slice 内推进, 路由早就锁定。

## 目录

- [顶层决策树](#顶层决策树)
- [MasterGo 子任务路由](#mastergo-子任务路由)
- [阶段链路与交付物](#阶段链路与交付物)
- [疑点触发澄清](#疑点触发澄清)
- [执行阶段自动推进](#执行阶段自动推进)
- [状态台账](#状态台账)
- [澄清策略](#澄清策略)
- [反模式](#反模式)

---

## 顶层决策树

```text
1. 用户要完整 OPC / 从需求到上线?
   是 → 内部 OPC Stage Card → 02-clarification.md → 03-requirements.md
   否 → 进 2

2. 用户要 MasterGo 画布设计/修改?
   是 → MasterGo 子任务路由 → 05a-codify-design.md
   否 → 进 3

3. 用户给 MasterGo URL 并要还原/转代码?
   是 → MasterGo 子任务路由 → 05b-magic-restore.md
   否 → 进 4

4. 已有 PRD/设计要实现前端或全栈?
   是 → 04-solution.md(补齐缺口) → 06a-implementation-plan.md
   否 → 进 5

5. 要部署/CI/CD/上线?
   是 → 08-deployment.md
   否 → 02-clarification.md 判断真实交付物再路由
```

---

## MasterGo 子任务路由

**判错代价高**(整轮重做), **问错很便宜**(一句话能澄清)。模糊就问, 优先选择题, 保留自定义入口。

### 心智模型

| MCP | 定位 | 适合 |
|---|---|---|
| **Codify** (`mcp__codify__*`) | MasterGo 画布的"AI 工作台" | 在画布上**生产 / 修改 / 维护**设计 |
| **Magic** (`mcp__mastergo-magic-mcp__*`) | MasterGo 的"只读数据源" | 把已完成的设计**导出**变成代码 |

一句话: "我在 MasterGo 里要做点什么" → Codify; "我要把 MasterGo 上的东西拿出来" → Magic。

### Codify 信号词

设计 / 创建 / 修改 / 替换 / 删除 / 调整(颜色/字号/间距/布局) / 优化 / 美化 / 用 XX 组件库做一版 / 把页面复制一份 / 同步成母版。

### Magic 信号词

还原 / 复刻 / 实现 / 跑出来 / 落地 / D2C / DSL / getDsl / getD2c / 高保真 / 像素级 / 1:1 还原 / 把设计稿做成网站(Next.js/Vue/...)。

给出 `https://mastergo.com/file/...?layer_id=...` 并说"还原" → Magic + layerId 解析。

### 模糊场景(必须问)

"帮我做个登录页" / "看看这个文件" / "处理一下这个设计稿" / "把这个改一下"(指代不清)。

澄清模板:

```
我先确认你想要的:
A. 在 MasterGo 画布上做设计(Codify, 成果在画布上)
B. 把 MasterGo 设计变成前端代码(Magic, 成果在本地仓库)
C. 自定义: 你直接写想要的结果

如果两个都要, 可以直接说顺序。
```

### 子路由决策树

```
1. 用户给了 mastergo URL?
   是 → URL 带 layer_id?
        是 → 语境是"实现/还原"?
              是 → Magic
              否 → 澄清
        否 → 让用户在画布选中后重发
   否 → 进 2

2. 用了画布动词(设计/创建/修改/添加/删除/替换)?
   是 → Codify
   否 → 进 3

3. 用了实现动词(还原/转代码/D2C/跑出来/复刻)?
   是 → Magic
   否 → 进 4

4. 是"看看页面"类查看请求?
   - 当前项目是 Magic 还原工程 → Magic 重拉 DSL
   - 跟 MasterGo 没关联 → 澄清
   - 其它 → 倾向 Codify, 简短确认

5. 都不匹配 → 直接澄清
```

### 路由完成后

告诉用户你选了哪条:

> 走 **Codify**(画布设计)。下一步看你订阅了哪些团队组件库, 选一个再开始生成。

> 走 **Magic**(D2C 还原)。下一步探嗅项目里现有的前端框架。

让用户随时能纠正(`不对, 我是想 XX`), 不默默改方向。

### 切换路由

- **设计完想还原**(常见): Codify 完成 → "现在把它变成代码" → 切 Magic
- **还原中回画布微调**(偶尔): Magic 中途 → "我去改一下设计" → 暂停 Magic, 等用户改完回 update-flow
- **频繁切**(罕见但合法): 两 MCP 同时在线即可

切换时**显式说一句**: "我现在切到 X MCP, 继续做 Y, 确认?"

---

## 阶段链路与交付物

| 阶段 | 节奏 | 交付物 | 完成证据 |
|---|---|---|---|
| intake | 内部路由 | 内部 Stage Card, `.opc/state/opc-task.json` | 阶段、范围、验收方式、默认假设摘要 |
| requirements | 按需澄清 | `.opc/requirements/prd.md` (+ discussion.md) | 高影响疑点已处理, PRD 可作为方案输入 |
| solution | 按需澄清 | `.opc/solution/solution-design.md` (+ discussion.md) | 后端栈/DB/部署目标明确, 方案覆盖 PRD |
| ui-design | 按需澄清 | 设计说明 / MasterGo 画布 (+ discussion.md) | 风格、语种、关键状态明确; 3A 验证或截图 |
| implementation-plan | 按需澄清 | `.opc/implementation-plan/index.md` + architecture/contracts/work-breakdown/verification/slices/ADR | 读取顺序、用户价值切片、技术契约和验证门禁明确 |
| implementation | **执行** | 前端代码 + Node 后端 + DB schema + API 路由 | lint/typecheck/test/build/Browser QA |
| verification | **执行** | `.opc/verification/verification.md` | 命令、截图、URL、数据刷新或差异证据 |
| deployment | **执行**(部署目标不明才确认) | preview/prod URL、env 记录、回滚方式 | 可访问链接、部署状态、健康检查 |
| calibration | **执行** | gap report、规则补丁、eval 更新 | 差距项闭合或 `skipped with reason` |

各阶段产物最低要求摘要:

- **PRD**: 目标、用户、JTBD、MoSCoW、用户故事、验收标准、Open Questions
- **方案**: 2-3 个候选(或写明为何只有一条)、推荐理由、Planning Packet、后端栈/DB/部署目标
- **UI 设计**: 信息架构、状态、语种、可访问性、性能预算、视觉验证
- **实现规划**: `index.md` + 架构/契约/验证文件 + 按用户价值拆的 slices + 必要 ADR + 固定 Read Set
- **全栈实现**: 现有项目约定 + 组件 + API routes + DB schema + 浏览器验证
- **CI/CD**: 先 preview、保护 secrets、release packet、stop conditions、回滚方式
- **回放校准**: AAR → 沉淀到规则、脚本或 eval

---

## 疑点触发澄清

进入定义阶段时:

1. 读 `.opc/<phase>/discussion.md` 和 `.opc/state/opc-task.json`
2. 抽取已知事实: 用户原话、现有文档、代码、截图、接口、配置
3. 判断是否有高影响不确定(标准见 02-clarification.md)
4. 没有高影响不确定 → 直接写阶段产物
5. 有高影响不确定 → 打开宿主原生选择/确认交互; 工具不可用才文本降级
6. 用户提交后更新 discussion log, 继续写产物或进入下一阶段

---

## 执行阶段自动推进

implementation-plan → implementation → verification → deployment → calibration **默认连续推进**。

1. 本阶段交付物、验收口径和下一阶段输入齐了, 立即 mark done 并进下一阶段
2. **不在每个阶段末尾问"是否继续"; 只在硬阻塞或高风险副作用前提问**
3. 用户说"继续 / 你决定 / 后面都做完 / 从需求到上线"时, 视为完整链路授权
4. 真正的确认门禁: production 部署、远端 push、覆盖 MasterGo 画布、写 secrets、付费资源、破坏性迁移
5. 用户只说"上线"没明确 production 时, 默认 preview/staging; 部署平台不明确才用原生选择
6. 阶段被明确跳过, 状态写 `skipped` + 原因 + 替代证据, 继续后续
7. 中间阶段恢复时, 先 resume state + discussion log
8. `ui-design` 收敛后默认下一步是 `implementation-plan`; 用户明确说"先别实现"或有 blocker 才停
9. `implementation-plan` 必写 `.opc/implementation-plan/index.md` + 第一条 `slices/*.md`; 不要用一个巨大文档或按 frontend/backend/database/tests 机械拆分
10. 进入 `implementation` 前先读 implementation-plan 的 Read Set; 缺失则回到 implementation-plan 补齐
11. 工作区没有现成代码仓库时, 按方案自动新建全栈工作区
12. 业务工作区没有 Git 仓库且不在父级仓库内时, 默认 `git init` + 补 `.gitignore`; 没有 remote 不是停点
13. 缺 mock 数据(用户已选演示)、测试脚本、CI/CD 或 preview 默认配置时, 先创建最小可用版本; 缺 API key、服务器、production 授权或风格/合规关键选择时走原生选择, 用户选完继续

---

## 状态台账

代理自动读写的恢复机制, **不是用户手动步骤**。进入任务时先读 [10-contracts.md](10-contracts.md#上下文持久化契约): 有 `.opc/state/opc-task.json` 就 `resume`, 没有就先写最小内部 Stage Card 再初始化。

定义阶段额外读 `.opc/<phase>/discussion.md`。

```bash
# 初始化
python3 <skill-dir>/scripts/mandatory/opc-task-state.py init \
  --goal "<原始用户目标>" \
  --delivery "从需求到上线的 OPC 交付" \
  --acceptance "用户能按验收标准访问并验证部署结果" \
  --next-action "进入 requirements; 若有高影响不确定则原生选择"

# 阶段推进
python3 <skill-dir>/scripts/mandatory/opc-task-state.py mark requirements done \
  --artifact ".opc/requirements/prd.md" \
  --evidence "高影响疑点已处理, PRD 可作为方案输入" \
  --next-action "进入 solution 阶段"

# 用户询问进度
python3 <skill-dir>/scripts/mandatory/opc-task-state.py brief

# 完成前
python3 <skill-dir>/scripts/mandatory/opc-task-state.py validate --for-completion
```

`blocked` 和 `pending` 不是完成。`skipped` 必须有用户授权或明确原因。

---

## 澄清策略

澄清不是固定问卷, 先判影响面:

- **高影响**: 原生选择交互优先; 文本降级必须有默认和自定义 / type something
- **低影响**: 自治处理, 记录在内部日志或结构化收尾
- **已锁定**: 不重复问

用户说"你决定", 低风险直接决定; 高影响给推荐默认和理由, 原生确认可用时打开确认框。

---

## 反模式

不要做这些:

- 把"每个定义阶段至少一轮确认"当硬规则
- 把内部确认卡完整贴给用户作为固定仪式
- 高影响不确定没处理就写 PRD 或代码
- 需求已经明确却仍问"是否继续"
- 低风险工程细节(文件名/目录/helper 拆法)让用户拍板
- 错误停点示例:
  - "我先产出可评审的设计包, 后面等你选下一步"
  - "这里不是 Git 仓库, 所以本轮先停在设计"
  - "MasterGo 画布、前端原型、API 契约, 你来选我再继续"
  - "没有 Git 仓库, 你先创建好我再继续"
  - "Vercel token 缺失, 我退回本地 production server"

外部最佳实践只作流程校准, 不把长文档塞进 Skill。保留为阶段门禁。
