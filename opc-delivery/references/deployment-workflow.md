# CI/CD 和部署工作流

目标: 把已验证实现发布到目标环境, 并给出可访问链接、状态证据和回滚方式。

部署阶段是执行阶段, 不是默认等用户继续的阶段。若部署目标、凭证或 production 意图已经明确, 直接执行。只有目标不明确、缺凭证、涉及 production、远端 push、付费资源或破坏性副作用时, 才使用原生选择/确认交互。

## 目录

- [进入条件](#进入条件)
- [部署目标确认](#部署目标确认)
- [部署决策](#部署决策)
- [Release packet 门禁](#release-packet-门禁)
- [CI/CD 最小规范](#cicd-最小规范)
- [Vercel 路径](#vercel-路径)
- [Netlify / Cloudflare Pages 路径](#netlify--cloudflare-pages-路径)
- [自有服务器路径](#自有服务器路径)
- [本地 production server 路径](#本地-production-server-路径)
- [部署交付物](#部署交付物)
- [完成门槛](#完成门槛)

## 进入条件

- 实现和验证阶段已完成, 或用户明确只要求部署现有项目;
- 能运行的 lint/typecheck/test/build 已通过或风险已记录;
- 已检查 solution、state 和环境配置;
- production、推送远端、覆盖服务器、写 secrets 等动作必须有真实意图或确认。

## 部署目标确认

先读 `.opc/solution/solution-design.md`、`.opc/solution/discussion.md` 和 `.opc/state/opc-task.json`。

直接执行的情况:

- solution 已明确目标平台 + 环境 + 凭证位置;
- 用户当前消息明确指定平台, 且所需凭证已存在;
- 用户只要求本地预览或本地 production server, 且无对外发布副作用。

需要原生选择/确认的情况:

- 部署目标未明确;
- 云平台缺 token/login, 不能默默降级成本地;
- 用户说“上线”但没说明 preview/staging/production;
- 需要 remote push、production、写 secrets、覆盖服务器或破坏性迁移;
- 多个部署路径成本、权限或回滚方式差异很大。

原生交互可用时, 打开真实选择框或确认框:

- 推荐项放第一并标推荐;
- 每题 2-3 个选项;
- 保留自定义入口;
- hand-off 只写“已打开原生交互、默认推荐、等你提交后继续”。

文本降级示例:

```text
[需要你拍板]
- A. Vercel preview (推荐) — Next.js 零配置, 需要 VERCEL_TOKEN 或本地登录
- B. Cloudflare Pages / Netlify — 静态优先, 需要对应 token
- C. 自有服务器 — 需要 SSH、主机、端口和回滚路径
- D. 本地 production server — 只在本机可访问, 不对外
- E. 自定义 / type something
- 默认 = A

[下一步]
等你回 A/B/C/D/E 后继续部署。
```

凭证处理:

- 用户贴 token -> 提醒已进入会话记录, 配置后建议 revoke / rotate, 只写安全位置;
- 用户说本地已 login -> 直接跑 CLI 探测, 失败再回到确认;
- 用户选本地路径 -> 在 release.md 写明“用户选择本地路径, 不对外部署”。

部署阶段反模式:

- 写“Vercel 或本地等价”这种不确定目标;
- token 缺失就静默退回 `next start`;
- 没有 git remote 就停;
- 无凭证就跳过整个 deployment;
- 部署“完成”但没有 URL、健康检查或状态证据。

## 部署决策

```text
1. 项目已有 CI/CD 配置吗?
   ├── 是 -> 读配置 -> 运行本地等价验证 -> 按现有流程部署
   └── 否 -> 进 2

2. 部署目标明确吗?
   ├── 否 -> 原生选择交互 / 文本降级, 等用户提交
   └── 是 -> 进 3

3. 按目标执行
   ├── Vercel -> preview first; production only explicit
   ├── Netlify / Cloudflare -> 同 Vercel 模式
   ├── 自有服务器 -> SSH / Docker / pm2 + 健康检查 + 回滚
   ├── 本地 production server -> next start / pm2 + 端口 + URL 证据
   └── 用户自定义 -> 按用户指令

4. 缺凭证或运行失败 -> 分类为卡住缺 X 或重新确认, 不静默降级
```

## Release packet 门禁

部署阶段先冻结 release profile:

- mode: preview-release / environment-promotion / production-rollout / rollback-response / release-hardening;
- artifact: build output、container image、platform build 或其它;
- environment: preview / staging / production / local-production;
- promotion model: same-artifact-promotion / rebuild-per-env / direct-deploy;
- rollout strategy: replace / rolling / blue-green / canary / feature-flag-assisted;
- verification depth: health-only / smoke-tests / release-checklist / automated-analysis。

production gate 前必须做 premortem; 高风险或涉及权限、数据、secrets、迁移、外部依赖时再做 red-team。premortem 记录 top risks、early warning、prevention、mitigation、owner。red-team 记录攻击面、失败模式、不可逆动作和加固建议。

## CI/CD 最小规范

- 构建前: 安装依赖、lint、typecheck、test、build;
- repo: 没有本地 Git 时初始化; 没有 remote 不是 preview/local release 的停点;
- secrets: 只放平台 secret store 或安全环境变量, 不写入仓库;
- environments: preview 和 production 分开;
- production gate: 明确审批、分支、tag 或 release 条件;
- stop conditions: 明确哪些信号会停止 promotion 或触发 rollback;
- rollback: 记录上一版本、平台 rollback 命令或回滚提交;
- evidence: 部署 URL、状态、构建日志摘要、健康检查、核心页面截图。

## Vercel 路径

- 默认 preview deployment;
- 若项目已有 `.vercel/project.json` 或 `.vercel/repo.json`, 按已链接项目走;
- 有 git remote 且用户批准 push 时, 优先 git push 触发平台构建;
- 无 git remote 或不想 push 时, 用 CLI preview;
- production 只有用户明确要求才用 `--prod`;
- DB 走 Postgres(Vercel Postgres / Supabase / Neon)；若 solution 锁的是 SQLite, 这里要同步说明并确认迁移。

Vercel token / login 缺失 -> 卡住缺凭证或回到部署目标确认, 不降级成本地。

## Netlify / Cloudflare Pages 路径

- token + CLI 或 git push;
- Netlify Functions / Cloudflare Workers 替代 Next.js API routes 时, 注意运行时差异(edge vs Node);
- DB 走平台对应服务或外部 Postgres。

## 自有服务器路径

- 先检查 `.github/workflows/`;
- 需要新增 workflow 时, 最小化到 build/test/deploy, 不塞无关 job;
- 使用 GitHub environments、环境变量和 required reviewers 保护 production;
- 若要排查失败 checks, 使用 `gh` 查看 run/job/log, 再改代码或 workflow;
- 服务器部署要记录 host、目录、启动命令、端口、反向代理、健康检查和回滚方式;
- Node 应用: pm2 / systemd / Docker; 反向代理: nginx / Caddy / Traefik;
- DB: 本地 Postgres / 外部托管, schema 迁移走 `prisma migrate deploy`。

## 本地 production server 路径

只在用户明确选了本地路径或需求只要求本机可访问时走。不是云部署失败的静默兜底。

步骤:

- 跑 `next build` 拿 standalone / `npm run build` 拿对应产物;
- 起 `next start` / `node dist/server.js` / `pm2 start` / `docker compose up`;
- 记录 URL: `http://localhost:<port>` 或宿主局域网 IP;
- 验证: `curl` 主路由拿 200, 浏览器打开看核心流程;
- DB: SQLite 文件 / 本地 Postgres, schema 已迁移, seed 已灌;
- 在 release.md 明确“用户选择本地路径, 不对外部署; 如需 cloud, 切 A/B/C 后升级”。

## 部署交付物

默认写 `.opc/deployment/release.md`:

```markdown
# Release Evidence

## 部署目标
- 用户选择: <原生选择提交结果 / 文本降级回复 / 已明确目标>
- 选择理由:
- 凭证位置:

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
- DB 数据真实持久(刷新后):
- Console errors:

## Rollback
- Previous version:
- Rollback command/path:
- Known risk:

## 升级路径(若选了本地路径)
- 切换到云平台的步骤:
- 需要补的凭证:
- 估计停机:
```

## 完成门槛

- 部署 URL 可访问, 或平台状态明确;
- 部署目标明确, 不是代理单方面退回;
- 关键页面和核心流程已验证, 且 DB 数据真实持久(本地路径也要有);
- production 有显式授权、premortem、stop conditions 和回滚方案;
- `.opc/state/opc-task.json` 中 `deployment` 标记为 `done`, 记录 URL 和证据。
