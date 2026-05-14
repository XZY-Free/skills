# 需求覆盖与澄清契约

## 目录

- [核心原则](#核心原则)
- [需求覆盖门禁](#需求覆盖门禁)
- [Gate Card 与任务台账](#gate-card-与任务台账)
- [优先选择题](#优先选择题)
- [中断后恢复](#中断后恢复)
- [完成判定](#完成判定)

本文件约束 MasterGo 设计任务的交付范围。目标不是判断"单页还是多页",
而是确保最终画布成果完整覆盖用户需求,并且在不确定时用低摩擦选择题澄清。

---

## 核心原则

- 不根据"企业级 / 平台 / 工作台 / 后台 / 协作"等关键词机械决定页面数量;
- 页面、状态、弹窗、抽屉、组件变体的数量由用户目标、角色、核心流程和验收标准决定;
- 不能把用户的完整需求擅自缩成一个首页、首屏、概念页或静态展示页;
- 如果本轮只做代表性页面,必须是用户明确选择,并标注它不是完整需求覆盖;
- 交付汇报先说覆盖了哪些需求单元,再说生成了哪些页面或文件。

---

## 需求覆盖门禁

从零设计或大范围改版前,先形成一份简短覆盖 brief:

```
目标: <用户要解决的问题 / 产品场景>
角色: <主要使用者或利益相关者>
核心流程: <用户完成目标必须经过的路径>
设计单元: <页面 / 状态 / 弹窗 / 抽屉 / 组件变体>
UI 文案语种: <用户指定 / 素材语言 / 当前聊天主语言 / 已选择的混排规则>
验收口径: <怎样算满足本轮需求>
```

高置信时可以直接执行,但必须在动手前把覆盖 brief 讲清楚。低置信或可能遗漏时,
先问用户选择,不要自由发挥。

不要把"完整覆盖"等同于"一定多页":
- 简单需求可能一个页面 + 几个状态就够;
- 复杂需求可能需要多页面、详情、配置、审批、异常态和运行日志;
- 关键是覆盖用户目标,不是凑页面数。
- 页面文案语种也是覆盖 brief 的一部分;中文聊天或中文素材默认简体中文 UI,
  细则见 [copy-language.md](copy-language.md)。
- 复杂平台可参考 [design-coverage-patterns.md](design-coverage-patterns.md) 生成候选设计单元,
  但模板是推荐,不是固定页数。

## Gate Card 与任务台账

覆盖 brief 必须进入 `design-workflow.md` 的 MasterGo 设计 Gate Card。Gate Card
同时是 `.codify/state/mastergo-task.json` 的初始化来源。

最低字段:

```json
{
  "originalUserGoal": "<原始用户目标>",
  "gateCard": {
    "delivery": "MasterGo 画布设计稿",
    "scope": "完整稿 / 评审方向稿 / 概念代表页 / 自定义",
    "copyLanguage": "simplified-chinese",
    "designDirection": "企业运营型 / AgentOps 观测型 / 高管演示型 / 自定义",
    "componentLibraryStrategy": "local-snapshot|remote-selected|declined|unavailable|pending",
    "writeMethod": "design|agent_create_page|agent_update_node|agent_sync_design"
  },
  "units": [
    {"id": "overview", "title": "总览工作台", "type": "page", "status": "planned"}
  ]
}
```

用脚本初始化和恢复,避免重启后丢失原目标:

```bash
python3 <skill-dir>/scripts/mastergo-task-state.py init ...
python3 <skill-dir>/scripts/mastergo-task-state.py resume
python3 <skill-dir>/scripts/mastergo-task-state.py validate --for-completion
```

台账是恢复来源和门禁来源,不是完成证据。完成仍要看 MasterGo 写入和 3A 验证。

---

## 优先选择题

除 token、URL、截图、文件路径、layerId、API key 这类必须填空的信息外,
澄清问题默认用选择题。

规则:
- 优先使用宿主的结构化输入;如果不可用,用 A/B/C/D 文本选项;
- 给 2-3 个可执行选项,第一个放推荐项;
- 最后保留"自定义 / type something"入口,让用户写不在选项里的范围;
- 每个选项说明交付范围差异,不要只写"是 / 否";
- 选择题一次只问关键决策,避免把用户拖进长问卷。

示例:

```
我先确认本轮设计覆盖范围:
A. 推荐完整稿:覆盖核心流程、主要界面、关键状态和治理细节
B. 评审方向稿:覆盖核心路径和少量关键状态,适合先定视觉和信息架构
C. 概念代表页:只做一个代表性页面/首屏,不作为完整产品设计交付
D. 自定义 / type something:你直接写希望包含的范围
```

如果用户说"你决定 / 直接做",就按对需求最稳妥的覆盖 brief 执行,不要降级成最小页面。

---

## 中断后恢复

MCP 配置、token 写入、宿主重启、reconnect 或工具重新加载后,继续原任务前必须先恢复上下文:

1. 复述原始用户目标和真实交付物;
2. 运行 `scripts/mastergo-task-state.py resume` 或从最近对话重建 Gate Card 和覆盖 brief;
3. 复述剩余设计单元和最近 Codify request 状态;
4. 重新跑 Codify / Magic 对应门禁;
5. 再继续推送、还原或验证。

不得因为刚配置完工具,就把原始设计需求缩成一个更小的本地页面或临时示例。

---

## 完成判定

设计任务完成必须同时满足:
- 覆盖 brief 中的设计单元都已处理;
- `.codify/state/mastergo-task.json` 里没有未闭合的 `planned/generated/pushed` 单元;
- 最近 Codify request 不是 `accepted` pending;
- 用户后来新增或确认的范围没有遗漏;
- MasterGo 画布已写入并通过 3A 验证;
- 未完成项被明确标为"待做 / 待验证 / 待用户动作",而不是被隐藏。

正向反馈("不错 / 可以 / 继续")只说明当前结果无 blocker。若覆盖 brief 尚未闭合,
继续做下一项;只有用户明确暂停或覆盖已闭合并验证通过,才结束。
