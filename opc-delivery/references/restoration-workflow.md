# Magic MCP 还原工作流(双模式)

## 目录

- [0. Magic MCP 可用性门禁](#0-magic-mcp-可用性门禁)
- [1. 解析 URL,提取 fileId 和 layerId](#1-解析-url提取-fileid-和-layerid)
- [2. 获取站点目录(整站还原时)](#2-获取站点目录整站还原时)
- [3. 拉每页 D2C](#3-拉每页-d2c)
- [4. 状态记录 + 资源落盘 + 设计 token 抽取](#4-状态记录--资源落盘--设计-token-抽取)
- [5. ★ 模式选择](#5--模式选择)
- [6. 模式 A:企业级实现(默认)](#6-模式-a企业级实现默认)
- [7. 模式 B:快速复刻(opt-in)](#7-模式-b快速复刻opt-in)
- [8. 关于"原型连线"的限制](#8-关于原型连线的限制)

定位:**用户要把 MasterGo 设计稿一次性转成前端代码**。

**两种模式**:

| 模式 | 用途 | 默认? | 代码形态 |
|---|---|---|---|
| **企业级实现** | 真正交付到生产、要接 API、要写业务逻辑 | ✅ **默认** | 正常 React/Vue 组件,Tailwind/CSS,正常 fetch,**D2C 当视觉参考稿** |
| **快速复刻** | 给客户/PM 看效果、临时演示、内部 demo | opt-in | `dangerouslySetInnerHTML` 整段塞 D2C HTML,**数据写死**,像素 100% 一致 |

**模式不混用,一个项目选一种**。需要在两种模式间切换就重新建工程。
模式选择见本文第 5 节;企业级实现是默认,**用户不主动说"快速复刻"就走企业级**。

前置:
- MasterGo Magic MCP 已通过 [mcp-setup.md](mcp-setup.md) 的配置文件检查;
- 框架已经通过 [framework-detect.md](framework-detect.md) 选定。

遵守 [delivery-contract.md](delivery-contract.md):Magic 还原路径的交付物是可运行且验证过
的前端实现,不是 DSL、D2C HTML、资源目录或截图报告。
同时遵守 [copy-language.md](copy-language.md):还原代码应保留原设计稿页面文案语言,
不要在组件化、接 API 或快速复刻时自动翻译 UI 文案。
还原任务也应写入 `.codify/state.json` 或 `.codify/state/mastergo-task.json` 的
restoration 记录: source fileId/layerId/contentId、页面列表、模式、页面主语言和验证状态。

**不要只因为 `tool_search` 暴露出 Magic MCP 工具就直接调用 `getDsl`**。
还原前必须确认当前宿主配置文件里有 `@mastergo/magic-mcp` 和非占位 token。
如果配置缺失/占位,先走安装配置;否则调用工具只会得到误导性的权限错误。

---

## 0. Magic MCP 可用性门禁

开始还原前必须确认:

- 当前宿主配置里有 MasterGo Magic MCP,且 token 不是占位;
- 当前会话能看到 `mcp__mastergo-magic-mcp__*` 或等价 Magic 工具;
- URL 里有可解析的 `layer_id`;
- 若用户要整站,有根容器 Frame 或每页 Frame 的链接。

缺任一项时:

```
1. 回 mcp-setup.md / troubleshooting-magic.md 定位阻塞
2. 按用户行动契约告诉用户缺什么、怎么补、补完后继续什么
3. 不创建本地前端项目、不手写假页面、不说还原完成
```

只有用户明确改口说"没有 MCP,先根据截图/描述写一个独立前端原型"时,才离开
opc-delivery 的 MasterGo 还原范围,转普通前端任务;不要仍称为 MasterGo 还原完成。

---

## 1. 解析 URL,提取 fileId 和 layerId

合法 URL 形态:

```
https://mastergo.com/file/<fileId>?file=<fileId>&layer_id=<a>%3A<b>&pageid=<x>%3A<y>
https://mastergo.com/goto/<short>?file=<fileId>&layer_id=<a>%3A<b>
```

**只取 `layer_id=`**。`%3A` URL-decode 是 `:`,MCP 会自己处理。
忽略 `pageid` / `page_id`,那是 MasterGo 的画布页 Tab,不是图层 ID。

优先用脚本解析,避免把 `page_id` 当成 `layerId`:

```bash
python3 <skill-dir>/scripts/parse-mastergo-url.py 'https://mastergo.com/file/193097526299871?layer_id=2%3A77196'
```

脚本会输出 `fileId`、`layerId` 和 `contentId`。

短链 `/goto/xxx` 如果用户没在画布选中状态下复制,往往不带 `layer_id=`,会报
`Could not extract layerId from URL`。让用户**画布选中目标 Frame 后重新复制 URL**。

---

## 2. 获取站点目录(整站还原时)

```
mcp__getDsl(fileId, rootLayerId)  # 一次拿到所有子页面
```

让用户在 MasterGo 里**画一个根容器 Frame 包住所有页面 Frame**,右键复制
这个根容器的链接(必须带 `layer_id=`),再走这一步。

解析返回 JSON,遍历根容器的 `children`,每个 type=FRAME、宽度 ≥ 1280 的子节点
就是一个独立页面。映射成路由,让用户**确认路由命名**,再开干。

整站根容器 DSL 偶尔会超过 20MB → 报 `Request too large`。改成对每个子 Frame 单独
`getDsl`,详见 [troubleshooting-magic.md](troubleshooting-magic.md)
`Request too large` 小节。

---

## 3. 拉每页 D2C

```python
contentId = f"{fileId}-{layerId.replace(':','-')}"
mcp__getD2c(contentId, fileId, outDir=f".mg/{routeKey}")
```

每个页面单独一个 outDir。返回结构:
```
.mg/<routeKey>/
├── <contentId>.html      # 主 HTML
└── asset/
    ├── icons/*.svg
    └── images/*.png|jpg
```

**遇到 `❌ 未找到该 contentId 对应的数据`**:让用户在 MasterGo 里点对应 Frame 的
"发送数据"按钮,等他点完再继续。**不让用户复制 contentId**,你能自己拼。

---

## 4. 状态记录 + 资源落盘 + 设计 token 抽取

### 4.0 状态记录

每次拉取 DSL/D2C 后记录:

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
    "verification": {
      "status": "pending"
    }
  }
}
```

页面主语言从 D2C/DSL 的可见文本推断，后续 JSX、mock、空态、错误态不要擅自翻译。
D2C / DSL 原始输出不是完成，只是实现输入。

### 4.1 资源落盘(两种模式都做)

bundled 脚本一行同步,避免每次重写 for-loop:

```bash
bash <skill-dir>/scripts/sync-d2c-assets.sh .mg src/<project>/public/assets
# 输出:每个 route 一行 "synced: <route>",末尾汇总数量
```

如果用了 `outDir=.mg_v2/...` 跑 update 流(见 [update-flow.md](update-flow.md)),
对应改成 `bash <skill-dir>/scripts/sync-d2c-assets.sh .mg_v2 src/<project>/public/assets`。

### 4.2 设计 token 抽取(仅企业级模式)

扫所有 D2C HTML 抽出颜色 / 字体 / 间距,输出到 `.codify/design-tokens.json`,
后续写进 Tailwind config 用:

```bash
python3 <skill-dir>/scripts/extract-tokens.py \
  --glob "<projectDir>/.mg/**/*.html" \
  --out "<projectDir>/.codify/design-tokens.json"
```

跑完 print 一份摘要给用户:

```
抽取到的设计 token:
  颜色(出现最多 10 个):
    #0A0E1A: 134 处
    #4FB8FF: 87 处
    #FFFFFF: 76 处
    ...
  字体:
    DingTalk JinBuTi: 标题
    PingFang SC: 正文
  字号:
    14px / 16px / 20px / 32px / 48px(主梯度)

建议把这些写进 tailwind.config.ts 的 theme.extend.colors / fontFamily / fontSize。
要我帮你生成 Tailwind 配置吗?
```

---

## 5. ★ 模式选择

**默认走企业级实现**(直接进第 6 节)。**只有以下情况切快速复刻**:

- 用户明确说"快速复刻 / 高保真原型 / 给客户看一眼 / 像素 100% 一致"
- 用户明确说"不用接 API / 数据先写死"
- 用户明确说"我不想要 React 组件,我要 dangerouslySetInnerHTML"

走快速复刻前,**显式跟用户确认一次**:

> 你确认要走快速复刻模式吗?这种模式产物**不适合接 API、不适合生产**,
> 只适合临时演示。后续要接 API 必须重做一遍企业级模式。
> 还是要走?(yes / no)

确认是就跳到第 7 节;否则回第 6 节。

---

## 6. 模式 A:企业级实现(默认)

默认走企业级实现。详细流程见 [restoration-enterprise.md](restoration-enterprise.md):设计 token、Tailwind、组件拆分、JSX、API 接入和企业级验证。

## 7. 模式 B:快速复刻(opt-in)

只有用户明确选择快速复刻时才走。详细流程见 [restoration-fast-prototype.md](restoration-fast-prototype.md):Next.js 快速脚手架、D2C HTML 装载、多页导航和像素级验证。

## 8. 关于"原型连线"的限制

**MasterGo Magic MCP 不下发画布上画的 Frame ↔ Frame 原型连线**——
这是 MCP 协议的能力边界,不是 bug、不是缓存、不是同步问题。

完整诊断方法、修法、判定脚本统一收敛到
[troubleshooting-magic.md A.6 "DSL 看不到画布上画的原型连线"](troubleshooting-magic.md#a6-dsl-看不到画布上画的原型连线)。
跨 Frame 跳转用自然语言确认后,代码里手写 `<Link>` / `router.push`。
