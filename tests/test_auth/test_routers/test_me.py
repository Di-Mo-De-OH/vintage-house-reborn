from httpx import AsyncClient

from app.auth.models import User


async def test_get_me_success(client: AsyncClient, test_user: User) -> None:
    login_response = await client.post(
        "/api/v1/auth/login", json={"email": "test@example.com", "password": "Password@1"}
    )
    access_token = login_response.json()["access_token"]
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert response.json()["nickname"] == "nickname"
    assert response.json()["name"] == "tester"
