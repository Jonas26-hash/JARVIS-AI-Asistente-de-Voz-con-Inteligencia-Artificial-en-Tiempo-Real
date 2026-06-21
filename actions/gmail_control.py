"""gmail_control.py — Gmail integration via Google API."""
from __future__ import annotations
import os, base64, json
from pathlib import Path
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
_TOKEN_DIR = Path(__file__).resolve().parent.parent / "config"
_TOKEN_FILE = _TOKEN_DIR / "gmail_token.json"
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
                return None, "No hay gmail_credentials.json en config/. Creá un proyecto en Google Cloud Console y descargá las credenciales."
            flow = InstalledAppFlow.from_client_secrets_file(str(_CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        _TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        _TOKEN_FILE.write_text(creds.to_json())
    service = build("gmail", "v1", credentials=creds)
    return service, None


def gmail_control(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = parameters.get("action", "inbox")
    count = parameters.get("count", 5)

    service, err = _get_service()
    if err:
        return err

    try:
        if action == "inbox":
            results = service.users().messages().list(userId="me", maxResults=count, q="in:inbox").execute()
            messages = results.get("messages", [])
            if not messages:
                return "No hay correos en la bandeja de entrada."
            output = []
            for msg in messages[:count]:
                m = service.users().messages().get(userId="me", id=msg["id"], format="metadata", metadataHeaders=["From", "Subject", "Date"]).execute()
                headers = {h["name"]: h["value"] for h in m["payload"]["headers"]}
                output.append(f"- {headers.get('From','?')}: {headers.get('Subject','?')}")
            return "Bandeja de entrada:\n" + "\n".join(output)

        elif action == "send":
            to = parameters.get("to", "")
            subject = parameters.get("subject", "")
            body = parameters.get("body", "")
            if not to:
                return "Falta destinatario (to)."
            msg = MIMEText(body)
            msg["To"] = to
            msg["Subject"] = subject or "Sin asunto"
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            service.users().messages().send(userId="me", body={"raw": raw}).execute()
            return f"Correo enviado a {to}."

        elif action == "search":
            query = parameters.get("query", "")
            results = service.users().messages().list(userId="me", q=query, maxResults=count).execute()
            messages = results.get("messages", [])
            if not messages:
                return f"Sin resultados para: {query}"
            output = []
            for msg in messages[:count]:
                m = service.users().messages().get(userId="me", id=msg["id"], format="metadata", metadataHeaders=["From", "Subject"]).execute()
                headers = {h["name"]: h["value"] for h in m["payload"]["headers"]}
                output.append(f"- {headers.get('From','?')}: {headers.get('Subject','?')}")
            return f"Resultados para '{query}':\n" + "\n".join(output)

        elif action == "read":
            msg_id = parameters.get("message_id", "")
            m = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
            headers = {h["name"]: h["value"] for h in m["payload"]["headers"]}
            snippet = m.get("snippet", "")
            return f"De: {headers.get('From','?')}\nAsunto: {headers.get('Subject','?')}\n{m['snippet'][:500]}"

        elif action == "reply":
            msg_id = parameters.get("message_id", "")
            body = parameters.get("body", "")
            original = service.users().messages().get(userId="me", id=msg_id, format="metadata", metadataHeaders=["From", "Subject"]).execute()
            headers = {h["name"]: h["value"] for h in original["payload"]["headers"]}
            reply_to = headers.get("From", "")
            subject = "Re: " + headers.get("Subject", "")
            msg = MIMEText(body)
            msg["To"] = reply_to
            msg["Subject"] = subject
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            service.users().messages().send(userId="me", body={"raw": raw, "threadId": original["threadId"]}).execute()
            return f"Respuesta enviada a {reply_to}."

        elif action == "archive":
            msg_id = parameters.get("message_id", "")
            service.users().messages().modify(userId="me", id=msg_id, body={"removeLabelIds": ["INBOX"]}).execute()
            return "Correo archivado."

        elif action == "delete":
            msg_id = parameters.get("message_id", "")
            service.users().messages().trash(userId="me", id=msg_id).execute()
            return "Correo eliminado."

        elif action == "mark_read":
            msg_id = parameters.get("message_id", "")
            service.users().messages().modify(userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}).execute()
            return "Correo marcado como leído."

        elif action == "labels":
            labels = service.users().labels().list(userId="me").execute()
            names = [l["name"] for l in labels.get("labels", [])]
            return "Etiquetas: " + ", ".join(names)

        return f"Gmail action '{action}' completado."
    except HttpError as e:
        return f"Error de Gmail: {e}"
    except Exception as e:
        return f"Error: {e}"
