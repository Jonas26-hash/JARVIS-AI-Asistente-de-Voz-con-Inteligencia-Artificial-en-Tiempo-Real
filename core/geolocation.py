"""geolocation.py — Detecta ubicación actual con respaldo manual desde config."""
from __future__ import annotations
import json, threading
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"

_LOCATION = {
    "city": "Lima",
    "district": "",
    "country": "Perú",
    "lat": -12.119,
    "lon": -77.030,
    "source": "config",
}

def _load_config_fallback():
    try:
        cfg = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
        _LOCATION["city"] = cfg.get("location_city", "Lima")
        _LOCATION["district"] = cfg.get("location_district", "") if cfg.get("location_include_district", False) else ""
        _LOCATION["country"] = cfg.get("location_country", "Perú")
        _LOCATION["source"] = "config"
        return bool(cfg.get("location_use_ip", False))
    except Exception:
        return False

def _detect_from_ip():
    try:
        import urllib.request
        resp = urllib.request.urlopen("http://ip-api.com/json/?fields=city,district,lat,lon,status", timeout=5)
        data = json.loads(resp.read().decode())
        if data.get("status") == "success":
            _LOCATION["city"] = data.get("city", _LOCATION["city"])
            _LOCATION["district"] = data.get("district", "") or _LOCATION["district"]
            _LOCATION["lat"] = data.get("lat", _LOCATION["lat"])
            _LOCATION["lon"] = data.get("lon", _LOCATION["lon"])
            _LOCATION["source"] = "ip"
            return True
    except Exception:
        pass
    return False

def detect():
    use_ip = _load_config_fallback()
    if use_ip:
        _detect_from_ip()
    return _LOCATION.copy()

def get_location_str() -> str:
    loc = _LOCATION
    if loc["district"] and loc["district"] != loc["city"]:
        return f"{loc['district']}, {loc['city']}"
    if loc.get("country"):
        return f"{loc['city']}, {loc['country']}"
    return loc["city"]

def detect_async(callback=None):
    def _run():
        use_ip = _load_config_fallback()
        if use_ip:
            _detect_from_ip()
        if callback:
            callback(_LOCATION.copy())
    threading.Thread(target=_run, daemon=True).start()
