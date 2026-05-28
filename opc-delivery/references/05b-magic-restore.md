# 05b — MasterGo Magic 还原

用户要把 MasterGo 设计稿一次性转成前端代码。真实交付物是可运行且验证过的前端实现, 不是 DSL、D2C HTML、资源目录或截图报告。

还原代码应**保留原设计稿页面文案语言**, 不要在组件化、接 API 或快速复刻时自动翻译 UI 文案。

## 何时读

- 收到 `https://mastergo.com/file/...?layer_id=...` 还原需求
- 还原中需要切换框架或回画布微调
- 配套设计流程在 [05a-codify-design.md](05a-codify-design.md)

跳过场景: 已经在某条 unit 内推进, Magic 流程已锁定。

## 目录

- [Magic MCP 可用性门禁](#magic-mcp-可用性门禁)
- [URL 解析](#url-解析)
- [整站目录拉取](#整站目录拉取)
- [拉每页 D2C](#拉每页-d2c)
- [状态记录 + 资源落盘 + token 抽取](#状态记录--资源落盘--token-抽取)
- [前端框架探嗅](#前端框架探嗅)
- [模式选择(默认企业级)](#模式选择默认企业级)
- [模式 A 企业级实现](#模式-a-企业级实现)
- [模式 B 快速复刻 opt-in](#模式-b-快速复刻-opt-in)
- [原型连线限制](#原型连线限制)

---

还原代码应**保留原设计稿页面文案语言**, 不要在组件化、接 API 或快速复刻时自动翻译 UI 文案。

**两种模式**:

| 模式 | 用途 | 默认 | 代码形态 |
|---|---|---|---|
| **企业级实现** | 真正交付到生产、要接 API、要写业务逻辑 | ✅ | 正常 React/Vue 组件, Tailwind/CSS, 正常 fetch, **D2C 当视觉参考稿** |
| **快速复刻** | 给客户/PM 看效果、临时演示、内部 demo | opt-in | `dangerouslySetInnerHTML` 整段塞 D2C HTML, 数据写死, 像素 100% 一致 |

**模式不混用, 一个项目选一种**。需要切换就重新建工程。

## Magic MCP 可用性门禁

开始还原前确认:

- 当前宿主配置里有 MasterGo Magic MCP, token 不是占位
- 当前会话能看到 `mcp__mastergo-magic-mcp__*` 或等价 Magic 工具
- URL 里有可解析的 `layer_id`
- 用户要整站 → 有根容器 Frame 或每页 Frame 的链接

缺任一项 → 回 [mcp-setup.md](mcp-setup.md) / [troubleshooting.md](troubleshooting.md#magic-排障) 定位阻塞, 按用户行动契约告诉用户缺什么、怎么补、补完后继续什么。**不创建本地前端项目、不手写假页面、不说还原完成**。

只有用户明确改口"没有 MCP, 先根据截图/描述写一个独立前端原型"时, 才离开 MasterGo 还原范围, 转普通前端任务。**不要仍称为 MasterGo 还原完成**。

**不要只因为 `tool_search` 暴露出 Magic MCP 工具就直接调用 `getDsl`**。还原前必须确认当前宿主配置文件里有 `@mastergo/magic-mcp` 和非占位 token。配置缺失/占位时调用工具只会得到误导性的权限错误。

## URL 解析

合法 URL 形态:

```
https://mastergo.com/file/<fileId>?file=<fileId>&layer_id=<a>%3A<b>&pageid=<x>%3A<y>
https://mastergo.com/goto/<short>?file=<fileId>&layer_id=<a>%3A<b>
```

**只取 `layer_id=`**。`%3A` URL-decode 是 `:`, MCP 会自己处理。忽略 `pageid` / `page_id`(那是画布页 Tab, 不是图层 ID)。

优先用脚本解析:

```bash
python3 <skill-dir>/scripts/mandatory/parse-mastergo-url.py \
  'https://mastergo.com/file/193097526299871?layer_id=2%3A77196'
```

脚本输出 `fileId`、`layerId` 和 `contentId`。

短链 `/goto/xxx` 用户没在画布选中状态下复制 → 往往不带 `layer_id=`, 报 `Could not extract layerId from URL`。让用户**画布选中目标 Frame 后重新复制 URL**。

## 整站目录拉取

```
mcp__getDsl(fileId, rootLayerId)  # 一次拿到所有子页面
```

让用户在 MasterGo 里**画一个根容器 Frame 包住所有页面 Frame**, 右键复制根容器链接(必须带 `layer_id=`), 再走这一步。

解析返回 JSON, 遍历根容器 `children`, 每个 type=FRAME、宽度 ≥ 1280 的子节点 = 独立页面。映射成路由, 让用户**确认路由命名**再开干。

整站根容器 DSL 偶尔超过 20MB → 报 `Request too large`。改成对每个子 Frame 单独 `getDsl`, 详见 [troubleshooting.md](troubleshooting.md#magic-request-too-large)。

## 拉每页 D2C

```python
contentId = f"{fileId}-{layerId.replace(':','-')}"
mcp__getD2c(contentId, fileId, outDir=f".mg/{routeKey}")
```

每个页面单独一个 outDir。返回:

```
.mg/<routeKey>/
├── <contentId>.html      # 主 HTML
└── asset/
    ├── icons/*.svg
    └── images/*.png|jpg
```

遇到 `❌ 未找到该 contentId 对应的数据` → 让用户在 MasterGo 里点对应 Frame 的"发送数据"按钮, 等他点完再继续。**不让用户复制 contentId, 你能自己拼**。

## 状态记录 + 资源落盘 + token 抽取

### 状态记录

```json
{
  "restoration": {
    "source": {
      "fileId": "<fileId>",
      "layerId": "<layerId>",
      "contentId": "<contentId>"
    },
    "mode": "enterprise|quick-mirror|pending",
    "pages": [
      {"route": "/dashboard", "language": "simplified-chinese", "dslHash": "...", "d2cHash": "..."}
    ],
    "verification": {"status": "pending"}
  }
}
```

页面主语言从 D2C/DSL 可见文本推断, 后续 JSX、mock、空态、错误态**不要擅自翻译**。

### 资源落盘(两种模式都做)

```bash
bash <skill-dir>/scripts/helpers/sync-d2c-assets.sh .mg src/<project>/public/assets
# 输出: 每个 route 一行 "synced: <route>", 末尾汇总数量
```

跑 update 流时(见 [07b-restore-verify.md](07d-restore-patches.md#设计稿更新流)): `bash <skill-dir>/scripts/helpers/sync-d2c-assets.sh .mg_v2 src/<project>/public/assets`。

### 设计 token 抽取(仅企业级模式)

```bash
python3 <skill-dir>/scripts/helpers/extract-tokens.py \
  --glob "<projectDir>/.mg/**/*.html" \
  --out "<projectDir>/.codify/design-tokens.json"
```

输出摘要给用户(高频色 top 10 / 字体 / 字号梯度), 建议写进 Tailwind config。

## 前端框架探嗅

走 Magic 还原前必须确认目标框架。流程: **自动探嗅 → 用户选择 → 推荐档查询 → 兜底默认**。

### 探嗅脚本

```bash
ROOT="<projectDir 绝对路径>"
test -f "$ROOT/package.json" && jq '{name, dependencies, devDependencies}' "$ROOT/package.json"
ls "$ROOT" 2>/dev/null | grep -E '(next|vite|nuxt|svelte|astro|remix|gatsby|vue|angular|tailwind|postcss|tsconfig)\.config\.(js|mjs|cjs|ts|json)$'
ls "$ROOT"/*lock* 2>/dev/null
test -d "$ROOT/src" && ls -d "$ROOT/src"/* 2>/dev/null | head -20
test -d "$ROOT/app" && echo "(发现 app/ → 可能是 Next.js App Router)"
test -d "$ROOT/pages" && echo "(发现 pages/ → 可能是 Next.js Pages Router / Nuxt)"
```

### 指纹解读

| 指纹 | 推断 |
|---|---|
| `next.config.*` + `dependencies.next` + `app/` | Next.js App Router 13.4+ |
| `next.config.*` + `pages/` | Next.js Pages Router(老项目) |
| `vite.config.*` + `react` | Vite + React |
| `vite.config.*` + `vue` | Vite + Vue |
| `nuxt.config.*` | Nuxt |
| `svelte.config.*` + `@sveltejs/kit` | SvelteKit |
| `astro.config.*` | Astro |
| `tailwind.config.*` + `@tailwindcss/postcss` | Tailwind v4 |
| `tailwind.config.*` + `postcss.config.js` 旧格式 | Tailwind v3 |
| 只有 `index.html` 无 config | 纯 HTML/CSS |

嗅出后对一句话: "我看到你项目用的是 X, 我按这个栈来还原, 可以吗?"

### 项目空白时

选项: 推荐档(我查最稳最流行) / Next.js 15 + React 19 + Tailwind v4 / Vite + React + TS / 纯 HTML + CSS。

用户选"推荐档"时用 bash + curl 查 npm 趋势 / 最新 stable / 社区调查(**不要 WebSearch / WebFetch**):

```bash
# npm 月下载量
for pkg in next react vue svelte @sveltejs/kit astro nuxt; do
  count=$(curl -sL "https://api.npmjs.org/downloads/point/last-month/$pkg" | jq -r '.downloads // "N/A"')
  echo "$pkg : $count"
done

# 最新 stable 版本
for pkg in next react vue svelte; do
  latest=$(curl -sL "https://registry.npmjs.org/$pkg/latest" | jq -r '.version')
  echo "$pkg latest: $latest"
done
```

简短总结给用户(3-5 句), 给出 1 个推荐 + 1 个候补。**所有数字基于实际查询, 不允许编造**。

### 兜底默认

所有分支失败 → **Next.js 15 + React 19 + TypeScript + Tailwind v4**。理由: 还原脚手架基于此栈模板齐全, SSR/静态/API 都覆盖, D2C HTML 用 `dangerouslySetInnerHTML` 在 React 系最自然。默认时也告诉用户"我先按此栈走, 不喜欢可以换"。

### 探嗅结果存放

```json
{
  "framework": {
    "name": "next.js",
    "version": "15.1.0",
    "router": "app",
    "ui": ["tailwindcss@4", "react@19"],
    "language": "typescript",
    "detectedAt": "<ISO 时间>",
    "source": "package.json"
  }
}
```

写入 `.codify/state.json`, 后续会话直接读。

### 切换框架

| 切换 | 改动量 |
|---|---|
| Next.js App ↔ Pages Router | 改路由层, page 文件不动 |
| Next.js ↔ Vite + React | 重建工程, React 组件代码可复用 |
| React ↔ Vue/Svelte | 几乎重写, 但 D2C HTML 可继续用 `v-html` / `{@html}` |

切换前一定让用户口头确认, **不要默默切**。

## 模式选择(默认企业级)

**默认走企业级实现**。**只有以下情况切快速复刻**:

- 用户明确说"快速复刻 / 高保真原型 / 给客户看一眼 / 像素 100% 一致"
- 用户明确说"不用接 API / 数据先写死"
- 用户明确说"我不想要 React 组件, 我要 dangerouslySetInnerHTML"

走快速复刻前**显式跟用户确认一次**:

> 你确认要走快速复刻模式吗? 这种模式产物**不适合接 API、不适合生产**, 只适合临时演示。后续要接 API 必须重做一遍企业级模式。还是要走?(yes / no)

## 模式 A 企业级实现

**D2C HTML 是视觉参考稿, 不是代码来源**。参照 D2C 写正常 React 组件, Tailwind 抄设计 token, SVG/PNG 直接用, 字体/蒙版/渐变用正常 CSS。**像素精度对齐 95-98%(允许小差异), 换来可维护/可测试/可演进**。

### A.1 Tailwind 配置(吃设计 token)

```typescript
import type { Config } from 'tailwindcss'

export default {
  content: ['./src/**/*.{ts,tsx,html}'],
  theme: {
    extend: {
      colors: {
        bg:       { canvas: '#0A0E1A', card: '#111729' },
        brand:    { 500: '#4FB8FF', 600: '#3BA8F0' },
        text:     { primary: '#FFFFFF', muted: '#9CA3AF' },
      },
      fontFamily: {
        display: ['DingTalk JinBuTi', 'PingFang SC', 'system-ui', 'sans-serif'],
        body:    ['PingFang SC', 'system-ui', 'sans-serif'],
      },
      // fontSize / spacing 按 design-tokens.json 抽到的梯度填
    },
  },
} satisfies Config
```

字体加载用 `next/font/local` 或 CDN `@font-face`(详见 [07b-restore-verify.md](07d-restore-patches.md#渲染补丁))。

### A.2 组件分解策略

D2C HTML 里的 `data-name="..."` 就是天然组件边界:

| D2C 节点 | 处理 |
|---|---|
| 一级 `data-name`(`topbar` / `hero` / `grid`) | → 一个 React 组件 `<TopBar />` |
| 二级带语义的 `data-name`(`brand` / `breadcrumb`) | → 子组件 |
| 重复结构(`act-1` / `act-2` / `act-3`) | → 一个组件 + `.map()` |
| 无 `data-name` 或语义模糊 | → 不单独拆, 留在父组件 |

先输出简短组件树清单。高置信、用户已说"直接做"时**自动执行**; 低置信或会影响公共组件边界时再选择。

### A.3 写 JSX(数据先写死)

D2C 给的:

```html
<div data-name="hero" style="background: #111729; padding: 32px; border-radius: 16px">
  <h1 style="font-family: 'DingTalk JinBuTi'; font-size: 48px; color: #FFFFFF">AURA Agent</h1>
  <p style="font-size: 16px; color: #9CA3AF; margin-top: 8px">智能客服系统</p>
</div>
```

改写成 JSX:

```tsx
export function Hero({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="bg-bg-card p-8 rounded-2xl">
      <h1 className="font-display text-5xl text-text-primary">{title}</h1>
      <p className="text-base text-text-muted mt-2">{subtitle}</p>
    </div>
  )
}
```

视觉参考做法: MasterGo 截图 + 你写的 JSX 渲染截图并排, 用 [07b-restore-verify.md](07b-restore-verify.md#3b-2-企业级实现验证) 3B-2 检查。差 1-3px 是可接受代价。

### A.4 接 API

写完 JSX 后**自动扫 `.codify/api-docs/`**:

- 找到接口文档 → 跑 `scripts/helpers/parse-api-docs.py` 生成 `.codify/api-endpoints.json`, 走 [06c-api-wiring.md](06c-api-wiring.md) 完整流程
- 没找到 → 友好提示用户怎么放, 等用户回应

**接 API 是企业级实现的标配步骤, 不接 API = 没做完**。即使用户暂时没接口文档, 也明确告诉他"现在数据是写死的, 接到 API 才算完整生产代码"。

用户明确说"暂时没有接口文档" → 状态标 `api-pending`, **不假装真数据已接入**。

### A.5 路由 / 入口

每页一个路由(Next.js App Router):

```tsx
// src/app/agent-detail/page.tsx
import { AgentDetailPage } from '@/components/agent-detail/AgentDetailPage'

export default async function Page() {
  const data = await getAgentDetail()
  return <AgentDetailPage data={data} />
}
```

`NavBar` 这种跨页导航抽到 `src/components/NavBar.tsx`, `app/layout.tsx` 全局挂载。

### A.6 验证

走 [07b-restore-verify.md](07b-restore-verify.md#3b-2-企业级实现验证) 3B-2:

- 视觉相似度 ≥ 95%(允许小差异)
- 接 API 后真数据正确渲染
- **强制打印 API 溯源汇报**
- 业务逻辑测试覆盖(可选)

## 模式 B 快速复刻 opt-in

**只有用户明确选这条路才进**。产物**不适合接 API、不适合生产**。后续如果用户要接 API、权限、表单提交或真实业务逻辑, **必须切回企业级实现重做**, 不要在 `dangerouslySetInnerHTML` 原型上硬接生产逻辑。

本模式**不抽设计 token**(`extract-tokens.py` 不跑), 整段 HTML 直接装载。

### B.1 脚手架(Next.js 15 + React 19 + Tailwind v4)

`package.json`:

```json
{
  "dependencies": { "next": "^15.1.0", "react": "^19.0.0", "react-dom": "^19.0.0" },
  "devDependencies": {
    "@tailwindcss/postcss": "^4.0.0",
    "@types/node": "^22", "@types/react": "^19", "@types/react-dom": "^19",
    "tailwindcss": "^4.0.0", "typescript": "^5"
  }
}
```

`postcss.config.mjs`: `{ plugins: { "@tailwindcss/postcss": {} } }`

`src/app/globals.css` 顶部:

```css
@import "tailwindcss";
@font-face {
  font-family: "DingTalk JinBuTi";
  src: url("https://cdn.jsdelivr.net/gh/cn-fontsource/cn-fontsource-ding-talk-jin-bu-ti/dist/font.woff2") format("woff2");
  font-display: swap;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
```

末尾追加 [07b-restore-verify.md](07d-restore-patches.md#渲染补丁) 的全局补丁 CSS。

### B.2 装载 D2C HTML

`src/lib/load-design.ts`:

```typescript
import fs from "node:fs"
import path from "node:path"

export function loadDesignHtml(page: string): string {
  const abs = path.join(process.cwd(), "src", "design", `${page}.html`)
  const raw = fs.readFileSync(abs, "utf-8")
  const rewritten = raw.replace(/\.\/asset\//g, `/assets/${page}/`)
  const cleaned   = rewritten.replace(/,\s*NaN\)/g, ", 1)")  // SVG 渐变 alpha 修
  const m = cleaned.match(/<body[^>]*>([\s\S]*)<\/body>/i)
  return m ? m[1] : cleaned
}
```

每个路由 `page.tsx`:

```tsx
import { loadDesignHtml } from "@/lib/load-design"

export default function Page() {
  const html = loadDesignHtml("agent-detail")
  return (
    <div className="design-page grid min-h-screen place-items-center bg-[#f0f3fa] p-4">
      <div
        className="relative shadow-2xl ring-1 ring-black/5"
        style={{ width: 1440, height: 900, overflow: "hidden" }}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  )
}
```

### B.3 NavBar(多页跳转条)

`src/components/NavBar.tsx`:

```tsx
import Link from "next/link"

const ROUTES = [
  { href: "/", label: "首页" },
  { href: "/agent-detail", label: "Agent 详情" },
]

export default function NavBar({ active }: { active: string }) {
  return (
    <nav className="fixed left-1/2 top-3 z-50 flex -translate-x-1/2 gap-1 rounded-full bg-white/80 p-1 shadow-md ring-1 ring-black/5 backdrop-blur">
      {ROUTES.map(r => (
        <Link key={r.href} href={r.href}
          className={
            "rounded-full px-3 py-1.5 text-xs " +
            (active === r.href ? "bg-[#2C68FF] text-white" : "text-[#1A1C27] hover:bg-black/5")
          }
        >
          {r.label}
        </Link>
      ))}
    </nav>
  )
}
```

### B.4 验证

走 [07b-restore-verify.md](07b-restore-verify.md#3b-1-快速复刻验证) 3B-1 像素全等比对。

## 原型连线限制

**MasterGo Magic MCP 不下发画布上画的 Frame ↔ Frame 原型连线** — 这是 MCP 协议的能力边界, 不是 bug、不是缓存、不是同步问题。

跨 Frame 跳转用自然语言确认后, 代码里手写 `<Link>` / `router.push`。完整诊断方法见 [troubleshooting.md](troubleshooting.md#dsl-看不到画布上画的原型连线)。
