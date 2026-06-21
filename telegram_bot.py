"""telegram_bot.py — Bot de Telegram para controlar JARVIS remotamente."""
from __future__ import annotations
import asyncio, json, os, signal, subprocess, sys, time
from datetime import datetime
from pathlib import Path

_BASE_DIR    = Path(__file__).resolve().parent
_CONFIG_PATH = _BASE_DIR / "config" / "api_keys.json"
_STATE_PATH  = _BASE_DIR / "telegram_state.json"
_INBOX_PATH  = _BASE_DIR / "telegram_in.json"
_OUTBOX_PATH = _BASE_DIR / "telegram_out.json"
_MAIN_PY     = _BASE_DIR / "main.py"

_jarvis_proc: subprocess.Popen | None = None
_loop: asyncio.AbstractEventLoop | None = None
_application = None

def _load_config() -> dict:
    try:
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _get_token() -> str:
    return _load_config().get("telegram_bot_token", "")

def _save_state(state: dict):
    try:
        _STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass

def _load_state() -> dict:
    try:
        return json.loads(_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"jarvis_pid": None, "chat_ids": []}

def _is_jarvis_running() -> bool:
    """Check if any main.py process is already running on the system."""
    try:
        import psutil as _ps
        for p in _ps.process_iter(["cmdline", "name", "pid"]):
            try:
                cmd = p.info.get("cmdline") or []
                if any("main.py" in part.replace("\\", "/") for part in cmd):
                    return True
            except Exception:
                continue
    except ImportError:
        try:
            import subprocess as _sp
            out = _sp.check_output(
                'wmic process where "name like \'%%python%%\'" get commandline /format:csv',
                shell=True, stderr=_sp.DEVNULL, timeout=3,
            ).decode("utf-8", errors="replace")
            for line in out.splitlines():
                if "main.py" in line.replace("\\", "/"):
                    return True
        except Exception:
            pass
    return False

def _main_keyboard():
    from telegram import ReplyKeyboardMarkup
    return ReplyKeyboardMarkup(
        [
            ["▶️ Iniciar JARVIS", "⏹️ Apagar JARVIS"],
            ["🔊 Sonido PC", "🔇 Silenciar PC"],
            ["🎤 Escuchar JARVIS", "🔇 Callar JARVIS"],
            ["📊 Estado"],
        ],
        resize_keyboard=True,
    )

