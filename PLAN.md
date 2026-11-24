# Memora — Build Plan

**Event:** ContextCon: Remember Everything (HackerEarth × YugabyteDB)
**Deadline: 17 Jan 2027, 11:00 PM IST**
**Strategy:** build the memory core first (it demos well even without a UI), UI last.

---

## Phase 1 — Memory Core (store / recall / forget)
*Target: by ~20 Dec 2026*

- [ ] `MemoryStore` interface: `remember / recall / forget / consolidate` (skeleton done — in-memory impl)
- [ ] PostgreSQL + pgvector schema: `episodes` and `facts` tables (embedding, importance, timestamps, source agent)
- [ ] Swap in-memory store for pgvector-backed store behind the same interface
- [ ] Embedding pipeline (Gemini embeddings) on the write path
- [ ] Fact extraction: LLM pass that pulls durable facts out of a conversation turn
- [ ] Hybrid recall: vector search + keyword match, re-ranked by recency × importance
- [ ] `forget` endpoint: hard-delete a memory by id (user control)
- [ ] API endpoints: `POST /memory`, `GET /memory/search`, `DELETE /memory/{id}`
- [ ] Tests: remember → recall round-trip, forget actually removes

## Phase 2 — Consolidation Job ("sleep cycle")
*Target: by ~31 Dec 2026*

- [ ] Nightly worker (cron / background task) that scans a user's memories
- [ ] Near-duplicate detection (embedding similarity threshold) → merge into one memory
- [ ] Promotion rule: episodes reinforced ≥ N times become semantic facts
- [ ] Importance decay for stale, never-recalled memories
- [ ] Contradiction handling: newer fact supersedes older one, old one kept in history
- [ ] Consolidation run log (what was merged/promoted/decayed) — this is demo gold
- [ ] Manual trigger endpoint `POST /memory/consolidate` for the demo

## Phase 3 — Multi-Agent Shared Memory
*Target: by ~7 Jan 2027*

- [ ] Per-user memory namespace shared across agents; per-agent write tags (provenance)
- [ ] Two demo agents on one memory: a support agent + a planning agent
- [ ] Cross-agent test: fact told to Agent A is recalled by Agent B
- [ ] Agent-scoped recall filters (an agent can prefer its own episodes)

## Phase 4 — Memory Timeline UI
*Target: by ~12 Jan 2027*

- [ ] React app: chronological timeline of memories (episodes vs facts visually distinct)
- [ ] Search / filter the timeline
- [ ] Edit a memory inline; pin (protect from decay); delete (forget)
- [ ] Consolidation log view ("last night your agent merged 6 memories into 2 facts")
- [ ] Chat panel wired to a demo agent so the timeline updates live

## Phase 5 — Demo + Submission
*Target: 13–17 Jan 2027 (buffer included)*

- [ ] Record demo video (Day 1 chat → overnight consolidation → Day 2 cross-agent recall → timeline edit/forget)
- [ ] README final pass: architecture, setup instructions, screenshots/GIF
- [ ] One-command local run (docker compose: API + Postgres/pgvector + Redis)
- [ ] Clean repo, tagged release
- [ ] Submit on HackerEarth **before** 17 Jan 2027, 11:00 PM IST — aim for 16 Jan

---

## Risks / notes

- pgvector setup is the main infra risk — keep the in-memory implementation as a fallback demo path.
- Demo must not depend on live "overnight" waiting: the manual consolidate trigger exists for exactly this.
- Everything user-facing about memory must be honest: if it isn't stored, the agent shouldn't claim to remember it.
