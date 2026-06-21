"""google_drive.py — Google Drive integration via Google API."""
from __future__ import annotations
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from pathlib import Path
import json, os, io

SCOPES = ["https://www.googleapis.com/auth/drive"]
_TOKEN_DIR = Path(__file__).resolve().parent.parent / "config"
_TOKEN_FILE = _TOKEN_DIR / "drive_token.json"
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
    service = build("drive", "v3", credentials=creds)
    return service, None


def google_drive(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = parameters.get("action", "list")

    service, err = _get_service()
    if err:
        return err

    try:
        if action == "list":
            folder_id = parameters.get("folder_id", "root")
            results = service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                pageSize=20, fields="files(id,name,mimeType,size)"
            ).execute()
            files = results.get("files", [])
            if not files:
                return "La carpeta está vacía."
            output = [f"{f['name']} ({f.get('mimeType','?')})" for f in files]
            return "Archivos:\n" + "\n".join(output)

        elif action == "search":
            query = parameters.get("query", "")
            results = service.files().list(
                q=f"name contains '{query}' and trashed=false",
                pageSize=10, fields="files(id,name,mimeType)"
            ).execute()
            files = results.get("files", [])
            if not files:
                return f"Sin resultados para: {query}"
            return "Resultados:\n" + "\n".join(f"- {f['name']}" for f in files)

        elif action == "upload":
            path = parameters.get("path", "")
            if not os.path.isfile(path):
                return f"Archivo no encontrado: {path}"
            name = os.path.basename(path)
            media = MediaFileUpload(path, resumable=True)
            service.files().create(body={"name": name}, media_body=media).execute()
            return f"Archivo subido: {name}"

        elif action == "download":
            file_id = parameters.get("file_id", "")
            dest = parameters.get("destination", str(Path.home() / "Downloads"))
            os.makedirs(dest, exist_ok=True)
            meta = service.files().get(fileId=file_id, fields="name").execute()
            fpath = os.path.join(dest, meta["name"])
            request = service.files().get_media(fileId=file_id)
            with io.FileIO(fpath, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
            return f"Descargado: {fpath}"

        elif action == "create_folder":
            name = parameters.get("name", "Nueva carpeta")
            folder_id = parameters.get("folder_id", "root")
            meta = {"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [folder_id]}
            service.files().create(body=meta).execute()
            return f"Carpeta '{name}' creada."

        elif action == "delete":
            file_id = parameters.get("file_id", "")
            service.files().delete(fileId=file_id).execute()
            return "Archivo eliminado de Drive."

        elif action == "share":
            file_id = parameters.get("file_id", "")
            email = parameters.get("email", "")
            role = parameters.get("role", "reader")
            perm = {"type": "user", "role": role, "emailAddress": email}
            service.permissions().create(fileId=file_id, body=perm).execute()
            return f"Compartido con {email} ({role})."

        elif action == "info":
            file_id = parameters.get("file_id", "")
            f = service.files().get(fileId=file_id, fields="name,mimeType,size,createdTime,owners").execute()
            return f"Nombre: {f['name']}\nTipo: {f['mimeType']}\nCreado: {f['createdTime']}"

        return f"Drive action '{action}' completado."
    except Exception as e:
        return f"Error: {e}"
