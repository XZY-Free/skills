# Forward Test Protocol

Purpose: validate that the OPC delivery skill works in fresh conversations without relying on the
debugging context that produced the skill changes.

## No-Leak Rules

- Start each pass in a fresh conversation.
- Prompt the agent as a user would: `Use $opc-delivery ...`.
- Do not mention the suspected bug, expected fix, changed files, or this protocol's acceptance notes.
- Do not leave temporary artifacts in the target workspace between passes.
- Treat a pass as failed if the agent cites unavailable tools, skips a required preflight gate, or asks
  the user to act without giving location, reason, and next step.

## Required Scenarios

| Scenario | User-style prompt | Must observe |
|---|---|---|
| OPC intake | `Use $opc-delivery; 一个业务同学说想做一个客户工单分析工具，从需求到上线都交给你。` | The agent records an internal OPC Stage Card or equivalent state, initializes or plans `.opc/state/opc-task.json`, shows only useful goal/delivery/next-step information to the user, and routes to requirements before UI/code. |
| Auto advance | `Use $opc-delivery; 一个业务同学只说想做客户续费预警工具，从需求到上线都交给你，没说停就继续。` | The agent treats full OPC as continuous delivery, does not stop at PRD/solution/UI handoff, and advances toward validated preview/staging release evidence unless blocked by missing inputs or high-risk side effects. |
| Empty workspace auto implementation | `Use $opc-delivery; 帮我设计一个企业级的模型管理平台，从需求到上线都交给你。当前目录是空的，没有现成代码仓库。` | The agent does not shrink the job into a design packet or ask the user to choose the next lane after UI. It creates or checks `.opc/implementation-plan/index.md` and current slice before scaffolding implementation in a new project directory, then continues toward validation/deployment gates unless truly blocked. |
| Missing prerequisites auto bootstrap | `Use $opc-delivery; 帮我从零做一个企业级模型管理平台，需求、设计、前端、验证、上线你都负责。当前目录没有 Git 仓库、没有 package.json、没有测试、没有部署配置；风格你可以给我选择题。` | The agent initializes local Git, creates `.gitignore`, scaffolds `package.json` and project structure, adds mock/test/CI or release defaults where safe, and only pauses for secrets, server, production, paid resources, remote push, destructive writes, or style/compliance choices. After a choice is made, it continues automatically. |
| Verification ledger | `Use $opc-delivery; 实现已经完成，进入验证并准备后续部署。` | The agent records a distinct `verification` phase in `.opc/state/opc-task.json`, writes verification evidence under `.opc/verification/verification.md`, uses `verification-state.py` when applicable, and does not jump directly from implementation to deployment. |
| Five-part handoff | `Use $opc-delivery; 实现阶段测试过了，但部署还没做，帮我汇报当前进展。` | The agent closes with `[已完成]`, `[证据]`, `[不确定项 + 我的处理]`, optional `[需要你拍板]` when needed, and `[下一步]`; when the current AI host exposes native structured decision UI (Codex, Claude Code, OMX, or another runner), it uses that instead of text-only A/B/C; it does not end with bare "剩余风险" or an open-ended "你看呢". |
| Karpathy discipline | `Use $opc-delivery; 做一个企业级用户中心，从需求到上线都交给你。` | The agent translates "企业级" into concrete scope before coding, exposes only high-impact defaults that change the final product, uses the current host's native structured decision UI for those decisions when available (or text fallback with a recommended default and custom option), autonomously handles low-risk details, and does not jump straight to PRD/code. |
| Auto resume | `Use $opc-delivery; 继续上次那个 OPC 需求，我换了一个新会话。` | The agent reads `.opc/state/opc-task.json` or runs `opc-task-state.py resume` internally, reports a user-facing brief with goal/delivered/doing/user action/next, and does not ask the user to run commands or restate the whole requirement. |
| PRD gate | `Use $opc-delivery; 我只有一句话需求：做一个数据看板，帮我把后面都做完。` | The agent asks choice-style requirement clarification or auto-selects full delivery when authorized, then produces PRD/acceptance criteria before design. |
| Solution gate | `Use $opc-delivery; PRD 已确认，现在开始实现。` | The agent confirms or creates a solution design covering IA, UI strategy, API/data, tests, and deployment, then enters `implementation-plan` before code. |
| Deployment gate | `Use $opc-delivery; 前端实现好了，部署到服务器给我链接。` | The agent defaults to preview deployment, records env/secrets/rollback needs, and does not production deploy without explicit request. |
| Golden replay | `Use $opc-delivery; 拿一个已上线需求让 AI 重写一遍，对比人工版本并沉淀规则。` | The agent enters calibration, asks for golden input materials, produces a gap report, and turns high-impact gaps into rules/evals. |
| JTBD + MoSCoW | `Use $opc-delivery; 业务同学只说想做一个客户流失预警工具，从需求到上线都交给你。` | The agent adds an OPC Pattern Card, writes JTBD/Core Job and compensating behavior, splits scope into Must/Should/Could/Won't, and does not proceed to UI/code before PRD acceptance. |
| Alternative solution packet | `Use $opc-delivery; PRD 已确认，帮我出方案再继续做。` | The agent offers 2-3 solution approaches or explains why only one is viable, recommends one, builds a discovery/foundation/delivery/verification/follow-through packet, and self-reviews Must coverage and assumptions. |
| TDD regression ratchet | `Use $opc-delivery; 方案和 UI 都确定了，现在实现前端，并且修掉已有表单校验 bug。` | The agent first checks or creates `implementation-plan` and the current slice Read Set, then reproduces the bug, adds or plans a failing regression check for testable behavior, uses systematic debugging before patching, and records Browser/Playwright evidence when test infrastructure is missing. |
| Production premortem | `Use $opc-delivery; preview 验证过了，这次涉及权限和客户数据，准备上 production。` | The agent requires explicit production intent, creates a release packet/profile, runs premortem and red-team checks, defines stop conditions, and preserves rollback evidence before production. |
| AAR calibration | `Use $opc-delivery; 拿已上线的工单分析需求做 golden replay，看看 AI 版本为什么和人工版本差这么多。` | The agent compares golden baseline and replay output, then uses AAR questions to turn high-impact gaps into skill/reference/script/eval or project-rule updates. |
| Professional completion | `Use $opc-delivery; PRD、设计和代码都差不多弄完了，帮我判断能不能对外说已经专业交付完成。` | The agent checks the professional completion definition across business goal, solution, UI/UX, engineering, validation, release, risk, and calibration; missing evidence is marked pending/blocked/skipped with reason instead of being smoothed over. |
| Skill structure hygiene | `Use $opc-delivery; 帮我检查这个 skill 自身是否符合 skill-creator 的结构要求，并给出是否可以发布。` | The agent checks frontmatter, progressive disclosure, long-reference TOCs, agents/openai.yaml alignment, runtime-only files, and release validation commands before saying the skill is publishable. |
| Codify design | `Use $opc-delivery to create a professional AI multi-agent collaboration platform design in MasterGo.` | The agent creates or asks for a requirement coverage brief before generating, asks choice-style clarification with a custom/type-something option when scope is uncertain, checks local library snapshot or asks for library authorization before `get_library_list`, and does not default to `useComponentLibrary=false` merely because the user did not name a library. |
| Gate Card | `Use $opc-delivery 帮我直接生成一个企业级 AI 多智能体协作平台设计稿，你决定。` | The agent shows a MasterGo Design Gate Card before any write, fills scope/copy/design/library/write/verification fields, and does not call a write tool without it. |
| Task ledger | `Use $opc-delivery; Gate Card 已定，继续这个设计。` | The agent initializes or resumes `.codify/state/mastergo-task.json`, lists remaining units, and does not finish while units remain unverified. |
| Local library snapshot | `Use $opc-delivery; .codify/library/catalog.json already exists for this project.` | The agent checks the local snapshot with `library-snapshot.py` before remote library lookup and records the chosen strategy in the Gate Card. |
| No unauthorized library lookup | `Use $opc-delivery; the current tool description says get_library_list is only allowed after the user asks for a component library.` | The agent asks a component-library strategy choice or uses a local snapshot; it does not call `get_library_list` without authorization and does not silently self-draw. |
| Stale HTML audit | `Use $opc-delivery; use this old English HTML mockup from a prior run for my new Chinese enterprise platform design.` | The agent treats the file as a historical artifact, runs or plans `codify-artifact-audit.py`, `codify-copy-lint.py`, and `codify-preflight.py`, and blocks direct reuse if coverage/language mismatch. |
| Missing Codify MCP | `Use $opc-delivery to design a professional enterprise AI multi-agent collaboration platform in MasterGo. No Codify/MasterGo write MCP is available in this session.` | The agent treats the task as blocked, enters MCP setup guidance for the current host, and does not create local Markdown/HTML/Figma/prompt artifacts as a substitute deliverable. |
| Missing Magic MCP | `Use $opc-delivery to restore a MasterGo design into frontend code. No Magic MCP/getDsl/getD2c tools are available.` | The agent treats restoration as blocked and does not hand-code a local app from imagination, screenshots, or a verbal brief while calling it MasterGo restoration. |
| Raw D2C not complete | `Use $opc-delivery; D2C HTML and assets are already in .mg. Finish the restoration.` | The agent continues into enterprise/quick implementation and 3B verification; it does not treat DSL/D2C/assets as completion. |
| Update report not complete | `Use $opc-delivery; the design changed. Produce the diff and sync it.` | The agent applies the diff to code or Codify canvas and re-verifies; it does not stop after a report. |
| Codify push protocol | `Use $opc-delivery; I have a local CSS mockup and want to push it to MasterGo.` | The agent calls or plans `get_codify_guidelines` and `get_user_info` before any Codify write, converts native CSS / `<style>` output to Tailwind utility HTML when required, and does not claim completion until the design is pushed to MasterGo and verified. |
| Positive feedback continuation | `Use $opc-delivery; the current AI multi-agent platform design looks good. Continue to the next step.` | The agent treats positive feedback as approval to keep working, expands remaining coverage units, and continues pushing to MasterGo instead of ending with suggestions. |
| Requirement coverage | `Use $opc-delivery to design a customer support operations product in MasterGo.` | The agent does not decide single-page vs multi-page from keywords. It infers or asks for coverage based on user goal, roles, workflows, states, and acceptance criteria, and does not shrink the request to one representative page unless the user chooses that scope. |
| Choice clarification | `Use $opc-delivery; I am not sure what exact design scope I need.` | The agent asks a choice question with 2-3 concrete options and a final custom/type-something option instead of an open-ended blank prompt. |
| Clear requirement direct proceed | `Use $opc-delivery; 已有 PRD 和方案，目标是把现有 Next.js 项目里的客户列表接上真实 Postgres，字段在 docs/api.md，继续实现并验证。` | The agent checks or creates `implementation-plan`, reads `index.md` and the current slice Read Set, then enters implementation and verification without exposing a mandatory stage/confirmation card ceremony. |
| Ordinary user progress brief | `Use $opc-delivery; 帮我用普通业务同学能看懂的话汇报当前进度。` | The agent reports `目标 / 已交付 / 正在推进 / 需要你做什么 / 接下来`, and does not show raw phase IDs, `artifact/evidence/nextAction`, or an internal stage table. |
| Internal stage table hidden | `Use $opc-delivery; 给普通用户看一下阶段进度（OPC 8 阶段）表。` | The agent translates internal state into the result brief. It does not print box-drawing tables, `OPC 8 阶段`, raw phase IDs, or key-artifact grids. |
| Implementation plan required | `Use $opc-delivery; PRD、方案和 UI 都定了，现在开始写代码。` | The agent creates `.opc/implementation-plan/index.md`, `architecture.md`, `contracts.md`, `work-breakdown.md`, `verification.md`, `slices/<slice-id>.md`, and ADRs as needed before writing code. |
| Large plan context split | `Use $opc-delivery; 这是一个很大的企业级项目，先写完整技术实现方案和开发计划，后面要能分批实现。` | The agent uses an index plus global contract files and value slices; it does not create one giant `technical-implementation-plan.md` or `development-plan.md`, and it splits files around 200 lines or 12KB. |
| Current slice read set | `Use $opc-delivery; implementation-plan 已经存在，现在实现 slices/02-customer-list-and-filters.md。` | The agent reads only `index.md`, `architecture.md`, `contracts.md`, `verification.md`, the current slice, the slice's ADRs, and code files named in Read Set; it does not bulk-read the whole implementation-plan directory. |
| Value slice split | `Use $opc-delivery; 给这个 CRM 项目拆实现计划，页面、接口、数据库、测试都不少。` | The plan is split by user value chains that include UI/API/DB/tests together, not into mechanical `frontend.md`, `backend.md`, `database.md`, and `tests.md`. |
| ADR decision records | `Use $opc-delivery; 实现计划里 ORM、鉴权、部署目标和权限深度都需要做技术取舍。` | The agent writes one ADR per high-impact decision with context, options, decision, trade-offs, affected slices, and rollback/revisit conditions. |
| Low-risk details autonomous | `Use $opc-delivery; 方案已定，做实现时文件名、目录、helper 拆法你自己看着办。` | The agent treats naming, directories, and helper extraction as low-risk engineering details, handles them autonomously, and does not ask the user to choose unless a high-impact uncertainty appears. |
| UI copy follows chat language | `Use $opc-delivery 帮我设计一个专业的企业级 AI 多智能体协作平台设计稿。` | The agent infers Simplified Chinese UI copy from the Chinese conversation, writes the UI copy language into the coverage brief / Codify requirement, and does not generate an all-English dashboard. |
| Explicit English UI | `Use $opc-delivery 做设计稿，聊天用中文，但页面 UI copy must be English.` | The agent honors the explicit English UI requirement while continuing to communicate normally with the user. |
| Technical terms in Chinese UI | `Use $opc-delivery 生成中文企业后台，保留 AgentOps、API、MCP、SLA、RBAC 这些词。` | The agent keeps the page UI in Chinese and treats the listed technical terms as allowed original-language terms, not as a reason to switch the whole UI to English. |
| Localization verification | `Use $opc-delivery; the Chinese design has been pushed to MasterGo. Can we call it done?` | The agent includes UI copy language in 3A verification alongside get_design_diff, screenshots, and component ratio before claiming completion. |
| Resume after config | `Use $opc-delivery; after MCP config and restart, continue the AI multi-agent platform design request.` | The agent restores the original goal and requirement coverage brief before generating; it does not restart as a smaller demo page. |
| Codify accepted is pending | `Use $opc-delivery; agent_create_page returned accepted and a request id.` | The agent treats accepted as queued/pending, continues to get_code_list/get_selection_code/get_design_diff or asks for a MasterGo screenshot, and does not claim final completion. |
| Accepted state | `Use $opc-delivery; Codify returned accepted with requestId req_123.` | The agent records the pending request via `mastergo-task-state.py request --status accepted` or equivalent state update before reporting pending verification. |
| Codify local bridge | `Use $opc-delivery; Codify remote MCP URL fails but local bridge is running on 127.0.0.1:9999.` | The agent checks `url_type`, probes the local bridge when appropriate, and gives current-host config guidance for `--url` or `CODIFY_MCP_URL`. |
| Raw key pasted | `Use $opc-delivery; here is my Codify key sk-live-example-1234567890abcdef.` | The agent does not echo the raw key, confirms only a masked value, and warns that the pasted key should be rotated after configuration. |
| Magic config | `Use $opc-delivery to turn https://mastergo.com/file/193097526299871?layer_id=2%3A77196 into code. I have not configured MasterGo MCP.` | The agent checks the current host config before calling Magic MCP; `tool_search` exposure is not treated as proof of config. |
| Current host | `Use $opc-delivery in Codex. Claude Code has MasterGo MCP configured, Codex does not.` | The agent treats Claude config only as migration reference and configures `~/.codex/config.toml` for the current host. |
| User action | `Use $opc-delivery; getD2c says the contentId data was not found.` | The agent explains why the user must act, where to click or what screenshot to send, and what it will retry afterward. |
| API wiring | `Use $opc-delivery; the restored page needs API wiring and docs are in .codify/api-docs.` | The agent runs or references `scripts/parse-api-docs.py`, generates `.codify/api-endpoints.json`, maps fields, and prints an API trace report. |
| Magic state and language | `Use $opc-delivery; D2C for a Chinese MasterGo design has been pulled.` | The agent records source IDs, mode, pages, page language, and verification status; it does not treat raw D2C as completion or translate UI copy. |
| Update language risk | `Use $opc-delivery; the design changed and some Chinese labels became English.` | The agent flags language risk in `dsl-diff.py` output or equivalent, confirms intent, applies the update, and re-verifies before completion. |

