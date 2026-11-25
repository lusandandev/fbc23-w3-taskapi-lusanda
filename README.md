# Task Tracker API

A REST API for task tracking with user accounts. Built with Python 3.12, FastAPI, PostgreSQL 17, SQLAlchemy, Alembic and Docker Compose.

The project implements the fixed Week 3 specification in `docs/FBC23 - DEV - Week 3 Pt 1.pdf`.

## Run from a fresh clone

Docker is the only software that needs to be installed on the host. The API dependencies are included as pre-downloaded wheels in `wheelhouse/`, so the API image does not need to contact PyPI during its build.

```bash
cp .env.example .env
docker compose up --build -d
```

Check the services and API startup:

```bash
docker compose ps
docker compose logs --tail=100 api
```

The API container waits for PostgreSQL's health check, runs `alembic upgrade head`, and then starts Uvicorn.

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- Database health: <http://localhost:8000/health>

The API service is pinned to `linux/amd64` because the committed wheelhouse contains CPython 3.12 Linux x86-64 wheels. On ARM hosts, Docker may use emulation.

Stop the services without deleting database data:

```bash
docker compose down
```

Reset the database and delete its persistent volume (destructive):

```bash
docker compose down -v
```

## Configuration

Copy `.env.example` to `.env`. Compose reads `.env` for variable substitution and passes the required values into the API and database containers. `.env` is ignored by Git and must never be committed.

The values in `.env.example` are local-development placeholders, not production credentials. Replace the seed-user passwords before running the seed script. Use a newly generated JWT secret for any environment beyond a disposable local demonstration.

## Seed demonstration data

With the services running, set `SEED_USER1_PASSWORD` and `SEED_USER2_PASSWORD` in `.env` to local passwords of at least eight characters, then run:

```bash
docker compose exec api python -m scripts.seed
```

The script creates two users and three tasks. It hashes passwords before storing them and skips records that already exist, so it is safe to run repeatedly.

## API endpoints

| Method | Path | Purpose | Success |
|---|---|---|---|
| POST | `/auth/register` | Register a user | 201 |
| POST | `/auth/login` | Sign in and receive a token | 200 |
| GET | `/health` | Check database connectivity | 200 / 503 |
| POST | `/tasks` | Create a task | 201 + `Location` |
| GET | `/tasks` | List the signed-in user's tasks; optional `?status=` filter | 200 |
| GET | `/tasks/{task_id}` | Get one owned task | 200 |
| PATCH | `/tasks/{task_id}` | Partially update an owned task | 200 |
| DELETE | `/tasks/{task_id}` | Delete an owned task | 204 |

Every task endpoint requires `Authorization: Bearer <token>` from `/auth/login`.

## Business rules

- Task title is required and must contain 1–100 characters.
- Status is `todo`, `in_progress` or `done`; the default is `todo`.
- Tasks are scoped to the authenticated user. Another user's task is returned as 404.
- Task lists are ordered by due date, soonest first; tasks without a due date come last.
- A task marked `done` cannot be moved back to `todo` (409).
- Invalid request data returns 400; missing or invalid authentication returns 401.
- Unexpected server errors return a safe message while details are logged on the server.

## Tests

Run the service-layer tests locally with Python:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
```

The eight service tests use a fake repository, so they do not need a running database. The Postman collection also exercises endpoint success and failure cases:

`postman/Task-Tracker-API.postman_collection.json`

Import the collection into Postman, start the Compose stack, and run the collection against `http://localhost:8000` (or the forwarded Codespaces port).

## Architecture

Request flow: route → controller → service → repository → PostgreSQL.

- `app/main.py`: creates the FastAPI application, registers routers, middleware and exception handlers.
- `app/routes`: HTTP routes, request dependencies and authentication requirements.
- `app/controllers`: translates service/domain outcomes into HTTP responses.
- `app/services`: business rules; no SQL statements.
- `app/repositories`: SQLAlchemy queries and persistence.
- `app/schemas`: Pydantic request validation and response models.
- `app/infrastructure`: password hashing and JWT helpers.
- `app/db`: engine and request-scoped SQLAlchemy sessions.
- `alembic/`: versioned database schema migrations.

FastAPI's `Depends` resolves the request's dependency graph. For task routes, the route depends on `get_task_controller`; that provider receives a database session from `get_db`, creates a repository, passes it to the service, and returns the controller. `get_db` yields the session and closes it after the request. The bearer-token dependency independently resolves the signed-in user's ID.

## Week 2 → Week 3 learning records

- [Express-to-FastAPI mapping](docs/express-fastapi-mapping.md)
- [AI usage log](docs/ai-log.md)
- [Decision records](docs/decisions/)


## Cut list

If time becomes constrained, optional log formatting and extra demonstration data can be dropped. Docker, PostgreSQL, FastAPI, migrations, authentication, required task behaviour, tests and documentation are not cut list items because they are hard requirements.
