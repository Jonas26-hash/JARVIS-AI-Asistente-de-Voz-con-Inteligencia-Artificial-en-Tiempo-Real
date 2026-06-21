"""sounds.py — Futuristic Iron Man / system-style ambient sounds."""
from __future__ import annotations
import numpy as np
import threading
from pathlib import Path

_SAMPLE_RATE = 44100
_PLAYING = threading.Event()
_BASE_DIR = Path(__file__).resolve().parent.parent

# ── Initialize pygame mixer once (separate from sounddevice streams) ──
_PYGAME_OK = False
try:
    import pygame
    pygame.mixer.init(frequency=_SAMPLE_RATE, size=-16, channels=1, buffer=512)
    _PYGAME_OK = True
except Exception:
    pass


def _play(wave: np.ndarray):
    if wave.size == 0:
        return
    _PLAYING.set()
    if not _PYGAME_OK:
        return
    try:
        if wave.dtype in (np.float32, np.float64):
            wave = np.clip(wave * 32767, -32768, 32767).astype(np.int16)
        pygame.mixer.Sound(wave).play()
    except Exception:
        pass


def _sine(freq: float, duration: float, attack: float = 0.005, release: float = 0.01, amp: float = 0.3) -> np.ndarray:
    n = int(_SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    env = np.ones(n)
    a = max(1, int(_SAMPLE_RATE * attack))
    r = max(1, int(_SAMPLE_RATE * release))
    env[:a] = np.linspace(0, 1, a)
    env[-r:] = np.linspace(1, 0, r)
    return np.sin(2 * np.pi * freq * t) * env * amp

def _square(freq: float, duration: float, amp: float = 0.2) -> np.ndarray:
    n = int(_SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    wave = np.sign(np.sin(2 * np.pi * freq * t)) * amp
    a = max(1, int(_SAMPLE_RATE * 0.002))
    env = np.ones(n)
    env[:a] = np.linspace(0, 1, a)
    return wave * env * 0.5

def _echo(wave: np.ndarray, delay: float = 0.08, decay: float = 0.4) -> np.ndarray:
    d = int(_SAMPLE_RATE * delay)
    out = np.copy(wave)
    for i in range(3):
        pad = np.zeros(d * (i + 1))
        echo = np.concatenate([pad, wave * (decay ** (i + 1))])
        if len(echo) > len(out):
            out = np.pad(out, (0, len(echo) - len(out)))
        out[:len(echo)] += echo
    return out

def notification():
    """Clean digital chime — system notification."""
    a = _sine(1047, 0.08, amp=0.25)
    gap = np.zeros(int(_SAMPLE_RATE * 0.04))
    b = _sine(1319, 0.12, amp=0.25)
    wave = np.concatenate([a, gap, b])
    threading.Thread(target=_play, args=(_echo(wave),), daemon=True).start()

def action_start():
    """Quick ascending computer tones — system initializing."""
    notes = [523, 659, 784, 1047]
    parts = []
    for f in notes:
        parts.append(_sine(f, 0.06, amp=0.2))
        parts.append(np.zeros(int(_SAMPLE_RATE * 0.015)))
    threading.Thread(target=_play, args=(np.concatenate(parts),), daemon=True).start()

def action_complete():
    """Satisfying descending confirmation with reverb."""
    a = _sine(1319, 0.15, amp=0.25)
    b = _sine(988, 0.25, amp=0.2)
    gap = np.zeros(int(_SAMPLE_RATE * 0.03))
    wave = np.concatenate([a, gap, b])
    threading.Thread(target=_play, args=(_echo(wave, 0.12, 0.3),), daemon=True).start()

def error():
    """Low authoritative alert tone."""
    n = int(_SAMPLE_RATE * 0.25)
    t = np.linspace(0, 0.25, n)
    wave = np.sin(2 * np.pi * 180 * t) * 0.3 + np.sin(2 * np.pi * 220 * t) * 0.15
    a = int(_SAMPLE_RATE * 0.003)
    env = np.ones(n)
    env[:a] = np.linspace(0, 1, a)
    wave *= env
    threading.Thread(target=_play, args=(wave,), daemon=True).start()

def startup():
    """JARVIS iconic startup sequence — layered arpeggio."""
    notes = [262, 330, 392, 523, 659, 784, 1047, 1319]
    parts = []
    for i, f in enumerate(notes):
        t = 0.07 + (i * 0.002)
        parts.append(_sine(f, t, amp=0.25))
        parts.append(np.zeros(int(_SAMPLE_RATE * 0.02)))
    wave = np.concatenate(parts)
    threading.Thread(target=_play, args=(_echo(wave, 0.1, 0.25),), daemon=True).start()

def is_playing() -> bool:
    return _PLAYING.is_set()

def action_custom():
    """Play the custom MP3 sound from assets/sonido_jarvis.MP3."""
    mp3 = _BASE_DIR / "assets" / "sonido_jarvis.MP3"
    if not mp3.exists():
        action_start()
        return
    if not _PYGAME_OK:
        action_start()
        return
    try:
        pygame.mixer.music.load(str(mp3))
        pygame.mixer.music.play()
    except Exception:
        action_start()
