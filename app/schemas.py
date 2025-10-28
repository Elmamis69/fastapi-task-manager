from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

# =========================
# TASK SCHEMAS
# =========================

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


class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int

class TaskListOut(BaseModel):
    items: list[TaskOut]
    meta: PageMeta


# =========================
# AUTH / USER SCHEMAS
# =========================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime   # <- OJO: "created_at", no "create_at"

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
