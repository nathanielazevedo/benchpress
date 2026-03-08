<p align="center">
  <img src="benchpress.png" alt="Benchpress" width="360" />
</p>

<p align="center">
  <strong>Open source lab automation — ELN · LIMS · Instrument Control · Scheduler · AI</strong>
</p>

<p align="center">
  Replace Benchling, Dotmatics, and Labware with a single connected platform your team actually owns.
</p>

---

## What is Benchpress?

Benchpress is a polyglot, modular lab automation platform. Data flows continuously from physical instrument → ingestion layer → core API → ELN/LIMS → frontend. Every step is traceable, auditable, and open.

**Core principle:** A scientist registers a sample, triggers an instrument run, and sees results linked to their notebook entry — all without leaving the app, all with a full audit trail.

---

## Architecture

```
┌─────────────────────────────────────────┐
│              React Frontend              │
│  Dashboard · ELN · LIMS · Designer · AI │
└──────────────┬──────────────────────────┘
               │ HTTP / WebSocket
┌──────────────▼──────────────────────────┐
│          FastAPI Core Backend            │
│   Auth · REST API · WebSocket · Jobs    │
└──┬───────────┬──────────────┬───────────┘
   │           │              │
┌──▼──┐   ┌───▼───┐   ┌──────▼──────────┐
│ ELN │   │ LIMS  │   │ Instrument       │
│     │   │       │   │ Control          │
└──┬──┘   └───┬───┘   └──────┬───────────┘
   │           │              │ Python SDK
   └─────┬─────┘        ┌─────▼────────┐
         │              │  Opentrons /  │
┌────────▼───────────┐  │  Plate Reader │
│     PostgreSQL      │  └──────────────┘
│   (primary store)   │
└────────────────────┘
         ▲
┌────────┴───────────────┐
│  C# Ingestion Layer     │
│  (Lab Connect)          │
│  FileWatcher · Parser   │
│  · Normalizer · Queue   │
└────────────────────────┘
         ▲
┌────────┴────────────────┐
│   Lab Instruments        │
│  Plate readers · PCR     │
│  Liquid handlers · etc   │
└──────────────────────────┘
```

| Layer | Language | Key Tech |
|---|---|---|
| Frontend | TypeScript | React 18, Vite, MUI, React Flow, Zustand, TanStack Query |
| Core API | Python 3.12 | FastAPI, SQLAlchemy (async), Pydantic v2, Alembic, JWT |
| Background jobs | Python | Celery + Redis *(planned)* |
| Database | SQL | PostgreSQL 16 |
| Ingestion / Agent | C# / .NET 10 | FileSystemWatcher, vendor SDKs, Windows Service |
| Instrument control | Python | Opentrons SDK *(planned)* |
| Barcode | JS + Python | ZXing-js, python-barcode *(planned)* |
| AI | Python | Anthropic Claude API |

---

## Roadmap

### Platform Foundation
- [x] Multi-tenant auth — companies → labs → users with role hierarchy (`super_admin` → `company_admin` → `lab_admin` → `member`)
- [x] JWT authentication with bearer tokens
- [x] Async FastAPI backend with modular `core/` + `modules/<name>/{router,service,schemas}` structure
- [x] PostgreSQL with async SQLAlchemy + Alembic migrations (idempotent)
- [x] Typed React frontend with auto-generated API hooks (orval + React Query)
- [x] Docker Compose dev environment (db + backend + frontend)
- [x] Backend test suite (pytest + httpx, 26 tests)
- [x] Frontend test suite (Vitest + RTL, 13 tests)

### System Designer *(in progress)*
- [x] Interactive canvas with React Flow — drag-and-drop nodes and edges
- [x] AI assistant (Claude) — chat to add, remove, and modify nodes/edges via structured actions
- [x] Design CRUD — save and load diagrams per lab
- [ ] Node type library — predefined shapes for instruments, storage, workstations
- [ ] Export canvas to PDF / PNG
- [ ] Share / comment on designs

### Lab Connect — C# Instrument Agent
- [x] `IInstrumentAgent` interface + `LabInstrumentAgent` implementation
- [x] Heartbeat loop — agent registers itself with the backend on each poll cycle
- [x] Command polling — backend can dispatch commands to the agent
- [x] `appsettings.json` + `AGENT_` env var configuration
- [x] Backend instrument endpoints — heartbeat upsert, command queue, instrument list
- [ ] `FileSystemWatcher` — detect new instrument output files automatically
- [ ] Parser registry — map file types (CSV, XML, binary) to the correct parser
- [ ] Normalizer — map parsed data to the Benchpress common schema
- [ ] Local retry queue — buffer POSTs when backend is unreachable
- [ ] Windows Service host
- [ ] Vendor integrations: Thermo Fisher, Waters, Agilent

