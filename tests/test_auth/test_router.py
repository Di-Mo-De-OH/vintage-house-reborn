from unittest.mock import AsyncMock

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.redis import EmailRedis
from app.auth.service.email import CODE_EXPIRE_SECONDS
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


async def test_signup_success(client: AsyncClient, db: AsyncSession) -> None:
    await redis_client.set(EmailRedis.verify("sometoken123"), "signup@example.com", ex=600)
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "password": "Password@1",
            "confirm_password": "Password@1",
            "name": "testname",
            "nickname": "testnick",
            "address": "testaddress",
            "verify_token": "sometoken123",
        },
    )
    assert response.status_code == 201
    assert response.json()["email"] == "signup@example.com"
    assert response.json()["nickname"] == "testnick"


async def test_signup_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "password": "Password@1",
            "confirm_password": "Password@1",
            "name": "testname",
            "nickname": "testnick",
            "address": "testaddress",
            "verify_token": "noting",
        },
    )
    assert response.status_code == 404


async def test_signup_duplicate_nickname(client: AsyncClient, db: AsyncSession) -> None:
    db.add(User(email="test@example.com", hashed_password="hashed", name="tester", nickname="testnick"))
    await db.commit()
    await redis_client.set(EmailRedis.verify("sometoken456"), "new@example.com", ex=600)
    responses = await client.post(
        "/api/v1/auth/signup",
        json={
            "password": "Password@1",
            "confirm_password": "Password@1",
            "name": "testname",
            "nickname": "testnick",  # 위 유저와 동일 닉네임
            "verify_token": "sometoken456",
        },
    )
    assert responses.status_code == 409


async def test_signup_password_mismatch(client: AsyncClient) -> None:
    await redis_client.set(EmailRedis.verify("sometoken456"), "new@example.com", ex=600)
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "password": "Password@1",
            "confirm_password": "Password@2",
            "name": "testname",
            "nickname": "testnick",
            "address": "testaddress",
            "verify_token": "sometoken456",
        },
    )
    assert response.status_code == 422


async def test_signup_duplicate_email(client: AsyncClient, db: AsyncSession) -> None:
    db.add(User(email="dup@example.com", hashed_password="hashed", name="tester", nickname="original"))
    await db.commit()

    await redis_client.set(EmailRedis.verify("sometoken999"), "dup@example.com", ex=600)
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "password": "Password@1",
            "confirm_password": "Password@1",
            "name": "testname",
            "nickname": "nickname",
            "verify_token": "sometoken999",
        },
    )
    assert response.status_code == 409
