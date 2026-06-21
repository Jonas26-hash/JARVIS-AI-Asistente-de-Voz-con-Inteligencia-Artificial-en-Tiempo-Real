"""screen_reader.py — Screen reader functionality."""
from __future__ import annotations


def screen_reader(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    try:
        import pyautogui
        import pytesseract
        from PIL import Image
    except ImportError:
        return "Falta pytesseract o pyautogui."
    try:
        screenshot = pyautogui.screenshot()
        text = pytesseract.image_to_string(screenshot)
        if text.strip():
            return f"Texto detectado en pantalla:\n{text[:2000]}"
        return "No se detectó texto en pantalla."
    except Exception as e:
        return f"Error: {e}"