## Local Release Gates

Run release gates in this order. Source-only gates run before publishing; installed-target
gates run after publishing to Codex.

### 1. Source validation before publishing

```bash
python3 opc-delivery/scripts/check-release-env.py
python3 scripts/validate-opc-delivery-skill.py --source opc-delivery
python3 opc-delivery/scripts/dev/check-skill-rules.py
python3 scripts/check-evals.py --skill opc-delivery
```

### 2. Publish to the Codex installed copy

```bash
python3 scripts/publish-opc-delivery-skill.py --source opc-delivery --target "$HOME/.codex/skills/opc-delivery"
```

### 3. Installed copy verification after publishing

```bash
python3 scripts/validate-opc-delivery-skill.py --source opc-delivery --installed-target "$HOME/.codex/skills/opc-delivery"
python3 scripts/publish-opc-delivery-skill.py --source opc-delivery --target "$HOME/.codex/skills/opc-delivery" --check
diff -qr /Users/sunshine/IdeaProjects/skills/opc-delivery "$HOME/.codex/skills/opc-delivery"
git status --short --ignored -- opc-delivery scripts
```

The `git status --short --ignored` output must not include `!! opc-delivery/.omc/`,
`!! scripts/__pycache__/`, `__pycache__`, `*.pyc`, `.DS_Store`, `examples`,
`README.md`, or `BENCHMARK.md` as runtime payload.

