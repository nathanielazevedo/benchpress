<p align="center">
  <img src="benchpress.png" alt="Benchpress" width="340" />
</p>

A platform for designing and documenting lab system architectures with AI assistance. Labs can model their instrument topology as interactive node graphs, ask an AI assistant to suggest or modify the design, and deploy lightweight agents to their physical instruments.

---

## Architecture

```
┌─────────────┐     HTTP/REST      ┌──────────────────┐
│   Frontend  │ ◄────────────────► │     Backend      │
│  React/Vite │                    │  FastAPI + Async  │
└─────────────┘                    │  SQLAlchemy       │
                                   └────────┬─────────┘
                                            │
                              ┌─────────────┼──────────────┐
                              │             │              │
                        ┌─────▼────┐  ┌────▼──────┐  ┌───▼────────┐
                        │ Postgres │  │ Anthropic │  │ Instrument │
                        │    DB    │  │   API     │  │   Agents   │
                        └──────────┘  └───────────┘  └────────────┘
```

| Layer | Tech |
|---|---|
| Frontend | React 18, TypeScript, Vite, MUI, React Flow, Zustand, TanStack Query |
| Backend | FastAPI, SQLAlchemy (async), Pydantic v2, JWT auth, Alembic |
| Database | PostgreSQL 16 |
| AI | Anthropic Claude API |
| Instrument Agent | C# / .NET 10 |
| Container | Docker Compose |

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
SECRET_KEY=<generate with: openssl rand -hex 32>
ANTHROPIC_API_KEY=sk-ant-...
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_PASSWORD=changeme
```

### 2. Start the stack

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

On first boot the backend runs Alembic migrations and seeds a `super_admin` user with the credentials from your `.env`.

### 3. Generate the typed API client (first time)

With the backend running:

```bash
cd frontend
npm run generate-api
```

This calls orval against `http://localhost:8000/openapi.json` and writes typed React Query hooks to `src/api/` (git-ignored).

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
│   │   └── instruments/    # Instrument heartbeat + command polling
│   ├── alembic/            # DB migrations
│   ├── tests/              # pytest + httpx integration tests
│   ├── models.py           # SQLAlchemy models
│   └── main.py             # App entry point
│
├── frontend/
│   └── src/
│       ├── core/           # Axios instance, theme, layout
│       ├── modules/
│       │   ├── auth/       # Login page, auth store
│       │   ├── designer/   # Canvas, AI chat, design list
│       │   └── admin/      # Companies, Labs, Users pages
│       ├── api/            # Auto-generated (orval) — do not edit
│       └── types/          # Shared TypeScript types
│
└── instrument_agent/       # C# .NET 10 agent for lab instruments
    └── src/
        ├── IInstrumentAgent.cs
        ├── LabInstrumentAgent.cs
        ├── AgentConfig.cs
        └── ILogger.cs
```

---

## Role Hierarchy

| Role | Scope |
|---|---|
| `super_admin` | Full access to everything |
| `company_admin` | Manages labs and users within their company |
| `lab_admin` | Manages users and designs within their lab |
| `member` | Read/write designs within their lab |

---

## Development

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run tests
python -m pytest

# Apply migrations manually
alembic upgrade head
```

### Frontend

```bash
cd frontend
npm install
npm run dev       # dev server on :5173
npm test          # vitest watch mode
npm run test:run  # single run
```

### Instrument Agent

```bash
cd instrument_agent
# Edit appsettings.json to point at your backend
dotnet run
```

Environment variables override `appsettings.json` — prefix with `AGENT_`:

```bash
AGENT_AGENT__BACKENDURL=http://myserver:8000 dotnet run
```

---

## Running Tests

**Backend** (26 tests):
```bash
cd backend && python -m pytest
```

**Frontend** (13 tests):
```bash
cd frontend && npm run test:run
```
