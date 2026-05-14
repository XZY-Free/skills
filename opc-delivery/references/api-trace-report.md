# API 溯源汇报

## 8. ★ 溯源汇报(强制触发,固定模板)

**接 API 这一步做完,必须打印这份汇报给用户**。不打印就不算完成。

```
═══════════════════════════════════════════════════════════════════════
本次 API 接入汇报(模式:企业级实现)
═══════════════════════════════════════════════════════════════════════

路由: /agent-detail/[id]

  视图字段 ⟵ 接口 (字段路径)
  ───────────────────────────────────────────────────────────────────
  Hero.title             ⟵ GET /api/agents/{id}            (data.name)
  Hero.subtitle          ⟵ GET /api/agents/{id}            (data.description)
  Stats.userCount        ⟵ GET /api/agents/{id}            (data.stats.userCount)
  Stats.uptime           ⟵ GET /api/agents/{id}            (data.stats.uptime)
  Stats.satisfaction     ⟵ GET /api/agents/{id}            (data.stats.satisfaction)
  ActivityItem.title     ⟵ GET /api/agents/{id}/activities ([].title)
  ActivityItem.desc      ⟵ GET /api/agents/{id}/activities ([].description)
  ActivityItem.time      ⟵ GET /api/agents/{id}/activities ([].createdAt)

  源文档: .codify/api-docs/agents.openapi.yaml
  生成的数据层: src/lib/api/agents.ts
  Page 入口:   src/app/agent-detail/[id]/page.tsx

路由: /login

  视图字段 ⟵ 接口 (字段路径)
  ───────────────────────────────────────────────────────────────────
  LoginForm.submit       ⟵ POST /api/auth/login            (返回 token 存 localStorage + redirect)

  源文档: .codify/api-docs/auth.md (自由文本)
  生成的数据层: src/lib/api/auth.ts
  Page 入口:   src/app/login/page.tsx

═══════════════════════════════════════════════════════════════════════
未接 API 的字段(静态,不需要):
  - Hero.tag           "Beta"        (装饰文案)
  - TopBar.brandName   "AURA"        (品牌名)
  - CTA.button         "试用"        (按钮文案)

接口文档里没用到的接口(本次还原范围外):
  - GET  /api/agents/list           (本次还原没列表页,跳过)
  - DELETE /api/agents/{id}         (本次还原没删除场景,跳过)
═══════════════════════════════════════════════════════════════════════

下一步:
  1. 用真后端跑一遍 dev,看每页数据是否正确渲染
  2. 走 verification-implementation.md 3B-2 做最终验证
```

汇报里**每一项都必须能溯源到具体文件 + 行号 / 字段路径**,不允许只写"接了某接口"。
用户拿到这份汇报应该能立刻审计:哪些没接、接对没、漏了哪个文档里的接口。

---

## 9. 没文档时的引导

`.codify/api-docs/` 不存在或为空时,跟用户说:

```
我没找到接口文档。我设了一个默认目录,你按以下任一方式给我:

a) 把文档放进 <projectDir>/.codify/api-docs/(我会自动识别格式):
     - OpenAPI / Swagger: *.yaml / *.yml / *.json
     - Postman Collection: *.json
     - 自由文本:           *.md

b) 直接告诉我文档的绝对路径,我去读

c) 你只有 URL + sample 响应也行:
     原话告诉我 "接口 GET https://api.x.com/users/me 返回 {...}",
     我帮你拼成最小 OpenAPI 写进 .codify/api-docs/_inline.openapi.yaml

d) 暂时没有 → 我跳过接 API,数据先写死。**告知:这意味着企业级实现欠了这一步**,
   后续文档到位告诉我"重新接 API",我会自动接上。

你选哪个?
```

---
