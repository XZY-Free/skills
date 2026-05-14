# 前端实现工作流

目标: 把已确认的 PRD/方案/UI 变成可运行、可测试、可部署的前端项目。不要把 D2C、
截图或静态 mock 当成实现完成。

## 目录

- [进入条件](#进入条件)
- [框架选择](#框架选择)
- [空工作区启动规则](#空工作区启动规则)
- [Git / 工程初始化](#git--工程初始化)
- [TDD / regression ratchet](#tdd--regression-ratchet)
- [实现步骤](#实现步骤)
- [新项目脚手架补充](#新项目脚手架补充)
- [MasterGo 来源实现](#mastergo-来源实现)
- [完成门槛](#完成门槛)

## 进入条件

- 有 PRD 或足够明确的需求 brief；
- 有方案文档或轻量方案；
- 若来自 MasterGo，还原路径已经完成 DSL/D2C 拉取和模式选择；
- 若无 MasterGo 来源，已明确 UI 策略、页面、状态和验收标准。

## 框架选择

先遵循现有仓库:

1. 读 `package.json`、路由结构、组件目录、样式体系和测试命令。
2. 复用现有框架、组件库、图标库、数据层和 lint/typecheck/test 配置。
3. 未经明确需要，不新增依赖。

新项目默认:

- 复杂 app/dashboard/tool: React + Vite；
- 需要 SSR/路由/部署平台明显偏 Next.js: Next.js；
- 用户或仓库指定其它框架时服从指定。

## 空工作区启动规则

如果当前工作区没有现成前端仓库，不要把完整 OPC 收缩成“先交设计包”。应直接继续:

1. 读取 `.opc/requirements/prd.md`、`.opc/solution/solution-design.md`、`.opc/design/design-brief.md`；
2. 确认方案里写的是“新建项目”还是“复用现有项目”；
3. 没有现成项目时，按方案里的目标框架自动起脚手架；
4. 脚手架完成后立即继续组件、状态、API wiring、验证和部署链路。

默认目录策略:

- 当前目录为空或只有 `.opc/`、`.codify/`、`.omx/` 这类过程目录时，直接在当前目录起前端项目；
- 当前目录已是业务工作区但没有前端实现目录时，新建 `app/`、`web/` 或方案里明确的实现目录；
- 只有当目录选择会影响真实交付物、已有代码所有权或部署方式时，才向用户确认。

以下说法不允许作为完整 OPC 的收尾:

- “这里不是 Git 仓库，所以本轮先停在设计包”
- “我先把 PRD、方案、UI 做完，等你决定要不要实现”
- “下一步请在前端原型、API 契约、产品评审里选一个”

## Git / 工程初始化

完整 OPC 实现阶段默认补齐本地工程基础设施:

- 当前目录没有 `.git/` 且不在父级 Git 仓库内时，执行 `git init`；
- 缺 `.gitignore` 时创建，覆盖 `node_modules`、构建产物、`.env*`、日志和缓存；
- 缺 `package.json` 时按方案框架创建脚手架，不要求用户先准备项目；
- 缺 mock/API 后端时创建 typed mock、fixture 和字段映射 TODO，让主流程可运行；
- 缺测试命令时，新项目补最小 test/build/browser 验证；现有项目先复用已有命令；
- 没有 git remote 时继续本地实现和验证；远端 push、创建远端 repo 或改受保护分支才需要确认。

这些动作写入 `.opc/state/opc-task.json` 的 note/evidence。不要把“缺仓库 / 缺脚手架 /
缺测试”作为实现阶段停点。

## TDD / regression ratchet

可测试行为默认先补失败测试或回归用例，再写实现:

- 新业务逻辑、字段映射、权限、表单校验、状态机、API contract: 先写 unit/component/integration/contract 测试。
- 修 bug: 先复现失败，再补能证明该 bug 的最小回归用例。
- UI 交互或响应式风险: 先写 Playwright/Browser 场景或明确截图检查点。
- 项目没有测试基础设施时，记录原因，并用浏览器验证脚本、截图、console 和核心流程操作作为替代证据。

遇到红测、构建失败、运行时报错或视觉异常时，先走 systematic debugging:
复现 -> 读错误 -> 查最近变化 -> 提一个单一假设 -> 最小验证 -> 修根因。不要靠猜测连打补丁。

## 实现步骤

1. 建立实现 inventory:
   - 路由、组件、状态、表单、表格、弹窗、权限、空态/错误态；
   - API 字段映射和 mock 策略；
   - UI 文案语种和技术词保留；
   - 测试和部署命令；
   - TDD/regression ratchet 选择: 要先补哪些测试、哪些只能人工/浏览器验证。
   - 如果没有现成项目: 脚手架目录、框架、路由和初始依赖怎么落地。
2. 按项目模式拆组件:
   - app shell / route page / feature modules / reusable primitives / data helpers；
   - 不把复杂页面写成一个巨大组件；
   - 相同 UI 用同一组件或明确 variant。
3. 接 API:
   - 有 `.codify/api-docs/` 时读 [api-doc-parsing.md](api-doc-parsing.md)；
   - 字段不确定时读 [api-field-mapping.md](api-field-mapping.md)；
   - 完成后产出 [api-trace-report.md](api-trace-report.md) 口径的溯源报告。
4. 实现交互:
   - 控件要更新真实本地状态或真实数据；
   - 表单有校验、提交中、成功和失败状态；
   - 数据视图有 loading、empty、error、permission 状态。
5. 验证:
   - 运行项目支持的 lint、typecheck、unit/integration/e2e、build；
   - 写清 gate truth: local、PR、release 或 scheduled；
   - 启动本地服务，用 Browser 优先验证，不可用时用 Playwright；
   - 检查桌面和一个移动尺寸；
   - 截图或 DOM/console 证据要能证明非空、无框架 overlay、无相关 console error、核心交互有效。

## 新项目脚手架补充

从零起项目时，先把“能继续交付的最小工程”搭起来:

- 生成 `package.json`、启动命令、构建命令和必要的目录结构；
- 初始化本地 Git 和 `.gitignore`，除非已处在现有仓库内；
- 建立 app shell、基础路由、全局样式和页面骨架；
- 把 PRD 的核心流程先落成可点击的主链路，而不是只生成静态首页；
- 让 UI 文案跟随 PRD 语种规则，不默认变成英文 dashboard；
- 先记录 preview 部署路径和后续环境变量需求，避免实现完再回头补部署计划。

## MasterGo 来源实现

- 企业级实现默认读 [restoration-enterprise.md](restoration-enterprise.md)；
- 快速复刻只在用户明确 opt-in 后读 [restoration-fast-prototype.md](restoration-fast-prototype.md)；
- 视觉差异、字体、mask、SVG、渐变等问题读 [rendering-patches.md](rendering-patches.md)；
- 实现完必须进 [verification-implementation.md](verification-implementation.md)。

## 完成门槛

实现阶段完成必须满足:

- 代码覆盖方案里的 must-have；
- 关键 UI 状态和核心流程可交互；
- 可测试行为已有失败测试/回归用例，或记录了替代验证理由；
- lint/typecheck/test/build 中能运行的都已运行并读过输出；
- 浏览器验证已完成，含截图或等价证据；
- `.opc/state/opc-task.json` 中 `implementation` 标记为 `done`，记录代码路径和验证证据。

如果某项无法验证，标记为 `blocked` 或 `skipped` 并写明原因；不要说“已完成”。
