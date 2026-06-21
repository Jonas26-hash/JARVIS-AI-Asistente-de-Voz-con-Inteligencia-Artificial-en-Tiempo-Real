"""image_generation.py — AI image generation via Pollinations.ai (free, no API key)."""
from __future__ import annotations
import requests, os, json, uuid
from pathlib import Path
from datetime import datetime


def image_generation(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    prompt = parameters.get("prompt", "")
    if not prompt:
        return "Necesito una descripción para generar la imagen."
    count = min(parameters.get("count", 1), 4)
    aspect = parameters.get("aspect_ratio", "1:1")
    save_path = parameters.get("save_path", str(Path.home() / "Pictures" / "JARVIS_Generadas"))

    os.makedirs(save_path, exist_ok=True)
    results = []

    for i in range(count):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
            if aspect != "1:1":
                url += f"?ratio={aspect}"
            resp = requests.get(url, timeout=60, stream=True)
            if resp.status_code == 200:
                fname = f"jarvis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.jpg"
                fpath = os.path.join(save_path, fname)
                with open(fpath, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                results.append(fpath)
                if player:
                    try:
                        player.show_image([fpath])
                    except Exception:
                        pass
                    player.write_log(f"🎨 Imagen generada: {fpath}")
            else:
                results.append(f"Error HTTP {resp.status_code}")
        except Exception as e:
            results.append(f"Error: {e}")

    if results:
        msg = f"Generad{'a' if count == 1 else 'as'} {len(results)} imagen{'es' if count > 1 else ''} en {save_path}."
        return msg
    return "No se pudo generar la imagen."
