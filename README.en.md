<div align="center">

# 🧰 Skills

**A collection of reusable markdown skills for AI coding agents**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Maintainer](https://img.shields.io/badge/maintained_by-CR_Snow_AI_Team-DC2626.svg)](#acknowledgments)
[![Skills](https://img.shields.io/badge/Skills-2-7C3AED.svg)](#skills-included)

[简体中文](README.md) · **English**

</div>

---

## What is this

A repository that consolidates everyday workflows, domain knowledge, and external-platform integrations into reusable [markdown skills](https://docs.claude.com/en/docs/claude-code/skills). Each skill is a self-contained subdirectory that drops into any compatible AI coding agent — [Claude Code](https://docs.claude.com/en/docs/claude-code/quickstart) · [Codex CLI](https://github.com/openai/codex) · [Cursor](https://cursor.com) · other markdown skill loaders.

Skills are markdown files plus supporting assets (references / evals / assets) — no cloud services, no IDE lock-in, no subscriptions. **Copy-paste and go.**

> 🌱 **Good skills are welcome here.** See "Contributing new skills" below.

## Skills Included

| Skill | One-liner | Entry |
|---|---|---|
| 🚀 **opc-delivery** | Turn a one-line business idea into a real page that runs, with plan / QA / deploy evidence | [SKILL.md](opc-delivery/SKILL.md) |
| 🎞️ **webdeck** | Build presentation decks in HTML (training / reporting / sharing), tuned to *not look AI-made*, with a companion speaker script, exportable to editable PPT | [SKILL.md](webdeck/SKILL.md) |

> 2 skills so far. More to come — naming convention below.

### Learn about opc-delivery

Two entry points walk through how it pushes a one-line request to a shippable product:

- 🌐 **Landing page** — <http://119.45.222.120/plans/>, an 8-slide narrative: what it is, who uses it, what it produces, how to talk to it, how it runs, where it stops, product polish, and recap
- 📖 **Solution doc** — <http://119.45.222.120/plans/doc>, four core design ideas + a 7-stage flow + stop-the-line boundaries + how-to-roll-out / adoption metrics

For the skill source, see [`opc-delivery/SKILL.md`](opc-delivery/SKILL.md) and [`opc-delivery/references/`](opc-delivery/references/).

## Generic Install

Each skill keeps its operational guidance in `SKILL.md` and `references/`; the common install pattern is:

```bash
# 1. Clone this repo
git clone <repo-url> skills && cd skills

# 2. Copy the skill you want into your agent's skills directory
#    Claude Code:
cp -r <skill-name> ~/.claude/skills/
#    Codex CLI:
cp -r <skill-name> ~/.codex/skills/
#    Cursor / others: see your agent's docs

# 3. Restart the agent session so it discovers the new skill
```

If a skill needs additional MCPs / tokens / config, see its `SKILL.md` or setup reference.

## Contributing New Skills

New skills are welcome. Each skill is a `<skill-name>/` subdirectory containing at least:

```
<skill-name>/
├── SKILL.md            # Entry; frontmatter with name + description + trigger keywords
├── agents/
│   └── openai.yaml     # Recommended, UI metadata
├── references/         # On-demand guides (keeps context window small)
│   └── *.md
├── scripts/            # Optional deterministic checks / transforms
├── evals/
│   └── evals.json      # Eval cases
└── assets/             # Optional runtime templates / resources
```

Use `opc-delivery/` as a complete reference. Detailed contribution workflow, SKILL.md spec, commit / PR conventions are in [`CONTRIBUTING.en.md`](CONTRIBUTING.en.md).

Quick entry points:

- **MCP / skill errors** → file an issue using the [MCP error template](.github/ISSUE_TEMPLATE/mcp_error.yml)
- **New skill proposal** → use the [feature template](.github/ISSUE_TEMPLATE/feature_request.yml) to discuss the use case first
- **PRs** → see the [PR template](.github/PULL_REQUEST_TEMPLATE.md), describe how you tested

## Repository Layout

```
.
├── README.md / README.en.md     # This file: skills index
├── LICENSE                       # Apache-2.0
├── SECURITY.md                   # Shared security policy (token handling, etc.)
├── CLAUDE.md                     # Repo-level hint for Claude Code
├── .github/                      # Issue / PR templates
├── opc-delivery/                 # skill: idea → shipped, full delivery
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   ├── evals/
│   └── scripts/
└── webdeck/                      # skill: presentation decks in HTML
    ├── SKILL.md
    ├── references/
    ├── assets/                   # scaffold
    └── scripts/                  # screenshot self-check
```

## Security

Skills that handle tokens or credentials share one [`SECURITY.md`](SECURITY.md) policy: stored locally, never reused, never committed to VCS, redacted on echo.

## License

[Apache License 2.0](LICENSE)

## Acknowledgments

- **CR Snow Beer Digital & AI Team** (华润雪花啤酒智数 AI 团队) — resource & operational support
- [Anthropic](https://www.anthropic.com) — for proposing the [Skills spec](https://docs.claude.com/en/docs/claude-code/skills)
- Everyone filing issues, opening PRs, and sharing use cases — you shape what lands in v0.2 and beyond
