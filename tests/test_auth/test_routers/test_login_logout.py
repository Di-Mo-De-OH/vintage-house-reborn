from httpx import AsyncClient

from app.auth.models import User
from app.auth.utils.redis import LogoutRedis
from app.core.redis import redis_client
from app.core.utils.security import decode_access_token


async def test_login_success(client: AsyncClient, test_user: User) -> None:
    response = await client.post("/api/v1/auth/login", json={"email": test_user.email, "password": "Password@1"})

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.cookies


async def test_login_email_invalid(client: AsyncClient, test_user: User) -> None:
    response = await client.post("/api/v1/auth/login", json={"email": "test2@example.com", "password": "Password@1"})
    assert response.status_code == 401


async def test_login_password_invalid(client: AsyncClient, test_user: User) -> None:
    response = await client.post("/api/v1/auth/login", json={"email": test_user.email, "password": "Password@2"})
    assert response.status_code == 401


async def test_logout_success(client: AsyncClient, test_user: User) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "Password@1"},
    )
    access_token = login_response.json()["access_token"]
    response = await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 204


async def test_logout_without_session(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 204


async def test_logout_blacklist(client: AsyncClient, test_user: User) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "Password@1"},
    )
    access_token = login_response.json()["access_token"]
    await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
    payload = decode_access_token(access_token)

    assert await redis_client.exists(LogoutRedis.blacklist(payload["jti"]))
