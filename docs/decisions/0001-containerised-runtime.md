# Decision 0001: Run the API and PostgreSQL with Docker Compose

## Context

The Week 3 brief makes Docker, PostgreSQL and FastAPI hard requirements. A reviewer must be able to clone the repository, copy `.env.example` to `.env`, and start the API and database with Docker Compose. The database must persist across container recreation, and the API must not start migrations before PostgreSQL is ready.

## Decision

- Build the API from `python:3.12-slim` in the project `Dockerfile`.
- Run PostgreSQL 17 as the `db` Compose service.
- Run the API as the `api` Compose service and publish the configurable host port to container port 8000.
- Use a PostgreSQL `pg_isready` health check and `depends_on: condition: service_healthy` so the API starts after the database is ready.
- Store database data in the named `postgres_data` volume (`taskapi_postgres_data`).
- Run `alembic upgrade head` before starting Uvicorn in the API container command.
- Set `platform: linux/amd64` for the API because the committed wheelhouse contains CPython 3.12 Linux x86-64 wheels.

## Consequences

- The application and database can be started together with `docker compose up --build`.
- PostgreSQL data survives `docker compose down`; `docker compose down -v` deliberately deletes the volume and all stored data.
- The API container starts only after the database health check passes, and schema migrations run before the HTTP server starts.
- Pinning the API to AMD64 keeps the local wheelhouse compatible. ARM hosts may use emulation and run the API more slowly.
- Values that vary by environment are supplied through `.env`; `.env` is ignored and `.env.example` is committed.
