from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models, schemas
from .security import hash_password, verify_password, create_access_token

# Crear usuario (registro)
async def register_user(session: AsyncSession, payload: schemas.UserCreate):
    # Checar si ya existe un usuario con ese correo
    q = select(models.User).where(models.User.email == payload.email)
    res = await session.execute(q)
    existing = res.scalar_one_or_none()
    if existing:
        # el caller lo interpreta como "email repetido"
        return None

    user = models.User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# Login: validar credenciales y devolver token
async def login_user(session: AsyncSession, email: str, password: str):
    q = select(models.User).where(models.User.email == email)
    res = await session.execute(q)
    user = res.scalar_one_or_none()
    if not user:
        return None

    # checar password
    if not verify_password(password, user.hashed_password):
        return None

    # si pasó las validaciones, crear JWT
    token = create_access_token(subject=user.email)
    return token, user
