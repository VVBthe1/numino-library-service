# Neighborhood Library

Staff console for a small neighborhood library: manage books, members, and loans.

## What’s built

- **gRPC API** (Python) for auth, books, members, and loans, backed by PostgreSQL
- **JWT login** with a single staff account (`admin` / `admin`)
- **Next.js (React) UI** that talks to the API over gRPC-Web (Envoy)
- Soft-delete for books and members so loan history keeps its references

```
Browser (web :8080)
  → nginx → Envoy (:8081) → library-service gRPC (:50051)
                          → Postgres (:5432)
```

| Layer | Path |
|-------|------|
| Proto contracts | `proto/` |
| Backend | `library-service/` (models → repositories → services → gRPC servicers) |
| gRPC-Web proxy | `envoy/` |
| Staff UI | `web/` |

## Requirements

**Recommended (Docker):**

- Docker and Docker Compose

**Optional (run pieces without Docker):**

- Python 3.12+
- Node.js 22+ (frontend only)
- PostgreSQL 16
- [grpcurl](https://github.com/fullstorydev/grpcurl) (API smoke tests)

## Run locally

### With Docker (easiest)

From the repo root:

```bash
docker compose up --build
```

| Service | URL / port |
|---------|------------|
| Staff UI | http://localhost:8080 |
| gRPC-Web (Envoy) | http://localhost:8081 |
| HTTP health | http://localhost:8000/health |
| gRPC | localhost:50051 |
| Postgres | localhost:5432 |

Sign in at http://localhost:8080 with `admin` / `admin`.

Stop with `Ctrl+C`, or `docker compose down`.

### Frontend only (against running Compose)

With Envoy already up on 8081:

```bash
cd web
npm install
NEXT_PUBLIC_GRPC_BASE_URL=http://localhost:8081 npm run dev
# http://localhost:5173
```

### Backend only (no Docker for the API)

Needs a reachable Postgres (e.g. Compose `db` service, or local Postgres).

```bash
cd library-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

python scripts/generate_protos.py   # after editing proto/
alembic upgrade head
python -m app.rpc.server            # :50051
```

## How to test

### UI

1. Open http://localhost:8080 and sign in (`admin` / `admin`).
2. Create a book and a member.
3. Borrow / return on **Loans**.
4. Use filters on each list; check **Overdue** and **Out of stock** under Books.
5. Delete a book/member that only has returned loans — it should leave the catalog but remain on loan history.

### Backend unit tests

```bash
cd library-service
source .venv/bin/activate   # if using a venv
pip install -r requirements-dev.txt
python -m pytest -q
```

### gRPC with grpcurl

From the repo root, with the API on `:50051`:

```bash
PROTO=(-import-path proto -proto auth.proto -proto book.proto -proto member.proto -proto loan.proto -proto entities.proto)

# Login (grpcurl JSON uses camelCase: accessToken)
export TOKEN=$(grpcurl -plaintext "${PROTO[@]}" \
  -d '{"username":"admin","password":"admin"}' \
  localhost:50051 neighborhood.library.v1.AuthService/Login \
  | jq -r .accessToken)

AUTH=(-H "authorization: Bearer ${TOKEN}")

grpcurl -plaintext "${PROTO[@]}" "${AUTH[@]}" \
  -d '{"page_size":10}' \
  localhost:50051 neighborhood.library.v1.BookService/ListBooks
```

Other RPCs follow the same pattern (`CreateBook`, `CreateMember`, `BorrowBook`, `ReturnBook`, …). Without a Bearer token, domain calls return `UNAUTHENTICATED`.

```bash
grpcurl -plaintext "${PROTO[@]}" list localhost:50051
```
