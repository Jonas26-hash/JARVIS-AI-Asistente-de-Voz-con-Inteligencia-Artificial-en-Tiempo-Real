"""tiktok_analyzer.py — TikTok profile analyzer (public data via Playwright)."""
from __future__ import annotations
import time, re
from pathlib import Path


def tiktok_analyzer(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    profile_url = parameters.get("profile_url", "")
    max_videos = parameters.get("max_videos", 8)

    if not profile_url:
        return "Falta profile_url (ej: https://www.tiktok.com/@usuario)."

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return "Playwright no instalado."

    info = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(profile_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            text = page.inner_text("body")
            name = re.search(r'@(\w+)', text)
            followers = re.search(r'([\d,.KM]+)\s*Followers', text, re.IGNORECASE)
            following = re.search(r'([\d,.KM]+)\s*Following', text, re.IGNORECASE)
            likes = re.search(r'([\d,.KM]+)\s*Likes', text, re.IGNORECASE)
            info.append(f"Perfil: @{name.group(1) if name else 'desconocido'}")
            if followers: info.append(f"Seguidores: {followers.group(1)}")
            if following: info.append(f"Siguiendo: {following.group(1)}")
            if likes: info.append(f"Likes totales: {likes.group(1)}")
            video_links = page.locator('a[href*="/video/"]').all()[:max_videos]
            if video_links:
                info.append(f"\nVideos recientes ({len(video_links)}):")
                for v in video_links[:max_videos]:
                    href = v.get_attribute("href") or ""
                    vid_id = href.split("/video/")[-1] if "/video/" in href else "?"
                    info.append(f"  - Video ID: {vid_id[:15]}")
        except Exception as e:
            info.append(f"Error al analizar: {e}")
        finally:
            browser.close()

    return "\n".join(info) if info else "No se pudo analizar el perfil."
