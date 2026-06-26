# Project Paper Brain: Architecture & Implementation Blueprint

## 1. Executive System Summary

**Paper Brain** is an enterprise-grade, ontology-driven Industrial Knowledge Intelligence platform designed to combat knowledge fragmentation, mitigate operational downtime, and capture institutional tribal knowledge.

Unlike traditional document-search systems or flat vector RAG applications, Paper Brain abstracts industrial systems into a **Universal Asset Ontology** using a hybrid **GraphRAG** (Knowledge Graph + Semantic Vector Search) framework. This architecture enables the platform to reason over both natural language text (equipment manuals, safety logs) and deterministic topology networks (piping networks, electrical lines, upstream/downstream dependency maps).

---

## 2. Core Technological Stack

```text
+---------------------------------------------------------------------------------+
|                                APPLICATION LAYER                                |
|                        Progressive Web App (Next.js / Tailwind CSS)             |
+---------------------------------------------------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                              API & ORCHESTRATION                                |
|                 FastAPI + LangGraph / LlamaIndex Property Graph                 |
+---------------------------------------------------------------------------------+
                         /                               \
                        /                                 \
                       v                                   v
+---------------------------------------------+ +---------------------------------+
|               KNOWLEDGE GRAPH               | |         VECTOR DATABASE         |
|              Neo4j (Cypher QL)              | |           Qdrant                |
|  [Physical Topology & Asset Hierarchies]    | |  [Embedded Chunks & Manuals]    |
+---------------------------------------------+ +---------------------------------+
                       ^                                   ^
                       |                                   |
+---------------------------------------------------------------------------------+
|                                INGESTION LAYER                                  |
|       Google Document AI / Cloud Speech-to-Text / Gemini 2.5 Flash NER          |
+---------------------------------------------------------------------------------+
```

### 2.1 Ingestion Layer (The Eyes & Ears)

- **Multimodal Document Processing:** Paper Brain's custom neural OCR models, supplemented by **Google Document AI** for structured layout parsing (tables, sheets, forms, P&IDs) — superior to generic OCR for industrial document formats.
- **Audio Transcription:** **Google Cloud Speech-to-Text** for capturing field operator voice notes.
- **Named Entity Recognition (NER) & Resolution:** LLM routing (**Gemini 2.5 Flash**) constrained with strict JSON schemas to extract and format standardized industrial equipment tags from unstructured inputs.

### 2.2 Storage & Search Layer (The Memory)

- **Deterministic Topology (Knowledge Graph):** Neo4j (graph database native to Cypher querying) to hold physical and logical asset hierarchies.
- **Semantic Memory (Vector DB):** Qdrant utilizing dense vector embeddings (**Google `text-embedding-004`** via Vertex AI) for indexing text chunks from operation manuals.

### 2.3 Orchestration & Inference Layer (The Nervous System)

- **API Gateway:** FastAPI to handle high-performance asynchronous routing between the Next.js frontend and the AI backend.
- **Agentic Framework:** LangGraph or LlamaIndex.
- **Inference Model:** **Google Gemini 2.5 Flash** for context synthesis and generation (1M token context window — ideal for loading full equipment manuals).

---

## 3. Data Schema & Core Ontology Mapping

To ensure cross-industry scalability, the Knowledge Graph operates strictly on a **Universal Asset Ontology**.

### 3.1 Node Labels & Schema

| Node Label | Description | Properties |
|---|---|---|
| `Facility` | Top-level operating site | `id`, `name`, `location` |
| `FunctionalArea` | Geographically or operationally distinct zone | `id`, `name` |
| `Asset` | A physical or functional unit of machinery | `id`, `tag_number`, `model_number`, `manufacturer`, `install_date`, `base_emissions_co2_ppm` |
| `DocumentChunk` | A specific embedded segment of textual knowledge | `id`, `source_file`, `page_number`, `chunk_text` |
| `KnowledgeObservation` | Anecdotal or informal data injected into the platform (Tribal Knowledge) | `id`, `author`, `timestamp`, `transcript`, `confidence_score` |

### 3.2 Relationship Types

```
(:Facility)-[:HAS_AREA]->(:FunctionalArea)
(:FunctionalArea)-[:HAS_ASSET]->(:Asset)
(:Asset)-[:CONNECTED_TO {direction: "upstream"|"downstream"}]->(:Asset)
(:Asset)-[:DOCUMENTED_BY]->(:DocumentChunk)
(:Asset)-[:HAS_OBSERVATION]->(:KnowledgeObservation)
```

