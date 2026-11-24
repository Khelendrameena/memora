# Memora — An Agent Memory OS

> **AI agents that never forget.**
> Built for **ContextCon: Remember Everything** (HackerEarth × YugabyteDB).

Most AI agents wake up with amnesia. Every session starts from zero — the user repeats themselves, the agent re-learns the same facts, and anything that happened yesterday might as well not exist.

**Memora fixes that.** It is a memory layer ("memory OS") that sits underneath any LLM agent and gives it a brain that works the way human memory does:

- **Episodic memory** — what happened, when, and in what context ("on Tuesday the user said their deploy broke").
- **Semantic memory** — durable facts distilled from episodes ("the user deploys on Render, prefers Hinglish replies").
- **Consolidation** — a nightly "sleep" cycle that merges duplicates, promotes repeated episodes into facts, and decays stale memories.
- **Shared memory** — multiple agents (support agent, planner agent, coding agent) read and write one common memory, so knowledge transfers between them.
- **A visible timeline** — users can *see* what the agent remembers, correct it, or make it forget. Memory you can audit, not a black box.

---

## Architecture

```
                        ┌──────────────────────────────────────────┐
                        │            Any LLM Agent(s)              │
                        │   Support Agent   Planner   Code Agent   │
                        └───────┬──────────────────┬───────────────┘
                                │ remember()       │ recall(query)
                                ▼                  ▲
┌───────────────────────────────────────────────────────────────────────┐
│                        MEMORA  MEMORY  OS                             │
│                                                                       │
│   ┌────────────────┐   ┌────────────────┐   ┌──────────────────────┐  │
│   │  Write Path    │   │  Recall Path   │   │  Consolidation Job   │  │
│   │  extract facts │   │  hybrid search │   │  (nightly "sleep")   │  │
│   │  embed, dedupe │   │  vector + BM25 │   │  merge · promote ·   │  │
│   │  tag episode   │   │  + recency &   │   │  decay · summarise   │  │
│   │                │   │  importance    │   │                      │  │
│   └───────┬────────┘   └───────┬────────┘   └──────────┬───────────┘  │
│           │                    │                       │              │
│           ▼                    ▼                       ▼              │
│   ┌───────────────────────────────────────────────────────────────┐   │
│   │        PostgreSQL + pgvector  (episodes + facts)              │   │
│   │        Redis  (working memory / session cache)                │   │
│   └───────────────────────────────────────────────────────────────┘   │
│                                                                       │
│   ┌───────────────────────────────────────────────────────────────┐   │
│   │   Memory Timeline API  — list · search · edit · forget        │   │
│   └───────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────┘
                                ▲
                                │  "Show me what you remember about me"
                        ┌───────┴────────┐
                        │  Timeline UI   │   (React)
                        └────────────────┘
```

---

## Features

- **Persistent episodic + semantic memory** — raw events and distilled facts stored side-by-side in PostgreSQL + pgvector.
- **Nightly consolidation ("sleep")** — a background job that clusters near-duplicate memories, merges them, promotes frequently-reinforced episodes into semantic facts, and decays low-importance stale ones — modelled on how human memory consolidates during sleep.
- **Hybrid recall** — vector similarity (pgvector) + keyword (BM25-style) retrieval, re-ranked by recency and importance, so the agent recalls what *matters*, not just what *matches*.
- **Multi-agent shared memory** — namespaced per-user, shared across agents: tell the planner agent your budget once, the support agent already knows it.
- **Memory timeline UI** — a visual feed of everything the agent remembers; users can edit a memory, pin it, or delete it ("forget this"). Full user control = trust.
- **Importance scoring** — every memory carries an importance score that consolidation updates over time.
- **Pluggable LLM** — Gemini API for fact extraction and consolidation summaries; the memory core itself is model-agnostic.

## Demo idea

> **Day 1:** The user chats with a support agent powered by Memora. They mention their project is called *SupportIQ*, they deploy on Render, and their demo broke yesterday because of a CORS error.
> **That night:** Memora's consolidation job merges the scattered mentions into clean facts and marks the CORS issue as an open episode.
> **Day 2:** The user opens a *different* agent (a planning agent). Without being told anything, it greets them: *"How's SupportIQ going — did the Render CORS issue get fixed?"*
> Then the user opens the **Memory Timeline**, sees exactly which memories produced that greeting, edits one, and deletes another — and the agent's behaviour changes accordingly.

One user. Two agents. One shared, visible, editable memory.

## Tech stack

| Layer | Choice |
|---|---|
| API | FastAPI (Python) |
| Memory store | PostgreSQL + pgvector (episodes + semantic facts) |
| Working memory / cache | Redis |
| LLM | Gemini API (fact extraction, consolidation summaries) |
| Embeddings | Gemini / local model (pluggable) |
| Frontend | React (memory timeline UI) — Phase 4 |
| Jobs | Nightly consolidation worker |

## How Memora differs from a plain RAG chatbot

| | Plain RAG chatbot | Memora |
|---|---|---|
| What it stores | Static documents you upload | Lived experience: episodes from conversations, written automatically |
| Memory across sessions | None (or raw chat history dumped into context) | Curated, consolidated facts that survive and evolve |
| Duplicates & contradictions | Accumulate forever | Nightly consolidation merges, dedupes, and resolves them |
| Multiple agents | Each agent is an island | All agents share one memory per user |
| User visibility | Black box | Timeline UI: see, edit, pin, or forget any memory |
| Forgetting | Delete the whole history or nothing | Importance decay + per-memory forget |

RAG answers questions about documents. **Memora remembers a user.**

## Status

Hackathon scaffold — Phase 1 (memory core) in progress. See [PLAN.md](PLAN.md) for the build plan mapped to the 17 Jan 2027 deadline.

## Author

Khelendra Meena — B.Tech CSE, JECRC Jaipur · [github.com/Khelendrameena](https://github.com/Khelendrameena)
