from typing import Literal
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Task
from . import schemas

OrderBy = Literal["due_date", "created_at", "title"]

async def list_tasks(
    session: AsyncSession,
    user_id: int,
    completed: bool | None,
    limit: int,
    offset: int,
    order_by: OrderBy,
    order_dir: str,
):
    q = select(Task).where(Task.user_id == user_id)
    if completed is not None:
        q = q.where(Task.is_completed == completed)

    if order_by == "due_date":
        order_col = Task.due_date
    elif order_by == "title":
        order_col = Task.title
    else:
        order_col = Task.created_at

    q = q.order_by(order_col.desc() if order_dir == "desc" else order_col.asc()).limit(limit).offset(offset)
    res = await session.execute(q)
    items = res.scalars().all()

    count_q = select(func.count()).select_from(Task).where(Task.user_id == user_id)
    if completed is not None:
        count_q = count_q.where(Task.is_completed == completed)
    total = (await session.execute(count_q)).scalar_one()

    return items, total


async def get_task(session: AsyncSession, user_id: int, task_id: int):
    res = await session.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    return res.scalar_one_or_none()


async def create_task(session: AsyncSession, user_id: int, payload: schemas.TaskCreate):
    task = Task(
        title=payload.title,
        description=payload.description,
        is_completed=payload.is_completed,
        due_date=payload.due_date,
        user_id=user_id,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def update_task(session: AsyncSession, user_id: int, task_id: int, payload: schemas.TaskUpdate):
    task = await get_task(session, user_id, task_id)
    if not task:
        return None

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.is_completed is not None:
        task.is_completed = payload.is_completed
    if payload.due_date is not None:
        task.due_date = payload.due_date

    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, user_id: int, task_id: int) -> bool:
    task = await get_task(session, user_id, task_id)
    if not task:
        return False
    await session.delete(task)
    await session.commit()
    return True
