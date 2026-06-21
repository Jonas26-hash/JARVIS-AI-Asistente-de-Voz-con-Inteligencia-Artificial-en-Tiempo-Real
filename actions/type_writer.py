"""type_writer.py — Write text on screen via keyboard simulation."""
from __future__ import annotations
import time

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pyperclip
except ImportError:
    pyperclip = None

try:
    from pywinauto.keyboard import send_keys as _win_keys
except ImportError:
    _win_keys = None


def type_text(text: str, press_enter: bool = False, smart: bool = True) -> str:
    """Type text on screen using keyboard simulation.

    Args:
        text: The text to type.
        press_enter: Whether to press Enter after typing.
        smart: If True, use clipboard paste for long text (>20 chars).

    Returns:
        Status message.
    """
    if not text:
        return "No text provided to type."

    # Ensure a brief delay so the target field has focus
    time.sleep(0.5)

    try:
        # Smart paste for long text via clipboard
        if smart and len(text) > 20 and pyperclip:
            try:
                pyperclip.copy(str(text))
                time.sleep(0.15)
                if pyautogui:
                    pyautogui.hotkey("ctrl", "v")
                elif _win_keys:
                    _win_keys("^v")
                else:
                    raise RuntimeError("No keyboard library available")
            except Exception:
                # Fallback to character-by-character
                if pyautogui:
                    pyautogui.typewrite(str(text), interval=0.03)
                elif _win_keys:
                    _win_keys(str(text))
                else:
                    return "Cannot type: no keyboard library available."
        elif pyautogui:
            pyautogui.typewrite(str(text), interval=0.02)
        elif _win_keys:
            _win_keys(str(text))
        else:
            return "Cannot type: no keyboard library available."

        if press_enter:
            time.sleep(0.1)
            if pyautogui:
                pyautogui.press("enter")
            elif _win_keys:
                _win_keys("{ENTER}")

        return f"Escribi: {text[:60]}{'...' if len(text) > 60 else ''}"

    except Exception as e:
        return f"Error al escribir: {e}"


def type_writer(parameters=None, player=None, **kwargs) -> str:
    """Tool function: writes text on screen by simulating keyboard input.

    Expected parameters:
        - text: The text to type (required).
        - press_enter: Whether to press Enter after typing (optional, default false).

    Returns:
        Confirmation text.
    """
    if parameters is None:
        parameters = {}

    text = parameters.get("text") or parameters.get("value", "")
    if not text:
        return "Necesito el texto que quieres que escriba."

    press_enter = str(parameters.get("press_enter", "false")).lower() in (
        "true", "1", "yes"
    )

    return type_text(text, press_enter=press_enter)


if __name__ == "__main__":
    print(type_text("Hello world", press_enter=True))
