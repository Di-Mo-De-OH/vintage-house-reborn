from datetime import datetime, timedelta, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken, User
from app.core.utils.security import hash_refresh_token


async def test_refresh_success(client: AsyncClient, test_user: User) -> str | None:
    await client.post("/api/v1/auth/login", json={"email": test_user.email, "password": "Password@1"})
    response = await client.post("/api/v1/auth/refresh")

    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_refresh_invalid(client: AsyncClient, test_user: User) -> str | None:
    response = await client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


async def test_refresh_invalid_token(client: AsyncClient, test_user: User) -> str | None:
    response = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": "nonexistenttoken123"})

    assert response.status_code == 401


async def test_refresh_expired_token(client: AsyncClient, test_user: User, db: AsyncSession) -> str | None:
    expired_token = "expiredtokenvalue"
    db.add(
        RefreshToken(
            user_id=test_user.id,
            token_hash=hash_refresh_token(expired_token),
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
    )
    await db.commit()
    response = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": expired_token})
    assert response.status_code == 401