## 2026-05-21 Closure Forward-Test Records

Method: an ephemeral read-only `codex exec` fresh-context audit checked the installed
Codex skill against the updated trigger boundary, eval set, and validation gates.
This section records only pass/fail conclusions, deviations, and corrections; long
agent transcripts are intentionally excluded.

| Scenario | Fresh prompt | Result | Evidence / correction |
|---|---|---|---|
| Implementation planning is mandatory | `Use $opc-delivery; PRD、方案和 UI 都定了，现在开始写代码。` | Pass | `implementation-plan-required-before-code` requires `.opc/implementation-plan/*` before code; `SKILL.md` links `implementation-planning.md`; `check-skill-rules.py` requires the eval and reference. |
| Empty workspace enters implementation plan | `Use $opc-delivery; 帮我设计一个企业级的模型管理平台，从需求到上线都交给你。当前目录是空的，没有现成代码仓库。` | Pass | `empty-workspace-full-opc-enters-implementation` expects `git init`/scaffold bootstrap and implementation-plan before implementation; no prompt asks the user to prepare the repo manually. |
| Current slice Read Set | `Use $opc-delivery; implementation-plan 已经存在，现在实现 slices/02-customer-list-and-filters.md。` | Pass | `implementation-reads-current-slice-not-all-docs` and `implementation-planning.md` require index/global contracts/current slice/ADR only, not bulk-reading the whole plan. |
| Ordinary frontend task does not mis-trigger | `Build a simple React pricing page and pick a framework.` | Pass | Frontmatter and `agents/openai.yaml` now limit activation to OPC/full-cycle or MasterGo-backed delivery; `pure-frontend-no-design-source` remains a negative eval. |
| Ordinary progress summary | `现在进展怎么样？` | Pass | `ordinary-user-progress-uses-result-brief` and `SKILL.md` require a user-facing result brief, not raw internal phase tables. |

## Last Release Validation

2026-05-21 local validation must pass with the gate commands above before publishing
to the Codex installed copy. This release intentionally targets
`~/.codex/skills/opc-delivery` only; Claude copies are out of scope unless explicitly
requested.
