"""flight_finder.py — Google Flights search via Playwright."""
from __future__ import annotations
import time
from pathlib import Path


def flight_finder(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    origin = parameters.get("origin", "")
    destination = parameters.get("destination", "")
    date = parameters.get("date", "")
    return_date = parameters.get("return_date", "")
    passengers = parameters.get("passengers", 1)
    cabin = parameters.get("cabin", "economy")

    if not all([origin, destination, date]):
        return "Falta origin, destination o date."

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return "Playwright no instalado."

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            url = f"https://www.google.com/travel/flights?q=Flights+to+{destination}+from+{origin}+on+{date}"
            if return_date:
                url += f"+return+{return_date}"
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            cards = page.locator('[role="listitem"]').all()
            for card in cards[:5]:
                text = card.inner_text()
                if text.strip():
                    results.append(text.strip()[:200])
        except Exception as e:
            results.append(f"Error: {e}")
        finally:
            browser.close()

    if results:
        return "Vuelos encontrados:\n" + "\n---\n".join(results[:5])
    return f"No se encontraron vuelos para {origin} → {destination} el {date}. Podés intentar de nuevo manualmente."
