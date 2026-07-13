from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.redis import redis_client
from app.core.utils.security import hash_password


@pytest.fixture(autouse=True)
def mock_send_email() -> Generator[AsyncMock, None, None]:
    with patch("app.auth.services.email.send_email", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture(autouse=True)
async def cleanup_redis() -> AsyncGenerator[None, None]:
    yield
    async for key in redis_client.scan_iter("email:*"):
        await redis_client.delete(key)


@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    user = User(
        email="test@example.com",
        hashed_password=hash_password("Password@1"),
        name="tester",
        nickname="nickname",
    )
    db.add(user)
    await db.commit()
    return user


@pytest.fixture
async def test_user2(db: AsyncSession) -> User:
    user = User(
        email="test2@example.com",
        hashed_password=hash_password("Password@1"),
        name="test2",
        nickname="test2",
    )
    db.add(user)
    await db.commit()
    return user
