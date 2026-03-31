## Scripts

Small local utilities used alongside the cheatsheets and skills.

### Included files

- `toolbox.py`: unified entrypoint for listing and validating skills
- `find-skills.py`: list installed system, user, and linked skills
- `skill-vetter/check_skill.py`: validate skill folders and optionally generate Markdown reports

### Examples

```bash
python3 scripts/toolbox.py list-skills
python3 scripts/toolbox.py vet-skill skills/skill-vetter
python3 scripts/find-skills.py
python3 scripts/skill-vetter/check_skill.py skills/skill-vetter
```
