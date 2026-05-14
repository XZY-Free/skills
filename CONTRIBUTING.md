# 贡献指南

感谢愿意为这个 skills 集合贡献 —— 不管是修个错别字、提一个 issue、还是带来一个全新的 skill,都欢迎。

[English](CONTRIBUTING.en.md) · **简体中文**

---

## 项目欢迎什么贡献

按优先级排:

| 优先级 | 类型 | 怎么提 |
|---|---|---|
| ⭐⭐⭐ | **新 skill** | 先在 [feature 模板](.github/ISSUE_TEMPLATE/feature_request.yml) 里发个 issue 描述用例,等讨论达成共识再开 PR |
| ⭐⭐⭐ | **现有 skill 的 eval / forward test 补充** | 参考 [`opc-delivery/evals/forward-tests.md`](opc-delivery/evals/forward-tests.md),直接开 PR |
| ⭐⭐ | **bug 修复 + 文档错别字** | 小改可以直接开 PR;影响行为的改动建议先开 issue |
| ⭐⭐ | **现有 skill 的 references 补充**(troubleshooting / 新场景)| 直接开 PR,在 PR 描述里说清场景来源 |
| ⭐ | **SVG / 图片美化** | 直接开 PR,但请保持现有配色风格的一致性 |

## 开发流程

### 1. fork + clone

```bash
gh repo fork <repo-url> --clone
cd skills
```

### 2. 起 branch

```bash
git checkout -b feat/<short-name>      # 新功能
git checkout -b fix/<short-name>       # bug 修复
git checkout -b docs/<short-name>      # 仅文档
git checkout -b skill/<skill-name>     # 新 skill
```

### 3. 本地验证(尽量跑通后再发 PR)

```bash
# SVG 是否合法
python3 -c "import xml.etree.ElementTree as ET; \
  [ET.parse(f) for f in __import__('glob').glob('**/*.svg', recursive=True)]; \
  print('All SVGs OK')"

# Skill frontmatter 是否合法
for f in */SKILL.md; do
  head -5 "$f" | grep -q '^name:' || echo "缺 name 字段: $f"
done

# 文档内部链接是否都活着
python3 scripts/check-links.py     # (脚本会随 D 项 CI 一起落地)
```

### 4. commit + push

参考下方"commit 规范"。

### 5. 开 PR

走 [PR 模板](.github/PULL_REQUEST_TEMPLATE.md),把测试方式说清。

---

## Skill 的结构约定

每个 skill 是仓库根的一个子目录:

```
<skill-name>/
├── SKILL.md            # ⚠️ 必需,入口,完整工作流定义
├── agents/
│   └── openai.yaml     # 推荐,UI metadata
├── references/         # 推荐,按需触发的详细指引
│   └── *.md
├── scripts/            # 可选,确定性检查 / 转换脚本
├── evals/
│   └── evals.json      # 必需,评测用例
└── assets/             # 可选,运行时真正需要的模板 / 资源
```

### SKILL.md frontmatter 规范

```yaml
---
name: <skill-name>         # 必需,kebab-case,跟目录名一致
description: |              # 必需,触发说明 + 关键词清单
  这个 skill 处理什么场景。
  触发关键词:关键词 1、关键词 2、...
---
```

`description` 是 agent 决定是否触发本 skill 的依据,**触发关键词列得越具体,误触发率越低**。

### references 文件命名

- 用动词或场景命名(`troubleshooting.md`、`api-wiring.md`)而不是抽象命名(`utils.md`、`misc.md`)
- 每个 references 文件在 SKILL.md 末尾"何时读"表里登记一条

---

## Commit 规范

参考 [Conventional Commits](https://www.conventionalcommits.org/),但不强制 scope:

```
<type>: <短描述>

<可选 body,说明 why>
```

`type` 取值:

- `feat`: 新功能 / 新 skill / 新 reference 章节
- `fix`: bug 修复
- `docs`: 仅文档
- `refactor`: 重构,不改行为
- `test`: 加 / 改测试 / evals
- `chore`: 杂项(CI / 依赖 / 仓库元信息)
- `example`: 加 / 改 examples

例子:

```
feat: add update-flow.md for incremental design sync

  解决用户报告"设计稿改了不知道怎么增量重拉"的问题。
  新增 update-flow.md,放进 SKILL.md 阶段 4。
```

```
fix: correct broken anchor link in README.md acknowledgments badge
```

```
example: add e-commerce-detail walkthrough
```

---

## PR 流程

1. **小改动**(单文件、文档错字)→ 直接 PR
2. **中等改动**(单 skill 内的多文件、新 reference)→ PR 标题写清楚,描述里附本地验证截图
3. **大改动**(新 skill、跨 skill 重构)→ 先开 issue 讨论,达成共识再 PR

### Review 标准

- 是否破坏现有 skill 的对外行为(看 evals.json 没有被悄悄改)
- SKILL.md frontmatter 是否合法
- references 的 cross-link 是否完整(新加文档要在 SKILL.md 登记)
- 没有提交 `.env` / token / 真实 fileId / 内部 URL
- README 内部链接都活着

### 等多久

- 小 PR:24 小时内首次回复
- 中 / 大 PR:72 小时内首次回复
- 节假日期间会延后

---

## 行为准则

简单一条:**保持专业、对事不对人**。

- 讨论问题时给依据(代码片段、日志、官方文档链接)
- 不在 issue / PR 里贬低他人技术水平 / 经验
- skill 是工程产物不是个人秀场,**evidence over opinion**

我们参考 [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) 的精神,违规行为请发邮件给维护者。

---

## 不接受的贡献

- ❌ 把这个 skill 直接 fork 后改名重新打包发布(违反 license 的"署名"条款)
- ❌ 用真实生产数据 / 客户名 / 内部 URL 写 examples
- ❌ 在 skill 里硬编码任何账号 / token / 内网地址
- ❌ 引入对云端付费服务的依赖(本仓库的核心承诺是"本地零锁定")
- ❌ 把 SKILL.md 改成"温柔模式" —— 现有的硬规则("遇错查文档"、"完成判定看证据")是品牌,**别为了讨好新手稀释掉**

---

## 关于 Skill 内容本身的写作风格

skill 是给 AI agent 读的,不是给人读的。所以:

- **直接给指令,不要叙述**:用"先 curl 查官方文档"而不是"建议先查一下官方文档"
- **给条件,不要给软建议**:"如果用户给的 URL 没有 layer_id,则 X" 而不是"通常用户会给完整 URL"
- **示例代码片段越具体越好**:`curl -sL https://...` 而不是"用 curl 调一下"
- **保留中文 + 技术原词混排**:`layerId / D2C / DSL` 这类 API 术语不翻译

参考 [`opc-delivery/SKILL.md`](opc-delivery/SKILL.md) 的写作风格作为基准。

---

## 提问 / 求助

- bug → [bug 模板](.github/ISSUE_TEMPLATE/bug_report.yml)
- MCP 报错 → [MCP 错误模板](.github/ISSUE_TEMPLATE/mcp_error.yml)
- 用法讨论 / 路线图建议 → GitHub Discussions
- 安全问题 → 见 [SECURITY.md](SECURITY.md)

期待你的 PR :)
