# neighborhood-library-portal

Assessment for numinolabs interview.

## Structure

```
library-service/     Backend API (FastAPI), SQLAlchemy models, Alembic migrations
web/                 React frontend (Vite); nginx serves the production build
docker-compose.yml   Runs Postgres, library-service, and web together
```

## Docker

```bash
docker compose up --build
```

| Service           | URL                          |
|-------------------|------------------------------|
| web               | http://localhost:8080        |
| library-service   | http://localhost:8000        |
| Postgres          | localhost:5432               |

Migrations run on `library-service` startup (`alembic upgrade head`).

## Local library-service

```bash
cd library-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Migrations

From `library-service/`:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```
