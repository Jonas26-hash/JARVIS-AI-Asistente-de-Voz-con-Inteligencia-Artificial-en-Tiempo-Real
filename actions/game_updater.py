"""game_updater.py — Steam & Epic Games update management."""
from __future__ import annotations
import subprocess, os, json
from pathlib import Path
from datetime import datetime


def game_updater(parameters=None, player=None, speak=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = parameters.get("action", "update")
    platform = parameters.get("platform", "steam")
    game_name = parameters.get("game_name", "")

    steam_path = "C:\\Program Files (x86)\\Steam\\steam.exe"
    epic_path = os.path.expandvars("%LOCALAPPDATA%\\EpicGamesLauncher\\Portal\\Binaries\\Win32\\EpicGamesLauncher.exe")

    try:
        if action == "list":
            if platform in ("steam", "both"):
                try:
                    r = subprocess.run([steam_path, "-list"], capture_output=True, text=True, timeout=30)
                    return f"Steam: {r.stdout[:1000] or 'Usá Steam para ver la lista.'}"
                except FileNotFoundError:
                    return "Steam no encontrado en la ruta por defecto."
            return "Usá la app de Epic para ver juegos instalados."

        elif action == "update":
            if game_name:
                cmd = [steam_path, f"steam://rungameid/{game_name}"]
                subprocess.Popen(cmd, shell=True)
                return f"Actualizando {game_name}..."
            if platform == "steam":
                subprocess.Popen([steam_path, "-login", "anonymous"], shell=True)
                return "Steam iniciado. Las actualizaciones se ejecutarán automáticamente."
            return f"Actualización lanzada para {platform}."

        elif action == "install":
            app_id = parameters.get("app_id", "")
            if app_id:
                subprocess.Popen([steam_path, f"steam://install/{app_id}"], shell=True)
                return f"Instalando juego (AppID: {app_id})..."
            if game_name:
                return f"Buscá el AppID de '{game_name}' en steamdb.info y usá app_id."
            return "Falta app_id o game_name."

        elif action == "schedule":
            hour = parameters.get("hour", 3)
            minute = parameters.get("minute", 0)
            shutdown = parameters.get("shutdown_when_done", False)
            try:
                subprocess.run(["schtasks", "/Create", "/SC", "DAILY", "/TN", "JARVIS_GameUpdate",
                                "/TR", f'"{steam_path}" -login anonymous',
                                "/ST", f"{hour:02d}:{minute:02d}", "/F"],
                               capture_output=True, text=True, timeout=15)
                return f"Actualización programada a las {hour:02d}:{minute:02d}."
            except Exception as e:
                return f"Error: {e}"

        elif action == "cancel_schedule":
            subprocess.run(["schtasks", "/Delete", "/TN", "JARVIS_GameUpdate", "/F"],
                           capture_output=True, text=True, timeout=15)
            return "Programación cancelada."

        elif action == "schedule_status":
            r = subprocess.run(["schtasks", "/Query", "/TN", "JARVIS_GameUpdate", "/FO", "LIST"],
                               capture_output=True, text=True, timeout=15)
            return r.stdout.strip() or "No hay tarea programada."

        return f"Game Updater action '{action}' completado."
    except Exception as e:
        return f"Error: {e}"
