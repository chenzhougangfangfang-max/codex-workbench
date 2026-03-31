# Google Calendar Cheatsheet

## Natural Language Prompts

- `帮我看今天的日历安排`
- `列出我今天的 Google Calendar 事件`
- `帮我看接下来 10 个日历事件`
- `创建日历事件：标题=和客户开会，开始=2026-04-01T09:00:00+08:00，结束=2026-04-01T10:00:00+08:00，描述=讨论需求`

## Commands

Unified entrypoint:

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/toolbox.py calendar today
python3 scripts/toolbox.py calendar day 明天
python3 scripts/toolbox.py calendar summary today
python3 scripts/toolbox.py calendar summary today --format feishu
python3 scripts/toolbox.py calendar summary today --format telegram
python3 scripts/toolbox.py calendar push today --channel feishu --user-id ou_xxx
python3 scripts/toolbox.py calendar push today --channel telegram --chat-id 123456789 --token "<bot_token>"
python3 scripts/toolbox.py digest today
python3 scripts/toolbox.py digest today --format feishu
python3 scripts/toolbox.py digest today --format telegram
python3 scripts/toolbox.py digest push today --channel feishu --user-id ou_xxx
python3 scripts/toolbox.py digest push today --channel feishu --user-id ou_xxx --user-id ou_yyy
python3 scripts/toolbox.py digest push today --channel telegram --chat-id 123456789 --token "<bot_token>"
python3 scripts/toolbox.py calendar list
python3 scripts/toolbox.py calendar list-ids
python3 scripts/toolbox.py calendar search "和客户开会"
python3 scripts/toolbox.py calendar update <event_id> --summary "新标题"
python3 scripts/toolbox.py calendar create \
  --summary "和客户开会" \
  --start "2026-04-01T09:00:00+08:00" \
  --end "2026-04-01T10:00:00+08:00" \
  --description "讨论需求"
python3 scripts/toolbox.py calendar create \
  --summary "和客户开会" \
  --date "2026-04-01" \
  --start-time "09:00" \
  --end-time "10:00" \
  --description "讨论需求"
python3 scripts/toolbox.py calendar create \
  --summary "和客户开会" \
  --relative-date "明天" \
  --start-time "09:00" \
  --end-time "10:00" \
  --description "讨论需求"
python3 scripts/toolbox.py calendar create \
  --summary "和客户开会" \
  --relative-date "明天" \
  --period "上午" \
  --start-time "09:00" \
  --end-time "10:00" \
  --description "讨论需求"
python3 scripts/toolbox.py calendar create \
  --summary "请假" \
  --relative-date "明天" \
  --all-day \
  --description "全天请假"
python3 scripts/toolbox.py calendar create-text "明天下午三点和客户开会，讨论需求"
python3 scripts/toolbox.py calendar delete <event_id>
```

Show today:

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/google-calendar/today_events.py
```

Show next 10 events:

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/google-calendar/list_events.py
```

Create an event:

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/google-calendar/create_event.py \
  --summary "和客户开会" \
  --start "2026-04-01T09:00:00+08:00" \
  --end "2026-04-01T10:00:00+08:00" \
  --description "讨论需求"
```

Create with date and time only:

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/google-calendar/create_event.py \
  --summary "和客户开会" \
  --date "2026-04-01" \
  --start-time "09:00" \
  --end-time "10:00" \
  --description "讨论需求"
```

Create with a relative Chinese date:

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/google-calendar/create_event.py \
  --summary "和客户开会" \
  --relative-date "明天" \
  --start-time "09:00" \
  --end-time "10:00" \
  --description "讨论需求"
```

Create with Chinese period label:

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/google-calendar/create_event.py \
  --summary "和客户开会" \
  --relative-date "明天" \
  --period "上午" \
  --start-time "09:00" \
  --end-time "10:00" \
  --description "讨论需求"
```

Create an all-day event:

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/google-calendar/create_event.py \
  --summary "请假" \
  --relative-date "明天" \
  --all-day \
  --description "全天请假"
```

Format summary output for messaging:

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/toolbox.py calendar summary today --format feishu
python3 scripts/toolbox.py calendar summary today --format telegram
```

Push today summary directly:

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/toolbox.py calendar push today --channel feishu --user-id ou_xxx
python3 scripts/toolbox.py calendar push today --channel telegram --chat-id 123456789 --token "<bot_token>"
```

Combine today calendar and news request:

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/toolbox.py digest today
python3 scripts/toolbox.py digest today --format feishu
python3 scripts/toolbox.py digest today --format telegram
```

Push combined digest directly:

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/toolbox.py digest push today --channel feishu --user-id ou_xxx
python3 scripts/toolbox.py digest push today --channel feishu --user-id ou_xxx --user-id ou_yyy
python3 scripts/toolbox.py digest push today --channel telegram --chat-id 123456789 --token "<bot_token>"
```

Telegram quick usage:

```bash
cd /home/chengang/桌面/codex-workbench
source .venv/bin/activate
python3 scripts/toolbox.py digest today --format telegram
python3 scripts/toolbox.py calendar summary today --format telegram
python3 scripts/toolbox.py digest push today --channel telegram --chat-id 8241532640 --token "<bot_token>"
python3 scripts/toolbox.py calendar push today --channel telegram --chat-id 8241532640 --token "<bot_token>"
```

Use TELEGRAM_BOT_TOKEN to shorten commands:

```bash
export TELEGRAM_BOT_TOKEN="<bot_token>"
python3 scripts/toolbox.py digest push today --channel telegram --chat-id 8241532640
python3 scripts/toolbox.py calendar push today --channel telegram --chat-id 8241532640
```

## Notes

- `credentials.json` and `token.json` are local only and ignored by Git
- Telegram push can also read `TELEGRAM_BOT_TOKEN` from the environment
- Telegram bots usually need you to send them a first message before push tests work
- Never paste a real Telegram bot token into chat; rotate it if it has been exposed
- Event listings now include Chinese lunar date annotations
- `digest today` 目前合并的是“今日日历摘要 + 今日新闻摘要请求模板”，新闻部分不是本地实时抓取结果
- Event times should use ISO format with timezone, for example:
  `2026-04-01T09:00:00+08:00`
