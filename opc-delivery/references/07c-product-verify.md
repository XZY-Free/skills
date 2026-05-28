# 07c — 验证 SOP: 产品成立验收 (3C) + 归档

完整 OPC + 有方案产物时必跑。**工程成立 ≠ 产品成立**: 3A/3B 通过只代表代码能跑、视觉对齐, 不代表产品像成熟上线品。3C 用姿态 / 首屏 / 升降级 / 竞品 4 个对账校准产品成立。

## 何时读

- 3B-2(企业级)通过后进入 3C
- 完整 OPC 流程且 [04-solution.md](04-solution.md#产品姿态门禁) 已经产出方案 4 张产物
- 任何 3A/3B/3C 验证不达标时(见 [#不达标怎么办](#不达标怎么办))

Codify 设计验证(3A)见 [07a-design-verify.md](07a-design-verify.md)。
Magic 还原 / 渲染补丁 / 更新流见 [07b-restore-verify.md](07b-restore-verify.md)。

---

## 目录

- [3C 产品成立验收](#3c-产品成立验收)
- [验证归档](#验证归档)
- [不达标怎么办](#不达标怎么办)

---

## 3C 产品成立验收

3B-2 通过后跑。验证"产品成立"(不是"工程成立")。镜像方案阶段的产品姿态门禁 4 张产物, 做 4 个对账。详见 [03b-productization.md](03b-productization.md)。

### 进入条件

- 3B-2 企业级实现验证通过
- `.opc/solution/solution-design.md` 含产品姿态门禁 section
- `.opc/solution/competitor-survey.md` 存在

### 跳过场景

完整 OPC + 有方案阶段产物时**必跑**。允许跳过:

- Magic 纯还原 / 极小修改 / 用户明确说"先不要产品化收口"
- 方案阶段产品姿态门禁本身已标 `skipped`
- 跳过时记录 `skipped` + 原因到 `.opc/verification/3c-product-soundness.md`

### 两阶段验收

3C 拆成两阶段, 防代理自己审自己:

**Stage 1: 执行代理对账**

1. 用 webapp-testing 起 Playwright 拿截图(首页 desktop+mobile / 一级 nav 展开 / 主要二级页 / 设置入口) 存到 `.opc/verification/3c-screenshots/`
2. 跑 4 个对账(3C.1–3C.4), 每个出"文字判断 + 截图引用"
3. 偏离项分类: 修代码 / 修方案文档 / 接受偏离(给理由)
4. 输出 `.opc/verification/3c-product-soundness.md`

**Stage 2: 独立 reviewer subagent verify**

- 派发 reviewer subagent(用 `verifier` 或新增 `product-reviewer`)
- 输入: 截图 + `solution-design.md` + `3c-product-soundness.md`
- **不给代码上下文**
- 独立判: 产品成立 / 不成立 / 哪里偏
- 沿用 OMC writer / reviewer 分离原则(根级 CLAUDE.md `execution_protocols`)

### 3C.1 姿态对账

| 检查 | 通过标准 |
|---|---|
| 主姿态识别 | 给一个不知道这个产品的人看首页截图, 能否识别"这是 X 类产品"? |
| 反例排除验证 | 方案里写"不是 X 姿态" → 实际 UI 没有 X 姿态的味道? |

输出: 文字判断 + 截图引用, 不允许只写"通过"。
不通过 → 改 IA 或更新方案。

### 3C.2 首屏对账

| 检查 | 通过标准 |
|---|---|
| 主信号兑现 | 首屏视觉权重最大的元素 = 方案写的"主信号"? |
| 反 dashboard 化 | 首屏没退化成"N 个 KPI 卡 + N 个能力入口"? |
| 参照对比 | 与同品类成熟产品对比, 取舍逻辑一致或有合理偏离理由? |

输出: 首屏截图 + 主信号兑现度文字判断。
不通过 → 重排首页。

### 3C.3 升降级对账

实现后 IA 的实际入口对照方案的升降级表:

| 方案标的能力 | 方案标的层级 | 实际实现层级 | 一致? | 处理 |
|---|---|---|---|---|
| <A> | 高曝光 | 一级导航首位 | ✓ | - |
| <B> | 中曝光 | 一级导航末位 | ⚠️ 偏高 | 改 IA OR 写理由 |
| <C> | 低曝光 | 一级导航第 5 项 | ❌ 严重偏离 | 必须移到设置 |

通过标准:
- 所有"高曝光"能力都在一级或首页主区
- 所有"低曝光 / 仅上下文"能力都没在一级 nav 抢戏
- 偏离项要么改代码、要么改方案文档说明理由, 不允许隐藏

可选脚本辅助: OCR 出一级 nav 项数, 对照"高曝光"数量, > 5 直接 fail。

### 3C.4 竞品对账

| 检查 | 通过标准 |
|---|---|
| 学/不学的兑现 | competitor-survey 写"学 X 不学 Y", 实际 UI 兑现? |
| 同类成熟形态参照 | 同类产品突出 X 是否你也突出 X? 同类藏的 Y 你也藏了吗? |

输出: 文字判断 + 截图对比(有竞品截图最好, 没有就文字)。

### 偏离处理

| 偏离类型 | 处理 |
|---|---|
| 小(组件位置/顺序错) | 改代码, 重跑 3C |
| 中(一级 nav 多/少 1-2 项) | 重排 IA, 重跑 3C |
| 大(姿态错位 / 首屏完全没体现主信号) | 决定改方案还是改实现, 写决策记录 |
| 接受偏离 | 写明原因 + 同步更新 solution-design.md |

### 截图采集

```bash
# 用 webapp-testing 起 Playwright 拿:
# - 首页 (desktop 1440x900 + mobile 375x812)
# - 一级导航展开状态
# - 主要二级页 (2-3 个)
# - 设置入口 / 用户菜单
# 存到 .opc/verification/3c-screenshots/
```

截图回流走 [09-runtime-budget.md#截图回流](09-runtime-budget.md#截图回流) 的 thumb 约束。reviewer subagent 看截图也走同一预算。

### 通过标准

- [ ] 整站 IA 截图采集完成(desktop + mobile)
- [ ] Stage 1: 4 个对账都有"文字判断 + 截图引用"
- [ ] Stage 1: 偏离项已分类(小/中/大/接受)
- [ ] Stage 2: 独立 reviewer 跑通, 判定产品成立
- [ ] reviewer 判不成立 → 回到对应对账修, 重跑 3C
- [ ] `verification-state.py record --type product-soundness` 已归档

### 绝不允许

- 写"通过"但没截图 / 没文字判断
- 隐藏不一致项
- "等用户反馈"当 3C 通过
- 3C 由实现代理一人完成两阶段(违反 writer / reviewer 分离)
- 偏离不分类、不给理由直接放过

### 归档

```bash
python3 <skill-dir>/scripts/helpers/verification-state.py record \
  --type product-soundness \
  --stage1-passed \
  --stage2-reviewer-passed \
  --posture-diff "..." \
  --homepage-diff "..." \
  --exposure-diff "..." \
  --competitor-diff "..."
```

任一字段未通过 → 整体不算 3C 通过, 不能 mark verification done。

---

## 验证归档

每次验收后写 `.codify/state.json`, 同步设计单元状态:

```bash
python3 <skill-dir>/scripts/helpers/verification-state.py record \
  --type design \
  --unit-id overview \
  --passed \
  --diff "<get_design_diff 摘要或文件>" \
  --screenshot "<截图路径或用户截图说明>" \
  --copy-language simplified-chinese \
  --component-ratio "45%"
```

完成前:

```bash
python3 <skill-dir>/scripts/helpers/verification-state.py summary
python3 <skill-dir>/scripts/helpers/mastergo-task-state.py validate --for-completion
```

任一返回未通过 → 只能汇报待验证、待续作或待用户动作。

---


---

## 不达标怎么办

不达标不是失败, 是还有一轮要走:

1. 定位问题: diff、截图、语种、组件率、API、测试输出
2. 选修法: Codify 重新生成/局部更新, 或前端代码修正
3. 修改后重新过对应 SOP
4. 更新 task state 和 verification state

**不要降低标准凑合通过, 也不要隐藏未验证项**。
