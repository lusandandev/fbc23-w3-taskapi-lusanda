# Containerised Task API: Week 3

A task tracker REST API built with **Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic and Docker Compose**

## Reference
`/docs/FVC23 - DEV - Week 3 Pt 1.pdf`

## Start the system

Docker and Docker Compose are required. Codespaces works too.

```bash
cp .env.example .env
```

Edit `.env` and set a local `POSTGRES_PASSWORD` and a random `JWT_SECRET` of at least 32 characters. The Compose file builds the API `DATABASE_URL` from the same PostgreSQL variables. Leave the two seed user passwords. Then start the API and database:

```bash
docker compose build
docker compose up
```

Compose waits for PostgreSQL's health check. The API container runs `alembic upgrade head` before Uvicorn starts.

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

Then:

```bash
docker compose down
```

To remove the database volume and prove that migrations rebuild an empty database:

```bash
docker compose down -v
docker compose up --build
```

**Warning:** `docker compose down -v` permanently deletes the local PostgreSQL volume.

## Seed demonstration data

In a second terminal, run:

```bash
docker compose exec api python -m scripts.seed
```

The seed script is idempotent and creates two users plus three tasks if they do not already exist. The seed credentials are configured through `SEED_USER*_EMAIL` and `SEED_USER*_PASSWORD` in `.env`; change them before use. They are demonstration credentials, not production credentials.

## Authentication

Register a user:

```bash
curl -i -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"StrongPass123!"}'
```

Sign in:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"StrongPass123!"}'
```

Copy `access_token` from the response and send it on protected requests:

```bash
-H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

Registration and login do not require a token. The health endpoint does not require a token. All task endpoints require one.

## API endpoints

| Method | Endpoint | Purpose | Success |
|---|---|---|---|
| POST | `/auth/register` | Register a user | `201` |
| POST | `/auth/login` | Sign in and receive a JWT | `200` |
| GET | `/health` | Check database connectivity | `200` or `503` |
| POST | `/tasks` | Create a task | `201` + `Location` header |
| GET | `/tasks` | List own tasks; optional `?status=todo` filter | `200` |
| GET | `/tasks/{task_id}` | Get one of own tasks | `200` |
| PATCH | `/tasks/{task_id}` | Partially update own task | `200` |
| DELETE | `/tasks/{task_id}` | Delete own task | `204` |

Valid task statuses are `todo`, `in_progress` and `done`. New tasks default to `todo`. The list is ordered by soonest due date first, with tasks that have no due date at the end. An unknown status filter returns `400`.

A task with status `done` cannot be moved back to `todo`; the API returns `409` with a clear message. A task owned by another user is treated as not found (`404`).

## Testing

Install dependencies in a Python 3.12 virtual environment if you want to run tests outside Docker:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

The service tests use a fake task repository and do not need a running PostgreSQL database. The Postman collection is in `postman/Task-Tracker-API.postman_collection.json`; import it into Postman, start the Docker services and run the collection. The collection creates two users, captures their tokens and task IDs, checks endpoint success paths, verifies cross-user task isolation, and exercises failure cases.

## Layer responsibilities

- **Routes:** declare HTTP methods, paths, request models and FastAPI dependencies.
- **Controllers:** coordinate the service and translate known business exceptions into HTTP status codes.
- **Services:** implement business rules and call repository interfaces; they do not contain SQL.
- **Repositories:** own SQLAlchemy queries and persistence operations.
- **Schemas:** validate request data before business logic is called and shape API responses.
- **Infrastructure:** password hashing, JWT creation/verification and bearer-token parsing.

`Depends` is FastAPI's dependency-injection mechanism. A route declares that it needs a controller; FastAPI resolves the controller dependency, which requests a DB session, constructs a repository, passes it to a service, and passes the service to the controller. FastAPI then cleans up the request-scoped DB session after the request.

## Cut list if time is short

Keep all hard requirements and all functional requirements. Drop only non-required polish, in this order: custom logging formatting, extra README examples, and additional seed-data variety. Do not drop Docker, PostgreSQL, FastAPI, migrations, authentication, task ownership, the FR-8 rule, the tests or the Postman collection.

