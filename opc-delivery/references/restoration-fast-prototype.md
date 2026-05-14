# 快速复刻实现(模式 B,opt-in 入口)

## 目录

- [何时进本文件](#何时进本文件)
- [前置:跟谁衔接](#前置跟谁衔接)
- [7.1 脚手架(Next.js 15 + React 19 + Tailwind v4)](#71-脚手架nextjs-15--react-19--tailwind-v4)
- [7.2 装载 D2C HTML](#72-装载-d2c-html)
- [7.3 NavBar(多页跳转条)](#73-navbar多页跳转条)
- [7.4 验证](#74-验证)

## 何时进本文件

**只有用户明确选这条路才进**。产物**不适合接 API、不适合生产**,只服务于
"给客户/PM 看高保真效果"。判断流程见 [restoration-workflow.md](restoration-workflow.md)
第 5 节"模式选择"——默认走 [restoration-enterprise.md](restoration-enterprise.md),
不要无 opt-in 走这条路。
后续如果用户要接 API、权限、表单提交或真实业务逻辑，必须切回企业级实现重做，不要在
`dangerouslySetInnerHTML` 原型上硬接生产逻辑。

## 前置:跟谁衔接

进入本文件前应该已经完成 [restoration-workflow.md](restoration-workflow.md)
第 1-4.1 步:URL 解析、DSL 拉取、D2C HTML + 资源拉取、资源落盘。
**本模式不抽设计 token**(`extract-tokens.py` 不跑),整段 HTML 直接装载。

---

## 7.1 脚手架(Next.js 15 + React 19 + Tailwind v4)

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

`postcss.config.mjs`:
```javascript
const config = { plugins: { "@tailwindcss/postcss": {} } }
export default config
```

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

末尾追加 [rendering-patches.md](rendering-patches.md) 的全局补丁 CSS
(蒙版 / 胶囊 nowrap / 字体回退)。

## 7.2 装载 D2C HTML

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

## 7.3 NavBar(多页跳转条)

`src/components/NavBar.tsx`:
```tsx
import Link from "next/link"

const ROUTES = [
  { href: "/", label: "首页" },
  { href: "/agent-detail", label: "Agent 详情" },
  // ...
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

## 7.4 验证

走 [verification-implementation.md](verification-implementation.md)
**3B-1 快速复刻验证**(像素全等比对)。

---
