# Paper Brain — Project Roadmap

**Theme:** Industrial Knowledge Intelligence  
**Stack:** FastAPI + LangGraph + Neo4j + Qdrant + Gemini 2.5 Flash + Next.js 16  
**Judging:** Innovation 25% | Business Impact 25% | Technical Excellence 20% | Scalability 15% | UX 15%

---

## Progress Legend
- [x] Complete
- [ ] Pending

---

## Phase 0 — Environment & Infrastructure
**Goal:** Full dev environment running before any code.

- [x] Python 3.11 venv in `backend/`
- [x] All backend pip dependencies installed (`requirements.txt` frozen)
- [x] Next.js 16 scaffolded in `frontend/` (TypeScript + Tailwind + App Router)
- [x] Docker Desktop + WSL2 repaired
- [x] Neo4j container running (`paperbrain-neo4j`, bolt://localhost:7687)
- [x] Qdrant container running (`paperbrain-qdrant`, :6333)
- [x] Google Cloud project `paper-brain-491913` configured
- [x] Service account JSON in `backend/service-account.json`
- [x] All Google APIs enabled (Document AI, Speech-to-Text, Vertex AI)
- [x] Document AI processor `paper-brain-ocr` created (ID: `2e31dd363211f4a8`)
- [x] Seed CSV files: `data/seed/assets_seed.csv` + `data/seed/topology_seed.csv`

### ✅ Phase 0 Test Checkpoint
```powershell
# All must return OK
python -c "import fastapi, langgraph, neo4j, qdrant_client; print('Python deps OK')"
docker ps --filter "name=paperbrain"   # both containers listed
curl http://localhost:7474              # Neo4j browser responds
curl http://localhost:6333/collections # Qdrant responds
```

---

## Phase 1 — FastAPI Backend Core
**Goal:** All 6 API endpoints live, GraphRAG pipeline working.

- [x] `backend/config.py` — Pydantic Settings, `.env` loader
- [x] `backend/models/schemas.py` — all request/response Pydantic models
- [x] `backend/database/neo4j_client.py` — async driver, constraint creation
- [x] `backend/database/qdrant_client.py` — async client, collection init
- [x] `backend/services/gemini_service.py` — `chat_complete` + NER extraction (google.genai SDK)
- [x] `backend/services/embedding_service.py` — `text-embedding-004` via Vertex AI
- [x] `backend/services/documentai_service.py` — PDF OCR + chunking
- [x] `backend/services/speech_service.py` — Google Cloud Speech-to-Text
- [x] `backend/pipelines/ingestion_pipeline.py` — PDF → OCR → embed → Qdrant + Neo4j
- [x] `backend/pipelines/voice_pipeline.py` — Audio → STT → NER → KnowledgeObservation
- [x] `backend/pipelines/graphrag_pipeline.py` — LangGraph router (vector/graph/hybrid)
- [x] `backend/routers/seed.py` — CSV → Neo4j MERGE
- [x] `backend/routers/ingest.py` — `/ingest/document` + `/ingest/voice`
- [x] `backend/routers/query.py` — `/query` GraphRAG endpoint
- [x] `backend/routers/graph.py` — `/graph/asset/{tag_number}`
- [x] `backend/main.py` — FastAPI app, lifespan, CORS, `/health`

### ✅ Phase 1 Test Checkpoint
```powershell
# Start server
cd backend; .\venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000

# Run all checks
curl http://localhost:8000/health
# Expected: {"status":"healthy","neo4j":true,"qdrant":true,"gemini":true}

curl -X POST http://localhost:8000/seed
# Expected: {"assets_created":3,"relationships_created":2,...}

curl http://localhost:8000/graph/asset/P-101
# Expected: asset=P-101, connections=[V-20, B-04]

curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What happens if Valve V-20 trips?"}'
# Expected: route_taken="graph", latency < 5s

# FastAPI docs (interactive UI)
open http://localhost:8000/docs
```

---

## Phase 2 — Demo Data Ingestion
**Goal:** Load real documents so queries return meaningful answers.

- [ ] Create `data/docs/OEM-XR-900-Pump-Manual.pdf` — either real or a 2-page synthetic PDF with diagnostic text (vibration specs, valve upstream dependency)
- [ ] Create `data/docs/Tribal-Bob-Notes.txt` (or synthesize from the JSON seed) with voice-note-style text about V-20 causing P-101 cavitation
- [ ] Ingest pump manual via `POST /ingest/document` with `asset_tag=P-101`
- [ ] Ingest tribal note via `POST /ingest/voice` (or as document if no audio file available)
- [ ] Confirm Qdrant collection has > 0 vectors: `curl http://localhost:6333/collections/paper_brain_chunks`
- [ ] Confirm Neo4j has `DocumentChunk` and `KnowledgeObservation` nodes linked to `P-101`

### ✅ Phase 2 Test Checkpoint
```powershell
# Query that needs vector knowledge
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the torque specs for the XR-900 pump?"}'
# Expected: route_taken="vector", answer contains actual spec text

# Hybrid query — the key hackathon demo query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What happens if Valve V-20 trips and what does the manual say?"}'
# Expected: route_taken="hybrid", answer cites topology + document source

# Check Neo4j graph is enriched
curl http://localhost:8000/graph/asset/P-101
# Expected: observations=["...cavitation..."], document_sources=["OEM-XR-900-Pump-Manual.pdf"]
```

---

## Phase 3 — Frontend Core UI
**Goal:** Functional Next.js interface covering the 3 main user flows.

### 3.1 Project Setup
- [ ] Install additional packages: `npm install reactflow @tanstack/react-query axios lucide-react clsx`
- [ ] Create `frontend/src/lib/api.ts` — typed axios client pointing to `http://localhost:8000`
- [ ] Wrap `layout.tsx` with `QueryClientProvider`

### 3.2 Pages
- [ ] **`/` — Query Interface (Hero)** — search bar, answer card, route badge, source list
- [ ] **`/graph` — Asset Explorer** — asset lookup by tag, topology card, connections list
- [ ] **`/ingest` — Knowledge Ingestion** — PDF drag-drop upload + voice recorder tab

### 3.3 Shared Components
- [ ] `components/QueryBar.tsx` — input + submit, loading state
- [ ] `components/AnswerCard.tsx` — answer text, route badge (vector/graph/hybrid), latency chip, sources
- [ ] `components/AssetCard.tsx` — tag, model, manufacturer, emissions badge
- [ ] `components/ConnectionsList.tsx` — upstream/downstream connections with direction arrows
- [ ] `components/DocumentUploader.tsx` — drag-and-drop PDF, optional asset tag field, progress
- [ ] `components/VoiceRecorder.tsx` — browser MediaRecorder, record/stop, upload to `/ingest/voice`
- [ ] `components/RouteBadge.tsx` — color-coded pill: blue=vector, orange=graph, purple=hybrid

### 3.4 Frontend File Structure
```
frontend/src/
├── app/
│   ├── layout.tsx          (QueryClientProvider wrapper)
│   ├── page.tsx            (Query Interface — hero page)
│   ├── graph/page.tsx      (Asset Explorer)
│   └── ingest/page.tsx     (Knowledge Ingestion)
├── components/
│   ├── QueryBar.tsx
│   ├── AnswerCard.tsx
│   ├── AssetCard.tsx
│   ├── ConnectionsList.tsx
│   ├── DocumentUploader.tsx
│   ├── VoiceRecorder.tsx
│   ├── RouteBadge.tsx
│   └── NavBar.tsx
└── lib/
    └── api.ts              (typed API client)
```

### ✅ Phase 3 Test Checkpoint
```bash
cd frontend && npm run dev   # http://localhost:3000

# Manual UI tests:
# [ ] Type a question in the query bar → answer appears with route badge
# [ ] Navigate to /graph, enter "P-101" → asset card + connections show
# [ ] Navigate to /ingest, upload a PDF → success toast with chunk count
# [ ] On /ingest voice tab, record 5 seconds → transcript + observation_id shown
# [ ] No console errors in browser DevTools
# [ ] TypeScript compiles clean: npm run build
```

---

## Phase 4 — Backend-Frontend Integration Polish
**Goal:** Smooth end-to-end flows, no rough edges for demo.

- [ ] Add streaming support to `/query` endpoint (Server-Sent Events) for progressive answer rendering
- [ ] Add `/graph/topology` endpoint returning all assets + all edges for full graph visualization
- [ ] Add React Flow topology visualization on `/graph` page (nodes = assets, edges = CONNECTED_TO)
- [ ] Add emissions CO₂ badge color-coding (green/amber/red based on `base_emissions_co2_ppm`)
- [ ] Add `/seed` button on `/ingest` page with confirmation modal (for demo reset)
- [ ] Error boundaries and loading skeletons on all pages
- [ ] Tailwind dark/industrial color theme (slate-900 background, amber accents)

### ✅ Phase 4 Test Checkpoint
```bash
# Full demo run-through:
# [ ] Fresh seed via UI → confirms 3 assets / 2 relationships
# [ ] Upload pump manual PDF → ingestion success
# [ ] Query: "What shuts down if Boiler 4 trips?" → hybrid route, traces topology
# [ ] Query: "What is the operating pressure for P-101?" → vector route, cites manual
# [ ] Graph page shows all 3 assets with topology arrows
# [ ] Voice note recorded in browser → KnowledgeObservation linked to P-101
# [ ] Response latency < 5s shown on answer card
# [ ] Page reloads without losing state (react-query cache)
```

---

## Phase 5 — Demo Hardening & Presentation Prep
**Goal:** Bullet-proof demo, presentation materials ready.

- [ ] Add `data/demo/` folder with pre-prepared PDF and audio file for offline demo
- [ ] Add `POST /demo/load` endpoint that ingests the demo files in one call (idempotent)
- [ ] Test full flow on a fresh Neo4j + Qdrant reset: `docker restart paperbrain-neo4j paperbrain-qdrant`
- [ ] Screenshot every page for the presentation deck
- [ ] Record a 3-minute demo video covering all 3 user flows
- [ ] Draft Architecture Diagram slide (use `ARCHITECTURE.md` stack diagram as base)
- [ ] Prepare the "3 killer stats" slide: 35% hours lost / 18-22% unplanned downtime / knowledge cliff
- [ ] Prepare the live demo script with fallback screenshots if network fails

### ✅ Phase 5 Test Checkpoint (Full Demo Dry Run)
```
Simulate judging panel demo in order:

1. Open http://localhost:3000 (hero page)
2. Click "Seed Knowledge Graph" → 3 assets, 2 connections confirmed
3. Upload OEM-XR-900-Pump-Manual.pdf on /ingest page
4. Record voice note: "Pump P-101 shows vibration at high thermal loads.
   Operator manually opens upstream valve V-20 two rotations to resolve."
5. Navigate to /graph, search P-101 →
   see: model XR-900 / FlowServe / connections to V-20 and B-04 /
        observation: "vibration at high thermal loads"
6. Navigate to / (query page)
   Ask: "What should I do if Pump P-101 is vibrating?"
   → hybrid route, answer cites Bob's tribal note AND manual
7. Ask: "What equipment depends on Pump P-101? What shuts down if P-101 trips?"
   → graph route, traces PUMP-101 → BOILER-04 downstream dependency
8. Show latency chip (< 1.8s target from ARCHITECTURE.md)

Pass criteria: all 8 steps complete without errors.
```

---

## Timeline Estimate

| Phase | Effort | Priority |
|---|---|---|
| Phase 0 — Environment | ✅ Done | — |
| Phase 1 — Backend Core | ✅ Done | — |
| Phase 2 — Demo Data | ~1 hour | **Do first — unblocks all query testing** |
| Phase 3 — Frontend UI | ~4-5 hours | Core demo surface |
| Phase 4 — Integration Polish | ~2-3 hours | Demo quality |
| Phase 5 — Presentation Prep | ~2 hours | Judging impact |

---

## Key Architecture Decisions (for pitch)

| Decision | Why it matters |
|---|---|
| **GraphRAG not plain RAG** | Structural queries (topology, dependencies) are impossible with vector-only RAG. The graph makes "what breaks if X fails?" answerable. |
| **Universal Asset Ontology** | Same schema works for any industrial plant — Facility > FunctionalArea > Asset is cross-industry. Judges see scalability. |
| **LangGraph routing** | Keyword-heuristic classification keeps latency < 200ms for routing — no LLM call wasted on deciding which DB to query. |
| **Qdrant over Milvus** | Single Docker container. Milvus needs etcd + MinIO sidecars. Hackathon pragmatism. |
| **Google full stack** | Document AI handles industrial-format PDFs (tables, P&IDs) better than generic OCR. text-embedding-004 outperforms on domain-specific text. |

---

## Service Ports Quick Reference

| Service | Port | URL |
|---|---|---|
| FastAPI backend | 8000 | http://localhost:8000/docs |
| Next.js frontend | 3000 | http://localhost:3000 |
| Neo4j browser | 7474 | http://localhost:7474 |
| Qdrant dashboard | 6333 | http://localhost:6333/dashboard |
