from fastapi import HTTPException, Response, status
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import (
    InvalidStatusTransitionError,
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

    def update_task(self, user_id: int, task_id: int, payload: TaskUpdate):
        try:
            return self.service.update_task(
                user_id=user_id, task_id=task_id, payload=payload
            )
        except TaskNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc
        except InvalidStatusTransitionError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(exc)
            ) from exc