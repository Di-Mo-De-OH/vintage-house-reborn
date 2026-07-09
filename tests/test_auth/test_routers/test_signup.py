from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.utils.redis import EmailRedis
from app.core.redis import redis_client


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
