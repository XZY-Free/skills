# 07a — 验证 SOP: Codify 设计完 (3A)

MasterGo Codify 设计写入完成后的标准验证流程。**真实交付物的最后一道关**: 截图证据 + 结构验证 + 文案语种 + 组件库映射率 + accepted pending 闭环。

## 何时读

- Codify 设计写入完成, 进入 3A 验证
- 收到 `accepted: false` / `pending` 反馈
- 设计稿更新需要重做验证(见 [07d-restore-patches.md#设计稿更新流](07d-restore-patches.md#设计稿更新流))

Magic 还原验证(3B / 渲染补丁 / 更新流)见 [07b-restore-verify.md](07b-restore-verify.md)。
产品成立验收(3C)见 [07c-product-verify.md](07c-product-verify.md)。

---

## 目录

- [3A: Codify 设计完 SOP](#3a-codify-设计完-sop)
- [accepted pending 分支](#accepted-pending-分支)
- [截图要求](#截图要求)

---

## 3A: Codify 设计完 SOP

设计完成必须**同时**满足:

- Gate Card 和覆盖 brief 已闭合
- `.codify/state/mastergo-task.json` 中所有设计单元是 `verified` 或明确 `blocked`
- 本轮设计单元已推送到 MasterGo 画布
- `get_design_diff` 与预期一致, 没有意外新增/删除
- 截图视觉验证通过
- 设计质量 brief 已按 [04-solution.md](04-solution.md#体验设计质量门禁) 检查, 没有 generic AI aesthetics blocker
- UI 文案语种符合 [03-requirements.md](03-requirements.md#ui-文案语种契约)
- 使用组件库时组件映射率达标
- 用户主观反馈无 blocker

### 3A.1 结构验证

确认本轮写操作已遵守 [05a-codify-design.md](05a-codify-design.md#写入前-preflight-硬门禁):

- `get_codify_guidelines` 已运行
- `get_user_info` 已运行
- `scripts/mandatory/codify-preflight.py` 通过
- 原生 CSS / `<style>` 稿已转换为 Codify 可解析 HTML
- UI 文案语种规则已写入 requirement / HTML

然后:

```text
get_design_diff(filePath="<本地基准 HTML 绝对路径>", projectDir="...")
```

预期改动应该能在 diff 中看到; 意外删除、新增或布局漂移必须回 Codify 修正。

### 3A.2 UI 文案语种验证

```bash
python3 <skill-dir>/scripts/helpers/codify-copy-lint.py <html-file> \
  --expected simplified-chinese --mode strict
```

无法跑脚本时人工抽查导航、标题、按钮、表头、状态、空态、审批、审计、监控和日志。中文需求出现大面积未授权英文 UI → **不能完成**; 回 `agent_update_node` / `agent_replace_node` 或重新生成。

### 3A.3 组件库映射率

```bash
bash <skill-dir>/scripts/helpers/component-ratio.sh <html-file> full-components
bash <skill-dir>/scripts/helpers/component-ratio.sh <html-file> hybrid
```

经验阈值:

- `full-components`: 组件占比应 ≥ 40%
- `hybrid`: 组件占比应 ≥ 15%

低于阈值 → 回到 Codify requirement, 明确使用选定团队库和关键组件。

---

## accepted pending 分支

`accepted` 只代表请求已受理/入队。必须记录:

```bash
python3 <skill-dir>/scripts/helpers/mastergo-task-state.py request \
  --request-id "<requestId>" --status accepted
```

后续尝试顺序: `get_code_list` → `get_selection_code` → `get_design_diff` → 用户截图。

没有图层、diff 或截图证据时:

```text
状态: 已发送, 待画布完成验证
阻塞: waiting-for-canvas-verification
不能说: 设计已完成
```

---

## 截图要求

让用户回 MasterGo 截图时, 给明确范围:

- 整页或根 Frame, 缩放 100%
- 关键弹窗、抽屉、空态、错误态和审批态分别截图
- 多页面产品至少每个已推送设计单元一张

无法截图时, `get_selection_code` + `get_design_diff` 只能作为结构验证; 视觉仍是待用户动作。

截图对照清单:

1. 配色、字体、字号、行高
2. 关键间距、对齐、层级和对比度
3. 组件库是否真的应用
4. UI 文案语种是否正确
5. 目的、调性和记忆点是否能从界面看出来
6. 是否存在"AI 味儿"问题: 渐变混乱、饱和度过高、字号跳变、模板化卡片堆或无意义装饰

用户说"不错 / 可以 / 没问题"只代表当前轮无 blocker。若 task state 还有未闭合单元, **继续下一单元**(不要回头问"接下来做什么")。

---

