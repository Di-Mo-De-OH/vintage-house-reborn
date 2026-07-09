from unittest.mock import AsyncMock

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.services.email import CODE_EXPIRE_SECONDS
from app.auth.utils.redis import EmailRedis
from app.core.redis import redis_client


async def test_send_email_success(client: AsyncClient, mock_send_email: AsyncMock) -> None:
    response = await client.post("/api/v1/auth/send-email", json={"email": "test@example.com"})

    assert response.status_code == 204
    mock_send_email.assert_called_once()


async def test_send_email_cooldown(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/send-email", json={"email": "cooldown@example.com"})
    response = await client.post("/api/v1/auth/send-email", json={"email": "cooldown@example.com"})

    assert response.status_code == 429


async def test_verify_email_success(client: AsyncClient) -> None:
    await redis_client.set(EmailRedis.code("verify@example.com"), "123456", ex=CODE_EXPIRE_SECONDS)

    response = await client.post(
        "/api/v1/auth/verify-email",
        json={"email": "verify@example.com", "code": "123456"},
    )

    assert response.status_code == 200
    assert "verify_token" in response.json()


async def test_verify_email_wrong_code(client: AsyncClient) -> None:
    await redis_client.set(EmailRedis.code("wrong@example.com"), "123456", ex=CODE_EXPIRE_SECONDS)

    response = await client.post(
        "/api/v1/auth/verify-email",
        json={"email": "wrong@example.com", "code": "654321"},
    )

    assert response.status_code == 400


async def test_verify_email_duplicate(client: AsyncClient, db: AsyncSession) -> None:
    db.add(
        User(
            email="duplicate@example.com",
            hashed_password="hashed",
            name="tester",
            nickname="tester",
        )
    )
    await db.commit()

    await redis_client.set(EmailRedis.code("duplicate@example.com"), "123456", ex=CODE_EXPIRE_SECONDS)

    response = await client.post(
        "/api/v1/auth/verify-email",
        json={"email": "duplicate@example.com", "code": "123456"},
    )

    assert response.status_code == 409
