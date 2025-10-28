from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .db import get_session, init_models
from . import crud, schemas
from . import auth_crud
from .security import decode_token
from .models import User  # para /me

app = FastAPI(title="Task Manager API", version="0.3.0")

# CORS config (ajústalo si luego tienes frontend específico)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod limitas esto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await init_models()


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


# =========================
# AUTH ROUTES
# =========================

@app.post("/auth/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: schemas.UserCreate,
    session: AsyncSession = Depends(get_session),
):
    user = await auth_crud.register_user(session, payload)
    if user is None:
        # ya existe ese correo
        raise HTTPException(status_code=400, detail="Email is already registered")
    return user


@app.post("/auth/login", response_model=schemas.TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    token_and_user = await auth_crud.login_user(session, form_data.username, form_data.password)
    if token_and_user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token, user = token_and_user
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserOut)
async def read_current_user(
    token: str = Query(..., description="JWT access token"),
    session: AsyncSession = Depends(get_session),
):
    email = decode_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    res = await session.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# =========================
# TASK ROUTES
# =========================

@app.get("/tasks", response_model=schemas.TaskListOut)
async def list_tasks(
    completed: bool | None = Query(default=None, description="Filtrar por completadas (true/false)"),
    limit: int = Query(default=10, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    order_by: crud.OrderBy = Query(default="due_date", description="due_date|created_at|title"),
    order_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
    session: AsyncSession = Depends(get_session),
):
    items, total = await crud.list_tasks(
        session,
        completed=completed,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_dir=order_dir,
    )
    return {
        "items": items,
        "meta": {"total": total, "limit": limit, "offset": offset},
    }


@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
async def get_task(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await crud.get_task(session, task_id)
    if not task:
        raise HTTPException(404, detail="Task not found")
    return task


@app.post("/tasks", response_model=schemas.TaskOut, status_code=201)
async def create_task(payload: schemas.TaskCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_task(session, payload)


@app.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
async def update_task(task_id: int, payload: schemas.TaskUpdate, session: AsyncSession = Depends(get_session)):
    task = await crud.update_task(session, task_id, payload)
    if not task:
        raise HTTPException(404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session)):
    ok = await crud.delete_task(session, task_id)
    if not ok:
        raise HTTPException(404, detail="Task not found")
    return None
