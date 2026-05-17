# CI/CD 和部署工作流

目标: 把已验证实现发布到目标环境, 并给出可访问链接、状态证据和回滚方式。

**部署目标必须先在 ConfirmCard 锁定**, 不允许 AI 在 Stage Card 写"Vercel 或本地等价"这种"或"假设, 也不允许在凭证缺失时默默从云平台退回本地。如果 solution 阶段已经锁定部署目标, 本阶段直接执行; 如果没锁或凭证不齐, 进本阶段时先抛一轮 ConfirmCard。

**节奏 = 执行式, 但开局必须先确认目标**。

## 目录

- [进入条件](#进入条件)
- [部署目标 ConfirmCard](#部署目标-confirmcard)
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

- 实现阶段已完成或用户明确只要求部署现有项目;
- 能运行的 lint/typecheck/test/build 已通过或风险已记录;
- **部署目标已明确**(平台 + 环境 + 凭证位置); 没明确就在本阶段补一轮 ConfirmCard 再继续;
- production、推送远端、覆盖服务器、写 secrets 等动作已确认真实意图。

## 部署目标 ConfirmCard

进 deployment 阶段时, 先读 `.opc/solution/discussion.md` 和 `.opc/state/opc-task.json` 看部署目标是否已锁定。

**已锁定**(solution ConfirmCard 里有明确平台 + 用户认可) → 直接执行对应路径。

**未锁定 或 锁定的平台缺凭证 / 缺前置条件** → 必须抛一轮 ConfirmCard:

```text
OPC ConfirmCard · deployment · 部署目标确认

[现状]
- 构建产物: <next build 输出 / dist/ / standalone>
- 当前环境: <已检测到的 vercel CLI? netlify CLI? gh CLI? 远端 git remote? SSH key?>
- solution 阶段锁定的部署目标 = <复述, 或"未锁定">
- 凭证状态 = <Vercel token: 有/无; ssh: 有/无; GitHub remote: 有/无>

[我需要你选一个具体平台来部署]
A. Vercel(若前端是 Next.js / 静态站, 推荐)
   - 需要: VERCEL_TOKEN 或登录态; 我会用 CLI preview 或 git push
   - 你提供方式: 把 token 贴这里 / 你本地已经 vercel login / 跳过 cloud 走 B 或 C
B. Netlify / Cloudflare Pages
   - 类似 A, 需要对应 token / 登录
C. 自有服务器(VPS / Docker / Node + pm2)
   - 需要: SSH 凭证 + 主机地址 + 端口 + 域名(可选)
   - 你提供方式: 给我 host + 部署用户, 或我把构建产物打包让你自己上传
D. 本地 production server(只在你机器上跑, 不对外)
   - 适用: 没有云账号、不需对外暴露、只要给团队演示
   - 我会跑 next start / pm2 / docker compose up 并给出 http://localhost:<port>
E. 自定义 / 其它

[我的默认推荐]
- 如果 solution 锁定了 X, 推荐还是 X, 但需要 <凭证项>
- 如果 solution 未锁定, 推荐 D(本地零成本) 作为首次部署, 等真要对外再切 A-C

[你回答这条之前, 我不会去 build/push/deploy]
```

用户明确选了某项, 才进入对应路径。**不允许 ConfirmCard 没回应就 build, 也不允许凭证缺失时悄悄降级**。

凭证还可以这样给:

- 用户在聊天里贴 token → 提醒已进入会话记录, 配置后建议 revoke / rotate, 然后写入宿主 user-scope 安全位置(不进版本控制)。
- 用户说"我本地已经 vercel login" → 直接用 `vercel` CLI 试一次, 失败再回到 ConfirmCard。
- 用户说"用 D 本地就行" → 走本地 production server 路径, 在 release.md 明确"用户授权 D 路径"。

deployment 阶段反模式 (不允许出现):

- ❌ Stage Card 写"Vercel 或本地等价" — 必须确定其中一个
- ❌ Vercel token 缺失就静默退回 `next start` — 凭证缺失应抛 ConfirmCard, 不自动降级
- ❌ 没有 git remote 就停 — 默认本地 `git init` 已在 implementation 阶段完成, 部署继续走 preview; 远端 push 才需要用户授权
- ❌ "无部署凭证/服务器" 解释成"跳过整个 deployment 阶段" — 应抛 deployment ConfirmCard 走 D 本地 production 路径作为兜底
- ❌ 部署"完成" 但没给可访问 URL + 健康检查证据

## 部署决策

```text
1. 项目已有 CI/CD 配置吗?
   ├── 是 -> 读配置 -> 运行本地等价验证 -> 按现有流程部署
   └── 否 -> 进 2

2. 部署目标 ConfirmCard 已收敛吗?
   ├── 否 -> 抛 ConfirmCard, 等用户选
   └── 是 -> 进 3

3. 按用户选的目标走
   ├── A. Vercel -> preview first; production only explicit
   ├── B. Netlify / Cloudflare -> 同 Vercel 模式
   ├── C. 自有服务器 -> SSH / Docker / pm2 + 健康检查 + 回滚
   ├── D. 本地 production server -> next start / pm2 + 端口 + URL 证据
   └── E. 用户自定义 -> 按用户指令

4. 缺凭证或运行失败 -> 回 ConfirmCard, 不要降级
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
- DB 走 Postgres(Vercel Postgres / Supabase / Neon) — 若 solution 锁的是 SQLite, 这里要切到 Postgres(用户已知或在 ConfirmCard 里同步说明)。

**Vercel token / login 缺失 → 回 ConfirmCard, 不降级**。
不允许"VERCEL_TOKEN 不存在 → 退回 next start"这种悄悄降级。

## Netlify / Cloudflare Pages 路径

- 类似 Vercel: token + CLI 或 git push;
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

**只在用户明确选了 D 选项时才走**。不是云部署失败的兜底。

步骤:

- 跑 `next build` 拿 standalone / `npm run build` 拿对应产物;
- 起 `next start` / `node dist/server.js` / `pm2 start` / `docker compose up`;
- 记录 URL: `http://localhost:<port>` 或宿主局域网 IP;
- 验证: `curl` 主路由拿 200, 浏览器打开看核心流程;
- DB: SQLite 文件 / 本地 Postgres, schema 已迁移, seed 已灌;
- 在 release.md 明确"用户授权 D 路径, 不对外部署; 如需 cloud, 切 A/B 后用 X 步骤升级"。

## 部署交付物

默认写 `.opc/deployment/release.md`:

```markdown
# Release Evidence

## 部署目标(已 ConfirmCard 锁定)
- 用户选择: A / B / C / D / E
- 选择理由(摘自 discussion):
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

## 升级路径(若选了 D)
- 切换到 A/B/C 的步骤:
- 需要补的凭证:
- 估计停机:
```

## 完成门槛

- 部署 URL 可访问, 或平台状态明确;
- 部署目标是用户在 ConfirmCard 里明确选的, 不是 AI 单方面退回的;
- 关键页面和核心流程已验证, 且 DB 数据真实持久(本地路径也要有);
- production 有显式授权、premortem、stop conditions 和回滚方案;
- `.opc/state/opc-task.json` 中 `deployment` 标记为 `done`, 记录 URL 和证据。
