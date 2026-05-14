# Scripts

仓库的本地校验 + CI 用脚本。所有脚本设计成 **本地能跑、CI 也能跑**,失败时非 0 退出。

| 脚本 | 用途 |
|---|---|
| [`check-links.py`](check-links.py) | 校验 markdown 文档内部链接 + 图片路径都活着 |
| [`check-svgs.py`](check-svgs.py) | 校验所有 SVG 文件是合法 XML |
| [`check-skill-frontmatter.py`](check-skill-frontmatter.py) | 校验每个 `*/SKILL.md` 的 frontmatter 含 name + description |
| [`check-evals.py`](check-evals.py) | 校验每个 `*/evals/evals.json` schema 正确 |
| [`run-evals.py`](run-evals.py) | 从某 skill 的 `evals.json` 生成 `BENCHMARK.md` 骨架,由维护者手动跑 eval 后填实测数据 |

## 本地一次性跑全部

```bash
python3 scripts/check-links.py && \
python3 scripts/check-svgs.py && \
python3 scripts/check-skill-frontmatter.py && \
python3 scripts/check-evals.py && \
echo "✅ All checks passed"
```

CI 上跑的就是这四个脚本。`run-evals.py` 不在 CI 里(因为它需要真 token + 真 MCP),由维护者手动跑:

```bash
python3 scripts/run-evals.py opc-delivery --write    # 生成 opc-delivery/BENCHMARK.md 骨架
# 然后人工跑每个 eval case,把结果填进 BENCHMARK.md 提交
```

## 写新脚本的约定

- 单文件 Python(尽量只用标准库,避免 pip install)
- 退出码:`0` = 通过,`1` = 校验失败,`2` = 脚本本身出错(异常)
- 输出格式:每行一条 `<status> <file>: <msg>`,失败行以 `✗` 开头,通过以 `✓` 开头
- 跑成功最后一行打 `✅ <check-name> OK`
