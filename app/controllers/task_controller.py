"""Translate task-service results and domain errors into HTTP-level responses."""

from fastapi import HTTPException, Response, status

from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import (
    InvalidStatusTransitionError,
    InvalidTaskStatusError,
    TaskNotFoundError,
    TaskService,
)


class TaskController:
    """Coordinate task service calls and convert expected domain errors into HTTP errors."""
    def __init__(self, service: TaskService) -> None:
        """Store the task service used by this controller."""
        self.service = service

    def create_task(self, user_id: int, payload: TaskCreate, response: Response):
        """Create a task for the authenticated user and return its resource location."""
        task = self.service.create_task(user_id=user_id, payload=payload)
        response.headers["Location"] = f"/tasks/{task.id}"
        return task

    def list_tasks(self, user_id: int, status_filter: str | None = None):
        """List the user's tasks, optionally filtering by a validated status."""
        try:
            return self.service.list_tasks(user_id=user_id, status_filter=status_filter)
        except InvalidTaskStatusError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    def get_task(self, user_id: int, task_id: int):
        """Return one task belonging to the authenticated user."""
        try:
            return self.service.get_task(user_id=user_id, task_id=task_id)
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    def update_task(self, user_id: int, task_id: int, payload: TaskUpdate):
        """Apply a partial update and translate missing-task or invalid-transition errors."""
        try:
            return self.service.update_task(
                user_id=user_id, task_id=task_id, payload=payload
            )
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except InvalidStatusTransitionError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    def delete_task(self, user_id: int, task_id: int) -> None:
        """Delete a task owned by the authenticated user."""
        try:
            self.service.delete_task(user_id=user_id, task_id=task_id)
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
