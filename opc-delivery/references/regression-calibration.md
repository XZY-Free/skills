# 已上线需求回放校准

目标: 不拿全新需求直接赌效果，而是用已经上线、资料完整、效果已知的需求做 golden
replay，调到 AI 产物接近或超过人工产物，再推广到新需求。

## 适用场景

- 团队要沉淀 OPC “宪法/规约”；
- 需要证明 skill 从需求到上线的效果；
- 现有规则不好判断是否够用；
- 组长要求拿已上线版本的需求重跑、对比 AI 和人工差距。

## 输入包

优先收集:

- 原始需求/PRD；
- 设计稿或截图；
- 接口文档和字段说明；
- 已上线代码或发布分支；
- 测试用例、验收记录、线上截图；
- 事故、返工、评审意见。

资料不全也能跑，但要在 gap report 里标注缺口。

## 回放步骤

1. 建立 golden baseline:
   - 记录人工版本的需求、设计、代码、部署和验收证据；
   - 不把人工实现细节提前泄漏给生成阶段，避免污染。
2. 用 OPC 正常流程重跑:
   - requirements -> solution -> UI -> implementation-plan -> implementation -> verification -> deployment/check；
   - 每阶段产物独立落盘。
3. 对比差距:
   - 需求覆盖: 少了哪些角色、流程、状态、异常；
   - UI 设计: 页面数量、信息架构、语种、可访问性、组件库；
   - 代码实现: 组件边界、API wiring、状态、错误处理、测试；
   - 部署验证: 构建、环境变量、访问、回滚。
4. 沉淀规则:
   - 能普遍复用的写入 SKILL.md 或 reference；
   - 具体项目规则写入项目自己的 AGENTS.md / docs / skill reference；
   - 可自动检查的变成 scripts 或 evals。
5. 做 AAR:
   - what expected: 原本预期 AI 在每阶段做到什么；
   - what happened: 实际 replay 输出和 golden baseline 有何差异；
   - why different: 缺需求、缺方案、缺 UI 规则、缺验证，还是工具/环境问题；
   - what changes: 规则、脚本、eval、项目约定分别怎么更新。

## Gap Report 模板

写到 `.opc/calibration/<feature-name>-gap-report.md`:

```markdown
# Calibration Gap Report

## Golden Feature
- 名称:
- 上线版本:
- 输入材料:

## Replay Output
- PRD:
- Solution:
- UI:
- Code:
- Deployment/verification:

## Gaps
| 类型 | Golden | Replay | 影响 | 修复规则 |
|---|---|---|---|---|

## Rule Updates
- SKILL.md:
- references:
- scripts:
- evals:

## AAR
- What expected:
- What happened:
- Why different:
- What changes:
- Owner / follow-up:

## Decision
- 可用于新需求 / 需要继续校准 / 暂不推广
```

## 完成门槛

- 有 golden baseline 和 replay output；
- 差距被分类，不只是主观“差不多”；
- AAR 已回答 expected / happened / why / changes；
- 每个高影响差距有规则更新或明确后续；
- `.opc/state/opc-task.json` 中 `calibration` 标记为 `done` 或 `blocked` 并写原因。
