# Magic 实现验证 SOP

## 目录

- [3B-1 快速复刻验证(`dangerouslySetInnerHTML` 模式)](#3b-1-快速复刻验证dangerouslysetinnerhtml-模式)
  - [3B-1.1 启动 dev server](#3b-11-启动-dev-server)
  - [3B-1.2 截图比对工具优先级](#3b-12-截图比对工具优先级)
  - [3B-1.3 Playwright 自动截图脚本](#3b-13-playwright-自动截图脚本)
  - [3B-1.4 逐页检查清单(像素级,严)](#3b-14-逐页检查清单像素级严)
  - [3B-1.5 不要靠 HTTP 200 自称完成](#3b-15-不要靠-http-200-自称完成)
  - [3B-1.6 通过标准](#3b-16-通过标准)
- [3B-2 企业级实现验证(组件化 + 接 API 模式,默认)](#3b-2-企业级实现验证组件化--接-api-模式默认)
  - [3B-2.1 启动 dev + 接真后端](#3b-21-启动-dev--接真后端)
  - [3B-2.2 视觉相似度验证(允许小差异)](#3b-22-视觉相似度验证允许小差异)
  - [3B-2.3 数据接入正确性(必做)](#3b-23-数据接入正确性必做)
  - [3B-2.4 ★ 强制展示 API 溯源汇报](#3b-24--强制展示-api-溯源汇报)
  - [3B-2.5 业务逻辑测试覆盖(可选)](#3b-25-业务逻辑测试覆盖可选)
  - [3B-2.6 通过标准](#3b-26-通过标准)

定位:Magic 还原实现完之后的双模式验收 SOP——同时是 SKILL.md
[📸 证据契约](../SKILL.md#-证据契约完成判定) 在还原场景下的具体落地。
同时遵守 [delivery-contract.md](delivery-contract.md):DSL / D2C HTML / 资源目录 /
dev server HTTP 200 都只是中间产物,不能替代可运行前端项目的最终验收。
还原实现要遵守 [copy-language.md](copy-language.md):页面静态文案默认保留 MasterGo
原稿语种,接 API 或重构组件时不得无意翻译。
每次验证结果都写入 `.codify/state.json`;可用
`scripts/verification-state.py record --type implementation ...` 归档。

## 3B ── 实现完 SOP(Magic 路径,**双模式分开验**)

Magic 还原有两种模式(见 [restoration-workflow.md](restoration-workflow.md) 第 5 节):

| 模式 | 验证 SOP |
|---|---|
| **企业级实现**(默认) | 走 **3B-2** |
| **快速复刻**(opt-in) | 走 **3B-1** |

---

## 3B-1 快速复刻验证(`dangerouslySetInnerHTML` 模式)

模式特点:HTML 整段塞 React,数据写死,**追求像素级 100% 一致**。

### 3B-1.1 启动 dev server

```bash
cd <project>
pnpm install
pnpm dev &
sleep 3
curl -sI http://localhost:3000  # HTTP 200 仅是开始,不是完成
```

### 3B-1.2 截图比对工具优先级

```
1. 当前宿主有 Browser / Playwright 能力 → 直接截图
2. 没有 → 复制 `<skill-dir>/scripts/screenshot.mjs` 到目标项目并安装 Playwright:
     pnpm add -D playwright && npx playwright install chromium
3. 安装失败 / 用户中断 / 用户拒绝 → 回退到手动:
     "请打开 http://localhost:3000/<路由>, 截一张完整页面图发我。
      我会对照 MasterGo 原稿检查布局、字体、配色、蒙版和资源位置。"
```

### 3B-1.3 Playwright 自动截图脚本

```javascript
cp <skill-dir>/scripts/screenshot.mjs scripts/screenshot.mjs
node scripts/screenshot.mjs --base http://localhost:3000 --routes /,/v2,/portal,/leave-with --out screenshots
```

### 3B-1.4 逐页检查清单(像素级,严)

每个路由对照下面 5 条,**任何一条没过都不算通过**:

- [ ] **蒙版**:头像 / 圆形 / 异形 mask 是否生效;
- [ ] **字体**:钉钉进步体 / Alimama / 自定义字体是否加载;
- [ ] **胶囊换行**:`border-radius:40px` 的 pill chip 文字是否 `white-space:nowrap`;
- [ ] **配色 / 渐变**:背景光晕 / 卡片底色 / 文字色 100% 匹配原稿;
- [ ] **装饰 SVG 位置**:云形 / 装饰圆等是否在原稿位置。
- [ ] **文案语种**:导航、标题、按钮、表头、状态、空态和提示沿用原稿语言。

哪条不过 → 回 [rendering-patches.md](rendering-patches.md) 找对应渲染补丁。

### 3B-1.5 不要靠 HTTP 200 自称完成

**禁用以下话术**:
- ✗ "dev 起来了,HTTP 200,完成 ✅"
- ✗ "构建成功,完成 ✅"
- ✗ "D2C 拉取成功,完成 ✅"
- ✗ "HTML 和资源已落盘,完成 ✅"

**允许的完成话术**:
- ✓ "5/5 路由截图通过,5 项检查清单全过,完成"

### 3B-1.6 通过标准

- [ ] 所有路由 HTTP 200 + 渲染成功(不报红);
- [ ] 所有路由截图比对**像素级**通过;
- [ ] 5 条检查清单全过;
- [ ] 用户口头确认"看起来对了"。
- [ ] `scripts/verification-state.py record --type implementation --mode quick-mirror` 已归档。

---

## 3B-2 企业级实现验证(组件化 + 接 API 模式,默认)

模式特点:正常 React 组件 + Tailwind + 真 API 数据。
**像素精度允许 95-98%**(可维护性 >> 强迫症)。若当前实现不是严格 MasterGo 来源,
同时按 [frontend-design-quality.md](frontend-design-quality.md) 检查设计质量 brief 是否落到 UI。

### 3B-2.1 启动 dev + 接真后端

```bash
pnpm install
# 确认 .env 里有 NEXT_PUBLIC_API_BASE 指向真后端(或本地 mock)
pnpm dev &
sleep 3
curl -sI http://localhost:3000  # HTTP 200 仅是开始
```

后端没起?**让用户起后端再来**,不要用假数据假装完成。

### 3B-2.2 视觉相似度验证(允许小差异)

走 3B-1.2 的截图工具优先级,但比对**判定标准放宽**:

| 维度 | 通过标准 |
|---|---|
| 整体布局 | ≥ 95% 一致(主要区块位置 / 比例 / 层次正确) |
| 颜色 | hex 一致;允许 1-3 个色阶的差异(因为 Tailwind palette 离散) |
| 字体 | 字族正确;字号允许 ±2px 差异 |
| 间距 | padding / margin / gap 允许 ±4px 差异 |
| 蒙版 / 圆角 / 渐变 | 视觉上能识别是同一种效果即可 |
| 图标 / 资源 | 跟 D2C 切图一致(默认就用切图) |

**不需要像素级 100%**,但**主要观感 / 信息密度 / 层次结构必须对**。
如果整体观感跟 MasterGo 原稿差异太大(色彩偏移、布局错位、字号梯度不对),回去改。
如果没有 MasterGo 原稿, 就按设计质量 brief 检查 purpose、tone、differentiation、
state coverage、桌面/移动无重叠和反 generic AI aesthetics guardrails; 不要只用构建通过代替视觉验收。

### 3B-2.3 数据接入正确性(必做)

打开每页**真后端**,看真数据是否正确渲染:

- [ ] 列表数据:数量 / 顺序 / 关键字段对得上后端实际返回?
- [ ] 详情数据:标题 / 描述 / 统计数字跟后端一致?
- [ ] 时间格式化:`createdAt` 显示成 "2 小时前" 还是 ISO 字符串?(看设计稿要求)
- [ ] 加载态:`Suspense` / `loading.tsx` 显示了吗?
- [ ] 错误态:接口报错时,有没有友好提示?(404 / 500 / 网络)
- [ ] 空态:列表空数组时,显示了 empty state 吗?
- [ ] 静态文案:页面导航、按钮、状态和错误提示是否沿用原稿语种?

接口报错 / 字段对不上 → 回 [api-field-mapping.md](api-field-mapping.md)
检查字段映射并修正。

### 3B-2.4 ★ 强制展示 API 溯源汇报

**这一步不能省**。把 [api-trace-report.md](api-trace-report.md) 定义的溯源汇报
**完整打印给用户**,内容包括:

- 每页 / 每字段 ← 接哪个接口 ← 哪条字段路径 ← 哪个源文档(精确到行号 / operationId);
- 未接 API 的静态字段清单;
- 接口文档里没用到的接口清单。

汇报缺失 = 实现没完成。

### 3B-2.5 业务逻辑测试覆盖(可选)

企业级实现的好处是代码**可测试**。鼓励但不强制:

```bash
# 数据层单元测试
pnpm test src/lib/api/

# 组件渲染快照
pnpm test src/components/

# E2E(可选)
pnpm playwright test
```

没写测试不阻塞验收通过,但要**告诉用户:补测试是企业级实现的可选加分项**。

### 3B-2.6 通过标准

- [ ] 所有路由 HTTP 200 + 渲染成功;
- [ ] 视觉相似度 ≥ 95%(按 3B-2.2 标准);
- [ ] 数据接入正确性 6 项必检(按 3B-2.3);
- [ ] **API 溯源汇报已展示**(按 3B-2.4);
- [ ] 用户口头确认。
- [ ] `scripts/verification-state.py record --type implementation --mode enterprise` 已归档。

缺 API 文档、后端、截图能力或用户确认时,标记为"待接 API / 待后端 /
待视觉验证 / 待用户确认",不要说企业级实现完成。

---
