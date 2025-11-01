
"""Simplified async memory manager used during bootstrapping."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List


class MemoryManager:
    """In-memory store for demo purposes."""

    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []
        self._learnings: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def find_similar_events(self, _event: Any) -> List[Dict[str, Any]]:
        async with self._lock:
            return list(self._events)[-3:]

    async def store_learning(self, payload: Dict[str, Any]) -> None:
        async with self._lock:
            self._learnings.append(payload)
