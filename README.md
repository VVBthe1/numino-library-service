# neighborhood-library-portal

Assessment for numinolabs interview.

## Structure

```
proto/                 Shared Protobuf contracts (source of truth)
library-service/
  app/
    pb/                Generated Python stubs (from proto/)
    rpc/               gRPC handlers + JWT interceptor
    services/          Business logic (no proto / HTTP)
    repositories/      Database access (SQLAlchemy only)
    models/            SQLAlchemy models
  scripts/
    generate_protos.py
    start.sh           migrations → gRPC + HTTP health
envoy/                 gRPC-Web proxy (browser → gRPC)
web/                   Next.js React staff UI; nginx serves static export
docker-compose.yml
```

## Request flow

```
gRPC request
  → AuthInterceptor (Bearer JWT; Login is public)
  → app/rpc/servicers/*     (map proto → call service)
  → app/services/*          (rules, orchestration)
  → app/repositories/*      (SQL)
  → Postgres
```

## Auth

Single hardcoded user (defaults): `admin` / `admin`.

1. Call `AuthService.Login` (no token).
2. Send `authorization: Bearer <access_token>` on all other RPCs.
3. Logout = discard the token on the client (no server logout).

## Testing gRPC (grpcurl)

Install [grpcurl](https://github.com/fullstorydev/grpcurl). Server has no reflection, so pass the local protos from the repo root.

```bash
# from repo root, with library-service listening on :50051
PROTO=(-import-path proto -proto auth.proto -proto book.proto -proto member.proto -proto loan.proto -proto entities.proto)
```

### 1. Login and capture the JWT

```bash
grpcurl -plaintext "${PROTO[@]}" \
  -d '{"username":"admin","password":"admin"}' \
  localhost:50051 neighborhood.library.v1.AuthService/Login
```

Copy `access_token` from the response, then:

```bash
# bash
export TOKEN='paste-access_token-here'

# optional one-liner (needs jq)
export TOKEN=$(grpcurl -plaintext "${PROTO[@]}" \
  -d '{"username":"admin","password":"admin"}' \
  localhost:50051 neighborhood.library.v1.AuthService/Login \
  | jq -r .accessToken)
```

> grpcurl JSON uses lowerCamelCase field names (`accessToken`), even though the proto field is `access_token`.

Without a token (or with a bad one), domain RPCs return `UNAUTHENTICATED`.

### 2. Call APIs with the JWT

```bash
AUTH=(-H "authorization: Bearer ${TOKEN}")

# Books
grpcurl -plaintext "${PROTO[@]}" "${AUTH[@]}" \
  -d '{
    "title":"Dune",
    "author":"Frank Herbert",
    "isbn":"9780441172719",
    "genre":"GENRE_SCIENCE_FICTION",
    "total_quantity":3
  }' \
  localhost:50051 neighborhood.library.v1.BookService/CreateBook

grpcurl -plaintext "${PROTO[@]}" "${AUTH[@]}" \
  -d '{"page_size":10}' \
  localhost:50051 neighborhood.library.v1.BookService/ListBooks

grpcurl -plaintext "${PROTO[@]}" "${AUTH[@]}" \
  -d '{"id":1}' \
  localhost:50051 neighborhood.library.v1.BookService/GetBook

# Members
grpcurl -plaintext "${PROTO[@]}" "${AUTH[@]}" \
  -d '{
    "name":"Ada Lovelace",
    "email":"ada@example.com",
    "membership_start_date":"2024-01-01"
  }' \
  localhost:50051 neighborhood.library.v1.MemberService/CreateMember

grpcurl -plaintext "${PROTO[@]}" "${AUTH[@]}" \
  -d '{"page_size":10}' \
  localhost:50051 neighborhood.library.v1.MemberService/ListMembers

# Loans (use real book_id / member_id from the creates above)
grpcurl -plaintext "${PROTO[@]}" "${AUTH[@]}" \
  -d '{"book_id":1,"member_id":1}' \
  localhost:50051 neighborhood.library.v1.LoanService/BorrowBook

grpcurl -plaintext "${PROTO[@]}" "${AUTH[@]}" \
  -d '{"loan_id":1}' \
  localhost:50051 neighborhood.library.v1.LoanService/ReturnBook

grpcurl -plaintext "${PROTO[@]}" "${AUTH[@]}" \
  -d '{"page_size":10,"active_only":true}' \
  localhost:50051 neighborhood.library.v1.LoanService/ListLoans
```

### 3. Sanity checks

```bash
# missing Bearer → UNAUTHENTICATED
grpcurl -plaintext "${PROTO[@]}" \
  -d '{"page_size":10}' \
  localhost:50051 neighborhood.library.v1.BookService/ListBooks

# bad password → UNAUTHENTICATED on Login
grpcurl -plaintext "${PROTO[@]}" \
  -d '{"username":"admin","password":"nope"}' \
  localhost:50051 neighborhood.library.v1.AuthService/Login
```

List all methods (still needs protos):

```bash
grpcurl -plaintext "${PROTO[@]}" list localhost:50051
grpcurl -plaintext "${PROTO[@]}" describe localhost:50051 neighborhood.library.v1.BookService
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
app/rpc/server.py        interceptors + servicers → listen
    │
    ▼
python -m app.rpc.server   (port 50051)
```

Backend gRPC path is wired: `repositories/` → `services/` → `rpc/servicers/`.
Use `session_scope()` from `app.database` for a DB session per RPC.
Frontend (`web/`) is a **Next.js** (React) staff console in plain JavaScript. It talks **gRPC-Web** through nginx → Envoy → the library service. Sign in with `admin` / `admin`, then manage books, members, and loans at http://localhost:8080. Proto clients under `web/src/gen/` are generated TypeScript (from protobuf-ts).

## Docker

```bash
docker compose up --build
```

| Service           | URL / port                   |
|-------------------|------------------------------|
| web               | http://localhost:8080        |
| gRPC-Web (Envoy)  | http://localhost:8081        |
| HTTP health       | http://localhost:8000/health |
| gRPC              | localhost:50051              |
| Postgres          | localhost:5432               |

### Frontend (local Next.js)

With compose already running (Envoy on 8081):

```bash
cd web
npm install
NEXT_PUBLIC_GRPC_BASE_URL=http://localhost:8081 npm run dev
# open http://localhost:5173
```

Docker/nginx uses same-origin gRPC-Web proxy (no env needed).

After editing `.proto` files, regenerate the gRPC clients:

```bash
cd web
npm run gen:proto
```

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
