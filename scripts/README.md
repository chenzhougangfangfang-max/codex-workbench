## Scripts

Small local utilities used alongside the cheatsheets and skills.

### Included files

- `toolbox.py`: unified entrypoint for listing and validating skills
- `find-skills.py`: list installed system, user, and linked skills
- `google-calendar/`: local Google Calendar integration scaffold
- `skill-vetter/check_skill.py`: validate skill folders and optionally generate Markdown reports

### Examples

```bash
python3 scripts/toolbox.py list-skills
python3 scripts/toolbox.py vet-skill skills/skill-vetter
python3 scripts/toolbox.py calendar today
python3 scripts/toolbox.py calendar list
python3 scripts/toolbox.py calendar create --summary "Test event" --start "2026-04-01T09:00:00+08:00" --end "2026-04-01T10:00:00+08:00"
python3 scripts/find-skills.py
python3 scripts/skill-vetter/check_skill.py skills/skill-vetter
```
