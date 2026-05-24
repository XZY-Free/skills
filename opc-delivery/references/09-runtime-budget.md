# 09 — 执行期资源边界

把"世界压缩成证据回流给模型"作为一类规则统一处理。**这一条直接来自实际事故**: 跑 OPC 验证时多次出现 `Request too large (max 32MB)` 中断, 起因都是把多张高分截图或大段日志原样塞回单次 tool_result。

不读不写 reference 时, 永远默认 5MB 单次 tool_result 是安全区。

## 何时读

- 进入 verification / implementation 阶段, 即将截图或读长日志
- 一次要查看 2+ 张截图
- 跑了产生大量输出的命令(`npm test`、`build`、`tsc`、长 DSL/D2C 拉取)
- 感觉单次 request 可能超 5MB

## 目录

- [32MB 红线](#32mb-红线)
- [截图回流](#截图回流)
- [长日志回流](#长日志回流)
- [reference 读取节流](#reference-读取节流)
- [DSL / D2C 拉取](#dsl--d2c-拉取)
- [反模式](#反模式)

---

## 32MB 红线

Anthropic API 单次 request 上限是 **32MB**。这是 HTTP request 级别的, 跟上下文窗口大小无关——即使你有 1M 上下文还没用完, **一次 tool_result 里同时附带多张高分 PNG 也会让这次 HTTP request 超 32MB 被拒**。

经验值:

| 大小 | 状态 |
|---|---|
| 单次 tool_result < 5MB | 安全区 |
| 5MB-15MB | 黄区, 需评估 |
| 15MB-32MB | 红区, 容易撞顶 |
| > 32MB | 必中断 |

超过 5MB 就走"压缩 → 摘要 → 入证据目录"路径, **不要硬塞**。

## 截图回流

### 默认产两份产物

`screenshot.mjs` / Playwright 默认产:

- `foo.png` — 原图, 留证用, 写入 `.opc/verification/screenshots/`
- `foo-thumb.jpg` — ≤200KB, 给模型看用

> 在改 `screenshot.mjs` 之前, 临时方案是: 截图时显式用 `device_scale_factor=1` + `fullPage=false`, 单张控制在 ~500KB 以内。

### 模型查图规则

- **只 Read `*-thumb.jpg`, 不 Read 原图**
- **单 turn 最多 Read 1 张**
- 多张需要比对 → 先用 `ls -la screenshots/` 确认文件存在和大小, 决定哪一张值得看
- 多张确实都要看 → 拆到下一 turn

### 截图证据但不读图

实际上很多 turn 只需要知道"截图存在且大小合理", 不需要模型亲眼看。让 `verification-state.py record` 记录路径 + 文件大小 + 渲染状态即可。

### 32MB 事故复现示例

| 触发场景 | 后果 |
|---|---|
| `device_scale_factor=2` + `fullPage=true` 截 6 张 → Read 3 张 | 必撞顶 |
| 截了 1440×900 普通图 6 张(各 ~2MB) → 一次 Read 3 张 | 撞顶 |
| 跑完 typecheck + write 多个文件后 → 又 Read 3 张图 | 累计撞顶 |

## 长日志回流

`npm test` / `build` / `tsc` / `prisma migrate` 输出 > 100 行时:

```bash
# 看尾部错误
npm run test 2>&1 | tail -50

# 只看失败行
npm run test 2>&1 | grep -E "(FAIL|ERROR|✗)" | head -20

# typecheck 错误数 + 错误摘要
npx tsc --noEmit 2>&1 | tail -40
echo "exit=$?"
```

**不要**把整段日志当 tool_result 拉回。证据只需"通过/失败 + 关键行"。

如果命令本身在 background 跑(用 `run_in_background`), 完成时只读 tail, 不读全文。

## reference 读取节流

- **单 turn 最多 Read 1 个 reference**(除非 SKILL.md 显式指引并读)
- 实现 slice 时只读: SKILL.md + 当前 slice md + 06-implementation.md 的 anchor
- 不预防性 Read("以防万一先把这个文件加载进来"是反模式)
- reference 之间已有 anchor 链接, 需要时再跳

## DSL / D2C 拉取

- 整站根容器 DSL 偶尔 > 20MB 报 `Request too large` → 改成对每个子 Frame 单独 `getDsl`(见 [07-verification.md](07-verification.md#设计稿更新流))
- D2C HTML 一般 1-2MB, 单次拉取没问题
- 但**不要在同一 turn 里既拉 D2C 又 Read 截图**

## 反模式

- ❌ 截图后立即 `Read 3 files`(3 张高分 PNG 同 turn) — 必撞顶
- ❌ "我看一下截图效果" 之后无差别 Read 所有刚截的图
- ❌ 把 `npm test` 整段输出当 tool_result 拉回
- ❌ Read 5 个 reference 文件"做完整了解" — 不需要
- ❌ `device_scale_factor=2` + `fullPage=true` 当默认 — 高分图必然累计撞顶
- ❌ Read PDF 整个文档不指定 pages — 跟大图同性质问题

正模式:

- ✅ 截图后先 `ls -la screenshots/` 看文件存在 + 大小
- ✅ 真要看 → 读单张 thumb.jpg
- ✅ 长日志先 `tail -50` 或 `grep ERROR`
- ✅ 单 turn 内 Read reference 数量 ≤ 1
- ✅ 跑长测试用 `run_in_background`, 完成时只读 tail
