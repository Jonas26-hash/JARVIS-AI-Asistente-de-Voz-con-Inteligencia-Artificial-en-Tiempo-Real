"""weather_report.py — Override del .pyc original: usa ubicación manual estable."""
from __future__ import annotations
import importlib.util, sys, json
from pathlib import Path

_MODULE_PATH = Path(__file__).resolve()
_BASE_DIR    = _MODULE_PATH.parent.parent
_CONFIG_PATH = _BASE_DIR / "config" / "api_keys.json"

_orig = None

def _get_current_location() -> str:
    try:
        from core.geolocation import detect, get_location_str
        detect()
        return get_location_str()
    except Exception:
        pass
    try:
        cfg = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
        city = cfg.get("location_city", "Lima")
        country = cfg.get("location_country", "Perú")
        dist = cfg.get("location_district", "") if cfg.get("location_include_district", False) else ""
        if dist and dist != city:
            return f"{dist}, {city}"
        return f"{city}, {country}" if country else city
    except Exception:
        return "Lima, Perú"

def weather_action(parameters: dict, response=None, player=None, session_memory=None) -> str:
    global _orig
    if _orig is None:
        spec = importlib.util.spec_from_file_location(
            "weather_report_orig",
            str(_MODULE_PATH.with_suffix(".pyc"))
        )
        _orig = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_orig)

    loc = _get_current_location()
    if not parameters.get("city") or parameters["city"] in ("", "ubicación actual", "mi ciudad"):
        parameters["city"] = loc
    return _orig.weather_action(parameters=parameters, response=response, player=player, session_memory=session_memory)
