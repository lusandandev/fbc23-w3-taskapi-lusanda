from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

TaskStatus = Literal["todo", "in_progress", "done"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = None
    due_date: datetime | None = None
    status: TaskStatus = "todo"


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    due_date: datetime | None = None
    status: TaskStatus | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    due_date: datetime | None
    status: TaskStatus
    user_id: int