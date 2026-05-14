# UI 文案语种契约

## 目录

- [判断顺序](#判断顺序)
- [中文场景默认行为](#中文场景默认行为)
- [选择题澄清](#选择题澄清)
- [写入 Codify requirement](#写入-codify-requirement)
- [推送前 copy lint](#推送前-copy-lint)
- [修改和还原场景](#修改和还原场景)
- [验证](#验证)

本文件约束 MasterGo 设计稿、Codify HTML 和 Magic 还原代码里的页面 UI 文案语种。
它不约束助手回复语言;助手回复仍按宿主和用户语言习惯处理。

---

## 判断顺序

页面文案语种按下面顺序决定:

1. 用户明确指定的语言;
2. 用户提供的截图、已有设计稿、素材或品牌规范里的主要语言;
3. 当前对话的主要语言;
4. 目标用户 / 业务区域能明确推断的语言。

如果上述信号冲突或低置信,用选择题澄清。不要因为企业级、SaaS、Dashboard、
AgentOps 等词就默认英文 UI。

---

## 中文场景默认行为

用户全程中文沟通、截图为中文、或需求明显面向中文团队时:

- 默认使用简体中文 UI 文案;
- 导航、标题、按钮、表头、筛选项、状态标签、空态、错误态、审批、审计、监控、
  日志和提示都应是中文;
- 品牌名、产品名、缩写、协议名和常用技术名词可以保留原文:
  MasterGo、Codify、AI、Agent、API、MCP、D2C、SLA、SSO、RBAC、AgentOps;
- 中英混排要自然,不要把整页变成英文后台模板。

---

## 选择题澄清

语种不确定时,遵守选择题澄清契约:

```
我先确认页面 UI 文案语种:
A. 跟随当前聊天语言(推荐):页面文案用简体中文,保留必要英文技术名词
B. 中文 UI + 更多英文技术标签:适合面向研发 / AgentOps 团队
C. English UI:导航、按钮、状态和说明全部用英文
D. 自定义 / type something:你直接写希望的语种或混排规则
```

如果用户说"你决定 / 直接做",且当前聊天是中文,默认选 A 并继续。

---

## 写入 Codify requirement

调用 `design()`、`agent_create_page()` 或生成 Tailwind HTML 前,把语种写入 requirement。
不要只在口头回复里说。

推荐短句:

```
UI copy language: Simplified Chinese.
Keep product names, brand names, and technical acronyms as-is:
MasterGo, Codify, AI, Agent, API, MCP, D2C, SLA, SSO, RBAC, AgentOps.
All navigation labels, titles, buttons, table headers, states, empty states,
errors, approval/audit/monitoring copy, and log snippets should follow this language.
```

如果用户选择英文或自定义语种,把对应规则替换进去。

## 推送前 copy lint

推送 Codify HTML 前优先运行 bundled 语言检查。它只解析可见文本和少量可见属性,
不扫描 class 名，也不会把 MasterGo、Codify、AI、Agent、API、MCP、D2C、SLA、
SSO、RBAC、AgentOps 等技术词判为违规。

```bash
python3 <skill-dir>/scripts/codify-copy-lint.py <html-file> \
  --expected simplified-chinese \
  --mode strict
```

模式:

- `--mode strict`: Codify 写入前默认使用；大面积未授权英文 UI 直接阻断。
- `--mode warning`: 还原已有英文稿、用户要求混排、或需要保留原设计语言时使用；
  warning 必须写进验证记录。

英文 UI 显式需求:

```bash
python3 <skill-dir>/scripts/codify-copy-lint.py <html-file> \
  --expected english \
  --mode strict
```

误伤处理: 如果用户明确要求保留其它术语，用 `--allow Term` 追加白名单。不要为了让
lint 通过而把整页 UI 改成英文。

---

## 修改和还原场景

- 局部修改 UI 文案时,沿用目标画布 / 页面当前主要语言,除非用户明确要求翻译;
- Magic 还原代码时,保留原设计稿文案语言,不要在还原或组件化时自动翻译;
- 接 API 或替换假数据时,字段名、枚举值可以按接口原文处理,但界面静态文案仍按本契约;
- 设计稿更新流中,若新旧版本语种不一致,把它当作 diff 风险点,先向用户确认是否有意改变。

---

## 验证

推送前和 3A 验证至少抽查:

- 左侧 / 顶部导航;
- 页面主标题和区块标题;
- 主要按钮和二级按钮;
- 表格列名、筛选项、状态标签;
- 空态、错误态、审批提示、审计时间线、监控告警、运行日志。

未获授权的英文 UI 文案大面积出现时,不要说设计完成;回 `agent_update_node` /
`agent_replace_node` 或重新生成符合语种契约的 Codify HTML。

推送后将 copy lint 或人工抽查结果写入:

```bash
python3 <skill-dir>/scripts/verification-state.py record \
  --type design \
  --unit-id <unit-id> \
  --copy-language simplified-chinese \
  --note "UI 文案语种抽查通过"
```
