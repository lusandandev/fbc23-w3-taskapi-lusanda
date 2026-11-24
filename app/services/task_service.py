from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    pass


class InvalidStatusTransitionError(Exception):
    pass


class TaskService:
    def __init__(self, repo: TaskRepository) -> None:
        self.repo = repo

    def create_task(self, user_id: int, payload: TaskCreate):
        return self.repo.create(user_id=user_id, data=payload.model_dump())

    def update_task(self, user_id: int, task_id: int, payload: TaskUpdate):
        task = self.repo.get_by_id_and_user(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError("Task not found")

        # A task that is done cannot be moved back to todo
        if task.status == "done" and payload.status == "todo":
            raise InvalidStatusTransitionError(
                "A task marked as done cannot be moved back to todo"
            )

        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(task, field, value)

        return self.repo.save(task)