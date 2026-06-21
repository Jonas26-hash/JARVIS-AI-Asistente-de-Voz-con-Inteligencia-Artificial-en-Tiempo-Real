"""task_queue.py — Background task queue for complex multi-step operations."""
from __future__ import annotations
import asyncio, json, time, uuid
from pathlib import Path
from enum import IntEnum
from typing import Optional


class TaskPriority(IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2


class _TaskQueue:
    def __init__(self):
        self._tasks: dict[str, dict] = {}

    def submit(self, goal: str, priority: TaskPriority = TaskPriority.NORMAL, speak=None) -> str:
        task_id = uuid.uuid4().hex[:8]
        self._tasks[task_id] = {
            "id": task_id,
            "goal": goal,
            "priority": priority,
            "status": "queued",
            "created": time.time(),
        }
        return task_id

    def status(self, task_id: str) -> Optional[dict]:
        return self._tasks.get(task_id)

    def list(self) -> list[dict]:
        return sorted(self._tasks.values(), key=lambda t: (-t["priority"], t["created"]))


_queue: _TaskQueue | None = None


def get_queue() -> _TaskQueue:
    global _queue
    if _queue is None:
        _queue = _TaskQueue()
    return _queue
