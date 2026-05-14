# API 接入(企业级实现专用)

## 目录

- [1. 触发条件](#1-触发条件)
- [2. API 接入子流程](#2-api-接入子流程)
- [3. 跟其它文件的衔接](#3-跟其它文件的衔接)

定位:**Magic 还原走"企业级实现"模式时,把页面上写死的占位数据换成真实接口数据**。
**快速复刻模式不走本流程**(快速复刻就是给人看的,数据写死合理)。

---

## 1. 触发条件

进入企业级模式 + 写完 JSX 后,**自动触发**:

```
1. 检查 <projectDir>/.codify/api-docs/ 目录
   ├── 存在且非空 → 列出文件 → 自动识别格式 → 进入 api-doc-parsing.md
   └── 不存在 / 空 → 走 api-trace-report.md 的"没文档时的引导"
2. 用户引导后给到文档 → 同上进入字段检测
3. 用户明确说"暂时没文档" → 跳过本流程,但要明确告诉用户:
     "数据现在是写死的,后续接口文档到位后,把它放进 .codify/api-docs/
      告诉我'重新接 API',我自动接上。"
```

**不接 API ≠ 完成**。哪怕用户跳过本步,企业级实现也要明确告知 "未接 API" 状态,
让用户知道这一步欠着。

---

## 2. API 接入子流程

按顺序读取并执行:

1. [api-doc-parsing.md](api-doc-parsing.md):创建/扫描 `.codify/api-docs/`,运行 `scripts/parse-api-docs.py` 生成 `.codify/api-endpoints.json`;
2. [api-field-mapping.md](api-field-mapping.md):检测 D2C/JSX 动态字段,让用户确认映射,生成数据层并替换写死数据;
3. [api-trace-report.md](api-trace-report.md):强制输出每个字段到接口/文档的溯源汇报,缺失则不算完成。

## 3. 跟其它文件的衔接

- 接 API 前的 JSX(数据写死):由 [restoration-enterprise.md](restoration-enterprise.md)
  完成
- 接 API 后的验证:由 [verification-implementation.md](verification-implementation.md)
  **3B-2** 完成,
  其中**展示溯源汇报**是必检项
- 文档格式 / 解析报错:先查 [api-doc-parsing.md](api-doc-parsing.md),再回
  [troubleshooting.md](troubleshooting.md) 的错误路由表
