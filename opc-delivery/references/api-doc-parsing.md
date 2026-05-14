# API 文档解析

## 2. 默认目录与多文件支持

约定的标准目录:

```
<projectDir>/.codify/api-docs/
  ├── auth.openapi.yaml          # 用户认证接口(OpenAPI)
  ├── agents.openapi.yaml        # Agent 业务接口(OpenAPI)
  ├── billing.postman.json       # 计费接口(Postman Collection)
  ├── activities.md              # 活动接口(自由文本)
  └── README.md                  # 可选:用户自己写的接口说明索引
```

- 目录不存在就**自动创建**(`mkdir -p .codify/api-docs/`)
- 多文件支持,**所有文件都会被扫**
- 用户随手往里扔即可,**不要求统一格式**

---

## 3. 支持的文档格式 + 识别方式

按优先级:

| 格式 | 文件名特征 / 识别方式 | 解析方法 |
|---|---|---|
| **OpenAPI / Swagger** | `.yaml` / `.yml` / `.json`,顶层有 `openapi: 3.x` 或 `swagger: 2.0` | `js-yaml` / `jq` → 拿 `paths` + `components.schemas` |
| **Postman Collection** | `.json`,顶层有 `info.schema` 包含 `postman.com` 域名 | `jq '.item[] | {name, request}'` |
| **自由文本 markdown** | `.md`,直接读全文 | 让 AI 解析:把 `## GET /xxx` 当 endpoint,代码块当 sample |
| **URL + sample**(用户在对话里直接贴) | 用户说"接口 `GET https://api.x.com/users/me` 返回 `{...}`" | 当场拼一个最小 OpenAPI 写到 `.codify/api-docs/_inline.openapi.yaml` |

### 解析脚本

优先运行 bundled script,把接口摘要写成机器可读文件:

```bash
python3 <skill-dir>/scripts/parse-api-docs.py \
  --dir <projectDir>/.codify/api-docs \
  --out <projectDir>/.codify/api-endpoints.json
```

脚本支持 OpenAPI JSON、Postman JSON、Markdown/自由文本中的 `GET /path` 写法。
YAML 文档如果没有可用解析库,脚本会按文本 endpoint 规则提取,然后由你读取原文补充字段。

---
