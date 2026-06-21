"""accessibility.py — Accessibility features: task simplification, routines, emotional support."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, date

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
_ROUTINES_FILE = _CONFIG_DIR / "accessibility_routines.json"


def _load_routines() -> dict:
    try:
        return json.loads(_ROUTINES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_routines(r: dict) -> None:
    _ROUTINES_FILE.parent.mkdir(parents=True, exist_ok=True)
    _ROUTINES_FILE.write_text(json.dumps(r, indent=2), encoding="utf-8")


def accessibility(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = parameters.get("action", "task_simplify")
    text = parameters.get("text", "")
    fmt = parameters.get("format", "steps")
    name = parameters.get("name", "")
    stress_level = parameters.get("stress_level", 0.5)
    setting = parameters.get("setting", "")
    value = parameters.get("value", "")
    level = parameters.get("level", 0.5)

    if action == "task_simplify":
        if not text:
            return "Falta text (la tarea a simplificar)."
        sentences = [s.strip() for s in text.replace(".", ".").split(".") if s.strip()]
        if fmt == "steps":
            steps = [f"Paso {i+1}: {s}" for i, s in enumerate(sentences)]
            return "Tarea descompuesta:\n" + "\n".join(steps)
        elif fmt == "summary":
            return f"Resumen: {' | '.join(sentences[:5])}"
        elif fmt == "explain":
            return f"Explicación simple:\n" + "\n".join(f"  • {s}" for s in sentences[:5])

    elif action == "routine":
        routines = _load_routines()
        if name:
            if name in routines:
                routine = routines[name]
                if "streak" not in routine:
                    routine["streak"] = 0
                routine["streak"] += 1
                routine["last_done"] = str(date.today())
                _save_routines(routines)
                return f"Rutina '{name}' completada. Racha: {routine['streak']} días."
            routines[name] = {"created": str(date.today()), "streak": 1, "last_done": str(date.today())}
            _save_routines(routines)
            return f"Rutina '{name}' creada y completada."
        active = {k: v for k, v in routines.items() if v.get("last_done") == str(date.today())}
        return "Rutinas activas hoy:\n" + ("\n".join(f"  - {k} (racha: {v.get('streak',0)})" for k, v in active.items()) or "  Ninguna.")

    elif action == "emotional":
        msg = ""
        if stress_level > 0.7:
            msg = "Parece que tenés un nivel de estrés alto. Sugiero una pausa de 2 minutos: respirá hondo 5 veces."
        elif stress_level > 0.4:
            msg = "Noto algo de tensión. Recordá mantener una postura cómoda."
        else:
            msg = "Todo parece estar en orden a nivel emocional."
        if text:
            msg += f"\n\nSobre '{text}': mantené perspectivas realistas."
        return msg

    elif action == "speech_config":
        config_file = _CONFIG_DIR / "accessibility_config.json"
        config = {}
        try:
            config = json.loads(config_file.read_text())
        except Exception:
            pass
        if setting and value:
            config[setting] = value
            config_file.write_text(json.dumps(config, indent=2))
            return f"Configuración de voz actualizada: {setting} = {value}"
        config["vad_threshold"] = level
        config_file.write_text(json.dumps(config, indent=2))
        return f"Tolerancia de voz ajustada a {level}. (0.1=más sensible, 1.0=más tolerante)"

    elif action == "config":
        config_file = _CONFIG_DIR / "accessibility_config.json"
        try:
            config = json.loads(config_file.read_text())
            return "Configuración de accesibilidad:\n" + "\n".join(f"  {k}: {v}" for k, v in config.items())
        except Exception:
            return "Configuración por defecto activa."

    return f"Accessibility action '{action}' completado."
