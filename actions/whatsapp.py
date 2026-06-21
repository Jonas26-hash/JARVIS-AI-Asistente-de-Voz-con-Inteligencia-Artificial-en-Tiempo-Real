"""whatsapp.py — WhatsApp Desktop app integration via pywinauto + URIs."""
from __future__ import annotations
import os, json, time, re, subprocess, urllib.parse
from pathlib import Path

_CONTACTS_FILE = Path(__file__).resolve().parent.parent / "config" / "whatsapp_contacts.json"

def _load_contacts() -> dict:
    try:
        return json.loads(_CONTACTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_contacts(contacts: dict) -> None:
    _CONTACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CONTACTS_FILE.write_text(json.dumps(contacts, indent=2, ensure_ascii=False), encoding="utf-8")

def _find_whatsapp_window():
    try:
        import pywinauto
        desktop = pywinauto.Desktop(allow_magic_lookup=False)
        for w in desktop.windows():
            try:
                title = w.window_text().lower()
                if "whatsapp" in title:
                    return pywinauto.Application().connect(handle=w.handle), w
            except Exception:
                continue
    except ImportError:
        pass
    return None, None

def _launch_whatsapp():
    try:
        subprocess.Popen(["start", "whatsapp://"], shell=True)
        time.sleep(3)
        return True
    except Exception:
        return False

def _focus_chat(contact_name: str) -> str | None:
    app, win = _find_whatsapp_window()
    if not win:
        return "No se pudo encontrar la ventana de WhatsApp Desktop"
    try:
        win.set_focus()
        time.sleep(0.5)
        import pywinauto.keyboard as kb
        kb.send_keys("^n")
        time.sleep(1)
        kb.send_keys(contact_name)
        time.sleep(1.5)
        kb.send_keys("{ENTER}")
        time.sleep(1)
        return None
    except Exception as e:
        return f"Error al enfocar chat: {e}"

def whatsapp(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = parameters.get("action", "")
    if not _find_whatsapp_window()[0]:
        _launch_whatsapp()
    result = ""
    contacts = _load_contacts()

    if action == "add_contact":
        name = parameters.get("name", "")
        phone = parameters.get("phone", "")
        if name and phone:
            contacts[name] = phone
            _save_contacts(contacts)
            result = f"Contacto {name} guardado con {phone}."
        else:
            result = "Falta name o phone."

    elif action == "list_contacts":
        if contacts:
            result = "Contactos:\n" + "\n".join(f"  - {n}: {p}" for n, p in contacts.items())
        else:
            result = "No hay contactos guardados."

    elif action == "delete_contact":
        name = parameters.get("name", "")
        if name in contacts:
            del contacts[name]
            _save_contacts(contacts)
            result = f"Contacto {name} eliminado."
        else:
            result = f"No se encontró {name}."

    elif action in ("send", "send_image"):
        receiver = parameters.get("receiver", "")
        message = parameters.get("message", "")
        if receiver in contacts:
            phone = contacts[receiver]
        elif receiver.startswith("+"):
            phone = receiver
        else:
            result = f"Contacto '{receiver}' no encontrado. Usá add_contact primero o poné el número con +."
            if player:
                player.write_log(f"WA: {result}")
            return result

        if action == "send_image":
            image_path = parameters.get("image_path", "")
            caption = parameters.get("caption", "")
            path_obj = Path(image_path)
            if not path_obj.is_file():
                result = f"No se encontró la imagen: {image_path}"
                if player:
                    player.write_log(f"WA: {result}")
                return result
            try:
                text = urllib.parse.quote(f"{caption}\n{path_obj.name}" if caption else path_obj.name)
                whatsapp_uri = f"whatsapp://send?phone={phone}&text={text}"
                subprocess.Popen(["start", whatsapp_uri], shell=True)
                time.sleep(2)
                import pywinauto.keyboard as kb
                kb.send_keys("%{TAB}")
                time.sleep(0.5)
                kb.send_keys(path_obj.resolve().as_posix())
                time.sleep(0.5)
                kb.send_keys("{ENTER}")
                time.sleep(1)
                kb.send_keys("{ENTER}")
                result = f"Imagen enviada a {receiver} por WhatsApp Desktop."
            except Exception as e:
                result = f"Error enviando imagen: {e}. Intentá copiar la imagen manualmente."
        else:
            try:
                import pywinauto.keyboard as kb
                import pyperclip

                app, win = _find_whatsapp_window()
                if not win:
                    _launch_whatsapp()
                    app, win = _find_whatsapp_window()

                if not win:
                    result = "No se pudo encontrar WhatsApp Desktop."
                else:
                    win.set_focus()
                    time.sleep(0.3)
                    kb.send_keys("^n")
                    time.sleep(0.5)
                    kb.send_keys(receiver)
                    time.sleep(0.8)
                    kb.send_keys("{ENTER}")
                    time.sleep(0.8)
                    pyperclip.copy(message)
                    time.sleep(0.2)
                    kb.send_keys("^v")
                    time.sleep(0.3)
                    kb.send_keys("{ENTER}")
                    time.sleep(0.5)
                    result = f"Mensaje enviado a {receiver} por WhatsApp Desktop."
            except Exception as e:
                result = f"Error enviando mensaje: {e}"

    elif action == "read":
        err = _focus_chat(parameters.get("chat", ""))
        if err:
            result = err
        else:
            try:
                import pywinauto.keyboard as kb
                kb.send_keys("^a")
                time.sleep(0.3)
                kb.send_keys("^c")
                time.sleep(1)
                import pyperclip
                text = pyperclip.paste()
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                result = "Últimos mensajes:\n" + "\n".join(lines[:int(parameters.get("count", 10))])
            except Exception as e:
                result = f"Error leyendo mensajes: {e}"

    elif action == "unread":
        result = "Usá 'read' con el nombre del chat para ver mensajes recientes."

    if not result:
        result = f"WhatsApp action '{action}' completado."
    if player:
        player.write_log(f"WA: {result}")
    return result
