# 07b — 验证 SOP: Magic 还原 (3B)

Magic 还原项目核心验证集合。覆盖 3B-1 快速复刻像素级比对、3B-2 企业级实现真后端联调。视觉差异修复(渲染补丁) + 设计稿更新流(增量同步) 拆到 [07d-restore-patches.md](07d-restore-patches.md)。

## 何时读

- Magic 还原代码完成进入 3B 验证
- 视觉异常(蒙版 / 字体 / 胶囊 / SVG / 渐变) → [07d-restore-patches.md#渲染补丁](07d-restore-patches.md#渲染补丁)
- MasterGo 设计稿更新, 同步代码 → [07d-restore-patches.md#设计稿更新流](07d-restore-patches.md#设计稿更新流)

Codify 设计验证(3A)见 [07a-design-verify.md](07a-design-verify.md)。
产品成立验收(3C)见 [07c-product-verify.md](07c-product-verify.md)。

---

## 目录

- [3B Magic 还原验证](#3b-magic-还原验证)
- [3B-1 快速复刻验证](#3b-1-快速复刻验证)
- [3B-2 企业级实现验证](#3b-2-企业级实现验证)

---

## 3B Magic 还原验证

Magic 还原实现分两种模式:

| 模式 | 验证 SOP |
|---|---|
| **企业级实现**(默认) | 走 [3B-2](#3b-2-企业级实现验证) |
| **快速复刻**(opt-in) | 走 [3B-1](#3b-1-快速复刻验证) |

DSL / D2C HTML / 资源目录 / dev server HTTP 200 都只是中间产物, **不能替代**可运行前端项目的最终验收。

每次验证结果写入 `.codify/state.json`:

```bash
python3 <skill-dir>/scripts/helpers/verification-state.py record \
  --type implementation --mode quick-mirror|enterprise ...
```

还原实现要保留 MasterGo 原稿语种, 接 API 或重构组件时**不得无意翻译**。

---

## 3B-1 快速复刻验证

模式特点: HTML 整段塞 React, 数据写死, **追求像素级 100% 一致**。

### 3B-1.1 启动 dev server

```bash
cd <project>
pnpm install
pnpm dev &
sleep 3
curl -sI http://localhost:3000  # HTTP 200 仅是开始, 不是完成
```

### 3B-1.2 截图比对工具优先级

```
1. 当前宿主有 Browser / Playwright 能力 → 直接截图
2. 没有 → 复制 <skill-dir>/scripts/helpers/screenshot.mjs 到目标项目并安装 Playwright:
     pnpm add -D playwright && npx playwright install chromium
3. 安装失败 / 用户中断 / 用户拒绝 → 手动:
     "请打开 http://localhost:3000/<路由>, 截一张完整页面图发我。"
```

### 3B-1.3 Playwright 自动截图

```bash
node <skill-dir>/scripts/helpers/screenshot.mjs --base http://localhost:3000 \
  --routes /,/v2,/portal,/leave-with --out screenshots
```

> ⚠️ 截图回流给模型时遵守 [09-runtime-budget.md](09-runtime-budget.md#截图回流): 单 turn 最多 Read 1 张, 用 thumb 不用原图。

### 3B-1.4 逐页检查清单(像素级, 严)

每个路由对照下面 6 条, **任何一条没过都不算通过**:

- [ ] **蒙版**: 头像 / 圆形 / 异形 mask 是否生效
- [ ] **字体**: 钉钉进步体 / Alimama / 自定义字体是否加载
- [ ] **胶囊换行**: `border-radius:40px` 的 pill chip 文字是否 `white-space:nowrap`
- [ ] **配色 / 渐变**: 背景光晕 / 卡片底色 / 文字色 100% 匹配原稿
- [ ] **装饰 SVG 位置**: 云形 / 装饰圆等是否在原稿位置
- [ ] **文案语种**: 导航、标题、按钮、表头、状态、空态和提示沿用原稿语言

哪条不过 → 见 [07d-restore-patches.md#渲染补丁](07d-restore-patches.md#渲染补丁)。

### 3B-1.5 禁用话术

**禁用**:

- ✗ "dev 起来了, HTTP 200, 完成 ✅"
- ✗ "构建成功, 完成 ✅"
- ✗ "D2C 拉取成功, 完成 ✅"
- ✗ "HTML 和资源已落盘, 完成 ✅"

**允许**:

- ✓ "5/5 路由截图通过, 6 项检查清单全过, 完成"

### 3B-1.6 通过标准

- [ ] 所有路由 HTTP 200 + 渲染成功(不报红)
- [ ] 所有路由截图比对**像素级**通过
- [ ] 6 条检查清单全过
- [ ] 用户口头确认"看起来对了"
- [ ] `verification-state.py record --type implementation --mode quick-mirror` 已归档

---

## 3B-2 企业级实现验证

模式特点: 正常 React 组件 + Tailwind + 真 API 数据。**像素精度允许 95-98%**(可维护性 >> 强迫症)。

若当前实现不是严格 MasterGo 来源, 同时按 [04-solution.md](04-solution.md#体验设计质量门禁) 检查设计质量 brief 是否落到 UI。

### 3B-2.1 启动 dev + 接真后端

```bash
pnpm install
# 确认 .env 里有 NEXT_PUBLIC_API_BASE 指向真后端
pnpm dev &
sleep 3
curl -sI http://localhost:3000
```

后端没起 → **让用户起后端再来**, 不要用假数据假装完成。

### 3B-2.2 视觉相似度(允许小差异)

| 维度 | 通过标准 |
|---|---|
| 整体布局 | ≥ 95% 一致(主要区块位置 / 比例 / 层次正确) |
| 颜色 | hex 一致; 允许 1-3 个色阶差异(Tailwind palette 离散) |
| 字体 | 字族正确; 字号允许 ±2px |
| 间距 | padding / margin / gap 允许 ±4px |
| 蒙版 / 圆角 / 渐变 | 视觉上能识别是同一种效果即可 |
| 图标 / 资源 | 跟 D2C 切图一致(默认就用切图) |

不需要像素级 100%, 但主要观感 / 信息密度 / 层次结构必须对。

整体观感跟 MasterGo 原稿差异太大(色彩偏移、布局错位、字号梯度不对) → 回去改。

没有 MasterGo 原稿 → 按设计质量 brief 检查 purpose、tone、differentiation、state coverage、桌面/移动无重叠和反 generic AI aesthetics guardrails; **不要只用构建通过代替视觉验收**。

### 3B-2.3 数据接入正确性(必做)

打开每页**真后端**, 看真数据是否正确渲染:

- [ ] 列表数据: 数量 / 顺序 / 关键字段对得上后端实际返回?
- [ ] 详情数据: 标题 / 描述 / 统计数字跟后端一致?
- [ ] 时间格式化: `createdAt` 显示成 "2 小时前" 还是 ISO 字符串?
- [ ] 加载态: `Suspense` / `loading.tsx` 显示了吗?
- [ ] 错误态: 接口报错时有没有友好提示?(404 / 500 / 网络)
- [ ] 空态: 列表空数组时显示了 empty state 吗?
- [ ] 静态文案: 页面导航、按钮、状态和错误提示是否沿用原稿语种?

接口报错 / 字段对不上 → 回 [06c-api-wiring.md](06c-api-wiring.md#字段映射) 检查字段映射并修正。

### 3B-2.4 ⚠️ 强制展示 API 溯源汇报

**这一步不能省**。把 [06c-api-wiring.md](06c-api-wiring.md#-强制溯源汇报) 定义的溯源汇报**完整打印**给用户:

- 每页 / 每字段 ← 接哪个接口 ← 哪条字段路径 ← 哪个源文档
- 未接 API 的静态字段清单
- 接口文档里没用到的接口清单

汇报缺失 = 实现没完成。

### 3B-2.5 业务逻辑测试(可选)

```bash
pnpm test src/lib/api/       # 数据层单元
pnpm test src/components/    # 组件渲染快照
pnpm playwright test         # E2E(可选)
```

没写测试不阻塞验收, 但**告诉用户**: 补测试是企业级实现的可选加分项。

### 3B-2.6 通过标准

- [ ] 所有路由 HTTP 200 + 渲染成功
- [ ] 视觉相似度 ≥ 95%
- [ ] 数据接入正确性 6 项必检
- [ ] **API 溯源汇报已展示**
- [ ] 用户口头确认
- [ ] `verification-state.py record --type implementation --mode enterprise` 已归档

缺 API 文档、后端、截图能力或用户确认时, 标记"待接 API / 待后端 / 待视觉验证 / 待用户确认", **不要说企业级实现完成**。

---


