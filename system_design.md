# Benchpress — System Design

> An open source lab automation platform combining ELN, LIMS, instrument control, and data ingestion into a single connected system.

---

## Overview

Benchpress is a polyglot, modular lab automation platform designed to replace the patchwork of expensive enterprise tools (Benchling, Dotmatics, Labware) that most labs pay hundreds of thousands of dollars for annually.

**Core principle:** Data flows continuously from physical instrument → ingestion layer → core API → ELN/LIMS → frontend. Every step is traceable, auditable, and open.

---

## Architecture Layers

```
┌─────────────────────────────────────────┐
│              React Frontend              │
│   Dashboard · ELN · LIMS · Barcodes     │
└──────────────┬──────────────────────────┘
               │ HTTP / WebSocket
┌──────────────▼──────────────────────────┐
│          FastAPI Core Backend            │
│   Auth · REST API · WebSocket · Jobs    │
└──┬───────────┬──────────────┬───────────┘
   │           │              │
┌──▼──┐   ┌───▼───┐   ┌──────▼──────┐
│ ELN │   │ LIMS  │   │  Instrument  │
│     │   │       │   │   Control    │
└──┬──┘   └───┬───┘   └──────┬───────┘
   │           │              │
   └─────┬─────┘              │
         │                    │ Python SDK
┌────────▼──────────┐   ┌─────▼────────┐
│     PostgreSQL     │   │  Opentrons   │
│   (primary store)  │   │  Liquid Handler │
└────────────────────┘   └─────────────┘
         ▲
         │
┌────────┴──────────────┐
│  C# Ingestion Layer    │
│  (Lab Connect)         │
│  File Watcher · Parser │
│  · Normalizer          │
└────────────────────────┘
         ▲
         │
┌────────┴────────────── ┐
│   Lab Instruments      │
│  Plate readers · PCR   │
│  Liquid handlers · etc │
└────────────────────────┘
```

---

## Modules

### 1. C# Ingestion Layer (Lab Connect)

**Language:** C# / .NET  
**Why C#:** Most vendor instrument SDKs and drivers are .NET native (Thermo Fisher, Waters, Agilent). C# gives us native interop without wrappers.

**Responsibilities:**
- Watch configured directories for new instrument output files
- Parse raw vendor-specific formats (CSV, XML, binary) into normalized JSON
- Extract and attach metadata (instrument ID, timestamp, operator, run ID)
- POST normalized data to the FastAPI core via HTTP
- Maintain a local queue for retry if the API is unavailable

**Key components:**
- `FileSystemWatcher` — monitors instrument output directories
- Parser registry — maps file extensions / instrument types to the correct parser
- Normalizer — maps parsed data to the Benchpress common data schema
- Agent service — runs as a Windows service, remotely manageable

**Data flow:**
```
Instrument writes file → FileSystemWatcher triggers → Parser selected → 
Data normalized → POST to /api/v1/ingestion → Stored in PostgreSQL
```

---

### 2. FastAPI Core Backend

**Language:** Python 3.11+  
**Framework:** FastAPI  
**Database ORM:** SQLAlchemy  
**Migrations:** Alembic  
**Background tasks:** Celery + Redis  
**Auth:** JWT (OAuth2 compatible)

**Responsibilities:**
- Central API hub — all modules communicate through here
- Authentication and authorization (role-based: scientist, admin, lab engineer)
- Instrument run orchestration
- Background job management (long-running instrument tasks)
- WebSocket server for real-time instrument status and log streaming
- Audit trail — every write operation is logged with user, timestamp, and diff

**Key API routes:**
```
POST   /api/v1/ingestion          # Receive data from C# layer
GET    /api/v1/samples            # List samples
POST   /api/v1/samples            # Register new sample
GET    /api/v1/experiments        # List ELN experiments
POST   /api/v1/experiments        # Create experiment
GET    /api/v1/instruments        # List connected instruments
POST   /api/v1/instruments/run    # Trigger instrument run
WS     /ws/instruments/{id}       # Real-time instrument status
```

---

### 3. LIMS Module

**Language:** Python  
**Storage:** PostgreSQL

**Responsibilities:**
- Sample registration and lifecycle tracking
- Barcode generation and scanning
- Inventory management (reagents, consumables, plates)
- Location tracking (freezer → rack → position)
- Chain of custody — full audit trail per sample
- Compliance-ready data export

**Core database tables:**
```
samples
  id, barcode, name, type, status, created_by, created_at,
  location_id, parent_sample_id

locations
  id, name, type (freezer/rack/shelf/position), parent_location_id

reagents
  id, name, barcode, lot_number, expiry_date, quantity, unit, location_id

barcodes
  id, value, format (CODE128/QR), entity_type, entity_id, created_at

audit_log
  id, entity_type, entity_id, action, user_id, timestamp, diff_json
```

