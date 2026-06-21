"""memory_panel.py - Editable long-term memory actions for JARVIS."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path


_MEMORY_FILE = Path(__file__).resolve().parent.parent / "memory" / "long_term.json"
_DEFAULT_CATEGORIES = ("identity", "preferences", "projects", "relationships", "wishes", "notes")


def _load_memory() -> dict:
    try:
        data = json.loads(_MEMORY_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for category in _DEFAULT_CATEGORIES:
                data.setdefault(category, {})
            return data
    except Exception:
        pass
    return {category: {} for category in _DEFAULT_CATEGORIES}


def _save_memory(memory: dict) -> None:
    _MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _MEMORY_FILE.write_text(json.dumps(memory, indent=2, ensure_ascii=False), encoding="utf-8")


def _entry_value(entry):
    if isinstance(entry, dict) and "value" in entry:
        return entry.get("value", "")
    return entry


def _flatten(memory: dict) -> list[tuple[str, str, str]]:
    rows = []
    for category, values in memory.items():
        if not isinstance(values, dict):
            continue
        for key, entry in values.items():
            rows.append((category, key, str(_entry_value(entry))))
    return rows


def memory_panel(parameters=None, player=None, **kwargs):
    """List, edit, and delete long-term memory entries."""
    if parameters is None:
        parameters = {}

    action = str(parameters.get("action", "list")).lower()
    category = str(parameters.get("category", "")).strip() or "notes"
    key = str(parameters.get("key", "")).strip()
    value = parameters.get("value", "")
    query = str(parameters.get("query", "")).strip().lower()

    memory = _load_memory()

    if action in ("categories", "schema"):
        return "Categorias de memoria:\n" + "\n".join(f"- {name}" for name in memory.keys())

    if action in ("list", "show"):
        rows = _flatten(memory)
        if query:
            rows = [row for row in rows if query in row[0].lower() or query in row[1].lower() or query in row[2].lower()]
        if category and category != "all" and not query:
            rows = [row for row in rows if row[0] == category]
        if not rows:
            return "No hay recuerdos guardados para ese filtro."
        return "Memoria editable:\n" + "\n".join(f"- {cat}.{k}: {v}" for cat, k, v in rows[:80])

    if action == "get":
        if not key:
            return "Falta key."
        entry = memory.get(category, {}).get(key)
        if entry is None:
            return f"No encontre {category}.{key}."
        return f"{category}.{key}: {_entry_value(entry)}"

    if action in ("set", "save", "update"):
        if not key:
            return "Falta key."
        memory.setdefault(category, {})
        memory[category][key] = {
            "value": value,
            "updated": str(date.today()),
        }
        _save_memory(memory)
        if player and hasattr(player, "refresh_memory_panel"):
            try:
                player.refresh_memory_panel()
            except Exception:
                pass
        return f"Memoria actualizada: {category}.{key}."

    if action in ("delete", "remove"):
        if not key:
            return "Falta key."
        if key not in memory.get(category, {}):
            return f"No encontre {category}.{key}."
        del memory[category][key]
        _save_memory(memory)
        if player and hasattr(player, "refresh_memory_panel"):
            try:
                player.refresh_memory_panel()
            except Exception:
                pass
        return f"Memoria eliminada: {category}.{key}."

    if action == "clear_category":
        if category not in memory:
            return f"Categoria desconocida: {category}."
        memory[category] = {}
        _save_memory(memory)
        return f"Categoria limpiada: {category}."

    return f"Accion de memoria desconocida: {action}."
