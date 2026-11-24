"""Define validated task request and response models, including partial-update rules."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

TaskStatus = Literal["todo", "in_progress", "done"]


class TaskCreate(BaseModel):
    """Validate the fields accepted when a task is created."""
    title: str = Field(min_length=1, max_length=100)
    description: str | None = None
    due_date: datetime | None = None
    status: TaskStatus = "todo"


class TaskUpdate(BaseModel):
    # None is allowed as the default so fields may be omitted from a PATCH.
    # title and status themselves cannot explicitly be set to null.
    """Validate optional fields for a partial task update while rejecting null required fields."""
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    due_date: datetime | None = None
    status: TaskStatus | None = None

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        """Reject explicit null values for title and status while allowing omitted fields."""
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("title cannot be null")
        if "status" in self.model_fields_set and self.status is None:
            raise ValueError("status cannot be null")
        return self


class TaskResponse(BaseModel):
    """Define the task fields returned by the API, including its owner ID."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    due_date: datetime | None
    status: TaskStatus
    user_id: int
