"""google_calendar.py — Google Calendar integration via Google API."""
from __future__ import annotations
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pathlib import Path
from datetime import datetime, timedelta
import json

SCOPES = ["https://www.googleapis.com/auth/calendar"]
_TOKEN_DIR = Path(__file__).resolve().parent.parent / "config"
_TOKEN_FILE = _TOKEN_DIR / "calendar_token.json"
_CREDS_FILE = _TOKEN_DIR / "gmail_credentials.json"


def _get_service():
    creds = None
    if _TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(_TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not _CREDS_FILE.exists():
                return None, "No hay gmail_credentials.json en config/."
            flow = InstalledAppFlow.from_client_secrets_file(str(_CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        _TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        _TOKEN_FILE.write_text(creds.to_json())
    service = build("calendar", "v3", credentials=creds)
    return service, None


def _parse_dt(s: str):
    formats = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%d"]
    for f in formats:
        try:
            return datetime.strptime(s, f).isoformat()
        except ValueError:
            continue
    return datetime.now().isoformat()


def google_calendar(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = parameters.get("action", "list")

    service, err = _get_service()
    if err:
        return err

    try:
        if action == "list":
            days = parameters.get("days_ahead", 7)
            now = datetime.utcnow()
            end = now + timedelta(days=days)
            events = service.events().list(
                calendarId="primary",
                timeMin=now.isoformat() + "Z",
                timeMax=end.isoformat() + "Z",
                singleEvents=True,
                orderBy="startTime",
                maxResults=20
            ).execute()
            items = events.get("items", [])
            if not items:
                return f"No hay eventos en los próximos {days} días."
            output = []
            for e in items:
                start = e["start"].get("dateTime", e["start"].get("date", "?"))
                output.append(f"- {start}: {e.get('summary','?')}")
            return "Próximos eventos:\n" + "\n".join(output)

        elif action == "create":
            summary = parameters.get("summary", "Evento")
            start_str = parameters.get("start", "")
            end_str = parameters.get("end", "")
            desc = parameters.get("description", "")
            location = parameters.get("location", "")
            if not start_str:
                return "Falta start (fecha/hora de inicio)."
            start_dt = _parse_dt(start_str)
            end_dt = _parse_dt(end_str) if end_str else (
                (datetime.fromisoformat(start_dt) + timedelta(hours=1)).isoformat()
            )
            event = {
                "summary": summary,
                "description": desc,
                "location": location,
                "start": {"dateTime": start_dt, "timeZone": "UTC"},
                "end": {"dateTime": end_dt, "timeZone": "UTC"},
            }
            created = service.events().insert(calendarId="primary", body=event).execute()
            return f"Evento creado: {created.get('htmlLink', summary)}"

        elif action == "edit":
            event_id = parameters.get("event_id", "")
            summary = parameters.get("summary", "")
            event = service.events().get(calendarId="primary", eventId=event_id).execute()
            if summary:
                event["summary"] = summary
            service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
            return "Evento actualizado."

        elif action == "delete":
            event_id = parameters.get("event_id", "")
            service.events().delete(calendarId="primary", eventId=event_id).execute()
            return "Evento eliminado."

        return f"Calendar action '{action}' completado."
    except Exception as e:
        return f"Error: {e}"
