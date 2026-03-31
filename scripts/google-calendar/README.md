# Google Calendar

Minimal Google Calendar integration for local desktop OAuth.

## What it does

- completes a one-time browser OAuth flow
- stores local auth in `token.json`
- lists the next 10 events from your primary calendar
- creates events in your primary calendar
- shows Chinese lunar dates alongside calendar views

## Setup

1. Go to Google Cloud Console and create a project or reuse one.
2. Enable the Google Calendar API.
3. Create OAuth client credentials for a Desktop app.
4. Download the JSON file and place it here as:

```text
scripts/google-calendar/credentials.json
```

## Install dependencies

```bash
cd /home/chengang/桌面/codex-workbench
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/google-calendar/requirements.txt
```

## First run

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/google-calendar/list_events.py
```

On first run it will open a browser window for Google authorization and then save:

```text
scripts/google-calendar/token.json
```

## Show today's events

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/google-calendar/today_events.py
```

## Notes

- `credentials.json` and `token.json` are ignored by Git.
- Current scope:
  `https://www.googleapis.com/auth/calendar`

## Create an event

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/google-calendar/create_event.py \
  --summary "Test event" \
  --start "2026-04-01T09:00:00+08:00" \
  --end "2026-04-01T10:00:00+08:00" \
  --description "Created from codex-workbench"
```
