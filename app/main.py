from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session, init_models
from . import crud, schemas

app = FastAPI(title="Task Manager API", version="0.2.0")

# ... (CORS y startup se quedan igual)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

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
        order_dir=order_dir,  # "asc" | "desc"
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