### 3.3 Target Reference Code (Universal Cypher Mapping)

```cypher
// Example: Creating the physical and conceptual backbone
CREATE (f:Facility {id: "FAC-MUM-01", name: "Mumbai Plant"})
CREATE (a:FunctionalArea {id: "AREA-COOL-01", name: "Cooling Infrastructure"})
CREATE (m1:Asset {id: "PUMP-101", tag_number: "P-101", model_number: "XR-900", manufacturer: "FlowServe", base_emissions_co2_ppm: 45})
CREATE (m2:Asset {id: "VALVE-20", tag_number: "V-20", model_number: "V-LOK-2", manufacturer: "Swagelok"})

CREATE (f)-[:HAS_AREA]->(a)
CREATE (a)-[:HAS_ASSET]->(m1)
CREATE (a)-[:HAS_ASSET]->(m2)
CREATE (m2)-[:CONNECTED_TO {direction: "upstream"}]->(m1);
```

---

## 4. End-to-End Pipeline Execution Specifications

### 4.1 Ingestion Pipeline (Documents & Diagrams)

- **Input:** Scanned P&ID PDF document or OEM Operation Manual.
- **Execution:** Google Document AI splits the asset data out. The text chunks undergo vectorization via Google `text-embedding-004` and are deposited into Qdrant.
- **Graph Sync:** Concurrently, an LLM extracts structural relationships from P&IDs (e.g., PUMP-101 links to VALVE-20) and merges them into Neo4j via exact match `tag_number` constraints.

### 4.2 Tribal Knowledge Voice Pipeline

- **Input:** Voice note recorded on the frontend client.
- **Execution:** Audio passes through **Google Cloud Speech-to-Text**. Transcript is passed to Gemini 2.5 Flash as an entity extractor with a strict schema template:

```json
{
  "target_asset_tag": "P-101",
  "observed_issue": "Vibration during high thermal loads",
  "mitigation_action": "Manually open upstream valve V-20 by two full rotations",
  "confidence_index": 0.85
}
```

- **Graph Update:** System creates a new `(:KnowledgeObservation)` node and binds it to `(:Asset {tag_number: "P-101"})`.

### 4.3 Agentic Retrieval Flow (GraphRAG Routing)

When a query enters the engine, the orchestrator routes based on intent:

| Query Type | Route | Example |
|---|---|---|
| **Factual Text Query** | Vector DB only | *"What is the torque spec?"* |
| **Structural / Dependency Query** | Neo4j only | *"What shuts down if Boiler 4 trips?"* |
| **Hybrid Crisis Query** | Both DBs — fused into LLM context | Complex multi-system fault diagnosis |

---

## 5. Prerequisite Golden Dataset (Hackathon Preparation)

To prevent runtime hallucinations, the platform relies on three structured seed files loaded on initialization.

### 5.1 Asset Infrastructure Table (`assets_seed.csv`)

| id | tag_number | model_number | manufacturer | functional_area | base_emissions_co2_ppm |
|---|---|---|---|---|---|
| PUMP-101 | P-101 | XR-900 | FlowServe | Cooling | 45 |
| VALVE-020 | V-20 | V-LOK-2 | Swagelok | Cooling | 0 |
| BOILER-04 | B-04 | BLR-MAX | Thermax | Power-Gen | 320 |

### 5.2 Topology Connectivity Map (`topology_seed.csv`)

| source_id | target_id | relationship_type | directional_flow |
|---|---|---|---|
| VALVE-020 | PUMP-101 | CONNECTED_TO | upstream |
| PUMP-101 | BOILER-04 | CONNECTED_TO | upstream |

### 5.3 Technical Document Dictionary Mapping

| File Name | Description |
|---|---|
| `OEM-XR-900-Pump-Manual.pdf` | Contains clear diagnostic text linking flow rate drops to upstream valve closures |
| `Tribal-Bob-Notes.json` | Pre-embedded node array representing a voice note confirming the common issue with Valve V-20 causing P-101 cavitation |

---

## 6. Verification Metrics

| Metric | Target |
|---|---|
| **Extraction Precision** | Minimum 92% accuracy matching unstructured string IDs to registered graph nodes (`tag_number`) |
| **Retrieval Latency** | Full Graph + Vector traversal routing executed under **1.8 seconds** |
| **Hallucination Containment** | Zero pathing generations authorized without structural linkage confirmation inside the Neo4j relational hierarchy |
