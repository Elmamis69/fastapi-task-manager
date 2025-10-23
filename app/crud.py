from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Sequence
from . import models, schemas

async def list_tasks(
    session: AsyncSession,
    completed: bool | None = None,
    limit: int = 50,
    offset: int = 0
) -> Sequence[models.Task]:
    stmt = select(models.Task).order_by(models.Task.due_date.is_(None), models.Task.due_date, models.Task.created_at)
    if completed is not None:
        stmt = stmt.filter(models.Task.is_completed == completed)
    stmt = stmt.limit(limit).offset(offset)
    result = await session.execute(stmt)
    return result.scalars().all()

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
    # row[0] is models.Task (SQLAlchemy 2.0 returning)
    return row[0]

async def delete_task(session: AsyncSession, task_id: int) -> bool:
    stmt = delete(models.Task).where(models.Task.id == task_id)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0
