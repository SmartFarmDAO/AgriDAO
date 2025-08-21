## AgriDAO Python Backend (FastAPI)

Run a minimal backend API that supports the AgriDAO epics: Identity/Onboarding, Marketplace, Finance, AI Advice (stub), Supply Chain, and Governance.

### Quick start (Docker)
```bash
# From repository root
docker compose up --build
# Or with live reload for development
docker compose -f docker-compose.yml -f docker-compose.override.yml up --build
```
Backend: http://localhost:8000 (Swagger UI at /docs)

### Prerequisites (local without Docker)
- Python 3.11+
- PostgreSQL running locally (or adjust DATABASE_URL)

### Setup (local)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agridb
alembic upgrade head
uvicorn app.main:app --reload
```

### Notes
- Database schema is managed via Alembic migrations.
- Default Docker Compose spins up Postgres + backend.
- CORS is enabled for Vite dev server at `http://localhost:5173`.
- Endpoints are intentionally minimal and can be extended with auth, DID integrations, and on-chain adapters.

