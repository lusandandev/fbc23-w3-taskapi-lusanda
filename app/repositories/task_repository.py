from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.task import Task


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user_id: int, data: dict) -> Task:
        task = Task(user_id=user_id, **data)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id_and_user(self, task_id: int, user_id: int) -> Task | None:
        stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        return self.db.scalar(stmt)

    def save(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task