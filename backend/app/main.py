"""Memora API — minimal skeleton.

Run from the backend/ directory:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel

from .memory import MemoryStore

app = FastAPI(title="Memora", description="An agent memory OS — agents that never forget.")
store = MemoryStore()


class RememberRequest(BaseModel):
    text: str
    kind: str = "episode"
    agent: str = "default"


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "memora"}


@app.post("/memory")
def remember(req: RememberRequest) -> dict:
    memory = store.remember(req.text, kind=req.kind, agent=req.agent)
    return {"id": memory.id, "text": memory.text, "kind": memory.kind, "agent": memory.agent}


@app.get("/memory/search")
def search(q: str, limit: int = 5) -> dict:
    results = store.recall(q, limit=limit)
    return {"results": [{"id": m.id, "text": m.text, "kind": m.kind} for m in results]}


@app.delete("/memory/{memory_id}")
def forget(memory_id: int) -> dict:
    return {"forgotten": store.forget(memory_id)}


@app.post("/memory/consolidate")
def consolidate() -> dict:
    return store.consolidate()
