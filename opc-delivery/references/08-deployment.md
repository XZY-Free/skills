# 08 — 部署、校准

把已验证实现发布到目标环境, 给出可访问链接、状态证据和回滚方式。已上线后用 golden replay 校准 skill。

部署阶段是**执行阶段**。**默认终点是本地 production server**(`npm run build && npm run start` + 浏览器/curl 端到端过); 用户没说"上线/部署到服务器"时不主动问。收尾时附一句"要不要部署到你的服务器", 用户回"暂时不要"就收手, 回"要"并贴 SSH 凭证就走 [08b-ssh-deploy.md](08b-ssh-deploy.md)。

OPC 现阶段**不支持** Vercel / Netlify / Cloudflare Pages / GitHub Actions 平台路径——用户实际不用, 加进来只会让模型问出用户听不懂的选项。需要时由用户**显式**说"我要部署到 Vercel", 才走外部资料补 + 临时方案; 这条不进默认流。

## 何时读

- 进入 deployment 阶段(实现和验证已完成或用户只要求部署)
- 用户贴 SSH 凭证, 要部署到自己的服务器 → 同时读 [08b-ssh-deploy.md](08b-ssh-deploy.md)
- 上线后做 golden replay 校准

## 目录

- [Part 1: 部署](#part-1-部署)
  - [部署进入条件](#部署进入条件)
  - [部署决策树](#部署决策树)
  - [本地 production server 路径](#本地-production-server-路径)
  - [远程服务器 SSH 路径](#远程服务器-ssh-路径)
  - [收尾附一问](#收尾附一问)
  - [Release packet 门禁](#release-packet-门禁)
  - [部署交付物](#部署交付物)
  - [部署完成门槛](#部署完成门槛)
  - [反模式](#部署反模式)
- [Part 2: 校准](#part-2-校准-已上线需求回放)

---

# Part 1: 部署

## 部署进入条件

- 实现和验证阶段已完成, 或用户明确只要求部署现有项目
- 能运行的 lint/typecheck/test/build 已通过或风险已记录
- 已读 `.opc/solution/solution-design.md`、`.opc/state/opc-task.json`

## 部署决策树

```text
1. 项目已有 CI/CD / 部署脚本配置?
   ├── 是 → 读配置, 跑本地等价验证, 按现有流程部署
   └── 否 → 进 2

2. 用户当前消息或 solution 里有"上线 / 部署 / 服务器 / SSH / production"?
   ├── 否 → 走本地 production server, 在收尾附一句"要不要部署到你的服务器"
   └── 是 → 进 3

3. 用户给的是 SSH 凭证(IP + 账号或 key)?
   ├── 是 → 走 远程服务器 SSH 路径 (详见 [08b-ssh-deploy.md](08b-ssh-deploy.md))
   ├── 否 → 问"要部署到自己的服务器吗? 是的话发我 IP + 账号(例如 192.0.2.10 deploy/<password>)"
   └── 用户说 Vercel / Netlify / 其它 PaaS → 告诉他: 当前 OPC 默认不内置 PaaS 路径,
       让他给出他熟悉的部署方式, 或同意走本地 / SSH 替代
```

## 本地 production server 路径

**OPC 默认终点**。不需要用户额外授权。

步骤:

```bash
# 1. production build
npm run build

# 2. 起 production server (后台运行)
npm run start &
# 或 pm2: pm2 start npm --name <app> -- start

# 3. 健康检查
curl -sf http://localhost:3000 -o /dev/null -w "%{http_code}\n"

# 4. 浏览器或 curl 端到端 (按 verification 阶段的主链路, 此处复跑一次确认 production build 没破)
```

写 `.opc/deployment/release.md`(简短版本, 因为本地路径不需要 premortem):

```markdown
# Release Evidence — local production server

## Mode
local-prod-server

## Build
- Command: npm run build
- Output: .next/standalone (size <X MB)

## Start
- Command: npm run start (或 pm2 start npm --name <app> -- start)
- URL: http://localhost:3000

## Verification
- HTTP 200 / 主链路 e2e 过 / DB 数据真实持久
- (列出 verification 阶段已经跑过的关键证据)

## Rollback
- 停服务: pm2 stop <app> 或 kill 进程
- 重 build: git checkout <prev-commit> && npm run build && pm2 restart <app>

## 升级到远程服务器(如果以后要)
- 准备 1 台 Linux 服务器 + SSH 账号
- 把 IP + 账号告诉 AI(例如 192.0.2.10 deploy/<password>), 走 [08b-ssh-deploy.md]
```

## 远程服务器 SSH 路径

用户已经贴了 SSH 凭证 → 跳到 [08b-ssh-deploy.md](08b-ssh-deploy.md)。

凭证缺失 → 用 [收尾附一问](#收尾附一问) 的话术让用户贴。**不要列 Vercel/Netlify/Cloudflare** 4 选 1。

## 收尾附一问

本地 production server 完成时, 收尾**附一句**问要不要部署到服务器, **但不阻塞 mark deployment done**。用户回"暂时不要"或没回应, 当前轮就算完成; 用户回了凭证就走 SSH 路径。

模板:

```text
[已完成]
- 本地 production build 跑通: <build 摘要>
- production server 已启动: http://localhost:3000
- 端到端 <N> 项验证全过(<关键场景列表>)

[证据]
- build log: <路径或摘要>
- 启动命令: npm run start (或 pm2 ...)
- e2e 命令: <复跑命令>

[任务完成]
- 本地已可用, 启动命令 npm run start。

如果你想部署到自己的服务器, 发我 IP + 账号(例如 `192.0.2.10 deploy/<password>`),
我接着 ssh 上去装 Docker / MySQL / Node / pm2 并完成部署。
暂时不需要的话回一句"就这样"即可。
```

用户后续贴凭证(可能下一轮) → resume 进 [08b-ssh-deploy.md](08b-ssh-deploy.md)。

## Release packet 门禁

远程部署 production 时, 先冻结 release profile:

- **mode**: local-prod-server / remote-ssh-preview / remote-ssh-production / rollback-response
- **artifact**: build output / docker image / rsync source
- **environment**: local / staging / production
- **rollout strategy**: replace / rolling / blue-green
- **verification depth**: health-only / smoke-tests / release-checklist

**production gate 前必须做 premortem**; 高风险(涉及权限、用户数据、secrets、迁移、外部依赖)再做 red-team。这是"重要事该停就停"的硬性要求, 不因"减少打断"而放弃。

- premortem 记录: top risks、early warning、prevention、mitigation、owner
- red-team 记录: 攻击面、失败模式、不可逆动作、加固建议

本地 production server 路径**不强制** premortem(没有外部影响面)。

## 部署交付物

`.opc/deployment/release.md`。本地路径用上一节的简短模板; 远程 SSH 路径用 [08b-ssh-deploy.md#健康检查--releasemd](08b-ssh-deploy.md#健康检查--releasemd) 的完整模板。

凭证(密码 / 私钥内容 / DB root pass)按 [10-contracts.md#token-安全契约](10-contracts.md#token-安全契约) 占位脱敏, 不写明文。

## 部署完成门槛

**本地 production server** 完成必须:

- [ ] `npm run build` 通过
- [ ] `npm run start` 或 pm2 起进程, HTTP 200
- [ ] 主链路 e2e 复跑过(production build 上, 不只是 dev)
- [ ] release.md 写明: build / start / e2e 命令, URL, rollback 方式
- [ ] `.opc/state/opc-task.json` 中 `deployment` 标记为 `done`, mode=local-prod-server

**远程 SSH** 完成必须:

- 走 [08b-ssh-deploy.md#部署完成门槛](08b-ssh-deploy.md#部署完成门槛) 全部 checklist
- production 部署额外要 premortem + stop conditions + rollback 实测

任一项缺 → 标 `blocked` 或 `skipped` 并写明原因, **不说"已部署"**。

## 部署反模式

- ❌ 列 "Vercel / Netlify / Cloudflare / 自有服务器" 4 选 1 让用户选 — 用户认不出
- ❌ 默认问 production 凭证 — 默认应是本地 prod, 远端是收尾后用户主动要求
- ❌ 把"本地 production server 跑通"说成"未部署 / 待 production" — 它就是合法的 deployment done
- ❌ 写"Vercel 或本地等价"这种不确定目标
- ❌ 凭证缺失就静默退回 `next start` 假装完成
- ❌ 没有 git remote 就停
- ❌ 部署"完成"但没有 URL、健康检查或状态证据
- ❌ 用户贴 IP + 密码后, AI 在回显 / commit / release.md 里**明文留存密码**(违反凭证回显契约)
- ❌ 远端 production 部署跳 premortem — 重要的事就要停下来问

---

# Part 2: 校准 (已上线需求回放)

不拿全新需求直接赌效果, 用已经上线、资料完整、效果已知的需求做 **golden replay**, 调到 AI 产物接近或超过人工产物, 再推广到新需求。

## 适用场景

- 团队要沉淀 OPC "宪法/规约"
- 需要证明 skill 从需求到上线的效果
- 现有规则不好判断是否够用
- 组长要求拿已上线版本的需求重跑、对比 AI 和人工差距

## 输入包

优先收集:

- 原始需求/PRD
- 设计稿或截图
- 接口文档和字段说明
- 已上线代码或发布分支
- 测试用例、验收记录、线上截图
- 事故、返工、评审意见

资料不全也能跑, 但要在 gap report 里标注缺口。

## 回放步骤

1. **建立 golden baseline**:
   - 记录人工版本的需求、设计、代码、部署和验收证据
   - **不把人工实现细节提前泄漏给生成阶段**, 避免污染

2. **用 OPC 正常流程重跑**:
   - requirements → solution → UI → implementation-plan → implementation → verification → deployment/check
   - 每阶段产物独立落盘

3. **对比差距**:
   - 需求覆盖: 少了哪些角色、流程、状态、异常
   - UI 设计: 页面数量、信息架构、语种、可访问性、组件库
   - 代码实现: 组件边界、API wiring、状态、错误处理、测试
   - 部署验证: 构建、环境变量、访问、回滚

4. **沉淀规则**:
   - 能普遍复用的写入 SKILL.md 或 reference
   - 具体项目规则写入项目自己的 docs / skill reference
   - 可自动检查的变成 scripts 或 evals

5. **做 AAR**:
   - what expected: 原本预期 AI 在每阶段做到什么
   - what happened: 实际 replay 输出和 golden baseline 的差异
   - why different: 缺需求、缺方案、缺 UI 规则、缺验证, 还是工具/环境问题
   - what changes: 规则、脚本、eval、项目约定分别怎么更新

## Gap Report 模板

写到 `.opc/calibration/<feature-name>-gap-report.md`:

```markdown
# Calibration Gap Report

## Golden Feature
- 名称 / 上线版本 / 输入材料

## Replay Output
- PRD / Solution / UI / Code / Deployment/verification

## Gaps
| 类型 | Golden | Replay | 影响 | 修复规则 |
|---|---|---|---|---|

## Rule Updates
- SKILL.md / references / scripts / evals

## AAR
- What expected / What happened / Why different / What changes
- Owner / follow-up

## Decision
- 可用于新需求 / 需要继续校准 / 暂不推广
```

## 校准完成门槛

- 有 golden baseline 和 replay output
- 差距被分类, 不只是主观"差不多"
- AAR 已回答 expected / happened / why / changes
- 每个高影响差距有规则更新或明确后续
- `.opc/state/opc-task.json` 中 `calibration` 标记为 `done` 或 `blocked` 并写原因
