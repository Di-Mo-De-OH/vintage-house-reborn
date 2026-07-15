import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.utils.security import hash_password


@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    user = User(
        email="admin@example.com",
        hashed_password=hash_password("Password@1"),
        name="admin",
        nickname="admin",
        is_admin=True,
    )
    db.add(user)
    await db.commit()
    return user


@pytest.fixture
async def normal_user(db: AsyncSession) -> User:
    user = User(
        email="user@example.com",
        hashed_password=hash_password("Password@1"),
        name="user",
        nickname="user",
    )
    db.add(user)
    await db.commit()
    return user
