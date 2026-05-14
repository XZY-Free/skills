# Contributing

Thanks for considering a contribution to this skills collection — whether it's a typo fix, an issue report, or a brand new skill, all are welcome.

**English** · [简体中文](CONTRIBUTING.md)

---

## What contributions are welcome

In priority order:

| Priority | Type | How to propose |
|---|---|---|
| ⭐⭐⭐ | **A new skill** | First file an issue using the [feature template](.github/ISSUE_TEMPLATE/feature_request.yml) describing the use case; open a PR after consensus |
| ⭐⭐⭐ | **Eval / forward-test additions** | Reference [`opc-delivery/evals/forward-tests.md`](opc-delivery/evals/forward-tests.md) — go straight to PR |
| ⭐⭐ | **Bug fixes + doc typos** | Small ones can go straight to PR; behavior-changing fixes should start with an issue |
| ⭐⭐ | **New references for existing skills** (troubleshooting, new scenarios) | Direct PR — describe the scenario in the PR body |
| ⭐ | **SVG / image polish** | Direct PR, but please keep the existing color palette consistent |

## Workflow

### 1. Fork + clone

```bash
gh repo fork <repo-url> --clone
cd skills
```

### 2. Create a branch

```bash
git checkout -b feat/<short-name>      # New feature
git checkout -b fix/<short-name>       # Bug fix
git checkout -b docs/<short-name>      # Docs only
git checkout -b skill/<skill-name>     # New skill
```

### 3. Verify locally (try to pass before opening PR)

```bash
# Are all SVGs valid XML?
python3 -c "import xml.etree.ElementTree as ET; \
  [ET.parse(f) for f in __import__('glob').glob('**/*.svg', recursive=True)]; \
  print('All SVGs OK')"

# Is SKILL.md frontmatter valid?
for f in */SKILL.md; do
  head -5 "$f" | grep -q '^name:' || echo "missing name: $f"
done

# Are internal doc links alive?
python3 scripts/check-links.py     # (lands with the D item CI)
```

### 4. Commit + push

See "Commit conventions" below.

### 5. Open the PR

Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md) and describe how you tested.

---

## Skill structure conventions

Each skill is a subdirectory at the repo root:

```
<skill-name>/
├── SKILL.md            # ⚠️ Required, entry, complete workflow definition
├── agents/
│   └── openai.yaml     # Recommended, UI metadata
├── references/         # Recommended, on-demand guides
│   └── *.md
├── scripts/            # Optional, deterministic checks / transforms
├── evals/
│   └── evals.json      # Required, eval cases
└── assets/             # Optional, runtime templates / resources
```

### SKILL.md frontmatter rules

```yaml
---
name: <skill-name>         # Required, kebab-case, matches directory name
description: |              # Required, trigger description + keyword list
  What this skill handles.
  Trigger keywords: keyword 1, keyword 2, ...
---
```

`description` is what the agent uses to decide whether to invoke the skill. **The more specific the trigger keywords, the lower the false-positive rate.**

### References file naming

- Name by verb or scenario (`troubleshooting.md`, `api-wiring.md`), not by abstract category (`utils.md`, `misc.md`)
- Every reference file should be registered in SKILL.md's "when to read" table at the bottom

---

## Commit conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/) lightly (scope is optional):

```
<type>: <short description>

<optional body explaining why>
```

`type`:

- `feat`: New feature / new skill / new reference section
- `fix`: Bug fix
- `docs`: Docs only
- `refactor`: Refactor, no behavior change
- `test`: Add / modify tests / evals
- `chore`: Misc (CI / deps / repo metadata)
- `example`: Add / modify examples

Examples:

```
feat: add update-flow.md for incremental design sync

  Addresses user reports that incremental re-fetch after design
  changes was unclear. Adds update-flow.md and wires it into
  SKILL.md phase 4.
```

```
fix: correct broken anchor link in README.md acknowledgments badge
```

```
example: add e-commerce-detail walkthrough
```

---

## PR flow

1. **Small** (single file, doc typo) → straight to PR
2. **Medium** (multiple files within one skill, new reference) → clear PR title, attach local verification output in body
3. **Large** (new skill, cross-skill refactor) → file an issue first, reach consensus before opening PR

### Review criteria

- Doesn't break existing skill behavior (evals.json wasn't silently changed)
- SKILL.md frontmatter is valid
- References cross-links are complete (newly added docs are registered in SKILL.md)
- No `.env`, no tokens, no real fileIds, no internal URLs committed
- All internal README links work

### How long

- Small PRs: first response within 24 hours
- Medium / Large PRs: first response within 72 hours
- Slower around holidays

---

## Code of Conduct

One rule: **be professional, address the issue, not the person**.

- Back up claims with evidence (code snippets, logs, official doc links)
- Don't disparage someone's skills or experience in issues / PRs
- Skills are engineering artifacts, not personal showcases — **evidence over opinion**

We follow the spirit of the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Report violations to maintainers via email.

---

## What we don't accept

- ❌ Forking, renaming, and re-publishing this skill as if it were yours (violates the license's attribution clause)
- ❌ Using real production data / customer names / internal URLs in examples
- ❌ Hardcoding any account / token / internal address into a skill
- ❌ Adding dependencies on paid cloud services (the core promise of this repo is local zero-lock-in)
- ❌ Softening SKILL.md's hard rules ("check docs before guessing", "evidence before completion") — these are the brand; **don't dilute them to appease newcomers**

---

## A note on writing style inside skills

Skills are read by AI agents, not by humans. So:

- **Give directives, not narration**: "First curl the official docs" rather than "you might want to check the official docs first"
- **State conditions, not soft suggestions**: "If the user-provided URL has no layer_id, then X" rather than "usually the user gives a full URL"
- **Be concrete with examples**: `curl -sL https://...` rather than "use curl"
- **Mix Chinese with technical English terms**: `layerId / D2C / DSL`-style API terms stay in English

See [`opc-delivery/SKILL.md`](opc-delivery/SKILL.md) as the style baseline.

---

## Questions / help

- Bug → [bug template](.github/ISSUE_TEMPLATE/bug_report.yml)
- MCP error → [MCP error template](.github/ISSUE_TEMPLATE/mcp_error.yml)
- Usage discussion / roadmap suggestions → GitHub Discussions
- Security issues → see [SECURITY.md](SECURITY.md)

Looking forward to your PR :)
