# Task Tracker API

A REST API for tasks with user accounts. Built with Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic and Docker Compose.

Brief: `docs/FBC23 - DEV - Week 3 Pt 1.pdf`

## Run it

Only Docker is needed.

```bash
cp .env.example .env
docker compose up --build
```

The defaults in `.env.example` work for local use. Migrations run automatically before the API starts.

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>

Stop: `docker compose down`

Reset the database (deletes all data): `docker compose down -v`

## Seed demo data

With the stack running:

```bash
docker compose exec api python -m scripts.seed
```

Creates two users and three tasks. The logins come from the `SEED_*` values in `.env` (default `alice@example.com` and `bob@example.com`, password `ChangeMe123!`). Safe to run more than once.

## Endpoints

| Method | Path | What it does | Success |
|---|---|---|---|
| POST | `/auth/register` | Register a user | 201 |
| POST | `/auth/login` | Sign in, get a token | 200 |
| GET | `/health` | Check the database connection | 200 / 503 |
| POST | `/tasks` | Create a task | 201 + `Location` |
| GET | `/tasks` | List your tasks (`?status=todo`) | 200 |
| GET | `/tasks/{id}` | Get one task | 200 |
| PATCH | `/tasks/{id}` | Update a task | 200 |
| DELETE | `/tasks/{id}` | Delete a task | 204 |

All `/tasks` endpoints need `Authorization: Bearer <token>` from `/auth/login`.

## Rules

- Status is `todo`, `in_progress` or `done`. The default is `todo`.
- The list is sorted by due date, soonest first. Tasks with no due date come last.
- A `done` task cannot go back to `todo` (409).
- Another user's task is a 404.
- Invalid input is a 400. A missing or bad token is a 401.

## Tests

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
```

The service tests use a fake repository, so no database is needed.

Postman: import `postman/Task-Tracker-API.postman_collection.json`, start the stack, run the collection.

## Structure

Request flow: route → controller → service → repository → PostgreSQL.

- `app/routes`: paths and FastAPI dependencies
- `app/controllers`: turn service errors into HTTP responses
- `app/services`: business rules, no SQL
- `app/repositories`: all database queries
- `app/schemas`: request validation and response shapes
- `app/infrastructure`: password hashing and tokens

FastAPI's `Depends` builds each request's chain: the route asks for a controller, which needs a service, which needs a repository, which needs a database session. The session is closed after the request.

## Cut list

If time ran short, i would drop log formatting, extra seed data. Could never be drop a hard requirement.
