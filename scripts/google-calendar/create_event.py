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


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Google Calendar event in the primary calendar.")
    parser.add_argument("--summary", required=True, help="Event title")
    parser.add_argument("--start", required=True, help="Start datetime in ISO format")
    parser.add_argument("--end", required=True, help="End datetime in ISO format")
    parser.add_argument("--description", default="", help="Optional description")
    parser.add_argument("--location", default="", help="Optional location")
    args = parser.parse_args()

    creds = load_credentials()
    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": args.summary,
        "description": args.description,
        "location": args.location,
        "start": {"dateTime": parse_datetime(args.start)},
        "end": {"dateTime": parse_datetime(args.end)},
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
    print("Created event:")
    print(created.get("htmlLink", "(no link)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
