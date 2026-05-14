# API 字段映射与数据层

# API 字段映射与数据层

## 目录

- [4. 字段检测(扫 D2C HTML 找候选)](#4-字段检测扫-d2c-html-找候选)
- [5. 字段映射(用户确认后)](#5-字段映射用户确认后)
- [6. 数据层生成(per endpoint)](#6-数据层生成per-endpoint)
- [7. JSX 消费(替换写死数据)](#7-jsx-消费替换写死数据)

定位:进入 [api-wiring.md](api-wiring.md) 子流程的中段——已经用
`scripts/parse-api-docs.py` 拿到 `.codify/api-endpoints.json`,
现在要把 D2C/JSX 里写死的数据跟接口对齐。

## 4. 字段检测(扫 D2C HTML 找候选)

扫所有 D2C HTML / 你写的 JSX,自动识别"看着像写死数据"的节点。启发式:

| 节点特征 | 大概率是动态数据 |
|---|---|
| `data-name` 带有 `name` / `title` / `desc` / `text` / `value` / `count` / `time` / `date` 等关键词 | ✅ 动态 |
| 内容是纯数字(`2.4K` / `87%` / `¥1,234`) | ✅ 动态 |
| 内容是时间(`2025-01-15` / `15:30` / `2 小时前`) | ✅ 动态 |
| 重复结构 `act-1` / `act-2` / `act-3` —— 列表 | ✅ 动态 |
| 用户名 / 邮箱 / 手机号样式的字符串 | ✅ 动态 |
| 头像 / 图片 src(经常是用户 avatar) | ⚠️ 可能动态 |
| 内容是按钮文案("提交" / "登录") | ❌ 静态(除非 i18n) |
| 内容是标签 / 装饰文字("Beta" / "New") | ❌ 静态 |
| 内容是 logo / brand name | ❌ 静态 |

输出候选清单让用户确认:

```
扫到这些可能是动态的字段,你确认一下(可以勾选哪些是动态、哪些其实是文案):

agent-detail 页:
  [?] hero.title          "AURA Agent"            ← 很可能动态(用户名)
  [?] hero.subtitle       "智能客服系统"          ← 很可能动态(描述)
  [?] stats.userCount     "2.4K"                  ← 几乎肯定动态
  [?] stats.uptime        "1.8s"                  ← 几乎肯定动态
  [?] stats.satisfaction  "87%"                   ← 几乎肯定动态
  [?] act-1.title         "用户进入对话"          ← 几乎肯定动态(列表项)
  [?] act-1.time          "2 小时前"              ← 几乎肯定动态
  [+]  hero.tag            "Beta"                  ← 静态文案,不动
  [+]  cta.button          "试用"                  ← 静态文案
  
请回:全部接受 / 列出要排除的 ID
```

---

## 5. 字段映射(用户确认后)

每个动态字段 → 跟接口文档对一遍,做映射。优先级:

1. **字段名直接匹配**:HTML `data-name="user-name"` → API `data.user.name` 或 `data.name`
2. **语义匹配**:HTML "2.4K"(类型 number)→ 看 API 哪个字段是 number + 含 "count" / "total"
3. **重复结构 → 数组映射**:HTML `act-1/act-2/act-3` → API 返回的 `activities[]` 数组
4. **匹配不上 → 问用户**

映射结果存到 `.codify/api-mapping.json`:

```json
{
  "agent-detail": {
    "endpoint": "GET /api/agents/{id}",
    "source": ".codify/api-docs/agents.openapi.yaml#paths./agents/{id}.get",
    "fields": {
      "hero.title":       "data.name",
      "hero.subtitle":    "data.description",
      "stats.userCount":  "data.stats.userCount",
      "stats.uptime":     "data.stats.uptime",
      "stats.satisfaction": "data.stats.satisfaction"
    },
    "lists": {
      "activities": {
        "endpoint": "GET /api/agents/{id}/activities",
        "source": ".codify/api-docs/agents.openapi.yaml#paths./agents/{id}/activities.get",
        "itemFields": {
          "title": "title",
          "desc":  "description",
          "time":  "createdAt"
        }
      }
    }
  }
}
```

---

## 6. 数据层生成(per endpoint)

按映射结果在 `src/lib/api/` 下生成 fetch 模块:

```typescript
// src/lib/api/agents.ts
import { fetcher } from './_base'

export interface Agent {
  id: string
  name: string
  description: string
  stats: { userCount: number; uptime: number; satisfaction: number }
}

export async function getAgent(id: string): Promise<Agent> {
  return fetcher(`/api/agents/${id}`)
}

export interface Activity {
  id: string
  title: string
  description: string
  createdAt: string
}

export async function getAgentActivities(id: string): Promise<Activity[]> {
  return fetcher(`/api/agents/${id}/activities`)
}
```

`src/lib/api/_base.ts` 一个轻量 fetch 封装(根据项目栈选):

```typescript
// Next.js RSC + fetch(默认)
export async function fetcher<T>(path: string, init?: RequestInit): Promise<T> {
  const base = process.env.NEXT_PUBLIC_API_BASE ?? ''
  const res = await fetch(`${base}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}
```

如果项目用 SWR / React Query / Axios,跟着项目惯例走(嗅探 package.json)。

---

## 7. JSX 消费(替换写死数据)

把第 6.3 节写的 JSX 里**写死的字符串换成 prop 传入 + fetch 注入**:

改前:
```tsx
export function Hero() {
  return (
    <div className="bg-bg-card p-8 rounded-2xl">
      <h1 className="font-display text-5xl">AURA Agent</h1>
      <p className="text-base text-text-muted mt-2">智能客服系统</p>
    </div>
  )
}
```

改后:
```tsx
export function Hero({ agent }: { agent: Agent }) {
  return (
    <div className="bg-bg-card p-8 rounded-2xl">
      <h1 className="font-display text-5xl">{agent.name}</h1>
      <p className="text-base text-text-muted mt-2">{agent.description}</p>
    </div>
  )
}
```

入口 page.tsx:
```tsx
// src/app/agent-detail/[id]/page.tsx
import { getAgent, getAgentActivities } from '@/lib/api/agents'
import { AgentDetailPage } from '@/components/agent-detail/AgentDetailPage'

export default async function Page({ params }: { params: { id: string } }) {
  const [agent, activities] = await Promise.all([
    getAgent(params.id),
    getAgentActivities(params.id),
  ])
  return <AgentDetailPage agent={agent} activities={activities} />
}
```

---
