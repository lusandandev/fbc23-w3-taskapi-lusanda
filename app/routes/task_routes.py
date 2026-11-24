"""Expose authenticated task CRUD endpoints and assemble their controller dependencies."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.controllers.task_controller import TaskController
from app.db.session import get_db
from app.infrastructure.auth import get_current_user_id
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_controller(db: Session = Depends(get_db)) -> TaskController:
    """Build the task repository, service, and controller for the current request."""
    repository = TaskRepository(db)
    return TaskController(TaskService(repository))


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
def create_task(
    payload: TaskCreate,
    response: Response,
    user_id: int = Depends(get_current_user_id),
    controller: TaskController = Depends(get_task_controller),
):
    """Create a task for the authenticated user."""
    return controller.create_task(user_id=user_id, payload=payload, response=response)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    task_status: str | None = Query(default=None, alias="status"),
    user_id: int = Depends(get_current_user_id),
    controller: TaskController = Depends(get_task_controller),
):
    """List the authenticated user's tasks, optionally filtered by status."""
    return controller.list_tasks(user_id=user_id, status_filter=task_status)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    controller: TaskController = Depends(get_task_controller),
):
    """Retrieve a task belonging to the authenticated user."""
    return controller.get_task(user_id=user_id, task_id=task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    user_id: int = Depends(get_current_user_id),
    controller: TaskController = Depends(get_task_controller),
):
    """Partially update a task belonging to the authenticated user."""
    return controller.update_task(user_id=user_id, task_id=task_id, payload=payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    controller: TaskController = Depends(get_task_controller),
):
    """Delete a task belonging to the authenticated user and return HTTP 204."""
    controller.delete_task(user_id=user_id, task_id=task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
