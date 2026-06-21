"""automation_center.py - Proactive, lightweight automations for JARVIS."""
from __future__ import annotations

import json
import threading
import time
from datetime import date, datetime
from pathlib import Path


_CONFIG_FILE = Path(__file__).resolve().parent.parent / "config" / "proactive_automations.json"
_RUNNER_STARTED = False

_DEFAULT_RULES = {
    "system_health": {
        "enabled": True,
        "type": "system_health",
        "interval_seconds": 300,
        "cpu_threshold": 92,
        "ram_threshold": 92,
        "last_run": 0,
        "last_alert": "",
    },
    "daily_memory_review": {
        "enabled": False,
        "type": "memory_review",
        "interval_seconds": 86400,
        "last_run": 0,
        "last_alert": "",
    },
}


def _load_rules() -> dict:
    try:
        data = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for name, rule in _DEFAULT_RULES.items():
                data.setdefault(name, rule.copy())
            return data
    except Exception:
        pass
    return {name: rule.copy() for name, rule in _DEFAULT_RULES.items()}


def _save_rules(rules: dict) -> None:
    _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text(json.dumps(rules, indent=2, ensure_ascii=False), encoding="utf-8")


def _notify(player, speak, message: str) -> None:
    if player:
        try:
            player.write_log(f"AUTO: {message}")
        except Exception:
            pass
    if speak:
        try:
            speak(message)
        except Exception:
            pass


def _run_rule(name: str, rule: dict, player=None, speak=None) -> str:
    rtype = rule.get("type", name)
    now = time.time()

    if rtype == "system_health":
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
        except Exception as exc:
            return f"{name}: no se pudo leer sistema ({exc})."

        cpu_limit = float(rule.get("cpu_threshold", 92))
        ram_limit = float(rule.get("ram_threshold", 92))
        if cpu >= cpu_limit or ram >= ram_limit:
            today_key = f"{date.today()}:{int(cpu)}:{int(ram)}"
            if rule.get("last_alert") != today_key:
                message = f"Sistema exigido: CPU {cpu:.0f}% y RAM {ram:.0f}%."
                rule["last_alert"] = today_key
                _notify(player, speak, message)
                return message
        return f"Sistema OK: CPU {cpu:.0f}%, RAM {ram:.0f}%."

    if rtype == "memory_review":
        memory_file = Path(__file__).resolve().parent.parent / "memory" / "long_term.json"
        try:
            memory = json.loads(memory_file.read_text(encoding="utf-8"))
            total = sum(len(v) for v in memory.values() if isinstance(v, dict))
        except Exception:
            total = 0
        message = f"Revision de memoria lista: {total} recuerdos registrados."
        _notify(player, speak, message)
        return message

    rule["last_run"] = now
    return f"{name}: tipo '{rtype}' sin ejecutor especifico."


def _runner(player=None, speak=None):
    while True:
        rules = _load_rules()
        changed = False
        now = time.time()
        for name, rule in rules.items():
            if not rule.get("enabled", False):
                continue
            interval = int(rule.get("interval_seconds", 300))
            last_run = float(rule.get("last_run", 0))
            if now - last_run < interval:
                continue
            result = _run_rule(name, rule, player=player, speak=speak)
            rule["last_run"] = now
            rule["last_result"] = result
            rule["last_checked_at"] = datetime.now().isoformat(timespec="seconds")
            changed = True
        if changed:
            _save_rules(rules)
        time.sleep(30)


def start_runner(player=None, speak=None):
    global _RUNNER_STARTED
    if _RUNNER_STARTED:
        return
    _RUNNER_STARTED = True
    thread = threading.Thread(target=_runner, kwargs={"player": player, "speak": speak}, daemon=True)
    thread.start()


def automation_center(parameters=None, player=None, speak=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = str(parameters.get("action", "list")).lower()
    name = str(parameters.get("name", "")).strip()
    rtype = str(parameters.get("type", "system_health")).strip()

    rules = _load_rules()

    if action in ("list", "status"):
        return "Automatizaciones proactivas:\n" + "\n".join(
            f"- {n} [{r.get('type', n)}] {'ON' if r.get('enabled') else 'OFF'} cada {r.get('interval_seconds', '?')}s"
            for n, r in sorted(rules.items())
        )

    if action in ("enable", "disable"):
        if not name or name not in rules:
            return f"Automatizacion no encontrada: {name or '(sin nombre)'}."
        rules[name]["enabled"] = action == "enable"
        _save_rules(rules)
        return f"{name} {'activada' if action == 'enable' else 'desactivada'}."

    if action == "add":
        if not name:
            return "Falta name."
        rules[name] = {
            "enabled": bool(parameters.get("enabled", True)),
            "type": rtype,
            "interval_seconds": int(parameters.get("interval_seconds", 300)),
            "cpu_threshold": float(parameters.get("cpu_threshold", 92)),
            "ram_threshold": float(parameters.get("ram_threshold", 92)),
            "last_run": 0,
        }
        _save_rules(rules)
        return f"Automatizacion agregada: {name}."

    if action in ("remove", "delete"):
        if name in rules:
            del rules[name]
            _save_rules(rules)
            return f"Automatizacion eliminada: {name}."
        return f"No encontre {name}."

    if action == "check_now":
        selected = [name] if name else list(rules.keys())
        results = []
        for item in selected:
            if item in rules:
                results.append(_run_rule(item, rules[item], player=player, speak=speak))
                rules[item]["last_run"] = time.time()
                rules[item]["last_checked_at"] = datetime.now().isoformat(timespec="seconds")
        _save_rules(rules)
        return "Chequeo proactivo:\n" + "\n".join(results or ["Sin reglas para revisar."])

    return f"Accion de automatizacion desconocida: {action}."
