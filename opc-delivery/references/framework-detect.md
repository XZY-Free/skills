# 前端框架探嗅 + 推荐档

## 目录

- [总流程](#总流程)
- [步骤 1 ── 项目嗅探脚本](#步骤-1--项目嗅探脚本)
- [步骤 2 ── 指纹解读表](#步骤-2--指纹解读表)
- [步骤 3 ── 项目空白时询问用户](#步骤-3--项目空白时询问用户)
- [步骤 4 ── 推荐档触发联网查询](#步骤-4--推荐档触发联网查询)
- [步骤 5 ── 兜底默认](#步骤-5--兜底默认)
- [切换框架的代价](#切换框架的代价)
- [探嗅结果的存放](#探嗅结果的存放)
- [与脚手架阶段的衔接](#与脚手架阶段的衔接)

走 Magic 还原前必须确认目标框架。本文件覆盖**自动探嗅 → 用户选择 → 推荐档查询 → 兜底默认**全链。

---

## 总流程

```
1. 探嗅项目里现有指纹(package.json / config.* / 目录结构)
2. 找到了 → 跟现框架走,只问用户一句"沿用现栈?是 / 不是"
3. 找不到 → 直接询问用户给选项(含"推荐"档)
4. 用户选"推荐" → bash + curl 查"当前最稳最流行" → 决定 stack
5. 任何分支失败 → 兜底默认:Next.js 15 + React 19 + Tailwind v4
```

---

## 步骤 1 ── 项目嗅探脚本

```bash
ROOT="<projectDir 绝对路径>"
echo "=== package.json ==="
test -f "$ROOT/package.json" && jq '{name, dependencies, devDependencies}' "$ROOT/package.json"

echo "=== 配置文件指纹 ==="
ls "$ROOT" 2>/dev/null | grep -E '(next|vite|nuxt|svelte|astro|remix|gatsby|vue|angular|tailwind|postcss|tsconfig)\.config\.(js|mjs|cjs|ts|json)$'

echo "=== 锁文件 ==="
ls "$ROOT"/*lock* 2>/dev/null

echo "=== 源码目录结构 ==="
test -d "$ROOT/src" && ls -d "$ROOT/src"/* 2>/dev/null | head -20
test -d "$ROOT/app" && echo "(发现 app/ 目录 → 可能是 Next.js App Router)"
test -d "$ROOT/pages" && echo "(发现 pages/ 目录 → 可能是 Next.js Pages Router / Nuxt)"
```

---

## 步骤 2 ── 指纹解读表

| 指纹 | 推断框架 | 注意 |
|---|---|---|
| `next.config.*` + `dependencies.next` + `app/` 目录 | **Next.js App Router** | 13.4+ |
| `next.config.*` + `pages/` 目录 | Next.js Pages Router | 老项目 |
| `vite.config.*` + `dependencies.react` | Vite + React | |
| `vite.config.*` + `dependencies.vue` | Vite + Vue | |
| `nuxt.config.*` | Nuxt(Vue) | |
| `svelte.config.*` + `dependencies.@sveltejs/kit` | SvelteKit | |
| `astro.config.*` | Astro | |
| `remix.config.*` | Remix | |
| `angular.json` | Angular | |
| 只有 `index.html` 没有任何 config | 纯 HTML/CSS | 还原起来最简单 |
| `tailwind.config.*` + `@tailwindcss/postcss` | Tailwind v4 | |
| `tailwind.config.*` + `postcss.config.js` 旧格式 | Tailwind v3 | 写补丁 CSS 时注意 v3/v4 语法差异 |

### 嗅出框架后

跟用户对一句话:

> 我看到你项目用的是 **Next.js 15 App Router + Tailwind v4 + TypeScript**,
> 我就按这个栈来还原,可以吗?
> (yes → 继续;no → 跳到步骤 3)

---

## 步骤 3 ── 项目空白时询问用户

如果项目根没有任何指纹(空目录 / 只有 README),直接问用户选哪个栈:

```
question: 你想用什么前端栈来还原这个设计?
options:
  - label: "推荐档(我查当前最稳最流行的栈)"
    description: "我用 bash + curl 查最新社区数据,优先稳定 + 生态成熟"
  - label: "Next.js 15 + React 19 + Tailwind v4"
    description: "默认推荐栈,SSR / 静态 / API 一把抓,生态最全"
  - label: "Vite + React + TypeScript"
    description: "纯 SPA / 嵌入应用 / 不需要 SSR 时更轻"
  - label: "纯 HTML + CSS"
    description: "单页静态预览,最快出货,后续可手工套框架"
```

---

## 步骤 4 ── 推荐档触发联网查询

用户选"推荐档"时,跑下面这套 bash 查询(**不要 WebSearch / WebFetch**):

```bash
# 1. State of JS / State of CSS 最新调查(年度框架使用率)
python3 <skill-dir>/scripts/fetch-doc-snippet.py \
  'https://duckduckgo.com/html/?q=state+of+js+2026+frontend+framework+usage' \
  --keyword "React" --keyword "Next.js" --keyword "Vue"

# 2. npm 趋势 / 包下载量(过去 30 天)
for pkg in next react vue svelte @sveltejs/kit astro nuxt; do
  count=$(curl -sL "https://api.npmjs.org/downloads/point/last-month/$pkg" | jq -r '.downloads // "N/A"')
  echo "$pkg : $count"
done

# 3. 各框架最新 stable 版本
for pkg in next react vue svelte; do
  latest=$(curl -sL "https://registry.npmjs.org/$pkg/latest" | jq -r '.version')
  echo "$pkg latest: $latest"
done

# 4. DDG 搜社区当前推荐
curl -sL 'https://duckduckgo.com/html/?q=best+frontend+framework+2026+production' | head -100
```

把查询结果**简短总结给用户**(3-5 句话),然后给出**1 个推荐 + 1 个候补**:

```
查到了:
- Next.js 15.x 月下载 1.4 亿,React 19 月下载 4 亿,生态最稳
- Vite + React 月下载 1.6 亿,SPA 场景活跃
- SvelteKit 月下载 800 万,小项目快但生态偏小

推荐你用 Next.js 15 + React 19 + Tailwind v4(综合最稳),备选 Vite + React。
确认就开干,要换告诉我换哪个。
```

**所有数字都基于实际查询结果,不允许编造**。

---

## 步骤 5 ── 兜底默认

如果以上分支全部失败(嗅探查不到 / 用户未选择 / 联网查询 timeout),
**默认上 Next.js 15 + React 19 + TypeScript + Tailwind v4**。

理由:
- 现有 opc-delivery skill 的 `restoration-workflow.md` 脚手架就基于此栈,模板齐全;
- SSR / 静态 / API 都覆盖;
- React 19 + Tailwind v4 是当前推荐组合(2025+);
- D2C HTML 用 `dangerouslySetInnerHTML` 在 React 系最自然。

**默认时也告诉用户**:"我先按 Next.js 15 + React 19 + Tailwind v4 走,你不喜欢可以让我换"。

---

## 切换框架的代价

如果还原中途用户要换框架:

| 切换 | 改动量 |
|---|---|
| Next.js App Router ↔ Pages Router | 改路由层,page 文件不动 |
| Next.js ↔ Vite + React | 重建工程,React 组件代码可复用 |
| React ↔ Vue/Svelte | 几乎重写,但 D2C HTML 可继续用 `v-html` / `{@html}` 等机制 |

切换前一定让用户口头确认,**不要默默切**。

---

## 探嗅结果的存放

把探嗅结论写入 `.codify/state.json`(如果还没有就建一个):

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

后续会话直接读这个,不用每次重嗅。

---

## 与脚手架阶段的衔接

确认完框架后,回到 [restoration-workflow.md](restoration-workflow.md) 的"脚手架"步骤,
按选定框架建工程结构。当前 `restoration-workflow.md` 提供 Next.js 15 模板;
其它框架时,**先 `bash + curl` 查该框架最新 quickstart**,
再根据 quickstart 建工程,**不要凭印象写脚手架**。
