<!-- 感谢 PR！请填写以下信息，让 review 更顺畅 -->

## 变更说明

<!-- 一两句话说清楚改了什么、为什么 -->

## 关联 issue

<!-- Closes #123 / Refs #456，没有可留空 -->

## 变更类型

- [ ] 修 bug（不改变现有行为预期）
- [ ] 新增功能 / 工作流分支
- [ ] 文档（SKILL.md / references / README）
- [ ] 重构（不改变行为）
- [ ] 测试 / evals
- [ ] 其它（请说明）

## 测试方式

<!-- 必填。仅靠 review 看不出 skill 是否真的工作。请描述你怎么验证的 -->

- [ ] 跑了 `mastergo/evals/evals.json` 里相关的 case，把 Claude 的回答粘在下面
- [ ] 手工触发了相关场景（描述步骤）
- [ ] 改的是文档/注释，无需运行验证

<details>
<summary>验证输出 / 截图</summary>

<!-- 粘 Claude 的对话片段、截图或日志 -->

</details>

## 自检清单

- [ ] 我没有把 token / 内网信息 / 真实 fileId 带进代码
- [ ] 改 SKILL.md 的话，frontmatter 仍然合法（name / description 字段在）
- [ ] 改 references/*.md 的话，cross-link（其它文档对它的引用）仍然成立
- [ ] 如果新增 reference 文件，已经在 SKILL.md 末尾"引用文件何时读"表里登记
