from types import SimpleNamespace

import pytest

from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import (
    InvalidStatusTransitionError,
    InvalidTaskStatusError,
    TaskNotFoundError,
    TaskService,
)


class FakeTaskRepository:
    def __init__(self, tasks=None):
        self.tasks = tasks or {}
        self.created = []
        self.deleted = []

    def create(self, user_id: int, data: dict):
        task = SimpleNamespace(id=99, user_id=user_id, **data)
        self.created.append(task)
        self.tasks[task.id] = task
        return task

    def list_by_user(self, user_id: int, status_filter=None):
        return [
            task
            for task in self.tasks.values()
            if task.user_id == user_id
            and (status_filter is None or task.status == status_filter)
        ]

    def get_by_id_and_user(self, task_id: int, user_id: int):
        task = self.tasks.get(task_id)
        return task if task is not None and task.user_id == user_id else None

    def save(self, task):
        self.tasks[task.id] = task
        return task

    def delete(self, task):
        self.deleted.append(task.id)
        del self.tasks[task.id]


def build_task(task_id=1, user_id=7, status="todo"):
    return SimpleNamespace(
        id=task_id,
        user_id=user_id,
        title="Original title",
        description=None,
        due_date=None,
        status=status,
    )


def test_create_task_uses_authenticated_user_and_default_status():
    repo = FakeTaskRepository()
    service = TaskService(repo)

    created = service.create_task(7, TaskCreate(title="Write tests"))

    assert created.user_id == 7
    assert created.title == "Write tests"
    assert created.status == "todo"


def test_list_tasks_can_filter_by_status():
    repo = FakeTaskRepository({1: build_task(1, 7, "todo"), 2: build_task(2, 7, "done")})

    results = TaskService(repo).list_tasks(7, "done")

    assert [task.id for task in results] == [2]


def test_list_tasks_rejects_unknown_status():
    service = TaskService(FakeTaskRepository())

    with pytest.raises(InvalidTaskStatusError):
        service.list_tasks(7, "blocked")


def test_get_task_returns_only_task_owned_by_user():
    service = TaskService(FakeTaskRepository({1: build_task()}))

    assert service.get_task(7, 1).id == 1
    with pytest.raises(TaskNotFoundError):
        service.get_task(8, 1)


def test_update_task_applies_only_supplied_fields():
    repo = FakeTaskRepository({1: build_task()})
    service = TaskService(repo)

    updated = service.update_task(7, 1, TaskUpdate(title="New title"))

    assert updated.title == "New title"
    assert updated.status == "todo"


def test_done_task_cannot_move_back_to_todo():
    repo = FakeTaskRepository({1: build_task(status="done")})

    with pytest.raises(InvalidStatusTransitionError):
        TaskService(repo).update_task(7, 1, TaskUpdate(status="todo"))


def test_delete_task_removes_owned_task():
    repo = FakeTaskRepository({1: build_task()})

    TaskService(repo).delete_task(7, 1)

    assert repo.deleted == [1]
    assert 1 not in repo.tasks


def test_update_missing_task_returns_not_found():
    with pytest.raises(TaskNotFoundError):
        TaskService(FakeTaskRepository()).update_task(7, 100, TaskUpdate(title="Nope"))