### LIMS — Sample & Inventory Management
- [ ] Sample registration with auto-generated barcodes (Code 128 + QR)
- [ ] Sample lifecycle tracking (created → in-use → consumed → archived)
- [ ] Location tree — freezer → rack → shelf → position
- [ ] Reagent and consumable inventory
- [ ] Chain of custody — full audit trail per sample
- [ ] Barcode scanning in-browser (ZXing-js camera integration)
- [ ] Compliance export (CSV, PDF)

### ELN — Electronic Lab Notebook
- [ ] Rich structured notebook entries (ProseMirror JSON schema)
- [ ] Link entries to samples, reagents, and instrument runs
- [ ] Entry versioning with full diff history
- [ ] Real-time collaboration via WebSocket
- [ ] E-signatures (GLP/GMP compliant)
- [ ] Export to PDF and Word

### Instrument Control
- [ ] Opentrons Python SDK integration — trigger liquid handler protocols from the UI
- [ ] Protocol storage — Python protocol scripts stored in PostgreSQL
- [ ] Background job queue (Celery + Redis) for long-running runs
- [ ] Real-time run status streaming via WebSocket
- [ ] Auto-link completed run data to ELN entries
- [ ] Abstract `InstrumentProtocol` interface for multi-vendor support (Hamilton, Tecan, plate readers)

### Scheduler
- [ ] Instrument booking calendar
- [ ] Protocol scheduling — queue runs with dependencies
- [ ] Conflict detection and notifications
- [ ] Integration with ELN entries for planned vs actual execution

### AI Layer
- [x] Claude-powered system design assistant
- [ ] Experiment suggestion based on prior ELN entries
- [ ] Anomaly detection in instrument run data
- [ ] Auto-summarize experiment results into notebook entries
- [ ] Natural language queries over LIMS data

### Infrastructure
- [ ] Kubernetes manifests for cloud deployment
- [ ] Mobile app — barcode scanning from a phone in the lab
- [ ] Webhook system — notify external tools on sample/run events
- [ ] SSO / OAuth2 provider support

---

## Getting Started

### Prerequisites

- Docker + Docker Compose
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Configure environment

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/ai_system_design
SECRET_KEY=<openssl rand -hex 32>
ANTHROPIC_API_KEY=sk-ant-...
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_PASSWORD=changeme
```

### 2. Start the stack

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |

On first boot, Alembic migrations run automatically and a `super_admin` user is seeded from your `.env`.

### 3. Generate the typed API client

With the backend running:

```bash
cd frontend
npm run generate-api
```

Calls orval against the live OpenAPI spec and writes typed React Query hooks to `src/api/` (git-ignored — regenerate any time the backend changes).

---

## Project Structure

```
.
├── backend/
│   ├── core/               # Database, auth, permissions, pagination, logging
│   ├── modules/
│   │   ├── auth/           # Login, /me
│   │   ├── companies/      # Company CRUD
│   │   ├── labs/           # Lab CRUD
│   │   ├── users/          # User CRUD
│   │   ├── designs/        # System design CRUD
│   │   ├── ai/             # Claude chat endpoint
│   │   └── instruments/    # Agent heartbeat + command dispatch
│   ├── alembic/            # DB migrations
│   ├── tests/              # pytest + httpx (26 tests)
│   ├── models.py
│   └── main.py
│
├── frontend/
│   └── src/
│       ├── core/           # Axios instance, theme, layout
│       ├── modules/
│       │   ├── auth/       # Login page, auth store
│       │   ├── designer/   # Canvas, AI chat, design list
│       │   └── admin/      # Companies, Labs, Users pages
│       ├── api/            # Auto-generated by orval — do not edit
│       └── types/          # Shared TypeScript types + role helpers
│
└── instrument_agent/       # C# .NET 10 — runs on lab instruments
    └── src/
        ├── IInstrumentAgent.cs
        ├── LabInstrumentAgent.cs
        ├── AgentConfig.cs
        └── ILogger.cs
```

---

## Role Hierarchy

| Role | Can do |
|---|---|
| `super_admin` | Everything — manage all companies, labs, users |
| `company_admin` | Manage labs and users within their company |
| `lab_admin` | Manage users and resources within their lab |
| `member` | Read/write within their lab |

---

## Development

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest          # run tests
alembic upgrade head      # apply migrations manually
```

### Frontend

```bash
cd frontend
npm install
npm run dev               # dev server on :5173
npm run test:run          # single test run
npm test                  # watch mode
```

### Instrument Agent

```bash
cd instrument_agent
# configure appsettings.json or use env vars:
# AGENT_AGENT__BACKENDURL=http://myserver:8000
dotnet run
```
