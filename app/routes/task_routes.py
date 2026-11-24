from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.controllers.task_controller import TaskController
from app.db.session import get_db
from app.infrastructure.auth import get_current_user_id
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_controller(db: Session = Depends(get_db)) -> TaskController:
    repo = TaskRepository(db)
    service = TaskService(repo)
    return TaskController(service)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
def create_task(
    payload: TaskCreate,
    response: Response,
    user_id: int = Depends(get_current_user_id),
    controller: TaskController = Depends(get_task_controller),
):
    return controller.create_task(user_id=user_id, payload=payload, response=response)


@router.patch("/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    user_id: int = Depends(get_current_user_id),
    controller: TaskController = Depends(get_task_controller),
):
    return controller.update_task(user_id=user_id, task_id=task_id, payload=payload)