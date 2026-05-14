# 前端实现工作流

目标: 把已确认的 PRD/方案/UI 变成可运行、可测试、可部署的前端项目。不要把 D2C、
截图或静态 mock 当成实现完成。

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
