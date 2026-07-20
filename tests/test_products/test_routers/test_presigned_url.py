from httpx import AsyncClient

from app.auth.models import User
from tests.utils import login


async def test_create_presigned_url_success(
    client: AsyncClient,
    admin_user: User,
) -> None:
    headers = await login(client, admin_user)
    response = await client.put("/api/v1/products/presigned-url", headers=headers, json={"content_type": "image/jpeg"})
    assert response.status_code == 200
    body = response.json()
    assert body["upload_url"].startswith("https://")
    assert body["key"].startswith("products/")
    assert body["key"].endswith(".jpeg")


async def test_create_presigned_url_forbidden_for_non_admin(
    client: AsyncClient,
    normal_user: User,
) -> None:
    headers = await login(client, normal_user)
    response = await client.put("/api/v1/products/presigned-url", headers=headers, json={"content_type": "image/jpeg"})
    assert response.status_code == 403


async def test_create_presigned_url_unauthorized(
    client: AsyncClient,
) -> None:
    response = await client.put("/api/v1/products/presigned-url", json={"content_type": "image/jpeg"})
    assert response.status_code == 401


async def test_create_presigned_url_invalid_content_type(
    client: AsyncClient,
    admin_user: User,
) -> None:
    headers = await login(client, admin_user)
    response = await client.put("/api/v1/products/presigned-url", headers=headers, json={"content_type": "image/pdf"})
    assert response.status_code == 422
