# CI/CD 和部署工作流

目标: 把已验证实现发布到目标环境，并给出可访问链接、状态证据和回滚方式。默认先
preview，不默认 production。

完整 OPC 任务到达部署阶段时必须继续推进到可访问的 preview/staging 链接，除非缺平台、
凭证、构建条件或用户明确暂停。不要因为 production 需要确认就停止部署阶段；先交付安全的
预览上线证据，再记录 production gate。

缺部署前置条件时先补齐能本地完成的部分: 没有 Git 仓库就本地 `git init`，没有 CI/CD 就补
最小 build/test workflow 或 release checklist，没有 preview 平台凭证就先完成本地 preview
和部署包证据，再用选择题收集平台、服务器或 token。

## 目录

- [进入条件](#进入条件)
- [部署决策](#部署决策)
- [Release packet 门禁](#release-packet-门禁)
- [CI/CD 最小规范](#cicd-最小规范)
- [Vercel 路径](#vercel-路径)
- [GitHub Actions / 服务器路径](#github-actions--服务器路径)
- [部署交付物](#部署交付物)
- [完成门槛](#完成门槛)

## 进入条件

- 实现阶段已完成或用户明确只要求部署现有项目；
- 能运行的 lint/typecheck/test/build 已通过或风险已记录；
- 已确认目标平台、环境变量/secrets、构建命令和访问域名；
- production、推送远端、覆盖服务器、写 secrets 等动作已确认真实意图。

## 部署决策

```text
1. 项目已有 CI/CD 配置吗?
   ├── 是 -> 读配置 -> 运行本地等价验证 -> 按现有流程部署
   └── 否 -> 进 2

2. 用户指定平台吗?
   ├── Vercel -> preview first; production only explicit
   ├── GitHub Actions/server -> workflow + environment/secrets + rollback
   └── 未指定但项目有安全默认路径 -> 自动 preview/staging
       未指定且无安全默认路径 -> 选择题澄清

3. 缺少本地发布基础设施吗?
   ├── 无 Git -> git init + .gitignore，然后继续本地 build/preview
   ├── 无 CI -> 补最小 build/test workflow 或 release checklist
   └── 无部署凭证/服务器 -> 记录 blocked gate，给选择题拿 token/server
```

选择题:

```text
部署目标我按哪种走?
A. Preview 部署(推荐): 先给可访问预览链接，验证通过后再考虑 production。
B. 直接 production: 我会先确认环境变量、回滚和风险。
C. 自定义 / type something: 你写平台、服务器或 CI/CD 要求。
```

## Release packet 门禁

部署阶段先冻结 release profile:

- mode: preview-release / environment-promotion / production-rollout / rollback-response / release-hardening；
- artifact: build output、container image、platform build 或其它；
- environment: preview / staging / production；
- promotion model: same-artifact-promotion / rebuild-per-env / direct-deploy；
- rollout strategy: replace / rolling / blue-green / canary / feature-flag-assisted；
- verification depth: health-only / smoke-tests / release-checklist / automated-analysis。

production gate 前必须做 premortem；高风险或涉及权限、数据、secrets、迁移、外部依赖时再做 red-team。
premortem 记录 top risks、early warning、prevention、mitigation、owner。red-team 记录攻击面、
失败模式、不可逆动作和加固建议。

## CI/CD 最小规范

- 构建前: 安装依赖、lint、typecheck、test、build；
- repo: 没有本地 Git 时初始化；没有 remote 不是 preview/local release 的停点；
- secrets: 只放平台 secret store 或安全环境变量，不写入仓库；
- environments: preview 和 production 分开；
- production gate: 明确审批、分支、tag 或 release 条件；
- stop conditions: 明确哪些信号会停止 promotion 或触发 rollback；
- rollback: 记录上一版本、平台 rollback 命令或回滚提交；
- evidence: 部署 URL、状态、构建日志摘要、健康检查、核心页面截图。

## Vercel 路径

- 默认 preview deployment；
- 若项目已有 `.vercel/project.json` 或 `.vercel/repo.json`，按已链接项目走；
- 有 git remote 且用户批准 push 时，优先 git push 触发平台构建；
- 无 git remote 或不想 push 时，用 CLI preview；
- production 只有用户明确要求才用 `--prod`。
- 如果用户只说“上线 / 给链接”，先完成 preview deployment；不要把 production gate 当成阻塞整体上线交付的理由。

## GitHub Actions / 服务器路径

- 先检查 `.github/workflows/`；
- 需要新增 workflow 时，最小化到 build/test/deploy，不塞无关 job；
- 使用 GitHub environments、环境变量和 required reviewers 保护 production；
- 若要排查失败 checks，使用 `gh` 查看 run/job/log，再改代码或 workflow；
- 服务器部署要记录 host、目录、启动命令、端口、反向代理、健康检查和回滚方式。

## 部署交付物

默认写 `.opc/deployment/release.md`:

```markdown
# Release Evidence

## Build
- Commands:
- Result:

## Deployment
- Platform:
- Environment:
- URL:
- Status:
- Commit/Version:

## Release Profile
- Mode:
- Artifact:
- Promotion model:
- Rollout strategy:
- Stop conditions:

## Environment
- Required vars:
- Secrets location:

## Premortem / Red-team
- Top risks:
- Early warnings:
- Prevention:
- Mitigation / owner:
- Red-team findings:

## Verification
- Health check:
- Browser screenshot:
- Core flow:
- Console errors:

## Rollback
- Previous version:
- Rollback command/path:
- Known risk:
```

## 完成门槛

- 部署 URL 可访问，或平台状态明确；
- 关键页面和核心流程已验证；
- production 有显式授权、premortem、stop conditions 和回滚方案；
- `.opc/state/opc-task.json` 中 `deployment` 标记为 `done`，记录 URL 和证据。
