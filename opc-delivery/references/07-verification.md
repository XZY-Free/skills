# 07 — 验证 SOP(设计完 / 实现完 / 更新流)

不验证不算完成。HTTP 200、命令退出码 0、本地 HTML 存在、`accepted`、代码列表非空都**不是**最终完成证据。

## 何时读

- Codify 设计推送后(3A)
- Magic 还原实现完后(3B)
- 设计稿增量更新(用户说"页面更新了 / 重新拉一下")
- D2C 渲染问题(蒙版 / 字体 / 胶囊 / SVG 等)

## 目录

- [3A: Codify 设计完 SOP](#3a-codify-设计完-sop)
- [accepted pending 分支](#accepted-pending-分支)
- [截图要求](#截图要求)
- [3B Magic 还原验证](#3b-magic-还原验证)
- [3B-1 快速复刻验证](#3b-1-快速复刻验证)
- [3B-2 企业级实现验证](#3b-2-企业级实现验证)
- [验证归档](#验证归档)
- [渲染补丁](#渲染补丁)
- [设计稿更新流](#设计稿更新流)
- [不达标怎么办](#不达标怎么办)

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

确认本轮写操作已遵守 [05-mastergo.md](05-mastergo.md#写入前-preflight-硬门禁):

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
cp <skill-dir>/scripts/helpers/screenshot.mjs scripts/screenshot.mjs
node scripts/screenshot.mjs --base http://localhost:3000 \
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

哪条不过 → 见下文 [渲染补丁](#渲染补丁)。

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

接口报错 / 字段对不上 → 回 [06-implementation.md](06-implementation.md#字段映射) 检查字段映射并修正。

### 3B-2.4 ⚠️ 强制展示 API 溯源汇报

**这一步不能省**。把 [06-implementation.md](06-implementation.md#-强制溯源汇报) 定义的溯源汇报**完整打印**给用户:

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

## 渲染补丁

D2C HTML 在浏览器渲染跟 MasterGo 原稿不一致时, 按分类找补丁。触发场景: 快速复刻模式 + 部分企业级实现的字体/蒙版细节。

### C.1 蒙版(mask)丢失: 头像缺一块 / 圆形变方形

**症状**: D2C 渲染的头像 PNG 是矩形完整原图, 不是设计稿里的圆形(设计师用圆形蒙版裁掉了高出部分)。

**根因**: MasterGo 设计里头像图是 `SVG_ELLIPSE mask=outline + fill PNG`, D2C 转 HTML 时部分 Frame 会丢掉 mask 信息。

**全局补丁**(写到 `globals.css` 末尾):

```css
.design-page div:has(> img[src*="<头像PNG文件名片段>"]) {
  background: #cae4ff !important;
  border-radius: 9999px !important;
  overflow: hidden !important;
  box-shadow: inset 0 0 0 1px #ffffff !important;
}
```

异形蒙版(非圆形): `clip-path: path('M ...')` 或 `mask-image: url(...)`, DSL 里 `path` 节点的 `data` 直接拿来用。

### C.2 胶囊文字换行(border-radius:40px 的 pill chip)

**症状**: 胶囊宽度紧贴文字, 但 D2C 输出 span 没有 `white-space:nowrap`, flex 父级一收紧就换行。

**修法**:

```css
.design-page [style*="border-radius: 40px"] span,
.design-page [style*="border-radius: 40px"] p {
  white-space: nowrap !important;
}
.design-page [style*="border-radius: 40px"] img,
.design-page [style*="border-radius: 40px"] svg {
  flex-shrink: 0;
}
```

### C.3 字体回退(钉钉进步体 / Alimama 数黑体)

**症状**: D2C 内联 `font-family: "DingTalk JinBuTi"` 但浏览器没这字体, 回退默认衬线字体。

**修法**: CDN 加载 + 全局 fallback 链。`globals.css` 顶部:

```css
@font-face {
  font-family: "DingTalk JinBuTi";
  src: url("https://cdn.jsdelivr.net/gh/cn-fontsource/cn-fontsource-ding-talk-jin-bu-ti/dist/font.woff2") format("woff2");
  font-display: swap;
}
@font-face {
  font-family: "Alimama ShuHeiTi";
  src: url("https://cdn.jsdelivr.net/gh/cn-fontsource/cn-fontsource-alimama-shu-hei-ti/dist/font.woff2") format("woff2");
  font-display: swap;
}
```

末尾补 fallback:

```css
.design-page * {
  font-family: "PingFang SC", "Microsoft YaHei", system-ui, -apple-system, sans-serif;
}
.design-page [style*="DingTalk JinBuTi"],
.design-page [style*="DingTalk JinBuTi"] * {
  font-family: "DingTalk JinBuTi", "PingFang SC", system-ui, sans-serif !important;
}
```

### C.4 SVG 路径里出现 NaN

**症状**: D2C 内联 SVG 渐变出现 `rgba(242, 246, 255, NaN)`, 浏览器可能拒绝渲染。

**根因**: MasterGo 渐变 alpha 通道未设 → 序列化为 NaN。

**修法**(已包含在 `loadDesignHtml` 里):

```typescript
const cleaned = raw.replace(/,\s*NaN\)/g, ", 1)");
```

### C.5 装饰大 SVG 跑出画布

**症状**: 装饰背景 SVG(云形、装饰圆)的 `relativeX` 是负数, 超出 1440×780 画布。

**根因**: 设计师故意让装饰元素超出 Frame 边界营造层次感。

**修法**: 根容器加 `overflow: hidden`:

```tsx
<div style={{ width: 1440, height: 780, overflow: "hidden" }}>...</div>
```

### 全局补丁 CSS(完整一份, 直接抄)

```css
/* ─── MasterGo D2C 修正层 ─── */

.design-page div:has(> img[src*="<HEAD_AVATAR_HASH>"]) {
  background: #cae4ff !important;
  border-radius: 9999px !important;
  overflow: hidden !important;
  box-shadow: inset 0 0 0 1px #ffffff !important;
}

.design-page [style*="border-radius: 40px"] span,
.design-page [style*="border-radius: 40px"] p {
  white-space: nowrap !important;
}
.design-page [style*="border-radius: 40px"] img,
.design-page [style*="border-radius: 40px"] svg {
  flex-shrink: 0;
}

.design-page * {
  font-family: "PingFang SC", "Microsoft YaHei", system-ui, -apple-system, sans-serif;
}
.design-page [style*="DingTalk JinBuTi"],
.design-page [style*="DingTalk JinBuTi"] * {
  font-family: "DingTalk JinBuTi", "PingFang SC", system-ui, sans-serif !important;
}
.design-page [style*="Alimama ShuHeiTi"],
.design-page [style*="Alimama ShuHeiTi"] * {
  font-family: "Alimama ShuHeiTi", "DingTalk JinBuTi", "PingFang SC", system-ui, sans-serif !important;
}
```

跟设计稿对照后还有问题 → 先 bash + curl 查文档, 再继续往这里加补丁, 把新发现的坑写进对应章节。

---

## 设计稿更新流

用户说"页面更新了 / 设计变了 / 重新拉一下"时进入。**核心: 增量比对, 只补差异, 不重头来**。

更新流的交付物是**增量变更已应用到目标代码并复验**, 不是 diff 报告本身。

### 适用性门禁

进入前确认:

- 当前项目已有 Magic 还原落盘结构(`src/design/<route>.html`)或明确的 Codify 设计基准
- 当前宿主 Magic MCP 可用, 或 Codify 设计路径可用
- 有旧 DSL / 旧 D2C / 旧代码可比对
- 用户给的是"更新已有成果", 不是第一次还原或设计

不满足时:

- 第一次还原 → [05-mastergo.md Magic 部分](05-mastergo.md#magic-还原)
- Codify 画布设计 → [05-mastergo.md Codify 部分](05-mastergo.md#codify-设计) + 上文 3A
- 缺 MCP / token / layerId → [mcp-setup.md](mcp-setup.md) 或 [troubleshooting.md](troubleshooting.md)
- **不能只输出"变更分析报告"后说同步完成**

### 拉最新 DSL

```
mcp__getDsl(fileId, rootLayerId)         # 根容器
mcp__getDsl(fileId, page1LayerId)        # 各子页面(避免 20MB 限制)
mcp__getDsl(fileId, page2LayerId)
```

并发拉, 每个调用单独保存到不同的 outDir 或缓存。

### 找到旧 DSL 缓存

Claude Code 自动落盘所有 MCP 调用结果:

```
~/.claude/projects/<project-hash>/tool-results/toolu_*.json
```

`<project-hash>` 是当前工作目录路径转的 hash。

```bash
ls -lt ~/.claude/projects/-*-mcp--/tool-results/toolu_*.json | head -10
```

按文件大小区分: 根容器 DSL 一般 1-2MB, 单页 60-100KB, D2C 1-2MB。

### 解析嵌套 JSON

MCP 工具结果是双层 JSON: 外层数组 `[{type:"text", text:"..."}]`, 内层 text 是 JSON 字符串需要二次解析。**直接用 bundled 脚本**:

```bash
python3 <skill-dir>/scripts/helpers/dsl-diff.py <old.toolu.json> <new.toolu.json>
# 默认 JSON 输出; 加 --output summary 只看汇总
python3 <skill-dir>/scripts/helpers/dsl-diff.py <old.toolu.json> <new.toolu.json> --language-risk
```

脚本输出 `added` / `removed` / `changed` 三类 + 每个 changed 节点的字段级 diff + `categories.text/fill/layout/interaction` 和 `language_risks`。

文本 diff 新旧版本语种发生变化 → 先判断是不是用户有意改; 不确定用选择题澄清。

### 关注字段优先级

| 字段 | 含义 | 优先处理 |
|---|---|---|
| `text` 子节点的 text | 文本(标题/按钮文案改动) | ⭐⭐⭐ |
| `interactive` | 跳转钩子(组件级, 不是页面跳转) | ⭐⭐⭐ |
| 节点新增/删除(id 集合 diff) | 整块图层增删 | ⭐⭐⭐ |
| `fill` (paint_*) | 颜色 token | ⭐⭐ |
| `font_*` | 字号 / 字体 | ⭐⭐ |
| `layoutStyle.width/height` | 元素尺寸 | ⭐⭐ |
| `relativeX/Y` | 元素位置 | ⭐ |
| `path.data` | SVG 路径数据 | ⭐ |

### 原型连线限制

**MasterGo Magic MCP 的 DSL 不下发画布 Frame ↔ Frame 的原型连线**。update 流程里这条限制的影响:

做 DSL diff 时不要期望 `interactive` 字段出现新的跨 Frame 跳转; 用户说"我刚加了一条连线" → 解释清楚 MCP 能力边界后, 让用户口述跳转关系, 代码里手写 `<Link>` / `router.push`。

### 对应 D2C 重拉

DSL 验证设计真变了之后, 让用户**重新点"发送数据"**触发 D2C 重生成, 再用**新 outDir** 重拉:

```python
mcp__getD2c(contentId, fileId, outDir=f".mg_v2/{routeKey}")
```

对比新旧 D2C HTML 的 md5:

```bash
md5 .mg/<route>/*.html .mg_v2/<route>/*.html
```

- md5 一样 = 缓存还没刷新 → 让用户再点一次
- md5 不同 → 把新资源拷到 `public/assets/`, HTML 拷到 `src/design/`, 覆盖旧的

### 增量推到代码

只动变化的页面:

```bash
cp .mg_v2/<route>/*.html src/design/<route>.html
cp -r .mg_v2/<route>/asset/icons/*  public/assets/<route>/icons/
cp -r .mg_v2/<route>/asset/images/* public/assets/<route>/images/ 2>/dev/null

# 起 dev 重新跑 3B 节
```

跳转关系变了 → 用自然语言描述补 `<Link>`。

### 更新归档

```bash
python3 <skill-dir>/scripts/helpers/verification-state.py record \
  --type update --passed \
  --diff ".codify/diff/update-<timestamp>.json" \
  --note "已应用设计稿增量并复验"
```

保留上一轮 DSL hash、D2C hash、本次 diff 文件路径和已应用文件清单。**用户在画布上并行修改时, 先重新拉最新 DSL, 不要用旧 diff 覆盖用户的新改动**。

### 报告模板

每次 diff 完给用户列清单:

```
本次设计稿变更(vs 上次拉取):

  ~ 改动节点 N 个
    - 文本变化:   [节点 id] "旧文本" → "新文本"
    - 颜色变化:   [节点 id] paint_xxx #ABC → #DEF
    - 尺寸变化:   [节点 id] 100×40 → 120×40
  + 新增节点 M 个
  - 删除节点 K 个

interactive 字段变化: <无 / 有 X 条新增>
(注: MCP 不下发原型连线, 只有组件级状态过渡)

D2C 重拉状态:
  ✅ 已刷新: <路由列表>
  ⏳ 缓存未变, 需用户在 MasterGo 点"发送数据": <路由列表>

代码已应用变更:
  - 文件 1 / 文件 2 ...

待截图确认: http://localhost:3000/<路由>
```

让用户走上文 3B 节验证截图。**没有应用和复验前, 只能说 diff 已生成或待同步, 不能说更新完成**。

---

## 不达标怎么办

不达标不是失败, 是还有一轮要走:

1. 定位问题: diff、截图、语种、组件率、API、测试输出
2. 选修法: Codify 重新生成/局部更新, 或前端代码修正
3. 修改后重新过对应 SOP
4. 更新 task state 和 verification state

**不要降低标准凑合通过, 也不要隐藏未验证项**。
