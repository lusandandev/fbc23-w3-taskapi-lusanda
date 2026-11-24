"""Implement task use cases and enforce task ownership, status validation, and transition rules."""

from typing import Protocol

from app.schemas.task import TaskCreate, TaskUpdate

VALID_STATUSES = {"todo", "in_progress", "done"}


class TaskRepositoryPort(Protocol):
    """Describe the repository operations required by the task service."""
    def create(self, user_id: int, data: dict): ...
    def list_by_user(self, user_id: int, status_filter: str | None = None): ...
    def get_by_id_and_user(self, task_id: int, user_id: int): ...
    def save(self, task): ...
    def delete(self, task) -> None: ...


class TaskNotFoundError(Exception):
    """Signal that a task does not exist for the requested user."""
    pass


class InvalidStatusTransitionError(Exception):
    """Signal that a requested task status change violates a business rule."""
    pass


class InvalidTaskStatusError(Exception):
    """Signal that a task status filter is not supported."""
    pass


class TaskService:
    """Apply task-management business rules without depending on HTTP or database details."""
    def __init__(self, repo: TaskRepositoryPort) -> None:
        """Store the repository implementation used by this service."""
        self.repo = repo

    def create_task(self, user_id: int, payload: TaskCreate):
        """Create a task using the authenticated user's ID and validated request data."""
        return self.repo.create(user_id=user_id, data=payload.model_dump())

    def list_tasks(self, user_id: int, status_filter: str | None = None):
        """Validate an optional status filter before retrieving the user's tasks."""
        if status_filter is not None and status_filter not in VALID_STATUSES:
            raise InvalidTaskStatusError(
                "Unknown status. Use todo, in_progress or done"
            )
        return self.repo.list_by_user(user_id=user_id, status_filter=status_filter)

    def get_task(self, user_id: int, task_id: int):
        """Retrieve a task for its owner or raise a not-found domain error."""
        task = self.repo.get_by_id_and_user(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError("Task not found")
        return task

    def update_task(self, user_id: int, task_id: int, payload: TaskUpdate):
        """Apply only supplied fields after checking the allowed status transition."""
        task = self.get_task(user_id=user_id, task_id=task_id)
        # exclude_unset keeps omitted PATCH fields unchanged instead of overwriting them with defaults.
        updates = payload.model_dump(exclude_unset=True)

        # FR-8: a completed task cannot be moved back to todo.
        if task.status == "done" and updates.get("status") == "todo":
            raise InvalidStatusTransitionError(
                "A task marked as done cannot be moved back to todo"
            )

        for field, value in updates.items():
            setattr(task, field, value)
        return self.repo.save(task)

    def delete_task(self, user_id: int, task_id: int) -> None:
        """Delete a task only after confirming that it belongs to the user."""
        task = self.get_task(user_id=user_id, task_id=task_id)
        self.repo.delete(task)
