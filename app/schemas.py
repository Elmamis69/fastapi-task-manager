from pydantic import BaseModel, Field
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    is_completed: bool = False
    due_date: datetime | None = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    is_completed: bool | None = None
    due_date: datetime | None = None

class TaskOut(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- NEW: pagination metadata ----------
class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int

class TaskListOut(BaseModel):
    items: list[TaskOut]
    meta: PageMeta