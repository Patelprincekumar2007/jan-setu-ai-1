# NagrikLens AI: Product Master Plan and Technical Architecture Specification

## 1. Executive Summary and Problem Statement

### Core Challenge
Public administrative bodies and local government departments in India receive thousands of development requests, public petitions, and infrastructure grievances across diverse channels (in-person submissions, web portals, letters, ward meetings). These submissions arrive in multiple regional languages with varying levels of detail and unstructured narrative formats.

Administrative officers face three structural bottlenecks:
1. **Channel Fragmentation and Language Silos:** Inability to aggregate and extract structured civic needs from multilingual text inputs.
2. **Context Disconnect:** Civic requests are evaluated in isolation without immediate automated linkage to ground-truth census data, existing public infrastructure registries, or sanctioned scheme budgets.
3. **Subjective Prioritisation:** Lack of a transparent, data-driven, evidence-backed scoring framework to rank civic interventions based on demographic vulnerability, infrastructure deficit, and budget feasibility.

### Proposed Solution: NagrikLens AI
NagrikLens AI is an institutional-grade, multilingual citizen development intelligence platform designed for Digital Public Infrastructure (DPI). The system ingests citizen development requests in natural text, applies Google Gemini for multilingual structured extraction, executes a grounded Retrieval-Augmented Generation (RAG) pipeline over verified open public datasets, and runs an objective multi-criteria prioritisation engine to generate policy-ready action dossiers for administrators.

---

## 2. System Architecture

```
+-----------------------------------------------------------------------------------+
|                                 CITIZEN INTERFACE                                 |
|  - Multilingual Grievance/Need Submission Portal (English, Hindi, Regional)        |
|  - Real-time Reference ID and Application Status Tracker                          |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                     FASTAPI API GATEWAY / INGESTION LAYER                         |
|  - Input Validation, Sanitisation, Rate Limiting (Python FastAPI)                 |
|  - Asynchronous Dispatch to Cognitive Processing Services                         |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                  GOOGLE GEMINI COGNITIVE PROCESSING ENGINE                        |
|  - SDK: Official Google GenAI Python SDK (google-genai)                           |
|  - Configurable Model ID (GEMINI_MODEL environment variable)                      |
|  1. Language Detection and Administrative Normalisation                           |
|  2. Entity Extraction: Administrative Division (State, District, Block, Ward)     |
|  3. Categorisation: Sector (Water, Sanitation, Roads, Electricity, Education)     |
|  4. Urgency and Impact Severity Extraction                                        |
|  5. Synthetic De-identification (Masking PII like Aadhaar/Phone/Name)             |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                       HYBRID VECTOR & STRUCTURED RAG PIPELINE                     |
|  - Vector Index (ChromaDB / PostgreSQL pgvector):                                 |
|    * District Master Plans, Scheme Guidelines, Past Sanctioned Works              |
|  - Structured Relational Datasets (SQLite / PostgreSQL):                         |
|    * Census Demographics (Population, Marginalised Ratio, Vulnerability Index)    |
|    * Asset Registry (Existing Schools, PHCs, Borewells, Road Network Density)     |
|    * Scheme Allocation (Available funds under JJM, PMGSY, Samagra Shiksha, etc.)  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                       CIVIC PRIORITISATION & SCORING ENGINE                       |
|  - Multi-Criteria Decision Model (MCDM):                                          |
|    * Severity Index (30%)                                                         |
|    * Demographic and Vulnerability Reach (30%)                                    |
|    * Existing Infrastructure Deficit (25%)                                        |
|    * Budgetary and Scheme Feasibility (15%)                                       |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                     POLICYMAKER & WARD OFFICER DASHBOARD                          |
|  - Spatial/Ward-level Need Heatmaps and Sectoral Breakdowns                       |
|  - Ranked Prioritisation Queue with Evidence Citations                            |
|  - AI-Generated Actionable Project Proposal and Scheme Matching Dossier           |
|  - Decision Audit Trail: Under Review, Approved, Sanctioned, or Escalated         |
+------------------------------------------+----------------------------------------+
```

---

## 3. Technology Stack and Technical Choices

