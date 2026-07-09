from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest

from app.core.redis import redis_client


@pytest.fixture(autouse=True)
def mock_send_email() -> Generator[AsyncMock, None, None]:
    with patch("app.auth.services.email.send_email", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture(autouse=True)
async def cleanup_redis() -> AsyncGenerator[None, None]:
    yield
    async for key in redis_client.scan_iter("email:*"):
        await redis_client.delete(key)
