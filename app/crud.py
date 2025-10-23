from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from typing import Sequence, Literal
from . import models, schemas

OrderBy = Literal["due_date", "created_at", "title"]

async def list_tasks(
    session: AsyncSession,
    completed: bool | None = None,
    limit: int = 50,
    offset: int = 0,
    order_by: OrderBy = "due_date",
    order_dir: Literal["asc", "desc"] = "asc",
):
    # base query
    stmt = select(models.Task)
    if completed is not None:
        stmt = stmt.filter(models.Task.is_completed == completed)

    # ordering
    order_col = {
        "due_date": models.Task.due_date,
        "created_at": models.Task.created_at,
        "title": models.Task.title,
    }[order_by]

    if order_by == "due_date":
        # nulls last
        stmt = stmt.order_by(models.Task.due_date.is_(None))
    stmt = stmt.order_by(order_col.desc() if order_dir == "desc" else order_col.asc())

    # pagination
    stmt = stmt.limit(limit).offset(offset)

    # fetch items
    result = await session.execute(stmt)
    items = result.scalars().all()

    # total count (with same filter but without limit/offset)
    count_stmt = select(func.count(models.Task.id))
    if completed is not None:
        count_stmt = count_stmt.filter(models.Task.is_completed == completed)
    total = (await session.execute(count_stmt)).scalar_one()

    return items, total

async def get_task(session: AsyncSession, task_id: int) -> models.Task | None:
    result = await session.execute(select(models.Task).where(models.Task.id == task_id))
    return result.scalar_one_or_none()

async def create_task(session: AsyncSession, payload: schemas.TaskCreate) -> models.Task:
    task = models.Task(**payload.model_dump())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

async def update_task(session: AsyncSession, task_id: int, payload: schemas.TaskUpdate) -> models.Task | None:
    data = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not data:
        return await get_task(session, task_id)

    stmt = (
        update(models.Task)
        .where(models.Task.id == task_id)
        .values(**data)
        .returning(models.Task)
    )
    result = await session.execute(stmt)
    row = result.fetchone()
    if not row:
        await session.rollback()
        return None
    await session.commit()
    return row[0]

async def delete_task(session: AsyncSession, task_id: int) -> bool:
    stmt = delete(models.Task).where(models.Task.id == task_id)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0
