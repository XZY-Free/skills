# 06c — API 接入

**定位**: Magic 还原企业级实现模式或全栈实现把页面写死的占位数据换成真实接口数据。**快速复刻模式不走本流程**。

**不接 API ≠ 完成**。哪怕用户跳过, 企业级实现也要明确告知未接 API状态, 让用户知道这一步欠着。

## 何时读

- Magic 企业级模式写完 JSX 后(自动触发)
- 全栈实现把占位数据换真实接口
- 接 API 完成后必须打印**强制溯源汇报**(见本文末)

前置: [06a-implementation-plan.md](06a-implementation-plan.md) + [06b-implementation.md](06b-implementation.md)

---


**定位**: Magic 还原"企业级实现"模式或全栈实现把页面写死的占位数据换成真实接口数据。**快速复刻模式不走本流程**。

**不接 API ≠ 完成**。哪怕用户跳过, 企业级实现也要明确告知"未接 API"状态, 让用户知道这一步欠着。

## 目录

- [触发条件](#触发条件)
- [文档解析](#文档解析)
- [字段检测(扫 D2C HTML / JSX)](#字段检测扫-d2c-html--jsx)
- [字段映射](#字段映射)
- [数据层生成](#数据层生成)
- [JSX 消费(替换写死数据)](#jsx-消费替换写死数据)
- [⚠️ 强制溯源汇报](#-强制溯源汇报)
- [没文档时的引导](#没文档时的引导)

---

## 触发条件

进入企业级模式 + 写完 JSX 后**自动触发**:

```
1. 检查 <projectDir>/.codify/api-docs/ 目录
   ├── 存在且非空 → 列出文件 → 自动识别格式 → 进入文档解析
   └── 不存在 / 空 → 走"没文档时的引导"
2. 用户引导后给到文档 → 进入字段检测
3. 用户明确说"暂时没文档" → 跳过本流程, 但明确告诉用户:
     "数据现在是写死的, 后续接口文档到位后, 把它放进 .codify/api-docs/
      告诉我'重新接 API', 我自动接上。"
```

## 文档解析

约定标准目录:

```
<projectDir>/.codify/api-docs/
  ├── auth.openapi.yaml          # 用户认证(OpenAPI)
  ├── agents.openapi.yaml        # Agent 业务(OpenAPI)
  ├── billing.postman.json       # 计费(Postman Collection)
  ├── activities.md              # 活动接口(自由文本)
  └── README.md                  # 可选: 用户自己写的索引
```

目录不存在 → 自动 `mkdir -p .codify/api-docs/`。多文件支持, 所有文件都会被扫。**用户随手往里扔即可, 不要求统一格式**。

支持格式:

| 格式 | 识别 | 解析 |
|---|---|---|
| OpenAPI / Swagger | `.yaml/.yml/.json`, 顶层有 `openapi: 3.x` 或 `swagger: 2.0` | `paths` + `components.schemas` |
| Postman Collection | `.json`, 顶层有 `info.schema` 含 `postman.com` | `jq '.item[] \| {name, request}'` |
| 自由文本 markdown | `.md` | `## GET /xxx` 当 endpoint, 代码块当 sample |
| URL + sample(对话里贴) | 用户口述 `GET https://...` 返回 `{...}` | 当场拼最小 OpenAPI 写到 `_inline.openapi.yaml` |

```bash
python3 <skill-dir>/scripts/helpers/parse-api-docs.py \
  --dir <projectDir>/.codify/api-docs \
  --out <projectDir>/.codify/api-endpoints.json
```

## 字段检测(扫 D2C HTML / JSX)

启发式识别"看着像写死数据"的节点:

| 节点特征 | 大概率动态 |
|---|---|
| `data-name` 含 `name/title/desc/text/value/count/time/date` | ✅ |
| 纯数字(`2.4K` / `87%` / `¥1,234`) | ✅ |
| 时间(`2025-01-15` / `15:30` / `2 小时前`) | ✅ |
| 重复结构 `act-1` / `act-2` / `act-3` 列表 | ✅ |
| 用户名 / 邮箱 / 手机号样式 | ✅ |
| 头像 / 图片 src | ⚠️ 可能 |
| 按钮文案("提交" / "登录") | ❌ 静态 |
| 标签("Beta" / "New") / 品牌名 / logo | ❌ 静态 |

输出候选清单让用户确认(高置信、用户已说"直接做" → 自动接受)。

## 字段映射

每个动态字段 → 跟接口文档对一遍:

1. **字段名直接匹配**: `data-name="user-name"` → `data.user.name` 或 `data.name`
2. **语义匹配**: "2.4K"(number) → API 哪个字段是 number + 含 `count` / `total`
3. **重复结构 → 数组**: `act-1/act-2/act-3` → API 返回的 `activities[]`
4. **匹配不上 → 问用户**

存到 `.codify/api-mapping.json`:

```json
{
  "agent-detail": {
    "endpoint": "GET /api/agents/{id}",
    "source": ".codify/api-docs/agents.openapi.yaml#paths./agents/{id}.get",
    "fields": {
      "hero.title":       "data.name",
      "hero.subtitle":    "data.description",
      "stats.userCount":  "data.stats.userCount"
    },
    "lists": {
      "activities": {
        "endpoint": "GET /api/agents/{id}/activities",
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

## 数据层生成

按映射在 `src/lib/api/` 下生成 fetch 模块:

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

export async function getAgentActivities(id: string): Promise<Activity[]> {
  return fetcher(`/api/agents/${id}/activities`)
}
```

`src/lib/api/_base.ts` 轻量 fetch 封装(根据项目栈选):

```typescript
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

项目用 SWR / React Query / Axios → 跟着项目惯例(嗅探 `package.json`)。

## JSX 消费(替换写死数据)

写死的字符串 → prop 传入 + fetch 注入。

```tsx
// 改前
export function Hero() {
  return <h1>AURA Agent</h1>
}

// 改后
export function Hero({ agent }: { agent: Agent }) {
  return <h1>{agent.name}</h1>
}

// 入口
export default async function Page({ params }: { params: { id: string } }) {
  const [agent, activities] = await Promise.all([
    getAgent(params.id),
    getAgentActivities(params.id),
  ])
  return <AgentDetailPage agent={agent} activities={activities} />
}
```

## ⚠️ 强制溯源汇报

**接 API 这一步做完, 必须打印这份汇报给用户**。不打印就不算完成。

```
═══════════════════════════════════════════════════════════════════════
本次 API 接入汇报(模式: 企业级实现)
═══════════════════════════════════════════════════════════════════════

路由: /agent-detail/[id]

  视图字段 ⟵ 接口 (字段路径)
  ───────────────────────────────────────────────────────────────────
  Hero.title             ⟵ GET /api/agents/{id}            (data.name)
  Hero.subtitle          ⟵ GET /api/agents/{id}            (data.description)
  Stats.userCount        ⟵ GET /api/agents/{id}            (data.stats.userCount)
  ActivityItem.title     ⟵ GET /api/agents/{id}/activities ([].title)
  ActivityItem.time      ⟵ GET /api/agents/{id}/activities ([].createdAt)

  源文档: .codify/api-docs/agents.openapi.yaml
  生成的数据层: src/lib/api/agents.ts
  Page 入口:   src/app/agent-detail/[id]/page.tsx

═══════════════════════════════════════════════════════════════════════
未接 API 的字段(静态):
  - Hero.tag           "Beta"        (装饰文案)
  - CTA.button         "试用"        (按钮文案)

接口文档里没用到的接口(本次还原范围外):
  - GET  /api/agents/list           (本次没列表页, 跳过)
═══════════════════════════════════════════════════════════════════════

下一步:
  1. 用真后端跑一遍 dev, 看每页数据是否正确渲染
  2. 走 [07b-restore-verify.md](07b-restore-verify.md#3b-2-企业级实现验证) 做最终验证
```

汇报里**每一项都必须能溯源到具体文件 + 字段路径**, 不允许只写"接了某接口"。用户拿到这份汇报应该能立刻审计: 哪些没接、接对没、漏了哪个文档里的接口。

## 没文档时的引导

`.codify/api-docs/` 不存在或为空 → 跟用户说:

```
我没找到接口文档。我设了一个默认目录, 你按以下任一方式给我:

a) 把文档放进 <projectDir>/.codify/api-docs/(我会自动识别格式):
     - OpenAPI / Swagger: *.yaml / *.yml / *.json
     - Postman Collection: *.json
     - 自由文本:           *.md

b) 直接告诉我文档的绝对路径, 我去读

c) 你只有 URL + sample 响应也行:
     原话告诉我 "接口 GET https://api.x.com/users/me 返回 {...}",
     我帮你拼成最小 OpenAPI 写进 .codify/api-docs/_inline.openapi.yaml

d) 暂时没有 → 我跳过接 API, 数据先写死。
   告知: 这意味着企业级实现欠了这一步, 后续文档到位告诉我"重新接 API", 我会自动接上。
```

