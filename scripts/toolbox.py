#!/usr/bin/env python3
import argparse
import datetime as dt
import re
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from lunardate import LunarDate


SYSTEM_ROOT = Path("/home/chengang/.codex/skills/.system")
USER_ROOT = Path("/home/chengang/.codex/skills")
AGENTS_ROOT = Path("/home/chengang/.agents/skills")
CALENDAR_DIR = Path("/home/chengang/桌面/codex-workbench/scripts/google-calendar")
CALENDAR_CREDENTIALS_FILE = CALENDAR_DIR / "credentials.json"
CALENDAR_TOKEN_FILE = CALENDAR_DIR / "token.json"
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]


def has_skill_md(path: Path) -> bool:
    return (path / "SKILL.md").is_file()


def list_dirs(root: Path):
    if not root.exists() or not root.is_dir():
        return []
    return sorted([p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")], key=lambda p: p.name)


def collect_system_skills():
    return [p for p in list_dirs(SYSTEM_ROOT) if has_skill_md(p)]


def collect_user_skills():
    return [p for p in list_dirs(USER_ROOT) if has_skill_md(p)]


def collect_agent_linked_skills():
    skills = []
    for entry in list_dirs(AGENTS_ROOT):
        if entry.is_symlink():
            target = entry.resolve()
            for child in list_dirs(target):
                if has_skill_md(child):
                    skills.append((entry.name, child))
    return skills


def print_section(title: str, items):
    print(title)
    if not items:
        print("- (none)")
        print()
        return
    for item in items:
        print(f"- {item}")
    print()


def list_skills(args) -> int:
    system_skills = [p.name for p in collect_system_skills()]
    user_skills = [p.name for p in collect_user_skills()]
    agent_skills = [f"{source}:{skill.name}" for source, skill in collect_agent_linked_skills()]

    if args.flat:
        for name in system_skills + user_skills + agent_skills:
            print(name)
        return 0

    print_section("System Skills", system_skills)
    print_section("User Skills", user_skills)
    print_section("Agent-linked Skills", agent_skills)
    return 0


def parse_frontmatter(text: str):
    if not text.startswith("---\n"):
        return None, "SKILL.md must start with YAML frontmatter"
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return None, "SKILL.md frontmatter is not closed with ---"
    return parts[0][4:], None


def extract_key(frontmatter: str, key: str):
    pattern = re.compile(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$")
    match = pattern.search(frontmatter)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
        value = value[1:-1]
    return value.strip()


def collect_skill_result(root: Path):
    errors = []
    warnings = []
    oks = []

    if not root.exists():
        errors.append(f"skill directory not found: {root}")
        return {"path": str(root), "ok": oks, "warn": warnings, "error": errors}
    if not root.is_dir():
        errors.append(f"path is not a directory: {root}")
        return {"path": str(root), "ok": oks, "warn": warnings, "error": errors}

    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        errors.append("missing SKILL.md at skill root")
    else:
        oks.append("SKILL.md exists")
        text = skill_md.read_text(encoding="utf-8")
        frontmatter, frontmatter_error = parse_frontmatter(text)
        if frontmatter_error:
            errors.append(frontmatter_error)
        else:
            oks.append("frontmatter detected")
            name = extract_key(frontmatter, "name")
            description = extract_key(frontmatter, "description")
            if not name:
                errors.append("frontmatter missing required name")
            else:
                oks.append(f"name: {name}")
                if name != root.name:
                    warnings.append(f"frontmatter name '{name}' differs from directory name '{root.name}'")
                if not re.fullmatch(r"[a-z0-9-]{1,63}", name):
                    warnings.append("name should usually use lowercase letters, digits, and hyphens only")
            if not description:
                errors.append("frontmatter missing required description")
            else:
                oks.append("description present")

    for folder in ("agents", "scripts", "references", "assets"):
        p = root / folder
        if p.exists():
            if p.is_dir():
                oks.append(f"optional folder present: {folder}/")
            else:
                warnings.append(f"{folder} exists but is not a directory")

    readme = root / "README.md"
    if readme.exists():
        warnings.append("README.md found; most skills should keep guidance inside SKILL.md or bundled references")

    return {
        "path": str(root),
        "ok": oks,
        "warn": warnings,
        "error": errors,
    }


def print_skill_result(result: dict) -> int:
    for line in result["ok"]:
        print(f"OK: {line}")
    for line in result["warn"]:
        print(f"WARN: {line}")
    for line in result["error"]:
        print(f"ERROR: {line}")
    return 1 if result["error"] else 0


def write_report(path: Path, results: list[dict]) -> None:
    lines = ["# Skill Vetter Report", ""]
    for result in results:
        status = "FAIL" if result["error"] else "PASS"
        lines.append(f"## {result['path']}")
        lines.append("")
        lines.append(f"- Status: `{status}`")
        lines.append(f"- OK: `{len(result['ok'])}`")
        lines.append(f"- Warnings: `{len(result['warn'])}`")
        lines.append(f"- Errors: `{len(result['error'])}`")
        lines.append("")
        if result["ok"]:
            lines.append("### OK")
            lines.append("")
            for item in result["ok"]:
                lines.append(f"- {item}")
            lines.append("")
        if result["warn"]:
            lines.append("### Warnings")
            lines.append("")
            for item in result["warn"]:
                lines.append(f"- {item}")
            lines.append("")
        if result["error"]:
            lines.append("### Errors")
            lines.append("")
            for item in result["error"]:
                lines.append(f"- {item}")
            lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def iter_skills(root: Path):
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            continue
        yield child


def vet_skill(args) -> int:
    root = Path(args.path).expanduser().resolve()
    if not args.batch:
        result = collect_skill_result(root)
        exit_code = print_skill_result(result)
        if args.report:
            write_report(Path(args.report).expanduser().resolve(), [result])
        return exit_code

    if not root.exists():
        print(f"ERROR: directory not found: {root}")
        return 1
    if not root.is_dir():
        print(f"ERROR: path is not a directory: {root}")
        return 1

    any_failures = False
    checked = 0
    results = []
    for skill_dir in iter_skills(root):
        checked += 1
        print(f"== {skill_dir} ==")
        result = collect_skill_result(skill_dir)
        results.append(result)
        exit_code = print_skill_result(result)
        if exit_code != 0:
            any_failures = True
        print()

    if checked == 0:
        print(f"WARN: no skill directories found under {root}")
        return 0

    if args.report:
        write_report(Path(args.report).expanduser().resolve(), results)

    return 1 if any_failures else 0


def load_calendar_credentials() -> Credentials:
    creds = None
    if CALENDAR_TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(CALENDAR_TOKEN_FILE), CALENDAR_SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not CALENDAR_CREDENTIALS_FILE.exists():
            raise SystemExit(
                "Missing credentials.json. Place it in scripts/google-calendar/ before using calendar commands."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(CALENDAR_CREDENTIALS_FILE), CALENDAR_SCOPES)
        creds = flow.run_local_server(port=0)

    CALENDAR_TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


def calendar_service():
    return build("calendar", "v3", credentials=load_calendar_credentials())


def format_lunar(date_obj: dt.date) -> str:
    lunar = LunarDate.fromSolarDate(date_obj.year, date_obj.month, date_obj.day)
    leap = " leap" if lunar.isLeapMonth else ""
    return f"Lunar {lunar.year}-{lunar.month:02d}-{lunar.day:02d}{leap}"


def parse_event_date(event: dict) -> dt.date | None:
    start = event.get("start", {})
    if "dateTime" in start:
        return dt.datetime.fromisoformat(start["dateTime"]).date()
    if "date" in start:
        return dt.date.fromisoformat(start["date"])
    return None


def calendar_list(_: argparse.Namespace) -> int:
    service = calendar_service()
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
        return 0

    for idx, event in enumerate(events, 1):
        start = event["start"].get("dateTime", event["start"].get("date"))
        summary = event.get("summary", "(no title)")
        event_date = parse_event_date(event)
        lunar_text = f"  [{format_lunar(event_date)}]" if event_date else ""
        print(f"{idx}. {start}  {summary}{lunar_text}")
    return 0


def calendar_today(_: argparse.Namespace) -> int:
    service = calendar_service()
    local_now = dt.datetime.now().astimezone()
    start_of_day = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + dt.timedelta(days=1)

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        print("No events scheduled for today.")
        return 0

    print(f"Today's events ({start_of_day.date()}, {format_lunar(start_of_day.date())}):")
    for idx, event in enumerate(events, 1):
        start = event["start"].get("dateTime", event["start"].get("date"))
        summary = event.get("summary", "(no title)")
        event_date = parse_event_date(event)
        lunar_text = f"  [{format_lunar(event_date)}]" if event_date else ""
        print(f"{idx}. {start}  {summary}{lunar_text}")
    return 0


def resolve_relative_date(label: str) -> dt.date:
    today = dt.date.today()
    mapping = {
        "今天": today,
        "明天": today + dt.timedelta(days=1),
        "后天": today + dt.timedelta(days=2),
    }
    if label not in mapping:
        raise SystemExit("Relative date must be one of: 今天, 明天, 后天")
    return mapping[label]


def calendar_day(args: argparse.Namespace) -> int:
    service = calendar_service()
    target_date = resolve_relative_date(args.relative_date)
    local_tz = dt.datetime.now().astimezone().tzinfo
    start_of_day = dt.datetime.combine(target_date, dt.time.min, tzinfo=local_tz)
    end_of_day = start_of_day + dt.timedelta(days=1)

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        print(f"No events scheduled for {args.relative_date}.")
        return 0

    print(f"{args.relative_date}的事件 ({target_date}, {format_lunar(target_date)}):")
    for idx, event in enumerate(events, 1):
        start = event["start"].get("dateTime", event["start"].get("date"))
        summary = event.get("summary", "(no title)")
        event_date = parse_event_date(event)
        lunar_text = f"  [{format_lunar(event_date)}]" if event_date else ""
        print(f"{idx}. {start}  {summary}{lunar_text}")
    return 0


def parse_datetime(value: str) -> str:
    try:
        return dt.datetime.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise SystemExit("Datetime must use ISO format like 2026-04-01T09:00:00+08:00") from exc


def parse_local_datetime(date_text: str, time_text: str) -> str:
    try:
        date_part = dt.date.fromisoformat(date_text)
        time_part = dt.time.fromisoformat(time_text)
    except ValueError as exc:
        raise SystemExit("Date/time must use values such as 2026-04-01 and 09:00") from exc
    local_tz = dt.datetime.now().astimezone().tzinfo
    return dt.datetime.combine(date_part, time_part, tzinfo=local_tz).isoformat()


def parse_relative_date(label: str) -> str:
    today = dt.date.today()
    mapping = {
        "今天": today,
        "明天": today + dt.timedelta(days=1),
        "后天": today + dt.timedelta(days=2),
    }
    if label not in mapping:
        raise SystemExit("Relative date must be one of: 今天, 明天, 后天")
    return mapping[label].isoformat()


def normalize_time_label(period: str | None, time_text: str) -> str:
    if not period:
        return time_text
    try:
        hour_str, minute_str = time_text.split(":", 1)
        hour = int(hour_str)
        minute = int(minute_str)
    except ValueError as exc:
        raise SystemExit("Time must use HH:MM format") from exc

    if period == "上午":
        if hour == 12:
            hour = 0
    elif period in ("下午", "晚上"):
        if 1 <= hour <= 11:
            hour += 12
    else:
        raise SystemExit("Period must be one of: 上午, 下午, 晚上")

    return f"{hour:02d}:{minute:02d}"


def calendar_create(args: argparse.Namespace) -> int:
    service = calendar_service()
    if args.all_day and args.date:
        start_value = args.date
        end_value = (dt.date.fromisoformat(args.date) + dt.timedelta(days=1)).isoformat()
        event_start = {"date": start_value}
        event_end = {"date": end_value}
    elif args.all_day and args.relative_date:
        resolved_date = parse_relative_date(args.relative_date)
        start_value = resolved_date
        end_value = (dt.date.fromisoformat(resolved_date) + dt.timedelta(days=1)).isoformat()
        event_start = {"date": start_value}
        event_end = {"date": end_value}
    elif args.start and args.end:
        start_value = parse_datetime(args.start)
        end_value = parse_datetime(args.end)
        event_start = {"dateTime": start_value}
        event_end = {"dateTime": end_value}
    elif args.date and args.start_time and args.end_time:
        start_value = parse_local_datetime(args.date, normalize_time_label(args.period, args.start_time))
        end_value = parse_local_datetime(args.date, normalize_time_label(args.period, args.end_time))
        event_start = {"dateTime": start_value}
        event_end = {"dateTime": end_value}
    elif args.relative_date and args.start_time and args.end_time:
        resolved_date = parse_relative_date(args.relative_date)
        start_value = parse_local_datetime(resolved_date, normalize_time_label(args.period, args.start_time))
        end_value = parse_local_datetime(resolved_date, normalize_time_label(args.period, args.end_time))
        event_start = {"dateTime": start_value}
        event_end = {"dateTime": end_value}
    else:
        raise SystemExit(
            "Provide either --all-day with --date/--relative-date, "
            "--start/--end, --date/--start-time/--end-time, "
            "or --relative-date/--start-time/--end-time."
        )
    event = {
        "summary": args.summary,
        "description": args.description,
        "location": args.location,
        "start": event_start,
        "end": event_end,
    }
    created = service.events().insert(calendarId="primary", body=event).execute()
    print("Created event:")
    print(created.get("htmlLink", "(no link)"))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Unified toolbox entrypoint for local Codex utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-skills", help="List installed Codex skills on this machine.")
    list_parser.add_argument("--flat", action="store_true", help="Print a flat list without sections.")
    list_parser.set_defaults(func=list_skills)

    vet_parser = subparsers.add_parser("vet-skill", help="Validate Codex skill folders.")
    vet_parser.add_argument("path", help="Path to a skill directory or a parent directory containing skill folders.")
    vet_parser.add_argument("--batch", action="store_true", help="Treat path as a directory containing many skill folders.")
    vet_parser.add_argument("--report", help="Write a Markdown report to this file path.")
    vet_parser.set_defaults(func=vet_skill)

    calendar_parser = subparsers.add_parser("calendar", help="Google Calendar utilities.")
    calendar_subparsers = calendar_parser.add_subparsers(dest="calendar_command", required=True)

    calendar_list_parser = calendar_subparsers.add_parser("list", help="List the next 10 calendar events.")
    calendar_list_parser.set_defaults(func=calendar_list)

    calendar_today_parser = calendar_subparsers.add_parser("today", help="List today's calendar events.")
    calendar_today_parser.set_defaults(func=calendar_today)

    calendar_day_parser = calendar_subparsers.add_parser("day", help="List events for 今天/明天/后天.")
    calendar_day_parser.add_argument("relative_date", help="One of: 今天, 明天, 后天")
    calendar_day_parser.set_defaults(func=calendar_day)

    calendar_create_parser = calendar_subparsers.add_parser("create", help="Create a calendar event.")
    calendar_create_parser.add_argument("--summary", required=True, help="Event title")
    calendar_create_parser.add_argument("--start", help="Start datetime in ISO format")
    calendar_create_parser.add_argument("--end", help="End datetime in ISO format")
    calendar_create_parser.add_argument("--date", help="Event date in YYYY-MM-DD")
    calendar_create_parser.add_argument("--relative-date", help="Relative date in Chinese: 今天, 明天, 后天")
    calendar_create_parser.add_argument("--period", help="Optional Chinese period label: 上午, 下午, 晚上")
    calendar_create_parser.add_argument("--start-time", help="Start time in HH:MM")
    calendar_create_parser.add_argument("--end-time", help="End time in HH:MM")
    calendar_create_parser.add_argument("--all-day", action="store_true", help="Create an all-day event")
    calendar_create_parser.add_argument("--description", default="", help="Optional description")
    calendar_create_parser.add_argument("--location", default="", help="Optional location")
    calendar_create_parser.set_defaults(func=calendar_create)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
