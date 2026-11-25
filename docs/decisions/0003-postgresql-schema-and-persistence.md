# Decision 0003: Use PostgreSQL migrations and a named data volume

## Context

The brief requires PostgreSQL as the only running database, schema creation through migrations, and persistent data that survives a container restart. Creating tables manually or relying on an in-memory or SQLite database would not meet the requirement.

## Decision

Use PostgreSQL 17 for runtime persistence and SQLAlchemy for data access. Use Alembic to version schema changes. The initial migration creates `users` and `tasks`, including a unique email index and a foreign key from each task to its owner. Compose stores PostgreSQL files in a named volume mounted at `/var/lib/postgresql/data`.

The database service exposes a `pg_isready` health check. Compose marks the API as dependent on `db` with `condition: service_healthy`. The API container runs `alembic upgrade head` before Uvicorn.

## Consequences

- A fresh database receives the same schema by running the committed Alembic migrations.
- Application data survives ordinary container recreation.
- Schema changes must be added as new migration revisions, not made manually in a running database.
- `docker compose down -v` removes the named volume and is therefore a destructive reset.
