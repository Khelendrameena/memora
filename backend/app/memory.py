"""Memora — agent memory core.

Defines the MemoryStore interface plus a simple in-memory implementation
so the API runs without a database. The pgvector-backed implementation
(Phase 1) will sit behind this same interface.
"""

from __future__ import annotations

import itertools
import time
from dataclasses import dataclass, field


@dataclass
class Memory:
    """A single stored memory."""

    id: int
    text: str
    kind: str = "episode"  # "episode" (raw event) or "fact" (distilled)
    agent: str = "default"  # which agent wrote this memory
    importance: float = 0.5  # 0.0–1.0, updated by consolidation
    created_at: float = field(default_factory=time.time)


class MemoryStore:
    """In-memory memory store.

    Interface contract (the pgvector implementation must match):
      remember(text, kind, agent) -> Memory
      recall(query, limit)        -> list[Memory]
      forget(memory_id)           -> bool
      consolidate()               -> dict (run summary)
    """

    def __init__(self) -> None:
        self._memories: dict[int, Memory] = {}
        self._ids = itertools.count(1)

    def remember(self, text: str, kind: str = "episode", agent: str = "default") -> Memory:
        """Store a new memory and return it.

        In the full implementation this embeds `text`, dedupes against
        near-identical existing memories, and persists to pgvector.
        """
        memory = Memory(id=next(self._ids), text=text, kind=kind, agent=agent)
        self._memories[memory.id] = memory
        return memory

    def recall(self, query: str, limit: int = 5) -> list[Memory]:
        """Return up to `limit` memories relevant to `query`.

        Stub ranking: substring/keyword overlap, newest first.
        The real implementation uses hybrid vector + keyword search
        re-ranked by recency and importance.
        """
        terms = {t.lower() for t in query.split() if t}
        scored = []
        for memory in self._memories.values():
            words = {w.lower().strip(".,!?") for w in memory.text.split()}
            overlap = len(terms & words)
            scored.append((overlap, memory.created_at, memory))
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [memory for _, _, memory in scored[:limit]]

    def forget(self, memory_id: int) -> bool:
        """Permanently delete a memory by id. Returns True if it existed."""
        return self._memories.pop(memory_id, None) is not None

    def consolidate(self) -> dict:
        """Run one consolidation ("sleep") cycle.

        Stub: exact-duplicate texts are merged. The real job also merges
        near-duplicates by embedding similarity, promotes repeated
        episodes into facts, and decays stale low-importance memories.
        Returns a summary dict of what the cycle did.
        """
        seen: dict[str, Memory] = {}
        merged = 0
        for memory in list(self._memories.values()):
            key = memory.text.strip().lower()
            if key in seen:
                self._memories.pop(memory.id, None)
                merged += 1
            else:
                seen[key] = memory
        return {"merged": merged, "promoted": 0, "decayed": 0, "total": len(self._memories)}
