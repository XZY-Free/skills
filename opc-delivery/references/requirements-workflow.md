# 需求阶段工作流

目标: 把口语化、模糊、甚至不懂业务边界的输入, 变成能驱动设计、实现和验收的 PRD。

需求阶段不是“必须先给用户一轮确认卡”。正确节奏是: 先抽事实, 内部记录默认假设和缺口; 只有高影响不确定才打开原生选择交互。信息足够时直接写 `.opc/requirements/prd.md`, 然后自动进 solution 阶段。

## 目录

- [输入检查](#输入检查)
- [高影响疑点判断](#高影响疑点判断)
- [用户 framing 翻译](#用户-framing-翻译)
- [JTBD + MoSCoW 门禁](#jtbd--moscow-门禁)
- [PRD 最小结构](#prd-最小结构)
- [收敛与完成判断](#收敛与完成判断)

## 输入检查

优先从用户原话、会议纪要、已上线需求、接口文档、截图、现有代码和业务规则中抽取信息。先抽再问。

输入里包含承诺性词(“企业级 / 完整 / 专业 / 生产级 / 智能 / 后台 / 小需求”) 时, 必须翻译成具体清单。若翻译结果会改变范围或成本, 用原生选择交互让用户确认; 若只是记录默认理解, 写进 PRD 和 discussion log 后继续。

## 高影响疑点判断

必须确认:

- 数据来源: 真实接入、演示数据、用户上传或第三方 API;
- 权限深度: 账号、角色、RBAC、SSO、审计、多租户;
- 范围裁剪: “企业级 / 完整 / 生产级”包含或不包含哪些模块;
- 合规/品牌: 客户数据、法务、品牌强约束;
- 验收边界: 是否必须上线、是否允许仅预览、是否涉及真实用户;
- 用户给出多个互斥目标且无法同时满足。

不用确认:

- 文档标题、文件名、目录结构;
- 小依赖、helper、内部路由;
- 可逆默认, 如分页大小、默认排序;
- 已由用户原话或现有资料明确给出的范围。

需要确认时, 按 [clarification-loop.md](clarification-loop.md) 打开宿主原生选择交互; 不可用时才文本降级。

## 用户 framing 翻译

把用户的抽象词翻成可验收范围:

| 用户原话 | 需要翻译成的清单 |
|---|---|
| 企业级 | 是否含登录、RBAC、SSO、审计日志、多租户、数据导出、SLA、合规 |
| 完整 / 完整上线 | 是否端到端可用、是否真实数据、是否可部署、是否含回滚 |
| 专业级 / 高级 | 是视觉质感、功能完整度、工程质量还是运营后台能力 |
| 生产级 / production-ready | 是 preview/staging 还是 production; 是否有真实用户访问 |
| 智能 / AI | 真接 LLM/Embedding API 还是演示响应; 哪家模型; 成本限制 |
| 数据看板 / 后台 | 真实数据源、角色、实时性、权限、导入导出、审计 |
| 小需求 | 单页单接口, 还是用户口中的“小”但涉及多模块 |

示例:

```text
“企业级用户中心”
默认理解:
- 含: 登录、账号列表、角色、基础 RBAC、审计日志、数据导出
- 暂不含: SSO、多租户、计费、复杂审批
- 需要拍板: 权限深度是“基础 RBAC”还是“SSO + 多租户”
```

如果当前宿主支持 `request_user_input`, 权限深度这种高影响项用选择框确认; 不要求用户手敲 A/B/C。

## JTBD + MoSCoW 门禁

PRD 必须包含:

- Core Job: `当 <场景>, <角色> 想要 <能力>, 以便 <业务结果>`;
- Functional / Emotional / Social job;
- Compensating behavior: 用户现在用什么土办法;
- MoSCoW: Must / Should / Could / Won't。

MoSCoW 可以由 AI 先草拟, 但高影响裁剪必须暴露:

- 若裁剪会明显改变交付物, 用选择交互确认;
- 若只是低风险默认, 在 PRD 的 Won't 和 discussion log 写明“我已默认处理”。

## PRD 最小结构

写 `.opc/requirements/prd.md`(除非项目已有规范路径)。PRD 是收敛后的最终稿, 讨论纪要单独留在 `.opc/requirements/discussion.md`。

```markdown
# <需求名称> PRD

> 状态: requirements 阶段产出
> 讨论日志: .opc/requirements/discussion.md
> 交互说明: 高影响不确定已通过原生选择交互 / 文本降级 / 现有资料解决

## 背景和目标
- 背景:
- 目标:
- 非目标:
- 成功指标:

## 用户和场景
- 角色:
- 使用场景:
- 触发条件:

## JTBD
- Core Job:
- Functional jobs:
- Emotional / social jobs:
- Compensating behavior:

## 范围
- Must:
- Should:
- Could:
- Won't:
- 依赖:

## 用户故事
- 作为 <角色>, 我想 <能力>, 以便 <价值>。

## 核心流程
1. 入口:
2. 操作:
3. 成功结果:
4. 异常/空态/权限态:

## 数据和接口
- 数据来源: (真实接入 / 演示数据 / 用户上传 / 第三方 API)
- 关键字段:
- 接口/后端依赖: (Node 后端默认; 接什么外部服务)

## UI/交互要求
- 页面/模块:
- 状态:
- 文案语种:
- 可访问性:

## 非功能要求
- 性能:
- 安全/权限:
- 兼容性:
- 日志/审计:

## 验收标准
- Given/When/Then:
- 必须通过的测试/截图/部署检查:

## Open Questions
- [ ] <问题> | 影响: <影响> | 当前处理: 自治默认 / 需要拍板 / 卡住缺 X

## 决策记录
- <日期>: <决策> | 原因: <依据, 可引用 discussion.md>
```

## 收敛与完成判断

可以完成 requirements 的信号:

- 用户 framing 已翻译成具体范围;
- 真实数据/演示数据、主要角色、核心流程和成功结果明确;
- Must / Should / Won't 能写入 PRD;
- 高影响不确定已确认或有明确阻塞记录;
- PRD 能驱动方案阶段, 不需要再猜。

完成动作:

1. 写 `.opc/requirements/prd.md`;
2. 更新 `.opc/requirements/discussion.md`, 记录已处理的高影响疑点和自治默认;
3. 写 `.opc/requirements/last-handoff.md`;
4. 跑 `scripts/handoff-lint.py --phase requirements`;
5. `opc-task-state.py mark requirements done --artifact .opc/requirements/prd.md --evidence "PRD 覆盖目标、范围、数据和验收标准" --next-action "进入 solution 阶段"`;
6. 自动进入 solution 阶段。

如果用户明确要“只要轻量 PRD / 我自己写 PRD / 跳过这步”, 记录用户授权、风险和替代证据, 再继续; 不把跳过伪装成完整需求收敛。
