"""beta_config.py — JARVIS Full (sin restricciones Beta)."""
from __future__ import annotations

PRO_TOOLS: set[str] = set()

DAILY_LIMIT = 999999

def is_pro_tool(tool_name: str) -> bool:
    return False

def check_daily_limit() -> tuple[bool, int]:
    return True, 0

def increment_calls() -> int:
    return 0

def pro_tool_message(tool_name: str) -> str:
    return ""

def daily_limit_message(calls: int) -> str:
    return ""
