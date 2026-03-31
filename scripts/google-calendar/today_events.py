#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from lunardate import LunarDate


SCOPES = ["https://www.googleapis.com/auth/calendar"]
BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


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


def main() -> int:
    creds = load_credentials()
    service = build("calendar", "v3", credentials=creds)

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


if __name__ == "__main__":
    raise SystemExit(main())