### Frontend
- **Framework:** React 18 with Vite (TypeScript)
- **Styling Architecture:** Vanilla CSS / Modular CSS with a strict Institutional Design System (custom tokens, zero purple gradients, zero pill buttons, high contrast, clean typography)
- **Typography:** Outfit (Display/Headings), Inter (UI & Data Grids), JetBrains Mono (Reference Codes & Technical Tokens)
- **Icons:** Standard accessible Lucide React icons (strictly zero emojis)
- **Routing:** React Router v7

### Backend & AI Pipeline
- **Runtime:** Python 3.11+ / FastAPI
- **AI SDK:** Official Google GenAI Python SDK (`google-genai`)
- **LLM Configuration:** Configurable via `GEMINI_MODEL` (e.g., `gemini-2.5-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`)
- **Vector Search:** ChromaDB / pgvector (Phase 5)
- **Relational Storage:** SQLite / PostgreSQL (Phase 3)

---

## 4. MVP Scope Definition

### Included in MVP
1. **Citizen Portal (Text Submission):**
   - Multilingual text input across Indian regional languages.
   - Structured entry with national administrative hierarchy (State > District > Locality/Ward).
   - Reference Tracking Code generation.
2. **Gemini Extraction & Classification:**
   - Parsing raw citizen narratives into structured schemas (Summary, Sector, Urgency, Affected population estimate).
3. **Public Data RAG Pipeline:**
   - Grounded context retrieval from open demographic datasets and verified scheme guidelines.
4. **Prioritisation Engine:**
   - Multi-Criteria Decision Model (MCDM) scoring from 0 to 100.
5. **Officer Intelligence Dashboard:**
   - Filterable, sortable priority queue with side-by-side evidence inspection.

---

## 5. Page Structure and Information Architecture

```
/
|-- / (Home / Platform Overview)
|   |-- System overview, track mandate, workflow explanation, entry points
|
|-- /submit (Citizen Submission Portal)
|   |-- Multilingual text input area
|   |-- Administrative location selector (State, District, Locality)
|   |-- Sector category and affected household count
|   |-- Data minimisation and PII safety advisory
|   |-- Reference tracking token generation
|
|-- /track (Citizen Status Tracker)
|   |-- Reference ID lookup interface
|   |-- Processing stage verification
|
|-- /dashboard (Policymaker / Administrative Portal)
|   |-- Executive Metrics Overview (Total Ingested, High Priority, Verified Deficits)
|   |-- Filter toolbar (Sector, State, Urgency)
|   |-- Prioritised Action Queue and Empty States
|
|-- /datasets (Open Data & Reference Repositories)
|   |-- Catalog of open government datasets (Census, JJM, PMGSY, NHM, UDISE+)
|   |-- Explicit status indicators (Planned)
|
|-- /privacy-policy (Institutional Privacy Policy)
|-- /terms (Terms and Conditions of Public Service Use)
```

---

## 6. Implementation Roadmap

- **Phase 1 (Complete):** Foundation (FastAPI backend shell, React Vite frontend shell, Institutional Design System, all routes, health endpoint, unit tests).
- **Phase 2 Step 1 (Complete):** Citizen Submission and Tracking Portal SQLite persistence with unique reference IDs.
- **Phase 2 Step 2 (Complete):** Google Gemini Structured Understanding integration (`google-genai`), Pydantic validation, and graceful fallback.
- **Phase 2 Step 3A + 3B (Complete):** Public Data Foundation, deterministic normalization pipeline, verified JJM dataset ingestion, dataset catalog UI, and API.
- **Phase 2 Step 3C-1 (Complete):** Knowledge Ingestion and Retrieval Contract Layer (deterministic evidence builder, provenance tracking, baseline metadata retriever, search API).
- **Phase 2 Step 3C-2A (Complete):** Semantic Embeddings and FAISS Vector Index foundation.
- **Phase 2 Step 3C-2B (Complete):** Semantic Retrieval API + Retrieval Evaluation.
- **Phase 2 Step 3C-2C (Next):** Hybrid Search Orchestration.
- **Phase 3:** Hybrid Vector and Structured RAG Pipeline.
- **Phase 4:** Civic Prioritisation Engine (MCDM Scoring).
- **Phase 5:** Officer Intelligence Dashboard and Evidence Inspector.
- **Phase 6:** Security Auditing, Launch Gates Verification and Final Packaging.
