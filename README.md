# neighborhood-library-portal

Assessment for numinolabs interview.

## Structure

```
proto/                 Shared Protobuf contracts (source of truth)
library-service/
  app/
    pb/                Generated Python stubs (from proto/)
    rpc/               gRPC handlers (thin; proto ↔ services)
    services/          Business logic (no proto / HTTP)
    repositories/      Database access (SQLAlchemy only)
    models/            SQLAlchemy models
  scripts/
    generate_protos.py
    start.sh           migrations → gRPC + HTTP health
web/                   React frontend (Vite); nginx serves production build
docker-compose.yml
```

## Request flow

```
gRPC request
  → app/rpc/servicers/*     (map proto → call service)
  → app/services/*          (rules, orchestration)
  → app/repositories/*      (SQL)
  → Postgres
```

## gRPC wiring

```
proto/*.proto
    │  python scripts/generate_protos.py
    ▼
app/pb/*_pb2.py          messages
app/pb/*_pb2_grpc.py     stubs + Servicer base + add_*_to_server
    │
    ▼
app/rpc/servicers/*.py   handlers (subclass *Servicer)
    │
    ▼
app/rpc/server.py        create grpc.Server → register servicers → listen
    │
    ▼
python -m app.rpc.server   (port 50051)
```

Fill in: `repositories/` → `services/` → `rpc/servicers/` (handlers still `UNIMPLEMENTED`).
Use `session_scope()` from `app.database` when you wire a DB session per RPC.

## Docker

```bash
docker compose up --build
```

| Service           | URL / port                   |
|-------------------|------------------------------|
| web               | http://localhost:8080        |
| HTTP health       | http://localhost:8000/health |
| gRPC              | localhost:50051              |
| Postgres          | localhost:5432               |

## Local library-service

```bash
cd library-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# regenerate stubs after editing proto/
python scripts/generate_protos.py

alembic upgrade head
python -m app.rpc.server
# optional health: uvicorn app.main:app --reload --port 8000
```

## Migrations

From `library-service/`:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```
