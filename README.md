# codex-workbench

Personal AI tooling workspace for Codex, GitHub CLI, Feishu CLI, browser automation, and reusable prompt cheatsheets.

## What's inside

- `cheatsheets/`: quick references for daily tools and skills
- `scripts/`: small local utilities
- `docs/`: reports and supporting notes
- `skills/`: placeholders for custom skill indexes or future exports

## Current contents

### Cheatsheets

- `agent-browser-cheatsheet.md`
- `feishu-cli-cheatsheet.md`
- `github-cli-cheatsheet.md`
- `news-prompts-cheatsheet.md`
- `playwright-skill-cheatsheet.md`
- `top-10-skills-cheatsheet.md`

### Scripts

- `find-skills.py`: list installed Codex skills on this machine
- `scripts/skill-vetter/check_skill.py`: validate local skill folders and generate Markdown reports

### Docs

- `skill-vetter-report.md`: validation report for local user-installed skills

### Skills

- `skills/skill-vetter/SKILL.md`: local custom skill for validating Codex skill structure

## Quick start

Clone the repo:

```bash
git clone https://github.com/chenzhougangfangfang-max/codex-workbench.git
cd codex-workbench
```

Browse the quick references:

```bash
ls cheatsheets
```

Run the local skill listing utility:

```bash
python3 scripts/find-skills.py
```

## Purpose

This repository is intended to keep together:

- reusable AI workflows
- local tool notes
- CLI usage references
- custom skill validation utilities

It is a lightweight workbench rather than a packaged application.
