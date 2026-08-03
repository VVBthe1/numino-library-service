# Neighborhood Library

Staff console for a small neighborhood library: manage books, members, and loans.

For request flow, design choices, assumptions, and known issues, see the [Implementation doc](IMPLEMENTATION.md).

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

- Docker and Docker Compose

## Run locally

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

On first boot the API runs migrations (`alembic upgrade head`) and an idempotent seed (`scripts/seed.py`): a few books/members, one **overdue** loan, and an **out of stock** title so those screens aren’t empty.

**Protobuf:** sources live in `proto/`. Generated Python stubs are checked in under `library-service/app/pb/` (and the web clients under `web/src/gen/`). To regenerate after editing `.proto` files:

```bash
docker compose exec library-service python scripts/generate_protos.py
```

(Frontend stubs are produced separately with the protobuf-ts tooling in `web/` when you change the API contract.)

**Main env vars** (also set in `docker-compose.yml` for the API service): `DATABASE_URL`, `GRPC_HOST`, `GRPC_PORT`, `JWT_SECRET`, `AUTH_USERNAME`, `AUTH_PASSWORD`.

Stop with `Ctrl+C`, or `docker compose down`.

## How to test

### UI

1. Open http://localhost:8080 and sign in (`admin` / `admin`).
2. Seeded data should already show books, members, loans; open **Overdue** and **Out of stock**.
3. Create more records or borrow / return on **Loans**.
4. Use filters on each list.
5. Delete a book/member that only has returned loans — it should leave the catalog but remain on loan history.

### Unit tests

With the stack up (`docker compose up --build`), run pytest inside the API container:

```bash
docker compose exec library-service sh -c "pip install -q -r requirements-dev.txt && python -m pytest -v"
```

### gRPC with grpcurl (optional)

Stack must be up (`docker compose up --build`). Run from the **repo root**. grpcurl JSON uses **camelCase** field names.

Install [grpcurl](https://github.com/fullstorydev/grpcurl) and [jq](https://jqlang.github.io/jq/) if needed:

```bash
# Debian / Ubuntu / WSL — jq
sudo apt-get update && sudo apt-get install -y jq

# macOS (Homebrew) — both
brew install grpcurl jq

# grpcurl via Go (ensure $(go env GOPATH)/bin is on PATH)
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# or grpcurl Linux amd64 binary (no Go)
curl -sL "https://github.com/fullstorydev/grpcurl/releases/download/v1.9.3/grpcurl_1.9.3_linux_x86_64.tar.gz" | sudo tar -xz -C /usr/local/bin grpcurl
```

Other platforms: https://github.com/fullstorydev/grpcurl/releases

```bash
# Shared setup
PROTO=(-import-path proto -proto auth.proto -proto book.proto -proto member.proto -proto loan.proto -proto entities.proto); HOST=localhost:50051

# 1. Login (domain calls without this return UNAUTHENTICATED)
export TOKEN=$(grpcurl -plaintext "${PROTO[@]}" -d '{"username":"admin","password":"admin"}' "$HOST" neighborhood.library.v1.AuthService/Login | jq -r .accessToken)

# 2. Create a book
BOOK=$(grpcurl -plaintext "${PROTO[@]}" -H "authorization: Bearer ${TOKEN}" -d '{"title":"The Dispossessed","author":"Ursula K. Le Guin","isbn":"9780060512750","genre":"GENRE_SCIENCE_FICTION","totalQuantity":2}' "$HOST" neighborhood.library.v1.BookService/CreateBook); echo "$BOOK" | jq .; BOOK_ID=$(echo "$BOOK" | jq -r .book.id)

# 3. Create a member
MEMBER=$(grpcurl -plaintext "${PROTO[@]}" -H "authorization: Bearer ${TOKEN}" -d '{"name":"Grace Hopper","email":"grace.hopper@example.com","membershipStartDate":"2024-01-01"}' "$HOST" neighborhood.library.v1.MemberService/CreateMember); echo "$MEMBER" | jq .; MEMBER_ID=$(echo "$MEMBER" | jq -r .member.id)

# 4. Borrow the book
LOAN=$(grpcurl -plaintext "${PROTO[@]}" -H "authorization: Bearer ${TOKEN}" -d "{\"bookId\":${BOOK_ID},\"memberId\":${MEMBER_ID}}" "$HOST" neighborhood.library.v1.LoanService/BorrowBook); echo "$LOAN" | jq .; LOAN_ID=$(echo "$LOAN" | jq -r .loan.id)

# 5. List that member’s active loans
grpcurl -plaintext "${PROTO[@]}" -H "authorization: Bearer ${TOKEN}" -d "{\"pageSize\":10,\"memberId\":${MEMBER_ID},\"activeOnly\":true}" "$HOST" neighborhood.library.v1.LoanService/ListLoans | jq .

# 6. List books / members
grpcurl -plaintext "${PROTO[@]}" -H "authorization: Bearer ${TOKEN}" -d '{"pageSize":10}' "$HOST" neighborhood.library.v1.BookService/ListBooks | jq .
grpcurl -plaintext "${PROTO[@]}" -H "authorization: Bearer ${TOKEN}" -d '{"pageSize":10}' "$HOST" neighborhood.library.v1.MemberService/ListMembers | jq .

# 7. Return the book
grpcurl -plaintext "${PROTO[@]}" -H "authorization: Bearer ${TOKEN}" -d "{\"loanId\":${LOAN_ID}}" "$HOST" neighborhood.library.v1.LoanService/ReturnBook | jq .

# Discover services
grpcurl -plaintext "${PROTO[@]}" "$HOST" list
```

Other useful calls: `GetOverdueBooks`, `GetOutOfStockBooks`, `UpdateBook`, `DeleteBook`.
