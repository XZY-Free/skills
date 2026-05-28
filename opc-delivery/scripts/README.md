# opc-delivery scripts 索引

按用途分三层。SKILL.md 只显式列 `mandatory/`,本文是 helper / dev 入口,避免别人重复造轮子。

## mandatory/ — 流程门禁,必须跑

| 脚本 | 何时用 | 失败=阻断什么 |
|---|---|---|
| `handoff-lint.py` | `opc-task-state.py mark <phase> done` 前自动调用 | mark done(进入下一阶段) |
| `opc-task-state.py` | 任务初始化 / resume / checkpoint / mark done | 状态台账写入 |
| `codify-preflight.py` | MasterGo Codify 写入前 | 写入工具调用 |
| `check-mcp-config.py` | MCP 配置变更或排障 | 不阻断,给诊断输出 |
| `parse-mastergo-url.py` | 解析 MasterGo URL → fileId / layerId | 还原任务路由 |

## helpers/ — 按需调用

| 脚本 | 何时用 |
|---|---|
| `codify-artifact-audit.py` | Codify 写入后审计本地产物结构 |
| `codify-copy-lint.py` | Codify 文案合规检查 |
| `codify-html-lint.py` | Codify 原生 CSS HTML → Tailwind utility HTML 校验 |
| `component-ratio.sh` | 组件库引用比例统计(MasterGo 设计质量信号) |
| `dsl-diff.py` | Magic DSL 前后 diff(还原差异定位) |
| `extract-tokens.py` | 从 Codify token JSON 抽取设计 token |
| `fetch-doc-snippet.py` | 抓外部文档片段(API 文档 / 设计规范) |
| `ia-map-aggregator.py` | 聚合各 slice 的 Product Surface → 总 IA Map |
| `library-snapshot.py` | 组件库快照(Codify Gate Card 用) |
| `mastergo-task-state.py` | MasterGo 子任务台账(独立于主 opc-task) |
| `parse-api-docs.py` | 把 `.codify/api-docs/` 解析成 `api-endpoints.json` |
| `screenshot.mjs` | 浏览器截图(Playwright,验证证据) |
| `sync-d2c-assets.sh` | 同步 Magic D2C 落盘资源 |
| `verification-state.py` | 验证阶段状态记录(3A / 3B / 3C) |

## dev/ — 维护本 skill 自身

| 脚本 | 何时用 |
|---|---|
| `check-file-sizes.py` | 提交前自检: 单文件不超 500 行 md / 1000 行 json |
| `check-anchor-links.py` | 提交前自检: 跨文件 markdown anchor 链接全部有效 |
| `check-skill-rules.py` | CI / 提交前: frontmatter + evals 结构 + scripts 索引完整性 |
| `check-release-env.py` | 发布 OMC 时检查环境 |

## 调用约定

- mandatory: 流程内自动调用,**不要**手动跳过(handoff-lint 自动卡 mark done)
- helpers: 在 reference 里明确引导时才调用,不要主动"以防万一跑一下"
- dev: 改完 skill 自身后跑一次,确认没破坏 anchor / 文件大小 / 结构契约
