from httpx import AsyncClient

from app.auth.models import User


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
