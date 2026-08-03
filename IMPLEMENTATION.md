# Implementation

How the Neighborhood Library app is put together: request flow, main design choices, assumptions, and known issues.

## High-level flow

```
Staff browser
  → web (nginx :8080)          serves the Next.js static UI
       → Envoy (:8081)         gRPC-Web → native gRPC
            → library-service (:50051)
                 → PostgreSQL (:5432)
```

1. Staff opens the UI and signs in (`admin` / `admin` by default).
2. The UI calls gRPC-Web methods generated from `proto/` (books, members, loans, auth).
3. Those calls go to the **same origin** as the page. Nginx matches paths under `neighborhood.library.v1.*` and proxies them to Envoy.
4. Envoy converts gRPC-Web to gRPC and forwards to `library-service:50051`.
5. The Python server checks JWT (except `Login`), runs service/repo logic, and reads/writes Postgres.

## Layers


| Piece              | Role                                                                       |
| ------------------ | -------------------------------------------------------------------------- |
| `proto/`           | API contract (messages + RPC methods). Package: `neighborhood.library.v1`. |
| `library-service/` | Models → repositories → services → gRPC servicers. Alembic for schema.     |
| `envoy/`           | gRPC-Web gateway (also handles CORS).                                      |
| `web/`             | Next.js staff console (static export) served by nginx.                     |


Typical write path (example: create a book):

UI form → `BookService/CreateBook` → Envoy → servicer → `BookService.create` → repository → Postgres → response mapped back to protobuf → UI table refresh.

Borrow / return follow the same path through `LoanService`, with stock and membership checks in the service layer.

## Database schema (summary)

Three main tables in PostgreSQL (Alembic migrations under `library-service/alembic/versions/`):

| Table | Purpose |
|-------|---------|
| `books` | Catalog (title, author, ISBN, genre, quantities, …). Soft-deleted via `deleted_at`. |
| `members` | Patrons (name, email, contact, membership dates). Soft-deleted via `deleted_at`. |
| `loans` | Borrow events (`book_id`, `member_id`, `borrowed_at`, `due_at`, `returned_at`). Hard-deleted only if ever removed; history kept when books/members are soft-deleted. |

Relationships: a loan references one book and one member. Available stock is derived from total quantity minus active loans.

## Soft deletes

Books and members are **soft-deleted** (`deleted_at`), not removed from the database.

- A book (or member) with only returned loans can be removed from the catalog/staff lists without breaking past loan rows that still reference it.
- Hard delete would either fail on foreign keys or wipe borrow history.
- Active loans still block delete so you cannot drop something that is currently checked out.

## Authentication

Login is **config-based**: username/password and JWT secret come from environment settings (`AUTH_USERNAME`, `AUTH_PASSWORD`, `JWT_SECRET`, etc.). There is a single staff account for the demo.

- `AuthService/Login` is public and returns a JWT.
- All other RPCs require `Authorization: Bearer <token>`.
- **Authorization** (roles, permissions, per-resource access) is out of scope.

## Assumptions

- One staff user is enough; no multi-tenant or member-facing portal.
- Default loan length is 7 days unless a due date is chosen at borrow time.
- gRPC + gRPC-Web (via Envoy) is the service interface; no full REST API (only a small HTTP `/health` endpoint).
- Seed data on first boot is for demos (overdue + out-of-stock examples); it is idempotent.
- Docker Compose is how the full stack is run and tested.

## Considerations

- **Soft deletes** were added so staff can retire books/members that are no longer offered, without losing borrow history. Hard deletes would either block those deletes or erase historical links.
- **Config-based auth** keeps the take-home focused on library operations. Building a full user store and authorization model was treated as out of scope.
- List RPCs use **offset page tokens** and a UI page-size control (10 / 20 / 50).
- Validation (ISBN length, email format, stock, membership dates) and clear gRPC errors are handled in the service layer.

## Known issues

- **Stale JWT after rebuild or long idle.** If the Docker image/stack is rebuilt (or the UI sits long enough for the token to expire), the web app may show an invalid-token style error. **Fix:** log out and log in again.
- **Error placement.** Failures are shown in a fixed message area near the top of the page, not as a toast/banner next to the action. When delete fails because of active loans, you may need to **scroll up** to see the error.

## How to run and test

See the [README](README.md) for Docker setup, credentials, seed behavior, UI checks, unit tests in the container, and optional grpcurl.