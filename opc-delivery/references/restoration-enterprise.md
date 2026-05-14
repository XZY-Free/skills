# 企业级还原实现(模式 A,默认入口)

## 目录

- [核心理念](#核心理念)
- [前置:跟谁衔接](#前置跟谁衔接)
- [6.1 写 Tailwind 配置(吃设计 token)](#61-写-tailwind-配置吃设计-token)
- [6.2 组件分解策略](#62-组件分解策略)
- [6.3 写 JSX(数据先写死)](#63-写-jsx数据先写死)
- [6.4 接 API(跳 api-wiring.md)](#64-接-api跳-api-wiringmd)
- [6.5 路由 / 入口](#65-路由--入口)
- [6.6 验证](#66-验证)

定位:**Magic 还原的默认模式**。本文件是该模式的完整入口——
SKILL.md / restoration-workflow.md 第 5 节"模式选择"判完是默认时,直接读本文件。

## 核心理念

**D2C HTML 是视觉参考稿,不是代码来源**。我们参照 D2C 写正常 React 组件,
用 Tailwind 抄设计 token,SVG/PNG 直接用,字体 / 蒙版 / 渐变用正常 CSS 实现。
**像素精度对齐 95-98%(允许小差异),换来可维护 / 可测试 / 可演进**。

## 前置:跟谁衔接

进入本文件前应该已经完成 [restoration-workflow.md](restoration-workflow.md)
第 1-4 步:
- URL 解析(`scripts/parse-mastergo-url.py`)
- DSL 拉取(整站 / 单页)
- D2C HTML + 资源拉取(`getD2c`)
- 资源落盘(`scripts/sync-d2c-assets.sh`)+ 设计 token 抽取(`scripts/extract-tokens.py`)
- restoration state 已记录 source fileId/layerId/contentId、页面主语言、模式和验证状态

前置没做完不要直接跳进本文件——会拿不到 design-tokens.json 之类下游需要的产物。

---

## 6.1 写 Tailwind 配置(吃设计 token)

根据 `.codify/design-tokens.json` 写 `tailwind.config.ts`:

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
        // 按 design-tokens.json 里的高频色填
      },
      fontFamily: {
        display: ['DingTalk JinBuTi', 'PingFang SC', 'system-ui', 'sans-serif'],
        body:    ['PingFang SC', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        // 按 design-tokens.json 里抽到的字号梯度填
      },
      spacing: {
        // 同上
      },
    },
  },
} satisfies Config
```

字体加载用 `next/font/local` 或 CDN `@font-face`(详见
[rendering-patches.md](rendering-patches.md) 的字体补丁)。

## 6.2 组件分解策略

D2C HTML 里 `data-name="agent-hero"` / `data-name="user-card"` 等就是天然的
**组件边界**。决策规则:

| D2C 节点 | 怎么处理 |
|---|---|
| 一级 `data-name` 节点(`topbar` / `hero` / `grid` 等) | → 一个 React 组件 `<TopBar />` / `<Hero />` / `<Grid />` |
| 二级带语义的 `data-name`(`brand` / `breadcrumb` / `tb-share`) | → 子组件,放到对应一级组件里 |
| 重复结构(`act-1` / `act-2` / `act-3`) | → 一个组件 + `.map()` 循环渲染 |
| 无 `data-name` 或语义模糊的(`group-1234`) | → 不单独拆,留在父组件 JSX 里 |

先输出简短组件树清单。高置信、用户已说“直接做”时可以自动执行；低置信或会影响公共
组件边界时再让用户选择，不要变成长问卷。

```
我准备这样拆 agent-detail 这一页:

src/components/agent-detail/
├── AgentDetailPage.tsx     ← 总入口
├── TopBar.tsx              ← 品牌 + 面包屑 + 分享(原 data-name="topbar")
├── Hero.tsx                ← 头部介绍(原 data-name="hero")
├── ActivityTimeline.tsx    ← 时间轴(原 data-name="grid")
└── ActivityItem.tsx        ← 单个 act-N 节点的组件(.map 渲染)

这样拆 OK 吗?有要调整的吗?
```

## 6.3 写 JSX(数据先写死)

参考 D2C HTML 写 JSX,用 Tailwind 类(吃 6.1 配置),例:

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

**视觉参考做法**:把 MasterGo 截图 + 你写的 JSX 渲染截图并排,
用 [verification-implementation.md](verification-implementation.md) 3B-2 检查。
差 1-3px 是可接受代价。

## 6.4 接 API(跳 [api-wiring.md](api-wiring.md))

写完 JSX 后,**自动扫 `.codify/api-docs/`**:

- 找到接口文档 → 先运行 `scripts/parse-api-docs.py` 生成 `.codify/api-endpoints.json`,
  再走 `api-wiring.md` 完整流程(字段检测 → 映射 → 数据层 → JSX 消费 → 溯源汇报)
- 没找到 → 友好提示用户怎么放,等用户回应

**接 API 是企业级实现的标配步骤,不接 API = 没做完**。
即使用户暂时没接口文档,也要明确告诉他"现在数据是写死的,接到 API 才算完整生产代码"。
用户明确说“暂时没有接口文档”时，状态标为 `api-pending`，不要假装真数据已接入。

## 6.5 路由 / 入口

每页一个路由(Next.js App Router):

```tsx
// src/app/agent-detail/page.tsx
import { AgentDetailPage } from '@/components/agent-detail/AgentDetailPage'

export default async function Page() {
  // RSC 模式:在这里 fetch 数据(api-wiring.md 会生成)
  const data = await getAgentDetail()
  return <AgentDetailPage data={data} />
}
```

`NavBar` 这种跨页导航单独抽到 `src/components/NavBar.tsx`,
放在 `app/layout.tsx` 里全局挂载。

## 6.6 验证

走 [verification-implementation.md](verification-implementation.md)
**3B-2 企业级实现验证**:
- 视觉相似度 ≥ 95%(允许小差异)
- 接 API 后真数据正确渲染
- **强制打印 API 溯源汇报**(见 [api-trace-report.md](api-trace-report.md))
- 业务逻辑测试覆盖(可选)

---
