# D2C 渲染补丁

# D2C 渲染补丁

## 目录

- [C.1 蒙版(mask)丢失](#c1-蒙版mask丢失头像缺一块--圆形变方形)
- [C.2 胶囊文字换行](#c2-胶囊文字换行border-radius40px-的-pill-chip)
- [C.3 字体回退](#c3-字体回退钉钉进步体--alimama-数黑体)
- [C.4 SVG 路径里出现 `NaN`](#c4-svg-路径里出现-nan)
- [C.5 装饰大 SVG 跑出画布](#c5-装饰大-svg-跑出画布)
- [全局补丁 CSS(完整一份,直接抄)](#全局补丁-css完整一份直接抄)

定位:D2C HTML 在浏览器里渲染出来跟 MasterGo 原稿不一致时,按本文件分类找补丁。
触发场景:快速复刻模式 + 部分企业级实现的字体/蒙版细节。

## C. 渲染问题(D2C HTML 跑出来不对劲)

### C.1 蒙版(mask)丢失:头像缺一块 / 圆形变方形

**症状**:D2C 渲染出来的头像 PNG 是矩形完整原图(122×94),不是设计稿里的 94×94
圆形(设计师把 PNG 高出来的部分用圆形蒙版裁掉了)。

**根因**:MasterGo 设计里头像图是 `SVG_ELLIPSE mask=outline + fill PNG`,D2C 转
HTML 时部分 Frame 会丢掉 mask 信息。

**全局补丁**:用 `:has()` 选择器一次修掉所有页面(写到 `globals.css` 末尾):

```css
/* 头像 PNG 父容器一律按圆形蒙版处理 */
.design-page div:has(> img[src*="<头像PNG文件名片段>"]) {
  background: #cae4ff !important;            /* DSL 里给的底色 */
  border-radius: 9999px !important;
  overflow: hidden !important;
  box-shadow: inset 0 0 0 1px #ffffff !important;  /* 1px 白描边 */
}
```

`<头像PNG文件名片段>` 用文件名稳定的部分,比如 `58bdedd8ec1ec1e8`。多个头像就写多
条选择器或者用更通用的属性匹配。

**异形蒙版**(不是圆形):用 `clip-path: path('M ...')` 或 `mask-image: url(...)`,
DSL 里 `path` 节点的 `data` 直接拿来用。

### C.2 胶囊文字换行(border-radius:40px 的 pill chip)

**症状**:胶囊宽度紧贴文字,但 D2C 输出 span 没有 `white-space:nowrap`,flex 父级
一收紧就换行。"请明天的年假" 拆成两行。

**根因**:D2C 输出胶囊用 flex 布局,文字容器 `flex-shrink` 默认开,又没设
`white-space`。

**全局补丁**:

```css
/* 所有 40px 圆角的胶囊(pill chip)内文字单行不换行 */
.design-page [style*="border-radius: 40px"] span,
.design-page [style*="border-radius: 40px"] p {
  white-space: nowrap !important;
}

/* 胶囊里的图标 flex-shrink:0 防挤压 */
.design-page [style*="border-radius: 40px"] img,
.design-page [style*="border-radius: 40px"] svg {
  flex-shrink: 0;
}
```

### C.3 字体回退(钉钉进步体 / Alimama 数黑体)

**症状**:D2C 内联 `font-family: "DingTalk JinBuTi"` 但浏览器没这字体,回退到
默认衬线字体,看着完全不一样。

**根因**:MasterGo 的 D2C 不会把 webfont 文件打包进来;本地系统也大概率没装。

**修法**:用 CDN 加载 + 全局 fallback 链:

`globals.css` 顶部:
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
.design-page [style*="Alimama ShuHeiTi"],
.design-page [style*="Alimama ShuHeiTi"] * {
  font-family: "Alimama ShuHeiTi", "DingTalk JinBuTi", "PingFang SC", system-ui, sans-serif !important;
}
```

### C.4 SVG 路径里出现 `NaN`

**症状**:D2C HTML 内联 SVG 渐变里出现 `rgba(242, 246, 255, NaN)`,浏览器可能拒绝渲染。

**根因**:MasterGo 的渐变 alpha 通道未设导致序列化为 NaN。

**修法**:全局正则替换 D2C HTML(已经包含在 `loadDesignHtml` 里):

```typescript
const cleaned = raw.replace(/,\s*NaN\)/g, ", 1)");
```

### C.5 装饰大 SVG 跑出画布

**症状**:装饰背景 SVG(云形、装饰圆)的 `relativeX` 是负数,超出 1440×780 画布。

**根因**:设计师故意让装饰元素超出 Frame 边界营造层次感。

**修法**:根容器加 `overflow: hidden`:

```tsx
<div style={{ width: 1440, height: 780, overflow: "hidden" }}>
  ...
</div>
```

D2C HTML 里的 `<body>` 最外层一般已经设过,确认一下就行。

---

## 全局补丁 CSS(完整一份,直接抄)

```css
/* ─── MasterGo D2C 修正层 ─── */

/* 头像圆形蒙版(按需替换 PNG 文件名片段) */
.design-page div:has(> img[src*="<HEAD_AVATAR_HASH>"]) {
  background: #cae4ff !important;
  border-radius: 9999px !important;
  overflow: hidden !important;
  box-shadow: inset 0 0 0 1px #ffffff !important;
}

/* 胶囊文字单行不换行 */
.design-page [style*="border-radius: 40px"] span,
.design-page [style*="border-radius: 40px"] p {
  white-space: nowrap !important;
}
.design-page [style*="border-radius: 40px"] img,
.design-page [style*="border-radius: 40px"] svg {
  flex-shrink: 0;
}

/* 字体回退 */
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

跟设计稿对照后还有问题,**先 bash + curl 查文档**,再继续往这里加补丁,并把新发现的坑
写进本文档对应章节。
