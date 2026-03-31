#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]
BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def load_credentials() -> Credentials:
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not CREDENTIALS_FILE.exists():
            raise SystemExit(
                "Missing credentials.json. Download OAuth desktop app credentials "
                "from Google Cloud Console and place them in scripts/google-calendar/."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
        creds = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Google Calendar event in the primary calendar.")
    parser.add_argument("--summary", required=True, help="Event title")
    parser.add_argument("--start", help="Start datetime in ISO format")
    parser.add_argument("--end", help="End datetime in ISO format")
    parser.add_argument("--date", help="Event date in YYYY-MM-DD")
    parser.add_argument("--relative-date", help="Relative date in Chinese: 今天, 明天, 后天")
    parser.add_argument("--period", help="Optional Chinese period label: 上午, 下午, 晚上")
    parser.add_argument("--start-time", help="Start time in HH:MM")
    parser.add_argument("--end-time", help="End time in HH:MM")
    parser.add_argument("--description", default="", help="Optional description")
    parser.add_argument("--location", default="", help="Optional location")
    args = parser.parse_args()

    if args.start and args.end:
        start_value = parse_datetime(args.start)
        end_value = parse_datetime(args.end)
    elif args.date and args.start_time and args.end_time:
        start_value = parse_local_datetime(args.date, normalize_time_label(args.period, args.start_time))
        end_value = parse_local_datetime(args.date, normalize_time_label(args.period, args.end_time))
    elif args.relative_date and args.start_time and args.end_time:
        resolved_date = parse_relative_date(args.relative_date)
        start_value = parse_local_datetime(resolved_date, normalize_time_label(args.period, args.start_time))
        end_value = parse_local_datetime(resolved_date, normalize_time_label(args.period, args.end_time))
    else:
        raise SystemExit(
            "Provide either --start/--end, --date/--start-time/--end-time, "
            "or --relative-date/--start-time/--end-time."
        )

    creds = load_credentials()
    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": args.summary,
        "description": args.description,
        "location": args.location,
        "start": {"dateTime": start_value},
        "end": {"dateTime": end_value},
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
    print("Created event:")
    print(created.get("htmlLink", "(no link)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
