# 07d — 验证 SOP: 渲染补丁 + 设计稿更新流

Magic 还原的视觉差异修复(渲染补丁) 和 设计稿迭代后的代码同步(更新流)。从 [07b-restore-verify.md](07b-restore-verify.md) 拆出,两个流程跟核心 3B 验证(运行/接 API/截图)独立,可独立读独立用。

## 何时读

- D2C HTML 在浏览器渲染跟 MasterGo 原稿不一致 → [渲染补丁](#渲染补丁)
- MasterGo 设计稿更新(用户上传新版/修改),需同步代码 → [设计稿更新流](#设计稿更新流)

核心 3B 验证(快速复刻 / 企业级)见 [07b-restore-verify.md](07b-restore-verify.md)。

---

## 目录

- [渲染补丁](#渲染补丁)
- [设计稿更新流](#设计稿更新流)

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

- 第一次还原 → [05b-magic-restore.md](05b-magic-restore.md)
- Codify 画布设计 → [05a-codify-design.md](05a-codify-design.md) + [07a-design-verify.md](07a-design-verify.md)
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

