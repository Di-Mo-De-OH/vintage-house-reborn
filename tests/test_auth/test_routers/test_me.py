from httpx import AsyncClient
from sqlalchemy import select

from app.auth.models import User
from tests.utils import login


async def test_get_me_success(client: AsyncClient, test_user: User) -> None:
    headers = await login(client, test_user)

    response = await client.get(
        "/api/v1/auth/me",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert response.json()["nickname"] == "nickname"
    assert response.json()["name"] == "tester"


async def test_get_me_unauthorized(client: AsyncClient, test_user: User) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_patch_me_success(client: AsyncClient, test_user: User) -> None:
    headers = await login(client, test_user)
    response = await client.patch(
        "/api/v1/auth/me",
        headers=headers,
        json={"nickname": "새로운닉네임", "name": "새로운이름", "address": "새로운주소"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "새로운이름"
    assert response.json()["nickname"] == "새로운닉네임"
    assert response.json()["address"] == "새로운주소"


async def test_patch_me_partial_update(client: AsyncClient, test_user: User) -> None:
    headers = await login(client, test_user)
    response = await client.patch("/api/v1/auth/me", headers=headers, json={"nickname": "부분수정닉"})

    assert response.status_code == 200
    assert response.json()["nickname"] == "부분수정닉"
    assert response.json()["name"] == test_user.name
    assert response.json()["address"] == test_user.address


async def test_patch_me_invalid(client: AsyncClient, test_user: User, test_user2: User) -> None:
    headers = await login(client, test_user)
    response = await client.patch(
        "/api/v1/auth/me",
        headers=headers,
        json={"nickname": test_user2.nickname},
    )
    assert response.status_code == 409


async def test_patch_me_unauthorized(client: AsyncClient) -> None:
    response = await client.patch(
        "/api/v1/auth/me",
        json={"nickname": "닉네임"},
    )
    assert response.status_code == 401


async def test_delete_me_success(client: AsyncClient, test_user: User, db: AsyncClient) -> None:
    headers = await login(client, test_user)
    response = await client.delete(
        "/api/v1/auth/me",
        headers=headers,
    )
    assert response.status_code == 204
    result = await db.execute(select(User).where(User.id == test_user.id))
    assert result.scalar_one_or_none() is None


async def test_delete_me_unauthorized(client: AsyncClient) -> None:
    response = await client.delete("/api/v1/auth/me")
    assert response.status_code == 401
