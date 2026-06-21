"""spotify_control.py — Control de Spotify vía teclas multimedia + API opcional."""
from __future__ import annotations
import json, os, subprocess, time, threading
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"
_PYCAW_CACHE = {"time": 0, "sessions": None}

def _load_config():
    try:
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _send_media_key(key: str):
    """Send media keys via Windows API."""
    import ctypes
    from ctypes import wintypes
    MEDIA_VK = {
        "play_pause": 0xB3,
        "playpause": 0xB3,
        "next": 0xB0,
        "nexttrack": 0xB0,
        "previous": 0xB1,
        "prevtrack": 0xB1,
        "stop":      0xB2,
    }
    APPCMD = {
        "play_pause": 0x0E0000,  # APPCOMMAND_MEDIA_PLAY_PAUSE
        "next": 0x0B0000,        # APPCOMMAND_MEDIA_NEXTTRACK
        "previous": 0x0C0000,    # APPCOMMAND_MEDIA_PREVIOUSTRACK
        "stop": 0x0D0000,        # APPCOMMAND_MEDIA_STOP
    }
    vk = MEDIA_VK.get(key)
    cmd = APPCMD.get(key)
    user32 = ctypes.windll.user32

    if cmd:
        # ── Method 1: Direct PostMessage to Spotify window ──────────
        WM_APPCOMMAND = 0x0319
        hwnd = user32.FindWindowW("Chrome_WidgetWin_0", None)
        if not hwnd:
            hwnd = user32.FindWindowW("SpotifyMainWindow", None)
        if hwnd:
            user32.PostMessageW(hwnd, WM_APPCOMMAND, 0, cmd)
            return

    if vk:
        # ── Method 2: SendInput with proper argtypes ────────────────
        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [
                ("wVk",      wintypes.WORD),
                ("wScan",    wintypes.WORD),
                ("dwFlags",  wintypes.DWORD),
                ("time",     wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
            ]

        class INPUT(ctypes.Structure):
            _fields_ = [
                ("type", wintypes.DWORD),
                ("ki",   KEYBDINPUT),
            ]

        user32.SendInput.argtypes = [
            wintypes.UINT,
            ctypes.POINTER(INPUT),
            ctypes.c_int,
        ]
        user32.SendInput.restype = wintypes.UINT

        INPUT_KEYBOARD = 1
        KEYEVENTF_KEYUP = 0x0002
        for flags in (0, KEYEVENTF_KEYUP):
            inp = INPUT(INPUT_KEYBOARD, KEYBDINPUT(vk, 0, flags, 0, None))
            result = user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
            if result == 0:
                break
        else:
            return  # both keydown and keyup succeeded

        # ── Method 3: Fallback keybd_event ──────────────────────────
        user32.keybd_event(vk, 0, 0, None)          # keydown
        user32.keybd_event(vk, 0, 0x0002, None)     # keyup

def _spotify_session_volume(action: str, value=None) -> str:
    """Control Spotify's Windows audio session without changing master volume."""
    try:
        from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
    except Exception as e:
        return f"No pude acceder al mezclador de apps de Windows: {e}"

    sessions = AudioUtilities.GetAllSessions()
    matches = []
    for session in sessions:
        proc = session.Process
        if proc and proc.name().lower() == "spotify.exe":
            matches.append(session)
    if not matches:
        return "No encontré una sesión de audio activa de Spotify. Reproduce algo en Spotify e intenta de nuevo."

    results = []
    for session in matches:
        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        current = float(volume.GetMasterVolume())
        if action in ("spotify_volume_up", "spotify_up"):
            new_val = min(1.0, current + 0.08)
        elif action in ("spotify_volume_down", "spotify_down"):
            new_val = max(0.0, current - 0.08)
        elif action in ("spotify_mute",):
            muted = bool(volume.GetMute())
            volume.SetMute(0 if muted else 1, None)
            results.append("Spotify activado." if muted else "Spotify silenciado.")
            continue
        else:
            if value is None or value == "":
                new_val = min(1.0, current + 0.08)
            else:
                new_val = max(0.0, min(1.0, int(value) / 100))
        volume.SetMasterVolume(new_val, None)
        results.append(f"Volumen de Spotify al {int(new_val * 100)}%.")
    return results[-1] if results else "Volumen de Spotify actualizado."

def spotify_control(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = parameters.get("action", "play_pause")
    result = ""
    config = _load_config()
    cid = config.get("spotify_client_id", "")
    csecret = config.get("spotify_client_secret", "")

    # Lauch Spotify if not running (async — no blocking)
    try:
        import psutil
        spotify_running = any(
            p.info["name"] == "spotify.exe"
            for p in psutil.process_iter(["name"], attrs=["name"])
        )
    except Exception:
        spotify_running = False
    if not spotify_running:
        subprocess.Popen(["start", "spotify:"], shell=True)

    if action in ("play_pause", "play", "pause", "toggle", "resume"):
        _send_media_key("play_pause")
        result = "Reproduciendo."

    elif action == "next":
        _send_media_key("next")
        result = "Siguiente tema."

    elif action == "previous":
        _send_media_key("previous")
        result = "Tema anterior."

    elif action in ("volume", "volume_up", "volume_down", "mute", "set_volume", "get_volume"):
        try:
            from pycaw.pycaw import AudioUtilities
            vol = AudioUtilities.GetSpeakers().EndpointVolume
            if action == "volume_up":
                current = vol.GetMasterVolumeLevelScalar()
                new_val = min(1.0, current + 0.08)
                vol.SetMasterVolumeLevelScalar(new_val, None)
                result = f"Volumen al {int(new_val * 100)}%."
            elif action == "volume_down":
                current = vol.GetMasterVolumeLevelScalar()
                new_val = max(0.0, current - 0.08)
                vol.SetMasterVolumeLevelScalar(new_val, None)
                result = f"Volumen al {int(new_val * 100)}%."
            elif action == "mute":
                muted = bool(vol.GetMute())
                from comtypes import GUID
                vol.SetMute(False if muted else True, GUID())
                result = "Sonido activado." if muted else "Silenciado."
            elif action in ("volume", "set_volume"):
                val = max(0, min(100, int(parameters.get("value", 50)))) / 100
                vol.SetMasterVolumeLevelScalar(val, None)
                result = f"Volumen al {int(val * 100)}%."
            elif action == "get_volume":
                val = int(vol.GetMasterVolumeLevelScalar() * 100)
                muted = bool(vol.GetMute())
                result = f"Volumen al {val}%." if not muted else "Silenciado."
        except Exception as e:
            result = f"Error de volumen: {e}"

    elif action == "current_track":
        result = "Usá la tecla de play/pause para ver el tema actual en Spotify."

    elif action in ("spotify_volume", "spotify_volume_up", "spotify_volume_down", "spotify_up", "spotify_down", "spotify_mute"):
        result = _spotify_session_volume(action, parameters.get("value"))

    elif action in ("play_playlist", "playlist", "search", "queue"):
        if cid and csecret:
            try:
                import spotipy
                from spotipy.oauth2 import SpotifyOAuth
                sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_id=cid, client_secret=csecret,
                    redirect_uri=config.get("spotify_redirect_uri", "http://127.0.0.1:8888/callback"),
                    scope="user-modify-playback-state user-read-playback-state playlist-read-private"
                ))
                if action in ("play_playlist", "playlist"):
                    q = parameters.get("query", "")
                    results = sp.search(q, type="playlist", limit=1)
                    if results["playlists"]["items"]:
                        uri = results["playlists"]["items"][0]["uri"]
                        sp.start_playback(context_uri=uri)
                        result = f"Reproduciendo playlist."
                    else:
                        result = "No encontré esa playlist."
                elif action == "search":
                    q = parameters.get("query", "")
                    results = sp.search(q, limit=5)
                    tracks = results["tracks"]["items"]
                    if tracks:
                        sp.start_playback(uris=[tracks[0]["uri"]])
                        result = f"Reproduciendo {tracks[0]['name']}."
                    else:
                        result = "No encontré esa canción."
                elif action == "queue":
                    q = parameters.get("query", "")
                    results = sp.search(q, limit=1)
                    if results["tracks"]["items"]:
                        sp.add_to_queue(results["tracks"]["items"][0]["uri"])
                        result = "Agregado a la cola."
            except Exception as e:
                result = f"Error con API de Spotify: {e}. Para búsqueda avanzada, configurá spotify_client_id y spotify_client_secret en api_keys.json"
        else:
            result = "Búsqueda avanzada requiere API key. Para play/pause/next/previous ya funciona sin configuración."

    elif action == "launch":
        subprocess.Popen(["start", "spotify:"], shell=True)
        result = "Abriendo Spotify."

    else:
        result = f"Acción '{action}' no reconocida. Usá: play_pause, next, previous, volume_up, volume_down, spotify_volume_up, spotify_volume_down, mute, search, play_playlist, launch"

    if not result:
        result = f"Spotify: {action} completado."
    if player:
        player.write_log(f"SP: {result}")
    return result
