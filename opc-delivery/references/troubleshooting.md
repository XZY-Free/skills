# 报错处理总入口

## 目录

- [最高优先级原则:遇错先查文档,不要瞎猜](#最高优先级原则遇错先查文档不要瞎猜)
- [需要用户行动时的输出契约](#需要用户行动时的输出契约)
- [错误类型查询路由](#错误类型查询路由)

## 最高优先级原则:遇错先查文档,不要瞎猜

任何 MCP 报错、行为异常、不熟字段、配置卡住 → **先 `bash + curl` 拉官方文档 / npm
registry / DuckDuckGo**,再决定怎么提示用户。**绝不允许凭印象答用户**——
这是 [📸 证据契约](../SKILL.md#-证据契约完成判定) 的对应面:回答有依据,
跟"完成有证据"是一对原则。

```bash
# 1. MasterGo 官方帮助页(HTML,约 100KB)
python3 <skill-dir>/scripts/fetch-doc-snippet.py https://mastergo.com/help/MG/MCP \
  --keyword "个人访问令牌" --keyword "生成令牌" --keyword "发送数据"

# 2. magic-mcp 源码 / README(npm 公开包)
curl -sL https://registry.npmjs.org/@mastergo/magic-mcp/latest | jq -r '.dist.tarball'
# 下载 tarball 解压看 README / src,便于摸清字段
TARBALL=$(curl -sL https://registry.npmjs.org/@mastergo/magic-mcp/latest | jq -r '.dist.tarball')
curl -sL "$TARBALL" -o /tmp/mg.tgz && tar -xzf /tmp/mg.tgz -C /tmp/mg-mcp-src

# 3. Codify MCP 包名 / 文档(包名按 npm 实际查)
curl -sL https://registry.npmjs.org/-/v1/search?text=codify | jq '.objects[].package | {name, description, links}'

# 4. DDG 搜社区案例 / 报错关键词
curl -sL 'https://duckduckgo.com/html/?q=mastergo+mcp+<错误关键词>'
```

---

## 需要用户行动时的输出契约

本节是 SKILL.md [🙋 用户行动契约](../SKILL.md#-用户行动契约) 在报错语境下的具体落地。
任何报错要让用户动手时,回复必须同时包含:**为什么 / 依据 / 具体步骤 / 完成后继续 / 兜底** 五项。

禁止只说:"把 token 发我" / "去 MasterGo 点发送数据" / "订阅一下组件库" /
"把接口文档给我" / "截图发我" —— 这些都必须改成带路径和下一步的可执行说明。

---

## 错误类型查询路由

| 报错来源 | 读取文件 |
|---|---|
| Magic 工具(`getDsl` / `getD2c` / `getMeta`) | [troubleshooting-magic.md](troubleshooting-magic.md) |
| Codify 工具(`design` / `agent_*` / `get_*`) | [troubleshooting-codify.md](troubleshooting-codify.md) |
| 渲染问题(蒙版 / 字体 / 胶囊 / SVG) | [rendering-patches.md](rendering-patches.md) |
| API 文档格式 / 字段映射 / 溯源汇报问题 | [api-wiring.md](api-wiring.md) |
