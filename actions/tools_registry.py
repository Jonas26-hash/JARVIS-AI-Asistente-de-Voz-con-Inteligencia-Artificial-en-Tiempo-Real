"""tools_registry.py - Lightweight registry for JARVIS tools and modules."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


_ROOT = Path(__file__).resolve().parent.parent
_ACTIONS_DIR = _ROOT / "actions"
_REGISTRY_FILE = _ROOT / "config" / "tools_registry.json"

_CORE_TOOLS = {
    "memory_panel": {"category": "personal", "description": "Editar y consultar memoria larga."},
    "tools_registry": {"category": "system", "description": "Listar, activar y documentar herramientas."},
    "automation_center": {"category": "automation", "description": "Automatizaciones proactivas y monitoreo."},
}


def _load_registry() -> dict:
    try:
        data = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {"overrides": {}, "custom": {}}


def _save_registry(data: dict) -> None:
    _REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _REGISTRY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _discover_action_modules() -> dict:
    discovered = {}
    for path in sorted(_ACTIONS_DIR.glob("*.py")):
        if path.name.startswith("_") or path.name == "__init__.py":
            continue
        name = path.stem
        spec = importlib.util.spec_from_file_location(f"_jarvis_probe_{name}", str(path))
        ok = bool(spec)
        discovered[name] = {
            "name": name,
            "category": _CORE_TOOLS.get(name, {}).get("category", "action"),
            "description": _CORE_TOOLS.get(name, {}).get("description", f"Modulo actions/{path.name}"),
            "source": str(path),
            "available": ok,
            "enabled": True,
        }
    return discovered


def _merged_tools() -> dict:
    registry = _load_registry()
    tools = _discover_action_modules()
    for name, meta in _CORE_TOOLS.items():
        tools.setdefault(name, {"name": name, "source": "runtime", "available": True, "enabled": True})
        tools[name].update(meta)
    for name, meta in registry.get("custom", {}).items():
        tools[name] = {
            "name": name,
            "category": meta.get("category", "custom"),
            "description": meta.get("description", ""),
            "source": meta.get("source", "custom"),
            "available": True,
            "enabled": meta.get("enabled", True),
        }
    for name, override in registry.get("overrides", {}).items():
        if name in tools:
            tools[name].update(override)
    return tools


def tools_registry(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = str(parameters.get("action", "list")).lower()
    name = str(parameters.get("name", "")).strip()
    category = str(parameters.get("category", "")).strip()
    description = str(parameters.get("description", "")).strip()
    source = str(parameters.get("source", "")).strip()

    registry = _load_registry()
    tools = _merged_tools()

    if action in ("list", "status"):
        selected = list(tools.values())
        if category:
            selected = [tool for tool in selected if tool.get("category") == category]
        selected.sort(key=lambda item: (item.get("category", ""), item["name"]))
        if not selected:
            return "No hay herramientas para ese filtro."
        return "Registro de herramientas:\n" + "\n".join(
            f"- {tool['name']} [{tool.get('category','?')}] {'ON' if tool.get('enabled', True) else 'OFF'}"
            for tool in selected
        )

    if action == "categories":
        cats = sorted({tool.get("category", "action") for tool in tools.values()})
        return "Categorias:\n" + "\n".join(f"- {cat}" for cat in cats)

    if action == "info":
        if not name or name not in tools:
            return f"Herramienta no encontrada: {name or '(sin nombre)'}."
        tool = tools[name]
        return (
            f"{name}\n"
            f"Categoria: {tool.get('category','action')}\n"
            f"Estado: {'ON' if tool.get('enabled', True) else 'OFF'}\n"
            f"Fuente: {tool.get('source','?')}\n"
            f"Descripcion: {tool.get('description','')}"
        )

    if action in ("enable", "disable"):
        if not name or name not in tools:
            return f"Herramienta no encontrada: {name or '(sin nombre)'}."
        registry.setdefault("overrides", {}).setdefault(name, {})["enabled"] = action == "enable"
        _save_registry(registry)
        return f"{name} {'activada' if action == 'enable' else 'desactivada'} en el registro."

    if action == "register":
        if not name:
            return "Falta name."
        registry.setdefault("custom", {})[name] = {
            "category": category or "custom",
            "description": description,
            "source": source or "custom",
            "enabled": True,
        }
        _save_registry(registry)
        return f"Herramienta registrada: {name}."

    if action in ("unregister", "remove"):
        if name in registry.get("custom", {}):
            del registry["custom"][name]
            _save_registry(registry)
            return f"Herramienta personalizada eliminada: {name}."
        return f"{name} no es una herramienta personalizada registrada."

    if action == "suggest":
        return (
            "Sugerencias de arquitectura:\n"
            "- Crear un modulo actions/<nombre>.py con una funcion principal del mismo nombre.\n"
            "- Registrarlo con tools_registry action=register para que aparezca en paneles.\n"
            "- Conectarlo en main.py solo cuando ya este probado."
        )

    return f"Accion de registro desconocida: {action}."
