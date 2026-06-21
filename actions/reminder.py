"""reminder.py — Set reminders using Windows Task Scheduler (or native schedulers)."""
from __future__ import annotations
import json
import secrets
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# Load timezone from config
def _get_timezone():
    """Load timezone from api_keys.json, defaults to America/Lima."""
    try:
        config_path = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        tz_name = config.get("timezone", "America/Lima")
        return ZoneInfo(tz_name)
    except Exception:
        return ZoneInfo("America/Lima")

_TZ = _get_timezone()

# Persistent reminder storage
_REMINDERS_FILE = Path(__file__).resolve().parent.parent / "config" / "reminders.json"


def _load_reminders() -> list[dict]:
    """Load reminders from persistent storage."""
    if not _REMINDERS_FILE.exists():
        return []
    try:
        data = json.loads(_REMINDERS_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def _save_reminders(reminders: list[dict]) -> None:
    """Save reminders to persistent storage."""
    _REMINDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _REMINDERS_FILE.write_text(json.dumps(reminders, indent=2, ensure_ascii=False), encoding="utf-8")


def _clean_expired_reminders() -> None:
    """Remove one-time reminders that have passed (for startup/init cleanup)."""
    reminders = _load_reminders()
    now = datetime.now(_TZ)
    active = []
    cleaned = 0
    for r in reminders:
        is_recurring = r.get("recurrence") is not None
        if is_recurring:
            active.append(r)
            continue
        try:
            dt_str = f"{r['date']} {r['time']}"
            target_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M').replace(tzinfo=_TZ)
            if target_dt >= (now - timedelta(hours=1)):
                active.append(r)
            else:
                cleaned += 1
        except Exception:
            pass
    if cleaned > 0:
        _save_reminders(active)


def _parse_time_input(date_str: str, time_str: str) -> tuple[datetime | None, str]:
    try:
        date_part = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None, "Invalid date format. Please use YYYY-MM-DD (e.g., 2025-12-25)."
    try:
        time_obj = datetime.strptime(time_str.strip(), "%H:%M").time()
    except ValueError:
        return None, "Invalid time format. Please use HH:MM in 24-hour format (e.g., 19:30 for 7:30 PM)."
    try:
        target_dt = datetime.combine(date_part, time_obj, tzinfo=_TZ)
        return target_dt, None
    except Exception as e:
        return None, f"Error parsing date/time: {e}"


def _is_time_in_past(target_dt: datetime) -> bool:
    now = datetime.now(_TZ)
    return target_dt < (now - timedelta(seconds=30))


def _schedule_windows_task(uid: str, target_dt: datetime, message: str, recurring: bool = False) -> str:
    """Schedule a Task Scheduler task using a .bat file (no Windows Defender issues)."""
    try:
        import base64
        local_dt = target_dt.astimezone().replace(tzinfo=None)
        task_name = f"JARVIS_R_{uid}"
        task_path = "\\JARVIS\\"

        # Write a .bat file that runs the notification via encoded PowerShell
        batch_dir = Path.home() / ".jarvis" / "reminders"
        batch_dir.mkdir(parents=True, exist_ok=True)
        batch_file = batch_dir / f"reminder_{uid}.bat"

        # Encode the notification command (avoid all quoting)
        ps_code = (
            "Add-Type -AssemblyName PresentationFramework;"
            "[System.Windows.MessageBox]::Show('" + message.replace("'", "''") + "','JARVIS Reminder')"
        )
        ps_bytes = ps_code.encode("utf-16-le")
        encoded = base64.b64encode(ps_bytes).decode("ascii")

        # Minimal .bat file: runs encoded PowerShell, then deletes itself
        batch_content = (
            "@echo off\r\n"
            "powershell -NoProfile -WindowStyle Hidden -EncodedCommand " + encoded + "\r\n"
            "del \"%~f0\"\r\n"
        )
        batch_file.write_text(batch_content, encoding="ascii")

        # Register the task to run the .bat file
        register_cmd = (
            "Unregister-ScheduledTask -TaskName '" + task_name + "' -TaskPath '" + task_path + "' -Confirm:$false -ErrorAction SilentlyContinue\r\n"
            "$trigger = New-ScheduledTaskTrigger -At '" + local_dt.strftime("%Y-%m-%d %H:%M:%S") + "' -Once\r\n"
            "$action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c \"" + str(batch_file) + "\"'\r\n"
            "$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable\r\n"
            "Register-ScheduledTask -TaskName '" + task_name + "' -TaskPath '" + task_path + "' -Trigger $trigger -Action $action -Settings $settings -Force | Out-Null\r\n"
            "Write-Host 'OK'\r\n"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", register_cmd],
            capture_output=True, text=True, timeout=10
        )

        if "OK" in result.stdout or result.returncode == 0:
            return f"Recordatorio establecido para {local_dt.strftime('%d/%m/%Y a las %H:%M')}."
        else:
            error = result.stderr or result.stdout or "Unknown error"
            return f"Error: {error[:100]}"

    except subprocess.TimeoutExpired:
        return "Error: timeout al crear recordatorio"
    except Exception as e:
        return f"Error al programar recordatorio: {e}"


def _gen_uid() -> str:
    """Generate a short unique ID for each reminder."""
    import hashlib, time
    raw = f"{time.time_ns()}{secrets.token_hex(4)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def _advance_recurring(uid: str) -> bool:
    """
    Advance a recurring reminder to the next occurrence date.
    Returns True if updated, False if not found or not recurring.
    """
    reminders = _load_reminders()
    for r in reminders:
        if r.get("uid") != uid:
            continue
        rec = r.get("recurrence")
        if not rec:
            return False
        try:
            current_date = datetime.strptime(r["date"], "%Y-%m-%d").date()
            time_str = r["time"]

            day_nums = {"mon":0,"tue":1,"wed":2,"thu":3,"fri":4,"sat":5,"sun":6}
            next_date = None

            if rec == "daily":
                next_date = current_date + timedelta(days=1)
            elif rec == "weekly":
                next_date = current_date + timedelta(days=7)
            else:
                # Comma-separated weekday list
                days = [d.strip().lower() for d in rec.split(",") if d.strip()]
                if days:
                    current_dow = current_date.weekday()  # 0=Mon
                    day_numbers = sorted([day_nums[d] for d in days if d in day_nums])
                    if day_numbers:
                        next_num = None
                        for dn in day_numbers:
                            if dn > current_dow:
                                next_num = dn
                                break
                        if next_num is None:
                            next_num = day_numbers[0]
                            days_ahead = (7 - current_dow) + next_num
                        else:
                            days_ahead = next_num - current_dow
                        next_date = current_date + timedelta(days=days_ahead)
                    else:
                        next_date = current_date + timedelta(days=1)

            if next_date:
                r["date"] = next_date.strftime("%Y-%m-%d")
                _save_reminders(reminders)

                # Reschedule Task Scheduler
                target_dt = datetime.combine(next_date, datetime.strptime(time_str, "%H:%M").time(), tzinfo=_TZ)
                result = _schedule_windows_task(uid, target_dt, r.get("message", ""), recurring=True)
                return "establecido" in result.lower() or "OK" in result
        except Exception:
            pass
        return False
    return False


def reminder(parameters=None, response=None, player=None, **kwargs) -> str:
    if parameters is None:
        parameters = {}

    action = parameters.get("action", "set").lower()

    if action in ("list", "listar", "mostrar", "show"):
        return _list_reminders_action(player)

    if action in ("delete", "borrar", "eliminar", "remove"):
        rm_uid = parameters.get("uid", "").strip()
        if rm_uid:
            return _delete_by_uid(rm_uid, player)
        date_str = parameters.get("date", "").strip()
        time_str = parameters.get("time", "").strip()
        if not date_str or not time_str:
            return "Para borrar un recordatorio, necesito el uid (desde 'listar'), o la fecha y hora."
        return _delete_reminder_action(date_str, time_str, player)

    date_str = parameters.get("date", "").strip()
    time_str = parameters.get("time", "").strip()
    message = parameters.get("message", "Recordatorio de JARVIS").strip()
    recurrence = parameters.get("recurrence")

    if not date_str or not time_str:
        return "I need both a date (YYYY-MM-DD) and a time (HH:MM) to set a reminder."

    target_dt, error = _parse_time_input(date_str, time_str)
    if error:
        return error

    if _is_time_in_past(target_dt):
        return "That time has already passed — I can't set a reminder in the past."

    uid = _gen_uid()
    result = _schedule_windows_task(uid, target_dt, message, recurring=bool(recurrence))

    if "establecido" in result.lower() or "OK" in result:
        reminders = _load_reminders()
        reminders.append({
            "uid": uid,
            "date": date_str,
            "time": time_str,
            "message": message,
            "recurrence": recurrence,
            "created_at": datetime.now(_TZ).isoformat()
        })
        _save_reminders(reminders)

    if player:
        try:
            player.write_log(f"REMINDER: {result}")
        except Exception:
            pass

    return result


def _list_reminders_action(player=None) -> str:
    _clean_expired_reminders()
    reminders = _load_reminders()

    if not reminders:
        return "No tienes recordatorios pendientes."

    now = datetime.now(_TZ)
    output = ["Tus recordatorios pendientes:"]

    for r in reminders:
        try:
            dt_str = f"{r['date']} {r['time']}"
            target_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M').replace(tzinfo=_TZ)
            delta = target_dt - now
            rec = r.get("recurrence")
            rec_label = f" ({rec})" if rec else ""

            if delta.days > 0:
                time_left = f"en {delta.days} dia(s) a las {r['time']}"
            else:
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                if hours > 0:
                    time_left = f"en {hours}h {minutes}m"
                else:
                    time_left = f"en {minutes} minutos"

            uid_short = r.get("uid", "?")[:6]
            output.append(f"  [{uid_short}] {r['message']}: {time_left}{rec_label}")
        except Exception:
            pass

    result = "\n".join(output)
    if player:
        try:
            player.write_log(f"REMINDERS LIST: {len(reminders)} pending")
        except Exception:
            pass
    return result


def _delete_by_uid(uid: str, player=None) -> str:
    reminders = _load_reminders()
    initial = len(reminders)
    reminders = [r for r in reminders if r.get("uid") != uid]
    if len(reminders) < initial:
        _save_reminders(reminders)
        result = "Recordatorio eliminado."
    else:
        result = "No encontre ese recordatorio."
    if player:
        try:
            player.write_log(f"REMINDER DELETE: {result}")
        except Exception:
            pass
    return result


def _delete_reminder_action(date_str: str, time_str: str, player=None) -> str:
    reminders = _load_reminders()
    initial_count = len(reminders)
    reminders = [
        r for r in reminders
        if not (r['date'] == date_str and r['time'] == time_str)
    ]
    if len(reminders) < initial_count:
        _save_reminders(reminders)
        result = f"Recordatorio de {date_str} a las {time_str} eliminado."
    else:
        result = f"No encontre un recordatorio para {date_str} a las {time_str}."
    if player:
        try:
            player.write_log(f"REMINDER DELETE: {result}")
        except Exception:
            pass
    return result


def startup_clean() -> None:
    """Call this at JARVIS startup to remove expired one-time reminders and reschedule recurring ones."""
    _clean_expired_reminders()
    # Reschedule any recurring reminders whose Task Scheduler task is missing or passed
    reminders = _load_reminders()
    now = datetime.now(_TZ)
    for r in reminders:
        rec = r.get("recurrence")
        if not rec:
            continue
        try:
            dt_str = f"{r['date']} {r['time']}"
            target_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M').replace(tzinfo=_TZ)
            if target_dt < (now - timedelta(hours=1)):
                # This should have fired while JARVIS was off; advance to next
                uid = r.get("uid", _gen_uid())
                if uid:
                    _advance_recurring(uid)
        except Exception:
            pass
