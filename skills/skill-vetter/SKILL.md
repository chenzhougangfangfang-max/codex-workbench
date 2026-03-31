---
name: skill-vetter
description: Validate Codex skill folders for required structure and common mistakes. Use when creating or reviewing a local skill, checking whether a skill directory contains a valid SKILL.md, YAML frontmatter with name and description, optional agents metadata, or basic script/reference/assets layout.
---

# Skill Vetter

Validate local Codex skills before using or sharing them.

## When to use

- A user asks to review a skill folder
- A new skill was created and needs a quick structure check
- A skill is not loading and you need to inspect likely metadata problems

## What to validate

Check these items first:

1. `SKILL.md` exists at the skill root
2. `SKILL.md` starts with YAML frontmatter
3. Frontmatter contains non-empty `name` and `description`
4. Frontmatter `name` matches the directory name closely enough to be intentional
5. Optional folders such as `agents/`, `scripts/`, `references/`, and `assets/` are only checked for obvious issues

## Workflow

1. Run `scripts/check_skill.py <skill-dir>` for a quick validation pass
2. If the script reports warnings or errors, inspect the referenced files directly
3. When reviewing quality, keep the main focus on broken loading conditions first, then on lower-risk issues like naming drift or extra clutter

## Commands

```bash
python3 scripts/check_skill.py /path/to/skill
python3 scripts/check_skill.py /home/chengang/.codex/skills/skill-vetter
python3 scripts/check_skill.py --batch /home/chengang/.codex/skills
```

## Notes

- The script is intentionally strict about required fields and intentionally light on style opinions
- It prints `OK`, `WARN`, and `ERROR` lines so findings are easy to scan
- A non-zero exit code means at least one blocking problem was found
