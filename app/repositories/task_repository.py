"""Persist and query task records while consistently scoping operations to their owner."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task


class TaskRepository:
    """Implement database persistence and retrieval for task records."""
    def __init__(self, db: Session) -> None:
        """Store the SQLAlchemy session used by task queries and writes."""
        self.db = db

    def create(self, user_id: int, data: dict) -> Task:
        """Insert a task for a user, commit it, and refresh its database-generated values."""
        task = Task(user_id=user_id, **data)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list_by_user(self, user_id: int, status_filter: str | None = None) -> list[Task]:
        """Return a user's tasks, optionally filtered by status and ordered by due date."""
        stmt = select(Task).where(Task.user_id == user_id)
        if status_filter is not None:
            stmt = stmt.where(Task.status == status_filter)
        stmt = stmt.order_by(Task.due_date.asc().nulls_last(), Task.id.asc())
        return list(self.db.scalars(stmt).all())

    def get_by_id_and_user(self, task_id: int, user_id: int) -> Task | None:
        """Find a task only when both its ID and owning user ID match."""
        # Filter by owner in the database query so another user's task is never returned.
        stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        return self.db.scalar(stmt)

    def save(self, task: Task) -> Task:
        """Commit changes to a task and refresh its persisted state."""
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        """Delete a task record and commit the transaction."""
        self.db.delete(task)
        self.db.commit()