**Barcode strategy:**
- Code 128 for samples and reagents (scanner-friendly)
- QR codes for plates and equipment (more data capacity)
- ZXing on the frontend for camera-based scanning
- Every barcode scan is logged in the audit trail

---

### 4. ELN Module (Electronic Lab Notebook)

**Language:** Python  
**Storage:** PostgreSQL  
**Rich text:** Stored as structured JSON (ProseMirror schema)

**Responsibilities:**
- Create and version experiment notebooks
- Link notebook entries to samples, reagents, and instrument runs
- Structured data blocks within notebooks (tables, results, observations)
- Real-time collaboration (WebSocket-based)
- Export to PDF and Word
- GLP/GMP-compliant e-signatures

**Core database tables:**
```
experiments
  id, title, description, status, created_by, created_at, project_id

experiment_entries
  id, experiment_id, content_json, version, created_by, created_at

entry_links
  id, entry_id, entity_type (sample/reagent/run), entity_id

experiment_versions
  id, experiment_id, version, snapshot_json, created_by, created_at
```

**Key design decision:** Notebook content is stored as structured JSON not raw HTML. This allows programmatic querying of results and supports downstream AI/ML analysis.

---

### 5. Instrument Control Module

**Language:** Python  
**Primary integration:** Opentrons Python SDK  

**Responsibilities:**
- Unified interface for sending commands to lab instruments
- Abstract hardware differences behind a common protocol definition
- Queue and manage instrument runs as background jobs (Celery)
- Stream real-time status back to the frontend via WebSocket
- Link completed runs to ELN entries automatically

**Protocol abstraction:**
```python
class InstrumentProtocol:
    def initialize(self) -> None
    def run(self, protocol: ProtocolDefinition) -> RunResult
    def get_status(self) -> InstrumentStatus
    def cancel(self) -> None
    def get_run_data(self, run_id: str) -> RunData
```

Each instrument (Opentrons, plate reader, etc.) implements this interface.

**Opentrons integration:**
- Uses the Opentrons Python API v2
- Protocols defined as Python scripts, stored in PostgreSQL
- Run results automatically fed into the ingestion pipeline

---

### 6. React Frontend

**Framework:** React 18  
**State:** Zustand  
**Data fetching:** React Query  
**UI components:** shadcn/ui  
**Charts:** Recharts  
**Barcode scanning:** ZXing-js  
**Diagrams:** React Flow  

**Key views:**
- **Dashboard** — live instrument status, recent runs, alerts
- **ELN** — experiment notebook editor with barcode linking
- **LIMS** — sample registry, inventory, location map
- **Instrument Control** — protocol runner, real-time status, run history
- **Data Explorer** — visualize instrument output data
- **Admin** — user management, instrument configuration, audit log

---

## Data Flow: End to End

```
1. Scientist registers a sample in LIMS → barcode generated and printed
2. Sample loaded onto Opentrons liquid handler
3. Scientist triggers run from Benchpress frontend
4. Instrument Control sends protocol to Opentrons via Python SDK
5. Run executes → instrument writes output file to watched directory
6. C# ingestion layer detects file → parses → normalizes → POSTs to API
7. API stores run data → links to sample via barcode → updates ELN entry
8. Frontend receives real-time update via WebSocket
9. Scientist reviews results in ELN → e-signs the entry
10. Full audit trail stored: sample → run → raw data → notebook entry
```

---

## Tech Stack Summary

| Layer | Language | Key Technologies |
|-------|----------|-----------------|
| Ingestion | C# / .NET | FileSystemWatcher, vendor SDKs |
| Core API | Python | FastAPI, SQLAlchemy, Alembic |
| Background jobs | Python | Celery, Redis |
| Database | SQL | PostgreSQL |
| Instrument control | Python | Opentrons SDK |
| Frontend | JavaScript | React, Zustand, React Query |
| Barcode | JS + Python | ZXing-js, python-barcode |
| Auth | Python | JWT, OAuth2 |

---

## Video Series Map

| Video | Module | Stack |
|-------|--------|-------|
| 1 | Architecture overview (this doc) | Excalidraw |
| 2 | C# ingestion layer — file watchers + parsers | C# |
| 3 | FastAPI core — API design + database schema | Python |
| 4 | LIMS — samples, barcoding, inventory | Python |
| 5 | Instrument control — Opentrons API | Python |
| 6 | ELN — structured notebooks, versioning | Python |
| 7 | React frontend — dashboard + barcode scanning | React |
| 8 | End to end — connecting all layers | Full stack |

---

## Open Questions / Future Work

- **Multi-tenancy** — should Benchpress support multiple labs/orgs in one instance?
- **Cloud vs self-hosted** — target deployment (Docker Compose for self-hosted, K8s for cloud)
- **Additional instruments** — Hamilton, Tecan, plate readers
- **AI layer** — experiment suggestion, anomaly detection in instrument data
- **Mobile app** — barcode scanning from a phone in the lab