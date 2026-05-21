# 验证 SOP(设计完 / 实现完)

## 目录

- [3A: Codify 设计完 SOP](#3a-codify-设计完-sop)
- [accepted pending 分支](#accepted-pending-分支)
- [截图要求](#截图要求)
- [3B: Magic 实现完 SOP](#3b-magic-实现完-sop)
- [验证归档](#验证归档)
- [不达标怎么办](#不达标怎么办)

不验证不算完成。HTTP 200、命令退出码 0、本地 HTML 存在、`accepted`、代码列表非空都
不是最终完成证据。

## 3A: Codify 设计完 SOP

设计完成必须同时满足:

- Gate Card 和覆盖 brief 已闭合。
- `.codify/state/mastergo-task.json` 中所有设计单元是 `verified` 或明确 `blocked`。
- 本轮设计单元已推送到 MasterGo 画布。
- `get_design_diff` 与预期一致，没有意外新增/删除。
- 截图视觉验证通过。
- 设计质量 brief 已按 [frontend-design-quality.md](frontend-design-quality.md) 检查, 没有 generic AI aesthetics blocker。
- UI 文案语种符合 [copy-language.md](copy-language.md)。
- 使用组件库时组件映射率达标。
- 用户主观反馈无 blocker。

### 3A.1 结构验证

先确认本轮写操作已遵守 [codify-push-protocol.md](codify-push-protocol.md):

- `get_codify_guidelines` 已运行。
- `get_user_info` 已运行。
- `scripts/codify-preflight.py` 通过。
- 原生 CSS / `<style>` 稿已转换为 Codify 可解析 HTML。
- UI 文案语种规则已写入 requirement / HTML。

然后运行或调用:

```text
get_design_diff(filePath="<本地基准 HTML 绝对路径>", projectDir="...")
```

预期改动应该能在 diff 中看到；意外删除、新增或布局漂移必须回 Codify 修正。

### 3A.2 UI 文案语种验证

推送前或验证时跑:

```bash
python3 <skill-dir>/scripts/codify-copy-lint.py <html-file> \
  --expected simplified-chinese \
  --mode strict
```

无法跑脚本时，人工抽查导航、标题、按钮、表头、状态、空态、审批、审计、监控和日志。
中文需求出现大面积未授权英文 UI 时，不能完成；回 `agent_update_node`、
`agent_replace_node` 或重新生成。

### 3A.3 组件库映射率

用了组件库时运行:

```bash
bash <skill-dir>/scripts/component-ratio.sh <html-file> full-components
bash <skill-dir>/scripts/component-ratio.sh <html-file> hybrid
```

经验阈值:

- `full-components`: 组件占比应 ≥ 40%。
- `hybrid`: 组件占比应 ≥ 15%。

低于阈值时，回到 Codify requirement，明确使用选定团队库和关键组件。

## accepted pending 分支

`accepted` 只代表请求已受理/入队。必须记录:

```bash
python3 <skill-dir>/scripts/mastergo-task-state.py request \
  --request-id "<requestId>" \
  --status accepted
```

后续尝试顺序:

1. `get_code_list`
2. `get_selection_code`
3. `get_design_diff`
4. 用户截图

没有图层、diff 或截图证据时:

```text
状态: 已发送，待画布完成验证
阻塞: waiting-for-canvas-verification
不能说: 设计已完成
```

## 截图要求

让用户回 MasterGo 截图时，给明确范围:

- 整页或根 Frame，缩放 100%。
- 关键弹窗、抽屉、空态、错误态和审批态分别截图。
- 如果是多页面产品，至少每个已推送设计单元一张。

无法截图时，`get_selection_code` + `get_design_diff` 只能作为结构验证；视觉仍是待用户动作。

截图对照清单:

1. 配色、字体、字号、行高。
2. 关键间距、对齐、层级和对比度。
3. 组件库是否真的应用。
4. UI 文案语种是否正确。
5. 目的、调性和记忆点是否能从界面看出来。
6. 是否存在“AI 味儿”问题，如渐变混乱、饱和度过高、字号跳变、模板化卡片堆或无意义装饰。

用户说“不错 / 可以 / 没问题”只代表当前轮无 blocker。若 task state 还有未闭合单元，
继续下一单元。

## 3B: Magic 实现完 SOP

Magic 还原实现分两种模式:

- 企业级实现: 视觉相似度 + 真数据/API + API 溯源 + 文案语种。
- 快速复刻: 像素相似度 + 资源完整性。

详细步骤见 [verification-implementation.md](verification-implementation.md)。D2C HTML、
DSL、资源目录和 diff 报告不是完成；必须跑起目标前端并完成截图或测试验证。

## 验证归档

每次验收后写 `.codify/state.json`，并尽量同步设计单元状态:

```bash
python3 <skill-dir>/scripts/verification-state.py record \
  --type design \
  --unit-id overview \
  --passed \
  --diff "<get_design_diff 摘要或文件>" \
  --screenshot "<截图路径或用户截图说明>" \
  --copy-language simplified-chinese \
  --component-ratio "45%"
```

完成前跑:

```bash
python3 <skill-dir>/scripts/verification-state.py summary
python3 <skill-dir>/scripts/mastergo-task-state.py validate --for-completion
```

任何一个返回未通过，都只能汇报待验证、待续作或待用户动作。

## 不达标怎么办

不达标不是失败，是还有一轮要走:

1. 定位问题: diff、截图、语种、组件率、API、测试输出。
2. 选修法: Codify 重新生成/局部更新，或前端代码修正。
3. 修改后重新过对应 SOP。
4. 更新 task state 和 verification state。

不要降低标准凑合通过，也不要隐藏未验证项。
