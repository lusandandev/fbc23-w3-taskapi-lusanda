from fastapi import HTTPException, Response, status

from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import (
    InvalidStatusTransitionError,
    InvalidTaskStatusError,
    TaskNotFoundError,
    TaskService,
)


class TaskController:
    def __init__(self, service: TaskService) -> None:
        self.service = service

    def create_task(self, user_id: int, payload: TaskCreate, response: Response):
        task = self.service.create_task(user_id=user_id, payload=payload)
        response.headers["Location"] = f"/tasks/{task.id}"
        return task

    def list_tasks(self, user_id: int, status_filter: str | None = None):
        try:
            return self.service.list_tasks(user_id=user_id, status_filter=status_filter)
        except InvalidTaskStatusError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    def get_task(self, user_id: int, task_id: int):
        try:
            return self.service.get_task(user_id=user_id, task_id=task_id)
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    def update_task(self, user_id: int, task_id: int, payload: TaskUpdate):
        try:
            return self.service.update_task(
                user_id=user_id, task_id=task_id, payload=payload
            )
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except InvalidStatusTransitionError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    def delete_task(self, user_id: int, task_id: int) -> None:
        try:
            self.service.delete_task(user_id=user_id, task_id=task_id)
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