async def start_jarvis(update, context):
    global _jarvis_proc
    state = _load_state()
    if _jarvis_proc and _jarvis_proc.poll() is None:
        await update.message.reply_text(
            "⚠️ JARVIS ya está encendido.",
            reply_markup=_main_keyboard(),
        )
        return
    if _is_jarvis_running():
        await update.message.reply_text(
            "⚠️ JARVIS ya está corriendo (lo iniciaste manualmente).\n"
            "Usá los botones de control o esperá a que termine.",
            reply_markup=_main_keyboard(),
        )
        return
    try:
        python = sys.executable or "python"
        _jarvis_proc = subprocess.Popen(
            [python, str(_MAIN_PY)],
            cwd=str(_BASE_DIR),
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        _save_state({"jarvis_pid": _jarvis_proc.pid, "chat_ids": list(state.get("chat_ids", []))})
        await update.message.reply_text(
            "✅ JARVIS encendido.\n"
            "Mandale cualquier mensaje y se lo paso.\n"
            "Usá /stop para apagarlo.",
            reply_markup=_main_keyboard(),
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error al iniciar: {e}")

async def stop_jarvis(update, context):
    global _jarvis_proc
    if _jarvis_proc and _jarvis_proc.poll() is None:
        try:
            _jarvis_proc.terminate()
            try:
                _jarvis_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _jarvis_proc.kill()
        except Exception:
            pass
        _jarvis_proc = None
        _save_state({"jarvis_pid": None, "chat_ids": []})
        await update.message.reply_text(
            "🛑 JARVIS apagado.",
            reply_markup=_main_keyboard(),
        )
    else:
        await update.message.reply_text(
            "JARVIS ya está apagado.",
            reply_markup=_main_keyboard(),
        )

async def status_jarvis(update, context):
    if (_jarvis_proc and _jarvis_proc.poll() is None) or _is_jarvis_running():
        await update.message.reply_text(
            "✅ JARVIS está encendido.",
            reply_markup=_main_keyboard(),
        )
    else:
        await update.message.reply_text(
            "💤 JARVIS está apagado. Usá /start.",
            reply_markup=_main_keyboard(),
        )

async def menu(update, context):
    await update.message.reply_text(
        "🤖 *JARVIS — Control Remoto*\n\n"
        "Usá los botones de abajo o escribí cualquier mensaje.\n\n"
        "• ▶️ *Iniciar JARVIS* — Enciende el asistente\n"
        "• ⏹️ *Apagar JARVIS* — Lo apaga\n"
        "• 📊 *Estado* — Ver si está corriendo",
        parse_mode="Markdown",
        reply_markup=_main_keyboard(),
    )

async def handle_message(update, context):
    global _jarvis_proc
    text = update.message.text or ""

    # Handle keyboard button presses
    if text == "▶️ Iniciar JARVIS":
        await start_jarvis(update, context)
        return
    if text == "⏹️ Apagar JARVIS":
        await stop_jarvis(update, context)
        return
    if text == "📊 Estado":
        await status_jarvis(update, context)
        return
    if text == "🔇 Silenciar PC":
        await _send_to_jarvis(update, "silenciar")
        return
    if text == "🔊 Sonido PC":
        await _send_to_jarvis(update, "activar sonido")
        return
    if text == "🔇 Callar JARVIS":
        await _send_to_jarvis(update, "callar jarvis")
        return
    if text == "🎤 Escuchar JARVIS":
        await _send_to_jarvis(update, "escuchar jarvis")
        return

    if not (_jarvis_proc and _jarvis_proc.poll() is None) and not _is_jarvis_running():
        await update.message.reply_text(
            "JARVIS está apagado. Usá /start para encenderlo.",
            reply_markup=_main_keyboard(),
        )
        return

    await _send_to_jarvis(update, text)

async def _send_to_jarvis(update, text: str):
    chat_id = update.effective_chat.id
    msg_id = int(time.time() * 1000)
    inbox = []
    try:
        inbox = json.loads(_INBOX_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    inbox.append({"id": msg_id, "text": text, "chat_id": chat_id})
    _INBOX_PATH.write_text(json.dumps(inbox, ensure_ascii=False), encoding="utf-8")
    await update.message.reply_text("📤 Mensaje enviado a JARVIS...", reply_markup=_main_keyboard())

async def poll_outbox(context):
    """Cada 2s revisa si JARVIS respondió y reenvía a Telegram."""
    try:
        outbox = json.loads(_OUTBOX_PATH.read_text(encoding="utf-8"))
    except Exception:
        return
    if not outbox:
        return
    remaining = []
    for item in outbox:
        try:
            await context.bot.send_message(
                chat_id=item["chat_id"],
                text=f"🤖 *JARVIS:* {item['text']}",
                parse_mode="Markdown",
            )
        except Exception:
            remaining.append(item)
    _OUTBOX_PATH.write_text(json.dumps(remaining, ensure_ascii=False), encoding="utf-8")

async def post_init(application):
    global _loop
    _loop = asyncio.get_event_loop()
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(poll_outbox, interval=2.0, first=2.0)

async def welcome(update, context):
    """Mensaje de bienvenida al iniciar el bot por primera vez."""
    await update.message.reply_text(
        "🤖 *¡Bienvenido a JARVIS!*\n\n"
        "Soy tu asistente personal con IA.\n"
        "Usá los botones de abajo para controlarme:\n\n"
        "• ▶️ *Iniciar JARVIS* — Enciende el asistente\n"
        "• ⏹️ *Apagar JARVIS* — Lo apaga\n"
        "• 📊 *Estado* — Ver si está corriendo\n"
        "• 🔇 *Silenciar PC* — Mutea el audio del equipo\n"
        "• 🔊 *Sonido PC* — Restaura el audio del equipo\n"
        "• 🔇 *Callar JARVIS* — JARVIS deja de escuchar\n"
        "• 🎤 *Escuchar JARVIS* — JARVIS vuelve a escuchar\n\n"
        "También podés escribirme lo que quieras y se lo paso.",
        parse_mode="Markdown",
        reply_markup=_main_keyboard(),
    )

def main():
    token = _get_token()
    if not token:
        print("[Telegram] No hay token. Configurá telegram_bot_token en config/api_keys.json")
        input("Presioná Enter para salir...")
        return

    from telegram.ext import Application, CommandHandler, MessageHandler, filters

    app = Application.builder().token(token).post_init(post_init).build()
    app.add_handler(CommandHandler("start", welcome))
    app.add_handler(CommandHandler("iniciar", start_jarvis))
    app.add_handler(CommandHandler("stop", stop_jarvis))
    app.add_handler(CommandHandler("apagar", stop_jarvis))
    app.add_handler(CommandHandler("status", status_jarvis))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("[Telegram] Bot iniciado. Esperando mensajes...")
    app.run_polling(allowed_updates=["messages"])

if __name__ == "__main__":
    main()
