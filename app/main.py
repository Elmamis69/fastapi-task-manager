from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session, init_models
from . import crud, schemas, auth_crud
from .models import User
from .deps import get_current_user

app = FastAPI(title="Task Manager API", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_models()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

# ======= AUTH =======

@app.post("/auth/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: schemas.UserCreate, session: AsyncSession = Depends(get_session)):
    user = await auth_crud.register_user(session, payload)
    if user is None:
        raise HTTPException(status_code=400, detail="Email is already registered")
    return user

@app.post("/auth/login", response_model=schemas.TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    token_and_user = await auth_crud.login_user(session, form_data.username, form_data.password)
    if token_and_user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token, _user = token_and_user
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.UserOut)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

# ======= TASKS (protegidas) =======

@app.get("/tasks", response_model=schemas.TaskListOut)
async def list_tasks(
    completed: bool | None = Query(default=None, description="Filtrar por completadas (true/false)"),
    limit: int = Query(default=10, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    order_by: crud.OrderBy = Query(default="due_date", description="due_date|created_at|title"),
    order_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    items, total = await crud.list_tasks(
        session,
        user_id=current_user.id,
        completed=completed,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_dir=order_dir,
    )
    return {"items": items, "meta": {"total": total, "limit": limit, "offset": offset}}

@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
async def get_task(task_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    task = await crud.get_task(session, current_user.id, task_id)
    if not task:
        raise HTTPException(404, detail="Task not found")
    return task

@app.post("/tasks", response_model=schemas.TaskOut, status_code=201)
async def create_task(payload: schemas.TaskCreate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    return await crud.create_task(session, current_user.id, payload)

@app.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
async def update_task(task_id: int, payload: schemas.TaskUpdate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    task = await crud.update_task(session, current_user.id, task_id, payload)
    if not task:
        raise HTTPException(404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    ok = await crud.delete_task(session, current_user.id, task_id)
    if not ok:
        raise HTTPException(404, detail="Task not found")
    return None
