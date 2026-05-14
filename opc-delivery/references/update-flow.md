# 设计稿更新流(增量 diff)

## 目录

- [0. 更新流适用性门禁](#0-更新流适用性门禁)
- [1. 拉最新 DSL(先根容器,再每页)](#1-拉最新-dsl先根容器再每页)
- [2. 找到旧 DSL 缓存位置](#2-找到旧-dsl-缓存位置)
- [3. 解析嵌套 JSON 字符串(直接用脚本)](#3-解析嵌套-json-字符串直接用脚本)
- [4. 关注的字段优先级](#4-关注的字段优先级)
- [5. 关于"原型连线"的限制(再次强调)](#5-关于原型连线的限制再次强调)
- [6. 对应 D2C 重拉](#6-对应-d2c-重拉)
- [7. 增量推到代码](#7-增量推到代码)
- [8. 状态归档和完成判定](#8-状态归档和完成判定)
- [9. 总结对话用的报告模板](#9-总结对话用的报告模板)

用户说"页面更新了 / 设计变了 / 重新拉一下"时进入。**核心思想:增量比对,只补差异,
不重头来**。

前置:这条流程只对 **Magic 还原项目**(项目里已经有 `src/design/<route>.html` 之类
落盘结构)有意义。Codify 设计项目用 `get_design_diff` 走 [verification.md](verification.md)
的 3A 即可。

遵守 [delivery-contract.md](delivery-contract.md):更新流的交付物是增量变更已应用到目标
代码并复验,不是 diff 报告本身。
文本 diff 还要遵守 [copy-language.md](copy-language.md):如果新旧版本语种发生变化,
先判断是不是用户有意改文案语种;不确定时用选择题澄清。

---

## 0. 更新流适用性门禁

进入更新流前确认:

- 当前项目已有 Magic 还原落盘结构或明确的 Codify 设计基准;
- 当前宿主 Magic MCP 可用,或 Codify 设计路径可用;
- 有旧 DSL / 旧 D2C / 旧代码可比对;
- 用户给的是"更新已有成果",不是第一次还原或第一次设计。

不满足时:

- 第一次还原 → 回 [restoration-workflow.md](restoration-workflow.md);
- Codify 画布设计 → 回 [design-workflow.md](design-workflow.md) + 3A;
- 缺 MCP / token / layerId → 回 [mcp-setup.md](mcp-setup.md) 或 troubleshooting;
- 不能只输出"变更分析报告"后说同步完成。

---

## 1. 拉最新 DSL(先根容器,再每页)

```
mcp__getDsl(fileId, rootLayerId)         # 根容器
mcp__getDsl(fileId, page1LayerId)        # 各子页面(避免 20MB 限制)
mcp__getDsl(fileId, page2LayerId)
...
```

并发拉,每个调用单独保存到不同的 outDir 或缓存。

---

## 2. 找到旧 DSL 缓存位置

Claude Code 自动落盘所有 MCP 调用结果,在:

```
~/.claude/projects/<project-hash>/tool-results/toolu_*.json
```

`<project-hash>` 是当前工作目录路径转的 hash(例如
`/Users/sunshine/IdeaProjects/人力mcp测试` 对应
`-Users-sunshine-IdeaProjects---mcp--`)。

定位最近的 DSL 调用:

```bash
ls -lt ~/.claude/projects/-*-mcp--/tool-results/toolu_*.json | head -10
```

按文件大小区分:根容器 DSL 一般 1-2MB,单页 60-100KB,D2C 1-2MB。

---

## 3. 解析嵌套 JSON 字符串(直接用脚本)

MCP 工具结果是双层 JSON:外层数组 `[{type:"text", text:"..."}]`,内层 text 是
JSON 字符串需要二次解析。**直接用 bundled 脚本**,不要每次重写:

```bash
python3 <skill-dir>/scripts/dsl-diff.py <old.toolu.json> <new.toolu.json>
# 默认 JSON 输出;加 --output summary 只看汇总
python3 <skill-dir>/scripts/dsl-diff.py <old.toolu.json> <new.toolu.json> --language-risk
```

脚本会自动:
- 处理双层 JSON(`[{text: "..."}]` → 解析内层);
- 收集每个 `id` 的签名(`type / name / text / fill / strokeColor / interactive`);
- 输出 `added` / `removed` / `changed` 三类 + 每个 changed 节点的字段级 diff。
- 输出 `categories.text/fill/layout/interaction` 和 `language_risks`。如果新旧文案语种
  可能变化,先确认是否为用户有意修改。

---

## 4. 关注的字段优先级

| 字段 | 含义 | 优先处理 |
|---|---|---|
| `text` 子节点的 text | 文本内容(标题/按钮文案改动) | ⭐⭐⭐ |
| `interactive` | 跳转钩子(注意只是组件级,不是页面跳转) | ⭐⭐⭐ |
| `fill` (paint_*) | 颜色 token | ⭐⭐ |
| `font_*` | 字号 / 字体 | ⭐⭐ |
| `layoutStyle.width/height` | 元素尺寸 | ⭐⭐ |
| `relativeX/Y` | 元素位置 | ⭐ |
| `path.data` | SVG 路径数据 | ⭐ |
| 节点新增/删除(id 集合 diff) | 整块图层增删 | ⭐⭐⭐ |

---

## 5. 关于"原型连线"的限制(再次强调)

**MasterGo Magic MCP 的 DSL 不下发画布 Frame ↔ Frame 的原型连线**——完整诊断脚本、
判定逻辑、修法见
[troubleshooting-magic.md A.6 "DSL 看不到画布上画的原型连线"](troubleshooting-magic.md#a6-dsl-看不到画布上画的原型连线)。

在 update 流程里,这条限制的具体影响是:做 DSL diff 时不要期望 `interactive` 字段
出现新的跨 Frame 跳转;如果用户说"我刚加了一条连线",在解释清楚 MCP 能力边界后,
让用户口述跳转关系,代码里手写 `<Link>` / `router.push`。

---

## 6. 对应 D2C 重拉

DSL 验证设计真的变了之后,让用户**重新点"发送数据"**触发 D2C 重生成,再用**新
outDir** 重拉 D2C:

```python
# 用一个版本号目录避免覆盖旧资源
mcp__getD2c(contentId, fileId, outDir=f".mg_v2/{routeKey}")
```

对比新旧 D2C HTML 的 md5:

```bash
md5 .mg/<route>/*.html .mg_v2/<route>/*.html
```

- md5 一样 = 缓存还没刷新(让用户再点一次,详见
  [troubleshooting-magic.md](troubleshooting-magic.md) 的 D2C 缓存小节);
- md5 不同 = 把新资源拷到 `public/assets/`,HTML 拷到 `src/design/`,覆盖旧的。

---

## 7. 增量推到代码

只动变化的页面:

```bash
# 1. 把变了的 D2C 替换
cp .mg_v2/<route>/*.html src/design/<route>.html
cp -r .mg_v2/<route>/asset/icons/*  public/assets/<route>/icons/
cp -r .mg_v2/<route>/asset/images/* public/assets/<route>/images/ 2>/dev/null

# 2. 起 dev 重新跑 verification-implementation.md 第 3B 节(实现完 SOP)
```

跳转关系如果变了,用自然语言描述补 `<Link>`(参考
[troubleshooting-magic.md](troubleshooting-magic.md) 的原型连线限制)。

---

## 8. 状态归档和完成判定

diff 报告不是完成。必须应用到代码或画布并复验。

每次 update 写入状态:

```bash
python3 <skill-dir>/scripts/verification-state.py record \
  --type update \
  --passed \
  --diff ".codify/diff/update-<timestamp>.json" \
  --note "已应用设计稿增量并复验"
```

建议在 `.codify/state.json` 或项目自己的状态文件里保留上一轮 DSL hash、D2C hash、
本次 diff 文件路径和已应用文件清单。用户在画布上并行修改时，先重新拉最新 DSL，
不要用旧 diff 覆盖用户的新改动。

## 9. 总结对话用的报告模板

每次 diff 完给用户列一个清单:

```
本次设计稿变更(vs 上次拉取):

  ~ 改动节点 N 个
    - 文本变化:   [节点 id] "旧文本" → "新文本"
    - 颜色变化:   [节点 id] paint_xxx #ABC → #DEF
    - 尺寸变化:   [节点 id] 100×40 → 120×40
  + 新增节点 M 个
    - [节点 id] (类型, 名称)
  - 删除节点 K 个
    - [节点 id] (类型, 名称)

interactive 字段变化: <无 / 有 X 条新增>
(注:MCP 不下发原型连线,只有组件级状态过渡)

D2C 重拉状态:
  ✅ 已刷新: <路由列表>
  ⏳ 缓存未变,需用户在 MasterGo 点"发送数据": <路由列表>

代码已应用变更:
  - 文件 1 / 文件 2 ...

待截图确认: http://localhost:3000/<路由>
(走 verification-implementation.md 3B 节做最终验收)
```

让用户走 [verification-implementation.md](verification-implementation.md) 3B 节验证截图。
没有应用和复验前，只能说 diff 已生成或待同步，不能说更新完成。
